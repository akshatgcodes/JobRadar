"""
scoring.py
==========

Computes the "fit score" for each job listing -- JobRadar's X factor.

The fit score is a weighted keyword-match percentage: how much of the
configured skill profile's total weight is found (as whole words/phrases)
in a listing's description, expressed as 0-100%.

This is a real, deterministic algorithm (no randomness):

    fit_score = (sum of weights of skills found in the description)
                / (sum of weights of ALL skills in the profile)
                * 100

Matching is case-insensitive and uses word-boundary regex matching so that,
e.g., "sql" does not spuriously match inside "mysqlite" and "aws" doesn't
match inside "jaws". Multi-word skills like "rest api" are matched as a
contiguous phrase.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from scraper import JobListing

DEFAULT_SKILLS_PROFILE_PATH = Path(__file__).parent / "config" / "skills_profile.json"


def load_skill_profile(path: Path = DEFAULT_SKILLS_PROFILE_PATH) -> list[dict]:
    """
    Load the skill profile config (JSON) and return a normalized list of
    {"keyword": str, "weight": float} dicts.

    Every skill must contribute a positive weight; a `weight` key is
    optional per-entry and defaults to 1.0 when omitted.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Skill profile config not found at {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    skills = data.get("skills", [])
    if not skills:
        raise ValueError(f"Skill profile at {path} defines no skills.")

    normalized = []
    for entry in skills:
        keyword = str(entry["keyword"]).strip().lower()
        weight = float(entry.get("weight", 1.0))
        if not keyword or weight <= 0:
            continue
        normalized.append({"keyword": keyword, "weight": weight})

    if not normalized:
        raise ValueError(f"Skill profile at {path} has no usable (keyword, weight) entries.")

    return normalized


def _keyword_pattern(keyword: str) -> re.Pattern:
    """Build a case-insensitive, word-boundary regex for a (possibly
    multi-word) skill keyword."""
    escaped = re.escape(keyword)
    # Allow flexible whitespace between words in multi-word phrases (e.g.
    # "rest api" also matches "REST  API" or "rest-api" loosely) while
    # keeping strict word boundaries on the ends.
    escaped = escaped.replace(r"\ ", r"[\s\-]+")
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


def compute_fit_score(description: str, skill_profile: list[dict]) -> tuple[float, list[str]]:
    """
    Compute the weighted fit score (0-100, rounded to nearest integer) for
    a single job description against the given skill profile.

    Returns (score, matched_skill_keywords).
    """
    if not description:
        return 0.0, []

    total_weight = sum(s["weight"] for s in skill_profile)
    matched_weight = 0.0
    matched_keywords: list[str] = []

    for skill in skill_profile:
        pattern = _keyword_pattern(skill["keyword"])
        if pattern.search(description):
            matched_weight += skill["weight"]
            matched_keywords.append(skill["keyword"])

    if total_weight <= 0:
        return 0.0, matched_keywords

    raw_score = (matched_weight / total_weight) * 100
    score = round(min(raw_score, 100.0), 1)
    return score, matched_keywords


def score_listings(
    listings: list[JobListing], skill_profile: list[dict]
) -> list[JobListing]:
    """Score every listing in place (sets .fit_score and .matched_skills)
    and return the same list, sorted by fit score descending."""
    for listing in listings:
        score, matched = compute_fit_score(listing.description, skill_profile)
        listing.fit_score = score
        listing.matched_skills = matched

    return sorted(listings, key=lambda l: l.fit_score, reverse=True)
