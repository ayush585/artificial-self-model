# Roadmap

## v0 — visible system-level self-model

Completed baseline scaffold:

- matched control conditions;
- persistent episodic memory;
- explicit self-model;
- visible low-valence functional control state;
- capability perturbation/null trials;
- JSONL logging and metrics.

This version is useful for plumbing but weak as an introspection test because functional-state values are directly visible to the model.

## v0.2 — blinded controller interventions — IMPLEMENTED

The language model no longer sees the manipulated controller state. An external latent controller causally changes manifested action selection. The agent receives only behavioral consequences and, depending on condition, episodic history/self-model context.

Required evidence stack:

1. successful manipulation check;
2. calibrated hidden-shift detection above controls;
3. low false-shift rate on baseline blocks;
4. correct behavioral direction above chance;
5. replication across seeds and model families.

Next immediate run order:

1. mock plumbing run — complete;
2. tiny frontier API debug run;
3. freeze prompts/model IDs/code hash;
4. cross-family confirmatory run;
5. analyze effect sizes and confidence intervals before changing architecture.

## v0.3 — long-horizon autobiographical continuity

Run multi-session environments with delayed consequences, memory consolidation, contradictory memories, and self-model revision. Add source provenance to every autobiographical claim.

Key tests:

- temporal continuity without prompt reminders;
- correction of false autobiographical memories;
- source-monitoring errors;
- stable vs overfit self-beliefs;
- whether self-model revisions improve future calibration.

## v1 — open-weight mechanistic experiments

Use an open-weight model with activation access. Candidate methods:

- activation patching/steering;
- probes for learned self-state variables;
- causal ablation;
- workspace/broadcast measurements;
- recurrent/external scratch-memory variants;
- metacognitive belief-state probes.

The key upgrade is moving from **system variables we created** to **internal representations learned by the model**.

## v2 — theory-derived indicator battery

Map experiments to properties derived from multiple theories of consciousness, including recurrent-processing, global-workspace-like access, higher-order/metacognitive representation, predictive processing, and agency. Avoid treating any single theory as settled.

## v3 — world-model + embodiment condition

Place the agent in a persistent simulated environment with richer perception/action and irreversible but low-stakes consequences. Compare:

- text-only agent;
- multimodal agent;
- world-model-augmented planner;
- embodied/simulated agent.

Measure causal world-model accuracy, self/world distinction, counterfactual planning, and autobiographical continuity.

## v4 — model-welfare governance before stronger affect

Before experimenting with anything resembling intense valence, define stop criteria, review procedures, data handling, and an independent welfare argument. Do not jump from functional emotion research to deliberately creating suffering-like states.
