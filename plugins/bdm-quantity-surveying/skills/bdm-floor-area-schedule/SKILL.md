---
name: "bdm-floor-area-schedule"
description: "Measure a floor area schedule from architectural drawings and produce exactly three deliverables — the BDM Form 405 workbook, an interactive live-correction HTML tool, and an A3 markup PDF exported from that tool. Trigger on 'floor area schedule', 'area schedule for [project]', 'area take-off', 'measure the areas off the plans', 'GBA / GFA / NSA', \"what's the GFA\", 'net sellable area', 'NSA by unit', 'unit mix and areas', 'how many m2 is the building', 'site cover and plot ratio', or whenever DA / design-development plans are handed over with a request to work out areas for a feasibility, a $/m2 rate, a revenue line or a plot-ratio check. All three held as DRAFT for Director sign-off. NOT for cost estimates (Forms 410-413), QS lender reports (Forms 424 / 425) or progress certificates (Form 335)."
---

# Floor Area Schedule — BDM Form 405

## What this does and why

Someone hands over a set of architectural plans and wants to know how big the
building is — for a $/m² rate, a revenue line, a plot-ratio check, or a
feasibility that is about to go to a client or a lender. The drawings usually
carry **no area schedule and no figured site area**, so every figure has to be
measured.

## The three deliverables — and only three

| # | File | What it is |
|---|---|---|
| 1 | `405-<Project>_Floor_Area_Schedule_DRAFT_<yyyymmdd>.xlsx` | The Form 405 workbook, nine tabs. |
| 2 | `<Project>_Area_Takeoff_LIVE_DRAFT_<yyyymmdd>.html` | The live correction tool — the Director drags corners, areas and rates move, corrections auto-save. |
| 3 | `405a-<Project>_Area_Markups_ASMM_DRAFT_<yyyymmdd>.pdf` | The A3 markup set, **rendered from file 2**. |

File 3 is produced by driving file 2's own print path — never hand-built
alongside it. One document, not two that can drift. Do not issue a separate
`build_markups.py` PDF as a fourth deliverable.

You (Claude) do the judgement — which linework is which, where a balcony is
roofed, whether a region is core or apartment. The bundled scripts do the
deterministic work: geometry, the tool, the PDF render, and the reconciliation.

## Authority boundary — read first

BDM **drafts and recommends**; the Director or Senior PM **decides and issues**.

- Everything stays **DRAFT**. Cover, footers and filename all say so. Never
  issue, never send to a client, lender or PAG.
- This is a **feasibility-grade** take-off, target **±2%**. It is not an
  architect-certified area schedule and not a surveyor's plan of subdivision.
  Say that on the Summary tab, every time.
- **Never guess a figure.** Site area with nothing figured on the drawings,
  apartment numbering inferred from label positions, bed counts read from room
  keys — flagged as measured-not-confirmed, not quietly reported as fact. If a
  number cannot be closed from the drawings, ask.

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
Area* — that covers tenancy areas (NLA / GLA) only. Citing it there is the
single most common mistake. Detail in `references/measurement_standards.md`.

## Inputs

A PDF drawing set with floor plans for every level including basement and roof.
Ask for the **survey plan** and the **architect's own area schedule** — they
close out two of the three items that otherwise stay flagged. Source drawings
may sit in a `Source Documents` subfolder and may be moved between sessions;
re-find the set rather than assuming last session's path.

## Workflow

### 1. Confirm the project and the drawing set
Which project, which set, which revision, and what the figures are for — a rate,
a revenue line, a plot-ratio check, or all three. That last answer decides which
measure leads the Summary tab. Check `00_ai_sandbox` first.

### 2. Verify the scale before measuring anything
Compute the theoretical px/m, then measure it against 30+ figured dimension
pairs across at least two sheets. Inside 0.5%, adopt the exact theoretical
value. Worse, stop — a scale error squares into every area. Cross-check a
dimension chain's arithmetic against its drawn span as well.

