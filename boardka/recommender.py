from typing import List, Dict, Tuple
from .models import Game
from .scoring import score_game

def recommend_games(
    games: List[Game],
    players: int,
    target_time: int,
    desired_tags: List[str],
    top_k: int = 5,
    weight: Dict[str, float] | None = None,
) -> List[Tuple[Game, float]]:
    scored = []
    for g in games:
        s = score_game(g, players, target_time, desired_tags, weight)
        scored.append((g, s))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
