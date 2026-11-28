/* 생물 퀴즈 사진(선택, 기본 꺼짐) — 2026-11-28 사용자 요청. 이 파일은 tools/dev/bio_apply.py 가 bio_photo_tpl.js 로 만들어요(직접 고치지 마세요).
   정답이 생물 이름인 문제(MAP: 퀴즈 파일 → {정답: 한국어 위키백과 항목})에서 정답을 고른 뒤에만 사진을 보여 줘요(힌트가 되지 않게).
   MAP 값 = [커먼즈 사진 파일, 위키백과 항목]. 사진은 bio_build.py 가 '찍힌 것(depicts)' 기록으로 그 생물만 찍힌 사진(뼈·화석 제외, 공룡은 복원도)을 고른 것이고,
   폰은 online.js 의 commonsPhoto 로 그 파일만 불러오며 라이선스(공개 도메인·CC0·CC BY·CC BY-SA)를 다시 확인해요.
   사진은 폰·저장소에 저장하지 않고, 사진 아래에 찍은 사람·라이선스·원본 링크를 적어요.
   🌐 온라인을 허락하지 않았으면 「📷 사진 보기」 단추만 보이고, 누르면 한 번 허락을 받아요. 「사진 자동으로 안 보기」는 bio-photo-v1 = "off". */
