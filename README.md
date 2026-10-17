<p align="center">
  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24"
       fill="none" stroke="#34d399" stroke-width="1.5"
       stroke-linecap="round" stroke-linejoin="round">
    <path d="M19.07 4.93A10 10 0 0 0 6.99 3.34"/><path d="M4 6h.01"/>
    <path d="M2.29 9.62A10 10 0 1 0 21.31 8.35"/><path d="M16.24 7.76A6 6 0 1 0 8.23 16.67"/>
    <path d="M12 18h.01"/><path d="M17.99 11.66A6 6 0 0 1 15.77 16.67"/>
    <circle cx="12" cy="12" r="2"/><path d="m13.41 10.59 5.66-5.66"/>
  </svg>
</p>

<h1 align="center">JobRadar</h1>

<p align="center">
  <strong>A job-listing scraper that filters, de-duplicates and ranks every listing by a weighted fit score against your skills, then exports a CSV.</strong>
</p>

<p align="center">
  <a href="https://jobradar.akshatgcodes.in">
    <img src="https://img.shields.io/badge/project_page-34d399-34d399?style=flat-square" alt="Project page">
  </a>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/BeautifulSoup-111111?style=flat-square" alt="BeautifulSoup">
  <img src="https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white" alt="pandas">
  <img src="https://img.shields.io/badge/license-GPL--3.0-34d399?style=flat-square" alt="License">
</p>

---

## What is JobRadar?

Job boards sort by date, so the listing that actually fits you is buried under fifty that don't. JobRadar parses a results page, keeps listings that match your role and location, removes duplicates, and scores each one from 0–100% against a weighted skills profile you define. The best fits come first, and everything lands in a dated CSV.

> **Project page →** [jobradar.akshatgcodes.in](https://jobradar.akshatgcodes.in)
> It's a CLI: `pip install -r requirements.txt && python jobradar.py --role "Python Developer" --location "Bangalore"`

```
Rank  Score  Company           Role
1     89%    Razorpay          Backend Engineer (Python)
2     49%    Freshworks        Python Developer - Integrations
3     47%    Swiggy            Data Engineer - Python/Spark
📁 Full results exported to jobs_2026-10-18.csv
```

---

## What you get

- **Fit score** — `sum(weights of skills found) / sum(all weights) × 100`, with word-boundary matching so `sql` doesn't match inside `mysqlite`.
- **Your profile, your ranking** — edit `config/skills_profile.json` to change what counts and how much.
- **De-duplication** — pandas drops repeats by normalised company + role and keeps the highest-scoring copy.
- **Polite live mode** — `--live` checks `robots.txt` and waits between requests (2 s by default).
- **CSV export** — every ranked listing, with matched skills, in `jobs_YYYY-MM-DD.csv`.

---

## Stack

| Layer | Tech |
|---|---|
| Language | Python 3.8+ |
| Parsing | BeautifulSoup 4 with CSS selectors |
| Data | pandas (de-dup, CSV export) |
| HTTP | `requests` · `urllib.robotparser` |
| Project page | Next.js 16 on Vercel · GoDaddy DNS |

---

## Engineering Decisions

**Why a weighted keyword score instead of ML or an LLM?**
It's deterministic and explainable. Every percentage is traceable to the skills that matched, and changing a weight changes the ranking in a way you can predict.

**Why parse a local fixture by default?**
The parse → score → de-dup → export pipeline runs offline and in CI with no network and no risk of breaking a site's terms. `--live` uses the exact same parser on a real page.

**Why filter broadly, then rank?**
A listing passes if its title shares any significant word with your role query. Weak matches still show up, ranked low, which is how a real search box behaves.

**What would you do differently in v2?**
Ship selector presets for a few real job boards, since today `--live` needs the CSS selectors adjusted per site.

---

## Docs

| Document | Description |
|---|---|
| [PRD](docs/PRD.md) | Product requirements — goals, user stories, non-goals |
| [Architecture](docs/ARCHITECTURE.md) | Pipeline, scoring maths, modules |
| [Decisions](docs/DECISIONS.md) | Every major technical decision and why |
| [Setup](docs/SETUP.md) | Install, every flag, live mode |
| [Deploy](docs/DEPLOY.md) | How the project page is deployed |
| [Contributing](CONTRIBUTING.md) | How to propose changes |
| [Changelog](CHANGELOG.md) | What changed in each release |
| [Security](SECURITY.md) | How to report a vulnerability |

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
