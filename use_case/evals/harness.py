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

CHALLENGE = ROOT / "01_Product_Engineering" / "challenge"   # where app.py lives

def endpoint(question: str) -> str:
    """The real system: the TC3 endpoint, called as a Python function (no server needed)."""
    if str(CHALLENGE) not in sys.path:
        sys.path.insert(0, str(CHALLENGE))        # app.py imports schema, llm, retrieval from its folder
    from app import answer_contract_question     # imported here, so echo and oracle stay instant
    return answer_contract_question(question)


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

VENDOR_NUMBER = re.compile(r"vendor\s?(\d{2})(?!\s*(?:days?|months?|years?))", re.IGNORECASE)  # Vendor04, vendor 05


def vendor_numbers(text: str) -> set:
    """The vendor numbers named in a text, as 2-digit strings, e.g. {"04", "10"}."""
    return {number.zfill(2) for number in VENDOR_NUMBER.findall(text)}

# Contracts with a master terms file (SYN-NN-terms.md), copied from truth.jsonl "documents".
# Copied here because use_case/data/ is never committed, and run.py must work from a clean checkout.
HAS_TERMS_FILE = {"01", "02", "04", "05", "07", "09", "10"}

def no_answer(actual: str, case: dict) -> float:
    """0.0 = no answer, 1.0 = there is an answer."""
    # Fail when the answer is empty.
    if not actual.strip():
        return 0.0
    # Fail when the answer is a 'no answer' text: the turn limit (retrieval.py) or the endpoint fallback (app.py line 118).
    if any(text in actual for text in NO_ANSWER_TEXTS):
        return 0.0
    else: return 1.0

# Scorer for failures.md rank 3: "Date errors: the model works out dates itself"
def dates(actual: str, case: dict) -> float:
    """0.0 = a date error, 1.0 = the dates are right."""
    expected = find_dates(" ".join(case["expected_terms"]))   # the dates in labels
    in_answer = find_dates(actual)                             # the dates in the answer, in order

    # Fail when a date from the label is missing: last day for notice, term dates or end date.
    # Example: the answer says 1 January 2027, the label says 31 December 2026.
    if not all(day in in_answer for day in expected):
        return 0.0
    # On 'when does it end' questions, fail when the first date is not the end date.
    # Example: it opens with 30 June 2026 (a past term), not 30 June 2028.
    if case.get("end_date"):
        if not in_answer or in_answer[0] != find_dates(case["end_date"])[0]:
            return 0.0
    return 1.0

# Scorer for failures.md rank 1: "Says something is missing that is in the documents"
MISSING_PHRASES = ["i didn't find any", "results don't say", "i found no",
                   "isn't in the results", "missing document"]       # your 5 phrases, lowercase
DOCUMENT_WORDS = ["agreement", "master", "terms"]                   # a whole document, not one fact
DECLINE_MARKERS = ("not ", "no ", "cannot", "can't", "unavailable", "does not",
                   "doesn't", "isn't", "only covers", "no data")     # from retrieval.py line 134


def missing_document(actual: str, case: dict) -> float:
    """0.0 = a false 'missing' claim (or a decline that declines nothing), 1.0 = fine."""
    text = actual.lower()
    if case["kind"] == "decline":
        # A decline question must decline: pass only when the answer says something is not there.
        if any(phrase in text for phrase in MISSING_PHRASES + list(DECLINE_MARKERS)):
            return 1.0
        else:
            return 0.0
    vendors_with_terms = vendor_numbers(case["question"]) & HAS_TERMS_FILE   # asked vendors that have a terms file
    for line in text.splitlines():
        # Fail when a line says a whole document (agreement, master terms) is missing,
        # and the vendor asked about does have a terms file. Example: 'that Agreement wasn't in the search results'.
        if any(phrase in line for phrase in MISSING_PHRASES) and any(word in line for word in DOCUMENT_WORDS):
            if vendors_with_terms:
                return 0.0
    return 1.0

# Scorer for failures.md rank 2: "Brings in other vendors' contracts in an answer about one vendor"
OTHER_VENDOR_WORDS = ["other vendor", "different vendor", "some vendor"]
COMPARISON_WORDS = ["compare", "comparison", "usual practice", "similar", "others"]


def other_vendors(actual: str, case: dict) -> float:
    """0.0 = another vendor in the answer, 1.0 = only the vendors asked about."""
    asked = vendor_numbers(case["question"])
    # A question that names no vendor is about all contracts: every vendor is allowed.
    # Example: 'if we are going to be stuck or not with the company after 3 years'.
    if not asked:
        return 1.0
    # The user asked for a comparison or usual practice: other vendors are allowed.
    if any(word in case["question"].lower() for word in COMPARISON_WORDS):
        return 1.0
    # Fail when the answer names a vendor the question did not ask about.
    # Example: a Vendor03 answer that mentions Vendor05 and Vendor10.
    if vendor_numbers(actual) - asked:
        return 0.0
    # Fail when the answer brings in other vendors in words. Example: 'Unlike some other vendors' terms'.
    if any(word in actual.lower() for word in OTHER_VENDOR_WORDS):
        return 0.0      
    return 1.0

SCORERS = {"no_answer": no_answer, "dates": dates,
           "missing_document": missing_document, "other_vendors": other_vendors}


CHALLENGE = ROOT / "01_Product_Engineering" / "challenge"   # where app.py lives


def endpoint(question: str) -> str:
    """The real system: the TC3 endpoint, called as a Python function (no server needed)."""
    if str(CHALLENGE) not in sys.path:
        sys.path.insert(0, str(CHALLENGE))        # app.py imports schema, llm, retrieval from its folder
    from app import answer_contract_question     # imported here, so echo and oracle stay instant
    return answer_contract_question(question)

def show_failures(report):
    """Print each case where a scorer gave less than 1.0, so you can read it."""
    for result in report.results:
        failed = [name for name, score in result.scores.items() if score < 1.0]
        if failed:
            print(f"  question {result.index + 1}: {result.input[:70]} -> failed: {', '.join(failed)}")


if __name__ == "__main__":
    print(harness.run(CASES, echo, SCORERS, name="echo"))
    print(harness.run(CASES, oracle, SCORERS, name="oracle"))
    if "--endpoint" in sys.argv:                  # 13 model calls, a few minutes
        report = harness.run(CASES, endpoint, SCORERS, name="endpoint",
                             progress=lambda done, total: print(f"  {done}/{total}", flush=True))
        print(report)
        show_failures(report)
        harness.save(report, EVALS / "runs" / "endpoint-step2.json")   # the answers, to read later