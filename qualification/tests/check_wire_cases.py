# SPDX-License-Identifier: Apache-2.0
"""Run structural fixtures against the checked local schemas."""

import argparse
import json
import sys

from check_traceability import ROOT, _unique, check, read
from jsonschema import Draft202012Validator
from referencing import Registry, Resource


def _validator(name: str = "request") -> Draft202012Validator:
    schemas = [read(path) for path in sorted((ROOT / "schema").glob("*.schema.json"))]
    for schema in schemas:
        Draft202012Validator.check_schema(schema)
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in schemas
    )
    request = read(ROOT / "schema" / f"{name}.schema.json")
    return Draft202012Validator(request, registry=registry)


def main() -> None:
    """Check the fixtures or answer one structural validation request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    validator = _validator()
    if args.serve:
        limit = 2 * 1024 * 1024
        raw = sys.stdin.buffer.read(limit + 1)
        valid = False
        if len(raw) <= limit:
            try:
                document = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique)
                valid = validator.is_valid(document) and document["operation"] == "validate"
            except (ValueError, RecursionError):
                pass
        print(json.dumps({"status": "valid" if valid else "invalid"}))
        return

    matrix = check(ROOT)
    directories = sorted((ROOT / "suite" / "wire").iterdir())
    wire_ids = {directory.name for directory in directories}
    expected_cases = {
        case: status
        for entry in matrix.values()
        for role, status in (("positive", "valid"), ("negative", "invalid"))
        for case in entry[role]
        if case in wire_ids
    }
    for directory in directories:
        expected = read(directory / "expected.json")["status"]
        observed = "valid" if validator.is_valid(read(directory / "input.json")) else "invalid"
        if expected_cases[directory.name] != expected or observed != expected:
            raise SystemExit(f"wire case disagrees with schema or registry: {directory.name}")
    print(json.dumps({"requirements": len(matrix), "wire_cases": len(expected_cases)}))
    response = _validator("response")
    verification = _validator("verification-request")
    rdf_verification = _validator("rdf-verification-request")
    rdf_profile = rdf_verification.schema["properties"]["profile"]["const"]
    for name in ("assessment", "receiver"):
        for directory in sorted((ROOT / "suite" / name).iterdir()):
            document = read(directory / "input.json")
            if name == "assessment":
                input_validator = validator
            else:
                input_validator = (
                    rdf_verification if document["profile"] == rdf_profile else verification
                )
            input_validator.validate(document)
            response.validate(read(directory / "expected.json"))


if __name__ == "__main__":
    main()
