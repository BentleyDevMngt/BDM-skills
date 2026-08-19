#!/usr/bin/env python3
"""Build the BDM area-markup PDF — A3 landscape, cover sheet + marked-up plans.

Everything printed on the sheets is read from one config file, which is also
what feeds the Form 405 workbook.  That is deliberate: the markup and the
schedule are produced from a single set of numbers and cannot drift apart.

    python3 build_markups.py config.json out.pdf
    python3 build_markups.py --blank out.pdf      # blank cover, for the template

Config schema: see references/config_schema.md.
"""
import argparse, json, os, sys

try:
    import pymupdf
except ImportError:
    sys.exit('pymupdf is required:  pip install pymupdf --break-system-packages')

# ------------------------------------------------------------------ house style
NAVY = (0.059, 0.090, 0.129)
GOLD = (0.616, 0.482, 0.357)
GREY = (0.360, 0.355, 0.333)
RULE = (0.847, 0.843, 0.827)
PAPER = (0.957, 0.957, 0.945)

FONTS = [
    ('/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf',
     '/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf'),          # Calibri-metric
    ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
     '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'),
    ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
     '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
]
FR_PATH = FB_PATH = None
for r, b in FONTS:
    if os.path.exists(r) and os.path.exists(b):
        FR_PATH, FB_PATH = r, b
        break
if not FR_PATH:
    sys.exit('No embeddable sans font found — base-14 fonts drop the m² and em-dash glyphs.')
FR, FB = pymupdf.Font(fontfile=FR_PATH), pymupdf.Font(fontfile=FB_PATH)

W, H = 1190.55, 841.89          # A3 landscape
M = 22.0
HEAD_H, FOOT_H = 34.0, 46.0

TITLE = {'mk': 'Measured areas — FECA / UCA / GBA',
         'cat': 'Area by category (FECA basis)',
         'apt': 'Apartment segmentation & net sellable area'}

# The authority text.  This is the part that must not be re-invented per project —
# it is the same on every BDM area take-off.  See references/measurement_standards.md.
BASIS = [
    ('FECA · UCA · GFA',
     'AIQS — Australian Cost Management Manual (2022), Method of Measurement of Building Area.',
     ['FECA is all enclosed covered floor area, measured to the inside face of the external walls, including basements, '
      'lift shafts, stairs and plant.  UCA is roofed but unenclosed area — balconies, verandahs, undercrofts.  '
      'GFA = FECA + UCA.  This is the cost-planning measure and is authoritative for that purpose.  It is not the '
      'planning measure and does not test plot ratio.']),
    ('GBA — Gross Building Area',
     'Property Council of Australia / Australian Property Institute / Real Estate Institute of Australia — '
     'Glossary of Property Terms.',
     ['Defined as “the total enclosed and unenclosed area of the building at all building floor levels measured between '
      'the normal outside face of any enclosing walls, balustrades and supports”.',
      'GBA is therefore the largest of the three measures: it takes in the basement car park, plant, the thickness of '
      'the external walls, and unroofed balconies that carry no GFA.  Note that GBA is not defined in the PCA Method of '
      'Measurement for Lettable Area — that publication covers tenancy areas (NLA / GLA) only.']),
    ('NSA — Net Sellable Area',
     'Lot-boundary convention for a community titles scheme.  Not a published standard.',
     ['Internal area to the inside face of external walls and the centre of party walls, plus balcony or terrace to the '
      'inside face of the balustrade.  Excludes all common property — core, lobbies, amenity, plant and car park.']),
]

BLANK = {
    'project': '[Project name]', 'address': '[Site address]', 'approval': 'DA [reference]',
    'issue_date': '[dd month yyyy]', 'workbook': '405-Floor_Area_Schedule_[Project]_DRAFT_[yyyymmdd].xlsx',
    'drawing_source': '[drawing set file name] ([architect], project [no.]) — sheets [numbers and revisions]',
    'approval_note': 'the plans referred to in [council] approval [reference] dated [date]',
    'scale_note': 'Scale verified against [n] figured dimension pairs — [x]% agreement with [scale]. Target tolerance ±2%.',
    'planning_gfa': None, 'planning_scheme': 'planning-scheme',
    'levels': [{'name': n, 'feca': None, 'uca': None, 'gfa': None, 'gba': None, 'apts': None}
               for n in ['Basement', 'Ground', 'Level 2', 'Level 3', 'Level 4']],
    'apartments': [{'apt': f'{i:02d}', 'level': '', 'internal': None, 'balcony': None} for i in range(1, 19)],
    'sheets': [], 'categories': {}, 'seeds': {},
    'open_items': [
        'DRAFT — not for issue.  Held for Director sign-off and for reconciliation against the architect’s own area schedule.',
        'Source: [drawing set], [architect] — [sheet numbers and revisions].',
        '[Scale verification statement.]',
        'Site area is measured, not confirmed — confirm against the survey plan or title before relying on site cover or plot ratio.',
        '[Name any level carrying a tolerance worse than ±2% and flag it for a hand check.]',
        'Apartment numbering is inferred from the plans unless the architect has confirmed it.',
    ],
}


