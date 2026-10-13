# Project charter

<!--
  Fill this in during TC1, from your Getting to Concreteness worksheet.
  Every week's Session 2 notebook reads this file and stops if it is still the
  template. That is on purpose.
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

A system that takes the owner’s renew or terminate decision plus the contract’s key dates and produces a draft or notice, which the owner approves before anything is sent.

**Input → Output.** Be specific enough that someone could build it wrong and you
would notice.

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
| 3 | Retrieval approach | <!-- TC3 --> |
| 5 | Agent architecture | <!-- TC5 --> |
| 8 | Model | <!-- TC8 --> |
