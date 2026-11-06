"""TC5 Steps 4 and 5: the two implementations of answer_contract_question,
measured on the same two questions. Per run: model calls, capability calls,
seconds, tokens, the size of one search response, and how many tool calls
the model asked for in its first turn (parallel or not).

Run from 01_Product_Engineering/challenge:
    uv run python measure.py                # Step 4: sections, as the endpoint returns today
    uv run python measure.py --full-pages   # Step 5: the whole page of each hit
Read-only on the contracts. Writes one JSON file under use_case/evals/runs/
(write justified: the README cites these numbers, so the raw runs are kept).
"""

import argparse
import asyncio
import json
import statistics
import time

from fastmcp import Client
from fastmcp.client import PythonStdioTransport

import mcp_agent
import retrieval

QUESTIONS = {
    "one search (Vendor07 price)": "What is the price per user in the Vendor07 contract?",
    "several searches (Vendor04 cancellation)": "What's the cancellation period for the Vendor04 contract?",
}
REPEATS = 3                       # tool calls vary between runs: report the median of 3
ORIGINAL_ASK = retrieval.ask_model
COLUMNS = ("model calls", "capability calls", "seconds", "tokens", "search response chars")


class Meter:
    """Counts model round trips, and the tool calls the model asked for in its first turn."""

    def __init__(self):
        self.calls = 0
        self.first_turn = None

    def counted(self, messages, tools):
        response = ORIGINAL_ASK(messages, tools)
        self.calls += 1
        if self.first_turn is None:
            self.first_turn = len(response.choices[0].message.tool_calls or [])
        return response


def counting(funcs, counts):
    """The same functions, each adding 1 to counts[name] when it runs (tool path: same process)."""
    def wrap(name, func):
        def counted(**kwargs):
            counts[name] = counts.get(name, 0) + 1
            return func(**kwargs)
        return counted
    return {name: wrap(name, func) for name, func in funcs.items()}


async def run_tool(question, full_pages):
    funcs = dict(retrieval.RAG_FUNCS)
    if full_pages:
        funcs["search_chunks"] = retrieval.search_full_pages     # added in Chunk 3
    counts = {}
    result = retrieval.run_agent(question, retrieval.RAG_TOOLS, counting(funcs, counts))
    return result, sum(counts.values())


async def run_mcp(question, full_pages):
    args = ["--full-pages"] if full_pages else []
    async with Client(PythonStdioTransport(mcp_agent.SERVER_FILE, args=args, keep_alive=False)) as client:
        result = await mcp_agent.run_agent_mcp(question, client)
    return result, len(result["trace"])      # counted on the client: the server is another process


async def measure_once(way, question, full_pages):
    meter = Meter()
    retrieval.ask_model = mcp_agent.ask_model = meter.counted
    started = time.perf_counter()
    try:
        runner = run_tool if way == "tool" else run_mcp
        result, capability_calls = await runner(question, full_pages)
    finally:
        retrieval.ask_model = mcp_agent.ask_model = ORIGINAL_ASK
    sizes = [step["chars"] for step in result["trace"] if step["tool"] == "search_chunks"]
    return {"model calls": meter.calls, "capability calls": capability_calls,
            "seconds": round(time.perf_counter() - started, 1),
            "tokens": result["tokens_in"] + result["tokens_out"],
            "search response chars": round(statistics.mean(sizes)) if sizes else 0,
            "first-turn tool calls": meter.first_turn,
            "tools": [step["tool"] for step in result["trace"]],
            "answer": " ".join(result["answer"].split())[:100]}


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-pages", action="store_true", help="Step 5: search returns whole pages")
    full_pages = parser.parse_args().full_pages
    rows = []
    for label, question in QUESTIONS.items():
        for way in ("tool", "mcp"):
            runs = [await measure_once(way, question, full_pages) for _ in range(REPEATS)]
            median = {column: statistics.median(run[column] for run in runs) for column in COLUMNS}
            first = [run["first-turn tool calls"] for run in runs]
            rows.append({"request": label, "way": way, **median, "first-turn tool calls": first, "runs": runs})
            print(f"{label:42} {way:4} model {median['model calls']}  capability {median['capability calls']}  "
                  f"{median['seconds']} s  {median['tokens']} tokens  "
                  f"search response {median['search response chars']} chars  first turn {first}")
    out = retrieval.RUNS_DIR / ("measure-step5-full-pages.json" if full_pages else "measure-step4.json")
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("saved", out)


if __name__ == "__main__":
    asyncio.run(main())