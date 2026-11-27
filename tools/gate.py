# SPDX-License-Identifier: Apache-2.0
"""Check reachable Git history against externally supplied publication rules."""

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

LICENSE_SHA256 = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
MAX_BLOB_BYTES = 5 * 1024 * 1024
LEGACY_SUBJECT = re.compile(rb"[a-z0-9][a-z0-9 ._-]{0,49}")
CONVENTIONAL_SUBJECT = re.compile(
    r"[a-z][a-z0-9-]*(?:\([a-z0-9][a-z0-9._/-]*\))?!?: \S(?:.*\S)?",
    re.ASCII | re.IGNORECASE,
)
PR_SUFFIX = re.compile(rb" \(#[1-9][0-9]*\)$")
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


def conventional_subject(message: bytes) -> bool:
    """Check a single UTF-8 commit subject with a Conventional Commits prefix."""
    try:
        subject = message.removesuffix(b"\n").decode("utf-8")
    except UnicodeDecodeError:
        return False
    return subject.isprintable() and CONVENTIONAL_SUBJECT.fullmatch(subject) is not None


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--check-subject":
        if conventional_subject(Path(sys.argv[2]).read_bytes()):
            return 0
        print("expected one Conventional Commit subject, e.g. feat: add export")
        return 1

    os.chdir(os.fsdecode(git("rev-parse", "--show-toplevel").rstrip(b"\n")))
    hard = patterns("GATE_PATTERNS_HARD")
    review = patterns("GATE_PATTERNS_REVIEW")
    findings: set[tuple[str, str]] = set()
    squash = None
    if os.environ.get("GATE_REQUIRE_PR_ID") == "true":
        squash = git("rev-parse", "HEAD").decode("ascii").strip()

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
        msg = body.removesuffix(b"\n")
        conventional = conventional_subject(body)
        legacy = LEGACY_SUBJECT.fullmatch(msg) and not msg.endswith((b".", b" "))
        pr_suffix = PR_SUFFIX.search(msg) if conventional else None
        if rev == squash and pr_suffix is None:
            findings.add(("expected a conventional squash subject with a PR number", rev))
        elif not conventional and not legacy:
            findings.add(("invalid commit message", rev))
        if sum(line.startswith(b"parent ") for line in metadata.splitlines()) > 1:
            findings.add(("nonlinear history", rev))
        # The final PR number is GitHub metadata. Scan all other subject text.
        scan(msg[: pr_suffix.start()] if pr_suffix else body, rev)
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
    except (ValueError, OSError, subprocess.CalledProcessError, re.error) as error:
        print(f"gate could not complete ({type(error).__name__})")
        raise SystemExit(1) from None
