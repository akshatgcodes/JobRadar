# Local Setup — JobRadar

> **Project page:** [jobradar.akshatgcodes.in](https://jobradar.akshatgcodes.in)
> JobRadar is a command-line tool, so it runs on your machine. This guide covers installing and using it.

---

## Prerequisites

- Python 3.8+

---

## 1. Clone and install

```bash
git clone https://github.com/akshatgcodes/JobRadar
cd JobRadar
pip install -r requirements.txt
```

---

## 2. Environment variables

None. Everything is set with flags and `config/skills_profile.json`.

---

## 3. Run

```bash
python jobradar.py --role "Python Developer" --location "Bangalore"
```

This parses the bundled fixture, prints the top 10 and writes `jobs_YYYY-MM-DD.csv`.

### Flags

| Flag | Default | What it does |
|---|---|---|
| `--role` | required | Role to search for |
| `--location` | required | Location substring, e.g. `Bangalore` |
| `--skills-config` | `config/skills_profile.json` | Your weighted skills |
| `--fixture-path` | `fixtures/sample_job_listings.html` | HTML to parse when not in live mode |
| `--live` | off | Fetch `--source-url` over the network instead |
| `--source-url` | — | Results page URL (required with `--live`) |
| `--rate-limit` | `2.0` | Seconds to wait before a live request |
| `--user-agent` | `JobRadarBot/1.0 (...)` | User-Agent for live requests and the `robots.txt` check |
| `--top-n` | `10` | Rows to print |
| `--output-dir` | current directory | Where the CSV goes |

### Your skills profile

Edit `config/skills_profile.json`:

```json
{ "skills": [
    { "keyword": "python", "weight": 3.0 },
    { "keyword": "rest api", "weight": 2.0 },
    { "keyword": "docker" }
] }
```

Weight defaults to 1.0. Higher weight means the skill counts more towards the score.

### Live mode

```bash
python jobradar.py --role "Python Developer" --location "Bangalore" \
    --live --source-url "https://example-job-board.com/search?q=python"
```

JobRadar checks the site's `robots.txt`, waits `--rate-limit` seconds, and fetches the page. For a real board, adjust the selectors in `scraper.parse_listings_html()` (`.job-card`, `.job-title`, `.job-company`, `.job-location`, `.job-date`, `.job-description`) to match its HTML.

---

## 4. Project page (optional)

```bash
cd landing && npm install && npm run dev   # http://localhost:3000
```

See [DEPLOY.md](DEPLOY.md) for how it's hosted.

---

## Testing

There's no automated test suite yet. CI checks that every Python file compiles and that the project page lints and builds. To check a change by hand, run the default command and confirm Razorpay's backend role is ranked first at 89%, with no duplicate company + role rows.

---

## Known limitations

- Live mode only works for sites whose HTML matches the selectors.
- Some job boards forbid scraping in their terms even when `robots.txt` allows it. Check before using `--live`.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
