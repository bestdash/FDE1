import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]   # evals -> use_case -> repo root
sys.path.insert(0, str(ROOT))                # lets Python find the helpers folder
from helpers import harness                  

EVALS = Path(__file__).resolve().parent      # the use_case/evals folder
# One sentence a correct decline says.
DECLINE_TEXT = "Missing document."


def oracle_text(case: dict) -> str:
    """The perfect answer for one case, built from the labels only."""
    if case["kind"] == "decline":
        parts = [DECLINE_TEXT]
    else:
        parts = []
        if case.get("end_date"):              # end-date questions: end date first
            parts.append(case["end_date"])  
        parts += case["expected_terms"]
    parts += [f"[{gold}]" for gold in case["gold"]]   # gold citations
    return "\n".join(parts)

def load_questions():
    """One case per line of retrieval.jsonl."""
    cases = []
    for line in (EVALS / "retrieval.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue                         # skip empty lines
        case = json.loads(line)              # keeps question, kind, gold, expected_terms
        case["input"] = case["question"]     # harness.run sends case["input"] to the system
        case["output"] = oracle_text(case)   # the perfect answer
        cases.append(case)
    return cases


CASES = load_questions()

def echo(question: str) -> str:
    """Dumb baseline: returns the question unchanged."""
    return question

ORACLE = {case["input"]: case["output"] for case in CASES}   # question -> perfect answer

def oracle(question: str) -> str:
    """Perfect baseline: returns the oracle text for this question."""
    return ORACLE[question]

# Scorer for failures.md rank 4: "No answer: turn limit hit, cause unknown"
NO_ANSWER_TEXTS = [
    "(max turns reached)",                           # retrieval.py runs
    "I searched the contracts and found no answer",  # endpoint fallback, app.py line 118
]

def no_answer(actual: str, case: dict) -> float:
    """0.0 = no answer, 1.0 = there is an answer."""
    # if the answer is empty, return 0.0
    if not actual.strip():
        return 0.0
    # if any text from NO_ANSWER_TEXTS is in the answer, return 0.0
    if any(text in actual for text in NO_ANSWER_TEXTS):
        return 0.0
    else: return 1.0

SCORERS = {"no_answer": no_answer}   # grows to 4 scorers

if __name__ == "__main__":
    print(harness.run(CASES, echo, SCORERS, name="echo"))
    print(harness.run(CASES, oracle, SCORERS, name="oracle"))
    print(CASES[3]["output"])