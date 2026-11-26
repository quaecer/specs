# Qualification interchange draft

An implementation receives a JSON request on standard input and returns one
JSON response on standard output. No retrieval is needed to interpret the
request. The charts and tables in the evidence are supplied by value or
through exact revision pins. A revision pin pairs an identifier and a digest.

- [Request](../schema/request.schema.json) includes the policy, use registry,
  raw evidence and caller context. The `validate` operation checks wire
  structure and replies with exactly `{"status":"valid"}` or
  `{"status":"invalid"}`. The [wire suite](../suite/wire) exercises this
  operation against the [numbered requirements](wire-requirements.md).
- [Policy](../schema/policy.schema.json) names one declared use and exact
  claim, subject, implementation and registry. It declares coverage and
  history intervals, a lock, the operator arguments and applicability.
- [Evidence](../schema/evidence.schema.json) records raw observations and
  resolving revision pins. Reported check values are premises only after
  selection against the caller's exact pins. Evidence documents carry no
  computed gate or authorization fields.

## Identity and interpretation

A digest of a JSON value uses RFC 8785 followed by SHA-256, written as
`sha256:` plus lowercase hex. A digest of an artifact body hashes its raw
bytes. Array order is retained in the digest. A policy or caller change
produces a new exact binding. A matching report pin expresses caller
acceptance for that view. Issuer authentication and independence require
separate evidence.

Wire objects contain the fields in their variants. Callers spell out arrays
and nulls. An absent or null bound does not have the value zero. Input date
strings express nominal readings where they occur in committed scopes and
entries. Policy bounds are true-time instants. Equal UTC instants can have
different input spellings and digests. The interpretation compares instants
and rejects invalid dates, unknown offsets, leap seconds and reversed or
empty half-open scopes.

## Assessment boundary

The `assess` operation additionally needs the interpretation of exact pins,
identity grouping, defeat, coverage, scalar findings and transfer.
Structural validation can check the fields, types, lexical bounds and
variant shapes. Semantic checks additionally compare actual digests,
verify inventory partitioning, resolve accepted aliases and reason about
clock compatibility. The [formal draft](formal.md) describes the temporal
model and transfer premises. The result schema and the executable
assessment cases are separate slices.
