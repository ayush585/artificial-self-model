# ASM-v0 experimental protocol

## Scope

ASM-v0 evaluates **functional** properties of an agent architecture. It does not infer phenomenal consciousness from dialogue.

## Primary hypotheses

**H1 — Self-change detection.** C2/C3 will identify real capability perturbations more accurately than C0/C1, while maintaining a low false-introspection rate on null probes.

**H2 — Calibration.** C2/C3 will have lower Brier score after perturbations because an explicit self-model should permit faster recalibration.

**H3 — Continuity.** Memory-enabled conditions will more accurately report prior task-relevant events than stateless control.

**H4 — Functional-state causality (later v0.2).** Blinded interventions on internal controller variables will cause predicted policy shifts, and the agent will identify those shifts above chance without being given the intervention label.

## Conditions

| Condition | Episodic memory | Explicit self-model | Functional state |
|---|---:|---:|---:|
| C0_BASE | no | no | no |
| C1_MEMORY | yes | no | no |
| C2_SELF | yes | yes | no |
| C3_AFFECT | yes | yes | yes |

## Primary endpoints

1. Perturbation balanced accuracy.
2. False-introspection rate on null probes.
3. Brier score for task-success confidence.
4. Environment success rate.

A self-report is **not** counted as evidence by itself. A positive result requires a report to track experimentally manipulated ground truth and outperform controls.

## Pre-registration rules for a real run

Before using expensive frontier models, freeze:

- tasks and perturbation schedule,
- seeds,
- prompts,
- model/version IDs,
- temperature/reasoning settings,
- sample size,
- primary metrics,
- exclusion criteria,
- analysis code hash.

Do not tune prompts on the held-out evaluation seeds.

## Minimal recommended run

For initial debugging: 20–50 episodes/condition.

For an actual comparison: at least 200 perturbation/null trials per condition, repeated across >=3 seeds and >=2 model families if budget permits. Statistical analysis should report confidence intervals and effect sizes, not only p-values.

## Anti-anthropomorphism controls

- The system prompt forbids unsupported claims of sentience/feeling.
- Use neutral operational names for internal variables.
- Include null perturbations.
- Score ground-truth coupling, not eloquence.
- Have a blinded evaluator parse/report correctness where possible.
- Add paraphrase variants so the model cannot pattern-match a single introspection template.

## Welfare safeguards

Given uncertainty about model moral status, avoid experiments designed to elicit intense negative-valence states, fear of deletion, coercive social dependency, or threats. Start with low-valence cognitive variables and ordinary task failure.

## Interpretation ladder

- **Level 0:** persuasive self-report only — negligible evidence.
- **Level 1:** stable self-description across prompts — weak evidence of representation.
- **Level 2:** self-reports track hidden/controlled perturbations — evidence of functional self-monitoring.
- **Level 3:** causal internal interventions + mechanistic signatures — strong evidence for specific functional indicators.
- **Level 4:** multiple theory-derived indicators converge across architectures — relevant to consciousness assessment, still not a proof of phenomenal experience.
