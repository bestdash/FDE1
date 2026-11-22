"""TC7 Chunk 6: the cost-saving test (README Part 3, test 2).

Asks the same questions with memory off (attempt 1: the agent must search)
and with memory on (attempt 2: the contract record answers), RUNS times each,
and checks that attempt 2 is cheaper. Calls the model: about 30 conversations.

Run from the repo root:
    uv run python use_case/evals/cost_saving.py
Break check (empty memory, 1 run each):
    MEMORY_DB=/tmp/empty_memory.sqlite RUNS=1 uv run python use_case/evals/cost_saving.py
"""
import importlib
import os
import sys
from pathlib import Path
from statistics import mean

CHALLENGE = Path(__file__).resolve().parents[2] / "01_Product_Engineering" / "challenge"
sys.path.insert(0, str(CHALLENGE))
import retrieval

# Week 4 questions (retrieval.jsonl) whose answer is in the contract record.
RECORD_QUESTIONS = [
"What's the cancellation period for the Vendor04 contract?",
"What are the renewal terms of the Vendor10 contract?",
"When does the Vendor05 contract end?",
"When does the Vendor02 contract end?"
]
# Not in the record: memory should not make this one cheaper.
CONTROL = "What is the price per user in the Vendor07 contract?"
RUNS = int(os.getenv("RUNS", "3"))

def load(memory):
    """Re-import retrieval.py with MEMORY=on or off, so its tools and SYSTEM match that mode."""
    os.environ["MEMORY"] = memory
    return importlib.reload(retrieval)


def measure(question, memory):
    """Average tool calls and tokens in over RUNS answers to one question."""
    agent = load(memory)
    calls, tokens = [], []
    for _ in range(RUNS):
        result = agent.run_agent(question, agent.RAG_TOOLS, agent.RAG_FUNCS)
        calls.append(len(result["trace"]))
        tokens.append(result["tokens_in"])
    return mean(calls), mean(tokens)


def main():
    rows = []
    for question in RECORD_QUESTIONS + [CONTROL]:
        off_calls, off_tokens = measure(question, "off")
        on_calls, on_tokens = measure(question, "on")
        rows.append((question, off_calls, on_calls, off_tokens, on_tokens))
        print(f"{question[:55]:55}  calls {off_calls:.1f} -> {on_calls:.1f}"
              f"   tokens in {off_tokens:.0f} -> {on_tokens:.0f}")

    record_rows = rows[:-1]   # the control is printed, not asserted
    control = rows[-1]
    
    off_calls = sum(row[1] for row in record_rows)
    on_calls = sum(row[2] for row in record_rows)
    off_tokens = sum(row[3] for row in record_rows)
    on_tokens = sum(row[4] for row in record_rows)
    calls_ratio = on_calls / off_calls       # 0.5 = memory on used half the calls
    tokens_ratio = on_tokens / off_tokens

    print()
    print(f"Total, {len(record_rows)} record questions, {RUNS} runs each:")
    print(f"  tool calls {off_calls:.1f} -> {on_calls:.1f}  (on/off = {calls_ratio:.2f})")
    print(f"  tokens in  {off_tokens:.0f} -> {on_tokens:.0f}  (on/off = {tokens_ratio:.2f})")
    print(f"Control (not in the record): calls {control[1]:.1f} -> {control[2]:.1f}, "
          f"tokens in {control[3]:.0f} -> {control[4]:.0f}")

    # Pass rule (decided Nov 21, before the first run): memory on uses at most
    # half the tool calls and at most half the tokens in of memory off.
    failures = []
    if calls_ratio > 0.5:
        failures.append(f"calls not halved (on/off = {calls_ratio:.2f})")
    if tokens_ratio > 0.5:
        failures.append(f"tokens in not halved (on/off = {tokens_ratio:.2f})")
    if failures:
        print("FAIL: " + "; ".join(failures))
        sys.exit(1)
    print("PASS: memory on halves tool calls and tokens in on the record questions")



if __name__ == "__main__":
    main()