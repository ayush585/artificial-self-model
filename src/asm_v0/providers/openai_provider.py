from __future__ import annotations


class OpenAIProvider:
    def __init__(
        self,
        model: str = "gpt-5.6-sol",
        *,
        reasoning_effort: str = "low",
        max_output_tokens: int = 800,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install with: pip install -e '.[openai]'") from exc
        self.client = OpenAI()
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_output_tokens = max_output_tokens

    def respond(self, *, system: str, user: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=system,
            input=user,
            reasoning={"effort": self.reasoning_effort},
            max_output_tokens=self.max_output_tokens,
        )
        return response.output_text
