# ─────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────

import typer  # CLI framework: turns Python functions into terminal commands
from rich.console import Console  # Rich's main object for printing styled output
from rich.panel import Panel  # Rich's bordered box for single-item summaries
from rich.table import Table  # Rich's table for displaying tabular data

from github_analyzer.api import (  # Import our existing data-fetching functions
    fetch_branches,
    fetch_open_prs,
    fetch_recent_commits,
    fetch_repo_metadata,
)

# ─────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────

# Creates the typer application object.
# Every command we define below gets attached to this app.
app = typer.Typer()

# Shared rich console instance used across all commands for styled output
console = Console()

# ─────────────────────────────────────────────
# CLI Commands
# ─────────────────────────────────────────────


@app.command()
def info(repo: str) -> None:
    """
    Display repository metadata: name, description, language,
    stars, forks, open issues, and last updated date.

    Args:
        repo: Full repository name in the format "owner/repo"
    """
    try:
        # Call the existing API function to fetch the data — unchanged from before
        data = fetch_repo_metadata(repo)

        # Build a single formatted string with one field per line
        # rich's inline style syntax [bold]...[/bold] lets us highlight specific values
        content = (
            f"[bold]Description:[/bold] {data['description']}\n"
            f"[bold]Language:[/bold] {data['language']}\n"
            f"[bold]Stars:[/bold] [yellow]{data['stars']}[/yellow]\n"
            f"[bold]Forks:[/bold] {data['forks']}\n"
            f"[bold]Open Issues:[/bold] [red]{data['open_issues']}[/red]\n"
            f"[bold]Last Updated:[/bold] {data['last_updated']}"
        )

        # Wrap the content in a Panel — a bordered box with a title
        panel = Panel(content, title=data["name"], border_style="cyan")

        # Print via the rich console instead of typer.echo()
        console.print(panel)

    except Exception as e:
        console.print(f"[bold red]Error fetching repo info:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def commits(repo: str, count: int = 10) -> None:
    """
    Display recent commits for a repository.

    Args:
        repo:  Full repository name in the format "owner/repo"
        count: Number of recent commits to display (default: 10)
    """
    try:
        # Call the existing API function to fetch commit data — unchanged from before
        data = fetch_recent_commits(repo, count)

        # Create a table with a title and one column per field
        table = Table(title=f"Recent Commits — {repo}")
        table.add_column("SHA", style="cyan")
        table.add_column("Date")
        table.add_column("Author")
        table.add_column("Message")

        # Add one row per commit
        for commit in data:
            table.add_row(
                commit["sha"],
                commit["date"],
                commit["author"],
                commit["message"],
            )

        # Print the table via the rich console
        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error fetching commits:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def prs(repo: str) -> None:
    """
    Display open pull requests and branches for a repository.

    Args:
        repo: Full repository name in the format "owner/repo"
    """
    try:
        # Fetch both open PRs and branches — unchanged from before
        open_prs = fetch_open_prs(repo)
        branches = fetch_branches(repo)

        # ── Open Pull Requests table ──
        pr_table = Table(title=f"Open Pull Requests — {repo}")
        pr_table.add_column("#", style="cyan")
        pr_table.add_column("Title")
        pr_table.add_column("From → Into")
        pr_table.add_column("Author")

        if open_prs:
            for pr in open_prs:
                pr_table.add_row(
                    str(pr["number"]),
                    pr["title"],
                    f"{pr['from_branch']} → {pr['into_branch']}",
                    pr["author"],
                )
        else:
            # add_row with a single value still needs one string per column,
            # so we pass empty strings for the remaining columns
            pr_table.add_row("[dim]No open pull requests[/dim]", "", "", "")

        console.print(pr_table)

        # ── Branches table ──
        branch_table = Table(title="Branches")
        branch_table.add_column("Name", style="magenta")
        branch_table.add_column("Latest Commit", style="cyan")

        for branch in branches:
            branch_table.add_row(branch["name"], branch["latest_commit_sha"])

        console.print(branch_table)

    except Exception as e:
        console.print(f"[bold red]Error fetching PRs/branches:[/bold red] {e}")
        raise typer.Exit(code=1)
