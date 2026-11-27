# Formal semantics

The [coverage](coverage.md), [clock](clock.md) and [transfer](transfer.md)
contracts define the wire rules.

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

### Transfer conformance cases

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
map `τ` is nondecreasing and satisfies `|τ(r) − r| ≤ δ` on the
specified nominal scope of each bound. The same clock
identity shares one map across channels, issuers and committed units. Policy
windows and authoritative event bounds are true time. A nominal interval
`[a,b)` denotes `[τ(a),τ(b))`. Equality of mapped endpoints is allowed.

A finite set of clock readings is sufficient for compatibility. Restrict an
admissible map to the mentioned readings to obtain ordered values inside the
error bands. Include the endpoints of every scoped accuracy declaration.
Conversely, linearly interpolate ordered values between adjacent readings.
Every band covering one such segment covers both endpoints, so their
offsets interpolate inside that band. Extend outside the outer readings
by the constant offset at each outer endpoint. The construction preserves
the scoped bounds, shared readings and monotonicity.

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

## Coverage, defeat and witnesses

Write `P⁺(x)` for the positive timing formula of a view. It contains resolved
identity equalities, authoritative event bounds, typed inventory brackets,
clock order and declared accuracy bands. Typed entries and accuracy bands
can contribute from incomplete, disabled or unknown captures. A positive
timing premise supplies no completeness on its own.

A committed unit `u` is an unsegmented statement or one committed segment.
It has clock `kᵤ`, nominal interval `[aᵤ,bᵤ)`, error bound `δᵤ`, channels and
inventory `Eᵤ`. A unit is eligible if it is selected, complete, has the declared
identity scheme, has a resolved inventory and satisfies `δᵤ ≤ m` for fixed
policy margin `m`. Its true-time image is
`Iᵤ(τ) = [τₖᵤ(aᵤ), τₖᵤ(bᵤ))`.

### Omission and violation

For a selected occurrence `e` on channel `c`, consider eligible units on
`c` that omit `e`, can meet its time envelope, and certify its distinctness
from every resolved inventory entry. Eligibility and distinctness use the
bound occurrence identities. For each candidate unit, completeness asserts
the omission clause `O(e,u) ≡ tₑ < τₖᵤ(aᵤ) or τₖᵤ(bᵤ) ≤ tₑ`.
Let `P(x)` be `P⁺(x)` conjoined with all such clauses.

- `W(e,u)` is the singleton omission witness. `W*(e,K)` is the joint witness
  for a nonempty set `K` of candidates for one occurrence with a resolved,
  finite envelope. It requires satisfiable `P⁺(x)` and unsatisfiable
  `P⁺(x) ∧ ∧{O(e,u) | u ∈ K}`. Thus every positive timing world places
  the occurrence in at least one candidate's true image. Positive calibration
  may establish this fact even when error-band erosion alone cannot.
  The witness names the occurrence and the committed units. Incompatibility
  of `P(x)` can also have a global explanation across occurrences, with no
  bounded single-occurrence witness.
- `V(e)` witnesses a violation when the occurrence's resource and channel
  match policy and a satisfiable `P⁺(x)` forces `tₑ ∈ H`, where
  `H = [history_scope.start, lock_at)`. Equivalently, the query with
  `tₑ < start or lock_at ≤ tₑ` is unsatisfiable. An independently
  sufficient direct observation with its entire closed range inside `H`
  remains a witness if other timing premises conflict. Thus the upper
  endpoint must be strictly before the lock. Omission clauses play no
  part in deriving `V`.

Each member of a witnessed `K` is defeated over its committed unit on the
occurrence's channel. A selected, matched capture challenge or the same
observer's incomplete or disabled status also defeats a unit if `P⁺(x)`
forces nonempty overlap. A possible overlap supplies no defeat. The policy
can widen the defeated set to the containing statement, the observer's
complete units on the same channel, or all complete units of that observer.
Another observer's partial capture contributes no opposition to the
commitment. Compute violations and consistency independently of one another.

