# SPDX-License-Identifier: Apache-2.0
"""Check requirement-to-case links and emit a deterministic coverage matrix."""

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
_REQUIREMENT = re.compile(r"QUAL-REQ-[0-9]{3}")
_CASE = re.compile(r"QUAL-TC-[0-9]{4}")
_HEADING = re.compile(r"^## (QUAL-REQ-[0-9]{3})\b", re.MULTILINE)


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON member")
    return result


def read(path: Path) -> Any:
    """Read UTF-8 JSON and reject duplicated members."""
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique)


def check(root: Path) -> dict[str, dict[str, list[str]]]:
    """Require symmetric links, exact clauses and cases of both polarities."""
    cases: dict[str, set[str]] = {}
    for metadata in sorted((root / "suite").rglob("case.json")):
        identifier = metadata.parent.name
        definition = read(metadata)
        if not _CASE.fullmatch(identifier) or identifier in cases or definition["id"] != identifier:
            raise ValueError(f"invalid or repeated case identity: {identifier}")
        links = definition["requirements"]
        if not links or len(set(links)) != len(links):
            raise ValueError(f"invalid requirement links: {identifier}")
        read(metadata.with_name("input.json"))
        read(metadata.with_name("expected.json"))
        cases[identifier] = set(links)

    definitions = read(root / "registry" / "requirements.json")
    sections: dict[str, str] = {}
    for document in sorted((root / "spec").glob("*.md")):
        content = document.read_text(encoding="utf-8")
        for identifier in _HEADING.findall(content):
            if identifier in sections:
                raise ValueError(f"duplicate normative heading: {identifier}")
            sections[identifier] = document.relative_to(root).as_posix()

    matrix: dict[str, dict[str, list[str]]] = {}
    linked: dict[str, set[str]] = {}
    for requirement in definitions:
        identifier = requirement["id"]
        if not _REQUIREMENT.fullmatch(identifier) or identifier in matrix:
            raise ValueError(f"invalid or repeated requirement identity: {identifier}")
        section = sections.get(identifier)
        if section is None or requirement["section"] != f"{section}#{identifier.lower()}":
            raise ValueError(f"unresolved normative section: {identifier}")
        content = (root / section).read_text(encoding="utf-8")
        clause = re.search(
            rf"^## {identifier}\b[^\n]*\n\n([^\n]+)",
            content,
            re.MULTILINE,
        )
        if clause is None or clause.group(1) != requirement["text"]:
            raise ValueError(f"normative text differs from registry: {identifier}")
        if any(
            not re.fullmatch(r"[0-9]+\.[0-9]+", requirement[key])
            for key in ("introduced_in", "modified_in")
        ):
            raise ValueError(f"invalid requirement version: {identifier}")

        polarity: dict[str, list[str]] = {"positive": [], "negative": []}
        seen: set[str] = set()
        for link in requirement["cases"]:
            case, role = link["id"], link["polarity"]
            if role not in polarity or case not in cases or case in seen:
                raise ValueError(f"invalid case link: {identifier} {case}")
            polarity[role].append(case)
            seen.add(case)
            linked.setdefault(case, set()).add(identifier)
        if not all(polarity.values()):
            raise ValueError(f"both polarities require cases: {identifier}")
        matrix[identifier] = {role: sorted(ids) for role, ids in polarity.items()}

    if not matrix or set(matrix) != sections.keys() or linked != cases:
        raise ValueError("case, registry and normative section links differ")
    return matrix


if __name__ == "__main__":
    try:
        print(json.dumps(check(ROOT), sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"traceability: {error}") from None
