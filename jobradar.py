#!/usr/bin/env python3
"""
jobradar.py
===========

JobRadar -- a CLI tool that scrapes job listings, filters them by role and
location, deduplicates across sources, scores each listing against a
configurable skills profile (the "fit score"), and exports a ranked CSV.

Usage:
    python jobradar.py --role "Python Developer" --location "Bangalore"

By default this parses the local HTML fixture at
fixtures/sample_job_listings.html (see scraper.py / README.md for why, and
for how to point it at a live source instead with --live --source-url).
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from dedup import deduplicate
from scoring import DEFAULT_SKILLS_PROFILE_PATH, load_skill_profile, score_listings
from scraper import (
    DEFAULT_FIXTURE_PATH,
    DEFAULT_RATE_LIMIT_SECONDS,
    DEFAULT_USER_AGENT,
    JobListing,
    scrape_fixture,
    scrape_live,
)

STOPWORDS = {"a", "an", "the", "for", "in", "at", "of", "and", "to", "with"}


def _significant_words(text: str) -> list[str]:
    """Lowercase, alnum-only words of length >= 3, minus stopwords."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if len(w) >= 3 and w not in STOPWORDS]


def filter_listings(
    listings: list[JobListing], role_query: str, location_query: str
) -> list[JobListing]:
    """
    Keep listings relevant to the requested role and location.

    - Location match: the location query must appear as a substring of the
      listing's location field (case-insensitive) -- e.g. "Bangalore"
      matches "Bangalore, India".
    - Role match: at least one significant word from the role query (e.g.
      "python", "developer") must appear in the listing's job title. This
      mirrors how a real job-search box works (broad title matching) --
      irrelevant results that slip through still get ranked low by the fit
      score, which is the whole point of JobRadar.
    """
    role_words = set(_significant_words(role_query))
    location_query_norm = location_query.strip().lower()

    filtered = []
    for listing in listings:
        title_words = set(_significant_words(listing.role))
        role_ok = bool(role_words & title_words) if role_words else True
        location_ok = (
            location_query_norm in listing.location.lower() if location_query_norm else True
        )
        if role_ok and location_ok:
            filtered.append(listing)

    return filtered


def print_ranked_table(listings: list[JobListing], top_n: int) -> None:
    """Print a ranked table matching JobRadar's sample CLI output style."""
    if not listings:
        print("No listings matched your search criteria.")
        return

    header = f"{'Rank':<5} {'Score':<6} {'Company':<17} {'Role'}"
    print(header)

    for idx, listing in enumerate(listings[:top_n], start=1):
        score_str = f"{listing.fit_score:.0f}%"
        print(f"{idx:<5} {score_str:<6} {listing.company:<17} {listing.role}")

    remaining = len(listings) - top_n
    if remaining > 0:
        print("...")


def export_to_csv(listings: list[JobListing], output_dir: Path) -> Path:
    """Export the full (deduped, scored, sorted) results to a dated CSV via pandas."""
    rows = []
    for rank, listing in enumerate(listings, start=1):
        row = listing.as_dict()
        row["rank"] = rank
        row["fit_score_pct"] = f"{listing.fit_score:.0f}%"
        rows.append(row)

    df = pd.DataFrame(rows)
    column_order = [
        "rank",
        "fit_score_pct",
        "fit_score",
        "company",
        "role",
        "location",
        "date",
        "matched_skills",
        "description",
        "source",
    ]
    df = df[[c for c in column_order if c in df.columns]]

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"jobs_{date.today().isoformat()}.csv"
    output_path = output_dir / filename
    df.to_csv(output_path, index=False)
    return output_path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jobradar.py",
        description="Scrape, filter, score, and rank job listings by fit to your skills.",
    )
    parser.add_argument("--role", required=True, help='Role to search for, e.g. "Python Developer"')
    parser.add_argument("--location", required=True, help='Location to search in, e.g. "Bangalore"')
    parser.add_argument(
        "--skills-config",
        default=str(DEFAULT_SKILLS_PROFILE_PATH),
        help="Path to the skills profile JSON config used to compute fit scores.",
    )
    parser.add_argument(
        "--fixture-path",
        default=str(DEFAULT_FIXTURE_PATH),
        help="Path to the local HTML fixture to parse (used unless --live is passed).",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help=(
            "Fetch --source-url over the network instead of using the local fixture. "
            "Checks robots.txt and rate-limits requests. Off by default."
        ),
    )
    parser.add_argument(
        "--source-url",
        default=None,
        help="Live job-board search-results URL to scrape when --live is passed.",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=DEFAULT_RATE_LIMIT_SECONDS,
        help="Seconds to sleep before each live HTTP request (default: %(default)s).",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="User-Agent string sent with live requests and checked against robots.txt.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top-ranked listings to print to the console (default: %(default)s). The full result set is always exported to CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write the exported CSV into (default: current directory).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    print(f'Searching for "{args.role}" in "{args.location}"...\n')

    if args.live:
        if not args.source_url:
            parser.error("--live requires --source-url to be set.")
        try:
            listings = scrape_live(
                args.source_url,
                user_agent=args.user_agent,
                rate_limit_seconds=args.rate_limit,
            )
        except PermissionError as exc:
            print(f"Blocked by robots.txt: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:  # network errors, HTTP errors, etc.
            print(f"Failed to fetch live source: {exc}", file=sys.stderr)
            return 1
    else:
        listings = scrape_fixture(Path(args.fixture_path))

    filtered = filter_listings(listings, args.role, args.location)

    skill_profile = load_skill_profile(Path(args.skills_config))
    scored = score_listings(filtered, skill_profile)

    deduped = deduplicate(scored)
    deduped.sort(key=lambda l: l.fit_score, reverse=True)

    print_ranked_table(deduped, args.top_n)

    if deduped:
        output_path = export_to_csv(deduped, Path(args.output_dir))
        print(f"\n\U0001F4C1 Full results exported to {output_path.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Built incrementally - see git history for the development progression.
