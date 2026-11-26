# SPDX-License-Identifier: Apache-2.0
"""Validate a use registry and compute its declared order."""

import argparse
import json
import re
from graphlib import CycleError, TopologicalSorter
from pathlib import Path

_FIELDS = {
    "format": "qualification-use-registry@1",
    "closure": "reflexive_transitive",
    "instance_relation": "canonical_semantic_equality",
}
_USE = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    fields = dict(pairs)
    if len(fields) != len(pairs):
        raise ValueError("duplicate JSON member")
    return fields


def use_order(raw: bytes) -> frozenset[tuple[str, str]]:
    """Return the reflexive, transitive order as `(target, source)` pairs.

    Read UTF-8 bytes. Raise ValueError for an invalid registry or cyclic graph.
    Each returned pair permits a transfer attempt under the declared order.

    >>> example = (
    ...     b'{"format":"qualification-use-registry@1","uses":["review"],'
    ...     b'"edges":[],"closure":"reflexive_transitive",'
    ...     b'"instance_relation":"canonical_semantic_equality"}'
    ... )
    >>> sorted(use_order(example))
    [('review', 'review')]
    """
    parsed = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(parsed, dict) or parsed.keys() != _FIELDS.keys() | {"uses", "edges"}:
        raise ValueError("invalid registry members")
    for field, value in _FIELDS.items():
        if parsed[field] != value:
            raise ValueError(f"invalid {field}")

    uses: set[str] = set()
    if not isinstance(parsed["uses"], list) or not parsed["uses"]:
        raise ValueError("uses must be a nonempty array")
    for use in parsed["uses"]:
        if not isinstance(use, str) or not _USE.fullmatch(use):
            raise ValueError("invalid use identifier")
        if use in uses:
            raise ValueError("duplicate use identifier")
        uses.add(use)

    sources: dict[str, set[str]] = {use: set() for use in uses}
    if not isinstance(parsed["edges"], list):
        raise ValueError("edges must be an array")
    for edge in parsed["edges"]:
        if not isinstance(edge, dict) or edge.keys() != {"target", "source"}:
            raise ValueError("invalid edge members")
        target, source = edge["target"], edge["source"]
        if not isinstance(target, str) or not isinstance(source, str):
            raise ValueError("edge identifiers must be strings")
        if target not in uses or source not in uses:
            raise ValueError("edge refers to an undeclared use")
        if target == source:
            raise ValueError("reflexive edges are implicit")
        if source in sources[target]:
            raise ValueError("duplicate edge")
        sources[target].add(source)

    try:
        ordered = tuple(TopologicalSorter(sources).static_order())
    except CycleError as error:
        raise ValueError("cyclic use order") from error

    closure: dict[str, set[str]] = {}
    for target in ordered:
        reachable = {target}
        for source in sources[target]:
            reachable.update(closure[source])
        closure[target] = reachable
    return frozenset(
        (target, source) for target, reachable in closure.items() for source in reachable
    )


def main() -> None:
    """Validate a registry file and show the order in sorted JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    args = parser.parse_args()
    try:
        order = use_order(args.registry.read_bytes())
    except (OSError, ValueError) as error:
        parser.exit(1, f"invalid use registry: {error}\n")
    print(json.dumps([{"target": target, "source": source} for target, source in sorted(order)]))


if __name__ == "__main__":
    main()
