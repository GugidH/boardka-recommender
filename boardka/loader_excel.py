import pandas as pd
from .models import Game

def load_games_from_excel(path: str):
    df = pd.read_excel(path)

    games = []
    for _, row in df.iterrows():
        games.append(Game(
            id=str(row["이름"]),          # id는 일단 이름 문자열
            name_ko=str(row["이름"]),
            min_players=int(row["최소인원"]),
            max_players=int(row["최대인원"]),
            min_time=int(row["최소 플레이타임"]),
            max_time=int(row["최대 플레이타임"]),
            difficulty=int(row["난이도"]),
            tags=[],                     # 나중에 엑셀에 태그 컬럼 만들면 여기서 채우기
            rating=0.0
        ))
    return games
