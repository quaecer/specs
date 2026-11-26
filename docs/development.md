# Development

Start with `uv sync --locked`. Run `uv run --locked pytest` and
`uv run --locked mypy src` from the directory containing `pyproject.toml`.
From the repository root, install the hooks with
`uv run --project qualification --locked pre-commit install`.
The secret-scanning hook needs Gitleaks on `PATH`.

Use a single-line Conventional Commit subject for commits and pull request
titles, such as `feat: add export` or `fix(parser): validate dates`.
Squash with the pull request title followed by the pull request number in
parentheses and leave the commit body empty.
Run `python3 .github/gate.py` with the maintainer's pattern environment before promotion.

Set `GATE_GITHUB_REPOSITORY` to the GitHub owner and repository and authenticate
`gh` to include all pull request and issue text in the publication scan.
CI scans repository text for owner branches. Run a maintainer scan before
promotion. Repository settings remove merged topic branches.

## Installed integration

The pull request job builds the current qualification drafts from exact Git
commits, installs their wheels together and runs the shipped case suites.
For a pull request outside a topic stack, it uses that pull request's exact
head in place of the corresponding draft. For a stacked topic, its exact
head must be an ancestor of the assembled draft. Unit and contract tests
also run on each topic's own head.

Review each stack from its first topic. After a squash merge, restack the
pending descendants onto the new base before the next merge.
