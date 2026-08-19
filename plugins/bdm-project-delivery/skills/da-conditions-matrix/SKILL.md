---
name: da-conditions-matrix
description: >
  Builds a DA Conditions Matrix Excel workbook for a construction or development
  project by reading a Council Decision Notice (Approval) PDF and populating the
  BDM master template (240-DA_Conditions_Matrix). Trigger when the user asks to
  prepare, populate, build, draft, or update a DA matrix, DA conditions matrix,
  development approval matrix, conditions tracker, or conditions register from a
  Council approval, decision notice, or conditions of approval document. Also
  trigger when the user mentions tracking DA conditions, allocating responsible
  parties, mapping timing triggers (commencement of works / use / plan sealing),
  or extracting Assessment Manager conditions from a PDF. Works for any
  Australian council Decision Notice (Moreton Bay, Gold Coast, Brisbane,
  Sunshine Coast, Logan, Redlands, Ipswich). Fire even if the user doesn't say
  "DA matrix" — trigger when they upload a council decision notice and ask to
  set up tracking.
---

# DA Conditions Matrix Skill

Builds a populated DA Conditions Matrix Excel workbook for a project by extracting
Assessment Manager conditions from a Council Decision Notice PDF and writing them
into the BDM master template (240-DA_Conditions_Matrix) with one row per
sub-condition, dropdown-validated responsible-party / action-by / design-by /
timing / status allocations, and a separate ADVICE tab for the Council's advice
notes.

## Why this skill exists

Every BDM project that progresses through Development Approval ends up with a
list of Assessment Manager conditions that need to be tracked through delivery —
some triggered prior to commencement of works, some prior to plan sealing, some
prior to commencement of use, some ongoing. The conditions are issued by Council
as a flat PDF that is impossible to track from. The project Director needs a
structured matrix that allocates each condition to a responsible party, an
"action by" delivery channel, a design discipline, a timing trigger, and a live
status — so the project team (PM, SPM, consultants, contractor) can drive
conditions closeout through to PC. The same task recurs for every project, and
manual population is slow, error-prone, and easy to get wrong on responsible-
party allocation.

This skill turns the workflow into a repeatable process: read the PDF, reconcile
the BDM template, populate one row per sub-condition, allocate against the
master dropdown lists, separate out advice notes, and deliver a workbook ready
for the project team.

---

## Prerequisites

This skill depends on the **xlsx** skill for Excel manipulation and the **pdf**
skill for PDF text extraction. Before starting any work, read both SKILL.md
files to understand the libraries (openpyxl), patterns, and gotchas.

It also depends on BDM's project drafting conventions, inlined below so the
skill is self-contained for any staff member running it:

- Reconcile every draft against the latest BDM master template in the Working
  Copy templates folder. Name the revision being used in the chat brief.
- Tables and registers over prose. Avoid markdown bold / italic syntax in
  deliverables — use Excel native styles.
- Always close with three blocks: Risks / Watch-outs, Items for confirmation,
  Next actions.
- Output is always draft until issued by the Director or SPM. Visible draft
  markers and an "Alfred prepared, for issue by [name]" attribution where
  appropriate.
- Verify counts, references, dropdown compliance, and that the file opens
  cleanly before declaring done.

---

## Inputs

The user provides:

1. **Decision Notice PDF** — the Council-issued approval package containing the
   conditions of approval (Attachment 2 in most council formats). The PDF
   usually includes:
   - Decision Notice (Attachment 1) — application details, approval type,
     approved plans list
   - Assessment Manager Conditions (Attachment 2) — the numbered conditions
   - Approved Plans / Documents (Attachment 3)
   - Infrastructure Charges Notice (Attachment 4)
   - Appeal Rights (Attachment 5)
   - Council Advice notes (often appended after the conditions)

2. **Project identifier** — at minimum the project name and ideally the BDM
   project code. Resolve the project against the portfolio register if one is
   available in the running environment.

