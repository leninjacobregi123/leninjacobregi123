#!/usr/bin/env python3
"""Generate the SVG cards for the GitHub profile README.

    GITHUB_TOKEN=$(gh auth token) python3 scripts/gen_assets.py assets               # everything
    python3 scripts/gen_assets.py assets --stats-only                                 # what the daily Action runs

Palette (RecChaos brand): ink black, white, sky blue; red only for faults.
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import math
import os
import pathlib
import random
import sys
import urllib.request
from xml.sax.saxutils import escape

HERE = pathlib.Path(__file__).resolve().parent
LOGIN = "leninjacobregi123"

# ---- Update these as RecChaos progresses ------------------------------------
WEEK = 1                                   # current RecChaos week, of 11
DONE = ["P1"]                              # finished projects
NEXT = "P2 · matrix factorization (BPR)"   # what's next
# ------------------------------------------------------------------------------

SANS = "'Inter','Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',monospace"
SKY, INK, RED = "#0EA5E9", "#0A0E17", "#DC2626"

THEMES = {
    "dark": dict(card="#111723", border="#263041", text="#F8FAFC", muted="#94A3B8", sky="#38BDF8",
                 chip="#0B111C", track="#1E2836"),
    "light": dict(card="#F6F8FB", border="#E3E8EF", text="#0A0E17", muted="#64748B", sky="#0369A1",
                  chip="#FFFFFF", track="#E3E8EF"),
}

STACK = [("python", "Python"), ("pytorch", "PyTorch"), ("tensorflow", "TensorFlow"), ("huggingface", "Hugging Face"),
         ("pandas", "pandas"), ("numpy", "NumPy"), ("fastapi", "FastAPI"), ("langchain", "LangChain"),
         ("ollama", "Ollama"), ("milvus", "Milvus"), ("postgresql", "PostgreSQL"), ("docker", "Docker"),
         ("typescript", "TypeScript"), ("javascript", "JavaScript"), ("babylondotjs", "Babylon.js"),
         ("cloudflareworkers", "Cloudflare Workers"), ("linux", "Linux"), ("git", "Git")]

ICONS_FILE = HERE / "icons.json"
ICONS = json.loads(ICONS_FILE.read_text()) if ICONS_FILE.exists() else {}


# ---------------------------------------------------------------- helpers
def attr(s: str) -> str:
    return escape(s, {'"': "&quot;"})


def svg(w, h, body, label, style=""):
    st = f"<style>{style}</style>" if style else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{attr(label)}">{st}{body}</svg>\n')


def text(x, y, s, size, fill, weight=400, family=SANS, anchor="start", ls=0, raw=False, cls=""):
    a = [f'x="{x}"', f'y="{y}"', f'font-family="{family}"', f'font-size="{size}"', f'font-weight="{weight}"', f'fill="{fill}"']
    if anchor != "start":
        a.append(f'text-anchor="{anchor}"')
    if ls:
        a.append(f'letter-spacing="{ls}"')
    if cls:
        a.append(f'class="{cls}"')
    return f'<text {" ".join(a)}>{s if raw else escape(s)}</text>'


def wrap(s, size, width, cw=0.54):
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if cur and len(trial) * size * cw > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def frame(w, h, t):
    return f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="14" fill="{t["card"]}" stroke="{t["border"]}"/>'


def icon(slug, x, y, size, fill):
    return f'<path transform="translate({x} {y}) scale({size/24:.4f})" d="{ICONS[slug]}" fill="{fill}"/>'


def logo(x, y, s, border="#263041"):
    k = s / 64
    return (f'<g transform="translate({x} {y}) scale({k:.4f})"><rect width="64" height="64" rx="14" fill="{INK}" '
            f'stroke="{border}" stroke-width="{1/k:.2f}"/><path d="M10 36 H22 L27 22 L34 46 L39 30 L43 36 H54" fill="none" '
            f'stroke="{SKY}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="50" cy="18" r="5" fill="{RED}"/></g>')


def poly(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


# ---------------------------------------------------------------- banner (one version for both themes)
def palm(x, base, h, lean, k=1.0, samples=36):
    """A palm silhouette: curved tapering trunk plus a crown of serrated, drooping fronds."""
    def b3(p0, p1, p2, p3, t):
        u = 1 - t
        return (u**3 * p0[0] + 3*u*u*t * p1[0] + 3*u*t*t * p2[0] + t**3 * p3[0],
                u**3 * p0[1] + 3*u*u*t * p1[1] + 3*u*t*t * p2[1] + t**3 * p3[1])
    p0, p3 = (x, base), (x + lean, base - h)
    p1, p2 = (x + lean * 0.05, base - h * 0.35), (x + lean * 0.75, base - h * 0.72)
    left, right = [], []
    for i in range(19):
        t = i / 18
        ax, ay = b3(p0, p1, p2, p3, t)
        bx, by = b3(p0, p1, p2, p3, min(1, t + 0.01))
        cx_, cy_ = b3(p0, p1, p2, p3, max(0, t - 0.01))
        dx, dy = bx - cx_, by - cy_
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        w = (5.0 * (1 - t) + 2.2 * t) * k / 2
        left.append((ax + nx * w, ay + ny * w))
        right.append((ax - nx * w, ay - ny * w))
    parts = [poly(left + right[::-1])]
    cx, cy = p3
    flen = max(20, min(86, h * 0.46))
    spec = [(-176, .95, .55), (-152, 1.0, .42), (-128, .9, .28), (-104, .74, .14), (-80, .72, .12),
            (-56, .88, .26), (-32, 1.0, .42), (-8, .96, .56), (166, .72, .78), (14, .72, .78)]
    for a, lf, droop in spec:
        a += lean * 0.15
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        L = flen * lf
        q0 = (cx, cy)
        q1 = (cx + dx * L * 0.5, cy + dy * L * 0.5 - L * 0.10)
        q2 = (cx + dx * L, cy + dy * L + droop * L)
        le, ri = [], []
        for i in range(samples + 1):
            t = i / samples
            u = 1 - t
            px = u*u*q0[0] + 2*u*t*q1[0] + t*t*q2[0]
            py = u*u*q0[1] + 2*u*t*q1[1] + t*t*q2[1]
            tx = 2*u*(q1[0]-q0[0]) + 2*t*(q2[0]-q1[0])
            ty = 2*u*(q1[1]-q0[1]) + 2*t*(q2[1]-q1[1])
            ln = math.hypot(tx, ty) or 1
            nx, ny = -ty / ln, tx / ln
            bw = L * 0.13 * (math.sin(math.pi * min(1, t * 1.04)) ** 0.7)
            wl = bw * (0.3 + 1.2 * ((t * 9) % 1))
            wr = bw * (0.3 + 1.2 * ((t * 9 + 0.5) % 1))
            le.append((px + nx * wl, py + ny * wl))
            ri.append((px - nx * wr, py - ny * wr))
        parts.append(poly(le + ri[::-1]))
    for ox, oy in [(-3, 4), (2.5, 5), (0, 2)]:
        r = 2.3 * k
        parts.append(f"M{cx+ox-r:.1f} {cy+oy:.1f} a{r:.1f} {r:.1f} 0 1 0 {2*r:.1f} 0 a{r:.1f} {r:.1f} 0 1 0 {-2*r:.1f} 0 Z")
    return " ".join(parts)


def ridge(fn, x0, x1, step, bottom):
    pts = [(x, fn(x)) for x in range(x0, x1 + step, step)]
    return f"M{x0} {bottom} " + " ".join(f"L{x} {y:.1f}" for x, y in pts) + f" L{x1} {bottom} Z"


def banner():
    W, H = 1200, 300
    rnd = random.Random(11)
    css = """
