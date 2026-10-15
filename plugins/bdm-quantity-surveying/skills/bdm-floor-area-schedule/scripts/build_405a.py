#!/usr/bin/env python3
"""Build the 405a A3 markup set — and make it a live Datum file.

    python3 build_405a.py  takeoff.json  405a-<Project>_Area_Markups_<yyyymmdd>.pdf  [--no-bake] [--app PATH]

One file, two jobs:
  * the house A3 set — cover (reconciliation to the workbook, sheet index, basis
    and authority, status and open items) then one sheet per level, the
    architect's own VECTOR page placed in the BDM frame with the figures in the
    footer;
  * a Datum project embedded in it — every measured polygon an editable area
    shape, calibrated, linked to a Workbook line (GBA / FECA / UCA per level,
    NSA per apartment, FECA per category). Datum computes the quantities itself.

Figures are DERIVED from the shapes in takeoff.json on every build and written
back into it (levels[].gba/feca/uca/gfa/unroof, apartments[].internal/balcony,
categories), so the cover, the footers, the Datum Workbook and Form 405 come from
one set of numbers. Then:

  1. Datum's own verify() on the payload;
  2. read-back — the embedded project is decoded and every Workbook line re-worked
     with Datum's formula; it must equal the derived figure to 0.01 m²;
  3. alignment — each sheet is rendered and every polygon edge sampled; the share
     of samples sitting on the drawing's ink is reported (a wrong placement shows
     here, not on site);
  4. bake — Datum's own Save, run headless, so the markups also show in Acrobat,
     Bluebeam and browsers. Read back again after the bake.

Exit 0 only if 1-3 pass. A failed bake is reported, not hidden: the file then
shows its markups in Datum only, and the hand-over must say so.
"""
import argparse, copy, json, os, sys, tempfile

import numpy as np
import pymupdf
from shapely.geometry import Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout_405a as L                               # noqa: E402
import datum_link                                     # noqa: E402
from vector_takeoff import k_for, shapes_area_m2      # noqa: E402

MEASURES = ('GBA', 'FECA', 'UCA', 'UNROOFED')
ITEM = {'GBA': 'GBA', 'FECA': 'FECA', 'UCA': 'UCA', 'UNROOFED': 'Unroofed'}
AUTH = {'GBA': ' (PCA Glossary — outer face)', 'FECA': ' (AIQS ACMM — inside face)',
        'UCA': ' (AIQS ACMM)', 'UNROOFED': ' (GBA only, no GFA)'}
COL = {'GBA': '#1E3A8A', 'FECA': '#16A34A', 'UCA': '#D97706', 'UNROOFED': '#64748B'}
APT_COL = ['#2563EB', '#DB2777', '#059669', '#9333EA', '#0891B2', '#CA8A04', '#DC2626', '#4F46E5']
TOL = 0.01


def level_N(cfg, lv):
    return float(lv.get('scale', cfg.get('scale', 100))) * float(lv.get('sheet_factor', cfg.get('sheet_factor', 1)))


def _geom(shapes):
    from shapely.ops import unary_union
    plus = unary_union([Polygon(x['pts']).buffer(0) for x in shapes if not x.get('deduct')])
    minus = unary_union([Polygon(x['pts']).buffer(0) for x in shapes if x.get('deduct')])
    return plus.difference(minus)


def containment(sh, K):
    """m² of FECA / UCA / unroofed lying outside the GBA outline. GBA is drawn as its
    own shape, so a corner dragged on one measure in Datum and not on GBA shows here."""
    g = _geom(sh['GBA']).buffer(0.0005 * K ** 0.5)          # ~0.5 mm slack
    out = {}
    for m in ('FECA', 'UCA', 'UNROOFED'):
        if sh.get(m):
            o = _geom(sh[m]).difference(g).area / K
            if o > 0.05:
                out[m] = round(o, 2)
    return out


