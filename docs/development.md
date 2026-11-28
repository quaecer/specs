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

From `qualification/`, run `python tests/check_traceability.py` to check
the links between numbered clauses and positive and negative cases.
`uv run --locked python tests/check_wire_cases.py` also checks the schemas
and runs the structural cases with offline reference resolution.

The wheel includes the draft schemas, registries, specification, suite,
JSON-LD contexts and SHACL shapes from their source directories. The installed
module exposes `schema(name)`, `registry(name)`, `suite_path(name)`,
`context(name)` and `shape(name)`. After editing resources in a local
checkout, reinstall the distribution before testing the installed copies.

For the installed check, build wheels for this specification and the
assessment, receiving, runner and sealing commands. Install the specification
into each assessor's environment to keep their schema data identical.
The receiver environment needs only its wheel and the specification data.
Run `qualification/tests/check_assessors.py --help` for the path arguments.
Pass the `suite` directory from the installed specification and a new output
directory. The check retains one EARL and one JSON report per invocation
and verifies an exact manifest of those reports.

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
