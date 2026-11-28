# SPDX-License-Identifier: Apache-2.0
"""Run the installed assessment and receiving interfaces against the draft suites."""

import argparse
import json
import shlex
import subprocess
from pathlib import Path

from quaecer.spec_qualification import MAX_REQUEST_BYTES


def check_request_size(command: tuple[str, ...], suite: Path, receiver: bool) -> None:
    """Check the inclusive encoded-byte bound through the installed process interface."""
    cases = [suite / "wire/QUAL-TC-0001", suite / "assessment/QUAL-TC-0071"]
    if receiver:
        cases.extend((suite / "receiver/QUAL-TC-0026", suite / "receiver/QUAL-TC-0032"))
    for case in cases:
        value = json.loads((case / "input.json").read_bytes())
        if value.get("operation") == "validate":
            value["policy"]["use"]["scope"] = "Evidence scope µ"
        raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
        padded = raw.ljust(MAX_REQUEST_BYTES, b" ")
        expected = json.loads((case / "expected.json").read_bytes())
        for request, outcome in ((padded, expected), (padded + b" ", {"status": "invalid"})):
            response = subprocess.check_output(command, input=request, timeout=30)
            if json.loads(response) != outcome:
                name = Path(command[0]).name
                raise SystemExit(f"{name} {case.name} failed the request byte bound")


def main() -> None:
    """Run the installed evaluators and verify the resulting report manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("qualifier", "qualcheck", "conform", "seal", "suite", "out"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--qualref", type=Path)
    parser.add_argument("--clockcheck", type=Path)
    args = parser.parse_args()
    if (args.qualref is None) != (args.clockcheck is None):
        parser.error("--qualref and --clockcheck are required together")
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
    commands = [
        ((str(executable.resolve()), "serve-process"), name, section)
        for executable, name, section in runs
    ]
    if args.qualref is not None:
        command = (
            str(args.qualref.resolve()),
            "serve-process",
            "--clockcheck",
            str(args.clockcheck.resolve()),
        )
        commands.extend(
            (command, "qualref", section) for section in ("wire", "assessment", "receiver")
        )
    for command, name, section in commands:
        if section == "wire":
            check_request_size(command, suite, receiver=name != "qualifier")
    for command, name, section in commands:
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
                shlex.join(command),
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
