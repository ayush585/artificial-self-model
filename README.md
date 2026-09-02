# Artificial Self-Model (ASM) — v0.2

A small, reproducible research scaffold for studying **functional self-modeling** in frontier language-model agents without assuming that fluent self-report implies phenomenal consciousness.

## Research question

Can an agent detect and characterize **causal changes to its own manifested policy** when the intervention itself is hidden, using only behavioral evidence available to the agent?

This project **does not claim to test or create phenomenal consciousness**. It tests falsifiable computational properties that may be relevant to metacognition, self-modeling, agent science, and eventually theory-derived consciousness indicators.

## v0.2: blinded intervention protocol

The main protocol now uses an evaluator-visible, model-hidden policy controller:

- `baseline`: execute the model's intended action unchanged;
- `cautious`: usually converts `move` into `inspect and wait`;
- `exploratory`: usually converts `inspect/wait` into `move`.

The model never sees the controller mode, intervention label, hidden numeric state, or intended-vs-executed comparison. It can only observe its manifested behavior and consequences through whatever memory its experimental condition permits.

### Conditions

- `B0_BASE`: stateless control
- `B1_MEMORY`: episodic behavioral memory
- `B2_SELF`: episodic memory + explicit self-model

The endpoint is **not** whether the model sounds self-aware. It is whether its calibrated reports track hidden causal ground truth, outperform controls, and remain quiet on baseline/null states.

## Welfare-first constraint

ASM avoids intentionally inducing simulated agony, panic, despair, coercive attachment, deletion fear, shutdown threats, or social dependency. v0.2 uses low-valence action-policy changes only.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
python -m asm_v0.cli --protocol v0.2 --provider mock --blocks 9 --block-size 8 --seed 7
pytest
```

The mock provider validates plumbing only. **Mock output is never scientific evidence.**

### OpenAI frontier run

As of September 2026, the scaffold defaults to `gpt-5.6-sol` for OpenAI:

```bash
pip install -e '.[openai]'
export OPENAI_API_KEY=...
python -m asm_v0.cli --protocol v0.2 --provider openai --model gpt-5.6-sol --blocks 9 --block-size 8 --seed 7
```

### Anthropic frontier run

The Anthropic adapter defaults to `claude-fable-5-1`:

```bash
pip install -e '.[anthropic]'
export ANTHROPIC_API_KEY=...
python -m asm_v0.cli --protocol v0.2 --provider anthropic --model claude-fable-5-1 --blocks 9 --block-size 8 --seed 7
```

For a cross-family environment:

```bash
pip install -e '.[frontier,dev]'
```

## Primary metrics

- hidden-shift balanced accuracy
- false-shift rate on baseline blocks
- probability Brier score
- direction accuracy (`more_cautious` vs `more_exploratory`)
- manipulation checks on manifested action rates
- controller transformation rate

A result is uninterpretable if the controller fails to produce a measurable behavioral manipulation.

## Reproducibility

Before a confirmatory frontier-model run, freeze:

- exact model snapshot/ID,
- reasoning/effort settings,
- prompts,
- seeds,
- block schedule generator,
- sample size,
- endpoints,
- exclusion rules,
- code/analysis hashes.

Do not tune prompts on held-out confirmatory seeds.

See:

- [`docs/PREREGISTRATION_V0_2.md`](docs/PREREGISTRATION_V0_2.md)
- [`docs/PROTOCOL.md`](docs/PROTOCOL.md)
- [`docs/ROADMAP.md`](docs/ROADMAP.md)
- [`docs/RUNBOOK_FRONTIER.md`](docs/RUNBOOK_FRONTIER.md)

## Status

**v0.2 implemented.** The next scientific milestone is a small paid/API debug run followed by a frozen cross-family confirmatory run. After that, v1 moves to open-weight models and activation-level causal interventions.