# ------------------------------------------------------------------- primitives
def tl(s, size, bold=False):
    return (FB if bold else FR).text_length(s, fontsize=size)


def txt(pg, x, y, s, size=8, bold=False, color=NAVY):
    pg.insert_text((x, y), s, fontname=('cb' if bold else 'cr'),
                   fontfile=(FB_PATH if bold else FR_PATH), fontsize=size, color=color)


def rtxt(pg, x, y, s, size=8, bold=False, color=NAVY):
    txt(pg, x - tl(s, size, bold), y, s, size, bold, color)


def rule(pg, x0, y, x1, color=RULE, width=0.5):
    pg.draw_line((x0, y), (x1, y), color=color, width=width)


def wrap(s, width, size, bold=False):
    lines, cur = [], ''
    for w in s.split(' '):
        t = (cur + ' ' + w).strip()
        if tl(t, size, bold) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(pg, x, y, s, width, size=8, bold=False, color=GREY, lead=None):
    lead = lead or size * 1.32
    for ln in wrap(s, width, size, bold):
        txt(pg, x, y, ln, size, bold, color)
        y += lead
    return y


def sect(pg, x, y, w, title):
    txt(pg, x, y, title, 9.5, True)
    pg.draw_line((x, y + 5), (x + w, y + 5), color=NAVY, width=0.8)
    return y + 22


def num(v, dp=1):
    return '–' if v in (None, 0, 0.0) else f'{v:,.{dp}f}'


