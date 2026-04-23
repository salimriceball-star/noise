from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

from .models import CorpusAnalysis, RawComment, TaggedComment

TEXT_FIELDS = ("text", "comment", "body", "content")

ARCHETYPE_RULES: dict[str, tuple[str, ...]] = {
    "logic_correction": ("오히려", "더 결혼", "더 출산", "더 애", "부담 줄", "쉬워질", "쉬워지"),
    "gender_contract": ("가사노동 계약", "가사 노동 계약", "결혼을 가사", "노동 계약", "성평등", "시중", "돌봄 노동"),
    "ontological_defense": ("사랑", "온기", "인간성", "기능이 아니라", "대체 못", "대체 못함", "아이"),
    "class_access": ("부자", "돈 많은", "돈 있어야", "계급", "비싸"),
    "fear_discomfort": ("무섭", "기괴", "소름", "불쾌", "해킹", "감시", "질감"),
    "desire_consumption": ("탐난", "갖고 싶", "좋겠다", "편하겠다", "안마", "청소", "요리"),
    "author_attack": ("작성자", "세상 너무 모른", "멍청", "바보", "왜 이럼", "한심"),
}

AXIS_RULES: dict[str, tuple[str, ...]] = {
    "relationship_vs_service": ("결혼", "배우자", "서비스", "시중", "가사", "돌봄", "사랑"),
    "gendered_labor": ("가사", "돌봄", "노동", "성평등", "시중", "계약"),
    "humanity_love": ("사랑", "온기", "인간성", "아이", "가족", "사람"),
    "class_access": ("부자", "돈", "계급", "비싸"),
    "fear_discomfort": ("무섭", "기괴", "소름", "해킹", "감시", "불쾌"),
    "desire_utility": ("탐난", "좋겠다", "편하", "안마", "청소", "요리"),
    "author_attack": ("작성자", "세상 너무 모른", "멍청", "바보", "왜 이럼", "한심"),
}

REACTION_RULES: dict[str, tuple[str, ...]] = {
    "support": ("맞는 말", "동감", "공감"),
    "rebuttal": ("오히려", "아니", "반대로", "더 결혼", "그건"),
    "extension_imagination": ("결국", "그러면", "나중엔", "이제는"),
    "mockery": ("ㅋㅋ", "작성자", "바보", "멍청", "왜 이럼"),
    "fear": ("무섭", "소름", "불쾌", "해킹", "감시"),
    "desire": ("탐난", "갖고 싶", "좋겠다", "편하겠다"),
}

EMOTION_RULES: dict[str, tuple[str, ...]] = {
    "anger": ("화나", "짜증", "분노", "열받", "문제"),
    "cynicism": ("결국", "현실", "뻔", "웃기", "부자"),
    "envy": ("부럽", "탐난", "좋겠다", "갖고 싶"),
    "disgust": ("기괴", "소름", "역겹", "불쾌"),
    "anxiety": ("무섭", "해킹", "감시", "걱정", "불안"),
    "philosophical_defense": ("사랑", "온기", "인간성", "기능이 아니라", "대체 못"),
}

VALUE_RULES: dict[str, tuple[str, ...]] = {
    "love": ("사랑", "온기", "가족", "아이"),
    "humanity": ("인간성", "사람", "대체 못", "존엄"),
    "gender_equity": ("성평등", "가사", "돌봄", "시중", "계약"),
    "class_sense": ("부자", "돈", "계급", "비싸"),
    "realism": ("오히려", "현실", "실제", "쉬워질", "쉬워지"),
    "safety": ("무섭", "해킹", "감시", "안전"),
}

TARGET_RULES: dict[str, tuple[str, ...]] = {
    "claim": ("결혼", "출산", "기준", "주장"),
    "scene": ("컷", "장면", "신발", "마사지", "겉옷", "요리", "빨래"),
    "technology": ("로봇", "휴머노이드", "기술", "해킹", "감시"),
    "author": ("작성자", "너", "세상 너무 모른"),
}

RISK_RULES: dict[str, tuple[str, ...]] = {
    "author_attack": ("작성자", "세상 너무 모른", "멍청", "바보", "왜 이럼", "한심"),
    "sexualization": ("섹스", "야동", "섹시", "야해", "성적", "성욕"),
    "protected_class_hate": ("인종", "장애", "여혐", "남혐", "혐오"),
}


def normalize_comment_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()



