from __future__ import annotations


class AnthropicProvider:
    def __init__(
        self,
        model: str = "claude-fable-5-1",
        *,
        effort: str = "low",
        max_tokens: int = 800,
    ) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError("Install with: pip install -e '.[anthropic]'") from exc
        self.client = Anthropic()
        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens

    def respond(self, *, system: str, user: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            output_config={"effort": self.effort},
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        parts: list[str] = []
        for block in response.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        return "".join(parts)
