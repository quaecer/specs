# Formal semantics

Draft for review.

## Use order and transfer

A use identifies the purpose for which prerequisites are assessed. The built-in
order is the reflexive and transitive closure of the following edges. The
left operand is the proposed target use and the right operand is the source.

| Target | Source |
| --- | --- |
| `computational_reanalysis` | `new_empirical_anchor` |
| `computational_reanalysis` | `held_out` |
| `computational_reanalysis` | `prospective_locked` |
| `prospective_locked` | `held_out` |

The order selects which transfer attempts are admissible. It expresses no
entailment between gates on its own. For example, a held-out assessment may
have no finding for the target lock. An extension use and its edges belong
to a versioned registry. A registry with a cycle between distinct uses is
invalid.

### Transfer premises

Let `x` select an exact subject revision, accepted reports, body bytes, clock
and identity assumptions, and the trust decisions used in deriving findings.
Let `S` and `T` be the source and target policies for the same `x`. A criterion
instance binds the predicate, normalized parameters, history and channel scope
where applicable, all evaluation semantics and their versions. Its digest is
the digest of its canonical representation. Rule IDs and human labels do not
determine instance equality. A use identifier matters to instance equality
when the predicate depends on that identifier. Applicability belongs to each
policy and is checked before transferring any result.

For the first version, the relation on criterion instances is equality of
canonical semantics. It is mechanically decidable by comparing their exact
canonical representations or verifying their digests. An edge cannot serve
as an assertion that different predicates entail one another. The proof uses
one accepted view, including the same resolving inputs for both policies.
Different trust snapshots, overlap of input subsets, or a clock claim with
unresolved compatibility cannot supply that premise.

Let `F(p,c,x)` be the sound finding about applicable criterion `c` under
policy `p` in view `x`. Findings distinguish support only, opposition only,
both, and neither. Inapplicable and untested are execution statuses. A passed
criterion requires support only, and a failed criterion requires opposition
only under the sceptical rule. A contradictory or unknown finding carries no
definite criterion through transfer.

A transfer certificate binds the source and target policy digests, the view
digest, the use-order registry digest, and each source finding and target
criterion instance. The receiver rechecks the bindings and criterion equality.
A source finding blocked by an unresolved premise, a defeat, or a violated
obligation cannot establish a target prerequisite. Neither a passed source
gate nor an aggregation of source reasons replaces a direct finding. A target
criterion without a usable source finding is assessed directly or stays
unresolved. The target recomputes its gate from all target findings. Source
authorization and its legal or institutional basis are outside this operation.

### P1. Soundness of criterion transfer

For target `t` and source `s` with `t ⪯ s`, suppose the source finding is
sound for the accepted and compatible view `x`, both criteria apply, and the
criterion instances and all bindings match. Then any transferred definite
finding is sound for the target criterion in `x`. A target prerequisite pass
requires sound passed findings for every required target criterion.

**Proof.** Equality of instances binds the same predicate and the same
admissible evidence premises. Thus an argument establishing support or
opposition for the source instance establishes the same information for the
target instance. The sceptical projection is identical for the matched pair.
The rule for the target gate checks the conjunction of its own applicable
requirements, so an omitted or unresolved target criterion gives no gate
pass. An unmatched source failure has no implication for the target. If the
exact target criterion is matched, opposition about that shared predicate
can transfer as a failed finding. No inference is made about other predicates.

### Cases to require before implementation

| Case | Expected |
| --- | --- |
| Each declared distinct-use edge, compatible common view, all instances equal | Carry the matching findings and recompute the target gate |
| Reverse edge or unrelated use | Refuse transfer |
| An edge with a changed window, role, threshold or required channel | Keep the affected target criterion unresolved until directly assessed |
| Different subject revision, evidence view, accepted policy premises or registry | Refuse transfer |
| Conflicting source support or unresolved clock compatibility | No transferred pass |
| Matched failed finding | Transfer only the definite opposition for that instance |
| An unmatched source failure | Recompute the target without treating that failure as target evidence |
| Unknown or untested source finding or an unmatched required target rule | No transferred prerequisites pass |

## Clock compatibility

For each named clock `k`, nominal reading `r`, and accuracy `δ`, an admissible
map `τ` is nondecreasing and satisfies `|τ(r) − r| ≤ δ`. The same clock
identity shares one map across channels, issuers and committed units. Policy
windows and authoritative event bounds are true time. A nominal interval
`[a,b)` denotes `[τ(a),τ(b))`. Equality of mapped endpoints is allowed.

A finite set of clock readings is sufficient for compatibility. Restrict an
admissible map to the mentioned readings to obtain ordered values inside the
error band. Conversely, linearly interpolate ordered values between adjacent
readings. Their offsets interpolate inside the closed accuracy band. Extend
outside the readings by the constant offset at each outer endpoint. The
construction preserves the bounds, shared readings and monotonicity.

Use one real variable for each distinct reading on each clock, and one for
true time of each required occurrence. UTC bounds are closed. A typed
inventory reading `[l,u]` constrains the occurrence to
`τ(l) ≤ t ≤ τ(u)`. This premise can hold even if its parent supplies no
completeness commitment. For an existing occurrence certainly distinct from
all entries in an eligible complete unit on its channel, the unit asserts
`t < τ(a)` or `τ(b) ≤ t`. This is the exact complement of membership in a
half-open interval. Optional events can be absent when checking satisfiability.
An exposure or coverage query for a fresh event adds that event and every
applicable omission constraint before testing its window membership.

A satisfying assignment extends to continuous maps by the construction above.
A continuous compatible world restricts to a satisfying assignment. Thus
compatibility of the resolved clock premises is exactly satisfiability of a
finite formula of weak and strict real difference bounds with disjunctions.
Source acceptance and occurrence resolution determine which premises enter
this formula. An unsupported translation or a timed-out check leaves
compatibility unresolved. A classified contradiction can prove incompatibility.
Finding no classified contradiction alone cannot establish compatibility.

A prerequisite pass requires the accepted clock premises to be compatible.
In particular, a contradiction can derive from positive readings across
several clocks without any completeness premise. Absence entailment over
an empty set of worlds does not produce a pass.

### Clock bounds and absence

For a committed nominal interval `[a,b)`, the certain image contains
`[a + δ,b − δ)` when nonempty. A contiguous nominal union on a shared
clock maps to a contiguous union, so merge its intervals before taking
the bound. This argument does not apply to adjacent readings on different
clocks. The bounds can establish individual conclusions. If a decision
requires exact compatibility, assess the joint constraints.

An absence test is conditional on accepted commitments, truthful clock
identity and valid declared bounds. For each possible forbidden occurrence
covered by the test, add its required class, channel and true-time window
to the compatibility formula. If the base formula is satisfiable and
every exhaustive violation alternative is unsatisfiable, no compatible
world contains that violation. An unresolved translation of an alternative
or an incomplete alternative enumeration cannot establish absence by
this argument. This deduction does not establish that a real-world clock
followed its declared bound or that an issuer's commitment was true.
