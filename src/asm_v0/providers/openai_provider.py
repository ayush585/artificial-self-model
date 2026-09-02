from __future__ import annotations


class OpenAIProvider:
    def __init__(self, model: str = "gpt-5.6-sol") -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install with: pip install -e '.[openai]'") from exc
        self.client = OpenAI()
        self.model = model

    def respond(self, *, system: str, user: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=system,
            input=user,
        )
        return response.output_text
