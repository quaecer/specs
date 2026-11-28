# Qualification interchange draft

An implementation receives a JSON request on standard input and returns one
JSON response on standard output. No retrieval is needed to interpret the
request. Reports are supplied by value. A revision pin pairs a linked
record's identifier and digest.

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
model and transfer premises. The executable assessment cases are a separate
slice.

## Result representation

The [response schema](../schema/response.schema.json) accepts the validation
statuses or a [structured assessment](../schema/result.schema.json). An
evaluated criterion carries support, opposition, both or neither. The
sceptical projection maps them to passed, failed, cannot tell and cannot
tell respectively. Execution can separately mark a criterion inapplicable
or untested. The [reason registry](../registry/reasons.json) fixes the draft
labels used to describe the basis.

A positive qualification requires an exact compatible clock result,
consistent accepted evidence, at least one passed criterion, and passed
outcomes on every applicable criterion. A definite failed criterion gives
a failed qualification even when timing or consistency is unresolved.
The result always carries `authorization: not_granted`.

Coverage has separate window and history compositions. Each retains
covered regions, gaps, defeated regions and the involved commitments.
Dependence has a dimension, exact comparison, relation and retained
basis. Transfer records bind criterion and source policy digests.
The resolving-set field is reserved with status `not_run`.

An extension use is representable in a policy with the same identifier
grammar as the registry. Assessment additionally checks that the bound
registry declares the use. Structural validation alone checks its shape.
