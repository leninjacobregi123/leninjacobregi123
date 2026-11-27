### Hi, I'm Lenin 👋

**Recommender Systems Engineer.** I build retrieval and ranking systems and keep them healthy in production. My niche is **RecSysOps** and **cold start**.

Final-year B.Tech CSE (AI/ML) at Karunya Institute of Technology and Sciences (2027) · **Smart India Hackathon 2025 Grand Finalist** · I lead the Generative AI community at Karunya Innovation & Design Studio (KIDS).

---

## 🔧 Building now: [RecChaos](https://github.com/leninjacobregi123/RecChaos)

<a href="https://github.com/leninjacobregi123/RecChaos"><img src="https://raw.githubusercontent.com/leninjacobregi123/RecChaos/main/docs/assets/architecture.png" alt="RecChaos architecture" width="720"></a>

**A fault-injection benchmark for recommender systems.** Recommenders rarely crash; they fail silently. RecChaos rebuilds six landmark recommender papers into one working stack, then breaks it on purpose in 10 recommender-specific ways and scores which monitors notice.

- **Week 1 result:** Amazon's 2003 item-to-item CF beats all-time bestsellers about 6×, but loses to a 30-day popularity list: 33% of December interactions went to games released in the previous 60 days. [Read the experiment →](https://leninjacobregi.me/RecChaos/experiments/exp-001-week1-baselines/)
- Built in public: daily devlog, every decision as an ADR. **[Docs →](https://leninjacobregi.me/RecChaos/)**

## Open source

- **[airllm](https://github.com/lyogavin/airllm):** 3× inference throughput on a 4 GB GPU
- **[lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)** (EleutherAI)

## 🏮 Also built: Kinlight, my first game

<a href="https://kinlight.kinlight.workers.dev"><img src="kinlight.jpg" alt="Kinlight: the Great Gate opens when enough players' lights stand on its ring at the same moment" width="560"></a>

**[▶ Play Kinlight](https://kinlight.kinlight.workers.dev)**: free, in any browser, on a phone or a computer.

A daily co-op game: at midnight UTC a new world of floating ruins appears, the same for everyone on Earth. Every glowing figure you meet is a recording of someone who played earlier that day, and when you rest on a stone, your light keeps that gate open for everyone after you.

- 3D in the browser with Babylon.js (WebGL), written in TypeScript
- Runs on Cloudflare Workers, with each day's lights kept in a Durable Object's SQLite database
- Installs like an app, and plays offline after the first visit

---

[Website](https://leninjacobregi.me) · [LinkedIn](https://www.linkedin.com/in/lenin-jacob-regi) · Writing a series: *RecSysOps in Practice*