.tw{animation:tw 4.5s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.2}50%{opacity:.95}}
.drift{animation:drift 26s ease-in-out infinite alternate}
@keyframes drift{from{transform:translateX(-40px)}to{transform:translateX(40px)}}
.sh{animation:sh 3.8s ease-in-out infinite}
@keyframes sh{0%,100%{opacity:.08}50%{opacity:.45}}
.flk{animation:flk 10s infinite}
@keyframes flk{0%,84%{fill:#EAF6FF}86%,91%{fill:#DC2626}93%,100%{fill:#EAF6FF}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""
    defs = f"""<defs>
<clipPath id="clip"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#060A12"/><stop offset=".45" stop-color="#0C1A2C"/>
  <stop offset=".72" stop-color="#16344F"/><stop offset="1" stop-color="#245676"/></linearGradient>
<radialGradient id="hglow" cx="72%" cy="74%" r="55%"><stop offset="0" stop-color="#38BDF8" stop-opacity=".30"/>
  <stop offset="1" stop-color="#38BDF8" stop-opacity="0"/></radialGradient>
<linearGradient id="far" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1B3651"/>
  <stop offset=".55" stop-color="#25506F"/><stop offset="1" stop-color="#2D6283"/></linearGradient>
<linearGradient id="mid" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0F2238"/>
  <stop offset="1" stop-color="#18405D"/></linearGradient>
<radialGradient id="mist"><stop offset="0" stop-color="#E0F2FE" stop-opacity=".16"/>
  <stop offset="1" stop-color="#E0F2FE" stop-opacity="0"/></radialGradient>
<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1D4A6B"/>
  <stop offset="1" stop-color="#0B1E31"/></linearGradient>
<radialGradient id="warm"><stop offset="0" stop-color="#BAE6FD" stop-opacity=".55"/>
  <stop offset="1" stop-color="#BAE6FD" stop-opacity="0"/></radialGradient>
<linearGradient id="refl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EAF6FF" stop-opacity=".5"/>
  <stop offset="1" stop-color="#EAF6FF" stop-opacity="0"/></linearGradient>
<linearGradient id="shade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#060A12" stop-opacity=".94"/>
  <stop offset=".55" stop-color="#060A12" stop-opacity=".55"/><stop offset="1" stop-color="#060A12" stop-opacity="0"/></linearGradient>
</defs>"""
    g = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', f'<rect width="{W}" height="{H}" fill="url(#hglow)"/>']
    for _ in range(46):
        x, y, r = rnd.uniform(420, 1190), rnd.uniform(8, 120), rnd.uniform(0.5, 1.4)
        cls = ' class="tw"' if rnd.random() < 0.3 else ""
        g.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#E0F2FE" opacity="{rnd.uniform(.25, .8):.2f}"{cls} '
                 f'style="animation-delay:-{rnd.uniform(0, 4.5):.1f}s"/>')
    g.append(f'<path d="{ridge(lambda x: 150 + 20*math.sin(x/97) + 13*math.sin(x/41 + 1) + 8*math.sin(x/23 + 2), 0, W, 8, H)}" fill="url(#far)"/>')
    for cx, cy, rx, ry, d in [(300, 200, 360, 30, 0), (820, 188, 420, 34, -9), (1100, 210, 300, 26, -17)]:
        g.append(f'<ellipse class="drift" style="animation-delay:{d}s" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#mist)"/>')
    g.append(f'<path d="{ridge(lambda x: 206 + 13*math.sin(x/130 + .5) + 7*math.sin(x/53 + 2), 0, W, 8, H)}" fill="url(#mid)"/>')
    g.append(f'<ellipse class="drift" style="animation-delay:-5s" cx="640" cy="226" rx="520" ry="16" fill="url(#mist)"/>')
    g.append(f'<path d="{ridge(lambda x: 231 + 2.5*math.sin(x/37) + 1.5*math.sin(x/11), 0, W, 6, 240)}" fill="#0A1828"/>')
    far_palms = [(610, 232, 46, 3), (648, 232, 60, -4), (700, 233, 40, 2), (858, 232, 66, 5), (902, 232, 52, -3),
                 (946, 233, 72, 4), (1086, 232, 58, -5), (1118, 232, 44, 3)]
    g.append('<path fill="#0B1A2B" d="' + " ".join(palm(x, b, h, l, 0.55, samples=20) for x, b, h, l in far_palms) + '"/>')
    hx, hy = 1012, 234
    g.append(f'<circle cx="{hx}" cy="{hy-14}" r="58" fill="url(#warm)"/>')
    house = [
        f'<rect x="{hx-34}" y="{hy-5}" width="68" height="5" fill="#070C16"/>',
        f'<rect x="{hx-29}" y="{hy-27}" width="58" height="22" fill="#0B1424"/>',
        f'<rect x="{hx-22}" y="{hy-21}" width="9" height="9" fill="#EAF6FF"/>',
        f'<rect x="{hx-4}" y="{hy-21}" width="8" height="16" fill="#EAF6FF" opacity=".92"/>',
        f'<rect x="{hx+13}" y="{hy-21}" width="9" height="9" fill="#EAF6FF" class="flk"/>',
        f'<path d="M{hx-22} {hy-16.5} h9 M{hx-17.5} {hy-21} v9 M{hx+13} {hy-16.5} h9 M{hx+17.5} {hy-21} v9" stroke="#0B1424" stroke-width="1"/>',
        f'<path d="M{hx-54} {hy-27} L{hx-48} {hy-25} L{hx-32} {hy-46} L{hx+32} {hy-46} L{hx+48} {hy-25} L{hx+54} {hy-27} L{hx+50} {hy-21} L{hx-50} {hy-21} Z" fill="#04070D"/>',
        f'<path d="M{hx-21} {hy-45} L{hx} {hy-64} L{hx+21} {hy-45} Z" fill="#04070D"/>',
        f'<path d="M{hx-11} {hy-46} L{hx} {hy-57} L{hx+11} {hy-46} Z" fill="#0E1A2C"/>',
    ]
    g += house
    g.append(f'<rect x="0" y="236" width="{W}" height="40" fill="url(#water)"/>')
    for x, w in [(hx-22, 9), (hx-4, 8), (hx+13, 9)]:
        g.append(f'<rect x="{x}" y="238" width="{w}" height="26" fill="url(#refl)"/>')
    for _ in range(26):
        x, y, w = rnd.uniform(380, 1180), rnd.uniform(241, 270), rnd.uniform(14, 60)
        g.append(f'<rect class="sh" style="animation-delay:-{rnd.uniform(0, 3.8):.1f}s" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" '
                 f'height="1.2" rx=".6" fill="#7DD3FC"/>')
    g.append(f'<path d="{ridge(lambda x: 279 + 5*math.sin(x/61) + 3*math.sin(x/19 + 1), 0, W, 6, H)}" fill="#04070D"/>')
    fore = [(1180, 290, 230, -26, 1.25), (1132, 292, 182, 16, 1.1), (1062, 290, 120, -10, 0.9), (770, 288, 150, -34, 1.0)]
    g.append('<path fill="#04070D" d="' + " ".join(palm(x, b, h, l, k, samples=40) for x, b, h, l, k in fore) + '"/>')
    g.append(f'<rect width="760" height="{H}" fill="url(#shade)"/>')
    dot = f'<tspan fill="{SKY}"> · </tspan>'
    g.append(text(64, 100, "LENIN JACOB REGI", 15, "#38BDF8", 700, MONO, ls=4))
    g.append(text(62, 158, f"Build{dot}Break{dot}Detect", 46, "#F8FAFC", 300, ls=0.5, raw=True))
    g.append('<line x1="64" y1="184" x2="452" y2="184" stroke="#F8FAFC" stroke-opacity=".28"/>')
    g.append(text(64, 216, "Recommender Systems Engineer", 19, "#E2E8F0", 600))
    g.append(text(64, 244, "RETRIEVAL · RANKING · RECSYSOPS · COLD START", 13, "#94A3B8", 500, MONO, ls=1.5))
    body = defs + f'<g clip-path="url(#clip)">{"".join(g)}</g>' + \
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="#263041"/>'
    return svg(W, H, body, "Lenin Jacob Regi, Recommender Systems Engineer. Build, break, detect.", css)


# ---------------------------------------------------------------- cards
def chip(x, y, label, t, size=14, h=30, active=False, dot=False):
    w = 24 + len(label) * size * 0.6 + (14 if dot else 0)
    fill = t["chip"]
    stroke = SKY if active else t["border"]
    col = t["sky"] if active else t["muted"]
    s = f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="{h}" rx="{h/2:.0f}" fill="{fill}" stroke="{stroke}"/>'
    tx = x + 12
    if dot:
        s += f'<circle cx="{x+15:.0f}" cy="{y+h/2:.0f}" r="4" fill="{SKY}"/>'
        tx += 14
    s += text(f"{tx:.0f}", f"{y + h/2 + size*0.36:.0f}", label, size, col, 600, MONO)
    return s, w


def about(t):
    W, H = 580, 300
    b = [frame(W, H, t), text(32, 52, "About me", 24, t["text"], 700)]
    body = ("I'm a recommender systems engineer. I build retrieval and ranking systems and keep them healthy "
            "in production. My niche is RecSysOps and cold start: catching the silent failures dashboards miss.")
    for i, line in enumerate(wrap(body, 17, W - 64)):
        b.append(text(32, 92 + i * 27, line, 17, t["muted"]))
    x = 32
    for lab in ["SIH 2025 GRAND FINALIST", "B.TECH CSE (AI/ML) '27"]:
        c, w = chip(x, 200, lab, t)
        b.append(c)
        x += w + 10
    x = 32
    for lab, act in [("GENAI COMMUNITY LEAD · KIDS", False), ("OPEN TO INTERNSHIPS", True)]:
        c, w = chip(x, 240, lab, t, active=act, dot=act)
        b.append(c)
        x += w + 10
    return svg(W, H, "".join(b), "About me: " + body + " Smart India Hackathon 2025 Grand Finalist. "
               "B.Tech CSE (AI/ML), Karunya, 2027. Generative AI community lead at KIDS. Open to internships.")


def stats(t, s):
    W, H = 400, 300
    b = [frame(W, H, t)]
    for i, hh in enumerate([9, 15, 21]):
        b.append(f'<rect x="{32 + i*7}" y="{47 - hh}" width="4.5" height="{hh}" rx="1.5" fill="{SKY}"/>')
    b.append(text(62, 47, "GitHub stats", 22, t["text"], 700))
    b.append(text(W - 32, 45, "AS OF " + s["date"], 11, t["muted"], 600, MONO, "end", 1))
    b.append(text(W / 2, 104, f'{s["total"]:,}', 44, t["text"], 800, anchor="middle"))
    b.append(text(W / 2, 128, "contributions in the last year", 14, t["muted"], anchor="middle"))
    weeks = s["weeks"][-26:]
    mx = max(weeks) or 1
    x0, x1, base, top = 32, W - 32, 184, 142
    bw = (x1 - x0) / len(weeks)
    for i, v in enumerate(weeks):
        hh = max(2.0, (base - top) * v / mx)
        b.append(f'<rect x="{x0 + i*bw + 1.4:.1f}" y="{base - hh:.1f}" width="{bw - 2.8:.1f}" height="{hh:.1f}" rx="1.5" '
                 f'fill="{SKY if v else t["track"]}"/>')
    b.append(f'<line x1="32" y1="200" x2="{W-32}" y2="200" stroke="{t["border"]}"/>')
    rows = [("Public repositories", s["repos"]), ("Followers", s["followers"]), ("Following", s["following"])]
    for i, (lab, v) in enumerate(rows):
        y = 226 + i * 25
        b.append(text(32, y, lab, 15, t["muted"]))
        b.append(text(W - 32, y, str(v), 15, t["text"], 700, anchor="end"))
    return svg(W, H, "".join(b), f'GitHub stats: {s["total"]} contributions in the last year, {s["repos"]} public '
               f'repositories, {s["followers"]} followers, {s["following"]} following.')


def tech(t):
    W = 580
    size, h, gap = 14, 32, 8
    x, y = 32, 70
    b = []
    for slug, label in STACK:
        w = 10 + 15 + 7 + len(label) * size * 0.56 + 11
        if x + w > W - 32:
            x, y = 32, y + h + 10
        b.append(f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="{h}" rx="8" fill="{t["chip"]}" stroke="{t["border"]}"/>')
        b.append(icon(slug, f"{x+10:.0f}", f"{y + (h-15)/2:.1f}", 15, t["sky"]))
        b.append(text(f"{x+32:.0f}", f"{y + h/2 + 5:.0f}", label, size, t["text"], 500))
        x += w + gap
    H = max(260, y + h + 30)
    return [frame(W, H, t), text(32, 50, "Tech stack", 22, t["text"], 700)] + b, H


def current(t, H):
    W = 400
    b = [frame(W, H, t),
         f'<circle cx="41" cy="40" r="9" fill="none" stroke="{SKY}" stroke-width="2.2"/><circle cx="41" cy="40" r="3.6" fill="{SKY}"/>',
         text(60, 47, "Currently working on", 22, t["text"], 700)]
    lines = wrap("Building RecChaos in public: six recommender papers rebuilt into one stack, then broken on purpose.",
                 17, W - 50 - 32)
    for i, line in enumerate(lines):
        b.append(text(50, 92 + i * 25, line, 17, t["text"]))
    y = 92 + len(lines) * 25 + 12
    b.append(text(50, y, f"WEEK {WEEK} OF 11", 12, t["muted"], 600, MONO, ls=1.5))
    sw = (W - 32 - 50 - 10 * 4) / 11
    for i in range(11):
        on = i < WEEK
        b.append(f'<rect x="{50 + i*(sw+4):.1f}" y="{y+10}" width="{sw:.1f}" height="8" rx="2" fill="{SKY if on else t["track"]}"/>')
    b.append(text(50, y + 46, "Next: " + NEXT, 15, t["sky"], 600))
    b.append(f'<rect x="32" y="72" width="4" height="{y + 52 - 72}" rx="2" fill="{SKY}"/>')
    return svg(W, H, "".join(b), f"Currently working on: RecChaos, week {WEEK} of 11. Next: {NEXT}.")


def fit_lines(s, width, max_lines=3, sizes=(15, 14, 13)):
    for size in sizes:
        lines = wrap(s, size, width)
        if len(lines) <= max_lines:
            return lines, size
    return wrap(s, sizes[-1], width), sizes[-1]


def project(t, kind):
    W, H = 490, 178
    b = [frame(W, H, t)]
    if kind == "recchaos":
        b.append(logo(24, 22, 28, t["border"]))
        b.append(text(62, 42, "RecChaos", 20, t["sky"], 700))
        b.append(text(166, 41, "BUILDING IN PUBLIC", 11, t["muted"], 600, MONO, ls=1))
        desc = "Fault-injection benchmark for recommender systems. Six papers rebuilt, then broken on purpose."
        meta = [("Python", True), (f"Week {WEEK} of 11", False), ("✓ " + ", ".join(DONE) + " done", False)]
        cx, cy, r = W - 84, 84, 46
        circ = 2 * math.pi * r
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["track"]}" stroke-width="9"/>')
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{SKY}" stroke-width="9" stroke-linecap="round" '
                 f'stroke-dasharray="{circ * WEEK / 11:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>')
        b.append(text(cx, cy + 4, f"W{WEEK}", 24, t["text"], 800, anchor="middle"))
        b.append(text(cx, cy + 24, "of 11", 12, t["muted"], 500, MONO, "middle"))
        label = "RecChaos: fault-injection benchmark for recommender systems."
    else:
        b.append(f'<circle cx="38" cy="36" r="13" fill="{INK}" stroke="{t["border"]}"/><circle cx="38" cy="36" r="6" fill="#EAF6FF"/>'
                 f'<circle cx="38" cy="36" r="10" fill="none" stroke="{SKY}" stroke-opacity=".6"/>')
        b.append(text(62, 42, "Kinlight", 20, t["sky"], 700))
        b.append(text(152, 41, "MY FIRST GAME", 11, t["muted"], 600, MONO, ls=1))
        desc = "A daily co-op 3D browser game: play with the recorded lights of everyone before you."
        meta = [("TypeScript", True), ("▶ Play in your browser", False)]
        thumb = base64.b64encode((HERE / "kinlight-thumb.jpg").read_bytes()).decode()
        tx, ty, tw, th = W - 24 - 165, 24, 165, 110
        b.append(f'<clipPath id="th"><rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="10"/></clipPath>')
        b.append(f'<image href="data:image/jpeg;base64,{thumb}" x="{tx}" y="{ty}" width="{tw}" height="{th}" '
                 f'preserveAspectRatio="xMidYMid slice" clip-path="url(#th)"/>')
        b.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="10" fill="none" stroke="{t["border"]}"/>')
        label = "Kinlight: a daily co-op 3D browser game. Play it free in any browser."
    text_w = (W - 84 - 46 - 20 - 24) if kind == "recchaos" else (W - 24 - 24 - 165 - 20)
    lines, size = fit_lines(desc, text_w)
    assert size == 15, f"{kind} description needs shortening: {lines}"
    for i, line in enumerate(lines):
        b.append(text(24, 74 + i * (size + 7), line, size, t["muted"]))
    x = 24
    for lab, lang in meta:
        if lang:
            b.append(f'<circle cx="{x+6}" cy="151" r="6" fill="{SKY}"/>')
            b.append(text(x + 18, 156, lab, 14, t["text"], 500))
            x += 18 + len(lab) * 14 * 0.56 + 18
        else:
            b.append(text(x, 156, lab, 14, t["muted"]))
            x += len(lab) * 14 * 0.56 + 18
    return svg(W, H, "".join(b), label)


