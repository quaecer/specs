# SPDX-License-Identifier: Apache-2.0
"""Check that the wire cannot present unresolved evidence as a satisfied gate."""

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://quaecer.github.io/specs/qualification/1.0/"


def _validator(name):
    schemas = [
        json.loads(path.read_bytes()) for path in sorted((ROOT / "schema").glob("*.schema.json"))
    ]
    resources = Registry().with_resources(
        (document["$id"], Resource.from_contents(document)) for document in schemas
    )
    return Draft202012Validator(
        resources.contents(BASE + name + ".schema.json"), registry=resources
    )


def _result():
    request = json.loads((ROOT / "suite/wire/QUAL-TC-0001/input.json").read_bytes())
    caller = request["caller"]
    fact = {
        "criterion": "capture",
        "execution": "evaluated",
        "value": "support",
        "outcome": "passed",
        "reasons": [],
        "basis": caller["report_pins"],
    }
    return {
        "profile": BASE + "result",
        "policy_digest": caller["policy_digest"],
        "use_registry_digest": caller["use_registry_digest"],
        "view_digest": "sha256:" + "a" * 64,
        "use": caller["use"],
        "subject": caller["subject"],
        "implementation": caller["implementation"],
        "clock_compatibility": "compatible",
        "consistency": "consistent",
        "qualification": "prerequisites_satisfied",
        "authorization": "not_granted",
        "findings": [fact],
        "coverage": [],
        "dependence": [],
        "inconsistencies": [],
        "transfers": [],
        "resolving_sets": {"status": "not_run", "sets": [], "search_bound_reached": None},
    }


def test_all_five_outcomes_have_exact_four_valued_bindings():
    validator = _validator("response")
    for state, value, outcome, gate in (
        ("evaluated", "support", "passed", "prerequisites_satisfied"),
        ("evaluated", "opposition", "failed", "prerequisites_failed"),
        ("evaluated", "both", "cantTell", "prerequisites_unresolved"),
        ("evaluated", "neither", "cantTell", "prerequisites_unresolved"),
        ("not_run", "neither", "untested", "prerequisites_unresolved"),
        ("not_applicable", "neither", "inapplicable", "prerequisites_unresolved"),
    ):
        record = _result()
        record["findings"][0].update(execution=state, value=value, outcome=outcome)
        record["qualification"] = gate
        validator.validate(record)
        bad = copy.deepcopy(record)
        bad["findings"][0]["value"] = "opposition" if value == "support" else "support"
        assert not validator.is_valid(bad)


def test_positive_gate_needs_compatible_clocks_and_unconflicted_support():
    validator = _validator("result")
    result = _result()
    validator.validate(result)
    for changes in (
        {"clock_compatibility": "unresolved"},
        {"clock_compatibility": "incompatible", "consistency": "inconsistent"},
        {"authorization": "granted"},
    ):
        assert not validator.is_valid(dict(result, **changes))
    failed = copy.deepcopy(result)
    failed["findings"][0].update(outcome="failed", value="opposition")
    assert not validator.is_valid(failed)
    failed.update(
        clock_compatibility="incompatible",
        consistency="inconsistent",
        qualification="prerequisites_failed",
    )
    validator.validate(failed)


def test_reason_codes_match_the_registry():
    schema = _validator("result").schema
    registry = json.loads((ROOT / "registry/reasons.json").read_bytes())
    assert set(schema["$defs"]["reason"]["properties"]["code"]["enum"]) == registry["codes"].keys()


def test_extension_use_is_representable():
    request = json.loads((ROOT / "suite/wire/QUAL-TC-0001/input.json").read_bytes())
    request["use_registry"]["uses"].append("independent_review")
    request["policy"]["use"]["kind"] = "independent_review"
    request["policy"]["rules"][0]["uses"] = ["independent_review"]
    _validator("request").validate(request)


def test_result_rdf_preserves_required_fields_and_ordered_outcomes():
    from pyshacl import validate
    from rdflib import RDF, Graph, Namespace
    from rdflib.collection import Collection

    qual = Namespace(BASE + "terms/")
    earl = Namespace("http://www.w3.org/ns/earl#")
    context = json.loads((ROOT / "context/result.jsonld").read_bytes())
    result = _result()
    result["qualification"] = "prerequisites_unresolved"
    result["findings"].append(
        {
            "criterion": "quality",
            "execution": "not_run",
            "value": "neither",
            "outcome": "untested",
            "reasons": [],
            "basis": [],
        }
    )
    _validator("result").validate(result)
    for finding in result["findings"]:
        finding["@type"] = "earl:TestResult"
    result["resolving_sets"]["search_bound_reached"] = {"@id": str(qual.Null)}
    graph = Graph().parse(
        data=json.dumps({**context, "@type": "qual:Result", **result}),
        format="json-ld",
    )
    shapes = Graph().parse(ROOT / "shapes/result.ttl", format="turtle")
    conforms, _, report = validate(graph, shacl_graph=shapes)
    assert conforms, report
    root = graph.value(predicate=RDF.type, object=qual.Result)
    findings = graph.value(root, qual.findings)
    assert [graph.value(node, earl.outcome) for node in Collection(graph, findings)] == [
        earl.passed,
        earl.untested,
    ]
    graph.remove((root, qual.view_digest, None))
    conforms, _, _ = validate(graph, shacl_graph=shapes)
    assert not conforms
