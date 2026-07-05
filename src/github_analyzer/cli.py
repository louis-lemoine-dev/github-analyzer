# ─────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────

import typer  # CLI framework: turns Python functions into terminal commands

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
        # Call the existing API function to fetch the data
        data = fetch_repo_metadata(repo)

        # Print each field in a simple, readable format
        typer.echo(f"Name:          {data['name']}")
        typer.echo(f"Description:   {data['description']}")
        typer.echo(f"Language:      {data['language']}")
        typer.echo(f"Stars:         {data['stars']}")
        typer.echo(f"Forks:         {data['forks']}")
        typer.echo(f"Open Issues:   {data['open_issues']}")
        typer.echo(f"Last Updated:  {data['last_updated']}")

    except Exception as e:
        # Catch any error (network issue, bad token, repo not found, etc.)
        # and display it cleanly instead of crashing with a raw traceback
        typer.echo(f"Error fetching repo info: {e}")
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
        # Call the existing API function to fetch commit data
        data = fetch_recent_commits(repo, count)

        # Print each commit on its own line
        for commit in data:
            typer.echo(
                f"{commit['sha']}  {commit['date']}  {commit['author']}: {commit['message']}"
            )

    except Exception as e:
        typer.echo(f"Error fetching commits: {e}")
        raise typer.Exit(code=1)


@app.command()
def prs(repo: str) -> None:
    """
    Display open pull requests and branches for a repository.

    Args:
        repo: Full repository name in the format "owner/repo"
    """
    try:
        # Fetch both open PRs and branches
        open_prs = fetch_open_prs(repo)
        branches = fetch_branches(repo)

        # Display open PRs
        typer.echo("Open Pull Requests:")
        if open_prs:
            for pr in open_prs:
                typer.echo(
                    f"  #{pr['number']} {pr['title']} ({pr['from_branch']} → {pr['into_branch']}) by {pr['author']}"
                )
        else:
            typer.echo("  No open pull requests.")

        typer.echo("")  # blank line for readability

        # Display branches
        typer.echo("Branches:")
        for branch in branches:
            typer.echo(f"  {branch['name']} ({branch['latest_commit_sha']})")

    except Exception as e:
        typer.echo(f"Error fetching PRs/branches: {e}")
        raise typer.Exit(code=1)


# ─────────────────────────────────────────────
# Entry point for running the CLI directly during development
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app()
