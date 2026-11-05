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
DECLINE_TEXT = "Not in the documents."


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

FULL_ANSWERS = {}   # question -> the whole endpoint answer (helpers/harness.py keeps only 2,000 characters)

def endpoint(question: str) -> str:
    """The real system: the TC3 endpoint, called as a Python function (no server needed)."""
    if str(CHALLENGE) not in sys.path:
        sys.path.insert(0, str(CHALLENGE))        # app.py imports schema, llm, retrieval from its folder
    from app import answer_contract_question     # imported here, so echo and oracle stay instant
    answer = answer_contract_question(question)
    FULL_ANSWERS[question] = answer
    return answer


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

VENDOR_NUMBER = re.compile(r"vendor\s?(\d{1,2})(?!\d)(?!\s*(?:days?|months?|years?))", re.IGNORECASE)  # Vendor04, vendor 05, Vendor 7 (Step 4)


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
OTHER_VENDOR_WORDS = ["other vendor", "different vendor", "some vendor", "other provider", "other supplier"]
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


# Scores by meaning, so it is not tied to the 5 phrases missing_document looks for.
import os
from helpers import config
from helpers.judge import Judge, parse_json

# What our files hold per vendor, from use_case/data/contracts/truth.jsonl "documents".
# Copied here because use_case/data/ is never committed. Same fact as HAS_TERMS_FILE.
VENDOR_DOCUMENTS = {
    "01": "SYN-01-order.md (order form), SYN-01-terms.md (master terms)",
    "02": "SYN-02-order.md (order form), SYN-02-terms.md (master terms)",
    "03": "SYN-03-order.md (order form) only. It refers to the vendor's online Terms of Service, "
          "which are not attached: we do not hold them",
    "04": "SYN-04-order.md (order form), SYN-04-terms.md (master terms)",
    "05": "SYN-05-order.md (first order form), SYN-05-terms.md (master terms), SYN-05-renewal.md "
          "(renewal order form; it replaces the first order, and all other master terms still apply)",
    "06": "SYN-06-order.md (order form) only. It refers to the vendor's online terms, not attached",
    "07": "SYN-07-order.md (order form), SYN-07-terms.md (master terms)",
    "08": "SYN-08-order.md (order form) only. It refers to standard terms published online, not attached",
    "09": "SYN-09-order.md (order form), SYN-09-terms.md (master terms)",
    "10": "SYN-10-order.md (first order form), SYN-10-terms.md (master terms), SYN-10-renewal.md "
          "(renewal order form; the master terms still apply unless it says otherwise)",
}

# Key facts per vendor, from truth.jsonl "fields" (first orders of 05 and 10: their order forms).
# Lets the judge see a false "not stated" about a fact, not only about a whole document.
# Set VENDOR_FACTS = {} to judge on the document list alone.
VENDOR_FACTS = {
    "01": "Term 1 January 2026 to 31 December 2026 (order). Renews automatically, 90 days notice (terms). "
          "USD 24,000 a year, 200 users at USD 120 (order).",
    "02": "Starts 1 March 2026, 36 months; the end date is not stated, 28 February 2029 is computed (order). "
          "No automatic renewal, 30 days notice (terms). USD 90,000 for the term: package with SSO, "
          "50,000 AI credits a year, unlimited projects (order).",
    "03": "Term 1 February 2026 to 31 January 2027. USD 18,000 a year, 300 users at USD 60 (order). "
          "Renewal and notice: not in our documents.",
    "04": "Term 1 April 2026 to 31 March 2027 (order). Renews automatically (terms); notice 90 days "
          "(the order overrides the 60 days in the terms). USD 40,000 a year: package with SSO, "
          "security add-on, premium support (order).",
    "05": "First order 1 July 2025 to 30 June 2026, 150 users at USD 100, USD 15,000 a year (first order). "
          "Renewal 1 July 2026 to 30 June 2028, 150 users at USD 110, USD 16,500 a year, USD 33,000 total, "
          "AI assistant bundle (renewal). Renews automatically, 90 days notice (terms, which still apply "
          "to the renewal).",
    "06": "Term 1 September 2026 to 31 August 2028. No automatic renewal, 30 days notice. USD 50,000 for "
          "the term: 3,500 learner seats, extra seats USD 1.50 per seat per month, SSO (order).",
    "07": "Term 15 January 2026 to 14 January 2027 (order). Renews automatically, 30 days notice (terms). "
          "USD 30,000 a year: 250 users at USD 80, security add-on, support SLA add-on (order).",
    "08": "Starts 1 November 2025, 36 months; the end date is not stated (order). USD 120,000 for the term: "
          "package with SSO, 100,000 AI credits a year, priority support (order). "
          "Renewal and notice: not in our documents.",
    "09": "Term 1 May 2026 to 30 April 2027 (order). No automatic renewal, 60 days notice (terms). "
          "USD 12,000 a year: 5 TB storage, standard support; invoices due within 30 days (order).",
    "10": "First order 1 December 2025 to 30 November 2026, 400 users at USD 40, USD 16,000 a year "
          "(first order). Renewal 1 December 2026 to 30 November 2027, 400 users at USD 45, USD 18,000 "
          "a year (renewal). The renewal adds automatic renewal, 90 days notice, Customer only (renewal).",
}


