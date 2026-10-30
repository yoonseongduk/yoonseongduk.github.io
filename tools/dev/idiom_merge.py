import re, json
S=""
rows=[]
for line in open(S+"idiom_data.txt",encoding="utf-8"):
    line=line.rstrip("\n").replace('\\"','"')
    if not line.strip(): continue
    f=line.split("|"); assert len(f)==5,line
    rows.append(f)
assert len(set(r[0] for r in rows))==len(rows) and len(set(r[2] for r in rows))==len(rows)
D=[[r[0],r[2],[],"",r[1]+" · "+r[3],r[4]] for r in rows]
p="out/yoonseongduk.github.io/idiom-quiz.html"; s=open(p,encoding="utf-8").read()
s=re.sub(r"const D = \[.*?\];\n", "const D = "+json.dumps(D,ensure_ascii=False)+";\n", s, 1, flags=re.S)
s=s.replace("// [문제, 정답, 틀린 보기(없으면 같은 분류의 다른 정답에서 뽑음), 분류, 해설]","// [사자성어, 뜻, 틀린 보기(비우면 다른 성어의 뜻에서 뽑음), 분류, 한자·풀이, 쓰이는 예시]")
s=s.replace('if (d[4]) $("q").insertAdjacentHTML("beforeend", `<span class="note">${esc(d[4])}</span>`);',
 'if (d[4]) $("q").insertAdjacentHTML("beforeend", `<span class="note"><b>📖 ${esc(d[4])}</b></span>` + (d[5] ? `<span class="note eg">💬 ${esc(d[5])}</span>` : ""));')
s=s.replace(".q .note{",".q .note.eg{background:var(--soft);border-radius:10px;padding:8px 10px;color:var(--fg)}\n.q .note{",1)
s=re.sub(r"(<p class=\"muted\">)[^<]*(</p>\n</main>)", lambda m: m.group(1)+"사자성어의 뜻을 맞혀 보세요. 정답을 고르면 한자와 풀이, 쓰이는 예시가 나와요. 사자성어 %d개가 들어 있어요."%len(D)+m.group(2), s, 1)
open(p,"w",encoding="utf-8").write(s); print(len(D))
