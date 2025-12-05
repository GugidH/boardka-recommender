import pandas as pd
from .models import Game

def load_games_from_excel(path: str):
    df = pd.read_excel(path)

    games = []
    for _, row in df.iterrows():
        # tags 컬럼이 비어있을 경우
        raw_tags = str(row.get("tags", "")).strip()

        if raw_tags == "" or raw_tags.lower() == "nan":
            tags = []
        else:
            # 쉼표 분리
            tags = [t.strip() for t in raw_tags.split(",")]

        games.append(Game(
            id=str(row["이름"]),
            name_ko=str(row["이름"]),
            min_players=int(row["최소인원"]),
            max_players=int(row["최대인원"]),
            min_time=int(row["최소 플레이타임"]),
            max_time=int(row["최대 플레이타임"]),
            difficulty=int(row["난이도"]),
            tags=tags,
            rating=0.0
        ))
    return games
