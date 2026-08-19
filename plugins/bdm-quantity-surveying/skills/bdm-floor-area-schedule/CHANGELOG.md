# CHANGELOG — Floor Area Schedule Skill

## R3 / 2026-08 — the live tool made general; the PDF exporter written

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

## R2 / 2026-08 — Excel integrity gate; library copy resynced

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

## R1 / July 2026 — first issue

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
