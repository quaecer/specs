# Exact clock compatibility

The [formal reduction](formal.md#clock-compatibility) defines continuous
compatibility for the resolved timing premises of an accepted view. The
process uses integer microsecond input coordinates and real-valued unknown
true times. Date and offset checks precede compilation. A closed event
interval includes both endpoints. A capture and the required history are
half-open, including their start and excluding their end.

## Accepted premises

- A selected exposure describes an occurrence with an authoritative
  true-time bound. Its reporter's clock identifier is attribution. The
  uncertainty fields already incorporate the reporter's clock error.
- A selected typed inventory entry establishes an occurrence even if the
  corresponding exposure body is missing or unselected. It describes a
  closed bracket of nominal readings on its parent clock. The parent's
  error bound applies throughout this bracket. A used exposure body
  with the same event identifier binds the exact usage digest, channel,
  resource and occurrence identity. Different reporters may describe
  different timing intervals for the same occurrence.
- An observation supplies a closed bracket when its reading and both
  uncertainty bounds are known and both endpoints are representable.
  A partial bracket leaves timing unresolved and supplies no clock bound.
- A reference resolves to a selected exposure or to an event described by
  a selected typed entry. Its channel belongs to the committed unit.
  A valid reference lists the occurrence and adds no reading. A missing
  reference supplies no positive scope obligation and records
  `missing_usage`. Group unresolved entry identifiers per committed unit.
  The reason names the parent report in `report_ids`, unresolved entry
  identifiers in `related_ids`, and null channel and criterion. This also
  applies when conflicting descriptors prevent resolution. Unselected
  bodies supply no equality or time bound.
- Canonical occurrence identifiers under `occurrence/explicit-id` are
  stable for the channel and exact resource pin. Accepted aliases name
  other report or entry identifiers for that occurrence. Close equal
  canonical identifiers and valid aliases transitively. An alias may
  confirm a canonical identifier or join an unspecified identifier to
  an occurrence. Conflicting known canonical identifiers or descriptors
  record `conflicting_observations` and supply no equality premise.
  When exact descriptors disagree for one identifier, exclude that
  disputed occurrence from the clock formula. Group incompatible alias
  declarations by originating event identifier. These descriptor and
  alias reasons carry the contributing report IDs, null channel and
  criterion, and empty `related_ids`. Missing alias targets leave
  compatibility unresolved.
- Every selected known accuracy applies on the closed nominal extent of
  the unit's scope, including both endpoints. All readings in that
  extent obey the bound, whether introduced by the unit or another
  observation on the same clock. An incomplete or disabled capture can
  provide timing evidence. It supplies no completeness premise.
- Every eligible complete committed unit constrains a certainly distinct
  unlisted occurrence on its channel to fall strictly before its mapped
  start or at or after its mapped end. An accepted occurrence is
  certainly distinct from a listed one if their exact resource revisions
  differ, their known canonical identifiers differ within the scheme,
  or their independently bounded true-time envelopes are disjoint.
  Missing identity or membership information supplies no defeat.
  The elapsed time bounds describe observations of the event. An
  inventory can also list an event outside the scope it commits to cover.

Clock readings with equal clock and nominal value share one true-time
variable across all units, channels and observers. Variables are ordered
by nominal reading per clock. A typed entry places the true occurrence
between the true times of its bracket endpoints. Apply the tightest
applicable accuracy to each reading. Interpolation between consecutive
readings extends a solution to the whole scoped clock. Each declared
band intersects the interpolation only over subintervals whose
endpoints already satisfy that band.

## Decisions and explanations

Check positive timing constraints on their own, then also enforce all
eligible omission premises. A contradiction in either check establishes
`incompatible`. Complete satisfiability establishes `compatible`.
Missing bounds, unresolved identities and an incomplete bounded search
leave `unresolved` unless a contradiction is established. Expose the
accepted premise set with `clock_incompatible`, or report a bounded
`omitted_event` witness when the omission constraints for one occurrence
are sufficient. The profile requires a sound incompatibility decision
and does not require enumeration of every witness or a minimal
unsatisfiable subset. When the joint formula is unsatisfiable and no
single-occurrence explanation is established, emit `clock_incompatible`.
This includes contradictions that require several occurrences and search
limits reached while explaining an already established contradiction.
It is evidence of incompatibility and blocks qualification even with no
localized defeat record. The clock decision and non-clock inconsistencies
are separate.

### Positive clock premises

The result MUST retain the records that contribute bounds to the positive
formula, including a looser declaration subsumed by a tighter one. The
records have an exact accepted `report` pin, and closed `lower` and `upper`
bounds in normalized UTC spelling. The kind determines their meaning.

| Kind | Coordinates | Source and interpretation |
| --- | --- | --- |
| `capture_accuracy` | Nominal on `clock_id` | The `unit` and `observer` declare `accuracy_us` across these readings. Partial or disabled captures can contribute this premise. |
| `entry_clock` | Nominal on `clock_id` | The typed `event_id` in the parent report's `unit` lies between these readings, with `accuracy_us` applied by the parent. |
| `event_utc` | True UTC | An exposure report bounds the event directly. The reporter's named clock supplies no further constraint. |

For each event premise, `occurrence` is the lexically first event
identifier in its resolved group, so direct and typed-entry bounds for
that occurrence join even when their source identifiers differ. The
compiled monotonicity edges follow from clock identity and readings,
and do not need additional source records. Sort and deduplicate the
array by RFC 8785 bytes. A witness's `clock_constraints_digest` is the
SHA-256 digest of that canonical array. It binds all positive premises
available to the query, including any cross-channel calibrators. It
does not assert that every retained premise was necessary.

A capture challenge is a selected assertion with a bound witness pin and
a true-time interval. A capture challenge selects a channel and observer,
while a channel-scope challenge selects a channel. Defeat applies if
positive timing premises force a nonempty overlap with the eligible
unit on that channel. The same overlap check applies to an observer's
own incomplete or disabled statement against an eligible complete unit.
A possible overlap alone contributes no defeat. Group witnesses by
affected committed unit and channel before applying the policy's
defeat scope.

A forbidden occurrence can oppose absence if accepted positive timing
premises force it into the required history. A contradictory event
group cannot prove an interval by itself. Independently sufficient
direct readings are retained even when the joint constraints fail.
Omission constraints never prove a positive violation. For absence
support, require guaranteed coverage under the policy margin and
compatible timing. Test each existing forbidden occurrence against
the history with the full compatible formula. Any possible occurrence
inside the history gives `possible_exposure`. The guaranteed coverage
rules out a fresh unlisted forbidden occurrence on every required
channel. The inference is conditional on the accepted clock and
completeness declarations.

The exact search uses scaled integer difference bounds. With `n`
vertices, scale each integer bound by `n + 1` and subtract one for strict
inequalities. A simple cycle has at most `n` edges. Scaling preserves
the sign of nonzero integral cycle sums, and a zero sum with a strict
edge becomes negative. Conjunctive feasibility is therefore exact over
real time, including solutions between adjacent microseconds. Check
disjunctions by branching on a clause violated by a feasible
conjunctive assignment. Implementations may bound work. Exhausting the
allowance never establishes compatibility, absence or transfer.

See [the linked requirements](clock-requirements.md).
