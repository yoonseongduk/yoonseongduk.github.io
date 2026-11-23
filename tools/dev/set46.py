# 그림·음원 저장 현황 화면(offline-media.html) 생성기. 온라인으로 받아 쓰는 세 게임(명화·클래식·오케스트라)의 '전체 수 / 이 폰에 저장된 수 / 저장 용량'을 한곳에서 보여 주고 지울 수 있게 해요.
#   실행: py set46.py → py ship.py '[["offline-media.html","📊","그림·음원 저장 현황","…","life","home"]]'
#   전체 수는 각 모드 파일(art-mode.js·orch-mode.js·classic-mode.js)의 자료에서 읽어요. 저장된 수·용량은 폰 안(localStorage·Cache)에서 읽어요.
import re, json, sys
sys.path.insert(0, ".")
from mkpage import make
def data_of(path):
    line = [l for l in open(path, encoding="utf-8").read().split("\n") if l.startswith("  var DATA = ")][0]
    return json.loads(line[len("  var DATA = "):line.rindex("};") + 1])
art = data_of("../../art-mode.js"); orch = data_of("../../orch-mode.js"); cls = data_of("../../classic-mode.js")
ITEMS = [
 {"id": "art", "name": "명화 작가 퀴즈·모음", "emoji": "🖼️", "unit": "점", "label": "명화 그림", "total": len(art["W"]), "ls": "art-saved-v1", "cache": "fg-art-saved-v1", "link": "art-quiz.html", "note": "위키백과·위키미디어 공개 도메인 그림"},
 {"id": "orch", "name": "오케스트라 퀴즈·악기 도감", "emoji": "🎻", "unit": "종", "label": "악기 사진", "total": len(orch["I"]), "ls": "orch-saved-v1", "cache": "fg-orch-saved-v1", "link": "orchestra-quiz.html", "note": "위키백과·위키미디어 악기 사진(CC BY·CC BY-SA 포함, 사진가 표시)"},
 {"id": "cls", "name": "클래식 작곡가 퀴즈·모음", "emoji": "🎧", "unit": "곡", "label": "클래식 음원", "total": len(cls["P"]), "ls": "classic-saved-v1", "cache": "fg-classic-saved-v1", "link": "classic-quiz.html", "note": "공개 도메인·CC0 클래식 녹음의 앞부분(음질 선별이 끝난 곡만 듣기가 돼요)"},
]
BODY = '''  <div class="card"><p class="muted">온라인으로 받아 쓰는 그림·사진·음원이 <b>전체 몇 개 중 이 폰에 몇 개</b> 저장돼 있는지 보여 줘요. 저장하면 인터넷 없이도 볼 수 있어요. 저장 여부는 각 게임에서 직접 골라요.</p><p id="sum" class="center" style="font-size:1.05rem"></p><p id="est" class="muted center"></p></div>
  <div id="list"></div>
  <div class="card"><button class="btn" id="clrall" type="button">🗑️ 모두 지우기</button><p class="muted">지워도 게임에서 다시 보면 (인터넷이 있을 때) 또 저장할 수 있어요.</p></div>'''
JS = '''const ITEMS = ''' + json.dumps(ITEMS, ensure_ascii=False) + ''';
const fmt = b => b >= 1048576 ? (b / 1048576).toFixed(1) + "MB" : Math.max(1, Math.round(b / 1024)) + "KB";
function savedCount(it) { try { const o = JSON.parse(localStorage.getItem(it.ls) || "null"); return o && typeof o === "object" ? Object.keys(o).length : 0; } catch (e) { return 0; } }
async function bytes(it) { try { if (!("caches" in window)) return 0; const c = await caches.open(it.cache), ks = await c.keys(); let n = 0; for (const k of ks) { const r = await c.match(k); if (r) { const b = await r.blob(); n += b.size; } } return n; } catch (e) { return 0; } }
async function render() {
  let tot = 0, sv0 = 0, by = 0, html = "";
  for (const it of ITEMS) {
    const n = savedCount(it), b = await bytes(it); tot += it.total; sv0 += n; by += b;
    const pct = it.total ? Math.min(100, Math.round(n * 100 / it.total)) : 0;
    html += `<article class="card"><h2>${it.emoji} ${esc(it.name)}</h2><p class="muted">${esc(it.note)}</p><p>${it.total ? `<b>${esc(it.label)}</b> 전체 ${it.total}${it.unit} 중 이 폰에 <b>${n}${it.unit}</b> 저장 (${pct}%)` : `<b>${esc(it.label)}</b> 아직 준비 중이에요(음질 선별이 끝나면 듣기가 열리고 여기에 숫자가 나와요) · 이 폰에 ${n}${it.unit} 저장`}${b ? ` · 약 ${fmt(b)}` : ""}</p><div style="height:10px;border-radius:6px;background:var(--line);overflow:hidden"><div style="height:100%;width:${pct}%;background:var(--accent)"></div></div><div class="row" style="margin-top:8px"><a class="btn" href="${it.link}" style="text-decoration:none;text-align:center">${it.emoji} 열기</a>${n ? `<button class="btn ghost" type="button" data-clr="${it.id}">🗑️ 지우기</button>` : ""}</div></article>`;
  }
  $("list").innerHTML = html; $("sum").innerHTML = `전체 <b>${tot}</b>개 중 이 폰에 <b>${sv0}</b>개 저장 · 약 <b>${fmt(by)}</b>`;
  try { if (navigator.storage && navigator.storage.estimate) { const e = await navigator.storage.estimate(); if (e.quota) $("est").textContent = `이 앱이 쓰는 저장 공간 ${fmt(e.usage || 0)} / 쓸 수 있는 공간 약 ${fmt(e.quota)}`; } } catch (e) {}
}
async function clearItem(it) { try { if ("caches" in window) await caches.delete(it.cache); } catch (e) {} try { localStorage.removeItem(it.ls); } catch (e) {} }
$("list").addEventListener("click", async ev => { const b = ev.target.closest("[data-clr]"); if (!b) return; const it = ITEMS.find(x => x.id === b.dataset.clr); if (it && confirm(it.label + " 저장분을 지울까요?")) { await clearItem(it); render(); } });
$("clrall").addEventListener("click", async () => { if (confirm("저장한 그림·사진·음원을 모두 지울까요?")) { for (const it of ITEMS) await clearItem(it); render(); } });
render();'''
make("out/offline-media.html", "그림·음원 저장 현황", "📊", 200, "offline-media-v1", "온라인으로 받아 쓰는 그림·사진·음원이 전체 몇 개 중 이 폰에 몇 개 저장돼 있는지 보여 줘요.", BODY, JS, "")
print("전체", {it["id"]: it["total"] for it in ITEMS})
