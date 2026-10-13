# Step 13: cost per draft and model comparison

Run on 2026-10-13 at commit `06e261d`. Model measured: `anthropic/claude-sonnet-4-6`. 9 goldens, one call each, no caching, no batch.

Labels: **measured** = read from a run. **looked up** = taken from a public page. **your input** = a claim about your company.

## 1. Token spend per golden (measured)

| Golden | message_type | Tokens in | Tokens out | Seconds |
| ---: | --- | ---: | ---: | ---: |
| 1 | termination_draft | 580 | 99 | 3.79 |
| 2 | renewal_review_email | 704 | 223 | 3.94 |
| 3 | late_notice_to_owner | 479 | 169 | 4.08 |
| 4 | missing_file_notice | 411 | 107 | 2.77 |
| 5 | escalation_to_procurement | 458 | 114 | 2.75 |
| 6 | escalation_to_procurement | 459 | 166 | 3.3 |
| 7 | termination_draft | 579 | 124 | 2.93 |
| 8 | termination_draft | 580 | 102 | 2.24 |
| 9 | renewal_review_email | 717 | 263 | 4.34 |
| **mean** | | **552** | **152** | **3.3** |

Latency over 9 calls: p50 2.9s, p95 4.3s (nine samples, so p95 is the slowest call).

## 2. Prices (looked up)

Standard rates in USD per million tokens, checked 2026-10-13. Haiku 5.5 is the rate for prompts up to 100,000 tokens; ours are far below that.

| Model | $/1M in | $/1M out | Source |
| --- | ---: | ---: | --- |
| Claude Haiku 5.5 | 0.1 | 0.5 | https://platform.claude.com/docs/en/about-claude/pricing |
| Claude Haiku 4.5 | 1 | 5 | https://platform.claude.com/docs/en/about-claude/pricing |
| Claude Sonnet 5.5 | 2 | 10 | https://platform.claude.com/docs/en/about-claude/pricing |
| Claude Sonnet 5 | 2 | 10 | https://platform.claude.com/docs/en/about-claude/pricing |
| Claude Sonnet 4.6 | 3 | 15 | https://platform.claude.com/docs/en/about-claude/pricing |
| Claude Sonnet 4.5 | 3 | 15 | https://platform.claude.com/docs/en/about-claude/pricing |
| Claude Opus 5.5 | 4 | 20 | https://platform.claude.com/docs/en/about-claude/pricing |
| Claude Opus 5 | 5 | 25 | https://platform.claude.com/docs/en/about-claude/pricing |
| Claude Opus 4.5 | 5 | 25 | https://platform.claude.com/docs/en/about-claude/pricing |
| gpt-4.1-mini | 0.4 | 1.6 | https://developers.openai.com/api/docs/models/gpt-4.1-mini |

## 3. Cost of one draft by model

Priced on the mean token counts above (measured on `anthropic/claude-sonnet-4-6`). Rows other than the measured model are estimates.

| Model | Cost per draft | Drafts per $1 | vs measured model |
| --- | ---: | ---: | ---: |
| Claude Haiku 5.5 | $0.00013 | 7,626 | 0.03x |
| gpt-4.1-mini | $0.00046 | 2,156 | 0.12x |
| Claude Haiku 4.5 | $0.00131 | 763 | 0.33x |
| Claude Sonnet 5.5 | $0.00262 | 381 | 0.67x |
| Claude Sonnet 5 | $0.00262 | 381 | 0.67x |
| Claude Sonnet 4.6 (measured) | $0.00393 | 254 | 1.00x |
| Claude Sonnet 4.5 | $0.00393 | 254 | 1.00x |
| Claude Opus 5.5 | $0.00525 | 191 | 1.33x |
| Claude Opus 5 | $0.00656 | 153 | 1.67x |
| Claude Opus 4.5 | $0.00656 | 153 | 1.67x |

Spread on `anthropic/claude-sonnet-4-6`: cheapest draft $0.00284, dearest $0.00610, mean $0.00393.

By message_type:

