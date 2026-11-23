"""Leakage test (TC7 Chunk 8): a contract's record never shows another contract's facts.

The boundary tested here is the contracts and owners: get_contract_record for one contract
must return that contract's record for given owner and nothing from any other. No model call.

Needs the seeded memory (10 live records). Run from the repo root:
    uv run python 01_Product_Engineering/challenge/seed_memory.py
    uv run --group dev python -m pytest use_case/evals/test_leakage.py -q
"""
import re
import sys
from pathlib import Path



def visible(viewer):
    """The contract ids one viewer gets from memory."""
    return {record["contract_id"] for record in memory.records_for(memory.connect(), viewer)}

def contracts_of(owner):
    """The contract ids OWNERS gives this owner."""
    return {contract for contract, who in OWNERS.items() if who == owner}

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "01_Product_Engineering" / "challenge"))
import retrieval                                    # get_contract_record lives here
import memory
from seed_memory import OWNERS      # the owners you assigned in 8-2b: the test reads them, never retypes them

CONTRACT_IN_TEXT = re.compile(r"SYN-(\d{2})")          # every contract id the record text mentions


def contracts_shown(text):
    """The contract numbers a tool result mentions, for example {"04"}."""
    return set(CONTRACT_IN_TEXT.findall(text))


def test_each_record_shows_only_its_contract():
    for number in range(1, 11):
        vendor = f"Vendor{number:02d}"
        text = retrieval.get_contract_record(vendor)
        assert contracts_shown(text) == {f"{number:02d}"}, f"Vendor{number:02d} shows wrong contracts: {contracts_shown(text)}"


# ways the model might name a contract, each with the contract number
# it must lead to, or None when it must find no record. At least one that names a
# vendor but also contains another number.
HOW_THE_MODEL_ASKS = [
    ("Vendor04", "04"),
    ("SYN-04", "04"),
    ("Vendor 4", "04"),
    ("contract 2 of Vendor04", "04"),
    ("Acme", None)
]

def test_other_wordings_do_not_cross():
    for asked, expected in HOW_THE_MODEL_ASKS:
        shown = contracts_shown(retrieval.get_contract_record(asked))
        wanted = {expected} if expected else set()
        assert shown == wanted, f"{asked!r}: expected {wanted or 'no record'}, got {shown or 'no record'}"

def test_two_owners_do_not_see_each_other():
    for owner in sorted(set(OWNERS.values())):
        seen = visible(owner)
        wanted = contracts_of(owner)
        assert seen == wanted, f"{owner} sees wrong contracts: {seen}, expected {wanted}"

def test_see_all_groups_see_everything():
    for group in memory.SEE_ALL:
        assert visible(group) == set(OWNERS.keys()), f"{group} sees wrong contracts: {visible(group)}"

def test_unknown_viewer_sees_nothing():
    assert visible("nobody") == set(), f"unknown viewer sees contracts: {visible('nobody')}"
    assert visible("") == set(), f"empty viewer sees contracts: {visible('')}"

def test_owner_tools_do_not_reach_other_contracts():
    """An owner's tools return nothing from a contract that is not theirs."""
    owner = "owner 1"
    other_contract = next(contract for contract, who in OWNERS.items() if who != owner)
    other_vendor = "Vendor" + other_contract[4:6]          # "SYN-03" -> "Vendor03": the refusal repeats the input
    mine = {contract[4:6] for contract in contracts_of(owner)}   # {"01", "02", "07", "10"}
    funcs = retrieval.tools_for(owner)

    record = funcs["get_contract_record"](other_vendor)
    assert contracts_shown(record) == set(), f"{owner} sees {other_vendor}'s record: {record}"

    shown = contracts_shown(funcs["search_chunks"]("notice period"))
    assert shown and shown <= mine, f"{owner} search shows {shown}, owns {mine}"   # empty fails too

    shown = contracts_shown(funcs["search_chunks"]("notice period", vendor=other_vendor))
    assert shown == set(), f"{owner} sees {other_vendor} in search: {shown}"