# gui.py
# 보드게임 추천기 GUI 버전 (tkinter, 태그 체크박스)

import tkinter as tk
from tkinter import ttk, messagebox

from boardka.loader_excel import load_games_from_excel
from boardka.recommender import recommend_games

DATA_PATH = "data/GameList.xlsx"


class BoardGameRecommenderGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("보드카 보드게임 추천기 (GUI)")

        # 게임 데이터 로드
        try:
            self.games = load_games_from_excel(DATA_PATH)
        except FileNotFoundError:
            messagebox.showerror(
                "오류",
                f"데이터 파일을 찾을 수 없습니다:\n{DATA_PATH}\n"
                "data 폴더 안에 GameList.xlsx가 있는지 확인해주세요.",
            )
            self.root.destroy()
            return

        # 태그별 게임 개수 계산
        self.tag_counts = self._build_tag_counts(self.games)
        self.tag_vars: dict[str, tk.BooleanVar] = {}

        # --- 메인 프레임 설정 ---
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 플레이어 수
        ttk.Label(main_frame, text="플레이어 수").grid(row=0, column=0, sticky="w", pady=2)
        self.players_var = tk.StringVar()
        self.players_entry = ttk.Entry(main_frame, textvariable=self.players_var, width=10)
        self.players_entry.grid(row=0, column=1, sticky="w", pady=2)

        # 목표 시간
        ttk.Label(main_frame, text="목표 시간(분)").grid(row=1, column=0, sticky="w", pady=2)
        self.time_var = tk.StringVar()
        self.time_entry = ttk.Entry(main_frame, textvariable=self.time_var, width=10)
        self.time_entry.grid(row=1, column=1, sticky="w", pady=2)
        ttk.Label(main_frame, text="(입력 안 하면 시간은 무시됩니다)").grid(
            row=1, column=2, sticky="w", pady=2
        )

        # 태그 선택 영역 (체크박스)
        tags_frame = ttk.LabelFrame(main_frame, text="선호 태그 선택", padding=8)
        tags_frame.grid(row=2, column=0, columnspan=3, sticky="we", pady=(8, 4))
        tags_frame.columnconfigure(0, weight=1)
        tags_frame.columnconfigure(1, weight=1)
        tags_frame.columnconfigure(2, weight=1)

        # 태그 체크박스 생성 (게임 개수 포함)
        # 정렬: 게임 개수 많은 순 → 이름순
        sorted_tags = sorted(
            self.tag_counts.items(),
            key=lambda item: (-item[1], item[0])
        )

        for idx, (tag, count) in enumerate(sorted_tags):
            var = tk.BooleanVar(value=False)
            self.tag_vars[tag] = var
            text = f"{tag} ({count})"
            cb = ttk.Checkbutton(tags_frame, text=text, variable=var)
            # 3열 그리드 배치
            row = idx // 3
            col = idx % 3
            cb.grid(row=row, column=col, sticky="w", padx=2, pady=2)

        if not sorted_tags:
            ttk.Label(tags_frame, text="등록된 태그가 없습니다.").grid(
                row=0, column=0, sticky="w"
            )

        # 난이도
        ttk.Label(main_frame, text="원하는 난이도").grid(row=3, column=0, sticky="w", pady=2)
        self.difficulty_var = tk.StringVar()
        self.difficulty_combo = ttk.Combobox(
            main_frame,
            textvariable=self.difficulty_var,
            values=["1", "2", "3", "4", "5"],
            width=5,
            state="readonly",
        )
        self.difficulty_combo.grid(row=3, column=1, sticky="w", pady=2)
        self.difficulty_combo.set("")  # 기본: 선택 안 함
        ttk.Label(
            main_frame,
            text="(선택 안 하면 기본값 2로 처리됩니다)",
            foreground="#666666",
        ).grid(row=3, column=2, sticky="w", pady=2)

        # 추천 버튼
        self.recommend_button = ttk.Button(
            main_frame, text="추천 받기", command=self.on_recommend
        )
        self.recommend_button.grid(row=4, column=0, columnspan=3, sticky="we", pady=10)

        # 결과 영역
        result_frame = ttk.LabelFrame(main_frame, text="추천 결과", padding=8)
        result_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(5, 0))
        main_frame.rowconfigure(5, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        self.result_text = tk.Text(result_frame, height=15, wrap="word")
        self.result_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            result_frame, orient="vertical", command=self.result_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=scrollbar.set)

        # 초기 안내 메시지
        self.result_text.insert(
            "1.0",
            f"총 {len(self.games)}개의 게임을 불러왔습니다.\n"
            "플레이어 수, (선택사항) 시간/태그/난이도를 입력한 뒤 [추천 받기] 버튼을 눌러주세요.",
        )
        self.result_text.configure(state="disabled")

    def _build_tag_counts(self, games) -> dict[str, int]:
        """
        게임 목록에서 태그별로 몇 개의 게임이 있는지 세어 반환.
        """
        counts: dict[str, int] = {}
        for g in games:
            if not getattr(g, "tags", None):
                continue
            for t in g.tags:
                tag = t.strip()
                if not tag:
                    continue
                counts[tag] = counts.get(tag, 0) + 1
        return counts

    def _get_selected_tags(self) -> list[str]:
        """
        체크된 태그들만 리스트로 반환.
        """
        selected: list[str] = []
        for tag, var in self.tag_vars.items():
            if var.get():
                selected.append(tag)
        return selected

    def on_recommend(self):
        # 플레이어 수
        players_str = self.players_var.get().strip()
        if not players_str:
            messagebox.showwarning("입력 오류", "플레이어 수를 입력해주세요.")
            return
        try:
            players = int(players_str)
            if players <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("입력 오류", "플레이어 수는 1 이상의 정수여야 합니다.")
            return

        # 시간 (선택사항)
        time_str = self.time_var.get().strip()
        if time_str == "":
            target_time = None
        else:
            try:
                target_time = int(time_str)
                if target_time <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(
                    "입력 오류", "목표 시간은 1 이상의 정수이거나, 아예 비워 두어야 합니다."
                )
                return

        # 체크된 태그들
        tags = self._get_selected_tags()

        # 난이도 (선택사항)
        diff_str = self.difficulty_var.get().strip()
        if diff_str == "":
            desired_difficulty = None
        else:
            try:
                desired_difficulty = int(diff_str)
            except ValueError:
                messagebox.showwarning("입력 오류", "난이도는 1~5 중 하나여야 합니다.")
                return

        # 추천 개수는 5개 고정
        results = recommend_games(
            self.games,
            players=players,
            target_time=target_time,
            desired_tags=tags,
            desired_difficulty=desired_difficulty,
            top_k=5,
        )

        # 결과 출력
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")

        if target_time is None:
            header = f"인원 {players}명 기준 추천 결과 (최대 5개)\n\n"
        else:
            header = f"인원 {players}명, 목표 시간 {target_time}분 기준 추천 결과 (최대 5개)\n\n"

        if tags:
            header += "선택한 태그: " + ", ".join(tags) + "\n\n"

        self.result_text.insert("1.0", header)

        if not results:
            self.result_text.insert("end", "조건에 맞는 게임이 없습니다.\n")
            self.result_text.configure(state="disabled")
            return

        for rank, (game, score) in enumerate(results, start=1):
            tags_str = ", ".join(game.tags) if game.tags else "(태그 없음)"
            self.result_text.insert(
                "end",
                f"[{rank}] {game.name_ko}\n"
                f"    인원: {game.min_players}~{game.max_players}명\n"
                f"    시간: {game.min_time}~{game.max_time}분\n"
                f"    난이도: {game.difficulty}/5\n"
                f"    태그: {tags_str}\n"
                f"    점수: {score:.3f}\n\n",
            )

        self.result_text.configure(state="disabled")


def main():
    root = tk.Tk()
    app = BoardGameRecommenderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
