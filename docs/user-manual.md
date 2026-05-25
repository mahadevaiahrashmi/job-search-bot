# User manual

A practical, copy-pasteable guide to using `job-search-bot`. Read this
start-to-finish your first time; skim it after.

---

## 1. Install (one time)

### Requirements

- macOS or Linux (Windows works via WSL)
- Python 3.11 or newer
- [`uv`](https://github.com/astral-sh/uv) — fast Python package manager
- Internet connection

Check what you have:

```bash
python3 --version    # should print 3.11.x or higher
uv --version         # should print a version string
```

If `uv` is missing:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Get the code

```bash
git clone https://github.com/mahadevaiahrashmi/job-search-bot.git
cd job-search-bot
uv sync
```

`uv sync` reads `pyproject.toml`, creates a `.venv/`, and installs the
three runtime dependencies (`anthropic`, `httpx`, `rich`). Takes ~10
seconds.

---

## 2. Your first search (slot-fill mode)

```bash
uv run job-search-bot
```

You'll see:

```
──────────── Job Search Bot ────────────
Running in slot-filling mode (no ANTHROPIC_API_KEY detected).
Known companies: Adobe, Cisco, JPMorgan Chase, NVIDIA, Netflix,
PricewaterhouseCoopers, Salesforce, Workday

Company (or 'quit'):
```

Type a company name (case doesn't matter; aliases like `pwc`, `jpmc`,
`jp morgan` all work):

```
Company (or 'quit'): pwc
```

Then a keyword. You can leave it blank to get *all* jobs at the
company:

```
Keyword/field (e.g. AI): AI
```

Then an optional location filter. Press Enter to skip:

```
Location filter (optional, press Enter to skip): Bangalore
```

The bot calls the company's Workday API, paginates results, and prints
a summary table:

```
                  100 job(s) found
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Job ID   ┃ Title                      ┃ Location       ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ 728909WD │ IN_Senior Associate _AI…   │ Bengaluru      │
│ 716931WD │ IN-Senior Manager_Palantir │ Bengaluru      │
│ …        │ (+90 more)                 │                │
└──────────┴────────────────────────────┴────────────────┘
Saved: output/pricewaterhousecoopers_ai_2026-05-25.csv
```

Type `quit` (or press Ctrl-D / Ctrl-C) when you're done.

---

## 3. The output CSV

Every search creates one file in `./output/`. Filename pattern:

```
{company_slug}_{keyword_slug}_{YYYY-MM-DD}.csv
```

So a second search the same day overwrites the first. Move or rename
the file before re-running if you want to keep both.

### Columns

| Column | Example |
|---|---|
| `company` | `PricewaterhouseCoopers` |
| `job_id` | `728909WD` |
| `title` | `IN_Senior Associate _Agentic + Gen AI…` |
| `location` | `Bengaluru Millenia` |
| `posted_on` | `Posted Today` |
| `url` | `https://pwc.wd3.myworkdayjobs.com/job/…` |

### Open it

```bash
open output/pricewaterhousecoopers_ai_2026-05-25.csv   # Numbers / Excel
```

Or import into Google Sheets via File → Import → Upload.

---

## 4. Chatbot mode (optional, costs money)

If you have an Anthropic API key, set it once and the bot becomes
conversational:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run job-search-bot
```

Now type plain English:

```
You: Find me PwC jobs about AI in Bangalore
Bot: I found 11 AI roles at PwC in Bangalore. Saved to
     output/pricewaterhousecoopers_ai_2026-05-25.csv.

You: What about Salesforce data scientist roles?
Bot: …
```

### Cost note

Each search ≈ 1 Claude Haiku call, well under $0.01. You'll spend cents
per session, not dollars. To make the key persist across terminal
windows, add the export line to `~/.zshrc` or `~/.bashrc`.

### Choosing a different model

```bash
export ANTHROPIC_MODEL=claude-sonnet-4-5-20250929  # for example
```

The default is Haiku 4.5 (cheapest, fast enough for this).

---

## 5. Adding a new company

The bot ships with eight built-in companies. To add a ninth:

### Step A — find the company's Workday URL

Go to their careers page and watch the URL. You're looking for
something like:

```
https://acme.wd5.myworkdayjobs.com/en-US/External
                ───┬─               ──┬───
                tenant              site
```

If the URL doesn't contain `myworkdayjobs.com`, the company isn't on
Workday and this bot can't fetch them (yet — see *Limits* below).

### Step B — add a line to the registry

Edit [`src/job_search_bot/companies.py`](../src/job_search_bot/companies.py)
and append to `_REGISTRY`:

```python
"acme": Company(
    canonical_name="Acme Corporation",
    base_url="https://acme.wd5.myworkdayjobs.com",
    tenant="acme",
    site="External",
),
```

Save the file. No restart of `uv sync` needed — the next
`uv run job-search-bot` picks it up.

### Step C — verify

```
Company (or 'quit'): acme
Keyword/field (e.g. AI):
Location filter (optional, press Enter to skip):

100 job(s) found
Saved: output/acme_corporation_all_2026-05-25.csv
```

If you get `0 job(s) found` and the company definitely has openings,
the `site` value is probably wrong. Open the careers page, copy the
path segment after `myworkdayjobs.com/` (before any locale), and use
that.

---

## 6. Common questions

### "Will this break their careers site?"

No. The bot uses the same JSON API the careers website itself uses to
populate its job listings. You're being one polite visitor.

### "Do I need to log in?"

No. The Workday careers JSON API is unauthenticated.

### "Can I run this on a schedule?"

Yes — wrap `uv run job-search-bot` in a cron job. The slot-fill mode
accepts stdin, so:

```bash
* 9 * * * cd /path/to/job-search-bot && printf 'pwc\nAI\n\nquit\n' | uv run job-search-bot
```

But you'll re-create the same CSV each day. For real "new jobs since
yesterday" tracking, the bot needs a small SQLite layer — see
*Extension points* in [`docs/technical.md`](technical.md).

### "I want results from multiple companies in one CSV"

Run the bot once per company, then concatenate:

```bash
head -1 output/pricewaterhousecoopers_ai_*.csv > all.csv
tail -n +2 -q output/*_ai_*.csv >> all.csv
```

---

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| `command not found: uv` | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh`, then open a new terminal. |
| `Connection refused` / timeouts | Check your internet. The bot hits `myworkdayjobs.com`. |
| `I don't know 'foo'` | Company isn't in the registry. Add it (Section 5) or try an alias (`pwc` instead of `pricewaterhousecoopers`). |
| `0 job(s) found` for a known company | The keyword matched nothing. Try broader terms or leave blank. |
| Garbled emoji / table | Your terminal isn't UTF-8. Switch to iTerm2 or set `LANG=en_US.UTF-8`. |
| `anthropic.AuthenticationError` | API key is wrong, revoked, or has no balance. Re-create at console.anthropic.com. |

---

## 8. Limits — what this bot does NOT do

- Companies not on Workday (e.g. anything using Greenhouse, Lever,
  iCIMS). Extending support is one new file — see
  [`docs/technical.md`](technical.md).
- Applying to jobs. Output is read-only.
- Saving search history. Each run is independent; same-day re-runs
  overwrite the CSV.
- Notifying you when new jobs appear. Possible via cron + diff, not
  built in.
- Reading your résumé and ranking by fit. Possible with the API key
  enabled, not built in.

---

## 9. Uninstalling

```bash
rm -rf /path/to/job-search-bot
```

No background processes, no system files touched.

---

## 10. Getting help

- File an issue: https://github.com/mahadevaiahrashmi/job-search-bot/issues
- See the technical reference: [`docs/technical.md`](technical.md)
- See the plain-English overview: [`docs/non-technical.md`](non-technical.md)
