# boardka/loader_excel.py

import pandas as pd
from .models import Game


def load_games_from_excel(path: str) -> list[Game]:
    df = pd.read_excel(path)

    games: list[Game] = []

    for idx, row in df.iterrows():
        # 1) 이름 없으면 스킵
        name_ko = str(row.get("이름", "")).strip()
        if not name_ko:
            continue

        # 2) 난이도 없는 게임은 아예 로딩 단계에서 제외
        raw_diff = row.get("난이도", None)
        if pd.isna(raw_diff):
            continue

        try:
            difficulty = int(raw_diff)
        except (TypeError, ValueError):
            # 이상한 값이면 그냥 버림
            continue

        # 3) 인원 정보
        raw_min_players = row.get("최소인원", 1)
        raw_max_players = row.get("최대인원", raw_min_players)

        try:
            min_players = int(raw_min_players)
        except (TypeError, ValueError):
            min_players = 1

        try:
            max_players = int(raw_max_players)
        except (TypeError, ValueError):
            max_players = min_players

        # 4) 시간 정보
        raw_min_time = row.get("최소 플레이타임", 0)
        raw_max_time = row.get("최대 플레이타임", raw_min_time)

        if pd.isna(raw_min_time):
            min_time = 0
        else:
            try:
                min_time = int(raw_min_time)
            except (TypeError, ValueError):
                min_time = 0

        if pd.isna(raw_max_time):
            max_time = min_time
        else:
            try:
                max_time = int(raw_max_time)
            except (TypeError, ValueError):
                max_time = min_time

        # 5) 태그
        raw_tags = row.get("tags", "")
        if pd.isna(raw_tags):
            tags: list[str] = []
        else:
            tags = [t.strip() for t in str(raw_tags).split(",") if t.strip()]

        # 6) id 설정
        #    - 엑셀에 'id' 컬럼이 있으면 그거 사용
        #    - 없으면 DataFrame 인덱스 기반으로 1부터 번호 매김
        raw_id = row.get("id", None)
        game_id: int
        if raw_id is None or (isinstance(raw_id, float) and pd.isna(raw_id)):
            game_id = int(idx) + 1
        else:
            try:
                game_id = int(raw_id)
            except (TypeError, ValueError):
                game_id = int(idx) + 1

        # 7) Game 인스턴스 생성
        game = Game(
            id=game_id,
            name_ko=name_ko,
            min_players=min_players,
            max_players=max_players,
            min_time=min_time,
            max_time=max_time,
            difficulty=difficulty,
            tags=tags,
        )
        games.append(game)

    return games