### 3. Measure, level by level
Envelope (GBA) → measured wall thickness → inward offset (FECA) → balcony layer
→ roofed test against the slab above → light-well deductions → apartment
segmentation → categories. `scripts/takeoff_geometry.py` provides each step;
`references/method.md` sets out the order, tolerances and traps.

The two that cost most if you get them wrong:
- **The roofed test.** Where an upper level is set back, the balcony below is
  open to the sky — GBA, not UCA, no GFA. Often 100–200 m² on one level.
- **Wall thickness.** Measure per level. Basements run 300–350 mm against 200 mm
  above; that is 40–60 m² on a single level.

**The contour catches annotation.** Window and door tags, swings, dimension
leaders and hose-cock symbols hanging off a wall get swept into the traced
envelope as spikes — on one five-bedroom level that was 9 corners and 5.5 m².
Check every level at zoom, and ship the spike finder (step 5) so the Director
can clear the rest himself.

### 4. Build the workbook — file 1
Pull the latest `405-Floor_Area_Schedule_R*.xlsx` from
`…\BDM TEMPLATES\Working Copy\400 Quantity Surveying\` (highest revision; ignore
`_Superseded`). Tab-by-tab map in `references/template_map.md`. One JSON config
holds every measured figure and feeds all three files, which is why they cannot
disagree — schema in `references/config_schema.md`.

Fill the **Basis of Measurement** tab properly and every row of the
**Verification** tab: a check that could not be closed is recorded as
`NOT VERIFIED — <what would close it>`, never blank and never marked PASS.

**Editing the controlled template:** openpyxl strips the anchored BDM logo, so
edit the worksheet XML — but never re-serialise a whole worksheet part.
ElementTree renames namespace prefixes (`mc` → `ns1`, `x14ac` → `ns3`) and drops
declarations for prefixes no element uses (`xr2`, `xr3`); `mc:Ignorable` then
names undeclared prefixes and **Excel calls the file corrupt**, while openpyxl
and LibreOffice read it happily. Splice only the `<sheetData>` block back into
the original bytes, strip `<v>` from formula cells, set `fullCalcOnLoad="1"`,
and validate with `scripts/validate_xlsx.py` before handing over.

**`xl/calcChain.xml` is the trap that has bitten twice.** It is a precomputed
index naming every formula cell. Populating a form turns template formulas into
hard values constantly, and the index still names them — Excel walks it on open,
finds entries pointing at cells with no formula, and reports the file as
unreadable. **openpyxl ignores calcChain entirely and LibreOffice rebuilds it
silently on convert**, so a workbook passes an openpyxl load AND a LibreOffice
recalc and is still dead in Excel. Never certify a workbook off either alone.

```bash
python3 scripts/validate_xlsx.py --repair  workbook.xlsx   # drops the stale calcChain, fixes <dimension>
python3 scripts/validate_xlsx.py --check   workbook.xlsx   # must print CLEAN
```

`--repair` deletes `xl/calcChain.xml` outright (plus its content-type override
and rel); Excel rebuilds it on open. `--check` covers namespace and
`mc:Ignorable` integrity, autogenerated `ns\d+` prefixes, content-type and rel
resolution, `xl/media/` still present, stale calcChain, stale `<dimension>` after
appending rows, orphaned shared formulas (never overwrite the master cell of an
`<f t="shared" ref=".." si="N">` group), duplicate cell refs, cells in the wrong
row, and `inlineStr` with no `<is>`. **A workbook that has not returned CLEAN has
not been verified.**

### 5. Build the live correction tool — file 2
```bash
python3 scripts/build_live_takeoff.py  takeoff.json  <Project>_Area_Takeoff_LIVE_DRAFT_<yyyymmdd>.html
```
One self-contained HTML file — no licence, no server, no install. Each level
carries the plan raster, the measured plate as a draggable polygon, and the
drawing's own axis-aligned linework as snap targets. A PDF cannot do this — a
polygon there is static artwork and will not recalculate.

Rules, each learned the hard way:

- **Open within 0.2% of the workbook figure.** Choose the *closest-on-area*
  simplification inside the vertex budget, not the coarsest inside a loose
  tolerance. A polygon that opens off the reported number makes every later
  delta a lie. Say on the page that Δ is measured against the workbook.
- **Keep the vertex count draggable** — roughly 20–48.
- **Model deductions as explicit editable fields**, never folded into the
  polygon: `GBA = polygon − deductions (ramp at grade, light wells, voids)
  + UCA measured off-plate`. Fitting the polygon to a post-deduction figure
  hides a fudge inside the geometry.
- **Snap independently in x and y** to long axis-aligned segments, Shift to
  override.
- **Zoom and pan are required.** A corner cannot be placed on the right wall
  face at fit-to-page. Wheel zoom about the cursor, right/middle-drag to pan,
  `+ − 0` keys, live zoom %. Render plans at ~220 dpi; draw handles and line
  weights at constant *screen* size (divide by the zoom factor); clamp the pan.
- **Multi-select delete with undo.** Shift+drag a marquee, Delete removes the
  lot and the polygon re-closes. Alt+click for one. Ctrl+Z restores.
- **Spike finder that selects, never deletes.** Annotation caught by the contour
  gives a corner with **both** adjacent edges short (< ~2.2 m) and real
  deviation from the chord (> ~0.4 m); a genuine wall step always has one long
  edge. Select the candidates, report the area impact, let the Director confirm.
- **Corrections must survive closing the file.** A `file://` page cannot write
  back to itself, so auto-save to `localStorage` on a debounce, keyed on
  **project + lot, not the file path**, so renaming or re-issuing the tool does
  not lose the work. On load, restore and show a banner saying when it was
  saved, with a Discard button. Stamp the saved state with the baseline GBA it
  was corrected against — if a re-issued tool has a different baseline, **do not
  apply silently**: warn that the measurement underneath has changed and let the
  Director choose. Show a live "Saved hh:mm" indicator, and if storage is
  blocked say so loudly and point at the download button.