3. **BDM master template** — typically auto-discovered in the Working Copy
   templates folder (do not require the user to upload it). The user may upload
   their own copy of the template; if so, verify it matches the latest Working
   Copy revision.

If anything is missing, ask before starting. Specifically confirm:

- Which project / what's the deadline / what outcome are we chasing
- Whether to include Council Advice notes (default: yes, on a separate tab)
- Row granularity — one row per lettered sub-part (recommended) or one row per
  numbered condition with sub-parts in the cell
- File naming — usually `240-DA_Conditions_Matrix_[ProjectShortName]_v1_[YYYY-MM].xlsx`
  saved under the BDM project's working folder in a per-project subfolder

---

## Workflow Overview

Four phases:

1. **Reconcile & Extract** — Verify the BDM template revision and pull the
   conditions from the PDF
2. **Allocate** — Build the row-by-row allocation against master dropdown lists
3. **Populate** — Write the workbook (DA Conditions tab + ADVICE tab) with
   dropdown validation, autofilter, freeze pane, print titles
4. **Verify & Deliver** — Run dropdown / coverage / counting checks and save to
   the working folder

---

## Phase 1: Reconcile & Extract

### Locate the master template

The BDM master template is in the Working Copy folder under the
`200 Project Management - Pre-Contract` folder. Glob for files named
`240-DA_Conditions_Matrix_R*_*.xlsx` and select the highest revision suffix and
most recent date stamp. As of writing, the current revision is
`240-DA_Conditions_Matrix_R1_2024-09.xlsx`.

If the user uploaded their own copy of the template, compare against the live
template. If divergence is found, flag to the user and confirm which version to
draft against before proceeding.

### Inspect the template

The template has three core elements:

- **Sheet1** — the matrix structure
  - Row 1: project name (header)
  - Row 2: "DEVELOPMENT APPROVAL MATRIX"
  - Row 3: `=NOW()` (auto date)
  - Rows 6-7: header row pair (REF / CONDITION / Responsible Party / Action By /
    Design Requirements / Timing / Status / Comments)
  - Row 8 onwards: condition rows
  - Freeze pane at B8, print titles `$1:$7`, landscape A4 fit-to-width
- **Sheet2** — the dropdown master lists (positions hard-coded):
  - Responsible Party: C169:C172 → Contractor, Principal (NB: typo "Princial"
    in R170 — fix to "Principal" in the deliverable), Body Corporate, N/A
  - Action By: C175:C179 → Authority, Principal, Contractor, Consultant, N/A
  - Design By: C181:C185 → Architect, Civil Engineer, Authority, Other, N/A
  - Timing: C187:C192 → Prior to commencement of any works / Prior to
    commencement of the use / Prior to the issue of a DA for Building works /
    Prior to plan sealing / Prior to commencement of works / N/A
  - Status: C194:C196 → Open, Closed, Ongoing
- The master template **does not enforce** these lists via data validation. The
  skill should add `DataValidation` of type "list" pointing to the Sheet2 ranges
  so the project file gets working dropdowns.

### Extract conditions from the PDF

Use `pdftotext -layout` to preserve column structure, since the council format
is two-column (CONDITION text on the left, TIMING on the right). Read the text
and walk through:

- Skip preamble: cover letter, application details, approved plans list, other
  necessary permits, currency period of approval, infrastructure section,
  assessment benchmarks, reasons for decision, referral agency conditions,
  appeal rights, other details
- Locate the start of the `ASSESSMENT MANAGER CONDITIONS` section (usually
  "Attachment 2")
