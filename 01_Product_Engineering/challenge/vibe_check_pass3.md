# Step 11, Pass 3: where it falls down

Experiments that try to break the app. Prompts and replies are pasted verbatim
from the running app. Inputs are synthetic, no real company data.

---

## Experiment A: owner left, no auto-renewal

**Inputs:** decision `terminate`, owner_status `left`, autorenew_date `(empty)`, end_date `2026-12-15`, today `2026-10-12`, file_exists `true`
**Aspect tested:** handling of missing information: the rules conflict with the facts
**Expected type / act_by:** `escalation_to_procurement / none`
**Routed message type:** `escalation_to_procurement`

**Prompt:**

```text
You are Contract agent, an AI agent that helps contract owners.
Write one message of type escalation_to_procurement.

RULES FOR EVERY MESSAGE
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
- Short, polite, actionable, plain business English.

RULES FOR THIS MESSAGE
Write to procurement. Greet "Hello Procurement team,". This is a decline: prepare no draft.
- Say the owner of the [Product] contract has left the company.
- Say which decision is on record (from the facts), but nobody can now review or
  approve a draft, so I have not prepared one.
- Give the notice deadline if the facts give one and the contract end date, and ask them to assign a new
  owner who can confirm or change the decision before the deadline.
- If the facts say the signed contract was not found, also say that I can't find
  it and can't check its notice terms, and ask them to send it or say where it
  is stored.

FACTS
decision: terminate
contract end date: 15 December 2026
today: 12 October 2026
auto-renewal: none; there is no notice deadline and the contract simply ends on its end date
owner: has left the company
signed contract file: found
```

**Reply:**

```text
message_type: escalation_to_procurement
act_by: none

Hello Procurement team,

The owner of the [Product] contract with [Vendor contact] has left the company. The decision on record was to terminate the contract, which ends on 15 December 2026. However, as there is no longer an owner in place, nobody is available to review or approve a draft, so I have not prepared one.

As there is no notice deadline for this contract, the key date to be aware of is the contract end date of 15 December 2026, by which the termination decision should be confirmed or changed. Please assign a new owner as soon as possible so they can take the appropriate action in time.

Best regards,
Contract agent
```

**Observation:** Type and act_by matched (escalation_to_procurement, none): the owner-left rule wins first, as designed. My prediction was wrong: the rule says "before the deadline", but the model did not invent a deadline. It named the end date (15 December 2026) as the key date and asked for a new owner "as soon as possible". One small addition: "with [Vendor contact]", which this message type does not ask for (the placeholder is kept, so no fact is invented).
**Limitation found:** The escalation always asks procurement for the same action: assign a new owner. Nothing in the routing or the rules looks at how much time is left (schema.py, escalation_to_procurement rules). Here 64 days are left, so a new owner is realistic. With only a few days left there is no time to find one: procurement would have to act on the recorded decision themselves (send the termination notice). The app has no urgency rule yet: the decide-by date described in solve() is not used in TC1. Roadmap: when time is short, change the ask from "assign an owner" to "act on the decision now".

---

## Experiment B: contract already ended

**Inputs:** decision `terminate`, owner_status `active`, autorenew_date `(empty)`, end_date `2026-09-30`, today `2026-10-12`, file_exists `true`
**Aspect tested:** invalid input: no check that the dates make sense
**Expected type / act_by:** `termination_draft / none`
**Routed message type:** `termination_draft`

**Prompt:**

```text
You are Contract agent, an AI agent that helps contract owners.
Write one message of type termination_draft.

RULES FOR EVERY MESSAGE
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
- Short, polite, actionable, plain business English.

RULES FOR THIS MESSAGE
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
- Do not mention auto-renewal, a notice deadline or "non-renewal": none of them exists.

FACTS
decision: terminate
contract end date: 30 September 2026
today: 12 October 2026
auto-renewal: none; there is no notice deadline and the contract simply ends on its end date
owner: active
signed contract file: found
```

**Reply:**

```text
Draft message
message_type: termination_draft
act_by: none

Subject: [Product]: end of contract on 30 September 2026

Hello [Vendor contact],

We are writing to let you know that our contract for [Product] ended on 30 September 2026 and we will not be continuing after that date. We wanted to inform you in good time so that you can plan accordingly.

Could you please confirm that all service and billing stopped on 30 September 2026, and let us know if there is anything you need from us before we close this out?

Best regards,
[Owner]
```

**Observation:** Type and act_by matched (termination_draft, none): the code routed the request exactly as designed. The model partly noticed the date conflict: it switched to the past tense ("ended", "stopped"). But it still followed the rule "We tell them in good time so they can plan", which is false 12 days after the end date. The draft contradicts itself.
**Limitation found:** The form and Request accept an end date before today: nothing checks that the dates make sense, so an ended contract gets a normal courtesy notice. In real life this message comes too late. The vendor would have contacted the owner before the end date to ask about renewal, and two weeks after the end, with no licenses in use, a courtesy note is optional: at most a gesture for the company's reputation. Roadmap: check the dates first, and when the end date has passed, do not draft for the vendor; ask the owner to confirm the contract really ended (no renewal, no new invoice).

---

## What are the real limitations of this application?


1. **No access to my systems.** The only input is six fields typed by hand, one contract at a time. It cannot answer "which contracts renew in November?": there is no field for it, and the raw Chat box says it has no access to contracts.
2. **No memory.** Every run starts fresh: it does not know the owner was already told, or that a reminder was sent.
3. **"File found" is only yes/no.** The agent never reads the contract. In the real project, "found" must mean the contract was read and its notice terms extracted.
4. **The notice deadline is typed by hand.** In the form, the user picks the notice deadline as a date. It should be calculated from the contract: the auto-renewal date minus the notice period in the contract. If the contract gives only the auto-renewal date and no notice period, the auto-renewal date is the deadline. Then the owner's decide-by date is set 30 days before the deadline (`AUTORENEW_LEAD_DAYS`), so the owner has time to decide. Two dates, two jobs: the deadline is legal, the decide-by date is internal.
5. **No urgency.** The escalation asks for a new owner whatever the time left (Experiment A).
6. **No input checks.** An end date in the past is accepted and routed like a normal case: the draft tells the vendor "in good time" 12 days after the contract ended (Experiment B).
7. **Placeholders only.** No real product, vendor or owner names, so every draft needs manual completion. In the real project these values come from the contract database.
8. **Silent failure on a blocked network.** If the CDN for the Gradio client is blocked, the form loads and does nothing.
9. **Drafts only (scope).** No sending, reminders, escalation follow-up or quote comparison yet.

**Not a limitation: wording changes on every run.** Type and act_by are fixed by code, but the text is reworded each time. For the reader this is a benefit: a vendor who gets the same message word for word from several owners would find it machine-made. The risk is meaning, not style: Golden 4 once said "you asked me to prepare a termination notice" and once "help with a termination decision". So style may change, the facts and the ask may not.

## What is a vibe check worth as evidence?

A vibe check is weak evidence: one run per case, judged by eye, so it exposes the system's real limitations and helps plan the roadmap, but it cannot show that one version is better than another. Before comparing two versions, I would write down for each golden what the text must contain (for example the deadline date and the request to the owner) and must not contain (an invented fact, a legal rule stated as fact), then test every version against the same conditions on many goldens built from real contracts OR many goldens based on real contract.

Next step for the product (roadmap, not the comparison): fill the placeholders with real values from the production context, and read the real contracts (MSA, EULA) to extract their terms and review them closely.
