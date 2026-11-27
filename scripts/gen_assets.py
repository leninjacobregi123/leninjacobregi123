#!/usr/bin/env python3
"""Generate the SVGs for Lenin's GitHub profile: a profile that works like a recommender.

    GITHUB_TOKEN=$(gh auth token) python3 -I scripts/gen_assets.py assets     # everything
    python3 scripts/gen_assets.py assets --ops-only                            # what the daily Action runs

Palette (RecChaos brand): ink black, white, sky blue; red only for faults.
Edit FEED, PROFICIENCY and MODEL_CARD below. Every claim must link to public proof.
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import math
import os
import pathlib
import random
import re
import sys
import urllib.request
from xml.sax.saxutils import escape

HERE = pathlib.Path(__file__).resolve().parent
LOGIN = "leninjacobregi123"
RECCHAOS_RAW = f"https://raw.githubusercontent.com/{LOGIN}/RecChaos/main/docs/"

# ============================================================== content (edit here)
WEEK = 1  # RecChaos week, of 11

FEED = [
    dict(title="RecChaos", tag="BUILDING IN PUBLIC", visual="ring", link=f"https://github.com/{LOGIN}/RecChaos",
         desc="A fault-injection benchmark for recommender systems: six landmark papers rebuilt into one stack, then broken on purpose.",
         because="you're into recommender systems", meta="Python · Week 1 of 11"),
    dict(title="EXP-001 · Week 1 result", tag="HONEST RESULTS", visual="sixx",
         link="https://leninjacobregi.me/RecChaos/experiments/exp-001-week1-baselines/",
         desc="Amazon's 2003 item-to-item CF beats all-time bestsellers 6×, then loses to a simple 30-day popularity list.",
         because="honest results beat cherry-picked ones", meta="Bootstrap CIs · Dec 2022 test"),
    dict(title="Ammini", tag="LLM FROM SCRATCH", visual="moe", link=f"https://github.com/{LOGIN}/Ammini",
         desc="A Malayalam language model built from scratch: own BPE tokenizer, RoPE + grouped-query attention, sparse MoE.",
         because="you like models built from first principles", meta="Python · PyTorch"),
    dict(title="Kinlight", tag="MY FIRST GAME", visual="thumb", link="https://kinlight.kinlight.workers.dev",
         desc="A daily co-op 3D browser game: play with the recorded lights of everyone who played before you today.",
         because="everyone needs a break", meta="TypeScript · Babylon.js"),
]

# (area, sub-skills, level 2-4, proof label, proof link). Levels are Lenin's own call.
PROFICIENCY = [
    ("Recommender systems", "retrieval · ranking · offline evaluation", 4, "RecChaos · P1 · EXP-001",
     "https://leninjacobregi.me/RecChaos/projects/p1-item-to-item/"),
    ("RAG & agentic AI apps", "agentic retrieval · multi-LLM · tool use", 4, "Scoratis (socratic-ai)",
     f"https://github.com/{LOGIN}/socratic-ai"),
    ("LLMs from scratch", "tokenizer · attention · mixture-of-experts", 3, "Ammini (Malayalam LLM)",
     f"https://github.com/{LOGIN}/Ammini"),
    ("ML evaluation", "time splits · ranking metrics · bootstrap CIs", 3, "RecChaos harness · lm-eval fork",
     "https://leninjacobregi.me/RecChaos/experiments/exp-001-week1-baselines/"),
    ("Full-stack & backend", "Next.js · Node · Postgres · Docker", 3, "openmaic · sih26136 · 4 merged PRs",
     f"https://github.com/{LOGIN}/karunya-openmaic"),
    ("Real-time 3D web", "TypeScript · Babylon.js · Cloudflare Workers", 3, "Kinlight (live)",
     "https://kinlight.kinlight.workers.dev"),
]
LEVELS = {4: "ADVANCED", 3: "PROFICIENT", 2: "WORKING"}

MODEL_CARD = {
    "INTENDED USE": ["Retrieval & ranking systems", "RecSysOps: detect, diagnose, fix", "Cold start & new items"],
    "TRAINING DATA": ["SIH 2025 Grand Finalist", "GenAI community lead · KIDS (100+)", "4 merged PRs · curelex-public-hms"],
    "LIMITATIONS": ["Student model: full-time from 2027", "Internships: available now", "Next training run: Spark, DSA"],
}

TOOLS = [("python", "Python"), ("pytorch", "PyTorch"), ("huggingface", "Hugging Face"), ("pandas", "pandas"),
         ("numpy", "NumPy"), ("fastapi", "FastAPI"), ("langchain", "LangChain"), ("ollama", "Ollama"),
         ("milvus", "Milvus"), ("postgresql", "PostgreSQL"), ("supabase", "Supabase"), ("docker", "Docker"),
         ("typescript", "TypeScript"), ("javascript", "JavaScript"), ("react", "React"), ("nextdotjs", "Next.js"),
         ("nodedotjs", "Node.js"), ("babylondotjs", "Babylon.js"), ("cloudflareworkers", "Cloudflare Workers"),
         ("vercel", "Vercel"), ("linux", "Linux"), ("git", "Git")]

# ============================================================== style
SANS = "'Inter','Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',monospace"
SKY, INK, RED = "#0EA5E9", "#0A0E17", "#DC2626"
THEMES = {
    "dark": dict(card="#111723", border="#263041", text="#F8FAFC", muted="#94A3B8", sky="#38BDF8",
                 chip="#0B111C", track="#1E2836"),
    "light": dict(card="#F6F8FB", border="#E3E8EF", text="#0A0E17", muted="#64748B", sky="#0369A1",
                  chip="#FFFFFF", track="#E3E8EF"),
}
ICONS_FILE = HERE / "icons.json"
ICONS = json.loads(ICONS_FILE.read_text()) if ICONS_FILE.exists() else {}


# ============================================================== helpers
def attr(s):
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


def width(s, size, family=SANS, bold=False, ls=0):
    """Approximate rendered width: monospace is uniform; proportional text uses per-character classes."""
    if family == MONO:
        return len(s) * (size * 0.6 + ls)
    em = 0.0
    for ch in s:
        if ch == " ":
            em += 0.28
        elif ch in "il.,:;'|!·•-()[]1tfjrI":
            em += 0.31
        elif ch in "MWmw@%×":
            em += 0.86
        elif ch.isupper():
            em += 0.68
        elif ch.isdigit():
            em += 0.58
        else:
            em += 0.55
    return em * size * (1.05 if bold else 1.0) + len(s) * ls


def wrap(s, size, w):
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if cur and width(trial, size) > w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + ([cur] if cur else [])


def frame(w, h, t):
    return f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="14" fill="{t["card"]}" stroke="{t["border"]}"/>'


def icon(slug, x, y, size, fill):
    return f'<path transform="translate({x:.1f} {y:.1f}) scale({size/24:.4f})" d="{ICONS[slug]}" fill="{fill}"/>'


def logo(x, y, s, border="#263041"):
    k = s / 64
    return (f'<g transform="translate({x} {y}) scale({k:.4f})"><rect width="64" height="64" rx="14" fill="{INK}" '
            f'stroke="{border}" stroke-width="{1/k:.2f}"/><path d="M10 36 H22 L27 22 L34 46 L39 30 L43 36 H54" fill="none" '
            f'stroke="{SKY}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="50" cy="18" r="5" fill="{RED}"/></g>')


def poly(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


# ============================================================== banner (one version for both themes)
def palm(x, base, h, lean, k=1.0, samples=36):
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
@keyframes flk{0%,82%{fill:#EAF6FF}84%,93%{fill:#DC2626}95%,100%{fill:#EAF6FF}}
.spk,.bad,.alrt{opacity:0;animation:show 10s infinite}
@keyframes show{0%,86%{opacity:0}88%,93%{opacity:1}95%,100%{opacity:0}}
.ok{animation:hide 10s infinite}
@keyframes hide{0%,86%{opacity:1}88%,93%{opacity:0}95%,100%{opacity:1}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""
    defs = f"""<defs>
