#!/usr/bin/env python3
"""혼자 하기 화면 위에 '🎮 누구와 할까요?' 선택 카드를 넣는다(이미 있으면 그대로 둠 → 여러 번 돌려도 같음).
같이 하기(net-*) 게임이 있는 시작 화면 게임이 대상이에요. 카드에서 고르면 같이 하기 허브(play-together.html)가
?play=게임&bots=N 으로 열려 컴퓨터 N명과 연습을 바로 시작하거나(bots), 방(초대 QR)을 만들고 그 게임만 보여 줘요.
  종류  duo   = 2명 전용 같이 하기: [지금 화면] [각자 폰으로]
        bots  = 컴퓨터를 붙여 연습 가능한 여러 명 게임: [지금 화면] [컴퓨터 2명] [컴퓨터 3명] [각자 폰으로]
        phone = 말로 하는 게임·진행자가 필요한 게임(허브의 '컴퓨터와 연습'에서 빠진 것): [지금 화면] [각자 폰으로]
쓰는 곳: ship.py 가 새 페이지를 저장소에 넣을 때 자동 실행. 이미 있는 페이지에는 `py modesel.py` 한 번(저장소 파일을 직접 고침).
새 게임에 같이 하기 짝이 생기면 아래 CONFIG 에 한 줄 추가하세요."""
import os, re, sys
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
# 혼자 하기 파일: (같이 하기 파일, 종류, 사람 수 글자)
CONFIG = {
    "tic-tac-toe.html": ("net-tictactoe.html", "duo", "2명"), "omok.html": ("net-omok.html", "duo", "2명"), "flip-board.html": ("net-flip.html", "duo", "2명"),
    "four-in-row.html": ("net-four.html", "duo", "2명"), "checkers.html": ("net-checkers.html", "duo", "2명"), "mancala.html": ("net-mancala.html", "duo", "2명"),
    "hex-game.html": ("net-hex.html", "duo", "2명"), "dots-boxes.html": ("net-dots.html", "duo", "2명"), "ship-hunt.html": ("net-ship-hunt.html", "duo", "2명"),
    "number-baseball.html": ("net-baseball.html", "duo", "2명"), "bingo.html": ("net-bingo.html", "duo", "2명"), "high-card.html": ("net-highcard.html", "duo", "2명"),
    "memory-duel.html": ("net-memory.html", "duo", "2명"), "pig-dice.html": ("net-pig.html", "duo", "2명"), "game-31.html": ("net-31.html", "duo", "2명"),
    "rps-streak.html": ("net-rps.html", "duo", "2명"), "rps-tournament.html": ("net-rps.html", "duo", "2명"),
    "dice-combo.html": ("net-yacht.html", "bots", "2~6명"), "blackjack.html": ("net-21.html", "bots", "1~6명"), "poker-draw.html": ("net-poker.html", "bots", "2~6명"),
    "reaction-duel.html": ("net-react.html", "phone", "여러 명"), "reaction-test.html": ("net-react.html", "phone", "여러 명"), "word-trick.html": ("net-wordtrick.html", "phone", "여러 명"),
    "mafia-helper.html": ("net-mafia.html", "phone", "여러 명"), "lots.html": ("net-lots.html", "phone", "여러 명"), "bomb-pass.html": ("net-bomb.html", "phone", "여러 명"),
    "quiz-buzzer.html": ("net-buzzer.html", "phone", "여러 명"), "go-stop.html": ("net-gostop.html", "phone", "2~3명"),
}
CSS = ".modes{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0 0}.modes a,.modes span{border:1px solid var(--line);border-radius:999px;padding:8px 12px;font-size:.92rem;color:var(--fg);text-decoration:none;background:transparent}.modes span.on{background:var(--accent,var(--grass,#2f6f4f));color:var(--accent-fg,var(--grass-fg,#fff));border-color:transparent;font-weight:700}.modes small{opacity:.85;font-weight:400}.modesel{border:1px solid var(--line);border-radius:16px;padding:12px;margin:10px 0;background:var(--surface,transparent)}\n"

def card(net, kind, n):
    href = "play-together.html?play=" + net
    opts = '<span class="on">📱 지금 화면 <small>(이 폰에서)</small></span>'
    if kind == "bots":
        opts += f'<a href="{href}&amp;bots=2">🤖 컴퓨터 2명과 연습 · 3인</a><a href="{href}&amp;bots=3">🤖 컴퓨터 3명과 연습 · 4인</a>'
    opts += f'<a href="{href}">👫 가족·친구와 각자 폰으로 <small>({n})</small></a>'
    note = "각자 폰으로 할 때는 '같이 하기' 화면이 열려 QR로 폰을 연결해요." + (" 컴퓨터와 연습은 혼자서 여러 명 게임을 해 볼 수 있어요." if kind == "bots" else "")
    return f'  <div class="modesel" id="playSel" data-modesel="1"><b>🎮 누구와 할까요?</b><div class="modes">{opts}</div><p class="muted" style="margin:6px 0 0;font-size:.85rem">{note}</p></div>\n'

def apply(s, f):
    """페이지 글자 s 에 선택 카드를 넣어 돌려준다(대상이 아니거나 이미 있으면 그대로)."""
    if f not in CONFIG or 'data-modesel' in s: return s
    net, kind, n = CONFIG[f]
    i = s.find("</h1>")
    if i < 0 or "</style>" not in s: print("⚠️ 선택 카드 못 넣음(제목·스타일 없음):", f); return s
    j = s.find("\n", i); j = j + 1 if j >= 0 else i + 5   # 제목 줄 바로 다음 줄에 넣어요
    s = s[:j] + card(net, kind, n) + s[j:]
    if ".modes{" not in s: s = s.replace("</style>", CSS + "</style>", 1)
    return s

if __name__ == "__main__":
    n = 0
    for f in CONFIG:
        p = REPO + "/" + f
        if not os.path.exists(p): print("없음:", f); continue
        s = open(p, encoding="utf-8").read(); t = apply(s, f)
        if t != s: open(p, "w", encoding="utf-8", newline="").write(t); n += 1; print("넣음:", f)
    print("선택 카드를", n, "개 페이지에 넣었어요")
