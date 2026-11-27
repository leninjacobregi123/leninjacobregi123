#!/usr/bin/env python3
"""Draw the profile banner: a still Kerala night scene with Lenin's name, title and focus areas.

    python3 -I scripts/banner.py      # writes assets/banner.svg

One version works in both GitHub themes, because it carries its own night sky. No animation.
Palette (RecChaos brand): ink black, white, sky blue.
"""
from __future__ import annotations

import math
import pathlib
import random
from xml.sax.saxutils import escape

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "banner.svg"

# ============================================================== content (edit here)
NAME = "Lenin Jacob Regi"
TITLE = "Recommender Systems Engineer"
FOCUS = ["RETRIEVAL", "RANKING", "RECSYSOPS", "COLD START"]

# ============================================================== style
W, H = 1200, 220
SANS = "'Inter','Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',monospace"
SKY = "#38BDF8"


def text(x, y, s, size, fill, weight=400, family=SANS, ls=0.0, raw=False):
    spacing = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}"{spacing}>{s if raw else escape(s)}</text>')


def width(s, size, family=SANS, ls=0.0):
    """Approximate rendered width, used to size the rule under the name."""
    if family == MONO:
        return len(s) * (size * 0.6 + ls)
    em = sum(0.28 if c == " " else 0.31 if c in "il.,:;'|!·-()1tfjrI" else 0.68 if c.isupper() else 0.55 for c in s)
    return em * size + len(s) * ls


