import argparse
from boardka.loader_excel import load_games_from_excel
from boardka.recommender import recommend_games

def parse_args():
    parser = argparse.ArgumentParser(
        description="보드게임 추천기 (엑셀 기반)"
    )
    parser.add_argument(
        "--data",
        default="data/GameList.xlsx",
        help="보드게임 엑셀 파일 경로",
    )
    parser.add_argument(
        "--players",
        type=int,
        required=True,
        help="플레이어 수",
    )
    parser.add_argument(
        "--time",
        type=int,
        required=True,
        help="목표 플레이 시간(분 단위)",
    )
    parser.add_argument(
        "--difficulty",
        type=int,
        default=None,
        help="원하는 난이도(1~5). 입력하지 않으면 기본값 2로 설정됨."
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        default=[],
        help="선호 태그들",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="추천 게임 개수",
    )
    return parser.parse_args()

def main():
    args = parse_args()
    games = load_games_from_excel(args.data)

    results = recommend_games(
        games,
        players=args.players,
        target_time=args.time,
        desired_tags=args.tags,
        desired_difficulty=args.difficulty,  
        top_k=5,
    )


    print("\n=== 추천 결과 ===")
    if not results:
        print("조건에 맞는 게임이 없습니다.")
        return

    for rank, (game, score) in enumerate(results, start=1):
        tags_str = ", ".join(game.tags) if game.tags else "(태그 없음)"
        print(f"[{rank}] {game.name_ko}")
        print(
            f"    인원: {game.min_players}~{game.max_players}명, "
            f"시간: {game.min_time}~{game.max_time}분, "
            f"난이도: {game.difficulty}/5"
        )
        print(f"    태그: {tags_str}")
        print(f"    점수: {score:.3f}")
        print()


if __name__ == "__main__":
    main()
