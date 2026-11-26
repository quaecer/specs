# SPDX-License-Identifier: Apache-2.0
"""Check use-order direction and reject ambiguous registry inputs."""

import doctest
import json
import unittest
from pathlib import Path

from quaecer.spec_qualification import use_registry

REGISTRY = Path(__file__).resolve().parents[2] / "registry" / "uses.json"


def _registry(**fields: object) -> bytes:
    value = {
        "format": "qualification-use-registry@1",
        "uses": ["screening", "review", "audit", "rerun"],
        "edges": [],
        "closure": "reflexive_transitive",
        "instance_relation": "canonical_semantic_equality",
    }
    value.update(fields)
    return json.dumps(value).encode("utf-8")


class UseRegistryTest(unittest.TestCase):
    def test_built_in_order(self) -> None:
        expected = {
            ("computational_reanalysis", "computational_reanalysis"),
            ("computational_reanalysis", "new_empirical_anchor"),
            ("computational_reanalysis", "held_out"),
            ("computational_reanalysis", "prospective_locked"),
            ("new_empirical_anchor", "new_empirical_anchor"),
            ("held_out", "held_out"),
            ("prospective_locked", "prospective_locked"),
            ("prospective_locked", "held_out"),
        }
        self.assertEqual(use_registry.use_order(REGISTRY.read_bytes()), expected)

    def test_transitive_edge_without_an_explicit_shortcut(self) -> None:
        edges = [
            {"target": "screening", "source": "review"},
            {"target": "review", "source": "audit"},
        ]
        expected = {
            ("screening", "screening"),
            ("review", "review"),
            ("audit", "audit"),
            ("rerun", "rerun"),
            ("screening", "review"),
            ("review", "audit"),
            ("screening", "audit"),
        }
        self.assertEqual(use_registry.use_order(_registry(edges=edges)), expected)
        self.assertEqual(use_registry.use_order(_registry(edges=edges[::-1])), expected)

    def test_invalid_registry_members(self) -> None:
        cases = [
            (b"[]", "registry members"),
            (_registry(extra=None), "registry members"),
            (_registry(format="qualification-use-registry@2"), "format"),
            (_registry(closure="symmetric"), "closure"),
            (_registry(instance_relation=[]), "instance_relation"),
            (_registry(uses=[]), "nonempty array"),
            (_registry(uses=["review", "review"]), "duplicate use"),
            (_registry(uses=["review\n"]), "use identifier"),
            (_registry(uses=["révision"]), "use identifier"),
            (_registry(uses=["review__case"]), "use identifier"),
            (_registry(uses=[True]), "use identifier"),
            (_registry(edges={}), "edges must be an array"),
        ]
        for document, message in cases:
            with self.subTest(document=document), self.assertRaisesRegex(ValueError, message):
                use_registry.use_order(document)

    def test_invalid_edges(self) -> None:
        self_link = {"target": "review", "source": "review"}
        link = {"target": "review", "source": "audit"}
        cases = [
            ([{"target": "review"}], "edge members"),
            ([{"target": "review", "source": []}], "edge identifiers"),
            ([{"target": "review", "source": "unregistered"}], "undeclared use"),
            ([self_link], "reflexive edges"),
            ([link, link], "duplicate edge"),
            ([link, {"target": "audit", "source": "review"}], "cyclic use order"),
            (
                [
                    link,
                    {"target": "audit", "source": "screening"},
                    {"target": "screening", "source": "review"},
                ],
                "cyclic use order",
            ),
        ]
        for edges, message in cases:
            with self.subTest(edges=edges), self.assertRaisesRegex(ValueError, message):
                use_registry.use_order(_registry(edges=edges))

    def test_duplicate_json_members_and_invalid_utf8(self) -> None:
        for raw in (b'{"uses":[],"uses":["review"]}', b'{"edge":{"target":1,"target":2}}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "duplicate JSON member"):
                use_registry.use_order(raw)
        with self.assertRaises(UnicodeDecodeError):
            use_registry.use_order(b"\xff")

    def test_example(self) -> None:
        failures, examples = doctest.testmod(use_registry)
        self.assertEqual(failures, 0)
        self.assertGreater(examples, 0)
