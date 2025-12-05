# boardka/scoring.py

from typing import List, Optional
from .models import Game

# 상수 정의: 태그 / 난이도 최대 점수
MAX_TAG_SCORE = 40.0
MAX_DIFF_SCORE = 40.0

# 난이도 기본값: 사용자가 입력하지 않았을 때
DEFAULT_DESIRED_DIFFICULTY = 2


def compute_tag_score(game: Game, desired_tags: List[str]) -> float:
    """
    게임의 태그와 사용자가 입력한 태그가 겹치는 정도에 따라
    0 ~ 40점 사이의 점수를 계산
    """
    if not desired_tags or not game.tags:
        return 0.0

    # 공백 제거 후 집합으로 변환
    desired = {t.strip() for t in desired_tags if t.strip()}
    actual = {t.strip() for t in game.tags if t.strip()}

    if not desired or not actual:
        return 0.0

    overlap = len(desired & actual)
    if overlap == 0:
        return 0.0

    # 원하는 태그 중 몇 개나 맞았는지 비율 (0.0 ~ 1.0)
    ratio = overlap / len(desired)

    # 0.0 ~ 1.0 → 0 ~ 40점으로 스케일링
    return MAX_TAG_SCORE * ratio


def compute_difficulty_score(
    game: Game,
    desired_difficulty: Optional[int],
) -> float:
    """
    게임 난이도와 사용자 입력 난이도의 차이에 따라
    0 ~ 40점 사이의 점수를 계산
    """
    if desired_difficulty is None:
        desired_difficulty = DEFAULT_DESIRED_DIFFICULTY

    # 타입 문제 방지
    gd = int(game.difficulty)
    dd = int(desired_difficulty)

    diff = abs(gd - dd)

    if diff == 0:
        return MAX_DIFF_SCORE
    elif diff == 1:
        return MAX_DIFF_SCORE * 0.4
    else:
        return 0.0


def score_game(
    game: Game,
    desired_tags: List[str],
    desired_difficulty: Optional[int],
) -> float:
    """
    태그, 난이도로 기본 점수 계산
    시간/인원 관련 페널티는 recommender.py 쪽에서 따로 처리

    반환값: 0 ~ 80점 사이 (태그 최대 40 + 난이도 최대 40)
    """
    tag_score = compute_tag_score(game, desired_tags)
    difficulty_score = compute_difficulty_score(game, desired_difficulty)

    return tag_score + difficulty_score
