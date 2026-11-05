#!/usr/bin/env python3
"""새 게임을 사이트 폴더로 옮기고(앱 설치용 머리말/글꼴 연결 포함) 시작 화면에 등록한 뒤 sw.js를 갱신한다.
사용: ship.py '<JSON: [[파일,아이콘,제목,설명,분류],...]>'"""
import os
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import sys, json, re, shutil, subprocess
R = REPO + "/"
HEAD = '<link rel="manifest" href="manifest.webmanifest">\n<meta name="theme-color" content="#c4552b">\n<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-title" content="가족 게임">\n<link rel="apple-touch-icon" href="apple-touch-icon.png">\n<link rel="icon" type="image/png" href="favicon-48.png">\n'
REG = '<script>if ("serviceWorker" in navigator) addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));</script>\n'
games = json.loads(sys.argv[1])
for f, *_ in games:
    s = open("out/" + f, encoding="utf-8").read()
    s = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]*">', '<link rel="stylesheet" href="fonts/fonts.css">', s)
    if 'rel="manifest"' not in s:
        s = s.replace('<link rel="stylesheet" href="fonts/fonts.css">', '<link rel="stylesheet" href="fonts/fonts.css">\n' + HEAD, 1)
    if 'register("sw.js")' not in s:
        s = s.replace("</body>", REG + "</body>", 1)
    if ("class=\"opt\"" in s or "WrongNotes" in s) and "wrong-hook.js" not in s: s = s.replace("</body>", '<script src="wrong-hook.js"></script>\n</body>', 1)
    if "FAMILY." in s and "family.js" not in s and "<script>\nconst $ = id" in s: s = s.replace("<script>\nconst $ = id", '<script src="family.js"></script>\n<script>\nconst $ = id', 1)
    # net-* 는 같이 하기 화면 안에서 열려서, 약 알림이 두 번 뜨지 않게 넣지 않아요
    if "med-notify.js" not in s and not f.endswith("med-check.html") and not f.startswith("net-"): s = s.replace("</body>", '<script src="med-notify.js" defer></script>\n</body>', 1)
    assert "googleapis" not in s and 'rel="manifest"' in s and 'register("sw.js")' in s, f
    open(R + f, "w", encoding="utf-8").write(s)
subprocess.run([sys.executable, "addgames.py", json.dumps([g for g in games if g[4] != "-"], ensure_ascii=False)], check=True)  # 분류 "-"는 시작 화면에 등록하지 않음(같이 하기 안에서만 여는 게임 등)
subprocess.run([sys.executable, "gamenum.py"], check=True)  # 새 게임에 고유번호 붙이기(시작 화면 검색용)
subprocess.run([sys.executable, R + "tools/make-sw.py"], check=True)
