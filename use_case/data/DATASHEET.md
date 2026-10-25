# Datasheet

## What this data is

**Generated on:** 2026-10-15
**Generated from:** the `Request` / `Response` schema, the three variation axes below, and goldens 1 to 6 as examples. The goldens were written from memory with placeholders, not from real contracts. No real record was used.
**Rows:** 128 schema-valid rows in `synthetic_v1.jsonl` (gitignored)

## How it was generated

- **Model:** `anthropic/claude-sonnet-4-6` (Claude Sonnet 4.6, Anthropic API)
- **Temperature:** not set in either run (Anthropic default 1.0, looked up). **Top-p:** not set (provider default, about 0.99, looked up)
- **Prompt:** S4 `build_prompt`, all 27 combinations
- **Dedupe:** character 4-gram Jaccard on `input`, threshold 0.9 (reasons in `decisions.md`)
- **Validator:** pydantic model with `input: Request`, `output: Response`, `why: str`, imported from `01_Product_Engineering/challenge/schema.py`

| Run | Seeds shown | Rows per combination | Generated | After dedupe | Schema-valid | Dead combinations |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | goldens 1 to 3 | 3 | 81 | 75 | 31 | 0 |
| 2 (kept) | goldens 1 to 6 | 6 | 162 | 130 | 128 | 0 |

**Run 1 finding:** no decline or escalation row survived validation. The prompt showed only goldens 1 to 3, so the model never saw `missing_file_notice`, `escalation_to_procurement` or `owner_status: "left"`, and it invented its own names and values. Run 2 shows goldens 1 to 6, which cover all five message types: 2 rows rejected (invented `decision` value).

## Variation axes

| Axis | Values | Reason |
| --- | --- | --- |
| `time_left` | 1. more than 30 days before the deadline (auto-renewal date if one exists, otherwise end date): comfortable<br>2. 14 to 30 days left: the owner must answer now<br>3. less than 14 days left: not enough time for the internal purchase request and order | Time left decides the tone, the recipient, and whether the purchase process can still finish (it needs about 2 weeks) |
| `contract_complexity` | 1. simple: per-user or per-usage subscription, one price line<br>2. complex: priced on compute capacity, plus license and support fees, so the quantity is hard to estimate<br>3. very complex: several cloud instances, each with its own users and third-party add-ons, plus a paid security support line where the vendor's responsibility in incidents matters | Stakes and review depth grow with the number of price lines and the security risk |
| `record_completeness` | 1. nothing missing: owner active, signed file found<br>2. partly missing: the owner has left, signed file found<br>3. critical missing (decline): signed contract file not found | Missing information changes who gets the message, and some gaps block drafting |

**After the sponsor review (for the next run, not used to generate this data):** complex and very complex contracts involve several departments, which must provide last year's usage and next year's forecast before a quote can be requested. Very complex also covers products used by internal users and customers at once. Support and security are two separate paid add-ons, not one "security support line".

## What it can validate

This is prototyping data: inputs that look like real renewal cases, with no labels a person verified.

- The pipeline runs end to end: generate, dedupe, validate.
- The generated inputs fit the current `Request` schema, for each combination of `time_left` and `record_completeness`.
- The validator rejects rows that do not fit, and the counts show how many.
- Routing coverage: 128 input situations (decision, dates, owner status, file status), each with the type and `act_by` the model chose, to test routing in Week 4. Not message quality.
- Plausibility, narrowly: the contract owner read 14 rows and found no situation that would never happen ("we are covered at 99%"). That is one expert on 14 rows, not a measure of the whole file.


## What it cannot validate

- Message variety and writing quality: messages are close paraphrases of the goldens.
- Deadlines set by the vendor: an early-renewal price deadline can arrive weeks before the end date, so `time_left` from the database can be wrong (expert review, Oct 16).
- Real complexity: the expert defines it by how many business units must approve, and whether the product serves internal users and customers at once. It is often discovered only at the first quote. None of this is in the schema or the data.
- Realistic contract wording: the axis value "paid security support line" is something the expert has never seen in a contract. Real contracts have two separate paid options: a software support add-on and a security add-on.
- A missing vendor contact: when the vendor's people change and the new email is not in our files, the process blocks. No row covers it. It matters in a later step, after the owner has reviewed the contract.
- Dedupe uses character overlap, which cannot see a one-word change in a structured field: one renew row was dropped as a twin of a terminate row in run 1.
- Validation checks types and allowed values only: not that dates are consistent, that `act_by` is right, or that the message matches the decision.
- Which message types appear depends on which goldens the prompt shows: with 3 seeds, run 1 produced zero decline rows.
- With less than 14 days left, the model wanted an urgent-warning message type the schema does not have. Urgency exists only in the message text.
- Rows reuse the goldens' invented dates (2026-10-12, 2026-11-15, 2026-12-15), so date variety is lower than it looks.

