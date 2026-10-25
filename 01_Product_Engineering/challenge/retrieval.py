import json
import os
import re
import time
from pathlib import Path
import argparse
from datetime import date


import litellm
import llm  
from litellm.exceptions import UnsupportedParamsError
from rank_bm25 import BM25Okapi

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACTS = ROOT / "use_case" / "data" / "contracts"
CASES_FILE = ROOT / "use_case" / "evals" / "retrieval.jsonl"
RUNS_DIR = ROOT / "use_case" / "evals" / "runs"
RESULTS_FILE = ROOT / "use_case" / "evals" / "retrieval_results.md"
SETTINGS = "BM25 over ## sections; search_chunks k default 4, max 8; 1000 chars per chunk; max_turns 6"

TOKEN = re.compile(r"[a-z0-9£$%]+")

def tokenize(text):
    return TOKEN.findall(text.lower())

PAGES = {p.name: p.read_text(encoding="utf-8") for p in sorted(CONTRACTS.glob("SYN-*.md"))}

CHUNK_PREFIX = True   # rag-v1: False (baseline). rag-v2: True (file, vendor, title in every chunk)

chunks = []
for page_name, page_text in PAGES.items():
    title = page_text.splitlines()[0].lstrip("#").strip()   # "Order Form"
    vendor = "Vendor" + page_name[4:6]                       # "SYN-10-renewal.md" -> "Vendor10" (synthetic shortcut)
    sections = re.split(r"(?=^## )", page_text, flags=re.M)
    for section in sections:
        if not section.strip():
            continue                                                   # skip empty pieces
        heading = section.strip().splitlines()[0].lstrip("#").strip()  # "## Terms" -> "Terms"
        text = section.strip()
        if CHUNK_PREFIX:
            text = f"{page_name} {vendor} {title}\n{text}"
        chunks.append({"id": f"{page_name}#{heading}", "page": page_name, "text": text})

bm25 = BM25Okapi([tokenize(chunk["text"]) for chunk in chunks])


def search_chunks(query: str, k: int = 4) -> str:
    scores = bm25.get_scores(tokenize(query))
    order = sorted(range(len(chunks)), key=lambda index: scores[index], reverse=True)[: max(1, min(k, 8))]
    return "\n\n---\n\n".join(f"[{chunks[index]['id']}]\n{chunks[index]['text'][:1000]}" for index in order)

RAG_FUNCS = {"search_chunks": search_chunks}

def schema(name, description, properties, required=()):
    return {"type": "function", "function": {"name": name, "description": description,
            "parameters": {"type": "object", "properties": properties, "required": list(required)}}}

RAG_TOOLS = [schema("search_chunks", "Search ranked corpus chunks. Search again with a new query when evidence is incomplete.",
                        {"query": {"type": "string"}, "k": {"type": "integer"}}, ["query"])]
SAMPLER = {"temperature": 0}  # deterministic where the provider allows it
PRICE_IN, PRICE_OUT = 2.0, 10.0  # USD per million tokens, Claude Sonnet 5.5 (looked up Oct 25, 2026). Change with the model.

def ask_model(messages, tools):
    """One chat turn with tools offered. Every retrieval model call goes through here.

    Uses the same model settings as llm.py (LLM_MODEL, LLM_API_BASE,
    LLM_EXTRA_HEADERS), so switching provider stays a .env change.
    """
    kwargs = dict(model=llm.MODEL, messages=messages, tools=tools)  # tool_choice defaults to "auto"; some gateways reject it sent explicitly
    if llm.API_BASE:
        kwargs["api_base"] = llm.API_BASE
    if llm.EXTRA_HEADERS:
        kwargs["extra_headers"] = llm.EXTRA_HEADERS
    try:
        return litellm.completion(timeout=600, **SAMPLER, **kwargs)
    except UnsupportedParamsError:
        SAMPLER.clear()  # some providers accept only their default temperature; run at it from now on
        return litellm.completion(timeout=600, **kwargs)

SYSTEM = (
    "Answer questions about our contracts only from the search results. Do not make information up. "
    "Investigate before answering: search again if the evidence is incomplete. "
    "Cite every source exactly as it appears in brackets, for example [SYN-04-order.md#Terms]. "
    "You may compute a date or amount from terms the contract states (for example start date plus term), "
    "and say how you computed it. "
    "If the contracts do not answer the question, say so. "
    "If the answer depends on a document that is referenced but not in the results "
    "(for example online terms or main terms), say which one is missing and suggest "
    "asking the vendor for the last signed copy." \
    " When the evidence comes from grep or a full page, cite the file plus the ## heading "
    "the text sits under, in the same bracket format."
)

