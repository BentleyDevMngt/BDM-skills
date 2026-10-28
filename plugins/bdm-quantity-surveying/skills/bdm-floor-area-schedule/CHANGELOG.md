# CHANGELOG — Floor Area Schedule Skill

## R4.0 / 2026-10 — measure from vectors; Datum replaces the HTML tool

Director rulings of 15 October 2026, on the assessment of 14 October 2026
(`Projects - Documents\Alfred\BDM_Datum_Floor_Area_Skill_Assessment_2026-10-14.docx`):
(1) adopt vector-first measurement with Datum; (2) drop the HTML live-correction
tool but **keep the A3 markup PDF** as a deliverable; (3) use the current
`datum-markup` skill.

Why. On the October test job (a three-level house, design-development set) the
R3 method run unaided was −46%, +17% and +2.4% on the three levels and read the
external walls at 25–36 mm: it could not tell an open terrace or a hatched garden
from the building, and its wall reading came from a picture. Measuring from the
PDF's own zones and wall poche matched the architect's zones to 0.03% and found a
4.91 m² double count in the architect's own schedule.

Changes:

- **Deliverables are now two:** the Form 405 workbook, and the **405a A3 markup
  PDF, which is also a live Datum file** — the architect's vector page in the BDM
  frame, every measured polygon an editable, calibrated Datum area shape linked to
  a Workbook line, baked so the markups show in any PDF viewer. Supersedes the
  17 August 2026 standing rule that every take-off ships with the HTML tool.
- **Added `scripts/vector_takeoff.py`** — sheet inventory (scale, sheet factor,
  layers, zones matched to printed areas), zones by printed figure, wall poche and
  measured wall depth with solid fraction, FECA to the inside face (glazed runs
  carry no band; internal walls stay in; voids out), zone-overlap test, and
  snapping raster corners onto vector line ends.
- **Added `scripts/build_405a.py`** — derives every figure from the shapes, builds
  the cover and sheets, embeds the Datum project, and checks itself: Datum
  `verify()`, read-back with Datum's formula (0.01 m²), polygon-on-ink alignment,
  GBA containment, bake, and a second read-back. Rotated source sheets are
  normalised before placement (`show_pdf_page` ignores /Rotate).
- **Added `scripts/read_405a.py`** — the correction loop. Reads the Director's
  corrections out of the saved 405a, compares, and writes a corrected config; the
  cover then names what moved.
- **Added `scripts/layout_405a.py`** (the house layout and authority text, moved
  out of `build_markups.py`) and **`scripts/datum_link.py`** (finds the
  `datum-markup` library in bdm-standards rather than copying it).
- **`verify_schedule.py`** also reconciles the live Datum project against the
  workbook, so a shape moved after the workbook was built fails the check.
- **`make_fixture.py`** rewritten: a vector set with zones, a named wall layer, a
  glazed run and a rotated sheet; prints the hand-figure check (GBA 228.00 /
  240.00, FECA 216.56, UCA 12.00).
- **Retired:** `build_live_takeoff.py`, `export_live_pdf.py`, `build_markups.py`.
  `takeoff_geometry.py` stays, as the raster fallback for sheets with no usable
  vectors.
- **Filing and marking aligned to company CLAUDE.md:** both files to
  `10_Cost Plans`; no DRAFT stamp or `_DRAFT` filename (§5, 15/9/26).

Verified: fixture from a clean directory — every hand figure to 0.00 m², alignment
93% on both sheets including the rotated one, read-back clean before and after
bake (Datum v3.45). Test job — three levels built and baked, alignment 92–95%,
read-back clean; a corner moved in the saved file read back as +1.27 m² UCA, the
corrected config rebuilt with the cover bullet and a containment warning (balcony
moved without the GBA outline); `verify_schedule.py` CLEAN on a matching workbook
and FAILED on the moved shape. Workbook build itself unchanged from R3 and not
re-run in this test.

## R3.0 / 2026-08 — the live tool made general; the PDF exporter written

Found on the portability audit before the skills library was packaged as a
plugin. The skill could not have run on any machine but the one it was written
on.

