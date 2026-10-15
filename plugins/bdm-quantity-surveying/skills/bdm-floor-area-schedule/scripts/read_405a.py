#!/usr/bin/env python3
"""Read a 405a markup set back out of Datum — the correction loop.

    python3 read_405a.py  405a.pdf  takeoff.json                     # compare
    python3 read_405a.py  405a.pdf  takeoff.json  --write corrected.json

The Director corrects the take-off in Datum — drags a corner, adds or deletes a
shape — and saves. This reads the project Datum saved inside the PDF, works every
Workbook line with Datum's own rule (Σ polygon pt² ÷ pixelsPerMm² ÷ 10⁶,
deductions subtracted), and compares it with the figures the set was built from.

--write maps the corrected shapes back onto the source drawing and writes a new
take-off config with a `corrections` list. Re-run build_405a.py on it, then
rebuild the Form 405 workbook from it: the cover, the footers, the Workbook and
Form 405 then all carry the corrected figures, and the cover names what moved.
Corrections live in the PDF, so they travel with the file — not in one browser.
"""
import argparse, base64, json, re, sys

from pypdf import PdfReader

PAT = [(re.compile(r'^(GBA|FECA|UCA|Unroofed) — (.+?)(?: \(.*\))?$'), 'L'),
       (re.compile(r'^NSA (internal|balcony) — Apt (.+)$'), 'A'),
       (re.compile(r'^FECA · (.+) — (.+)$'), 'C')]
MEAS = {'GBA': 'GBA', 'FECA': 'FECA', 'UCA': 'UCA', 'Unroofed': 'UNROOFED'}
FIELD = {'GBA': 'gba', 'FECA': 'feca', 'UCA': 'uca', 'UNROOFED': 'unroof'}
TOL = 0.01


def payload(pdf):
    md = PdfReader(pdf).metadata or {}
    if '/BDMMarkupData' not in md:
        sys.exit(f'{pdf}: no Datum project in this file')
    return json.loads(base64.b64decode(md['/BDMMarkupData']).decode('utf-8')), md.get('/BDMBakedOverlay')


def _area(pts):
    s = 0.0
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        s += a['x'] * b['y'] - b['x'] * a['y']
    return abs(s) / 2


def readback(pdf):
    j, baked = payload(pdf)
    items = {t['id']: t for t in j.get('takeoffItems', [])}
    rb = {'levels': {}, 'apartments': {}, 'categories': {}, 'shapes': {}, 'unlinked': 0, 'baked': baked}
    for a in j.get('annotations', []):
        if a.get('type') != 'area':
            continue
        it = items.get(a.get('takeoffItemId'))
        if not it:
            rb['unlinked'] += 1
            continue
        cal = (j.get('pageCalibrations') or {}).get(str(a['page'])) or j.get('defaultCalibration')
        m2 = _area(a['points']) / cal['pixelsPerMm'] ** 2 / 1e6 * (-1 if a.get('isDeduction') else 1)
        key = None
        for pat, kind in PAT:
            m = pat.match(it['name'])
            if m:
                if kind == 'L':
                    key = ('L', m.group(2), MEAS[m.group(1)])
                    d = rb['levels'].setdefault(m.group(2), {})
                    d[MEAS[m.group(1)]] = d.get(MEAS[m.group(1)], 0) + m2
                elif kind == 'A':
                    key = ('A', m.group(2), m.group(1))
                    d = rb['apartments'].setdefault(m.group(2), {})
                    d[m.group(1)] = d.get(m.group(1), 0) + m2
                else:
                    key = ('C', m.group(2), m.group(1))
                    d = rb['categories'].setdefault(m.group(2), {})
                    d[m.group(1)] = d.get(m.group(1), 0) + m2
                break
        if key is None:
            rb['unlinked'] += 1
            continue
        rb['shapes'].setdefault(key, []).append(
            {'page': a['page'], 'pts': [(p['x'], p['y']) for p in a['points']], 'deduct': bool(a.get('isDeduction'))})
    return rb


