---
name: job-search
description: Search a company's Workday careers site for job postings matching keywords and write the results to a CSV. Trigger when the user asks to find, list, or fetch jobs at a known company (PwC, JPMorgan, Salesforce, Cisco, Adobe, NVIDIA, Netflix, Workday) — e.g., "find me PwC AI jobs", "show data scientist roles at Salesforce", "list NVIDIA jobs in Bangalore". Do NOT trigger for résumé review, interview prep, or jobs at companies not on Workday.
---

# job-search

A skill for fetching real-time job postings from any Workday-based
company's public careers API and saving them to a timestamped CSV.

## When to use this

The user is asking to **find or list job openings** at one of the
companies registered in the bot. Example trigger phrases:

- "Find me PwC jobs related to AI"
- "Show me NVIDIA AI jobs in Bangalore"
- "List Salesforce data scientist roles"
- "Get all Cisco jobs"

If the company isn't in the registry below, tell the user and offer to
add it (one-line code change).

## Built-in companies

`pwc`, `jpmorgan` (aliases: `jpmc`, `jp morgan`, `chase`), `salesforce`
(alias: `sfdc`), `cisco`, `adobe`, `nvidia`, `netflix`, `workday`.

## How to run

The skill assumes the user has the repo cloned at
`~/Documents/job/job-search-bot/` (or you can `cd` to wherever they
have it). Use the slot-fill CLI — it works without any API key:

```bash
cd ~/Documents/job/job-search-bot
printf '<company>\n<keywords>\n<location_or_blank>\nquit\n' | uv run job-search-bot
```

For example, to find PwC AI jobs in Bangalore:

```bash
printf 'pwc\nAI\nBangalore\nquit\n' | uv run job-search-bot
```

The output ends with a line like:

```
Saved: output/pricewaterhousecoopers_ai_2026-05-25.csv
```

Surface that path to the user. They can open it directly:

```bash
open output/pricewaterhousecoopers_ai_2026-05-25.csv
```

## What the CSV contains

Six columns: `company, job_id, title, location, posted_on, url`.
One row per posting, deduplicated by `job_id`.

## What this skill does NOT do

- It does not apply to jobs.
- It does not score postings against a résumé.
- It does not notify the user when new jobs appear.
- It does not work for companies outside Workday (Greenhouse, Lever,
  iCIMS, custom careers sites).

For any of those, fall back to a normal response — don't pretend the
skill can do them.

## Adding a new company

If the user wants a company not in the registry, look at
`src/job_search_bot/companies.py`. Adding a new entry is a single
dataclass row — the URL pattern is
`https://{tenant}.wd{N}.myworkdayjobs.com` and the `site` is the path
segment after `myworkdayjobs.com/` on the company's careers page.

Confirm with the user before making the edit.
