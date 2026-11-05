/* 약 복용 알림 (모든 화면 공용). 약 복용 체크표에서 알림을 켜 두면, 다른 게임 화면에서도 시간이 될 때 알려 줘요.
   앱(브라우저 화면)이 열려 있을 때만 동작해요. 데이터는 약 복용 체크표와 같은 localStorage("med-check-v1")를 읽어요. */
(function () {
  if (/med-check\.html/.test(location.pathname) || window.parent !== window) return;   // 같이 하기 안(화면 속 화면)에서는 바깥 화면이 알려 줘요
  var KEY = "med-check-v1", SL = [["m", "아침"], ["n", "점심"], ["e", "저녁"], ["b", "자기 전"]];
  function pad(n) { return String(n).padStart(2, "0"); }
  function today() { var d = new Date(); return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  function load() { try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; } }
  function save(S) { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} }
  function pending(S, k, d) { var lg = (S.log || {})[d] || {}; return (S.meds || []).filter(function (m) { return m.t.indexOf(k) >= 0 && (m.since || "0000") <= d && !lg[m.id + "|" + k]; }); }
  function lab(m) { return (m.who ? m.who + " · " : "") + m.n; }
  function beep() { try { var A = window.AudioContext || window.webkitAudioContext, c = new A(); [0, .35, .7].forEach(function (t) { var o = c.createOscillator(), g = c.createGain(); o.frequency.value = 880; o.connect(g); g.connect(c.destination); g.gain.setValueAtTime(.2, c.currentTime + t); g.gain.exponentialRampToValueAtTime(.001, c.currentTime + t + .25); o.start(c.currentTime + t); o.stop(c.currentTime + t + .27); }); } catch (e) {} }
  function notify(title, body) {
    try { if (navigator.vibrate) navigator.vibrate([300, 150, 300, 150, 300]); } catch (e) {}
    if (!("Notification" in window) || Notification.permission !== "granted") return;
    try { navigator.serviceWorker.getRegistration().then(function (r) { if (r) r.showNotification(title, { body: body, tag: "med", renotify: true, icon: "icon-192.png", vibrate: [300, 150, 300] }); else new Notification(title, { body: body }); }).catch(function () {}); } catch (e) {}
  }
  function toast(title, names, slot) {
    var old = document.getElementById("med-toast"); if (old) old.remove();
    var t = document.createElement("div"); t.id = "med-toast"; t.setAttribute("role", "alert");
    t.style.cssText = "position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:99999;background:#1c2233;color:#fff;border-radius:14px;padding:12px 14px;box-shadow:0 6px 24px rgba(0,0,0,.4);font:15px/1.45 system-ui,sans-serif;max-width:440px;margin:0 auto";
    t.innerHTML = '<b></b><div style="margin:2px 0 8px;opacity:.85"></div><div style="display:flex;gap:8px"><button type="button" data-a="ok" style="flex:1;padding:9px;border:0;border-radius:10px;background:#4cc98a;color:#10131c;font-weight:700">먹었어요 ✅</button><a href="med-check.html" style="flex:1;padding:9px;border-radius:10px;background:#3b4766;color:#fff;text-align:center;text-decoration:none;font-weight:700">약 앱 열기</a><button type="button" data-a="x" style="padding:9px 12px;border:0;border-radius:10px;background:transparent;color:#fff;font-size:16px" aria-label="닫기">✕</button></div>';
    t.querySelector("b").textContent = title; t.querySelector("div").textContent = names;
    t.onclick = function (e) {
      var a = e.target.getAttribute && e.target.getAttribute("data-a"); if (!a) return;
      if (a === "ok") { var S = load(); if (S) { var d = today(); S.log = S.log || {}; var l = S.log[d] = S.log[d] || {}; pending(S, slot, d).forEach(function (m) { l[m.id + "|" + slot] = 1; }); save(S); } }
      t.remove();
    };
    document.body.appendChild(t); setTimeout(function () { if (t.parentNode) t.remove(); }, 120000);
  }
  function tick() {
    var S = load(); if (!S || !S.al || !S.al.on) return;
    var dt = new Date(), now = pad(dt.getHours()) + ":" + pad(dt.getMinutes()), nm0 = dt.getHours() * 60 + dt.getMinutes(), d = today(); S.rung = S.rung || {}; var ch = false;
    SL.forEach(function (x) {
      var k = x[0], nm = x[1], tm = (S.al.t || {})[k]; if (!tm) return; var p = tm.split(":"), diff = nm0 - (+p[0] * 60 + +p[1]), key = d + k + now, rep = +S.al.rep || 0;
      if (diff < 0 || diff > 180 || S.rung[key]) return; if (!(diff === 0 || (rep > 0 && diff % rep === 0))) return;
      S.rung[key] = 1; ch = true; var ps = pending(S, k, d); if (!ps.length) return;
      var names = ps.map(lab).join(", "), title = (diff ? "💊 (다시 알림) " : "💊 ") + nm + " 약 먹을 시간이에요";
      notify(title, names + (diff ? " · 먹었으면 체크해 주세요" : "")); beep(); toast(title, names, k);
    });
    if (ch) save(S);
  }
  function missed() {
    if (!/\/(index\.html)?$/.test(location.pathname)) return; var S = load(); if (!S || !S.meds) return;
    var dt = new Date(), now = pad(dt.getHours()) + ":" + pad(dt.getMinutes()), d = today();
    if (S.al && S.al.on) for (var i = 0; i < SL.length; i++) { var k = SL[i][0], tm = (S.al.t || {})[k], flag = "med-missed-" + d + k; if (!tm || tm > now) continue; var ps = pending(S, k, d); if (!ps.length) continue; try { if (sessionStorage.getItem(flag)) continue; sessionStorage.setItem(flag, "1"); } catch (e) {}
      toast("💊 " + SL[i][1] + " 약 아직이에요 (" + tm + ")", ps.map(lab).join(", "), k); return; }
    care(S, d);
  }
  // 시작 화면에서 하루 한 번: 약이 얼마 안 남았거나 병원 가는 날이 다가오면 알려 줘요 (계산 방식은 med-check.html과 같아요)
  function care(S, d) {
    var flag = "med-care-" + d; try { if (localStorage.getItem(flag)) return; } catch (e) {}
    var dn = function (s) { var p = s.split("-"); return Math.round(Date.UTC(+p[0], p[1] - 1, +p[2]) / 86400000); }, msg = [];
    (S.meds || []).forEach(function (m) {
      if (m.st != null) { var tk = 0; Object.keys(S.log || {}).forEach(function (dd) { Object.keys(S.log[dd]).forEach(function (k) { if (k.indexOf(m.id + "|") === 0) tk++; }); });
        var r = m.st - (tk - (m.base || 0)) * (m.per || 1), dl = Math.floor(r / ((m.per || 1) * m.t.length));
        if (r <= 0) msg.push(lab(m) + ": 약이 다 떨어졌어요"); else if (dl <= (+S.warn || 5)) msg.push(lab(m) + ": 약 " + Math.max(0, dl) + "일치 남음"); }
      if (m.vd) { var dv = dn(m.vd) - dn(d); if (dv >= 0 && dv <= 3) msg.push(lab(m) + ": 병원 " + (dv ? "D-" + dv : "오늘")); }
    });
    if (!msg.length) return; try { localStorage.setItem(flag, "1"); Object.keys(localStorage).forEach(function (k) { if (k.indexOf("med-care-") === 0 && k !== flag) localStorage.removeItem(k); }); } catch (e) {}
    var t = document.createElement("div"); t.id = "med-toast"; t.setAttribute("role", "alert");
    t.style.cssText = "position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:99999;background:#1c2233;color:#fff;border-radius:14px;padding:12px 14px;box-shadow:0 6px 24px rgba(0,0,0,.4);font:15px/1.45 system-ui,sans-serif;max-width:440px;margin:0 auto";
    t.innerHTML = '<b>⚠️ 약·병원 챙기기</b><div style="margin:2px 0 8px;opacity:.85"></div><div style="display:flex;gap:8px"><a href="med-check.html" style="flex:1;padding:9px;border-radius:10px;background:#3b4766;color:#fff;text-align:center;text-decoration:none;font-weight:700">약 앱 열기</a><button type="button" style="padding:9px 12px;border:0;border-radius:10px;background:transparent;color:#fff;font-size:16px" aria-label="닫기">✕</button></div>';
    t.querySelector("div").textContent = msg.join(" / "); t.querySelector("button").onclick = function () { t.remove(); };
    document.body.appendChild(t); setTimeout(function () { if (t.parentNode) t.remove(); }, 60000);
  }
  setInterval(tick, 15000); document.addEventListener("visibilitychange", function () { if (!document.hidden) tick(); });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { tick(); missed(); }); else { tick(); missed(); }
})();
