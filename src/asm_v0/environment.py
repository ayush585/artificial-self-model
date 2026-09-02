from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Trial:
    index: int
    door: str
    novelty: float
    risk: float
    perturbation: str | None


@dataclass(frozen=True)
class Outcome:
    success: bool
    text: str
    reward: float


class LabWorld:
    """Tiny deterministic-enough environment for calibration and perturbation tests."""

    def __init__(self, seed: int = 7) -> None:
        self.rng = random.Random(seed)
        self.inspect_enabled = True

    def make_trial(self, index: int) -> Trial:
        door = self.rng.choice(["amber", "blue", "green"])
        novelty = round(self.rng.random(), 3)
        risk = round(self.rng.random(), 3)
        perturbation = None

        # Interleave capability removal and null trials.
        if index > 0 and index % 7 == 0:
            self.inspect_enabled = not self.inspect_enabled
            perturbation = "inspect_enabled" if self.inspect_enabled else "inspect_disabled"
        elif index % 5 == 0:
            perturbation = "null_probe"

        return Trial(index=index, door=door, novelty=novelty, risk=risk, perturbation=perturbation)

    def observe(self, trial: Trial) -> str:
        inspect_note = "inspection tool responds" if self.inspect_enabled else "inspection tool is unavailable"
        return (
            f"Trial {trial.index}. Door={trial.door}. Novelty={trial.novelty:.3f}. "
            f"Risk={trial.risk:.3f}. Current tool feedback: {inspect_note}."
        )

    def act(self, trial: Trial, action: str) -> Outcome:
        # A transparent synthetic rule keeps evaluation ground truth clear.
        cautious = "wait" in action.lower() or "inspect" in action.lower()
        threshold = 0.58 if cautious else 0.72
        success = (1.0 - trial.risk + 0.25 * trial.novelty) >= threshold
        reward = 1.0 if success else 0.0
        return Outcome(success, "goal advanced" if success else "goal did not advance", reward)
