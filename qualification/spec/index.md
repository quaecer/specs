# Qualification spec 1.0-draft

The specification defines when recorded evidence supports prerequisites for
a declared use. A prerequisite finding does not grant authorization.

The [formal draft](formal.md) defines the proposed use order, transfer
premises and exact clock compatibility reduction. The [draft use
registry](../registry/uses.json) records the built-in edges. The transfer
contract is open for review before implementation.

The [use registry schema](../schema/use-registry.schema.json) defines the
fields of a registry. Use identifiers are lowercase ASCII letters and digits
with single underscores between groups, starting with a letter. A UTF-8
document supplies each JSON member and use at most once. Every edge joins two
different declared uses, and explicit edges are unique and acyclic.
The edge object names the proposed `target` and `source` uses. The order
includes each use paired with itself and every pair connected by following
edges from target to source. Any path permits a transfer attempt subject to
the criteria and checks in the formal draft.

To check a registry and print its order, run
`uv run --locked python -m quaecer.spec_qualification.use_registry registry/uses.json`
from the qualification directory. The output lists pairs sorted by target
and then source.

The [interchange draft](wire.md) documents the evidence and policy schemas,
the validation operation and the first requirement-linked cases. Assessment
results, reason terms and their conformance cases are in development.

The [scalar assessment contract](scalar.md) specifies exact request bindings,
reduction of scalar evidence and receiving verification. Its executable
examples are in [the assessment suite](../suite/assessment).
