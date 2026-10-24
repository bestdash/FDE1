"""Generate the TC3 synthetic contract corpus from a truth table.

Truth first, text second: every value in CONTRACTS is the correct answer, so
the same table is the gold for Stage 1 extraction and for retrieval labels.
Everything is invented: vendors, prices, dates. No real contract is used.
The document structure follows my own outline of 5 expired contract sets
(kept locally, not in this repo).

Run from this folder:
    uv run python make_contracts.py            # generate missing files, then check
    uv run python make_contracts.py --force    # regenerate every file, then check
    uv run python make_contracts.py --check    # only check the files on disk

Writes to use_case/data/contracts/ (gitignored): one Markdown file per
document, index.md (one line per page, for list/grep/read) and truth.jsonl.
Read-only towards everything else: it only creates files in that folder.
"""

import argparse
import calendar
import json
import os
import re
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "use_case" / "data" / "contracts"
CUSTOMER = "Customer Co"

ORDER = ["Parties", "Order Summary", "Subscription Term", "Products and Fees",
         "Payment Terms", "Terms", "Signatures"]
TERMS = ["1. Definitions", "2. Services", "3. Fees and Payment", "4. Support",
         "5. Confidentiality", "6. Warranties", "7. Limitation of Liability",
         "8. Term and Termination", "9. Notices", "10. General"]
RENEWAL = ["Parties", "Renewal Summary", "Renewal Term", "Products and Fees",
           "Payment Terms", "Purchase Terms", "Signatures"]

# Phrases that would leak renewal terms into a contract whose truth is "not found".
NO_RENEWAL = ["renew automatically", "renews automatically", "automatic renewal",
              "auto-renew", "notice of non-renewal", "days' notice", "days notice",
              "days before the end", "days prior"]

