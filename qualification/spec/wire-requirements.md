# Wire requirements

These statements govern structural validation of the draft interchange.
The key word MUST is interpreted as described in [BCP 14](https://www.rfc-editor.org/info/bcp14).

<a id="qual-req-001"></a>
## QUAL-REQ-001 Version tags

A validation request MUST use the exact published profile identifiers.

<a id="qual-req-002"></a>
## QUAL-REQ-002 Operator arguments

A rule MUST provide exactly the fields of its operator.

<a id="qual-req-003"></a>
## QUAL-REQ-003 Timestamp precision

A timestamp in the wire profile MUST have at most six fractional digits and a known offset.

<a id="qual-req-004"></a>
## QUAL-REQ-004 Raw report envelope

A report MUST include its identity, issuer, exact subject, implementation and nonempty basis.

<a id="qual-req-005"></a>
## QUAL-REQ-005 Segmented inventories

A segmented statement MUST use an empty parent inventory and null parent digest.

<a id="qual-req-006"></a>
## QUAL-REQ-006 Bounded request and caller selection

The complete UTF-8 request MUST occupy at most 2,097,152 bytes, and MUST supply caller report pins and artifact bodies as explicit arrays.

<a id="qual-req-007"></a>
## QUAL-REQ-007 Unrun observation

A check or control with state not_run MUST carry a null result or observed field respectively.

<a id="qual-req-021"></a>
## QUAL-REQ-021 Identity grammar

An identity MUST match the absolute IRI grammar and retain its exact spelling.
