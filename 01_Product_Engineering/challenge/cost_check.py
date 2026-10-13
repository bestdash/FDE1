"""Step 13: what does one draft cost, and what would other models charge for it?

  uv run python cost_check.py --run    call your model once per golden (9 calls, a few cents),
                                       save cost_run1.json, then write cost_comparison.md
  uv run python cost_check.py          no model call: re-render cost_comparison.md from
                                       cost_run1.json (use it after editing PRICES or INPUTS)

Token counts are measured on the model in LLM_MODEL. Every other model is priced
on those same counts, which is an estimate: tokenizers differ by a few percent.
The prompt is built by schema.build_prompt, so it is the one the endpoint sends.
"""

import json
import os
import statistics
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GOLDEN = ROOT / "use_case" / "evals" / "golden.jsonl"
RUN_FILE = HERE / "cost_run1.json"
REPORT = HERE / "cost_comparison.md"

# Looked up, not measured. Dollars per million tokens at standard rates, no caching,
# no batch discount. Check the date before you quote a number from this table.
PRICES_CHECKED = "2026-10-13"
ANTHROPIC_URL = "https://platform.claude.com/docs/en/about-claude/pricing"
OPENAI_URL = "https://developers.openai.com/api/docs/models/gpt-4.1-mini"
PRICES = {
    # name: (usd per 1M input, usd per 1M output, source)
    "Claude Haiku 5.5": (0.10, 0.50, ANTHROPIC_URL),  # prompts up to 100k tokens
    "Claude Haiku 4.5": (1.00, 5.00, ANTHROPIC_URL),
    "Claude Sonnet 5.5": (2.00, 10.00, ANTHROPIC_URL),
    "Claude Sonnet 5": (2.00, 10.00, ANTHROPIC_URL),
    "Claude Sonnet 4.6": (3.00, 15.00, ANTHROPIC_URL),
    "Claude Sonnet 4.5": (3.00, 15.00, ANTHROPIC_URL),
    "Claude Opus 5.5": (4.00, 20.00, ANTHROPIC_URL),
    "Claude Opus 5": (5.00, 25.00, ANTHROPIC_URL),
    "Claude Opus 4.5": (5.00, 25.00, ANTHROPIC_URL),
    "gpt-4.1-mini": (0.40, 1.60, OPENAI_URL),
}
# Which PRICES row the model in LLM_MODEL maps to. Add a line if you change LLM_MODEL.
MODEL_TO_PRICE_ROW = {
    "anthropic/claude-sonnet-4-6": "Claude Sonnet 4.6",
    "anthropic/claude-sonnet-5-5": "Claude Sonnet 5.5",
    "gpt-4.1-mini": "gpt-4.1-mini",
}

# Your company's numbers. Left as None on purpose: these are claims about your
# workplace, so they are yours to fill in. Mark each one measured or looked up
# in the README. Annual and ratio lines stay out of the report until all are set.
INPUTS = {
    # 120 contracts x (3 to 4 review emails + 3 to 4 negotiation emails each) per year.
    "drafts_per_year": {"low": 720, "base": 840, "high": 960},
    # One manual pass incl. preparation: 10 for a simple SaaS contract, 20 for a complex
    # one. Looked up, not timed.
    "minutes_per_draft": {"low": 10, "base": 15, "high": 20},
    # About $120K a year, a very rough figure: 120000 / (250 days x 8 h). Salary only,
    # no overhead, so the human cost is understated and the ratio is conservative.
    "loaded_usd_per_hour": 60,
    # Negotiation is not a message_type yet. Every draft is priced like this type,
    # the dearest one, so the budget is a maximum.
    "price_basis": "renewal_review_email",
}


def load_env() -> None:
    """Read the repo root .env into os.environ before llm.py reads it at import."""
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        env = ROOT / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                key, sep, value = line.partition("=")
                if sep and not line.lstrip().startswith("#"):
                    os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_goldens() -> list[dict]:
    with GOLDEN.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE,
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def measure() -> dict:
    """One non-streaming call per golden. Non-streaming returns exact usage."""
    load_env()
    import llm
    from litellm import completion
    from schema import Request, build_prompt, route_request

    records = []
    for number, golden in enumerate(load_goldens(), start=1):
        request = Request(**golden["input"])
        message_type, _ = route_request(request)
        kwargs = {
            "model": llm.MODEL,
            "messages": [
                {"role": "system", "content": llm.SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(request, message_type)},
            ],
        }
        if llm.API_BASE:
            kwargs["api_base"] = llm.API_BASE
        if llm.EXTRA_HEADERS:
            kwargs["extra_headers"] = llm.EXTRA_HEADERS

        started = time.perf_counter()
        response = completion(**kwargs)
        seconds = time.perf_counter() - started
        usage = response.usage
        records.append({
            "golden": number,
            "message_type": message_type,
            "tokens_in": usage.prompt_tokens,
            "tokens_out": usage.completion_tokens,
            "seconds": round(seconds, 2),
            "reply": response.choices[0].message.content.strip(),
        })
        print(f"golden {number}: {message_type}, {usage.prompt_tokens} in, "
              f"{usage.completion_tokens} out, {seconds:.1f}s")

    return {
        "date": date.today().isoformat(),
        "model": llm.MODEL,
        "commit": git_commit(),
        "records": records,
    }