# Each fact: (section, sentence to include, strings that must appear in that section).
# Each truth field: (value, document key, section), or None when the documents do
# not state it (then it is computed by code, or "not found").
CONTRACTS = [
    {
        "id": "SYN-01", "vendor": "Vendor01 Software Inc.", "complexity": "simple",
        "case": "baseline, auto-renewal",
        "docs": {
            "order": {"title": "Order Form", "headings": ORDER, "forbid": [], "facts": [
                ("Subscription Term", "The subscription term starts on 1 January 2026 and ends on 31 December 2026 (12 months).", ["1 January 2026", "31 December 2026"]),
                ("Products and Fees", "200 user licences at USD 120 per user per year, standard support included. Annual fee: USD 24,000.", ["200", "USD 120", "24,000"]),
                ("Terms", "This order is governed by the Master Subscription Agreement between the parties.", ["Master Subscription Agreement"]),
            ]},
            "terms": {"title": "Master Subscription Agreement", "headings": TERMS, "forbid": [], "facts": [
                ("8. Term and Termination", "Each order renews automatically for a period equal to its current term unless either party gives written notice of non-renewal at least 90 days before the end of the current term.", ["automatically", "90 days"]),
            ]},
        },
        "truth": {
            "start_date": ("2026-01-01", "order", "Subscription Term"),
            "term_months": (12, "order", "Subscription Term"),
            "end_date": ("2026-12-31", "order", "Subscription Term"),
            "renewal_type": ("auto", "terms", "8. Term and Termination"),
            "notice_days": (90, "terms", "8. Term and Termination"),
            "annual_contract_value": (24000, "order", "Products and Fees"),
            "total_contract_value": None,
            "pricing_model": ("user-based", "order", "Products and Fees"),
            "price_per_user": (120, "order", "Products and Fees"),
            "features": (["200 users", "standard support"], "order", "Products and Fees"),
        },
    },
    {
        "id": "SYN-02", "vendor": "Vendor02 Cloud Ltd.", "complexity": "complex",
        "case": "end date not stated: start + term",
        "docs": {
            "order": {"title": "Order Form", "headings": ORDER,
                      "forbid": ["28 February 2029", "ends on", "end date"], "facts": [
                ("Subscription Term", "The subscription term starts on 1 March 2026 and runs for 36 months.", ["1 March 2026", "36 months"]),
                ("Products and Fees", "Platform package including SSO, AI credits (50,000 per year) and unlimited projects. Total fee for the 36-month term: USD 90,000.", ["SSO", "AI credits", "90,000"]),
                ("Terms", "This order is governed by the Master Services Agreement between the parties.", ["Master Services Agreement"]),
            ]},
            "terms": {"title": "Master Services Agreement", "headings": TERMS, "forbid": ["renews automatically"], "facts": [
                ("8. Term and Termination", "A subscription may be renewed only by a new written agreement signed by both parties. Either party may give written notice of non-renewal at least 30 days before the end of the term.", ["written agreement", "30 days"]),
            ]},
        },
        "truth": {
            "start_date": ("2026-03-01", "order", "Subscription Term"),
            "term_months": (36, "order", "Subscription Term"),
            "end_date": None,
            "renewal_type": ("manual", "terms", "8. Term and Termination"),
            "notice_days": (30, "terms", "8. Term and Termination"),
            "annual_contract_value": None,
            "total_contract_value": (90000, "order", "Products and Fees"),
            "pricing_model": ("package", "order", "Products and Fees"),
            "price_per_user": None,
            "features": (["SSO", "AI credits: 50,000 per year", "unlimited projects"], "order", "Products and Fees"),
        },
    },
    {
        "id": "SYN-03", "vendor": "Vendor03 Analytics Inc.", "complexity": "simple",
        "case": "main terms referenced, not attached: renewal and notice not found",
        "docs": {
            "order": {"title": "Order Form", "headings": ORDER, "forbid": NO_RENEWAL, "facts": [
                ("Subscription Term", "The subscription term starts on 1 February 2026 and ends on 31 January 2027.", ["1 February 2026", "31 January 2027"]),
                ("Products and Fees", "300 user licences at USD 60 per user per year. Annual fee: USD 18,000.", ["300", "USD 60", "18,000"]),
                ("Terms", "This order is governed by the Vendor's online Terms of Service, as updated from time to time. They are not attached to this order form.", ["Terms of Service"]),
            ]},
        },
        "truth": {
            "start_date": ("2026-02-01", "order", "Subscription Term"),
            "term_months": (12, "order", "Subscription Term"),
            "end_date": ("2027-01-31", "order", "Subscription Term"),
            "renewal_type": None,
            "notice_days": None,
            "annual_contract_value": (18000, "order", "Products and Fees"),
            "total_contract_value": None,
            "pricing_model": ("user-based", "order", "Products and Fees"),
            "price_per_user": (60, "order", "Products and Fees"),
            "features": (["300 users"], "order", "Products and Fees"),
        },
    },
    {
        "id": "SYN-04", "vendor": "Vendor04 Security Ltd.", "complexity": "complex",
        "case": "order form overrides main terms: notice 90, not 60",
        "docs": {
            "order": {"title": "Order Form", "headings": ORDER, "forbid": [], "facts": [
                ("Subscription Term", "The subscription term starts on 1 April 2026 and ends on 31 March 2027 (12 months).", ["1 April 2026", "31 March 2027"]),
                ("Products and Fees", "Business package with SSO, a security add-on and premium support. Annual fee: USD 40,000.", ["SSO", "security add-on", "40,000"]),
                ("Terms", "If this order form and the Master Subscription Agreement conflict, this order form prevails. Notwithstanding the Agreement, notice of non-renewal must be given at least 90 days before the end of the current term.", ["prevails", "90 days"]),
            ]},
            "terms": {"title": "Master Subscription Agreement", "headings": TERMS, "forbid": [], "facts": [
                ("8. Term and Termination", "Each subscription renews automatically for successive 12-month periods unless either party gives written notice of non-renewal at least 60 days before the end of the current term.", ["automatically", "60 days"]),
            ]},
        },
        "truth": {
            "start_date": ("2026-04-01", "order", "Subscription Term"),
            "term_months": (12, "order", "Subscription Term"),
            "end_date": ("2027-03-31", "order", "Subscription Term"),
            "renewal_type": ("auto", "terms", "8. Term and Termination"),
            "notice_days": (90, "order", "Terms"),
            "annual_contract_value": (40000, "order", "Products and Fees"),
            "total_contract_value": None,
            "pricing_model": ("package", "order", "Products and Fees"),
            "price_per_user": None,
            "features": (["SSO", "security add-on", "premium support"], "order", "Products and Fees"),
        },
    },
    {
        "id": "SYN-05", "vendor": "Vendor05 Collaboration Inc.", "complexity": "complex",
        "case": "renewal order replaces the first order: new term, price up, bundle added",
        "docs": {
            "order": {"title": "Order Form", "headings": ORDER, "forbid": [], "facts": [
                ("Subscription Term", "The subscription term starts on 1 July 2025 and ends on 30 June 2026 (12 months).", ["1 July 2025", "30 June 2026"]),
                ("Products and Fees", "150 user licences at USD 100 per user per year. Annual fee: USD 15,000.", ["150", "USD 100", "15,000"]),
                ("Terms", "This order is governed by the Master Subscription Agreement between the parties.", ["Master Subscription Agreement"]),
            ]},
            "terms": {"title": "Master Subscription Agreement", "headings": TERMS, "forbid": [], "facts": [
                ("8. Term and Termination", "Each order renews automatically for a period equal to its current term unless either party gives written notice of non-renewal at least 90 days before the end of the current term.", ["automatically", "90 days"]),
            ]},
            "renewal": {"title": "Renewal Order Form", "headings": RENEWAL, "forbid": [], "facts": [
                ("Renewal Term", "The renewal term starts on 1 July 2026 and ends on 30 June 2028 (24 months). This renewal order replaces the previous order form for this period.", ["1 July 2026", "30 June 2028", "replaces"]),
                ("Products and Fees", "150 user licences at USD 110 per user per year, with an AI assistant bundle included at no extra charge. Annual fee: USD 16,500. Total for the 24-month term: USD 33,000.", ["USD 110", "AI assistant", "16,500", "33,000"]),
                ("Purchase Terms", "All other terms of the Master Subscription Agreement continue to apply.", ["Master Subscription Agreement"]),
            ]},
        },
        "truth": {
            "start_date": ("2026-07-01", "renewal", "Renewal Term"),
            "term_months": (24, "renewal", "Renewal Term"),
            "end_date": ("2028-06-30", "renewal", "Renewal Term"),
            "renewal_type": ("auto", "terms", "8. Term and Termination"),
            "notice_days": (90, "terms", "8. Term and Termination"),
            "annual_contract_value": (16500, "renewal", "Products and Fees"),
            "total_contract_value": (33000, "renewal", "Products and Fees"),
            "pricing_model": ("user-based", "renewal", "Products and Fees"),
            "price_per_user": (110, "renewal", "Products and Fees"),
            "features": (["150 users", "AI assistant bundle"], "renewal", "Products and Fees"),
        },
    },
    {
        "id": "SYN-06", "vendor": "Vendor06 Learning Ltd.", "complexity": "very complex",
        "case": "free tier for customers plus paid overage; no auto-renewal stated in the order",
        "docs": {
            "order": {"title": "Order Form", "headings": ORDER, "forbid": [], "facts": [
                ("Subscription Term", "The subscription term starts on 1 September 2026 and ends on 31 August 2028 (24 months).", ["1 September 2026", "31 August 2028"]),
                ("Products and Fees", "Learning platform package: up to 3,500 learner seats for the Customer's own customers and partners, included in the package; additional learner seats at USD 1.50 per seat per month; SSO included. Total fee for the 24-month term: USD 50,000.", ["3,500", "USD 1.50", "SSO", "50,000"]),
                ("Terms", "This subscription does not renew automatically. Any renewal requires a new order form signed by both parties. Either party may give notice of non-renewal at least 30 days before the end date. All other terms are the Vendor's online terms.", ["does not renew automatically", "30 days"]),
            ]},
        },
        "truth": {
            "start_date": ("2026-09-01", "order", "Subscription Term"),
            "term_months": (24, "order", "Subscription Term"),
            "end_date": ("2028-08-31", "order", "Subscription Term"),
            "renewal_type": ("manual", "order", "Terms"),
            "notice_days": (30, "order", "Terms"),
            "annual_contract_value": None,
            "total_contract_value": (50000, "order", "Products and Fees"),
            "pricing_model": ("package", "order", "Products and Fees"),
            "price_per_user": None,
            "features": (["3,500 learner seats for customers and partners", "additional seats at USD 1.50 per seat per month", "SSO"], "order", "Products and Fees"),
        },
    },
    {
        "id": "SYN-07", "vendor": "Vendor07 Systems Inc.", "complexity": "complex",
        "case": "user-based with add-ons: annual fee / users is not the price per user",
        "docs": {
            "order": {"title": "Order Form", "headings": ORDER, "forbid": [], "facts": [
                ("Subscription Term", "The subscription term starts on 15 January 2026 and ends on 14 January 2027 (12 months).", ["15 January 2026", "14 January 2027"]),
                ("Products and Fees", "250 user licences at USD 80 per user per year (USD 20,000); security add-on USD 5,000 per year; support SLA add-on USD 5,000 per year. Total annual fee: USD 30,000.", ["250", "USD 80", "security add-on", "support SLA", "30,000"]),
                ("Terms", "This order is governed by the Master Subscription Agreement between the parties.", ["Master Subscription Agreement"]),
            ]},
            "terms": {"title": "Master Subscription Agreement", "headings": TERMS, "forbid": [], "facts": [
                ("8. Term and Termination", "Each subscription renews automatically for a further 12 months unless either party gives written notice of non-renewal at least 30 days before the end of the current term.", ["automatically", "30 days"]),
            ]},
        },
        "truth": {
            "start_date": ("2026-01-15", "order", "Subscription Term"),
            "term_months": (12, "order", "Subscription Term"),
            "end_date": ("2027-01-14", "order", "Subscription Term"),
            "renewal_type": ("auto", "terms", "8. Term and Termination"),
            "notice_days": (30, "terms", "8. Term and Termination"),
            "annual_contract_value": (30000, "order", "Products and Fees"),
            "total_contract_value": None,
            "pricing_model": ("user-based", "order", "Products and Fees"),
            "price_per_user": (80, "order", "Products and Fees"),
            "features": (["250 users", "security add-on", "support SLA add-on"], "order", "Products and Fees"),
        },
    },
    {
        # Very complex because several divisions must approve: internal knowledge the
        # owner has, never written in a vendor contract (owner review, Oct 24).
        "id": "SYN-08", "vendor": "Vendor08 Media Ltd.", "complexity": "very complex",
        "case": "silent: terms online, not attached; end date not stated",
        "docs": {
            "order": {"title": "Service Order", "headings": ORDER,
                      "forbid": NO_RENEWAL + ["31 October 2028", "ends on", "end date"], "facts": [
                ("Subscription Term", "The services start on 1 November 2025 and continue for 36 months.", ["1 November 2025", "36 months"]),
                ("Products and Fees", "Enterprise package: SSO, AI credits (100,000 per year) and priority support. Total fee for the 36-month term: USD 120,000.", ["SSO", "AI credits", "120,000"]),
                ("Terms", "This order is governed by the Vendor's standard terms published online. They are not attached to this order.", ["standard terms"]),
            ]},
        },
        "truth": {
            "start_date": ("2025-11-01", "order", "Subscription Term"),
            "term_months": (36, "order", "Subscription Term"),
            "end_date": None,
            "renewal_type": None,
            "notice_days": None,
            "annual_contract_value": None,
            "total_contract_value": (120000, "order", "Products and Fees"),
            "pricing_model": ("package", "order", "Products and Fees"),
            "price_per_user": None,
            "features": (["SSO", "AI credits: 100,000 per year", "priority support"], "order", "Products and Fees"),
        },
    },
    {
        "id": "SYN-09", "vendor": "Vendor09 Storage Inc.", "complexity": "simple",
        "case": "baseline, no auto-renewal",
        "docs": {
            "order": {"title": "Order Form", "headings": ORDER, "forbid": [], "facts": [
                ("Subscription Term", "The subscription term starts on 1 May 2026 and ends on 30 April 2027 (12 months).", ["1 May 2026", "30 April 2027"]),
                ("Products and Fees", "Storage package: 5 TB of storage and standard support. Annual fee: USD 12,000.", ["5 TB", "12,000"]),
                ("Terms", "This order is governed by the Master Subscription Agreement between the parties.", ["Master Subscription Agreement"]),
            ]},
            "terms": {"title": "Master Subscription Agreement", "headings": TERMS, "forbid": ["renews automatically"], "facts": [
                ("8. Term and Termination", "A subscription ends at the end of its term and does not renew automatically. Either party may give written notice of non-renewal at least 60 days before the end of the term.", ["does not renew automatically", "60 days"]),
            ]},
        },
        "truth": {
            "start_date": ("2026-05-01", "order", "Subscription Term"),
            "term_months": (12, "order", "Subscription Term"),
            "end_date": ("2027-04-30", "order", "Subscription Term"),
            "renewal_type": ("manual", "terms", "8. Term and Termination"),
            "notice_days": (60, "terms", "8. Term and Termination"),
            "annual_contract_value": (12000, "order", "Products and Fees"),
            "total_contract_value": None,
            "pricing_model": ("package", "order", "Products and Fees"),
            "price_per_user": None,
            "features": (["5 TB storage", "standard support"], "order", "Products and Fees"),
        },
    },
    {
        "id": "SYN-10", "vendor": "Vendor10 Design Ltd.", "complexity": "complex",
        "case": "first terms silent; renewal order adds auto-renewal (customer-only notice); 30-day cure period as a distractor",
        "docs": {
            "order": {"title": "Order Form", "headings": ORDER, "forbid": [], "facts": [
                ("Subscription Term", "The subscription term starts on 1 December 2025 and ends on 30 November 2026 (12 months).", ["1 December 2025", "30 November 2026"]),
                ("Products and Fees", "400 user licences at USD 40 per user per year, with an introductory discount. Annual fee: USD 16,000.", ["400", "USD 40", "16,000"]),
                ("Terms", "This order is governed by the Master Subscription Agreement between the parties.", ["Master Subscription Agreement"]),
            ]},
            "terms": {"title": "Master Subscription Agreement", "headings": TERMS,
                      "forbid": ["renews automatically", "renew automatically", "non-renewal"], "facts": [
                ("8. Term and Termination", "This Agreement continues while any order is in effect. Either party may terminate for material breach that is not cured within 30 days of written notice.", ["material breach", "30 days"]),
            ]},
            "renewal": {"title": "Renewal Order Form", "headings": RENEWAL, "forbid": [], "facts": [
                ("Renewal Term", "The renewal term starts on 1 December 2026 and ends on 30 November 2027 (12 months).", ["1 December 2026", "30 November 2027"]),
                ("Products and Fees", "400 user licences at USD 45 per user per year. The introductory discount no longer applies. Annual fee: USD 18,000.", ["USD 45", "18,000"]),
                ("Purchase Terms", "This subscription renews automatically for successive 12-month periods unless the Customer gives written notice of non-renewal at least 90 days before the end of the current term.", ["automatically", "90 days"]),
            ]},
        },
        "truth": {
            "start_date": ("2026-12-01", "renewal", "Renewal Term"),
            "term_months": (12, "renewal", "Renewal Term"),
            "end_date": ("2027-11-30", "renewal", "Renewal Term"),
            "renewal_type": ("auto", "renewal", "Purchase Terms"),
            "notice_days": (90, "renewal", "Purchase Terms"),
            "annual_contract_value": (18000, "renewal", "Products and Fees"),
            "total_contract_value": None,
            "pricing_model": ("user-based", "renewal", "Products and Fees"),
            "price_per_user": (45, "renewal", "Products and Fees"),
            "features": (["400 users"], "renewal", "Products and Fees"),
        },
    },
]


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


