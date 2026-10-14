# Decision log

One row per architectural decision, with the option you rejected and why.

> **Week 5 asks you to defend your agent architecture against the alternatives.**
> **Week 10's handoff doc is largely this file.** Both are much easier if you
> wrote the reasoning down while you still remembered it.

A decision without a rejected alternative is not a decision, it is a default.
If you cannot name what you did not do, you did not choose.

| Week | Decision | What you rejected | Why | What would change your mind |
| --- | --- | --- | --- | --- |
| 1 | Pilot runs as a POC on a VM, not on the planned AKS cluster with managed PostgreSQL | Waiting for the cluster before starting the pilot | The cluster could not be created (subnet error on every IT VNet subnet) and the VM is available now; the code does not change, only how it runs (timer and restart instead of CronJob, database location, secrets) | The cluster subnet is fixed: move back with the same manifests. Or the sponsor confirms the VM as the pilot target: then the managed database and monitoring of the daily job become requirements before real data |
| 1 | Pipeline: a function, not an agent (0 of 4 questions true) | An agent | Q1: No. Every contract goes through the same steps. A different number of review points per contract changes the size of the output, not the steps. Q2: closest call: current SaaS terms on the vendor website would need a fetch, but that is one fixed step, not an agent. The rule for which contracts trigger it is written in code. Q3: No. Every draft goes to the owner for review before anything is sent, and the failure cases (deadline passed, contract missing, owner left) route to a person instead of retrying. Q4: No. The input is always a contract and the owner's decision, from a closed set: terminate or renew. | We decided to set a goal for every contract renewal and would allow agent to negotiate instead of human |
| 1 | Slice: step B. The owner's decision (terminate or renew) comes in; the system returns the kind of output (vendor draft, owner notice, or escalation), the draft text and the act_by date. | Step A first: read each contract, extract the conditions negotiated in it (for example number of users, price per user, features) and prepare contract-specific review points for the owner. Or both A and B in TC1. | A's output is open-ended: the number and kind of review points differ per contract, so one correct answer is hard to write by hand, and the owner cannot easily review the goldens. B has a small, fixed set of outputs, so five goldens can cover it and the owner can check each one. B also contains the model's drafting work. A is deferred to a later week, not dropped. | If A were reduced to a small, fixed set of fields, such as number of users and price per user (about half of the SaaS contracts), its goldens could be written and reviewed, and A could come first. |
| 1 | Owners who have not answered (no reply after 3 reminders): out of TC1 | Handling them in this version | `decision` is a required input, so a silent owner has no Request; reminders belong to step A, which is deferred | Step A enters scope in a later week |
| 1 | Decide-by date: the earlier of (autorenew_date minus 30) and (end_date minus 90) | The later of the two | The owner gets the most lead time. Example: 31 Oct and 31 Dec 2026 give 1 Oct and 2 Oct, so 1 Oct | The sponsor sets a different lead-time policy |
| 1 | Terminate on a contract with no auto-renewal: courtesy notice to the vendor, as termination_draft for owner review | No message (the contract just ends) | The vendor learns early that we are not renewing, through the same approval path as every vendor message | Pilot vendors or owners say the notice is not needed |
| 1 | Decision values: terminate and renew only | A third value "review" | Review is an action that follows renew, not a decision | [write] |
| 1 | `today` is an input field | Reading the real date from the clock | I need to verify different scenarios (deadline open, deadline passed); each golden fixes its own date, so it gives the same result every time it runs | None expected: in production the entry point passes the real date in as `today` |
| 1 | Pilot user: IT contract owners only | Contract owners in all departments | Other departments may need decisions or rules the schema and goldens do not cover yet | Contracts from another department turning out to fit the same two decisions and five cases |
| 1 | TC1 scope unchanged; pilot user stays IT contract owners | Widening TC1 to personal subscriptions | The designer is not the pilot user; her main request (overview and feature analysis) is step A, planned for a later week | IT contract owners also ask for the overview or alerts first; then step A moves earlier |
| 1 | Record "owner unknown" as a missing case; TC1 schema unchanged (owner_status stays active \| left) | Adding owner_status "unknown" in TC1 | The TC1 pilot covers IT contracts, where the owner is known; outside IT the sponsor often does not know the owner | The pilot extends to non-IT contracts |


Oct 13: the sponsor asked first for automatic alerts and contract terms (step A), which meets the condition in row a. Candidate to move step A earlier: decide in Week 2.

**Strongest case for the opposite verdict (agent):** I would switch to an agent if, over 1 year, owners approve the proposed drafts without edits in at least 90% of cases, and the next step keeps depending on the vendor’s reply. Then the human check adds cost without value, and a fixed pipeline cannot follow the negotiation.

**Out of scope for TC1:**
- 3-month escalation to procurement for a missing contract
- Vendor website fetch for current SaaS terms
- Step A (the scheduled alert) and quote comparison

---

The last column is the one people skip and the one people ask about. "We chose
dense retrieval; we would switch to hybrid if exact-match queries went above ~20%
of traffic" is an engineering position. "We chose dense retrieval" is a
preference.
