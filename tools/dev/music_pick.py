# 클래식 곡마다 "음질이 괜찮은" 위키미디어 커먼즈 녹음을 골라 music_pick.json 에 파일 이름(글)만 적어요. 음원 파일은 저장소에 두지 않아요(분석용으로 앞부분만 잠깐 받고 지워요).
#   py music_pick.py              (1단계: 이름·라이선스·길이·비트레이트로 거르고 → 2단계: 앞 20초를 분석해 잡음·옛 녹음 티가 나는 것 제외)
#   py music_pick.py --no-screen  (1단계만)   --only 곡제목   --limit N   --ia-only (위키가 429로 막혔을 때 아카이브 녹음만 분석)
# 거르는 기준: 파일 이름에 옛 녹음(1900년대 초 음반·78회전)·MIDI·편곡·피아노 연주 같은 낱말이 없을 것, 공개 도메인·CC0 표시, 길이 25초 이상,
#   손실 압축(ogg·mp3)은 64kbps 이상, 앞 20초 분석에서 ① 소리 크기 변화폭 22dB 이상 ② 높은 소리(6kHz 이상)가 남아 있을 것(잡음 많은 옛 녹음은 변화폭이 작고 고음이 잘려 있어요).
import os, re, sys, json, time, subprocess, urllib.request, urllib.error, urllib.parse
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from music_audio import AUDIO
HERE = os.path.dirname(os.path.abspath(__file__)); STATE = os.path.join(HERE, "music_pick_state.json"); OUT = os.path.join(HERE, "music_pick.json"); TMP = "/tmp/claude-0/music_tmp"
UA = "FamilyGamesMusicPick/1.0 (educational family quiz; public-domain recordings only)"
PD = re.compile(r"public domain|^pd\b|^pd-|cc0|cc-zero", re.I)
CC = re.compile(r"^cc[- ]by(-sa)?[ -]\d", re.I)   # 2026-11-24 사용자 결정: 클래식 음원도 CC BY·CC BY-SA 허용(비영리·변경금지 제외, 녹음한 사람 표시)
BAD = re.compile(r"\b(18\d\d|19[0-4]\d)\b|victor|columbia|edison|gramophone|berliner|\b78 ?rpm\b|cylinder|shellac|vinyl|lp rip|midi|synth|piano performance|piano arrangement|for piano|arrangement|transcription|karaoke|\bcover\b|remix|ringtone|\bdemo\b|sample|loop|8-?bit|music box|fragment", re.I)
EXT = (".ogg", ".oga", ".opus", ".mp3", ".flac", ".wav"); LOSSY = (".ogg", ".oga", ".opus", ".mp3")
PACE = float(os.environ.get("MUSIC_PACE", "2.5"))
GET_DEADLINE = float(os.environ.get("MUSIC_GET_DEADLINE", "240"))   # 한 번 받기에 쓰는 최대 시간(초)
# 옛 음반(1900~1940년대 SP판) 상표·옮긴 곳·그 시절 연주자 이름(2026-11-24 사용자 요청: 너무 오래된 음원은 최신 음원으로)
OLD = re.compile(r"jukebox|\bhmv\b|polydor|odeon|parlophon|brunswick|\bpdp\b|pdp-ch|georgeblood|78rpm|\b78\b|toscanini|stokowski|caruso|godowsky|rethberg|prihoda|schlusnus|sassoli|\bdux\b|melba|kreisler|paderewski|furtw|mengelberg|\bwblp\b|historic", re.I)
# 클래식이 아닌 편곡(사용자 지적 2026-11-24: 캐논이 댄스 편곡). 곡 검색어에 그 낱말이 들어 있으면(Hungarian Dance 등) 괜찮아요
STYLE = ["dance", "techno", "rock", "metal", "jazz", "pop", "electro", "edm", "trap", "hip hop", "hiphop", "lofi", "lo-fi", "chill", "ambient", "relax", "sleep", "meditation", "baby", "version", "mix", "mashup", "medley", "tribute", "instrumental", "ukulele", "kalimba", "ocarina", "harmonica", "accordion", "sax", "beatbox", "cappella", "whistl", "chiptune", "ghost", "montesano", "guitar", "harp", "cello suite"]
# 원곡과 다른 악기로 편곡한 것: 갈래가 이 악기와 맞지 않으면 빼요
INSTR = {"piano": ("피아노 독주곡", "협주곡", "실내악", "가곡·성악곡"), "organ": ("오르간곡", "종교 음악")}
MUSOPEN = {   # 인터넷 아카이브의 Musopen 모음집(공개 도메인, 2012년 무렵 현대 연주). 곡이 맞는지 파일 이름으로 확인해 지정했어요
 "골트베르크 변주곡": "MusopenCollectionAsFlac/Bach_GoldbergVariations/JohannSebastianBach-01-GoldbergVariationsBwv.988-Aria.mp3",
 "교향곡 3번 '영웅'": "MusopenCollectionAsFlac/Beethoven_SymphonyNo.3Eroica/LudwigVanBeethoven-SymphonyNo.3InEFlatMajorEroicaOp.55-01-AllegroConBrio.mp3",
 "아침(페르 귄트 중)": "MusopenCollectionAsFlac/Greig_PeerGynt/EdvardGrieg-PeerGyntSuiteNo.1Op.46-01-Morning.mp3",
 "페르 귄트": "MusopenCollectionAsFlac/Greig_PeerGynt/EdvardGrieg-PeerGyntSuiteNo.1Op.46-04-InTheHallOfTheMountainKing.mp3",
 "마술피리": "MusopenCollectionAsFlac/Mozart_MagicFluteOverture/WolfgangAmadeusMozart-MagicFluteOverture.mp3",
 "피가로의 결혼": "MusopenCollectionAsFlac/Mozart_MarriageOfFigaro/WolfgangAmadeusMozart-MarriageOfFigaro.mp3",
 "교향곡 40번 g단조": "MusopenCollectionAsFlac/Mozart_SymphonyNo.40inGMinor/WolfgangAmadeusMozart-SymphonyNo.40InGMinorK.550-01-MoltoAllegro.mp3",
 "몰다우": "MusopenCollectionAsFlac/Smetana_Vltava/BedichSmetana-MVlast-Vltava.mp3",
 "즉흥 환상곡": "musopen-chopin/Fantasie Impromptu Op. 66.mp3",
 "녹턴 Op.9-2": "musopen-chopin/Nocturne Op. 9 no. 2 in E flat major.mp3",
 "영웅 폴로네즈": "musopen-chopin/PolonaiseOp.53InAFlatMajorheroic.mp3",
 "강아지 왈츠": "musopen-chopin/Waltz Op. 64 no. 1 in D flat major.mp3",
 "빗방울 전주곡": "musopen-chopin/Prelude Op. 28 no. 15.mp3",
}
def _genres():
    import music_data as M; g = {}; sur = set()
    for c in M.COMPOSERS:
        sur.add(c[2].split()[-1].lower())
        for w in c[7]: g[w[0]] = w[2]
    return g, sur
