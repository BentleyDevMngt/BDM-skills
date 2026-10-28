---
name: "bdm-floor-area-schedule"
description: "Measure a floor area schedule from architectural drawings and produce two deliverables — the BDM Form 405 workbook and the 405a A3 markup PDF, which is also a live Datum file (every polygon editable, quantities worked by Datum). Measures from the drawing's own vector linework, not a picture of it. Trigger on 'floor area schedule', 'area schedule for [project]', 'area take-off', 'measure the areas off the plans', 'GBA / GFA / NSA', \"what's the GFA\", 'net sellable area', 'NSA by unit', 'unit mix and areas', 'how many m2 is the building', 'site cover and plot ratio', or whenever DA / design-development plans are handed over to work out areas for a feasibility, a $/m2 rate, a revenue line or a plot-ratio check. Also when the Director has corrected a 405a in Datum and the schedule needs rebuilding. Held for Director sign-off. NOT for cost estimates (Forms 410-413), QS lender reports (Forms 424 / 425) or progress certificates (Form 335)."
---

# Floor Area Schedule — BDM Form 405 (R4.0)

**Revision: R4.0 · 2026-10** — skill revisions carry one decimal place: a scope change raises the whole number, a correction or refinement raises the decimal. The release history is in this skill's CHANGELOG (where it has one) and the repository CHANGELOG.

## What this does and why

Someone hands over a set of architectural plans and wants to know how big the
building is — for a $/m² rate, a revenue line, a plot-ratio check, or a
feasibility about to go to a client or a lender.

**R4 measures from the drawing's vectors.** An architect's PDF carries the zone
fills its area schedule was taken from, the wall poche on its own named layer,
and every corner at CAD precision. Taking corners from that linework gives
figures that trace to a line on the sheet. The R3 method — rendering the plan to
a picture and flood-filling it — stays as a fallback for sheets with no usable
vectors. On the October 2026 test job (a three-level house, design-development set) the vector method matched
the architect's zones to 0.03%; R3 run unaided was −46%, +17% and +2.4% on the
three levels, because it could not tell a terrace or a garden from the building.

## The two deliverables

| # | File | What it is |
|---|---|---|
| 1 | `405-<Project>_Floor_Area_Schedule_<yyyymmdd>.xlsx` | The Form 405 workbook, nine tabs. |
| 2 | `405a-<Project>_Area_Markups_<yyyymmdd>.pdf` | The A3 markup set — cover plus one sheet per level, the architect's own vector page in the BDM frame — **with a Datum project embedded**: every measured polygon is a live, calibrated area shape linked to a Workbook line. Baked, so the markups also show in Acrobat, Bluebeam and browsers. |

One take-off config (`<project>_takeoff.json`) holds the shapes. Every figure is
**derived from the shapes** on every build, so the 405a cover, its footers, the
Datum Workbook and Form 405 cannot disagree.

There is no HTML correction tool any more (retired in R4 by Director ruling of
15 October 2026). **Datum is the correction tool:** the Director drags a corner
in Datum and saves; the skill reads the file back and rebuilds both deliverables.
Corrections live in the PDF, so they travel with the file.

## Authority boundary — read first

BDM **drafts and recommends**; the Director or Senior PM **decides and issues**.

- Both files are held for sign-off. Never issue, never send to a client, lender or
  PAG. Company CLAUDE.md §5 (15/9/26): do **not** stamp DRAFT on the files or in
  the filename — the hold is a process, not a label.
- This is a **feasibility-grade** take-off, target **±2%**. It is not an
  architect-certified area schedule and not a surveyor's plan of subdivision.
  Say that on the Summary tab, every time.
- **Never guess a figure.** Site area with nothing figured on the drawings,
  apartment numbering inferred from label positions, bed counts read from room
  keys — flagged as measured-not-confirmed. If a number cannot be closed from the
  drawings, ask.
- **Never copy the architect's zones as BDM's measure without testing them.**
  They are a starting point. Overlaps, gaps and zones that stop short of or run
  past the wall face are exactly what this schedule exists to catch.

## Non-negotiable: name the authority for every measure

There is **no Australian Standard** for measuring building area. Every measure
is reported with its source, on the Summary tab and the Basis of Measurement tab:

- **FECA · UCA · GFA** → AIQS *Australian Cost Management Manual* (2022),
  Method of Measurement of Building Area. GFA = FECA + UCA.
- **GBA** → Property Council of Australia / API / REIA *Glossary of Property
  Terms*: *"the total enclosed and unenclosed area of the building at all
  building floor levels measured between the normal outside face of any
  enclosing walls, balustrades and supports"*.
- **Planning GFA** → the applicable planning scheme. Statutory; the only one
  that tests plot ratio.
- **NSA** → lot-boundary convention for a community titles scheme. A market
  convention, not a published standard — label it as such.

**The GBA trap:** GBA is *not* in the PCA *Method of Measurement for Lettable
Area* — that covers tenancy areas (NLA / GLA) only. Detail in
`references/measurement_standards.md`.

## Inputs

