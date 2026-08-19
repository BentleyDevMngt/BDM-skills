#!/usr/bin/env python3
"""Synthetic 1:100 drawing set + plate masks + take-off config, so the live
take-off tool can be exercised end to end without a real job.

    python3 make_fixture.py [outdir]          # defaults to ./fixture
    python3 build_live_takeoff.py  fixture/testbed_takeoff.json  fixture/tool.html
    python3 export_live_pdf.py     fixture/tool.html             fixture/markups.pdf

Run it before trusting a change to the take-off pipeline. The building is a
20 x 12 m rectangle with a 4 x 3 m notch — 228.0 m² — so the polygon the tool
opens with can be checked against a figure worked out by hand.

Never writes inside the skill folder unless told to.
"""
import json
import os
import sys

import numpy as np
import pymupdf

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'fixture')
os.makedirs(os.path.join(OUT, 'plates'), exist_ok=True)

PT_PER_M = 1000.0 / 100 / 25.4 * 72.0          # 1:100 -> 28.3465 pt per metre
MASK_DPI = 300
PPM300 = 1000.0 / 100 / 25.4 * MASK_DPI        # 118.11 px per metre at 300 dpi
S = MASK_DPI / 72.0                            # pt -> 300 dpi px

PAGE_W, PAGE_H = 1191, 842                     # A3 landscape, points
ORIGIN = (100.0, 100.0)                        # building setout, points

# 20 x 12 m rectangle with a 4 x 3 m notch bitten out of the top right corner
#   area = 240 - 12 = 228.0 m2
OUTLINE_M = [(0, 0), (20, 0), (20, 9), (16, 9), (16, 12), (0, 12)]
TRUE_AREA = 228.0


def to_pt(p):
    return (ORIGIN[0] + p[0] * PT_PER_M, ORIGIN[1] + p[1] * PT_PER_M)


def build_pdf(path, pages=('Ground', 'Level 1')):
    doc = pymupdf.open()
    for title in pages:
        page = doc.new_page(width=PAGE_W, height=PAGE_H)
        sh = page.new_shape()
        pts = [to_pt(p) for p in OUTLINE_M]
        # external wall, drawn as discrete straight segments so get_drawings()
        # reports the axis-aligned linework the snapper looks for
        for i in range(len(pts)):
            sh.draw_line(pymupdf.Point(*pts[i]), pymupdf.Point(*pts[(i + 1) % len(pts)]))
        # a few internal walls and a grid line, all axis aligned
        for x_m in (5, 10, 15):
            sh.draw_line(pymupdf.Point(*to_pt((x_m, 0))), pymupdf.Point(*to_pt((x_m, 9))))
        for y_m in (4, 8):
            sh.draw_line(pymupdf.Point(*to_pt((0, y_m))), pymupdf.Point(*to_pt((16, y_m))))
        sh.finish(width=1.2, color=(0, 0, 0))
        sh.commit()
        page.insert_text(pymupdf.Point(100, 60), f'{title} — synthetic test plan  1:100',
                         fontsize=14)
    doc.save(path)
    doc.close()
    return path


def build_mask(path):
    """The measured plate, as a boolean raster in 300 dpi page coordinates."""
    w = int(round(PAGE_W * S))
    h = int(round(PAGE_H * S))
    m = np.zeros((h, w), dtype=bool)
    ox, oy = ORIGIN[0] * S, ORIGIN[1] * S
    # fill the L: full 20 x 9 band, plus the 16 x 3 upper band
    def box(x0_m, y0_m, x1_m, y1_m):
        x0 = int(round(ox + x0_m * PPM300)); x1 = int(round(ox + x1_m * PPM300))
        y0 = int(round(oy + y0_m * PPM300)); y1 = int(round(oy + y1_m * PPM300))
        m[y0:y1, x0:x1] = True
    box(0, 0, 20, 9)
    box(0, 9, 16, 12)
    np.save(path, m)
    return float(np.count_nonzero(m)) / PPM300 ** 2


pdf = build_pdf(os.path.join(OUT, 'test_drawings.pdf'))
a_ground = build_mask(os.path.join(OUT, 'plates', 'ground.npy'))
a_l1 = build_mask(os.path.join(OUT, 'plates', 'level1.npy'))
print(f'plate raster area: {a_ground:.2f} m2  (geometry says {TRUE_AREA:.2f})')

cfg = {
    "project": "Testbed Apartments",
    "address": "1 Test Street, Southport",
    "lot_plan": "Lot 9 RP123456",
    "site_area": 405.7,
    "approval": "DA TEST/2026/1",
    "issue_date": "19 August 2026",
    "drawing_set": "Test set, rev A",
    "architect": "Test Architects",
    "workbook": "405-Testbed_Floor_Area_Schedule_DRAFT_20260819.xlsx",
    "planning_scheme": "Gold Coast City Plan",

    "levels": [
        {"name": "Ground",  "label": "Ground floor", "feca": 200.0, "uca": 10.0,
         "gfa": 210.0, "gba": 228.0, "unroof": 0.0, "apts": 2,
         "note": "Synthetic level for testing."},
        {"name": "Level 1", "label": "Level 1", "feca": 195.0, "uca": 12.0,
         "gfa": 207.0, "gba": 228.0, "unroof": 3.0, "apts": 1}
    ],

    "apartments": [
        {"apt": "G01", "level": "Ground",  "internal": 84.0, "balcony": 12.0},
        {"apt": "G02", "level": "Ground",  "internal": 79.5, "balcony": 10.5},
        {"apt": "101", "level": "Level 1", "internal": 92.0, "balcony": 14.0}
    ],

    "rates": {"label": "Test Builder", "ex_gst": 2_400_000.0,
              "inc_gst": 2_640_000.0, "benchmark_rate": 5200.0},

    "open_items": [
        "DRAFT — not for issue. Held for Director sign-off.",
        "Synthetic drawing set. Every figure here is a test fixture, not a measurement.",
        "Site area is figured, not surveyed."
    ],

    "live": {
        "pdf": "test_drawings.pdf",
        "dpi": 220,
        "scale": 100,
        "clip": [350, 2850, 350, 1900],
        "levels": {
            "Ground":  {"page": 0, "mask": "plates/ground.npy", "sheet": "A2.101"},
            "Level 1": {"page": 1, "mask": "plates/level1.npy", "sheet": "A2.102",
                        "uca_offplate": 0.0}
        }
    }
}
with open(os.path.join(OUT, 'testbed_takeoff.json'), 'w', encoding='utf-8') as f:
    json.dump(cfg, f, indent=2)
print('fixture written to', OUT)
