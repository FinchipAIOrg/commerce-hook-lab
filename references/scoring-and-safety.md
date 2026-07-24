# Scoring and safety

Read this before selecting production winners.

## Editorial scores

Score each dimension from 1 to 5:

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| `product_relevance` | Bait is unrelated | Connection arrives later | Product and hook connect naturally |
| `audience_fit` | Generic audience | Broad but plausible | Precise context and language |
| `first_frame_clarity` | Cannot picture it | Understandable with explanation | Immediately executable and legible |
| `curiosity` | No open question | Some tension | Clear information gap with a fair payoff |
| `proofability` | Cannot be proved | Needs additional asset | Visible or directly sourced proof |
| `feed_native` | Reads like corporate copy | Serviceable ad language | Credible creator or demo language |
| `model_feasibility` | Likely unstable or misleading | Needs references/editing | Simple, controllable generation |
| `distinctness` | Paraphrase | Some structural difference | Tests a materially different hypothesis |

Calculate `readiness_score` as the arithmetic mean rounded to one decimal. It is not a performance forecast.

## Decision rules

Use `advance` only when:

- No score is below 3.
- `product_relevance`, `first_frame_clarity`, and `proofability` are at least 4.
- The hook has valid supporting facts.
- Risk flags are empty or explicitly reviewed.

Use `revise` when the creative premise is sound but evidence, clarity, or feasibility is incomplete.

Use `reject` for unsupported bait, fake testimony, unverifiable transformation, prohibited claims, or a payoff the video cannot deliver.

## Risk flags

Use these stable values:

- `regulated-claim`
- `unsupported-number`
- `testimonial`
- `before-after`
- `comparison`
- `scarcity`
- `guarantee`
- `price-or-offer`
- `likeness-or-voice`
- `copyright`
- `ai-demonstration`
- `platform-policy`

Set `human_review_required: true` whenever any risk flag is present.

## Prohibited shortcuts

- Fake customer comments or reviews.
- AI avatars presented as real customers.
- Unsupported "sold out," "last chance," "#1," or sales count.
- Unqualified "best," "safest," "clinically proven," "guaranteed," or "works for everyone."
- Before/after footage that does not reflect the real product result.
- Competitor imitation, logo misuse, or unlicensed creator likeness.
- Numeric performance predictions for the proposed creative.
