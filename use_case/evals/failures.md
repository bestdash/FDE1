# Failure taxonomy (TC4 Step 1)

Read on 29 and 30 Oct 2026, by me as a contract owner: 49 traces.

- 40 answers: the 10 labelled questions in `retrieval.jsonl` answered by 4 runs (endpoint-v1, rag-v2b, dci-v1, dense-v1).
- 9 drafted messages: one model run in `01_Product_Engineering/challenge/solve_run1.txt`, one message per golden in `golden.jsonl`.

**17 of 49 traces had a failure** (16 of 40 answers, 1 of 9 messages). One trace (Q2 rag-v2b) shows two failures, so the counts below add up to 18.

| Rank | Failure | Count | Traces |
| --- | --- | --- | --- |
| 1 | Says something is missing that is in the documents (cause unknown: not retrieved or not found) | 7 | Q1 dense-v1, Q2 endpoint-v1, Q2 rag-v2b, Q2 dense-v1, Q3 endpoint-v1, Q4 dense-v1, Q7 rag-v2b |
| 2 | Brings in other vendors' contracts in an answer about one vendor | 5 | Q9 endpoint-v1, Q9 rag-v2b, Q9 dense-v1, Q10 endpoint-v1, Q10 rag-v2b |
| 3 | Date errors: the model works out dates itself (wrong arithmetic, or a past date treated as current) | 4 | Q1 dci-v1, Q2 rag-v2b, Q4 endpoint-v1, Q5 dci-v1 |
| 4 | Invents a doubt or claim that no fact supports | 1 | golden 6 message ("the owner may not have to accept the current deadline interpretation") |
| 4 | No answer: turn limit hit, cause unknown | 1 | Q10 dense-v1 |

Group 3 fix: today's date and all date calculations in code, not by the model.

## My criteria were less consistent than I assumed

- "About 31 December" was first too approximate for me; I accepted it when the answer cites the term, because I can check the date at once.
- A wrong fact and a missing fact are not the same.
- For "when does it end?" on a contract that renews automatically, a complete answer also gives the last day to give notice.
- Naming other vendors, or quoting their terms, fails. Exception: the user asks for a comparison (negotiation, usual practice).
- Q3: I expected one price; an answer with both prices (before and now) is better, because I can compare.
- Drafted messages: a small invention passes when it does not block the owner (golden 4); a doubt about a date that comes from the code fails (golden 6).
- The old scorers were far more generous than I am: expected terms + cited sources passed 29 of 30 answers in rag-v2b, dci-v1 and dense-v1 (I passed 19); the TC1 check (message type and act_by only) passed 9 of 9 messages (I passed 8).

## Not covered

- Q11 to Q13 (Step 6 questions) have no traces yet; they join the baseline run on Monday.
- The drafted messages were judged against the current goldens. The goldens change in Step 2 from the sponsor review (`decisions.md` line 23), before the baseline.
- Q3 was scored on the old wording ("last year"); the question is reworded and its label expects 16,000 and 18,000 for the baseline.
- Q8 gold also accepts SYN-09-terms#3 from the baseline on.
- Labels changed on 30 Oct, after Step 1, for the baseline: notice dates added to Q1, Q2, Q4; end_date added to Q4, Q5; term dates added to Q3.
