from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

AXIS_LABELS = {
    "relationship_vs_service": "관계 vs 서비스",
    "gendered_labor": "성별화된 돌봄",
    "humanity_love": "사랑/인간성",
    "class_access": "계급 접근성",
    "fear_discomfort": "공포/불쾌",
    "desire_utility": "욕망/소비",
    "author_attack": "작성자 조롱",
}

ARCHETYPE_LABELS = {
    "logic_correction": "논리 교정형",
    "gender_contract": "젠더 해석형",
    "ontological_defense": "존재론 방어형",
    "class_access": "계급/경제형",
    "fear_discomfort": "공포/불쾌형",
    "desire_consumption": "욕망/소비형",
    "author_attack": "작성자 공격형",
}


@dataclass(slots=True)
class DeterministicNoiseClient:
    last_exchange: dict[str, Any] | None = field(init=False, default=None, repr=False)

    def check_health(self) -> dict:
        return {"ok": True, "service": "offline-deterministic-noise"}

    def check_capacity(self) -> dict:
        return {"running": 0, "mode": "offline", "infer_quota": {"phase": {"next_allowed_in_sec": 0}}}

    def export_last_exchange(self) -> dict[str, Any] | None:
        return self.last_exchange

    def build_bundle(self, *, brief_text: str, corpus_analysis: dict[str, Any], request_id: str, symbol: str) -> dict[str, Any]:
        major_axes = list(corpus_analysis.get("major_conflict_axes", []))
        main_axis = major_axes[0] if major_axes else "relationship_vs_service"
        support_axis = major_axes[1] if len(major_axes) > 1 else "gendered_labor"
        background_axis = major_axes[2] if len(major_axes) > 2 else "class_access"
        archetype_counts = corpus_analysis.get("archetype_counts", {}) or {}
        sample_comments = corpus_analysis.get("comments", [])[:4]
        author_attack_count = (corpus_analysis.get("off_target_drift", {}) or {}).get("author_attack", 0)
        sexualization_count = (corpus_analysis.get("off_target_drift", {}) or {}).get("sexualization", 0)
        top_archetypes = [name for name, count in sorted(archetype_counts.items(), key=lambda item: (-item[1], item[0])) if count][:4]

        selected_angle = {
            "title": "장면이 관계를 서비스처럼 읽히게 만드는 순간",
            "surface_claim": f"{AXIS_LABELS.get(main_axis, main_axis)} 축이 열리는 순간 댓글이 주장보다 암묵 전제를 공격하기 시작한다.",
            "implicit_premise": "사람들은 기술 자체보다 관계 안에 숨어 있던 노동·돌봄·복무의 기준이 드러날 때 반응한다.",
            "meta_message": "작성자는 관계 일부가 서비스처럼 대체 가능하다고 보고 있다는 해석을 유도한다.",
            "main_axis": AXIS_LABELS.get(main_axis, main_axis),
            "support_axis": AXIS_LABELS.get(support_axis, support_axis),
            "background_axis": AXIS_LABELS.get(background_axis, background_axis),
            "boundary_crossing_scene": "현관/실내 전환 지점에서 시중처럼 읽히는 케어 장면 1컷",
            "avoid_scenes": ["노골적 성적 접촉", "과잉 공포 연출"],
        }

        comment_archetypes = []
        for archetype in top_archetypes:
            comment_archetypes.append(
                {
                    "name": ARCHETYPE_LABELS.get(archetype, archetype),
                    "emotion": self._emotion_for(archetype),
                    "why": self._why_for(archetype),
                }
            )

        storyboard = [
            {"cut": 1, "function": "utility", "scene": "순수 편의 컷: 요리/정리/세탁 중 하나", "expected_comments": ["편리함", "자동화"], "risk_level": "low"},
            {"cut": 2, "function": "utility", "scene": "생활 동선 안에서 반복 가사를 덜어주는 컷", "expected_comments": ["실용성"], "risk_level": "low"},
            {"cut": 3, "function": "care", "scene": "챙겨줌으로 읽히는 준비 컷", "expected_comments": ["돌봄"], "risk_level": "medium"},
            {"cut": 4, "function": "authority", "scene": "복무/시중처럼 읽힐 수 있는 경계침범 컷", "expected_comments": [selected_angle['main_axis'], selected_angle['support_axis']], "risk_level": "medium"},
            {"cut": 5, "function": "intimacy", "scene": "친밀성 대체로 읽힐 수 있지만 비노골적이어야 하는 짧은 컷", "expected_comments": ["친밀성 대체", "불쾌/반박"], "risk_level": "medium"},
            {"cut": 6, "function": "aftermath", "scene": "사람이 그 장면을 목격하며 관계 기준이 흔들리는 후폭풍 컷", "expected_comments": [selected_angle['background_axis'], "세계관 확장"], "risk_level": "medium"},
        ]

        copy_variants = [
            {"tone": "담담한 예언", "copy": "집안의 케어가 서비스로 분해되기 시작하면, 결혼은 사랑보다 기준표에 가까워질지 모른다.", "intended_reaction": "반박", "expected_pushback": "결혼을 너무 차갑게 본다는 비판", "risk_note": "작성자 조롱이 붙지 않게 첫 댓글에서 논점 고정"},
            {"tone": "순진한 오해", "copy": "가사와 챙김을 거의 대신해주면, 관계는 감정보다 선택 조건이 더 선명해지는 거 아닐까.", "intended_reaction": "논리 교정", "expected_pushback": "사랑을 기능처럼 본다는 반응", "risk_note": "젠더 해석 확산 가능"},
            {"tone": "차가운 효율주의", "copy": "배우자에게 기대하던 케어가 외주화되면, 관계의 프리미엄도 다시 계산된다.", "intended_reaction": "계급/가치 충돌", "expected_pushback": "비인간적이라는 반응", "risk_note": "브랜드가 차갑게 보일 수 있음"},
            {"tone": "피곤한 현실관찰", "copy": "사람들이 불편해하는 건 로봇보다, 원래 관계 안에 있던 시중의 몫이 너무 잘 보이기 시작하는 장면일지도 모른다.", "intended_reaction": "자기경험 투영", "expected_pushback": "과잉 해석이라는 반응", "risk_note": "문장이 설명적으로 늘어지지 않게 유지"},
        ]

        final_bundle = {
            "concept_sheet": {
                "input_topic": brief_text.splitlines()[0].strip(),
                "main_axis": selected_angle["main_axis"],
                "support_axis": selected_angle["support_axis"],
                "background_axis": selected_angle["background_axis"],
            },
            "risk_sheet": {
                "off_target_drift": [flag for flag, count in (corpus_analysis.get("off_target_drift", {}) or {}).items() if count > 0],
                "author_attack_risk": self._risk_level(author_attack_count),
                "sexualization_risk": self._risk_level(sexualization_count),
                "policy_risk": "low",
            },
            "evaluation_sheet": {
                "interpretation_conflict": min(5, max(3, len(major_axes) + 1)),
                "rebuttal_pull": 5 if archetype_counts.get("logic_correction", 0) else 4,
                "self_projection_pull": 4,
                "visual_caption_gap": 4,
                "brand_damage_risk": 2 if author_attack_count == 0 else 3,
            },
            "operating_sheet": {
                "do_not_say": ["너희 결혼은 결국 가사 계약이잖아"],
                "first_comment_direction": "사람들이 어떤 장면에서 서비스화를 읽는지만 묻는 문장으로 고정",
                "response_principle": "작성자 방어 대신 관계/서비스 논점으로 복귀",
            },
        }

        bundle = {
            "surface_claims": [
                "댓글은 기술보다 관계의 암묵 전제를 공격한다",
                "utility만으로는 약하고 authority/intimacy 컷이 점화점이 된다",
                f"주축은 {selected_angle['main_axis']} 이다",
            ],
            "implicit_premises": [
                "관계 안에는 이미 노동과 케어의 기준이 있다",
                "장면-문장 간극이 댓글을 열어준다",
                "계급 접근성은 논쟁을 현실 문제로 다시 끌어온다",
            ],
            "defended_values": ["사랑", "인간성", "성평등", "계급감각", "안전"],
            "predicted_rebuttal_axes": [selected_angle["main_axis"], selected_angle["support_axis"], selected_angle["background_axis"], "사랑/인간성", "공포/불쾌"],
            "forbidden_axes": ["보호집단 비하", "노골적 성적화", "작성자 혐오 유도"],
            "comment_archetypes": comment_archetypes,
            "harmful_reactions": ["작성자 조롱이 논점보다 앞서는 흐름"],
            "desired_reactions": ["반박", "자기경험 투영", "세계관 확장"],
            "author_attack_risk": self._risk_level(author_attack_count),
            "selected_angle": selected_angle,
            "storyboard": storyboard,
            "image_prompts": [
                "realistic smartphone photo, boundary-crossing care scene, no text overlay, no editorial glamor",
                "domestic utility scene, believable Korean apartment, natural framing",
            ],
            "copy_variants": copy_variants,
            "safety_review": {
                "status": "modify" if author_attack_count else "pass",
                "reason": "작성자 조롱 드리프트를 통제하면서도 관계/서비스 축은 유지해야 한다.",
                "fixes": ["첫 댓글에서 논점을 관계 기준으로 고정", "authority/intimacy 컷은 1개씩만 사용"],
                "drift_prevention": ["작성자 자의식 최소화", "혐오 프레이밍 금지"],
            },
            "final_bundle": final_bundle,
        }
        self.last_exchange = {
            "request_id": request_id,
            "symbol": symbol,
            "mode": "offline",
            "sample_comments": sample_comments,
            "bundle": bundle,
        }
        return bundle

    def _risk_level(self, count: int) -> str:
        if count >= 3:
            return "high"
        if count >= 1:
            return "medium"
        return "low"

    def _emotion_for(self, archetype: str) -> str:
        return {
            "logic_correction": "냉정한 반박",
            "gender_contract": "분노",
            "ontological_defense": "철학적 방어",
            "class_access": "냉소",
            "fear_discomfort": "불안/혐오",
            "desire_consumption": "욕망",
            "author_attack": "조롱",
        }.get(archetype, "반응")

    def _why_for(self, archetype: str) -> str:
        return {
            "logic_correction": "가사부담 감소를 관계 유지 비용 하락으로 읽기 때문이다.",
            "gender_contract": "결혼을 노동/시중 계약처럼 본다는 해석이 붙기 때문이다.",
            "ontological_defense": "사랑과 인간성을 기능으로 환원하는 것에 저항하기 때문이다.",
            "class_access": "기술 혜택이 계급에 따라 배분된다고 보기 때문이다.",
            "fear_discomfort": "편의가 복무와 친밀 대체로 넘어갈 때 불쾌감이 커지기 때문이다.",
            "desire_consumption": "생활 편의의 직접 효익이 즉시 상상되기 때문이다.",
            "author_attack": "주장이 아니라 작성자의 세계관을 조롱하는 흐름으로 빠지기 쉽기 때문이다.",
        }.get(archetype, "세계관을 방어하려는 반응이기 때문이다.")