def file_name(contract_id: str, doc_key: str) -> str:
    return f"{contract_id}-{doc_key}.md"


def build_prompt(c: dict, doc: dict) -> str:
    headings = "\n".join(f"## {h}" for h in doc["headings"])
    facts = "\n".join(f"- In \"{s}\": {text}" for s, text, _ in doc["facts"])
    return f"""You write one synthetic contract document for a software test set. Everything is invented.

Document: {doc['title']} between {c['vendor']} (the Vendor) and {CUSTOMER} (the Customer).

Write it in Markdown. The first line is "# {doc['title']}". Then use exactly these
section headings, in this order, each on its own line:
{headings}

Put each fact below in the section named, in natural contract language.
Keep every date, number and amount exactly as written:
{facts}

Rules:
- Fill every other section with 2 to 5 short, realistic, generic clauses.
- Do not add any other date, duration, notice period, renewal rule, price or quantity.
  Exception: "Payment Terms" may say invoices are due within 30 or 45 days.
- No real company, product or person names. Use only the names given above.
- "Signatures": signature lines with role titles only (for example "Authorised signatory"), no names.
- No tables. Return only the document, no comments around it."""


def generate(prompt: str) -> str:
    import llm  # imported here so --check runs without an API key
    text = ""
    for text in llm.stream_reply(prompt):  # each value is the text so far
        pass
    text = text.strip()
    text = re.sub(r"^```[a-z]*\n|\n```$", "", text)  # drop a code fence if the model adds one
    return text.strip() + "\n"