def compare(cfg, rb, tol=TOL):
    """Every figure the set was built from against what Datum now computes."""
    fails = []
    for lv in cfg['levels']:
        got = rb['levels'].get(lv['name'], {})
        for m, f in FIELD.items():
            want = lv.get(f) or 0
            have = got.get(m, 0)
            if abs(want - have) > tol:
                fails.append(f"{lv['name']} {m}: built {want:,.2f} · Datum {have:,.2f} ({have - want:+,.2f})")
    for a in cfg.get('apartments', []):
        got = rb['apartments'].get(a['apt'], {})
        for part in ('internal', 'balcony'):
            if abs((a.get(part) or 0) - got.get(part, 0)) > tol:
                fails.append(f"Apt {a['apt']} {part}: built {a.get(part) or 0:,.2f} · Datum {got.get(part, 0):,.2f}")
    for lvn, d in (cfg.get('categories') or {}).items():
        for k, v in d.items():
            have = rb['categories'].get(lvn, {}).get(k, 0)
            if abs(v - have) > tol:
                fails.append(f'{lvn} category {k}: built {v:,.2f} · Datum {have:,.2f}')
    return fails


def corrected(cfg, rb):
    """New config: shapes from Datum, mapped back onto the source page."""
    fr_by_page = {f['page']: f for f in cfg.get('_frames', [])}
    if not fr_by_page:
        sys.exit('takeoff.json has no _frames — it was not written by build_405a.py')

    def back(sh):
        fr = fr_by_page[sh['page']]
        return {'pts': [[round(fr['x0'] + (x - fr['ox']) / fr['s'], 3), round(fr['y0'] + (y - fr['oy']) / fr['s'], 3)]
                        for x, y in sh['pts']], 'deduct': sh['deduct']}

    new = json.loads(json.dumps(cfg))
    moves = []
    for lv in new['levels']:
        old = {m: lv.get(f) or 0 for m, f in FIELD.items()}
        lv['shapes'] = {m: [back(s) for s in rb['shapes'].get(('L', lv['name'], m), [])] for m in FIELD}
        lv['shapes'] = {m: v for m, v in lv['shapes'].items() if v}
        for m in FIELD:
            have = round(rb['levels'].get(lv['name'], {}).get(m, 0), 2)
            if abs(have - old[m]) > 0.05:
                moves.append({'level': lv['name'], 'measure': m, 'from': old[m], 'to': have})
    for a in new.get('apartments', []):
        a['shapes'] = {p: [back(s) for s in rb['shapes'].get(('A', a['apt'], p), [])] for p in ('internal', 'balcony')}
    if new.get('category_shapes'):
        for lvn, d in new['category_shapes'].items():
            for k in list(d):
                d[k] = [back(s) for s in rb['shapes'].get(('C', lvn, k), [])]
    new['corrections'] = (cfg.get('corrections') or []) + moves
    return new, moves


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('config')
    ap.add_argument('--write', metavar='CORRECTED.json')
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding='utf-8'))
    rb = readback(a.pdf)
    print(f"Datum project read: {sum(len(v) for v in rb['shapes'].values())} linked shapes, "
          f"{rb['unlinked']} not linked to a Form 405 line; baked = {rb['baked']}")
    print(f"{'Level':16s} {'Measure':9s} {'Built':>10s} {'Datum now':>10s} {'Moved':>8s}")
    for lv in cfg['levels']:
        for m, f in FIELD.items():
            b, d = lv.get(f) or 0, rb['levels'].get(lv['name'], {}).get(m, 0)
            if b or d:
                print(f"{lv['name']:16s} {m:9s} {b:10,.2f} {d:10,.2f} {d - b:+8.2f}")
    fails = compare(cfg, rb)
    if not a.write:
        print('UNCHANGED — Datum agrees with the build.' if not fails else f'{len(fails)} figure(s) moved in Datum.')
        return 0
    new, moves = corrected(cfg, rb)
    json.dump(new, open(a.write, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'{len(moves)} level figure(s) moved; corrected config -> {a.write}. Re-run build_405a.py on it, then rebuild Form 405.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
