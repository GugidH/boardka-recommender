# boardka/scoring.py

from typing import List, Optional
from .models import Game

# 상수 정의: 태그 / 난이도 최대 점수
MAX_TAG_SCORE = 60.0
MAX_DIFF_SCORE = 40.0


def compute_tag_score(game: Game, desired_tags: List[str]) -> float:
    """
    선택 태그 점수 계산 (0 ~ 60)
    """
    if not desired_tags or not game.tags:
        return 0.0

    desired = {t.strip() for t in desired_tags if t.strip()}
    actual = {t.strip() for t in game.tags if t.strip()}

    if not desired or not actual:
        return 0.0

    overlap = len(desired & actual)
    if overlap == 0:
        return 0.0

    ratio = overlap / len(desired)
    return MAX_TAG_SCORE * ratio


def compute_preferred_score(game: Game, preferred_tags: List[str]) -> float:
    """
    선호 태그 점수 계산 (선택 태그보다 약한 0.3배)
    """
    if not preferred_tags or not game.tags:
        return 0.0

    preferred = {t.strip() for t in preferred_tags if t.strip()}
    actual = {t.strip() for t in game.tags if t.strip()}

    overlap = len(preferred & actual)
    if overlap == 0:
        return 0.0

    ratio = overlap / len(preferred)
    return (MAX_TAG_SCORE * ratio) * 0.3   # 0.3배 반영


def compute_difficulty_score(game: Game, desired_difficulty: Optional[int]) -> float:
    """
    난이도 점수 계산.
    - 난이도 입력 없는 경우 난이도 무시(0점, 패널티 없음)
    - 입력된 경우에만 0 ~ 40점 계산
    """
    if desired_difficulty is None:
        return 0.0  # 난이도 무시

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
    selected_tags: List[str],
    preferred_tags: List[str],
    desired_difficulty: Optional[int],
) -> float:
    """
    선택 태그(0~60), 선호 태그(0~18), 난이도(0~40) 합산.
    """
    tag_score = compute_tag_score(game, selected_tags)
    pref_score = compute_preferred_score(game, preferred_tags)
    diff_score = compute_difficulty_score(game, desired_difficulty)

    return tag_score + pref_score + diff_score

