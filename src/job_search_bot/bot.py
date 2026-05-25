"""Conversational CLI entry point.

If `ANTHROPIC_API_KEY` is set, runs as a Claude-powered chatbot that parses
natural language and calls the Workday search tool.

If not set, falls back to a slot-filling REPL: asks for company and keyword
in turn. The underlying Workday client works the same either way, so the bot
is always usable even without an API key.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .companies import known_companies, resolve_company
from .csv_writer import write_csv
from .models import JobPosting
from .workday import search_jobs

_console = Console()

_SYSTEM_PROMPT = """You are a helpful job-search assistant. The user is looking for \
job postings at known companies on Workday. When they describe what they want, call \
the `search_workday_jobs` tool with the company name, keywords (e.g. "AI", "data \
science"), and optional location filter (e.g. "Bangalore"). After the tool returns, \
tell the user how many jobs were found and where the CSV was saved. Be concise."""

_TOOL_SPEC = {
    "name": "search_workday_jobs",
    "description": (
        "Search a company's Workday careers site for job postings matching the given "
        "keywords (and optionally a location filter). Writes results to a CSV and "
        "returns a summary."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "company": {
                "type": "string",
                "description": "Company name, e.g. 'PwC', 'NVIDIA', 'Salesforce'.",
            },
            "keywords": {
                "type": "string",
                "description": "Search terms like 'AI', 'data scientist', 'platform engineer'.",
            },
            "location": {
                "type": "string",
                "description": "Optional city or country filter, e.g. 'Bangalore'.",
            },
            "limit": {
                "type": "integer",
                "description": "Max results to return. Default 100.",
            },
        },
        "required": ["company", "keywords"],
    },
}


def _run_search(
    company_name: str,
    keywords: str,
    location: str | None = None,
    limit: int = 100,
) -> tuple[list[JobPosting], Path | None, str | None]:
    """Resolve the company, fetch jobs, write CSV. Returns (jobs, csv_path, error)."""
    company = resolve_company(company_name)
    if company is None:
        return (
            [],
            None,
            (
                f"I don't know '{company_name}' yet. "
                f"Known companies: {', '.join(known_companies())}."
            ),
        )

    postings = search_jobs(company, keywords=keywords, location=location, limit=limit)
    if not postings:
        return [], None, None
    csv_path = write_csv(postings, company.canonical_name, keywords or "all")
    return postings, csv_path, None


def _print_summary(postings: list[JobPosting], csv_path: Path | None) -> None:
    if not postings:
        _console.print("[yellow]No matching jobs found.[/yellow]")
        return
    table = Table(title=f"{len(postings)} job(s) found")
    table.add_column("Job ID", style="cyan")
    table.add_column("Title")
    table.add_column("Location", style="green")
    for p in postings[:10]:
        table.add_row(p.job_id, p.title, p.location)
    if len(postings) > 10:
        table.add_row("…", f"(+{len(postings) - 10} more)", "")
    _console.print(table)
    if csv_path is not None:
        _console.print(f"[bold]Saved:[/bold] {csv_path}")


def _slot_fill_loop() -> None:
    """Fallback REPL when no Anthropic key is configured."""
    _console.print(
        "[dim]Running in slot-filling mode (no ANTHROPIC_API_KEY detected).[/dim]"
    )
    _console.print(f"[dim]Known companies: {', '.join(known_companies())}[/dim]\n")
    while True:
        try:
            company = _console.input("[bold]Company[/bold] (or 'quit'): ").strip()
        except (EOFError, KeyboardInterrupt):
            return
        if company.lower() in {"quit", "exit", "q"}:
            return
        if not company:
            continue
        keywords = _console.input("[bold]Keyword/field[/bold] (e.g. AI): ").strip()
        location = _console.input(
            "[bold]Location filter[/bold] (optional, press Enter to skip): "
        ).strip() or None
        postings, csv_path, error = _run_search(company, keywords, location)
        if error:
            _console.print(f"[red]{error}[/red]\n")
            continue
        _print_summary(postings, csv_path)
        _console.print("")


def _chat_loop(api_key: str) -> None:
    """Conversational REPL using the Anthropic SDK and tool use."""
    try:
        from anthropic import Anthropic
    except ImportError:
        _console.print(
            "[red]anthropic package not installed. "
            "Run `pip install anthropic` or use the no-API fallback.[/red]"
        )
        return

    client = Anthropic(api_key=api_key)
    model = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    messages: list[dict] = []
    _console.print(
        f"[dim]Chat mode (model={model}). Type 'quit' to exit.[/dim]\n"
    )

    while True:
        try:
            user_input = _console.input("[bold cyan]You:[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            return
        if user_input.lower() in {"quit", "exit", "q"}:
            return
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})

        while True:
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                system=_SYSTEM_PROMPT,
                tools=[_TOOL_SPEC],
                messages=messages,
            )
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue
                    args = block.input
                    postings, csv_path, error = _run_search(
                        company_name=args.get("company", ""),
                        keywords=args.get("keywords", ""),
                        location=args.get("location"),
                        limit=int(args.get("limit", 100)),
                    )
                    _print_summary(postings, csv_path)
                    if error:
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": error,
                                "is_error": True,
                            }
                        )
                    else:
                        summary = (
                            f"{len(postings)} jobs found. "
                            f"CSV: {csv_path}" if csv_path else "No matching jobs."
                        )
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": summary,
                            }
                        )
                messages.append({"role": "user", "content": tool_results})
                continue

            for block in response.content:
                if getattr(block, "type", None) == "text":
                    _console.print(f"[bold magenta]Bot:[/bold magenta] {block.text}\n")
            break


def main() -> int:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    _console.rule("[bold]Job Search Bot[/bold]")
    if api_key:
        _chat_loop(api_key)
    else:
        _slot_fill_loop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
