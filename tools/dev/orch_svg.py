# 오케스트라 악기 그림(SVG). 직접 그린 단순한 그림이에요(저작권 문제 없음, 인터넷 없이 항상 나와요).
# 120x120 칸, 밝은 바탕 위에 그려서 밝은/어두운 화면 모두에서 잘 보여요.
WOOD, WOOD2, DARK, BRASS, BRASS2, SILVER, SILVER2, SKIN, RED = "#c47a35", "#7a431a", "#2c2a29", "#e2b43a", "#a97f12", "#cfd6de", "#8d98a5", "#f3e3c3", "#b5342b"
BG = '<rect width="120" height="120" rx="14" fill="#f6efe0"/>'
def svg(body, label): return f'<svg viewBox="0 0 120 120" role="img" aria-label="{label}" xmlns="http://www.w3.org/2000/svg">{BG}{body}</svg>'
def rot(body, deg, cx=60, cy=60): return f'<g transform="rotate({deg} {cx} {cy})">{body}</g>'

def bowed(s, endpin=False, bass=False):
    """바이올린 계열: s=크기. 위에서부터 소용돌이·목·몸통(두 번 불룩)·줄·브리지."""
    cx = 60; tr = 12 * s
    body = f'<ellipse cx="{cx}" cy="{64}" rx="{15*s:.1f}" ry="{12*s:.1f}" fill="{WOOD}" stroke="{WOOD2}" stroke-width="2"/>'
    body += f'<ellipse cx="{cx}" cy="{88}" rx="{19*s:.1f}" ry="{15*s:.1f}" fill="{WOOD}" stroke="{WOOD2}" stroke-width="2"/>'
    body += f'<rect x="{cx-10*s:.1f}" y="66" width="{20*s:.1f}" height="14" fill="{WOOD}"/>'
    body += f'<rect x="{cx-3}" y="14" width="6" height="52" rx="2" fill="{DARK}"/><circle cx="{cx}" cy="11" r="5" fill="{WOOD2}"/>'
    for dx in (-1.5, -0.5, 0.5, 1.5): body += f'<line x1="{cx+dx}" y1="16" x2="{cx+dx}" y2="{96}" stroke="#e9e9e9" stroke-width=".7"/>'
    body += f'<rect x="{cx-7*s:.1f}" y="88" width="{14*s:.1f}" height="2.5" fill="{WOOD2}"/>'
    body += f'<path d="M{cx-9*s:.1f} 80 q-3 6 0 10 M{cx+9*s:.1f} 80 q3 6 0 10" stroke="{DARK}" stroke-width="1.6" fill="none"/>'
    if endpin: body += f'<line x1="{cx}" y1="{88+15*s:.1f}" x2="{cx}" y2="114" stroke="{DARK}" stroke-width="2.5"/>'
    if bass: body += f'<path d="M{cx-19*s:.1f} 70 L{cx-14*s:.1f} 60 M{cx+19*s:.1f} 70 L{cx+14*s:.1f} 60" stroke="{WOOD2}" stroke-width="2"/>'
    body += f'<line x1="22" y1="108" x2="98" y2="26" stroke="{DARK}" stroke-width="1.6" opacity=".55"/>'   # 활
    return body

def keys(x0, x1, y, n, r=2.2, col=SILVER2):
    step = (x1 - x0) / (n - 1); return "".join(f'<circle cx="{x0+i*step:.1f}" cy="{y}" r="{r}" fill="{col}"/>' for i in range(n))

