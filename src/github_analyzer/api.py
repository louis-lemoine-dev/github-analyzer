# ─────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────

import os  # Access environment variables at runtime

import requests  # HTTP client for calling the GitHub REST API
from dotenv import (
    load_dotenv,
)  # Reads .env file and loads its key-value pairs into the environment

# Load environment variables from .env file into os.environ
# Called once at module level so all functions in this file can access them
load_dotenv()

# ─────────────────────────────────────────────
# API Functions
# ─────────────────────────────────────────────


# ─────────────────────────────────────────────────────────
# Repo Metadata
# ─────────────────────────────────────────────────────────


def _fetch_repo_metadata_raw(repo: str) -> dict:
    """
    Makes the authenticated HTTP request to GitHub for repo metadata
    and returns the raw, unprocessed JSON response.

    This function handles network I/O only — no parsing logic lives here.

    Args:
        repo: Full repository name in the format "owner/repo"

    Returns:
        The raw JSON response from GitHub as a dictionary.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN not found. Make sure it is set in your .env file."
        )

    url = f"https://api.github.com/repos/{repo}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def _parse_repo_metadata(data: dict) -> dict:
    """
    Extracts the relevant repo metadata fields from a raw GitHub API response.

    This is a pure function: no network calls, no side effects. Given the
    same input, it always returns the same output — which makes it trivial
    to test in isolation.

    Args:
        data: Raw JSON response from the GitHub repo metadata endpoint.

    Returns:
        A clean dictionary containing only the fields the CLI cares about.
    """
    return {
        "name": data["name"],
        "description": data["description"],
        "language": data["language"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "last_updated": data["updated_at"],
    }


def fetch_repo_metadata(repo: str) -> dict:
    """
    Fetches and parses metadata for a GitHub repository.

    Public entry point used by the CLI. Combines the raw fetch and the
    parsing step, so callers don't need to know these are two separate
    pieces internally.

    Args:
        repo: Full repository name in the format "owner/repo"
              e.g. "louis-lemoine-dev/github-analyzer"

    Returns:
        A dictionary containing key repository metadata fields.
    """
    raw_data = _fetch_repo_metadata_raw(repo)
    return _parse_repo_metadata(raw_data)


# ─────────────────────────────────────────────────────────
# Recent Commits
# ─────────────────────────────────────────────────────────


def _fetch_recent_commits_raw(repo: str, count: int = 10) -> list[dict]:
    """
    Makes the authenticated HTTP request to GitHub for recent commits
    and returns the raw, unprocessed JSON response.

    This function handles network I/O only — no parsing logic lives here.

    Args:
        repo:  Full repository name in the format "owner/repo"
        count: Number of recent commits to fetch (default: 10)

    Returns:
        The raw JSON response from GitHub as a list of commit objects.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN not found. Make sure it is set in your .env file."
        )

    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    params = {"per_page": count}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def _parse_recent_commits(data: list[dict]) -> list[dict]:
    """
    Extracts the relevant fields from a raw GitHub API commits response.

    This is a pure function: no network calls, no side effects. Given the
    same input, it always returns the same output — which makes it trivial
    to test in isolation.

    Args:
        data: Raw JSON response from the GitHub commits endpoint —
              a list of commit objects.

    Returns:
        A list of clean dictionaries, one per commit, containing
        the SHA, message, author name, and date.
    """
    return [
        {
            "sha": item["sha"][:7],
            "message": item["commit"]["message"].split("\n")[0],
            "author": item["commit"]["author"]["name"],
            "date": item["commit"]["author"]["date"],
        }
        for item in data
    ]


def fetch_recent_commits(repo: str, count: int = 10) -> list[dict]:
    """
    Fetches and parses the most recent commits for a GitHub repository.

    Public entry point used by the CLI. Combines the raw fetch and the
    parsing step, so callers don't need to know these are two separate
    pieces internally.

    Args:
        repo:  Full repository name in the format "owner/repo"
               e.g. "louis-lemoine-dev/github-analyzer"
        count: Number of recent commits to fetch (default: 10)

    Returns:
        A list of dictionaries, one per commit, containing
        the SHA, message, author name, and date.
    """
    raw_data = _fetch_recent_commits_raw(repo, count)
    return _parse_recent_commits(raw_data)


