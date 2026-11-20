/* 카드·화투 놀이(모의 도박풍 게임) 보이기/숨기기 — 시작 화면·같이 하기 목록이 함께 쓰는 공용 스크립트.
   켜짐/꺼짐은 이 폰에 저장해요(localStorage "fg-casino-v1": "0"이면 숨김, 없으면 보임).
   게임 목록(FILES)은 여기 한 곳에서만 고쳐요. 새 모의 도박풍 게임을 만들면 FILES에 넣고, 시작 화면 분류는 "casino"로 해요.
   (스토어에 앱 2개로 나눠 등록할 때는 여기에 모드를 추가하면 돼요 — playstore/README_플레이스토어_준비.md 6번) */
(function () {
  if (window.fgCasino) return;
  var K = "fg-casino-v1";
  var FILES = { "blackjack.html": 1, "go-stop.html": 1, "high-low.html": 1, "poker-draw.html": 1, "lotto-picker.html": 1,
                "net-21.html": 1, "net-poker.html": 1, "net-hula.html": 1, "net-gostop.html": 1 };
  function on() { try { return window.localStorage.getItem(K) !== "0"; } catch (e) { return true; } }
  window.fgCasino = {
    files: FILES, on: on,
    set: function (b) { try { window.localStorage.setItem(K, b ? "1" : "0"); } catch (e) {} },
    hidden: function (f) { return !!FILES[f] && !on(); },
    show: function (f) { return !(FILES[f] && !on()); }
  };
})();
