# Datasheet

<!-- Written in TC2, alongside your synthetic data. This file is committed; the
     data itself is not. -->

## What this data is

**Generated on:** 2026-10-15
**Generated from:** the `Request` / `Response` schema, the three variation axes below, and goldens 1 to 6 as examples. The goldens were written from memory with placeholders, not from real contracts. No real record was used.
**Rows:** 128 schema-valid rows in `synthetic_v1.jsonl` (gitignored)

## How it was generated

- **Model:** Claude Sonnet 4.6
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

## What it can validate

This is prototyping data: inputs that look like real renewal cases, with no labels a person verified.

- The pipeline runs end to end: generate, dedupe, validate.
- The generated inputs fit the current `Request` schema, for each combination of `time_left` and `record_completeness`.
- The validator rejects rows that do not fit, and the counts show how many.


## What it cannot validate

- Dedupe uses character overlap, which cannot see a one-word change in a structured field: one renew row was dropped as a twin of a terminate row.
- Validation checks types and allowed values only: not that dates are consistent, that `act_by` is right, or that the message matches the decision.
- Which message types appear depends on which goldens the prompt shows: with 3 seeds, run 1 produced zero decline rows.
- With less than 14 days left, the model wanted an urgent-warning message type the schema does not have. Urgency exists only in the message text.
- Rows reuse the goldens' invented dates (2026-10-12, 2026-11-15, 2026-12-15), so date variety is lower than it looks.

## What it must never be compared against

<!-- If you have real ground truth somewhere, say where, and say explicitly that
     these rows are not it. -->


## Leakage check — outward (what left)

- [X] No real record was used as a seed.
- [X] No real entity names, IDs, or identifiers appear.
- [X] No distinctive internal formats that would identify the firm.
- [X] Rare categories were generated, not copied.

## Leakage check — inward (what the eval shares with the training data)

**Are the goldens disjoint from anything the system was, or will be, tuned on?**
No: overlap. The goldens were written from memory, not from real contracts, but in TC1 the drafting prompt for each message type was adjusted until the goldens passed. A passing score on the goldens partly measures that tuning, not correctness on new cases. This file was generated from goldens 1 to 6, so it must never be used to tune anything the goldens later score: no prompt examples, no fine-tuning.

**Overlap between `golden.jsonl` and this file, by the dedupe measure:** 
122 of 128 rows within 0.5 of a golden. The number is inflated: every row shares the same field names, due to my input data structure, so it does not mean the content was copied.
