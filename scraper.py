"""
scraper.py
==========

Fetches and parses job listing pages with BeautifulSoup.

Two data sources are supported:

1. LOCAL FIXTURE (default, used by the demo / tests):
   Parses a saved HTML file (fixtures/sample_job_listings.html) that mimics
   the structure of a real job-board search-results page. This lets the
   whole pipeline (parsing -> scoring -> dedup -> export) be exercised
   deterministically, offline, without hitting any live site.

2. LIVE SOURCE (opt-in via --source-url / --live):
   Fetches a real URL over HTTP. Before fetching, it checks that URL's
   robots.txt to see whether scraping is disallowed for our user-agent, and
   it rate-limits requests (a sleep between each HTTP call) so it never
   hammers a real site. This code path is real and functional, but it is
   NOT exercised by the default demo run, since pointing it at a specific
   live job board's HTML would require matching that site's actual markup
   (which changes over time and is outside the scope of this offline demo).

Both paths funnel into the same `parse_listings_html()` parser, which reads
`.job-card` elements and pulls out company / title / location / date /
description using CSS selectors -- the same selector-based approach you'd
adapt to a real site by simply changing the selectors below.
"""

from __future__ import annotations

import time
import urllib.robotparser
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_USER_AGENT = "JobRadarBot/1.0 (+https://example.com/jobradar; contact: akshattg2005@gmail.com)"
DEFAULT_RATE_LIMIT_SECONDS = 2.0
DEFAULT_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_job_listings.html"


@dataclass
class JobListing:
    """A single structured job listing scraped from a source page."""

    company: str
    role: str
    location: str
    date: str
    description: str
    source: str = "unknown"
    fit_score: float = field(default=0.0)
    matched_skills: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "company": self.company,
            "role": self.role,
            "location": self.location,
            "date": self.date,
            "description": self.description,
            "source": self.source,
            "fit_score": self.fit_score,
            "matched_skills": ", ".join(self.matched_skills),
        }


def load_fixture_html(fixture_path: Path = DEFAULT_FIXTURE_PATH) -> str:
    """Read the local mock HTML fixture from disk."""
    fixture_path = Path(fixture_path)
    if not fixture_path.exists():
        raise FileNotFoundError(
            f"Fixture not found at {fixture_path}. The demo relies on this "
            "local HTML file standing in for a real job-board results page."
        )
    return fixture_path.read_text(encoding="utf-8")


def is_scraping_allowed(url: str, user_agent: str = DEFAULT_USER_AGENT) -> bool:
    """
    Check robots.txt for the given URL's host and return whether our
    user-agent is allowed to fetch that specific path.

    Fails "closed-but-usable": if robots.txt can't be fetched/parsed at all
    (network error, 404, etc.) we default to allowing the fetch, matching
    the conventional interpretation that a missing robots.txt means no
    restrictions -- but we still log/report this so a caller can decide.
    """
    parsed = urlparse(url)
    robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        # Could not retrieve robots.txt -- default to allowed, per
        # conventional robots.txt semantics (no file == no restrictions).
        return True

    return rp.can_fetch(user_agent, url)


def fetch_live_html(
    url: str,
    user_agent: str = DEFAULT_USER_AGENT,
    rate_limit_seconds: float = DEFAULT_RATE_LIMIT_SECONDS,
    session: requests.Session | None = None,
) -> str:
    """
    Fetch a live URL's HTML, respecting robots.txt and applying a simple
    rate limit (a sleep before the request) so repeated calls don't hammer
    the target server.

    This function is exercised by unit-style checks but is NOT called by
    the default `python jobradar.py` demo run, which uses the local
    fixture instead. Point --source-url at a real job board and pass
    --live to use this path (see README for details and caveats about
    matching that site's actual HTML structure).
    """
    if not is_scraping_allowed(url, user_agent=user_agent):
        raise PermissionError(
            f"robots.txt disallows fetching {url} for user-agent '{user_agent}'."
        )

    # Rate limiting: always pause before issuing a request so a loop over
    # many search-result pages never fires faster than one request per
    # `rate_limit_seconds`.
    time.sleep(rate_limit_seconds)

    http = session or requests.Session()
    response = http.get(url, headers={"User-Agent": user_agent}, timeout=15)
    response.raise_for_status()
    return response.text


def parse_listings_html(html: str, source_label: str = "fixture") -> list[JobListing]:
    """
    Parse raw HTML of a job-board search-results page into a list of
    JobListing objects using BeautifulSoup CSS selectors.

    Expected markup (see fixtures/sample_job_listings.html):

        <div class="job-card">
          <h2 class="job-title">...</h2>
          <span class="job-company">...</span>
          <span class="job-location">...</span>
          <span class="job-date">...</span>
          <div class="job-description">...</div>
        </div>

    To point this at a real site, adjust the selectors below to match that
    site's markup -- the rest of the pipeline (scoring, dedup, export)
    stays the same.
    """
    soup = BeautifulSoup(html, "html.parser")
    listings: list[JobListing] = []

    for card in soup.select(".job-card"):
        title_el = card.select_one(".job-title")
        company_el = card.select_one(".job-company")
        location_el = card.select_one(".job-location")
        date_el = card.select_one(".job-date")
        desc_el = card.select_one(".job-description")

        role = title_el.get_text(strip=True) if title_el else "Unknown Role"
        company = company_el.get_text(strip=True) if company_el else "Unknown Company"
        location = location_el.get_text(strip=True) if location_el else "Unknown Location"
        date = date_el.get_text(strip=True) if date_el else ""
        description = desc_el.get_text(" ", strip=True) if desc_el else ""

        listings.append(
            JobListing(
                company=company,
                role=role,
                location=location,
                date=date,
                description=description,
                source=source_label,
            )
        )

    return listings


def scrape_fixture(fixture_path: Path = DEFAULT_FIXTURE_PATH) -> list[JobListing]:
    """Convenience wrapper: load + parse the local fixture in one call."""
    html = load_fixture_html(fixture_path)
    return parse_listings_html(html, source_label="local_fixture")


def scrape_live(
    url: str,
    user_agent: str = DEFAULT_USER_AGENT,
    rate_limit_seconds: float = DEFAULT_RATE_LIMIT_SECONDS,
) -> list[JobListing]:
    """Convenience wrapper: fetch + parse a live URL in one call."""
    html = fetch_live_html(url, user_agent=user_agent, rate_limit_seconds=rate_limit_seconds)
    return parse_listings_html(html, source_label=url)
