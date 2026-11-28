# Transfer between declared uses

A [transfer request](../schema/transfer-request.schema.json) has profile
`https://quaecer.github.io/specs/qualification/1.0/transfer-request`,
operation `transfer`, and two ordinary assessment requests named
`source` and `target`. Both have operation `assess`. The response is a
target assessment with any carried findings listed in `transfers`.
The request has no source result field.

Bind both requests as for direct assessment. Their exact view digests
must agree, including the claim, subject, implementation, selected report
digests, supplied bodies, reference inventory and use registry. If both
uses have the same identifier, the whole declared use agrees. The target
kind reaches the source kind in the registry's reflexive transitive
closure. Refuse an inexact binding or disallowed direction.

## Criterion identity

Create a canonical object with `profile` set to
`https://quaecer.github.io/specs/qualification/1.0/criterion-instance`,
`predicate` set to the following rule parameters, and `settings` set
to the applicable policy parameters below.

- The predicate consists of every rule field except `id` and `uses`.
  Compare applicability separately. Sort selection pins and dependence
  endpoints by canonical JSON bytes. Represent a control's expected
  value and tolerance as reduced rational strings with positive
  denominators, omitting the denominator for integers.
- Settings include the conflict policy for every instance. Coverage
  and absence also bind the scope margin and defeat scope.
- For coverage, include `window`, with its start and end normalized to
  UTC using the `+00:00` offset. For absence, include `start` from history
  scope and `lock_at` with the same normalization, sorted `channels`
  and canonical-byte-sorted `forbidden` pins. UTC timestamps omit the
  fraction when zero and otherwise write six digits.
- No built-in predicate depends on its rule label, use name or the
  free-text description of its purpose. All other supplied rule
  parameters bind exactly.

## Carry and verify

Derive the source finding from its accepted inputs. Both source and
target need compatible clocks and consistent views. A source finding
must apply to the source use, be evaluated and be passed or failed.
Carry it to an applicable target criterion only if their canonical
instances coincide. If several source findings match, choose the
lexically first source criterion. The carried value and outcome also
agree with direct target assessment. Retain the source finding's
basis and reasons, substituting the target criterion identifier in
rules that name it.

Order certificates by target criterion identifier. Each certificate
binds the source and target use identifiers and policy digests, common
view and registry digests, criterion instance digest, source and target
criterion identifiers and the digest of the complete original source
finding. The target verdict checks all of its own applicable criteria.
A blocked transfer leaves the direct target assessment. A matched
opposition may fail the target. Authorization remains `not_granted`.

The receiver accepts the regular verification envelope with a transfer
request in its `request` field. For the compact RDF envelope, frame the
evidence of each nested assessment with the installed evidence context.
Frame the carried result with the installed result context. Compare the
full carried result with the recomputation. The accepted source and
target reports supply all premises for receiving verification.

See [the linked requirements](transfer-requirements.md) and
[the transfer soundness statement](formal.md#p1-soundness-of-criterion-transfer).
