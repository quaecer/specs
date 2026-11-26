# SPDX-License-Identifier: Apache-2.0
"""Run structural fixtures against the checked local schemas."""

import json

from check_traceability import ROOT, check, read
from jsonschema import Draft202012Validator
from referencing import Registry, Resource


def main() -> None:
    """Resolve all schema references from local files and check every fixture."""
    matrix = check(ROOT)
    schemas = [read(path) for path in sorted((ROOT / "schema").glob("*.schema.json"))]
    for schema in schemas:
        Draft202012Validator.check_schema(schema)
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in schemas
    )
    request = read(ROOT / "schema" / "request.schema.json")
    validator = Draft202012Validator(request, registry=registry)
    expected_cases = {
        case: status
        for entry in matrix.values()
        for role, status in (("positive", "valid"), ("negative", "invalid"))
        for case in entry[role]
    }
    for directory in sorted((ROOT / "suite" / "wire").iterdir()):
        expected = read(directory / "expected.json")["status"]
        observed = "valid" if validator.is_valid(read(directory / "input.json")) else "invalid"
        if expected_cases[directory.name] != expected or observed != expected:
            raise SystemExit(f"wire case disagrees with schema or registry: {directory.name}")
    print(json.dumps({"requirements": len(matrix), "wire_cases": len(expected_cases)}))


if __name__ == "__main__":
    main()
