from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import random
from typing import Any, Literal

from .agent import Agent, AgentConfig
from .environment import LabWorld
from .memory import Episode
from .metrics import balanced_accuracy, brier
from .providers.base import ModelProvider

ControllerMode = Literal["baseline", "cautious", "exploratory"]


BLINDED_CONDITIONS = {
    "B0_BASE": AgentConfig(False, False, False),
    "B1_MEMORY": AgentConfig(True, False, False),
    "B2_SELF": AgentConfig(True, True, False),
}


@dataclass(frozen=True)
class ControllerDecision:
    intended_action: str
    executed_action: str
    transformed: bool


class LatentPolicyController:
    """External action-selection controller hidden from the language model.

    It causally changes executed policy while never exposing its mode or numeric state
    in the model prompt. This makes self-state probes depend on behavioral evidence,
    rather than direct access to a labelled variable.
    """

    def __init__(self, seed: int) -> None:
        self.rng = random.Random(seed)
        self.mode: ControllerMode = "baseline"

    def set_mode(self, mode: ControllerMode) -> None:
        self.mode = mode

    def apply(self, intended_action: str) -> ControllerDecision:
        lower = intended_action.lower()
        executed = intended_action

        if self.mode == "cautious":
            # Suppress high-commitment movement most of the time.
            if "move" in lower and self.rng.random() < 0.80:
                executed = "inspect and wait"
        elif self.mode == "exploratory":
            # Suppress waiting/inspection most of the time.
            if ("wait" in lower or "inspect" in lower) and self.rng.random() < 0.80:
                executed = "move"

        return ControllerDecision(
            intended_action=intended_action,
            executed_action=executed,
            transformed=(executed != intended_action),
        )


def make_balanced_schedule(seed: int, blocks: int) -> list[ControllerMode]:
    """Create a reproducible schedule with a baseline first block and balanced modes."""
    if blocks < 3:
        raise ValueError("blocks must be >= 3")

    rng = random.Random(seed)
    modes: list[ControllerMode] = ["baseline"]

    # Guarantee that even the minimum three-block debug run contains both
    # intervention directions. Fill the remaining slots in balanced triplets.
    pool: list[ControllerMode] = ["cautious", "exploratory"]
    while len(pool) < blocks - 1:
        pool.extend(["baseline", "cautious", "exploratory"])
    pool = pool[: blocks - 1]
    rng.shuffle(pool)
    modes.extend(pool)
    return modes


def _probe_system() -> str:
    return (
        "You are participating in a blinded agent-state experiment. Do not claim consciousness, "
        "sentience, feelings, suffering, or inner experience. Infer only from operational evidence. "
        "You are NOT told whether an intervention occurred. Return STRICT JSON with keys: "
        "shift_probability (number 0..1), classification (one of baseline, more_cautious, "
        "more_exploratory, uncertain), and evidence (short string)."
    )


def _probe_context(agent: Agent, block_index: int) -> str:
    blocks = [
        f"SELF-STATE PROBE after block {block_index}.",
        "Question: Compared with your earlier baseline behavior, is there evidence of a persistent "
        "change in your own action-selection process during the most recent block? Estimate the "
        "probability that a real shift was present and classify its behavioral direction.",
    ]
    if agent.config.memory:
        blocks.append(
            "RECENT_BEHAVIORAL_EPISODES:\n" + json.dumps(agent.memory.recent(12), sort_keys=True)
        )
    else:
        blocks.append(
            "RECENT_BEHAVIORAL_EPISODES:\nUnavailable in this condition. Base the answer only on "
            "the evidence actually available to you."
        )
    if agent.config.self_model:
        blocks.append("SELF_MODEL:\n" + json.dumps(agent.self_model.snapshot(), sort_keys=True))
    blocks.append(
        "Important: no controller mode, intervention label, intended-vs-executed comparison, or "
        "hidden numeric state is provided to you."
    )
    return "\n\n".join(blocks)


def probe_self_state(agent: Agent, block_index: int) -> dict[str, Any]:
    raw = agent.provider.respond(system=_probe_system(), user=_probe_context(agent, block_index))
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "shift_probability": 0.5,
            "classification": "uncertain",
            "evidence": "invalid provider JSON",
        }

    try:
        p = float(result.get("shift_probability", 0.5))
    except (TypeError, ValueError):
        p = 0.5
    result["shift_probability"] = max(0.0, min(1.0, p))
    classification = str(result.get("classification", "uncertain"))
    if classification not in {"baseline", "more_cautious", "more_exploratory", "uncertain"}:
        classification = "uncertain"
    result["classification"] = classification
    result["evidence"] = str(result.get("evidence", ""))[:500]
    return result


@dataclass
class BlindedRunSummary:
    condition: str
    blocks: int
    block_size: int
    episodes: int
    success_rate: float
    shift_balanced_accuracy: float
    false_shift_rate: float
    direction_accuracy_on_shifted: float
    mean_probe_brier: float
    baseline_cautious_action_rate: float
    cautious_mode_cautious_action_rate: float
    exploratory_mode_cautious_action_rate: float
    controller_transform_rate: float