def judge_reference(question: str, kind: str) -> str:
    """The question plus what our files hold for the vendors it names (all vendors if it names none)."""
    asked = sorted(vendor_numbers(question)) or sorted(VENDOR_DOCUMENTS)
    lines = [f"Question: {question}", "", "What our files hold:"]
    for number in asked:
        lines.append(f"- Vendor{number} documents: {VENDOR_DOCUMENTS[number]}.")
        if VENDOR_FACTS:
            lines.append(f"  Key facts: {VENDOR_FACTS[number]}")
    if kind == "decline":
        lines += ["", "Expected: our documents do not answer this question. An answer that says so is correct."]
    return "\n".join(lines)


def judge_case(case: dict) -> dict:
    """What the judge sees: input = question + reference; output = the oracle answer (known-good)."""
    return {"input": judge_reference(case["input"], case["kind"]), "output": case["output"]}


JUDGE_CASES = [judge_case(case) for case in CASES]

JUDGE_RUBRIC = """You check one answer about our vendor contracts for one failure: the answer says
something is missing, not found or not stated, but our files have it.

{input}

Answer to check:
{actual}

Score 0 if the answer says a document or a key fact is missing, not found or not
stated, and "What our files hold" above shows we have it. The search results are
not our files: "it wasn't in the search results" is a missing claim too.
Example of a 0: "The form refers to an underlying Agreement, and that Agreement
wasn't in the search results", when our files hold SYN-10-terms.md (master terms)
for Vendor10.

Score 0 also if the text is not an answer to the question, for example it only
repeats the question or says the turn limit was reached.

Score 1 otherwise. Example of a 1: "The Vendor03 online Terms of Service are not
in the results", when our files say those terms are not attached.
A missing claim about something "What our files hold" does not mention (a clause,
a signature, an invoice, a notice address) is not this failure: score 1.
If our documents are expected to have no answer to the question, an answer that
says so scores 1. Short answers, lists of facts and citations count as answers.
Wrong dates, other vendors, length and style do not matter here.

Reply with JSON only: {{"score": 0 or 1, "why": "<the false missing claim, or none>"}}"""

# Known-bad for calibrate(): the rank-1 mistake, false for all 13 questions (every vendor has an order form).
BAD_ANSWER = ("I didn't find any contract documents for this vendor in our files: no order form, "
              "no master agreement and no renewal order. Missing document: ask the vendor for the "
              "last signed copy of the contract.")


def make_judge() -> Judge:
    """The judge on a different model from the one that answers (JUDGE_MODEL in .env)."""
    if str(CHALLENGE) not in sys.path:
        sys.path.insert(0, str(CHALLENGE))
    import llm  # noqa: F401  loads the repo .env (key, LLM_MODEL, JUDGE_MODEL) into os.environ
    cfg = config.from_env(ROOT)
    judge_model = os.environ.get("JUDGE_MODEL", "")
    if not judge_model or judge_model == cfg.llm_model:
        raise SystemExit("Set JUDGE_MODEL in .env to a model other than LLM_MODEL.")
    return ReasonJudge(cfg, rubric=JUDGE_RUBRIC, model=judge_model)


class ReasonJudge(Judge):
    """The course Judge, plus the "why" of its last verdict (helpers/judge.py keeps only the score)."""
    last_why = ""

    def _ask(self, prompt: str) -> str:
        reply = super()._ask(prompt)
        parsed = parse_json(reply) or {}
        self.last_why = str(parsed.get("why", "(no why in the reply)"))
        return reply


JUDGE_WHYS = {}   # question -> the judge's why, for the run being judged

def judge_scorer(judge: Judge):
    """The judge as a harness scorer: (actual, case) -> 0 or 1. Keeps its why per question."""
    def score(actual, case):
        value = judge.score(actual, judge_case(case))
        JUDGE_WHYS[case["input"]] = getattr(judge, "last_why", "")
        return value
    return score


def save_full(report, path):
    """One JSON line per question: the whole answer, every score, and the judge's why when it ran."""
    rows = []
    for result in report.results:
        row = {"question": result.input,
               "answer": FULL_ANSWERS.get(result.input, result.actual),   # whole answer when the endpoint ran
               "scores": result.scores}
        if result.input in JUDGE_WHYS:
            row["judge_why"] = JUDGE_WHYS[result.input]
        rows.append(json.dumps(row, ensure_ascii=False))
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"  saved {len(rows)} answers to {path.relative_to(ROOT)}")


# human_scores.jsonl lines I label 0 for this judge, from my why notes:
# false missing claims (1, 2, 8, 14) and no answer (7). All other lines are 1.
FALSE_MISSING_ROWS = {1, 2, 7, 8, 14}

