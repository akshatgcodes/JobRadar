# JobRadar — Architecture

---

## 1. Stack

| Layer | Tech |
|---|---|
| Language | Python 3.8+ |
| CLI | `argparse` |
| Parsing | BeautifulSoup 4 (CSS selectors) |
| Data | pandas (`DataFrame.drop_duplicates`, `to_csv`) |
| HTTP | `requests` (live mode) · `urllib.robotparser` |
| Project page | Next.js 16 static site in `landing/`, on Vercel |

---

## 2. Components

```
jobradar.py                 CLI entry: args, filtering, ranked table, CSV export
scraper.py                  JobListing model, fixture loading, robots.txt check, live fetch, HTML parsing
scoring.py                  skill profile loading, keyword regex, fit score
dedup.py                    pandas-based de-duplication
config/skills_profile.json  weighted skills that drive the score
fixtures/sample_job_listings.html  mock results page for offline runs and CI
landing/                    Next.js project page
```

### Scraper (`scraper.py`)

- `scrape_fixture()` reads `fixtures/sample_job_listings.html`.
- `is_scraping_allowed(url)` fetches `robots.txt` for the host and checks it for the User-Agent.
- `fetch_live_html(url)` checks `robots.txt`, sleeps `--rate-limit`, and `GET`s with a 15 s timeout.
- `parse_listings_html(html)` turns `.job-card` elements into `JobListing` objects. Both paths use it.

### Scoring (`scoring.py`)

- `_keyword_pattern(kw)` builds `\b<kw>\b` (case-insensitive), with spaces inside `kw` matching `[\s\-]+`.
- `compute_fit_score(description, profile)` returns `(score, matched_keywords)`.

### De-dup (`dedup.py`)

Loads listings into a DataFrame, normalises company and role, sorts by score descending, and `drop_duplicates(keep="first")` on the normalised pair.

---

## 3. Data Flow

```
args --> scrape (fixture | --live: robots.txt → sleep → GET)
     --> parse_listings_html  (.job-card → JobListing[])
     --> filter_listings      (role word overlap AND location substring)
     --> score_listings       (weighted keyword regex → fit_score, matched skills)
     --> deduplicate          (pandas, best score per company+role)
     --> sort by fit_score desc
     --> print top N table
     --> export jobs_YYYY-MM-DD.csv to --output-dir
```

---

## 4. Scoring Maths

```
fit_score = Σ weight(skill) for skills found in description
            ─────────────────────────────────────────────── × 100
            Σ weight(skill) for all skills in the profile
```

With the default profile (total weight 22.5), a description that mentions Python (3.0), Django (2.0), REST API (2.0) and Docker (1.5) scores 8.5 / 22.5 × 100 ≈ 38%.

---

## 5. Security & Politeness

- **robots.txt:** checked before every live fetch. If it disallows the URL for the User-Agent, the fetch is refused. If `robots.txt` itself can't be fetched, the URL is treated as allowed.
- **Rate limit:** a fixed sleep before each request, 2 s by default.
- **Identification:** the default User-Agent names the bot and gives a contact address.
- **Timeouts:** 15 s on live requests.
- **Parsing:** BeautifulSoup only reads text, and nothing scraped is executed.
- **Secrets:** none.

---

## 6. Error Handling

| Failure | Behaviour |
|---|---|
| `--live` without `--source-url` | argparse error and exit |
| Fixture missing | Clear error naming the expected path |
| `robots.txt` disallows the URL | `Blocked by robots.txt: …` on stderr, and the run stops |
| Network error or non-200 response | `Failed to fetch live source: …` on stderr, and the run stops |
| No listings after filtering | "No listings matched your search criteria." and no CSV is written |

---

## 7. Deployment

The CLI isn't hosted. It's installed and run locally. The project page in `landing/` is a Vercel project with root directory `landing`, deployed on every push to `master` (see [DEPLOY.md](DEPLOY.md)).

---

## 8. Explicit Scope Cuts

- **Per-site selector presets** — selectors are edited in `parse_listings_html()`.
- **Pagination / JavaScript-rendered boards** — one static page per run.
- **Persistence** — each run is independent. History lives in the dated CSVs.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
