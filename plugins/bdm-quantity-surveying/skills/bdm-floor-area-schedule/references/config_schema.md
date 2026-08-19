# Take-off config (`<project>_takeoff.json`)

One file holds every measured figure. It feeds **both** the Form 405 workbook
and the markup PDF, which is why the two can never disagree. Write it once, at
the end of the measurement pass, and treat it as the record.

```json
{
  "project":        "Pearl Runaway Bay",
  "address":        "24 Oatland Ave, Runaway Bay",
  "approval":       "DA MIN/2023/681",
  "issue_date":     "29 July 2026",
  "workbook":       "405-Floor_Area_Schedule_Pearl_DRAFT_20260729.xlsx",
  "logo":           "/path/to/bdm-logo.png",
  "planning_scheme": "Gold Coast City Plan",
  "planning_gfa":   4113.6,

  "levels": [
    {"name": "Basement", "feca": 1466.3, "uca": 0.0,   "gfa": 1466.3, "gba": 1517.0, "apts": 0},
    {"name": "Ground",   "feca": 1053.5, "uca": 132.0, "gfa": 1185.5, "gba": 1232.6, "apts": 5}
  ],

  "apartments": [
    {"apt": "01", "level": "Ground", "internal": 134.2, "balcony": 16.5}
  ],

  "categories": {
    "Basement": {"car park, bays, aisles & ramp": 1329.6, "bike lockers": 31.8,
                 "plant room": 26.8, "waste / bin room": 38.0, "core, lifts & stairs": 40.1}
  },

  "seeds": {
    "Ground": [[1276, 857], [1739, 897], [2534, 1002], [3090, 1262], [1756, 2182]]
  },

  "sheets": [
    {"image": "seg/MK_Basement.png",  "level": "Basement", "kind": "mk"},
    {"image": "seg/CAT_Basement.png", "level": "Basement", "kind": "cat",
     "note": "How these rooms roll into the workbook's categories."},
    {"image": "seg/APT_Ground.png",   "level": "Ground",   "kind": "apt"}
  ],

  "open_items": [
    "DRAFT — not for issue. Held for Director sign-off …"
  ],

  "lot_plan":     "Lot 9 RP123456",
  "site_area":    405.7,
  "drawing_set":  "DA set, rev C, 01.07.26",
  "architect":    "Rothelowman",

  "rates": {
    "label":           "Dawson",
    "ex_gst":          9012192.0,
    "inc_gst":         9893411.38,
    "benchmark_rate":  6900.0
  },

  "live": {
    "pdf":       "Source Documents/575100_TENDER 010726.pdf",
    "dpi":       220,
    "scale":     100,
    "clip":      [2150, 6250, 2500, 4300],
    "levels": {
      "Basement": {"page": 4, "mask": "plates/basement_gba.npy", "sheet": "A2.101"},
      "Ground":   {"page": 5, "mask": "plates/ground_encl3.npy", "sheet": "A2.102",
                   "uca_offplate": 132.0}
    }
  }
}
```

## Field notes

**`levels`** — one row per level, in the order they should print. `gfa` must
equal `feca + uca`; `verify_schedule.py` checks it against the workbook.

**`apartments`** — `internal` and `balcony` only. TOTAL NSA is derived
(`internal + balcony`) everywhere it appears, so it can never be inconsistent.
`level` must match a `levels[].name` exactly.

**`categories`** — keyed by level, then by room description. Use readable
lower-case descriptions; they print verbatim in the sheet footer. The values
must sum to that level's FECA.

**`seeds`** — the LIVING-room seed point for each apartment, in **raster pixel
coordinates at the take-off dpi**, in the same order as that level's apartments.
The markup builder anchors the NSA callout to these, so the label lands inside
the right apartment rather than on the core.

**`sheets`** — `kind` is one of:

