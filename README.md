# job-search-bot

A conversational CLI that fetches job postings from any company's Workday
careers site and saves them to a CSV.

```
> Find me PwC jobs related to AI
Bot: Looking up PricewaterhouseCoopers… found 11 AI roles. Saved to
     output/pricewaterhousecoopers_ai_2026-05-25.csv
```

Works without an API key (slot-filling mode), or as a real chatbot when
`ANTHROPIC_API_KEY` is set.

## Quick start

```bash
git clone https://github.com/mahadevaiahrashmi/job-search-bot.git
cd job-search-bot
uv sync
uv run job-search-bot
```

You'll get two prompts:

```
Company (or 'quit'): pwc
Keyword/field (e.g. AI): AI
Location filter (optional, press Enter to skip):
```

CSV lands in `output/`.

## Chatbot mode

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run job-search-bot
```

Now you can type things like:

- `Find me PwC jobs related to AI in Bangalore`
- `Any data scientist roles at Salesforce?`
- `Show me NVIDIA AI jobs`

## Supported companies

Out of the box: **PwC**, **JPMorgan Chase**, **Salesforce**, **Cisco**,
**Adobe**, **NVIDIA**, **Netflix**, **Workday**.

Add more by editing
[`src/job_search_bot/companies.py`](src/job_search_bot/companies.py) — every
Workday tenant follows the same URL pattern.

## How it works

1. You give the bot a company name and a search field (or just chat).
2. It looks up the company's Workday API endpoint
   (`{tenant}.wdN.myworkdayjobs.com/wday/cxs/.../jobs`).
3. It pages through the JSON results and applies your location filter.
4. It writes a deduplicated CSV with columns:
   `company, job_id, title, location, posted_on, url`.

No browser automation, no scraping fragile HTML, no API key needed — the
Workday careers JSON API is public.

## Project layout

```
src/job_search_bot/
  bot.py          CLI entry + chat loop + slot-fill fallback
  companies.py    Known Workday tenant registry
  workday.py      JSON API client + pagination
  csv_writer.py   Writes timestamped CSVs to ./output/
  models.py       JobQuery, JobPosting dataclasses
```

## Documentation

- [docs/non-technical.md](docs/non-technical.md) — what it does, in plain English, with simple flow diagrams.
- [docs/technical.md](docs/technical.md) — system design, sequence diagrams, Workday API contract, extension points.

## License

MIT
