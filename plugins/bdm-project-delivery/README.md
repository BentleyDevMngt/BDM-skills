# bdm-project-delivery

Development and project management delivery — the reporting, approvals tracking
and record-keeping that runs a job month to month.

Depends on [`bdm-standards`](../bdm-standards/README.md).

**Version 0.1.0 — staged, not signed off.** Every skill here drafts and holds.
See [GOVERNANCE.md](../../GOVERNANCE.md) §4.

---

## Skills

| Skill | Produces | Form |
| --- | --- | --- |
| `bdm-monthly-project-report` | Client-side monthly report to the Principal | — |
| `monthly-report-update` | Financier's / lender's monthly report, tracked changes | — |
| `da-conditions-matrix` | DA conditions matrix from a Council decision notice | 240 |
| `bdm-consultancy-agreement` | Consultancy agreement from a consultant's fee proposal | 105 |
| `meeting-minutes-update` | Meeting minutes rolled forward with tracked changes | — |
| `bdm-site-inspection-report` | Site inspection record from a OneNote export | 331 |
| `bdm-invoice-filing` | Project invoices swept from the mailbox and filed to the job folder, with a sync log | — |
| `bdm-meeting-brief` | Pre-meeting brief for the Director, emailed | — |

## Open items

**~~`bdm-monthly-project-report` carries an embedded master document.~~
CLOSED 2026-08-20.** The master is now **Form 260 Monthly Project Report R1**,
issued into `BDM TEMPLATES\Working Copy\200 Project Management - Pre-Contract\`
under CN-2026-033 on Director instruction. The embedded copy is deleted and the
skill resolves the form at run time like every other, pinned to R1. No skill in
this repository now carries a controlled artefact.

**Two copies of the minutes skills exist.** The legacy `JamesBDM/bdm-plugins`
repository holds `meeting-minutes-update` at **R3 · 2026-08-18**; the copy here is
**R1 · 2026-06**, and JG's carries material the R1 does not — Phase 0 project
context, the drop-closed-items rule, renumbering logic and the OOXML
track-changes patterns. **Do not overwrite JG's with this one.** It also holds
`bdm-site-and-adhoc-minutes`, which belongs in this plugin and has no counterpart
here. Both resolve under the next Change Note.

**`bdm-meeting-brief` is not self-contained — open for the Director.** The skill is a
short form that directs the reader to `Projects - Documents\Alfred\
BDM_Meeting_Brief_Procedure_2026-08-30.md` as its source of truth, so it cannot run
for anyone without that path, and the procedure it depends on is versioned outside
this repository and edited by hand. It is also written for one named recipient
rather than a role. Either the procedure comes into the skill and the recipient
becomes a parameter, or the skill stays a personal tool and out of the controlled
estate. Not resolved here.

**`bdm-invoice-filing` belongs to project delivery — Director ruling, 31 August 2026.**
It was staged under `bdm-quantity-surveying` on the reasoning that everything it feeds
(the Form 201 fee register, the head contract progress claim, the Form 335 certificate)
sits there. The Director ruled otherwise: filing project correspondence into the job
folder is delivery record-keeping, not cost control. Placement closed.

The skill carries a standing exclusion naming **202415 South Pine Rd, Everton Park**,
because that job runs the only `01a_Accounts` payment chain and a second copy of those
invoices would make the progress claim unauditable. A live job name hardcoded into a
skill is a separate open item for sign-off — the rule is right, the hardcoding is not.