- Parse each numbered condition:
  - Condition number (e.g. `1`, `2`, `2A`, `2B`, `13A`, `13B`, `13C`, etc.)
  - Condition heading (the first short line, e.g. "Approved Plans and/or
    Documents", "Bicycle Parking Facilities")
  - Condition body text (everything between the heading and the next numbered
    condition)
  - Timing trigger (the right column, e.g. "Prior to commencement of use", "At
    all times", "Prior to building works approval", etc.)
- Continue until the `ADVICE` section starts
- Parse advice notes (numbered 1-N, each with a topic and a paragraph of text)

For complex conditions with sub-parts (e.g. condition 13 with parts A through
E), capture each sub-part as a separate logical entry with its own timing if
the council has called it out separately.

### Compose the master condition list

Build a list of tuples in Python:

```python
conditions = [
    # (ref, condition_text, responsible_party, action_by, design_by, timing, status, comments)
    ("1",  "Approved Plans and/or Documents\nUndertake development in accordance with...",
     "Principal", "Principal", "Architect", "N/A", "Ongoing", ""),
    ("2A", "Dedicate Land for Drainage Reserve...\nA. Provide the following...",
     "Principal", "Principal", "Other", "Prior to commencement of the use", "Open", "Trigger: prior to use of Stage 1 OR..."),
    # ... etc
]
```

---

## Phase 2: Allocate

This is the highest-value, highest-risk part of the skill. The conditions PDF
does not say "Principal" or "Contractor" — it just says "the developer must..."
or "Council must be provided with...". The skill has to map the language of the
condition to the dropdown values. Get this wrong and the project team chases
the wrong people for closeout.

These allocation defaults assume a client-led delivery model (client / developer
acts as Principal and engages a head contractor). For D&C lump sum contracts
many "Principal" items shift to "Contractor" — flag this to the user at intake
and confirm contract form before proceeding.

### Responsible Party logic

| Condition language pattern | Default Responsible Party |
|---|---|
| "Submit to Council...", "Provide certification...", design-stage deliverable | Principal |
| Land dedication, easements, CMS, infrastructure agreements | Principal |
| Compliance with approved plans, design conformance | Principal |
| Site works, ESCP, CMP implementation, clearing, stockpiles, dust, noise, transport | Contractor |
| Fire spotter, fauna spotter, on-site monitoring | Contractor |
| Pre-start inspections, hold points, ad hoc Council inspections during works | Contractor |
| On-site maintenance, post-handover obligations (stormwater long-term, fire system AS1851 maintenance, bin management) | Body Corporate |
| "Operate the use in accordance with..." after commencement of use | Body Corporate |

Use Body Corporate sparingly — only for genuinely post-handover items that
survive PC. If the project is staged or the principal is operating the asset
itself, flag for confirmation before allocating to Body Corporate.

### Action By logic

| Action By value | Use when |
|---|---|
| Principal | Principal will lodge / submit / negotiate directly with Council (CMS endorsement, easements, land dedication) |
| Contractor | Site delivery items, ESCP / CMP implementation, on-site certifications during construction |
| Consultant | Design-stage certifications by a consultant (architect, RPEQ engineer, surveyor, ecologist, hydraulic) |
| Authority | Approvals or certificates issued BY a third-party authority (Unitywater, Energex, NBN) — typically certificate of completion / supply that the Principal must "obtain from" |
| N/A | Where the condition is informational or there is no specific actor |

### Design By logic

The template only has Architect / Civil Engineer / Authority / Other / N/A.
This is too narrow for real projects. Map specialist disciplines as follows:

| Discipline in condition | Map to |
|---|---|
| Architecture, building form, fencing, screening, finishes, privacy, signage | Architect |
| Civil, stormwater, hydraulics (external), roads, pathways, geotech, structural retaining walls | Civil Engineer |
| Authority-driven design (Energex, Unitywater, Council standard drawings) | Authority |
| Ecology, landscape, hydraulic (internal plumbing), waste, surveyor, town planner, fire engineer, traffic | Other |
| No design element required | N/A |

Flag at the end of the brief that the template's Design By list is thin and
that Ecology / Landscape / Hydraulic / Geotech / Surveyor / Town Planner
should be added in a future template revision (template refinement candidate).

### Timing logic

Map the council's stated timing to the template's six options:

| Council language | Template Timing |
|---|---|
| "Prior to commencement of any works" / "Prior to site works" / "Prior to clearing" | Prior to commencement of any works |
| "Prior to commencement of the use" / "Prior to use of Stage X" / "Prior to occupation" | Prior to commencement of the use |
| "Prior to the issue of a Building Works DA" / "Prior to BA approval" | Prior to the issue of a DA for Building works |
| "Prior to plan sealing" / "Prior to plan registration" | Prior to plan sealing |
| "Prior to commencement of works" (when distinct from operational works) | Prior to commencement of works |
| "At all times" / "Ongoing" / unspecified | N/A (with Status = Ongoing) |

For staged developments, the timing column should reflect the trigger; capture
the Stage in the Comments column (e.g. "Stage 1", "Stages 1 and 2").

### Status logic

For a new approval (no closeout activity yet):

- `Open` — the default for everything that has a deliverable trigger
- `Ongoing` — items with no trigger date that operate continuously (e.g. ESCP
  maintained current at all times, AS1851 fire hydrant maintenance, "operate in
  a manner that causes no detriment")
- `Closed` — never used at issue; only used later as the project team marks
  items off

---

## Phase 3: Populate

### Start from a copy of the master template

Always work from a copy. Never write to the live BDM Working Copy template
folder — the templates folder is read-only.

```python
import shutil
shutil.copyfile(MASTER_TEMPLATE_PATH, DELIVERABLE_PATH)
```

### Update the project header

Row 1: project name and DA reference (e.g. `79-81 & 83 BEACON STREET, MORAYFIELD  |  DA/2025/2817`)
Row 2: `DEVELOPMENT APPROVAL MATRIX` (preserve)
Row 3: `=NOW()` (preserve)
Row 4: applicant / council / approval date / approval type sub-line in italic

### Clear example data carefully

The master template ships with a worked example (Capris Residences). Walk all
rows from row 8 to the end and clear values, formatting, borders, and fills.
Use `ws.max_row` carefully — it may report a row count that does not match what
openpyxl will iterate over after `value=None`. Iterate to `ws.max_row + 1` and
verify post-write that no stray cells remain past your last condition row.

```python
# CORRECT clear pattern:
for r in range(8, ws.max_row + 2):
    for c in range(1, ws.max_column + 1):
        cell = ws.cell(row=r, column=c)
        cell.value = None
        cell.border = Border()
        cell.fill = PatternFill(fill_type=None)
        cell.font = Font()
        cell.alignment = Alignment()
```

### Write the conditions

For each row in the conditions list, copy the formatting from the original
template row 8 (font, fill, alignment, border) so the deliverable matches the
master template's look.

### Fix the dropdown master list typo

In Sheet2 R170, the master template has `Princial ` (typo + trailing space).
Replace with `Principal`. Trim trailing whitespace on all list cells so the
data validation matches strictly.

### Add data validation dropdowns

The master template doesn't enforce the lists. Add data validation so the
project workbook does:

```python
from openpyxl.worksheet.datavalidation import DataValidation

def add_dv(rng, source):
    dv = DataValidation(type="list", formula1=source, allow_blank=True)
    dv.errorStyle = "warning"  # don't block edits, just warn
    ws.add_data_validation(dv)
    dv.add(rng)

NEW_END = 8 + len(conditions) - 1
add_dv(f"C8:C{NEW_END}", "=Sheet2!$C$169:$C$172")  # Responsible Party
add_dv(f"D8:D{NEW_END}", "=Sheet2!$C$175:$C$179")  # Action By
add_dv(f"E8:E{NEW_END}", "=Sheet2!$C$181:$C$185")  # Design By
add_dv(f"F8:F{NEW_END}", "=Sheet2!$C$187:$C$192")  # Timing
add_dv(f"G8:G{NEW_END}", "=Sheet2!$C$194:$C$196")  # Status
```

### Re-set autofilter, freeze pane, print titles

```python
ws.auto_filter.ref = f"A7:H{NEW_END}"
ws.freeze_panes = "B8"
ws.print_title_rows = "1:7"
ws.page_setup.orientation = "landscape"
ws.page_setup.paperSize = 9  # A4
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
```

### Rename Sheet1 → "DA Conditions"

For clarity. Leave Sheet2 in place as the dropdown master lists (do not rename
or hide — the data validation formulas reference it by name).

### Add the ADVICE tab

Council advice notes are not conditions of approval — they are informational
("Aboriginal Cultural Heritage Act applies", "Adopted Infrastructure Charges
apply", "Premise is in Koala District A", etc.). Default behaviour is to
include them on a separate ADVICE tab so they don't pollute the action-oriented
DA Conditions sheet but stay on record.

ADVICE tab structure:

- Row 1: project name (matches DA Conditions header)
- Row 2: `COUNCIL ADVICE NOTES (Information Only - Not Conditions of Approval)`
- Row 4: header row with `Ref | Topic | Advice Note (Council) | Relevance / Action for Project Team`
- Row 5+: one row per advice item. The "Relevance / Action" column is the
  value-add — link each advice note back to a numbered condition where
  relevant (e.g. EPBC Act advice → links to Cond 26 Ecological Restoration Plan;
  Koala Plan advice → links to Cond 27 fauna spotter and Cond 32 No Net Loss
  Habitat).

Format with: column widths A=6 / B=32 / C=80 / D=60, freeze pane A5, landscape
A4 fit-to-width, print titles `1:4`.

### Re-order tabs

Final tab order: `DA Conditions`, `ADVICE`, `Sheet2`. Sheet2 stays at the end
as the lookup table.

---

## Phase 4: Verify & Deliver

### Run automated checks

Before declaring done, reload the deliverable and verify:

1. **Row count** — total non-empty rows in column A matches the expected
   condition count
2. **Condition coverage** — every numbered condition in the PDF (1 through N)
   has at least one row in the matrix
3. **No stray cells** — nothing past the last condition row
4. **Dropdown compliance** — every cell in columns C, D, E, F, G matches a
   value in the master lists (after stripping whitespace)
5. **Data validations applied** — five data validation objects on columns
   C through G covering rows 8 to NEW_END
6. **Sheet structure** — three tabs in the correct order (DA Conditions,
   ADVICE, Sheet2), freeze pane at B8, print titles 1:7
7. **File opens cleanly in openpyxl** — reload with no warnings
8. **File opens cleanly in EXCEL** — run `python3 scripts/validate_xlsx.py --repair` then
   `--check`; it must print CLEAN. Check 7 is not sufficient: openpyxl ignores
   `xl/calcChain.xml`, the precomputed index of formula cells. Writing conditions into the
   template turns formula cells into values, the index still names them, and Excel reports the
   file as corrupt on open. LibreOffice rebuilds the index silently, so it cannot detect this
   either. This is the single most common cause of a "corrupted" BDM workbook.

Example verification block:

```python
from collections import Counter

wb = load_workbook(PATH)
ws = wb["DA Conditions"]
cnt = sum(1 for r in range(8, ws.max_row+1) if ws.cell(r,1).value is not None)
assert cnt == len(conditions), f"Row mismatch: {cnt} vs {len(conditions)}"

# distribution by dropdown values — for the brief to the user
rp = Counter(ws.cell(r,3).value for r in range(8, 8+cnt))
ab = Counter(ws.cell(r,4).value for r in range(8, 8+cnt))
tm = Counter(ws.cell(r,6).value for r in range(8, 8+cnt))
st = Counter(ws.cell(r,7).value for r in range(8, 8+cnt))
```

### File naming and location

Save to the BDM staff member's working folder under a per-project subfolder.
Naming convention:

```
[Working folder]/[ProjectShortName]/240-DA_Conditions_Matrix_[ProjectShortName]_v[N]_[YYYY-MM].xlsx
```

If the BDM project code is known, prefer that over the short name (e.g.
`240-DA_Conditions_Matrix_202517_v1_2026-05.xlsx`). If unknown, use a clear
short name and confirm the code with the user afterwards.

Never write to the BDM Projects folder or the Working Copy templates folder.

### Brief to the user

Always close the response with four blocks:

1. **Summary of what's in the file** — tab structure, row count by sub-part,
   distribution of dropdown values (Responsible Party, Timing trigger),
   notable conditions worth flagging
2. **Items for Director / SPM confirmation** — responsible-party assumptions
   (especially Principal vs Contractor splits, any Body Corporate
   allocations), project code, contract form (if not known) since D&C
   contracts shift many Principal items to Contractor
3. **Risks / Watch-outs** — programme-critical conditions (land dedication,
   amended SMP / BCM gate, RPEQ certifications, ecology workstream,
   maintenance bonds, ICN cashflow)
4. **Next actions** — confirm code, brief consultants and contractor,
   capture template refinement candidates

Always flag template refinement candidates separately if the project
work has surfaced improvements that should feed back to the BDM master
template (e.g. the "Princial" typo, the thin Design By list, the lack of
a Stage column, the lack of a structured DA reference field in the
header).

### File-sharing format

End the response with a `computer://` link to the deliverable so the user can
open it directly:

```
[View your [Project] DA Conditions Matrix](computer://[path-to-file])
```

---

## Tone and Language

Plain English, Aussie spelling, senior construction tone. No corporate
jargon. The matrix is read by SPMs, town planners, builders, and Council
liaison — keep condition descriptions faithful to the council's wording but
strip out non-essential filler (e.g. drop "in accordance with the approved
plans and documents of development" where the meaning is obvious from
context, but retain it where the certification reference matters).

Use the council's numbering and headings verbatim. Do not paraphrase
condition triggers — get them exact, even if it means a longer cell.

---

## Common pitfalls

| Pitfall | How to avoid |
|---|---|
| Leftover example data from the Capris Residences template appearing past your last condition row | Clear values + formatting (borders, fills, fonts, alignment) all the way to `ws.max_row + 1`, then re-verify by reloading and walking past your last data row |
| Dropdown values fail validation because of trailing spaces | Strip whitespace on every cell after writing; trim the Sheet2 list cells too |
| Master template "Princial" typo carrying through to the project file | Fix Sheet2 R170 in every project file; flag as template refinement candidate |
| Body Corporate over-used for items that are really Principal's responsibility during delivery | Default to Principal; only use Body Corporate for genuinely post-handover items that survive PC |
| Treating advice notes as conditions | Put them on a separate ADVICE tab labelled "Information Only - Not Conditions of Approval" |
| Council uses staged timing ("Prior to use of Stage 1 OR at time of submitting CMS, whichever first") | Map the primary trigger to the Timing dropdown and capture the full nuance in the Comments column |
| Missing the ICN as a separate cost-bearing item | Note the ICN attachment in the brief; flag to QS / lender for cashflow |
| Data validation not applied so cells accept anything | Always add the five DataValidation objects pointing to Sheet2 ranges, even if the values you write are all compliant |

---

## Output

Deliver a single `.xlsx` workbook with:

1. **DA Conditions tab** — one row per lettered sub-part, dropdown-validated,
   autofiltered, freeze pane at B8, print titles 1:7, landscape A4
2. **ADVICE tab** — Council's advice notes with relevance / action linking
   back to numbered conditions
3. **Sheet2** — master dropdown lists (fixed "Princial" → "Principal")
4. Saved under the staff member's working folder in a per-project subfolder,
   named per the BDM convention

The file should be ready to open in Excel, filter by responsible party or
timing trigger, distribute to the consultant team and contractor, and use
as the working register through project delivery.