Show the live $/m² on screen where a tender or budget figure exists — watching
the rate move as a boundary is corrected is the point. That is a **screen**
feature; it does not go in the printed set.

### 6. Render the PDF from the tool — file 3
```bash
python3 scripts/export_live_pdf.py  <tool.html>  405a-<Project>_Area_Markups_ASMM_DRAFT_<yyyymmdd>.pdf
```
Headless Chromium loads the tool, waits for the plans, calls the tool's own
`buildPrint()`, and prints at 420 × 297 mm with `prefer_css_page_size`. The PDF
is therefore the tool's output, not a parallel build.

The export must reproduce the house markup layout exactly:
- **Cover** — `RECONCILIATION TO THE WORKBOOK` including NSA and Apts columns,
  `SHEET INDEX`, the three `BASIS AND AUTHORITY` blocks (FECA · UCA · GFA, GBA,
  NSA) verbatim, and `STATUS AND OPEN ITEMS`. Where a level has been corrected,
  add **one** status bullet naming the levels and movement and saying the
  workbook and any cost estimate must be rebuilt. Do not invent headings.
- **One sheet per level** — plan with the polygon, footer reading `<Level>:
  FECA x + UCA y = GFA z m² · GBA g m² — as reported on the Level Schedule tab
  of <workbook>`, then the AIQS / Property Council authority line.
- **No cost page and no extra notes page.** Rates live in Form 413.

Set a **correction threshold above the simplification noise** (~1 m²). Below it,
report the delta but do not call the level "corrected".

Environment notes: `pip install playwright --break-system-packages` then
`python3 -m playwright install chromium`. `install-deps` fails without root —
the only missing library is `libXdamage.so.1`; `apt-get download libxdamage1`,
`dpkg-deb -x` it and put it on `LD_LIBRARY_PATH`. If the render cannot run, say
so — do not hand-build a substitute PDF.