A PDF drawing set with floor plans for every level including basement and roof —
**the PDF as exported from CAD**, not a scan or a print-to-PDF of a print. Ask
for the **survey plan** and the **architect's own area schedule**. Source
drawings may sit in a `Source Documents` subfolder and may move between
sessions; re-find the set rather than assuming last session's path.

## Workflow

### 1. Confirm the project and the drawing set
Which project, which set, which revision, and what the figures are for — a rate,
a revenue line, a plot-ratio check, or all three. That decides which measure
leads the Summary tab. Check `00_ai_sandbox` first. **Use the current revision**
— check the drawing register / `06_Drawings & Specifications` for a later issue.

### 2. Read the drawing before measuring anything
```bash
python3 scripts/vector_takeoff.py  plans.pdf --page <n>
```
Prints the stated scale and paper, the sheet factor (A1 issued at A3 = 2), the
named layers, every grey-filled zone with its area, and which zones match an
area printed on the sheet. Then:

- **Scale.** Stated scale × sheet factor must agree with figured dimensions —
  check at least ten pairs across two sheets. Inside 0.5%, adopt the stated
  value. Worse, stop: a scale error squares into every area.
- **Architect's schedule.** Reconcile each printed line to its zone. A zone that
  matches its printed figure to ~0.05% proves the schedule was taken from it.
- **Usable vectors?** If the plan sheets have no fills, no layers and no
  linework (scanned, flattened, image-only), go to step 3b for those sheets.

### 3a. Measure from vectors (the default)
`scripts/vector_takeoff.py` — `references/method.md` sets out the order:

1. **Envelope (GBA)** from the zone outlines to the outside face, or from the
   external-wall poche outline where no zones are drawn. Union the enclosed and
   unenclosed zones; close drafting gaps under 0.5 m²; voids as deductions.
2. **Test the zones.** `overlaps()` — any area counted twice. Where an enclosed
   zone and a balcony zone overlap, the balcony zone (drawn to the glazing line)
   wins; record the overlap as a finding for the architect.
3. **Wall thickness** with `wall_depth()` — measured off the poche, per level,
   with the solid fraction of the perimeter. Basements run 300–350 mm against
   200–260 mm above; never assume.
4. **FECA** with `feca()` — to the inside face of the solid external walls and to
   the glazing line where there is no wall. Internal walls stay in. Voids out.
   Do not offset the whole outline by the wall thickness: on a glazed façade that
   understates FECA by 2–4%.
5. **UCA and the roofed test** — each balcony / terrace / carport tested against
   the slab or roof above. Open to the sky = GBA, not UCA, no GFA (`UNROOFED`).
6. **Apartments and categories** (apartment projects) — from the architect's
   zones where drawn; otherwise segment (step 3b) and snap. Apartments + core −
   light well = FECA, level by level.

Write each polygon into the take-off config with `shape_list()` (5 mm
simplification — the area moves by less than 0.01 m²). Schema in
`references/config_schema.md`.

### 3b. Raster fallback — only where a sheet has no usable vectors
`scripts/takeoff_geometry.py` (the R3 method): render, seal, flood, segment. Then
`VectorSheet.snap()` every corner onto any vector line ends that do exist. Record
on the Verification tab which sheets were measured this way and why — their
tolerance is the R3 tolerance (±1% on a clean outline, worse where terraces,
paving or landscape touch the building).

### 4. Build the 405a — deliverable 2
```bash
npm install playwright        # once per sandbox; a system Chrome/Edge also works
python3 scripts/build_405a.py  <project>_takeoff.json  405a-<Project>_Area_Markups_<yyyymmdd>.pdf
```
It derives every figure, builds the cover and sheets, embeds the Datum project,
then checks itself: Datum's `verify()`; **read-back** (every Datum Workbook line
re-worked with Datum's own formula must equal the derived figure to 0.01 m²);
**alignment** (share of polygon edges sitting on the drawing's ink — under 85%
is a placement or outline error to look at); **containment** (FECA / UCA outside
the GBA outline); then **bake** — Datum's own Save, run headless — and a second
read-back. It needs `bdm-standards` installed (it uses that plugin's
`datum-markup` library; `scripts/datum_link.py` finds it).

If the bake cannot run (no Node, no browser, no internet), the file still opens
fully in Datum; say on hand-over that the markups show in Datum only until it is
opened there and saved. Never hand-build a substitute PDF.

