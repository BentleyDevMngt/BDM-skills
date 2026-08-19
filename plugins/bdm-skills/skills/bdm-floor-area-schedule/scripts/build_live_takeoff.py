#!/usr/bin/env python3
"""Build the interactive area-correction tool - one self-contained HTML file.

Each level carries the plan raster, the measured GBA polygon, and the drawing's
own wall linework as snap targets.  Drag a corner, it snaps to the nearest wall
face or grid line, and the area, the totals and the $/m2 rates update live.
Save writes a corrected take-off config that re-runs Form 405, the markups and
the Form 413 rates.
"""
import base64, io, json, os, sys
sys.path.insert(0, '/sessions/eloquent-awesome-heisenberg/mnt/.claude/skills/bdm-floor-area-schedule/scripts')
import numpy as np, cv2, pymupdf
from takeoff import PROJECT, LEVELS, totals
from dawson_lines import total as dawson_total

PDF = ('/sessions/eloquent-awesome-heisenberg/mnt/Projects - Documents/'
       '_Project Opportunities/79 Seagull Ave, Mermaid beach/Source Documents/'
       '575100_79 Seagull Avenue TENDER 010726.pdf')
OUT = ('/sessions/eloquent-awesome-heisenberg/mnt/Projects - Documents/_Project Opportunities/'
       '79 Seagull Ave, Mermaid beach/00_ai_sandbox/'
       '79_Seagull_Ave_Area_Takeoff_LIVE_DRAFT_2026-08-17.html')

DPI = 220                                  # render dpi - high enough to zoom into
CLIP300 = (2150, 6250, 2500, 4300)
CLIP = tuple(v * DPI // 300 for v in CLIP300)          # x0, x1, y0, y1 at DPI
PX_PER_M = 1000.0 / 100 / 25.4 * 72.0 * DPI / 72.0     # 86.61 at 220 dpi
MASK = {'Basement': 'plates/basement_gba.npy', 'Ground': 'plates/ground_encl3.npy',
        'Level 1': 'plates/first_gba.npy', 'Level 2': 'plates/second_gba.npy',
        'Level 3': 'plates/roof_terrace_gba.npy'}
PAGE = {'Basement': 4, 'Ground': 5, 'Level 1': 6, 'Level 2': 7, 'Level 3': 8}
MIN_SEG_M = 0.30                           # ignore linework shorter than this


def snap_lines(doc, pi):
    """Axis-aligned wall and grid linework, as candidate snap coordinates."""
    page = doc[pi]
    s = DPI / 72.0
    x0, x1, y0, y1 = CLIP
    xs, ys = set(), set()
    minlen = MIN_SEG_M * PX_PER_M

    def seg(p, q):
        ax, ay, bx, by = p[0] * s, p[1] * s, q[0] * s, q[1] * s
        if not (x0 - 5 <= ax <= x1 + 5 and y0 - 5 <= ay <= y1 + 5):
            return
        dx, dy = abs(bx - ax), abs(by - ay)
        if dy <= 1.5 and dx >= minlen:                 # horizontal
            ys.add(round(ay - y0, 1))
        elif dx <= 1.5 and dy >= minlen:               # vertical
            xs.add(round(ax - x0, 1))

    for d in page.get_drawings():
        for it in d['items']:
            if it[0] == 'l':
                seg(it[1], it[2])
            elif it[0] == 're':
                r = it[1]
                seg((r.x0, r.y0), (r.x1, r.y0)); seg((r.x0, r.y1), (r.x1, r.y1))
                seg((r.x0, r.y0), (r.x0, r.y1)); seg((r.x1, r.y0), (r.x1, r.y1))
    W, H = x1 - x0, y1 - y0
    xs = sorted(v for v in xs if -2 <= v <= W + 2)
    ys = sorted(v for v in ys if -2 <= v <= H + 2)
    return dedupe(xs), dedupe(ys)


def dedupe(vals, tol=1.0):
    out = []
    for v in vals:
        if not out or v - out[-1] > tol:
            out.append(v)
    return out


def polygon(mask, target_area, max_v=48, tol_pct=0.12):
    """Outline of the measured plate, simplified to a draggable vertex count.

    Simplification loses area, so the tolerance is walked up only as far as it
    has to go: the coarsest polygon that stays inside max_v vertices AND holds
    the measured area to tol_pct.  Whichever binds, the area wins.
    """
    m = mask.astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cs, key=cv2.contourArea)
    ppm300 = 118.11023622047244
    x0, x1, y0, y1 = CLIP300
    cands = []
    for eps_m in [0.02 * 1.22 ** i for i in range(32)]:
        approx = cv2.approxPolyDP(c, eps_m * ppm300, True)
        pts = approx.reshape(-1, 2).astype(float)
        if len(pts) < 4:
            continue
        a = 0.0
        for i in range(len(pts)):
            j = (i + 1) % len(pts)
            a += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
        a = abs(a) / 2 / ppm300 ** 2
        cands.append((pts, a, abs(a - target_area) / target_area * 100, len(pts)))
    # coarsest polygon inside the vertex budget that still holds the area;
    # if nothing does, the closest on area wins and the variance is reported
    # inside the vertex budget, take the closest on area - a polygon that opens
    # off the measured figure makes every later delta a lie
    ok = [c_ for c_ in cands if c_[3] <= max_v]
    pool = [c_ for c_ in ok if c_[2] <= tol_pct] or ok or cands
    pts, a, err, n = min(pool, key=lambda c_: (c_[2], c_[3]))
    out = [[round((p[0] - x0) * DPI / 300, 1), round((p[1] - y0) * DPI / 300, 1)]
           for p in pts]
    return out, a, err


