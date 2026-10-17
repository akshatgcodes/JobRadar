# JobRadar — Product Requirements Document

**Status:** Final (v1 shipped)
**Owner:** Akshat Gupta
**One-liner:** A job-listing scraper that filters, de-duplicates and ranks every listing by a weighted fit score against your skills, then exports a CSV.

---

## 1. Problem

Job searching means scrolling the same boards every day, re-reading duplicate posts, and judging fit by eye. Results are sorted by date or "relevance" to the board, not to you, so a strong match on page three is easy to miss. A daily run that hands back a short, ranked list of what actually fits your skills saves that time.

---

## 2. Goals (v1)

1. Take a role and a location on the command line.
2. Parse job cards (title, company, location, date, description) from a results page.
3. Keep listings whose title matches the role and whose location matches the query.
4. Score every listing 0–100% against a weighted skills profile in a JSON file.
5. Remove duplicates, keeping the best-scoring copy.
6. Print a ranked table and export everything to a dated CSV.
7. Run offline by default, with an opt-in live mode that respects `robots.txt`.

---

## 3. Non-Goals (explicit scope cuts)

- **Built-in support for specific job boards** — live mode needs the CSS selectors adjusted per site.
- **Logging in, pagination or JavaScript-rendered pages** — one static HTML page per run.
- **Applying to jobs or tracking applications** — JobRadar ranks, it doesn't apply.
- **ML or LLM scoring** — the score is a transparent weighted keyword match.

---

## 4. Users

**Primary:** A job seeker who wants a daily, personalised shortlist instead of scrolling boards.

**Secondary:** Engineers reviewing a scraping pipeline built with care for `robots.txt` and rate limits.

---

## 5. User Stories

1. *As a job seeker,* I run `--role "Python Developer" --location "Bangalore"` so that I see a ranked table of matches.
2. *As a job seeker,* I raise the weight of `django` in my profile so that Django-heavy roles rank higher.
3. *As a job seeker,* I open the CSV so that I can see every match with its score and matched skills.
4. *As a job seeker,* I see one entry per company and role, even when the board lists it twice.
5. *As a careful user,* I run with `--live` and trust it won't fetch a page that `robots.txt` disallows.

---

## 6. Functional Requirements

### 6.1 Input

- Required: `--role`, `--location`.
- Optional: `--skills-config`, `--fixture-path`, `--live`, `--source-url` (required with `--live`), `--rate-limit` (default 2 s), `--user-agent`, `--top-n` (default 10), `--output-dir`.

### 6.2 Parsing

- Cards are found with `.job-card`. Fields come from `.job-title`, `.job-company`, `.job-location`, `.job-date` and `.job-description`.

### 6.3 Filtering

- Location: the query must be a case-insensitive substring of the listing's location.
- Role: at least one significant word from the query (3+ characters, not a stopword) must be in the title.

### 6.4 Scoring

- Each skill keyword is matched case-insensitively with word boundaries. Spaces in a keyword also match hyphens or extra spaces.
- `fit_score = sum(weights found) / sum(all weights) × 100`. Weight defaults to 1.0.

### 6.5 De-duplication and export

- Duplicates by normalised (company, role) are dropped, keeping the highest score.
- Results are sorted by score, the top N printed, and all of them written to `jobs_YYYY-MM-DD.csv`.

---

## 7. Non-Functional Requirements

- **Politeness:** live mode checks `robots.txt` before fetching, sleeps `--rate-limit` seconds first, sends an identifying User-Agent and has a 15 s timeout.
- **Determinism:** the same input and profile always give the same ranking.
- **Offline-first:** the default run needs no network, so CI and demos are reliable.

---

## 8. Success Metrics

| Metric | Target |
|---|---|
| Relevance | The best-fitting fixture listing (Razorpay backend role) ranks first for the default profile |
| Correctness | No duplicate (company, role) pairs in the output |
| Safety | Live mode refuses URLs that `robots.txt` disallows |

---

## 9. Risks & Open Questions

- **Selectors break** — any change to a real site's HTML breaks live parsing for that site.
- **Keyword gaming** — descriptions stuffed with buzzwords score high regardless of the real role.
- **Terms of service** — some boards forbid scraping even where `robots.txt` allows it. That's the user's responsibility.

---

## 10. v2 Candidates

- Selector presets for a few public job boards.
- Multi-page results and pagination.
- A "must-have" flag in the profile that zeroes the score when a skill is missing.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
