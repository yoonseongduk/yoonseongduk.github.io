/* 가족 게임 공용(머리말에서 가장 먼저 읽는다):
   ① 사람별 기록 — 게임의 최고 기록 키(-best-·-wins-·-stats-)를 "현재 플레이어"별로 나눠 저장한다.
      이 폰 주인(family-me-v1)의 기록은 예전 키 그대로, 다른 사람은 "키::이름"으로 저장한다(게임 코드는 그대로).
   ② 포인트 — 게임을 해 보면 기본 점수, 이기거나 최고 기록을 세우면 가산 점수(저장 fg-points-v1).
   점수 숫자는 아래 CFG 한 곳에서만 고친다(design 결정 D6). 게임 목록은 tools/dev/person_gen.py 가 GAMES 줄을 채운다. */
(function () {
  if (window.fgPerson || location.protocol === "about:") return;
  var LS, g0, s0, r0;
  try { LS = window.localStorage; var SP = Storage.prototype; g0 = SP.getItem; s0 = SP.setItem; r0 = SP.removeItem; } catch (e) { return; }
  var CFG = { base: 10, perDay: 3, win: 20, best: 30, first: 20, hard: 1.5, streakStep: 5, streakMax: 30, minSec: 10, keepLog: 60 };
  /*GAMES*/ var GAMES = {"aim-trainer.html":1,"air-hockey.html":1,"alien-defense.html":1,"alkkagi.html":1,"animal-quiz.html":1,"archery.html":1,"arrow-reaction.html":1,"balance-game.html":1,"ball-juggle.html":1,"balloon-pop.html":1,"basketball-shoot.html":1,"binary-game.html":1,"bingo.html":1,"blackjack.html":1,"block-puzzle.html":1,"block-stack.html":1,"bomb-pass.html":1,"bowling.html":1,"breakout.html":1,"bug-squash.html":1,"cannon-shot.html":1,"capital-quiz.html":1,"car-dodge.html":1,"cave-flyer.html":1,"cham-cham-cham.html":1,"charades.html":1,"checkers.html":1,"choseong-party.html":1,"chosung-quiz.html":1,"click-speed.html":1,"clock-quiz.html":1,"coin-chase.html":1,"color-code.html":1,"color-fill.html":1,"color-match.html":1,"color-mix-quiz.html":1,"color-sequence.html":1,"count-flash.html":1,"dialect-quiz.html":1,"dice-combo.html":1,"dino-quiz.html":1,"dobble-match.html":1,"dots-boxes.html":1,"earth-quiz.html":1,"economy-quiz.html":1,"emoji-english-quiz.html":1,"emoji-quiz.html":1,"english-quiz.html":1,"equation-fill.html":1,"fairytale-quiz.html":1,"fishing.html":1,"flag-quiz.html":1,"flip-board.html":1,"food-worldcup.html":1,"four-in-row.html":1,"frog-jump.html":1,"fruit-catch.html":1,"fruit-slice.html":1,"game-31.html":1,"gravity-flip.html":1,"hangman.html":1,"hanja-idiom-quiz.html":1,"hanja-quiz.html":1,"hanja-today.html":1,"hanja-write.html":1,"hanoi.html":1,"heritage-quiz.html":1,"hero-quiz.html":1,"hex-game.html":1,"high-card.html":1,"high-low.html":1,"idiom-quiz.html":1,"insect-quiz.html":1,"invention-quiz.html":1,"it-quiz.html":1,"jlpt-quiz.html":1,"job-quiz.html":1,"jump-runner.html":1,"jump-up.html":1,"knights-tour.html":1,"korea-quiz.html":1,"korean-food-quiz.html":1,"korean-history-quiz.html":1,"ladder-game.html":1,"light-off.html":1,"magic-square.html":1,"make24.html":1,"mancala.html":1,"math-quiz.html":1,"maze.html":1,"memory-duel.html":1,"memory-match.html":1,"meteor-dodge.html":1,"mine-puzzle.html":1,"mini-golf.html":1,"mini-sudoku.html":1,"mirror-pattern.html":1,"mukjjippa.html":1,"music-quiz.html":1,"n-queens.html":1,"nonogram.html":1,"number-baseball.html":1,"number-memory.html":1,"number-merge.html":1,"number-pyramid.html":1,"number-sort.html":1,"number-tap.html":1,"odd-color.html":1,"odd-emoji.html":1,"odd-even.html":1,"omok.html":1,"one-card.html":1,"one-stroke.html":1,"onomatopoeia-quiz.html":1,"ox-quiz.html":1,"pancake-flip.html":1,"pattern-memory.html":1,"peg-solitaire.html":1,"penalty-kick.html":1,"pig-dice.html":1,"pipe-connect.html":1,"plant-quiz.html":1,"plinko.html":1,"poker-draw.html":1,"proverb-quiz.html":1,"purekorean-quiz.html":1,"quick-math.html":1,"quiz-buzzer.html":1,"reaction-duel.html":1,"reaction-test.html":1,"red-green-light.html":1,"reverse-memory.html":1,"reverse-tap.html":1,"rhythm-tap.html":1,"road-cross.html":1,"robot-path.html":1,"rps-streak.html":1,"rps-tournament.html":1,"safety-quiz.html":1,"sea-quiz.html":1,"sentence-order.html":1,"sequence-quiz.html":1,"ship-hunt.html":1,"size-compare.html":1,"slide-puzzle.html":1,"snake.html":1,"snakes-ladders.html":1,"space-quiz.html":1,"space-shooter.html":1,"spelling-quiz.html":1,"sports-quiz.html":1,"spot-memory.html":1,"stack-tower.html":1,"stroop-color.html":1,"sudoku.html":1,"table-tennis.html":1,"tap-duel.html":1,"ten-pairs.html":1,"tic-tac-toe.html":1,"time-stop.html":1,"times-table.html":1,"tradition-quiz.html":1,"treasure-hunt.html":1,"trivia-quiz.html":1,"truth-dare.html":1,"twenty-questions.html":1,"typing-test.html":1,"up-down.html":1,"water-sort.html":1,"weather-quiz.html":1,"weekday-quiz.html":1,"whack-a-mole.html":1,"wing-bird.html":1,"word-chain.html":1,"word-guess-en.html":1,"word-scramble.html":1,"word-search.html":1,"word-trick.html":1,"world-food-quiz.html":1,"worldhero-quiz.html":1,"wrong-notes.html":1,"yut-nori.html":1,"zodiac-quiz.html":1}; var HARD = {"sudoku.html":1,"mini-sudoku.html":1,"nonogram.html":1,"n-queens.html":1,"knights-tour.html":1,"magic-square.html":1,"hanoi.html":1,"water-sort.html":1,"mine-puzzle.html":1,"block-stack.html":1,"hanja-write.html":1,"peg-solitaire.html":1,"checkers.html":1}; /*/GAMES*/
  var PAT = /-best-|-wins-|-stats-/, PK = "fg-points-v1", PLAYER = "fg-player-v1", ME = "family-me-v1";
  var RAWPAGE = /\/(backup|family-points)\.html$/.test(location.pathname); // 이 화면들은 사람별 키 변환 없이 저장소를 그대로 읽는다

  function rg(k) { try { return g0.call(LS, k); } catch (e) { return null; } }
  function rs(k, v) { try { s0.call(LS, k, v); } catch (e) {} }
  function jp(k) { try { return JSON.parse(rg(k)); } catch (e) { return null; } }
  function owner() { var v = jp(ME); return typeof v === "string" ? v : ""; }
  function player() { var p = rg(PLAYER); return p || owner(); }
  function suffix() { var p = player(); return p && p !== owner() ? p : ""; }
  function map(k) {
    if (RAWPAGE || typeof k !== "string" || !PAT.test(k) || k.indexOf("::") >= 0 || k.indexOf("play-together") === 0) return k;
    var s = suffix(); return s ? k + "::" + s : k;
  }

  // ── 사람별 기록: 저장소 읽기·쓰기를 가로채 키 이름만 바꾼다
  var bestHook = null;
  Storage.prototype.getItem = function (k) { return g0.call(this, this === LS ? map(k) : k); };
  Storage.prototype.removeItem = function (k) { return r0.call(this, this === LS ? map(k) : k); };
  Storage.prototype.setItem = function (k, v) {
    if (this !== LS) return s0.call(this, k, v);
    var mk = map(k), old = null;
    if (bestHook && typeof k === "string" && /-best-/.test(k)) { try { old = g0.call(this, mk); } catch (e) {} }
    s0.call(this, mk, v);
    if (bestHook && old !== String(v)) bestHook();
  };

  // ── 포인트
  function ymd(t) { var d = new Date(t); return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2); }
  function load() { var s = jp(PK); if (!s || typeof s !== "object" || !s.p) s = { v: 1, p: {} }; return s; }
  function me() { return player() || "(이 폰)"; }
  var file = location.pathname.split("/").pop() || "index.html";
  function award(kind) {
    if (!GAMES[file]) return null;
    var s = load(), n = me(), u = s.p[n] || (s.p[n] = { total: 0, day: "", lastDay: "", streak: 0, today: {}, bonus: {}, seen: [], log: [] }), now = Date.now(), td = ymd(now), pts = 0, why = [];
    if (u.day !== td) { u.streakNew = true; u.day = td; u.today = {}; u.bonus = {}; }
    var mult = HARD[file] ? CFG.hard : 1;
    if (kind === "play") {
      if ((u.today[file] || 0) >= CFG.perDay) return null;
      u.today[file] = (u.today[file] || 0) + 1; pts += Math.round(CFG.base * mult); why.push("플레이");
      if (u.seen.indexOf(file) < 0) { u.seen.push(file); pts += CFG.first; why.push("처음 해 본 게임"); }
      if (u.streakNew) { var y = ymd(now - 86400000); u.streak = u.lastDay === y ? (u.streak || 0) + 1 : 1; u.lastDay = td; u.streakNew = false; var sb = Math.min(CFG.streakMax, CFG.streakStep * u.streak); pts += sb; why.push(u.streak + "일 연속"); }
    } else {
      if ((u.bonus[file] || 0) >= CFG.perDay) return null;
      u.bonus[file] = (u.bonus[file] || 0) + 1; pts += Math.round((kind === "win" ? CFG.win : CFG.best) * mult); why.push(kind === "win" ? "이겼어요" : "최고 기록");
    }
    delete u.streakNew; u.total += pts; u.log.push({ t: now, f: file, p: pts, w: why.join("·") }); if (u.log.length > CFG.keepLog) u.log.splice(0, u.log.length - CFG.keepLog);
    rs(PK, JSON.stringify(s)); toast("+" + pts + "p  " + why.join("·")); return pts;
  }
  var tq = [], tt = 0;
  function toast(t) {
    tq.push(t); clearTimeout(tt);
    tt = setTimeout(function () {
      var m = tq.join("  /  "); tq = [];
      var d = document.createElement("div"); d.textContent = "⭐ " + m;
      d.style.cssText = "position:fixed;left:50%;bottom:calc(16px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:99997;background:#1c2233;color:#fff;border-radius:999px;padding:8px 16px;font:700 .9rem/1.3 system-ui,sans-serif;box-shadow:0 4px 18px rgba(0,0,0,.35);pointer-events:none;max-width:92vw;text-align:center";
      (document.body || document.documentElement).appendChild(d); setTimeout(function () { d.remove(); }, 2600);
    }, 250);
  }

  window.fgPerson = {
    cfg: CFG, games: GAMES, hard: HARD, pointsKey: PK, playerKey: PLAYER,
    player: player, owner: owner,
    setPlayer: function (n) { rs(PLAYER, n || ""); },
    points: function (n) { var u = load().p[n || me()]; return u ? u.total : 0; },
    all: function () { return load().p; }
  };

  // ── 플레이 감지: 입력이 있고 minSec 초가 지나면 "한 판"으로 친다. 이김 글귀·최고 기록 저장도 감지한다.
  if (!GAMES[file] || window.parent !== window) return;
  var input = 0, t0 = Date.now(), played = false, won = false, bested = false;
  ["pointerdown", "keydown", "touchstart"].forEach(function (ev) { addEventListener(ev, function () { input++; }, { capture: true, passive: true }); });
  setInterval(function () { if (!played && input > 0 && Date.now() - t0 >= CFG.minSec * 1000) { played = true; award("play"); } }, 1000);
  bestHook = function () { if (!bested && input > 0 && Date.now() - t0 >= 3000) { bested = true; setTimeout(function () { ensure(); award("best"); }, 0); } };
  function ensure() { if (!played) { played = true; award("play"); } }
  var OK_RE = /완성했|성공했|성공!|클리어|다 맞혔|모두 맞혔|모두 찾았|모두 맞췄|해냈어요|축하해요|축하합니다|이겼어요|탈출했|탈출 성공/, NG_RE = /컴퓨터가 이겼|컴퓨터 승리|졌어요|게임 ?오버|실패했/;
  function watch() {
    if (!window.MutationObserver) return;
    new MutationObserver(function (ms) {
      if (won || input === 0) return;
      for (var i = 0; i < ms.length && !won; i++) {
        var nodes = ms[i].addedNodes; for (var j = 0; j < nodes.length; j++) {
          var t = (nodes[j].textContent || "").trim(); if (!t || t.length > 300) continue;
          if (NG_RE.test(t) || /컴퓨터/.test(t)) continue;
          if (OK_RE.test(t) || t.indexOf("🎉") === 0) { won = true; ensure(); award("win"); break; }
        }
      }
    }).observe(document.documentElement, { childList: true, subtree: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", watch); else watch();
})();
