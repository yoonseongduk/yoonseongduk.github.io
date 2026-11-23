# 클래식 곡마다 "음질이 괜찮은" 위키미디어 커먼즈 녹음을 골라 music_pick.json 에 파일 이름(글)만 적어요. 음원 파일은 저장소에 두지 않아요(분석용으로 앞부분만 잠깐 받고 지워요).
#   py music_pick.py              (1단계: 이름·라이선스·길이·비트레이트로 거르고 → 2단계: 앞 20초를 분석해 잡음·옛 녹음 티가 나는 것 제외)
#   py music_pick.py --no-screen  (1단계만)   --only 곡제목   --limit N
# 거르는 기준: 파일 이름에 옛 녹음(1900년대 초 음반·78회전)·MIDI·편곡·피아노 연주 같은 낱말이 없을 것, 공개 도메인·CC0 표시, 길이 25초 이상,
#   손실 압축(ogg·mp3)은 96kbps 이상, 앞 20초 분석에서 ① 소리 크기 변화폭 22dB 이상 ② 높은 소리(6kHz 이상)가 남아 있을 것(잡음 많은 옛 녹음은 변화폭이 작고 고음이 잘려 있어요).
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
            if ext in LOSSY and kbps is not None and kbps < 96: continue
            if ext not in LOSSY and size > 80_000_000: continue
            score = (kbps if ext in LOSSY else 160) if kbps or ext not in LOSSY else 60
            out.append({"f": name[5:], "url": ii["url"], "lic": lic, "kbps": round(kbps) if kbps else None, "dur": round(dur) if dur else None, "size": size, "score": round(score)})
    out.sort(key=lambda c: -c["score"]); return out
def analyze(c):
    """앞부분을 잠깐 받아 20초를 분석: 소리 크기 변화폭(dB)과 높은 소리가 남아 있는지(98% 에너지 주파수). 파일은 바로 지워요."""
    ext = os.path.splitext(c["f"].lower())[1]; n = 3_500_000 if ext not in LOSSY else 1_600_000
    d = get(c["url"], binary=True, rng=f"bytes=0-{n - 1}")
    if not d or len(d) < 50_000: return None
    os.makedirs(TMP, exist_ok=True); p = os.path.join(TMP, "an" + ext); open(p, "wb").write(d)
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-t", "20", "-ac", "1", "-ar", "22050", "-f", "s16le", "-"], capture_output=True)
    try: os.remove(p)
    except Exception: pass
    x = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float64) / 32768
    if len(x) < 22050 * 6: return None
    fr = 1102; m = len(x) // fr; e = np.sqrt((x[:m * fr].reshape(m, fr) ** 2).mean(1)) + 1e-9; db = 20 * np.log10(e); db = db[db > -80]
    if len(db) < 20: return None
    dyn = float(np.percentile(db, 95) - np.percentile(db, 10))
    seg = x[:len(x) // 2048 * 2048].reshape(-1, 2048) * np.hanning(2048); ps = (np.abs(np.fft.rfft(seg, axis=1)) ** 2).mean(0); cs = np.cumsum(ps) / ps.sum()
    roll = float(np.searchsorted(cs, 0.98) * 22050 / 2048)
    return {"dyn": round(dyn, 1), "roll": round(roll)}
def good(a): return a is not None and a["dyn"] >= 22 and a["roll"] >= 3000
def main():
    a = sys.argv[1:]; screen = "--no-screen" not in a; only = a[a.index("--only") + 1] if "--only" in a else None; limit = int(a[a.index("--limit") + 1]) if "--limit" in a else None
    st = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    works = [t for t in AUDIO if not only or t == only]
    if limit: works = works[:limit]
    for n, t in enumerate(works, 1):
        s = st.setdefault(t, {})
        if "cands" not in s: s["cands"] = candidates(t)
        picked = [c for c in s["cands"] if screen and c["f"] in s.get("scr", {}) and good(s["scr"][c["f"]])]
        tried = 0
        if screen:
            s.setdefault("scr", {})
            for c in s["cands"]:
                if len(picked) >= 2 or tried >= 4: break
                if c["f"] in s["scr"]: continue
                s["scr"][c["f"]] = analyze(c); tried += 1
                if good(s["scr"][c["f"]]): picked.append(c)
        elif not screen: picked = s["cands"][:2]
        json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False)
        res = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
        if picked: res[t] = [{"f": c["f"], "lic": c["lic"], "kbps": c["kbps"], "scr": (s.get("scr") or {}).get(c["f"])} for c in picked[:2]]
        else: res.pop(t, None)
        json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        top = picked[0] if picked else None
        print(f"[{n}/{len(works)}] {'✓' if top else '✗'} {t}: 후보 {len(s['cands'])}개" + (f" → {top['f'][:60]} ({top['kbps']}kbps, {(s.get('scr') or {}).get(top['f'])})" if top else " → 쓸 만한 녹음 없음(글로만)"), flush=True)
    res = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    print(f"\n음질 확인을 통과한 곡 {len(res)} / {len(works)}")
if __name__ == "__main__": main()
