# 클래식 음질 분석 결과를 앱에 반영하는 한 번에 실행 도구(tools\음질분석.bat 이 불러요)
# 순서: set44.py(곡 목록 다시 만들기) → ship.py(클래식 두 화면 등록) → 릴리스 노트 → sw.js → 기능 색인 점검
import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PY = sys.executable
def run(args, cwd):
    print(">", " ".join(args[1:]) if args[0] == PY else " ".join(args), flush=True)
    r = subprocess.run(args, cwd=cwd)
    if r.returncode: print("오류가 났어요:", " ".join(args)); sys.exit(1)
PAGES = [["classic-quiz.html", "🎼", "클래식 작곡가 퀴즈", "클래식 작곡가·곡·시대를 맞혀요. 작곡가별 모음도 있어요.", "quiz", "culture"],
         ["classic-gallery.html", "🎻", "클래식 작곡가별 모음", "클래식 작곡가와 대표곡을 시대별로 익혀요. 검색도 돼요.", "life", "culture"]]
run([PY, "set44.py"], HERE)
run([PY, "ship.py", json.dumps(PAGES, ensure_ascii=False)], HERE)
n = len(json.load(open(os.path.join(HERE, "music_pick.json"), encoding="utf-8")))
run([PY, os.path.join("tools", "release.py"), "클래식 음질 분석 반영(PC)", f"음질 분석을 거친 녹음으로 곡 목록을 바꿨어요(소리가 나오는 곡 {n}곡)"], ROOT)
run([PY, os.path.join("tools", "make-sw.py")], ROOT)
run([PY, os.path.join("tools", "dev", "featcheck.py")], ROOT)
print(f"\n반영 끝: 소리가 나오는 곡 {n}곡")