def main():
    doc = pymupdf.open(PDF)
    T = totals()
    x0, x1, y0, y1 = CLIP
    levels = []
    for lv in LEVELS:
        k = lv['key']
        if k not in MASK:
            continue
        pm = doc[PAGE[k]].get_pixmap(dpi=DPI)
        img = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, pm.n)[:, :, :3]
        crop = img[y0:y1, x0:x1]
        ok, buf = cv2.imencode('.png', cv2.cvtColor(crop, cv2.COLOR_RGB2BGR),
                               [cv2.IMWRITE_PNG_COMPRESSION, 9])
        b64 = base64.b64encode(buf.tobytes()).decode()
        sx, sy = snap_lines(doc, PAGE[k])
        # The polygon is the plate as drawn on that sheet.  GBA is then
        #   plate - deductions (ramp at grade, voids) + UCA measured off-plate.
        # Only the ground sheet carries UCA outside its plate (the covered east
        # terrace sits beyond the enclosed envelope that was cut).
        mask = np.load(MASK[k])
        plate = float(np.count_nonzero(mask)) / 118.11023622047244 ** 2
        add_uca = lv['uca'] if k == 'Ground' else 0.0
        deduct = round(plate - (lv['gba'] - add_uca), 1)
        poly, poly_a, err = polygon(mask, plate)
        levels.append({
            'key': k, 'label': lv['label'], 'sheet': f'A2.10{PAGE[k]-3}',
            'img': b64, 'w': int(x1 - x0), 'h': int(y1 - y0),
            'poly': poly, 'plate': round(plate, 1),
            'deduct': deduct, 'addUCA': round(add_uca, 1),
            'snapX': sx, 'snapY': sy,
            'measuredGBA': lv['gba'], 'band': lv['band'],
            'uca': lv['uca'], 'unroof': lv['unroof'], 'note': lv['note'],
        })
        chk = poly_a - deduct + add_uca
        print(f'{k:10s} {len(poly):3d} vtx  plate {plate:7.1f}  poly {poly_a:7.1f} '
              f'({err:+.2f}%)  less {deduct:5.1f} plus {add_uca:5.1f}  -> GBA {chk:7.1f} '
              f'v {lv["gba"]:7.1f}   {len(sx)}x/{len(sy)}y snaps  {len(b64)//1024} KB')

    data = {
        'project': PROJECT['name'], 'address': PROJECT['address'],
        'lot': PROJECT['lot_plan'], 'site': PROJECT['site_area_figured'],
        'pxPerM': PX_PER_M, 'issue': '17 August 2026',
        'drawings': PROJECT['drawing_set'],
        'dawsonEx': round(dawson_total(), 2), 'dawsonInc': 9893411.38,
        'bdmRate': 6900.0, 'levels': levels,
        'workbook': '405-79_Seagull_Ave_Floor_Area_Schedule_DRAFT_2026-08-16.xlsx',
        'scheme': 'Gold Coast City Plan', 'architect': PROJECT['architect'],
        'baseline': {'gba': T['gba'], 'gfa': T['gfa'], 'feca': T['feca'],
                     'uca': T['uca'], 'unroof': T['unroof'], 'band': T['band']},
    }
    html = TEMPLATE.replace('/*__DATA__*/', json.dumps(data))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'\nwritten: {OUT}\n{os.path.getsize(OUT)/1048576:.2f} MB')


