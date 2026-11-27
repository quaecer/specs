# Development

Start with `uv sync --locked`. Run `uv run --locked pytest` and
`uv run --locked mypy src` from the directory containing `pyproject.toml`.
From the repository root, install the hooks with
`uv run --project qualification --locked pre-commit install`.
The secret-scanning hook needs Gitleaks on `PATH`.

Use a single-line Conventional Commit subject for commits and pull request
titles, such as `feat: add export` or `fix(parser): validate dates`.
Squash with the checked title followed by the pull request number in
parentheses and leave the commit body empty.
Run `tools/gate.sh` with the maintainer's pattern environment before promotion.
