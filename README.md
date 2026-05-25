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

The docs are split by audience. Pick the one that matches what you need.

### 📖 For non-technical readers

**→ [docs/non-technical.md](docs/non-technical.md)**

Plain-English overview of what the bot does and why it exists. No code,
no jargon, simple flow diagrams. Read this if you want to understand
the tool before deciding whether to use it.

Covers:
- What problem it solves (and what it doesn't)
- A walk-through of a single search
- What's happening "under the hood" without any code
- Who this is for

---

### 🛠 For technical readers

**→ [docs/technical.md](docs/technical.md)**

System design and reference documentation for developers extending or
integrating the bot.

Covers:
- Component layout and module responsibilities
- Mermaid sequence diagrams for both REPL modes
- Workday API contract (endpoint, request/response shapes)
- Job-ID extraction regex and dedup logic
- Pagination, error handling, edge cases
- Extension points: adding Greenhouse/Lever, swapping in a local LLM

---

### 📘 User manual

**→ [docs/user-manual.md](docs/user-manual.md)**

Step-by-step guide for actually running the bot. Start here if you
just want to use it.

Covers:
- Install (one-time)
- Your first search
- Reading the output CSV
- Enabling chatbot mode with an API key
- Adding a new company to the registry
- Common questions, troubleshooting table, and limits

---

## License

MIT
