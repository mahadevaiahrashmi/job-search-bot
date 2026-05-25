# What this bot does — plain English

You're job hunting. You want a list of every "AI" role at PwC, or every
"data scientist" job at Salesforce, without scrolling through 47 pages
on their careers site.

This bot does that in 5 seconds and gives you a spreadsheet.

---

## How a single search feels

```
You:  job-search-bot
Bot:  Company? → PwC
Bot:  Keyword? → AI
Bot:  Location? → (you press enter)

Bot:  ✓ Found 100 jobs.
      Saved to output/pricewaterhousecoopers_ai_2026-05-25.csv
```

That's the whole interaction. The spreadsheet has six columns:

| company | job_id | title | location | posted_on | url |
|---|---|---|---|---|---|
| PricewaterhouseCoopers | 728909WD | IN_Senior Associate Agentic + Gen AI | Bengaluru Millenia | Posted Today | https://… |

Open it in Excel or Google Sheets, sort by date, click any URL to apply.

---

## What's happening under the hood (no code)

```
       ┌──────────────────────────┐
       │ You type: company + AI   │
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │ Bot looks up the company │
       │ in its address book      │
       │ (PwC → pwc.wd3...)       │
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │ Bot asks the company's   │
       │ careers website:         │
       │ "Got any AI roles?"      │
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │ Website returns a list   │
       │ of matching jobs         │
       └────────────┬─────────────┘
                    │
                    ▼
       ┌──────────────────────────┐
       │ Bot writes the list to a │
       │ spreadsheet on your Mac  │
       └──────────────────────────┘
```

Every company in the bot's address book runs on the same kind of careers
website (a system called Workday). The bot knows how to talk to that
system in its native language, so it doesn't have to pretend to be a
human clicking buttons. Much faster, never breaks when the page redesigns.

---

## Two ways to use it

### Simple way (no setup, free forever)

Type the company name and the keyword in two prompts. Press enter. Get
your spreadsheet.

This is what runs by default.

### Chatbot way (more flexible, needs a paid AI key)

If you set an API key from Anthropic, the bot listens to natural English:

> "Find me PwC AI jobs in Bangalore"

It figures out the company, the keyword, and the location filter from
your sentence and does the same lookup. Useful if you want to chain
several searches without re-typing fields.

You don't need this. The simple way produces the exact same spreadsheet.

---

## What it can NOT do (yet)

- Companies that don't use Workday (e.g. anything on Greenhouse, Lever,
  iCIMS). Adding those is one file change but isn't done today.
- Apply to jobs for you. It only lists them.
- Notify you when new jobs appear. (Could be added — let me know.)
- Read your résumé and rank jobs by fit. (Could be added — would need
  the AI key.)

---

## Who is this for

People who:

- Apply to a lot of jobs and want a tracking spreadsheet, not a browser
  history graveyard.
- Want to compare openings across 5 companies side-by-side.
- Are tired of careers sites with broken filters.

---

## Where the spreadsheets live

`/Users/rashmi/Documents/job/job-search-bot/output/`

One file per search, named so they sort by date and don't overwrite
each other.

---

## "But what is a Workday?"

It's the software most big companies use to run their HR — payroll,
benefits, and the public careers page. About 3,000 companies use it,
including PwC, JPMorgan, Salesforce, Cisco, Adobe, NVIDIA, Netflix,
and Workday itself.

If a company's careers URL has `myworkdayjobs.com` in it, this bot can
search it. Add it to the address book and you're done.
