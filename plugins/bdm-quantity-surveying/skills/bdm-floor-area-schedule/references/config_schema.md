# Take-off config (`<project>_takeoff.json`) — R4

One file holds every measured **shape**. `build_405a.py` derives every figure from
the shapes on each build and writes the figures back into the file, so the 405a
cover, its sheet footers, the embedded Datum project and the Form 405 workbook
all come from one set of numbers. Keep it in the project's `00_ai_sandbox`.

```json
{
  "project":        "Pearl Runaway Bay",
  "address":        "24 Oatland Ave, Runaway Bay",
  "approval":       "DA MIN/2023/681",
  "issue_date":     "29 July 2026",
  "workbook":       "405-Pearl_Floor_Area_Schedule_20260729.xlsx",
  "logo":           "/path/to/bdm-logo.png",
  "planning_scheme": "Gold Coast City Plan",
  "planning_gfa":   4113.6,
  "drawing_source": "575100 DA set rev C, Rothelowman — A2.101–A2.106",

  "source_pdf":     "Source Documents/575100_DA_C.pdf",
  "scale":          100,
  "sheet_factor":   2,

  "levels": [
    {"name": "Basement", "page": 4, "sheet": "A2.101",
     "clip": [150, 120, 2240, 1560],
     "shapes": {
       "GBA":      [{"pts": [[x, y], …], "deduct": false}],
       "FECA":     [{"pts": [[x, y], …], "deduct": false},
                    {"pts": [[x, y], …], "deduct": true}],
       "UCA":      [],
       "UNROOFED": []
     }}
  ],

  "apartments": [
    {"apt": "01", "level": "Ground",
     "shapes": {"internal": [{"pts": …}], "balcony": [{"pts": …}]}}
  ],

  "category_shapes": {
    "Basement": {"car park, bays, aisles & ramp": [{"pts": …}], "plant room": [{"pts": …}]}
  },

  "sheets": [
    {"level": "Basement", "kind": "mk"},
    {"level": "Basement", "kind": "cat", "note": "How these rooms roll into the workbook's categories."},
    {"level": "Ground",   "kind": "apt"}
  ],

  "open_items": [
    "Held for Director sign-off and for reconciliation against the architect's own area schedule.",
    "Source: …", "Scale verified …"
  ]
}
```

## Field notes

**Coordinates.** Every `pts` list is in PDF points on the **source** page, display
space (rotation applied, origin top-left, y down) — exactly what
`vector_takeoff.py` returns. Do not repeat the first point. `deduct: true` makes
the shape subtract (voids, light wells, ramps at grade). `shape_list()` writes
polygons-with-holes this way.

**`scale`, `sheet_factor`** — the drawing scale denominator and the ratio of the
paper the scale is stated at to the paper issued (A1 issued at A3 = 2). Both can
be overridden per level. Measuring scale N = scale × sheet_factor.

**`levels[].page`** — zero-based page in `source_pdf`. **`clip`** (optional) —
`[x0, y0, x1, y1]` in source points: the part of the sheet placed in the 405a
frame. Omit to place the whole sheet; clip to zoom the plan when the title block
and site plan take most of the sheet. Calibration follows the placement
automatically.

**`levels[].shapes`** — `GBA` and `FECA` are required on every level; `UCA` and
`UNROOFED` as measured. Figures derived per level: `gba`, `feca`, `uca`,
`unroof`, `gfa` (= feca + uca), `apts`. The external wall band is `gba − feca −
uca − unroof`, never carried.

**`apartments`** — `internal` and `balcony` derived from the shapes. TOTAL NSA is
`internal + balcony` everywhere it appears. `level` must match a level name.

**`category_shapes`** — keyed by level, then readable lower-case descriptions
(they print verbatim). Derived into `categories`; values must sum to the level's
FECA.

**`sheets`** — one 405a sheet each. `kind`:

| kind | sheet | Datum Workbook lines | footer carries |
|---|---|---|---|
| `mk` | measured areas — FECA / UCA / GBA | `GBA — <level>`, `FECA — <level>`, `UCA — <level>`, `Unroofed — <level>` | FECA + UCA = GFA, GBA, and the AIQS / PCA references |
| `cat` | area by category, FECA basis | `FECA · <description> — <level>` | the categories and how they sum to FECA |
| `apt` | apartment segmentation | `NSA internal — Apt <n>`, `NSA balcony — Apt <n>` | NSA per unit and the level total |

The Workbook line names are how `read_405a.py` maps Datum back to the schedule.
Renaming a line in Datum breaks that mapping — tell the Director not to.

**`open_items`** — STATUS AND OPEN ITEMS on the cover, verbatim. Lead with the
hold line. Add the drawing source, the scale verification, any zone overlap or
schedule error, and anything measured-but-unconfirmed. Never drop an item to tidy
the page. Where `corrections` exist, one bullet naming each level, measure and
movement is inserted after the first item automatically.

## Written by the tools — do not edit by hand

| key | written by | |
|---|---|---|
| `levels[].gba / feca / uca / unroof / gfa`, `apartments[].internal / balcony`, `categories` | `build_405a.py` | derived from the shapes on every build |
| `levels[]._containment` | `build_405a.py` | m² of FECA / UCA / unroofed outside the GBA outline |
| `_frames` | `build_405a.py` | where each source page sits on the 405a sheet — needed to read corrections back |
| `corrections` | `read_405a.py --write` | each level / measure moved in Datum, from → to |

## Usage

```bash
python3 scripts/vector_takeoff.py  plans.pdf --page 5
python3 scripts/build_405a.py      takeoff.json  405a-<Project>_Area_Markups_<yyyymmdd>.pdf
python3 scripts/read_405a.py       405a.pdf  takeoff.json  [--write corrected.json]
python3 scripts/verify_schedule.py workbook.xlsx  takeoff.json  405a.pdf
```

To exercise the pipeline without a job:

```bash
python3 scripts/make_fixture.py  /tmp/fx                 # prints the hand-figure check
python3 scripts/build_405a.py    /tmp/fx/testbed_takeoff.json  /tmp/fx/405a-Testbed_Area_Markups.pdf
python3 scripts/read_405a.py     /tmp/fx/405a-Testbed_Area_Markups.pdf  /tmp/fx/testbed_takeoff.json
```
