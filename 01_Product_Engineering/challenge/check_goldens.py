"""Check the app against the goldens in use_case/evals/golden.jsonl.

One stage per build step, so each piece is tested on its own:

  uv run python check_goldens.py rules                  8a: route_request(), no model call, free
  uv run python check_goldens.py solve 1 4              8b: solve() on goldens 1 and 4, calls the model,
                                                        writes goldens_report.md
  uv run python check_goldens.py endpoint NAME 1 3 4    8c and Step 9: the running app on localhost:7860

With no golden numbers, every line is checked. This is a test tool: it only
reads files and calls your own app, it never writes anything.
"""

import json
import sys
from datetime import date
from pathlib import Path

# challenge/ -> 01_Product_Engineering/ -> repository root
GOLDEN = Path(__file__).resolve().parents[2] / "use_case" / "evals" / "golden.jsonl"
APP_URL = "http://localhost:7860"
REPORT = Path(__file__).resolve().parent / "goldens_report.md"

# Who sends and who receives each message_type, so the report reads like Outlook.
SENDER_TO = {
    "termination_draft": ("[Owner]", "[Vendor contact]"),
    "escalation_to_procurement": ("Contract agent", "Procurement team"),
}
DEFAULT_SENDER_TO = ("Contract agent", "[Owner]")


def load_goldens(wanted: list[int]) -> list[tuple[int, dict]]:
    goldens = []
    with GOLDEN.open(encoding="utf-8") as f:
        for number, line in enumerate(f, start=1):
            if line.strip() and (not wanted or number in wanted):
                goldens.append((number, json.loads(line)))
    return goldens


def expected(golden: dict) -> tuple[str, date | None]:
    out = golden["output"]
    act_by = date.fromisoformat(out["act_by"]) if out["act_by"] else None
    return out["message_type"], act_by


def report(number: int, ok: bool, want: tuple, got: tuple) -> int:
    print(f"golden {number}: {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(f"   expected: {want[0]}, act_by={want[1]}")
        print(f"   got:      {got[0]}, act_by={got[1]}")
    return 0 if ok else 1


def what_we_test(golden: dict) -> str:
    """A title that says which situation this golden covers, built from its input."""
    i, out = golden["input"], golden["output"]
    decision = {"terminate": "Termination requested", "renew": "Renewal confirmed"}.get(
        i["decision"], i["decision"]
    )
    facts = []
    if not i["autorenew_date"]:
        facts.append("no auto-renewal date")
    elif date.fromisoformat(i["today"]) > date.fromisoformat(i["autorenew_date"]):
        facts.append("notice deadline passed")
    else:
        facts.append("notice deadline still open")
    if i["owner_status"] != "active":
        facts.append(f"owner {i['owner_status']}")
    if not i["file_exists"]:
        facts.append("signed contract missing")
    return f"{decision}, {', '.join(facts)} → {out['message_type']}"


def as_outlook(message: str, message_type: str) -> str:
    """Render a message as a quoted Outlook mail: From, To, Subject, then the body."""
    sender, to = SENDER_TO.get(message_type, DEFAULT_SENDER_TO)
    subject = "(not specified)"
    body = message.strip()
    if body.startswith("Subject:"):
        first, _, body = body.partition("\n")
        subject = first.removeprefix("Subject:").strip()
        body = body.strip()
    lines = [f"**From:** {sender}  ", f"**To:** {to}  ", f"**Subject:** {subject}", "", *body.splitlines()]
    return "\n".join(f"> {line}".rstrip() for line in lines)


def write_report(entries: list[dict]) -> None:
    passed = sum(e["ok"] for e in entries)
    parts = ["# Golden check report", "", f"**{passed} of {len(entries)} passed**", ""]
    for e in entries:
        parts += [
            f"## Golden {e['number']}: {e['ok'] and 'PASS' or 'FAIL'}. {e['title']}",
            "",
        ]
        if not e["ok"]:
            parts += [f"Expected `{e['want'][0]}`, act_by `{e['want'][1]}`. "
                      f"Got `{e['got'][0]}`, act_by `{e['got'][1]}`.", ""]
        parts += ["### Your message", "", as_outlook(e["mine"], e["got"][0]), "",
                  "### Golden message", "", as_outlook(e["golden"], e["want"][0]), "", "---", ""]
    REPORT.write_text("\n".join(parts), encoding="utf-8")
    print(f"report written to {REPORT}")


def check_rules(goldens) -> int:
    """8a: message_type and act_by only. No model call."""
    from schema import Request, route_request

    failures = 0
    for number, g in goldens:
        want = expected(g)
        got = route_request(Request(**g["input"]))
        failures += report(number, tuple(got) == want, want, tuple(got))
    return failures


def check_solve(goldens) -> int:
    """8b: the full solve(). Type and act_by are checked; the text is for your eyes."""
    from schema import Request, solve

    failures = 0
    entries = []
    for number, g in goldens:
        want = expected(g)
        response = solve(Request(**g["input"]))
        got = (response.message_type, response.act_by)
        ok = got == want and response.message.strip() != ""
        failures += report(number, ok, want, got)
        if not response.message.strip():
            print("   message is empty")
        entries.append({
            "number": number, "ok": ok, "want": want, "got": got,
            "title": what_we_test(g), "mine": response.message, "golden": g["output"]["message"],
        })

    write_report(entries)
    return failures


def check_endpoint(api_name: str, goldens) -> int:
    """8c and Step 9: call the running app the way the UI or an agent would.

    Dates are sent as text, and no auto-renewal is sent as an empty string.
    The check passes when the expected message_type appears in the reply.
    """
    from gradio_client import Client

    client = Client(APP_URL)
    failures = 0
    for number, g in goldens:
        args = dict(g["input"])
        args["autorenew_date"] = args["autorenew_date"] or ""
        reply = str(client.predict(**args, api_name=f"/{api_name.lstrip('/')}"))
        want_type = g["output"]["message_type"]
        ok = want_type in reply
        print(f"golden {number}: {'PASS' if ok else 'FAIL'} (expected {want_type} in the reply)")
        print(reply)
        print()
        failures += 0 if ok else 1
    return failures


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] not in ("rules", "solve", "endpoint"):
        print(__doc__)
        sys.exit(2)

    stage = args[0]
    if stage == "endpoint":
        if len(args) < 2:
            print("endpoint needs the name= you gave @app.api, for example:")
            print("  uv run python check_goldens.py endpoint my_endpoint_name 1 3 4")
            sys.exit(2)
        api_name, numbers = args[1], args[2:]
    else:
        numbers = args[1:]

    goldens = load_goldens([int(n) for n in numbers])
    if stage == "rules":
        failures = check_rules(goldens)
    elif stage == "solve":
        failures = check_solve(goldens)
    else:
        failures = check_endpoint(api_name, goldens)

    print(f"{len(goldens) - failures} of {len(goldens)} passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
