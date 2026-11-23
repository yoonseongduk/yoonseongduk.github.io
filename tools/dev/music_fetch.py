# 클래식 곡 음원 확보 도구: 위키미디어 커먼즈에서 공개 도메인·CC0 표시가 있는 녹음을 찾아 20초 조각으로 잘라 classic-audio/ 에 저장해요.
#   py music_fetch.py --dry-run            (받지 않고 후보와 라이선스만 확인)
#   py music_fetch.py [--only 곡제목] [--limit N] [--refresh]
# 안전장치: ① 파일 이름에 곡 낱말이 모두 있을 것 ② 라이선스 표시가 공개 도메인·CC0일 것 ③ 파일이 20MB 이하일 것 ④ ffprobe 로 길이 15초 이상. 하나라도 틀리면 그 곡은 음원 없이 글로만 나와요.
import os, re, sys, json, time, subprocess, urllib.request, urllib.error, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from music_audio import AUDIO
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "classic-audio")
TMP = "/tmp/claude-0/music_tmp"
UA = "FamilyGamesMusicFetch/1.0 (educational family quiz; public-domain recordings only)"
PD = re.compile(r"public domain|^pd\b|^pd-|cc0|cc-zero", re.I)
PACE = float(os.environ.get("MUSIC_PACE", "2.5")); CLIP = 20
EXT = (".ogg", ".oga", ".opus", ".mp3", ".flac", ".wav")
LAST = {"s": 0}
def get(u, binary=False, tries=7):
    for n in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=60) as r:
                d = r.read(); LAST["s"] = 200; time.sleep(PACE); return d if binary else json.loads(d.decode("utf-8"))
        except urllib.error.HTTPError as e:
            LAST["s"] = e.code
            if e.code == 404: return None
            if e.code in (429, 500, 502, 503, 504):
                try: ra = int(e.headers.get("Retry-After", "10"))
                except Exception: ra = 10
                time.sleep(min(ra, 150) + 1 + n); continue
            return None
        except Exception: LAST["s"] = 0; time.sleep(3 + n)
    return None
def api(**p): return get("https://commons.wikimedia.org/w/api.php?format=json&" + urllib.parse.urlencode(p))
def ok_name(fn, toks):
    f = fn.lower()
    return all(any(alt in f for alt in t.split("/")) for t in toks)
def find(title):
    q, toks = AUDIO[title].split("|"); toks = [t.strip().lower() for t in toks.split(",")]
    d = api(action="query", list="search", srsearch=q + " filetype:audio", srnamespace=6, srlimit=25)
    files = [r["title"] for r in (d or {}).get("query", {}).get("search", []) if r["title"].lower().endswith(EXT) and ok_name(r["title"], toks)]
    if not files: return None, "후보 없음(검색 결과에 맞는 이름이 없음)"
    d = api(action="query", prop="imageinfo", iiprop="extmetadata|url|size", titles="|".join(files[:12]))
    pages = {p["title"]: p for p in ((d or {}).get("query", {}).get("pages", {}) or {}).values()}
    why = "라이선스 표시가 공개 도메인·CC0가 아님"
    for fn in files[:12]:
        ii = ((pages.get(fn) or {}).get("imageinfo") or [{}])[0]; md = ii.get("extmetadata", {}); lic = (md.get("LicenseShortName") or {}).get("value", "")
        if not lic or not PD.search(lic): continue
        if (ii.get("size") or 0) > 20_000_000: why = "파일이 너무 큼"; continue
        return {"file": fn, "url": ii.get("url"), "lic": lic, "page": ii.get("descriptionurl") or ("https://commons.wikimedia.org/wiki/" + urllib.parse.quote(fn.replace(" ", "_")))}, None
    return None, why
def clip(src, dst):
    """앞쪽 무음을 걷어 내고 CLIP 초만 가져와 모노 Opus(약 40kbps)로 저장."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True)
    try: dur = float(r.stdout.strip())
    except Exception: return False, "길이를 못 읽음"
    if dur < 15: return False, f"너무 짧음({dur:.0f}초)"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-af", "silenceremove=start_periods=1:start_threshold=-45dB", "-t", str(CLIP), "-ac", "1", "-c:a", "libopus", "-b:a", "40k", "-application", "audio", dst]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return (p.returncode == 0 and os.path.exists(dst) and os.path.getsize(dst) > 3000), p.stderr[-120:]
def main():
    a = sys.argv[1:]; dry = "--dry-run" in a; refresh = "--refresh" in a; only = a[a.index("--only") + 1] if "--only" in a else None
    limit = int(a[a.index("--limit") + 1]) if "--limit" in a else None
    os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
    ip = os.path.join(OUT, "index.json"); idx = json.load(open(ip, encoding="utf-8")) if os.path.exists(ip) else {}
    works = [t for t in AUDIO if not only or t == only]
    if limit: works = works[:limit]
    ok = skip = 0; fails = []
    for n, t in enumerate(works, 1):
        if not refresh and t in idx and os.path.exists(os.path.join(OUT, idx[t]["f"])): skip += 1; continue
        info, why = find(t)
        if not info: fails.append((t, why)); print(f"[{n}/{len(works)}] ✗ {t}: {why}", flush=True); continue
        if dry: ok += 1; print(f"[{n}/{len(works)}] ✓ {t} ← {info['file'][5:70]} ({info['lic']})", flush=True); continue
        ext = os.path.splitext(info["file"])[1].lower(); tmp = os.path.join(TMP, "in" + ext)
        data = get(info["url"], binary=True)
        if not data: fails.append((t, "내려받기 실패")); print(f"[{n}/{len(works)}] ✗ {t}: 내려받기 실패", flush=True); continue
        open(tmp, "wb").write(data); fn = f"{abs(hash(t)) % 10**8:08d}.ogg" if False else "a%03d.ogg" % (list(AUDIO).index(t) + 1); dst = os.path.join(OUT, fn)
        good, msg = clip(tmp, dst)
        if not good: fails.append((t, "자르기 실패: " + msg)); print(f"[{n}/{len(works)}] ✗ {t}: 자르기 실패 {msg}", flush=True); continue
        idx[t] = {"f": fn, "p": info["page"], "t": info["file"][5:], "l": info["lic"]}; ok += 1
        json.dump(idx, open(ip, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"[{n}/{len(works)}] ✓ {t} ← {info['file'][5:60]} ({info['lic']}, {os.path.getsize(dst)//1024}KB)", flush=True)
    if not dry:
        open(os.path.join(OUT, "LICENSE.txt"), "w", encoding="utf-8").write("이 폴더의 음원은 위키미디어 커먼즈 녹음 파일의 앞부분 약 20초이며, 파일마다 공개 도메인·CC0 표시를 확인한 것만 담았어요.\n곡 이름·원본 파일 이름·출처 주소·라이선스 표시는 index.json 에 있어요. 권리자께서 삭제를 요청하시면 확인 후 바로 지워요.\n")
    print(f"\n통과 {ok} · 건너뜀 {skip} · 걸러짐 {len(fails)} (전체 {len(works)}){' · 검증만(dry-run)' if dry else ''}")
    from collections import Counter
    for k, v in Counter(w for _, w in fails).most_common(): print("  ·", k, v)
if __name__ == "__main__": main()
