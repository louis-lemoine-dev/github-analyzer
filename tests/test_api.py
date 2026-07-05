# ─────────────────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────────────────

from github_analyzer.api import (
    _parse_branches,
    _parse_open_prs,
    _parse_recent_commits,
    _parse_repo_metadata,
)

# ─────────────────────────────────────────────────────────
# Tests for _parse_repo_metadata
# ─────────────────────────────────────────────────────────


def test_parse_repo_metadata_extracts_expected_fields():
    """
    Given a realistic raw GitHub API response for repo metadata,
    _parse_repo_metadata should extract exactly the fields the CLI needs,
    with no extra or missing keys.
    """
    # Arrange: a fake but realistic GitHub API response.
    # Only the fields _parse_repo_metadata actually reads are included —
    # a real response has dozens more fields we don't care about.
    raw_response = {
        "name": "github-analyzer",
        "description": "A CLI tool to analyze GitHub repos",
        "language": "Python",
        "stargazers_count": 5,
        "forks_count": 2,
        "open_issues_count": 1,
        "updated_at": "2026-07-05T08:31:51Z",
    }

    # Act: call the function under test
    result = _parse_repo_metadata(raw_response)

    # Assert: the output matches exactly what we expect
    assert result == {
        "name": "github-analyzer",
        "description": "A CLI tool to analyze GitHub repos",
        "language": "Python",
        "stars": 5,
        "forks": 2,
        "open_issues": 1,
        "last_updated": "2026-07-05T08:31:51Z",
    }


# ─────────────────────────────────────────────────────────
# Tests for _parse_recent_commits
# ─────────────────────────────────────────────────────────


def test_parse_recent_commits_extracts_expected_fields():
    """
    Given a realistic raw GitHub API response for commits,
    _parse_recent_commits should extract exactly the fields the CLI needs,
    shorten the SHA to 7 characters, and keep only the first line of the message.
    """
    # Arrange: a fake but realistic GitHub API commits response.
    # Commits are returned as a list, and the message includes a multi-line
    # body to verify only the first line is kept.
    raw_response = [
        {
            "sha": "9b7a47d1234567890abcdef1234567890abcdef",
            "commit": {
                "message": (
                    "feat: add fetch_repo_metadata function\n\nLonger body text here."
                ),
                "author": {
                    "name": "Louis Lemoine",
                    "date": "2026-05-30T18:06:19Z",
                },
            },
        }
    ]

    # Act
    result = _parse_recent_commits(raw_response)

    # Assert
    assert result == [
        {
            "sha": "9b7a47d",
            "message": "feat: add fetch_repo_metadata function",
            "author": "Louis Lemoine",
            "date": "2026-05-30T18:06:19Z",
        }
    ]


# ─────────────────────────────────────────────────────────
# Tests for _parse_open_prs
# ─────────────────────────────────────────────────────────


def test_parse_open_prs_extracts_expected_fields():
    """
    Given a realistic raw GitHub API response for pull requests,
    _parse_open_prs should extract exactly the fields the CLI needs,
    correctly navigating the nested user/head/base structure.
    """
    # Arrange: a fake but realistic GitHub API pulls response.
    raw_response = [
        {
            "number": 5,
            "title": "feat: add fetch_recent_commits function",
            "user": {"login": "louis-lemoine-dev"},
            "head": {"ref": "feat/list-recent-commits"},
            "base": {"ref": "main"},
            "created_at": "2026-05-31T13:12:13Z",
        }
    ]

    # Act
    result = _parse_open_prs(raw_response)

    # Assert
    assert result == [
        {
            "number": 5,
            "title": "feat: add fetch_recent_commits function",
            "author": "louis-lemoine-dev",
            "from_branch": "feat/list-recent-commits",
            "into_branch": "main",
            "opened_at": "2026-05-31T13:12:13Z",
        }
    ]


# ─────────────────────────────────────────────────────────
# Tests for _parse_branches
# ─────────────────────────────────────────────────────────


def test_parse_branches_extracts_expected_fields():
    """
    Given a realistic raw GitHub API response for branches,
    _parse_branches should extract the branch name and shorten
    the latest commit SHA to 7 characters.
    """
    # Arrange: a fake but realistic GitHub API branches response.
    raw_response = [
        {
            "name": "main",
            "commit": {"sha": "d895fe61234567890abcdef1234567890abcdef"},
        }
    ]

    # Act
    result = _parse_branches(raw_response)

    # Assert
    assert result == [
        {
            "name": "main",
            "latest_commit_sha": "d895fe6",
        }
    ]