def connect(kind):
    b = [f'<circle cx="28" cy="28" r="26.5" fill="{INK}" stroke="{SKY}" stroke-width="1.5"/>']
    if kind == "linkedin":
        b.append(text(28, 36, "in", 23, "#38BDF8", 800, anchor="middle"))
        label = "LinkedIn"
    elif kind == "website":
        b.append('<g fill="none" stroke="#38BDF8" stroke-width="1.8"><circle cx="28" cy="28" r="11"/>'
                 '<ellipse cx="28" cy="28" rx="4.8" ry="11"/><path d="M17 28 H39 M19.5 22.5 H36.5 M19.5 33.5 H36.5"/></g>')
        label = "Website"
    else:
        b.append(f'<path d="M14 30 H20 L23.5 21 L28 37 L31.5 25 L34 30 H42" fill="none" stroke="#38BDF8" stroke-width="2.4" '
                 f'stroke-linecap="round" stroke-linejoin="round"/><circle cx="40" cy="20" r="2.8" fill="{RED}"/>')
        label = "RecChaos docs"
    return svg(56, 56, "".join(b), label)


# ---------------------------------------------------------------- data
def fetch_stats():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    q = f"""{{ user(login: "{LOGIN}") {{
      followers {{ totalCount }} following {{ totalCount }}
      repositories(privacy: PUBLIC, ownerAffiliations: OWNER) {{ totalCount }}
      contributionsCollection {{ contributionCalendar {{ totalContributions
        weeks {{ contributionDays {{ contributionCount }} }} }} }} }} }}"""
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": q}).encode(),
                                 headers={"Authorization": f"Bearer {token}", "User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    if d.get("errors"):
        sys.exit(f"GraphQL error: {d['errors']}")
    u = d["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    return dict(total=cal["totalContributions"],
                weeks=[sum(day["contributionCount"] for day in w["contributionDays"]) for w in cal["weeks"]],
                repos=u["repositories"]["totalCount"], followers=u["followers"]["totalCount"],
                following=u["following"]["totalCount"],
                date=dt.datetime.now(dt.timezone.utc).strftime("%d %b").upper())


def main():
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    s = fetch_stats()
    for k, t in THEMES.items():
        (out / f"stats-{k}.svg").write_text(stats(t, s))
    if "--stats-only" in sys.argv:
        print("stats refreshed:", {k: v for k, v in s.items() if k != "weeks"})
        return
    (out / "banner.svg").write_text(banner())
    for k, t in THEMES.items():
        (out / f"about-{k}.svg").write_text(about(t))
        parts, H = tech(t)
        (out / f"tech-{k}.svg").write_text(svg(580, H, "".join(parts), "Tech stack: " + ", ".join(l for _, l in STACK)))
        (out / f"current-{k}.svg").write_text(current(t, H))
        (out / f"recchaos-{k}.svg").write_text(project(t, "recchaos"))
        (out / f"kinlight-{k}.svg").write_text(project(t, "kinlight"))
    for kind in ["linkedin", "website", "docs"]:
        (out / f"connect-{kind}.svg").write_text(connect(kind))
    print("written:", ", ".join(sorted(p.name for p in out.iterdir())))


if __name__ == "__main__":
    main()
