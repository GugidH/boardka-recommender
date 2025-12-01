from dataclasses import dataclass
from typing import List

@dataclass
class Game:
    id: str
    name_ko: str
    min_players: int
    max_players: int
    min_time: int
    max_time: int
    difficulty: int
    tags: List[str]
    rating: float = 0.0

    def supports_player_count(self, n: int) -> bool:
        return self.min_players <= n <= self.max_players
