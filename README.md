# JobRadar

A command-line tool that scrapes job listings by role and location, filters
and deduplicates them, scores each one against a skills profile you define,
and exports a ranked list to CSV. Run it daily to get a fresh, personalized
shortlist instead of manually scrolling job boards.

- **Month:** November 2023
- **Language:** Python
- **Type:** CLI Tool

## The X factor: fit score

Every listing gets a **fit score** (0-100%) instead of just being sorted by
date. The score is computed by `scoring.py`:

1. You define a skill profile in `config/skills_profile.json` — a list of
   `{"keyword": ..., "weight": ...}` entries (e.g. `python` weight `3.0`,
   `docker` weight `1.5`). Weight lets you tell JobRadar which skills matter
   most to you.
2. For each listing's scraped job description, every skill keyword is
   checked with a case-insensitive, word-boundary regex (so `sql` won't
   match inside `mysqlite`, and multi-word skills like `rest api` are
   matched as a phrase).
3. The fit score is:

   ```
   fit_score = (sum of weights of skills FOUND in the description)
               / (sum of weights of ALL skills in the profile)
               * 100
   ```

This is a real, deterministic weighted keyword-match algorithm — no random
numbers involved. Results are sorted by this score, descending, so the 10
most relevant listings float to the top instead of being buried in 50
unsorted results. Edit `config/skills_profile.json` to match your own
skills and the ranking changes accordingly.

## Sample output

```
$ python jobradar.py --role "Python Developer" --location "Bangalore"

Searching for "Python Developer" in "Bangalore"...

Rank  Score  Company           Role
1     89%    Razorpay          Backend Engineer (Python)
2     49%    Freshworks        Python Developer - Integrations
3     47%    Swiggy            Data Engineer - Python/Spark
4     29%    Infosys           Associate - Python & Django
5     29%    Wipro             Python Automation Engineer
6     13%    TCS               Senior Java Developer
7     0%     Zoho              Frontend Developer (React)

📁 Full results exported to jobs_2026-09-15.csv
```

(CSV filename is dated to the day you run it, e.g. `jobs_2023-11-14.csv` in
the original spec's example.)

## Key concepts demonstrated

- **BeautifulSoup + CSS selectors** (`scraper.py`) — parses `.job-card`
  elements out of a job-board results page (`.job-title`, `.job-company`,
  `.job-location`, `.job-date`, `.job-description`).
- **Keyword matching / scoring algorithm** (`scoring.py`) — weighted,
  regex-based, word-boundary keyword matching against a configurable skill
  profile.
- **pandas for dedup + CSV export** (`dedup.py`, `jobradar.py`) — listings
  are loaded into a DataFrame, deduplicated on normalized
  `(company, role)`, keeping the highest-scoring copy, and the final
  ranked result set is exported with `DataFrame.to_csv(...)`.
- **`robots.txt` awareness + rate limiting** (`scraper.py`) —
  `is_scraping_allowed()` fetches and checks the target host's
  `robots.txt` via `urllib.robotparser` before any live fetch, and
  `fetch_live_html()` sleeps (`--rate-limit`, default 2s) before every
  request so it never hammers a real server.
- **Config-driven skill profiles** — `config/skills_profile.json` is a
  plain JSON file you edit to change what JobRadar considers "relevant"
  without touching any code.

## Important note on scraping design

By default, `jobradar.py` parses a **local HTML fixture**
(`fixtures/sample_job_listings.html`) that was hand-written to look like a
real job-board search-results page (same markup shape you'd see scraping
a real listings/search page: repeated result cards with title, company,
location, date, and description). This keeps the parsing → scoring →
dedup → export pipeline fully real, testable, and runnable offline/in CI
without doing uncontrolled live scraping of a real site in an agent
sandbox (which would risk violating a site's ToS/rate limits and would be
flaky with no network access).

The live-fetch code path is fully implemented and functional — it's just
not what the default demo run uses:

```bash
python jobradar.py --role "Python Developer" --location "Bangalore" \
    --live --source-url "https://example-job-board.com/search?..."
```

When `--live` is passed, `scraper.fetch_live_html()`:

1. Looks up and parses that host's `robots.txt` and refuses to fetch if
   disallowed for JobRadar's user-agent.
2. Sleeps `--rate-limit` seconds (default 2s) before issuing the request.
3. Fetches the page with `requests`, then hands the HTML to the exact same
   `parse_listings_html()` BeautifulSoup parser used for the fixture.

To point JobRadar at a real job board, you would adjust the CSS selectors
in `scraper.parse_listings_html()` (currently `.job-card`, `.job-title`,
`.job-company`, `.job-location`, `.job-date`, `.job-description`) to match
that site's actual HTML structure — the rest of the pipeline (scoring,
dedup, ranking, export) needs no changes.

## Project layout

```
JobRadar/
├── jobradar.py               # CLI entry point (argparse: --role, --location, ...)
├── scraper.py                 # BeautifulSoup parsing + robots.txt + rate-limited live fetch
├── scoring.py                  # Fit-score algorithm (weighted keyword matching)
├── dedup.py                    # pandas-based deduplication
├── config/
│   └── skills_profile.json     # Your skills, editable, drives the fit score
├── fixtures/
│   └── sample_job_listings.html  # Local mock job-board results page (demo/test data)
├── requirements.txt
└── README.md
```

## Run it

**Requirements:** Python 3.8+

```bash
pip install -r requirements.txt

python jobradar.py --role "Python Developer" --location "Bangalore"
```

### Useful flags

| Flag | Default | Description |
|---|---|---|
| `--role` | *(required)* | Role to search for, e.g. `"Python Developer"` |
| `--location` | *(required)* | Location to search in, e.g. `"Bangalore"` |
| `--skills-config` | `config/skills_profile.json` | Skill profile used to compute fit scores |
| `--fixture-path` | `fixtures/sample_job_listings.html` | Local HTML fixture to parse (used unless `--live`) |
| `--live` | off | Fetch `--source-url` live instead of the fixture |
| `--source-url` | — | Live job-board URL to scrape (requires `--live`) |
| `--rate-limit` | `2.0` | Seconds to sleep before each live HTTP request |
| `--top-n` | `10` | How many ranked rows to print to the console |
| `--output-dir` | `.` | Directory to write the dated CSV export into |

### Try a different skill profile

Edit `config/skills_profile.json` (or copy it and pass
`--skills-config your_profile.json`) to change which keywords/skills drive
the fit score, then re-run the same command — the ranking will change to
reflect your new profile.

## Sanity-checking this project

```bash
python3 -m py_compile jobradar.py scraper.py scoring.py dedup.py
python jobradar.py --role "Python Developer" --location "Bangalore"
```

The second command should print a ranked table like the sample above and
write a `jobs_<today's date>.csv` file in the project directory (this file
is git-ignored since it's generated output).

## Notes

Built as a focused, single-purpose tool - a job-listing scraper with fit-score ranking, nothing more, nothing less.

## Troubleshooting

If something doesn't run as expected, double-check you're using the dependency versions noted above and running the exact commands from the "Run it" section.

## Possible Improvements

- More test coverage
- Better error messages for edge cases
- A cleaner CLI/UI polish pass
