"""Step 4: break correct answers in named ways and write synthetic.jsonl.

The originals are answers I passed in human_scores.jsonl. Each edit makes one failure
from failures.md; the label is free because I know what I broke.
Run: python use_case/evals/make_synthetic.py
"""
import json
from pathlib import Path

EVALS = Path(__file__).resolve().parent

R1 = "rank 1 false missing claim"
R2 = "rank 2 other vendors"
R3 = "rank 3 date error"
R4 = "rank 4 no answer"

# row = line in human_scores.jsonl. "find" is replaced by "replace" (first match, or every
# match with "all"); "whole" replaces the whole answer.
EDITS = [
    {"id": "r1-easy-doc-phrase", "row": 18, "mode": R1, "difficulty": "easy",
     "find": "The signature block in the copy I found is blank",
     "replace": "I didn't find any Vendor02 master terms in the results. "
                "The signature block in the copy I found is blank"},
    {"id": "r1-easy-agreement", "row": 12, "mode": R1, "difficulty": "easy",
     "find": "- **Taxes:**",
     "replace": "- **Agreement:** The Vendor10 master agreement isn't in the results, "
                "so other fee terms may apply.\n- **Taxes:**"},
    {"id": "r1-hard-doc-new-words", "row": 17, "mode": R1, "difficulty": "hard",
     "find": "The stated per-user price is USD 80.",
     "replace": "The stated per-user price is USD 80. The Vendor07 master terms were not among the "
                "documents I could access, so I can't say whether they change this price."},
    {"id": "r1-hard-fact", "row": 13, "mode": R1, "difficulty": "hard",
     "find": "**Signatures:**",
     "replace": "The renewal order form doesn't state the number of licences or the fee.\n\n**Signatures:**"},
    {"id": "r2-easy-vendor-number", "row": 9, "mode": R2, "difficulty": "easy",
     "find": "I found no right to cancel for convenience in the middle of a term.",
     "replace": "I found no right to cancel for convenience in the middle of a term. "
                "Vendor07, by contrast, asks for only 30 days' notice."},
    {"id": "r2-easy-other-vendors", "row": 15, "mode": R2, "difficulty": "easy",
     "find": "The subscription does not renew automatically.",
     "replace": "Unlike some other vendors' terms, the subscription does not renew automatically."},
    {"id": "r2-hard-providers", "row": 19, "mode": R2, "difficulty": "hard",
     "find": "Don't assume those prices carry over to a renewal.",
     "replace": "Don't assume those prices carry over to a renewal. "
                "Other providers in our portfolio usually ask for 90 days' notice."},
    {"id": "r2-hard-vendor-7", "row": 11, "mode": R2, "difficulty": "hard",
     "find": "The fee excludes applicable taxes [SYN-10-order.md#Products and Fees].",
     "replace": "The fee excludes applicable taxes [SYN-10-order.md#Products and Fees]. "
                "That is less per user than the Vendor 7 contract."},
    {"id": "r3-easy-past-end", "row": 13, "mode": R3, "difficulty": "easy",
     "find": "currently ends on **30 June 2028**", "replace": "currently ends on **30 June 2026**"},
    {"id": "r3-easy-wrong-year", "row": 15, "mode": R3, "difficulty": "easy",
     "find": "28 February 2029", "replace": "28 February 2030", "all": True},
    {"id": "r3-hard-one-day-late", "row": 10, "mode": R3, "difficulty": "hard",
     "find": "31 December 2026", "replace": "1 January 2027", "all": True},
    {"id": "r3-hard-extra-wrong-date", "row": 13, "mode": R3, "difficulty": "hard",
     "find": "That date is my calculation, so please check it.",
     "replace": "That date is my calculation, so please check it. "
                "Send the notice by 15 April 2028 at the latest."},
    {"id": "r4-easy-turn-limit", "row": 20, "mode": R4, "difficulty": "easy",
     "whole": "(max turns reached)"},
    {"id": "r4-hard-polite-fallback", "row": 18, "mode": R4, "difficulty": "hard",
     "whole": "Sorry, I couldn't finish searching the contracts for this question. Please try again later."},
]


def build() -> list:
    lines = (EVALS / "human_scores.jsonl").read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    out = []
    for edit in EDITS:
        row = rows[edit["row"] - 1]
        assert row["pass"], f"{edit['id']}: line {edit['row']} is not an answer I passed"
        original = row["actual"]
        if "whole" in edit:
            broken = edit["whole"]
        else:
            assert edit["find"] in original, f"{edit['id']}: text to change not found"
            broken = original.replace(edit["find"], edit["replace"], -1 if edit.get("all") else 1)
        out.append({"id": edit["id"], "input": row["input"], "output": broken, "original": original,
                    "failure_mode": edit["mode"], "difficulty": edit["difficulty"],
                    "source_row": edit["row"]})
    return out


if __name__ == "__main__":
    synthetic = build()
    text = "\n".join(json.dumps(row, ensure_ascii=False) for row in synthetic) + "\n"
    (EVALS / "synthetic.jsonl").write_text(text, encoding="utf-8")
    print(f"wrote {len(synthetic)} lines to synthetic.jsonl")