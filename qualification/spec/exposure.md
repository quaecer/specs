# Accepted exposure and true time

An accepted exposure with known uncertainty numbers establishes the closed
range from `at - uncertainty_before_us` through
`at + uncertainty_after_us`. Exposure bounds are already true-time
limits. Overflow or a missing endpoint remains unknown.

The [exact clock contract](clock.md) defines shared occurrence identity,
report alias resolution and translation of inventory readings. Accepted
aliases name the same canonical occurrence. Distinct known canonical
identifiers cannot be made equal by an alias. An unresolved alias leaves
clock compatibility unresolved.

A forbidden occurrence opposes absence when its resource pin and channel
match policy and the full range is contained in
`[history_scope.start, lock_at)`. A bound at the lock is outside the
required history. For a nonempty intersection, the reason retains the
reports of that occurrence. For an empty intersection, keep any direct
in-scope observation as opposition, citing only that direct report.
An incompatible clock does not prove a violation on its own.

An absence criterion without a definite violation requires committed
coverage over the full required history for every policy channel.

See [the linked requirements](exposure-requirements.md).