ICONS = {}
ICONS["violin"] = bowed(0.78)
ICONS["viola"] = bowed(0.9)
ICONS["cello"] = bowed(1.0, endpin=True)
ICONS["doublebass"] = bowed(1.08, endpin=True, bass=True)
# 하프
ICONS["harp"] = f'<path d="M34 100 L34 28 Q34 14 52 18 Q86 28 96 46 L96 100 Z" fill="none" stroke="{BRASS2}" stroke-width="5" stroke-linejoin="round"/>' + "".join(f'<line x1="{36+i*3.6:.1f}" y1="{100-i*0.4:.1f}" x2="{44+i*3.9:.1f}" y2="{26+i*3.0:.1f}" stroke="#555" stroke-width=".9"/>' for i in range(15)) + f'<rect x="30" y="98" width="70" height="8" rx="3" fill="{BRASS}"/>'
# 목관: 가로로 그린 뒤 비스듬히
ICONS["flute"] = rot(f'<rect x="6" y="56" width="108" height="8" rx="4" fill="{SILVER}" stroke="{SILVER2}"/><ellipse cx="26" cy="52" rx="5" ry="3" fill="{SILVER2}"/>{keys(44,104,60,8)}', -28)
ICONS["piccolo"] = rot(f'<rect x="26" y="57" width="68" height="6" rx="3" fill="{WOOD}" stroke="{WOOD2}"/><ellipse cx="38" cy="54" rx="3.5" ry="2.2" fill="{WOOD2}"/>{keys(52,86,60,5,1.7,DARK)}', -28)
ICONS["oboe"] = rot(f'<rect x="14" y="57" width="86" height="6" fill="{DARK}"/><path d="M96 54 L114 49 L114 71 L96 66 Z" fill="{DARK}"/><rect x="4" y="58.5" width="14" height="3" fill="{WOOD}"/>{keys(30,90,60,7,1.8,SILVER)}', -28)
ICONS["englishhorn"] = rot(f'<rect x="20" y="58" width="68" height="5" fill="{DARK}"/><circle cx="96" cy="60" r="12" fill="{DARK}"/><path d="M20 60 Q8 50 12 36" stroke="{SILVER}" stroke-width="3" fill="none"/>{keys(34,82,60,6,1.6,SILVER)}', -22)
ICONS["clarinet"] = rot(f'<rect x="16" y="56" width="80" height="8" fill="{DARK}"/><path d="M92 54 L112 46 L112 74 L92 66 Z" fill="{DARK}"/><path d="M6 60 L20 55 L20 65 Z" fill="{WOOD}"/>{keys(32,88,60,7,2,SILVER)}', -28)
ICONS["bassoon"] = f'<rect x="48" y="30" width="9" height="76" rx="3" fill="{WOOD}" stroke="{WOOD2}"/><rect x="63" y="30" width="9" height="62" rx="3" fill="{WOOD}" stroke="{WOOD2}"/><path d="M52 106 Q60 114 68 106" stroke="{WOOD2}" stroke-width="4" fill="none"/><path d="M68 30 Q78 14 92 12" stroke="{SILVER2}" stroke-width="3" fill="none"/><path d="M60 92 L74 98 L74 108 Z" fill="{WOOD2}"/>{keys(52.5,67.5,44,2,2)}{keys(52.5,67.5,60,2,2)}{keys(52.5,67.5,76,2,2)}'
ICONS["contrabassoon"] = f'<rect x="34" y="22" width="10" height="82" rx="3" fill="{WOOD}" stroke="{WOOD2}"/><rect x="52" y="22" width="10" height="68" rx="3" fill="{WOOD}" stroke="{WOOD2}"/><rect x="70" y="30" width="10" height="74" rx="3" fill="{WOOD}" stroke="{WOOD2}"/><rect x="34" y="100" width="46" height="10" rx="5" fill="{WOOD2}"/><path d="M80 34 Q90 22 98 24" stroke="{SILVER2}" stroke-width="3" fill="none"/><circle cx="85" cy="104" r="10" fill="{BRASS2}"/>'
# 금관
ICONS["trumpet"] = rot(f'<rect x="8" y="58" width="50" height="4" fill="{BRASS}"/><path d="M58 60 q20 -22 26 0 q6 22 -22 22 L40 82" stroke="{BRASS}" stroke-width="4" fill="none"/><path d="M84 60 L112 44 L112 76 Z" fill="{BRASS}" stroke="{BRASS2}"/><rect x="44" y="48" width="4" height="12" fill="{BRASS2}"/><rect x="52" y="48" width="4" height="12" fill="{BRASS2}"/><rect x="60" y="48" width="4" height="12" fill="{BRASS2}"/>', -10)
ICONS["horn"] = f'<circle cx="56" cy="64" r="34" fill="none" stroke="{BRASS}" stroke-width="5"/><circle cx="56" cy="64" r="24" fill="none" stroke="{BRASS}" stroke-width="5"/><path d="M82 40 Q112 12 112 52 Q100 60 84 50 Z" fill="{BRASS}" stroke="{BRASS2}"/><rect x="26" y="52" width="8" height="12" rx="2" fill="{BRASS2}"/><rect x="38" y="46" width="8" height="12" rx="2" fill="{BRASS2}"/><rect x="50" y="42" width="8" height="12" rx="2" fill="{BRASS2}"/>'
ICONS["trombone"] = f'<rect x="12" y="48" width="86" height="5" fill="{BRASS}"/><rect x="12" y="68" width="86" height="5" fill="{BRASS}"/><path d="M12 50 q-12 10 0 20" stroke="{BRASS}" stroke-width="5" fill="none"/><rect x="92" y="42" width="5" height="36" fill="{BRASS2}"/><path d="M98 40 Q118 32 118 60 Q118 88 98 80 Z" fill="{BRASS}" stroke="{BRASS2}"/><rect x="40" y="53" width="5" height="15" fill="{BRASS2}"/>'
ICONS["tuba"] = f'<ellipse cx="52" cy="82" rx="30" ry="24" fill="none" stroke="{BRASS}" stroke-width="6"/><path d="M30 70 L40 18 L66 18 L70 70" fill="none" stroke="{BRASS}" stroke-width="6" stroke-linejoin="round"/><path d="M22 14 L84 14 L72 4 L34 4 Z" fill="{BRASS2}"/><circle cx="50" cy="44" r="4" fill="{BRASS2}"/><circle cx="62" cy="48" r="4" fill="{BRASS2}"/><path d="M20 14 Q10 14 12 22" stroke="{BRASS2}" stroke-width="3" fill="none"/>'
# 타악
ICONS["timpani"] = f'<path d="M18 52 Q60 30 102 52 Q102 100 60 108 Q18 100 18 52 Z" fill="{BRASS2}" stroke="#7b5a0d" stroke-width="2"/><ellipse cx="60" cy="50" rx="42" ry="14" fill="#f0e5c8" stroke="{SKIN}"/><path d="M40 106 L34 118 M80 106 L86 118" stroke="{DARK}" stroke-width="4"/><line x1="86" y1="24" x2="74" y2="46" stroke="{DARK}" stroke-width="2.5"/><circle cx="87" cy="22" r="5" fill="{SKIN}" stroke="{DARK}"/>'
ICONS["snaredrum"] = f'<rect x="26" y="52" width="68" height="40" fill="{SILVER}" stroke="{SILVER2}" stroke-width="2"/><ellipse cx="60" cy="52" rx="34" ry="11" fill="#f2ecdf" stroke="{SILVER2}" stroke-width="2"/><ellipse cx="60" cy="92" rx="34" ry="9" fill="{SILVER}" stroke="{SILVER2}" stroke-width="2"/><path d="M30 60 L40 94 M44 62 L52 100 M62 64 L66 102 M78 62 L82 100 M92 60 L84 94" stroke="{SILVER2}" stroke-width="1.5"/><line x1="26" y1="24" x2="50" y2="48" stroke="{WOOD2}" stroke-width="3"/><line x1="94" y1="24" x2="70" y2="48" stroke="{WOOD2}" stroke-width="3"/>'
ICONS["bassdrum"] = f'<circle cx="60" cy="62" r="46" fill="{RED}" stroke="{DARK}" stroke-width="3"/><circle cx="60" cy="62" r="36" fill="#f2ecdf" stroke="{SKIN}"/><path d="M60 62 L100 62 M60 62 L88 90 M60 62 L88 34" stroke="#d9cfb8" stroke-width="1"/><line x1="90" y1="14" x2="70" y2="46" stroke="{DARK}" stroke-width="3"/><circle cx="92" cy="12" r="6" fill="{SKIN}" stroke="{DARK}"/>'
ICONS["cymbals"] = f'<ellipse cx="46" cy="52" rx="34" ry="12" fill="{BRASS}" stroke="{BRASS2}" stroke-width="2" transform="rotate(-24 46 52)"/><ellipse cx="74" cy="72" rx="34" ry="12" fill="{BRASS}" stroke="{BRASS2}" stroke-width="2" transform="rotate(24 74 72)"/><circle cx="46" cy="52" r="4" fill="{BRASS2}"/><circle cx="74" cy="72" r="4" fill="{BRASS2}"/>'
ICONS["triangle"] = f'<path d="M60 16 L24 84 L96 84" fill="none" stroke="{SILVER2}" stroke-width="5" stroke-linejoin="round"/><path d="M60 16 L60 6" stroke="{DARK}" stroke-width="2"/><line x1="94" y1="30" x2="72" y2="62" stroke="{SILVER2}" stroke-width="3"/>'
ICONS["xylophone"] = "".join(f'<rect x="{12+i*16}" y="{30+i*2}" width="12" height="{62-i*4}" rx="3" fill="{WOOD}" stroke="{WOOD2}"/>' for i in range(6)) + f'<line x1="14" y1="40" x2="104" y2="40" stroke="#555"/><line x1="14" y1="84" x2="104" y2="84" stroke="#555"/><line x1="22" y1="12" x2="48" y2="38" stroke="{DARK}" stroke-width="3"/><circle cx="20" cy="10" r="5" fill="{RED}"/>'
ICONS["glockenspiel"] = "".join(f'<rect x="{12+i*16}" y="{32+i*2}" width="12" height="{58-i*4}" rx="3" fill="{SILVER}" stroke="{SILVER2}"/>' for i in range(6)) + f'<line x1="14" y1="42" x2="104" y2="42" stroke="#555"/><line x1="14" y1="82" x2="104" y2="82" stroke="#555"/><line x1="26" y1="12" x2="50" y2="38" stroke="{DARK}" stroke-width="3"/><circle cx="24" cy="10" r="4" fill="{SKIN}" stroke="{DARK}"/>'
ICONS["gong"] = f'<path d="M14 108 L14 14 L106 14 L106 108" fill="none" stroke="{WOOD2}" stroke-width="6"/><line x1="14" y1="14" x2="106" y2="14" stroke="{WOOD2}" stroke-width="6"/><circle cx="60" cy="62" r="34" fill="{BRASS}" stroke="{BRASS2}" stroke-width="3"/><circle cx="60" cy="62" r="12" fill="{BRASS2}"/><line x1="60" y1="14" x2="60" y2="28" stroke="{DARK}"/>'
ICONS["tambourine"] = f'<circle cx="60" cy="60" r="40" fill="#eadfc8" stroke="{WOOD2}" stroke-width="9"/><circle cx="60" cy="60" r="31" fill="none" stroke="#d6c9a8"/>' + "".join(f'<ellipse cx="{60+40*__import__("math").cos(a*0.785):.1f}" cy="{60+40*__import__("math").sin(a*0.785):.1f}" rx="5" ry="2" fill="{SILVER}" stroke="{SILVER2}" transform="rotate({a*45} {60+40*__import__("math").cos(a*0.785):.1f} {60+40*__import__("math").sin(a*0.785):.1f})"/>' for a in range(8))
ICONS["castanets"] = f'<path d="M14 52 Q40 22 60 56 Q40 86 14 52 Z" fill="{RED}" stroke="{WOOD2}" stroke-width="3"/><path d="M106 68 Q80 38 60 72 Q80 102 106 68 Z" fill="{RED}" stroke="{WOOD2}" stroke-width="3"/><path d="M40 56 Q58 62 72 72" stroke="{SKIN}" stroke-width="3" fill="none"/><circle cx="40" cy="56" r="3" fill="{SKIN}"/>'
# 건반·하프
ICONS["piano"] = f'<path d="M12 22 L72 14 Q110 14 108 52 Q106 70 84 74 L12 74 Z" fill="{DARK}" stroke="#000" stroke-width="2"/><rect x="12" y="74" width="96" height="28" fill="#fffaf0" stroke="#000" stroke-width="2"/>' + "".join(f'<line x1="{12+i*8}" y1="74" x2="{12+i*8}" y2="102" stroke="#999"/>' for i in range(1, 12)) + "".join(f'<rect x="{18+i*8}" y="74" width="5" height="16" fill="{DARK}"/>' for i in (0,1,3,4,5,7,8,10)) + f'<path d="M72 14 L106 6" stroke="{DARK}" stroke-width="3"/>'
ICONS["celesta"] = f'<rect x="20" y="14" width="80" height="48" rx="6" fill="{WOOD}" stroke="{WOOD2}" stroke-width="3"/><rect x="28" y="22" width="64" height="12" fill="{SILVER}" stroke="{SILVER2}"/>' + "".join(f'<line x1="{28+i*8}" y1="22" x2="{28+i*8}" y2="34" stroke="{SILVER2}"/>' for i in range(1, 8)) + f'<rect x="16" y="62" width="88" height="14" fill="#fffaf0" stroke="#000" stroke-width="2"/>' + "".join(f'<line x1="{16+i*8}" y1="62" x2="{16+i*8}" y2="76" stroke="#999"/>' for i in range(1, 11)) + f'<rect x="24" y="76" width="6" height="30" fill="{WOOD2}"/><rect x="90" y="76" width="6" height="30" fill="{WOOD2}"/>'
ICONS["organ"] = "".join(f'<rect x="{12+i*12}" y="{10+abs(5-i)*5}" width="9" height="{60-abs(5-i)*5}" rx="3" fill="{SILVER}" stroke="{SILVER2}"/>' for i in range(9)) + f'<rect x="10" y="74" width="100" height="22" rx="3" fill="{WOOD}" stroke="{WOOD2}" stroke-width="3"/><rect x="16" y="78" width="88" height="8" fill="#fffaf0" stroke="#000"/><rect x="40" y="100" width="40" height="8" rx="2" fill="{WOOD2}"/>'

