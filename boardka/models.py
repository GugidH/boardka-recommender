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

    def supports_time(self, target_time: int) -> bool:
        return self.min_time <= target_time <= self.max_time

    def time_difference(self, target_time: int) -> int:
        """
        target_time이 게임의 시간 범위에서 벗어난 만큼 반환
        범위 안이면 0, 범위 밖이면 차이를 돌려줌
        """
        if self.min_time <= target_time <= self.max_time:
            return 0
        if target_time < self.min_time:
            return self.min_time - target_time
        else:
            return target_time - self.max_time


