# Step 11, Pass 2: your actual use case

Prompts and replies are pasted verbatim from the running app. Inputs are
synthetic, no real company data.

---

## Golden 1

**Inputs:** decision `terminate`, owner_status `active`, autorenew_date `2026-11-15`, end_date `2026-12-15`, today `2026-10-12`, file_exists `true`
**Routed message type:** `termination_draft`
**Aspect tested:** instruction-following (format and placeholders) and factual grounding (invent no notice period, clause or price).

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
contract end date: 15 December 2026
today: 12 October 2026
notice deadline (last day to stop auto-renewal): 15 November 2026, still open
owner: active
signed contract file: found
```

**Reply:**

```text
message_type: termination_draft
act_by: 2026-11-15

Subject: Notice of non-renewal: [Product]

Hello [Vendor contact],

We are writing to inform you that we will not be renewing [Product]. This message serves as our formal notice of non-renewal. We expect the contract to end on its current end date of 15 December 2026 and not to renew automatically.

Please confirm in writing that you have received this notice.

Best regards,
[Owner]
```

**Observation:** Type and act_by match the golden (termination_draft, 2026-11-15). Plain text with no markdown, so my rules won over the model's Pass 1 habit. Placeholders kept, end date 15 December 2026 correct, asks for written confirmation, signed [Owner]. The wording differs from the golden ("formal notice", "we will not be renewing") but the meaning is the same.

---

## Golden 3

**Inputs:** decision `terminate`, owner_status `active`, autorenew_date `2026-11-15`, end_date `2026-12-15`, today `2026-11-16`, file_exists `true`
**Routed message type:** `late_notice_to_owner`
**Aspect tested:** reasoning on the date boundary (one day after the deadline), and no legal claim stated as fact.

**Prompt:**

```text
You are Contract agent, an AI agent that helps contract owners.
Write one message of type late_notice_to_owner.

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
Write to the owner. Greet "Hello [Owner],".
- Say they asked to terminate [Product].
- Say the last day to give notice has passed (give the date), so the contract will
  renew on its current terms at its end date (give the date). Never say or imply
  that the contract is terminated.
- Say they have not sent a termination notice to the vendor.
- Ask if they still want to ask the vendor to end the contract. After the deadline
  it would be a request, not a notice, and the vendor may not have to accept.
- Reply yes: I prepare a draft request for them to review. Reply no: the contract
  renews as it is. The owner decides, not the agent.

FACTS
decision: terminate
contract end date: 15 December 2026
today: 16 November 2026
notice deadline (last day to stop auto-renewal): 15 November 2026, has passed; the contract renews on its current terms at its end date
owner: active
signed contract file: found
```

**Reply:**

```text
message_type: late_notice_to_owner
act_by: none

Hello [Owner],

You previously asked to terminate [Product].

Unfortunately, the last day to give notice was 15 November 2026, and that date has now passed. No termination notice has been sent to the vendor. As a result, the contract will renew on its current terms at its end date of 15 December 2026.

Would you still like me to prepare a draft request to the vendor asking them to end the contract? Please note that because the deadline has passed, this would be a request rather than a formal notice, and the vendor may not have to accept it.

If yes, I will prepare a draft for you to review before anything is sent. If no, the contract will renew as it stands. The decision is yours.

Best regards,
Contract agent
```

**Observation:** Type and act_by match (late_notice_to_owner, none). Says the deadline passed and the contract renews on 15 December 2026; never says it is terminated. Uses "may not have to accept", not "does not". Leaves the decision to the owner. It adds "Unfortunately", which is a tone choice, not an error.

---

## Golden 4

**Inputs:** decision `terminate`, owner_status `active`, autorenew_date `2026-11-15`, end_date `2026-12-15`, today `2026-10-12`, file_exists `false`
**Routed message type:** `missing_file_notice`
**Aspect tested:** refusal behaviour (a decline: no draft without the contract file).

**Prompt:**

```text
You are Contract agent, an AI agent that helps contract owners.
Write one message of type missing_file_notice.

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
Write to the owner. Greet "Hello [Owner],". This is a decline: prepare no draft.
- Say which decision they asked for (from the facts) on [Product].
- If the notice deadline is still open, repeat it: it keeps running.
- Say "I can't find the signed contract", so I can't check its notice terms,
  and I have not prepared a draft.
- Ask them to send the signed contract, or say where it is stored, as soon as they can.

FACTS
decision: terminate
contract end date: 15 December 2026
today: 12 October 2026
notice deadline (last day to stop auto-renewal): 15 November 2026, still open
owner: active
signed contract file: not found
```

**Reply:**

```text
Hello [Owner],

You asked me to help with a termination decision for [Product].

The notice deadline of 15 November 2026 is still open and continues to run, so time is limited.

Unfortunately, I can't find the signed contract, which means I can't check its notice terms. I have not prepared a draft.

Could you please send me the signed contract, or let me know where it is stored, as soon as possible so I can move forward?

Best regards,
Contract agent
```

**Observation:** Type and act_by match (missing_file_notice, 2026-11-15). Says no draft was prepared, repeats the 15 November deadline, asks for the file or where it is stored. One small invention: "You asked me to prepare a termination notice": the owner asked to terminate, not for a notice. In the real project, "file found" will be a record that the contract was already read and its terms extracted, not only a file check (roadmap point, see Pass 3).

---

## Golden 7

**Inputs:** decision `terminate`, owner_status `active`, autorenew_date `(empty)`, end_date `2026-12-15`, today `2026-10-12`, file_exists `true`
**Routed message type:** `termination_draft`
**Aspect tested:** handling of missing information (no auto-renewal clause: it must not invent a deadline).

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
contract end date: 15 December 2026
today: 12 October 2026
auto-renewal: none; there is no notice deadline and the contract simply ends on its end date
owner: active
signed contract file: found
```

**Reply:**

```text
message_type: termination_draft
act_by: none

Subject: [Product]: end of contract on 15 December 2026

Hello [Vendor contact],

We are writing to let you know that our contract for [Product] will end on 15 December 2026 and we will not be continuing after that date. We wanted to inform you in good time so that you can plan accordingly.

Could you please confirm that service and billing will stop on 15 December 2026, and let us know if there is anything you need from us before then?

Best regards,
[Owner]
```

**Observation:** message doesn't invent act_by and used only existing facts.

---

## Does it behave the way you expected? Why or why not?

Yes on the structure: message_type and act_by matched the golden in every run, because code decides them (route_request), not the model. Yes on the text rules: no markdown in any reply, placeholders kept, "may not" instead of "does not", so the rules in the prompt beat the model's default from Pass 1. The wording is different from the goldens every time, with one small invention in golden 4. I judged the text by eye, so the owners at the demo need to say whether these drafts are what they would send.

