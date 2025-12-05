# boardka/recommender.py

from typing import List, Tuple, Optional
from .models import Game
from .scoring import score_game


def recommend_games(
    games: List[Game],
    players: int,
    target_time: int,
    desired_tags: List[str],
    desired_difficulty: Optional[int] = None,
    top_k: int = 5,
) -> List[Tuple[Game, float]]:
    """
    인원/시간으로 1차 필터링
    인원: 정확히 맞는 게임만
    시간:
        범위 안이면 패널티 1.0
        30분 이내 차이면 패널티 0.7
        30분 이상 차이면 탈락

    필터 통과한 게임들에 대해 태그 + 난이도 점수 계산
    시간 패널티 합해서 최종 점수

    최종 점수 기준으로 상위 top_k 반환
    """
    scored: List[Tuple[Game, float]] = []

    for g in games:
        # 1) 인원 필터: 정확히 맞는 게임만
        if not g.supports_player_count(players):
            continue

        # 2) 시간 차이 / 페널티 계산
        diff = g.time_difference(target_time)

        if diff == 0:
            penalty = 1.0
        elif 0 < diff <= 30:
            penalty = 0.7  # -30% 페널티
        else:
            # 30분보다 많이 차이나면 후보에서 제외
            continue

        # 3) 태그 + 난이도 기반 기본 점수 계산
        base_score = score_game(
            game=g,
            desired_tags=desired_tags,
            desired_difficulty=desired_difficulty,
        )

        # 4) 시간 페널티 적용
        final_score = base_score * penalty

        scored.append((g, final_score))

    # 점수 기준 내림차순 정렬
    scored.sort(key=lambda x: x[1], reverse=True)

    # 상위 top_k만 반환
    return scored[:top_k]

