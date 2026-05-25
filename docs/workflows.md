# Workflows

Practical, end-to-end workflows the bot supports. Each is a recipe —
copy-paste, swap the values, run.

> If you haven't installed the bot yet, see
> [user-manual.md §1](user-manual.md).

---

## Workflow A — Quick one-off search

**Goal:** "Show me all AI jobs at PwC, right now."

**Steps:**

1. Open Terminal in the project folder:
   ```bash
   cd ~/Documents/job/job-search-bot
   ```
2. Run the bot:
   ```bash
   uv run job-search-bot
   ```
3. Type when prompted:
   ```
   Company: pwc
   Keyword: AI
   Location: (Enter)
   ```
4. Open the CSV the bot printed:
   ```bash
   open output/pricewaterhousecoopers_ai_2026-05-25.csv
   ```

**Time:** ~10 seconds.

---

## Workflow B — Compare the same role across multiple companies

**Goal:** "Which company has more 'data scientist' openings right now —
PwC, Salesforce, or Cisco?"

**Steps:**

1. Run the bot three times, once per company:
   ```bash
   printf 'pwc\ndata scientist\n\nquit\n' | uv run job-search-bot
   printf 'salesforce\ndata scientist\n\nquit\n' | uv run job-search-bot
   printf 'cisco\ndata scientist\n\nquit\n' | uv run job-search-bot
   ```
2. Concatenate the CSVs into one file:
   ```bash
   head -1 output/pricewaterhousecoopers_data_scientist_*.csv > combined.csv
   tail -n +2 -q output/*_data_scientist_*.csv >> combined.csv
   ```
3. Open `combined.csv` in Numbers / Excel and pivot by `company`.

**Time:** ~1 minute end-to-end.

---

## Workflow C — Daily job-hunt loop

**Goal:** "Each morning, get a fresh list of new postings at my top 3
target companies."

**Steps:**

1. Create a small shell script `~/bin/daily-jobs.sh`:
   ```bash
   #!/usr/bin/env bash
   set -e
   cd ~/Documents/job/job-search-bot
   for company in nvidia salesforce adobe; do
     printf "%s\nAI\n\nquit\n" "$company" | uv run job-search-bot
   done
   echo "Done. CSVs in ~/Documents/job/job-search-bot/output/"
   ```
2. Make it executable:
   ```bash
   chmod +x ~/bin/daily-jobs.sh
   ```
3. Schedule with `cron` to run at 9 AM weekdays:
   ```bash
   crontab -e
   # then add:
   0 9 * * 1-5  /Users/rashmi/bin/daily-jobs.sh > /tmp/daily-jobs.log 2>&1
   ```
4. Each morning, three fresh CSVs land in `output/`.

> **Note:** Same-day re-runs *overwrite* the CSV. The cron job above
> only gives you one file per company per day, which is what you want.
> For new-since-yesterday tracking, see Workflow E below.

---

## Workflow D — Conversational search (with API key)

**Goal:** "Ask in plain English without remembering field names."

**Steps:**

1. Set your Anthropic key once:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   # add to ~/.zshrc to persist
   ```
2. Run the bot:
   ```bash
   uv run job-search-bot
   ```
3. Chat naturally:
   ```
   You: find me senior PwC AI jobs in Bangalore
   Bot: Found 22 senior AI jobs at PwC in Bangalore. Saved to
        output/pricewaterhousecoopers_ai_2026-05-25.csv.

   You: now show me data engineer roles at Cisco
   Bot: ...
   ```

**Cost:** Less than $0.01 per session (Claude Haiku is cheap).

---

## Workflow E — Diff against yesterday's results

**Goal:** "Show me only the postings that are NEW since yesterday."

**Steps:**

1. Today's run (after the cron job has produced a CSV):
   ```bash
   today=$(date +%Y-%m-%d)
   yesterday=$(date -v-1d +%Y-%m-%d)        # macOS
   # On Linux: yesterday=$(date -d "yesterday" +%Y-%m-%d)

   diff \
     <(cut -d, -f2 output/pricewaterhousecoopers_ai_$yesterday.csv | sort) \
     <(cut -d, -f2 output/pricewaterhousecoopers_ai_$today.csv     | sort) \
     | grep '^>' | sed 's/^> //'
   ```

   This prints the job IDs that exist in today's CSV but not
   yesterday's. Pipe into grep to pull the full rows back:

   ```bash
   grep -Ff <(diff_command_above) output/pricewaterhousecoopers_ai_$today.csv
   ```

2. For a cleaner experience, ask for the SQLite persistence layer (see
   [system-design.md §14](system-design.md), 4 hours of work).

---

## Workflow F — Importing into Google Sheets

**Goal:** "I want to share my job tracker with a friend."

**Steps:**

1. Open Google Sheets → File → Import → Upload → drag the CSV.
2. Select "Replace current sheet" or "Insert new sheet."
3. Make a column called `Status` (Applied / Interviewing / Rejected).
4. Sort by `posted_on` desc to see freshest jobs first.

---

## Workflow G — Add a new company

**Goal:** "I want to search Acme Corp's Workday jobs but it's not in
the registry."

**Steps:**

1. Find their careers URL — e.g.,
   `https://acme.wd5.myworkdayjobs.com/en-US/External`.
2. Open
   [`src/job_search_bot/companies.py`](../src/job_search_bot/companies.py).
3. Add a new entry to `_REGISTRY`:
   ```python
   "acme": Company(
       canonical_name="Acme Corporation",
       base_url="https://acme.wd5.myworkdayjobs.com",
       tenant="acme",
       site="External",
   ),
   ```
4. Save. Run the bot — `acme` is now a valid company.

**Time:** 2 minutes. No `uv sync` rerun needed.

---

## Workflow H — Use the Claude Code skill

**Goal:** "Run a job search from any Claude Code session, without `cd`'ing."

If you have this repo open in Claude Code, the skill in
`.claude/skills/job-search/SKILL.md` is automatically available. Just
ask Claude:

```
> Find me PwC AI jobs
```

Claude will invoke the skill, run the CLI behind the scenes, and surface
the CSV path. See `.claude/skills/job-search/SKILL.md` for the full
trigger description.

---

## Workflow I — Resume scoring (future)

**Goal:** "Of the 100 PwC AI jobs, which 5 fit my résumé best?"

**Status:** not built. Would require the API key path and an extra LLM
tool. Estimated ~1 day of work — see
[system-design.md §14](system-design.md).

---

## Anti-workflows — what to NOT do

- **Don't run the bot in a tight loop with no delay.** Even though the
  Workday API hasn't rate-limited us in testing, repeatedly hammering
  the same tenant is rude and could change that.
- **Don't commit CSVs to git.** The `.gitignore` already excludes
  `output/*.csv`. If you want to track searches over time, see the
  SQLite extension point.
- **Don't manually edit CSV filenames.** The bot uses the filename to
  decide whether a previous run exists. Renaming breaks diff workflows.
