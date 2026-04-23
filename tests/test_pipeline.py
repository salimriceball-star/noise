from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from noise_engine.corpus import analyze_corpus
from noise_engine.guivm import GUIVMClient
from noise_engine.pipeline import NoisePipeline, render_bundle_markdown
from noise_engine.prompting import build_bundle_prompt


class FakeGUIVMClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def check_health(self) -> dict:
        return {"ok": True, "service": "fake-guivm"}

    def check_capacity(self) -> dict:
        return {"running": 0, "infer_quota": {"phase": {"next_allowed_in_sec": 0}}}

    def infer_json(self, *, stage: str, symbol: str, prompt: str, request_id: str) -> dict:
        self.calls.append({"stage": stage, "symbol": symbol, "prompt": prompt, "request_id": request_id})
        return {
            "surface_claims": [
                "휴머노이드가 가사와 케어를 맡으면 결혼의 기준이 바뀐다",
                "편리함보다 복무/친밀의 대체 가능성이 댓글을 연다",
                "사람들은 기술보다 관계의 암묵 전제에 반응한다",
            ],
            "implicit_premises": [
                "관계에는 노동과 케어의 거래 조건이 섞여 있다",
                "장면이 보여주는 복무감이 서비스화 해석을 만든다",
                "계급 접근성이 관계 논쟁을 다시 연다",
            ],
            "defended_values": ["사랑", "인간성", "성평등", "계급감각", "안전"],
            "predicted_rebuttal_axes": ["관계 vs 서비스", "젠더화된 돌봄", "계급 접근성", "인간성", "공포/불쾌"],
            "forbidden_axes": ["보호집단 비하", "노골적 성적화", "작성자 혐오 유도"],
            "comment_archetypes": [
                {"name": "논리 교정형", "emotion": "냉정한 반박", "why": "가사부담 감소를 결혼 용이성으로 읽음"},
                {"name": "젠더 해석형", "emotion": "분노", "why": "결혼을 노동계약으로 환원했다고 봄"},
                {"name": "존재론 방어형", "emotion": "철학적 방어", "why": "사랑과 온기의 비대체성을 지킴"},
                {"name": "계급/경제형", "emotion": "냉소", "why": "기술 혜택의 계급 편중을 지적함"},
            ],
            "harmful_reactions": ["작성자 조롱이 중심이 되는 흐름"],
            "desired_reactions": ["반박", "자기경험 투영", "세계관 확장"],
            "author_attack_risk": "medium",
            "selected_angle": {
                "title": "관계가 사랑인지 서비스인지 헷갈리게 만드는 가정용 휴머노이드",
                "surface_claim": "휴머노이드가 집안의 케어 노동을 대신하기 시작하면 결혼의 기준도 조용히 바뀐다.",
                "implicit_premise": "관계 안에는 이미 보이지 않는 노동과 시중의 기대가 섞여 있다.",
                "meta_message": "작성자는 배우자 역할의 일부가 서비스처럼 대체될 수 있다고 본다.",
                "main_axis": "관계 vs 서비스",
                "support_axis": "성별화된 돌봄",
                "background_axis": "계급 접근성",
                "boundary_crossing_scene": "퇴근한 사람의 겉옷과 신발을 벗겨 주는 순간",
                "avoid_scenes": ["노골적 성적 접촉", "과잉 공포 연출"],
            },
            "storyboard": [
                {"cut": 1, "function": "utility", "scene": "저녁 식재료 정리", "expected_comments": ["편리함"]},
                {"cut": 2, "function": "utility", "scene": "세탁물 개기", "expected_comments": ["가사 자동화"]},
                {"cut": 3, "function": "care", "scene": "아침 도시락 챙기기", "expected_comments": ["돌봄"]},
                {"cut": 4, "function": "authority", "scene": "현관에서 겉옷 받아주고 신발 벗겨주기", "expected_comments": ["서비스화", "젠더"]},
                {"cut": 5, "function": "intimacy", "scene": "어깨를 잠깐 주무르는 장면", "expected_comments": ["친밀성 대체", "불쾌"]},
                {"cut": 6, "function": "aftermath", "scene": "사람 배우자가 가만히 보는 컷", "expected_comments": ["관계 재정의", "계급"]},
            ],
            "image_prompts": [
                "realistic smartphone photo, apartment hallway, subtle service dynamic, no text overlay",
                "casual home kitchen utility shot, no editorial glamor",
            ],
            "copy_variants": [
                {"tone": "담담한 예언", "copy": "집안의 케어가 외주화되기 시작하면, 결혼은 사랑보다 기준표에 가까워질지도 모른다.", "intended_reaction": "반박", "expected_pushback": "사랑을 너무 모른다는 반응", "risk_note": "작성자 조롱 주의"},
                {"tone": "순진한 오해", "copy": "가사랑 돌봄을 거의 대신해주면, 결혼은 이제 감정보다 선택이 쉬워지는 문제 아닐까.", "intended_reaction": "논리 교정", "expected_pushback": "결혼을 계약처럼 본다는 비판", "risk_note": "젠더 논쟁 점화"},
                {"tone": "차가운 효율주의", "copy": "배우자에게 기대하던 케어가 서비스로 분해되면, 관계의 프리미엄은 빠르게 재계산된다.", "intended_reaction": "계급/가치 충돌", "expected_pushback": "비인간적이라는 반응", "risk_note": "차갑게 보일 수 있음"},
                {"tone": "피곤한 현실관찰", "copy": "사람들이 불편해하는 건 로봇이 아니라, 원래 관계 안에 있던 시중의 몫이 너무 선명해지는 장면일지도.", "intended_reaction": "자기경험 투영", "expected_pushback": "과잉 해석이라는 반응", "risk_note": "설명적으로 길어지지 않게 유지"},
            ],
            "safety_review": {
                "status": "modify",
                "reason": "댓글축은 충분하지만 author attack 비중을 낮출 장치가 더 필요함",
                "fixes": ["첫 댓글로 논점을 관계/서비스 축에 고정", "마사지 컷은 짧고 비노골적으로 유지"],
                "drift_prevention": ["작성자 자아노출 최소화", "혐오 프레이밍 금지"]
            },
            "final_bundle": {
                "concept_sheet": {
                    "input_topic": "휴머노이드가 집안의 케어 노동을 대신하는 장면",
                    "main_axis": "관계 vs 서비스",
                    "support_axis": "성별화된 돌봄",
                    "background_axis": "계급 접근성"
                },
                "risk_sheet": {
                    "off_target_drift": ["작성자 조롱 과다"],
                    "author_attack_risk": "medium",
                    "sexualization_risk": "low",
                    "policy_risk": "low"
                },
                "evaluation_sheet": {
                    "interpretation_conflict": 5,
                    "rebuttal_pull": 5,
                    "self_projection_pull": 4,
                    "visual_caption_gap": 5,
                    "brand_damage_risk": 3
                },
                "operating_sheet": {
                    "do_not_say": ["너희 결혼은 결국 가사 계약이잖아"],
                    "first_comment_direction": "관계의 기준이 어디서 흔들리는지 묻는 문장으로 고정",
                    "response_principle": "작성자 방어 대신 논점 복귀"
                }
            }
        }