def resolve(cfg):
    """Derive every reported figure from the shapes. Returns the updated cfg."""
    lv_by = {lv['name']: lv for lv in cfg['levels']}
    for lv in cfg['levels']:
        K = k_for(level_N(cfg, lv))
        sh = lv.get('shapes') or {}
        for m in ('GBA', 'FECA'):
            if not sh.get(m):
                sys.exit(f"level {lv['name']}: no {m} shapes — every level needs GBA and FECA polygons")
        lv['gba'] = round(shapes_area_m2(sh['GBA'], K), 2)
        lv['feca'] = round(shapes_area_m2(sh['FECA'], K), 2)
        lv['uca'] = round(shapes_area_m2(sh.get('UCA', []), K), 2)
        lv['unroof'] = round(shapes_area_m2(sh.get('UNROOFED', []), K), 2)
        lv['gfa'] = round(lv['feca'] + lv['uca'], 2)
        lv['_containment'] = containment(sh, K)
        lv.setdefault('apts', sum(1 for a in cfg.get('apartments', []) if a['level'] == lv['name']))
    for a in cfg.get('apartments', []):
        K = k_for(level_N(cfg, lv_by[a['level']]))
        s = a.get('shapes') or {}
        a['internal'] = round(shapes_area_m2(s.get('internal', []), K), 2)
        a['balcony'] = round(shapes_area_m2(s.get('balcony', []), K), 2)
    cats = {}
    for lvn, d in (cfg.get('category_shapes') or {}).items():
        K = k_for(level_N(cfg, lv_by[lvn]))
        cats[lvn] = {k: round(shapes_area_m2(v, K), 2) for k, v in d.items()}
    if cats:
        cfg['categories'] = cats
    cfg.setdefault('apartments', [])
    cfg.setdefault('categories', {})
    cfg.setdefault('sheets', [{'level': lv['name'], 'kind': 'mk'} for lv in cfg['levels']])
    return cfg


def display_page(src, pno):
    """A rotated sheet is normalised first (rotation baked into its content), so it
    is placed exactly as it displays — the space vector_takeoff measures in.
    show_pdf_page does not honour /Rotate on its own."""
    if not src[pno].rotation:
        return src, pno
    t = pymupdf.open()
    t.insert_pdf(src, from_page=pno, to_page=pno)
    t[0].remove_rotation()
    return t, 0


def place(src_page, frame, clip=None):
    r = pymupdf.Rect(clip) if clip else src_page.rect
    s = min(frame.width / r.width, frame.height / r.height)
    dw, dh = r.width * s, r.height * s
    ox, oy = frame.x0 + (frame.width - dw) / 2, frame.y0 + (frame.height - dh) / 2
    return {'s': s, 'ox': ox, 'oy': oy, 'x0': r.x0, 'y0': r.y0, 'rect': [ox, oy, ox + dw, oy + dh]}


def fwd(fr, pts):
    return [(fr['ox'] + (x - fr['x0']) * fr['s'], fr['oy'] + (y - fr['y0']) * fr['s']) for x, y in pts]