(function () {
  "use strict";
  var MAP = /*MAP*/{"animal-quiz.html":{"치타":["Male_cheetah_facing_left_in_South_Africa.jpg","치타"],"아프리카코끼리":["178_Male_African_bush_elephant_in_Etosha_National_Park_Photo_by_Giles_Laurent.jpg","아프리카코끼리"],"오리너구리":["Duck-billed_platypus_(Ornithorhynchus_anatinus)_Scottsdale.jpg","오리너구리"],"참새":["Tree_Sparrow_August_2007_Osaka_Japan.jpg","참새"],"올빼미":["Himalayan_Wood_Owl.jpg","올빼미"],"타조":["Struthio_camelus_-_Etosha_2014_(3).jpg","타조"],"박쥐":["Wikipedia-Bats-001-v01.jpg","박쥐"],"흰수염고래":["Anim1754_-_Flickr_-_NOAA_Photo_Library.jpg","대왕고래"],"고래상어":["Whale_shark_Georgia_aquarium.jpg","고래상어"],"거미":["Spiders_Diversity.jpg","거미"],"황제펭귄":["Aptenodytes_forsteri_-Snow_Hill_Island,_Antarctica_-adults_and_juvenile-8.jpg","황제펭귄"],"대나무":["El_bambú_cerca_de_la_quebrada_en_Sector_Santo_Domingo,_Perchas_2,_San_Sebastián,_Puerto_Rico.jpg","대나무"],"유칼립투스":["Starr_031002-0027_Eucalyptus_globulus.jpg","유칼립투스"],"진딧물":["Aphidoidea_fight.jpg","진딧물"],"까마귀":["00_3108_Rabenvogel_(Aaskrähe,_Corvus_corone).jpg","까마귀"],"따오기":["Nipponia_nippon_77371852.jpg","따오기"],"괭이갈매기":["Black-tailed_gull.jpg","괭이갈매기"],"푸들":["Dog_at_Marymoor_Park_(3618929472).jpg","푸들"],"티라노사우루스":["Tyrannosaurus_TD.png","티라노사우루스"],"브라키오사우루스":["Brachiosaurus_TD.png","브라키오사우루스"],"트리케라톱스":["Triceratops_TD.png","트리케라톱스"],"코끼리":["178_Male_African_bush_elephant_in_Etosha_National_Park_Photo_by_Giles_Laurent.jpg","코끼리"],"산양":["Nemorhaedus_caudatus.jpg","산양"],"고양이":["Cat_poster_1.jpg","고양이"],"돼지":["Sow_with_piglet.jpg","돼지"],"판다":["A_Panda_eating.jpg","대왕판다"],"고슴도치":["Erinaceus_amurensis.jpg","고슴도치"],"북극곰":["Polar_Bear_-_Alaska_(cropped).jpg","북극곰"],"반달가슴곰":["Ursus_thibetanus_3_(Wroclaw_zoo).JPG","아시아흑곰"],"무당벌레":["Asian_lady_beetle-(Harmonia-axyridis).jpg","무당벌레"],"개미":["Red_forest_ant_(Formica_rufa)_on_an_alfalfa_flower_(Medicago_sativa).jpg","개미"],"늑대":["Eurasian_wolf_2.jpg","회색늑대"],"제비":["Деревенская_ласточка_(Hirundo_rustica),_Мелихово.jpg","제비"],"말벌":["Hornet-vespa.jpg","말벌"]},"sea-quiz.html":{"흰수염고래":["Anim1754_-_Flickr_-_NOAA_Photo_Library.jpg","대왕고래"],"문어":["Enteroctopus_dolfeini.jpg","문어"],"황새치":["Xiphias_gladius_23056964.jpg","황새치"],"진주조개":["Pinctada_fucata_(Japanese_pearl_oyster)_(Japan).jpg","진주조개"],"고래상어":["Whale_shark_Georgia_aquarium.jpg","고래상어"],"북극곰":["Polar_Bear_-_Alaska_(cropped).jpg","북극곰"],"귀상어":["Sphyrna_zygaena_noaa.jpg","귀상어"],"백상아리":["White_shark.jpg","백상아리"],"만타가오리":["Manta_birostris-Thailand3.jpg","대왕쥐가오리"],"전기가오리":["Naturalis_Biodiversity_Center_-_RMNH.ART.52_-_Narke_japonica_(Temminck_and_Schlegel)_-_Kawahara_Keiga_-_1823_-_1829_-_Siebold_Collection_-_pencil_drawing_-_water_colour.jpeg","전기가오리"],"낙지":["Octopus_minor_by_OpenCage.jpg","낙지"],"고등어":["Scomber_japonicus.png","참고등어"],"아귀":["Lophiomus_setigerus_2.png","아귀"],"초롱아귀":["Himantolophus_groenlandicus_by_OpenCage.jpg","초롱아귀"],"혹등고래":["Humpback_whales_in_singing_position.jpg","혹등고래"],"짱뚱어":["Mutsugoroh0809.jpg","짱뚱어"],"파랑돔":["Neon_damselfish.jpg","파랑돔"]},"insect-quiz.html":{"사마귀":["Tenodera_angustipennis_Saussure(Pregnant)_DSCN9575.jpg","사마귀"],"개미":["Red_forest_ant_(Formica_rufa)_on_an_alfalfa_flower_(Medicago_sativa).jpg","개미"],"장수풍뎅이":["Kabutomushi-JapaneseBeetle-July2004.jpg","장수풍뎅이"],"무당벌레":["Asian_lady_beetle-(Harmonia-axyridis).jpg","무당벌레"],"누에":["Silkworms3000px.jpg","누에나방"],"거미":["Spiders_Diversity.jpg","거미"],"쇠똥구리":["Gymnopleurus_mopsus.jpg","소똥구리"],"배추흰나비":["Pieris_rapae_male.jpg","배추흰나비"],"호랑나비":["Papilio_xuthus_070707.jpg","호랑나비"],"제왕나비":["Monarch_butterfly_in_Grand_Canary.jpg","제왕나비"],"사슴벌레":["Lucanus_maculifemoratus_maculifemoratus_sjh.jpg","사슴벌레"],"장수하늘소":["Callipogon_relictus_female_84_mm.JPG","장수하늘소"],"말벌":["Hornet-vespa.jpg","말벌"],"칠성무당벌레":["BIEDRONA.JPG","칠성무당벌레"],"노래기":["Millipede_coiled_on_the_ground.jpg","노래기강"],"참매미":["Cicada_seoul.jpg","참매미"],"지렁이":["Earthworm.jpg","지렁이"],"베짱이":["Grasshopper_on_the_stairs_-_2.jpg","베짱이"],"여치":["Korean_Katydid.jpeg","여치"],"고추잠자리":["Crocothemis_servilia_male_by_kadavoor.jpg","고추잠자리"],"방아깨비":["Acrida_cinerea_Kyoto_03.jpg","방아깨비"],"파리지옥":["Venus_Flytrap_showing_trigger_hairs.jpg","파리지옥"],"버마재비":["Tenodera_angustipennis_Saussure(Pregnant)_DSCN9575.jpg","사마귀"],"말매미":["Cryptotympana_facialis1.jpg","말매미"],"쓰름매미":["Meimuna_mongolica.jpg","쓰름매미"],"장수잠자리":["Anotogaster_sieboldii_(male_s8).jpg","장수잠자리"]},"plant-quiz.html":{"개나리":["Forsythia_koreana.jpg","개나리"],"진달래":["Rhododendron_mucronulatum_-_Copenhagen_Botanical_Garden_-_DSC07477.JPG","진달래"],"해바라기":["Sunflower_sky_backdrop.jpg","해바라기"],"무궁화":["Hibiscus_syriacus_chinensis_RHS.jpeg","무궁화"],"단풍나무":["Portland_Japanese_Garden_maple.jpg","단풍나무"],"은행나무":["GINKGOBAUM-2.jpg","은행나무"],"감자":["Solanales_-_Solanum_tuberosum_-_3.jpg","감자"],"상추":["Iceberg_lettuce_in_SB.jpg","상추"],"연꽃":["Sacred_lotus_Nelumbo_nucifera.jpg","연꽃"],"창포":["Acorus_calamus1.jpg","창포"],"밤나무":["Castanea_crenata3.jpg","밤나무"],"파리지옥":["Venus_Flytrap_showing_trigger_hairs.jpg","파리지옥"],"끈끈이주걱":["Drosera-rotundifolia.jpg","끈끈이주걱"],"나팔꽃":["Ipomoea_nil_Akatsukinoumi1.jpg","나팔꽃"],"개구리밥":["Spirodela_polyrrhiza_marais_poitevin.jpg","개구리밥"],"국화":["Chrysanthemum_×_morifolium_flowers.jpg","국화 (식물)"],"매화":["Prunus_mume.JPG","매실나무"],"튤립":["Tulipa_suaveolens_floriade_to_Canberra.jpg","튤립"],"강아지풀":["Groene_naaldaar_aarpluim_(Setaria_viridis).jpg","강아지풀"],"억새":["Japanese_pampas_grass_ススキの穂波PB080105.jpg","참억새"],"지렁이":["Earthworm.jpg","지렁이"],"감나무":["Kaki_20041002.jpg","감나무"],"도깨비바늘":["Bidens_bipinnata_3_4x3.jpg","도깨비바늘"],"봉선화":["Impatiens_balsamina_Blanco_clean.jpg","봉선화"],"동백나무":["Camellia_japonica_var._decumbens_3.JPG","동백나무"],"할미꽃":["Pulsatilla_koreana.JPG","할미꽃"],"카카오나무":["Theobroma_cacao_-_Köhler–s_Medizinal-Pflanzen-136.jpg","카카오"],"올리브나무":["Olive-tree-fruit-august-0.jpg","올리브나무"],"차나무":["Csinensis.jpg","차나무"],"복수초":["Adonis_amurensis_2010.jpg","복수초"],"모시풀":["Boehmeria_nivea_1.jpg","모시풀"],"닥나무":["Broussonetia_kazinoki_1.JPG","닥나무"]},"dino-quiz.html":{"티라노사우루스":["Tyrannosaurus_TD.png","티라노사우루스"],"트리케라톱스":["Triceratops_TD.png","트리케라톱스"],"스테고사우루스":["Stegosaurus_stenops_Life_Reconstruction_(flipped).png","스테고사우루스"],"브라키오사우루스":["Brachiosaurus_TD.png","브라키오사우루스"],"안킬로사우루스":["Ankylosaurus_TD.png","안킬로사우루스"],"벨로키랍토르":["Velociraptor_TD.png","벨로키랍토르"],"프테라노돈":["Pteranodon_TD.png","프테라노돈"],"플레시오사우루스":["Plesiosaurus_3DB.jpg","플레시오사우루스"],"오비랍토르":["Oviraptor_TD.png","오비랍토르"],"파키케팔로사우루스":["Pachycephalosaurus_Reconstruction.jpg","파키케팔로사우루스"],"하드로사우루스":["Hadrosaurus_TD.png","하드로사우루스"],"마이아사우라":["Maiasaura_TD.png","마이아사우라"],"이구아노돈":["Iguanodon_paleoart_2025.png","이구아노돈"],"스피노사우루스":["Spinosaurus_mirabilis.png","스피노사우루스"],"콤프소그나투스":["Compsognathus_TD.png","콤프소그나투스"],"티라노사우루스 렉스":["Tyrannosaurus_TD.png","티라노사우루스"],"케찰코아틀루스":["Quetzalcoatlus_lawsoni.png","케찰코아틀루스"],"시노사우롭테릭스":["Sinosauropteryx_lingyuanensis.png","시노사우롭테릭스"],"알로사우루스":["Allosaurus_anax.png","알로사우루스"],"디플로도쿠스":["Diplodocus_longus(2).jpg","디플로도쿠스"],"은행나무":["GINKGOBAUM-2.jpg","은행나무"]}}/*/MAP*/;
  var file = (location.pathname.split("/").pop() || "").replace(/\?.*$/, ""), M = MAP[file];
  if (!M || typeof window.pick !== "function" || !window.fgOnline) return;
  var PK = "bio-photo-v1";
  function get() { try { return localStorage.getItem(PK); } catch (e) { return null; } }
  function set(v) { try { if (v) localStorage.setItem(PK, v); else localStorage.removeItem(PK); } catch (e) {} }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  /* 사진 크게 보기(2026-11-28 사용자 요청): 사진을 누르면 화면 전체에 크게. 작은 그림을 먼저 보이고 큰 그림(폭 1280)을 받으면 바꿔요. 화면·✕를 누르거나 뒤로 가기로 닫혀요. */
  function fgZoom(small, file, cap) {
    var o = document.createElement("div"); o.className = "fgzoom"; o.setAttribute("role", "dialog"); o.setAttribute("aria-label", "사진 크게 보기");
    o.innerHTML = '<button type="button" class="fgzx" aria-label="닫기">✕</button><img alt=""><p></p>';
    var im = o.querySelector("img"); im.src = small; im.alt = cap || ""; o.querySelector("p").textContent = cap || "";
    if (file) { var big = new Image(); big.referrerPolicy = "no-referrer"; big.onload = function () { im.src = big.src; }; big.src = "https://commons.wikimedia.org/wiki/Special:FilePath/" + encodeURIComponent(file) + "?width=1280"; }
    var closed = false;
    function close(fromBack) { if (closed) return; closed = true; o.remove(); window.removeEventListener("popstate", onPop); if (!fromBack) try { history.back(); } catch (e) {} }
    function onPop() { close(true); }
    o.addEventListener("click", function () { close(false); });
    document.body.appendChild(o);
    try { history.pushState({ fgzoom: 1 }, ""); } catch (e) {}
    window.addEventListener("popstate", onPop);
  }
  
  var st = document.createElement("style");
  st.textContent = ".biop{display:block;margin:10px auto 0;text-align:center;font-size:.8rem;line-height:1.45}.biop img{display:block;max-width:100%;max-height:170px;margin:0 auto 4px;border-radius:10px;object-fit:contain;background:rgba(127,127,127,.12)}.biop .cap{opacity:.8;word-break:break-all}.biop a{color:inherit}.biop button{font:inherit;font-size:.85rem;padding:6px 12px;border-radius:999px;border:1px solid rgba(127,127,127,.45);background:transparent;color:inherit;cursor:pointer}.biop img{cursor:zoom-in}.fgzoom{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.92);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:12px;cursor:zoom-out}.fgzoom img{max-width:100%;max-height:calc(100% - 48px);object-fit:contain}.fgzoom p{color:#fff;margin:8px 0 0;font-size:.9rem;text-align:center}.fgzoom .fgzx{position:absolute;top:10px;right:10px;width:44px;height:44px;border-radius:50%;border:0;background:rgba(255,255,255,.2);color:#fff;font-size:1.3rem;cursor:pointer}.biop .off{margin-top:4px;font-size:.75rem;opacity:.7;border:0;padding:2px 6px;text-decoration:underline}";
  document.head.appendChild(st);
  var wikiUrl = function (t) { return "https://ko.wikipedia.org/wiki/" + encodeURIComponent(t.replace(/ /g, "_")); };
  function load(box, name, ent, token) {
    var file = ent[0], title = ent[1];
    box.innerHTML = "📷 " + esc(name) + " 사진을 불러오는 중…";
    window.fgOnline.commonsPhoto([file], true).then(function (r) {
      if (token !== cur || !box.isConnected) return;   // 그사이 다음 문제로 넘어갔으면 그리지 않아요
      if (!r) { box.innerHTML = '📷 사진을 찾지 못했어요 · <a href="' + wikiUrl(title) + '" target="_blank" rel="noopener">🔗 위키백과에서 보기</a>'; return; }
      var lic = r.licenseUrl ? '<a href="' + esc(r.licenseUrl) + '" target="_blank" rel="noopener">' + esc(r.license) + "</a>" : esc(r.license);
      box.innerHTML = '<img alt="' + esc(name) + ' 사진" loading="lazy" referrerpolicy="no-referrer" src="' + esc(r.src) + '">' +
        '<span class="cap">📷 ' + esc(name) + (r.artist ? " · 사진: " + esc(r.artist.slice(0, 60)) : "") + " · " + lic +
        ' · <a href="' + esc(r.filePage || r.page) + '" target="_blank" rel="noopener">원본</a> · <a href="' + wikiUrl(title) + '" target="_blank" rel="noopener">위키백과</a></span>' +
        '<button type="button" class="off">사진 자동으로 안 보기</button>';
      var img = box.querySelector("img"); img.onerror = function () { img.remove(); }; img.onclick = function () { fgZoom(img.src, file, "📷 " + name); };
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
