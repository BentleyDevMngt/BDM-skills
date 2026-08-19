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

## Open items

**`bdm-monthly-project-report` carries an embedded master document.**
`assets/BDM_Monthly_Project_Report_MASTER_R1_2026-08.docx` is the one skill in
the repository that does not resolve its template from the controlled library at
run time, because the form is not in the library — it has no form number and no
entry in the register. Under the template policy adopted 2026-08-20
([GOVERNANCE.md](../../GOVERNANCE.md) §5) it should be issued a form number,
filed into `BDM TEMPLATES\Working Copy`, and the skill converted to resolve it
like every other. **Director action** — allocating a form number is a controlled
act, not a repository edit.

**Two copies of the minutes skills exist.** The legacy `JamesBDM/bdm-plugins`
repository holds `meeting-minutes-update` at **R3 · 2026-08-18**; the copy here is
**R1 · 2026-06**, and JG's carries material the R1 does not — Phase 0 project
context, the drop-closed-items rule, renumbering logic and the OOXML
track-changes patterns. **Do not overwrite JG's with this one.** It also holds
`bdm-site-and-adhoc-minutes`, which belongs in this plugin and has no counterpart
here. Both resolve under the next Change Note.