def poly(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def ridge(fn, x0, x1, step, bottom):
    return f"M{x0} {bottom} " + " ".join(f"L{x} {fn(x):.1f}" for x in range(x0, x1 + step, step)) + f" L{x1} {bottom} Z"


def palm(x, base, h, lean, k=1.0, samples=36):
    """A coconut palm: a curved trunk (cubic Bezier with tapering width) and ten drooping fronds."""
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


def banner():
    rnd = random.Random(11)
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
    for _ in range(40):  # stars, kept off the text side
        x, y, r = rnd.uniform(470, 1190), rnd.uniform(8, 72), rnd.uniform(0.5, 1.4)
        g.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#E0F2FE" opacity="{rnd.uniform(.25, .8):.2f}"/>')
    g.append(f'<path d="{ridge(lambda x: 80 + 14*math.sin(x/97) + 9*math.sin(x/41 + 1) + 6*math.sin(x/23 + 2), 0, W, 8, H)}" fill="url(#far)"/>')
    for cx, cy, rx, ry in [(300, 122, 360, 24), (820, 112, 420, 26), (1100, 130, 300, 20)]:
        g.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#mist)"/>')
    g.append(f'<path d="{ridge(lambda x: 128 + 11*math.sin(x/130 + .5) + 6*math.sin(x/53 + 2), 0, W, 8, H)}" fill="url(#mid)"/>')
    g.append('<ellipse cx="640" cy="146" rx="520" ry="13" fill="url(#mist)"/>')
    g.append(f'<path d="{ridge(lambda x: 151 + 2.5*math.sin(x/37) + 1.5*math.sin(x/11), 0, W, 6, 160)}" fill="#0A1828"/>')
    far_palms = [(610, 152, 40, 3), (648, 152, 52, -4), (700, 153, 34, 2), (858, 152, 56, 5), (902, 152, 44, -3),
                 (946, 153, 62, 4), (1086, 152, 50, -5), (1118, 152, 38, 3)]
    g.append('<path fill="#0B1A2B" d="' + " ".join(palm(x, b, h, l, 0.55, samples=20) for x, b, h, l in far_palms) + '"/>')
    hx, hy = 1012, 154  # the house on the river bank, windows lit
    g.append(f'<circle cx="{hx}" cy="{hy-14}" r="58" fill="url(#warm)"/>')
    g += [
        f'<rect x="{hx-34}" y="{hy-5}" width="68" height="5" fill="#070C16"/>',
        f'<rect x="{hx-29}" y="{hy-27}" width="58" height="22" fill="#0B1424"/>',
        f'<rect x="{hx-22}" y="{hy-21}" width="9" height="9" fill="#EAF6FF"/>',
        f'<rect x="{hx-4}" y="{hy-21}" width="8" height="16" fill="#EAF6FF" opacity=".92"/>',
        f'<rect x="{hx+13}" y="{hy-21}" width="9" height="9" fill="#EAF6FF"/>',
        f'<path d="M{hx-22} {hy-16.5} h9 M{hx-17.5} {hy-21} v9 M{hx+13} {hy-16.5} h9 M{hx+17.5} {hy-21} v9" stroke="#0B1424" stroke-width="1"/>',
        f'<path d="M{hx-54} {hy-27} L{hx-48} {hy-25} L{hx-32} {hy-46} L{hx+32} {hy-46} L{hx+48} {hy-25} L{hx+54} {hy-27} L{hx+50} {hy-21} L{hx-50} {hy-21} Z" fill="#04070D"/>',
        f'<path d="M{hx-21} {hy-45} L{hx} {hy-64} L{hx+21} {hy-45} Z" fill="#04070D"/>',
        f'<path d="M{hx-11} {hy-46} L{hx} {hy-57} L{hx+11} {hy-46} Z" fill="#0E1A2C"/>',
    ]
    g.append(f'<rect x="0" y="156" width="{W}" height="40" fill="url(#water)"/>')
    for x, w in [(hx-22, 9), (hx-4, 8), (hx+13, 9)]:
        g.append(f'<rect x="{x}" y="158" width="{w}" height="26" fill="url(#refl)"/>')
    for _ in range(22):  # light on the water
        x, y, w = rnd.uniform(380, 1180), rnd.uniform(161, 190), rnd.uniform(14, 60)
        g.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="1.2" rx=".6" fill="#7DD3FC" opacity="{rnd.uniform(.12, .38):.2f}"/>')
    g.append(f'<path d="{ridge(lambda x: 199 + 5*math.sin(x/61) + 3*math.sin(x/19 + 1), 0, W, 6, H)}" fill="#04070D"/>')
    fore = [(1180, 210, 158, -26, 1.2), (1132, 212, 128, 16, 1.05), (1062, 210, 90, -10, 0.85), (770, 208, 110, -34, 0.95)]
    g.append('<path fill="#04070D" d="' + " ".join(palm(x, b, h, l, k, samples=40) for x, b, h, l, k in fore) + '"/>')
    g.append(f'<rect width="760" height="{H}" fill="url(#shade)"/>')
    # bio
    dot = f'<tspan fill="{SKY}"> · </tspan>'
    focus = dot.join(escape(f) for f in FOCUS)
    # sizes are set for GitHub, which shows the 1200-wide banner at about 830 px (so 16 here reads as about 11)
    rule = max(width(NAME, 48, ls=0.5), width(" · ".join(FOCUS), 16, MONO, 1.6))
    g.append(text(62, 82, NAME, 48, "#F8FAFC", 300, ls=0.5))
    g.append(f'<line x1="64" y1="106" x2="{64 + rule:.0f}" y2="106" stroke="#F8FAFC" stroke-opacity=".28"/>')
    g.append(text(64, 142, TITLE, 22, "#E2E8F0", 600))
    g.append(text(64, 172, focus, 16, "#A5B4C8", 500, MONO, 1.6, raw=True))
    body = defs + f'<g clip-path="url(#clip)">{"".join(g)}</g>' + \
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="#263041"/>'
    label = f"{NAME}, {TITLE}: " + ", ".join(f.lower() for f in FOCUS) + "."
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{escape(label)}">{body}</svg>\n')


if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(banner())
    print(f"wrote {OUT.relative_to(OUT.parent.parent)} ({OUT.stat().st_size // 1024} KB)")
