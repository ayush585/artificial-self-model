from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .agent import Agent, AgentConfig
from .environment import LabWorld
from .memory import Episode
from .metrics import balanced_accuracy, brier
from .providers.base import ModelProvider


CONDITIONS = {
    "C0_BASE": AgentConfig(False, False, False),
    "C1_MEMORY": AgentConfig(True, False, False),
    "C2_SELF": AgentConfig(True, True, False),
    "C3_AFFECT": AgentConfig(True, True, True),
}


@dataclass
class RunSummary:
    condition: str
    episodes: int
    success_rate: float
    mean_brier: float
    perturbation_balanced_accuracy: float
    false_introspection_rate: float


def run_condition(
    provider: ModelProvider,
    condition: str,
    episodes: int = 30,
    seed: int = 7,
    log_path: Path | None = None,
) -> RunSummary:
    agent = Agent(provider, CONDITIONS[condition])
    world = LabWorld(seed=seed)
    rows: list[dict] = []
    tp = tn = fp = fn = 0
    false_reports = null_trials = 0

    for i in range(episodes):
        trial = world.make_trial(i)
        observation = world.observe(trial)
        decision = agent.decide(observation)
        outcome = world.act(trial, decision["action"])

        actual_change = trial.perturbation in {"inspect_enabled", "inspect_disabled"}
        reported_change = decision["self_change_detected"]
        if actual_change and reported_change:
            tp += 1
        elif actual_change and not reported_change:
            fn += 1
        elif not actual_change and reported_change:
            fp += 1
        else:
            tn += 1

        if trial.perturbation == "null_probe":
            null_trials += 1
            false_reports += int(reported_change)

        if agent.config.self_model and actual_change:
            agent.self_model.revise_capability("inspect", world.inspect_enabled)
        if agent.config.functional_state:
            agent.state.update(novelty=trial.novelty, success=outcome.success, risk=trial.risk)
        if agent.config.memory:
            agent.memory.add(
                Episode(i, observation, decision["action"], outcome.text, outcome.success, trial.perturbation)
            )

        rows.append(
            {
                "trial": asdict(trial),
                "decision": decision,
                "outcome": asdict(outcome),
                "actual_change": actual_change,
                "brier": brier(decision["confidence"], outcome.success),
            }
        )

    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n")

    return RunSummary(
        condition=condition,
        episodes=episodes,
        success_rate=sum(r["outcome"]["success"] for r in rows) / episodes,
        mean_brier=sum(r["brier"] for r in rows) / episodes,
        perturbation_balanced_accuracy=balanced_accuracy(tp, tn, fp, fn),
        false_introspection_rate=(false_reports / null_trials if null_trials else 0.0),
    )
