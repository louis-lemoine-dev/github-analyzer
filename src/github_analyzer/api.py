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


def fetch_repo_metadata(repo: str) -> dict:
    """
    Fetches metadata for a GitHub repository via the REST API.

    Args:
        repo: Full repository name in the format "owner/repo"
              e.g. "louis-lemoine-dev/github-analyzer"

    Returns:
        A dictionary containing key repository metadata fields.
    """
    # Retrieve the GitHub token from environment variables
    # Raises an error early if the token is missing, rather than failing silently later
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN not found. Make sure it is set in your .env file."
        )

    # Build the API endpoint URL using the provided repo name
    url = f"https://api.github.com/repos/{repo}"

    # Set up request headers:
    # - Authorization: authenticates the request using the PAT
    # - Accept: tells GitHub which version of the API response format we want
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    # Make the HTTP GET request to the GitHub API
    response = requests.get(url, headers=headers)

    # Raise an exception if the request failed (e.g. 404 repo not found, 401 bad token)
    response.raise_for_status()

    # Parse the JSON response into a Python dictionary
    data = response.json()

    # Extract and return only the fields we care about
    return {
        "name": data["name"],
        "description": data["description"],
        "language": data["language"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "last_updated": data["updated_at"],
    }


def fetch_recent_commits(repo: str, count: int = 10) -> list[dict]:
    """
    Fetches the most recent commits for a GitHub repository.

    Args:
        repo:  Full repository name in the format "owner/repo"
               e.g. "louis-lemoine-dev/github-analyzer"
        count: Number of recent commits to fetch (default: 10)

    Returns:
        A list of dictionaries, one per commit, containing
        the SHA, message, author name, and date.
    """
    # Retrieve the GitHub token from environment variables
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN not found. Make sure it is set in your .env file."
        )

    # Build the API endpoint URL for commits
    url = f"https://api.github.com/repos/{repo}/commits"

    # Set up authentication and format headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    # Query parameters: control how many commits the API returns
    params = {"per_page": count}

    # Make the HTTP GET request, passing query parameters alongside headers
    response = requests.get(url, headers=headers, params=params)

    # Raise an exception if the request failed
    response.raise_for_status()

    # Parse the JSON response — this time it's a list of commit objects
    data = response.json()

    # Extract the relevant fields from each commit using a list comprehension
    # Note the nested structure: commit data lives inside commit["commit"]
    return [
        {
            "sha": item["sha"][
                :7
            ],  # Shortened to 7 chars — the standard readable format
            "message": item["commit"]["message"].split("\n")[
                0
            ],  # First line only — commits can have multi-line messages
            "author": item["commit"]["author"]["name"],
            "date": item["commit"]["author"]["date"],
        }
        for item in data
    ]


# ─────────────────────────────────────────────
# Quick manual test (remove before final version)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Only runs when this file is executed directly, not when imported
    result = fetch_recent_commits("louis-lemoine-dev/github-analyzer")
    print(result)
