from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from noise_engine.grok_parser import extract_noise_json, split_axes


class GrokParserTests(unittest.TestCase):
    def test_extracts_noise_json_between_tags(self) -> None:
        raw = "prefix\n<noise_json>{\"ideas\":[{\"topic\":\"팬덤\",\"likely_comment_axes\":\"축하 vs 소비, 진심 vs 상업\"}]}</noise_json>\nsuffix"
        parsed = extract_noise_json(raw)
        self.assertEqual(parsed["ideas"][0]["topic"], "팬덤")
        self.assertEqual(parsed["ideas"][0]["likely_comment_axes"], ["축하 vs 소비", "진심 vs 상업"])

    def test_uses_answer_tag_when_prompt_echo_contains_empty_schema_tag(self) -> None:
        raw = "prompt echo <noise_json>{\"ideas\":[]}</noise_json>\nanswer <noise_json>{\"ideas\":[{\"topic\":\"팬덤\",\"likely_comment_axes\":\"축하 vs 소비\"}]}</noise_json>"
        parsed = extract_noise_json(raw)
        self.assertEqual(parsed["ideas"][0]["topic"], "팬덤")

    def test_extracts_first_json_object_when_tags_are_missing(self) -> None:
        raw = "Grok answer: {\"ideas\":[{\"topic\":\"연령 인증\",\"likely_comment_axes\":[\"안전 vs 자유\"]}]} trailing"
        parsed = extract_noise_json(raw)
        self.assertEqual(parsed["ideas"][0]["likely_comment_axes"], ["안전 vs 자유"])

    def test_split_axes_handles_commas_and_korean_separators(self) -> None:
        self.assertEqual(split_axes("자립 촉구 vs 현실 공감, 부모 세대 비판 / 구조 문제"), ["자립 촉구 vs 현실 공감", "부모 세대 비판", "구조 문제"])


if __name__ == "__main__":
    unittest.main()
