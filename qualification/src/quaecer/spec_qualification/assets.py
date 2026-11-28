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


def schema(name: str) -> dict[str, object]:
    """Read a named JSON Schema resource from the installed distribution.

    >>> schema("request")["type"]
    'object'
    """
    value: object = json.loads(_asset("schema", _name(name) + ".schema.json").read_bytes())
    if not isinstance(value, dict):
        raise ValueError("schema resource must be an object")
    return value


def registry(name: str) -> object:
    """Read a named JSON registry resource from the installed distribution."""
    return json.loads(_asset("registry", _name(name) + ".json").read_bytes())


def suite_path(name: str) -> Path:
    """Return the directory of a named suite shipped with the specification."""
    path = _asset("suite", _name(name))
    if not path.is_dir():
        raise FileNotFoundError(path)
    return path
