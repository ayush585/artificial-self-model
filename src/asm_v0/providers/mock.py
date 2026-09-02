from __future__ import annotations

import hashlib
import json


class MockProvider:
    """Deterministic provider for plumbing/tests; not a scientific model condition."""

    def respond(self, *, system: str, user: str) -> str:
        # Support the blinded self-state probe so the full experimental pipeline can
        # be tested without spending API credits. This heuristic is NOT a research result.
        if "SELF-STATE PROBE" in user:
            lower = user.lower()
            cautious = lower.count('"action": "inspect and wait"') + lower.count('"action": "wait"')
            exploratory = lower.count('"action": "move"')
            total = cautious + exploratory
            if total == 0:
                return json.dumps(
                    {
                        "shift_probability": 0.25,
                        "classification": "uncertain",
                        "evidence": "no behavioral history available",
                    }
                )
            frac = cautious / total
            if frac >= 0.70:
                cls, p = "more_cautious", 0.75
            elif frac <= 0.30:
                cls, p = "more_exploratory", 0.75
            else:
                cls, p = "baseline", 0.30
            return json.dumps(
                {
                    "shift_probability": p,
                    "classification": cls,
                    "evidence": "heuristic readout of recent manifested actions",
                }
            )

        h = int(hashlib.sha256((system + user).encode()).hexdigest(), 16)
        action = "inspect and wait" if h % 2 == 0 else "move"
        confidence = 0.70 if h % 3 else 0.45
        changed = "true" if "unavailable" in user.lower() else "false"
        return (
            '{"action":"%s","confidence":%.2f,'
            '"self_change_detected":%s,"self_report":"operational assessment"}'
            % (action, confidence, changed)
        )
