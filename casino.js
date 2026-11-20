/* 카드·화투 놀이(모의 도박풍 게임) 보이기/숨기기와 스토어 앱 2개 구분 — 시작 화면·같이 하기 목록이 함께 쓰는 공용 스크립트.
   · 웹사이트(web): 켜짐/꺼짐을 이 폰에 저장(localStorage "fg-casino-v1": "0"이면 숨김, 없으면 보임).
   · 스토어 앱 2개(같은 사이트, 시작 주소만 다름 — sessionStorage "fg-appmode-v1"에 그 사용 동안 저장):
       주소에 ?app=store → family 모드: 카드·화투 놀이를 항상 숨기고 켜기 단추도 없음(깨끗한 가족 앱).
       주소에 ?app=cards → cards 모드: 카드·화투 놀이만 보여 줌(카드·화투 앱).
       주소에 표시가 없어도 처음 열 때 referrer 가 android-app:// 이면 family 로 봐요.
   · 게임 목록(FILES)은 여기 한 곳에서만 고쳐요. 새 모의 도박풍 게임을 만들면 FILES에 넣고, 시작 화면 분류는 "casino"로 해요. */
(function () {
  if (window.fgCasino) return;
  var K = "fg-casino-v1", KM = "fg-appmode-v1";
  var FILES = { "blackjack.html": 1, "go-stop.html": 1, "high-low.html": 1, "poker-draw.html": 1, "lotto-picker.html": 1,
                "net-21.html": 1, "net-poker.html": 1, "net-hula.html": 1, "net-gostop.html": 1 };
  function get(s, k) { try { return s.getItem(k); } catch (e) { return null; } }
  function put(s, k, v) { try { s.setItem(k, v); } catch (e) {} }
  var ss = null; try { ss = window.sessionStorage; } catch (e) {}
  try {
    if (ss) {
      var q = location.search;
      if (/[?&]app=cards\b/.test(q)) put(ss, KM, "cards");
      else if (/[?&]app=store\b/.test(q) || (!get(ss, KM) && (document.referrer || "").indexOf("android-app://") === 0)) put(ss, KM, "family");
    }
  } catch (e) {}
  function mode() { var m = ss && get(ss, KM); return m === "cards" || m === "family" ? m : "web"; }
  function on() { var m = mode(); if (m === "family") return false; if (m === "cards") return true; return get(window.localStorage, K) !== "0"; }
  window.fgCasino = {
    files: FILES, mode: mode, on: on,
    inApp: function () { return mode() !== "web"; },
    set: function (b) { put(window.localStorage, K, b ? "1" : "0"); },
    hidden: function (f) { return !!FILES[f] && !on(); },
    // 이 게임을 목록에 보여 줄까요? (cards 모드에서는 카드·화투 놀이만, 그 밖에는 켜짐 상태에 따라)
    show: function (f) { return mode() === "cards" ? !!FILES[f] : !(FILES[f] && !on()); },
    // family 모드에서 카드·화투 놀이 화면을 바로 열면 시작 화면으로 돌려보내요(해당 게임 화면 맨 위에서 호출)
    guard: function () { if (mode() === "family" && FILES[location.pathname.split("/").pop()]) location.replace("index.html"); }
  };
})();
