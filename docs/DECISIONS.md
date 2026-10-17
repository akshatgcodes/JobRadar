# Engineering Decisions — JobRadar

---

## Decision 1 — A weighted keyword score, not ML or an LLM

**Context:** Listings need to be ranked by how well they fit one person's skills.

**Decision:** A JSON skills profile with weights, matched with word-boundary regexes, giving `found weight / total weight × 100`.

**Reason:** It's deterministic and explainable. Every score is traceable to specific matched skills, which are also exported, and editing a weight changes the ranking predictably. No API key or model is needed.

**Tradeoff:** It only sees keywords. A description stuffed with buzzwords scores high, and a synonym ("Postgres" vs `postgresql`) isn't matched unless it's in the profile.

---

## Decision 2 — Word-boundary matching with flexible phrase spacing

**Context:** Naive substring matching gives false hits (`sql` inside `mysqlite`), and multi-word skills appear as "REST API", "rest-api" or "REST  API".

**Decision:** `\b<keyword>\b`, case-insensitive, with spaces inside a keyword matching `[\s\-]+`.

**Reason:** Matches stay precise at the edges and tolerant in the middle.

**Tradeoff:** Keywords with symbols at the edges (like `c++`) need care, because `\b` treats `+` as a non-word character.

---

## Decision 3 — An offline fixture by default, live mode opt-in

**Context:** Live scraping is flaky (network, layout changes) and can breach a site's rules if done carelessly.

**Decision:** The default run parses `fixtures/sample_job_listings.html`. `--live --source-url` uses the same parser on a real page, after a `robots.txt` check and a rate-limit sleep.

**Reason:** The whole pipeline (parse, filter, score, de-dup, export) runs the same way in CI and demos with no network. Live mode is a different input, not a different code path.

**Tradeoff:** Pointing it at a real board means adjusting the CSS selectors in `parse_listings_html()` for that site.

---

## Decision 4 — Filter broadly, rank strictly

**Context:** Too strict a filter hides useful near-matches. Too loose a filter floods the list.

**Decision:** Keep a listing if its title shares any significant word (3+ characters, not a stopword) with the role query and its location contains the location query. Let the fit score do the ordering.

**Reason:** It mirrors a real search box. Weak matches still appear but sink to the bottom. In the fixture, a Java role with some Python overlap scores 13% and lands near the end.

**Tradeoff:** Generic role words ("engineer", "developer") let through listings that are clearly off-topic. They just rank last.

---

## Decision 5 — pandas for de-dup and export

**Context:** Boards often repeat the same posting. Results need to end up in a spreadsheet.

**Decision:** Load listings into a DataFrame, normalise company and role, sort by score, `drop_duplicates(keep="first")`, then `to_csv`.

**Reason:** Keeping the best-scoring duplicate is one sort plus one call, and CSV export comes for free.

**Tradeoff:** pandas is a heavy dependency for a CLI this size.

---

## What I'd do differently in v2

- **Selector presets** per job board, chosen by `--source`.
- **Must-have skills** that zero the score when missing.
- **Treat an unreachable `robots.txt` as "disallowed"** instead of allowed, to be stricter about politeness.

---

## Explicit non-decisions (deferred to v2)

| Feature | Why deferred |
|---|---|
| Pagination / JavaScript-rendered boards | Needs a headless browser or per-site APIs |
| Run history and diffs ("new since yesterday") | Dated CSVs are enough for v1 |
| Applying to jobs | Out of scope. JobRadar ranks, it doesn't act |

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
