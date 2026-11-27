"""Generate brand SVGs for the GitHub profile README (dark + light).

Palette from docs/brand.md: ink black, white, sky blue (signal), red (faults only).
"""
import sys, pathlib
OUT = pathlib.Path(sys.argv[1])

SANS = "'Inter','Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',monospace"
THEMES = {
    "dark":  dict(bg="#0A0E17", panel="#111827", grid="#141C2B", line="#1F2937", text="#FFFFFF", muted="#94A3B8",
                  sky="#38BDF8", skyfill="#0EA5E9", red="#F87171", redfill="#DC2626", grey="#334155", chip="#0B2236", glow=0.22),
    "light": dict(bg="#FFFFFF", panel="#F6F8FB", grid="#EEF2F7", line="#E3E8EF", text="#0A0E17", muted="#64748B",
                  sky="#0369A1", skyfill="#0EA5E9", red="#DC2626", redfill="#DC2626", grey="#CBD5E1", chip="#E0F2FE", glow=0.10),
}


def logo(x, y, s, t):
    k = s / 64
    return (f'<g transform="translate({x},{y}) scale({k})">'
            f'<rect width="64" height="64" rx="14" fill="#0A0E17" stroke="{t["line"]}" stroke-width="{1/k:.2f}"/>'
            '<path d="M10 36 H22 L27 22 L34 46 L39 30 L43 36 H54" fill="none" stroke="#0EA5E9" stroke-width="4" '
            'stroke-linecap="round" stroke-linejoin="round"/><circle cx="50" cy="18" r="5" fill="#DC2626"/></g>')


def glow(cx, cy, r, op):
    return (f'<defs><radialGradient id="glow" cx="{cx}" cy="{cy}" r="{r}">'
            f'<stop offset="0" stop-color="#0EA5E9" stop-opacity="{op}"/>'
            '<stop offset="1" stop-color="#0EA5E9" stop-opacity="0"/></radialGradient></defs>')


def pill(x, y, label, t, size=14, h=30, charw=8.7):
    w = 32 + len(label) * charw
    return (f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="{h}" rx="{h/2:.0f}" fill="{t["chip"]}"/>'
            f'<text x="{x + w/2:.0f}" y="{y + h/2 + size*0.36:.0f}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="{size}" font-weight="700" fill="{t["sky"]}">{label}</text>'), w


def tag(x, y, label, t, active, size=13, h=30, charw=7.9):
    w = 20 + len(label) * charw
    fill = t["chip"] if active else "none"
    stroke = t["skyfill"] if active else t["line"]
    col = t["sky"] if active else t["muted"]
    return (f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}"/>'
            f'<text x="{x + w/2:.0f}" y="{y + h/2 + size*0.36:.0f}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="{size}" font-weight="{700 if active else 400}" fill="{col}">{label}</text>'), w


