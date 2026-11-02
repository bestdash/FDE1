"""The TC4 baseline: python use_case/evals/run.py [--save]

Calls the endpoint on the 13 contract questions and scores every answer with the
4 model-free scorers and the judge. About 13 endpoint calls and 39 judge calls
(26 to calibrate, 13 to score). --save writes baseline.json; without it, the run
is compared against the saved baseline.
"""
import os
import random
import sys
from datetime import date

import harness as evals            # use_case/evals/harness.py: cases, scorers, endpoint, judge
from helpers import harness        # run, save, load, compare (harness.py put the repo root on sys.path)

BASELINE = evals.EVALS / "baseline.json"
HEADLINE = "missing_claim_judge"   # failures.md rank 1, the top line


def bootstrap_ci(scores, n_resamples=5000, level=0.95, seed=0):
    """95% interval for a mean, by resampling the scores we have (Session 7)."""
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(scores, k=len(scores))) / len(scores) for _ in range(n_resamples))
    low = means[int((1 - level) / 2 * n_resamples)]
    high = means[int((1 + level) / 2 * n_resamples) - 1]
    return low, high


def main():
    judge = evals.make_judge()
    print(judge.calibrate(evals.JUDGE_CASES, wrong_answer=evals.BAD_ANSWER))
    if not judge.calibration.passed:
        raise SystemExit("The judge failed calibration: no baseline from an unchecked judge.")

    scorers = {**evals.SCORERS, HEADLINE: evals.judge_scorer(judge)}
    report = harness.run(
        evals.CASES, evals.endpoint, scorers, name="week4-baseline",
        meta={"date": date.today().isoformat(), "llm_model": os.environ.get("LLM_MODEL"),
              "judge_model": os.environ.get("JUDGE_MODEL"), "calibration": str(judge.calibration)},
        progress=lambda done, total: print(f"  {done}/{total}", flush=True))
    print(report)
    evals.show_failures(report)

    scores = [result.scores[HEADLINE] for result in report.results]
    mean = sum(scores) / len(scores)
    low, high = bootstrap_ci(scores)
    report.meta["headline"] = {"scorer": HEADLINE, "mean": mean, "ci95": [low, high], "n": len(scores)}
    print(f"Headline {HEADLINE}: {mean:.3f}, 95% CI [{low:.3f}, {high:.3f}], n={len(scores)}")

    if "--save" in sys.argv:
        harness.save(report, BASELINE)
        print(f"saved {BASELINE.name}")
    if not BASELINE.exists():
        raise SystemExit("No baseline.json yet: run once with --save.")
    print(harness.compare(harness.load(BASELINE), report))


if __name__ == "__main__":
    main()