def cost(tokens_in: float, tokens_out: float, usd_in: float, usd_out: float) -> float:
    return tokens_in / 1e6 * usd_in + tokens_out / 1e6 * usd_out


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile. With 9 samples p95 is the slowest call."""
    ordered = sorted(values)
    return ordered[max(0, round(p / 100 * len(ordered)) - 1)]


def usd(value: float) -> str:
    return f"${value:.5f}" if value < 0.1 else f"${value:,.2f}"


def render(run: dict) -> str:
    records = run["records"]
    mean_in = statistics.mean(r["tokens_in"] for r in records)
    mean_out = statistics.mean(r["tokens_out"] for r in records)
    seconds = [r["seconds"] for r in records]
    own_row = MODEL_TO_PRICE_ROW.get(run["model"])
    lines = [
        "# Step 13: cost per draft and model comparison",
        "",
        f"Run on {run['date']} at commit `{run['commit']}`. Model measured: `{run['model']}`. "
        f"{len(records)} goldens, one call each, no caching, no batch.",
        "",
        "Labels: **measured** = read from a run. **looked up** = taken from a public page. "
        "**your input** = a claim about your company.",
        "",
        "## 1. Token spend per golden (measured)",
        "",
        "| Golden | message_type | Tokens in | Tokens out | Seconds |",
        "| ---: | --- | ---: | ---: | ---: |",
    ]
    for r in records:
        lines.append(f"| {r['golden']} | {r['message_type']} | {r['tokens_in']} | "
                     f"{r['tokens_out']} | {r['seconds']} |")
    lines += [
        f"| **mean** | | **{mean_in:.0f}** | **{mean_out:.0f}** | **{statistics.mean(seconds):.1f}** |",
        "",
        f"Latency over {len(records)} calls: p50 {percentile(seconds, 50):.1f}s, "
        f"p95 {percentile(seconds, 95):.1f}s (nine samples, so p95 is the slowest call).",
        "",
        "## 2. Prices (looked up)",
        "",
        f"Standard rates in USD per million tokens, checked {PRICES_CHECKED}. "
        "Haiku 5.5 is the rate for prompts up to 100,000 tokens; ours are far below that.",
        "",
        "| Model | $/1M in | $/1M out | Source |",
        "| --- | ---: | ---: | --- |",
    ]
    for name, (p_in, p_out, src) in PRICES.items():
        lines.append(f"| {name} | {p_in:g} | {p_out:g} | {src} |")

    lines += [
        "",
        "## 3. Cost of one draft by model",
        "",
        "Priced on the mean token counts above (measured on "
        f"`{run['model']}`). Rows other than the measured model are estimates.",
        "",
        "| Model | Cost per draft | Drafts per $1 | vs measured model |",
        "| --- | ---: | ---: | ---: |",
    ]
    base = cost(mean_in, mean_out, *PRICES[own_row][:2]) if own_row else None
    rows = sorted(PRICES.items(), key=lambda kv: cost(mean_in, mean_out, kv[1][0], kv[1][1]))
    for name, (p_in, p_out, _) in rows:
        c = cost(mean_in, mean_out, p_in, p_out)
        tag = " (measured)" if name == own_row else ""
        rel = f"{c / base:.2f}x" if base else "n/a"
        lines.append(f"| {name}{tag} | {usd(c)} | {1 / c:,.0f} | {rel} |")

    if own_row:
        p_in, p_out, _ = PRICES[own_row]
        per_golden = [cost(r["tokens_in"], r["tokens_out"], p_in, p_out) for r in records]
        lines += [
            "",
            f"Spread on `{run['model']}`: cheapest draft {usd(min(per_golden))}, "
            f"dearest {usd(max(per_golden))}, mean {usd(statistics.mean(per_golden))}.",
            "",
            "By message_type:",
            "",
            "| message_type | Drafts | Mean in | Mean out | Mean cost |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
        for mtype in sorted({r["message_type"] for r in records}):
            group = [r for r in records if r["message_type"] == mtype]
            g_in = statistics.mean(r["tokens_in"] for r in group)
            g_out = statistics.mean(r["tokens_out"] for r in group)
            lines.append(f"| {mtype} | {len(group)} | {g_in:.0f} | {g_out:.0f} | "
                         f"{usd(cost(g_in, g_out, p_in, p_out))} |")
    else:
        lines += ["", f"`{run['model']}` has no entry in MODEL_TO_PRICE_ROW, so the "
                      "measured model is not marked in the table."]

    lines += ["", "## 4. Annual math (your inputs)", ""]
    basis = INPUTS["price_basis"]
    basis_records = [r for r in records if r["message_type"] == basis]
    if own_row and basis_records and all(v is not None for v in INPUTS.values()):
        b_in = statistics.mean(r["tokens_in"] for r in basis_records)
        b_out = statistics.mean(r["tokens_out"] for r in basis_records)
        drafts, mins = INPUTS["drafts_per_year"], INPUTS["minutes_per_draft"]
        rate = INPUTS["loaded_usd_per_hour"]
        n, m = drafts["base"], mins["base"]
        human_year = m / 60 * rate * n
        # Dearest single golden on the measured model, for the worst-case budget.
        own_in, own_out = PRICES[own_row][:2]
        dearest = max(cost(r["tokens_in"], r["tokens_out"], own_in, own_out) for r in records)
        lines += [
            f"- drafts per year: {drafts['low']:,} / **{n:,}** / {drafts['high']:,} "
            "(low / base / high; **your input**: 120 contracts x 3 to 4 review emails "
            "+ 3 to 4 negotiation emails)",
            f"- minutes per manual draft: {mins['low']} / **{m}** / {mins['high']} "
            "(**looked up**, not timed: 10 simple SaaS, 20 complex, preparation included)",
            f"- loaded $/hour: {rate} (**your input**: about $120K a year divided by 2,000 hours, "
            "salary only)",
            f"- every draft priced like `{basis}`: mean {b_in:.0f} in, {b_out:.0f} out "
            "(**measured**), the dearest type, because negotiation is not built yet",
            "",
            f"Base scenario: {n:,} drafts, {m} minutes. Human per year is the same for every "
            f"model: {m} / 60 x ${rate} x {n:,} = {usd(human_year)}.",
            "",
            "| Model | Cost per draft | Model per year | Human per year | Ratio | Band |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
        basis_rows = sorted(PRICES.items(), key=lambda kv: cost(b_in, b_out, kv[1][0], kv[1][1]))
        for name, (p_in, p_out, _) in basis_rows:
            per_draft = cost(b_in, b_out, p_in, p_out)
            ratio = human_year / (per_draft * n)
            band = "comfortable" if ratio > 20 else "viable, with discipline" if ratio >= 3 else "thin"
            tag = " (measured)" if name == own_row else ""
            lines.append(f"| {name}{tag} | {usd(per_draft)} | {usd(per_draft * n)} | "
                         f"{usd(human_year)} | {ratio:,.0f}x | {band} |")

        lines += [
            "",
            f"Scenarios on `{run['model']}` (model per year / ratio). Rows are drafts per year, "
            "columns are minutes per manual draft.",
            "",
            "| Drafts per year | " + " | ".join(f"{k} min" for k in mins.values()) + " |",
            "| ---: | " + " | ".join("---:" for _ in mins) + " |",
        ]
        per_draft_own = cost(b_in, b_out, own_in, own_out)
        for count in drafts.values():
            cells = []
            for minutes in mins.values():
                h_year = minutes / 60 * rate * count
                cells.append(f"{usd(per_draft_own * count)} / {h_year / (per_draft_own * count):,.0f}x")
            lines.append(f"| {count:,} | " + " | ".join(cells) + " |")

        worst = dearest * drafts["high"]
        lines += [
            "",
            f"Maximum budget: high volume ({drafts['high']:,} drafts) with every draft as dear as "
            f"the dearest golden ({usd(dearest)}) is **{usd(worst)} per year** on `{run['model']}`.",
            "",
            "Formulas, as in the README: model per year = cost per draft x drafts per year; "
            "human per year = minutes / 60 x loaded $/hour x drafts per year; "
            "ratio = human / model. The README bands stop at 20x (comfortable); every row here is "
            "far above it.",
        ]
    else:
        lines += ["Not computed yet. Set `drafts_per_year`, `minutes_per_draft` and "
                  "`loaded_usd_per_hour` in `INPUTS` at the top of `cost_check.py`, then run "
                  "`uv run python cost_check.py` again (no new model calls)."]

    lines += [
        "",
        "## 5. Caveats",
        "",
        "- One run, nine goldens. The goldens are hand-picked cases, not a sample of real traffic, "
        "so the mean is a rough guide.",
        "- Other models are priced on this model's token counts. Their tokenizers differ, and a "
        "different model also writes a different length of reply.",
        "- Standard rates only. Prompt caching and batch discounts would lower the figures; "
        "the long, repeated rules block in the prompt is a caching candidate.",
        "- Cost is not quality. A cheaper model has to pass the same goldens before its price counts.",
        "- Negotiation emails have no message_type yet. They are priced like renewal_review_email, "
        "so the real cost of that part may differ once it is built.",
        "- The hourly rate is salary only, with no overhead, so human cost is understated and "
        "the ratio is conservative.",
        "- With a ratio this high, model cost is unlikely to stop adoption. Latency, approval and "
        "quality are the likelier blockers.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    if "--run" in sys.argv[1:]:
        run = measure()
        RUN_FILE.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"saved {RUN_FILE.name}")
    elif RUN_FILE.exists():
        run = json.loads(RUN_FILE.read_text(encoding="utf-8"))
    else:
        print(__doc__)
        sys.exit(2)

    REPORT.write_text(render(run), encoding="utf-8")
    print(f"report written to {REPORT}")


if __name__ == "__main__":
    main()
