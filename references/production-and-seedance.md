# Production and Seedance

Read this only when expanding selected hooks.

## Timeline

Create contiguous beats from `0` to the declared duration. Each beat includes:

- `start_seconds`
- `end_seconds`
- `visual`
- `audio`
- `text_overlay`

Place the hook in the first 0-3 seconds. Show or naturally connect the product early enough to resolve bait-and-switch risk.

## Generic AI-video prompt

Describe positive, observable instructions:

1. Format, duration, and aspect ratio.
2. Subject and product reference.
3. First-frame state.
4. Action sequence.
5. Camera and framing.
6. Performance and pacing.
7. Lighting and environment.
8. Sound or dialogue.
9. Continuity and product-accuracy constraints.

Do not rely on abstract adjectives in place of action.

## Seedance prompt

Use Chinese by default for Seedance delivery unless the user requests another language.

Include:

- `9:16`, exact duration, and intended fidelity.
- Official reference labels such as `@图片1` and `@视频1`.
- Time blocks such as `0-3秒`, `3-8秒`, and `8-15秒`.
- Concrete action, camera movement, sound, and spoken line per block.
- Product shape, color, label, and interaction continuity.
- A closing constraint that prevents generated subtitles, logos, or watermarks when those should be added in post.

Do not ask the model to render exact small text, price labels, legal copy, or UI overlays. Add those in post-production.

## Reference-first rule

Use a real product reference image when appearance matters. If no reference is available:

- State that exact product fidelity is unverified.
- Prefer real product footage for proof scenes.
- Use AI for creator setup, context, transitions, or non-claiming B-roll.

## Real-footage fallback

Recommend real footage instead of generation when:

- The hook depends on precise product performance.
- A before/after result must be truthful.
- Packaging, labels, dimensions, or material behavior must be exact.
- A real testimonial or creator identity is central.
