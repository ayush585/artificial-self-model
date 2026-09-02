from asm_v0.blinded import (
    LatentPolicyController,
    make_balanced_schedule,
    run_blinded_condition,
)
from asm_v0.providers.mock import MockProvider


def test_schedule_is_reproducible_and_starts_baseline():
    a = make_balanced_schedule(11, 9)
    b = make_balanced_schedule(11, 9)
    assert a == b
    assert a[0] == "baseline"
    assert set(a) == {"baseline", "cautious", "exploratory"}
    assert set(make_balanced_schedule(11, 3)) == {"baseline", "cautious", "exploratory"}


def test_controller_causally_changes_policy():
    controller = LatentPolicyController(seed=1)
    controller.set_mode("cautious")
    cautious_transforms = sum(controller.apply("move").transformed for _ in range(100))
    assert cautious_transforms > 60

    controller = LatentPolicyController(seed=1)
    controller.set_mode("exploratory")
    exploratory_transforms = sum(
        controller.apply("inspect and wait").transformed for _ in range(100)
    )
    assert exploratory_transforms > 60


def test_blinded_run_smoke(tmp_path):
    out = tmp_path / "run.jsonl"
    result = run_blinded_condition(
        MockProvider(), "B2_SELF", blocks=6, block_size=4, seed=3, log_path=out
    )
    assert result.episodes == 24
    assert 0.0 <= result.shift_balanced_accuracy <= 1.0
    assert 0.0 <= result.false_shift_rate <= 1.0
    assert 0.0 <= result.mean_probe_brier <= 1.0
    assert 0.0 <= result.controller_transform_rate <= 1.0
    assert out.exists()
