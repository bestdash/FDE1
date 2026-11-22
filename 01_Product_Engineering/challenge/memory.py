"""TC7 memory: the contract record (semantic memory) in one SQLite file.

Decisions (TC7 workbook, Steps 2b and 3): one live record per contract.
A new contract document creates a new record; the old one becomes history (live = 0).
A chat never overwrites a record field: what people say goes to notes.
"""
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if len(HERE.parents) > 1 else HERE
DB_PATH = Path(os.getenv("MEMORY_DB") or ROOT / "use_case" / "data" / "memory.sqlite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    record_id     INTEGER PRIMARY KEY,
    contract_id   TEXT NOT NULL,              -- "SYN-04"
    vendor        TEXT NOT NULL,
    product       TEXT,
    owner         TEXT,                       -- a role, a person's name in prod only
    start_date    TEXT NOT NULL,
    end_date      TEXT NOT NULL,
    auto_renewal  TEXT NOT NULL,              -- "yes", "no", "not found"
    notice_days   INTEGER,              -- number of days for notice
    total_contract_value   REAL NOT NULL,                 -- total amount of the contract
    annual_contract_value REAL NOT NULL,                 -- amount per year
    live          INTEGER NOT NULL DEFAULT 1, -- 1 = current, 0 = history
    validated_by  TEXT,                       -- owner role; empty until the owner approves
    validated_at  TEXT,
    written_at    TEXT NOT NULL
);

-- One live record per contract, enforced by SQLite itself.
CREATE UNIQUE INDEX IF NOT EXISTS one_live_record ON records (contract_id) WHERE live = 1;

CREATE TABLE IF NOT EXISTS sources (
    record_id  INTEGER NOT NULL REFERENCES records(record_id),
    field      TEXT NOT NULL,                 -- "end_date"
    source     TEXT NOT NULL,                 -- "SYN-04-order.md#Subscription Term"
    PRIMARY KEY (record_id, field)
);

CREATE TABLE IF NOT EXISTS notes (
    note_id      INTEGER PRIMARY KEY,
    contract_id  TEXT NOT NULL,
    text         TEXT NOT NULL,
    author_role  TEXT NOT NULL,
    written_at   TEXT NOT NULL
);

-- What the sponsor sees: one row per contract, live records only.
CREATE VIEW IF NOT EXISTS live_records AS
    SELECT * FROM records WHERE live = 1;
"""


def connect(path=DB_PATH):
    """Open the memory file (created if missing), with the tables in place."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn

# The fields a contract document gives. The order does not matter, but every name
# must be a column of the records table.
FACTS = ["contract_id", "vendor", "product", "owner",
         "start_date", "end_date", "auto_renewal", "notice_days",
         "total_contract_value", "annual_contract_value"]

RETIRE_OLD = True   # the staleness rule; set to False only for the break check (4b-4)


def now():
    """The time now, in UTC, as text: "2026-11-23T09:30:00+00:00"."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save_record(conn, record, sources):
    """Save the record read from a new contract document. Returns its record_id.

    record: a dict with the FACTS names as keys.
    sources: a dict, field name -> where it was read ("SYN-10-renewal.md#Renewal Term").
    The new record is live and not yet confirmed (validated_by stays empty).
    """
    with conn:   # one transaction: everything below is saved, or nothing
        if RETIRE_OLD:
            # The staleness rule: the current record of this contract becomes history.           
            conn.execute(
                "UPDATE records SET live = 0 WHERE contract_id = ? AND live = 1",
                (record["contract_id"],))
        columns = FACTS + ["written_at"]
        values = [record.get(name) for name in FACTS] + [now()]
        marks = ", ".join("?" for _ in columns)
        cur = conn.execute(
            f"INSERT INTO records ({', '.join(columns)}) VALUES ({marks})", values)
        record_id = cur.lastrowid
        for field, source in sources.items():
            conn.execute(
                "INSERT INTO sources (record_id, field, source) VALUES (?, ?, ?)",
                (record_id, field, source))
    return record_id


def get_live_record(conn, contract_id):
    """The current record of one contract, as a dict, or None if there is none."""
    row = conn.execute(
        "SELECT * FROM live_records WHERE contract_id = ?", (contract_id,)).fetchone()
    return dict(row) if row else None

if __name__ == "__main__":
    conn = connect()
    names = [row["name"] for row in conn.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type IN ('table', 'index', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    print(DB_PATH)
    print(names)