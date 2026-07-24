---
name: commerce-hook-lab
description: Turn product pages, briefs, images, reviews, approved claims, and offer details into evidence-backed short-form commerce video hooks, creative variants, production scripts, and AI-video prompts. Use when the user asks for TikTok Shop, Reels, Shorts, UGC, paid-social, product-demo, ecommerce, or 带货视频 hooks; wants to improve the first 1-3 seconds of an ad; needs spoken, visual, and text-overlay hooks; wants Seedance-ready prompts; or needs a testable hook matrix with claim traceability and deterministic QA.
---

# Commerce Hook Lab

Create commerce hooks that can be proved on screen, produced as short-form video, and tested as controlled creative variants. Never predict virality, CTR, CVR, sales, or platform approval.

## Select the run

- `quick`: Generate 6 hooks and expand the strongest one. Use only when the user explicitly asks for a small or fast set.
- `lab`: Generate 12 hooks across distinct angles and expand the strongest 3. Use by default.
- `audit`: Diagnose supplied hooks or scripts, repair weak openings, and return before/after evidence.
- `iterate`: Use supplied performance data to create the next test round. Treat correlations as local observations, not universal rules.

Record the mode in `hook-pack.json`.

## Gather inputs

Use information already supplied. Ask only when a missing answer would materially change the creative.

Required:

- Product information or an accessible product source.
- Intended audience or enough context to infer one and label the assumption.
- Platform, duration, and objective. Default to vertical 9:16, 15 seconds, and `hold` when omitted.
- Rights status for supplied images, reviews, competitor material, and likenesses: `owned`, `licensed`, `permission`, or `unknown`.

Helpful:

- Price, promotion, proof assets, real reviews, objections, brand voice, prohibited phrases, and current performance data.
- Product or character reference images for AI-video generation.

If a URL cannot be accessed, request pasted content or screenshots. Do not fill gaps from memory.

## Load references

- Always read [product-truth.md](references/product-truth.md) before extracting facts.
- Always read [hook-system.md](references/hook-system.md) before generating hooks.
- Always read [output-contract.md](references/output-contract.md) before writing the package.
- Always read [scoring-and-safety.md](references/scoring-and-safety.md) before selecting winners.
- Read [production-and-seedance.md](references/production-and-seedance.md) only when producing scripts or AI-video prompts.

## Workflow

### 1. Build the product truth ledger

Normalize each usable statement into a stable fact:

- `Fxx`: product, offer, price, feature, mechanism, usage, or verified result.
- `Qxx`: verbatim review or testimonial.
- `Rxx`: restriction, qualifier, uncertainty, or prohibited claim.

Record a precise `source_locator`, status, visual proof, and human-review flag. Keep uncertain statements in the ledger but do not present them as facts.

### 2. Define the audience and test

State:

- Persona, context, pain, desire, and likely awareness stage.
- One objective: `hold`, `click`, `add-to-cart`, or `conversion`.
- One variable to change in the test. Default to the opening hook.
- Controlled variables such as body, CTA, duration, creator, offer, audience, and placement.

Do not claim that an inferred persona or awareness stage is researched truth.

### 3. Create a real hook matrix

Generate 12 hooks in `lab` mode and 6 in `quick` mode. Cover materially distinct commerce angles rather than paraphrasing one line.

Every hook must include:

- Spoken opening.
- First-frame visual action.
- Text overlay.
- Angle and archetype.
- Supporting fact IDs.
- Proof plan.
- Risk flags and human-review status.
- Eight editorial scores from 1 to 5.
- Decision: `advance`, `revise`, or `reject`.

Do not repeat the same promise in all three channels. Let the visual prove, the spoken line open the loop, and the overlay orient the viewer.

### 4. Score without pretending to predict performance

Score product relevance, audience fit, first-frame clarity, curiosity, proofability, feed-native quality, model feasibility, and distinctness. Use [scoring-and-safety.md](references/scoring-and-safety.md).

Scores describe readiness for a test, not predicted market performance. Advance only hooks that:

- Use at least one valid fact.
- Have an executable first frame.
- Can deliver the promised payoff.
- Do not rely on an unsupported, prohibited, or disguised claim.

### 5. Expand the winners

In `lab` mode, expand exactly 3 advanced hooks into production packs. In `quick` mode, expand 1.

Each pack must contain:

- A continuous timeline beginning at 0 and ending at the declared duration.
- Visual, audio or spoken direction, and optional overlay for every beat.
- A CTA consistent with the objective.
- A generic AI-video prompt.
- A Seedance prompt with references, timestamps, aspect ratio, continuity, and text-generation constraints.
- Practical notes for real footage when AI generation would misrepresent the product.

Do not claim that a video, image, actor, voice, or ad has been generated unless the corresponding tool actually produced it.

### 6. Write the controlled test plan

Create a hypothesis for the selected hook family. List the variant hook IDs, controlled variables, primary metric, optional secondary metrics, and interpretation rule.

Never invent a benchmark or stopping threshold. If the user provides none, use `not provided` and explain what the media buyer should define.

### 7. Assemble and validate

Write:

```text
commerce-hook-output/
├── product-truth.md
├── audience-and-test.md
├── hook-matrix.md
├── hook-pack.json
├── production/
│   └── <pack-id>.md
└── qa-report.json
```

Use `hook-pack.json` as the machine-readable source of truth. Follow [output-contract.md](references/output-contract.md).

Run:

```bash
python3 <skill-dir>/scripts/validate_hook_pack.py \
  commerce-hook-output/hook-pack.json \
  --report commerce-hook-output/qa-report.json
```

Fix all errors before delivery. Review warnings individually and preserve them in the report.

## Quality gates

Fail the run when:

- A hook has no supporting fact.
- A hook uses a prohibited fact or an uncertain fact without review.
- A number, price, testimonial, result, comparison, or scarcity claim is unsupported.
- Spoken, visual, and overlay channels merely repeat one another.
- Production timelines overlap, contain gaps, or disagree with duration.
- A production pack references a rejected or unknown hook.
- Variants are too similar to represent a meaningful test.
- Required package files are missing or disagree with the manifest.

Treat taste, authenticity, legal approval, platform approval, and likely performance as human-review judgments.

## Boundaries

- Do not promise virality, revenue, ROAS, CTR, CVR, approval, or sales.
- Do not fabricate reviews, quantities sold, discounts, deadlines, comparisons, before/after results, guarantees, or creator experience.
- Do not convert an AI actor into a fake customer testimonial.
- Do not imitate a living creator, customer, or competitor without permission.
- Do not bypass advertising, platform, copyright, likeness, or regulated-claim requirements.
- Do not publish, upload, render, or spend ad budget without separate authorization.
- Verify current platform rules before publication when browsing is available.

## Example request

> Turn this product page and three approved reviews into 12 TikTok Shop hooks. Keep every claim traceable, expand the strongest three into 15-second scripts, and give me Seedance prompts plus a controlled test plan.

Expected result: a truth ledger, distinct hook matrix, three production packs, machine-readable manifest, and passing QA report, not a list of unsupported "viral hooks."