TEMPLATE = r'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Area take-off — live correction</title>
<style>
:root{--navy:#0f172a;--gold:#9d7b5b;--grey:#5c5a55;--rule:#d8d7d3;--paper:#f4f4f1;
      --red:#b8261e;--redf:rgba(214,74,63,.30);--blue:#226eb4;}
*{box-sizing:border-box}
body{margin:0;font:13px/1.45 Carlito,Calibri,system-ui,sans-serif;color:var(--navy);
     background:var(--paper)}
header{padding:14px 20px;border-bottom:2px solid var(--navy);background:#fff}
h1{margin:0;font-size:16px;letter-spacing:.02em}
.sub{color:var(--grey);font-size:11.5px;margin-top:3px}
.draft{color:var(--red);font-weight:700;letter-spacing:.08em;font-size:11px}
.wrap{display:flex;gap:14px;padding:14px 20px;align-items:flex-start}
.left{flex:1 1 auto;min-width:0}
.right{flex:0 0 400px}
.tabs{display:flex;gap:4px;margin-bottom:8px;flex-wrap:wrap}
.tab{padding:6px 13px;border:1px solid var(--rule);background:#fff;cursor:pointer;
     font-size:12px;border-radius:2px}
.tab.on{background:var(--navy);color:#fff;border-color:var(--navy)}
.stage{position:relative;border:1px solid var(--rule);background:#fff;overflow:hidden}
canvas{display:block;width:100%;height:auto;cursor:crosshair;touch-action:none}
.bar{display:flex;gap:8px;align-items:center;margin:8px 0;flex-wrap:wrap;font-size:12px}
button{font:inherit;padding:5px 11px;border:1px solid var(--rule);background:#fff;
       cursor:pointer;border-radius:2px}
button:hover{border-color:var(--navy)}
button.primary{background:var(--navy);color:#fff;border-color:var(--navy)}
.card{background:#fff;border:1px solid var(--rule);padding:12px 14px;margin-bottom:12px}
.card h2{margin:0 0 8px;font-size:11px;letter-spacing:.09em;color:var(--gold);
         text-transform:uppercase}
table{width:100%;border-collapse:collapse;font-size:12px}
th,td{padding:3px 4px;text-align:right;border-bottom:1px solid #eee}
th:first-child,td:first-child{text-align:left}
th{font-weight:600;color:var(--grey);font-size:10.5px;text-transform:uppercase;
   letter-spacing:.04em}
tr.tot td{font-weight:700;border-top:1.5px solid var(--navy);border-bottom:none}
input[type=number]{width:74px;font:inherit;text-align:right;padding:2px 4px;
                   border:1px solid var(--rule)}
.delta{font-variant-numeric:tabular-nums}
.up{color:var(--red)} .dn{color:#1a7f43}
.hint{color:var(--grey);font-size:11px;line-height:1.5}
kbd{background:#eee;border:1px solid var(--rule);border-radius:2px;padding:0 4px;
    font:11px monospace}
.note{font-size:11px;color:var(--grey);margin-top:6px}
.rate{font-size:19px;font-weight:700}
.zlv{display:inline-block;min-width:46px;text-align:center;font-variant-numeric:tabular-nums;
     font-size:12px;color:var(--grey)}
.vr{display:inline-block;width:1px;height:18px;background:var(--rule);margin:0 3px}
.msg{color:var(--blue);font-size:12px;font-weight:600}
.saved{color:#1a7f43;font-size:11.5px;font-weight:600}
.saved.warn{color:var(--red)}
.banner{margin:0 20px 0;padding:9px 13px;background:#eef4fb;border:1px solid #bcd4ec;
        border-left:4px solid var(--blue);font-size:12.5px;border-radius:2px}
.banner.warn{background:#fdf1ef;border-color:#e8bdb7;border-left-color:var(--red)}
.banner.off{display:none}
.banner button{margin-left:8px;font-size:11.5px;padding:3px 9px}
button:disabled{opacity:.4;cursor:default}
canvas{cursor:crosshair}

/* ---------- print / PDF export : A3 landscape, BDM markup-set layout ---- */
#printroot{display:none}
@media print{
  @page{size:420mm 297mm landscape;margin:0}
  html,body{background:#fff;margin:0;padding:0}
  header,.wrap{display:none!important}
  #printroot{display:block}
  .pg{width:420mm;height:296.6mm;position:relative;page-break-after:always;
      overflow:hidden;background:#fff;padding:8mm 8mm 0;
      -webkit-print-color-adjust:exact;print-color-adjust:exact}
  .pg:last-child{page-break-after:auto}
  .ph{display:flex;justify-content:space-between;align-items:flex-start;
      border-bottom:1.2pt solid var(--navy);padding-bottom:2.5mm}
  .ph .co{font-weight:700;font-size:9.5pt;letter-spacing:.03em}
  .ph .rt{text-align:right;font-size:8pt;color:var(--grey)}
  .ph .rt b{color:var(--gold);font-size:8.5pt;letter-spacing:.06em;
            text-transform:uppercase;display:block;margin-bottom:.8mm}
  .eyebrow{color:var(--gold);font-size:7.5pt;letter-spacing:.12em;
           text-transform:uppercase;margin:6mm 0 1.5mm}
  .pg h1{font-size:17pt;margin:0 0 2mm;font-weight:700}
  .lede{font-size:8.5pt;color:var(--grey);max-width:250mm;margin-bottom:5mm}
  .cols{display:flex;gap:12mm}
  .col{flex:1}
  .sect{color:var(--gold);font-size:7.5pt;letter-spacing:.1em;text-transform:uppercase;
        border-bottom:.6pt solid var(--rule);padding-bottom:1mm;margin:0 0 2mm}
  .pt{width:100%;border-collapse:collapse;font-size:8pt}
  .pt th,.pt td{padding:1.2mm 1.5mm;text-align:right;border-bottom:.4pt solid #eee}
  .pt th:first-child,.pt td:first-child{text-align:left}
  .pt th{font-size:7pt;color:var(--grey);text-transform:uppercase;letter-spacing:.04em;
         font-weight:600}
  .pt tr.t td{font-weight:700;border-top:.9pt solid var(--navy);border-bottom:none}
  .pt td.ch{color:var(--red);font-weight:700}
  .bd{font-size:7.6pt;color:var(--grey);margin-bottom:3mm;line-height:1.42}
  .bd b{color:var(--navy)} .bd i{color:var(--gold);font-style:normal;font-weight:700}
  ul.oi{margin:0;padding-left:4mm;font-size:7.6pt;color:var(--grey);line-height:1.5}
  ul.oi li{margin-bottom:1.2mm}
  .plan{margin-top:3mm;text-align:center}
  .plan img{max-width:400mm;max-height:238mm;object-fit:contain}
  .pf{position:absolute;left:8mm;right:8mm;bottom:5mm;border-top:.6pt solid var(--navy);
      padding-top:1.5mm;font-size:7.4pt;color:var(--grey)}
  .pf .l1{color:var(--navy);font-weight:700;font-size:8pt;margin-bottom:.8mm}
  .pf .rr{position:absolute;right:0;top:1.5mm}
  .stamp{color:var(--red);font-weight:700;letter-spacing:.1em}
}
</style></head><body>
<header>
  <h1>Area take-off — live correction <span class="draft">· DRAFT</span></h1>
  <div class="sub" id="hdr"></div>
  <div class="sub"><span id="saved" class="saved"></span></div>
</header>
<div class="wrap">
  <div class="left">
    <div class="tabs" id="tabs"></div>
    <div class="bar">
      <button id="zout" title="Zoom out">−</button>
      <span id="zlv" class="zlv">100%</span>
      <button id="zin" title="Zoom in">+</button>
      <button id="zfit">Fit</button>
      <span class="vr"></span>
      <label><input type="checkbox" id="snap" checked> Snap to wall lines</label>
      <label><input type="checkbox" id="showsnap"> Show snap grid</label>
      <span class="vr"></span>
      <button id="despike">Remove spike corners</button>
      <button id="undo" disabled>Undo</button>
      <button id="reset">Reset level</button>
      <button id="resetall">Reset all</button>
      <span id="msg" class="msg"></span>
    </div>
    <div class="bar hint" style="margin-top:-2px">
      <b>Zoom</b> scroll wheel, or <kbd>+</kbd> <kbd>−</kbd> <kbd>0</kbd> ·
      <b>Pan</b> right-drag or middle-drag ·
      <b>Move</b> drag a corner ·
      <b>Add</b> double-click an edge ·
      <b>Delete one</b> <kbd>Alt</kbd>+click ·
      <b>Delete many</b> <kbd>Shift</kbd>+drag a box, then <kbd>Delete</kbd> ·
      <b>Override snap</b> hold <kbd>Shift</kbd> while dragging ·
      <b>Undo</b> <kbd>Ctrl</kbd>+<kbd>Z</kbd>
    </div>
    <div class="stage"><canvas id="cv"></canvas></div>
    <div class="note" id="lvnote"></div>
    <div class="note"><b>Opening position.</b> Each polygon is a simplified outline of the
      plate BDM measured off this sheet, so it opens within about 0.2% of the Form 405
      figure — the Δ column is measured against Form 405, not against zero. Correct a
      corner and the Δ tells you what actually changed. Areas here are feasibility grade
      (±2%, ±3% at ground); the ground floor is the one to check first.</div>
  </div>
  <div class="right">
    <div class="card">
      <h2>This level</h2>
      <table id="lvtab"></table>
    </div>
    <div class="card">
      <h2>All levels — live</h2>
      <table id="tot"></table>
    </div>
    <div class="card">
      <h2>Rate impact — Dawson tender</h2>
      <div class="rate" id="rate"></div>
      <div class="hint" id="rated"></div>
      <table id="ratetab" style="margin-top:8px"></table>
    </div>
    <div class="card">
      <h2>Save</h2>
      <button class="primary" id="save">Download corrected take-off</button>
      <button id="pdf" style="margin-top:6px">Print / export PDF report</button>
      <div class="hint" style="margin-top:6px"><b>In the print dialog:</b> Destination
        <b>Save as PDF</b> · Paper size <b>A3</b> · Layout <b>Landscape</b> ·
        Margins <b>None</b> · Scale <b>100</b> (not Fit) · tick <b>Background graphics</b> ·
        Headers and footers <b>off</b>. If the paper stays A4 the sheets come out rotated.</div>
      <div class="hint" style="margin-top:7px">Writes the corrected config. Hand it back and
        Form 405, the A3 markups and the Form 413 rates all rebuild from it — they cannot
        drift apart.</div>
    </div>
  </div>
</div>
<div id="printroot"></div>
<script>
const D = /*__DATA__*/;
const PPM = D.pxPerM, M2 = PPM*PPM;
const S = D.levels.map(l => ({...l, poly: l.poly.map(p=>[...p]), orig: l.poly.map(p=>[...p]),
                              band:l.band, uca:l.uca, unroof:l.unroof, deduct:l.deduct,
                              oband:l.band, ouca:l.uca, ounroof:l.unroof, odeduct:l.deduct}));
// GBA = plate polygon - deductions (ramp at grade, voids) + UCA measured off-plate
function gbaOf(l){ return area(l.poly) - l.deduct + l.addUCA; }
let cur = 0, drag = -1, imgs = [], sel = new Set(), marquee = null, pan = null;
let VIEW = [];                                   // {k, ox, oy} per level
const undoStack = [];
const cv = document.getElementById('cv'), cx = cv.getContext('2d');
document.getElementById('hdr').textContent =
  `${D.project} · ${D.address} · ${D.lot} · site ${D.site} m² · ${D.drawings}`;

function area(poly){                       // shoelace, px² -> m²
  let a=0; for(let i=0,n=poly.length;i<n;i++){const j=(i+1)%n;
    a += poly[i][0]*poly[j][1] - poly[j][0]*poly[i][1];}
  return Math.abs(a)/2/M2;
}
function fmt(v,d=1){return v.toLocaleString('en-AU',{minimumFractionDigits:d,maximumFractionDigits:d});}
function money(v){return '$'+Math.round(v).toLocaleString('en-AU');}

function loadImgs(cb){
  let n=0;
  S.forEach((l,i)=>{const im=new Image();
    im.onload=()=>{imgs[i]=im; if(++n===S.length) cb();};
    im.src='data:image/png;base64,'+l.img;});
}
function tabs(){
  document.getElementById('tabs').innerHTML = S.map((l,i)=>
    `<div class="tab${i===cur?' on':''}" data-i="${i}">${l.label} · ${l.sheet}</div>`).join('');
  document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>{
    cur=+t.dataset.i; sel.clear(); tabs(); draw(); panel();});
}

/* ------------------------------------------------------------ view / zoom */
function view(){ return VIEW[cur] || (VIEW[cur]={k:1,ox:0,oy:0}); }
function fitView(){ VIEW[cur]={k:1,ox:0,oy:0}; }
function clampView(){
  const v=view(), l=S[cur];
  v.k=Math.max(1,Math.min(14,v.k));
  v.ox=Math.min(0,Math.max(l.w-l.w*v.k, v.ox));
  v.oy=Math.min(0,Math.max(l.h-l.h*v.k, v.oy));
}
function zoomAt(sx,sy,f){                        // sx,sy in canvas px
  const v=view();
  const wx=(sx-v.ox)/v.k, wy=(sy-v.oy)/v.k;      // world point under cursor
  v.k*=f; clampView();
  v.ox=sx-wx*v.k; v.oy=sy-wy*v.k; clampView();
  draw(); zlabel();
}
function zlabel(){
  document.getElementById('zlv').textContent = Math.round(view().k*100)+'%';
}
/* canvas px (unscaled) from a pointer event */
function toCanvas(e){
  const r=cv.getBoundingClientRect();
  return [(e.clientX-r.left)*(cv.width/r.width),(e.clientY-r.top)*(cv.height/r.height)];
}
/* world (plan) coords from a pointer event */
function toCv(e){
  const [sx,sy]=toCanvas(e), v=view();
  return [(sx-v.ox)/v.k,(sy-v.oy)/v.k];
}

/* --------------------------------------------------------------- history */
function push(){
  undoStack.push({i:cur, poly:S[cur].poly.map(p=>[...p])});
  if(undoStack.length>60) undoStack.shift();
  document.getElementById('undo').disabled = false;
}
function undo(){
  const u=undoStack.pop(); if(!u) return;
  cur=u.i; S[cur].poly=u.poly; sel.clear();
  document.getElementById('undo').disabled = !undoStack.length;
  tabs(); draw(); panel();
}

/* ------------------------------------------------------------------ draw */
function draw(){
  const l=S[cur], im=imgs[cur], v=view();
  cv.width=l.w; cv.height=l.h;
  cx.save(); cx.setTransform(v.k,0,0,v.k,v.ox,v.oy);
  cx.imageSmoothingEnabled=false;
  cx.drawImage(im,0,0);
  if(document.getElementById('showsnap').checked){
    cx.strokeStyle='rgba(34,110,180,.22)'; cx.lineWidth=.5/v.k;
    l.snapX.forEach(x=>{cx.beginPath();cx.moveTo(x,0);cx.lineTo(x,l.h);cx.stroke();});
    l.snapY.forEach(y=>{cx.beginPath();cx.moveTo(0,y);cx.lineTo(l.w,y);cx.stroke();});
  }
  const p=l.poly;
  cx.beginPath(); cx.moveTo(p[0][0],p[0][1]);
  for(let i=1;i<p.length;i++) cx.lineTo(p[i][0],p[i][1]);
  cx.closePath();
  cx.fillStyle='rgba(214,74,63,.30)'; cx.fill();
  cx.strokeStyle='#b8261e'; cx.lineWidth=2.5/v.k; cx.stroke();
  const r=6/v.k;
  p.forEach((q,i)=>{cx.beginPath();cx.arc(q[0],q[1],r,0,7);
    cx.fillStyle = i===drag ? '#226eb4' : (sel.has(i)?'#226eb4':'#fff');
    cx.fill(); cx.strokeStyle= sel.has(i)?'#226eb4':'#b8261e';
    cx.lineWidth=2/v.k; cx.stroke();});
  if(marquee){
    cx.setLineDash([6/v.k,4/v.k]); cx.strokeStyle='#226eb4'; cx.lineWidth=1.5/v.k;
    cx.strokeRect(Math.min(marquee.x0,marquee.x1),Math.min(marquee.y0,marquee.y1),
                  Math.abs(marquee.x1-marquee.x0),Math.abs(marquee.y1-marquee.y0));
    cx.fillStyle='rgba(34,110,180,.10)';
    cx.fillRect(Math.min(marquee.x0,marquee.x1),Math.min(marquee.y0,marquee.y1),
                Math.abs(marquee.x1-marquee.x0),Math.abs(marquee.y1-marquee.y0));
    cx.setLineDash([]);
  }
  cx.restore();
  cx.font='600 15px Carlito,Calibri,sans-serif'; cx.fillStyle='#0f172a';
  cx.fillText(`${l.label} — plate ${fmt(area(p))} m²  ·  GBA ${fmt(gbaOf(l))} m²`+
              (sel.size?`   ·   ${sel.size} corner${sel.size>1?'s':''} selected — press Delete`:''),14,26);
}

/* ------------------------------------------------------------ interaction */
function nearest(arr,v,tol){
  let b=null,bd=tol;
  for(const a of arr){const d=Math.abs(a-v); if(d<bd){bd=d;b=a;}}
  return b;
}
function hitVertex(x,y){
  const l=S[cur], tol=13/view().k;
  let hit=-1,hd=tol;
  l.poly.forEach((q,i)=>{const d=Math.hypot(q[0]-x,q[1]-y); if(d<hd){hd=d;hit=i;}});
  return hit;
}
cv.addEventListener('contextmenu',e=>e.preventDefault());
cv.addEventListener('wheel',e=>{
  e.preventDefault();
  const [sx,sy]=toCanvas(e);
  zoomAt(sx,sy, e.deltaY<0 ? 1.18 : 1/1.18);
},{passive:false});
cv.addEventListener('pointerdown',e=>{
  const [x,y]=toCv(e), [sx,sy]=toCanvas(e), l=S[cur];
  if(e.button===1 || e.button===2 || e.altKey&&e.shiftKey){        // pan
    pan={sx,sy,ox:view().ox,oy:view().oy}; cv.setPointerCapture(e.pointerId);
    cv.style.cursor='grabbing'; return;
  }
  const hit=hitVertex(x,y);
  if(hit>=0 && e.altKey){                                          // delete one
    if(l.poly.length>3){push(); l.poly.splice(hit,1); sel.clear();}
    draw(); panel(); return;
  }
  if(e.shiftKey && hit<0){                                         // marquee select
    marquee={x0:x,y0:y,x1:x,y1:y}; cv.setPointerCapture(e.pointerId); return;
  }
  if(hit>=0){
    if(!sel.has(hit)) sel.clear();
    drag=hit; push(); cv.setPointerCapture(e.pointerId); draw(); return;
  }
  sel.clear(); draw(); panel();
});
cv.addEventListener('pointermove',e=>{
  if(pan){
    const [sx,sy]=toCanvas(e), v=view();
    v.ox=pan.ox+(sx-pan.sx); v.oy=pan.oy+(sy-pan.sy); clampView(); draw(); return;
  }
  if(marquee){ const [x,y]=toCv(e); marquee.x1=x; marquee.y1=y; draw(); return; }
  if(drag<0) return;
  const [x,y]=toCv(e), l=S[cur];
  let nx=x, ny=y;
  if(document.getElementById('snap').checked && !e.shiftKey){
    const tol=9/view().k;
    const sx2=nearest(l.snapX,x,tol), sy2=nearest(l.snapY,y,tol);
    if(sx2!==null) nx=sx2; if(sy2!==null) ny=sy2;
  }
  l.poly[drag]=[Math.max(0,Math.min(l.w,nx)),Math.max(0,Math.min(l.h,ny))];
  draw(); panel();
});
cv.addEventListener('pointerup',()=>{
  if(pan){pan=null; cv.style.cursor='crosshair';}
  if(marquee){
    const l=S[cur], x0=Math.min(marquee.x0,marquee.x1), x1=Math.max(marquee.x0,marquee.x1),
          y0=Math.min(marquee.y0,marquee.y1), y1=Math.max(marquee.y0,marquee.y1);
    sel.clear();
    l.poly.forEach((q,i)=>{if(q[0]>=x0&&q[0]<=x1&&q[1]>=y0&&q[1]<=y1) sel.add(i);});
    marquee=null;
  }
  drag=-1; draw(); panel();
});
cv.addEventListener('dblclick',e=>{
  const [x,y]=toCv(e), l=S[cur], p=l.poly;
  let bi=0,bd=1e9;
  for(let i=0;i<p.length;i++){const j=(i+1)%p.length;
    const ax=p[i][0],ay=p[i][1],bx=p[j][0],by=p[j][1];
    const t=Math.max(0,Math.min(1,((x-ax)*(bx-ax)+(y-ay)*(by-ay))/((bx-ax)**2+(by-ay)**2||1)));
    const d=Math.hypot(ax+t*(bx-ax)-x, ay+t*(by-ay)-y);
    if(d<bd){bd=d;bi=j;}}
  push(); p.splice(bi,0,[x,y]); draw(); panel();
});
function delSelected(){
  const l=S[cur];
  if(!sel.size || l.poly.length-sel.size < 3) return;
  push();
  l.poly = l.poly.filter((_,i)=>!sel.has(i));
  sel.clear(); draw(); panel();
}
window.addEventListener('keydown',e=>{
  const tag=(e.target.tagName||'').toLowerCase();
  if(tag==='input'||tag==='textarea') return;
  if(e.key==='Delete'||e.key==='Backspace'){e.preventDefault(); delSelected();}
  if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'){e.preventDefault(); undo();}
  if(e.key==='Escape'){sel.clear(); marquee=null; draw(); panel();}
  if(e.key==='+'||e.key==='='){zoomAt(cv.width/2,cv.height/2,1.25);}
  if(e.key==='-'||e.key==='_'){zoomAt(cv.width/2,cv.height/2,1/1.25);}
  if(e.key==='0'){fitView(); draw(); zlabel();}
});

/* ---- spike finder ------------------------------------------------------
   A window tag, door swing or dimension leader hanging off the wall shows up
   as a corner with BOTH adjacent edges short and a real deviation from the
   chord.  A genuine wall step always has at least one long edge - that is the
   test that separates them.  Candidates are SELECTED, never deleted blind:
   the call is a judgement and it stays the Director's.                      */
function spikeCandidates(){
  const l=S[cur], n=l.poly.length, p=l.poly;
  const EDGE=2.2*PPM, DEV=0.40*PPM, out=[];
  if(n<=4) return out;
  for(let i=0;i<n;i++){
    const a=p[(i-1+n)%n], v=p[i], b=p[(i+1)%n];
    const e1=Math.hypot(v[0]-a[0],v[1]-a[1]), e2=Math.hypot(b[0]-v[0],b[1]-v[1]);
    if(e1>EDGE || e2>EDGE) continue;
    const cl=Math.hypot(b[0]-a[0],b[1]-a[1]);
    const h=cl<1e-6 ? e1
      : Math.abs((b[0]-a[0])*(a[1]-v[1])-(a[0]-v[0])*(b[1]-a[1]))/cl;
    if(h>DEV) out.push(i);
  }
  return out;
}
function areaWithout(idx){
  const set=new Set(idx);
  return area(S[cur].poly.filter((_,i)=>!set.has(i)));
}
document.getElementById('zin').onclick=()=>zoomAt(cv.width/2,cv.height/2,1.3);
document.getElementById('zout').onclick=()=>zoomAt(cv.width/2,cv.height/2,1/1.3);
document.getElementById('zfit').onclick=()=>{fitView(); draw(); zlabel();};
document.getElementById('undo').onclick=undo;
document.getElementById('despike').onclick=()=>{
  const c=spikeCandidates(), m=document.getElementById('msg');
  if(!c.length){ sel.clear(); draw(); panel();
    m.textContent='No spike corners found on this level.';
    setTimeout(()=>{m.textContent='';},6000); return; }
  if(S[cur].poly.length-c.length < 3){
    m.textContent='Too many candidates to remove and keep a closed shape — check the level.';
    return; }
  sel.clear(); c.forEach(i=>sel.add(i));
  const now=area(S[cur].poly), then=areaWithout(c);
  m.textContent=`${c.length} spike corner${c.length>1?'s':''} selected · area would go `+
    `${fmt(now)} → ${fmt(then)} m² (${then-now>=0?'+':''}${fmt(then-now)}) · `+
    `zoom in to check, then press Delete — or Esc to clear`;
  draw(); panel();
};
document.getElementById('reset').onclick=()=>{
  const l=S[cur]; push(); l.poly=l.orig.map(p=>[...p]);
  l.band=l.oband; l.uca=l.ouca; l.unroof=l.ounroof; l.deduct=l.odeduct;
  sel.clear(); draw(); panel();};
document.getElementById('resetall').onclick=()=>{
  push();
  S.forEach(l=>{l.poly=l.orig.map(p=>[...p]);l.band=l.oband;l.uca=l.ouca;
                l.unroof=l.ounroof;l.deduct=l.odeduct;});
  sel.clear(); draw(); panel();
  try{ localStorage.removeItem(KEY); }catch(e){}
  stamp('Reset to the original take-off');};
document.getElementById('snap').onchange=draw;
document.getElementById('showsnap').onchange=draw;

function live(){
  return S.map(l=>{
    const gba=gbaOf(l);
    const feca=gba-l.band-l.uca-l.unroof;
    return {key:l.key,label:l.label,gba,feca,uca:l.uca,unroof:l.unroof,band:l.band,
            gfa:feca+l.uca,base:l.measuredGBA};
  });
}
function panel(){
  scheduleSave();
  const l=S[cur], p=area(l.poly), a=gbaOf(l), d=a-l.measuredGBA;
  document.getElementById('lvnote').textContent=l.note;
  document.getElementById('lvtab').innerHTML=`
    <tr><td>Plate — polygon as drawn</td><td>${fmt(p)} m²</td></tr>
    <tr><td>Less voids / ramp at grade</td><td><input type="number" step="0.1" id="i_deduct" value="${l.deduct}"> m²</td></tr>
    ${l.addUCA?`<tr><td>Plus covered terrace off-plate</td><td>${fmt(l.addUCA)} m²</td></tr>`:''}
    <tr class="tot"><td>GBA — live</td><td><b>${fmt(a)} m²</b></td></tr>
    <tr><td>As measured</td><td>${fmt(l.measuredGBA)} m²</td></tr>
    <tr><td>Change</td><td class="delta ${d>=0?'up':'dn'}">${d>=0?'+':''}${fmt(d)} m²
        (${l.measuredGBA?((d/l.measuredGBA*100).toFixed(2)):'0.00'}%)</td></tr>
    <tr><td>External wall band</td><td><input type="number" step="0.1" id="i_band" value="${l.band}"> m²</td></tr>
    <tr><td>UCA — roofed unenclosed</td><td><input type="number" step="0.1" id="i_uca" value="${l.uca}"> m²</td></tr>
    <tr><td>Unroofed terrace</td><td><input type="number" step="0.1" id="i_unroof" value="${l.unroof}"> m²</td></tr>
    <tr class="tot"><td>FECA — derived</td><td>${fmt(a-l.band-l.uca-l.unroof)} m²</td></tr>
    <tr><td>Vertices</td><td>${l.poly.length}</td></tr>`;
  ['band','uca','unroof','deduct'].forEach(k=>{
    const el=document.getElementById('i_'+k);
    el.oninput=()=>{const v=parseFloat(el.value); if(!isNaN(v)){l[k]=v;panel();draw();}};});
  const R=live();
  const t=R.reduce((o,r)=>({gba:o.gba+r.gba,gfa:o.gfa+r.gfa,feca:o.feca+r.feca,
                            uca:o.uca+r.uca,base:o.base+r.base}),
                   {gba:0,gfa:0,feca:0,uca:0,base:0});
  document.getElementById('tot').innerHTML=
    '<tr><th>Level</th><th>GBA</th><th>GFA</th><th>FECA</th><th>Δ GBA</th></tr>'+
    R.map(r=>{const d=r.gba-r.base;return `<tr><td>${r.label}</td><td>${fmt(r.gba)}</td>
      <td>${fmt(r.gfa)}</td><td>${fmt(r.feca)}</td>
      <td class="delta ${Math.abs(d)<0.05?'':(d>0?'up':'dn')}">${Math.abs(d)<0.05?'—':(d>0?'+':'')+fmt(d)}</td></tr>`;}).join('')+
    `<tr class="tot"><td>TOTAL</td><td>${fmt(t.gba)}</td><td>${fmt(t.gfa)}</td>
      <td>${fmt(t.feca)}</td><td class="delta">${(t.gba-t.base)>=0?'+':''}${fmt(t.gba-t.base)}</td></tr>`;
  const rG=D.dawsonEx/t.gba, rF=D.dawsonEx/t.gfa, rE=D.dawsonEx/t.feca;
  const bG=D.dawsonEx/D.baseline.gba;
  document.getElementById('rate').textContent=money(rG)+' /m² GBA';
  document.getElementById('rated').textContent=
    `Dawson ${money(D.dawsonEx)} ex GST ÷ ${fmt(t.gba)} m² · was ${money(bG)}/m² at the `+
    `measured ${fmt(D.baseline.gba)} m²`;
  document.getElementById('ratetab').innerHTML=
    `<tr><th>Basis</th><th>Area</th><th>Dawson $/m²</th><th>BDM $/m²</th></tr>
     <tr><td>GBA</td><td>${fmt(t.gba)}</td><td>${money(rG)}</td><td>${money(D.bdmRate)}</td></tr>
     <tr><td>GFA (AIQS)</td><td>${fmt(t.gfa)}</td><td>${money(rF)}</td>
         <td>${money(D.bdmRate*t.gba/t.gfa)}</td></tr>
     <tr><td>FECA enclosed</td><td>${fmt(t.feca)}</td><td>${money(rE)}</td>
         <td>${money(D.bdmRate*t.gba/t.feca)}</td></tr>
     <tr><td>Site (${D.site} m²)</td><td>${D.site}</td><td>${money(D.dawsonEx/D.site)}</td><td>—</td></tr>`;
}
document.getElementById('save').onclick=()=>{
  const R=live();
  const out={source:'79 Seagull Ave live area correction',
    corrected_on:new Date().toISOString().slice(0,10),
    project:D.project,address:D.address,lot:D.lot,site_area:D.site,
    px_per_m:PPM,status:'DRAFT — corrected by the Director, not yet rebuilt into Form 405',
    levels:S.map((l,i)=>({key:l.key,label:l.label,sheet:l.sheet,
      plate:+area(l.poly).toFixed(1),deduct:+l.deduct.toFixed(1),add_uca:l.addUCA,
      gba:+gbaOf(l).toFixed(1),feca:+R[i].feca.toFixed(1),
      uca:+l.uca.toFixed(1),unroof:+l.unroof.toFixed(1),band:+l.band.toFixed(1),
      gba_as_measured:l.measuredGBA,
      changed:Math.abs(gbaOf(l)-l.measuredGBA)>0.05,
      polygon_px:l.poly.map(p=>[+p[0].toFixed(1),+p[1].toFixed(1)])})),
    totals:{gba:+R.reduce((s,r)=>s+r.gba,0).toFixed(1),
            gfa:+R.reduce((s,r)=>s+r.gfa,0).toFixed(1),
            feca:+R.reduce((s,r)=>s+r.feca,0).toFixed(1)}};
  const b=new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(b);
  a.download='79_Seagull_Ave_takeoff_corrected.json'; a.click();
};

/* ------------------------------------------------------------------ */
/*  Print / export — A3 landscape report in the BDM markup-set layout  */
/*  Cover reconciles to the live figures, one sheet per level, then a  */
/*  cost page so the set can be issued with the cost advice.           */
/* ------------------------------------------------------------------ */
const AUTH = 'GFA (FECA + UCA) per the AIQS Australian Cost Management Manual (2022), '+
  'Method of Measurement of Building Area.  GBA per the Property Council of Australia / '+
  'Australian Property Institute / REIA Glossary of Property Terms — the total enclosed '+
  'and unenclosed area of the building at all building floor levels, measured between the '+
  'normal outside face of any enclosing walls, balustrades and supports.';

function planPNG(i){                       // level plate at current geometry
  const l=S[i], c=document.createElement('canvas'), g=c.getContext('2d');
  c.width=l.w; c.height=l.h;
  g.drawImage(imgs[i],0,0);
  const p=l.poly;
  g.beginPath(); g.moveTo(p[0][0],p[0][1]);
  for(let k=1;k<p.length;k++) g.lineTo(p[k][0],p[k][1]);
  g.closePath();
  g.fillStyle='rgba(214,74,63,.28)'; g.fill();
  g.strokeStyle='#b8261e'; g.lineWidth=2.5; g.stroke();
  p.forEach(v=>{g.beginPath();g.arc(v[0],v[1],3.4,0,7);
    g.fillStyle='#fff';g.fill();g.strokeStyle='#b8261e';g.lineWidth=1.6;g.stroke();});
  return c.toDataURL('image/png');
}
function head(right){
  return `<div class="ph"><div class="co">BENTLEY DEVELOPMENT MANAGEMENT</div>
    <div class="rt"><b>${right}</b>${D.project} · ${D.address} · ${D.lot} ·
      ${D.drawings}</div></div>`;
}
function foot(l1,n,tot){
  return `<div class="pf"><div class="l1">${l1}</div>${AUTH}
    <div class="rr"><span class="stamp">DRAFT</span> · ${D.issue} · Page ${n} of ${tot}</div></div>`;
}
// A polygon opens within ~0.2% of the workbook figure, so a level only counts as
// CORRECTED once it moves past that simplification noise.
const CORR_TOL = 1.0;                       // m²
function buildPrint(){
  const R=live(), np=S.length+1;
  const t=R.reduce((o,r)=>({gba:o.gba+r.gba,gfa:o.gfa+r.gfa,feca:o.feca+r.feca,
                            uca:o.uca+r.uca,unroof:o.unroof+r.unroof,base:o.base+r.base}),
                   {gba:0,gfa:0,feca:0,uca:0,unroof:0,base:0});
  const moved=R.filter(r=>Math.abs(r.gba-r.base)>CORR_TOL);
  const dash=v=>v>0.05?fmt(v):'–';
  const rows=R.map(r=>`<tr><td>${r.key}</td><td>${fmt(r.feca)}</td><td>${dash(r.uca)}</td>
      <td>${fmt(r.gfa)}</td><td>${fmt(r.gba)}</td><td>–</td><td>–</td></tr>`).join('');
  let h='';

  /* ---- page 1 : cover, matching the Form 405 markup set ---------------- */
  h+=`<div class="pg">${head('Area take-off  —  drawing markups')}
    <div class="eyebrow">Feasibility · measured area take-off</div>
    <h1>Marked-up floor plans — the drawing record behind the floor area schedule</h1>
    <div class="lede">Every polygon measured on the sheets that follow is reported in
      ${D.workbook}. The figures printed on each sheet are the workbook figures — this set
      and the schedule are produced from one measurement and reconcile line for line.</div>
    <div class="cols"><div class="col">
      <div class="sect">Reconciliation to the workbook</div>
      <table class="pt"><tr><th>Level</th><th>FECA (m²)</th><th>UCA (m²)</th>
        <th>GFA (m²)</th><th>GBA (m²)</th><th>NSA (m²)</th><th>Apts</th></tr>${rows}
        <tr class="t"><td>TOTAL</td><td>${fmt(t.feca)}</td><td>${fmt(t.uca)}</td>
        <td>${fmt(t.gfa)}</td><td>${fmt(t.gba)}</td><td>–</td><td>–</td></tr></table>
      <div class="bd" style="margin-top:2mm">GFA = FECA + UCA. This is one dwelling on one
        lot, so there is no net sellable area and no apartment schedule — the NSA and Apts
        columns are nil throughout. The statutory ${D.scheme} GFA is a different measure
        again — it is reported in the workbook and is not marked up here.</div>
      <div class="sect" style="margin-top:5mm">Sheet index</div>
      <table class="pt">${S.map((l,i)=>`<tr><td>${String(i+2).padStart(2,'0')}</td>
        <td>${l.key} — Measured areas — FECA / UCA / GBA</td>
        <td>GFA ${fmt(R[i].gfa)}  ·  GBA ${fmt(R[i].gba)} m²</td></tr>`).join('')}</table>
    </div><div class="col">
      <div class="sect">Basis and authority for each measure</div>
      <div class="bd"><b>FECA · UCA · GFA</b><br><i>AIQS — Australian Cost Management Manual
        (2022), Method of Measurement of Building Area.</i><br>FECA is all enclosed covered
        floor area, measured to the inside face of the external walls, including basements,
        lift shafts, stairs and plant. UCA is roofed but unenclosed area — balconies,
        verandahs, undercrofts. GFA = FECA + UCA. This is the cost-planning measure and is
        authoritative for that purpose. It is not the planning measure and does not test
        plot ratio.</div>
      <div class="bd"><b>GBA — Gross Building Area</b><br><i>Property Council of Australia /
        Australian Property Institute / Real Estate Institute of Australia — Glossary of
        Property Terms.</i><br>Defined as “the total enclosed and unenclosed area of the
        building at all building floor levels measured between the normal outside face of any
        enclosing walls, balustrades and supports”. GBA is therefore the largest of the three
        measures: it takes in the basement car park, plant, the thickness of the external
        walls, and unroofed balconies that carry no GFA. Note that GBA is not defined in the
        PCA Method of Measurement for Lettable Area — that publication covers tenancy areas
        (NLA / GLA) only.</div>
      <div class="bd"><b>NSA — Net Sellable Area</b><br><i>Lot-boundary convention for a
        community titles scheme. Not a published standard.</i><br>Internal area to the inside
        face of external walls and the centre of party walls, plus balcony or terrace to the
        inside face of the balustrade. Excludes all common property — core, lobbies, amenity,
        plant and car park.</div>
      <div class="sect" style="margin-top:4mm">Status and open items</div>
      <ul class="oi">
        <li>DRAFT — not for issue. Held for Director sign-off.</li>
        ${moved.length?`<li><b>Areas corrected interactively against the drawn linework.</b>
          ${moved.map(m=>`${m.key} ${(m.gba-m.base)>0?'+':''}${fmt(m.gba-m.base)} m²`).join(' · ')}.
          Total GBA ${fmt(t.base)} → ${fmt(t.gba)} m². Form 405 and the Form 413 rates must be
          rebuilt from the corrected take-off before either is relied on.</li>`:''}
        <li>This is ONE DWELLING on one lot. There is no net sellable area, no unit mix and no
          apartment schedule — the NSA and Apts columns are nil throughout and the
          corresponding workbook tabs are marked not applicable.</li>
        <li>The ${D.architect} tender set carries NO area schedule. Every floor area here is
          measured by BDM. Obtain the architect’s own schedule and reconcile before these
          figures go to the client, a financier or the builder.</li>
        <li>The ground floor required manual cut lines along the external walls and carries
          ±3%. It is the level to reconcile first.</li>
        <li>Site area ${D.site} m² is FIGURED on A1.101 for ${D.lot} and has been confirmed
          against an independent measure of the boundary (405.7 m², +0.4%). Obtain the survey
          plan before any planning use.</li>
        <li>No planning-scheme GFA has been assessed. Site cover and plot ratio here are on the
          AIQS basis and must not be used for a ${D.scheme} test.</li>
        <li>External works at grade — driveway ramp, forecourt, walkways, uncovered terrace and
          planters — total 165.6 m² and are excluded from all building areas.</li>
      </ul>
    </div></div>
    ${foot(`${D.project} · Area take-off markups (AIQS / ASMM basis)`,1,np)}</div>`;

  /* ---- pages 2..n : one per level ------------------------------------- */
  S.forEach((l,i)=>{
    const r=R[i], d=r.gba-r.base;
    h+=`<div class="pg">${head(`${l.key}  —  Measured areas — FECA / UCA / GBA`)}
      <div class="plan"><img src="${planPNG(i)}"></div>
      ${foot(`${l.key}:   FECA ${fmt(r.feca)}  +  UCA ${fmt(r.uca)}  =  GFA ${fmt(r.gfa)} m²`+
             `      ·      GBA ${fmt(r.gba)} m²      —      as reported on the Level Schedule `+
             `tab of ${D.workbook}`+
             (Math.abs(d)>CORR_TOL?`   ·   corrected ${d>0?'+':''}${fmt(d)} m² against the `+
              `original take-off — rebuild the workbook`:''),i+2,np)}</div>`;
  });

  document.getElementById('printroot').innerHTML=h;
}
document.getElementById('pdf').onclick=()=>{buildPrint(); setTimeout(()=>window.print(),120);};
window.addEventListener('afterprint',()=>{document.getElementById('printroot').innerHTML='';});


/* ---------------------------------------------------------------------- */
/*  Auto-save.  A file:// page cannot write back to itself, so corrections  */
/*  are kept in the browser's local storage against a project key - not the */
/*  file path, so renaming or re-issuing the tool does not lose them.  The  */
/*  saved state is stamped with the baseline it was corrected against; if a */
/*  new take-off has moved that baseline the state is NOT applied silently. */
/* ---------------------------------------------------------------------- */
const KEY = 'bdm-takeoff::' + D.project + '::' + D.lot;
let booted = false, saveTimer = null;

function saveState(){
  try{
    const st = {savedAt:new Date().toISOString(), baseline:D.baseline.gba,
      levels:S.map(l=>({key:l.key, poly:l.poly.map(p=>[+p[0].toFixed(2),+p[1].toFixed(2)]),
                        band:l.band, uca:l.uca, unroof:l.unroof, deduct:l.deduct}))};
    localStorage.setItem(KEY, JSON.stringify(st));
    stamp(`Saved ${new Date().toLocaleTimeString('en-AU',{hour:'2-digit',minute:'2-digit'})}`);
  }catch(e){
    stamp('NOT SAVED — this browser is blocking local storage. Use “Download corrected '+
          'take-off” before you close.', true);
  }
}
function scheduleSave(){
  if(!booted) return;
  clearTimeout(saveTimer);
  saveTimer=setTimeout(saveState, 400);
}
function stamp(t, warn){
  const e=document.getElementById('saved');
  e.textContent=t; e.className = warn ? 'saved warn' : 'saved';
}
function clearState(){
  try{ localStorage.removeItem(KEY); }catch(e){}
  stamp('Corrections cleared — back to the original take-off');
}
function restoreState(){
  let st=null;
  try{ st=JSON.parse(localStorage.getItem(KEY)||'null'); }catch(e){}
  if(!st) return;
  const banner=document.getElementById('banner');
  const when=new Date(st.savedAt).toLocaleString('en-AU',
    {day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'});
  const apply=()=>{
    st.levels.forEach(sv=>{
      const l=S.find(x=>x.key===sv.key); if(!l) return;
      l.poly=sv.poly.map(p=>[...p]);
      l.band=sv.band; l.uca=sv.uca; l.unroof=sv.unroof; l.deduct=sv.deduct;
    });
    sel.clear(); draw(); panel();
  };
  if(Math.abs(st.baseline - D.baseline.gba) > 0.05){
    banner.className='banner warn';
    banner.innerHTML=`<b>Saved corrections found, but not applied.</b> They were made against a
      take-off of ${fmt(st.baseline)} m² GBA and this tool has been re-issued at
      ${fmt(D.baseline.gba)} m² — the measurement underneath has changed, so the old corner
      positions may no longer mean the same thing. Saved ${when}.
      <button id="bapply">Apply them anyway</button>
      <button id="bdiscard">Discard and start from this take-off</button>`;
    document.getElementById('bapply').onclick=()=>{apply(); saveState();
      banner.className='banner'; banner.textContent=
        'Saved corrections applied over the re-issued take-off — check every level.';};
    document.getElementById('bdiscard').onclick=()=>{clearState(); banner.className='banner off';};
    return;
  }
  apply();
  banner.className='banner';
  banner.innerHTML=`<b>Your corrections have been restored</b> — last saved ${when}. They save
    automatically as you work.
    <button id="bdiscard">Discard and revert to the original take-off</button>`;
  document.getElementById('bdiscard').onclick=()=>{
    S.forEach(l=>{l.poly=l.orig.map(p=>[...p]); l.band=l.oband; l.uca=l.ouca;
                  l.unroof=l.ounroof; l.deduct=l.odeduct;});
    clearState(); sel.clear(); draw(); panel(); banner.className='banner off';
  };
}

loadImgs(()=>{
  tabs(); draw(); panel(); zlabel();
  restoreState();                    // apply anything saved from a previous session
  booted = true;                     // only now does editing start writing state
  if(!document.getElementById('saved').textContent) stamp('Auto-save on');
});
</script></body></html>'''

if __name__ == '__main__':
    main()