def banner(t):
    W, H = 1200, 340
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(0, W, 40)) + \
           "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>' for y in range(0, H, 40))
    px, py, pw, ph = 742, 40, 412, 250
    BX, BW = px + pw - 150, 130
    items = [("#1", "Tears of the Kingdom", 0.94), ("#2", "Elden Ring", 0.88), ("#3", "Hogwarts Legacy", 0.81),
             ("#4", "God of War Ragnarök", 0.77), ("#5", "Pokémon Scarlet", 0.70)]
    rows = []
    for i, (rank, title, sc) in enumerate(items):
        y = py + 82 + i * 38
        cls = ' class="fault"' if i == 2 else ""
        rows.append(f'<g{cls}>'
                    f'<text x="{px+20}" y="{y+5}" font-family="{MONO}" font-size="14" fill="{t["muted"]}">{rank}</text>'
                    f'<text x="{px+56}" y="{y+5}" font-family="{SANS}" font-size="16" fill="{t["text"]}" class="ttl">{title}</text>'
                    f'<rect x="{BX}" y="{y-5}" width="{BW}" height="9" rx="4.5" fill="{t["grid"]}"/>'
                    f'<rect x="{BX}" y="{y-5}" width="{BW*sc:.0f}" height="9" rx="4.5" fill="{t["skyfill"]}" class="bar"/></g>')
    pills, x = [], 56
    for lab in ["RETRIEVAL", "RANKING", "RECSYSOPS", "COLD START"]:
        p, w = pill(x, 284, lab, t)
        pills.append(p)
        x += w + 10
    css = f"""
  .fault .bar {{ transform-box: fill-box; transform-origin: left center; animation: bar 7s infinite; }}
  .fault .ttl {{ animation: ttl 7s infinite; }}
  .tag-f {{ animation: tf 7s infinite; opacity: 0; }}
  .tag-d {{ animation: td 7s infinite; opacity: 0; }}
  .pulse {{ stroke-dasharray: 100; stroke-dashoffset: 100; animation: draw 7s infinite; }}
  .blink {{ animation: blink 1.4s steps(2) infinite; }}
  @keyframes bar {{ 0%,28% {{ fill:{t['skyfill']}; transform:scaleX(1) }} 34%,74% {{ fill:{t['redfill']}; transform:scaleX(0.14) }} 82%,100% {{ fill:{t['skyfill']}; transform:scaleX(1) }} }}
  @keyframes ttl {{ 0%,28% {{ fill:{t['text']} }} 34%,74% {{ fill:{t['red']} }} 82%,100% {{ fill:{t['text']} }} }}
  @keyframes tf {{ 0%,30% {{ opacity:0 }} 36%,76% {{ opacity:1 }} 82%,100% {{ opacity:0 }} }}
  @keyframes td {{ 0%,50% {{ opacity:0 }} 55%,76% {{ opacity:1 }} 82%,100% {{ opacity:0 }} }}
  @keyframes draw {{ 0% {{ stroke-dashoffset:100 }} 30%,100% {{ stroke-dashoffset:0 }} }}
  @keyframes blink {{ 0% {{ opacity:1 }} 100% {{ opacity:0.15 }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} .pulse {{ stroke-dashoffset: 0; }} }}
"""
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Lenin Jacob Regi: Recommender Systems Engineer">',
        f"<style>{css}</style>",
        glow("12%", "0%", "70%", t["glow"]),
        f'<rect width="{W}" height="{H}" rx="16" fill="{t["bg"]}"/>',
        f'<g stroke="{t["grid"]}" stroke-width="1">{grid}</g>',
        f'<rect width="{W}" height="{H}" rx="16" fill="url(#glow)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{t["line"]}"/>',
        logo(56, 40, 52, t),
        f'<text x="124" y="62" font-family="{MONO}" font-size="17" font-weight="700" letter-spacing="3" fill="{t["sky"]}">LENIN JACOB REGI</text>',
        f'<text x="124" y="86" font-family="{MONO}" font-size="14" fill="{t["muted"]}">B.Tech CSE (AI/ML) · Karunya \'27 · SIH 2025 Grand Finalist</text>',
        f'<text x="56" y="152" font-family="{SANS}" font-size="52" font-weight="800" letter-spacing="-1" fill="{t["text"]}">Recommender Systems</text>',
        f'<text x="56" y="206" font-family="{SANS}" font-size="52" font-weight="800" letter-spacing="-1" fill="{t["text"]}">Engineer<tspan fill="{t["skyfill"]}">.</tspan></text>',
        f'<text x="56" y="242" font-family="{SANS}" font-size="19" fill="{t["muted"]}">I build retrieval and ranking systems,</text>',
        f'<text x="56" y="266" font-family="{SANS}" font-size="19" fill="{t["muted"]}">and keep them healthy in production.</text>',
        "".join(pills),
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{t["panel"]}" stroke="{t["line"]}"/>',
        f'<text x="{px+20}" y="{py+30}" font-family="{MONO}" font-size="14" fill="{t["muted"]}">GET /recommend?user=u_4821</text>',
        f'<circle cx="{px+pw-26}" cy="{py+25}" r="5" fill="{t["skyfill"]}" class="blink"/>',
        f'<line x1="{px}" y1="{py+46}" x2="{px+pw}" y2="{py+46}" stroke="{t["line"]}"/>',
        "".join(rows),
        f'<g class="tag-f" font-family="{MONO}" font-size="13" font-weight="700">'
        f'<rect x="{BX+14}" y="{py+139}" width="62" height="24" rx="5" fill="{t["redfill"]}"/>'
        f'<text x="{BX+45}" y="{py+156}" text-anchor="middle" fill="#FFFFFF">FAULT</text></g>',
        f'<g class="tag-d" font-family="{MONO}" font-size="13" font-weight="700">'
        f'<rect x="{BX+82}" y="{py+139}" width="62" height="24" rx="5" fill="{t["bg"]}" stroke="{t["skyfill"]}" stroke-width="1.5"/>'
        f'<text x="{BX+113}" y="{py+156}" text-anchor="middle" fill="{t["sky"]}">ALERT</text></g>',
        f'<path class="pulse" pathLength="100" d="M{px} 316 H{px+150} L{px+168} 300 L{px+186} 330 L{px+204} 296 L{px+222} 316 H{px+pw}" '
        f'fill="none" stroke="{t["skyfill"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>',
        "</svg>"])