### 5. Build the workbook — deliverable 1
Pull the latest `405-Floor_Area_Schedule_R*.xlsx` from
`…\BDM TEMPLATES\Working Copy\400 Quantity Surveying\` (highest revision; ignore
`_Superseded`). Tab map in `references/template_map.md`. **Write the figures from
the take-off config as built** (2 dp — the form displays 1 dp), so the totals
round the way the 405a cover rounds them.

Fill the **Basis of Measurement** tab properly — including the measuring method
per sheet (vector or raster fallback), the wall thickness measured per level, and
any zone overlap found — and every row of the **Verification** tab: a check that
could not be closed is `NOT VERIFIED — <what would close it>`, never blank and
never PASS.

**Editing the controlled template:** openpyxl strips the anchored BDM logo, so
edit the worksheet XML — never re-serialise a whole worksheet part (ElementTree
renames namespace prefixes and drops declarations, and Excel then calls the file
corrupt). Splice only `<sheetData>` back into the original bytes, strip `<v>`
from formula cells, set `fullCalcOnLoad="1"`.

**`xl/calcChain.xml` is the trap that has bitten twice** — openpyxl ignores it
and LibreOffice rebuilds it silently, so a workbook passes both and is still dead
in Excel. Never certify a workbook off either alone. Never use LibreOffice on BDM
documents.

```bash
python3 scripts/validate_xlsx.py --repair  workbook.xlsx
python3 scripts/validate_xlsx.py --check   workbook.xlsx   # must print CLEAN
```

### 6. Reconcile — before you report anything
```bash
python3 scripts/verify_schedule.py  workbook.xlsx  <project>_takeoff.json  405a.pdf
```
Every figure printed on the 405a against the workbook cell it claims to come
from, the GBA authority on every sheet — and the **live Datum project** against
the workbook, so a shape moved after the workbook was built fails here. **It must
come back CLEAN.** Fix the figure, never the check.

`verify_schedule.py` assumes the apartment tabs exist. On a **single dwelling**
mark Apartment Schedule, NSA & Revenue and Unit Mix "NOT APPLICABLE — single
dwelling" and clear their rows; record on the Verification tab that you did.

### 7. Save and report
Both files go in the project's **`10_Cost Plans`** folder (company CLAUDE.md §8 —
a deliverable lives in its regular folder; Director instruction of 4 August 2026
for Forms 405/413). The take-off config and any working script go in
`00_ai_sandbox`. Superseded revisions to `ss\`. Report the headline in one line —
`GBA x · GFA (AIQS) y · NSA z` — then what is still open, including any zone
overlap or schedule error for the architect (external correspondence: drafted
and held). Update the project summary in the same pass.

Tell the Director, in one line, how to use the 405a: open it in Datum, drag a
corner, Save — then ask for the schedule to be rebuilt.

### 8. When the Director has corrected the 405a in Datum
```bash
python3 scripts/read_405a.py  405a.pdf  <project>_takeoff.json  --write <project>_takeoff_corrected.json
python3 scripts/build_405a.py <project>_takeoff_corrected.json  405a-<Project>_Area_Markups_<new yyyymmdd>.pdf
```
Then rebuild the workbook and re-run step 6. The cover's STATUS AND OPEN ITEMS
gains one bullet naming each level and measure that moved, and saying the
workbook and any cost estimate built on the earlier figures must be rebuilt. If
build reports a **containment** warning — a balcony moved without the GBA outline
— say so; do not fix the Director's geometry for him.

## Reporting rules

- Lead with **GBA** for a $/m² rate, **planning GFA** for plot ratio, **GFA
  (AIQS)** for the cost plan, **NSA** for revenue. Say which one you are giving.
- Always state the grade and tolerance. Never let a reader assume survey accuracy.
- Rate columns on the NSA tab stay **blank**. Rates are the Director's or Senior
  PM's input and live in Form 413.
- Sense ranges: NSA ÷ GBA 60–70% for apartments over basement parking; 28–35 m²
  per car bay; GBA > GFA > planning GFA, always.

## Bundled files

| File | Purpose |
|---|---|
| `scripts/vector_takeoff.py` | Vector measuring: inventory, zones by printed area, wall poche and depth, FECA to the inside face, overlap test, raster-corner snapping, shape lists. |
| `scripts/build_405a.py` | Builds deliverable 2 — cover, vector sheets, embedded Datum project — with verify, read-back, alignment, containment and bake. |
| `scripts/read_405a.py` | Reads a 405a back out of Datum; compares; writes a corrected config. |
| `scripts/layout_405a.py` | House layout and the verbatim authority text; `--blank` writes the 405a cover template. |
| `scripts/datum_link.py` | Finds the `datum-markup` library in the bdm-standards plugin. |
| `scripts/takeoff_geometry.py` | Raster fallback (the R3 method) for sheets without usable vectors. |
| `scripts/verify_schedule.py` | Reconciles the 405a — printed figures and live Datum project — against the workbook. Exit 0 = clean. |
| `scripts/validate_xlsx.py` | Excel-strict workbook check and repair. Mandatory. |
| `scripts/make_fixture.py` | Synthetic vector set with hand-worked figures (one sheet rotated) — run before trusting a change. |
| `references/measurement_standards.md` | The definitions, who publishes them, what standing they carry. |
| `references/method.md` | Vector method, raster fallback, tolerances, traps, cross-checks. |
| `references/config_schema.md` | The take-off config JSON. |
| `references/template_map.md` | Form 405 tab and cell map, filing and naming. |

## Not this skill

Cost estimates and elemental checks (Forms 410–413) · QS Initial Report
(Form 424) · QS Monthly Progress Valuation (Form 425) · Progress Certificate
(Form 335) · DA conditions tracking · general drawing markups (use
`bdm-standards:datum-markup`).
