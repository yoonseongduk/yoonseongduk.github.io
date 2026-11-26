# 게임이 시작 화면에 추가된 날짜 관리(신작 표시용). ship.py 가 자동 실행해요.
#   game_added.json = {파일: "YYYY-MM-DD"} — 한 번 정하면 바뀌지 않아요(파일을 다시 고쳐도 신작이 되지 않게).
#   처음 보는 파일은 git 기록의 '처음 추가된 날'을, 기록이 없으면 오늘 날짜를 써요.
#   index.html 의 /*ADDED*/…/*/ADDED*/ 칸에는 최근 30일 안에 추가된 게임만 넣어요(시작 화면이 신작 기준(14일)으로 거름).
import json, os, re, subprocess, datetime
R = "../../"
P = "game_added.json"
idx = open(R + "index.html", encoding="utf-8").read()
games = re.findall(r'^\s*\["([^"]+\.html)",', idx[idx.index("const GAMES = ["):], re.M)
data = json.load(open(P, encoding="utf-8")) if os.path.exists(P) else {}
today = datetime.date.today().isoformat()
first = {}
todo = [g for g in games if g not in data]
if todo:
    try:   # git 기록에서 파일마다 처음 추가된 날(얕은 복제면 정확하지 않을 수 있어요)
        out = subprocess.run(["git", "log", "--diff-filter=A", "--format=@%ad", "--date=short", "--name-only", "--reverse", "--", "*.html"],
                             cwd=R, capture_output=True, text=True, check=True).stdout
        d = None
        for line in out.splitlines():
            if line.startswith("@"): d = line[1:]
            elif line.strip() and line.strip() not in first: first[line.strip()] = d
    except Exception:
        pass
    for g in todo:
        if g not in first:   # 이름을 바꾼 파일은 --follow 로 옛 이름의 첫 추가 날짜를 찾아요
            try:
                o = subprocess.run(["git", "log", "--follow", "--format=%ad", "--date=short", "--", g], cwd=R, capture_output=True, text=True).stdout.split()
                if o: first[g] = o[-1]
            except Exception: pass
        data[g] = first.get(g, today)
json.dump(dict(sorted(data.items())), open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
cut = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
recent = {g: data[g] for g in games if data.get(g, "") >= cut}
# 🔧 업데이트: 최근 30일 안에 그 게임 파일을 고친 커밋의 가장 늦은 날짜. 한 번에 게임 화면 9개 이상을 고친 커밋은
#   공통 틀·머리글 같은 일괄 수정이라 빼요(UPD_MAX). 추가된 날과 같은 날 고친 것도 빼요(신작으로 이미 보임).
UPD_MAX = 8
upd = {}
try:
    out = subprocess.run(["git", "log", "--since=" + cut, "--format=@%ad", "--date=short", "--name-only", "--", "*.html"],
                         cwd=R, capture_output=True, text=True, check=True).stdout
    gs = set(games); commits = []; cur = None
    for line in out.splitlines():
        if line.startswith("@"): cur = [line[1:], []]; commits.append(cur)
        elif line.strip() in gs and cur: cur[1].append(line.strip())
    for d, fs in commits:
        if 0 < len(fs) <= UPD_MAX:
            for f in fs:
                if d > data.get(f, "") and d > upd.get(f, ""): upd[f] = d
except Exception:
    pass
block = "/*ADDED*/const ADDED = " + json.dumps(recent, ensure_ascii=False) + ", UPDATED = " + json.dumps(dict(sorted(upd.items())), ensure_ascii=False) + ";/*/ADDED*/"
if "/*ADDED*/" in idx:
    idx = re.sub(r"/\*ADDED\*/.*?/\*/ADDED\*/", lambda m: block, idx, flags=re.S)
else:
    idx = idx.replace("/*NUM*/", block + "\n/*NUM*/", 1)
open(R + "index.html", "w", encoding="utf-8").write(idx)
print("추가 날짜:", len(data), "개 기록 · 최근 30일 추가", len(recent), "개 · 최근 30일 업데이트", len(upd), "개")