def icon(i): return svg(ICONS[i], i)

# 무대 배치도(번호 자리): 관객이 보는 쪽 기준, 일반적인 배치
SEATS_XY = {1: (26, 94), 2: (46, 76), 3: (80, 76), 4: (98, 94), 5: (104, 64), 6: (60, 56), 7: (60, 36), 8: (60, 18), 9: (18, 62), 10: (60, 114)}
def seating(hl):
    body = '<path d="M4 108 A56 100 0 0 1 116 108 Z" fill="#efe3c9" stroke="#b79d6c" stroke-width="2"/>'
    for n, (x, y) in SEATS_XY.items():
        on = n == hl
        body += f'<circle cx="{x}" cy="{y}" r="8.5" fill="{"#e8742a" if on else "#d6c9a8"}" stroke="{"#7a3a0c" if on else "#9b8a62"}" stroke-width="{2 if on else 1}"/><text x="{x}" y="{y+3.5}" font-size="10" font-weight="700" text-anchor="middle" fill="{"#fff" if on else "#4a3f27"}">{n}</text>'
    return f'<svg viewBox="0 0 120 126" role="img" aria-label="오케스트라 무대 배치도" xmlns="http://www.w3.org/2000/svg"><rect width="120" height="126" rx="14" fill="#f6efe0"/>{body}</svg>'


