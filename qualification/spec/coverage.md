# Committed coverage

A coverage
criterion asks about its channel over `window`. An absence criterion asks
about every policy channel over `[history_scope.start, lock_at)`, with a
nonempty set of forbidden resource pins. Both use authoritative UTC.

## Commitments

A selected completeness report commits either its own interval or a
partition of that interval into named segments. The unit is the statement
itself when unsegmented, or one segment when segmented. Segments partition
the parent after sorting by start, with shared boundaries and no overlap.
Segment identifiers are distinct from report identifiers and from other
selected segments. The inventory digest is SHA-256 over the RFC 8785
canonical JSON entry array, in the supplied order, including for an empty
array. Event identifiers within a unit are unique. Assessment refuses an
invalid partition, identifier or commitment, or more than 100 selected
units or 500 total committed entries.

An eligible unit reports `complete`, explicitly declares the occurrence
identity scheme, has a known accuracy no greater than the policy margin
and has a resolved inventory. Both declared scope kinds commit all
information uses on their named channels for the specified interval.
Other capture statuses can add clock premises. A complete unit with
unmet obligations records `statement_obligation`. References and typed
entries are interpreted by the [clock contract](clock.md).

## Clocks and composition

A scope `[a,b)` is nominal on its named clock. True time is a non-decreasing
function of readings, with absolute error at most the declared accuracy on
the unit. Equal clock identifiers share that function. These premises are
conditional on the accepted declarations. Exposure intervals already give
closed true-time bounds.

Eligible units have declared accuracy at most the policy margin. Merge
their overlapping and adjacent nominal intervals on the same clock,
then erode each merged interval by the margin at both ends. Union these
intervals across clocks after erosion. Distinct clocks have no shared
boundary. Erosion discards empty ranges.

Compatibility uses the complete accepted clock formula. Region composition
uses the guaranteed intervals under the declared policy margin.

## Defeat and output

Omissions and challenges follow the [exact clock contract](clock.md).
A bounded omission can require several units. Defeat removes each
witnessed candidate unit on its channel. Policy may widen defeat to the
entire statement, the observer's complete commitments on that channel,
or all complete commitments by that observer. Another observer's unknown
or partial capture contributes no opposition.

For each policy channel, compose separate window and history results from
undefeated units. Clip regions to the requested interval, carry their unit
identifiers and emit the uncovered complement as gaps. List defeated
units' possible regions separately, so those regions can overlap with
support from a surviving unit. When no completeness report is selected,
the result has an empty coverage list.

Each `supports` row describes one same-clock contribution prior to
cross-clock union. It retains its merged nominal `lower` and `upper`
bounds, `clock_id`, maximum declared `accuracy_us`, actual `erosion_us`,
and lexically sorted distinct `observers` and `unit_ids`. The row's
`interval` is the guaranteed contribution clipped to the required
interval. Per-unit uncertainties and exact report pins resolve through
`capture_accuracy` records in the result's `clock_constraints`. The
union of the support intervals is exactly `covered`. Calibration can
affect compatibility and defeat. It cannot widen these support intervals
past the policy-margin calculation.

The compositions retain accepted statement pins, structured reasons and
`joint_omissions`. Each omission records the event's closed range, its
accepted occurrence report IDs, the resolved `occurrence`, the
`clock_constraints_digest`, the candidate unit IDs, the policy defeat
scope and the affected unit/channel pairs. Witnesses for a channel appear
in both compositions even when their effect lies outside one requested
interval. Statement pins and unit/report identifiers sort lexically.
Reasons and witnesses sort by canonical JSON.

Coverage support requires compatible timing, no capture inconsistency and
no gaps for the relevant interval and channels. A definite forbidden
exposure gives opposition independently, even when one of the commitments
is defeated. Unresolved temporal criteria carry `clock_unresolved` if
compatibility is unproved, otherwise `coverage_gap` for an unmet coverage prerequisite or
`possible_exposure` for a possible forbidden occurrence in covered history.

See [the linked requirements](coverage-requirements.md).
