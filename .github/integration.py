# SPDX-License-Identifier: Apache-2.0
"""Build and exercise the installed components from exact Git revisions."""

import argparse
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

DRAFTS = {
    "specs": "formal-semantics",
    "qualifier": "scalar-assessment",
    "qualcheck": "scalar-receiver",
    "qualref": "reference-evaluator",
    "clockcheck": "exact-constraints",
    "conform": "process-suite",
    "seal": "artifact-manifests",
}
STACKED = {"specs", "qualifier", "qualcheck"}


def checkout(root: Path, name: str, head: tuple[str, str, str]) -> None:
    """Fetch one current draft or its successor on main. Verify the triggering topic."""
    repository, branch, revision = head
    current = repository == f"quaecer/{name}"
    topic = current and name in STACKED and branch.startswith("topic/")
    remote = f"https://github.com/quaecer/{name}.git"
    ref = f"refs/heads/{DRAFTS[name]}"
    directory = root / name
    directory.mkdir()

    def git(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=directory,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode:
            raise SystemExit(f"{name}: git {args[0]} failed ({completed.returncode})")
        return completed.stdout.strip()

    git("init", "--quiet")
    if current and not topic:
        target = revision
    else:
        advertised = git("ls-remote", "--heads", remote, ref)
        target = advertised.split()[0] if advertised else "refs/heads/main"
    git("fetch", "--quiet", "--no-tags", remote, target)
    git("switch", "--quiet", "--detach", "FETCH_HEAD")
    if topic:
        git("fetch", "--quiet", "--no-tags", remote, revision)
        git("merge-base", "--is-ancestor", revision, "HEAD")
    print(f"{name} {git('rev-parse', 'HEAD')}", flush=True)


def installed_check(root: Path, scratch: Path, python: str, output: Path) -> None:
    """Build source wheels and run the specification's installed conformance check."""
    wheels = scratch / "wheels"
    wheels.mkdir()
    for name in DRAFTS:
        project = root / name
        if name == "specs":
            project /= "qualification"
        subprocess.run(
            ["uv", "build", "--wheel", "--out-dir", str(wheels)],
            cwd=project,
            check=True,
        )
    venv = scratch / "venv"
    subprocess.run(["uv", "venv", "--python", python, str(venv)], check=True)
    binary = venv / "bin"
    interpreter = str(binary / "python")
    constraints = scratch / "runtime.txt"
    subprocess.run(
        [
            "uv",
            "export",
            "--frozen",
            "--no-dev",
            "--no-emit-project",
            "--no-emit-package",
            "quaecer-spec-qualification",
            "--no-hashes",
            "--output-file",
            str(constraints),
            "--quiet",
        ],
        cwd=root / "qualifier",
        check=True,
    )
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            interpreter,
            "--constraint",
            str(constraints),
            *map(str, sorted(wheels.glob("*.whl"))),
        ],
        check=True,
    )
    suite = subprocess.check_output(
        [
            interpreter,
            "-I",
            "-c",
            "from quaecer.spec_qualification import suite_path; print(suite_path('wire').parent)",
        ],
        text=True,
    ).strip()
    command = [interpreter, str(root / "specs/qualification/tests/check_assessors.py")]
    for component in (
        "qualifier",
        "qualcheck",
        "qualref",
        "clockcheck",
        "conform",
        "seal",
    ):
        command.extend((f"--{component}", str(binary / component)))
    subprocess.run([*command, "--suite", suite, "--out", str(output)], check=True)


def main() -> None:
    """Run from local checkouts or from the currently assembled review heads."""
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--workspace", type=Path, help="directory containing the component checkouts"
    )
    source.add_argument("--head", nargs=3, metavar=("REPOSITORY", "BRANCH", "REVISION"))
    parser.add_argument("--python", default="3.12")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="qualification-integration-") as attempt:
        scratch = Path(attempt)
        if args.workspace is None:
            repo, branch, revision = args.head
            allowed = {f"quaecer/{name}" for name in DRAFTS} | {"quaecer/paper-qual"}
            if repo not in allowed or not re.fullmatch(r"[0-9a-f]{40}", revision):
                parser.error("invalid PR repository or head revision")
            root = scratch / "sources"
            root.mkdir()
            for name in DRAFTS:
                checkout(root, name, (repo, branch, revision))
        else:
            root = args.workspace.resolve()
        installed_check(root, scratch, args.python, args.out.resolve())


if __name__ == "__main__":
    main()
