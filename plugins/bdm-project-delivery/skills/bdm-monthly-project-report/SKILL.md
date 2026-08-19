---
name: bdm-monthly-project-report
description: >
  Produce the BDM Monthly Project Report — the client-side monthly report to the
  Principal, six pages: cover, a three-page body numbered 1.0 to 7.0, and Annexures
  A (critical risk register) and B (outstanding actions). Trigger on "monthly project
  report", "prepare/draft/roll forward the monthly report for [project]", "MR-NN",
  "project status report", "monthly status report", or "status report for [project]".
  The report SYNTHESISES existing project information — meeting minutes (design, site,
  construction, sales), the period's email correspondence, consultant fee
  registers, monthly cost reports, contractor's claims and progress certificates,
  construction programmes, and authority approvals in the job folder. It creates
  no new information. Produces a tracked-changes DRAFT held for Director/Senior PM
  review; never issues. NOT the financier's monthly report to a lender
  (that is monthly-report-update), NOT for QS lender reports (Forms 424/425),
  Progress Certificates (Form 335) or meeting minutes.
---

# BDM Monthly Project Report

Supersedes `bdm-project-status-report` (R3, 2026-08) — the one-page Project Summary
Report with the trend-arrow dashboard. That format is retired.

The client-side monthly report to the Principal. Six pages:

| Page | Content |
|---|---|
| 1 | Cover |
| 2 | 1.0 Report particulars · 2.0 Status summary · 3.0 Programme |
| 3 | 4.0 Cost (4.1 Development budget · 4.2 Professional fees · 4.3 Cost movement) |
| 4 | 5.0 Approvals · 6.0 Design · 7.0 Construction and delivery |
| 5 | Annexure A — Critical risk register |
| 6 | Annexure B — Outstanding actions |

Numbering runs 1.0 to 7.0 with 4.1–4.3 beneath, per Form 425. Master template:
`assets/BDM_Monthly_Project_Report_MASTER_R1_2026-08.docx`.

---

## The governing rule: synthesise, do not author

**This report creates no new information.** It draws on project information that
already exists, reconciles it, and reports the position with its provenance.

- Every statement traces to a named source document, with version and date.
- A figure with no source does not go in the report. It goes in Annexure B as an
  action to obtain the source.
- Where sources conflict, **report the conflict** — do not resolve it silently and do
  not pick a side.
- Where a source does not exist, the absence **is** the finding. See `n/e` below.
- BDM's own judgement is confined to the risk ratings and the recommendations.
  Everything else is reportage.

If you find yourself writing a fact you cannot point at a document for, stop. Either
find the document or move the item to Annexure B.

---

## Operating mode and boundaries

- **PRODUCE** task ending in a **DRAFT, held not issued**. Name files
  `yyyymmdd_<Project>_Monthly Project Report No.NN_DRAFT_vN.N.docx`.
- Draft-and-hold always. The report *reports* EOT and variation positions; it does not
  determine them. If one needs assessing, flag it — do not decide it here.
- Verify, don't guess. If a figure, date or reference is uncertain, flag it.
- Australian spelling. Plain, senior, commercially-aware tone. Tables over prose.
- **Never PDF a draft.** The clean PDF is exported by the Director from Word after
  accepting changes.

### Which skill, not this one
- Monthly report to a **financier / lender's credit team** → `monthly-report-update`.
- **QS** Initial or Progress Valuation report → `qs-initial-report` / `bdm-qs-progress-valuation`.
- **Progress Certificate** → `progress-certificate-update`.
- **Meeting minutes** → `meeting-minutes-update`.

The distinction that matters is audience: this report is written **for the Principal**;
`monthly-report-update` is written **for a lender**. Both are monthly, both are tracked-
changes Word documents. If the request names a financier, facility, drawdown or credit
team, it is not this skill.

---

## Phase 0 — Intake

1. Confirm the project, the **reporting period**, and the **data cut-off**. These are
   different dates and both appear in the report. The period ends at month end; the
   cut-off is when you stopped gathering. Movements between the two are flagged as such.
2. Confirm the report number (`No. NN`) and reference (`<project no> · MR-NN · R<n>`).
3. Read `00_ai_sandbox\Project_Summary_*.md` as a state primer — **treat as potentially
   stale**; the job folder wins.
4. Find the previous report. If none, start from the master template in `assets/`.

## Phase 1 — Harvest the sources

Work the checklist in `references/source-to-section-map.md`. Every section is populated
from named documents:

| Source | Feeds |
|---|---|
| Construction programmes | 3.0 — milestones, float, critical path, programme provenance |
| Consultant fee registers | 4.2 — forecast, cost to date, cost to complete, engagement status |
| Monthly cost reports | 4.1 · 4.2 |
| Contractor's claims | 4.1 · 7.0 |
| Progress certificates | 4.1 · 7.0 — certified vs claimed, retention, cost to complete |
| Authority approvals, decision notices | 5.0 |
| Design meeting minutes | 6.0 |
| Construction / site meeting minutes | 7.0 |
| Sales meeting minutes | Sales position — see "Sales" below |
| Email correspondence for the period | All sections — movements not yet in a formal document |
| Other reference documents in the job folder | All sections |

**Read every `.msg` in `00_Email Communication` for the period.** Do not sample. There
are typically 30–200 a month. For large folders, fan out to sub-agents (one per ~50–80
emails) returning only material items with date, sender and subject. Also search Outlook
mail and calendar for correspondence and meetings not yet filed.

**Verify against the job folder, not just the emails.** An email saying a permit is
pending is wrong if the folder holds the approved permit. The folder wins.

Build a written change-list — old → new, with source — before touching the document.

## Phase 2 — Write the report