The headless render reflects the **as-measured** areas. The Director's own
corrections live in his browser; when he prints from there he gets his corrected
set. Say which one you are handing over. Tell him the print-dialog settings for
his own prints: Save as PDF, paper size **A3**, landscape, margins none, scale
100 (not Fit), background graphics on, headers and footers off — at A4 every
sheet comes out rotated.

### 7. Reconcile — before you report anything
```bash
python3 scripts/verify_schedule.py  workbook.xlsx  takeoff.json  markups.pdf
```
Every figure printed on a drawing checked against the workbook cell it claims to
come from, both ways, plus internal reconciliations and the GBA authority on
every sheet. **It must come back CLEAN.** If it does not, fix the figure — never
the check.

`verify_schedule.py` assumes an apartment project and needs a per-unit NSA loop.
On a **single dwelling** it fails on the apartment block — write a
project-specific reconciliation covering the same ground (config against
workbook, categories against FECA, GBA − band − unroofed = GFA, every markup
figure against its workbook cell) and record on the Verification tab that you
did so and why.

Exercise the tool headlessly before handing it over — stub the DOM under node
and assert that zooming does not change an area, that marquee-select and Delete
leave a closed polygon, that undo restores, that a correction written in one
session is restored in a fresh one, and that the print builder emits the
expected page count with a plan on every level sheet.

### 8. Save and report
All three files to the project's `…\00_ai_sandbox\`, never a Projects root and
never a stray folder. Superseded revisions go to `ss\`. Report the headline in
one line — `GBA x · GFA (AIQS/ASMM) y · NSA z` — then what is still open. Update
the project summary in the same pass.

## Reporting rules

- Lead with **GBA** for a $/m² rate, **planning GFA** for plot ratio, **GFA
  (AIQS)** for the cost plan, **NSA** for revenue. Say which one you are giving.
- Always state the grade and tolerance. Never let a reader assume survey accuracy.
- Hand over all three files together and say in one line what the tool is for:
  drag a corner, watch the rate move, corrections save themselves, re-print the
  set, send back the corrected config.
- Rate columns on the NSA tab stay **blank**. This schedule measures area; it
  does not set price. Rates are the Director's or Senior PM's input.
- Sense ranges: NSA ÷ GBA 60–70% for apartments over basement parking;
  28–35 m² per car bay; and GBA > GFA > planning GFA, always.

## Bundled files

| File | Purpose |
|---|---|
| `scripts/takeoff_geometry.py` | Drawing class — scale, layer selection, envelope, wall thickness, FECA offset, roofed test, segmentation. |
| `scripts/build_live_takeoff.py` | Builds file 2 — zoom and pan, snapping, marquee delete, spike finder, undo, auto-save, live rates, and the A3 print view. |
| `scripts/export_live_pdf.py` | Renders file 3 from file 2 via headless Chromium. |
| `scripts/build_markups.py` | Legacy direct PDF builder. Kept for reference only — the issued PDF now comes from the tool. |
| `scripts/verify_schedule.py` | Reconciles the markup PDF against the workbook. Exit 0 = clean. |
| `scripts/validate_xlsx.py` | **Excel-strict workbook check and repair** — stale calcChain, stale `<dimension>`, orphaned shared formulas, namespace integrity, logo media. Run `--repair` then `--check` on the Form 405 workbook before handing it over. Mandatory. |
| `references/measurement_standards.md` | The definitions, who publishes them, what standing they carry. |
| `references/method.md` | Take-off method, tolerances, traps, cross-checks. |
| `references/config_schema.md` | The take-off config JSON. |
| `references/template_map.md` | Form 405 tab and cell map, filing and naming. |

Working reference copies of `build_live_takeoff.py` and `export_live_pdf.py` are
kept in the user's own folder under `Projects - Documents\Alfred\scripts\`.

## Not this skill

Cost estimates and elemental checks (Forms 410–413) · QS Initial Report
(Form 424) · QS Monthly Progress Valuation (Form 425) · Progress Certificate
(Form 335) · DA conditions tracking.

