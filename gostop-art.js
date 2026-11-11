/* 맞고 화투 48장 그림 — Wikimedia Commons 의 공개 그림(CC BY-SA 4.0, 저작자 Louie Mantia·すけじょ)을 그대로 써요.
   파일은 cards/ 폴더에 있고, 출처·라이선스 안내는 cards/LICENSE.txt 와 licenses.html 에 적어 뒀어요. 파일 내용은 고치지 않아요(고치면 같은 라이선스로 공개해야 해요).
   GoStopArt.url(번호) → 그림 파일 주소, GoStopArt.img(번호) → <img> 글자. 번호는 gostop-core.js 와 같아요(월 = (번호>>2)+1, 월 안 순서 = 번호&3).
   주의: 우리 11월(오동)은 Commons 의 December, 우리 12월(비·버들)은 Commons 의 November 그림이에요(일본과 한국의 월 순서가 달라요). */
(function (root) {
  "use strict";
  var MON = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  function type(id) { return root.GoStop.info(id).type; }
  function name(id) {
    var m = (id >> 2) + 1, k = id & 3, t = type(id), kind = t === "gwang" ? "Hikari" : t === "yeol" ? "Tane" : t === "ddi" ? "Tanzaku" : null, i, n = 0;
    if (m === 11) return "Hanafuda_December_" + (kind ? kind : k === 1 ? "Kasu_3" : k === 2 ? "Kasu_1" : "Kasu_2") + "_Alt.svg"; // 오동
    if (m === 12) return "Hanafuda_November_" + (kind ? kind : "Kasu") + "_Alt.svg"; // 비(버들)
    if (kind) return "Hanafuda_" + MON[m] + "_" + kind + "_Alt.svg";
    for (i = m * 4 - 4; i < id; i++) if (type(i) === "pi") n++; // 그 달의 첫 피 → Kasu_1, 둘째 피 → Kasu_2
    return "Hanafuda_" + MON[m] + "_Kasu_" + (n + 1) + "_Alt.svg";
  }
  function url(id) { return "cards/" + name(id); }
  function img(id) { return '<img src="' + url(id) + '" alt="" draggable="false">'; }
  function all() { var a = [], i; for (i = 0; i < 48; i++) a.push(url(i)); return a; }
  root.GoStopArt = { url: url, img: img, all: all };
})(typeof window !== "undefined" ? window : globalThis);
