"""TC7 Step 4c: fill the memory with the 10 synthetic contracts from truth.jsonl.

truth.jsonl holds the values read by hand from the synthetic documents, with the
file and section each value came from. No model reads anything here.

Run from the repo root:
    uv run python 01_Product_Engineering/challenge/seed_memory.py
Safe to run again: it deletes the memory file first and starts fresh.
"""
import json

import memory

TRUTH = memory.ROOT / "use_case" / "data" / "contracts" / "truth.jsonl"

# truth.jsonl says "auto", "manual" or null (None in Python).
RENEWAL_WORDS = {"auto": "yes", "manual": "no", None: "not found"}

# record column -> field name in truth.jsonl
FROM_TRUTH = {
    "start_date": "start_date",
    "end_date": "end_date",
    "auto_renewal": "renewal_type",
    "notice_days": "notice_days",
    "total_contract_value": "total_contract_value",
    "annual_contract_value": "annual_contract_value",
}

# A computed value keeps the trail of what it was computed from (found Nov 21, Chunk 6):
# with only "computed" as its source, the agent had nothing to cite, so it searched the
# document and redid the date math itself. Code computes; the record says from what.
# record column -> the truth.jsonl fields it is computed from
COMPUTED_FROM = {
    "end_date": ["start_date", "term_months"],
    "annual_contract_value": ["total_contract_value", "term_months"],
    "total_contract_value": ["annual_contract_value", "term_months"]
}

# Synthetic owners (roles, never names): who manages which contract (TC7 Chunk 8).
# YOU (blank 22): assign all 10 contracts. Give at least one owner several contracts,
# so "all my contracts" returns more than one, and use at least 3 owners.
OWNERS = {
    "SYN-01": "owner 1",
    "SYN-02": "owner 1",
    "SYN-03": "owner 2",
    "SYN-04": "owner 2",
    "SYN-05": "owner 3",
    "SYN-06": "owner 3",
    "SYN-07": "owner 1",
    "SYN-08": "owner 2",
    "SYN-09": "owner 3",
    "SYN-10": "owner 1"
}

def to_record(row):
    """One truth.jsonl line -> (record, sources), ready for memory.save_record."""
    fields = row["fields"]
    record = {
        "contract_id": row["contract_id"],
        "vendor": row["vendor"],
        "product": None,               # not in truth.jsonl; filled later from the documents
        "owner": OWNERS[row["contract_id"]],     # a missing contract fails loudly (KeyError)
    }
    sources = {}
    for column, name in FROM_TRUTH.items():
        field = fields.get(name) or {}
        record[column] = field.get("value")
        source = field.get("source")
        if source == "computed":
            if column not in COMPUTED_FROM:
                raise ValueError(
                    f"{row['contract_id']}: {column} is computed, but COMPUTED_FROM "
                    f"does not say from what; add it there")
            sections = []
            for name in COMPUTED_FROM[column]:
                section = (fields.get(name) or {}).get("source") or ""
                if section.startswith("SYN-") and section not in sections:
                    sections.append(section)           # the same section twice is cited once
            source = "computed from " + " + ".join(sections)
        if source:
            sources[column] = source
    word = record["auto_renewal"]
    if word not in RENEWAL_WORDS:
        raise ValueError(
            f"{row['contract_id']}: unknown renewal word {word!r} in truth.jsonl; "
            f"add it to RENEWAL_WORDS")
    record["auto_renewal"] = RENEWAL_WORDS[word]
    return record, sources


def main():
    if memory.DB_PATH.exists():
        memory.DB_PATH.unlink()        # delete the old memory file: start fresh
    conn = memory.connect()
    with open(TRUTH) as f:
        for line in f:
            record, sources = to_record(json.loads(line))
            memory.save_record(conn, record, sources)

    rows = conn.execute(
        "SELECT contract_id, end_date, auto_renewal, notice_days, annual_contract_value "
        "FROM live_records ORDER BY contract_id").fetchall()
    for row in rows:
        print(dict(row))
    print(len(rows), "live records")


if __name__ == "__main__":
    main()