def sections(md: str) -> dict[str, str]:
    """Map each '## heading' to the text under it."""
    out, current = {}, None
    for line in md.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            out[current] = ""
        elif current is not None:
            out[current] += line + "\n"
    return out


def check(md: str, doc: dict) -> list[str]:
    """Problems found in one generated document. An empty list means it passed."""
    problems = []
    found = sections(md)
    if list(found) != doc["headings"]:
        problems.append(f"headings differ: {list(found)}")
    for section, _, must in doc["facts"]:
        for s in must:
            if s.lower() not in found.get(section, "").lower():
                problems.append(f"'{s}' missing in '{section}'")
    for s in doc["forbid"]:
        if s.lower() in md.lower():
            problems.append(f"forbidden '{s}' present")
    return problems


def add_months(d: date, months: int) -> date:
    y, m = divmod(d.month - 1 + months, 12)
    year, month = d.year + y, m + 1
    return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


def truth_record(c: dict) -> dict:
    """Gold answer for Stage 1: each field with its source, 'computed' or 'not found'."""
    t = c["truth"]
    fields = {}
    for name, item in t.items():
        if item is None:
            fields[name] = {"value": None, "source": "not found"}
        else:
            value, doc_key, section = item
            fields[name] = {"value": value, "source": f"{file_name(c['id'], doc_key)}#{section}"}

    if t["price_per_user"] is None and t["pricing_model"][0] == "package":
        fields["price_per_user"]["source"] = "not applicable"

    start = date.fromisoformat(t["start_date"][0])
    term = t["term_months"][0]
    if t["end_date"] is None:
        end = add_months(start, term) - timedelta(days=1)
        fields["end_date"] = {"value": end.isoformat(), "source": "computed"}
    end = date.fromisoformat(fields["end_date"]["value"])

    years = term / 12
    if t["annual_contract_value"] is None:
        fields["annual_contract_value"] = {"value": round(t["total_contract_value"][0] / years), "source": "computed"}
    if t["total_contract_value"] is None:
        fields["total_contract_value"] = {"value": round(t["annual_contract_value"][0] * years), "source": "computed"}

    if t["renewal_type"] and t["renewal_type"][0] == "auto" and t["notice_days"]:
        autorenew = (end - timedelta(days=t["notice_days"][0])).isoformat()
    else:
        autorenew = None  # manual, or renewal terms not found
    fields["autorenew_date"] = {"value": autorenew, "source": "computed" if autorenew else "not applicable"}

    return {"contract_id": c["id"], "vendor": c["vendor"], "complexity": c["complexity"],
            "case": c["case"], "documents": [file_name(c["id"], k) for k in c["docs"]],
            "fields": fields}


