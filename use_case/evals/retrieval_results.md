# Retrieval results

One line per run. Full answers in `runs/<run>.md`.

## Findings: rag-v1 vs rag-v2

Adding the contract's identity (file, vendor, title) to every chunk raised pass from 7/10 to 10/10 and cited gold from 5/9 to 9/9, with 34 calls instead of 60 and half the evidence (72,791 vs 146,122 chars). One run each, so not yet proof.

The most important fix is Q1. rag-v1 answered 60 days with confidence, but the order form overrides the agreement to 90 days, and the override section was never retrieved. An alert built on that answer would be 30 days late.

Declines are the most expensive answer. In rag-v2, Q10 took 9 calls and 25,801 chars, and it makes up about 57% of the run's re-sent evidence (an estimate: tokens were not logged). The cause is the tool loop: every turn sends all earlier evidence again, so cost grows with the number of searches, not only with the evidence found. rag-v3 tests whether grep can say "not found" sooner.

Estimated cost for 10 questions on Sonnet 5.5 ($2 in / $10 out per million tokens): rag-v1 about $0.17 to $0.50, rag-v2 about $0.12 to $0.27. From rag-v3 on, tokens are logged per question.

The endpoint will get today's date, and code, not the model, will calculate deadlines. rag-v2 gave a notice deadline (1 Sep 2026) that had already passed, without saying so.

## Runs

| Run | Date | Change | Pass | Cited all gold | Calls | Evidence chars | Avg latency s | Hit max_turns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [rag-v1](runs/rag-v1.md) | 2026-10-24 | baseline: S5 chunks, vendor name only in Parties | 7/10 | 5/9 | 60 | 146,122 | 10.1 | 2 |
| [rag-v2](runs/rag-v2.md) | 2026-10-24 | file, vendor and title prefixed to every chunk | 10/10 | 9/9 | 34 | 72,791 | 7.2 | 0 |
