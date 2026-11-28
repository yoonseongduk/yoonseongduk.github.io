/* 이 기기 고유 번호(기기 ID) — 같이 하기 등에서 "어느 폰인지" 구별할 때 써요.
   웹 앱은 폰의 하드웨어 번호(일련번호·IMEI 등)를 읽을 수 없어서, 처음 한 번 무작위 UUID를 만들어 이 폰에만 저장하고 바꾸지 않아요.
   닉네임(기기 이름)은 사람이 마음대로 바꿀 수 있고, 기기 ID는 그대로라서 이름을 바꿔도 같은 폰으로 알아봐요.
   앱 데이터(사이트 데이터)를 지우면 새 번호가 만들어져요. 기록 백업·복원에는 넣지 않아요(다른 폰에 복원해도 번호가 겹치지 않게, family.js 의 META).
   window.fgDevice.id() → "xxxxxxxx-xxxx-4xxx-…"  ·  fgDevice.short() → 화면에 보이는 짧은 표시(앞 4자리, 예: 3F9A) */
(function () {
  var K = "fg-device-id-v1";
  function gen() {
    try { if (window.crypto && crypto.randomUUID) return crypto.randomUUID(); } catch (e) {}
    var a = new Uint8Array(16);
    try { crypto.getRandomValues(a); } catch (e) { for (var i = 0; i < 16; i++) a[i] = Math.floor(Math.random() * 256); }
    a[6] = (a[6] & 15) | 64; a[8] = (a[8] & 63) | 128;
    var h = Array.prototype.map.call(a, function (b) { return (b + 256).toString(16).slice(1); }).join("");
    return h.slice(0, 8) + "-" + h.slice(8, 12) + "-" + h.slice(12, 16) + "-" + h.slice(16, 20) + "-" + h.slice(20);
  }
  var id = null;
  try { id = localStorage.getItem(K); if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(id || "")) { id = gen(); localStorage.setItem(K, id); } } catch (e) { id = id || gen(); }
  window.fgDevice = {
    id: function () { return id; },
    short: function (x) { return String(x || id || "").replace(/-/g, "").slice(0, 4).toUpperCase(); }
  };
})();