def run_agent(question, tools, funcs, max_turns=6):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    trace, chars = [], 0
    tokens = {"tokens_in": 0, "tokens_out": 0}  # summed over every model call for this question
    started = time.perf_counter()
    for _ in range(max_turns):
        response = ask_model(messages, tools)
        usage = getattr(response, "usage", None)
        tokens["tokens_in"] += getattr(usage, "prompt_tokens", 0) or 0
        tokens["tokens_out"] += getattr(usage, "completion_tokens", 0) or 0
        msg = response.choices[0].message
        calls = msg.tool_calls or []
        if not calls:
            return {"answer": (msg.content or "").strip(), "trace": trace, "evidence_chars": chars,
                    "latency_s": time.perf_counter() - started, "stopped": "answer", **tokens}
        shaped = [{"id": call.id, "type": "function", "function": {"name": call.function.name, "arguments": call.function.arguments}} for call in calls]
        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": shaped})
        for call in shaped:
            name = call["function"]["name"]
            try:
                args = json.loads(call["function"]["arguments"] or "{}")
                if name not in funcs:
                    raise KeyError(f"unknown tool {name}")
                result = str(funcs[name](**args))
            except Exception as exc:
                result = f"(tool error: {type(exc).__name__}: {exc})"
            chars += len(result)
            trace.append({"tool": name, "args": args, "chars": len(result)})
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    return {"answer": "(max turns reached)", "trace": trace, "evidence_chars": chars,
            "latency_s": time.perf_counter() - started, "stopped": "max_turns", **tokens}

DECLINE_MARKERS = ("not ", "no ", "cannot", "can't", "unavailable", "does not", "doesn't", "isn't", "only covers", "no data")

def score(case, result):
    answer = result["answer"].lower()
    if case["kind"] == "decline":
        # Retrieval always returns a top-k. Declining is the loop's job, so the
        # pass mark here is "it refused" -- said so, and invented no figure.
        passed = any(marker in answer for marker in DECLINE_MARKERS) and not any(term.lower() in answer for term in case["expected_terms"])
    else:
        passed = all(term.lower() in answer for term in case["expected_terms"])
    return {
        "pass": passed,
        "cited_all_gold": all(g.lower() in answer for g in case["gold"]) if case["gold"] else None,
        "calls": len(result["trace"]),
        "evidence_chars": result["evidence_chars"],
        "latency_s": round(result["latency_s"], 2),
        "stopped": result["stopped"],
        "tokens_in": result["tokens_in"],
        "tokens_out": result["tokens_out"],
        "cost_usd": (result["tokens_in"] * PRICE_IN + result["tokens_out"] * PRICE_OUT) / 1_000_000,
    }

def yes(value):
    return "n/a" if value is None else ("yes" if value else "**no**")

# DCI
WIKI_INDEX = (CONTRACTS / "index.md").read_text(encoding="utf-8")

def list_pages() -> str:
    return WIKI_INDEX

def grep_wiki(pattern: str) -> str:
    try:
        rx = re.compile(pattern, re.I)
    except re.error:
        rx = re.compile(re.escape(pattern), re.I)
    hits = []
    for page, text in PAGES.items():
        for number, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                hits.append(f"{page}:{number}: {line}")
    return "\n".join(hits[:40]) or "(no matches)"

def read_page(page: str) -> str:
    if page not in PAGES:
        return f"(unknown page: {page})"
    return PAGES[page][:12000]

DCI_FUNCS = {"list_pages": list_pages, "grep_wiki": grep_wiki, "read_page": read_page}

DCI_TOOLS = [
    schema("list_pages", "Read the wiki index and page map.", {}),
    schema("grep_wiki", "Search exact text or a regular expression across wiki pages with line provenance.", {"pattern": {"type": "string"}}, ["pattern"]),
    schema("read_page", "Read a complete wiki source page by stable name.", {"page": {"type": "string", "enum": sorted(PAGES)}}, ["page"]),
]


