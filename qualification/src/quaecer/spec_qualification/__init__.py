# SPDX-License-Identifier: Apache-2.0
"""Versioned specifications, schemas and conformance cases."""

from .assets import context, registry, schema, shape, suite_path
from .projection import project

MAX_REQUEST_BYTES = 2 * 1024 * 1024

__all__ = ["MAX_REQUEST_BYTES", "context", "project", "registry", "schema", "shape", "suite_path"]
