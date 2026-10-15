#!/usr/bin/env python3
"""Synthetic VECTOR drawing set + take-off config, so the R4 pipeline can be run
end to end without a job — and checked against figures worked out by hand.

    python3 make_fixture.py [outdir]                         # defaults to ./fixture
    python3 build_405a.py   fixture/testbed_takeoff.json  fixture/405a-Testbed_Area_Markups.pdf
    python3 read_405a.py    fixture/405a-Testbed_Area_Markups.pdf  fixture/testbed_takeoff.json

The building is a 20 x 12 m rectangle with a 4 x 3 m notch, drawn at 1:100 on A3
the way an ArchiCAD export draws it: a grey area zone to the outside face, the
external walls as black poche on a 'Walls - External' layer, 200 mm thick, with
one 6 m glazed run on the south face that carries no poche.

  GBA  = 240 − 12                                          = 228.00 m²
  FECA = inner outline 19.6 x 8.6 + 15.6 x 3.0 = 215.36
         + the 6 m glazed run x 0.2 m back to the face       = 216.56 m²
  Level 1 adds a 4 x 3 m roofed balcony in the notch: UCA   =  12.00 m²
  Level 1 is issued ROTATED 90°, to prove placement survives a rotated sheet.

Run it before trusting a change to the pipeline. Never writes inside the skill
folder unless told to.
"""
import json, os, sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vector_takeoff import VectorSheet, shape_list   # noqa: E402

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'fixture')
os.makedirs(OUT, exist_ok=True)
PT_PER_M = 1000.0 / 100 / 25.4 * 72.0
ORIGIN = (300.0, 250.0)
OUTLINE = [(0, 0), (20, 0), (20, 9), (16, 9), (16, 12), (0, 12)]
INNER = [(0.2, 0.2), (19.8, 0.2), (19.8, 8.8), (15.8, 8.8), (15.8, 11.8), (0.2, 11.8)]
GLAZED = (7.0, 13.0)                       # south face (y = 0), x from 7 to 13 m: no poche
BALCONY = [(16, 9), (20, 9), (20, 12), (16, 12)]
HAND = {'Ground': {'gba': 228.0, 'feca': 216.56, 'uca': 0.0},
        'Level 1': {'gba': 240.0, 'feca': 216.56, 'uca': 12.0}}


def P(p):
    return pymupdf.Point(ORIGIN[0] + p[0] * PT_PER_M, ORIGIN[1] + p[1] * PT_PER_M)


def poly(sh, pts):
    for i in range(len(pts)):
        sh.draw_line(P(pts[i]), P(pts[(i + 1) % len(pts)]))


def build_pdf(path):
    doc = pymupdf.open()
    walls = doc.add_ocg('Walls - External')
    zones = doc.add_ocg('Zones - Building Areas')
    for title, balcony in (('Ground', False), ('Level 1', True)):
        page = doc.new_page(width=1190.55, height=841.89)
        sh = page.new_shape()                                  # area zone, outside face
        poly(sh, OUTLINE)
        sh.finish(fill=(0.773, 0.773, 0.773), color=None, oc=zones)
        if balcony:
            poly(sh, BALCONY)
            sh.finish(fill=(0.86, 0.86, 0.86), color=None, oc=zones)
            poly(sh, BALCONY)                                  # balustrade line
            sh.finish(color=(0, 0, 0), width=0.6)
        # poche: wall runs as rectangles, leaving the glazed run on the south face open
        for (x0, y0), (x1, y1) in (((0, 0), (GLAZED[0], 0.2)), ((GLAZED[1], 0), (20, 0.2)), ((19.8, 0.2), (20, 9)),
                                   ((15.8, 8.8), (19.8, 9)), ((15.8, 9), (16, 12)), ((0, 11.8), (15.8, 12)),
                                   ((0, 0.2), (0.2, 11.8))):
            sh.draw_rect(pymupdf.Rect(P((x0, y0)), P((x1, y1))))
        sh.finish(fill=(0, 0, 0), color=None, oc=walls)
        sh.draw_line(P((GLAZED[0], 0.1)), P((GLAZED[1], 0.1)))  # the glazing line
        sh.finish(color=(0, 0, 0), width=0.6)
        for x in (5, 10):                                      # internal walls, unlayered
            sh.draw_line(P((x, 0.2)), P((x, 8.8)))
        sh.finish(color=(0, 0, 0), width=1.0)
        sh.commit()
        page.insert_text(pymupdf.Point(60, 60), f'{title} — synthetic test plan   Scale 1:100 @ A3', fontsize=12)
        page.insert_text(P((8, 6)), '228.00 m2', fontsize=9)
        if balcony:
            page.insert_text(P((16.5, 10.5)), 'BALCONY 12.00 m2', fontsize=7)
    doc[1].set_rotation(90)
    doc.save(path)


def measure(path):
    levels = []
    for pg, name in ((0, 'Ground'), (1, 'Level 1')):
        vs = VectorSheet(path, pg, 100)
        env = vs.zone_near(228.0)
        wall = vs.wall_depth(env)
        feca = vs.feca(env, wall['median_mm'])
        shapes = {'GBA': shape_list(env), 'FECA': shape_list(feca)}
        if pg == 1:
            bal = vs.zone_near(12.0)
            shapes['UCA'] = shape_list(bal)
            shapes['GBA'] = shape_list(env.union(bal))
        levels.append({'name': name, 'page': pg, 'sheet': f'TB-10{pg}', 'scale': 100, 'shapes': shapes,
                       '_wall': wall})
    return levels


def main():
    pdf = os.path.join(OUT, 'testbed_plans.pdf')
    build_pdf(pdf)
    levels = measure(pdf)
    cfg = {
        'project': 'Testbed', 'address': '1 Example St, Nowhere', 'approval': 'DA TEST/0000',
        'issue_date': '1 January 2026', 'workbook': '405-Testbed_Floor_Area_Schedule_20260101.xlsx',
        'source_pdf': 'testbed_plans.pdf', 'scale': 100,
        'drawing_source': 'testbed_plans.pdf (synthetic) — TB-100, TB-101',
        'levels': levels, 'apartments': [],
        'sheets': [{'level': 'Ground', 'kind': 'mk'}, {'level': 'Level 1', 'kind': 'mk'}],
        'open_items': ['Held for Director sign-off.', 'Synthetic fixture — not a project.'],
    }
    cf = os.path.join(OUT, 'testbed_takeoff.json')
    json.dump(cfg, open(cf, 'w'), indent=1)
    from build_405a import resolve
    r = resolve(json.loads(json.dumps(cfg)))
    ok = True
    for lv in r['levels']:
        h = HAND[lv['name']]
        for k in ('gba', 'feca', 'uca'):
            good = abs(lv[k] - h[k]) <= 0.05
            ok &= good
            print(f"{lv['name']:8s} {k.upper():5s} measured {lv[k]:8.2f}  hand {h[k]:8.2f}  {'OK' if good else 'FAIL'}")
        print(f"         wall {lv['_wall']}")
    print(('FIXTURE OK — ' if ok else 'FIXTURE FAILED — ') + cf)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
