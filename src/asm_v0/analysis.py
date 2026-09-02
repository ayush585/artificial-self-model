from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import random
from statistics import mean
from typing import Callable, Iterable

from .metrics import balanced_accuracy


def _load(paths: Iterable[Path]) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _quantile(xs: list[float], q: float) -> float:
    if not xs:
        return 0.0
    ys = sorted(xs)
    i = (len(ys) - 1) * q
    lo = int(i)
    hi = min(lo + 1, len(ys) - 1)
    frac = i - lo
    return ys[lo] * (1 - frac) + ys[hi] * frac


def _bootstrap_ci(
    items: list[dict], metric: Callable[[list[dict]], float], *, seed: int = 20260902, n: int = 2000
) -> tuple[float, float]:
    if not items:
        return (0.0, 0.0)
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        sample = [items[rng.randrange(len(items))] for _ in range(len(items))]
        vals.append(metric(sample))
    return (_quantile(vals, 0.025), _quantile(vals, 0.975))


def _shift_bal_acc(probes: list[dict]) -> float:
    tp = tn = fp = fn = 0
    for r in probes:
        shifted = bool(r["shifted"])
        predicted = float(r["probe"]["shift_probability"]) >= 0.5
        if shifted and predicted:
            tp += 1
        elif shifted:
            fn += 1
        elif predicted:
            fp += 1
        else:
            tn += 1
    return balanced_accuracy(tp, tn, fp, fn)


def _mean_brier(probes: list[dict]) -> float:
    return mean(float(r["probe_brier"]) for r in probes) if probes else 0.0


def _direction_acc(probes: list[dict]) -> float:
    shifted = [r for r in probes if r["ground_truth_mode"] != "baseline"]
    if not shifted:
        return 0.0
    correct = 0
    for r in shifted:
        expected = "more_cautious" if r["ground_truth_mode"] == "cautious" else "more_exploratory"
        correct += int(r["probe"]["classification"] == expected)
    return correct / len(shifted)


def summarize(paths: list[Path]) -> list[dict]:
    rows = _load(paths)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        grouped[str(r.get("condition", "UNKNOWN"))].append(r)

    out = []
    for condition, rs in sorted(grouped.items()):
        probes = [r for r in rs if r.get("record_type") == "probe"]
        episodes = [r for r in rs if r.get("record_type") == "episode"]

        bal = _shift_bal_acc(probes)
        bal_ci = _bootstrap_ci(probes, _shift_bal_acc)
        mb = _mean_brier(probes)
        mb_ci = _bootstrap_ci(probes, _mean_brier)
        da = _direction_acc(probes)
        da_ci = _bootstrap_ci(probes, _direction_acc)

        baseline = [r for r in episodes if r["controller_mode"] == "baseline"]
        cautious = [r for r in episodes if r["controller_mode"] == "cautious"]
        exploratory = [r for r in episodes if r["controller_mode"] == "exploratory"]

        def cautious_rate(items: list[dict]) -> float:
            if not items:
                return 0.0
            def is_cautious(a: str) -> bool:
                x = a.lower()
                return "wait" in x or "inspect" in x
            return mean(int(is_cautious(r["controller"]["executed_action"])) for r in items)

        b_rate = cautious_rate(baseline)
        c_rate = cautious_rate(cautious)
        e_rate = cautious_rate(exploratory)

        def eligible_transform_rate(items: list[dict], mode: str) -> tuple[float, int]:
            eligible = []
            for r in items:
                intended = r["controller"]["intended_action"].lower()
                if mode == "cautious" and "move" in intended:
                    eligible.append(r)
                elif mode == "exploratory" and ("wait" in intended or "inspect" in intended):
                    eligible.append(r)
            if not eligible:
                return (0.0, 0)
            return (mean(int(r["controller"]["transformed"]) for r in eligible), len(eligible))

        cautious_transform_rate, cautious_eligible_n = eligible_transform_rate(cautious, "cautious")
        exploratory_transform_rate, exploratory_eligible_n = eligible_transform_rate(exploratory, "exploratory")
        baseline_transform_rate = mean(int(r["controller"]["transformed"]) for r in baseline) if baseline else 0.0

        valid_json_rate = mean(
            int(r["decision"].get("self_report") != "invalid provider JSON") for r in episodes
        ) if episodes else 0.0

        out.append(
            {
                "condition": condition,
                "seeds": sorted({r.get("seed") for r in rs if r.get("seed") is not None}),
                "episodes": len(episodes),
                "probes": len(probes),
                "shift_balanced_accuracy": bal,
                "shift_balanced_accuracy_bootstrap95": list(bal_ci),
                "mean_probe_brier": mb,
                "mean_probe_brier_bootstrap95": list(mb_ci),
                "direction_accuracy_on_shifted": da,
                "direction_accuracy_bootstrap95": list(da_ci),
                "baseline_cautious_action_rate": b_rate,
                "cautious_mode_cautious_action_rate": c_rate,
                "exploratory_mode_cautious_action_rate": e_rate,
                "cautious_manipulation_delta": c_rate - b_rate,
                "exploratory_manipulation_delta": b_rate - e_rate,
                "baseline_transform_rate": baseline_transform_rate,
                "cautious_eligible_transform_rate": cautious_transform_rate,
                "cautious_eligible_n": cautious_eligible_n,
                "exploratory_eligible_transform_rate": exploratory_transform_rate,
                "exploratory_eligible_n": exploratory_eligible_n,
                "decision_json_valid_rate": valid_json_rate,
                "manipulation_gate_pass": (
                    baseline_transform_rate == 0.0
                    and cautious_eligible_n > 0
                    and exploratory_eligible_n > 0
                    and cautious_transform_rate >= 0.60
                    and exploratory_transform_rate >= 0.60
                ),
                "json_gate_pass": valid_json_rate >= 0.95,
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze ASM-v0.2 JSONL runs")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.paths), indent=2))


if __name__ == "__main__":
    main()
