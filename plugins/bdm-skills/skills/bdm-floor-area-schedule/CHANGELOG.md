# CHANGELOG — Floor Area Schedule Skill

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