# ───────── 크기 비교 그림(같은 모양의 악기를 실제 크기 비율로 나란히): 현악기 네 가지 + 사람 키(약 170cm)
STR_SIZES = [("violin", "바이올린", 60), ("viola", "비올라", 67), ("cello", "첼로", 120), ("doublebass", "콘트라베이스", 180)]   # 전체 길이(cm), 대략
def size_compare(hl, names=False):
    """hl: 강조할 악기 id(없으면 모두 같은 색). names=True면 이름과 길이(cm)를 글자로 보여 줘요(문제 풀 때는 정답이 드러나서 False)."""
    K = 0.52; base = 104; W = 252; Hh = 126 if names else 112
    body = f'<line x1="6" y1="{base}" x2="{W-6}" y2="{base}" stroke="#b79d6c" stroke-width="1.5"/>'
    # 사람(170cm): 머리+몸통+다리를 단순하게
    ph = 170 * K; px = W - 24
    body += f'<g fill="#9aa4ae"><circle cx="{px}" cy="{base-ph+7}" r="7"/><rect x="{px-8}" y="{base-ph+15}" width="16" height="{ph*0.38:.1f}" rx="5"/><rect x="{px-7}" y="{base-ph+15+ph*0.38-2:.1f}" width="5.5" height="{ph*0.47:.1f}" rx="2"/><rect x="{px+1.5}" y="{base-ph+15+ph*0.38-2:.1f}" width="5.5" height="{ph*0.47:.1f}" rx="2"/></g>'
    x = 22
    for iid, nm, cm in STR_SIZES:
        h = cm * K; on = (hl is None) or iid == hl; col = WOOD if on else "#c9bfae"; edge = WOOD2 if on else "#a89c86"
        bw = 6 + cm * 0.055                          # 큰 악기일수록 몸통이 조금 넓어요
        top = base - h; cx = x + bw
        # 몸통(두 번 불룩), 목, 소용돌이
        by = base - (0.45 * h)
        body += (f'<ellipse cx="{cx:.1f}" cy="{base-0.20*h:.1f}" rx="{bw:.1f}" ry="{0.20*h:.1f}" fill="{col}" stroke="{edge}" stroke-width="1.5"/>'
                 f'<ellipse cx="{cx:.1f}" cy="{base-0.42*h:.1f}" rx="{bw*0.78:.1f}" ry="{0.13*h:.1f}" fill="{col}" stroke="{edge}" stroke-width="1.5"/>'
                 f'<rect x="{cx-1.6:.1f}" y="{top+2:.1f}" width="3.2" height="{0.62*h:.1f}" rx="1.2" fill="{DARK if on else "#8a8378"}"/>'
                 f'<circle cx="{cx:.1f}" cy="{top+1:.1f}" r="2.6" fill="{edge}"/>')
        if on and hl: body += f'<circle cx="{cx:.1f}" cy="{top-6:.1f}" r="3.6" fill="#e8742a"/>'
        if names: body += f'<text x="{cx:.1f}" y="{base+10}" font-size="7.6" text-anchor="middle" fill="#4a3f27" font-weight="{700 if iid==hl else 400}">{nm}</text><text x="{cx:.1f}" y="{base+19}" font-size="6.8" text-anchor="middle" fill="#7b6a45">약 {cm}cm</text>'
        x += 2 * bw + 18
    if names: body += f'<text x="{px}" y="{base+10}" font-size="7.2" text-anchor="middle" fill="#6b747d">사람</text><text x="{px}" y="{base+19}" font-size="6.8" text-anchor="middle" fill="#6b747d">약 170cm</text>'
    return f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="현악기 크기 비교" xmlns="http://www.w3.org/2000/svg"><rect width="{W}" height="{Hh}" rx="14" fill="#f6efe0"/>{body}</svg>'