## What it must never be compared against

Real ground truth is the real contracts and what contract owners actually decided and sent: the contract database and the project mailbox, inside the company's private system. These synthetic rows are not ground truth: their labels (message type, `act_by`, message) were written by the generating model and checked by no one. A masked copy of real contracts may become a backtesting set later, in the private company repo, never in this public fork.


## Leakage check — outward (what left)

- [X] No real record was used as a seed.
- [X] No real entity names, IDs, or identifiers appear.
- [X] No distinctive internal formats that would identify the firm.
- [X] Rare categories were generated, not copied.


**Read by me:** 50 random valid rows (sample seed 7). Removed: none. Looked for: real product or vendor names, internal formats, copied rare cases, and claims the agent cannot know.

- Product names are invented by the model (for example Graphline Analytics, Stackflow CRM). I checked: none is a product we use.
- Shown to the contract owner: 14 rows across two sessions (not 20, because the rest were near-copies); his answers are in `stakeholders.md`.
- Low variety: messages stay close to the goldens' wording. Renew messages always list the same four review points from golden 2, whatever the contract complexity. Missing-file notices are nearly identical whatever the time left.
- Complexity reaches the message only through the axis text, never through the contract, because the agent does not read the file. Reading the file comes with retrieval (Week 3).
- Dedupe compares inputs only, so rows with different dates but near-identical messages were all kept.
- Value of this data: coverage of input situations (decision, dates, owner, file) with the expected type and `act_by`, for routing tests. Not message variety.

**Expert check (Oct 16):** if this were public, the sensitive parts would be amounts and the technology stack, because knowing which tools we use shows an attacker where to aim. The rows contain no amounts, and the product and add-on names are invented, so they do not describe our stack. 

## Leakage check — inward (what the eval shares with the training data)

**Are the goldens disjoint from anything the system was, or will be, tuned on?**
No: overlap. The goldens were written from memory, not from real contracts, but in TC1 the drafting prompt for each message type was adjusted until the goldens passed. A passing score on the goldens partly measures that tuning, not correctness on new cases. This file was generated from goldens 1 to 6, so it must never be used to tune anything the goldens later score: no prompt examples, no fine-tuning.

**Overlap between `golden.jsonl` and this file, by the dedupe measure:** 
122 of 128 rows within 0.5 of a golden. The number is inflated: every row shares the same field names, due to my input data structure, so it does not mean the content was copied.

## Corpus 2: synthetic contracts (TC3)

### What this data is

19 Markdown documents for 10 invented vendors (`SYN-01` to `SYN-10`): order forms, master terms and some renewal orders. `contracts/index.md` lists them. Gitignored, in `use_case/data/contracts/`. It is the retrieval corpus for the 10 questions in `use_case/evals/retrieval.jsonl`.

### How it was generated

- **Outline:** headings, 5 to 8 fields (including renewal date and notice period), value ranges and odd cases. Extracted with Claude Opus 5.5 from expired contracts I manage for my team, in a memory-off chat that was then deleted. Only the outline was kept, no contract text.
- **Generation:** Oct 24, `01_Product_Engineering/challenge/make_contracts.py`, with `anthropic/claude-sonnet-5-5` (set in `.env`; the script does not record the model). Vendors, products and prices are invented.
- **Checks:** 18 of 19 documents were fine on the first run. SYN-08 was regenerated without a divisions clause. I did a 5-point check on SYN-04, SYN-08 and SYN-10.

### What it can validate

Retrieval over realistic contract shapes: a notice period instead of a last day to say no, an order form that overrides the master terms (SYN-04: 90 days, not 60), a linked document that is missing (SYN-03 online terms: the agent must decline), and answers that need two documents (order + renewal).

### What it cannot validate

- Signatures: every signature block is blank, so answers often warn that the contract may be unsigned.
- Contract identity: the vendor is named only in the Parties section. The rag-v2 prefix takes the vendor from the file name; in production it comes from the contract record. Real PDFs may also name the vendor in headers and footers, and real names can collide or be abbreviated.
- Approval complexity: internal knowledge, never written in a contract.
- Variety: payment terms are only net 30 or net 45, and the documents are clean Markdown, not scanned PDFs.

### What it must never be compared against

Real contracts and what owners decided: they stay in the company's private system. Scores on this corpus say nothing about accuracy on real contracts.

### Why not the TC2 rows

TC2 rows are the output of this stage: values already extracted from a contract (renewal date, notice period, owner) that the agent turns into an alert or a vendor email. They contain no contract text, so they cannot test retrieval. Details in `use_case/decisions.md` (corpus row).

### Leakage check

- [X] No real vendor, product, price or person name.
- [X] Outline only: no contract text copied.
- [X] The questions in `retrieval.jsonl` were written by me as contract owner, using the sponsor's sheet, not generated from the contracts.
