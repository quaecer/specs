# Committed coverage

The installed draft composes commitments with empty inventories. A coverage
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
and has an empty inventory. Both declared scope kinds commit all
information uses on their named channels for the specified interval.
Other capture statuses give no support. A complete unit outside this
fragment carries `statement_obligation`. Nonempty inventories retain their
exact commitments and leave clock compatibility unresolved in this fragment.

## Clocks and composition

A scope `[a,b)` is nominal on its named clock. True time is a non-decreasing
function of readings, with absolute error at most the declared accuracy on
the unit. Equal clock identifiers share that function. These premises are
conditional on the accepted declarations. Exposure intervals already give
closed true-time bounds.

At each known error bound among eligible units of one clock, merge the
overlapping and adjacent nominal intervals of units with error at most that
bound. Erode the merged intervals by that bound at both ends to recover
certain true-time intervals. For positive coverage also apply the policy
margin as a minimum erosion. Union these intervals across bounds and
clocks after erosion. Distinct clocks have no shared boundary. Erosion
discards empty ranges.

For compatibility, the identity map is a valid clock assignment for the
compiled fragment. It works if each occurrence's compatible closed UTC
range has a point outside all eligible nominal scopes on its channel.
This constructive check can prove compatibility if all accepted temporal
premises are compiled. If that assignment fails and no contradiction is
proved, compatibility remains unresolved. Capture challenges and
nonempty inventories still need the full translation to clock constraints.

## Defeat and output

An accepted exposure contradicts the empty commitments if its entire
closed UTC range lies in the certain union of their scopes on its channel.
Candidates are eligible commitments whose possible images
`[a - accuracy,b + accuracy)` meet that range. A witness may require several
units. An event at a right endpoint falls outside a half-open interval.
Defeat removes each candidate unit on the witnessing channel. Policy may
widen defeat to the entire statement, to complete commitments by that
observer on the channel, or to all of the observer's complete commitments.

An incomplete or disabled report contradicts a complete unit only when
they share observer and channel and their individual certain intervals
overlap. Group the opposing report identifiers by complete unit and
channel. An unknown report or another observer's partial capture
contributes no opposition. This inconsistency is distinct from clock
compatibility.

For each policy channel, compose separate window and history results from
undefeated units. Clip regions to the requested interval, carry their unit
identifiers and emit the uncovered complement as gaps. List defeated
units' possible regions separately, so those regions can overlap with
support from a surviving unit. When no completeness report is selected,
the result has an empty coverage list.

The compositions retain accepted statement pins, structured reasons and
`joint_omissions`. Each omission records the event's closed range, its
accepted exposure report IDs, the candidate unit IDs, the policy defeat
scope and the affected unit/channel pairs. Witnesses for a channel appear
in both compositions even when their effect lies outside one requested
interval. Statement pins and unit/report identifiers sort lexically.
Reasons and witnesses sort by canonical JSON.

Coverage support requires compatible timing, no capture inconsistency and
no gaps for the relevant interval and channels. A definite forbidden
exposure gives opposition independently, even when one of the commitments
is defeated. Unresolved temporal criteria carry `clock_unresolved` if
compatibility is unproved, and otherwise `coverage_gap` for a gap or an
unmet coverage prerequisite.

See [the linked requirements](coverage-requirements.md).
