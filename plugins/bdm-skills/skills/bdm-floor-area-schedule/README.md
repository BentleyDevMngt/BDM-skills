# bdm-floor-area-schedule

Measures a floor area schedule off architectural drawings and produces the BDM
**Form 405** workbook plus an A3 marked-up plan set that reconciles to it.

Built July 2026 from the pilot project feasibility take-off.

## What you get

| Output | Detail |
|---|---|
| **Form 405 workbook** | Nine tabs — Summary · Level Schedule · Area by Category · Apartment Schedule · NSA & Revenue · Unit Mix · Site & Parking · Basis of Measurement · Verification |
| **A3 markup PDF** | Cover sheet reconciling to the workbook, then measured-area, area-by-category and apartment-segmentation sheets, with NSA per unit printed on the plan |
| **Take-off config** | One JSON holding every measured figure — feeds both outputs, so they cannot disagree |

Both held as **DRAFT** for Director sign-off. Feasibility grade, target ±2%.

## What's in the package

```
SKILL.md                              triggers, authority boundary, workflow
README.md                             this file
INSTALL.md                            how to install and verify
CHANGELOG.md                          revision history
scripts/takeoff_geometry.py           scale, layer selection, envelope, FECA offset,
                                      roofed test, apartment segmentation
scripts/build_markups.py              builds the A3 markup PDF (--blank cuts the template)
scripts/verify_schedule.py            reconciles the markup against the workbook
references/measurement_standards.md   the definitions, who publishes them, what standing
                                      they carry, and which number to hand over for what
references/method.md                  take-off method, tolerances, traps, cross-checks
references/config_schema.md           the take-off config JSON
references/template_map.md            Form 405 tab and cell map, filing and naming
(pilot take-off config held with the project, not in this skill)
```

## Templates it uses

`…\BDM TEMPLATES\Working Copy\400 Quantity Surveying\`

- `405-Floor_Area_Schedule_R*.xlsx` — the workbook
- `405a-Area_Markup_Cover_R*.pdf` — the markup cover sheet

Always pull the highest revision; ignore `_Superseded`.

## The one thing to take away

There is **no Australian Standard** for measuring building area. Every figure
must be reported with its source. GFA (FECA + UCA) comes from the AIQS
*Australian Cost Management Manual*; **GBA comes from the Property Council /
API / REIA *Glossary of Property Terms***, not from the PCA *Method of
Measurement for Lettable Area* — that covers tenancy areas only, and citing it
for GBA is the most common mistake in the field.

## Dependencies

Python: `pymupdf`, `opencv-python-headless`, `numpy`, `scipy`, `scikit-image`,
`openpyxl`. An embeddable sans font (Carlito, Liberation or DejaVu) — the PDF
base-14 fonts silently drop the m² and em-dash glyphs. All present in the
Cowork sandbox.