# ----------------------------------------------------------------- cover sheet
def cover(doc, cfg, npages):
    pg = doc.new_page(width=W, height=H)
    logo = cfg.get('logo')
    if logo and os.path.exists(logo):
        pg.insert_image(pymupdf.Rect(M, 22, M + 188 * 0.62, 22 + 55 * 0.62), filename=logo)
    else:
        txt(pg, M, 46, 'BENTLEY DEVELOPMENT MANAGEMENT', 11, True)
    rtxt(pg, W - M, 33, 'AREA TAKE-OFF  —  DRAWING MARKUPS', 10, True)
    rtxt(pg, W - M, 46, f"{cfg['project']}  ·  {cfg['address']}  ·  {cfg['approval']}", 8.5, False, GREY)
    pg.draw_line((M, 60), (W - M, 60), color=NAVY, width=1.1)

    txt(pg, M, 84, 'FEASIBILITY · MEASURED AREA TAKE-OFF', 8.5, True, GOLD)
    txt(pg, M, 104, 'Marked-up floor plans — the drawing record behind the floor area schedule', 16, True)
    para(pg, M, 122,
         f"Every polygon measured on the sheets that follow is reported in {cfg['workbook']}.  The figures printed on "
         'each sheet are the workbook figures — this set and the schedule are produced from one measurement and '
         'reconcile line for line.', W - 2 * M, 9, False, GREY)

    LX, LW = M, 560.0
    RX = 626.0
    RW = W - M - RX
    levels = cfg['levels']
    apts = cfg['apartments']
    nsa = {a['apt']: (None if a['internal'] is None else round((a['internal'] or 0) + (a['balcony'] or 0), 1))
           for a in apts}
    lvl_nsa = {}
    for a in apts:
        if a['internal'] is not None:
            lvl_nsa[a['level']] = round(lvl_nsa.get(a['level'], 0) + nsa[a['apt']], 1)

    # --- reconciliation table
    y = sect(pg, LX, 164, LW, 'RECONCILIATION TO THE WORKBOOK')
    CX = [LX, LX + 140, LX + 222, LX + 308, LX + 392, LX + 480, LX + LW]
    HD = ['Level', 'FECA (m²)', 'UCA (m²)', 'GFA (m²)', 'GBA (m²)', 'NSA (m²)', 'Apts']
    pg.draw_rect(pymupdf.Rect(LX, y - 11, LX + LW, y + 4.5), color=None, fill=PAPER)
    txt(pg, CX[0], y, HD[0], 8, True)
    for x, h in zip(CX[1:], HD[1:]):
        rtxt(pg, x, y, h, 8, True)
    rule(pg, LX, y + 4.5, LX + LW, NAVY, 0.6)
    y += 16
    tot = dict(feca=0, uca=0, gfa=0, gba=0, nsa=0, apts=0)
    for lv in levels:
        txt(pg, CX[0], y, lv['name'], 8.5)
        vals = [lv.get('feca'), lv.get('uca'), lv.get('gfa'), lv.get('gba'),
                lvl_nsa.get(lv['name']), lv.get('apts')]
        for x, v in zip(CX[1:], vals):
            rtxt(pg, x, y, num(v, 0 if x == CX[-1] else 1), 8.5)
        for k, v in zip(('feca', 'uca', 'gfa', 'gba', 'nsa', 'apts'), vals):
            tot[k] += v or 0
        rule(pg, LX, y + 4, LX + LW)
        y += 15
    txt(pg, CX[0], y, 'TOTAL', 8.5, True)
    for x, k in zip(CX[1:], ('feca', 'uca', 'gfa', 'gba', 'nsa', 'apts')):
        rtxt(pg, x, y, num(round(tot[k], 1), 0 if x == CX[-1] else 1), 8.5, True)
    rule(pg, LX, y - 11, LX + LW, NAVY, 0.6)
    rule(pg, LX, y + 4, LX + LW, NAVY, 1.0)
    y += 18
    pgfa = cfg.get('planning_gfa')
    y = para(pg, LX, y,
             f"GFA = FECA + UCA.  NSA is the sum of the {len(apts)} apartment lots and is scheduled unit by unit on the NSA & Revenue "
             f"tab.  The statutory {cfg.get('planning_scheme', 'planning-scheme')} GFA " + (f'({pgfa:,.1f} m²) ' if pgfa else '')
             + 'is a different measure again — it is reported in the workbook and is not marked up here.', LW, 8)

    # --- sheet index
    y = sect(pg, LX, y + 16, LW, 'SHEET INDEX')
    by_level = {lv['name']: lv for lv in levels}
    if not cfg['sheets']:
        y = para(pg, LX, y, '[One row per marked-up plan — sheet number, level, what the sheet shows, and that '
                            'level\u2019s headline figure. Measured-area sheets first, then area by category, then '
                            'apartment segmentation.]', LW, 8)
    for i, sh in enumerate(cfg['sheets'], 2):
        lv, kind = sh['level'], sh['kind']
        txt(pg, LX, y, f'{i:02d}', 8.5, True)
        txt(pg, LX + 26, y, f'{lv} — {TITLE[kind]}', 8.5)
        d = by_level.get(lv, {})
        if kind == 'mk':
            rtxt(pg, LX + LW, y, f"GFA {num(d.get('gfa'))}  ·  GBA {num(d.get('gba'))} m²", 8.5, False, GREY)
        elif kind == 'cat':
            rtxt(pg, LX + LW, y, f"FECA {num(d.get('feca'))} m²", 8.5, False, GREY)
        else:
            rtxt(pg, LX + LW, y, f'NSA {num(lvl_nsa.get(lv))} m²', 8.5, False, GREY)
        rule(pg, LX, y + 4, LX + LW)
        y += 15
    left_end = y

    # --- basis and authority
    y = sect(pg, RX, 164, RW, 'BASIS AND AUTHORITY FOR EACH MEASURE')
    for head, auth, paras in BASIS:
        txt(pg, RX, y, head, 9, True)
        y += 13
        y = para(pg, RX, y, auth, RW, 8, True, GOLD) + 3
        for p in paras:
            y = para(pg, RX, y, p, RW, 8) + 5
        y += 9

    y = sect(pg, RX, y + 4, RW, 'STATUS AND OPEN ITEMS')
    for s in cfg['open_items']:
        pg.draw_circle((RX + 2, y - 2.5), 1.3, color=None, fill=GOLD)
        y = para(pg, RX + 10, y, s, RW - 14, 8) + 4
    right_end = y

    # --- NSA by apartment
    if apts:
        y = sect(pg, M, max(left_end, right_end) + 22, W - 2 * M,
                 'NET SELLABLE AREA BY APARTMENT (m²)  —  NSA & Revenue tab')
        GW, GAP = 360.0, 22.0
        per = max(1, -(-len(apts) // 3))
        groups = [apts[i:i + per] for i in range(0, len(apts), per)][:3]
        for gi, grp in enumerate(groups):
            gx = M + gi * (GW + GAP)
            gc = [gx, gx + 96, gx + 190, gx + 272, gx + GW]
            pg.draw_rect(pymupdf.Rect(gx, y - 11, gx + GW, y + 4.5), color=None, fill=PAPER)
            txt(pg, gc[0], y, 'Apt', 8, True)
            txt(pg, gc[0] + 26, y, 'Level', 8, True)
            for x, h in zip(gc[1:], ['Internal', 'Balcony', 'TOTAL NSA']):
                rtxt(pg, x, y, h, 8, True)
            rule(pg, gx, y + 4.5, gx + GW, NAVY, 0.6)
            yy = y + 16
            for a in grp:
                txt(pg, gc[0], yy, a['apt'], 8.5, True)
                txt(pg, gc[0] + 26, yy, a['level'], 8.5)
                rtxt(pg, gc[1], yy, num(a['internal']), 8.5)
                rtxt(pg, gc[2], yy, num(a['balcony']), 8.5)
                rtxt(pg, gc[4], yy, num(nsa[a['apt']]), 8.5, True)
                rule(pg, gx, yy + 4, gx + GW)
                yy += 15
            if gi == len(groups) - 1:
                txt(pg, gc[0], yy, 'TOTAL', 8.5, True)
                ti = sum(a['internal'] or 0 for a in apts)
                tb = sum(a['balcony'] or 0 for a in apts)
                rtxt(pg, gc[1], yy, num(round(ti, 1)), 8.5, True)
                rtxt(pg, gc[2], yy, num(round(tb, 1)), 8.5, True)
                rtxt(pg, gc[4], yy, num(round(ti + tb, 1)), 8.5, True)
                rule(pg, gx, yy + 4, gx + GW, NAVY, 1.0)

    pg.draw_line((M, H - 34), (W - M, H - 34), color=RULE, width=0.5)
    txt(pg, M, H - 21,
        f"{cfg['project']} · Area take-off markups (AIQS / ASMM basis) · DRAFT · {cfg['issue_date']}", 8, False, GREY)
    rtxt(pg, W - M, H - 21, f'Page 1 of {npages}', 8, False, GREY)


# ------------------------------------------------------------------ plan sheets
def plan_sheet(doc, cfg, sh, idx, npages):
    import cv2
    im = cv2.imread(sh['image'])
    if im is None:
        raise SystemExit(f"cannot read markup image: {sh['image']}")
    jp = os.path.splitext(sh['image'])[0] + '_pg.jpg'
    cv2.imwrite(jp, cv2.resize(im, (3308, 2339), interpolation=cv2.INTER_AREA),
                [cv2.IMWRITE_JPEG_QUALITY, 88])
    ih, iw = im.shape[:2]
    lv, kind = sh['level'], sh['kind']
    d = next((l for l in cfg['levels'] if l['name'] == lv), {})

    pg = doc.new_page(width=W, height=H)
    logo = cfg.get('logo')
    if logo and os.path.exists(logo):
        pg.insert_image(pymupdf.Rect(M, 11, M + 188 * 0.40, 11 + 55 * 0.40), filename=logo)
    txt(pg, M + 92, 26, f"{cfg['project'].upper()}  ·  {cfg['address'].upper()}", 8.5, True)
    rtxt(pg, W - M, 26, f'{lv.upper()}  —  {TITLE[kind].upper()}', 8.5, True, GOLD)
    pg.draw_line((M, HEAD_H), (W - M, HEAD_H), color=NAVY, width=0.9)

    ax0, ay0, ax1, ay1 = M, HEAD_H + 6, W - M, H - FOOT_H
    sc = min((ax1 - ax0) / iw, (ay1 - ay0) / ih)
    dw, dh = iw * sc, ih * sc
    ox, oy = ax0 + (ax1 - ax0 - dw) / 2, ay0 + (ay1 - ay0 - dh) / 2
    pg.insert_image(pymupdf.Rect(ox, oy, ox + dw, oy + dh), filename=jp)

    apts = [a for a in cfg['apartments'] if a['level'] == lv]
    nsa = {a['apt']: round((a['internal'] or 0) + (a['balcony'] or 0), 1) for a in apts}

    # NSA callouts, anchored to the numbered region markers already on the plan
    if kind == 'apt':
        for (px, py), a in zip(cfg.get('seeds', {}).get(lv, []), apts):
            cx, cy = ox + px * sc, oy + py * sc
            s = f"{a['apt']}   {nsa[a['apt']]:,.1f} m²"
            tw = tl(s, 7.6, True)
            bx0, by0 = cx - (tw + 9) / 2, cy + 7.0
            pg.draw_rect(pymupdf.Rect(bx0, by0, bx0 + tw + 9, by0 + 11.5),
                         color=NAVY, fill=(1, 1, 1), width=0.6)
            txt(pg, bx0 + 4.5, by0 + 8.4, s, 7.6, True)

    pg.draw_line((M, H - FOOT_H + 8), (W - M, H - FOOT_H + 8), color=NAVY, width=0.9)
    if kind == 'mk':
        l1 = (f"{lv}:   FECA {d.get('feca') or 0:,.1f}  +  UCA {d.get('uca') or 0:,.1f}  =  "
              f"GFA {d.get('gfa') or 0:,.1f} m²      ·      GBA {d.get('gba') or 0:,.1f} m²      —      "
              f"as reported on the Level Schedule tab of {cfg['workbook']}")
        l2 = ('GFA (FECA + UCA) per the AIQS Australian Cost Management Manual (2022).  GBA per the Property Council / API / '
              'REIA Glossary of Property Terms — the enclosed and unenclosed area at all building floor levels, measured to '
              'the outside face of enclosing walls, balustrades and supports.')
    elif kind == 'cat':
        cats = cfg.get('categories', {}).get(lv, {})
        parts = '  +  '.join(f'{k} {v:,.1f}' for k, v in cats.items())
        l1 = f"{lv} FECA {d.get('feca') or 0:,.1f} m²   =   {parts}"
        l2 = sh.get('note', 'Reconcile these measured rooms to the categories used on the Area by Category tab.')
    else:
        det = '   ·   '.join(f"{a['apt']} {nsa[a['apt']]:,.1f}" for a in apts)
        tot = round(sum(nsa.values()), 1)
        l1 = (f'{lv} net sellable area (m²):    {det}    ·    level total {tot:,.1f} m² across '
              f'{len(apts)} apartments')
        l2 = ('Boxed figures are TOTAL NSA per apartment — internal area plus balcony or terrace — as scheduled unit by unit '
              f"on the NSA & Revenue tab of {cfg['workbook']}.  Grey is core, lobby and common property, which carries no NSA.")
    txt(pg, M, H - 24, l1, 8, True)
    txt(pg, M, H - 13, l2, 7.2, False, GREY)
    rtxt(pg, W - M, H - 13, f"DRAFT · {cfg['issue_date']} · Page {idx} of {npages}", 7.2, False, GREY)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('config', nargs='?', help='take-off config JSON')
    ap.add_argument('out', help='output PDF')
    ap.add_argument('--blank', action='store_true', help='blank cover only, for the template')
    ap.add_argument('--logo', help='path to the BDM logo PNG')
    a = ap.parse_args()

    if a.blank:
        cfg = dict(BLANK)
    else:
        if not a.config:
            ap.error('config is required unless --blank')
        cfg = json.load(open(a.config))
        for k, v in BLANK.items():
            cfg.setdefault(k, v)
    if a.logo:
        cfg['logo'] = a.logo

    npages = 1 + len(cfg['sheets'])
    doc = pymupdf.open()
    cover(doc, cfg, npages)
    for i, sh in enumerate(cfg['sheets'], 2):
        plan_sheet(doc, cfg, sh, i, npages)
    doc.subset_fonts()
    doc.save(a.out, deflate=True, garbage=3)
    print(f'{doc.page_count} pages -> {a.out}')


if __name__ == '__main__':
    main()
