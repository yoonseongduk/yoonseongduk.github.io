# 클래식 곡마다 "음질이 괜찮은" 위키미디어 커먼즈 녹음을 골라 music_pick.json 에 파일 이름(글)만 적어요. 음원 파일은 저장소에 두지 않아요(분석용으로 앞부분만 잠깐 받고 지워요).
#   py music_pick.py              (1단계: 이름·라이선스·길이·비트레이트로 거르고 → 2단계: 앞 20초를 분석해 잡음·옛 녹음 티가 나는 것 제외)
#   py music_pick.py --no-screen  (1단계만)   --only 곡제목   --limit N
# 거르는 기준: 파일 이름에 옛 녹음(1900년대 초 음반·78회전)·MIDI·편곡·피아노 연주 같은 낱말이 없을 것, 공개 도메인·CC0 표시, 길이 25초 이상,
#   손실 압축(ogg·mp3)은 64kbps 이상, 앞 20초 분석에서 ① 소리 크기 변화폭 22dB 이상 ② 높은 소리(6kHz 이상)가 남아 있을 것(잡음 많은 옛 녹음은 변화폭이 작고 고음이 잘려 있어요).
import os, re, sys, json, time, subprocess, urllib.request, urllib.error, urllib.parse
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from music_audio import AUDIO
HERE = os.path.dirname(os.path.abspath(__file__)); STATE = os.path.join(HERE, "music_pick_state.json"); OUT = os.path.join(HERE, "music_pick.json"); TMP = "/tmp/claude-0/music_tmp"
UA = "FamilyGamesMusicPick/1.0 (educational family quiz; public-domain recordings only)"
PD = re.compile(r"public domain|^pd\b|^pd-|cc0|cc-zero", re.I)
BAD = re.compile(r"\b(18\d\d|19[0-4]\d)\b|victor|columbia|edison|gramophone|berliner|\b78 ?rpm\b|cylinder|shellac|vinyl|lp rip|midi|synth|piano performance|piano arrangement|for piano|arrangement|transcription|karaoke|\bcover\b|remix|ringtone|\bdemo\b|sample|loop|8-?bit|music box|fragment", re.I)
EXT = (".ogg", ".oga", ".opus", ".mp3", ".flac", ".wav"); LOSSY = (".ogg", ".oga", ".opus", ".mp3")
PACE = float(os.environ.get("MUSIC_PACE", "2.5"))
def get(u, binary=False, rng=None, tries=7):
    for n in range(tries):
        try:
            h = {"User-Agent": UA};
            if rng: h["Range"] = rng
            with urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=90) as r:
                d = r.read(); time.sleep(PACE); return d if binary else json.loads(d.decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            if e.code in (429, 500, 502, 503, 504):
                try: ra = int(e.headers.get("Retry-After", "10"))
                except Exception: ra = 10
                time.sleep(min(ra, 150) + 1 + n); continue
            return None
        except Exception: time.sleep(3 + n)
    return None
def api(**p): return get("https://commons.wikimedia.org/w/api.php?format=json&" + urllib.parse.urlencode(p))
def meta(ii, key):
    for m in ii.get("metadata") or []:
        if m.get("name") == key and isinstance(m.get("value"), (int, float)): return float(m["value"])
    return None
def candidates(title):
    q, toks = AUDIO[title].split("|"); toks = [t.strip().lower() for t in toks.split(",")]
    d = api(action="query", list="search", srsearch=q + " filetype:audio", srnamespace=6, srlimit=30)
    names = [r["title"] for r in (d or {}).get("query", {}).get("search", []) if r["title"].lower().endswith(EXT) and all(any(a in r["title"].lower() for a in t.split("/")) for t in toks) and not BAD.search(r["title"])]
    if not names: return []
    out = []
    for i in range(0, min(len(names), 24), 12):
        d = api(action="query", prop="imageinfo", iiprop="extmetadata|url|size|metadata", titles="|".join(names[i:i + 12]))
        for p in ((d or {}).get("query", {}).get("pages", {}) or {}).values():
            ii = (p.get("imageinfo") or [{}])[0]; lic = ((ii.get("extmetadata") or {}).get("LicenseShortName") or {}).get("value", "")
            if not lic or not PD.search(lic) or not ii.get("url"): continue
            name = p["title"]; ext = os.path.splitext(name.lower())[1]; size = ii.get("size") or 0
            dur = meta(ii, "length") or meta(ii, "playtime_seconds")
            if dur is not None and dur < 25: continue
            kbps = size * 8 / dur / 1000 if dur else None
            if ext in LOSSY and kbps is not None and kbps < 64: continue
            if ext not in LOSSY and size > 80_000_000: continue
            score = (kbps if ext in LOSSY else 160) if kbps or ext not in LOSSY else 60
            out.append({"f": name[5:], "url": ii["url"], "lic": lic, "kbps": round(kbps) if kbps else None, "dur": round(dur) if dur else None, "size": size, "score": round(score)})
    out.sort(key=lambda c: -c["score"]); return out

# ───────── 두 번째 후보 출처: 인터넷 아카이브(archive.org). 항목에 licenseurl(공개 도메인·CC0)이 있는 것만, 곡 낱말이 제목·식별자에 있어야 해요.
IAFMT = {"Ogg Vorbis": 3, "VBR MP3": 2, "MP3": 2, "128Kbps MP3": 1, "64Kbps MP3": 0, "Flac": 2}
def ia_candidates(title):
    q, toks = AUDIO[title].split("|"); toks = [t.strip().lower() for t in toks.split(",")]
    words = " ".join(w for w in re.sub(r"[^\w ]", " ", q).split() if len(w) > 2)
    qq = f"({words}) AND mediatype:audio AND (licenseurl:*publicdomain* OR licenseurl:*zero*)"
    d = get("https://archive.org/advancedsearch.php?" + urllib.parse.urlencode({"q": qq, "fl[]": ["identifier", "title", "licenseurl", "downloads"], "rows": 12, "sort[]": "downloads desc", "output": "json"}, doseq=True))
    out = []
    for doc in ((d or {}).get("response", {}).get("docs", []) or []):
        ident = doc["identifier"]; ttl = (str(doc.get("title", "")) + " " + ident).lower()
        if not all(any(a in ttl for a in t.split("/")) for t in toks) or BAD.search(ttl): continue
        m = get("https://archive.org/metadata/" + urllib.parse.quote(ident))
        if not m: continue
        lic = (m.get("metadata", {}) or {}).get("licenseurl", "")
        if not re.search(r"publicdomain|zero", str(lic)): continue
        best = None
        for f in m.get("files", []):
            fmt = f.get("format"); 
            if fmt not in IAFMT: continue
            try: size = int(f.get("size", 0)); dur = float(f.get("length", 0))
            except Exception: continue
            if dur < 25 or size > 80_000_000: continue
            kbps = size * 8 / dur / 1000
            if fmt != "Flac" and kbps < 64: continue
            key = (IAFMT[fmt], kbps)
            if not best or key > best[0]: best = (key, f, size, dur, kbps)
        if best:
            _, f, size, dur, kbps = best
            out.append({"f": "ia:" + ident + "/" + f["name"], "url": f"https://archive.org/download/{urllib.parse.quote(ident)}/{urllib.parse.quote(f['name'])}", "lic": "공개 도메인·CC0(인터넷 아카이브 표시)", "kbps": round(kbps), "dur": round(dur), "size": size, "score": round(kbps) + 5, "page": f"https://archive.org/details/{ident}"})
        if len(out) >= 4: break
    return out
def analyze(c):
    """앞부분을 받아 20초를 분석: 소리 크기 변화폭(dB)과 높은 소리가 남아 있는지(98% 에너지 주파수).
    받은 내용은 디스크에 쓰지 않고 메모리에서 바로 ffmpeg 로 넘겨요(클라우드에 음원 파일이 생기지 않아요). 남기는 건 숫자 두 개뿐이에요."""
    ext = os.path.splitext(c["f"].lower())[1]; n = 3_500_000 if ext not in LOSSY else 1_600_000
    d = get(c["url"], binary=True, rng=f"bytes=0-{n - 1}")
    if not d or len(d) < 50_000: return None
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-t", "20", "-ac", "1", "-ar", "22050", "-f", "s16le", "-"], input=d, capture_output=True); d = None
    x = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float64) / 32768
    if len(x) < 22050 * 6: return None
    fr = 1102; m = len(x) // fr; e = np.sqrt((x[:m * fr].reshape(m, fr) ** 2).mean(1)) + 1e-9; db = 20 * np.log10(e); db = db[db > -80]
    if len(db) < 20: return None
    dyn = float(np.percentile(db, 95) - np.percentile(db, 10))
    seg = x[:len(x) // 2048 * 2048].reshape(-1, 2048) * np.hanning(2048); ps = (np.abs(np.fft.rfft(seg, axis=1)) ** 2).mean(0); cs = np.cumsum(ps) / ps.sum()
    roll = float(np.searchsorted(cs, 0.98) * 22050 / 2048)
    return {"dyn": round(dyn, 1), "roll": round(roll)}
def good(a): return a is not None and a["dyn"] >= 22 and a["roll"] >= 3000
IAF = os.path.join(HERE, "music_pick_ia.json"); SCRF = os.path.join(HERE, "music_pick_scr.json")
def load(p): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
def save(p, d): json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
def main():
    """세 단계를 동시에 돌려도 서로 기록을 덮어쓰지 않게 단계마다 자기 기록 파일을 써요:
    1단계=music_pick_state.json(커먼즈 후보), 2단계=music_pick_ia.json(아카이브 후보), 3단계=music_pick_scr.json(음질 숫자)+music_pick.json(결과).
    3단계는 후보가 준비된 곡부터 바로 분석하고(--follow 면 1·2단계가 끝날 때까지 되풀이)."""
    import time
    a = sys.argv[1:]; screen = "--no-screen" not in a and "--ia" not in a; only = a[a.index("--only") + 1] if "--only" in a else None; limit = int(a[a.index("--limit") + 1]) if "--limit" in a else None
    works = [t for t in AUDIO if not only or t == only]
    if limit: works = works[:limit]
    if "--cands-only" in a:   # 음질 분석 없이 후보만으로 곡 목록(music_pick.json)을 만들어요: 위키 1개 + 아카이브 1개 + 다음 순위 1개(최대 3개, 한쪽 서버가 안 될 때 다른 쪽을 쓰게)
        st = load(STATE); ia = load(IAF); res = {}
        for t in works:
            com = sorted(st.get(t, {}).get("cands", []), key=lambda c: -c["score"]); iac = sorted(ia.get(t, {}).get("cands", []), key=lambda c: -c["score"]); pick = []
            for lst in (com, iac):
                if lst: pick.append(lst[0])
            rest = [c for c in com[1:] + iac[1:] if c not in pick]; rest.sort(key=lambda c: -c["score"]); pick += rest[:max(0, 3 - len(pick))]
            if pick: res[t] = [{"f": c["f"], "lic": c["lic"], "kbps": c["kbps"], "scr": None} for c in pick]
        save(OUT, res); print(f"후보만으로 만든 곡 {len(res)} / {len(works)} (음질 분석 전)"); return
    if "--ia" in a:   # 2단계: 인터넷 아카이브 후보(다른 서버라 1단계와 동시에 돌려도 돼요)
        ia = load(IAF)
        for n, t in enumerate(works, 1):
            if ia.get(t, {}).get("done"): continue
            add = ia_candidates(t); ia[t] = {"cands": add, "done": True}; save(IAF, ia)
            print(f"[{n}/{len(works)}] 인터넷 아카이브 후보 +{len(add)}: " + ", ".join(c["f"][3:50] for c in add[:2]), flush=True)
        return
    if not screen:   # 1단계: 커먼즈 후보
        st = load(STATE)
        for n, t in enumerate(works, 1):
            s = st.setdefault(t, {})
            if not s.get("cands"): s["cands"] = candidates(t)
            save(STATE, st)
            print(f"[{n}/{len(works)}] 후보 {len(s['cands'])}개: " + ", ".join(c["f"][:40] for c in s["cands"][:2]), flush=True)
        return
    follow = "--follow" in a   # 3단계: 음질 분석
    while True:
        st = load(STATE); ia = load(IAF); scr = load(SCRF); res = load(OUT); did = 0
        for n, t in enumerate(works, 1):
            if "cands" not in st.get(t, {}): continue   # 아직 1단계가 안 한 곡은 다음 바퀴에
            cands = sorted(st[t]["cands"] + [c for c in ia.get(t, {}).get("cands", []) if c["f"] not in {x["f"] for x in st[t]["cands"]}], key=lambda c: -c["score"])
            sc = scr.setdefault(t, {}); picked = [c for c in cands if c["f"] in sc and good(sc[c["f"]])]; tried = 0
            for c in cands:
                if len(picked) >= 2 or tried >= 4: break
                if c["f"] in sc: continue
                sc[c["f"]] = analyze(c); tried += 1; did += 1; save(SCRF, scr)
                if good(sc[c["f"]]): picked.append(c)
            if picked: res[t] = [{"f": c["f"], "lic": c["lic"], "kbps": c["kbps"], "scr": sc.get(c["f"])} for c in picked[:2]]
            elif all(sc.get(c["f"]) is not None for c in cands[:4] if c["f"] in sc): res.pop(t, None)   # 분석이 서버 문제로 실패(None)한 곡은 기존 목록을 그대로 둬요
            save(OUT, res)
            if tried: print(f"[{n}/{len(works)}] {'✓' if picked else '✗'} {t}: 후보 {len(cands)}개" + (f" → {picked[0]['f'][:60]} ({picked[0]['kbps']}kbps, {sc.get(picked[0]['f'])})" if picked else " → 쓸 만한 녹음 없음(글로만)"), flush=True)
        ready = all("cands" in st.get(t, {}) and ia.get(t, {}).get("done") for t in works)
        if not follow or (ready and did == 0): break
        time.sleep(60 if did == 0 else 1)
    res = load(OUT)
    print(f"\n음질 확인을 통과한 곡 {len(res)} / {len(works)}")
if __name__ == "__main__": main()
