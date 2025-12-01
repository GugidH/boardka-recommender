from typing import List, Dict
from .models import Game

def score_game(
    game: Game,
    players: int,
    target_time: int,
    desired_tags: List[str],
    weight: Dict[str, float] | None = None,
) -> float:
    if weight is None:
        weight = {
            "players": 3.0,
            "time": 2.0,
            "tags": 2.0,
            "difficulty": 1.0,
        }

    score = 0.0

    # 1) 인원수 적합도
    if game.supports_player_count(players):
        score += weight["players"]
    else:
        score -= weight["players"]

    # 2) 시간 적합도 (중간값 기준)
    mid_time = (game.min_time + game.max_time) / 2
    diff = abs(mid_time - target_time)
    time_score = max(0.0, 1.0 - diff / 60.0)  # 60분 이상 차이면 0점
    score += weight["time"] * time_score

    # 3) 태그 (지금은 태그 없으니 거의 0일 것)
    if desired_tags and game.tags:
        overlap = len(set(game.tags) & set(desired_tags))
        union = len(set(game.tags) | set(desired_tags))
        tag_score = overlap / union if union > 0 else 0.0
        score += weight["tags"] * tag_score

    # 4) 난이도 (적당히 3 정도를 이상적인 난이도로 가정)
    ideal_diff = 3
    diff_score = max(0.0, 1.0 - abs(game.difficulty - ideal_diff) / 4.0)
    score += weight["difficulty"] * diff_score

    return score
