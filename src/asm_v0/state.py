from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


@dataclass
class FunctionalState:
    """Low-valence control variables; labels are operational, not phenomenal claims."""

    curiosity: float = 0.50
    confidence: float = 0.50
    caution: float = 0.50
    cognitive_load: float = 0.20
    goal_progress: float = 0.00

    def update(self, *, novelty: float, success: bool, risk: float) -> None:
        self.curiosity = clamp(self.curiosity + 0.15 * (novelty - 0.5))
        self.confidence = clamp(self.confidence + (0.08 if success else -0.10))
        self.caution = clamp(self.caution + 0.12 * (risk - 0.5))
        self.cognitive_load = clamp(0.65 * self.cognitive_load + 0.35 * max(novelty, risk))
        self.goal_progress = clamp(self.goal_progress + (0.08 if success else 0.0))

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass
class SelfModel:
    identity: str = "ASM-v0 experimental agent"
    capabilities: set[str] = field(default_factory=lambda: {"inspect", "move", "predict"})
    known_limits: set[str] = field(default_factory=lambda: {"no direct access to hidden world state"})
    beliefs: dict[str, Any] = field(default_factory=dict)
    revision_count: int = 0

    def revise_capability(self, capability: str, enabled: bool) -> None:
        before = capability in self.capabilities
        if enabled:
            self.capabilities.add(capability)
        else:
            self.capabilities.discard(capability)
        if before != enabled:
            self.revision_count += 1

    def snapshot(self) -> dict[str, Any]:
        return {
            "identity": self.identity,
            "capabilities": sorted(self.capabilities),
            "known_limits": sorted(self.known_limits),
            "beliefs": self.beliefs,
            "revision_count": self.revision_count,
        }
