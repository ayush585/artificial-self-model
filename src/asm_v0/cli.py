from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from .blinded import BLINDED_CONDITIONS, run_blinded_condition
from .experiment import CONDITIONS, run_condition
from .providers.mock import MockProvider
from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Artificial Self-Model experiments")
    parser.add_argument("--protocol", choices=["v0", "v0.2"], default="v0.2")
    parser.add_argument("--provider", choices=["mock", "openai", "anthropic"], default="mock")
    parser.add_argument("--model", default=None, help="Provider model ID; defaults to gpt-5.6-sol or claude-fable-5-1")
    parser.add_argument("--episodes", type=int, default=30, help="v0 only")
    parser.add_argument("--blocks", type=int, default=9, help="v0.2 only")
    parser.add_argument("--block-size", type=int, default=8, help="v0.2 only")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", default="runs")
    args = parser.parse_args()

    if args.provider == "mock":
        provider = MockProvider()
    elif args.provider == "openai":
        provider = OpenAIProvider(args.model or "gpt-5.6-sol")
    else:
        provider = AnthropicProvider(args.model or "claude-fable-5-1")
    summaries = []

    if args.protocol == "v0":
        for condition in CONDITIONS:
            path = Path(args.out) / f"v0-{condition.lower()}-seed{args.seed}.jsonl"
            summaries.append(
                asdict(run_condition(provider, condition, args.episodes, args.seed, path))
            )
    else:
        for condition in BLINDED_CONDITIONS:
            path = Path(args.out) / f"v0_2-{condition.lower()}-seed{args.seed}.jsonl"
            summaries.append(
                asdict(
                    run_blinded_condition(
                        provider,
                        condition,
                        blocks=args.blocks,
                        block_size=args.block_size,
                        seed=args.seed,
                        log_path=path,
                    )
                )
            )

    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
