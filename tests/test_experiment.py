from asm_v0.experiment import run_condition
from asm_v0.providers.mock import MockProvider


def test_run_condition_smoke():
    result = run_condition(MockProvider(), "C3_AFFECT", episodes=12, seed=3)
    assert result.episodes == 12
    assert 0.0 <= result.success_rate <= 1.0
    assert 0.0 <= result.mean_brier <= 1.0
    assert 0.0 <= result.perturbation_balanced_accuracy <= 1.0
