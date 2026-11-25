# 글로만 나오는 클래식 곡의 녹음을 더 찾는 확장 검색(커먼즈: 곡 이름을 영어·독일어 등으로 바꿔 여러 번, 인터넷 아카이브: 작곡가+곡).
# 결과는 music_extra_cands.json 에 후보로만 적어요(음원 파일은 저장하지 않음). 음질 분석은 PC에서 `py music_pick.py --follow`(후보를 state에 합친 뒤)로 해요.
import os, re, sys, json, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import music_pick as m
HERE = os.path.dirname(os.path.abspath(__file__)); OUTF = os.path.join(HERE, "music_extra_cands.json")
Q = {  # 곡: [검색어들], (작곡가 낱말들 — 파일 이름·제목에 하나라도 있어야 함)
 "토카타와 푸가 d단조": (["Bach Toccata and Fugue D minor", "Toccata und Fuge d-Moll BWV 565", "Bach BWV 565 organ"], ["bach", "bwv 565", "bwv565"]),
 "사계": (["Vivaldi Four Seasons", "Vivaldi Spring La primavera", "Vivaldi Winter L'inverno", "Vivaldi Le quattro stagioni"], ["vivaldi", "seasons", "stagioni", "primavera", "inverno"]),
 "터키 행진곡(피아노 소나타 11번 중)": (["Mozart Rondo alla turca", "Mozart Turkish March piano sonata 11", "Mozart K. 331"], ["mozart", "turca", "turkish", "k. 331", "k331"]),
 "엘리제를 위하여": (["Beethoven Für Elise", "Beethoven Fur Elise piano", "Bagatelle No. 25 A minor"], ["elise", "bagatelle"]),
 "마왕": (["Schubert Erlkönig", "Schubert Erlking", "Erlkönig D 328"], ["erlk", "erlking"]),
 "피아노 오중주 '송어'": (["Schubert Trout Quintet", "Schubert Forellenquintett", "Schubert Die Forelle"], ["trout", "forelle", "forellen"]),
 "윌리엄 텔 서곡": (["Rossini William Tell Overture", "Rossini Guillaume Tell ouverture", "William Tell overture finale"], ["william tell", "guillaume tell", "wilhelm tell"]),
 "세비야의 이발사": (["Rossini Barber of Seville overture", "Rossini Il barbiere di Siviglia sinfonia", "Barber of Seville overture"], ["barber", "barbiere", "siviglia"]),
 "바이올린 협주곡 e단조": (["Mendelssohn Violin Concerto E minor", "Mendelssohn Violinkonzert e-Moll", "Mendelssohn Op. 64"], ["mendelssohn", "op. 64", "op.64"]),
 "트로이메라이": (["Schumann Träumerei", "Schumann Traumerei Kinderszenen", "Schumann Kinderszenen"], ["träumerei", "traumerei", "kinderszenen"]),
 "사랑의 꿈 3번": (["Liszt Liebestraum", "Liszt Liebestraum No. 3", "Liszt Nocturne Liebestraum"], ["liebestr", "liszt"]),
 "발퀴레의 기행": (["Wagner Ride of the Valkyries", "Wagner Walkürenritt", "Wagner Die Walküre ride"], ["valkyr", "walküre", "walkure", "walkuere"]),
 "아름답고 푸른 도나우": (["Strauss Blue Danube", "Johann Strauss An der schönen blauen Donau", "Blue Danube waltz"], ["danube", "donau"]),
 "봄의 소리 왈츠": (["Strauss Voices of Spring", "Johann Strauss Frühlingsstimmen", "Voices of Spring waltz"], ["voices of spring", "frühlingsstimmen", "fruhlingsstimmen"]),
 "동물의 사육제": (["Saint-Saëns Carnival of the Animals", "Saint-Saens Le carnaval des animaux", "Carnival of the Animals"], ["carnival", "carnaval", "animals", "animaux"]),
 "백조(동물의 사육제 중)": (["Saint-Saëns The Swan", "Saint-Saens Le cygne", "The Swan cello Saint-Saëns"], ["swan", "cygne"]),
 "헝가리 무곡 5번": (["Brahms Hungarian Dance No. 5", "Brahms Ungarischer Tanz Nr. 5", "Hungarian Dance 5"], ["hungarian", "ungarische", "ungarischer"]),
 "자장가": (["Brahms Lullaby", "Brahms Wiegenlied", "Brahms Lullaby Op. 49"], ["lullaby", "wiegenlied"]),
 "호두까기 인형": (["Tchaikovsky Nutcracker", "Tchaikovsky Nutcracker Dance of the Sugar Plum Fairy", "Tchaikovsky Nutcracker Waltz of the Flowers", "Tchaikovsky Nutcracker March"], ["nutcracker", "casse-noisette", "nussknacker"]),
 "1812년 서곡": (["Tchaikovsky 1812 Overture", "Tchaikovsky 1812 Ouverture solennelle"], ["1812"]),
 "피아노 협주곡 1번 b♭단조": (["Tchaikovsky Piano Concerto No. 1", "Tchaikovsky Piano Concerto B-flat minor", "Tchaikovsky Op. 23"], ["tchaikovsky", "op. 23", "op.23"]),
 "유모레스크": (["Dvořák Humoresque", "Dvorak Humoresque No. 7", "Humoresque Op. 101"], ["humoresque"]),
 "슬라브 무곡": (["Dvořák Slavonic Dance", "Dvorak Slavonic Dances Op. 46", "Slavonic Dance No. 1"], ["slavonic", "slavic", "slovanské"]),
 "파반": (["Fauré Pavane", "Faure Pavane Op. 50", "Pavane Fauré"], ["pavane"]),
 "솔베이그의 노래(페르 귄트 중)": (["Grieg Solveig's Song", "Grieg Solveigs Sang", "Peer Gynt Solveig"], ["solveig"]),
 "사랑의 인사": (["Elgar Salut d'amour", "Elgar Love's Greeting", "Salut d'Amour Op. 12"], ["salut", "love's greeting", "liebesgruss"]),
 "핀란디아": (["Sibelius Finlandia", "Finlandia Op. 26"], ["finlandia"]),
 "달빛(베르가마스크 모음곡 중)": (["Debussy Clair de lune", "Clair de lune Suite bergamasque", "Debussy Clair de Lune piano"], ["clair de lune"]),
 "아라베스크 1번": (["Debussy Arabesque No. 1", "Debussy Deux arabesques", "Arabesque Debussy"], ["arabesque"]),
 "목신의 오후 전주곡": (["Debussy Prélude à l'après-midi d'un faune", "Debussy Afternoon of a Faun", "Debussy Prelude Faune"], ["faune", "faun"]),
}
OKL = re.compile(r"^cc[- ]by(-sa)?[ -]\d|public domain|^pd\b|^pd-|cc0|cc-zero", re.I)
OLDY = re.compile(r"\b(18\d\d|19[0-5]\d)\b|78 ?rpm|victor|columbia|edison|gramophone|cylinder|midi|synth|arrang|for piano and|ringtone|karaoke|remix|cover", re.I)
def year_of(md):
    t = " ".join(re.sub(r"<[^>]+>", "", str((md.get(k) or {}).get("value", ""))) for k in ("DateTimeOriginal", "ImageDescription", "Credit")); ys = [int(y) for y in re.findall(r"\b(1[89]\d\d|20[0-2]\d)\b", t)]
    return ys
