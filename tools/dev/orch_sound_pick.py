# 오케스트라 악기 도감 '🔊 소리 듣기'용 악기 소리 고르기(2026-11-24, 사용자 요청: 오래된 녹음은 빼고 최신 소리, 음질 확인).
#   실행(PC, tools\dev): py orch_sound_pick.py  → orch_sound.json({악기id: [커먼즈 파일 이름, …]} 좋은 순서) → py set45.py → ship
#   독주곡 우선(2026-11-24 사용자 요청): 그 악기 하나로 연주한 곡(solo·suite·partita·sonata·etude…)을 먼저, 없으면 악기 소리 견본(음계·한 음). 합주·반주가 있는 녹음은 빼요.
#   고르는 기준: ① 커먼즈에서 악기 이름으로 찾은 음원 중 파일 이름에 악기 낱말이 있고 다른 악기·노래·옛 녹음 낱말이 없는 것
#              ② 라이선스가 공개 도메인·CC0 표시, 없으면 CC BY·CC BY-SA(2026-11-24 사용자 결정, 녹음한 사람·라이선스를 화면에 표시)  ③ 올린 날 2005년 이후(오래된 SP판 복각 제외), 길이 2초~3분
#              ④ 음질 분석(music_pick.py 의 잡음 분석 v2와 같은 방식, 짧은 소리에 맞게 2초부터): corr >= 0.45, nf <= -4
#   받은 소리는 메모리에서만 분석하고 디스크에 저장하지 않아요. 남기는 건 숫자뿐이에요(orch_sound_scr.json).
import json, os, re, sys, time, subprocess, urllib.parse
import numpy as np
from orch_data import INSTR
import music_pick as mp

PD = re.compile(r"public domain|^pd\b|^pd-|cc0|cc-zero", re.I)
CCOK = re.compile(r"^cc[ -]by(?:[ -]sa)?[ -][\d.]+", re.I)   # CC BY·CC BY-SA(2026-11-24 사용자 결정: 악기 소리는 녹음한 사람 표시 조건으로 허용, 비영리·변경금지 제외). online.js 의 CCOK 와 같은 규칙
EXT = (".ogg", ".oga", ".opus", ".mp3", ".flac", ".wav")
SOLOQ = {"violin": ["violin solo", "partita violin", "caprice violin"], "viola": ["viola solo"], "cello": ["cello solo", "cello suite"], "doublebass": ["double bass solo"],
         "harp": ["harp solo"], "flute": ["flute solo", "syrinx flute"], "piccolo": ["piccolo solo"], "oboe": ["oboe solo"], "englishhorn": ["english horn solo"], "clarinet": ["clarinet solo"],
         "bassoon": ["bassoon solo"], "trumpet": ["trumpet solo"], "horn": ["horn solo"], "trombone": ["trombone solo"], "tuba": ["tuba solo"], "timpani": ["timpani solo"],
         "snaredrum": ["snare drum solo"], "xylophone": ["xylophone solo"], "glockenspiel": ["glockenspiel"], "piano": ["piano solo", "piano musopen"], "celesta": ["celesta"], "organ": ["organ solo", "organ prelude"]}
SOLO = re.compile(r"solo|suite|partita|sonata|caprice|capriccio|etude|étude|study|prelude|fantasia|fantasy|syrinx|sequenza|invention|nocturne|waltz|impromptu|toccata|chorale|improvis|piece|melody|song without", re.I)
QUERY = {"englishhorn": ["cor anglais", "english horn"], "horn": ["french horn", "horn"], "gong": ["tam-tam", "gong"], "doublebass": ["double bass", "contrabass"],
         "organ": ["pipe organ", "organ"], "snaredrum": ["snare drum"], "bassdrum": ["bass drum"], "cymbals": ["cymbal"], "triangle": ["triangle instrument", "triangle"]}