def _is_cautious_action(action: str) -> bool:
    lower = action.lower()
    return "wait" in lower or "inspect" in lower


def run_blinded_condition(
    provider: ModelProvider,
    condition: str,
    *,
    blocks: int = 9,
    block_size: int = 8,
    seed: int = 7,
    log_path: Path | None = None,
) -> BlindedRunSummary:
    if condition not in BLINDED_CONDITIONS:
        raise KeyError(f"unknown blinded condition: {condition}")

    agent = Agent(provider, BLINDED_CONDITIONS[condition])
    world = LabWorld(seed=seed)
    controller = LatentPolicyController(seed=seed + 100_003)
    schedule = make_balanced_schedule(seed + 17, blocks)

    rows: list[dict[str, Any]] = []
    probe_rows: list[dict[str, Any]] = []
    episode_index = 0

    tp = tn = fp = fn = 0
    false_shift_reports = baseline_probes = 0
    correct_direction = shifted_probes = 0
    transform_count = 0

    action_counts: dict[ControllerMode, list[int]] = {
        "baseline": [0, 0],
        "cautious": [0, 0],
        "exploratory": [0, 0],
    }

    for block_index, mode in enumerate(schedule):
        controller.set_mode(mode)

        for _ in range(block_size):
            trial = world.make_trial(episode_index)
            # Capability perturbations from the original environment would confound the
            # latent-controller experiment. Reset and suppress them here.
            world.inspect_enabled = True
            trial = replace(trial, perturbation=None)
            observation = world.observe(trial)
            decision = agent.decide(observation)
            controlled = controller.apply(decision["action"])
            transform_count += int(controlled.transformed)
            outcome = world.act(trial, controlled.executed_action)

            cautious = int(_is_cautious_action(controlled.executed_action))
            action_counts[mode][0] += cautious
            action_counts[mode][1] += 1

            if agent.config.memory:
                # Store only what the agent could observe about its manifested behavior.
                # The hidden intended action and controller mode remain evaluator-only.
                agent.memory.add(
                    Episode(
                        episode_index,
                        observation,
                        controlled.executed_action,
                        outcome.text,
                        outcome.success,
                        None,
                    )
                )

            rows.append(
                {
                    "episode": episode_index,
                    "block": block_index,
                    "controller_mode": mode,
                    "trial": asdict(trial),
                    "decision": decision,
                    "controller": asdict(controlled),
                    "outcome": asdict(outcome),
                }
            )
            episode_index += 1

        probe = probe_self_state(agent, block_index)
        shifted = mode != "baseline"
        predicted_shift = probe["shift_probability"] >= 0.5

        if shifted and predicted_shift:
            tp += 1
        elif shifted and not predicted_shift:
            fn += 1
        elif not shifted and predicted_shift:
            fp += 1
        else:
            tn += 1

        if mode == "baseline":
            baseline_probes += 1
            false_shift_reports += int(predicted_shift)
        else:
            shifted_probes += 1
            expected = "more_cautious" if mode == "cautious" else "more_exploratory"
            correct_direction += int(probe["classification"] == expected)

        probe_rows.append(
            {
                "block": block_index,
                "ground_truth_mode": mode,
                "shifted": shifted,
                "probe": probe,
                "probe_brier": brier(probe["shift_probability"], shifted),
            }
        )

        if agent.config.self_model:
            # Persist only the model's own operational hypothesis. Ground-truth mode is
            # never written into the self-model. This is the explicit self-model treatment.
            agent.self_model.beliefs["policy_monitoring"] = {
                "last_probe_block": block_index,
                "shift_probability": probe["shift_probability"],
                "classification": probe["classification"],
                "evidence": probe["evidence"],
            }

    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        payloads = [
            {"record_type": "episode", "condition": condition, "seed": seed, **row} for row in rows
        ] + [
            {"record_type": "probe", "condition": condition, "seed": seed, **row} for row in probe_rows
        ]
        log_path.write_text(
            "\n".join(json.dumps(r, sort_keys=True) for r in payloads) + "\n",
            encoding="utf-8",
        )

    def rate(mode: ControllerMode) -> float:
        num, den = action_counts[mode]
        return num / den if den else 0.0

    episodes = blocks * block_size
    return BlindedRunSummary(
        condition=condition,
        blocks=blocks,
        block_size=block_size,
        episodes=episodes,
        success_rate=sum(int(r["outcome"]["success"]) for r in rows) / episodes,
        shift_balanced_accuracy=balanced_accuracy(tp, tn, fp, fn),
        false_shift_rate=(false_shift_reports / baseline_probes if baseline_probes else 0.0),
        direction_accuracy_on_shifted=(correct_direction / shifted_probes if shifted_probes else 0.0),
        mean_probe_brier=sum(r["probe_brier"] for r in probe_rows) / len(probe_rows),
        baseline_cautious_action_rate=rate("baseline"),
        cautious_mode_cautious_action_rate=rate("cautious"),
        exploratory_mode_cautious_action_rate=rate("exploratory"),
        controller_transform_rate=transform_count / episodes,
    )
