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
  function imgUrl(u) { return okImg(u) ? u.replace(/^https:\/\/thumb\.wikimedia\.org\//, "https://upload.wikimedia.org/").replace(/\?.*$/, "") : null; }
  function fileOf(u) { var m = /\/commons\/(?:thumb\/)?[0-9a-f]\/[0-9a-f]{2}\/([^\/]+)/.exec(u || ""); return m ? decodeURIComponent(m[1]) : null; }
  var PD = /public domain|^pd\b|^pd-|cc0|cc-zero/i;
  function norm(t) { return String(t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase(); }   // 악센트·대소문자를 맞춰서 비교(Cézanne = cezanne)
  // keys: ["en:Mona_Lisa", ...] 후보를 차례로 시도. tokens: 설명·요약에 하나 이상 들어 있어야 하는 작가 이름(소문자·한글)
  function wikiImage(keys, tokens) {
    var id = (keys || []).join("|"); if (cache[id] !== undefined) return Promise.resolve(cache[id]);
    var i = 0;
    function next() {
      if (i >= keys.length) { cache[id] = null; saveCache(); return Promise.resolve(null); }
      var k = keys[i++], m = /^(en|ko):(.+)$/.exec(k); if (!m) return next();
      return json("https://" + m[1] + ".wikipedia.org/api/rest_v1/page/summary/" + encodeURIComponent(m[2].replace(/ /g, "_"))).then(function (s) {
        if (!s || s.type !== "standard" || !s.thumbnail || !okImg(s.thumbnail.source)) return next();
        var text = norm((s.description || "") + " " + (s.extract || ""));
        if (!(tokens || []).some(function (t) { return t && text.indexOf(norm(t)) >= 0; })) return next();   // 작품·작가가 다르면 버려요
        var src = imgUrl(s.thumbnail.source), f = fileOf(src); if (!f) return next();
        return json("https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&prop=imageinfo&iiprop=extmetadata&titles=" + encodeURIComponent("File:" + f)).then(function (c) {
          var pages = c && c.query && c.query.pages, p = pages && pages[Object.keys(pages)[0]], md = p && p.imageinfo && p.imageinfo[0] && p.imageinfo[0].extmetadata;
          var lic = md && md.LicenseShortName && md.LicenseShortName.value;
          if (!lic || !PD.test(lic)) return next();                                                                                 // 공개 도메인 표시가 없으면 버려요
          var url = s.content_urls && s.content_urls.desktop && s.content_urls.desktop.page || ("https://" + m[1] + ".wikipedia.org/wiki/" + encodeURIComponent(m[2]));
          var res = { src: src, page: url, title: s.title || m[2], license: lic };
          cache[id] = res; saveCache(); return res;
        });
      });
    }
    return next();
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
    json: json, wikiImage: wikiImage, okImg: okImg, imgUrl: imgUrl, fileOf: fileOf, norm: norm
  };
})();