GENRE, SURNAMES = _genres()
def name_ok(c, title):
    """파일 이름으로 거르기: 옛 음반, 클래식이 아닌 편곡, 다른 악기 편곡, 다른 작곡가의 곡이면 False"""
    if c.get("musopen") or c["f"] == "ia:" + MUSOPEN.get(title, "-"): return True
    q = AUDIO[title].split("|")[0].lower(); nm = urllib.parse.unquote(c["f"]).lower().replace("_", " ")
    if OLD.search(nm): return False
    if any(w in nm and w not in q for w in STYLE): return False
    if any(w in nm and w not in q and GENRE.get(title) not in ok for w, ok in INSTR.items()): return False
    if "piano" in nm and "piano" not in q and GENRE.get(title) == "실내악" and not re.search(r"quintet|quartet|trio|sonata", nm): return False
    qn = set(re.findall(r"\b(\d+)\b", q)); fn = set(re.findall(r"\bno\.? ?(\d+)", nm))   # 곡 번호가 다르면(헝가리 무곡 5번인데 1번 파일) 빼요
    if qn and fn and not fn & qn: return False
    mine = q.split()[0]
    if any(s in nm for s in SURNAMES if len(s) > 3 and s != mine and s not in q): return False
    return True
def _ffmpeg():   # PATH의 ffmpeg → 없으면 파이썬 패키지 imageio-ffmpeg 안의 것(Windows PC용)
    import shutil
    f = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if f: return f
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception: return "ffmpeg"
FFMPEG = _ffmpeg()
def get(u, binary=False, rng=None, tries=7):
    for n in range(tries):
        try:
            h = {"User-Agent": UA};
            if rng: h["Range"] = rng
            with urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=90) as r:
                # 서버가 Range 를 무시하고 파일 전체(수백 MB)를 천천히 보내면 r.read() 가 몇 시간 멈춰요(2026-11-26 실제로 겪음).
                # 그래서 필요한 만큼만, 정해진 시간(GET_DEADLINE초) 안에서만 읽어요.
                lim = int(rng.split("-")[1]) + 1 if rng else None; t0 = time.time(); buf = bytearray()
                while True:
                    ch = r.read(65536)
                    if not ch: break
                    buf += ch
                    if lim and len(buf) >= lim: del buf[lim:]; break
                    if time.time() - t0 > GET_DEADLINE:
                        try:
                            with open("music_pick_http.log", "a", encoding="utf-8") as lf: lf.write(time.strftime("%Y-%m-%d %H:%M:%S") + f"\tslow\t{len(buf)}B/{GET_DEADLINE}s\t{u.split('?')[0][:120]}\n")
                        except Exception: pass
                        break
                d = bytes(buf); time.sleep(PACE); return d if binary else json.loads(d.decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            if e.code in (429, 500, 502, 503, 504):
                try: ra = int(e.headers.get("Retry-After", "10"))
                except Exception: ra = 10
                wait = min(ra, 150) + 1 + n
                try:   # 요청 제한·서버 오류 기록(추적용, 주소의 물음표 뒤는 뺌)
                    with open("music_pick_http.log", "a", encoding="utf-8") as lf: lf.write(time.strftime("%Y-%m-%d %H:%M:%S") + f"\t{e.code}\t재시도{n+1}/{tries}\t대기{wait}s\tRetry-After={e.headers.get('Retry-After', '-')}\t{u.split('?')[0][:120]}\n")
                except Exception: pass
                time.sleep(wait); continue
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
            if not lic or not (PD.search(lic) or CC.search(lic)) or not ii.get("url"): continue
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
    """앞부분을 받아 30초를 분석해요(v2, 2026-11-24). 받은 내용은 디스크에 쓰지 않고 메모리에서 바로 ffmpeg 로 넘겨요. 남기는 건 숫자뿐이에요.
    corr = 높은 소리(7~15kHz)가 음악(300Hz~3kHz)을 따라 커지고 작아지는 정도. 판 잡음(쉬익·지직)은 음악과 상관없이 늘 깔려 있어 0에 가까워요.
    nf   = 조용한 부분에서 높은 소리가 얼마나 줄어드는지(dB). 잡음이 깔려 있으면 거의 안 줄어요(0 근처).
    옛 녹음 9개·최근 녹음 5개로 맞춰 본 기준: corr >= 0.45 이고 nf <= -4 이면 통과(옛 녹음 8개 제외, 최근 녹음 모두 통과, 남은 1개는 이름 규칙 OLD 로 제외)."""
    ext = os.path.splitext(c["f"].lower())[1]; n = 3_500_000 if ext not in LOSSY else 1_600_000
    d = get(c["url"], binary=True, rng=f"bytes=0-{n - 1}")
    if not d or len(d) < 50_000: return None
    try: r = subprocess.run([FFMPEG, "-v", "error", "-i", "pipe:0", "-t", "30", "-ac", "1", "-ar", "32000", "-f", "s16le", "-"], input=d, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired: return None
    d = None
    x = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float64) / 32768
    if len(x) < 32000 * 6: return None
    N = 2048; seg = x[:len(x) // N * N].reshape(-1, N) * np.hanning(N); P = np.abs(np.fft.rfft(seg, axis=1)) ** 2; f = np.fft.rfftfreq(N, 1 / 32000)
    tot = P.sum(1) + 1e-12; hf = P[:, (f >= 7000) & (f < 15000)].sum(1) + 1e-15; mid = P[:, (f >= 300) & (f < 3000)].sum(1) + 1e-15
    loud = tot >= np.percentile(tot, 70); quiet = tot <= np.percentile(tot, 20)
    if loud.sum() < 5 or quiet.sum() < 5: return None
    nf = float(10 * np.log10(np.median(hf[quiet]) / np.median(hf[loud]))); corr = float(np.corrcoef(np.log10(hf), np.log10(mid))[0, 1])
    db = 10 * np.log10(tot); dyn = float(np.percentile(db, 95) - np.percentile(db, 10))
    return {"v": 2, "corr": round(corr, 2), "nf": round(nf, 1), "dyn": round(dyn, 1)}
def good(a): return isinstance(a, dict) and a.get("v") == 2 and a["corr"] >= 0.45 and a["nf"] <= -4
def done(a): return (isinstance(a, dict) and (a.get("v") == 2 or "old" in a))   # 예전(v1) 숫자·서버 실패(None)는 다시 분석해요
IAF = os.path.join(HERE, "music_pick_ia.json"); SCRF = os.path.join(HERE, "music_pick_scr.json")
# 사용자 지적으로 소리를 뺀 곡(후보가 전부 1900~1930년대 옛 음반 녹음이라 잡음이 심해요): 글로만 나오게 해요
# 직접 지정한 녹음(2026-11-24 사용자 결정으로 CC BY·CC BY-SA 허용 → 옛 녹음뿐이던 곡에 현대 녹음을 지정, 앱이 라이선스를 다시 확인하고 녹음한 사람을 화면에 표시)
PINNED = {"토카타와 푸가 d단조": ["Bach, Toccata und Fuge d-moll BWV 565, Norbert Schenk.mp3", "Toccata et Fugue BWV565.ogg"], "사계": ["Vivaldi - Four Seasons 1 Spring mvt 1 Allegro - John Harrison violin.oga", "Vivaldi - Four Seasons 4 Winter Air Force Strings - United States Air Force Band.mp3"], "터키 행진곡(피아노 소나타 11번 중)": ["Mozart - Piano Sonata No. 11 in A major - III. Allegro (Turkish March).ogg"], "엘리제를 위하여": ["FurElise.ogg", "Fur Elise.ogg"], "마왕": ["Schubert's Erlkönig, D.328 - Michael Jackson.ogg"], "윌리엄 텔 서곡": ["Guillaume Tell - Overture - (Rossini, Gioacchino) by Fritz Reiner (conductor).mp3", "Gioachino Rossini, William Tell Overture (military band version, 2000).ogg"], "바이올린 협주곡 e단조": ["Hankyung Arte Philharmonic - Mendelssohn's Violin Concerto in E minor, Op. 64, MWV O 14 - I. Allegro molto appassionato.ogg", "Hankyung Arte Philharmonic - Mendelssohn's Violin Concerto in E minor, Op. 64, MWV O 14 - III. Allegretto non troppo-Allegro molto vivace.ogg"], "발퀴레의 기행": ["Ride of the Valkyries.ogg"], "아름답고 푸른 도나우": ["Strauss, An der schönen blauen Donau.ogg", "\"An der schönen, blauen Donau\", performed by the US Marine Band.mp3"], "백조(동물의 사육제 중)": ["Camille Saint-Saëns - Le Cygne (No. 13) - Matilda Colliard and Stefano Ligoratti.ogg", "20091104 Alisa Weilerstein and Jason Yoder - Saint Saëns' The Swan.ogg"], "헝가리 무곡 5번": ["Ungarischer Tanz Nr. 5 in fis-Moll, Klavier zu 4 Händen.oga"], "호두까기 인형": ["Tchaikovsky - Dance of the Sugar Plum Fairy - The Nutcracker.ogg", "Tchaikovsky - Nutcracker Suite - Russian Dance - Philip Milman - Lud and Schlatts Musical Emporium.wav"], "피아노 협주곡 1번 b♭단조": ["Tchaikovsky, Concerto No.1 in B-flat minor Op.23, I. Allegro.ogg"], "유모레스크": ["Dvořák - Humoresque Op. 101 No. 7.ogg"], "슬라브 무곡": ["Slavonic Dance No. 2 - Strolling Strings - United States Air Force Band.mp3"], "사랑의 인사": ["Edward Elgar - Salut d'amour, Op. 12 - Emanuel Salvador and Pau Casan (2011).ogg"], "달빛(베르가마스크 모음곡 중)": ["Clair de lune (Claude Debussy) Suite bergamasque.ogg"], "아라베스크 1번": ["Claude Debussy - Première Arabesque - Patrizia Prati.ogg"],   # 2026-11-26 확장 검색(music_extra_search.py)으로 찾은 녹음 중 설명을 읽고 원곡·실제 연주만 고름(AI 작곡·시 낭독·다른 곡·학생 연습·너무 큰 파일 제외). 음질 분석 전이라 이상하면 사용자가 알려 주면 뺌
          "차라투스트라는 이렇게 말했다": ["Also Sprach Zarathustra - Einleitung.ogg", "Richard Strauss - Also Sprach Zarathustra.ogg"], "교향곡 94번 '놀람'": ["Haydn; Symphony No. 94 \"Surprise\", 2. Andante.ogg", "Haydn; Symphony No. 94 \"Surprise\", 4. Finale (Allegro molto).ogg"], "아베 마리아(엘렌의 노래 3번)": ["Franz Schubert - Ellens dritter Gesang.oga"], "수상 음악": ["Handel's Water Music - 14. Lentement - Chamber Orchestra - United States Marine Band.opus"], "G선상의 아리아": ["Wiki naxos 8.550194 01 13.ogg"],   # 2026-11-26 곡 목록 전수 점검: 차라투스트라=컴퓨터 펑크 편곡·끝부분 → 「일출」 도입부, 놀람=놀람이 나오는 2악장, 아베 마리아=원곡(노래+피아노), 수상 음악=피리·북 행진대 편곡 뺌, G선상=출처 불분명한 모음집 대신 낙소스 공개 녹음
          "한여름 밤의 꿈 서곡": ["A Midsummer Night's Dream Op. 61 Overture (Mendelssohn) European Archive.ogg"], "결혼 행진곡(한여름 밤의 꿈 중)": ["A Midsummer Night's Dream Op. 61 Wedding March (Mendelssohn) European Archive.ogg"],   # 2026-11-26 사용자 지적 '한여름 밤의 꿈 이상함': 서곡 자리에 결혼 행진곡 녹음이 들어가 있었음 → 서곡은 서곡 녹음으로(Musopen 공개 도메인)
          "교향곡 9번 '합창'": ["PMLP01607-Symphony No.9, Op.125 (Beethoven, Ludwig van), IV Presto.ogg"],   # 2026-11-26 사용자 지적 '합창 음원 이상함': 55초짜리 2악장 조각 대신 「환희의 송가」가 나오는 4악장 전체(IMSLP 녹음, CC BY-SA 3.0, 위키미디어 오늘의 소리). 합창이 나오는 부분부터 재생(set44.py STARTS)
          "캐논 D장조": ["Kevin MacLeod - Canon in D Major.ogg", "Pachelbel's Canon.ogg"],   # 2026-11-26 사용자 지적 '하모니카 소리': 아카이브 파일은 하모니카+피아노 편곡(cover)이라 빼고, 현악기 원래 편성(케빈 맥클라우드, 가상 악기 녹음, CC BY 3.0)과 피아노 독주(CC BY-SA 3.0)로. 실제 현악 합주 녹음은 허용 라이선스로 못 찾음
          "볼레로": ["Bolero-Maurice Ravel-ORTF National Orchestra-Georges Tzipine-23 March 1965.ogg", "Bolero-Maurice Ravel-Paris Orchestra-Charles Munch-1956.ogg"],   # 2026-11-25 사용자 지적 '북소리가 손뼉 소리': 아카이브의 두 파일은 플라멩코 편곡(플루트+손뼉)이라 빼고 실제 관현악 녹음으로(ORTF 국립 관현악단·치핀 1965, 파리 관현악단·뮌시 1956, 공개 도메인)
          "라 트라비아타": ["\"Brindisi\" from La Traviata - Singing Sergeants - United States Air Force Band.mp3", "La Traviata - Act 1 - Libiamo ne' lieti calici.ogg"],   # 2026-11-28 사용자 지적: ICBSA 옛 음반 잡음 심함 → 미 공군 군악대·합창단 2011년 녹음 「축배의 노래」(공개 도메인), 예비 CC0
          "아이다": ["Triumphal March from Aida.ogg", "Aida-Trompeten.ogg"],   # 2026-11-27 사용자 지적: ICBSA(옛 음반) 잡음 심함 → 미 해병대 군악대 2002년 녹음 「개선 행진곡」(공개 도메인)
          "전주곡 c♯단조": ["Prélude en Do dièse mineur de Rachmaninov op. 3 (Morceaux de fantaisie).ogg"],
          "짐노페디": ["Satie Gymnopèdie n.1 DariaBaiocchi.wav", "Gymnopedie No. 1 (ISRC USUAN1100787).mp3"],   # 2026-11-27 사용자 확인: 기존 녹음(Michael Laucke)은 기타 편곡 → 피아노 녹음(다리아 바이오키 2021년 스타인웨이, CC BY-SA 4.0 / 케빈 맥클라우드, CC BY 3.0)
          "랩소디 인 블루": ["US Marine Band Rhapsody in Blue.oga"]}
NOAUDIO = {"라 보엠": "후보가 1907~1938년 옛 녹음뿐(2026-11-24 사용자 지적: 잡음이 심함)"}
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
        for t0 in NOAUDIO: res.pop(t0, None)
        for t0, fs in PINNED.items(): res[t0] = [{"f": f, "lic": "직접 지정", "kbps": None, "scr": None} for f in fs]
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
    seen = set()
    ia_only = "--ia-only" in a   # 위키 서버가 막혔을 때(429): 인터넷 아카이브 녹음만 분석하고, 위키 후보는 다음에(기존 목록은 지우지 않음)
    while True:
        st = load(STATE); ia = load(IAF); scr = load(SCRF); res = load(OUT); did = 0
        for n, t in enumerate(works, 1):
            if "cands" not in st.get(t, {}): continue   # 아직 1단계가 안 한 곡은 다음 바퀴에
            cands = sorted(st[t]["cands"] + [c for c in ia.get(t, {}).get("cands", []) if c["f"] not in {x["f"] for x in st[t]["cands"]}], key=lambda c: -c["score"])
            if t in MUSOPEN:
                it, fp = MUSOPEN[t].split("/", 1)
                cands = [{"f": "ia:" + MUSOPEN[t], "url": "https://archive.org/download/" + it + "/" + urllib.parse.quote(fp), "lic": "공개 도메인·CC0(인터넷 아카이브 표시, Musopen)", "kbps": 192, "score": 999, "musopen": 1}] + cands
            if ia_only: cands = [c for c in cands if c["f"].startswith("ia:")]
            cands = [c for c in cands if name_ok(c, t)]
            sc = scr.setdefault(t, {}); tried = 0
            for c in cands:
                if sum(1 for x in cands if good(sc.get(x["f"]))) >= 2 or tried >= 6: break
                if c["f"] in sc and done(sc[c["f"]]): continue
                if c["f"] in seen: continue   # 이번 실행에서 이미 시도해 실패(None)한 녹음은 다시 받지 않아요(--follow 가 끝없이 되풀이하던 문제, 2026-11-26)
                seen.add(c["f"])
                if c["f"].startswith("ia:") and not c.get("musopen"):   # 아카이브 항목에 적힌 녹음 연도가 1955년 전이면 옛 녹음
                    md = (get("https://archive.org/metadata/" + urllib.parse.quote(c["f"][3:].split("/")[0])) or {}).get("metadata") or {}
                    yr = re.search(r"(1[89]\d\d|20\d\d)", str(md.get("date") or md.get("year") or ""))
                    if yr and int(yr.group(1)) < 1955: sc[c["f"]] = {"old": int(yr.group(1))}; save(SCRF, scr); continue
                sc[c["f"]] = analyze(c); tried += 1; did += 1; save(SCRF, scr)
            ok_ = lambda c: good(sc.get(c["f"])) or (c.get("musopen") and isinstance(sc.get(c["f"]), dict) and sc[c["f"]].get("v") == 2)   # Musopen 은 출처가 현대 녹음이라 분석만 되면 써요(조용한 피아노곡은 숫자가 낮게 나와요)
            picked = sorted([c for c in cands if ok_(c)], key=lambda c: (-bool(c.get("musopen")), -(sc[c["f"]]["corr"] - sc[c["f"]]["nf"] / 20)))
            if picked: res[t] = [{"f": c["f"], "lic": c["lic"], "kbps": c["kbps"], "scr": sc.get(c["f"])} for c in picked[:2]]
            elif ia_only:   # 아카이브만 검사한 경우: 검사에서 떨어진 녹음은 목록에서 빼고, 아직 검사 안 한 위키 녹음만 남겨요
                keep = [x for x in res.get(t, []) if name_ok(x, t) and not (x["f"] in sc and done(sc[x["f"]]) and not good(sc[x["f"]]))]
                if keep: res[t] = keep
                else: res.pop(t, None)
            elif all(sc.get(c["f"]) is not None for c in cands[:4] if c["f"] in sc): res.pop(t, None)   # 분석이 서버 문제로 실패(None)한 곡은 기존 목록을 그대로 둬요
            for t0 in NOAUDIO: res.pop(t0, None)
            for t0, fs in PINNED.items(): res[t0] = [{"f": f, "lic": "직접 지정", "kbps": None, "scr": None} for f in fs]
            save(OUT, res)
            if tried or t in MUSOPEN: print(f"[{n}/{len(works)}] {'✓' if picked else '✗'} {t}: 후보 {len(cands)}개" + (f" → {picked[0]['f'][:60]} ({sc.get(picked[0]['f'])})" if picked else " → 쓸 만한 녹음 없음(글로만)"), flush=True)
        ready = all("cands" in st.get(t, {}) and ia.get(t, {}).get("done") for t in works)
        if not follow or (ready and did == 0): break
        time.sleep(60 if did == 0 else 1)
    res = load(OUT)
    print(f"\n음질 확인을 통과한 곡 {len(res)} / {len(works)}")
if __name__ == "__main__": main()