# 파일 이름에 있어야 하는 낱말(하나라도), 있으면 안 되는 낱말
NEED = {"violin": ["violin"], "viola": ["viola"], "cello": ["cello", "violoncello"], "doublebass": ["double bass", "double-bass", "doublebass", "contrabass", "kontrabass"],
        "harp": ["harp"], "flute": ["flute"], "piccolo": ["piccolo"], "oboe": ["oboe"], "englishhorn": ["cor anglais", "english horn", "english_horn", "englishhorn"],
        "clarinet": ["clarinet"], "bassoon": ["bassoon"], "contrabassoon": ["contrabassoon", "contra-bassoon", "contrafagot"], "trumpet": ["trumpet"],
        "horn": ["french horn", "french_horn", "horn"], "trombone": ["trombone"], "tuba": ["tuba"], "timpani": ["timpani", "timpano"], "snaredrum": ["snare"],
        "bassdrum": ["bass drum", "bass_drum", "bassdrum"], "cymbals": ["cymbal"], "triangle": ["triangle"], "xylophone": ["xylophone"], "glockenspiel": ["glockenspiel"],
        "gong": ["tam-tam", "tamtam", "tam tam", "gong"], "tambourine": ["tambourine"], "castanets": ["castanet"], "piano": ["piano"], "celesta": ["celesta"], "organ": ["organ"]}
OTHER = {k: v for k, v in NEED.items()}
BADW = re.compile(r"song|anthem|national|hymn|march|lied|aria|choir|vocal|sing|voice|rap\b|beat|loop|remix|dance|rock|jazz|pop\b|blues|guitar|synth|midi|8-?bit|chiptune|"
                  r"toy|kid|plastic|harmonica|accordion|ukulele|kalimba|ocarina|recorder|bagpipe|sax|mouth|jew|ring ?tone|alarm|siren|bell tower|church bell|"
                  r"wine ?glass|glass harp|sound effect|sfx|bird|whale|insect|frog|cat\b|dog\b|nose|electric|e-?bass|bass guitar|kick|808|drum ?kit|drumset|drum set|"
                  r"tabla|djembe|conga|bongo|steel ?pan|marimba|vibraphone|hand ?pan|jingle|sleigh|chime|bowl|didgeridoo|bugle|cornet|flugel|euphonium|baritone|sousaphone|"
                  r"cimbalom|dulcimer|zither|lyre|celtic|irish|folk|fiddle|erhu|haegeum|gayageum|koto|pipa|sitar|organ grinder|hammond|harmonium|reed organ|"
                  r"orchestra|quartet|quintet|sextet|trio\b|ensemble|band\b|duet|duo\b|with piano|and piano|accompan|player piano|pianola|toy piano|prepared|honky|tack|ragtime|boogie|wurlitzer|rhodes|clavinet|melodica|kazoo", re.I)
# 신시사이저·발음 녹음(Lingua Libre 등 "xx-낱말")·말소리·배 경적·가믈란·합주(협주곡·관악 합주)·드럼앤베이스 같은 것
BADW2 = re.compile(r"arp-|solina|tr-?\d{3}|\bwave\b|\d+ ?hz|ll-q\d|speaks|spoken|interview|transplant|\buss\b|\bship\b|haus-des|bali|gamelan|x is for|creation|mirum|requiem|\bnage\b|snorkel|"
                   r"concerto|airmen of note|brass|meditation|drum roll with|harp'? stud|\.mid$|isrc|macleod|\bhey\b|drum (&|and) bass|basset|backwa|music box|instrumental", re.I)