### Rules that make the format work on any project

**1. Sections persist. Content states the position.** Never delete a section because
there is no activity. Say there is none and why — "No construction activity, contract or
executed ECI agreement, and accordingly no claims, variations, EOTs, notices or
defects." The reader must be able to tell "nothing happened" from "nobody reported it".

**2. `n/e` — not established.** Where a budget, cost plan or feasibility does not exist,
fill the cells with `n/e` and state the consequence: no total development cost, cost to
complete or expenditure-against-budget position can be reported. Never zeros, never
blanks, never omission.

**3. 2.0 Status summary is the index to the body.** Its column head is **Section**. Its
rows carry the section numbers, in section order: 3.0 Programme, 4.0 Cost, 5.0 Approvals,
6.0 Design, 7.0 Construction and delivery. One row per body section, no more and no
fewer. An issue that is not a section (electrical supply, say) folds into the section
that owns it. This is what stops the summary drifting from the body.

**4. Cite sources with versions** — including adverse findings about the sources
themselves. If the programme carries no status date and nothing has been statused, say
so and note that float is therefore an as-planned value, then recommend reissue.

**5. Ratings have a stated basis** — "BDM's assessment of residual risk to the Principal"
at the data cut-off. Not generic severity.

**6. Annexure A carries HIGH only**, in priority order. MEDIUM items are summarised in a
single trailing paragraph of prose, not tabulated. This keeps the register readable as
projects accumulate risk.

**7. The body is three pages.** That is a constraint, not a target. If it runs over,
condense — merge related rows, move milestones to Annexure B as actions, and strip design
numbers that are not reporting numbers.

### Risk-rating colour (BDM standing rule)
LOW = green `1A4A2A` · MEDIUM = amber `9D7B5B` · HIGH = red `B91C1C`, bold. Applies to
2.0 Status summary and Annexure A. Verify the cells render in the right colours before
reporting done.

### Cost
Reported on the **BDM Form 425 development-summary basis**, so the client report and the
financier report share one cost model. Categories in 4.1 are fixed: Land · Professional
fees · Authority fees and charges · Construction · Contingency · TOTAL. Categories in 4.2
are fixed: Executed agreements · Accepted, agreement pending · Issued, unexecuted ·
Proposal only, not engaged · Not quantified · TOTAL. **Check the fee categories sum to
the TOTAL and that the TOTAL ties to the fee register named in the Status column.**
All figures exclusive of GST.

### Sales
Where the project has a sales programme, report the sales position from the sales meeting
minutes. The current master has no sales section — if the project needs one, add **8.0
Sales and marketing** ahead of the annexures and raise it so the master can be updated.
Where there is no sales programme, say nothing rather than adding an empty section.

## Phase 3 — Tracked changes (roll-forward only)

Depends on the **docx** skill — read its SKILL.md for the unpack → edit XML → repack
workflow and the `<w:del>`/`<w:ins>` rules. `scripts/tracked_changes.py` finds a run by
its visible text, skips runs already inside `<w:del>`/`<w:ins>`, and rebuilds del/ins as
proper siblings, copying `<w:rPr>` into both. Author `Alfred`, date = issue date.

**Generate the version change record mechanically** — diff the two documents, count rows,
name what moved. Do not write it from recollection; a hand-written change record drifts
from what actually changed.

## Phase 4 — Deliver and verify

1. Save the draft to `00_ai_sandbox\<yyyymmdd>\`. Issued reports go to
   `08_Issued Reports\Monthly Project Reports\<yyyymmdd>\` — the Director issues, not you.
2. Run the docx `validate.py`.
3. **Confirm the file is on disk.** List it at its final path and check the byte size is
   non-zero. Do not report the write as done without looking. Drafts have been lost this
   way — v0.3 and v0.4 of the first report on the pilot project were both reported saved and neither
   reached the folder.
4. Render to PDF and read it back: six pages, three-page body, tracked changes visible,
   badge colours right, no placeholder brackets left unfilled.
5. Update `Project_Summary_*.md` in the same pass — the issued reports register and any
   status the report has moved.
6. Deliver with a short cover note: headline movements by section, then a clearly
   separated list of **flags and decisions for the Director**.

## Definition of done

The report is done when **all** of the following hold:

- Every section 1.0–7.0 is present, including any with no activity, and both annexures.
- Every statement traces to a named source document with version and date; nothing is
  authored.
- The 2.0 Status summary has exactly one row per body section, in section order, with
  matching section numbers.
- Cost figures sum: 4.2 categories tie to the 4.2 TOTAL, and the TOTAL ties to the fee
  register named in the Status column.
- Every unavailable figure reads `n/e` with its consequence stated — no zeros or blanks.
- Annexure A carries HIGH-rated risks only; MEDIUM items appear in the trailing paragraph.
- Rating colours match the ratings.
- Reporting period and data cut-off are both stated and distinct.
- The body is three pages; the document is six.
- The file exists at its final path with a non-zero size, verified by listing it.
- The draft is held, not issued, and no PDF has been presented as final.

## Environment gotchas

- **OneDrive cloud-only files:** copying a `.docx` out of the live project folder can
  yield a truncated placeholder. Do unpack/edit/pack work on a local copy; write only
  finished files into the project folder.
- **Delete/overwrite in the mount may be blocked** while creation works. Work in a local
  scratch dir.
- **`[trash]` folders** sometimes ride along inside an unpacked `.docx` — remove before
  packing or validation fails on "unreferenced file".
- **Image-only cost-report PDFs:** `pdftotext` returns nothing — render with `pdftoppm`
  and read the image.
- **Headers and footers carry project identity.** When building from a previous report or
  the master, check both — the body can be clean while the header still names the last
  project.
