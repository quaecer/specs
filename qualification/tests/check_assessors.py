# SPDX-License-Identifier: Apache-2.0
"""Run the installed assessment and receiving interfaces against the draft suites."""

import argparse
import json
import shlex
import subprocess
from pathlib import Path


def main() -> None:
    """Run both programs through the generic runner and verify the report manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("qualifier", "qualcheck", "conform", "seal", "suite", "out"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    suite = args.suite.resolve()
    output = args.out.resolve()
    output.mkdir()
    runs = [
        (args.qualifier, "qualifier", "wire"),
        (args.qualifier, "qualifier", "assessment"),
        (args.qualcheck, "qualcheck", "wire"),
        (args.qualcheck, "qualcheck", "assessment"),
        (args.qualcheck, "qualcheck", "receiver"),
    ]
    artifacts = []
    totals = {}
    for executable, name, section in runs:
        label = f"{name}-{section}"
        report = label + ".ttl"
        summary = label + ".json"
        result = subprocess.run(
            [
                str(args.conform.resolve()),
                "run",
                "--suite",
                str(suite / section),
                "--impl",
                shlex.join((str(executable.resolve()), "serve-process")),
                "--report",
                report,
            ],
            cwd=output,
            capture_output=True,
            check=False,
        )
        (output / summary).write_bytes(result.stdout)
        if result.returncode:
            detail = result.stderr.decode("utf-8", errors="replace")
            raise SystemExit(f"{label} failed: {detail}")
        checked = json.loads(result.stdout)["counts"]
        expected = len(list((suite / section).glob("*/case.json")))
        if checked != {"passed": expected, "failed": 0, "cantTell": 0}:
            raise SystemExit(f"{label} did not account for every case")
        totals[label] = expected
        artifacts.extend((report, summary))

    seal = str(args.seal.resolve())
    manifest = subprocess.check_output(
        [seal, "freeze", *artifacts, "--out", "manifest.json"],
        cwd=output,
        text=True,
    ).strip()
    verified = subprocess.check_output([seal, "verify", "manifest.json"], cwd=output, text=True)
    if verified.strip() != manifest:
        raise SystemExit("report manifest changed")
    print(json.dumps({"manifest": manifest, "checks": totals}, sort_keys=True))


if __name__ == "__main__":
    main()