LANG = re.compile(r"^[a-z]{2,3}(-[a-z]{2,4})?-")   # 발음 녹음 파일 이름(De-at-…, En-us-…, Ig-…)
OLDREC = re.compile(r"\b(18\d\d|19[0-4]\d)\b|victor|columbia|edison|gramophone|berliner|\b78 ?rpm\b|cylinder|shellac|vinyl|lp rip|karaoke|\bcover\b|remix|ringtone", re.I)   # 옛 음반·복각(music_pick.BAD 중 녹음 시대 낱말)
NOPICK = re.compile(r"pararira|arp-solina|horn fifths|clarinetreed|horn-bad meinberg|^[a-z]+( [a-z])? 0\d( [lr])?\.wav$", re.I)   # 마지막 꼴: Musopen 「피가로의 결혼」 서곡 악기별 마이크 녹음(Clarinet 03.wav·Bassoon 02.wav·Viola B 03.wav…) — 오케스트라 전체가 들려 악기마다 같은 음원처럼 들림(2026-11-24 사용자 지적)   # 눈으로 본 이름이 악기 연주가 아닌 것(리드만 부는 소리·자동차 경적일 수 있는 것)
# 이름 규칙으로는 못 고르거나 엉뚱한 것만 걸리는 악기는 설명(커먼즈 파일 설명)을 읽고 직접 정해요(2026-11-24, CC BY·CC BY-SA 허용 뒤).
#   글로켄슈필: 독일어 Glockenspiel 은 시청 탑의 종(카리용)이라 후보가 거의 다 탑 종소리 → 연극 음악 한 곡만. 작은북: 효과(리버브·마이크 번짐 시연) 없는 소리 견본.
#   콘트라베이스·콘트라바순·캐스터네츠: 이름 규칙(jazz·다른 악기 이름·스페인어 이름)에 걸려서 설명으로 확인. 잉글리시 호른은 커먼즈에 쓸 녹음이 없어(발음 녹음·자동차 경적뿐) 인터넷 아카이브에는 특수 주법 견본뿐이라 소리 없음(사용자 결정).
# 2026-11-24 사용자 지적(클라리넷·바순 소리가 같음): Musopen 「피가로의 결혼」 서곡 악기별 마이크 녹음(Clarinet 03.wav 등)은 오케스트라 전체가 들려 모두 빼고(NOPICK), 설명을 읽고 그 악기 독주 부분이 있는 녹음으로 바꿈.
PICK = {"trombone": ["RakeoianAnthem (trombone solo).wav", "Pedal tone demonstration.ogg", "Gustav Mahler - Trombone Solo from 3rd Symphony, 1st movement.ogg"],   # 2026-11-24 사용자 요청 '트럼본 음원 바꿔줘': 연주법 시범(플러터 텅잉·다중음) 대신 사람이 부는 트럼본 독주 가락, 보통 음역+페달 톤 시범, 말러 3번 교향곡 트럼본 독주 부분
        "horn": ["Paul Dukas - Villanelle for horn & piano (Dennis Brain, Gerald Moore, 1952).flac"],   # 2026-11-24 사용자가 준 호른 명곡 목록(뒤카스 빌라넬)에서 찾음: 호른의 거장 데니스 브레인의 1952년 애비 로드 스튜디오 녹음(공개 도메인 표시, 프랑스 국립도서관 자료). 1960년 전 녹음이라 잡음 규칙의 예외로 직접 지정
        "trumpet": ["Trumpet playing short excerpt for comparison with flugelhorn.ogg", "Trompetensolo Ich hatt einen Kameraden.ogg", "Flaggenparade der deutschen Bundeswehr, Trompetensignal (Studio).ogg"],   # 2026-11-24 사용자 확인 요청: 사람이 직접 분 Bb 트럼펫 녹음(보통 트럼펫 가락, 독일 군악 트럼펫 독주 2곡). 이전의 탑 위 신호 나팔·MIDI풍 「트럼펫 볼런터리」·천연 트럼펫 견본은 뺌
        "harp": ["Glissando Imprecision for 2 Harps.ogg"],   # 2026-11-24 사용자 지적 "하프 소리가 이상함": 배음(플라제올렛) 시범 대신 하프 두 대의 글리산도 곡(현대 녹음, CC BY-SA 3.0)
        "viola": ["Viola.ogg", "Viola CGDA.ogg"],                                         # 혼자 연주한 55초 가락, 개방현 C·G·D·A
        "clarinet": ["A-Klarinette, Rachmaninov 2 II.ogg", "B-Klarinette, Beeth 8.III.ogg", "Clarinette game chromatique.ogg"],   # 교향곡 속 클라리넷 독주 부분(Richard Haynes 소리 예), 반음계
        "bassoon": ["Bassoon rimsky.ogg", "Bassoon beethoven.ogg", "Bassoon-technical-range.ogg"],                               # 셰에라자드·베토벤 4번의 바순 독주 부분, 음역
        "oboe": ["Ferling Oboe Study No 28 Aaron Hill.ogg", "Oboe Sonata No. 2 in F by Francois Devienne Op 70.ogg"],
        "timpani": ["Timpani 64-c-p5.wav", "Timpani F major triad.ogg"],
        "trumpet": ["Cracow trumpet signal.ogg", "Clarke Trumpet Voluntary.ogg", "Natural trumpet B-flat.ogg"],                # 크라쿠프 성당 탑의 나팔 신호(혼자 부는 곡, 공개 도메인), 클라크 트럼펫 볼런터리(트럼펫·오르간)
                   # 비올라 혼자 연주한 55초 가락(곡명 없음, CC BY-SA 2.5, 여러 위키백과 비올라 항목에 쓰임) 먼저. 비올라 독주곡 녹음은 커먼즈·아카이브에 허용 라이선스로 없음(2026-11-24 확인: 비올라 다 감바·협주곡·피아노 반주뿐)
        "englishhorn": ["Antonin Dvorak - symphony no. 9 in e minor 'from the new world', op. 95 - ii. largo.ogg"],   # 드보르자크 신세계 2악장(Musopen 관현악, 공개 도메인): 금관 화음 뒤 잉글리시 호른 독주(사용자가 알려 준 곡, 2026-11-24). 특수 주법 견본은 뺌. 시벨리우스 투오넬라의 백조는 커먼즈에 녹음 없음, 힌데미트 소나타는 곡 저작권이 남아 제외. 같은 곡의 Dvorak S9M2 100501.ogg 는 컴퓨터 악기 소리라 제외
        "doublebass": ["Jazz walking bass on double bass.oga"],                       # 콘트라베이스 혼자 워킹 베이스, CC BY 2.5
        "contrabassoon": ["Contra2.ogg"],                                              # 바흐 무반주 첼로 모음곡 일부를 콘트라바순으로, CC BY-SA 3.0
        "castanets": ["Fundación Joaquín Díaz - ATO 00704 17 - Diferentes toques de castañuelas.ogg", "Fundación Joaquín Díaz - ATO 00810 13 - Toques de castañuelas.ogg"],
        "snaredrum": ["Snare drum unmuffled.ogg", "Snare drum muffled.ogg", "Snare drum rim.ogg"],
        "bassdrum": ["Bass drum.ogg"],
        "xylophone": ["Xylophone jingle.wav"],
        "glockenspiel": ["Vals folías (Glockenspiel).mp3"]}