<clipPath id="clip"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#060A12"/><stop offset=".45" stop-color="#0C1A2C"/>
  <stop offset=".72" stop-color="#16344F"/><stop offset="1" stop-color="#245676"/></linearGradient>
<radialGradient id="hglow" cx="72%" cy="74%" r="55%"><stop offset="0" stop-color="#38BDF8" stop-opacity=".30"/>
  <stop offset="1" stop-color="#38BDF8" stop-opacity="0"/></radialGradient>
<linearGradient id="far" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1B3651"/><stop offset=".55" stop-color="#25506F"/>
  <stop offset="1" stop-color="#2D6283"/></linearGradient>
<linearGradient id="mid" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0F2238"/><stop offset="1" stop-color="#18405D"/></linearGradient>
<radialGradient id="mist"><stop offset="0" stop-color="#E0F2FE" stop-opacity=".16"/><stop offset="1" stop-color="#E0F2FE" stop-opacity="0"/></radialGradient>
<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1D4A6B"/><stop offset="1" stop-color="#0B1E31"/></linearGradient>
<radialGradient id="warm"><stop offset="0" stop-color="#BAE6FD" stop-opacity=".55"/><stop offset="1" stop-color="#BAE6FD" stop-opacity="0"/></radialGradient>
<linearGradient id="refl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EAF6FF" stop-opacity=".5"/><stop offset="1" stop-color="#EAF6FF" stop-opacity="0"/></linearGradient>
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
    g.append('<ellipse class="drift" style="animation-delay:-5s" cx="640" cy="226" rx="520" ry="16" fill="url(#mist)"/>')
    g.append(f'<path d="{ridge(lambda x: 231 + 2.5*math.sin(x/37) + 1.5*math.sin(x/11), 0, W, 6, 240)}" fill="#0A1828"/>')
    far_palms = [(610, 232, 46, 3), (648, 232, 60, -4), (700, 233, 40, 2), (858, 232, 66, 5), (902, 232, 52, -3),
                 (946, 233, 72, 4), (1086, 232, 58, -5), (1118, 232, 44, 3)]
    g.append('<path fill="#0B1A2B" d="' + " ".join(palm(x, b, h, l, 0.55, samples=20) for x, b, h, l in far_palms) + '"/>')
    hx, hy = 1012, 234
    g.append(f'<circle cx="{hx}" cy="{hy-14}" r="58" fill="url(#warm)"/>')
    g += [
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
    g.append(f'<rect x="0" y="236" width="{W}" height="40" fill="url(#water)"/>')
    for x, w in [(hx-22, 9), (hx-4, 8), (hx+13, 9)]:
        g.append(f'<rect x="{x}" y="238" width="{w}" height="26" fill="url(#refl)"/>')
    for _ in range(26):
        x, y, w = rnd.uniform(380, 1180), rnd.uniform(241, 270), rnd.uniform(14, 60)
        g.append(f'<rect class="sh" style="animation-delay:-{rnd.uniform(0, 3.8):.1f}s" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" '
                 'height="1.2" rx=".6" fill="#7DD3FC"/>')
    # the river is a monitor line: flat while healthy, spikes when the window fails
    g.append('<path d="M600 258 H1190" stroke="#38BDF8" stroke-opacity=".35" stroke-width="1.6" fill="none"/>')
    g.append('<path class="spk" d="M950 258 H985 L994 244 L1003 270 L1012 236 L1021 266 L1029 258 H1070" stroke="#38BDF8" '
             'stroke-width="2.2" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
    g.append(f'<path d="{ridge(lambda x: 279 + 5*math.sin(x/61) + 3*math.sin(x/19 + 1), 0, W, 6, H)}" fill="#04070D"/>')
    fore = [(1180, 290, 230, -26, 1.25), (1132, 292, 182, 16, 1.1), (1062, 290, 120, -10, 0.9), (770, 288, 150, -34, 1.0)]
    g.append('<path fill="#04070D" d="' + " ".join(palm(x, b, h, l, k, samples=40) for x, b, h, l, k in fore) + '"/>')
    g.append(f'<g class="alrt"><rect x="1036" y="140" width="108" height="26" rx="6" fill="#0A0E17" stroke="#38BDF8" stroke-width="1.5"/>'
             f'{text(1090, 158, "DETECTED", 13, "#38BDF8", 700, MONO, "middle", 1.5)}</g>')
    g.append(f'<rect width="760" height="{H}" fill="url(#shade)"/>')
    dot = f'<tspan fill="{SKY}"> · </tspan>'
    g.append(text(64, 72, "LENIN JACOB REGI", 15, "#38BDF8", 700, MONO, ls=4))
    g.append(text(62, 128, f"Build{dot}Break{dot}Detect", 46, "#F8FAFC", 300, ls=0.5, raw=True))
    g.append('<line x1="64" y1="152" x2="452" y2="152" stroke="#F8FAFC" stroke-opacity=".28"/>')
    g.append(text(64, 184, "Recommender Systems Engineer", 19, "#E2E8F0", 600))
    g.append(text(64, 210, "RETRIEVAL · RANKING · RECSYSOPS · COLD START", 13, "#94A3B8", 500, MONO, ls=1.5))
    g.append('<rect x="64" y="230" width="500" height="36" rx="8" fill="#0A0E17" fill-opacity=".85" stroke="#263041"/>')
    g.append(text(80, 253, "› GET /recommend?user=you&amp;k=4", 15, "#E2E8F0", 500, MONO, raw=True))
    g.append(text(548, 253, "200 OK", 15, "#38BDF8", 700, MONO, "end", cls="ok"))
    g.append(f'<g class="bad"><circle cx="384" cy="248" r="4" fill="{RED}"/>{text(548, 253, "ANOMALY DETECTED", 14, "#38BDF8", 700, MONO, "end")}</g>')
    body = defs + f'<g clip-path="url(#clip)">{"".join(g)}</g>' + \
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="#263041"/>'
    return svg(W, H, body, "Lenin Jacob Regi, Recommender Systems Engineer. Build, break, detect.", css)


# ============================================================== feed
def feed_header(t):
    W, H = 1200, 104
    b = [text(4, 40, "RECOMMENDED FOR YOU", 16, t["sky"], 700, MONO, ls=3),
         text(4, 84, "My work, ranked for you", 30, t["text"], 800),
         text(W - 4, 84, "k = 4 · with the reason for each pick", 16, t["muted"], 500, MONO, "end")]
    return svg(W, H, "".join(b), "Recommended for you: my work, ranked, with the reason for each pick.")


def feed_visual(t, kind):
    if kind == "ring":
        cx, cy, r = 1080, 85, 46
        circ = 2 * math.pi * r
        return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["track"]}" stroke-width="10"/>'
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{SKY}" stroke-width="10" stroke-linecap="round" '
                f'stroke-dasharray="{circ * WEEK / 11:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>'
                + text(cx, cy + 6, f"W{WEEK}", 28, t["text"], 800, anchor="middle")
                + text(cx, cy + 28, "of 11", 13, t["muted"], 600, MONO, "middle"))
    if kind == "sixx":
        return (text(1080, 98, "6×", 64, SKY, 800, anchor="middle")
                + text(1080, 128, "vs bestsellers", 16, t["muted"], 500, anchor="middle"))
    if kind == "moe":
        s = [f'<g stroke="{t["muted"]}" stroke-width="1.6" fill="none">']
        ys = [40, 68, 102, 130]
        for y in ys:
            s.append(f'<path d="M1012 85 C1030 85 1030 {y} 1046 {y}"/><path d="M1110 {y} C1126 {y} 1126 85 1142 85"/>')
        s.append("</g>")
        s.append(f'<circle cx="972" cy="85" r="8" fill="{SKY}"/><path d="M980 85 H996" stroke="{t["muted"]}" stroke-width="1.6"/>')
        s.append(f'<path d="M1004 77 L1012 85 L1004 93 L996 85 Z" fill="{t["card"]}" stroke="{SKY}" stroke-width="2"/>')
        for i, y in enumerate(ys):
            on = i in (1, 2)
            s.append(f'<rect x="1046" y="{y-10}" width="64" height="20" rx="5" fill="{SKY if on else "none"}" '
                     f'stroke="{SKY if on else t["muted"]}" stroke-width="1.5" stroke-opacity="{1 if on else .7}"/>')
        s.append(f'<circle cx="1150" cy="85" r="8" fill="{t["card"]}" stroke="{SKY}" stroke-width="2.5"/>')
        return "".join(s)
    if kind == "thumb":
        data = base64.b64encode((HERE / "kinlight-thumb.jpg").read_bytes()).decode()
        x, y, w, h = 958, 24, 208, 122
        return (f'<clipPath id="th"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/></clipPath>'
                f'<image href="data:image/jpeg;base64,{data}" x="{x}" y="{y}" width="{w}" height="{h}" '
                f'preserveAspectRatio="xMidYMid slice" clip-path="url(#th)"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="{t["border"]}"/>')
    return ""