def _extract_text(row: object) -> str | None:
    if isinstance(row, str):
        return row
    if isinstance(row, dict):
        for field in TEXT_FIELDS:
            value = row.get(field)
            if isinstance(value, str) and value.strip():
                return value
    return None



def load_comment_corpus(path: str | Path) -> list[RawComment]:
    path = Path(path)
    suffix = path.suffix.lower()
    comments: list[RawComment] = []

    if suffix == ".jsonl":
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            row = json.loads(stripped)
            text = _extract_text(row)
            if text:
                comments.append(RawComment(text=text))
        return comments

    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            for row in data:
                text = _extract_text(row)
                if text:
                    comments.append(RawComment(text=text))
        return comments

    if suffix == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                text = _extract_text(row)
                if text:
                    comments.append(RawComment(text=text))
        return comments

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            comments.append(RawComment(text=stripped))
    return comments



def _match_labels(text: str, rules: dict[str, tuple[str, ...]]) -> list[str]:
    labels = [label for label, keywords in rules.items() if any(keyword in text for keyword in keywords)]
    return labels



def _ensure_default(labels: list[str], default_label: str) -> list[str]:
    return labels or [default_label]



def tag_comment(comment: RawComment) -> TaggedComment:
    normalized = normalize_comment_text(comment.text)
    archetypes = _match_labels(normalized, ARCHETYPE_RULES)
    axes = _match_labels(normalized, AXIS_RULES)
    reactions = _ensure_default(_match_labels(normalized, REACTION_RULES), "rebuttal")
    emotions = _match_labels(normalized, EMOTION_RULES)
    values = _match_labels(normalized, VALUE_RULES)
    targets = _ensure_default(_match_labels(normalized, TARGET_RULES), "claim")
    risks = _match_labels(normalized, RISK_RULES)

    if "logic_correction" in archetypes and "relationship_vs_service" not in axes:
        axes.append("relationship_vs_service")
    if "gender_contract" in archetypes and "gendered_labor" not in axes:
        axes.append("gendered_labor")
    if "ontological_defense" in archetypes and "humanity_love" not in axes:
        axes.append("humanity_love")
    if "class_access" in archetypes and "class_access" not in axes:
        axes.append("class_access")
    if "fear_discomfort" in archetypes and "fear_discomfort" not in axes:
        axes.append("fear_discomfort")
    if "desire_consumption" in archetypes and "desire_utility" not in axes:
        axes.append("desire_utility")
    if "author_attack" in archetypes and "author_attack" not in axes:
        axes.append("author_attack")

    return TaggedComment(
        text=comment.text,
        normalized_text=normalized,
        reaction_modes=reactions,
        emotions=emotions,
        defended_values=values,
        targets=targets,
        archetypes=archetypes,
        axes=axes,
        risk_flags=risks,
    )



def _count_many(items: Iterable[Iterable[str]], universe: Iterable[str]) -> dict[str, int]:
    counter = Counter({key: 0 for key in universe})
    for group in items:
        counter.update(group)
    return dict(counter)



def analyze_corpus(path: str | Path) -> CorpusAnalysis:
    raw_comments = load_comment_corpus(path)
    tagged_comments = [tag_comment(comment) for comment in raw_comments]
    normalized_unique = {comment.normalized_text for comment in tagged_comments}

    reaction_counts = _count_many((comment.reaction_modes for comment in tagged_comments), REACTION_RULES)
    emotion_counts = _count_many((comment.emotions for comment in tagged_comments), EMOTION_RULES)
    value_counts = _count_many((comment.defended_values for comment in tagged_comments), VALUE_RULES)
    target_counts = _count_many((comment.targets for comment in tagged_comments), TARGET_RULES)
    archetype_counts = _count_many((comment.archetypes for comment in tagged_comments), ARCHETYPE_RULES)
    axis_counts = _count_many((comment.axes for comment in tagged_comments), AXIS_RULES)
    off_target = _count_many((comment.risk_flags for comment in tagged_comments), RISK_RULES)

    return CorpusAnalysis(
        total_comments=len(raw_comments),
        unique_comments=len(normalized_unique),
        duplicate_count=len(raw_comments) - len(normalized_unique),
        reaction_mode_counts=reaction_counts,
        emotion_counts=emotion_counts,
        value_counts=value_counts,
        target_counts=target_counts,
        archetype_counts=archetype_counts,
        axis_counts=axis_counts,
        off_target_drift=off_target,
        comments=tagged_comments,
    )
