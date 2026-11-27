# SPDX-License-Identifier: Apache-2.0
"""Emit fixed JSON-LD frames for already checked qualification documents."""

from typing import Any, Literal

from .assets import context

_TYPES = {
    "evidence": ("qual:Evidence", "reports", "qual:Observation"),
    "result": ("qual:Result", "findings", "earl:TestResult"),
}


def _with_nulls(value: Any) -> Any:
    if value is None:
        return {"@id": "qual:Null"}
    if isinstance(value, list):
        return [_with_nulls(item) for item in value]
    if isinstance(value, dict):
        if any(key.startswith("@") for key in value):
            raise ValueError("input must contain plain JSON fields")
        return {key: _with_nulls(item) for key, item in value.items()}
    return value


def project(kind: Literal["evidence", "result"], document: dict[str, Any]) -> dict[str, Any]:
    """Project a validated document while preserving ordered lists and nulls."""
    root, members, member_type = _TYPES[kind]
    output: dict[str, Any] = _with_nulls(document)
    output[members] = [dict(item, **{"@type": member_type}) for item in output[members]]
    output.update(context(kind))
    output["@type"] = root
    return output
