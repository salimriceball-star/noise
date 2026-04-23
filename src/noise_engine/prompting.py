from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROMPT_FILES = {
    "tension_analyzer": "prompt_1_tension_analyzer.md",
    "comment_simulator": "prompt_2_comment_simulator.md",
    "angle_selector": "prompt_3_angle_selector.md",
    "storyboard_director": "prompt_4_storyboard_director.md",
    "copy_director": "prompt_5_copy_director.md",
    "safety_editor": "prompt_6_safety_editor.md",
    "bundle_orchestrator": "prompt_bundle_orchestrator.md",
}


def prompts_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "prompts"



def load_prompt(name: str) -> str:
    file_name = PROMPT_FILES[name]
    return (prompts_dir() / file_name).read_text(encoding="utf-8")



def _compact_corpus_analysis(corpus_analysis: dict[str, Any]) -> dict[str, Any]:
    comments = corpus_analysis.get("comments", [])
    compact_comments = []
    for comment in comments[:6]:
        compact_comments.append(
            {
                "text": comment.get("text", ""),
                "archetypes": comment.get("archetypes", []),
                "axes": comment.get("axes", []),
                "risk_flags": comment.get("risk_flags", []),
            }
        )
    return {
        "total_comments": corpus_analysis.get("total_comments", 0),
        "unique_comments": corpus_analysis.get("unique_comments", 0),
        "duplicate_count": corpus_analysis.get("duplicate_count", 0),
        "major_conflict_axes": corpus_analysis.get("major_conflict_axes", []),
        "archetype_counts": {k: v for k, v in (corpus_analysis.get("archetype_counts", {}) or {}).items() if v},
        "reaction_mode_counts": {k: v for k, v in (corpus_analysis.get("reaction_mode_counts", {}) or {}).items() if v},
        "emotion_counts": {k: v for k, v in (corpus_analysis.get("emotion_counts", {}) or {}).items() if v},
        "value_counts": {k: v for k, v in (corpus_analysis.get("value_counts", {}) or {}).items() if v},
        "target_counts": {k: v for k, v in (corpus_analysis.get("target_counts", {}) or {}).items() if v},
        "off_target_drift": corpus_analysis.get("off_target_drift", {}),
        "sample_comments": compact_comments,
    }



def build_bundle_prompt(*, brief_text: str, corpus_analysis: dict) -> str:
    template = load_prompt("bundle_orchestrator")
    prompt = template.replace("{{BRIEF_TEXT}}", brief_text.strip())
    prompt = prompt.replace(
        "{{CORPUS_ANALYSIS_JSON}}",
        json.dumps(_compact_corpus_analysis(corpus_analysis), ensure_ascii=False, indent=2),
    )
    return prompt
