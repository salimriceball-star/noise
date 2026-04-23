from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from noise_engine.corpus import analyze_corpus, load_comment_corpus, normalize_comment_text


class CorpusAnalysisTests(unittest.TestCase):
    def write_jsonl(self, rows: list[dict]) -> Path:
        temp_dir = Path(tempfile.mkdtemp(prefix="noise-corpus-"))
        path = temp_dir / "comments.jsonl"
        path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")
        return path

    def test_normalize_comment_text_collapses_whitespace(self) -> None:
        self.assertEqual(normalize_comment_text("  오히려   더 결혼하지  "), "오히려 더 결혼하지")

    def test_load_comment_corpus_supports_jsonl_and_dedupes_on_analysis(self) -> None:
        path = self.write_jsonl(
            [
                {"text": "오히려 가사 부담 줄면 더 결혼하지"},
                {"text": "오히려 가사 부담 줄면 더 결혼하지   "},
                {"text": "사람 온기랑 사랑은 대체 못 함"},
            ]
        )
        comments = load_comment_corpus(path)
        self.assertEqual([comment.text for comment in comments], [
            "오히려 가사 부담 줄면 더 결혼하지",
            "오히려 가사 부담 줄면 더 결혼하지   ",
            "사람 온기랑 사랑은 대체 못 함",
        ])

        analysis = analyze_corpus(path)
        self.assertEqual(analysis.total_comments, 3)
        self.assertEqual(analysis.unique_comments, 2)
        self.assertEqual(analysis.duplicate_count, 1)

    def test_analysis_assigns_expected_archetypes_axes_and_drift(self) -> None:
        path = self.write_jsonl(
            [
                {"text": "오히려 가사 부담 줄면 더 결혼하고 애 낳기 쉬워질 듯"},
                {"text": "결혼을 가사노동 계약으로 보냐는 반응 나오는 이유 알겠다"},
                {"text": "아이는 기능이 아니라 사랑이지 사람 온기까지 대체하진 못함"},
                {"text": "저건 결국 돈 많은 사람만 쓰는 기술 아니냐"},
                {"text": "신발 벗겨주고 마사지하는 컷은 좀 무섭고 기괴함"},
                {"text": "안마 청소 요리는 솔직히 탐난다"},
                {"text": "작성자 진짜 세상 너무 모른다"},
            ]
        )

        analysis = analyze_corpus(path)
        self.assertGreaterEqual(analysis.archetype_counts["logic_correction"], 1)
        self.assertGreaterEqual(analysis.archetype_counts["gender_contract"], 1)
        self.assertGreaterEqual(analysis.archetype_counts["ontological_defense"], 1)
        self.assertGreaterEqual(analysis.archetype_counts["class_access"], 1)
        self.assertGreaterEqual(analysis.archetype_counts["fear_discomfort"], 1)
        self.assertGreaterEqual(analysis.archetype_counts["desire_consumption"], 1)
        self.assertGreaterEqual(analysis.archetype_counts["author_attack"], 1)
        self.assertIn("relationship_vs_service", analysis.major_conflict_axes)
        self.assertIn("class_access", analysis.major_conflict_axes)
        self.assertGreaterEqual(analysis.off_target_drift["author_attack"], 1)
        self.assertEqual(analysis.off_target_drift["sexualization"], 0)

    def test_plain_text_loader_is_supported(self) -> None:
        temp_dir = Path(tempfile.mkdtemp(prefix="noise-text-"))
        path = temp_dir / "comments.txt"
        path.write_text("첫 댓글\n\n둘째 댓글\n", encoding="utf-8")

        comments = load_comment_corpus(path)
        self.assertEqual([comment.text for comment in comments], ["첫 댓글", "둘째 댓글"])


if __name__ == "__main__":
    unittest.main()
