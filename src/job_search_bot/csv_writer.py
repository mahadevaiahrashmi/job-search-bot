"""Write JobPosting lists to timestamped CSV files."""

from __future__ import annotations

import csv
import datetime as _dt
import re
from pathlib import Path

from .models import JobPosting

_CSV_COLUMNS = ["company", "job_id", "title", "location", "posted_on", "url"]


def _slug(text: str) -> str:
    """Lowercase, replace non-alphanumerics with underscores, collapse runs."""
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "unknown"


def write_csv(
    postings: list[JobPosting],
    company_slug: str,
    keyword_slug: str,
    output_dir: Path = Path("output"),
) -> Path:
    """Write postings to output_dir/{company}_{keyword}_{YYYY-MM-DD}.csv."""
    output_dir.mkdir(parents=True, exist_ok=True)
    date = _dt.date.today().isoformat()
    filename = f"{_slug(company_slug)}_{_slug(keyword_slug)}_{date}.csv"
    path = output_dir / filename

    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_COLUMNS)
        writer.writeheader()
        for p in postings:
            writer.writerow(
                {
                    "company": p.company,
                    "job_id": p.job_id,
                    "title": p.title,
                    "location": p.location,
                    "posted_on": p.posted_on,
                    "url": p.url,
                }
            )

    return path
