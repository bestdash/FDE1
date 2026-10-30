import json
import sys
import re
from datetime import date
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

MONTHS = {name: number for number, name in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}
DAY_MONTH_YEAR = re.compile(r"\b(\d{1,2}) ([A-Za-z]{3,9})\.? (\d{4})\b")   # 31 December 2026, 31 Dec 2026
ISO_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")                       # 2026-12-31


def find_dates(text: str) -> list:
    """Every date in a text, in the order it appears. Plumbing for the dates scorer."""
    found = []
    for match in DAY_MONTH_YEAR.finditer(text):
        month = MONTHS.get(match.group(2)[:3].lower())
        if month:
            try:
                found.append((match.start(), date(int(match.group(3)), month, int(match.group(1)))))
            except ValueError:
                pass                                   # not a real date, e.g. 31 February
    for match in ISO_DATE.finditer(text):
        try:
            found.append((match.start(), date(int(match.group(1)), int(match.group(2)), int(match.group(3)))))
        except ValueError:
            pass
    return [day for _, day in sorted(found)]           # sorted by position in the text

def no_answer(actual: str, case: dict) -> float:
    """0.0 = no answer, 1.0 = there is an answer."""
    # if the answer is empty, return 0.0
    if not actual.strip():
        return 0.0
    # if any text from NO_ANSWER_TEXTS is in the answer, return 0.0
    if any(text in actual for text in NO_ANSWER_TEXTS):
        return 0.0
    else: return 1.0

# Scorer for failures.md rank 3: "Date errors: the model works out dates itself"
def dates(actual: str, case: dict) -> float:
    """0.0 = a date error, 1.0 = the dates are right."""
    expected = find_dates(" ".join(case["expected_terms"]))   # the dates in labels
    in_answer = find_dates(actual)                             # the dates in the answer, in order

    # rule 1: if any expected date is missing from the answer, fail
    if not all(day in in_answer for day in expected):
        return 0.0
    # rule 2: on end-date questions, the first date in the answer must be the end date
    if case.get("end_date"):
        if not in_answer or in_answer[0] != find_dates(case["end_date"])[0]:
            return 0.0
    return 1.0  

SCORERS = {"no_answer": no_answer, "dates": dates}   # grows to 4 scorers


if __name__ == "__main__":
    print(harness.run(CASES, echo, SCORERS, name="echo"))
    print(harness.run(CASES, oracle, SCORERS, name="oracle"))
    #print(CASES[3]["output"])