| kind | sheet | footer carries |
|---|---|---|
| `mk` | measured areas — FECA / UCA / GBA overlay | the level's FECA + UCA = GFA, GBA, and the AIQS / PCA references |
| `cat` | area by category, FECA basis | the measured rooms and how they roll into the workbook categories |
| `apt` | apartment segmentation | NSA per unit on the plan, and the level total |

**`open_items`** — the status block. Always leads with the DRAFT line. Add the
drawing source, the scale verification, and anything measured-but-unconfirmed.
Never quietly drop an item because it makes the page look tidier. These print
verbatim on the markup cover under STATUS AND OPEN ITEMS; where a level has been
corrected in the live tool, a bullet naming the levels and the movement is
inserted after the first item automatically. Nothing else is added.

## Fields the live tool needs

`build_live_takeoff.py` reads everything above, plus:

**`lot_plan`, `site_area`, `drawing_set`, `architect`** — printed in the running
head and used for the $/m² of site line. `site_area` may be omitted; the site row
is then dropped rather than printed as a division by zero.

**`rates`** — optional. Where a tender or budget figure exists, the tool shows the
live $/m² as boundaries are corrected, which is the point of watching it. `label`
is whose figure it is — it prints as the column head, so use the tenderer's name.
Omit the block entirely and the rate panel says there is no figure rather than
inventing one. Rates never print in the issued set; they live in Form 413.

**`live`** — the raster inputs. Without this block the tool cannot build.

| key | | |
|---|---|---|
| `pdf` | required | source drawing set, relative to the config file |
| `dpi` | default 220 | render dpi — high enough to zoom to a wall face |
| `scale` | default 100 | drawing scale, 1:`scale` |
| `mask_dpi` | default 300 | dpi the plate masks were cut at |
| `clip` | optional | `[x0, x1, y0, y1]` in `mask_dpi` pixels, applied to every level unless a level overrides it. Omit to use the whole page |
| `min_seg_m` | default 0.30 | ignore linework shorter than this when collecting snap targets |
| `max_vertices` | default 48 | keep the polygon draggable |
| `tol_pct` | default 0.12 | open within this % of the measured plate |

**`live.levels`** — keyed by a `levels[].name`, one entry per level to be built.
A level with no entry is simply not in the tool.

| key | | |
|---|---|---|
| `page` | required | zero-based page index in the source PDF |
| `mask` | required | the measured plate as a boolean raster at `mask_dpi` — `.npy`, or any image where non-zero means inside |
| `sheet` | optional | the architect's sheet number, for the running head |
| `clip` | optional | overrides `live.clip` for this level |
| `uca_offplate` | default 0 | roofed-but-unenclosed area measured **outside** the plate that was cut. `GBA = plate − deductions + uca_offplate`, and the deduction is derived from the level's `gba`, so this is the only place an off-plate measure can enter |

`unroof` on a level (unroofed balcony — GBA but no GFA) is optional and defaults
to nil. The wall-thickness band is derived as `gba − feca − uca − unroof`, never
carried, so it cannot disagree with the workbook.

## Usage

```bash
python3 scripts/build_markups.py  takeoff.json  markups.pdf
python3 scripts/build_markups.py  --blank       cover_template.pdf
python3 scripts/build_live_takeoff.py  takeoff.json  <Project>_Area_Takeoff_LIVE_DRAFT_<yyyymmdd>.html
python3 scripts/export_live_pdf.py     <tool.html>   405a-<Project>_Area_Markups_ASMM_DRAFT_<yyyymmdd>.pdf
python3 scripts/verify_schedule.py  workbook.xlsx  takeoff.json  markups.pdf
```

To exercise the pipeline without a job — a 20 × 12 m building with a 4 × 3 m
notch, 228.0 m², so the polygon can be checked against a hand figure:

```bash
python3 scripts/make_fixture.py  /tmp/fx
python3 scripts/build_live_takeoff.py  /tmp/fx/testbed_takeoff.json  /tmp/fx/tool.html
python3 scripts/export_live_pdf.py     /tmp/fx/tool.html             /tmp/fx/markups.pdf
```