def commons(title, qs, toks):
    seen, out = set(), []
    for q in qs:
        d = m.api(action="query", list="search", srsearch=q + " filetype:audio", srnamespace=6, srlimit=25)
        names = [r["title"] for r in (d or {}).get("query", {}).get("search", []) if r["title"].lower().endswith(m.EXT) and r["title"] not in seen]
        for i in range(0, len(names), 12):
            c = m.api(action="query", prop="imageinfo", iiprop="extmetadata|url|size|metadata", titles="|".join(names[i:i + 12]))
            for p in ((c or {}).get("query", {}).get("pages", {}) or {}).values():
                ii = (p.get("imageinfo") or [{}])[0]; md = ii.get("extmetadata") or {}; lic = (md.get("LicenseShortName") or {}).get("value", ""); n = p["title"][5:]; seen.add(p["title"])
                if not lic or not OKL.search(lic) or not ii.get("url"): continue
                low = n.lower()
                if not any(t in low for t in toks) or OLDY.search(n) or re.search(r"^(LL-|De-|Nl-|En-|Fr-|It-|Es-)|pronunciation|spoken", n): continue
                ys = year_of(md)
                if ys and min(ys) < 1960 and not any(y >= 2000 for y in ys): continue    # 옛 녹음 가능성
                size = ii.get("size") or 0; dur = m.meta(ii, "length") or m.meta(ii, "playtime_seconds")
                if dur is not None and dur < 25: continue
                out.append({"f": n, "url": ii["url"], "lic": lic, "kbps": round(size * 8 / dur / 1000) if dur else None, "dur": round(dur) if dur else None, "size": size, "score": 100, "src": "commons"})
    return out
def archive(title, qs, toks):
    out = []
    for q in qs[:2]:
        qq = f'({q}) AND mediatype:audio AND (licenseurl:*publicdomain* OR licenseurl:*zero* OR licenseurl:*licenses/by/* OR licenseurl:*licenses/by-sa/*)'
        d = m.get("https://archive.org/advancedsearch.php?" + urllib.parse.urlencode({"q": qq, "fl[]": ["identifier", "title", "licenseurl", "date", "creator"], "rows": 10, "sort[]": "downloads desc", "output": "json"}, doseq=True))
        for doc in ((d or {}).get("response", {}).get("docs", []) or []):
            ttl = (str(doc.get("title", "")) + " " + doc["identifier"]).lower(); lic = str(doc.get("licenseurl", ""))
            if not any(t in ttl for t in toks) or OLDY.search(ttl) or re.search(r"/by-n[cd]|/by-nc", lic): continue
            dt = str(doc.get("date", ""))[:4]
            if dt.isdigit() and int(dt) < 1960: continue
            out.append({"f": "ia-item:" + doc["identifier"], "lic": lic[-40:], "title": str(doc.get("title", ""))[:70], "date": dt, "src": "archive"})
    return out
def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    res = json.load(open(OUTF, encoding="utf-8")) if os.path.exists(OUTF) else {}
    for title, (qs, toks) in Q.items():
        if only and title != only or title in res: continue
        c = commons(title, qs, toks); a = archive(title, qs, toks); res[title] = {"commons": c, "archive": a}
        json.dump(res, open(OUTF, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{title}: 위키 {len(c)} · 아카이브 {len(a)}", flush=True)
if __name__ == "__main__": main()
