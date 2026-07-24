# Product truth model

Read this before writing hooks.

## Ledger types

| Prefix | Use |
|---|---|
| `F` | Product, feature, mechanism, offer, price, usage, or verified outcome |
| `Q` | Verbatim customer review or testimonial |
| `R` | Restriction, qualifier, uncertainty, prohibited claim, or missing proof |

Each entry requires:

- `id`
- `kind`
- `statement`
- `source_locator`
- `status`
- `visual_proof`
- `requires_human_review`
- `required_companion_ids`

## Status

- `verified`: Supported by an authoritative supplied source or observable product property.
- `user-provided`: Supplied by the user but not independently verified.
- `uncertain`: Ambiguous, conflicting, inferred, or missing adequate support.
- `prohibited`: Must not be used as a promotional claim.

`user-provided` does not mean independently verified. Require human review for sensitive, comparative, regulated, time-sensitive, testimonial, or outcome claims.

## Extraction rules

1. Preserve scope and qualifiers. Do not turn "helps remove loose pet hair" into "removes all pet hair."
2. Keep price, discount, currency, bundle, region, and date together.
3. Store a review verbatim. Do not silently improve grammar or results.
4. Record the exact proof asset needed for a visual claim.
5. Add a restriction when a strong claim lacks evidence.
6. Link facts to required qualifiers with `required_companion_ids`.

## Sensitive claim classes

Require human review for:

- Health, medical, cosmetic outcome, supplement, safety, financial, legal, or child-directed claims.
- Before/after transformations.
- Comparative superiority.
- Environmental or sustainability claims.
- Testimonials, sales counts, rankings, scarcity, deadlines, guarantees, and quantified results.
- Claims based on AI-generated demonstrations.

## Rights

Record source rights as `owned`, `licensed`, `permission`, or `unknown`.

When rights are unknown:

- Use the material for analysis only.
- Do not reproduce a third party's protected copy, voice, face, footage, or distinctive execution.
- Extract general creative structure rather than making a close substitute.
