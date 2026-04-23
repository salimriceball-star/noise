from __future__ import annotations

import json
import re
from typing import Any

NOISE_JSON_RE = re.compile(r"<noise_json>\s*(\{.*?\})\s*</noise_json>", re.S | re.I)


def split_axes(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []
    pieces = re.split(r"\s*(?:,|/|；|;)\s*", text)
    return [piece.strip() for piece in pieces if piece.strip()]


def extract_noise_json(raw_text: str) -> dict[str, Any]:
    tagged_payloads = [match.group(1) for match in NOISE_JSON_RE.finditer(raw_text)]
    candidates = tagged_payloads if tagged_payloads else [_extract_first_json_object(raw_text)]
    parsed_candidates: list[dict[str, Any]] = []
    for payload_text in candidates:
        parsed = json.loads(payload_text)
        _normalize_parsed_ideas(parsed)
        parsed_candidates.append(parsed)
    for parsed in reversed(parsed_candidates):
        if parsed.get("ideas"):
            return parsed
    if parsed_candidates:
        return parsed_candidates[-1]
    raise ValueError("No JSON object found in Grok response")


def _normalize_parsed_ideas(parsed: dict[str, Any]) -> None:
    ideas = parsed.get("ideas")
    if not isinstance(ideas, list):
        raise ValueError("Grok response JSON must contain an ideas list")
    for idea in ideas:
        if isinstance(idea, dict):
            idea["likely_comment_axes"] = split_axes(idea.get("likely_comment_axes"))


def _extract_first_json_object(text: str) -> str:
    start = text.find("{")
    if start < 0:
        raise ValueError("No JSON object found in Grok response")
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise ValueError("Unterminated JSON object in Grok response")
