# Accepted exposure and true time

An accepted exposure with known uncertainty numbers establishes the closed
range from `at - uncertainty_before_us` through
`at + uncertainty_after_us`. Exposure bounds are already true-time
limits. Overflow or a missing endpoint remains unknown.

For this fragment all accepted events have the exact subject established by
the request. Equal occurrence IDs identify one event only inside the same
channel and resource revision. An explicit alias names another accepted
exposure report. Close equal IDs and in-scope explicit aliases transitively.
Links to unavailable reports leave compatibility unresolved. A link across
different channels or resources records a descriptor conflict and leaves
compatibility unresolved for that link.

An occurrence's compatible range is the closed intersection of its known
member ranges. An empty intersection is incompatible and cites the
contributing report IDs. If every accepted temporal premise is an exposure
with resolved identity and time bounds, these intersections decide
compatibility exactly. An exposure permits any occurrence time in its
intersection, independently of other events. Missing bindings or accepted
capture and challenge records require the wider clock translation and leave
compatibility unresolved unless an exact contradiction is already witnessed.

A forbidden occurrence opposes absence when its resource pin and channel
match policy and the full range is contained in
`[history_scope.start, lock_at)`. A bound at the lock is outside the
required history. For a nonempty intersection, the reason retains the
reports of that occurrence. For an empty intersection, keep any direct
in-scope observation as opposition, citing only that direct report.
An incompatible clock does not prove a violation on its own.

An absence criterion without a definite violation remains unresolved
until supported by committed coverage. The current issues and findings
are independent of the deferred full coverage compositions.

See [the linked requirements](exposure-requirements.md).
