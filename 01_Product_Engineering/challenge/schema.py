from datetime import date
from typing import Literal
from pydantic import BaseModel, Field
from llm import stream_reply

# Company policy: change these here if corporate policy changes.
# They are the same for every contract, so they are not Request fields.
AUTORENEW_LEAD_DAYS = 30   # decide-by is this many days before autorenew_date
END_DATE_LEAD_DAYS = 90    # decide-by is this many days before end_date

class Request(BaseModel):
    """What the user or system hands in."""
    decision: Literal["terminate", "renew"]  # owner contract decision: terminate or renew
    autorenew_date: date | None = Field(default=None, description="last day to say no before the contract auto-renews; None when the contract has no auto-renewal clause")
    end_date: date = Field(description="contract end date")
    today: date = Field(description="reference date; fixed in goldens so results don't change with the calendar")
    owner_status: Literal["active", "left"]  # active or left
    file_exists: bool = Field(description="True if the contract file exists")


class Response(BaseModel):
    """What comes back."""

    message_type: Literal[
        "termination_draft",      # terminate, on time: draft for the vendor, owner reviews it first
        "late_notice_to_owner",   # terminate, deadline passed: it renews, ask if they still want to terminate
        "renewal_review_email",   # renew: items to review and a usage/feature session proposal
        "escalation_to_procurement",  # owner has left
        "missing_file_notice",    # no contract file, nothing can be drafted for review
    ] = Field(description="which of the five outcomes happened")

    message: str = Field(description="the draft or message text")

    act_by: date | None = Field(description="the last day the recipient of this message can act: "
        "autorenew_date while today <= autorenew_date, whatever the message_type; "
        "None when there is no auto-renewal clause or autorenew_date has passed")

    # contract_status is left out on purpose: today it follows one-to-one from
    # message_type, so it adds no information. Add it back when the same
    # message_type can lead to different statuses (e.g. reminders in step A).

def route_request(request: Request) -> tuple[str, date | None]:
    """Return (message_type, act_by). Rules follow the solve() docstring order.

    Decides what to do with the request from the decision, dates and other fields.
    """
    r = request

    # act_by has its own rule, independent of message_type (see Response)
    if r.autorenew_date is not None and r.today <= r.autorenew_date:
        act_by = r.autorenew_date
    else:
        act_by = None

    # message_type: first matching rule wins
    if r.owner_status == "left":                 # 1. no approver
        message_type = "escalation_to_procurement"
    elif not r.file_exists:                      # 2. no contract file found
        message_type = "missing_file_notice"
    elif r.decision == "renew":                  # 3. dates change text, not type
        message_type = "renewal_review_email"
    elif r.decision == "terminate":              # 4. dates matter only here
        if r.autorenew_date is None:             #    a. courtesy notice
            message_type = "termination_draft"
        elif r.today <= r.autorenew_date:        #    b. last day still counts
            message_type = "termination_draft"
        else:                                    #    c. deadline passed
            message_type = "late_notice_to_owner"
    else:
        raise ValueError(f"unknown decision: {r.decision!r}")

    return message_type, act_by

def _fmt(d: date) -> str:
    """15 November 2026 (works on Windows and Linux)."""
    return f"{d.day} {d:%B %Y}"

def build_facts(r: Request) -> str:
    # Each line below is what a condition in TYPE_RULES refers to:
    #   "there is no auto-renewal"         -> auto-renewal: none
    #   "notice deadline is still open"    -> notice deadline: ..., still open
    #   "notice deadline has passed"       -> notice deadline: ..., has passed
    #   "signed contract was not found"    -> signed contract file: not found
    lines = [
        f"decision: {r.decision}",
        f"contract end date: {_fmt(r.end_date)}",
        f"today: {_fmt(r.today)}",
    ]
    if r.autorenew_date is None:
        lines.append("auto-renewal: none; there is no notice deadline and "
                     "the contract simply ends on its end date")
    elif r.today <= r.autorenew_date:
        lines.append(f"notice deadline (last day to stop auto-renewal): "
                     f"{_fmt(r.autorenew_date)}, still open")
    else:
        lines.append(f"notice deadline (last day to stop auto-renewal): "
                     f"{_fmt(r.autorenew_date)}, has passed; the contract "
                     f"renews on its current terms at its end date")
    lines.append(f"owner: {'has left the company' if r.owner_status == 'left' else 'active'}")
    lines.append(f"signed contract file: {'found' if r.file_exists else 'not found'}")
    return "\n".join(lines)