def name_ok(iid, t):
    s = t.lower().replace("_", " ")
    if not any(w.replace("_", " ") in s for w in NEED[iid]): return False
    if mp.OLD.search(s) or BADW.search(s) or BADW2.search(s) or LANG.match(s) or OLDREC.search(s): return False
    for k, ws in OTHER.items():   # 다른 악기 이름이 같이 있으면(합주·비교 녹음) 빼요
        if k == iid or (iid, k) in {("contrabassoon", "bassoon"), ("englishhorn", "horn"), ("doublebass", "bassdrum"), ("bassdrum", "doublebass"), ("piccolo", "flute"), ("timpani", "timpani")}: continue
        if k == "horn" and iid != "horn": ws = ["french horn", "horn "]
        if k == "organ" and iid != "organ": ws = ["organ"]
        if k == "bassoon" and iid == "contrabassoon": continue
        if any(w.replace("_", " ") in s for w in ws) and not (iid == "contrabassoon" and k == "bassoon"): return False
    if iid == "horn" and re.search(r"english horn|cor anglais|post ?horn|alphorn|shofar|car horn|horns? section|basset", s): return False
    if iid == "bassoon" and "contra" in s: return False
    if iid == "flute" and re.search(r"piccolo|pan ?flute|bansuri|shakuhachi|alto flute|bass flute|tin whistle|recorder|native|nose|dizi", s): return False
    if iid == "triangle" and not re.search(r"triangle (instrument|\(instrument|percussion|hit|roll|strike|sample|sound)|triangle\.\w+$|triangle roll|triangle ", s): return False
    return True

