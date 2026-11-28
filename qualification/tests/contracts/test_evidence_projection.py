# SPDX-License-Identifier: Apache-2.0
"""Check raw graph carriage and attribution (QUAL-REQ-020)."""

import json
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace, URIRef

from quaecer.spec_qualification import project, shape

ROOT = Path(__file__).resolve().parents[2]


def test_projected_evidence_requires_attribution_and_exact_pins() -> None:
    raw = json.loads((ROOT / "suite/assessment/QUAL-TC-0030/input.json").read_bytes())["evidence"]
    fixture = json.loads((ROOT / "suite/receiver/QUAL-TC-0032/input.json").read_bytes())
    projection = project("evidence", raw)
    assert projection == fixture["request"]["evidence"]
    graph = Graph().parse(data=json.dumps(projection), format="json-ld")
    rules = Graph().parse(data=shape("evidence"), format="turtle")
    ok, _, report = validate(graph, shacl_graph=rules)
    assert ok, report

    prov = Namespace("http://www.w3.org/ns/prov#")
    observation = URIRef(raw["reports"][0]["id"])
    assert graph.value(observation, prov.wasAttributedTo) == URIRef(
        raw["reports"][0]["issuer"]["id"]
    )
    graph.remove((observation, prov.wasAttributedTo, None))
    ok, _, _ = validate(graph, shacl_graph=rules)
    assert not ok


def test_result_projection_preserves_explicit_nulls() -> None:
    result = json.loads((ROOT / "suite/assessment/QUAL-TC-0030/expected.json").read_bytes())
    fixture = json.loads((ROOT / "suite/receiver/QUAL-TC-0032/input.json").read_bytes())
    assert project("result", result) == fixture["result"]
    assert result["resolving_sets"]["search_bound_reached"] is None


def test_joint_omission_witness_survives_rdf_projection() -> None:
    result = json.loads((ROOT / "suite/assessment/QUAL-TC-0042/expected.json").read_bytes())
    fixture = json.loads((ROOT / "suite/receiver/QUAL-TC-0050/input.json").read_bytes())
    projection = project("result", result)
    assert projection == fixture["result"]
    graph = Graph().parse(data=json.dumps(projection), format="json-ld")
    rules = Graph().parse(data=shape("result"), format="turtle")
    ok, _, report = validate(graph, shacl_graph=rules)
    assert ok, report

    qual = Namespace("https://quaecer.github.io/specs/qualification/1.0/terms/")
    assert len(set(graph.subjects(qual["lower"]))) == 2
    graph.remove((None, qual.unit, None))
    ok, _, _ = validate(graph, shacl_graph=rules)
    assert not ok