def card(t):
    W, H = 1200, 400
    seg = []
    for w in range(11):
        x = 56 + w * 56
        on = w == 0
        seg.append(f'<rect x="{x}" y="272" width="50" height="12" rx="3" fill="{t["skyfill"] if on else t["grid"]}" '
                   f'stroke="{t["skyfill"] if on else t["line"]}"/>')
        seg.append(f'<text x="{x+25}" y="304" text-anchor="middle" font-family="{MONO}" font-size="13" '
                   f'fill="{t["sky"] if on else t["muted"]}">W{w+1}</text>')
    tags, x = [], 56
    for i, lab in enumerate(["✓ P1 item-to-item", "P2 MF/BPR", "P3 YouTube DNN", "P4 two-tower", "P5 MMoE", "P6 MMR/DPP"]):
        g, w = tag(x, 326, lab, t, active=(i == 0))
        tags.append(g)
        x += w + 7
    cx, cy, cw = 846, 120, 220
    data = [("Popularity, all time", 0.0017, t["grey"], t["muted"], False),
            ("Item-to-item (P1)", 0.0101, t["skyfill"], t["sky"], True),
            ("Popularity, last 30 days", 0.0186, t["grey"], t["muted"], False)]
    bars = []
    for i, (lab, v, col, vcol, hi) in enumerate(data):
        y = cy + 30 + i * 66
        bw = max(6, cw * v / 0.0186)
        wt = 700 if hi else 400
        bars.append(f'<text x="{cx}" y="{y}" font-family="{SANS}" font-size="16" font-weight="{wt}" fill="{t["text"]}">{lab}</text>'
                    f'<rect x="{cx}" y="{y+12}" width="{bw:.0f}" height="18" rx="4" fill="{col}"/>'
                    f'<text x="{cx+bw+10:.0f}" y="{y+26}" font-family="{MONO}" font-size="15" font-weight="{wt}" fill="{vcol}">{v:.4f}</text>')
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        'aria-label="RecChaos: now building, week 1 of 11. Week 1 result: item-to-item beats all-time popularity, loses to 30-day popularity.">',
        glow("0%", "0%", "60%", t["glow"] * 0.75),
        f'<clipPath id="r"><rect width="{W}" height="{H}" rx="16"/></clipPath>',
        f'<g clip-path="url(#r)"><rect width="{W}" height="{H}" fill="{t["bg"]}"/>'
        f'<rect width="{W}" height="{H}" fill="url(#glow)"/><rect width="7" height="{H}" fill="{t["skyfill"]}"/></g>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{t["line"]}"/>',
        f'<text x="56" y="58" font-family="{MONO}" font-size="15" font-weight="700" letter-spacing="3" fill="{t["sky"]}">NOW BUILDING · IN PUBLIC</text>',
        logo(56, 76, 46, t),
        f'<text x="116" y="113" font-family="{SANS}" font-size="42" font-weight="800" letter-spacing="-0.5" fill="{t["text"]}">RecChaos</text>',
        f'<text x="56" y="164" font-family="{SANS}" font-size="21" font-weight="600" fill="{t["text"]}">A fault-injection benchmark for recommender systems.</text>',
        f'<text x="56" y="194" font-family="{SANS}" font-size="17" fill="{t["muted"]}">Rebuild six papers that shaped the industry into one stack,</text>',
        f'<text x="56" y="217" font-family="{SANS}" font-size="17" fill="{t["muted"]}">then break it in 10 silent ways and score which monitors notice.</text>',
        f'<text x="56" y="258" font-family="{MONO}" font-size="14" letter-spacing="1" fill="{t["muted"]}">WEEK 1 OF 11 · BUILD → BREAK → DETECT</text>',
        "".join(seg), "".join(tags),
        f'<line x1="806" y1="40" x2="806" y2="{H-40}" stroke="{t["line"]}"/>',
        f'<text x="{cx}" y="58" font-family="{MONO}" font-size="15" font-weight="700" letter-spacing="3" fill="{t["sky"]}">WEEK 1 RESULT</text>',
        f'<text x="{cx}" y="86" font-family="{SANS}" font-size="15" fill="{t["muted"]}">NDCG@10 · December 2022 test month</text>',
        "".join(bars),
        f'<text x="{cx}" y="{H-34}" font-family="{SANS}" font-size="14" fill="{t["text"]}">Beats bestsellers <tspan font-weight="700">6×</tspan>, loses to “what\'s hot”.</text>',
        "</svg>"])


for k, t in THEMES.items():
    (OUT / f"banner-{k}.svg").write_text(banner(t))
    (OUT / f"recchaos-{k}.svg").write_text(card(t))
print("written", sorted(p.name for p in OUT.iterdir()))
