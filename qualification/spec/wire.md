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

## RDF result projection

The [fixed JSON-LD context](../context/result.jsonld) projects an assessed
result into RDF. Type the root as `qual:Result` and each finding as
`earl:TestResult`. Use `{"@id":"qual:Null"}` at explicit null positions so
the RDF projection preserves absence of a value. Lists retain their wire
order. Exact pins have an IRI subject and a digest literal. EARL outcomes
retain their standard identifiers.

The [result shape](../shapes/result.ttl) tests structural carriage, including
the presence of exact binding fields, findings and reserved resolving-set
fields. Receivers select exactly one typed result before applying the shape.
The receiving evaluator derives findings from policy and raw
observations independently of this projection. These shapes describe the draft result surface.

## Fixed RDF receiving frame

For the [RDF verification envelope](../schema/rdf-verification-request.schema.json),
the request carries an evidence projection in its `evidence` field, and the
envelope's result carries the result projection. The evidence projection uses
the [evidence context](../context/evidence.jsonld) and root type
`qual:Evidence`. Type each report as `qual:Observation`. Report attribution
has the PROV-O `wasAttributedTo` predicate. Arrays and the explicit null
marker follow the result projection convention.

Select one correctly framed root for each document. The receiver compares
the contexts to its installed specification, checks types of the root and
list members, and only then reconstructs the raw fields. Nested JSON-LD
directives are refused. The exact report digests bind the reconstructed
plain JSON reports. The received result supplies no premises to evaluation.

The [evidence shape](../shapes/evidence.ttl) checks the retained observation
envelope and exact pins in RDF. The installed specification's
`project("evidence", evidence)` and `project("result", result)` functions
produce the fixed frames. The process interface accepts the documented compact
JSON-LD representation of the graph.

## Identity grammar

The common schema requires an absolute [RFC 3987](https://www.rfc-editor.org/rfc/rfc3987.html)
subset. It allows an ASCII scheme with a nonempty rootless path, an absolute
path that does not begin with two slashes, or a registered-name authority
with optional user information and numeric port. Paths, query and fragment
use unreserved and sub-delimiter characters, exact percent escapes and the
permitted Unicode ranges. Compare identifiers as supplied, including case
and encoding. Input offsets use valid signed hours and minutes. Assessment
also checks that the date denotes a representable UTC instant.
