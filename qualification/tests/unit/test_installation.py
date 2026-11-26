# SPDX-License-Identifier: Apache-2.0
"""Smoke test the installed namespace and distribution metadata."""

import importlib
import unittest
from importlib.metadata import version


class InstallationTest(unittest.TestCase):
    def test_import_and_distribution_metadata(self) -> None:
        module = importlib.import_module("quaecer.spec_qualification")
        self.assertEqual(module.__name__, "quaecer.spec_qualification")
        self.assertTrue(version("quaecer-spec-qualification").startswith("1.0.0"))

    def test_assets_match_the_source_checkout(self) -> None:
        import json
        from pathlib import Path

        from quaecer.spec_qualification import registry, schema, suite_path

        root = Path(__file__).resolve().parents[2]
        self.assertEqual(
            schema("request"), json.loads((root / "schema/request.schema.json").read_bytes())
        )
        self.assertEqual(registry("uses"), json.loads((root / "registry/uses.json").read_bytes()))
        case = "QUAL-TC-0001/input.json"
        self.assertEqual(
            (suite_path("wire") / case).read_bytes(),
            (root / "suite/wire" / case).read_bytes(),
        )
        with self.assertRaises(ValueError):
            schema("../policy")
