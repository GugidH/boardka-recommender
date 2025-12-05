# gui.py
# 보드게임 추천기 GUI 버전 (tkinter, 태그 체크박스 + 선호 태그 반영)

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

from boardka.loader_excel import load_games_from_excel
from boardka.recommender import recommend_games

DATA_PATH = "data/GameList.xlsx"
PREF_PATH = "data/user_prefs.json"  # 선호 태그 저장용


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

        # 유저 선호 태그 로드
        self.user_prefs: dict[str, int] = self._load_user_prefs()

        # 태그별 게임 개수 계산
        self.tag_counts = self._build_tag_counts(self.games)
        self.tag_vars: dict[str, tk.BooleanVar] = {}
        self.last_results: list[tuple] = []  # (game, score) 목록

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
        # 1) 태그 빈도 필터링: 게임이 3개 이하인 태그는 숨김
        filtered_tags = {tag: count for tag, count in self.tag_counts.items() if count > 3}

        # 2) 정렬: 게임 개수 많은 순 → 이름순
        sorted_tags = sorted(
            filtered_tags.items(),
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
            text="(선택 안 하면 난이도는 완전히 무시됩니다)",
            foreground="#666666",
        ).grid(row=3, column=2, sticky="w", pady=2)

        # 선호태그 반영 여부 체크박스
        self.use_pref_var = tk.BooleanVar(value=True)  # 기본값: 선호태그 사용
        self.pref_checkbox = ttk.Checkbutton(
            main_frame,
            text="선호태그 반영 안 함",
            variable=self.use_pref_var,
            onvalue=False,   # 체크되면 False = 사용 안 함
            offvalue=True    # 체크 해제 = True = 사용함
        )
        # 난이도 오른쪽에 배치
        self.pref_checkbox.grid(row=3, column=3, sticky="w", padx=10)

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

        # "마음에 든 게임" 리스트 (더블클릭하면 선호 태그로 반영)
        like_frame = ttk.LabelFrame(main_frame, text="마음에 든 게임 (더블클릭해서 선호 반영)", padding=8)
        like_frame.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=(5, 0))
        like_frame.columnconfigure(0, weight=1)
        like_frame.columnconfigure(1, weight=0)

        self.like_listbox = tk.Listbox(like_frame, height=5)
        self.like_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.like_listbox.bind("<Double-Button-1>", self.on_like)

        # 선호 태그 Top5 표시 라벨
        self.pref_info_label = ttk.Label(like_frame, text="선호 태그 상위 5개: (없음)")
        self.pref_info_label.grid(row=1, column=0, sticky="w", pady=(5, 0))

        # 선호태그 초기화 버튼
        self.reset_pref_button = ttk.Button(
            like_frame,
            text="선호태그 초기화",
            command=self.on_reset_prefs,
        )
        self.reset_pref_button.grid(row=1, column=1, sticky="e", padx=5, pady=(5, 0))

        # 초기 안내 메시지
        self.result_text.insert(
            "1.0",
            f"총 {len(self.games)}개의 게임을 불러왔습니다.\n"
            "플레이어 수, (선택사항) 시간/태그/난이도를 입력한 뒤 [추천 받기] 버튼을 눌러주세요.\n"
            "마음에 드는 추천 결과는 아래 리스트에서 더블클릭하면\n"
            "그 게임의 태그가 나의 선호 태그로 조금씩 반영됩니다.",
        )
        self.result_text.configure(state="disabled")

        # 선호 태그 Top5 표시 갱신
        self._update_pref_summary()

    # ----------------- 내부 헬퍼 메서드들 -----------------

    def _load_user_prefs(self) -> dict[str, int]:
        """
        이전에 클릭해서 쌓아둔 선호 태그 정보를 JSON에서 읽어온다.
        없으면 빈 dict 반환.
        """
        if not os.path.exists(PREF_PATH):
            return {}
        try:
            with open(PREF_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 값이 숫자가 아닐 수 있으니 안전하게 정수로 캐스팅
            prefs: dict[str, int] = {}
            for k, v in data.items():
                try:
                    prefs[str(k)] = int(v)
                except (TypeError, ValueError):
                    continue
            return prefs
        except Exception:
            # 망가진 파일이면 그냥 무시하고 새로 시작
            return {}

    def _save_user_prefs(self) -> None:
        """
        현재까지 쌓인 선호 태그 정보를 JSON 파일로 저장.
        """
        os.makedirs(os.path.dirname(PREF_PATH), exist_ok=True)
        with open(PREF_PATH, "w", encoding="utf-8") as f:
            json.dump(self.user_prefs, f, ensure_ascii=False, indent=2)

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

    def _update_pref_summary(self) -> None:
        """
        선호 태그 상위 5개를 라벨에 표시.
        """
        if not self.user_prefs:
            text = "선호 태그 상위 5개: (없음)"
        else:
            pref_sorted = sorted(self.user_prefs.items(), key=lambda x: -x[1])
            top5 = [t for t, _ in pref_sorted[:5]]
            text = "선호 태그 상위 5개: " + ", ".join(top5)
        self.pref_info_label.config(text=text)

    # ----------------- 이벤트 핸들러 -----------------

    def on_like(self, event=None):
        """
        아래 리스트박스에서 게임을 더블클릭하면,
        그 게임에 달려 있는 태그들의 선호도를 +1씩 올린다.
        """
        if not self.last_results:
            return

        selection = self.like_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        if idx >= len(self.last_results):
            return

        game, score = self.last_results[idx]

        if not getattr(game, "tags", None):
            messagebox.showinfo("선호 반영", f"'{game.name_ko}'에는 태그가 없어 저장할 정보가 없습니다.")
            return

        for tag in game.tags:
            self.user_prefs[tag] = self.user_prefs.get(tag, 0) + 1

        self._save_user_prefs()
        self._update_pref_summary()

        messagebox.showinfo(
            "선호 반영",
            f"'{game.name_ko}'의 태그가 선호 태그로 조금 더 반영되었습니다.\n"
            f"(현재 선호 태그 예: {', '.join(list(self.user_prefs.keys())[:5])})"
        )

    def on_reset_prefs(self):
        """
        선호 태그 전체 초기화.
        """
        if not self.user_prefs:
            messagebox.showinfo("초기화", "현재 저장된 선호 태그가 없습니다.")
            return

        ans = messagebox.askyesno(
            "선호태그 초기화",
            "정말로 모든 선호 태그를 초기화할까요?\n(되돌릴 수 없습니다)"
        )
        if not ans:
            return

        self.user_prefs.clear()
        self._save_user_prefs()
        self._update_pref_summary()
        messagebox.showinfo("초기화 완료", "선호 태그가 모두 초기화되었습니다.")

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

        # 선택 태그
        selected_tags = self._get_selected_tags()

        # 선호 태그 상위 5개 계산
        pref_sorted = sorted(self.user_prefs.items(), key=lambda x: -x[1])
        preferred_tags = [t for t, _ in pref_sorted[:5]]

        # 선호태그 반영 안 함 체크 시 preferred 제거
        if self.use_pref_var.get() is False:
            preferred_tags = []

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

        # 추천 호출 (5개 고정)
        results = recommend_games(
            self.games,
            players=players,
            target_time=target_time,
            desired_tags=selected_tags,       # 선택 태그
            preferred_tags=preferred_tags,    # 선호 태그
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

        if selected_tags:
            header += "선택 태그: " + ", ".join(selected_tags) + "\n"
        if preferred_tags:
            header += "선호 태그: " + ", ".join(preferred_tags) + "\n"
        elif self.user_prefs and self.use_pref_var.get() is False:
            header += "선호 태그: 반영 안 함\n"

        header += "\n"
        self.result_text.insert("1.0", header)

        if not results:
            self.result_text.insert("end", "조건에 맞는 게임이 없습니다.\n")
            self.result_text.configure(state="disabled")
            # 추천 결과가 없으면 리스트박스도 비움
            self.like_listbox.delete(0, "end")
            self.last_results = []
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

        # 리스트박스에 추천 결과 제목만 따로 보여주기 (클릭용)
        self.last_results = results
        self.like_listbox.delete(0, "end")
        for game, score in results:
            self.like_listbox.insert("end", game.name_ko)


def main():
    root = tk.Tk()
    app = BoardGameRecommenderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
