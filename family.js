/* 가족·친구 명단(공용)과 백업 알림. 가족 명단은 localStorage "family-members-v1", 친구 명단은 "friend-members-v1"에 이름 배열로,
   이 폰 주인(나)은 "family-me-v1"에 이름 하나로 저장돼요. */
(function () {
  var K = "family-members-v1", KF = "friend-members-v1", KME = "family-me-v1";
  function getK(k) { try { var a = JSON.parse(localStorage.getItem(k)); return Array.isArray(a) ? a.filter(function (x) { return typeof x === "string" && x; }) : []; } catch (e) { return []; } }
  function setK(k, a) { try { localStorage.setItem(k, JSON.stringify(a)); } catch (e) {} }
  function get() { return getK(K); }
  function set(a) { setK(K, a); }
  var me = {
    get: function () { try { var v = JSON.parse(localStorage.getItem(KME)); return typeof v === "string" ? v : ""; } catch (e) { return ""; } },
    set: function (v) { try { if (v) localStorage.setItem(KME, JSON.stringify(v)); else localStorage.removeItem(KME); } catch (e) {} }
  };
  window.FAMILY = { key: K, get: get, set: set, me: me };
  window.FRIENDS = { key: KF, get: function () { return getK(KF); }, set: function (a) { setK(KF, a); } };

  // 시작 화면에서만: 백업한 지 오래됐으면 부드럽게 알려 줘요
  if (!/\/(index\.html)?$/.test(location.pathname)) return;
  var META = ["fg-first-seen", "fg-backup-last", "fg-backup-snooze"], DAY = 86400000;
  function num(k) { try { return +localStorage.getItem(k) || 0; } catch (e) { return 0; } }
  function put(k, v) { try { localStorage.setItem(k, String(v)); } catch (e) {} }
  function hasData() { try { for (var i = 0; i < localStorage.length; i++) { var k = localStorage.key(i); if (META.indexOf(k) < 0 && !/-best-|-wins-|-stats-/.test(k) && k !== "wrongnotes-ui-v1") return true; } } catch (e) {} return false; }
  function run() {
    var now = Date.now(); if (!num(META[0])) put(META[0], now);
    if (!hasData() || now < num(META[2])) return;
    var last = num(META[1]), base = last || num(META[0]), gap = last ? 30 : 7;
    if (now - base < gap * DAY) return;
    var days = Math.floor((now - base) / DAY), t = document.createElement("div");
    t.style.cssText = "position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:99998;background:#1c2233;color:#fff;border-radius:14px;padding:12px 14px;box-shadow:0 6px 24px rgba(0,0,0,.4);font:15px/1.45 system-ui,sans-serif;max-width:440px;margin:0 auto";
    t.innerHTML = '<b>💾 기록 백업을 해 둘까요?</b><div style="margin:2px 0 8px;opacity:.85">' + (last ? "마지막 백업 후 " + days + "일이 지났어요." : "앱을 쓴 지 " + days + "일 됐는데 아직 백업이 없어요.") + ' 폰을 바꾸거나 앱을 지우면 기록이 사라질 수 있어요.</div><div style="display:flex;gap:8px"><a href="backup.html" style="flex:1;padding:9px;border-radius:10px;background:#4cc98a;color:#10131c;text-align:center;text-decoration:none;font-weight:700">백업하러 가기</a><button type="button" style="padding:9px 14px;border:0;border-radius:10px;background:#3b4766;color:#fff;font-weight:700">나중에</button></div>';
    t.querySelector("button").onclick = function () { put(META[2], Date.now() + 7 * DAY); t.remove(); };
    document.body.appendChild(t);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run); else run();
})();