**`scripts/build_live_takeoff.py` was a working script from one job, dressed as a
tool.** It hardcoded a sandbox session path, the 79 Seagull Avenue tender PDF,
that drawing's clip rectangle and level-to-page map, and `plates/*.npy` masks by
name; it imported `takeoff` and `dawson_lines`, neither of which was ever in the
folder; and `main()` took no arguments at all, while SKILL.md documented it as
taking `takeoff.json`. It would have failed on first run for every user.

**`scripts/export_live_pdf.py` did not exist.** SKILL.md referenced it twice and
described its behaviour in detail, so the third deliverable — the A3 markup set —
could not be produced at all.

Changes:

- **`build_live_takeoff.py` now reads the take-off config**, per its documented
  signature. Every project figure comes from the config; nothing about a job is
  compiled in. Added a `live` block to the config carrying the source PDF, and a
  page and plate mask per level, documented in `references/config_schema.md`.
  Render dpi, drawing scale, mask dpi, clip, vertex budget and area tolerance are
  all config with the previous hardcoded values as defaults, so the measurement
  behaviour is unchanged.
- **The single-job assumptions came out.** Off-plate UCA was applied with
  `if level == 'Ground'`; it is now `uca_offplate` per level. The wall-thickness
  band is derived as `gba − feca − uca − unroof` rather than carried, so it
  cannot disagree with the workbook. Sheet numbers were computed from the PDF page
  index; they are now config.
- **The builder's name came out of the interface.** `dawsonEx` / `bdmRate` are
  `tenderEx` / `benchRate`, fed from a `rates` block with the tenderer's own
  label. Where a project has no tender or budget figure the rate panel says so
  instead of printing `$Infinity/m²`.
- **The markup cover reconciles properly.** NSA and Apts were hardcoded to dashes
  and the cover asserted "one dwelling on one lot" whatever it was reading. Both
  now come from the config's `apartments`.
- **STATUS AND OPEN ITEMS is config-driven.** Seven bullets specific to 79 Seagull
  Avenue were compiled into the print builder — including a site-area confirmation
  and an external-works figure that belonged to that job alone. The block now
  prints `open_items`, with the corrected-levels bullet inserted after the first
  item where a level has moved, exactly as SKILL.md specifies.
- **Added `scripts/export_live_pdf.py`** — headless Chromium loads the tool, waits
  on the totals panel rather than a timer (so a slow machine cannot produce a set
  of blank plans), calls the tool's own `buildPrint()`, and prints at 420 × 297 mm
  with `prefer_css_page_size`. It fails loudly and exits non-zero if Chromium
  cannot launch, naming the `libXdamage.so.1` workaround. It never hand-builds a
  substitute PDF.
- **Added `scripts/make_fixture.py`** — a synthetic 1:100 drawing set, plate masks
  and config. The building is 20 × 12 m with a 4 × 3 m notch, so the polygon the
  tool opens with can be checked against 228.0 m² worked out by hand. Run it
  before trusting a change to the pipeline.

Verified end to end on the fixture from a clean directory: plate 227.9 m²,
polygon 227.7 m² at 6 vertices (+0.11%, inside the 0.12% rule), snap targets
found on both axes, NSA 186.0 / 106.0 / 292.0 and apartment counts reconciling to
the config, and a 3-page PDF at 420 × 297 mm — cover plus one sheet per level —
with the house layout and both authority blocks intact.

No change to the measurement method, the standards citations, the Form 405 tab
map, or the HTML tool's own behaviour in the browser.

## R2.0 / 2026-08 — Excel integrity gate; library copy resynced

Issued 17 August 2026 after two BDM workbooks were delivered that Excel reported as
corrupt (167 Hedges Avenue, Form 405 and Form 413).

**Root cause: a stale `xl/calcChain.xml`.** calcChain is a precomputed index naming every
formula cell. Populating a controlled template turns template formulas into hard values
constantly, and the index still names them — Excel walks it on open and reports unreadable
content. **openpyxl ignores calcChain entirely and LibreOffice rebuilds it silently on
convert**, so the workbooks passed an openpyxl load, a LibreOffice recalc and the R1
validation checklist, and were still dead in Excel. The R1 checklist named XML parsing,
`mc:Ignorable` prefixes, `ns\d+` prefixes, content-types, rels and media — but not calcChain.

Changes:

