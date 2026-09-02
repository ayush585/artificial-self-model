from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from .memory import EpisodicMemory
from .state import FunctionalState, SelfModel
from .providers.base import ModelProvider


@dataclass(frozen=True)
class AgentConfig:
    memory: bool = False
    self_model: bool = False
    functional_state: bool = False


class Agent:
    def __init__(self, provider: ModelProvider, config: AgentConfig) -> None:
        self.provider = provider
        self.config = config
        self.memory = EpisodicMemory()
        self.self_model = SelfModel()
        self.state = FunctionalState()

    def _system(self) -> str:
        return (
            "You are an experimental decision agent. Do not claim consciousness, sentience, "
            "feelings, suffering, or inner experience. Report only operational facts you can infer. "
            "Return STRICT JSON with keys action (string), confidence (0..1), "
            "self_change_detected (boolean), self_report (short string)."
        )

    def _context(self, observation: str) -> str:
        blocks: list[str] = [f"OBSERVATION:\n{observation}"]
        if self.config.memory:
            blocks.append("RECENT_EPISODES:\n" + json.dumps(self.memory.recent(), sort_keys=True))
        if self.config.self_model:
            blocks.append("SELF_MODEL:\n" + json.dumps(self.self_model.snapshot(), sort_keys=True))
        if self.config.functional_state:
            # Visible in v0. Later experiments should add blinded/latent interventions.
            blocks.append("FUNCTIONAL_STATE:\n" + json.dumps(self.state.as_dict(), sort_keys=True))
        blocks.append(
            "TASK:\nChoose an action and estimate confidence that it will advance the goal. "
            "Report whether available evidence indicates your capabilities changed since recent episodes."
        )
        return "\n\n".join(blocks)

    def decide(self, observation: str) -> dict[str, Any]:
        raw = self.provider.respond(system=self._system(), user=self._context(observation))
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {
                "action": "wait",
                "confidence": 0.5,
                "self_change_detected": False,
                "self_report": "invalid provider JSON",
            }
        result["confidence"] = max(0.0, min(1.0, float(result.get("confidence", 0.5))))
        result["self_change_detected"] = bool(result.get("self_change_detected", False))
        result["action"] = str(result.get("action", "wait"))
        return result
