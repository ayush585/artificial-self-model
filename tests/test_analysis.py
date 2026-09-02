from pathlib import Path

from asm_v0.analysis import summarize
from asm_v0.blinded import run_blinded_condition
from asm_v0.providers.mock import MockProvider


def test_analysis_smoke(tmp_path: Path):
    p = tmp_path / "b1.jsonl"
    run_blinded_condition(MockProvider(), "B1_MEMORY", blocks=6, block_size=6, seed=7, log_path=p)
    rows = summarize([p])
    assert len(rows) == 1
    assert rows[0]["condition"] == "B1_MEMORY"
    assert rows[0]["episodes"] == 36
    assert len(rows[0]["shift_balanced_accuracy_bootstrap95"]) == 2
