# Retrieval results

One line per run. Full answers in `runs/<run>.md`.

## Findings: rag-v1 vs rag-v2

Adding the contract's identity (file, vendor, title) to every chunk raised pass from 7/10 to 10/10 and cited gold from 5/9 to 9/9, with 34 calls instead of 60 and half the evidence (72,791 vs 146,122 chars). A repeat of rag-v2 (rag-v2b) gave the same 10/10 and 9/9, but 17% more evidence: quality held, while cost moves 15 to 20% between runs even at temperature 0.

The most important fix is Q1. rag-v1 answered 60 days with confidence, but the order form overrides the agreement to 90 days, and the override section was never retrieved. An alert built on that answer would be 30 days late.

Declines are the most expensive answer. In rag-v2, Q10 took 9 calls and 25,801 chars. Measured in rag-v2b, it used 39% of the run's input tokens and 33% of its cost. My estimate before measuring was 57%: it assumed one search per turn, but the model often runs several searches in one turn. The cause is the tool loop: every turn sends all earlier evidence again, so cost grows with the number of searches, not only with the evidence found. DCI answered that question: its decline took 4 calls and $0.033, against 6 calls and $0.081 in rag-v2b, by reading whole pages rather than by grep.

Estimated cost for 10 questions on Sonnet 5.5 ($2 in / $10 out per million tokens): rag-v1 about $0.17 to $0.50, rag-v2 about $0.12 to $0.27. Measured in rag-v2b: $0.25 for 10 questions (82,167 tokens in, 8,087 out); output is a third of the cost.

Dates, changed Oct 26: the endpoint gets no date, and the model still computes deadlines from the stated terms, labelled as its own calculation, so the endpoint stays the rag-v2 setup measured here. A code date tool comes in Week 4, measured as its own run. In the endpoint, the model once gave 2 April 2028 instead of 1 April (89 days, so too late). rag-v2 gave a notice deadline (1 Sep 2026) that had already passed, without saying so.

## Findings: three techniques

Shipped: rag-v2. Rejected: DCI and dense. Reasons and switch conditions: `use_case/decisions.md`, Week 3 retrieval row.

Dense (dense-v1) was weak on exact names: for "cancellation period Vendor04" its top hit was the empty title chunk and its third hit another vendor. Its decline question hit the turn limit after 9 searches.

The endpoint run (endpoint-v1, through `answer_contract_question`) cited all gold sections on 8 of 9 answerable questions. Q2 missed the master agreement and told the user to ask the vendor for it, although it is in the corpus. That loop did not log tokens.

**Embedding tokens: 0, measured.** rag-v2 and DCI embed nothing; dense used bge-small-en-v1.5 locally through fastembed, so nothing was sent.

## Runs

| Run | Date | Change | Pass | Cited all gold | Calls | Evidence chars | Tokens in | Tokens out | Cost $ | Avg latency s | Hit max_turns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [rag-v1](runs/rag-v1.md) | 2026-10-24 | baseline: S5 chunks, vendor name only in Parties | 7/10 | 5/9 | 60 | 146,122 | not logged | not logged | est. 0.17 to 0.50 | 10.1 | 2 |
| [rag-v2](runs/rag-v2.md) | 2026-10-24 | file, vendor and title prefixed to every chunk | 10/10 | 9/9 | 34 | 72,791 | not logged | not logged | est. 0.12 to 0.27 | 7.2 | 0 |
| [rag-v2b](runs/rag-v2b.md) | 2026-10-25 | rag-v2 repeat, tokens logged | 10/10 | 9/9 | 32 | 84,846 | 82,167 | 8,087 | 0.25 | 9.9 | 0 |
| [dci-v1](runs/dci-v1.md) | 2026-10-25 | DCI: index + grep (40 lines) + read_page, no chunks | 10/10 | 9/9 | 40 | 127,172 | 104,067 | 7,916 | 0.29 | 8.6 | 0 |
| [dense-v1](runs/dense-v1.md) | 2026-10-25 | dense: bge-small-en-v1.5 local, same chunks, cosine | 9/10 | 8/9 | 34 | 82,773 | 79,745 | 6,952 | 0.23 | 8.9 | 1 |
| [endpoint-v1](runs/endpoint-v1.md) | 2026-10-26 | rag-v2 through the `answer_contract_question` endpoint | not scored | 8/9 | not logged | not logged | not logged | not logged | not logged | not logged | 0 |