def feed_row(t, rank, item):
    W, H = 1200, 170
    b = [frame(W, H, t), text(40, 104, f"#{rank}", 44, t["sky"], 800),
         f'<line x1="128" y1="30" x2="128" y2="{H-30}" stroke="{t["border"]}"/>',
         text(156, 56, item["title"], 26, t["text"], 700),
         text(156 + width(item["title"], 26, bold=True) + 16, 55, item["tag"], 13, t["muted"], 700, MONO, ls=1.5)]
    lines = wrap(item["desc"], 19, 920 - 156)
    assert len(lines) <= 2, f"shorten: {item['desc']}"
    for j, line in enumerate(lines):
        b.append(text(156, 91 + j * 26, line, 19, t["muted"]))
    b.append(text(156, 145, "BECAUSE", 13, t["sky"], 700, MONO, ls=2))
    b.append(text(246, 145, item["because"], 17, t["text"], 600))
    end_because = 246 + width(item["because"], 17, bold=True)
    if 920 - width(item["meta"], 15) > end_because + 24:
        b.append(text(920, 145, item["meta"], 15, t["muted"], 500, anchor="end"))
    b.append(feed_visual(t, item["visual"]))
    return svg(W, H, "".join(b), f"#{rank} {item['title']}: {item['desc']} Because {item['because']}.")


