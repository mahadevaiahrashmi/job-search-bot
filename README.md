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

### 🏛 System design

**→ [docs/system-design.md](docs/system-design.md)**

Architecture and decision record. Read this if you're evaluating the
design, extending it, or writing a similar tool.

Covers:
- Goals and explicit non-goals
- Context diagram (where the bot sits among Workday + Anthropic + filesystem)
- Layered architecture with single-responsibility components
- Data model (Company, JobQuery, JobPosting)
- External interface contracts (Workday + Anthropic)
- Sequence diagrams for both REPL modes
- Failure modes, security & privacy, performance characteristics
- Design decisions explained (Why Workday-first? Why optional LLM? Why CLI?)
- Roadmap-style extension points with effort estimates

---

### 🧩 Skills

**→ [docs/skills.md](docs/skills.md)**

Documents two interpretations of "skill" in this project: the
invokable Claude Code skill and the internal module-as-skill framing.

Covers:
- The `.claude/skills/job-search/` skill — trigger phrases, how Claude
  invokes the bot under the hood, what it does and doesn't do
- Five internal skills (`company-resolve`, `workday-search`, `csv-write`,
  `chat-loop`, `slot-fill`) with input/output contracts and failure modes
- Composition diagram showing how the skills chain together
- A template for adding new skills

---

### 🔁 Workflows

**→ [docs/workflows.md](docs/workflows.md)**

Recipe-style guide for nine end-to-end user workflows. Copy-paste,
swap the values, run.

Covers:
- Quick one-off search · Compare role across multiple companies
- Daily job-hunt loop with cron · Conversational search with API key
- Diff against yesterday's results · Importing into Google Sheets
- Adding a new company · Using the Claude Code skill · Résumé scoring (future)
- Anti-workflows (what NOT to do)

---

## Repository extras

- **CI:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml) — runs
  on every push/PR against Python 3.11 and 3.12. Validates imports,
  the company registry, and the CSV writer.
- **Claude Code skill:** [`.claude/skills/job-search/SKILL.md`](.claude/skills/job-search/SKILL.md)
  — invoke the bot conversationally from any Claude Code session.

---

## License

MIT
