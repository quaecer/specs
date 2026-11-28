# SPDX-License-Identifier: Apache-2.0
"""Read version-matched assets from an installed specification distribution."""

import json
import re
from importlib.metadata import distribution
from pathlib import Path

_NAME = re.compile(r"[a-z][a-z0-9-]*")


def _asset(kind: str, filename: str) -> Path:
    relative = f"quaecer/spec_qualification/_assets/{kind}/{filename}"
    return Path(str(distribution("quaecer-spec-qualification").locate_file(relative)))


def _name(name: str) -> str:
    if not _NAME.fullmatch(name):
        raise ValueError("invalid asset name")
    return name


def _object(path: Path) -> dict[str, object]:
    value: object = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("resource must be a JSON object")
    return value


def schema(name: str) -> dict[str, object]:
    """Read a named JSON Schema resource from the installed distribution.

    >>> schema("request")["type"]
    'object'
    """
    return _object(_asset("schema", _name(name) + ".schema.json"))


def registry(name: str) -> object:
    """Read a named JSON registry resource from the installed distribution."""
    return json.loads(_asset("registry", _name(name) + ".json").read_bytes())


def context(name: str) -> dict[str, object]:
    """Read a named local JSON-LD context."""
    return _object(_asset("context", _name(name) + ".jsonld"))


def shape(name: str) -> str:
    """Read a named SHACL shape in Turtle syntax."""
    return _asset("shapes", _name(name) + ".ttl").read_text(encoding="utf-8")


def suite_path(name: str) -> Path:
    """Return the directory of a named suite shipped with the specification."""
    path = _asset("suite", _name(name))
    if not path.is_dir():
        raise FileNotFoundError(path)
    return path
