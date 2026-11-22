"""Staleness test (TC7 Chunk 5): a new contract document replaces the old record.

SYN-10: the first order form ends 30 Nov 2026; the renewal order form moves the
term to 1 Dec 2026 to 30 Nov 2027. After both are saved, the record the agent
reads must be the renewal, and the first order must be kept as history.

Run from the repo root:
    uv run --group dev python -m pytest use_case/evals/test_staleness.py -q
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # the repo root, two folders up
sys.path.insert(0, str(ROOT / "01_Product_Engineering" / "challenge"))
import memory                                        # memory.py, found through the line above

# Values read by hand from the two SYN-10 documents.
FIRST_ORDER = {
    "contract_id": "SYN-10", "vendor": "Vendor10 Design Ltd.", "product": None,
    "owner": "contract owner", "start_date": "2025-12-01", "end_date": "2026-11-30",
    "auto_renewal": "not found", "notice_days": None,
    "total_contract_value": 16000, "annual_contract_value": 16000,
}
RENEWAL = {
    "contract_id": "SYN-10", "vendor": "Vendor10 Design Ltd.", "product": None,
    "owner": "contract owner", "start_date": "2026-12-01", "end_date": "2027-11-30",
    "auto_renewal": "yes", "notice_days": 90,
    "total_contract_value": 18000, "annual_contract_value": 18000,
}


def test_new_document_replaces_old_record(tmp_path):
    conn = memory.connect(tmp_path / "test.sqlite")   # a fresh file; the real one is not touched
    old_id = memory.save_record(conn, FIRST_ORDER, {"end_date": "SYN-10-order.md#Subscription Term"})
    new_id = memory.save_record(conn, RENEWAL, {"end_date": "SYN-10-renewal.md#Renewal Term"})

    live = memory.get_live_record(conn, "SYN-10")
    assert live["record_id"] == new_id
    assert live["end_date"] == "2027-11-30"

    old = conn.execute("SELECT live FROM records WHERE record_id = ?", (old_id,)).fetchone()
    # YOU (blank 5): the value of live the first order must have now.
    assert old["live"] == 0

    count = conn.execute(
        "SELECT COUNT(*) FROM records WHERE contract_id = ?", ("SYN-10",)).fetchone()[0]
    assert count == 2   # history is kept, not deleted