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
  ]
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
Never quietly drop an item because it makes the page look tidier.

## Usage

```bash
python3 scripts/build_markups.py  takeoff.json  markups.pdf
python3 scripts/build_markups.py  --blank       cover_template.pdf
python3 scripts/verify_schedule.py  workbook.xlsx  takeoff.json  markups.pdf
```
