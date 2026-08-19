# CHANGELOG — BDM Monthly Project Report

## R1 / 2026-08 — packaging fix, 19 August 2026 (no revision bump)

The `description:` field measured **1,037 characters against the platform's 1,024 limit**, so
the package could not be installed at all — `field 'description' in SKILL.md must be at most
1024 characters`. Trimmed to **1,004** (20 characters of headroom).

Three phrases shortened, none of them trigger text:

- "the reporting period's email correspondence" → "the period's email correspondence"
- "authority approvals held in the job folder" → "authority approvals in the job folder"
- "NOT for the financier's monthly report to a lender's credit team" → "NOT the financier's
  monthly report to a lender"

All six trigger phrases retained. **Nothing below the frontmatter changed** — the instructional
body, the master template, both references and `tracked_changes.py` are byte-identical to the
original R1 package. Packaging-only, so the revision is unchanged per migration decision J1.
Outgoing package archived to `_SS\bdm-monthly-project-report_R1_2026-08_superseded-2026-08-19.skill`.


## R1 / 2026-08 — first issue, replacing bdm-project-status-report

Renamed from `bdm-project-status-report` so the skill is unmistakably associated with the
Monthly Project Report template. `bdm-project-status-report` R3 is superseded and retired;
its one-page Project Summary Report format is no longer used.

Built from **the pilot project's Monthly Project Report No. 01 DRAFT v0.4** (7 August 2026), adopted
as the company-wide form. The skill was adjusted to the report, not the report to the skill.

### What changed from bdm-project-status-report R3

**The deliverable.** One page with a six-row at-a-glance dashboard → six pages: cover, a
three-page body numbered 1.0 to 7.0 per Form 425, and Annexures A and B. Twelve tables,
none of which matched their nearest R3 equivalent in columns or purpose. The template was
replaced outright.

**Trend arrows retired.** R3 carried a Trend column (↑ Worsening / → Stable / ↓ Improving)
and a good deal of machinery to recolour the badges and avoid occurrence-matching traps.
The new format has no trend column. All of it removed.

**The governing rule is new: synthesise, do not author.** The report draws on project
information that already exists and creates none of its own. Every statement traces to a
named source with version and date. A figure with no source becomes an Annexure B action.
Conflicts between sources are reported, not resolved. BDM's judgement is confined to risk
ratings and recommendations. `references/source-to-section-map.md` is the intake checklist.

**Definition of done rebuilt.** R3's was truncated mid-word — "A validat" — in both the
library and running copies, so the skill had shipped with no working completion criteria
for an unknown period. Rewritten as eleven checkable conditions.

**File-on-disk verification is now mandatory.** Three artefacts from the pilot project's drafting
work — report v0.3, v0.4, and a project-memory record — were each reported as saved and
none reached disk. v0.3 survived only because it had been emailed; v0.4 only because the
Director held a copy. The skill must now list the finished file at its final path and
confirm a non-zero size rather than asserting the write succeeded.

**Trigger boundary drawn against `monthly-report-update`.** That skill (authored by James
Gill, in use on Britannia Avenue) serves a lender's credit team; this one serves the
Principal. Both are monthly tracked-changes Word reports, so the descriptions previously
overlapped on "monthly report" and "project status report". This skill's description now
excludes financier work explicitly. `monthly-report-update` was not modified.

### Rules carried into the skill from the v0.4 form

- **Sections persist; content states the position.** A section with no activity says so and
  says why. Never deleted.
- **`n/e` — not established.** Absence reported as a finding with its consequence stated,
  never zeros or blanks.
- **2.0 Status summary is the index to the body** — column head `Section`, one row per body
  section 3.0–7.0, in order, carrying section numbers. Non-section issues fold into the
  section that owns them.
- **Reporting period and data cut-off are separate dates**, both stated, movements between
  them flagged.
- **Sources cited with versions**, including adverse findings about the sources themselves.
- **Annexure A is HIGH only**, priority order; MEDIUM summarised in trailing prose.
- **The body is three pages** — a constraint, not a target.
- **Cost on the Form 425 development-summary basis**, so client and financier reports share
  one cost model. 4.1 and 4.2 categories fixed.

### Retained from R3

The complete-correspondence-review workflow, tracked changes via the docx skill,
`scripts/tracked_changes.py`, draft-and-hold discipline, the risk-rating colour rule, and
the OneDrive environment gotchas. None of it was format-dependent.

Added to the gotchas: headers and footers carry project identity — the body can be clean
while the header still names the previous project.

### Open items

- **Sales.** Sales meeting minutes are a named source but the form has no sales section.
  The pilot project has no sales programme so it never surfaced. A residential project will need
  **8.0 Sales and marketing**. Deferred to the month-end review deliberately — the form was
  settled and the skill follows the form.
- **Template control.** Whether the master belongs in `BDM TEMPLATES\Working Copy\` with a
  form number and Change Notice, or stays skill-internal, is unresolved. It ships inside the
  skill with no form number, since assigning an unverified number would put a false
  reference into the QA system.
- **Not yet exercised on a live contract.** The pilot project is pre-approval and pre-contract, so
  4.1, 7.0 and the contractor-sourced inputs have never run against claims, certificates,
  variations or EOTs.
