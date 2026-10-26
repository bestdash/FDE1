# Project charter

<!--
  Fill this in during TC1 Step 4, from your Getting to Concreteness form.
  Later weeks' notebooks read this file and stop if it is still the template.
  That is on purpose.
-->

**Department:** IT infrastructure

**Working title:** Contract Agent

---

## The problem

**Who has it?** One real role, not a department.

Contract owner. They are multiple within the company (usually head of every department). Particularly here Head of IT Infrastructure that owns today about 80-100 contracts.

**What are they trying to do?**

Renew contracts on time, with the right quantities and the right features.

**How do they handle it today?**

A shared spreadsheet, a review call every two weeks, manual emails, and a manual update at the end.

**What does that cost — time, money, risk, or relationships?**

About 120 person-hours per year in review meetings. About 1 in 5 renewals late or missed. Examples: a tool renewed when it was not wanted; a contract that could no longer be terminated; a penalty for renewing one day late.

**The problem in one sentence. No solution in it.**

Contract owners act too late on renewal notice deadlines, with about 1 in 5 renewals late or missed, because tracking is a manual spreadsheet reviewed on a call every two weeks, which costs about 120 person-hours per year across the team.

---

## Success

**What does the new world look like for that person?**

Contracts renewed on time; one review meeting per quarter.

**How would the firm measure it? Which numbers should move?**

 Alerts 100% in time; renewals on time about 80% to 95% (e.g. no penalties for late renewal); review meetings about 26 to 4 per year. Saved money for global contract envelope (first offered quote vs negotiated price vs last year price).

 Why 95% and not 100%: The system controls when the alert is sent, but a person still has to act. The remaining misses come from causes outside the system: an owner on leave, a slow decision from someone else, an escalation nobody picks up.

---

## The first product

**Your solution in one sentence.**

A system that reads each contract's documents and records its key terms with their source, computes the last day to say no, wakes the contract up a set time before that deadline to alert the owner with the terms to review, and turns the owner's renew or terminate decision into a draft or notice that the owner approves before anything is sent.

**Stages.** Week 3 charter update: Stage 1 is added in front of step B. The problem and the success measures do not change. Reasons in `decisions.md`, Week 3 rows.

1. **Record** (TC3): when a contract is signed, or once for all existing contracts at go-live, its key terms are read from its documents and stored with their source.
2. **Dormant** (Week 4 or 5): the contract waits until its alert date.
3. **Alert** (Week 4 or 5): the owner gets the deadline and the terms to review, and is asked: renew or terminate?
4. **Draft** (step B, TC1): the decision becomes a draft or notice for the owner to approve.

**Input → Output.** Be specific enough that someone could build it wrong and you
would notice.

### Stage 1: Record (TC3)

| | |
| --- | --- |
| **In** | `contract_id` (for example `SYN-03`) |
| **Out** | Each field below has a value with its source (document + section), or "not found" |

| Field | Values | Spreadsheet column today |
| --- | --- | --- |
| `start_date` | date | starting date |
| `term_months` | 12, 36, ... | contract duration |
| `end_date` | date; computed from `start_date` + `term_months` when not stated | end date |
| `renewal_type` | auto \| manual; "not found" when no document has a renewal clause (the system does not guess) | auto-renewal (Y/N) |
| `notice_days` | days before the end date | cancellation period |
| `annual_contract_value` (ACV) | amount per year | annual cost |
| `total_contract_value` (TCV) | amount for the whole term | contract amount |
| `pricing_model` | user-based \| package | (none) |
| `price_per_user` | only when the contract states a price per user | price per licence per year |
| `features` | list of short items as written in the contract ("350 users", "SSO", "AI credits") | licence number, description |

Computed by code, never by the model: `end_date` when not stated (`start_date` + `term_months`); whichever of ACV or TCV is not stated (TCV = ACV × `term_months` / 12); `autorenew_date` = `end_date` minus `notice_days` (empty when `renewal_type` is manual); `file_exists` = documents found for this `contract_id`.

Stage 1 feeds Stage 4: `end_date`, `autorenew_date` and `file_exists` come from Stage 1; `decision` and `owner_status` come from the owner and the owner record.

### Stage 4: Draft (step B, TC1)

| | |
| --- | --- |
| **In** | `decision` (terminate or renew); `end_date` (contract end date); `autorenew_date` (optional: last day to say no before the contract auto-renews; empty when there is no auto-renewal clause); `today` (the date the decision is evaluated on); `owner_status` (active or left); `file_exists` (contract file on record: yes or no) |
| **Out** | `message_type` (termination draft for the vendor awaiting owner approval, also used as a courtesy notice when there is no auto-renewal; late notice to the owner that the deadline has passed and the contract renews; renewal review email to the owner; escalation to procurement when the owner has left; missing file notice asking the owner for the signed contract or where it is stored); `message` (the draft or message text); `act_by` (the last day the recipient can act: `autorenew_date` while it has not passed; empty when there is no auto-renewal clause or the date has passed) |

---

## Decisions made later

<!--
  Amended as the cohort goes. Keep the reasoning, not just the choice — Week 5
  asks you to defend your architecture against the options you rejected, and
  Week 10's handoff doc is largely this section.
-->

| Week | Decision | Why, and what you rejected |
| --- | --- | --- |
| 3 | Retrieval approach | BM25 over contract sections with the contract's identity in every chunk (rag-v2), chosen over DCI and dense on 10 labelled questions. Reasons, rejected options and switch conditions: `decisions.md`, Week 3 retrieval row |
| 5 | Agent architecture | <!-- TC5 --> |
| 8 | Model | <!-- TC8 --> |
