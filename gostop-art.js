/* 맞고 화투 48장 그림 — 전부 직접 그린 단순한 도형(SVG)이에요. 외부 그림·글꼴·사진을 쓰지 않아요(저작권·오프라인).
   GoStopArt.svg(번호) → 100×100 칸에 그린 SVG 글자. 번호는 gostop-core.js 와 같아요(월 = (번호>>2)+1, 월 안 순서 = 번호&3).
   월마다 전통적인 소재(소나무·매화·벚꽃·싸리·창포·모란·억새·국화·단풍·오동·버들)를 도형으로 단순하게 그렸고,
   광·열끗(동물)·띠(리본)는 그 위에 덧그려요. 그림 모양만 이 파일에서 고쳐요. */
(function (root) {
  "use strict";
  var C = { green: "#2f8f4a", dgreen: "#1f6b34", lgreen: "#7cc576", brown: "#7a4a21", pink: "#f28ab2", lpink: "#fbc7da", red: "#d6453a", dred: "#a52a22", purple: "#6b4aa6", blue: "#3b6fd6", yellow: "#f2c230", gold: "#e0a81c", black: "#262626", white: "#ffffff", gray: "#8b93a1", sky: "#7fb4e8", tan: "#d9b46f", orange: "#ec8a2d" };
  var n = function (v) { return Math.round(v * 10) / 10; };
  function el(tag, a, inner) { var s = "<" + tag, k; for (k in a) s += " " + k + '="' + a[k] + '"'; return inner == null ? s + "/>" : s + ">" + inner + "</" + tag + ">"; }
  function circ(x, y, r, f, st) { return el("circle", { cx: n(x), cy: n(y), r: n(r), fill: f, stroke: st || "none", "stroke-width": st ? 1 : 0 }); }
  function ell(x, y, rx, ry, f, rot, st) { var a = { cx: n(x), cy: n(y), rx: n(rx), ry: n(ry), fill: f }; if (rot) a.transform = "rotate(" + rot + " " + n(x) + " " + n(y) + ")"; if (st) { a.stroke = st; a["stroke-width"] = 1; } return el("ellipse", a); }
  function path(d, f, st, sw) { return el("path", { d: d, fill: f || "none", stroke: st || "none", "stroke-width": sw || 0, "stroke-linecap": "round", "stroke-linejoin": "round" }); }
  function rect(x, y, w, h, f, rx) { return el("rect", { x: n(x), y: n(y), width: n(w), height: n(h), rx: rx || 0, fill: f }); }
  function poly(pts, f) { return el("polygon", { points: pts, fill: f }); }
  function grp(t, inner) { return el("g", { transform: t }, inner); }
  function flower(x, y, r, f, c) { var s = "", i, a; for (i = 0; i < 5; i++) { a = i * 72 * Math.PI / 180; s += circ(x + Math.sin(a) * r * 0.8, y - Math.cos(a) * r * 0.8, r * 0.62, f); } return s + circ(x, y, r * 0.4, c || C.yellow); }
  function bunch(x, y, f, len) { var s = path("M" + x + "," + y + " q-3,8 0,16", "none", C.dgreen, 1.6), i; for (i = 0; i < len; i++) s += ell(x + (i % 2 ? 2.6 : -2.6), y + 9 + i * 7, 4.4 - i * 0.4, 3.4, f); return s; }
  function leaf(x, y, w, h, rot, f) { return ell(x, y, w, h, f || C.green, rot); }
  function maple(x, y, s, f) { return grp("translate(" + x + " " + y + ") scale(" + s + ")", path("M0,-18 L4,-8 L14,-12 L10,-2 L18,2 L8,6 L10,16 L0,10 L-10,16 L-8,6 L-18,2 L-10,-2 L-14,-12 L-4,-8 Z", f, C.dred, 0.8)); }

  // ── 월별 바탕 그림 (소재)
  var PLANT = {
    1: function () { return rect(46, 58, 8, 34, C.brown, 2) + poly("50,10 22,44 78,44", C.dgreen) + poly("50,26 16,60 84,60", C.green) + poly("50,44 10,80 90,80", C.dgreen); },
    2: function () { return path("M8,88 Q38,66 62,44 T94,12", "none", C.brown, 4) + flower(30, 66, 9, C.pink) + flower(56, 46, 8, C.lpink) + flower(78, 24, 9, C.pink) + flower(46, 80, 6, C.lpink) + flower(86, 50, 6, C.pink); },
    3: function () { return path("M6,90 Q40,70 70,50 T96,16", "none", C.brown, 3) + flower(22, 72, 10, C.lpink) + flower(46, 58, 12, C.pink) + flower(72, 40, 11, C.lpink) + flower(84, 20, 9, C.pink) + flower(34, 86, 7, C.pink); },
    4: function () { return path("M10,12 Q50,6 90,14", "none", C.brown, 3) + bunch(24, 14, C.black, 5) + bunch(50, 12, "#4a3068", 6) + bunch(76, 14, C.black, 5) + leaf(34, 24, 5, 12, 30) + leaf(66, 24, 5, 12, -30); },
    5: function () { return path("M30,95 Q26,60 18,30", "none", C.green, 5) + path("M44,95 Q46,55 52,20", "none", C.dgreen, 5) + path("M60,95 Q70,60 84,36", "none", C.green, 5) + ell(36, 36, 10, 14, C.purple, -20) + ell(56, 30, 9, 13, C.blue, 12) + circ(46, 36, 4, C.yellow); },
    6: function () { return leaf(20, 62, 14, 7, -25) + leaf(80, 62, 14, 7, 25) + circ(50, 50, 28, "#e45a6a") + circ(50, 50, 20, C.red) + circ(50, 50, 12, C.dred) + circ(50, 50, 5, C.yellow) + leaf(50, 86, 10, 6, 0, C.dgreen); },
    7: function () { return path("M10,12 Q50,6 90,14", "none", C.brown, 3) + bunch(24, 14, "#c0502e", 6) + bunch(50, 12, "#e0643a", 7) + bunch(76, 14, "#c0502e", 6) + leaf(36, 26, 5, 12, 30, C.lgreen) + leaf(64, 26, 5, 12, -30, C.lgreen); },
    8: function () { return path("M0,100 L0,66 Q50,42 100,66 L100,100 Z", C.black) + path("M16,100 q-4,-30 -8,-40 M34,100 q-2,-24 0,-44 M66,100 q2,-26 -2,-46 M86,100 q4,-24 8,-38", "none", C.tan, 3); },
    9: function () { var s = "", i; for (i = 0; i < 12; i++) s += ell(50 + Math.sin(i * 30 * Math.PI / 180) * 18, 46 - Math.cos(i * 30 * Math.PI / 180) * 18, 5, 12, C.yellow, i * 30); return leaf(22, 78, 12, 6, -30) + leaf(78, 78, 12, 6, 30) + s + circ(50, 46, 11, C.orange); },
    10: function () { return path("M6,92 Q40,70 64,46 T96,14", "none", C.brown, 3) + maple(26, 66, 1, C.red) + maple(54, 44, 1.2, C.orange) + maple(78, 24, 0.9, C.red) + maple(46, 80, 0.7, C.orange) + maple(84, 56, 0.7, C.red); },
    11: function () { return path("M50,95 Q50,60 50,28", "none", C.brown, 4) + path("M50,60 Q22,60 18,36 Q42,38 50,60 Z", C.green) + path("M50,60 Q78,60 82,36 Q58,38 50,60 Z", C.dgreen) + ell(50, 22, 5, 11, C.purple) + ell(41, 26, 4, 9, "#8d6fc4", 20) + ell(59, 26, 4, 9, "#8d6fc4", -20); },
    12: function () { var s = "", i; for (i = 0; i < 7; i++) s += path("M" + (12 + i * 13) + ",10 q-4,30 0,62", "none", C.green, 2); for (i = 0; i < 9; i++) s += path("M" + (6 + i * 11) + ",20 l-5,16", "none", C.sky, 1.5); return path("M0,10 L100,10", "none", C.brown, 4) + s; }
  };

  // ── 광(빛) 장식
  var GWANG = {
    1: function () { return circ(66, 28, 15, C.red) + ell(38, 62, 20, 11, C.white, 0, C.gray) + path("M26,56 Q14,40 22,24", "none", C.white, 5) + path("M26,56 Q14,40 22,24", "none", C.gray, 1) + circ(22, 24, 5, C.white, C.gray) + circ(21, 22, 2, C.red) + poly("16,26 8,28 16,30", C.orange) + path("M52,70 l-4,18 M44,72 l-4,16", "none", C.gray, 2) + path("M54,58 q14,-2 22,6 q-10,4 -22,-2 Z", C.black); },
    3: function () { return rect(8, 14, 84, 46, C.red) + path("M8,37 Q30,24 50,37 T92,37", "none", C.white, 7) + rect(8, 14, 5, 52, C.brown) + rect(87, 14, 5, 52, C.brown) + circ(30, 76, 8, C.lpink) + circ(52, 82, 9, C.pink) + circ(74, 76, 8, C.lpink); },
    8: function () { return ""; },
    11: function () { return path("M30,60 Q20,30 40,24 Q56,20 60,36 Q64,52 46,60 Z", C.red) + circ(58, 30, 7, C.gold) + poly("64,28 76,24 66,34", C.orange) + circ(60, 28, 1.6, C.black) + path("M30,60 Q8,70 16,92 M36,64 Q22,84 40,94 M42,66 Q44,86 62,92", "none", C.gold, 4) + path("M44,50 q16,-4 28,10", "none", C.dred, 3); },
    12: function () { return path("M18,40 Q50,0 82,40 Z", C.red) + path("M50,22 L50,80", "none", C.black, 2.5) + circ(50, 62, 5, "#f1d3b0") + path("M50,67 L50,84 M50,72 L40,80 M50,72 L60,80 M50,84 L44,96 M50,84 L56,96", "none", C.black, 2.5); }
  };

  // ── 열끗(동물·물건) 장식
  function bird(x, y, s, body, belly) { return grp("translate(" + x + " " + y + ") scale(" + s + ")", ell(0, 0, 14, 9, body) + ell(2, 3, 9, 5, belly || body) + circ(-12, -6, 7, body) + poly("-18,-7 -26,-5 -18,-3", C.orange) + circ(-13, -7, 1.4, C.black) + path("M12,-2 L30,6 L20,0 Z", C.dgreen) + path("M-4,-3 Q4,-12 12,-4 Q4,2 -4,-3 Z", C.black)); }
  var YEOL = {
    2: function () { return bird(54, 56, 1.35, "#8aa63a", "#e9e2a4"); },
    4: function () { return bird(58, 60, 1.35, "#7c8794", "#e8e8ee"); },
    5: function () { return path("M4,88 Q50,36 96,88", "none", C.brown, 9) + path("M4,88 Q50,36 96,88", "none", "#a7713a", 4) + path("M14,66 l0,24 M30,50 l0,38 M50,44 l0,40 M70,50 l0,38 M86,66 l0,24", "none", C.brown, 2.5) + path("M0,94 Q25,88 50,94 T100,94", "none", C.sky, 5); },
    6: function () { return grp("translate(36 40)", ell(-9, 0, 11, 8, C.orange, -20, C.dred) + ell(9, 0, 11, 8, C.orange, 20, C.dred) + ell(-7, 10, 7, 5, C.yellow, 15) + ell(7, 10, 7, 5, C.yellow, -15) + rect(-1.4, -6, 2.8, 20, C.black, 1)) + grp("translate(66 66) scale(.8)", ell(-9, 0, 11, 8, C.sky, -20, C.blue) + ell(9, 0, 11, 8, C.sky, 20, C.blue) + rect(-1.4, -6, 2.8, 18, C.black, 1)); },
    7: function () { return grp("translate(50 62)", ell(0, 0, 28, 17, "#5a3b25") + circ(-26, -4, 12, "#5a3b25") + ell(-37, 0, 7, 6, "#caa27c") + path("M-34,6 q-4,4 -8,2", "none", C.white, 2) + poly("-30,-12 -26,-22 -22,-12", "#5a3b25") + circ(-28, -7, 1.6, C.white) + rect(-18, 10, 6, 16, "#3e281a") + rect(-4, 10, 6, 16, "#3e281a") + rect(10, 10, 6, 16, "#3e281a") + rect(20, 10, 6, 16, "#3e281a") + path("M28,-6 q8,-4 10,4", "none", "#5a3b25", 3) + path("M-16,-14 l4,8 M-8,-16 l3,8 M0,-16 l2,8", "none", "#3e281a", 2)); },
    8: function () { var g = function (x, y, s) { return grp("translate(" + x + " " + y + ") scale(" + s + ")", path("M-16,0 Q-8,-10 0,0 Q8,-10 16,0 Q8,-3 0,5 Q-8,-3 -16,0 Z", "#fdf1c4")); }; return g(34, 24, 1.1) + g(66, 38, 1) + g(46, 54, 0.9); },
    9: function () { return path("M26,50 Q50,106 74,50 Z", C.red, C.dred, 1.5) + ell(50, 50, 24, 6, C.gold) + ell(50, 50, 20, 3.4, "#7a1d16") + rect(44, 76, 12, 6, C.gold, 2) + path("M38,64 q12,10 24,0", "none", C.gold, 2); },
    10: function () { return grp("translate(52 58)", ell(0, 0, 22, 13, "#b8793c") + circle2() + rect(-16, 8, 5, 20, "#8b5a2b") + rect(-6, 8, 5, 20, "#8b5a2b") + rect(8, 8, 5, 20, "#8b5a2b") + rect(18, 8, 5, 20, "#8b5a2b") + path("M-20,-4 Q-34,-14 -34,-30", "none", "#b8793c", 7) + ell(-37, -32, 8, 6, "#b8793c", -20) + path("M-38,-38 l-5,-12 m5,12 l4,-12 m-4,8 l-10,-6 m16,6 l8,-8", "none", C.brown, 2) + circ(-41, -33, 1.4, C.black) + circ(-8, -4, 2, C.white) + circ(6, 2, 2, C.white) + circ(-2, 5, 1.6, C.white)); },
    12: function () { return grp("translate(52 54) scale(1.2)", ell(0, 0, 14, 7, C.black) + ell(-2, 3, 8, 4, C.white) + circ(-13, -3, 6, C.black) + poly("-18,-3 -24,-2 -18,0", C.orange) + circ(-14, -4, 1.2, C.white) + path("M10,0 L30,-10 L24,-1 L32,4 L12,4 Z", C.black) + path("M-4,-4 Q6,-16 16,-4 Q6,0 -4,-4 Z", "#33333f")); }
  };
  function circle2() { return ""; }

  // ── 띠(리본) 장식
  var RIBBON = { red: [C.red, "홍단"], blue: [C.blue, "청단"], cho: [C.green, "초단"], plain: ["#9aa0aa", ""] };
  function ribbon(sub) {
    var r = RIBBON[sub] || RIBBON.plain, t = "";
    if (r[1]) t = el("text", { x: 50, y: 58, "text-anchor": "middle", "font-size": 15, "font-weight": 800, fill: "#fff", "font-family": "sans-serif" }, r[1]);
    return poly("6,36 94,36 86,50 94,64 6,64 14,50", r[0]) + path("M6,36 L94,36 M6,64 L94,64", "none", "rgba(0,0,0,.25)", 1.2) + t;
  }

  // 월마다 바탕색(카드 그림이 한눈에 구분되게). 8월은 밤하늘.
  var BG = { 1: "#dff0ff", 2: "#ffeaf2", 3: "#ffdbe9", 4: "#ece2fb", 5: "#dfe9fc", 6: "#ffdfdc", 7: "#ffe6d3", 9: "#fff1c0", 10: "#ffe4c4", 11: "#e8dcf6", 12: "#d9e8f1" };
  function glow(cx, cy, r, f, o) { return el("circle", { cx: cx, cy: cy, r: r, fill: f, "fill-opacity": o }); }
  // 8월: 달이 뜬 밤 풍경. 광(보름달) 카드는 달을 크게 그려 한눈에 알아볼 수 있게 한다.
  function scene8(gw) {
    var s = rect(0, 0, 100, 100, gw ? "#5a2a68" : "#2b2350", 6), i, st = [[14, 14, 1.4], [30, 8, 1], [86, 12, 1.4], [70, 24, 1], [10, 36, 1], [92, 40, 1.2]];
    if (gw) s += glow(50, 40, 44, "#ff9fb8", 0.22) + glow(50, 40, 36, "#ffd0dc", 0.3) + circ(50, 40, 27, "#fffbe0") + circ(41, 32, 5, "#efe5b6") + circ(60, 46, 6, "#efe5b6") + circ(53, 27, 3, "#efe5b6");
    else { for (i = 0; i < st.length; i++) s += circ(st[i][0], st[i][1], st[i][2], "#fff"); s += circ(76, 26, 10, "#fff3c0") + circ(80, 23, 8, "#2b2350"); }
    s += path("M0,100 L0,68 Q50,44 100,68 L100,100 Z", gw ? "#2a1238" : "#15122e") + path("M16,100 q-4,-26 -8,-34 M34,100 q-2,-22 0,-38 M66,100 q2,-22 -2,-40 M86,100 q4,-22 8,-32 M50,100 q-1,-18 1,-28", "none", C.gold, 2.6);
    return s;
  }
  function svg(id) {
    var m = (id >> 2) + 1, body = "";
    var types = root.GoStop ? root.GoStop.info(id) : null, type = types ? types.type : null, sub = types ? types.sub : "";
    if (m === 8) body += scene8(type === "gwang"); else body += rect(0, 0, 100, 100, BG[m], 6) + PLANT[m]();
    if (type === "gwang") body += (GWANG[m] ? GWANG[m]() : "");
    else if (type === "yeol") body += YEOL[m]();
    else if (type === "ddi") body += ribbon(sub);
    else if (types && types.pi === 2) body += circ(82, 82, 9, C.red, C.dred) + el("text", { x: 82, y: 87, "text-anchor": "middle", "font-size": 12, "font-weight": 800, fill: "#fff", "font-family": "sans-serif" }, "2");
    return '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">' + body + "</svg>";
  }
  root.GoStopArt = { svg: svg };
})(typeof window !== "undefined" ? window : globalThis);