| message_type | Drafts | Mean in | Mean out | Mean cost |
| --- | ---: | ---: | ---: | ---: |
| escalation_to_procurement | 2 | 458 | 140 | $0.00348 |
| late_notice_to_owner | 1 | 479 | 169 | $0.00397 |
| missing_file_notice | 1 | 411 | 107 | $0.00284 |
| renewal_review_email | 2 | 710 | 243 | $0.00578 |
| termination_draft | 3 | 580 | 108 | $0.00336 |

## 4. Annual math (your inputs)

- drafts per year: 720 / **840** / 960 (low / base / high; **your input**: 120 contracts x 3 to 4 review emails + 3 to 4 negotiation emails)
- minutes per manual draft: 10 / **15** / 20 (**looked up**, not timed: 10 simple SaaS, 20 complex, preparation included)
- loaded $/hour: 60 (**your input**: about $120K a year divided by 2,000 hours, salary only)
- every draft priced like `renewal_review_email`: mean 710 in, 243 out (**measured**), the dearest type, because negotiation is not built yet

Base scenario: 840 drafts, 15 minutes. Human per year is the same for every model: 15 / 60 x $60 x 840 = $12,600.00.

| Model | Cost per draft | Model per year | Human per year | Ratio | Band |
| --- | ---: | ---: | ---: | ---: | --- |
| Claude Haiku 5.5 | $0.00019 | $0.16 | $12,600.00 | 77,902x | comfortable |
| gpt-4.1-mini | $0.00067 | $0.57 | $12,600.00 | 22,288x | comfortable |
| Claude Haiku 4.5 | $0.00193 | $1.62 | $12,600.00 | 7,790x | comfortable |
| Claude Sonnet 5.5 | $0.00385 | $3.23 | $12,600.00 | 3,895x | comfortable |
| Claude Sonnet 5 | $0.00385 | $3.23 | $12,600.00 | 3,895x | comfortable |
| Claude Sonnet 4.6 (measured) | $0.00578 | $4.85 | $12,600.00 | 2,597x | comfortable |
| Claude Sonnet 4.5 | $0.00578 | $4.85 | $12,600.00 | 2,597x | comfortable |
| Claude Opus 5.5 | $0.00770 | $6.47 | $12,600.00 | 1,948x | comfortable |
| Claude Opus 5 | $0.00963 | $8.09 | $12,600.00 | 1,558x | comfortable |
| Claude Opus 4.5 | $0.00963 | $8.09 | $12,600.00 | 1,558x | comfortable |

Scenarios on `anthropic/claude-sonnet-4-6` (model per year / ratio). Rows are drafts per year, columns are minutes per manual draft.

| Drafts per year | 10 min | 15 min | 20 min |
| ---: | ---: | ---: | ---: |
| 720 | $4.16 / 1,731x | $4.16 / 2,597x | $4.16 / 3,462x |
| 840 | $4.85 / 1,731x | $4.85 / 2,597x | $4.85 / 3,462x |
| 960 | $5.55 / 1,731x | $5.55 / 2,597x | $5.55 / 3,462x |

Maximum budget: high volume (960 drafts) with every draft as dear as the dearest golden ($0.00610) is **$5.85 per year** on `anthropic/claude-sonnet-4-6`.

Formulas, as in the README: model per year = cost per draft x drafts per year; human per year = minutes / 60 x loaded $/hour x drafts per year; ratio = human / model. The README bands stop at 20x (comfortable); every row here is far above it.

## 5. Caveats

- One run, nine goldens. The goldens are hand-picked cases, not a sample of real traffic, so the mean is a rough guide.
- Other models are priced on this model's token counts. Their tokenizers differ, and a different model also writes a different length of reply.
- Standard rates only. Prompt caching and batch discounts would lower the figures; the long, repeated rules block in the prompt is a caching candidate.
- Cost is not quality. A cheaper model has to pass the same goldens before its price counts.
- Negotiation emails have no message_type yet. They are priced like renewal_review_email, so the real cost of that part may differ once it is built.
- The hourly rate is salary only, with no overhead, so human cost is understated and the ratio is conservative.
- With a ratio this high, model cost is unlikely to stop adoption. Latency, approval and quality are the likelier blockers.