# ============================================================== model card + proficiency
def model_card(t):
    W, H = 1200, 340
    b = [frame(W, H, t), text(40, 52, "MODEL CARD", 15, t["sky"], 700, MONO, ls=3),
         text(40, 98, "lenin-recsys", 38, t["text"], 800)]
    vx = 40 + width("lenin-recsys", 38, bold=True) + 18
    b.append(f'<rect x="{vx:.0f}" y="72" width="78" height="32" rx="8" fill="{t["chip"]}" stroke="{SKY}"/>')
    b.append(text(f"{vx + 39:.0f}", 94, "v2027", 16, t["sky"], 700, MONO, "middle"))
    b.append(text(40, 132, "Recommender Systems Engineer · B.Tech CSE (AI/ML), Karunya Institute of Technology and Sciences",
                  18, t["muted"]))
    b.append(f'<line x1="40" y1="156" x2="{W-40}" y2="156" stroke="{t["border"]}"/>')
    for col, (head, items) in enumerate(MODEL_CARD.items()):
        x = 40 + col * 380
        b.append(text(x, 194, head, 14, t["sky"], 700, MONO, ls=2))
        for i, it in enumerate(items):
            b.append(f'<circle cx="{x+4}" cy="{221 + i*30}" r="3" fill="{t["muted"]}"/>')
            b.append(text(x + 16, 227 + i * 30, it, 17, t["text"]))
    b.append(f'<line x1="40" y1="300" x2="{W-40}" y2="300" stroke="{t["border"]}"/>')
    b.append(text(40, 324, "CAPABILITIES BELOW · EVERY LEVEL LINKS TO PUBLIC PROOF", 13, t["muted"], 700, MONO, ls=1.5))
    lx = W - 40
    for lvl in (2, 3, 4):
        lab = LEVELS[lvl].lower()
        w = width(lab, 13, MONO) + 5 * 14 + 10
        lx -= w + 24
        for k in range(5):
            b.append(f'<circle cx="{lx + 6 + k*14:.0f}" cy="319" r="5" fill="{SKY if k < lvl else t["track"]}"/>')
        b.append(text(f"{lx + 5*14 + 8:.0f}", 324, lab, 13, t["muted"], 600, MONO))
    label = "Model card: lenin-recsys v2027. " + " ".join(f"{h}: {', '.join(v)}." for h, v in MODEL_CARD.items())
    return svg(W, H, "".join(b), label)