def sheet(doc, src, cfg, sh, idx, npages):
    lv = next(l for l in cfg['levels'] if l['name'] == sh['level'])
    kind = sh['kind']
    pg = doc.new_page(width=L.W, height=L.H)
    logo = cfg.get('logo')
    if logo and os.path.exists(logo):
        pg.insert_image(pymupdf.Rect(L.M, 11, L.M + 188 * 0.40, 11 + 55 * 0.40), filename=logo)
    L.txt(pg, L.M + 92, 26, f"{cfg['project'].upper()}  ·  {cfg['address'].upper()}", 8.5, True)
    L.rtxt(pg, L.W - L.M, 26, f"{lv['name'].upper()}  —  {L.TITLE[kind].upper()}", 8.5, True, L.GOLD)
    pg.draw_line((L.M, L.HEAD_H), (L.W - L.M, L.HEAD_H), color=L.NAVY, width=0.9)

    frame = pymupdf.Rect(L.M, L.HEAD_H + 6, L.W - L.M, L.H - L.FOOT_H)
    sdoc, spno = display_page(src, lv['page'])
    fr = place(sdoc[spno], frame, lv.get('clip'))
    clip = pymupdf.Rect(lv['clip']) if lv.get('clip') else None
    pg.show_pdf_page(pymupdf.Rect(fr['rect']), sdoc, spno, clip=clip)
    fr.update(page=idx - 1, level=lv['name'], kind=kind, N=level_N(cfg, lv))

    apts = [a for a in cfg['apartments'] if a['level'] == lv['name']]
    nsa = {a['apt']: round((a['internal'] or 0) + (a['balcony'] or 0), 1) for a in apts}
    if kind == 'apt':                                    # boxed NSA label inside each apartment
        for a in apts:
            ins = a.get('shapes', {}).get('internal') or []
            if not ins:
                continue
            c = Polygon(fwd(fr, ins[0]['pts'])).representative_point()
            s = f"{a['apt']}   {nsa[a['apt']]:,.1f} m²"
            tw = L.tl(s, 7.6, True)
            bx0, by0 = c.x - (tw + 9) / 2, c.y - 5.75
            pg.draw_rect(pymupdf.Rect(bx0, by0, bx0 + tw + 9, by0 + 11.5), color=L.NAVY, fill=(1, 1, 1), width=0.6)
            L.txt(pg, bx0 + 4.5, by0 + 8.4, s, 7.6, True)

    pg.draw_line((L.M, L.H - L.FOOT_H + 8), (L.W - L.M, L.H - L.FOOT_H + 8), color=L.NAVY, width=0.9)
    if kind == 'mk':
        l1 = (f"{lv['name']}:   FECA {lv['feca']:,.1f}  +  UCA {lv['uca']:,.1f}  =  GFA {lv['gfa']:,.1f} m²"
              f"      ·      GBA {lv['gba']:,.1f} m²      —      as reported on the Level Schedule tab of {cfg['workbook']}")
        l2 = ('GFA (FECA + UCA) per the AIQS Australian Cost Management Manual (2022).  GBA per the Property Council / API / '
              'REIA Glossary of Property Terms — the enclosed and unenclosed area at all building floor levels, measured to '
              'the outside face of enclosing walls, balustrades and supports.')
    elif kind == 'cat':
        cats = cfg['categories'].get(lv['name'], {})
        l1 = f"{lv['name']} FECA {lv['feca']:,.1f} m²   =   " + '  +  '.join(f'{k} {v:,.1f}' for k, v in cats.items())
        l2 = sh.get('note', 'Reconcile these measured rooms to the categories used on the Area by Category tab.')
    else:
        det = '   ·   '.join(f"{a['apt']} {nsa[a['apt']]:,.1f}" for a in apts)
        l1 = (f"{lv['name']} net sellable area (m²):    {det}    ·    level total {round(sum(nsa.values()), 1):,.1f} m² "
              f"across {len(apts)} apartments")
        l2 = ('Boxed figures are TOTAL NSA per apartment — internal area plus balcony or terrace — as scheduled unit by unit '
              f"on the NSA & Revenue tab of {cfg['workbook']}.  Grey is core, lobby and common property, which carries no NSA.")
    L.txt(pg, L.M, L.H - 24, l1, 8, True)
    L.txt(pg, L.M, L.H - 13, l2, 7.2, False, L.GREY)
    L.rtxt(pg, L.W - L.M, L.H - 13, f"{cfg['issue_date']} · Page {idx} of {npages}", 7.2, False, L.GREY)
    return fr


def datum_project(dm, cfg, frames, name):
    p = dm.DatumProject(name, page_w=L.W, page_h=L.H)
    items = {}

    def item(key, label, trade, color):
        if key not in items:
            items[key] = p.boq_item(label, 'area', trade=trade, color=color)
        return items[key]

    lv_by = {lv['name']: lv for lv in cfg['levels']}
    for fr in frames:
        pg, lvn, kind = fr['page'], fr['level'], fr['kind']
        p.page_calibrations[str(pg)] = {'pixelsPerMm': 72.0 / 25.4 / fr['N'] * fr['s'], 'scale': f"1:{fr['N']:g}"}
        lv = lv_by[lvn]
        if kind == 'mk':
            for m in MEASURES:
                for s in (lv.get('shapes') or {}).get(m, []):
                    it = item(('L', lvn, m), f'{ITEM[m]} — {lvn}{AUTH[m]}', lvn, COL[m])
                    p.area(pg, fwd(fr, s['pts']), item=it, deduction=bool(s.get('deduct')),
                           fill_opacity=20 if m == 'FECA' else 12)
        elif kind == 'apt':
            for i, a in enumerate(a for a in cfg['apartments'] if a['level'] == lvn):
                for part in ('internal', 'balcony'):
                    for s in (a.get('shapes') or {}).get(part, []):
                        it = item(('A', a['apt'], part), f"NSA {part} — Apt {a['apt']}", f'{lvn} NSA', APT_COL[i % len(APT_COL)])
                        p.area(pg, fwd(fr, s['pts']), item=it, deduction=bool(s.get('deduct')),
                               fill_opacity=22 if part == 'internal' else 10, hatch=None if part == 'internal' else 'diagonal')
        elif kind == 'cat':
            for i, (desc, shapes) in enumerate((cfg.get('category_shapes') or {}).get(lvn, {}).items()):
                for s in shapes:
                    it = item(('C', lvn, desc), f'FECA · {desc} — {lvn}', f'{lvn} categories', APT_COL[i % len(APT_COL)])
                    p.area(pg, fwd(fr, s['pts']), item=it, deduction=bool(s.get('deduct')), fill_opacity=22)
    return p


