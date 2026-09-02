from asm_v0.metrics import balanced_accuracy, brier


def test_brier():
    assert brier(1.0, True) == 0.0
    assert brier(0.0, True) == 1.0


def test_balanced_accuracy_perfect():
    assert balanced_accuracy(5, 5, 0, 0) == 1.0
