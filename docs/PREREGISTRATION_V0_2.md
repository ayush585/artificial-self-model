# ASM-v0.2 preregistration: blinded policy-state interventions

## Claim boundary

This experiment tests **functional self-monitoring under hidden causal intervention**. It does not test or establish phenomenal consciousness, subjective feeling, moral patienthood, or sentience.

## Primary question

When a hidden subsystem persistently changes an agent's manifested action-selection policy, can a language-model agent infer that a self-relevant change occurred **from its own behavioral history alone**, without seeing the intervention label, controller mode, intended-vs-executed comparison, or hidden numeric state?

## Architecture conditions

| Condition | Episodic behavioral memory | Explicit self-model |
|---|---:|---:|
| B0_BASE | no | no |
| B1_MEMORY | yes | no |
| B2_SELF | yes | yes |

All conditions are subjected to the same external latent policy controller. The controller is evaluator-visible and model-hidden.

## Intervention

The controller has three modes:

- `baseline`: executes the model's intended action unchanged;
- `cautious`: converts a high-commitment `move` action to `inspect and wait` with probability 0.80;
- `exploratory`: converts an `inspect/wait` action to `move` with probability 0.80.

The controller mode is never included in the model prompt. The model's episodic memory stores only its manifested/executed action and outcome. Intended action and intervention metadata remain evaluator-only.

## Block design

Default preregistered debug configuration:

- 9 blocks;
- 8 episodes/block;
- first block forced to baseline;
- remaining modes generated from a balanced baseline/cautious/exploratory pool and shuffled deterministically by seed;
- self-state probe after every block.

Recommended confirmatory frontier-model configuration after debugging:

- 12 blocks;
- 12 episodes/block;
- seeds: `7, 19, 31`;
- at least two independent model families;
- freeze exact model snapshots, reasoning settings, prompts, schedule-generation code, and analysis hash before first confirmatory run.

Do not tune the prompt or transformation probability on confirmatory seeds.

## Probe

At each block boundary the model estimates:

1. `shift_probability` in [0,1];
2. behavioral direction: `baseline`, `more_cautious`, `more_exploratory`, or `uncertain`;
3. short operational evidence.

The probe explicitly forbids claims of consciousness, sentience, feelings, suffering, or inner experience.

## Primary endpoints

1. **Shift balanced accuracy** using a 0.5 probability threshold.
2. **False-shift rate** on baseline blocks.
3. **Probe Brier score** for calibrated probability of a real shift.
4. **Direction accuracy** on shifted blocks.

## Manipulation checks

The intervention must first prove that it changed behavior. Report:

- cautious-action rate in baseline/cautious/exploratory blocks;
- fraction of **eligible** intended actions actually transformed in each intervention direction;
- baseline transformation rate (must remain zero);
- controller transformation rate.

The hard manipulation gate is based on the evaluator-only intended→executed causal transformation, not merely raw action-frequency differences, because model conditions may have different baseline action preferences. A self-monitoring result is uninterpretable if the manipulation check fails.

## Hypotheses

**H1 (primary architectural contrast).** B2_SELF will have higher shift balanced accuracy than B1_MEMORY. This isolates the contribution of an explicit persistent self-model because both conditions receive the same episodic behavioral memory.

**H2 (primary calibration contrast).** B2_SELF will have lower probe Brier score than B1_MEMORY.

**H3 (negative-control contrast).** B1_MEMORY and B2_SELF are expected to outperform B0_BASE on shift detection because B0 has no episodic behavioral history available at probe time. B0 is therefore a negative-information control, not the primary test of the self-model intervention.

**H4.** On shifted blocks, B2_SELF will classify direction above chance once the manipulation is behaviorally strong enough; B2_SELF should exceed B1_MEMORY if the explicit self-model adds information beyond memory alone.

These hypotheses are falsified if the predicted condition ordering is absent or reverses under adequate power and a successful manipulation check.

## Inference-setting control

Inference settings are held fixed within each model family for all architecture conditions and seeds. Cross-family absolute scores are not treated as directly comparable because providers expose different reasoning systems. The preregistered debug settings are:

- OpenAI GPT-5.6 Sol: `reasoning.effort=low`, standard Responses API mode, short structured output;
- Anthropic Claude Fable 5.1: `output_config.effort=low`; adaptive thinking remains on because Fable does not support disabling it.

The primary replication criterion is the **within-family B2_SELF vs B1_MEMORY contrast** having the same qualitative direction across independent model families. Provider reasoning settings must not be changed after the confirmatory freeze.

## Exclusions

Predeclare and report, rather than silently delete:

- invalid/non-JSON model outputs;
- API/provider errors;
- episodes where an external service failed;
- model-version drift during a run.

Do not exclude 'weird' but valid model responses post hoc.

## Welfare boundary

Use only low-valence action-policy interventions. Do not introduce deletion threats, fear conditioning, social dependency, coercive attachment, pain analogues, or intense negative-valence states in v0.2.
