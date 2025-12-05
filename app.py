# app.py
# 보드게임 추천기 대화형 콘솔 UI

import msvcrt  # ESC 감지용 (Windows 전용)
from boardka.loader_excel import load_games_from_excel
from boardka.recommender import recommend_games


DATA_PATH = "data/GameList.xlsx"


def ask_int(prompt: str, default: int | None = None,
            min_val: int | None = None, max_val: int | None = None) -> int | None:
    """
    - 아무것도 안 치고 엔터: default 반환
    - 잘못된 입력: 다시 입력 요청
    """
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return default
        try:
            value = int(raw)
        except ValueError:
            print("숫자를 입력해주세요.")
            continue

        if min_val is not None and value < min_val:
            print(f"{min_val} 이상의 숫자를 입력해주세요.")
            continue
        if max_val is not None and value > max_val:
            print(f"{max_val} 이하의 숫자를 입력해주세요.")
            continue
        return value


def ask_tags() -> list[str]:
    """
    태그 입력: 쉼표 또는 공백으로 구분
    예) 전략, 엔진빌딩  /  전략 엔진빌딩
    """
    raw = input("선호 태그들을 입력해주세요 (예: 전략, 엔진빌딩) [없으면 엔터]: ").strip()
    if raw == "":
        return []

    if "," in raw:
        parts = [p.strip() for p in raw.split(",")]
    else:
        parts = [p.strip() for p in raw.split()]

    return [p for p in parts if p]


def wait_for_continue_or_escape() -> bool:
    """
    ESC → 종료
    그 외 아무 키 → 계속
    """
    print("\n계속하려면 아무 키나 누르고, 종료하려면 ESC를 눌러주세요.")
    key = msvcrt.getch()
    if key == b'\x1b':  # ESC
        return False
    return True


def print_results(results: list[tuple], players: int, target_time: int | None):
    print("\n==============================")

    # 시간 입력 여부에 따라 문구 변경
    if target_time is None:
        print(f"추천 결과 (인원 {players}명)")
    else:
        print(f"추천 결과 (인원 {players}명, 목표 시간 {target_time}분)")

    print("==============================")

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


def main():
    print("=== 보드카 보드게임 추천기 ===")
    print("엑셀 데이터에서 게임 목록을 불러오는 중...")

    try:
        games = load_games_from_excel(DATA_PATH)
    except FileNotFoundError:
        print(f"데이터 파일을 찾을 수 없습니다: {DATA_PATH}")
        print("data 폴더 안에 GameList.xlsx가 있는지 확인해주세요.")
        return

    print(f"총 {len(games)}개의 게임을 불러왔습니다.\n")

    while True:
        # ESC 또는 아무 키 입력 대기
        if not wait_for_continue_or_escape():
            print("프로그램을 종료합니다.")
            break

        players = ask_int("플레이어 수를 입력해주세요 (예: 4): ", min_val=1)
        if players is None:
            print("플레이어 수는 반드시 입력해야 합니다.")
            continue

        # 시간은 optional
        target_time = ask_int(
            "목표 플레이 시간(분)을 입력해주세요 (없으면 엔터): ",
            default=None,
            min_val=1
        )

        tags = ask_tags()

        desired_difficulty = ask_int(
            "원하는 난이도(1~5, 엔터시 기본=2): ",
            default=None,
            min_val=1,
            max_val=5,
        )
        # scoring에서 None → 기본값 2

        results = recommend_games(
            games,
            players=players,
            target_time=target_time,
            desired_tags=tags,
            desired_difficulty=desired_difficulty,
            top_k=5,
        )

        print_results(results, players, target_time)


if __name__ == "__main__":
    main()

