#!/usr/bin/env python3
"""person.js 의 /*GAMES*/ 줄을 시작 화면(index.html) 게임 목록에서 다시 만든다.
포인트를 주는 게임 = 분류가 brain·quiz·react·board·arcade·together 인 것 중 도구성 페이지를 뺀 것.
사용: py person_gen.py   (ship.py 가 자동으로 부른다)"""
import os, re, json
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")) + os.sep
NOT_GAME = {"link-test.html", "play-together.html", "team-split.html", "order-picker.html", "lots.html", "decision-roulette.html", "dice-roller.html", "coin-flip.html", "mafia-helper.html", "scoreboard.html"}
HARD = ["sudoku.html", "mini-sudoku.html", "nonogram.html", "n-queens.html", "knights-tour.html", "magic-square.html", "hanoi.html", "water-sort.html", "mine-puzzle.html", "block-stack.html", "hanja-write.html", "peg-solitaire.html", "checkers.html", "go-stop.html"]
t = open(R + "index.html", encoding="utf-8").read()
g = re.findall(r'\["([^"]+\.html)", "[^"]*", "[^"]*", "[^"]*", "(\w+)"\]', t)
files = sorted({f for f, k in g if k in ("brain", "quiz", "react", "board", "arcade", "together") and f not in NOT_GAME})
hard = [f for f in HARD if f in files]
line = "/*GAMES*/ var GAMES = " + json.dumps({f: 1 for f in files}, ensure_ascii=False, separators=(",", ":")) + "; var HARD = " + json.dumps({f: 1 for f in hard}, ensure_ascii=False, separators=(",", ":")) + "; /*/GAMES*/"
p = R + "person.js"; s = open(p, encoding="utf-8").read()
s2 = re.sub(r"/\*GAMES\*/.*?/\*/GAMES\*/", lambda m: line, s, count=1, flags=re.S)
open(p, "w", encoding="utf-8", newline="").write(s2)
print("person.js 게임 목록:", len(files), "개 (어려운 게임", len(hard), "개)")
