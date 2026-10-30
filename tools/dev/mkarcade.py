#!/usr/bin/env python3
"""아케이드 게임 생성기: 공통 틀(반복 갱신, 점수, 최고 기록, 일시정지, 입력)에 게임별 규칙을 끼워 넣는다."""
TPL = r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>@@TITLE@@</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Do+Hyeon&family=Noto+Sans+KR:wght@400;500;700&display=swap">
<style>
/* 레이아웃: 점수·최고·상태 줄, 가운데 게임 판(캔버스, 손가락으로 조작), 아래 설명. 시작과 끝은 판 위의 안내 화면에서 */
:root{--bg:hsl(@@H@@ 30% 94%);--surface:#fff;--fg:#1b2133;--muted:#5f6881;--line:hsl(@@H@@ 22% 84%);--field:hsl(@@H@@ 40% 16%);--accent:hsl(@@H@@ 75% 50%);--accent-fg:#fff;--ok:#2fb36a;--bad:#e8453c;--font-display:"Do Hyeon","Noto Sans KR",sans-serif;--font-body:"Noto Sans KR",system-ui,sans-serif;color-scheme:light}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:hsl(@@H@@ 25% 9%);--surface:hsl(@@H@@ 20% 15%);--fg:#e8ecf8;--muted:#95a0c0;--line:hsl(@@H@@ 20% 24%);--field:hsl(@@H@@ 40% 7%);--accent:hsl(@@H@@ 85% 66%);--accent-fg:#10131c;--ok:#4cd486;--bad:#ff6b5e;color-scheme:dark}}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}[hidden]{display:none!important}html,body{margin:0}
body{background:var(--bg);color:var(--fg);font-family:var(--font-body);line-height:1.5;padding-block:20px 40px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));user-select:none;-webkit-user-select:none}
main{max-width:440px;margin:0 auto;display:flex;flex-direction:column;gap:12px}
h1{font-family:var(--font-display);font-weight:400;font-size:2rem;margin:0}p{margin:0}.muted{color:var(--muted);font-size:.88rem}
button{font:inherit;cursor:pointer;color:inherit}button:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.stat{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:4px 12px;min-width:0}.stat small{display:block;color:var(--muted);font-size:.72rem}.stat b{font-family:var(--font-display);font-weight:400;font-size:1.35rem;font-variant-numeric:tabular-nums;white-space:nowrap}
.wrap{position:relative;border-radius:14px;overflow:hidden;border:2px solid var(--line);background:var(--field);touch-action:none;aspect-ratio:@@W@@/@@HEIGHT@@}
canvas{width:100%;height:100%;display:block}
.ov{position:absolute;inset:0;background:rgba(5,8,20,.58);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;text-align:center;padding:16px}
.ov b{font-family:var(--font-display);font-weight:400;font-size:1.9rem;line-height:1.2}.ov p{color:#e4e8f6}
.btn{background:var(--accent);color:var(--accent-fg);border:0;border-radius:12px;padding:10px 24px;font-family:var(--font-display);font-size:1.3rem}
</style>
</head>
<body>
<main>
  <h1>@@TITLE@@ @@EMOJI@@</h1>
  <div class="stats"><div class="stat"><small>점수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div><div class="stat"><small>@@INFO@@</small><b id="info">-</b></div></div>
  <div class="wrap" id="wrap"><canvas id="cv" aria-label="@@TITLE@@ 게임 판"></canvas><div class="ov" id="ov"></div></div>
  <p class="muted">@@HELP@@ (일시정지: 창을 벗어나면 자동, 컴퓨터는 P 키)</p>
</main>
<script>
const W = @@W@@, H = @@HEIGHT@@, KEY = "@@KEY@@";
const $ = id => document.getElementById(id);
const ld = k => { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } };
const sv = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
const clamp = (v, a, b) => Math.max(a, Math.min(b, v)), rand = (a, b) => a + Math.random() * (b - a), ri = (a, b) => Math.floor(rand(a, b + 1));
const cv = $("cv"), ctx = cv.getContext("2d");
let score = 0, best = ld(KEY) || 0, state = "ready", info = "", newBest = false, last = 0, keys = { l: 0, r: 0, u: 0, d: 0 }, C = {};
function readColors() { const css = getComputedStyle(document.documentElement); for (const k of ["fg", "surface", "line", "muted", "accent", "ok", "bad", "field"]) C[k] = css.getPropertyValue("--" + k).trim(); }
function setScore(n) { score = n; $("score").textContent = score; }
function addScore(n) { setScore(score + n); }
function setInfo(s) { info = s; $("info").textContent = s; }
function end() { if (state !== "play") return; state = "over"; if (score > best) { best = score; sv(KEY, best); newBest = true; } ui(); }
function start() { if (state === "ready" || state === "over") { setScore(0); newBest = false; reset(); } state = "play"; last = performance.now(); ui(); }
function pause() { if (state === "play") { state = "paused"; ui(); } }
function ui() {
  $("best").textContent = best; $("score").textContent = score; $("info").textContent = info; const ov = $("ov"); ov.hidden = state === "play";
  ov.innerHTML = state === "ready" ? `<b>@@TITLE@@</b><p>@@GOAL@@</p><button class="btn" data-a="go" type="button">시작</button>`
    : state === "paused" ? `<b>일시정지</b><button class="btn" data-a="go" type="button">계속하기</button>`
    : `<b>게임 오버</b><p>${score}점${newBest ? "<br>🏆 최고 기록!" : ""}</p><button class="btn" data-a="go" type="button">다시 하기</button>`;
}
function frame(t) {
  const dt = Math.min(.033, (t - last) / 1000 || 0); last = t; if (state === "play") update(dt);
  const w = cv.clientWidth, dpr = window.devicePixelRatio || 1; if (w) { const pw = Math.round(w * dpr); if (cv.width !== pw) { cv.width = pw; cv.height = Math.round(pw * H / W); } ctx.setTransform(cv.width / W, 0, 0, cv.width / W, 0, 0); ctx.clearRect(0, 0, W, H); draw(ctx); }
  requestAnimationFrame(frame);
}
const pos = e => { const r = cv.getBoundingClientRect(); return [(e.clientX - r.left) / r.width * W, (e.clientY - r.top) / r.height * H]; };
$("wrap").addEventListener("pointerdown", e => { if (e.target.closest("[data-a]")) return; if (state === "play") { e.preventDefault(); pointer("down", ...pos(e)); } });
$("wrap").addEventListener("pointermove", e => { if (state === "play") pointer("move", ...pos(e)); });
["pointerup", "pointercancel", "pointerleave"].forEach(ev => $("wrap").addEventListener(ev, e => { if (state === "play") pointer("up", ...pos(e)); }));
$("ov").addEventListener("click", e => { if (e.target.closest("[data-a=go]")) start(); });
document.addEventListener("keydown", e => {
  const m = { ArrowLeft: "l", ArrowRight: "r", ArrowUp: "u", ArrowDown: "d", a: "l", d: "r", w: "u", s: "d" }[e.key];
  if (m) { keys[m] = 1; e.preventDefault(); if (state === "play" && typeof key === "function") key("down", m); }
  else if (e.key === " ") { e.preventDefault(); if (state === "ready" || state === "over" || state === "paused") start(); else if (typeof key === "function") key("down", "space"); }
  else if (e.key === "p" || e.key === "P") { state === "play" ? pause() : state === "paused" && start(); }
});
document.addEventListener("keyup", e => { const m = { ArrowLeft: "l", ArrowRight: "r", ArrowUp: "u", ArrowDown: "d", a: "l", d: "r", w: "u", s: "d" }[e.key]; if (m) keys[m] = 0; });
document.addEventListener("visibilitychange", () => { if (document.hidden) pause(); });
readColors(); matchMedia("(prefers-color-scheme: dark)").addEventListener("change", readColors);
@@GAME@@
reset(); ui(); requestAnimationFrame(frame);
</script>
</body>
</html>
'''


def make(path, title, emoji, hue, key, w, h, info_label, goal, help_, game):
    s = (TPL.replace("@@HEIGHT@@", str(h)).replace("@@TITLE@@", title).replace("@@EMOJI@@", emoji).replace("@@H@@", str(hue))
         .replace("@@KEY@@", key).replace("@@W@@", str(w)).replace("@@INFO@@", info_label).replace("@@GOAL@@", goal)
         .replace("@@HELP@@", help_).replace("@@GAME@@", game.strip()))
    open(path, "w", encoding="utf-8").write(s)
    print("만듦:", path)