# ───────── 목관악기 크기 비교(길이를 가로 막대로, 실제 길이 비율): 피콜로·플루트·오보에·클라리넷·잉글리시 호른·바순·콘트라바순
WIND_SIZES = [("piccolo", "피콜로", 32), ("flute", "플루트", 67), ("oboe", "오보에", 62), ("clarinet", "클라리넷", 66), ("englishhorn", "잉글리시 호른", 80), ("bassoon", "바순", 134), ("contrabassoon", "콘트라바순", 150)]
def winds_compare(hl, names=False):
    """hl: 강조할 악기 id. 막대 길이가 실제 길이(바순·콘트라바순은 접은 높이)에 비례해요. names=True면 이름과 길이를 적어요."""
    K = 0.84 if names else 1.3; x0 = 78 if names else 14; rowh = 17; W = 252; H = 14 + rowh * len(WIND_SIZES)
    body = ""; y = 8
    for iid, nm, cm in WIND_SIZES:
        on = (hl is None) or iid == hl; L = cm * K
        col = {"piccolo": WOOD, "flute": SILVER, "oboe": DARK, "clarinet": DARK, "englishhorn": DARK, "bassoon": WOOD, "contrabassoon": WOOD}[iid] if on else "#cdc4b3"
        edge = ("#555" if iid in ("oboe", "clarinet", "englishhorn") else (WOOD2 if iid in ("piccolo", "bassoon", "contrabassoon") else SILVER2)) if on else "#a89c86"
        th = 9 if iid in ("bassoon", "contrabassoon") else 6 if iid != "piccolo" else 5
        body += f'<rect x="{x0}" y="{y+(rowh-th)/2-2:.1f}" width="{L:.1f}" height="{th}" rx="{th/2:.1f}" fill="{col}" stroke="{edge}" stroke-width="1"/>'
        if iid in ("oboe", "clarinet", "englishhorn"): body += f'<ellipse cx="{x0+L-3:.1f}" cy="{y+rowh/2-2:.1f}" rx="{3.6 if iid != "englishhorn" else 5}" ry="{5 if iid != "englishhorn" else 5.5}" fill="{col}" stroke="{edge}" stroke-width="1"/>'
        if on and hl: body += f'<circle cx="{x0+L+7:.1f}" cy="{y+rowh/2-2:.1f}" r="3.6" fill="#e8742a"/>'
        if names: body += f'<text x="{x0-6}" y="{y+rowh/2+1:.1f}" font-size="8.2" text-anchor="end" fill="#4a3f27" font-weight="{700 if iid==hl else 400}">{nm}</text><text x="{x0+L+(14 if (on and hl) else 5):.1f}" y="{y+rowh/2+1:.1f}" font-size="7.4" fill="#7b6a45">약 {cm}cm</text>'
        y += rowh
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="목관악기 크기 비교" xmlns="http://www.w3.org/2000/svg"><rect width="{W}" height="{H}" rx="14" fill="#f6efe0"/>{body}</svg>'
