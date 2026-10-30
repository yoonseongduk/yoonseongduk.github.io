#!/usr/bin/env python3
"""일반 페이지 생성기: 공통 스타일과 도구 함수에 게임별 화면(HTML)과 규칙(JS)을 끼워 넣는다."""
TPL = r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>@@TITLE@@</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Do+Hyeon&family=Noto+Sans+KR:wght@400;500;700&display=swap">
<style>
/* 레이아웃: 제목 아래에 설정과 결과 카드를 위에서 아래로 쌓는다. 버튼은 크게, 결과는 눈에 띄게 */
:root{--bg:hsl(@@H@@ 30% 95%);--surface:#fff;--fg:#1c2233;--muted:#626b82;--line:hsl(@@H@@ 22% 86%);--accent:hsl(@@H@@ 65% 46%);--accent-fg:#fff;--soft:hsl(@@H@@ 45% 92%);--ok:#1f9d62;--bad:#d6453a;--font-display:"Do Hyeon","Noto Sans KR",sans-serif;--font-body:"Noto Sans KR",system-ui,sans-serif;color-scheme:light}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:hsl(@@H@@ 22% 10%);--surface:hsl(@@H@@ 18% 15%);--fg:#e9edf7;--muted:#97a1b9;--line:hsl(@@H@@ 16% 25%);--accent:hsl(@@H@@ 75% 68%);--accent-fg:#10131c;--soft:hsl(@@H@@ 20% 20%);--ok:#4cc98a;--bad:#ff7b68;color-scheme:dark}}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}[hidden]{display:none!important}html,body{margin:0}
body{background:var(--bg);color:var(--fg);font-family:var(--font-body);line-height:1.5;padding-block:24px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));user-select:none;-webkit-user-select:none}
main{max-width:440px;margin:0 auto;display:flex;flex-direction:column;gap:14px}
h1{font-family:var(--font-display);font-weight:400;font-size:2rem;margin:0}h2{font-family:var(--font-display);font-weight:400;font-size:1.25rem;margin:0}p{margin:0}.muted{color:var(--muted);font-size:.9rem}.center{text-align:center}
button{font:inherit;cursor:pointer;color:inherit}button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:14px;display:flex;flex-direction:column;gap:10px}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.stat{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:6px 12px;min-width:0}.stat small{display:block;color:var(--muted);font-size:.72rem}.stat b{font-family:var(--font-display);font-weight:400;font-size:1.4rem;font-variant-numeric:tabular-nums}
.seg{display:grid;gap:8px;grid-template-columns:repeat(var(--n,3),1fr)}.seg button{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:8px 4px;font-weight:700;line-height:1.3}.seg button small{display:block;font-weight:400;color:var(--muted);font-size:.72rem}.seg button.on{background:var(--fg);border-color:var(--fg);color:var(--bg)}.seg button.on small{color:var(--bg);opacity:.8}
.btn{background:var(--accent);color:var(--accent-fg);border:0;border-radius:14px;padding:13px;font-family:var(--font-display);font-size:1.3rem}.btn.ghost{background:transparent;color:var(--fg);border:1px solid var(--line);font-family:var(--font-body);font-size:1rem;font-weight:700}.btn:disabled{opacity:.45;cursor:default}
.row{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.step{display:flex;align-items:center;justify-content:space-between;gap:10px}.step div{display:flex;align-items:center;gap:10px}.step button{width:42px;height:42px;border-radius:50%;border:1px solid var(--line);background:var(--soft);font-size:1.4rem;line-height:1}.step b{font-family:var(--font-display);font-weight:400;font-size:1.6rem;min-width:2ch;text-align:center}
input[type=text],input[type=number],textarea{width:100%;background:var(--soft);color:var(--fg);border:1px solid var(--line);border-radius:12px;padding:11px 12px;font:inherit;user-select:text;-webkit-user-select:text}textarea{resize:vertical;min-height:96px}
.res{text-align:center;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:14px}.res b{font-family:var(--font-display);font-weight:400;font-size:1.6rem}
.big{font-family:var(--font-display);font-size:clamp(1.8rem,9vw,2.6rem);line-height:1.3;overflow-wrap:anywhere}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@@CSS@@
</style>
</head>
<body>
<main>
  <h1>@@TITLE@@ @@EMOJI@@</h1>
@@BODY@@
  <p class="muted">@@HELP@@</p>
</main>
<script>
const $ = id => document.getElementById(id);
const ld = k => { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } };
const sv = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const shuf = a => { a = [...a]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const rand = (a, b) => a + Math.random() * (b - a), ri = (a, b) => Math.floor(rand(a, b + 1)), clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const KEY = "@@KEY@@";
@@JS@@
</script>
</body>
</html>
'''


def make(path, title, emoji, hue, key, help_, body, js, css=""):
    s = (TPL.replace("@@CSS@@", css).replace("@@BODY@@", body).replace("@@JS@@", js).replace("@@TITLE@@", title)
         .replace("@@EMOJI@@", emoji).replace("@@H@@", str(hue)).replace("@@KEY@@", key).replace("@@HELP@@", help_))
    open(path, "w", encoding="utf-8").write(s)
    print("만듦:", path)
