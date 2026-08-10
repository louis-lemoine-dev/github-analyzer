# GitHub Analyzer CLI

A command-line tool for exploring GitHub repositories directly from your terminal — view repo metadata, recent commits, and open pull requests with clean, formatted output.

Built as a learning project to practice working with REST APIs, building CLI tools, and following a professional development workflow (Git, automated testing, CI/CD).

## Features

- **`info`** — Display repository metadata: description, language, stars, forks, open issues, and last update date
- **`commits`** — List recent commits with SHA, date, author, and message
- **`prs`** — List open pull requests and branches

All output is rendered using [rich](https://github.com/Textualize/rich), with tables and panels for readability.

## Installation

**Prerequisites:** Python 3.12+, [Poetry](https://python-poetry.org/), and a GitHub account.

1. Clone the repository:

```bash
   git clone git@github.com:louis-lemoine-dev/github-analyzer.git
   cd github-analyzer
```

2. Install dependencies:

```bash
   poetry install
```

3. Create a `.env` file in the project root with a GitHub Personal Access Token:

```env
GITHUB_TOKEN=your_token_here
```

The token needs read-only access to the repositories you want to analyze. See [GitHub's documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) for how to generate one.

## Usage

Run commands via Poetry:

```bash
poetry run github-analyzer info louis-lemoine-dev/github-analyzer
poetry run github-analyzer commits louis-lemoine-dev/github-analyzer
poetry run github-analyzer commits louis-lemoine-dev/github-analyzer --count 5
poetry run github-analyzer prs louis-lemoine-dev/github-analyzer
```

All commands take a repository in the format `owner/repo`.

## Development

Run the test suite:

```bash
poetry run pytest
```

Run the linter and type checker:

```bash
poetry run ruff check .
poetry run pyright
```

All three checks run automatically in CI on every push and pull request via GitHub Actions.

## Tech stack

- [`requests`](https://requests.readthedocs.io/) — HTTP client for the GitHub REST API
- [`typer`](https://typer.tiangolo.com/) — CLI framework
- [`rich`](https://rich.readthedocs.io/) — terminal formatting
- [`pytest`](https://docs.pytest.org/) — testing
- [`ruff`](https://docs.astral.sh/ruff/) — linting and formatting
- [`pyright`](https://microsoft.github.io/pyright/) — static type checking