def write_index(rows: list[tuple[str, str, str, str, list[str]]]) -> None:
    lines = ["# Contract corpus index", "",
             "One line per document. Synthetic data: every vendor, price and date is invented.", "",
             "| File | Contract | Document | Vendor | Sections |", "| --- | --- | --- | --- | --- |"]
    for f, cid, title, vendor, heads in rows:
        lines.append(f"| `{f}` | {cid} | {title} | {vendor} | {'; '.join(heads)} |")
    (OUT / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="regenerate every file")
    parser.add_argument("--check", action="store_true", help="only check files on disk")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    if not args.check:
        load_env()

    failures, index_rows = 0, []
    for c in CONTRACTS:
        for key, doc in c["docs"].items():
            path = OUT / file_name(c["id"], key)
            if not args.check and (args.force or not path.exists()):
                for attempt in (1, 2):
                    md = generate(build_prompt(c, doc))
                    if not check(md, doc):
                        break
                    print(f"  retry {path.name} (attempt {attempt} failed)")
                path.write_text(md, encoding="utf-8")
            if not path.exists():
                print(f"MISSING {path.name}")
                failures += 1
                continue
            md = path.read_text(encoding="utf-8")
            problems = check(md, doc)
            failures += bool(problems)
            print(f"{'FAIL' if problems else 'ok  '} {path.name}" + "".join(f"\n       {p}" for p in problems))
            index_rows.append((path.name, c["id"], doc["title"], c["vendor"], list(sections(md))))

    write_index(index_rows)
    with (OUT / "truth.jsonl").open("w", encoding="utf-8") as f:
        for c in CONTRACTS:
            f.write(json.dumps(truth_record(c), ensure_ascii=False) + "\n")

    print(f"\n{len(index_rows)} documents, {failures} with problems. Wrote index.md and truth.jsonl to {OUT}")


if __name__ == "__main__":
    main()
