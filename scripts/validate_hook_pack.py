#!/usr/bin/env python3
"""Validate a Commerce Hook Lab package with the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


MODES = {"quick", "lab", "audit", "iterate"}
RIGHTS = {"owned", "licensed", "permission", "unknown"}
AWARENESS_STAGES = {
    "unaware",
    "problem-aware",
    "solution-aware",
    "product-aware",
    "most-aware",
}
GOALS = {"hold", "click", "add-to-cart", "conversion"}
FACT_STATUSES = {"verified", "user-provided", "uncertain", "prohibited"}
FACT_KINDS = {
    "product",
    "feature",
    "mechanism",
    "usage",
    "price",
    "offer",
    "result",
    "review",
    "restriction",
}
DECISIONS = {"advance", "revise", "reject"}
RISK_FLAGS = {
    "regulated-claim",
    "unsupported-number",
    "testimonial",
    "before-after",
    "comparison",
    "scarcity",
    "guarantee",
    "price-or-offer",
    "likeness-or-voice",
    "copyright",
    "ai-demonstration",
    "platform-policy",
}
SCORE_KEYS = {
    "product_relevance",
    "audience_fit",
    "first_frame_clarity",
    "curiosity",
    "proofability",
    "feed_native",
    "model_feasibility",
    "distinctness",
}
FACT_ID_RE = re.compile(r"^[FQR][0-9]{2,}$")
HOOK_ID_RE = re.compile(r"^H[0-9]{2,}$")
PACK_ID_RE = re.compile(r"^P[0-9]{2,}$")
ASPECT_RE = re.compile(r"^[0-9]+:[0-9]+$")
NUMBER_RE = re.compile(r"(?<![A-Za-z])(?:\d+(?:[.,]\d+)?%?|\$\d+(?:[.,]\d+)?)")
CJK_RE = re.compile(r"[\u3400-\u9fff]")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)?")
PLACEHOLDER_RE = re.compile(r"\[(?:TODO|TBD|INSERT|PLACEHOLDER)[^\]]*\]", re.IGNORECASE)
GENERIC_HYPE = {
    "game changer",
    "revolutionary",
    "you won't believe",
    "mind-blowing",
    "best ever",
    "works for everyone",
}
REQUIRED_PACKAGE_FILES = {
    "product-truth.md",
    "audience-and-test.md",
    "hook-matrix.md",
}


def issue(level: str, code: str, path: str, message: str) -> dict[str, str]:
    return {"level": level, "code": code, "path": path, "message": message}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any, *, allow_empty: bool = True) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(nonempty(item) for item in value)
    )


def normalized_text(value: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", value.casefold(), flags=re.UNICODE))


def similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalized_text(left), normalized_text(right)).ratio()


def speech_seconds(value: str) -> float:
    cjk = len(CJK_RE.findall(value))
    latin_words = len(WORD_RE.findall(CJK_RE.sub(" ", value)))
    return (cjk / 4.0) + (latin_words / 3.0)


def overlay_units(value: str) -> tuple[int, int]:
    return len(CJK_RE.findall(value)), len(WORD_RE.findall(CJK_RE.sub(" ", value)))


def build_report(issues: list[dict[str, str]], facts: int, hooks: int, packs: int) -> dict[str, Any]:
    errors = sum(item["level"] == "error" for item in issues)
    warnings = sum(item["level"] == "warning" for item in issues)
    return {
        "status": "fail" if errors else "pass",
        "summary": {
            "errors": errors,
            "warnings": warnings,
            "facts": facts,
            "hooks": hooks,
            "production_packs": packs,
        },
        "issues": issues,
        "limitations": [
            "A passing report does not predict creative performance.",
            "A passing report does not establish legal or platform-policy approval.",
            "Editorial scores and audience assumptions still require human judgment.",
        ],
    }


def validate_pack(
    data: Any,
    manifest_path: Path,
    *,
    max_similarity: float = 0.82,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    base_dir = manifest_path.parent.resolve()

    def add(level: str, code: str, path: str, message: str) -> None:
        issues.append(issue(level, code, path, message))

    if not isinstance(data, dict):
        add("error", "manifest_type", "$", "Manifest root must be an object.")
        return build_report(issues, 0, 0, 0)

    required_top = {
        "schema_version",
        "run",
        "product",
        "audience",
        "objective",
        "facts",
        "hooks",
        "production_packs",
        "test_plan",
        "review",
    }
    for key in sorted(required_top):
        if key not in data:
            add("error", "missing_top_level_key", f"$.{key}", f"Missing required key: {key}.")
    for key in data:
        if key not in required_top:
            add("warning", "unknown_top_level_key", f"$.{key}", "Unknown top-level key.")

    if data.get("schema_version") != "1.0":
        add("error", "schema_version", "$.schema_version", "schema_version must be '1.0'.")

    mode: str | None = None
    run = data.get("run")
    if not isinstance(run, dict):
        add("error", "run_type", "$.run", "run must be an object.")
    else:
        mode = run.get("mode")
        if mode not in MODES:
            add("error", "invalid_mode", "$.run.mode", f"mode must be one of {sorted(MODES)}.")
        for key in ("language", "created_at"):
            if not nonempty(run.get(key)):
                add("error", "required_string", f"$.run.{key}", f"{key} must be non-empty.")

    product = data.get("product")
    if not isinstance(product, dict):
        add("error", "product_type", "$.product", "product must be an object.")
    else:
        for key in ("name", "category", "source_summary"):
            if not nonempty(product.get(key)):
                add("error", "required_string", f"$.product.{key}", f"{key} must be non-empty.")
        if product.get("source_rights") not in RIGHTS:
            add(
                "error",
                "invalid_source_rights",
                "$.product.source_rights",
                f"source_rights must be one of {sorted(RIGHTS)}.",
            )

    audience = data.get("audience")
    if not isinstance(audience, dict):
        add("error", "audience_type", "$.audience", "audience must be an object.")
    else:
        for key in ("persona", "context", "pain", "desire"):
            if not nonempty(audience.get(key)):
                add("error", "required_string", f"$.audience.{key}", f"{key} must be non-empty.")
        if audience.get("awareness_stage") not in AWARENESS_STAGES:
            add(
                "error",
                "invalid_awareness_stage",
                "$.audience.awareness_stage",
                f"awareness_stage must be one of {sorted(AWARENESS_STAGES)}.",
            )
        if not isinstance(audience.get("is_inferred"), bool):
            add("error", "invalid_inferred_flag", "$.audience.is_inferred", "is_inferred must be boolean.")

    objective = data.get("objective")
    objective_duration: float | None = None
    aspect_ratio: str | None = None
    if not isinstance(objective, dict):
        add("error", "objective_type", "$.objective", "objective must be an object.")
    else:
        if not nonempty(objective.get("platform")):
            add("error", "required_string", "$.objective.platform", "platform must be non-empty.")
        aspect_ratio = objective.get("aspect_ratio")
        if not nonempty(aspect_ratio) or not ASPECT_RE.fullmatch(aspect_ratio):
            add("error", "invalid_aspect_ratio", "$.objective.aspect_ratio", "aspect_ratio must look like 9:16.")
        raw_duration = objective.get("duration_seconds")
        if not isinstance(raw_duration, (int, float)) or isinstance(raw_duration, bool) or raw_duration <= 0:
            add("error", "invalid_duration", "$.objective.duration_seconds", "duration_seconds must be positive.")
        else:
            objective_duration = float(raw_duration)
        if objective.get("goal") not in GOALS:
            add("error", "invalid_goal", "$.objective.goal", f"goal must be one of {sorted(GOALS)}.")

    facts_raw = data.get("facts")
    facts: dict[str, dict[str, Any]] = {}
    if not isinstance(facts_raw, list) or not facts_raw:
        add("error", "invalid_facts", "$.facts", "facts must be a non-empty array.")
        facts_raw = []

    for index, fact in enumerate(facts_raw):
        path = f"$.facts[{index}]"
        if not isinstance(fact, dict):
            add("error", "fact_type", path, "Fact must be an object.")
            continue
        fact_id = fact.get("id")
        if not nonempty(fact_id) or not FACT_ID_RE.fullmatch(fact_id):
            add("error", "invalid_fact_id", f"{path}.id", "Fact ID must match F01, Q01, or R01.")
        elif fact_id in facts:
            add("error", "duplicate_fact_id", f"{path}.id", f"Duplicate fact ID: {fact_id}.")
        else:
            facts[fact_id] = fact
        if fact.get("kind") not in FACT_KINDS:
            add("error", "invalid_fact_kind", f"{path}.kind", f"kind must be one of {sorted(FACT_KINDS)}.")
        for key in ("statement", "source_locator", "visual_proof"):
            if not nonempty(fact.get(key)):
                add("error", "required_string", f"{path}.{key}", f"{key} must be non-empty.")
        if fact.get("status") not in FACT_STATUSES:
            add("error", "invalid_fact_status", f"{path}.status", f"status must be one of {sorted(FACT_STATUSES)}.")
        if not isinstance(fact.get("requires_human_review"), bool):
            add("error", "invalid_review_flag", f"{path}.requires_human_review", "Must be boolean.")
        companions = fact.get("required_companion_ids")
        if not string_list(companions):
            add("error", "invalid_companion_ids", f"{path}.required_companion_ids", "Must be a string array.")

    for index, fact in enumerate(facts_raw):
        if not isinstance(fact, dict):
            continue
        fact_id = fact.get("id")
        companions = fact.get("required_companion_ids", [])
        if not isinstance(companions, list):
            continue
        if len(companions) != len(set(companions)):
            add("error", "duplicate_companion_id", f"$.facts[{index}].required_companion_ids", "Companion IDs must be unique.")
        for companion in companions:
            if companion == fact_id:
                add("error", "self_companion", f"$.facts[{index}].required_companion_ids", "A fact cannot require itself.")
            elif companion not in facts:
                add("error", "unknown_companion_id", f"$.facts[{index}].required_companion_ids", f"Unknown fact: {companion}.")

    hooks_raw = data.get("hooks")
    hooks: dict[str, dict[str, Any]] = {}
    hook_texts: list[tuple[str, str]] = []
    if not isinstance(hooks_raw, list) or not hooks_raw:
        add("error", "invalid_hooks", "$.hooks", "hooks must be a non-empty array.")
        hooks_raw = []
    if mode == "lab" and len(hooks_raw) != 12:
        add("error", "lab_hook_count", "$.hooks", "lab mode requires exactly 12 hooks.")
    if mode == "quick" and len(hooks_raw) != 6:
        add("error", "quick_hook_count", "$.hooks", "quick mode requires exactly 6 hooks.")

    for index, hook in enumerate(hooks_raw):
        path = f"$.hooks[{index}]"
        if not isinstance(hook, dict):
            add("error", "hook_type", path, "Hook must be an object.")
            continue
        hook_id = hook.get("id")
        if not nonempty(hook_id) or not HOOK_ID_RE.fullmatch(hook_id):
            add("error", "invalid_hook_id", f"{path}.id", "Hook ID must match H01.")
        elif hook_id in hooks:
            add("error", "duplicate_hook_id", f"{path}.id", f"Duplicate hook ID: {hook_id}.")
        else:
            hooks[hook_id] = hook

        for key in ("angle", "archetype", "spoken", "visual", "text_overlay", "proof_plan"):
            if not nonempty(hook.get(key)):
                add("error", "required_string", f"{path}.{key}", f"{key} must be non-empty.")
            elif PLACEHOLDER_RE.search(hook[key]):
                add("error", "placeholder_text", f"{path}.{key}", f"{key} contains a placeholder.")

        spoken = hook.get("spoken") if isinstance(hook.get("spoken"), str) else ""
        visual = hook.get("visual") if isinstance(hook.get("visual"), str) else ""
        overlay = hook.get("text_overlay") if isinstance(hook.get("text_overlay"), str) else ""
        hook_texts.append((str(hook_id), f"{spoken} {overlay}"))

        seconds = speech_seconds(spoken)
        if seconds > 4.0:
            add("error", "spoken_hook_too_long", f"{path}.spoken", f"Estimated delivery is {seconds:.1f}s; keep the opening near 3 seconds.")
        elif seconds > 3.2:
            add("warning", "spoken_hook_borderline", f"{path}.spoken", f"Estimated delivery is {seconds:.1f}s.")

        cjk_units, word_units = overlay_units(overlay)
        if cjk_units > 18 or word_units > 9:
            add("error", "overlay_too_long", f"{path}.text_overlay", "Overlay is too long for feed-speed reading.")
        elif cjk_units > 14 or word_units > 7:
            add("warning", "overlay_borderline", f"{path}.text_overlay", "Consider shortening the overlay.")

        if spoken and overlay and similarity(spoken, overlay) >= 0.82:
            add("error", "channel_repetition", path, "Spoken hook and text overlay repeat the same message.")
        if spoken and visual and similarity(spoken, visual) >= 0.90:
            add("error", "channel_repetition", path, "Spoken hook and visual direction are effectively identical.")

        for phrase in GENERIC_HYPE:
            if phrase in f"{spoken} {overlay}".casefold():
                add("warning", "generic_hype", path, f"Generic hype phrase detected: {phrase!r}.")

        refs = hook.get("supporting_fact_ids")
        if not string_list(refs, allow_empty=False):
            add("error", "invalid_supporting_facts", f"{path}.supporting_fact_ids", "At least one fact ID is required.")
            refs = []
        elif len(refs) != len(set(refs)):
            add("error", "duplicate_fact_reference", f"{path}.supporting_fact_ids", "Fact references must be unique.")
        for ref in refs:
            if ref not in facts:
                add("error", "unknown_fact_reference", f"{path}.supporting_fact_ids", f"Unknown fact: {ref}.")
                continue
            fact = facts[ref]
            if fact.get("status") == "prohibited":
                add("error", "prohibited_fact_used", f"{path}.supporting_fact_ids", f"Hook uses prohibited fact {ref}.")
            companions = fact.get("required_companion_ids", [])
            if isinstance(companions, list):
                missing = [item for item in companions if item not in refs]
                if missing:
                    add("error", "missing_fact_companion", f"{path}.supporting_fact_ids", f"Using {ref} also requires {', '.join(missing)}.")

        review_required = hook.get("human_review_required")
        if not isinstance(review_required, bool):
            add("error", "invalid_review_flag", f"{path}.human_review_required", "Must be boolean.")
        sensitive_refs = [
            ref
            for ref in refs
            if ref in facts
            and (
                facts[ref].get("status") in {"user-provided", "uncertain"}
                or facts[ref].get("requires_human_review") is True
            )
        ]
        if sensitive_refs and review_required is not True:
            add("error", "sensitive_fact_without_review", f"{path}.human_review_required", f"Review required for {', '.join(sensitive_refs)}.")

        risk_flags = hook.get("risk_flags")
        if not isinstance(risk_flags, list) or not all(item in RISK_FLAGS for item in risk_flags):
            add("error", "invalid_risk_flags", f"{path}.risk_flags", f"risk_flags must use {sorted(RISK_FLAGS)}.")
            risk_flags = []
        elif len(risk_flags) != len(set(risk_flags)):
            add("error", "duplicate_risk_flag", f"{path}.risk_flags", "risk_flags must be unique.")
        if risk_flags and review_required is not True:
            add("error", "risk_without_review", f"{path}.human_review_required", "Any risk flag requires human review.")

        scores = hook.get("scores")
        valid_scores: list[int] = []
        if not isinstance(scores, dict):
            add("error", "scores_type", f"{path}.scores", "scores must be an object.")
        else:
            for key in sorted(SCORE_KEYS):
                value = scores.get(key)
                if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 5:
                    add("error", "invalid_score", f"{path}.scores.{key}", "Score must be an integer from 1 to 5.")
                else:
                    valid_scores.append(value)
            for key in scores:
                if key not in SCORE_KEYS:
                    add("warning", "unknown_score", f"{path}.scores.{key}", "Unknown score dimension.")

        readiness = hook.get("readiness_score")
        if len(valid_scores) == len(SCORE_KEYS):
            calculated = round(sum(valid_scores) / len(valid_scores), 1)
            if not isinstance(readiness, (int, float)) or isinstance(readiness, bool):
                add("error", "invalid_readiness_score", f"{path}.readiness_score", "readiness_score must be numeric.")
            elif abs(float(readiness) - calculated) > 0.05:
                add("error", "readiness_mismatch", f"{path}.readiness_score", f"Expected {calculated}, found {readiness}.")

        decision = hook.get("decision")
        if decision not in DECISIONS:
            add("error", "invalid_decision", f"{path}.decision", f"decision must be one of {sorted(DECISIONS)}.")
        elif decision == "advance" and isinstance(scores, dict):
            required_minimums = {
                "product_relevance": 4,
                "first_frame_clarity": 4,
                "proofability": 4,
            }
            failed = [key for key, minimum in required_minimums.items() if scores.get(key, 0) < minimum]
            low = [key for key in SCORE_KEYS if isinstance(scores.get(key), int) and scores[key] < 3]
            if failed or low:
                add("error", "invalid_advance_decision", f"{path}.decision", "Advanced hook does not meet score gates.")

        referenced_statements = " ".join(
            facts[ref].get("statement", "")
            for ref in refs
            if ref in facts and isinstance(facts[ref].get("statement"), str)
        )
        fact_numbers = set(NUMBER_RE.findall(referenced_statements))
        hook_numbers = set(NUMBER_RE.findall(f"{spoken} {overlay}"))
        ungrounded_numbers = sorted(number for number in hook_numbers if number not in fact_numbers)
        if ungrounded_numbers:
            add(
                "warning",
                "number_not_in_supporting_facts",
                path,
                f"Review numeric language not found in supporting facts: {', '.join(ungrounded_numbers)}.",
            )

    for left_index, (left_id, left_text) in enumerate(hook_texts):
        for right_id, right_text in hook_texts[left_index + 1 :]:
            ratio = similarity(left_text, right_text)
            if ratio >= max_similarity:
                add("error", "hook_similarity", "$.hooks", f"{left_id} and {right_id} are {ratio:.0%} similar.")

    packs_raw = data.get("production_packs")
    packs: dict[str, dict[str, Any]] = {}
    if not isinstance(packs_raw, list):
        add("error", "invalid_production_packs", "$.production_packs", "production_packs must be an array.")
        packs_raw = []
    if mode == "lab" and len(packs_raw) != 3:
        add("error", "lab_pack_count", "$.production_packs", "lab mode requires exactly 3 production packs.")
    if mode == "quick" and len(packs_raw) != 1:
        add("error", "quick_pack_count", "$.production_packs", "quick mode requires exactly 1 production pack.")

    for index, pack in enumerate(packs_raw):
        path = f"$.production_packs[{index}]"
        if not isinstance(pack, dict):
            add("error", "pack_type", path, "Production pack must be an object.")
            continue
        pack_id = pack.get("id")
        if not nonempty(pack_id) or not PACK_ID_RE.fullmatch(pack_id):
            add("error", "invalid_pack_id", f"{path}.id", "Pack ID must match P01.")
        elif pack_id in packs:
            add("error", "duplicate_pack_id", f"{path}.id", f"Duplicate pack ID: {pack_id}.")
        else:
            packs[pack_id] = pack

        hook_id = pack.get("hook_id")
        if hook_id not in hooks:
            add("error", "unknown_pack_hook", f"{path}.hook_id", f"Unknown hook: {hook_id}.")
        elif hooks[hook_id].get("decision") != "advance":
            add("error", "pack_hook_not_advanced", f"{path}.hook_id", "Production pack must use an advanced hook.")

        duration = pack.get("duration_seconds")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
            add("error", "invalid_pack_duration", f"{path}.duration_seconds", "Must be positive.")
            duration_value = None
        else:
            duration_value = float(duration)
            if objective_duration is not None and abs(duration_value - objective_duration) > 0.01:
                add("error", "pack_objective_duration_mismatch", f"{path}.duration_seconds", "Pack duration differs from objective.")

        timeline = pack.get("timeline")
        if not isinstance(timeline, list) or not timeline:
            add("error", "invalid_timeline", f"{path}.timeline", "Timeline must be a non-empty array.")
            timeline = []
        cursor = 0.0
        for beat_index, beat in enumerate(timeline):
            beat_path = f"{path}.timeline[{beat_index}]"
            if not isinstance(beat, dict):
                add("error", "timeline_beat_type", beat_path, "Timeline beat must be an object.")
                continue
            start = beat.get("start_seconds")
            end = beat.get("end_seconds")
            if not isinstance(start, (int, float)) or isinstance(start, bool):
                add("error", "invalid_beat_start", f"{beat_path}.start_seconds", "Must be numeric.")
                continue
            if not isinstance(end, (int, float)) or isinstance(end, bool) or end <= start:
                add("error", "invalid_beat_end", f"{beat_path}.end_seconds", "Must be greater than start.")
                continue
            if abs(float(start) - cursor) > 0.01:
                add("error", "timeline_gap_or_overlap", beat_path, f"Expected start {cursor:g}, found {start}.")
            cursor = float(end)
            for key in ("visual", "audio"):
                if not nonempty(beat.get(key)):
                    add("error", "required_string", f"{beat_path}.{key}", f"{key} must be non-empty.")
            if not isinstance(beat.get("text_overlay"), str):
                add("error", "overlay_type", f"{beat_path}.text_overlay", "text_overlay must be a string.")
        if duration_value is not None and timeline and abs(cursor - duration_value) > 0.01:
            add("error", "timeline_duration_mismatch", f"{path}.timeline", f"Timeline ends at {cursor:g}, expected {duration_value:g}.")

        for key in ("cta", "generic_video_prompt", "seedance_prompt", "real_footage_notes"):
            if not nonempty(pack.get(key)):
                add("error", "required_string", f"{path}.{key}", f"{key} must be non-empty.")
        if not string_list(pack.get("reference_assets")):
            add("error", "invalid_reference_assets", f"{path}.reference_assets", "reference_assets must be a string array.")
        if not string_list(pack.get("generation_constraints"), allow_empty=False):
            add("error", "invalid_generation_constraints", f"{path}.generation_constraints", "At least one constraint is required.")

        generic_prompt = pack.get("generic_video_prompt", "")
        seedance_prompt = pack.get("seedance_prompt", "")
        if aspect_ratio and isinstance(generic_prompt, str) and aspect_ratio not in generic_prompt:
            add("warning", "generic_prompt_missing_aspect", f"{path}.generic_video_prompt", f"Prompt does not mention {aspect_ratio}.")
        if isinstance(seedance_prompt, str):
            for token in filter(None, [aspect_ratio, "0-3秒"]):
                if token not in seedance_prompt:
                    add("error", "seedance_prompt_missing_token", f"{path}.seedance_prompt", f"Seedance prompt must mention {token}.")
            if "@图片" not in seedance_prompt and "@视频" not in seedance_prompt:
                add("warning", "seedance_prompt_no_reference", f"{path}.seedance_prompt", "No official reference label found.")

        content_file = pack.get("content_file")
        if not nonempty(content_file):
            add("error", "content_file_required", f"{path}.content_file", "content_file must be non-empty.")
        else:
            target = (base_dir / content_file).resolve()
            try:
                target.relative_to(base_dir)
            except ValueError:
                add("error", "content_file_escape", f"{path}.content_file", "content_file escapes the package directory.")
            else:
                if not target.is_file():
                    add("error", "content_file_missing", f"{path}.content_file", f"Missing file: {content_file}.")
                else:
                    content = target.read_text(encoding="utf-8")
                    if nonempty(hook_id) and hook_id not in content:
                        add("warning", "content_file_missing_hook_id", f"{path}.content_file", f"File does not mention {hook_id}.")

    test_plan = data.get("test_plan")
    if not isinstance(test_plan, dict):
        add("error", "test_plan_type", "$.test_plan", "test_plan must be an object.")
    else:
        for key in ("hypothesis", "changed_variable", "primary_metric", "stop_condition", "interpretation_rule"):
            if not nonempty(test_plan.get(key)):
                add("error", "required_string", f"$.test_plan.{key}", f"{key} must be non-empty.")
        variants = test_plan.get("variant_hook_ids")
        if not string_list(variants, allow_empty=False):
            add("error", "invalid_test_variants", "$.test_plan.variant_hook_ids", "At least one variant hook ID is required.")
            variants = []
        elif len(variants) != len(set(variants)):
            add("error", "duplicate_test_variant", "$.test_plan.variant_hook_ids", "Variant hook IDs must be unique.")
        for variant in variants:
            if variant not in hooks:
                add("error", "unknown_test_variant", "$.test_plan.variant_hook_ids", f"Unknown hook: {variant}.")
        if not string_list(test_plan.get("controlled_variables"), allow_empty=False):
            add("error", "invalid_controls", "$.test_plan.controlled_variables", "At least one controlled variable is required.")
        if not string_list(test_plan.get("secondary_metrics")):
            add("error", "invalid_secondary_metrics", "$.test_plan.secondary_metrics", "secondary_metrics must be a string array.")

    review = data.get("review")
    if not isinstance(review, dict):
        add("error", "review_type", "$.review", "review must be an object.")
    else:
        for key in ("unsupported_claims", "human_review_items", "limitations"):
            if not string_list(review.get(key)):
                add("error", "invalid_review_list", f"$.review.{key}", f"{key} must be a string array.")

    for filename in sorted(REQUIRED_PACKAGE_FILES):
        if not (base_dir / filename).is_file():
            add("error", "package_file_missing", f"$.package.{filename}", f"Missing required package file: {filename}.")

    truth_path = base_dir / "product-truth.md"
    if truth_path.is_file():
        truth_text = truth_path.read_text(encoding="utf-8")
        for fact_id in facts:
            if fact_id not in truth_text:
                add(
                    "error",
                    "truth_file_missing_fact",
                    "$.package.product-truth.md",
                    f"product-truth.md does not mention {fact_id}.",
                )

    matrix_path = base_dir / "hook-matrix.md"
    if matrix_path.is_file():
        matrix_text = matrix_path.read_text(encoding="utf-8")
        for hook_id in hooks:
            if hook_id not in matrix_text:
                add(
                    "error",
                    "matrix_file_missing_hook",
                    "$.package.hook-matrix.md",
                    f"hook-matrix.md does not mention {hook_id}.",
                )

    audience_path = base_dir / "audience-and-test.md"
    if audience_path.is_file() and isinstance(audience, dict) and isinstance(test_plan, dict):
        audience_text = audience_path.read_text(encoding="utf-8").casefold()
        parity_values = {
            "awareness_stage": audience.get("awareness_stage"),
            "primary_metric": test_plan.get("primary_metric"),
            "changed_variable": test_plan.get("changed_variable"),
        }
        for key, value in parity_values.items():
            if nonempty(value) and value.casefold() not in audience_text:
                add(
                    "error",
                    "audience_file_mismatch",
                    "$.package.audience-and-test.md",
                    f"audience-and-test.md does not contain {key}: {value}.",
                )

    return build_report(issues, len(facts), len(hooks), len(packs))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to hook-pack.json")
    parser.add_argument("--report", type=Path, help="Optional QA report output path")
    parser.add_argument("--max-similarity", type=float, default=0.82)
    args = parser.parse_args()

    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Manifest not found: {args.manifest}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 2

    report = validate_pack(data, args.manifest.resolve(), max_similarity=args.max_similarity)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