class PipelineTests(unittest.TestCase):
    def test_guivm_client_initializes_session_state(self) -> None:
        client = GUIVMClient(base_url="http://example.com")
        self.assertIsNotNone(client.session)
        self.assertIsNone(client.export_last_exchange())

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="noise-pipeline-"))
        self.brief_path = self.temp_dir / "brief.md"
        self.brief_path.write_text("휴머노이드가 가사와 케어를 대신할 때 어떤 댓글 구조가 열리는지 설계한다.", encoding="utf-8")
        self.comments_path = self.temp_dir / "comments.jsonl"
        self.comments_path.write_text(
            "\n".join(
                [
                    json.dumps({"text": "오히려 더 결혼하기 쉬워진다"}, ensure_ascii=False),
                    json.dumps({"text": "결혼을 가사노동 계약처럼 보네"}, ensure_ascii=False),
                    json.dumps({"text": "저건 부자들만 쓰겠지"}, ensure_ascii=False),
                ]
            ),
            encoding="utf-8",
        )

    def test_build_bundle_prompt_includes_corpus_summary_and_stage_contracts(self) -> None:
        analysis = analyze_corpus(self.comments_path)
        prompt = build_bundle_prompt(
            brief_text=self.brief_path.read_text(encoding="utf-8"),
            corpus_analysis=analysis.to_dict(),
        )
        self.assertIn("긴장축 분석기", prompt)
        self.assertIn("댓글 시뮬레이터", prompt)
        self.assertIn("세이프티 에디터", prompt)
        self.assertIn("major_conflict_axes", prompt)
        self.assertLess(len(prompt), 7000)

    def test_pipeline_saves_bundle_markdown_and_raw_response(self) -> None:
        output_dir = self.temp_dir / "out"
        client = FakeGUIVMClient()
        pipeline = NoisePipeline(client=client)

        result = pipeline.run(
            brief_path=self.brief_path,
            comments_path=self.comments_path,
            output_dir=output_dir,
            symbol="noise-test",
        )

        self.assertEqual(len(client.calls), 1)
        self.assertTrue((output_dir / "bundle.json").exists())
        self.assertTrue((output_dir / "bundle.md").exists())
        self.assertTrue((output_dir / "corpus-analysis.json").exists())
        self.assertTrue((output_dir / "guivm-response.json").exists())
        saved_bundle = json.loads((output_dir / "bundle.json").read_text(encoding="utf-8"))
        self.assertEqual(saved_bundle["selected_angle"]["main_axis"], "관계 vs 서비스")
        self.assertIn("bundle_path", result)

    def test_render_bundle_markdown_mentions_core_sections(self) -> None:
        markdown = render_bundle_markdown(
            {
                "selected_angle": {"title": "테스트 앵글", "surface_claim": "표면 주장", "implicit_premise": "암묵 전제", "meta_message": "메타", "main_axis": "주축", "support_axis": "보조축", "background_axis": "배경축", "boundary_crossing_scene": "핵심 컷", "avoid_scenes": ["금지1"]},
                "storyboard": [{"cut": 1, "function": "utility", "scene": "장면", "expected_comments": ["반응"]}],
                "copy_variants": [{"tone": "담담한 예언", "copy": "카피", "intended_reaction": "반응", "expected_pushback": "역반응", "risk_note": "리스크"}],
                "final_bundle": {"risk_sheet": {"off_target_drift": ["조롱"]}, "evaluation_sheet": {"interpretation_conflict": 4}, "operating_sheet": {"first_comment_direction": "논점 고정"}},
            }
        )
        self.assertIn("# Noise Bundle", markdown)
        self.assertIn("## Concept Sheet", markdown)
        self.assertIn("## Storyboard Sheet", markdown)
        self.assertIn("## Copy Sheet", markdown)


if __name__ == "__main__":
    unittest.main()
