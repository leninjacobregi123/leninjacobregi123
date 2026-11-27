#!/usr/bin/env python3
"""Build Lenin's GitHub profile README: plain text, no images.

    python3 -I scripts/build_readme.py            # rebuild the whole README from the content below
    python3 -I scripts/build_readme.py --refresh  # only rewrite the "Latest from RecChaos" list (the daily Action)

Edit the content block below. Every claim must link to public proof.
The "Latest from RecChaos" list is read from the RecChaos docs, so it updates itself when a devlog day,
an experiment or a decision record is published there. No token is needed: the docs are public.
"""
from __future__ import annotations

import datetime as dt
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
GH = "https://github.com/leninjacobregi123"
DOCS = "https://leninjacobregi.me/RecChaos/"
RAW = "https://raw.githubusercontent.com/leninjacobregi123/RecChaos/main/docs/"
START, END = "<!-- recent starts -->", "<!-- recent ends -->"
RECENT_N = 5

# ============================================================== content (edit here)
NAME = "Lenin Jacob Regi"
INTRO = ("Recommender systems engineer. I build retrieval and ranking systems and keep them healthy in production. "
         "Final-year B.Tech CSE (AI/ML) at Karunya, graduating 2027, where I lead the Generative AI community "
         "at Karunya Innovation & Design Studio.")
NOW = (f"Building [RecChaos]({GH}/RecChaos) in public: a fault-injection benchmark for recommender systems. "
       "I rebuild six landmark recommender papers into one stack, then break it on purpose to measure which "
       "monitors notice. Week 1: Amazon's 2003 item-to-item CF scored about 6× all-time popularity on NDCG@10, "
       f"then lost to a 30-day popularity list ([EXP-001]({DOCS}experiments/exp-001-week1-baselines/)).")
WORK = [  # (name, link, what it is, built with)
    ("RecChaos", f"{GH}/RecChaos",
     "Fault-injection benchmark and RecSysOps stack for recommender systems", "Python · SciPy · pandas"),
    ("Scoratis", f"{GH}/socratic-ai",
     "Socratic tutor on agentic RAG: hybrid search with RRF, a LangGraph agent with 11 tools",
     "Python · LangGraph · React · Three.js"),
    ("Ammini", f"{GH}/Ammini",
     "Malayalam LLM from scratch: own BPE tokenizer, RoPE + grouped-query attention, sparse MoE", "Python · PyTorch"),
    ("Kinlight", "https://kinlight.kinlight.workers.dev",
     "Daily co-op 3D browser game: play with the recorded lights of everyone who played before you that day",
     "TypeScript · Babylon.js · Cloudflare Workers"),
]
LINKS = [("leninjacobregi.me", "https://leninjacobregi.me"),
         ("LinkedIn", "https://www.linkedin.com/in/lenin-jacob-regi"),
         ("leninjacob891@gmail.com", "mailto:leninjacob891@gmail.com")]
AVAILABILITY = "Open to ML and recommender systems internships now, and full-time roles from 2027."


# ============================================================== recent list (from the RecChaos docs)
def get(path: str) -> str:
    req = urllib.request.Request(RAW + path, headers={"User-Agent": "profile-readme"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode()


def url(section: str, md: str) -> str:
    """docs/<section>/<md> -> its page on the site (MkDocs serves each page as a directory)."""
    return f"{DOCS}{section}/{md.removesuffix('.md')}/"


def day_label(d: dt.date) -> str:
    return f"{d.day} {d:%b %Y}"


def recent() -> list[str]:
    items = []  # (date, kind rank, number, line); newest first, experiments before decisions before devlog days
    for date, title, md, result in re.findall(
            r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]*?)\s*\|", get("experiments/index.md"), re.M):
        n = int(re.search(r"\d+", title).group())
        items.append((dt.date.fromisoformat(date), 2, n, f"[{title}]({url('experiments', md)}): {result}"))
    for num, md, title, status in re.findall(
            r"^\|\s*\[(\d{3})\]\(([^)]+)\)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", get("decisions/index.md"), re.M):
        found = re.search(r"\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", get(f"decisions/{md}"))
        if found:
            items.append((dt.date.fromisoformat(found.group(1)), 1, int(num),
                          f"[ADR-{num} · {title}]({url('decisions', md)}): {status.lower()}"))
    for n, date, md in re.findall(r"\[Day (\d+) \(([^)]+)\)\]\(([^)]+)\)", get("devlog/index.md")):
        items.append((dt.datetime.strptime(date, "%d %b %Y").date(), 0, int(n),
                      f"[Devlog · Day {n}]({url('devlog', md)})"))
    if not items:
        sys.exit("No devlog, experiment or decision entries found; refusing to write an empty list.")
    items.sort(key=lambda x: x[:3], reverse=True)
    return [f"- {day_label(d)} · {line}" for d, _, _, line in items[:RECENT_N]]


# ============================================================== README
def block(lines: list[str]) -> str:
    return "\n".join([START, *lines, END])


def build(lines: list[str]) -> str:
    work = ["| Project | What it is | Built with |", "| :--- | :--- | :--- |"]
    work += [f"| [{name}]({link}) | {what} | {stack} |" for name, link, what, stack in WORK]
    links = " · ".join(f"[{text}]({href})" for text, href in LINKS)
    return "\n".join([
        f"# {NAME}", "", INTRO, "",
        "### Now", "", NOW, "",
        "### Selected work", "", *work, "",
        "### Latest from RecChaos", "", block(lines), "",
        f"{AVAILABILITY}  ", links, "",
    ])


def main() -> None:
    lines = recent()
    if "--refresh" in sys.argv:
        text = README.read_text()
        pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
        if not pattern.search(text):
            sys.exit(f"{README.name} has no {START} … {END} block; run without --refresh first.")
        new = pattern.sub(lambda _: block(lines), text)
    else:
        new = build(lines)
    if new != (README.read_text() if README.exists() else ""):
        README.write_text(new)
        print("README.md updated")
    else:
        print("README.md unchanged")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
