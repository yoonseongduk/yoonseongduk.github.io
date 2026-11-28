/* 생물 퀴즈 사진(선택, 기본 꺼짐) — 2026-11-28 사용자 요청. 이 파일은 tools/dev/bio_apply.py 가 bio_photo_tpl.js 로 만들어요(직접 고치지 마세요).
   정답이 생물 이름인 문제(MAP: 퀴즈 파일 → {정답: 한국어 위키백과 항목})에서 정답을 고른 뒤에만 사진을 보여 줘요(힌트가 되지 않게).
   사진은 위키백과 항목의 대표 사진만, 항목 내용에 그 이름이 있고 라이선스가 공개 도메인·CC0·CC BY·CC BY-SA일 때만(online.js 의 wikiImage, cc:true).
   사진은 폰·저장소에 저장하지 않고, 사진 아래에 찍은 사람·라이선스·원본 링크를 적어요.
   🌐 온라인을 허락하지 않았으면 「📷 사진 보기」 단추만 보이고, 누르면 한 번 허락을 받아요. 「사진 자동으로 안 보기」는 bio-photo-v1 = "off". */
(function () {
  "use strict";
  var MAP = /*MAP*/{"animal-quiz.html":{"치타":"치타","아프리카코끼리":"아프리카코끼리","기린":"기린","오리너구리":"오리너구리","참새":"참새","돌고래":"돌고래","캥거루":"캥거루","개구리":"개구리목","토끼":"토끼","올빼미":"올빼미","타조":"타조","박쥐":"박쥐","흰수염고래":"대왕고래","고래상어":"고래상어","거미류":"거미강","거미":"거미","동물":"동물","카멜레온":"카멜레온","파충류":"파충류","양서류":"양서류","황제펭귄":"황제펭귄","벌레":"벌레","암컷":"암컷","대나무":"대나무","유칼립투스":"유칼립투스","나무늘보":"나무늘보","돌고래과":"참돌고래과","포유류":"포유류","진딧물":"진딧물","복어":"복어","까마귀":"까마귀","앵무새":"앵무새","따오기":"따오기","괭이갈매기":"괭이갈매기","조랑말":"조랑말","푸들":"푸들","거북":"거북","티라노사우루스":"티라노사우루스","브라키오사우루스":"브라키오사우루스","트리케라톱스":"트리케라톱스","코끼리":"코끼리","벌새":"벌새","구관조":"구관조","산양":"산양","고양이":"고양이","돼지":"돼지","오리":"오리","판다":"대왕판다","원숭이":"원숭이","고슴도치":"고슴도치","물고기":"물고기","송아지":"송아지","북극곰":"북극곰","반달가슴곰":"아시아흑곰","오징어":"오징어","해파리":"해파리","꿀벌":"꿀벌","반딧불이":"반딧불이과","귀뚜라미":"귀뚜라미과","매미":"매미","무당벌레":"무당벌레","개미":"개미","늑대":"회색늑대","제비":"제비","전갈":"전갈목","일벌":"일벌","말벌":"말벌","상어":"상어"},"sea-quiz.html":{"흰수염고래":"대왕고래","문어":"문어","오징어":"오징어","성게":"성게류","해마":"해마 (동물)","복어":"복어","해파리":"해파리","황새치":"황새치","진주조개":"진주조개","고래":"고래","고래상어":"고래상어","가오리":"가오리","멸치":"멸치과","북극곰":"북극곰","포유류":"포유류","동물":"동물","물개":"물개","귀상어":"귀상어","백상아리":"백상아리","만타가오리":"대왕쥐가오리","전기가오리":"전기가오리","말미잘":"말미잘","낙지":"낙지","이매패류":"이매패류","복족류":"복족류","두족류":"두족류","갑각류":"갑각류","소라게":"소라게","크릴":"크릴","따개비":"따개비","날치":"날치","고등어":"참고등어","아귀":"아귀","초롱아귀":"초롱아귀","향유고래":"향고래","혹등고래":"혹등고래","물고기":"물고기","상어":"상어","조개":"조개","식물성 플랑크톤":"식물성 플랑크톤","바닷물고기":"바닷물고기","짱뚱어":"짱뚱어","민부리고래":"민부리고래","투구게":"투구게과","장수거북":"장수거북","상괭이":"상괭이","파랑돔":"파랑돔"},"insect-quiz.html":{"곤충":"곤충","꿀벌":"꿀벌","반딧불이":"반딧불이과","매미":"매미","귀뚜라미":"귀뚜라미과","나비":"나비","사마귀":"사마귀","개미":"개미","장수풍뎅이":"장수풍뎅이","무당벌레":"무당벌레","모기":"모기","잠자리":"잠자리","메뚜기":"메뚜기","누에":"누에나방","거미":"거미","소금쟁이":"소금쟁이","쇠똥구리":"소똥구리","하루살이":"하루살이목","나방":"나방","구더기":"구더기","암컷":"암컷","배추흰나비":"배추흰나비","호랑나비":"호랑나비","제왕나비":"제왕나비","사슴벌레":"사슴벌레","하늘소":"하늘소","장수하늘소":"장수하늘소","물방개":"물방개","송장헤엄치개":"송장헤엄치게","여왕벌":"여왕벌","일벌":"일벌","말벌":"말벌","대벌레":"대벌레","칠성무당벌레":"칠성무당벌레","지네":"순각류","진드기":"진드기","노래기":"노래기강","참매미":"참매미","파리":"파리 (곤충)","지렁이":"지렁이","바퀴벌레":"바퀴벌레","베짱이":"베짱이","여치":"여치","고추잠자리":"고추잠자리","수벌":"수벌","개똥벌레":"반딧불이과","방아깨비":"방아깨비","노린재":"노린재과","파리지옥":"파리지옥","버마재비":"사마귀","물장군":"물장군","말매미":"말매미","쓰름매미":"쓰름매미","갈색거저리":"갈색거저리","벌목":"벌목 (곤충)","나비목":"나비목","파리목":"파리목","몰포나비":"모르포나비","어른벌레":"어른벌레","장수잠자리":"장수잠자리","흰개미":"흰개미"},"plant-quiz.html":{"개나리":"개나리","진달래":"진달래","해바라기":"해바라기","무궁화":"무궁화","장미":"장미","단풍나무":"단풍나무","은행나무":"은행나무","소나무":"소나무","감자":"감자","당근":"당근","상추":"상추","민들레":"민들레","연꽃":"연꽃","창포":"창포","고사리":"고사리","이끼":"이끼","밤나무":"밤나무","참나무":"참나무속","벚나무":"벚나무아속","바오바브나무":"바오밥나무속","야자나무":"종려과","나무":"나무","파리지옥":"파리지옥","끈끈이주걱":"끈끈이주걱","나팔꽃":"나팔꽃","달맞이꽃":"달맞이꽃속","개구리밥":"개구리밥","국화":"국화 (식물)","매화":"매실나무","튤립":"튤립","강아지풀":"강아지풀","억새":"참억새","지렁이":"지렁이","사과나무":"사과나무","감나무":"감나무","귤나무":"감귤나무","도깨비바늘":"도깨비바늘","봉선화":"봉선화","부레옥잠":"부레옥잠","동백나무":"동백나무","할미꽃":"할미꽃","카카오나무":"카카오","올리브나무":"올리브나무","차나무":"차나무","겉씨식물":"겉씨식물","자작나무":"자작나무","라플레시아":"라플레시아","복수초":"복수초","장미과":"장미과","뿌리혹박테리아":"뿌리혹박테리아","가지과":"가지과","모시풀":"모시풀","닥나무":"닥나무"},"dino-quiz.html":{"티라노사우루스":"티라노사우루스","트리케라톱스":"트리케라톱스","스테고사우루스":"스테고사우루스","브라키오사우루스":"브라키오사우루스","안킬로사우루스":"안킬로사우루스","벨로키랍토르":"벨로키랍토르","프테라노돈":"프테라노돈","플레시오사우루스":"플레시오사우루스","용각류":"용각하목","매머드":"매머드","용반류":"용반목","조반류":"조반목","수각류":"수각류","각룡류":"각룡류","오비랍토르":"오비랍토르","파키케팔로사우루스":"파키케팔로사우루스","하드로사우루스":"하드로사우루스","마이아사우라":"마이아사우라","이구아노돈":"이구아노돈","물고기":"물고기","스피노사우루스":"스피노사우루스","익룡":"익룡","도마뱀":"도마뱀아목","콤프소그나투스":"콤프소그나투스","암모나이트":"암모나이트","티라노사우루스 렉스":"티라노사우루스","육식 공룡":"수각류","케찰코아틀루스":"케찰코아틀루스","시노사우롭테릭스":"시노사우롭테릭스","알로사우루스":"알로사우루스","디플로도쿠스":"디플로도쿠스","은행나무":"은행나무"}}/*/MAP*/;
  var file = (location.pathname.split("/").pop() || "").replace(/\?.*$/, ""), M = MAP[file];
  if (!M || typeof window.pick !== "function" || !window.fgOnline) return;
  var PK = "bio-photo-v1";
  function get() { try { return localStorage.getItem(PK); } catch (e) { return null; } }
  function set(v) { try { if (v) localStorage.setItem(PK, v); else localStorage.removeItem(PK); } catch (e) {} }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  var st = document.createElement("style");
  st.textContent = ".biop{display:block;margin:10px auto 0;text-align:center;font-size:.8rem;line-height:1.45}.biop img{display:block;max-width:100%;max-height:170px;margin:0 auto 4px;border-radius:10px;object-fit:contain;background:rgba(127,127,127,.12)}.biop .cap{opacity:.8;word-break:break-all}.biop a{color:inherit}.biop button{font:inherit;font-size:.85rem;padding:6px 12px;border-radius:999px;border:1px solid rgba(127,127,127,.45);background:transparent;color:inherit;cursor:pointer}.biop .off{margin-top:4px;font-size:.75rem;opacity:.7;border:0;padding:2px 6px;text-decoration:underline}";
  document.head.appendChild(st);
  var wikiUrl = function (t) { return "https://ko.wikipedia.org/wiki/" + encodeURIComponent(t.replace(/ /g, "_")); };
  function load(box, name, title, token) {
    box.innerHTML = "📷 " + esc(name) + " 사진을 불러오는 중…";
    window.fgOnline.wikiImage(["ko:" + title], [name, title.replace(/ \(.*\)$/, "")], "생물", { cc: true, nofb: true }).then(function (r) {
      if (token !== cur || !box.isConnected) return;   // 그사이 다음 문제로 넘어갔으면 그리지 않아요
      if (!r) { box.innerHTML = '📷 사진을 찾지 못했어요 · <a href="' + wikiUrl(title) + '" target="_blank" rel="noopener">🔗 위키백과에서 보기</a>'; return; }
      var lic = r.licenseUrl ? '<a href="' + esc(r.licenseUrl) + '" target="_blank" rel="noopener">' + esc(r.license) + "</a>" : esc(r.license);
      box.innerHTML = '<img alt="' + esc(name) + ' 사진" loading="lazy" referrerpolicy="no-referrer" src="' + esc(r.src) + '">' +
        '<span class="cap">📷 ' + esc(name) + (r.artist ? " · 사진: " + esc(r.artist.slice(0, 60)) : "") + " · " + lic +
        ' · <a href="' + esc(r.filePage || r.page) + '" target="_blank" rel="noopener">원본</a> · <a href="' + esc(r.page) + '" target="_blank" rel="noopener">위키백과</a></span>' +
        '<button type="button" class="off">사진 자동으로 안 보기</button>';
      var img = box.querySelector("img"); img.onerror = function () { img.remove(); };
      box.querySelector(".off").onclick = function () { set("off"); button(box, name, title, token); };
    });
  }
  function button(box, name, title, token) {
    box.innerHTML = '<button type="button">📷 ' + esc(name) + " 사진 보기 🌐</button>";
    box.querySelector("button").onclick = function () {
      if (!window.fgOnline.ask("생물 사진을 위키백과(위키미디어 서버)에서 불러와요.\n인터넷을 쓰고, 사진은 폰에 저장하지 않아요. 사진 아래에 찍은 사람과 라이선스를 적어요.\n계속할까요?")) return;
      set(""); load(box, name, title, token);
    };
  }
  var cur = 0, op = window.pick, os = window.show;
  if (typeof os === "function") window.show = function () { cur++; document.querySelectorAll(".biop").forEach(function (x) { x.remove(); }); return os.apply(this, arguments); };   // 다음 문제로 가면 사진을 치워요
  if (typeof window.finish === "function") { var of = window.finish; window.finish = function () { cur++; document.querySelectorAll(".biop").forEach(function (x) { x.remove(); }); return of.apply(this, arguments); }; }
  window.pick = function (k) {
    var was = typeof locked !== "undefined" && locked;   // 이미 답한 문제를 또 누르면 아무것도 안 해요
    var r = op.apply(this, arguments);
    try {
      if (was) return r;
      var d = qs[i].d, name = String(d[1]), title = M[name], o = document.getElementById("opts"); if (!title || !o) return r;
      var box = document.createElement("div"); box.className = "biop"; o.parentNode.insertBefore(box, o.nextSibling); var token = ++cur;   // 보기 아래(문제·보기를 밀어내지 않게)
      if (window.fgOnline.on() && get() !== "off") load(box, name, title, token); else button(box, name, title, token);
    } catch (e) {}
    return r;
  };
})();