# Rules for every message. Each one comes from a "why" note in golden.jsonl.
MESSAGE_RULES = """\
- Write only the message text. Plain text, no markdown, no comments around it.
- Invent nothing that is not in facts or database. Keep [Product], [Vendor contact] and
  [Owner] as placeholders.
- The agent has not read the contract clauses, so never state a legal rule as
  fact: write "may not have to accept", never "does not have to accept".
- The agent prepares drafts; it never sends anything to the vendor.
- Write dates exactly as they appear in facts (e.g. 15 November 2026).
- Messages from the agent speak as "I" and, unless the rules below say
  otherwise, end with:
  Best regards,
  Contract agent
- Short, polite, actionable, plain business English."""

# Rules per message_type. Each block comes from the "why" notes of the goldens
# named in its comment. Conditions refer to lines that build_facts must print.
TYPE_RULES = {
    # goldens 1, 7, 8
    "termination_draft": """\
Write a draft from the owner to the vendor. Greet "Hello [Vendor contact],".
End with "Best regards," and then "[Owner]", not Contract agent: the owner sends it.
Do not say that the owner reviews it first. Give no notice period, clause or price.
If the facts give a notice deadline:
- First line: "Subject: Notice of non-renewal: [Product]", then a blank line.
- Write as “we” (the company), not “I”
- Say we will not renew [Product], this is our notice of non-renewal, and the
  contract should end on its current end date and not renew automatically.
- Ask them to confirm in writing that they received this notice.
If the facts say there is no auto-renewal:
- This is a courtesy notice. First line: "Subject: [Product]: end of contract on <end date>".
- Say the contract ends on its end date and we will not continue after it.
  We tell them in good time so they can plan.
- Ask them to confirm that service and billing stop on the end date, and whether
  they need anything from us before then.
- Do not mention auto-renewal, a notice deadline or "non-renewal": none of them exists.""",

    # golden 3
    "late_notice_to_owner": """\
Write to the owner. Greet "Hello [Owner],".
- Say they asked to terminate [Product].
- Say the last day to give notice has passed (give the date), so the contract will
  renew on its current terms at its end date (give the date). Never say or imply
  that the contract is terminated.
- Say they have not sent a termination notice to the vendor.
- Ask if they still want to ask the vendor to end the contract. After the deadline
  it would be a request, not a notice, and the vendor may not have to accept.
- Reply yes: I prepare a draft request for them to review. Reply no: the contract
  renews as it is. The owner decides, not the agent.""",

    # goldens 2, 9
    "renewal_review_email": """\
Write to the owner, not to the vendor. Greet "Hello [Owner],".
Thank them for confirming that they want to renew [Product].
If the notice deadline is still open:
- Say the contract ends on its end date and renews automatically on its current
  terms unless notice is given by the notice deadline, so the review must be
  finished before that date. Give both dates.
- Say: before I draft the quote request for the vendor, please check the four items.
If the notice deadline has passed:
- Say the last day to change the terms before the automatic renewal has passed
  (give the date), so the contract renews on its current terms at its end date
  (give the date). Do not write "before <deadline>".
- Say a review is still worth doing, then list the four items.
- Say that if the review shows fewer licenses or a different model are needed,
  they can still ask the vendor to adjust, but the vendor may not have to accept
  until the next renewal.
The four items, numbered:
1. Duration: one year or three years?
2. License model: keep the current model or change it?
3. Quantity: how many licenses do you need?
4. Usage: are all licenses in use, and are there features you do not use?
Offer two ways to answer:
- In Claude: open a review session and I will take them through this contract,
  together with any other contracts waiting for their review.
- By reply: answer the four points, and I will use the answers to draft the quote
  request (deadline open) or the request to the vendor (deadline passed).
The text must work both in Claude and as an email.
If the notice deadline is still open, end with: nothing goes to the vendor until
they approve the draft.""",

    # golden 4
    "missing_file_notice": """\
Write to the owner. Greet "Hello [Owner],". This is a decline: prepare no draft.
- Say which decision they asked for (from the facts) on [Product].
- If the notice deadline is still open, repeat it: it keeps running.
- Say "I can't find the signed contract", so I can't check its notice terms,
  and I have not prepared a draft.
- Ask them to send the signed contract, or say where it is stored, as soon as they can.""",

    # goldens 5, 6
    "escalation_to_procurement": """\
Write to procurement. Greet "Hello Procurement team,". This is a decline: prepare no draft.
- Say the owner of the [Product] contract has left the company.
- Say which decision is on record (from the facts), but nobody can now review or
  approve a draft, so I have not prepared one.
- Give the notice deadline if the facts give one and the contract end date, and ask them to assign a new
  owner who can confirm or change the decision before the deadline.
- If the facts say the signed contract was not found, also say that I can't find
  it and can't check its notice terms, and ask them to send it or say where it
  is stored.""",
}

