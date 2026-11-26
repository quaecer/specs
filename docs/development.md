# Development

Start with `uv sync --locked`. Run `uv run --locked pytest` and
`uv run --locked mypy src` from the directory containing `pyproject.toml`.
From the repository root, install the hooks with
`uv run --project qualification --locked pre-commit install`.
The secret-scanning hook needs Gitleaks on `PATH`.

Use pull requests and squash with the checked title and an empty message body.
Run `tools/gate.sh` with the maintainer's pattern environment before promotion.