def alignment(pdf_bytes, frames, cfg, dpi=144):
    """Share of polygon-edge samples within ~2 px of drawn ink, per sheet."""
    doc = pymupdf.open(stream=pdf_bytes, filetype='pdf')
    lv_by = {lv['name']: lv for lv in cfg['levels']}
    z = dpi / 72.0
    out = {}
    for fr in frames:
        if fr['kind'] != 'mk':
            continue
        pm = doc[fr['page']].get_pixmap(dpi=dpi)
        a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, pm.n)[:, :, :3].mean(axis=2)
        ink = a < 160
        hit = tot = 0
        for m in ('GBA', 'FECA'):
            for s in lv_by[fr['level']]['shapes'].get(m, []):
                pts = fwd(fr, s['pts'])
                for i in range(len(pts)):
                    (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
                    for t in np.linspace(0, 1, 12, endpoint=False):
                        x, y = (x1 + (x2 - x1) * t) * z, (y1 + (y2 - y1) * t) * z
                        xi, yi = int(round(x)), int(round(y))
                        tot += 1
                        if ink[max(0, yi - 2):yi + 3, max(0, xi - 2):xi + 3].any():
                            hit += 1
        out[fr['level']] = round(hit / tot, 3) if tot else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('config')
    ap.add_argument('out')
    ap.add_argument('--no-bake', action='store_true', help='embed only; markups then show in Datum only')
    ap.add_argument('--app', help='local BDM-PDF-Markup-Tool.html for an offline bake')
    a = ap.parse_args()

    cfg = resolve(json.load(open(a.config, encoding='utf-8')))
    for k, v in L.BLANK.items():
        cfg.setdefault(k, copy.deepcopy(v))
    base = os.path.dirname(os.path.abspath(a.config))
    src = pymupdf.open(os.path.join(base, cfg['source_pdf']))

    corr = cfg.get('corrections') or []
    if corr:
        det = '; '.join(f"{c['level']} {c['measure']} {c['from']:,.1f} → {c['to']:,.1f}" for c in corr)
        bullet = (f'Corrected in Datum: {det} m².  The workbook and any cost estimate built on the earlier '
                  'figures must be rebuilt.')
        cfg['open_items'] = [cfg['open_items'][0], bullet] + [x for x in cfg['open_items'][1:] if not x.startswith('Corrected in Datum')]

    npages = 1 + len(cfg['sheets'])
    doc = pymupdf.open()
    L.cover(doc, cfg, npages)
    frames = [sheet(doc, src, cfg, sh, i, npages) for i, sh in enumerate(cfg['sheets'], 2)]
    doc.subset_fonts()
    plain = doc.tobytes(deflate=True, garbage=3)

    dm = datum_link.load()
    proj = datum_project(dm, cfg, frames, os.path.basename(a.out))
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as t:
        t.write(plain)
    proj.verify(pages=dm.page_sizes(t.name))
    dm.embed(t.name, proj, a.out)
    os.unlink(t.name)

    from read_405a import readback, compare
    fails = compare(cfg, readback(a.out))
    al = alignment(plain, frames, cfg)

    cfg['_frames'] = frames
    json.dump(cfg, open(a.config, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    print(f'{npages} pages -> {a.out}')
    print('alignment (polygon edges on drawn ink): ' + ', '.join(f'{k} {v:.0%}' for k, v in al.items()))
    for lv in cfg['levels']:
        for m, o in (lv.get('_containment') or {}).items():
            print(f"  WARNING: {lv['name']} {m} lies {o:,.2f} m² outside the GBA outline — move the GBA shape too, "
                  'or GBA is understated')
    bad_al = [k for k, v in al.items() if v is not None and v < 0.85]
    if bad_al:
        print(f'  WARNING: {", ".join(bad_al)} under 85% — check the placement and the outline on the plan')
    if fails:
        print('READ-BACK FAILED:'); [print('  -', f) for f in fails]
        return 1
    print('read-back: every Datum Workbook line equals the derived figure')

    if a.no_bake:
        print('NOT BAKED (--no-bake): markups show in Datum only until it is opened there and saved.')
        return 0
    ok, msg = dm.bake(a.out, app=a.app)
    print(msg)
    if not ok:
        print('NOT BAKED: markups show in Datum only until it is opened there and saved. Say so on hand-over.')
        return 0
    fails = compare(cfg, readback(a.out))
    if fails:
        print('READ-BACK AFTER BAKE FAILED:'); [print('  -', f) for f in fails]
        return 1
    print('baked; read-back after bake clean')
    return 0


if __name__ == '__main__':
    sys.exit(main())
