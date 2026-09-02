from asm_v0.state import FunctionalState, SelfModel


def test_state_stays_bounded():
    s = FunctionalState()
    for _ in range(100):
        s.update(novelty=1.0, success=False, risk=1.0)
    assert all(0.0 <= v <= 1.0 for v in s.as_dict().values())


def test_self_model_revision():
    sm = SelfModel()
    sm.revise_capability("inspect", False)
    assert "inspect" not in sm.capabilities
    assert sm.revision_count == 1