### Coverage composition

For channel `c` keep eligible, undefeated units on that channel. Within a
clock family, form the nominal union of units at each admitted accuracy
bound `d` using units with `δᵤ ≤ d`. For each connected component `[a,b)`
of this union use the nonempty interval `[a + max(d,m), b − max(d,m))`.
Union these intervals across the layers and clocks to obtain `C(c,x)`.
For a required interval `R`, covered regions are `C(c,x) ∩ R` and gaps are
`R \ C(c,x)`. The possible regions of defeated units are reported separately
and may overlap surviving coverage.

Window coverage checks its named channel over the fixed policy window.
Absence checks all policy channels over `H` and requires a nonempty set of
forbidden pins. Positive temporal findings require compatible timing,
no capture inconsistency and no relevant gaps. For absence, the full
compatible formula must also exclude membership in `H` for each
possibly forbidden listed occurrence. A possible in-range occurrence
or an unresolved query cannot establish absence.

### P2. Sound downgrade under removal

Keep policy, use, required criteria, clock model and exact bindings fixed.
Order views by removal of accepted premises, including selected reports
and caller-supplied bytes. A retained typed entry stays a premise when its
separate exposure body is removed. Use a consistent starting view and
assume resolved derivations respect restriction. In particular a retained
inventory and its resolved identities retain their meaning, and a lost
alias or body can make a premise unresolved. For a reduced view, definite
criterion findings and qualification can stay the same or weaken to
unresolved. Removal cannot introduce a new contradiction from a
consistent view. This concerns findings, qualification and consistency.
Execution diagnostics, reasons and provenance can change.

**Proof sketch.** Encode support and opposition as bits ordered by subset
of the supported polarities. A scalar derivation uses witnesses for a
fixed obligation, so its witnesses in the reduced view also exist in the
original. Resolved timing constraints under removal restrict the available
premises, so each original compatible world satisfies the surviving ones
under the same clock and identity interpretation. Thus a forced violation,
omission or overlap derived from surviving premises is also forced in the
original. This preserves violation opposition. A certain omission or
opposing capture overlap would contradict the consistent-start premise.
The set of eligible supporting units can only shrink. Within each fixed
accuracy layer, restoring eligible units preserves or enlarges their
joined, eroded regions. A reduced absence support excludes violations in
its compatible worlds by P3. It therefore excludes them in the original
worlds as well. These arguments compare completed, sound derivations
under restriction. Exact wire binding and premise resolution are needed
for the implementations to refine this argument.

A consistent finding contains at most one polarity. Its only strict
downgrade loses that polarity. The gate stays failed while a decisive
opposition survives. It stays passed while all applicable obligations
pass and consistency is established. Otherwise a definite gate weakens
to unresolved. The consistent-start premise matters. Removing a
witnessed omission or the opposing half of conflicting scalar evidence
can restore a definite finding from an inconsistent original.

### P3. Coverage soundness relative to commitments

Assume the accepted timing formula has a compatible world, clock identity
and bounds are truthful, and eligible inventories faithfully and completely
describe occurrences in their committed true-time captures. In every
compatible world, a covered region lies in the union of eligible,
undefeated captures on its channel. An absence pass entails no occurrence
with a forbidden pin on a required channel in `H` in any such world.

**Proof sketch.** On a shared clock, monotonicity and equal mapped
boundaries map a connected nominal union to `[τₖ(a),τₖ(b))`.
Its endpoints obey the layer's common error bound `d`. The eroded
component is therefore inside that union in every compatible assignment.
Union across clocks and clipping preserve containment. If a forbidden
occurrence fell in covered history, some eligible unit on that channel
would have to list it. A fresh, unlisted occurrence violates completeness,
and a listed one would satisfy a forbidden membership query that the
absence rule requires to be unsatisfiable. Both contradict the pass
premises. The compatible-world premise excludes vacuous success on an
inconsistent formula. This entailment is conditional on the accepted
commitments and clock model.
