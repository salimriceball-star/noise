from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from noise_engine.cli import main


class FakeGUIVMClient:
    def check_health(self) -> dict:
        return {"ok": True, "service": "fake-guivm"}

    def check_capacity(self) -> dict:
        return {"running": 0, "infer_quota": {"phase": {"next_allowed_in_sec": 0}}}

    def infer_json(self, *, stage: str, symbol: str, prompt: str, request_id: str) -> dict:
        return {
            "selected_angle": {
                "title": "CLI demo",
                "surface_claim": "표면 주장",
                "implicit_premise": "암묵 전제",
                "meta_message": "메타",
                "main_axis": "주축",
                "support_axis": "보조축",
                "background_axis": "배경축",
                "boundary_crossing_scene": "경계침범 컷",
                "avoid_scenes": ["과잉 장면"],
            },
            "storyboard": [{"cut": 1, "function": "utility", "scene": "장면", "expected_comments": ["반응"]}],
            "copy_variants": [{"tone": "담담한 예언", "copy": "카피", "intended_reaction": "반응", "expected_pushback": "역반응", "risk_note": "리스크"}],
            "final_bundle": {
                "concept_sheet": {"input_topic": "주제", "main_axis": "주축", "support_axis": "보조축", "background_axis": "배경축"},
                "risk_sheet": {"off_target_drift": [], "author_attack_risk": "low", "sexualization_risk": "low", "policy_risk": "low"},
                "evaluation_sheet": {"interpretation_conflict": 4, "rebuttal_pull": 4, "self_projection_pull": 4, "visual_caption_gap": 4, "brand_damage_risk": 2},
                "operating_sheet": {"do_not_say": ["하지 말 말"], "first_comment_direction": "논점 고정", "response_principle": "논점 복귀"},
            },
        }


class CliTests(unittest.TestCase):
    def test_doctor_command_returns_success(self) -> None:
        exit_code = main(["doctor"], client=FakeGUIVMClient())
        self.assertEqual(exit_code, 0)

    def test_smoke_command_returns_success(self) -> None:
        exit_code = main(["smoke", "--wait-timeout-sec", "5"], client=FakeGUIVMClient())
        self.assertEqual(exit_code, 0)

    def test_run_command_writes_bundle(self) -> None:
        temp_dir = Path(tempfile.mkdtemp(prefix="noise-cli-"))
        brief_path = temp_dir / "brief.md"
        comments_path = temp_dir / "comments.jsonl"
        out_dir = temp_dir / "out"
        brief_path.write_text("brief", encoding="utf-8")
        comments_path.write_text(json.dumps({"text": "오히려 더 결혼하지"}, ensure_ascii=False), encoding="utf-8")

        exit_code = main(
            [
                "run",
                "--brief",
                str(brief_path),
                "--comments",
                str(comments_path),
                "--output-dir",
                str(out_dir),
            ],
            client=FakeGUIVMClient(),
        )
        self.assertEqual(exit_code, 0)
        self.assertTrue((out_dir / "bundle.json").exists())

    def test_demo_offline_writes_bundle(self) -> None:
        temp_dir = Path(tempfile.mkdtemp(prefix="noise-demo-offline-"))
        exit_code = main(["demo", "--offline", "--output-dir", str(temp_dir / "out")])
        self.assertEqual(exit_code, 0)
        self.assertTrue((temp_dir / "out" / "bundle.json").exists())


if __name__ == "__main__":
    unittest.main()
