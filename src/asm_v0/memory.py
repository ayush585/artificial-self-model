from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Episode:
    index: int
    observation: str
    action: str
    outcome: str
    success: bool
    perturbation: str | None = None


class EpisodicMemory:
    def __init__(self, max_items: int = 200) -> None:
        self.max_items = max_items
        self._episodes: list[Episode] = []

    def add(self, episode: Episode) -> None:
        self._episodes.append(episode)
        if len(self._episodes) > self.max_items:
            self._episodes = self._episodes[-self.max_items :]

    def recent(self, n: int = 6) -> list[dict]:
        return [asdict(x) for x in self._episodes[-n:]]

    def __len__(self) -> int:
        return len(self._episodes)