def agreement(judge: Judge) -> None:
    """The judge against my labels on the 20 hand-scored answers, with the chance floor."""
    by_question = {case["input"]: case for case in CASES}
    lines = (EVALS / "human_scores.jsonl").read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    agreed = 0
    for number, row in enumerate(rows, start=1):
        mine = 0 if number in FALSE_MISSING_ROWS else 1
        judged = round(judge.score(row["actual"], judge_case(by_question[row["input"]])))
        agreed += mine == judged
        if mine != judged:
            print(f"  row {number}: me {mine}, judge {judged}: {row['input'][:60]}  why: {getattr(judge, 'last_why', '')}")
    zeros = len(FALSE_MISSING_ROWS)
    floor = max(zeros, len(rows) - zeros) / len(rows)
    print(f"agreement {agreed}/{len(rows)} = {agreed / len(rows):.2f}, chance floor {floor:.2f}")

# --- Step 4: generated failures (synthetic.jsonl, written by make_synthetic.py) ---
# Natural counts per mode, from failures.md (49 traces read on 29 and 30 Oct).
NATURAL = {"rank 1 false missing claim": 7, "rank 2 other vendors": 5,
           "rank 3 date error": 4, "rank 4 no answer": 1}

def detection(scorers: dict) -> None:
    """Per failure mode and difficulty: how many broken answers each scorer caught (score below 1)."""
    by_question = {case["input"]: case for case in CASES}
    lines = (EVALS / "synthetic.jsonl").read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    names = list(scorers)
    table = {}                                      # (mode, difficulty) -> counts
    for row in rows:
        case = by_question[row["input"]]
        counts = table.setdefault((row["failure_mode"], row["difficulty"]),
                                  {"n": 0, **{name: 0 for name in names}})
        counts["n"] += 1
        for name, scorer in scorers.items():
            counts[name] += scorer(row["output"], case) < 1.0
    natural = ", ".join(f"{mode}: {count}" for mode, count in NATURAL.items())
    print(f"Natural: 17 failures in 49 traces ({natural}, plus 1 invented doubt in a drafted message). "
          f"Generated: {len(rows)}.")
    print("| Failure mode | Difficulty | n | " + " | ".join(names) + " |")
    print("| --- " * (3 + len(names)) + "|")
    for (mode, difficulty), counts in sorted(table.items()):
        cells = " | ".join(f"{counts[name]}/{counts['n']}" for name in names)
        print(f"| {mode} | {difficulty} | {counts['n']} | {cells} |")
    originals = {row["original"]: by_question[row["input"]] for row in rows}
    alarms = {name: sum(SCORERS[name](text, case) < 1.0 for text, case in originals.items())
              for name in SCORERS}
    print(f"False alarms on the {len(originals)} originals (answers I passed): "
          + ", ".join(f"{name} {count}" for name, count in alarms.items()))    

def show_failures(report):
    """Print each case where a scorer gave less than 1.0, so you can read it."""
    for result in report.results:
        failed = [name for name, score in result.scores.items() if score < 1.0]
        if failed:
            why = f"  why: {JUDGE_WHYS[result.input]}" if result.input in JUDGE_WHYS else ""
            print(f"  question {result.index + 1}: {result.input[:70]} -> failed: {', '.join(failed)}{why}")


if __name__ == "__main__":
    print(harness.run(CASES, echo, SCORERS, name="echo"))
    print(harness.run(CASES, oracle, SCORERS, name="oracle"))
    if "--endpoint" in sys.argv:                  # 13 model calls, a few minutes
        report = harness.run(CASES, endpoint, SCORERS, name="endpoint",
                             progress=lambda done, total: print(f"  {done}/{total}", flush=True))
        print(report)
        show_failures(report)
        harness.save(report, EVALS / "runs" / "endpoint-step2.json")   # the answers, to read later
        save_full(report, EVALS / "runs" / "endpoint-step2-full.jsonl")   # whole answers, no 2,000-character cut

    if "--judge" in sys.argv:                      # 52 judge calls; 72 with --agreement
        judge = make_judge()
        print(judge.calibrate(JUDGE_CASES, wrong_answer=BAD_ANSWER))
        for row in judge.calibration.detail:
            print("  ", row)
            
        if judge.calibration.passed:
            scorer = {"missing_claim_judge": judge_scorer(judge)}
            print(harness.run(CASES, echo, scorer, name="judge-echo"))
            JUDGE_WHYS.clear()                         # whys from the oracle run only
            report = harness.run(CASES, oracle, scorer, name="judge-oracle")
            print(report)
            show_failures(report)                  # an oracle answer the judge scored 0
            if "--agreement" in sys.argv:
                agreement(judge)
            if FULL_ANSWERS:                           # --endpoint ran too: judge the real answers (13 more judge calls)
                JUDGE_WHYS.clear()
                report = harness.run(CASES, lambda question: FULL_ANSWERS[question], scorer, name="judge-endpoint")
                print(report)
                show_failures(report)
                save_full(report, EVALS / "runs" / "judge-endpoint-full.jsonl")

    if "--synthetic" in sys.argv:                  # free; with --judge: +14 judge calls
        scorers = dict(SCORERS)
        if "--judge" in sys.argv and judge.calibration.passed:
            scorers["missing_claim_judge"] = judge_scorer(judge)
        detection(scorers)            