"""
dedup.py
========

Deduplicates job listings that appear more than once (e.g. the same role
re-posted, or picked up from multiple sources) using pandas.

Two listings are considered duplicates if they share the same normalized
(company, role) pair. When duplicates are found, the highest fit-scoring
copy is kept (they should score identically if descriptions match, but this
also handles minor description differences gracefully).
"""

from __future__ import annotations

import pandas as pd

from scraper import JobListing


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def listings_to_dataframe(listings: list[JobListing]) -> pd.DataFrame:
    """Convert JobListing objects into a pandas DataFrame."""
    rows = [listing.as_dict() for listing in listings]
    return pd.DataFrame(rows)


def deduplicate(listings: list[JobListing]) -> list[JobListing]:
    """
    Remove duplicate listings using pandas, keyed on normalized
    (company, role). Keeps the highest-fit-score copy of each duplicate
    group.
    """
    if not listings:
        return []

    df = listings_to_dataframe(listings)
    df["_dedup_key_company"] = df["company"].map(_normalize)
    df["_dedup_key_role"] = df["role"].map(_normalize)

    # Sort so the highest fit_score comes first within each dedup group,
    # then drop_duplicates keeps the first occurrence per group.
    df = df.sort_values("fit_score", ascending=False)
    df = df.drop_duplicates(subset=["_dedup_key_company", "_dedup_key_role"], keep="first")
    df = df.drop(columns=["_dedup_key_company", "_dedup_key_role"])

    # Rebuild JobListing objects from the deduped rows, preserving order.
    deduped: list[JobListing] = []
    for _, row in df.iterrows():
        matched_skills = row["matched_skills"].split(", ") if row["matched_skills"] else []
        deduped.append(
            JobListing(
                company=row["company"],
                role=row["role"],
                location=row["location"],
                date=row["date"],
                description=row["description"],
                source=row["source"],
                fit_score=row["fit_score"],
                matched_skills=matched_skills,
            )
        )

    return deduped
