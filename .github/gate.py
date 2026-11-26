# SPDX-License-Identifier: Apache-2.0
"""Check reachable Git history against externally supplied publication rules."""

import hashlib
import json
import os
import re
import subprocess
from collections.abc import Iterator
from pathlib import Path, PurePosixPath

LICENSE_SHA256 = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
MAX_BLOB_BYTES = 5 * 1024 * 1024
PR_SUFFIX = re.compile(rb" \(#[1-9][0-9]*\)(?=\n?\Z)")
IDENTITY = re.compile(rb"(?:[^@\s]+@users\.noreply\.github\.com|noreply@github\.com)")


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def patterns(name: str) -> re.Pattern[str]:
    """Read the pattern without printing it or exposing it to shell expansion."""
    value = os.environ.get(name)
    if not value and (config := os.environ.get("GATE_CONFIG")):
        value = json.loads(Path(config).read_bytes()).get(name)
    if not value:
        raise ValueError(f"missing {name}")
    return re.compile(value, re.IGNORECASE)


def blocked_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    hidden = "." + "tracking"
    return (
        hidden in parts
        or "results" in parts[:-1]
        or any(p.startswith(".env") for p in parts)
        or path.lower().endswith(".pem")
    )


def github_pages(repo: str, path: str) -> list[dict[str, object]]:
    """Read every page from a repository metadata endpoint."""
    separator = "&" if "?" in path else "?"
    response = subprocess.run(
        [
            "gh",
            "api",
            "--paginate",
            "--slurp",
            f"repos/{repo}/{path}{separator}per_page=100",
        ],
        check=True,
        capture_output=True,
    )
    pages = json.loads(response.stdout)
    if not isinstance(pages, list) or any(not isinstance(page, list) for page in pages):
        raise ValueError("malformed GitHub response")
    records = [record for page in pages for record in page]
    if any(not isinstance(record, dict) for record in records):
        raise ValueError("malformed GitHub record")
    return records


def github_text(repo: str) -> Iterator[tuple[str, bytes]]:
    """Yield issue and pull request text, including all comment and review bodies."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("invalid GitHub repository")

    def fields(record: dict[str, object], label: str, *names: str) -> Iterator[tuple[str, bytes]]:
        for name in names:
            value = record[name]
            if value is not None:
                if not isinstance(value, str):
                    raise ValueError("invalid GitHub text")
                yield f"{label}/{name}", value.encode("utf-8")

    for issue in github_pages(repo, "issues?state=all"):
        number = issue["number"]
        if type(number) is not int or number <= 0:
            raise ValueError("invalid GitHub issue number")
        is_pull = "pull_request" in issue
        yield from fields(issue, f"{'pull' if is_pull else 'issue'}/{number}", "title", "body")
        if is_pull:
            for review in github_pages(repo, f"pulls/{number}/reviews"):
                yield from fields(review, f"pull/{number}/review/{review['id']}", "body")
    for endpoint in ("issues/comments", "pulls/comments"):
        for comment in github_pages(repo, endpoint):
            yield from fields(comment, f"{endpoint}/{comment['id']}", "body")


def main() -> int:
    os.chdir(os.fsdecode(git("rev-parse", "--show-toplevel").rstrip(b"\n")))
    hard = patterns("GATE_PATTERNS_HARD")
    review = patterns("GATE_PATTERNS_REVIEW")
    findings: set[tuple[str, str]] = set()

    def scan(raw: bytes, key: str) -> None:
        content = raw.decode("utf-8", errors="replace")
        if hard.search(content):
            findings.add(("blocked text", key))
        if review.search(content):
            findings.add(("review required", key))

    checked_blobs: dict[str, tuple[int, bool]] = {}
    for rev in git("rev-list", "--all", "HEAD").decode("ascii").splitlines():
        commit = git("cat-file", "commit", rev)
        metadata, _, body = commit.partition(b"\n\n")
        emails = re.findall(rb"^(?:author|committer) .* <([^<>]+)> ", metadata, re.MULTILINE)
        if len(emails) != 2 or any(not IDENTITY.fullmatch(email) for email in emails):
            findings.add(("unexpected email identity", rev))
        if sum(line.startswith(b"parent ") for line in metadata.splitlines()) > 1:
            findings.add(("nonlinear history", rev))
        # Exclude the final GitHub PR reference from the publication scan.
        scan(PR_SUFFIX.sub(b"", body), rev)
        entries = git("ls-tree", "-rz", rev).split(b"\0")
        license_found = False
        for entry in filter(None, entries):
            spec, _, raw_path = entry.partition(b"\t")
            mode, kind, sha = spec.decode("ascii").split()
            path = raw_path.decode("utf-8", errors="replace")
            scan(raw_path, sha)
            if blocked_path(path):
                findings.add(("blocked path", sha))
            if mode not in {"100644", "100755"} or kind != "blob":
                findings.add(("unexpected tree entry", sha))
                continue
            size, has_header = checked_blobs.get(sha, (-1, False))
            if size == -1:
                size = int(git("cat-file", "-s", sha))
                if size > MAX_BLOB_BYTES:
                    findings.add(("oversized blob", sha))
                else:
                    raw = git("cat-file", "blob", sha)
                    scan(raw, sha)
                    has_header = any(
                        b"SPDX-License-Identifier: Apache-2.0" in line
                        for line in raw.splitlines()[:3]
                    )
                checked_blobs[sha] = size, has_header
            if path.endswith((".py", ".sh")) and not has_header:
                findings.add(("missing license header", sha))
            if path == "LICENSE":
                license_found = (
                    size <= MAX_BLOB_BYTES
                    and hashlib.sha256(git("cat-file", "blob", sha)).hexdigest() == LICENSE_SHA256
                )
            if path.endswith(".ipynb") and size <= MAX_BLOB_BYTES:
                try:
                    cells = json.loads(git("cat-file", "blob", sha))["cells"]
                    if any(c.get("outputs") or c.get("execution_count") is not None for c in cells):
                        findings.add(("notebook execution state", sha))
                except (KeyError, TypeError, ValueError, AttributeError):
                    findings.add(("malformed notebook", sha))
        if any(entries) and not license_found:
            findings.add(("missing or changed license", rev))

    scan(git("for-each-ref", "refs/tags", "--format=%(refname)%0a%(contents)"), "tags")
    if repo := os.environ.get("GATE_GITHUB_REPOSITORY"):
        for label, content in github_text(repo):
            scan(content, label)
    outcome = subprocess.run(
        ["gitleaks", "git", "--log-opts=--all HEAD", "--redact=100", "--no-banner"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if outcome.returncode:
        findings.add(("secret scan failed", "history"))
    for reason, identity in sorted(findings):
        print(f"{reason}: {identity}")
    print(f"gate: {'blocked' if findings else 'pass'} ({len(findings)} findings)")
    return int(bool(findings))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        KeyError,
        ValueError,
        OSError,
        subprocess.CalledProcessError,
        re.error,
    ) as error:
        print(f"gate could not complete ({type(error).__name__})")
        raise SystemExit(1) from None