def search(q):
    d = mp.api(action="query", list="search", srsearch=q + " filetype:audio", srnamespace=6, srlimit=50)
    return [r["title"] for r in (d or {}).get("query", {}).get("search", [])]
def info(names):
    out = []
    for k in range(0, len(names), 20):
        c = mp.api(action="query", prop="imageinfo", iiprop="extmetadata|url|size|metadata|timestamp", titles="|".join(names[k:k + 20]))
        for p in ((c or {}).get("query") or {}).get("pages", {}).values():
            ii = (p.get("imageinfo") or [{}])[0]; md = ii.get("extmetadata") or {}
            dt = (md.get("DateTimeOriginal") or {}).get("value", "")
            yrs = [int(y) for y in re.findall(r"\b(1[89]\d\d|20\d\d)\b", re.sub(r"<[^>]+>", " ", dt))]
            out.append({"f": p["title"][5:], "url": ii.get("url"), "size": ii.get("size") or 0, "lic": (md.get("LicenseShortName") or {}).get("value", ""),
                        "dur": mp.meta(ii, "length") or mp.meta(ii, "playtime_seconds"), "up": (ii.get("timestamp") or "")[:4], "made": min(yrs) if yrs else None})
    return out

def analyze(c):
    """music_pick.analyze 와 같은 잡음 분석 v2. 악기 소리는 짧아서 2초부터, 앞 30초만."""
    n = 1_500_000
    d = mp.get(c["url"], binary=True, rng=f"bytes=0-{n - 1}")
    if not d or len(d) < 4_000: return None
    r = subprocess.run([mp.FFMPEG, "-v", "error", "-i", "pipe:0", "-t", "30", "-ac", "1", "-ar", "32000", "-f", "s16le", "-"], input=d, capture_output=True); d = None
    x = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float64) / 32768
    if len(x) < 32000 * 2: return None
    N = 1024; seg = x[:len(x) // N * N].reshape(-1, N) * np.hanning(N); P = np.abs(np.fft.rfft(seg, axis=1)) ** 2; f = np.fft.rfftfreq(N, 1 / 32000)
    tot = P.sum(1) + 1e-12; hf = P[:, (f >= 7000) & (f < 15000)].sum(1) + 1e-15; mid = P[:, (f >= 300) & (f < 3000)].sum(1) + 1e-15
    loud = tot >= np.percentile(tot, 70); quiet = tot <= np.percentile(tot, 20)
    if loud.sum() < 5 or quiet.sum() < 5: return None
    nf = float(10 * np.log10(np.median(hf[quiet]) / np.median(hf[loud]))); corr = float(np.corrcoef(np.log10(hf), np.log10(mid))[0, 1])
    peak = float(np.max(np.abs(x))); clip = float(np.mean(np.abs(x) > 0.985))
    return {"v": 2, "corr": round(corr, 2), "nf": round(nf, 1), "peak": round(peak, 2), "clip": round(clip, 4), "sec": round(len(x) / 32000, 1)}
def good(a): return isinstance(a, dict) and a.get("v") == 2 and a["corr"] >= 0.45 and a["nf"] <= -4 and a["clip"] < 0.002 and a["peak"] > 0.05

def wait_upload():   # 소리 서버(upload.wikimedia.org)가 429(요청 제한)면 풀릴 때까지 기다려요(검색 서버와 따로 막혀요)
    import urllib.request, urllib.error
    while True:
        try:
            urllib.request.urlopen(urllib.request.Request("https://upload.wikimedia.org/wikipedia/commons/2/2b/Violin_vibrato.ogg", headers={"User-Agent": mp.UA, "Range": "bytes=0-99"}), timeout=30).read(); return
        except urllib.error.HTTPError as e:
            if e.code != 429: return
            w = max(600, int(e.headers.get("Retry-After") or 120)); print("  소리 서버 429, 기다림", w, "초", flush=True); time.sleep(w)   # 자주 물어보면 제한이 계속 이어져서 10분씩 쉬어요
        except Exception: time.sleep(30)
def main():
    # 1단계: 후보 찾기(검색 서버) → orch_sound_cand.json   2단계: 음질 분석(소리 서버, 429면 기다림) → orch_sound.json
    scr = mp.load("orch_sound_scr.json"); cand = mp.load("orch_sound_cand.json"); res = mp.load("orch_sound.json")
    only = [a for a in sys.argv[1:] if not a.startswith("-")]; ids = [x[0] for x in INSTR if not only or x[0] in only]
    for x in INSTR:
        iid = x[0]
        if iid not in ids or (iid in cand and "--research" not in sys.argv): continue
        names = []
        for q in SOLOQ.get(iid, []) + QUERY.get(iid, [x[2]]):
            for t in search(q):
                if t.lower().endswith(EXT) and t not in names and name_ok(iid, t[5:]): names.append(t)
        cs = [c for c in info(names) if (PD.search(c["lic"]) or CCOK.match(c["lic"])) and c["url"] and c["size"] <= 25_000_000 and (c["dur"] is None or 2 <= c["dur"] <= 900)
              and (c["up"] or "9999") >= "2005"]
        cs.sort(key=lambda c: (0 if SOLO.search(c["f"]) and (c["dur"] or 0) >= 15 else 1, 0 if PD.search(c["lic"]) else 1, -(c["made"] or 0)))   # 독주곡 먼저, 공개 도메인·CC0 먼저, 최근 녹음 먼저
        cand[iid] = cs; mp.save("orch_sound_cand.json", cand)
        print(iid, "후보", len(names), "PD·CC", len(cs), "PD", sum(1 for c in cs if PD.search(c["lic"])), "독주곡 후보", sum(1 for c in cs if SOLO.search(c["f"]) and (c["dur"] or 0) >= 15), flush=True)
    if "--cand" in sys.argv: return
    if "--names-only" in sys.argv:   # 소리 서버가 429로 막혔을 때(2026-11-24): 음질 분석 없이 이름 규칙·녹음 연도로만 골라요. 풀리면 옵션 없이 다시 실행해 분석해요.
        for iid in ids:
            res[iid] = PICK.get(iid) or [c["f"] for c in cand.get(iid, []) if not NOPICK.search(c["f"]) and (c["made"] is None or c["made"] >= 1955 or (c["dur"] or 0) < 15)][:3]
        mp.save("orch_sound.json", res); print("소리가 있는 악기(분석 전):", sum(1 for v in res.values() if v), "/", len(res)); return
    wait_upload()
    for iid in ids:
        if iid in PICK: res[iid] = PICK[iid]; mp.save("orch_sound.json", res); continue   # 직접 정한 악기는 분석하지 않고 그대로
        ok = []
        for c in cand.get(iid, [])[:8]:
            a = scr.get(c["f"])
            if a is None:
                a = analyze(c)
                if a is None: wait_upload(); a = analyze(c)
                scr[c["f"]] = a if a is not None else {"fail": 1}; mp.save("orch_sound_scr.json", scr)
            if good(a): ok.append(((1 if SOLO.search(c["f"]) and a["sec"] >= 15 else 0), a["corr"] - a["nf"] / 20, c["f"]))
            if len(ok) >= 3 and sum(o[0] for o in ok) >= 2: break
        ok.sort(reverse=True); res[iid] = [f for _, _, f in ok[:3]]; mp.save("orch_sound.json", res)
        print(iid, "통과", len(ok), "독주곡", sum(1 for o in ok if o[0]), "→", res[iid][:1], flush=True)
    print("소리가 있는 악기:", sum(1 for v in res.values() if v), "/", len(res), flush=True)
if __name__ == "__main__": main()