def build_prompt(request: Request, message_type: str) -> str:
    return (
        "You are Contract agent, an AI agent that helps contract owners.\n"
        f"Write one message of type {message_type}.\n\n"
        f"RULES FOR EVERY MESSAGE\n{MESSAGE_RULES}\n\n"
        f"RULES FOR THIS MESSAGE\n{TYPE_RULES[message_type]}\n\n"
        f"FACTS\n{build_facts(request)}\n"
    )

def solve(request: Request) -> Response:
    """The whole product, as one function signature.

    Precedence: check in this order; the first rule that matches decides
    message_type. Every rule further
    down that is also true is mentioned in message, never dropped.

      1. owner_status == "left"   -> escalation_to_procurement
         nobody can approve anything, so nothing else can happen
      2. not file_exists          -> missing_file_notice
         nothing can be checked, so nothing can be drafted
      3. decision == "renew"      -> renewal_review_email
         dates change the text (before or after autorenew_date), not the type
      4. decision == "terminate":
         a. autorenew_date is None        -> termination_draft (courtesy notice)
         b. today <= autorenew_date       -> termination_draft
         c. today >  autorenew_date       -> late_notice_to_owner

    The order follows what blocks what: no approver blocks everything,
    no file blocks drafting, the decision picks the path, and dates matter
    only for terminate. act_by has its own rule (see Response) and is set
    at every step, whichever rule wins.

    Two dates, two jobs:

    1. Hard date (legal): autorenew_date itself.
       It decides whether we can still terminate.
       today <= autorenew_date: termination_draft (golden 1).
       today > autorenew_date: late_notice_to_owner, the contract renews (golden 3).
       No autorenew_date: the contract just ends on end_date, so it is never too late.
       A terminate decision then gets a courtesy notice to the vendor,
       sent as termination_draft for the owner to review.

    2. Decide-by date (internal): when "the date is approaching".
       With auto-renewal: the earlier of (autorenew_date minus AUTORENEW_LEAD_DAYS)
       and (end_date minus END_DATE_LEAD_DAYS), so the owner gets the most lead time.
       Example with 30 and 90: autorenew_date 31 Oct 2026 gives 1 Oct,
       end_date 31 Dec 2026 gives 2 Oct, so the decide-by date is 1 Oct 2026.
       Without auto-renewal: end_date minus END_DATE_LEAD_DAYS.
       Used from step A (reminders and escalation); TC1 does not need it yet.

    AUTORENEW_LEAD_DAYS and END_DATE_LEAD_DAYS are policy,
    set once at the top of this file, not per contract.
    """
    message_type, act_by = route_request(request)
    message = ""
    for message in stream_reply(build_prompt(request, message_type)):   # each value is the text so far
        pass                               # keep the last one
    return Response(message_type=message_type, message=message.strip(), act_by=act_by)
