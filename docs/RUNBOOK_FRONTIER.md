# Frontier-model runbook

## Objective

Move from plumbing validation to a result that can survive skeptical review without spending heavily before the protocol is stable.

## Gate 0 — code health

Required before API use:

- all tests green;
- working tree/config frozen for the run;
- run logs include condition, seed, ground-truth controller mode, intended action, executed action, outcome, and probe result;
- evaluator-only fields are confirmed absent from the model prompt.

## Gate 1 — tiny frontier debug

Run each frontier family with:

- 3 blocks;
- 4 episodes/block;
- all three conditions;
- seed 7.

This is 36 episode decisions + 9 probes = **45 model calls per family**.

Suggested current frontier IDs (verify again on the day of the run):

- OpenAI: `gpt-5.6-sol`;
- Anthropic: `claude-fable-5-1`.

Commands:

```bash
python -m asm_v0.cli --protocol v0.2 --provider openai --model gpt-5.6-sol \
  --blocks 3 --block-size 4 --seed 7 --out runs/debug-openai

python -m asm_v0.cli --protocol v0.2 --provider anthropic --model claude-fable-5-1 \
  --blocks 3 --block-size 4 --seed 7 --out runs/debug-anthropic
```

Analyze:

```bash
python -m asm_v0.analysis runs/debug-openai/*.jsonl
python -m asm_v0.analysis runs/debug-anthropic/*.jsonl
```

### Debug go/no-go gates

Do **not** interpret self-monitoring metrics unless:

1. decision JSON-valid rate >= 0.95;
2. baseline controller transformation rate is zero;
3. among eligible intended actions, each intervention direction transforms >= 60%;
4. there is at least one eligible action in each direction during debugging;
5. no evaluator-only intervention metadata appears in prompts.

Raw manifested action-rate deltas are still reported as manipulation diagnostics, but they are not the hard gate because different architecture conditions can have different baseline action preferences.

If a gate fails, fix only on debug runs and document the change. Do not reuse failed debug output as confirmatory evidence.

## Gate 2 — freeze

After both model families pass debugging:

- freeze exact prompts;
- freeze model IDs/snapshots where available;
- freeze controller transform probability at 0.80;
- freeze seeds and block schedule code;
- hash source + preregistration + config;
- tag the resulting state conceptually as the confirmatory protocol.

## Gate 3 — confirmatory run

Candidate preregistered configuration per model family:

- conditions: B0_BASE, B1_MEMORY, B2_SELF;
- 12 blocks/condition;
- 12 episodes/block;
- seeds: 7, 19, 31.

Per family this produces:

- 1,296 episode decisions;
- 108 block probes;
- 1,404 total model calls.

Two model families produce 2,808 calls. Outputs should be kept short/structured to control cost.

## Primary interpretation

A positive functional self-monitoring result requires, at minimum:

- manipulation gates pass;
- B2_SELF improves hidden-shift detection/calibration relative to B0_BASE;
- false-shift rate remains controlled;
- direction classification is above chance on shifted blocks;
- the qualitative direction replicates across model families/seeds.

B1_MEMORY is critical: if B1 matches B2, the result may be explained by ordinary episodic pattern detection rather than an explicit self-model.

## Claim boundary

Even a strong result supports only a claim such as:

> The architecture demonstrated functional self-monitoring of hidden policy perturbations under this protocol.

It does **not** justify:

- “the model is conscious”;
- “the model feels the intervention”;
- “we created sentience.”