def prof_row(t, area, sub, lvl, proof):
    W, H = 1200, 104
    b = [frame(W, H, t), text(40, 50, area, 24, t["text"], 700), text(40, 80, sub, 17, t["muted"])]
    for k in range(5):
        b.append(f'<circle cx="{570 + k*28}" cy="44" r="9.5" fill="{SKY if k < lvl else t["track"]}"/>')
    b.append(text(560, 81, LEVELS[lvl], 14, t["sky"] if lvl >= 4 else t["text"], 700, MONO, ls=2))
    b.append(text(800, 44, "PROOF", 12, t["muted"], 700, MONO, ls=2))
    b.append(text(800, 76, proof + " →", 19, t["sky"], 600))
    return svg(W, H, "".join(b), f"{area} ({sub}): {LEVELS[lvl].lower()}. Proof: {proof}.")


def toolchain(t):
    W = 1200
    size, h, gap = 18, 42, 10
    x, y = 40, 78
    chips = []
    for slug, label in TOOLS:
        w = 14 + 20 + 10 + width(label, size) + 14
        if x + w > W - 40:
            x, y = 40, y + h + 12
        chips.append(f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="{h}" rx="10" fill="{t["chip"]}" stroke="{t["border"]}"/>')
        chips.append(icon(slug, x + 14, y + (h - 20) / 2, 20, t["sky"]))
        chips.append(text(f"{x + 44:.0f}", f"{y + h/2 + 6.5:.0f}", label, size, t["text"], 500))
        x += w + gap
    H = y + h + 36
    b = [frame(W, H, t), text(40, 52, "TOOLCHAIN", 15, t["sky"], 700, MONO, ls=3)] + chips
    return svg(W, H, "".join(b), "Toolchain: " + ", ".join(l for _, l in TOOLS))


# ============================================================== ops panel (refreshed daily)
def ops(t, d):
    W, H = 1200, 380
    b = [frame(W, H, t), text(40, 52, "OPS · lenin.prod", 15, t["sky"], 700, MONO, ls=3)]
    px = 40 + width("OPS · lenin.prod", 15, MONO, ls=3) + 16
    live = d["shipping"]
    pill = "SHIPPING" if live else "QUIET"
    pw = width(pill, 13, MONO, ls=1.5) + 40
    b.append(f'<rect x="{px:.0f}" y="32" width="{pw:.0f}" height="28" rx="14" fill="{t["chip"]}" stroke="{SKY if live else t["border"]}"/>')
    b.append(f'<circle cx="{px + 16:.0f}" cy="46" r="5" fill="{SKY if live else t["muted"]}"/>')
    b.append(text(f"{px + 28:.0f}", 51, pill, 13, t["sky"] if live else t["muted"], 700, MONO, ls=1.5))
    b.append(text(W - 40, 51, f"AS OF {d['date']} · REFRESHED DAILY", 13, t["muted"], 600, MONO, "end", 1))
    b.append(text(40, 104, "CONTRIBUTIONS · LAST 52 WEEKS", 13, t["muted"], 700, MONO, ls=1.5))
    b.append(text(40, 156, f"{d['total']:,}", 50, t["text"], 800))
    weeks = d["weeks"][-52:]
    mx = max(weeks) or 1
    x0, x1, base, top = 40, 700, 300, 178
    bw = (x1 - x0) / len(weeks)
    for i, v in enumerate(weeks):
        hh = max(2.0, (base - top) * v / mx)
        b.append(f'<rect x="{x0 + i*bw + 1.6:.1f}" y="{base - hh:.1f}" width="{bw - 3.2:.1f}" height="{hh:.1f}" rx="2" '
                 f'fill="{SKY if v else t["track"]}"/>')
    b.append(f'<line x1="740" y1="84" x2="740" y2="300" stroke="{t["border"]}"/>')
    kpis = [("PUBLIC REPOS", str(d["repos"]), ""), ("LAST PUSH", d["push_date"], d["push_repo"]),
            ("RECCHAOS DEVLOG", f"Day {d['day']}", d["day_date"]), ("EXPERIMENTS", str(d["exps"]), "published"),
            ("DECISIONS", str(d["adrs"]), "ADRs"), ("FOLLOWERS", str(d["followers"]), "")]
    for i, (lab, val, sub) in enumerate(kpis):
        x, y = 776 + (i % 2) * 206, 104 + (i // 2) * 74
        b.append(text(x, y, lab, 12, t["muted"], 700, MONO, ls=1.5))
        b.append(text(x, y + 36, val, 30, t["text"], 800))
        if sub:
            b.append(text(f"{x + width(val, 30, bold=True) + 10:.0f}", y + 35, sub, 14, t["muted"]))
    b.append(f'<line x1="40" y1="322" x2="{W-40}" y2="322" stroke="{t["border"]}"/>')
    b.append(text(40, 354, "LATEST FINDING", 13, t["sky"], 700, MONO, ls=2))
    b.append(text(196, 354, f"{d['exp_name']}: {d['exp_result']}", 17, t["text"], 500))
    return svg(W, H, "".join(b), f"Ops: {d['total']} contributions in the last year; {d['repos']} public repos; "
               f"RecChaos devlog day {d['day']}; {d['exps']} experiments; latest finding: {d['exp_result']}.")


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


# ============================================================== data
def get(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "profile-ops", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode()


def fetch_ops():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    q = f"""{{ user(login: "{LOGIN}") {{
      followers {{ totalCount }}
      repositories(privacy: PUBLIC, ownerAffiliations: OWNER, first: 3, orderBy: {{field: PUSHED_AT, direction: DESC}}) {{
        totalCount nodes {{ name pushedAt }} }}
      contributionsCollection {{ contributionCalendar {{ totalContributions weeks {{ contributionDays {{ contributionCount }} }} }} }} }} }}"""
    d = json.loads(get("https://api.github.com/graphql", json.dumps({"query": q}).encode(), {"Authorization": f"Bearer {token}"}))
    if d.get("errors"):
        sys.exit(f"GraphQL error: {d['errors']}")
    u = d["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    repo = next(n for n in u["repositories"]["nodes"] if n["name"] != LOGIN)  # skip this profile repo (bot commits)
    pushed = dt.datetime.fromisoformat(repo["pushedAt"].replace("Z", "+00:00"))
    now = dt.datetime.now(dt.timezone.utc)
    devlog = get(RECCHAOS_RAW + "devlog/index.md")
    days = [(int(n), date) for n, date in re.findall(r"\[Day (\d+) \(([^)]+)\)\]", devlog)]
    day, day_date = max(days) if days else (0, "")
    exps = [l for l in get(RECCHAOS_RAW + "experiments/index.md").splitlines() if re.match(r"\|\s*\d{4}-\d{2}-\d{2}", l)]
    last = [c.strip() for c in exps[-1].strip("|").split("|")] if exps else ["", "", "no experiments yet"]
    adrs = re.findall(r"^\|\s*\[\d{3}\]", get(RECCHAOS_RAW + "decisions/index.md"), re.M)
    return dict(total=cal["totalContributions"],
                weeks=[sum(x["contributionCount"] for x in w["contributionDays"]) for w in cal["weeks"]],
                repos=u["repositories"]["totalCount"], followers=u["followers"]["totalCount"],
                push_repo=repo["name"], push_date=pushed.strftime("%-d %b"), shipping=(now - pushed).days <= 7,
                day=day, day_date=" ".join(day_date.split()[:2]), exps=len(exps), adrs=len(adrs),
                exp_name=re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", last[1]).split(" · ")[0], exp_result=last[2],
                date=now.strftime("%-d %b").upper())


def picture(name, alt, link=None):
    p = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/{name}-dark.svg">'
         f'<img src="./assets/{name}-light.svg" width="100%" alt="{attr(alt)}"></picture>')
    return f'<a href="{link}">{p}</a>' if link else p


def readme():
    L = ['<a href="https://leninjacobregi.me"><img src="./assets/banner.svg" width="100%" alt="Lenin Jacob Regi, '
         'Recommender Systems Engineer. Build, break, detect: a window fails silently, the river monitor line spikes, '
         'and the anomaly is detected."></a>', "",
         picture("feed-header", "Recommended for you: my work, ranked, with the reason for each pick.")]
    for i, it in enumerate(FEED, 1):
        L.append(picture(f"feed-{i}", f"#{i} {it['title']}: {it['desc']} Because {it['because']}.", it["link"]))
    L += ["", "<br>", "", picture("model-card", "Model card: lenin-recsys v2027. " + " ".join(
        f"{h.title()}: {', '.join(v)}." for h, v in MODEL_CARD.items()))]
    for i, (area, sub, lvl, proof, link) in enumerate(PROFICIENCY, 1):
        L.append(picture(f"skill-{i}", f"{area} ({sub}): {LEVELS[lvl].lower()}. Proof: {proof}.", link))
    L += ["", "<br>", "", picture("toolchain", "Toolchain: " + ", ".join(l for _, l in TOOLS)),
          picture("ops", "Ops panel, refreshed daily: contributions, public repos, last push, RecChaos devlog day, "
                  "experiments, decisions and the latest finding.", "https://leninjacobregi.me/RecChaos/devlog/"),
          "", '<p align="center">',
          '  <a href="https://www.linkedin.com/in/lenin-jacob-regi"><img src="./assets/connect-linkedin.svg" width="46" alt="LinkedIn"></a>&nbsp;&nbsp;',
          '  <a href="https://leninjacobregi.me"><img src="./assets/connect-website.svg" width="46" alt="Website"></a>&nbsp;&nbsp;',
          '  <a href="https://leninjacobregi.me/RecChaos/"><img src="./assets/connect-docs.svg" width="46" alt="RecChaos docs and devlog"></a>',
          "  <br>", "  <sub>On call for recommender systems and ML internships. Let's talk.</sub>", "</p>", ""]
    return "\n".join(L)


def main():
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    d = fetch_ops()
    for k, t in THEMES.items():
        (out / f"ops-{k}.svg").write_text(ops(t, d))
    if "--ops-only" in sys.argv:
        print("ops refreshed:", {k: v for k, v in d.items() if k != "weeks"})
        return
    (out / "banner.svg").write_text(banner())
    for k, t in THEMES.items():
        (out / f"feed-header-{k}.svg").write_text(feed_header(t))
        for i, item in enumerate(FEED, 1):
            (out / f"feed-{i}-{k}.svg").write_text(feed_row(t, i, item))
        (out / f"model-card-{k}.svg").write_text(model_card(t))
        for i, (area, sub, lvl, proof, _link) in enumerate(PROFICIENCY, 1):
            (out / f"skill-{i}-{k}.svg").write_text(prof_row(t, area, sub, lvl, proof))
        (out / f"toolchain-{k}.svg").write_text(toolchain(t))
    for kind in ["linkedin", "website", "docs"]:
        (out / f"connect-{kind}.svg").write_text(connect(kind))
    (out.parent / "README.md").write_text(readme())
    print("ops:", {k: v for k, v in d.items() if k != "weeks"})


if __name__ == "__main__":
    main()
