from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .corpus import analyze_corpus
from .prompting import build_bundle_prompt

UTC = timezone.utc


class NoisePipeline:
    def __init__(self, client: Any) -> None:
        self.client = client

    def run(self, *, brief_path: str | Path, comments_path: str | Path, output_dir: str | Path, symbol: str = "noise") -> dict[str, str]:
        brief_path = Path(brief_path)
        comments_path = Path(comments_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        brief_text = brief_path.read_text(encoding="utf-8")
        corpus_analysis = analyze_corpus(comments_path)
        prompt = build_bundle_prompt(brief_text=brief_text, corpus_analysis=corpus_analysis.to_dict())
        request_id = f"noise-bundle-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"

        health = self.client.check_health()
        capacity = self.client.check_capacity()
        bundle = None
        builder = getattr(self.client, "build_bundle", None)
        if callable(builder):
            bundle = builder(
                brief_text=brief_text,
                corpus_analysis=corpus_analysis.to_dict(),
                request_id=request_id,
                symbol=symbol,
            )
        else:
            bundle = self.client.infer_json(stage="noise-bundle", symbol=symbol, prompt=prompt, request_id=request_id)
        validated = self._validate_bundle(bundle)

        combined = {
            "request_id": request_id,
            "brief_text": brief_text,
            "corpus_analysis": corpus_analysis.to_dict(),
            "health": health,
            "capacity": capacity,
            **validated,
        }

        (output_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        (output_dir / "corpus-analysis.json").write_text(
            json.dumps(corpus_analysis.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (output_dir / "bundle.json").write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
        (output_dir / "bundle.md").write_text(render_bundle_markdown(combined), encoding="utf-8")

        raw_exchange = None
        exporter = getattr(self.client, "export_last_exchange", None)
        if callable(exporter):
            raw_exchange = exporter()
        if raw_exchange is None:
            raw_exchange = {"request_id": request_id, "response_json": validated}
        (output_dir / "guivm-response.json").write_text(
            json.dumps(raw_exchange, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return {
            "bundle_path": str(output_dir / "bundle.json"),
            "markdown_path": str(output_dir / "bundle.md"),
            "corpus_analysis_path": str(output_dir / "corpus-analysis.json"),
            "raw_response_path": str(output_dir / "guivm-response.json"),
        }

    def _validate_bundle(self, bundle: dict[str, Any]) -> dict[str, Any]:
        required_top_level = ["selected_angle", "storyboard", "copy_variants", "final_bundle"]
        missing = [key for key in required_top_level if key not in bundle]
        if missing:
            raise ValueError(f"bundle missing required keys: {missing}")
        final_bundle = bundle.get("final_bundle") or {}
        evaluation = final_bundle.get("evaluation_sheet") or {}
        for key in ("interpretation_conflict", "rebuttal_pull", "self_projection_pull", "visual_caption_gap", "brand_damage_risk"):
            value = evaluation.get(key)
            if not isinstance(value, int) or not (1 <= value <= 5):
                raise ValueError(f"invalid evaluation score for {key}: {value!r}")
        return bundle



def render_bundle_markdown(bundle: dict[str, Any]) -> str:
    selected_angle = bundle.get("selected_angle", {})
    storyboard = bundle.get("storyboard", [])
    copy_variants = bundle.get("copy_variants", [])
    final_bundle = bundle.get("final_bundle", {})
    risk_sheet = final_bundle.get("risk_sheet", {})
    evaluation_sheet = final_bundle.get("evaluation_sheet", {})
    operating_sheet = final_bundle.get("operating_sheet", {})

    lines = [
        "# Noise Bundle",
        "",
        "## Concept Sheet",
        f"- title: {selected_angle.get('title', '')}",
        f"- surface_claim: {selected_angle.get('surface_claim', '')}",
        f"- implicit_premise: {selected_angle.get('implicit_premise', '')}",
        f"- meta_message: {selected_angle.get('meta_message', '')}",
        f"- main_axis: {selected_angle.get('main_axis', '')}",
        f"- support_axis: {selected_angle.get('support_axis', '')}",
        f"- background_axis: {selected_angle.get('background_axis', '')}",
        f"- boundary_crossing_scene: {selected_angle.get('boundary_crossing_scene', '')}",
        "",
        "## Storyboard Sheet",
    ]
    for cut in storyboard:
        lines.extend(
            [
                f"- cut {cut.get('cut')}: [{cut.get('function')}] {cut.get('scene')}",
                f"  - expected_comments: {', '.join(cut.get('expected_comments', []))}",
            ]
        )
    lines.extend(["", "## Copy Sheet"])
    for variant in copy_variants:
        lines.extend(
            [
                f"- {variant.get('tone')}: {variant.get('copy')}",
                f"  - intended_reaction: {variant.get('intended_reaction')}",
                f"  - expected_pushback: {variant.get('expected_pushback')}",
                f"  - risk_note: {variant.get('risk_note')}",
            ]
        )
    lines.extend(
        [
            "",
            "## Risk Sheet",
            f"- off_target_drift: {', '.join(risk_sheet.get('off_target_drift', []))}",
            f"- author_attack_risk: {risk_sheet.get('author_attack_risk', '')}",
            f"- sexualization_risk: {risk_sheet.get('sexualization_risk', '')}",
            f"- policy_risk: {risk_sheet.get('policy_risk', '')}",
            "",
            "## Evaluation Sheet",
        ]
    )
    for key, value in evaluation_sheet.items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Operating Sheet",
            f"- first_comment_direction: {operating_sheet.get('first_comment_direction', '')}",
            f"- response_principle: {operating_sheet.get('response_principle', '')}",
            f"- do_not_say: {', '.join(operating_sheet.get('do_not_say', []))}",
            "",
        ]
    )
    return "\n".join(lines)
