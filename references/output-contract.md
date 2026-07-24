# Output contract

Write a package named `commerce-hook-output`.

## Files

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

`hook-pack.json` is the source of truth. Markdown files must agree with it.

## Manifest

Follow `schemas/hook-pack.schema.json`.

Required top-level keys:

- `schema_version`
- `run`
- `product`
- `audience`
- `objective`
- `facts`
- `hooks`
- `production_packs`
- `test_plan`
- `review`

## IDs

- Facts: `F01`, `Q01`, `R01`
- Hooks: `H01`
- Production packs: `P01`

Use unique IDs and stable ordering.

## Production files

Set each production pack's `content_file` to `production/<pack-id>.md`. The file must contain:

- Selected hook and evidence IDs.
- Timeline.
- Spoken, visual, overlay, and CTA direction.
- Generic prompt.
- Seedance prompt.
- Real-footage fallback notes.

## Review

Record:

- `unsupported_claims`
- `human_review_items`
- `limitations`

Use empty arrays when none exist. Do not omit them.

## Validator

Run:

```bash
python3 scripts/validate_hook_pack.py commerce-hook-output/hook-pack.json \
  --report commerce-hook-output/qa-report.json
```

The validator checks deterministic structure and traceability. It cannot prove legal compliance, platform approval, authenticity, creative quality, or performance.
