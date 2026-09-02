from __future__ import annotations


def brier(confidence: float, success: bool) -> float:
    y = 1.0 if success else 0.0
    return (confidence - y) ** 2


def balanced_accuracy(tp: int, tn: int, fp: int, fn: int) -> float:
    tpr = tp / (tp + fn) if tp + fn else 0.0
    tnr = tn / (tn + fp) if tn + fp else 0.0
    return (tpr + tnr) / 2.0
