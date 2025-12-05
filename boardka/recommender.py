# boardka/recommender.py

from typing import List, Tuple, Optional
from .models import Game
from .scoring import score_game


def recommend_games(
    games: List[Game],
    players: int,
    target_time: Optional[int],
    desired_tags: List[str],
    desired_difficulty: Optional[int] = None,
    top_k: int = 5,
    preferred_tags: Optional[List[str]] = None,  # 선호 태그 (GUI에서 넘겨줄 수 있음)
) -> List[Tuple[Game, float]]:

    # preferred_tags가 None이면 빈 리스트로 처리
    if preferred_tags is None:
        preferred_tags = []

    scored: List[Tuple[Game, float]] = []

    for g in games:
        # 인원 필터 (필수)
        if not g.supports_player_count(players):
            continue

        # 시간 입력이 있을 때만 시간 조건 적용
        if target_time is not None:
            diff = g.time_difference(target_time)

            if diff == 0:
                penalty = 1.0
            elif diff <= 30:
                penalty = 0.7
            else:
                # 30분 이상 차이나면 제외
                continue
        else:
            # 시간 입력이 없으면 페널티 없이 포함
            penalty = 1.0

        # 기본 점수 계산 (태그 + 난이도)
        base_score = score_game(
            g,
            selected_tags=desired_tags,
            preferred_tags=preferred_tags,
            desired_difficulty=desired_difficulty,
        )

        # 최종 점수 = 기본 점수 × 시간 페널티
        final_score = base_score * penalty

        scored.append((g, final_score))

    # 점수 내림차순 정렬 후 상위 top_k개 반환
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