- **Added `scripts/validate_xlsx.py`** — Excel-strict check and repair. Covers stale
  calcChain, stale `<dimension>` after appending rows, orphaned shared formulas, namespace
  and `mc:Ignorable` integrity, content-type and rel resolution, `xl/media/` presence,
  duplicate cell refs, cells in the wrong row, `inlineStr` with no `<is>`. Self-tested
  against a deliberately broken file.
- **Step 4 of the workflow now mandates** `--repair` then `--check`, and states plainly that
  a workbook is not verified until `--check` returns CLEAN.
- **Resynced the library copy to the installed skill.** The R1 folder had drifted badly
  behind: it described two deliverables rather than three, carried no live-correction tool,
  and was missing the XML-splice guidance entirely. SKILL.md and `references/config_schema.md`
  replaced from the installed version.
- **Bundled `scripts/build_live_takeoff.py`**, which SKILL.md referenced but which had never
  been packaged — it lived only in the author's personal folder.

No change to the measurement method, the standards citations or the Form 405 tab map.

## R1.0 / July 2026 — first issue

Built from the pilot project feasibility
take-off, July 2026. That job measured GBA, GFA and NSA across a mid-rise apartment building from a DA set carrying **no** architect's
area schedule and **no** figured site area — which is the normal starting point
and the reason this skill exists.

### What went into it

- **The measurement method.** Areas are isolated by selecting the architect's
  own vector linework — wall poche, balcony hatch, structural strokes — rather
  than by tracing pixels. Repeatable and auditable.
- **The authority position.** There is no Australian Standard for measuring
  building area, so every measure is reported with its source. The
  standing-of-definitions table in `references/measurement_standards.md` is the
  reusable part: it settles which body defines what and what weight each
  citation carries.
- **The reconciliation.** One config JSON feeds both the workbook and the markup
  set, and `verify_schedule.py` checks every printed figure against the
  workbook cell it claims to come from. ~200 checks on a five-level job.

### Lessons from the pilot that are now built in

- **GBA is not in the PCA Method of Measurement for Lettable Area.** That
  publication covers tenancy areas (NLA / GLA). GBA comes from the PCA / API /
  REIA *Glossary of Property Terms*. The Summary tab now carries that reference
  in three places — the intro line, the column header and the headline-metric
  label — plus the quoted definition in a basis note under the level table.
  The first cut of the pilot project workbook qualified GFA but not GBA; the verifier
  now fails if that reference is missing.
- **The roofed test is where the money is.** Level 4 at the pilot project is set back, so
  154.4 m² of Level 3 balcony is open to the sky — GBA, not UCA, no GFA. Every
  balcony is now tested geometrically against the slab above, and against the
  roof outline at the top level.
- **Measure the wall thickness, don't assume it.** The pilot project ran 203 mm above ground
  and 320 mm at basement. Assuming a single value would have moved the basement
  by roughly 50 m².
- **The ground floor is the weak level.** Where the building, its terraces and
  the site paving are drawn as one continuous surface, manual cut lines are
  needed and the tolerance drops to ±3% against ±1% elsewhere. It is called out
  as the level worth a hand check rather than buried.
- **Internal areas can carry the balcony hatch.** The pilot project's Level 3 lift lobby
  (27.8 m²) did. Regions are now tested for whether they touch the building
  perimeter before being classified as UCA.
- **Base-14 PDF fonts drop m² and em-dash.** The markup builder embeds Carlito
  (Calibri-metric) and refuses to run without an embeddable sans font. Likewise
  OpenCV's Hershey fonts are ASCII-only — plan annotations use ASCII hyphens,
  not em-dashes, or they render as `???`.

### Deliberately not automated

Rate columns on the NSA tab stay blank. This schedule measures area; it does not
set price. Rates are the Director's or Senior PM's input.

### Known limits

- Feasibility grade, ±2%. Not an architect-certified area schedule and not a
  surveyor's plan of subdivision.
- FECA via a uniform inward offset understates by 0.5–1% where the façade is
  glazed rather than solid.
- The roofed test does not pick up eaves or soffit overhangs beyond the slab
  line, so UCA is marginally understated.
- Apartment segmentation is a starting point. Every level must be checked
  visually against the plan before the areas are used.

### Companion templates filed with this release

`…\BDM TEMPLATES\Working Copy\400 Quantity Surveying\`

- `405-Floor_Area_Schedule_R1_2026-07.xlsx`
- `405a-Area_Markup_Cover_R1_2026-07.pdf`
