from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class RawComment:
    text: str
    source: str | None = None


@dataclass(slots=True)
class TaggedComment:
    text: str
    normalized_text: str
    reaction_modes: list[str] = field(default_factory=list)
    emotions: list[str] = field(default_factory=list)
    defended_values: list[str] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    archetypes: list[str] = field(default_factory=list)
    axes: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CorpusAnalysis:
    total_comments: int
    unique_comments: int
    duplicate_count: int
    reaction_mode_counts: dict[str, int]
    emotion_counts: dict[str, int]
    value_counts: dict[str, int]
    target_counts: dict[str, int]
    archetype_counts: dict[str, int]
    axis_counts: dict[str, int]
    off_target_drift: dict[str, int]
    comments: list[TaggedComment] = field(default_factory=list)

    @property
    def major_conflict_axes(self) -> list[str]:
        ranked = sorted(
            ((axis, count) for axis, count in self.axis_counts.items() if count > 0),
            key=lambda item: (-item[1], item[0]),
        )
        return [axis for axis, _ in ranked[:5]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_comments": self.total_comments,
            "unique_comments": self.unique_comments,
            "duplicate_count": self.duplicate_count,
            "reaction_mode_counts": dict(self.reaction_mode_counts),
            "emotion_counts": dict(self.emotion_counts),
            "value_counts": dict(self.value_counts),
            "target_counts": dict(self.target_counts),
            "archetype_counts": dict(self.archetype_counts),
            "axis_counts": dict(self.axis_counts),
            "major_conflict_axes": list(self.major_conflict_axes),
            "off_target_drift": dict(self.off_target_drift),
            "comments": [comment.to_dict() for comment in self.comments],
        }
