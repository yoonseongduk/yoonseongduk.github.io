/* 온라인 기능 공통 틀 (선택 사항). 이 앱은 기본이 오프라인 전용이고, 사용자가 허락한 기능만 인터넷을 써요.
   - fgOnline.on()          : 사용자가 온라인 기능을 허락했는지(기본 false)
   - fgOnline.ask(문구)     : 처음 한 번 설명을 보여 주고 허락을 받아요(예/아니오). 허락하면 localStorage `fg-online-v1`="1"
   - fgOnline.off()         : 허락을 거둬요
   - fgOnline.json(url)     : 시간 제한(8초)이 있는 JSON 요청. 실패하면 null (오프라인이면 요청하지 않아요)
   - fgOnline.wikiImage(...) : 위키백과 항목의 대표 그림 주소를 찾고, ① 항목이 그 작품·작가가 맞는지 ② 그림이 공개 도메인인지 확인해서 통과한 것만 돌려줘요
   새 온라인 기능은 이 틀의 on()을 먼저 확인하세요. 스토어 등록판에서 온라인 기능을 끄려면 ENABLED 를 false 로 바꾸면 돼요(playstore/스토어_관련_기록.md 참고). */
(function () {
  "use strict";
  var ENABLED = true, KEY = "fg-online-v1", CK = "fg-online-cache-v1";
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  var cache = {}; try { cache = JSON.parse(get(CK) || "{}") || {}; } catch (e) { cache = {}; }
  function saveCache() { var ks = Object.keys(cache); if (ks.length > 400) ks.slice(0, ks.length - 400).forEach(function (k) { delete cache[k]; }); set(CK, JSON.stringify(cache)); }
  // 위키 서버가 "요청이 너무 많다"(429·503)고 하면 잠깐 기다렸다가 최대 3번 다시 시도해요
  function json(url, ms, tries) {
    if (!ENABLED || navigator.onLine === false) return Promise.resolve(null);
    tries = tries === undefined ? 3 : tries;
    var ctl = typeof AbortController === "function" ? new AbortController() : null, t = ctl ? setTimeout(function () { ctl.abort(); }, ms || 12000) : null;
    return fetch(url, { signal: ctl ? ctl.signal : undefined, credentials: "omit", referrerPolicy: "no-referrer" })
      .then(function (r) {
        if (t) clearTimeout(t);
        if ((r.status === 429 || r.status === 503) && tries > 0) { var ra = parseInt(r.headers.get("retry-after"), 10); var wait = (isNaN(ra) ? 6 : Math.min(ra, 20)) * 1000 + Math.random() * 800; return new Promise(function (res) { setTimeout(res, wait); }).then(function () { return json(url, ms, tries - 1); }); }
        return r.ok ? r.json() : null;
      }).catch(function () { if (t) clearTimeout(t); return null; });
  }
  // 허용된 그림 파일 주소만(위키미디어 서버)
  // 위키백과 요약은 그림 주소를 thumb.wikimedia.org(+?utm_…)로 줘요. 같은 경로를 upload.wikimedia.org 에서 꼬리표 없이 받아요.
  function okImg(u) { return typeof u === "string" && /^https:\/\/(upload|thumb)\.wikimedia\.org\//.test(u); }
  function okMuseum(u) { return typeof u === "string" && /^https:\/\/(www\.artic\.edu\/iiif\/|openaccess-cdn\.clevelandart\.org\/)/.test(u); }
  function imgUrl(u) { return okImg(u) ? u.replace(/^https:\/\/thumb\.wikimedia\.org\//, "https://upload.wikimedia.org/").replace(/\?.*$/, "") : null; }
  function fileOf(u) { var m = /\/commons\/(?:thumb\/)?[0-9a-f]\/[0-9a-f]{2}\/([^\/]+)/.exec(u || ""); return m ? decodeURIComponent(m[1]) : null; }
  var PD = /public domain|^pd\b|^pd-|cc0|cc-zero/i;
  var CCOK = /^cc[ -]by(?:[ -]sa)?[ -][\d.]+/i;   // CC BY·CC BY-SA(저작자·라이선스 표시가 필요, 비영리·변경금지 제한은 제외)
  function okLic(lic, cc) { return !!lic && (PD.test(lic) || (!!cc && CCOK.test(lic))); }
  function plain(h) { return String(h || "").replace(/<[^>]*>/g, " ").replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/\s+/g, " ").trim().slice(0, 80); }
  function norm(t) { return String(t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase(); }   // 악센트·대소문자를 맞춰서 비교(Cézanne = cezanne)
  // ── 대체 출처(Plan B·C): 위키백과 항목에 그림이 없거나 공개 도메인 표시가 없을 때 차례로 시도해요. 모두 작가 이름 확인 + 공개 도메인·CC0 표시 확인을 거쳐요.
  function words(t) { return String(t || "").replace(/_/g, " ").replace(/[^\p{L}\p{N} ]/gu, " ").split(/\s+/).filter(function (w) { return w.length > 2 && ["the", "and", "with", "von", "van", "del", "della", "des", "les"].indexOf(w.toLowerCase()) < 0; }); }
  var NOTSAME = /\b(study|studies|sketch|drawing|print|etching|copy|after|detail|fragment|variant|replica|miniature)\b/i;   // 습작·스케치·판화·모사작은 같은 작품이 아니라서 거르기
  function sameTitle(a, b) { if (NOTSAME.test(b) && !NOTSAME.test(a)) return false; return sameTitle0(a, b); }
  function sameTitle0(a, b) {   // 두 제목의 낱말이 많이 겹치면 같은 작품으로 봐요(출처마다 영어 제목이 조금씩 달라서): 짧은 쪽 낱말의 75% 이상, 최소 2개
    var wa = words(norm(a)), wb = words(norm(b)); if (!wa.length || !wb.length) return false;
    var short = wa.length <= wb.length ? wa : wb, long = (wa.length <= wb.length ? wb : wa).join(" ");
    var hit = short.filter(function (w) { return long.indexOf(w) >= 0; }).length;
    return hit >= Math.min(2, short.length) && hit / short.length >= 0.75;
  }
  function hasTok(text, toks) { var t = norm(text); return (toks || []).some(function (k) { return k && t.indexOf(norm(k)) >= 0; }); }
  var KINDRE = { "그림": /painting|oil|tempera|panel|canvas/i, "벽화": /mural|fresco|painting/i, "서화": /painting|scroll|ink/i, "판화": /print|etching|woodcut|engraving/i, "드로잉": /drawing/i, "조각": /sculpture/i };
  function kindOk(kind, type) { return !kind || !KINDRE[kind] || KINDRE[kind].test(String(type || "")); }   // 작품 종류(그림·판화·조각…)가 같아야 같은 작품으로 봐요
  function srcCommons(en, toks, kind, cc) {   // B: 위키미디어 커먼즈 그림 파일 직접 검색
    return json("https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&generator=search&gsrnamespace=6&gsrlimit=8&gsrsearch=" + encodeURIComponent(en + " painting filetype:bitmap") + "&prop=imageinfo&iiprop=extmetadata|url&iiurlwidth=330").then(function (d) {
      var pages = (d && d.query && d.query.pages) || {}, ks = Object.keys(pages).sort(function (a, b) { return (pages[a].index || 0) - (pages[b].index || 0); });
      for (var i = 0; i < ks.length; i++) {
        var p = pages[ks[i]], ii = p.imageinfo && p.imageinfo[0]; if (!ii || !okImg(ii.thumburl)) continue;
        var md = ii.extmetadata || {}, lic = md.LicenseShortName && md.LicenseShortName.value, who = ((md.Artist && md.Artist.value) || "") + " " + ((md.ObjectName && md.ObjectName.value) || "") + " " + ((md.ImageDescription && md.ImageDescription.value) || "") + " " + p.title;
        var tt = kind === "악기" ? p.title : p.title + " " + who;   // 악기 사진은 파일 이름에 악기 이름이 있어야 해요(설명문만 맞는 엉뚱한 그림을 막아요)
        if (!okLic(lic, cc) || !sameTitle(en, tt) || (kind !== "악기" && !hasTok(who, toks)) || (kind === "악기" && !hasTok(p.title, toks))) continue;
        return { src: imgUrl(ii.thumburl), page: ii.descriptionurl, title: p.title.replace(/^File:/, ""), license: lic, label: "위키미디어 커먼즈", artist: plain(md.Artist && md.Artist.value), licenseUrl: md.LicenseUrl && md.LicenseUrl.value };
      }
      return null;
    });
  }
  function srcCMA(en, toks, kind) {   // D: 클리블랜드 미술관(CC0 표시)
    return json("https://openaccess-api.clevelandart.org/api/artworks/?cc0=1&has_image=1&limit=6&q=" + encodeURIComponent(en)).then(function (d) {
      var list = (d && d.data) || [];
      for (var i = 0; i < list.length; i++) { var a = list[i], who = (a.creators || []).map(function (c) { return c.description || ""; }).join(" "), u = a.images && a.images.web && a.images.web.url;
        if (!u || !okMuseum(u) || !kindOk(kind, a.type) || !sameTitle(en, a.title) || !hasTok(who, toks)) continue;
        return { src: u, page: a.url || "https://www.clevelandart.org/art/" + a.accession_number, title: a.title, license: "CC0(클리블랜드 미술관 표시)", label: "클리블랜드 미술관" };
      }
      return null;
    });
  }
  var CHAIN = [srcCommons, srcCMA];   // D 커먼즈 검색 → E 클리블랜드(시카고 미술관·Openverse API는 브라우저 CORS 차단으로 쓰지 않아요, 2026-11-23 확인)   // 시카고 미술관 API는 브라우저(CORS)에서 막혀 쓰지 않아요(2026-11-23 확인)
  function fallback(en, toks, kind, cc) {
    var i = 0; function next() { if (i >= CHAIN.length) return Promise.resolve(null); var f = CHAIN[i++]; return f(en, toks, kind, cc).then(function (r) { return r || next(); }).catch(function () { return next(); }); }
    return next();
  }
  // keys: ["en:Mona_Lisa", ...] 후보를 차례로 시도. tokens: 설명·요약에 하나 이상 들어 있어야 하는 작가 이름(소문자·한글)
  function wikiImage(keys, tokens, kind, opts) {
    var cc = !!(opts && opts.cc);
    var id = (keys || []).join("|") + "|" + (kind || "") + (cc ? "|cc" : ""); if (cache[id] !== undefined) return Promise.resolve(cache[id]);
    var i = 0;
    function next() {
      if (i >= keys.length) {
        var en = ((keys.filter(function (k) { return /^en:/.test(k); })[0] || keys[0] || "").replace(/^\w+:/, "")).replace(/_/g, " ");
        return fallback(en, tokens, kind, cc).then(function (r) { cache[id] = r || null; saveCache(); return r || null; });
      }
      var k = keys[i++], m = /^(en|ko|de):(.+)$/.exec(k); if (!m) return next();
      return json("https://" + m[1] + ".wikipedia.org/api/rest_v1/page/summary/" + encodeURIComponent(m[2].replace(/ /g, "_"))).then(function (s) {
        if (!s || s.type !== "standard" || !s.thumbnail || !okImg(s.thumbnail.source)) return next();
        var text = norm((s.description || "") + " " + (s.extract || ""));
        if (!(tokens || []).some(function (t) { return t && text.indexOf(norm(t)) >= 0; })) return next();   // 작품·작가가 다르면 버려요
        var src = imgUrl(s.thumbnail.source), f = fileOf(src); if (!f) return next();
        return json("https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&prop=imageinfo&iiprop=extmetadata&titles=" + encodeURIComponent("File:" + f)).then(function (c) {
          var pages = c && c.query && c.query.pages, p = pages && pages[Object.keys(pages)[0]], md = p && p.imageinfo && p.imageinfo[0] && p.imageinfo[0].extmetadata;
          var lic = md && md.LicenseShortName && md.LicenseShortName.value;
          if (!okLic(lic, cc)) return next();                                                                                 // 공개 도메인 표시가 없으면 버려요
          var url = s.content_urls && s.content_urls.desktop && s.content_urls.desktop.page || ("https://" + m[1] + ".wikipedia.org/wiki/" + encodeURIComponent(m[2]));
          var res = { src: src, page: url, title: s.title || m[2], license: lic, label: "위키백과", artist: plain(md && md.Artist && md.Artist.value), licenseUrl: md && md.LicenseUrl && md.LicenseUrl.value, filePage: "https://commons.wikimedia.org/wiki/File:" + encodeURIComponent(f) };
          cache[id] = res; saveCache(); return res;
        });
      });
    }
    return next();
  }
  // 커먼즈의 음원 파일 찾기: 검색어로 찾고 ① 파일 이름에 곡 낱말이 모두 있고 ② 라이선스가 공개 도메인·CC0 표시이고 ③ 크기가 한도 이하인 첫 파일만 돌려줘요
  var AEXT = /\.(ogg|oga|opus|mp3|flac|wav)$/i;
  function commonsAudio(query, toks, maxBytes) {
    var id = "a|" + query; if (cache[id] !== undefined) return Promise.resolve(cache[id]);
    return json("https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&list=search&srnamespace=6&srlimit=25&srsearch=" + encodeURIComponent(query + " filetype:audio")).then(function (d) {
      var names = ((d && d.query && d.query.search) || []).map(function (r) { return r.title; }).filter(function (t) { var f = t.toLowerCase(); return AEXT.test(t) && (toks || []).every(function (alt) { return alt.split("/").some(function (a) { return f.indexOf(a) >= 0; }); }); }).slice(0, 12);
      if (!names.length) { cache[id] = null; saveCache(); return null; }
      return json("https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&prop=imageinfo&iiprop=extmetadata|url|size&titles=" + encodeURIComponent(names.join("|"))).then(function (c) {
        var pages = (c && c.query && c.query.pages) || {}, by = {}; Object.keys(pages).forEach(function (k) { by[pages[k].title] = pages[k]; });
        for (var i = 0; i < names.length; i++) {
          var ii = by[names[i]] && by[names[i]].imageinfo && by[names[i]].imageinfo[0]; if (!ii) continue;
          var lic = ii.extmetadata && ii.extmetadata.LicenseShortName && ii.extmetadata.LicenseShortName.value;
          if (!lic || !PD.test(lic) || !okImg(ii.url) || (ii.size || 0) > (maxBytes || 60000000)) continue;
          var res = { src: ii.url, page: ii.descriptionurl || ("https://commons.wikimedia.org/wiki/" + encodeURIComponent(names[i].replace(/ /g, "_"))), title: names[i].replace(/^File:/, ""), license: lic, size: ii.size || 0 };
          cache[id] = res; saveCache(); return res;
        }
        cache[id] = null; saveCache(); return null;
      });
    });
  }
  // 미리 골라 둔 커먼즈 음원 파일 이름들(좋은 순서)을 확인: 공개 도메인·CC0 표시가 있는 것만 순서대로 돌려줘요
  function commonsFiles(names, maxBytes) {
    var id = "f|" + (names || []).join("|"); if (cache[id] !== undefined) return Promise.resolve(cache[id]);
    if (!names || !names.length) return Promise.resolve([]);
    return json("https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&prop=imageinfo&iiprop=extmetadata|url|size&titles=" + encodeURIComponent(names.map(function (n) { return "File:" + n; }).join("|"))).then(function (c) {
      if (!c) return [];
      var pages = (c.query && c.query.pages) || {}, by = {}; Object.keys(pages).forEach(function (k) { by[pages[k].title] = pages[k]; });
      var out = []; names.forEach(function (n) {
        var ii = by["File:" + n] && by["File:" + n].imageinfo && by["File:" + n].imageinfo[0]; if (!ii) return;
        var lic = ii.extmetadata && ii.extmetadata.LicenseShortName && ii.extmetadata.LicenseShortName.value;
        if (!lic || !PD.test(lic) || !okImg(ii.url) || (ii.size || 0) > (maxBytes || 80000000)) return;
        out.push({ src: ii.url, page: ii.descriptionurl || ("https://commons.wikimedia.org/wiki/" + encodeURIComponent(("File:" + n).replace(/ /g, "_"))), title: n, license: lic, size: ii.size || 0 });
      });
      cache[id] = out; saveCache(); return out;
    });
  }
  // 인터넷 아카이브(archive.org) 음원: 이름이 "ia:항목/파일" 꼴. 항목 정보(metadata)에 공개 도메인·CC0 라이선스 표시가 있고 파일이 실제로 있을 때만 써요
  var IALIC = /publicdomain|zero/i;
  function iaFile(n, maxBytes) {
    var m = /^ia:([^\/]+)\/(.+)$/.exec(n); if (!m) return Promise.resolve(null);
    var id = "i|" + n; if (cache[id] !== undefined) return Promise.resolve(cache[id]);
    return json("https://archive.org/metadata/" + encodeURIComponent(m[1])).then(function (d) {
      if (!d) return null;                                                                   // 서버가 안 되면 저장하지 않고 다음에 다시 시도해요
      var lic = d.metadata && d.metadata.licenseurl, f = (d.files || []).filter(function (x) { return x.name === m[2]; })[0], size = f ? parseInt(f.size, 10) || 0 : 0, res = null;
      if (f && IALIC.test(String(lic || "")) && size <= (maxBytes || 80000000))
        res = { src: "https://archive.org/download/" + encodeURIComponent(m[1]) + "/" + m[2].split("/").map(encodeURIComponent).join("/"), page: "https://archive.org/details/" + encodeURIComponent(m[1]), title: m[2], license: "공개 도메인·CC0(인터넷 아카이브 표시)", size: size, label: "인터넷 아카이브" };
      cache[id] = res; saveCache(); return res;
    });
  }
  // 미리 골라 둔 음원 이름들(좋은 순서, 커먼즈 파일 이름 또는 "ia:…")을 확인해 순서를 지킨 채 돌려줘요. 한쪽 서버가 느리거나 안 돼도 다른 쪽이 나오게 두 출처를 따로 물어봐요
  function audioFiles(names, maxBytes) {
    names = names || []; var com = names.filter(function (n) { return !/^ia:/.test(n); }), ia = names.filter(function (n) { return /^ia:/.test(n); });
    return Promise.all([com.length ? commonsFiles(com, maxBytes).catch(function () { return []; }) : [], Promise.all(ia.map(function (n) { return iaFile(n, maxBytes).catch(function () { return null; }); }))]).then(function (r) {
      var cm = {}; (r[0] || []).forEach(function (x) { cm[x.title] = x; }); var iam = {}; ia.forEach(function (n, i) { if (r[1][i]) iam[n] = r[1][i]; });
      var out = []; names.forEach(function (n) { var x = /^ia:/.test(n) ? iam[n] : cm[n]; if (x) out.push(x); });
      // 출처가 둘 다 있으면 번갈아 놓아서 첫 후보가 안 나와도 곧바로 다른 서버를 써 보게 해요
      var a = out.filter(function (x) { return x.label !== "인터넷 아카이브"; }), b = out.filter(function (x) { return x.label === "인터넷 아카이브"; });
      if (!a.length || !b.length) return out; var mix = []; while (a.length || b.length) { if (a.length) mix.push(a.shift()); if (b.length) mix.push(b.shift()); } return mix;
    });
  }
  // 미리 골라 둔 커먼즈 사진 파일 이름들(좋은 순서)에서 라이선스(공개 도메인·CC0, cc면 CC BY·BY-SA까지)가 맞는 첫 사진을 돌려줘요. 사진 주소는 500px 미리보기예요.
  function commonsPhoto(names, cc) {
    var id = "p|" + (names || []).join("|") + (cc ? "|cc" : ""); if (cache[id] !== undefined) return Promise.resolve(cache[id]);
    if (!names || !names.length) return Promise.resolve(null);
    return json("https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&prop=imageinfo&iiprop=extmetadata|url&iiurlwidth=500&titles=" + encodeURIComponent(names.map(function (n) { return "File:" + n; }).join("|"))).then(function (c) {
      if (!c) return null;
      var pages = (c.query && c.query.pages) || {}, by = {}; Object.keys(pages).forEach(function (k) { by[(pages[k].title || "").replace(/^File:/, "").replace(/_/g, " ")] = pages[k]; });
      for (var i = 0; i < names.length; i++) {
        var pg = by[names[i].replace(/_/g, " ")], ii = pg && pg.imageinfo && pg.imageinfo[0]; if (!ii || !okImg(ii.thumburl)) continue;
        var md = ii.extmetadata || {}, lic = md.LicenseShortName && md.LicenseShortName.value; if (!okLic(lic, cc)) continue;
        var res = { src: imgUrl(ii.thumburl), page: ii.descriptionurl, filePage: ii.descriptionurl, title: names[i], license: lic, licenseUrl: md.LicenseUrl && md.LicenseUrl.value, artist: plain(md.Artist && md.Artist.value), label: "위키미디어 커먼즈" };
        cache[id] = res; saveCache(); return res;
      }
      cache[id] = null; saveCache(); return null;
    });
  }
  window.fgOnline = {
    enabled: ENABLED,
    on: function () { return ENABLED && get(KEY) === "1"; },
    ask: function (text) {
      if (!ENABLED) return false; if (get(KEY) === "1") return true;
      var ok = false; try { ok = window.confirm(text || "인터넷에서 자료를 불러와요. 계속할까요?"); } catch (e) { ok = false; }
      if (ok) set(KEY, "1"); return ok;
    },
    off: function () { try { localStorage.removeItem(KEY); } catch (e) {} },
    json: json, wikiImage: wikiImage, commonsAudio: commonsAudio, commonsFiles: commonsFiles, audioFiles: audioFiles, commonsPhoto: commonsPhoto, imageFallback: fallback, _src: { commons: srcCommons, cma: srcCMA }, okImg: okImg, imgUrl: imgUrl, fileOf: fileOf, norm: norm
  };
})();