# ─────────────────────────────────────────────────────────
# Open Pull Requests
# ─────────────────────────────────────────────────────────


def _fetch_open_prs_raw(repo: str) -> list[dict]:
    """
    Makes the authenticated HTTP request to GitHub for open pull requests
    and returns the raw, unprocessed JSON response.

    This function handles network I/O only — no parsing logic lives here.

    Args:
        repo: Full repository name in the format "owner/repo"

    Returns:
        The raw JSON response from GitHub as a list of PR objects.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN not found. Make sure it is set in your .env file."
        )

    url = f"https://api.github.com/repos/{repo}/pulls"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    params = {"state": "open"}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def _parse_open_prs(data: list[dict]) -> list[dict]:
    """
    Extracts the relevant fields from a raw GitHub API pull requests response.

    This is a pure function: no network calls, no side effects. Given the
    same input, it always returns the same output — which makes it trivial
    to test in isolation.

    Args:
        data: Raw JSON response from the GitHub pulls endpoint —
              a list of PR objects.

    Returns:
        A list of clean dictionaries, one per PR, containing the number,
        title, author, source branch, target branch, and creation date.
    """
    return [
        {
            "number": pr["number"],
            "title": pr["title"],
            "author": pr["user"]["login"],
            "from_branch": pr["head"]["ref"],
            "into_branch": pr["base"]["ref"],
            "opened_at": pr["created_at"],
        }
        for pr in data
    ]


def fetch_open_prs(repo: str) -> list[dict]:
    """
    Fetches and parses all open pull requests for a GitHub repository.

    Public entry point used by the CLI. Combines the raw fetch and the
    parsing step, so callers don't need to know these are two separate
    pieces internally.

    Args:
        repo: Full repository name in the format "owner/repo"
              e.g. "louis-lemoine-dev/github-analyzer"

    Returns:
        A list of dictionaries, one per open PR, containing the number,
        title, author, source branch, target branch, and creation date.
    """
    raw_data = _fetch_open_prs_raw(repo)
    return _parse_open_prs(raw_data)


# ─────────────────────────────────────────────────────────
# Branches
# ─────────────────────────────────────────────────────────


def _fetch_branches_raw(repo: str) -> list[dict]:
    """
    Makes the authenticated HTTP request to GitHub for branches
    and returns the raw, unprocessed JSON response.

    This function handles network I/O only — no parsing logic lives here.

    Args:
        repo: Full repository name in the format "owner/repo"

    Returns:
        The raw JSON response from GitHub as a list of branch objects.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN not found. Make sure it is set in your .env file."
        )

    url = f"https://api.github.com/repos/{repo}/branches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def _parse_branches(data: list[dict]) -> list[dict]:
    """
    Extracts the relevant fields from a raw GitHub API branches response.

    This is a pure function: no network calls, no side effects. Given the
    same input, it always returns the same output — which makes it trivial
    to test in isolation.

    Args:
        data: Raw JSON response from the GitHub branches endpoint —
              a list of branch objects.

    Returns:
        A list of clean dictionaries, one per branch, containing the
        branch name and the shortened SHA of its latest commit.
    """
    return [
        {
            "name": branch["name"],
            "latest_commit_sha": branch["commit"]["sha"][:7],
        }
        for branch in data
    ]


def fetch_branches(repo: str) -> list[dict]:
    """
    Fetches and parses all branches for a GitHub repository.

    Public entry point used by the CLI. Combines the raw fetch and the
    parsing step, so callers don't need to know these are two separate
    pieces internally.

    Args:
        repo: Full repository name in the format "owner/repo"
              e.g. "louis-lemoine-dev/github-analyzer"

    Returns:
        A list of dictionaries, one per branch, containing the branch
        name and the shortened SHA of its latest commit.
    """
    raw_data = _fetch_branches_raw(repo)
    return _parse_branches(raw_data)
