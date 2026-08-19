# bdm-contract-admin

Contract administration under AS4000 — the instruments BDM issues as
Superintendent, and the tender documents that precede them.

Depends on [`bdm-standards`](../bdm-standards/README.md).

**Version 0.1.0 — staged, not signed off.** Every skill here drafts and holds.
None issues, and none signs. See [GOVERNANCE.md](../../GOVERNANCE.md) §4.

---

## Skills

| Skill | Produces | Form |
| --- | --- | --- |
| `bdm-tender-clarification` | Tender clarifications — close date extensions, tenderer RFIs, supplementary drawings | 218 |
| `progress-certificate-update` | Progress certificate, certifying a builder's claim under AS4000 cl.37.2 | 335 |

## Still to arrive

Seven skills in the legacy `JamesBDM/bdm-plugins` repository belong in this
plugin and come across under the next Change Note:

`bdm-contract-admin-router` · `bdm-contract-admin-register` ·
`bdm-variation-cover` · `bdm-variation-determination` · `bdm-eot-cover` ·
`bdm-eot-determination` · `bdm-tender-addendum`

Note for that merge: the legacy repository holds a **newer** copy of some shared
skills. Check the revision on both sides before taking either — direction of
merge is per skill, not per repository.

## Review note

Anything in this plugin produces a contractual instrument. Under GOVERNANCE the
reviewer must be someone other than the author.
