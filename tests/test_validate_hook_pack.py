#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_hook_pack.py"
SPEC = importlib.util.spec_from_file_location("validate_hook_pack", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def scores(**overrides: int) -> dict[str, int]:
    values = {
        "product_relevance": 4,
        "audience_fit": 4,
        "first_frame_clarity": 4,
        "curiosity": 4,
        "proofability": 4,
        "feed_native": 4,
        "model_feasibility": 4,
        "distinctness": 4,
    }
    values.update(overrides)
    return values


def hook(
    hook_id: str,
    angle: str,
    spoken: str,
    visual: str,
    overlay: str,
    *,
    decision: str = "revise",
) -> dict:
    value_scores = scores()
    return {
        "id": hook_id,
        "angle": angle,
        "archetype": "direct demonstration",
        "spoken": spoken,
        "visual": visual,
        "text_overlay": overlay,
        "supporting_fact_ids": ["F01"],
        "proof_plan": "Show one uncut pass across the fabric.",
        "risk_flags": [],
        "human_review_required": False,
        "scores": value_scores,
        "readiness_score": 4.0,
        "decision": decision,
    }


def base_manifest() -> dict:
    return {
        "schema_version": "1.0",
        "run": {
            "mode": "quick",
            "language": "en",
            "created_at": "2026-07-25",
        },
        "product": {
            "name": "Reusable Fabric Sweeper",
            "category": "household cleaning",
            "source_rights": "owned",
            "source_summary": "Owner-provided product brief and demonstration notes.",
        },
        "audience": {
            "persona": "Pet owners with dark fabric furniture",
            "context": "Cleaning visible loose pet hair before guests arrive",
            "pain": "Disposable lint sheets run out during routine cleaning",
            "desire": "A simple reusable tool for visible loose hair",
            "awareness_stage": "problem-aware",
            "is_inferred": False,
        },
        "objective": {
            "platform": "TikTok Shop",
            "aspect_ratio": "9:16",
            "duration_seconds": 15,
            "goal": "hold",
        },
        "facts": [
            {
                "id": "F01",
                "kind": "feature",
                "statement": "The hand tool collects visible loose pet hair from fabric.",
                "source_locator": "Owner demo notes, step 2",
                "status": "verified",
                "visual_proof": "One continuous pass over a dark fabric cushion.",
                "requires_human_review": False,
                "required_companion_ids": [],
            },
            {
                "id": "R01",
                "kind": "restriction",
                "statement": "Do not claim that the tool removes every embedded fiber.",
                "source_locator": "Owner demo notes, limitation",
                "status": "verified",
                "visual_proof": "Keep the camera close enough to show the actual surface.",
                "requires_human_review": False,
                "required_companion_ids": [],
            },
        ],
        "hooks": [
            hook(
                "H01",
                "visual-proof",
                "This cushion only looks clean.",
                "A hand wipes a dark cushion and reveals a dense line of loose hair.",
                "The hidden layer",
                decision="advance",
            ),
            hook(
                "H02",
                "pain-moment",
                "Guests are ten minutes away.",
                "A creator notices pale hair across a dark sofa and freezes.",
                "Last-minute sofa check",
            ),
            hook(
                "H03",
                "mechanism",
                "Watch where the loose hair goes.",
                "Macro view follows hair gathering at the tool edge.",
                "One pass, close up",
            ),
            hook(
                "H04",
                "identity-callout",
                "Black sofa and a white cat?",
                "Split frame shows the cat, then the marked sofa.",
                "Pet owner problem",
            ),
            hook(
                "H05",
                "routine",
                "My doorbell triggered this cleanup.",
                "Doorbell sounds while a hand reaches for the sweeper.",
                "Before they sit down",
            ),
            hook(
                "H06",
                "objection-reversal",
                "No fresh lint sheet this time.",
                "Empty disposable roll moves aside; reusable tool enters frame.",
                "Use it again",
            ),
        ],
        "production_packs": [
            {
                "id": "P01",
                "hook_id": "H01",
                "duration_seconds": 15,
                "timeline": [
                    {
                        "start_seconds": 0,
                        "end_seconds": 3,
                        "visual": "Reveal loose hair on a dark cushion in one pass.",
                        "audio": "This cushion only looks clean.",
                        "text_overlay": "The hidden layer",
                    },
                    {
                        "start_seconds": 3,
                        "end_seconds": 9,
                        "visual": "Macro shot follows hair collecting along the tool edge.",
                        "audio": "Show the mechanism without a cut.",
                        "text_overlay": "",
                    },
                    {
                        "start_seconds": 9,
                        "end_seconds": 15,
                        "visual": "Empty the collected hair and return to the real cushion.",
                        "audio": "Use a real product proof shot before the CTA.",
                        "text_overlay": "See the tool",
                    },
                ],
                "cta": "See how it works on your fabric.",
                "content_file": "production/p01.md",
                "generic_video_prompt": "Create a 15-second 9:16 product demonstration using the supplied product reference, opening on a dark fabric cushion and one continuous cleaning pass.",
                "seedance_prompt": "15秒，9:16，@图片1为产品外观参考。0-3秒：深色布艺坐垫特写，一次划过露出松散宠物毛；3-9秒：微距跟拍毛发聚拢；9-15秒：展示真实收集结果。禁止生成字幕、额外LOGO或水印。",
                "reference_assets": ["@图片1: owned product reference"],
                "generation_constraints": [
                    "Keep the product shape consistent with @图片1.",
                    "Use real footage for the final proof if generation changes the result.",
                ],
                "real_footage_notes": "Record the actual cleaning pass with the owned product for truthful proof.",
            }
        ],
        "test_plan": {
            "hypothesis": "A proof-first opening will hold problem-aware pet owners long enough to see the mechanism.",
            "variant_hook_ids": ["H01"],
            "changed_variable": "opening hook",
            "controlled_variables": ["body", "CTA", "duration", "creator", "audience"],
            "primary_metric": "3-second hold rate",
            "secondary_metrics": ["6-second hold rate", "click-through rate"],
            "stop_condition": "not provided",
            "interpretation_rule": "Compare only after the media buyer defines minimum exposure and a stopping rule.",
        },
        "review": {
            "unsupported_claims": [],
            "human_review_items": [],
            "limitations": [
                "The validator does not predict performance.",
                "Product proof must use the real owned item.",
            ],
        },
    }


class ValidateHookPackTests(unittest.TestCase):
    def write_package(self, root: Path, manifest: dict) -> Path:
        fact_ids = " ".join(item["id"] for item in manifest.get("facts", []))
        hook_ids = " ".join(item["id"] for item in manifest.get("hooks", []))
        audience = manifest.get("audience", {})
        test_plan = manifest.get("test_plan", {})
        (root / "product-truth.md").write_text(f"# Product truth\n\n{fact_ids}\n", encoding="utf-8")
        (root / "hook-matrix.md").write_text(f"# Hook matrix\n\n{hook_ids}\n", encoding="utf-8")
        (root / "audience-and-test.md").write_text(
            "\n".join(
                [
                    "# Audience and test",
                    str(audience.get("awareness_stage", "")),
                    str(test_plan.get("primary_metric", "")),
                    str(test_plan.get("changed_variable", "")),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        for pack in manifest.get("production_packs", []):
            target = root / pack["content_file"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"# {pack['id']}\n\nHook: {pack['hook_id']}\n", encoding="utf-8")
        path = root / "hook-pack.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def test_valid_quick_package_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = base_manifest()
            path = self.write_package(root, manifest)
            report = MODULE.validate_pack(manifest, path)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["summary"]["errors"], 0)

    def test_detects_prohibited_fact_risk_and_timeline_gap(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = base_manifest()
            manifest["facts"][0]["status"] = "prohibited"
            manifest["hooks"][0]["risk_flags"] = ["before-after"]
            manifest["hooks"][0]["human_review_required"] = False
            manifest["production_packs"][0]["timeline"][1]["start_seconds"] = 4
            path = self.write_package(root, manifest)
            report = MODULE.validate_pack(manifest, path)
            codes = {item["code"] for item in report["issues"]}
            self.assertEqual(report["status"], "fail")
            self.assertTrue(
                {
                    "prohibited_fact_used",
                    "risk_without_review",
                    "timeline_gap_or_overlap",
                }.issubset(codes)
            )

    def test_detects_channel_repetition(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = base_manifest()
            manifest["hooks"][0]["text_overlay"] = manifest["hooks"][0]["spoken"]
            path = self.write_package(root, manifest)
            report = MODULE.validate_pack(manifest, path)
            codes = {item["code"] for item in report["issues"]}
            self.assertIn("channel_repetition", codes)

    def test_detects_duplicate_hook_variants(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = base_manifest()
            duplicate = deepcopy(manifest["hooks"][0])
            duplicate["id"] = "H02"
            manifest["hooks"][1] = duplicate
            path = self.write_package(root, manifest)
            report = MODULE.validate_pack(manifest, path)
            codes = {item["code"] for item in report["issues"]}
            self.assertIn("hook_similarity", codes)


if __name__ == "__main__":
    unittest.main()