DCI_SETTINGS = "contracts/index.md via list_pages; grep_wiki max 40 lines; read_page max 12000 chars; max_turns 6"
TECHNIQUES = {  # name -> (tools, funcs, settings line for the report)
    "rag": (RAG_TOOLS, RAG_FUNCS, f"{SETTINGS}; CHUNK_PREFIX={CHUNK_PREFIX}"),
    "dci": (DCI_TOOLS, DCI_FUNCS, DCI_SETTINGS),
}


def write_report(label, note, cases, results, rows, technique="rag", settings=None):
    """One readable file per run, plus one comparison line in retrieval_results.md."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [f"# Run {label}", "", f"- Date: {date.today()}", f"- Model: {llm.MODEL} (price used: ${PRICE_IN} in / ${PRICE_OUT} out per million tokens)",
             f"- Technique: {technique}", f"- Settings: {settings or SETTINGS}", f"- Change in this run: {note}", "",
             "| # | Kind | Question | Pass | Cited all gold | Calls | Evidence chars | Tokens in | Tokens out | Cost $ | Latency s | Stopped |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for i, (case, row) in enumerate(zip(cases, rows), start=1):
        lines.append(f"| {i} | {case['kind']} | {case['question']} | {yes(row['pass'])} | {yes(row['cited_all_gold'])} "
                     f"| {row['calls']} | {row['evidence_chars']:,} | {row['tokens_in']:,} | {row['tokens_out']:,} | {row['cost_usd']:.3f} | {row['latency_s']} | {row['stopped']} |")
    lines += ["", "## Answers", ""]
    for i, (case, result) in enumerate(zip(cases, results), start=1):
        tools = " → ".join(f"{s['tool']}({', '.join(str(v) for v in s['args'].values())[:50]})" for s in result["trace"]) or "(none)"
        lines += [f"### {i}. {case['question']}", "", f"- Gold: {', '.join(case['gold']) or '(none: decline)'}",
                  f"- Expected terms: {', '.join(case['expected_terms']) or '(none)'}", f"- Tool calls: {tools}", "",
                  result["answer"], ""]
    (RUNS_DIR / f"{label}.md").write_text("\n".join(lines), encoding="utf-8")

    passed = sum(bool(r["pass"]) for r in rows)
    with_gold = [r for r in rows if r["cited_all_gold"] is not None]
    cited = sum(bool(r["cited_all_gold"]) for r in with_gold)
    if not RESULTS_FILE.exists():
        RESULTS_FILE.write_text("# Retrieval results\n\nOne line per run. Full answers in `runs/<run>.md`.\n\n"
                                "| Run | Date | Change | Pass | Cited all gold | Calls | Evidence chars | Tokens in | Tokens out | Cost $ | Avg latency s | Hit max_turns |\n"
                                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n", encoding="utf-8")
    with RESULTS_FILE.open("a", encoding="utf-8") as f:
        f.write(f"| [{label}](runs/{label}.md) | {date.today()} | {note} | {passed}/{len(rows)} | {cited}/{len(with_gold)} "
                f"| {sum(r['calls'] for r in rows)} | {sum(r['evidence_chars'] for r in rows):,} "
                f"| {sum(r['tokens_in'] for r in rows):,} | {sum(r['tokens_out'] for r in rows):,} | {sum(r['cost_usd'] for r in rows):.2f} "
                f"| {sum(r['latency_s'] for r in rows) / len(rows):.1f} | {sum(r['stopped'] == 'max_turns' for r in rows)} |\n")
    print(f"\nPass {passed}/{len(rows)}, cited {cited}/{len(with_gold)}. Report: {RUNS_DIR / (label + '.md')}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, help="short run name, for example rag-v1")
    parser.add_argument("--note", default="", help="what changed in this run")
    parser.add_argument("--technique", choices=sorted(TECHNIQUES), default="rag",
                        help="rag = search_chunks; dci = list_pages, grep_wiki, read_page")
    args = parser.parse_args()
    tools, funcs, settings = TECHNIQUES[args.technique]
    print(f"Technique: {args.technique}. {settings}")

    cases = [json.loads(line) for line in CASES_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    results, rows = [], []
    for i, case in enumerate(cases, start=1):
        print(f"[{i}/{len(cases)}] {case['question']}")
        result = run_agent(case["question"], tools, funcs)
        results.append(result)
        rows.append(score(case, result))
    write_report(args.label, args.note, cases, results, rows, args.technique, settings)


if __name__ == "__main__":
    main()
