# Scalar assessment and exact input binding

A request is first checked against the versioned wire schema. An operational
refusal produces `{"status":"invalid"}` and carries no assessment result.
The assessment is offline. Raw evidence and caller selections are explicit
inputs. A caller pin establishes the selected bytes for this decision.

## Accepted view

Resolve identifiers by exact string equality. Reference, report and selection
arrays define maps with distinct identifiers. A report identifier cannot also
name an external reference. Every revision pin appearing in the policy,
evidence or artifact selection resolves to its exact pair in the evidence's
reference inventory. Report pins resolve against the reports themselves.

Compare the requested use with the policy use identifier. Compare subject and
implementation pins across the policy, evidence and caller, and the claim
between policy and evidence. Compare the caller's expected policy and registry
digests with the canonical input values. The policy and evidence bindings must
agree with those values. The use and every rule applicability label must be
declared by the acyclic registry. At least one uniquely named rule must apply.

A selected report is accepted only when its full canonical digest matches its
caller pin, its referenced revisions resolve, and its subject and implementation
match the policy. An unselected report can explain an unresolved result, but
supplies no support, opposition or timing constraint. A selected missing or
changed report is an operational refusal.

The result's `view_digest` hashes an object with the following keys. Sort the
three arrays by their pin identifier before hashing.

| Key | Value |
| --- | --- |
| `claim`, `subject`, `implementation` | Exact pins from the accepted view |
| `use_registry_digest` | Digest of the supplied registry |
| `references` | All external revision pins from the evidence inventory |
| `reports` | Accepted exact report pins |
| `bodies` | Objects with `artifact` and `bytes_base64`, from the caller |

The body strings use canonical padded Base64. Hash the decoded bytes for the
body rule. Digesting the view binds the exact assessed inputs independently of
the policy's use identifier, which remains separately bound by the policy
digest. JSON input permits integer literals in the interoperable range. Decimal points
and exponents belong in the declared control strings. Use
decimal strings for controls. Reject duplicate members and invalid Unicode.

## Scalar predicates

A report matches the operator and its exact selector. Check and control use
the criterion key. Dependence uses the dimension and unordered comparison of
two exact pins. Run and body use exact run and artifact pins. Selection uses
the rule's fixed item set. Distinctness of identifiers alone gives no
dependence finding.

| Operator | Support | Opposition | Unresolved observation |
| --- | --- | --- | --- |
| `check` | Ran with `pass` | Ran with `fail` | Ran with `unknown` |
| `control` | Matching unit and distance at most tolerance | Matching unit and distance greater than tolerance | Different unit |
| `dependence` | Known relation matches the requirement, or any known relation when required is `known` | Known relation differs from the requirement | `unknown` relation |
| `run_status` | `succeeded` | `failed` or `interrupted` | `unknown` status |
| `body` | Supplied bytes match both size and digest | Supplied bytes differ in size or digest | Missing bytes |
| `selection` | Every required item has positive support and none is contested | An item is omitted without a positive report for that item | At least one item's inclusion is uncovered |

Tolerances are nonnegative and decimal comparison is exact. An accepted
observation explicitly marked `not_run` gives the `untested` execution
status when the criterion has unrun evidence and no accepted run or known
value. An accepted run without a decisive observation gives an evaluated
unknown. For other scalar rows, compatible report contributions accumulate.
Opposing definite contributions yield `both`. Conflicting reported relations
on a dependence dimension yield `both` even for the `known` predicate.
An omitted and included selection item is contested. Report this inconsistency
even when a different, definitively omitted item determines a failed result.
Without a definitively omitted item, a contested selection evaluates to
`both`.

A finding's basis is the union of accepted matching report pins and their
explicit supporting revision pins. Sort the pins by identifier. Unselected
reports can appear in a `report_not_accepted` reason for an untested or
unresolved criterion. A conflict reason identifies all contributing
opposing reports and the criterion, and is also carried in the result's
inconsistency list. A missing body identifies its artifact. An unresolved
scalar without another reason uses `unavailable_report` with its criterion.
An inapplicable criterion has an empty basis and reasons.

Sort findings by criterion identifier and dependence rows by dimension.
A dependence row carries the policy comparison, the known relation (or
`unknown` when unestablished or contested), the accepted matching reports and
their basis. At most one applicable dependence comparison is permitted.
Every reason has `code`, sorted `report_ids`, sorted `related_ids`, an
explicit `channel` or null and a separate `criterion` key or null. Sort reasons and inconsistencies by their
canonical byte representations.

## Initial evaluation scope

The [exposure fragment](exposure.md) handles declared true-time bounds and
definite forbidden occurrences. Committed coverage and transfer remain
deferred. A scalar proof does not bypass unresolved clock compatibility.

The receiver can evaluate the same request from raw input. It also accepts a
verification envelope with `profile` set to
`https://quaecer.github.io/specs/qualification/1.0/verification-request`,
`request` containing the assessment request and `result` containing the
claimed result. It returns `{"status":"verified"}` on complete equality
with its independently recomputed result and `{"status":"mismatch"}`
for a changed result. Invalid inputs produce the operational status above.
The received result supplies no premises.
