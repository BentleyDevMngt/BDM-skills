#!/usr/bin/env python3
"""Measure floor areas from the drawing's own VECTOR linework.

An architect's PDF is not a picture. It carries the zone fills the architect's
area schedule was taken from, the wall poche on its own layer (ArchiCAD and
Revit exports usually name it — 'Walls - External', 'A-WALL' …), and every
corner at the precision the CAD model holds. Measuring from that gives corners
that ARE the drawing's corners, so a figure can be traced to a line on the sheet.

    from vector_takeoff import VectorSheet
    vs = VectorSheet('plans.pdf', page=5, scale=150)        # 1:150 at the issued size
    inv = vs.inventory()                                     # layers, zones, printed areas
    env  = vs.zone_near(140.61)                              # the architect's zone, by its printed area
    wall = vs.wall_depth(env)                                # measured off the poche
    feca = vs.feca(env, wall['median_mm'])

    python3 vector_takeoff.py plans.pdf --page 5 --scale 150 [--sheet-factor 1]

Coordinates are PDF points in the page's DISPLAY space (rotation applied,
origin top-left, y down) — the same space Datum uses. Areas: m² = pt² / K,
K = (72 / 25.4 / N)² x 10⁶, N = scale x sheet_factor.

Where a sheet has no usable vectors (scanned, flattened), fall back to
takeoff_geometry.py and run snap() on the result.
"""
import argparse, json, re, sys

import numpy as np

try:
    import pymupdf
    from shapely.geometry import Point, Polygon, MultiPolygon, LineString
    from shapely.ops import unary_union
except ImportError as e:
    sys.exit(f'missing dependency ({e}).  pip install pymupdf shapely --break-system-packages')

PAPER_MM = {'A0': (1189, 841), 'A1': (841, 594), 'A2': (594, 420), 'A3': (420, 297), 'A4': (297, 210)}


def k_for(scale_den):
    """pt² per m² at 1:scale_den on the sheet as issued."""
    return (72.0 / 25.4 / scale_den) ** 2 * 1e6


def parts(g):
    if g is None or g.is_empty:
        return []
    return list(g.geoms) if hasattr(g, 'geoms') else [g]


def largest(g):
    p = parts(g)
    return max(p, key=lambda x: x.area) if p else Polygon()


def _bez(p0, p1, p2, p3, n=12):
    P = [np.array([q.x, q.y]) for q in (p0, p1, p2, p3)]
    return [tuple(((1 - s) ** 3) * P[0] + 3 * ((1 - s) ** 2) * s * P[1] + 3 * (1 - s) * s * s * P[2] + s ** 3 * P[3])
            for s in np.linspace(0, 1, n)[1:]]


def _subpaths(dr, M):
    """Split one get_drawings() item into closed point lists, display space."""
    subs, cur = [], []
    T = (lambda p: tuple(pymupdf.Point(p) * M)) if M else (lambda p: (p[0], p[1]) if isinstance(p, tuple) else (p.x, p.y))
    for it in dr['items']:
        op = it[0]
        if op == 're':
            r = it[1]
            subs.append([T(pymupdf.Point(r.x0, r.y0)), T(pymupdf.Point(r.x1, r.y0)),
                         T(pymupdf.Point(r.x1, r.y1)), T(pymupdf.Point(r.x0, r.y1))])
            continue
        if op == 'qu':
            q = it[1]
            subs.append([T(q.ul), T(q.ur), T(q.lr), T(q.ll)])
            continue
        a = T(it[1])
        if cur and (abs(cur[-1][0] - a[0]) > 1e-3 or abs(cur[-1][1] - a[1]) > 1e-3):
            subs.append(cur)
            cur = []
        if not cur:
            cur = [a]
        if op == 'l':
            cur.append(T(it[2]))
        elif op == 'c':
            pts = _bez(it[1], it[2], it[3], it[4])
            cur += [T(pymupdf.Point(*p)) for p in pts]
    if cur:
        subs.append(cur)
    return [s for s in subs if len(s) >= 3]


def _poly(pts):
    p = Polygon(pts)
    return p if p.is_valid else p.buffer(0)


def _drawing_polygon(dr, M):
    """A filled drawing as one polygon; inner sub-paths become holes (even-odd)."""
    polys = [_poly(s) for s in _subpaths(dr, M)]
    polys = [p for p in polys if not p.is_empty and p.area > 0]
    if not polys:
        return Polygon()
    polys.sort(key=lambda p: -p.area)
    out = polys[0]
    for p in polys[1:]:
        out = out.difference(p) if out.contains(p.representative_point()) else out.union(p)
    return out


class VectorSheet:
    def __init__(self, pdf, page, scale, sheet_factor=1.0):
        self.doc = pdf if isinstance(pdf, pymupdf.Document) else pymupdf.open(pdf)
        self.pno = page
        self.page = self.doc[page]
        self.N = float(scale) * float(sheet_factor)
        self.K = k_for(self.N)
        self.pt_per_mm = 72.0 / 25.4 / self.N
        self.M = self.page.rotation_matrix if self.page.rotation else None
        self._dr = None

    # ------------------------------------------------------------ basics
    def m2(self, g):
        return g.area / self.K

    def drawings(self):
        if self._dr is None:
            self._dr = self.page.get_drawings()
        return self._dr

    def fills(self, min_m2=0.0):
        out = []
        for dr in self.drawings():
            if dr['type'] not in ('f', 'fs') or not dr.get('fill'):
                continue
            g = _drawing_polygon(dr, self.M)
            if g.is_empty or self.m2(g) < min_m2:
                continue
            out.append({'poly': g, 'fill': tuple(round(c, 3) for c in dr['fill']),
                        'layer': dr.get('layer') or '', 'm2': self.m2(g)})
        return out

    def printed_areas(self):
        """Area labels printed on the sheet — '77.25 m2', '140.6 m²'."""
        found = []
        for w in self.page.get_text('blocks'):
            for m in re.finditer(r'(\d{1,5}(?:\.\d{1,2})?)\s*m(?:2|²)', w[4]):
                found.append(float(m.group(1)))
        return found

    def stated_scale(self):
        """('1:150', 'A3') from the title block text, if printed."""
        t = ' '.join(self.page.get_text().split())
        m = re.search(r'1\s*:\s*(\d{2,4})\s*@\s*(A[0-4])', t, re.I)
        return (int(m.group(1)), m.group(2).upper()) if m else (None, None)

    def check_sheet_size(self, paper):
        """Ratio of the paper the scale is stated at to the page as issued.
        1.0 = issued at the stated size. 2.0 = an A1 sheet issued at A3."""
        w_mm = self.page.rect.width / 72 * 25.4
        pw = max(PAPER_MM[paper])
        return round(pw / max(w_mm, self.page.rect.height / 72 * 25.4), 4)

    # ------------------------------------------------------------ inventory
    def inventory(self, zone_min_m2=1.0):
        layers = {}
        for dr in self.drawings():
            k = dr.get('layer') or '(none)'
            layers.setdefault(k, {'fills': 0, 'strokes': 0})
            layers[k]['fills' if dr['type'] in ('f', 'fs') else 'strokes'] += 1
        zones = []
        for f in self.fills(zone_min_m2):
            r, g, b = f['fill'][:3]
            grey = max(r, g, b) - min(r, g, b) < 0.03
            if grey and 0.25 < r < 0.97:
                zones.append(f)
        printed = self.printed_areas()
        for z in zones:
            hits = [p for p in printed if abs(p - z['m2']) <= max(0.05, 0.005 * p)]
            z['printed_match'] = hits[0] if hits else None
        scale, paper = self.stated_scale()
        return {'page': self.pno, 'layers': layers, 'zones': zones, 'printed': printed,
                'stated_scale': scale, 'paper': paper,
                'sheet_factor': self.check_sheet_size(paper) if paper else None}

    def zone_near(self, m2, tol=0.005, grey=None):
        """The zone polygon whose area matches a printed figure."""
        best = None
        for f in self.fills(1.0):
            if grey is not None and abs(f['fill'][0] - grey) > 0.01:
                continue
            d = abs(f['m2'] - m2) / m2
            if d <= tol and (best is None or d < best[0]):
                best = (d, f['poly'])
        if best is None:
            raise LookupError(f'no filled zone within {tol:.1%} of {m2} m² on page {self.pno}')
        return best[1]

    # ------------------------------------------------------------ walls
    def poche(self, layer_hint=None, dark=0.05):
        """Wall bodies: dark fills on the external-wall layer if the export names one
        ('Walls - External', 'A-WALL-EXT'), else any wall layer, else every near-black
        fill — the last case must be checked on the plan."""
        fl = [f for f in self.fills() if max(f['fill']) <= dark]
        tests = ([lambda n: layer_hint.lower() in n] if layer_hint else
                 [lambda n: 'wall' in n and 'ext' in n, lambda n: 'wall' in n])
        for t in tests:
            named = [f['poly'] for f in fl if t(f['layer'].lower())]
            if named:
                return unary_union(named)
        return unary_union([f['poly'] for f in fl])

    def wall_depth(self, envelope, poche=None, step_mm=100, max_mm=800):
        """Sample the outer face every step_mm and measure the poche depth inward.
        Returns median / p10 / p90 depth over the solid samples and the solid fraction
        (the rest of the perimeter is glazing or opening)."""
        env = largest(envelope)
        poche = self.poche() if poche is None else poche
        ring = env.exterior
        band = env.intersection(poche.intersection(ring.buffer(max_mm * self.pt_per_mm)))
        bb = band.buffer(1e-6)
        depths = []
        L = ring.length
        for s in np.arange(0, L, step_mm * self.pt_per_mm):
            p, q = ring.interpolate(s), ring.interpolate(min(s + 1, L))
            tx, ty = q.x - p.x, q.y - p.y
            n = (tx * tx + ty * ty) ** .5 or 1
            nx, ny = -ty / n, tx / n
            if not env.contains(Point(p.x + nx * 20 * self.pt_per_mm, p.y + ny * 20 * self.pt_per_mm)):
                nx, ny = -nx, -ny
            d = 0
            for k in range(1, int(max_mm / 10)):
                if bb.contains(Point(p.x + nx * k * 10 * self.pt_per_mm, p.y + ny * k * 10 * self.pt_per_mm)):
                    d = k * 10
                else:
                    break
            depths.append(d)
        a = np.array(depths)
        solid = a[a > 0]
        if not len(solid):
            return {'median_mm': None, 'p10_mm': None, 'p90_mm': None, 'solid_fraction': 0.0}
        return {'median_mm': int(np.median(solid)), 'p10_mm': int(np.percentile(solid, 10)),
                'p90_mm': int(np.percentile(solid, 90)), 'solid_fraction': round(len(solid) / len(a), 3)}

    def feca(self, envelope, wall_mm, poche=None, voids=None, island_m2=0.5):
        """FECA: the envelope less the external wall band — the poche attached to the
        outer face, no deeper than the wall. Glazed runs carry no band. Internal
        walls stay in (they are FECA); voids come out."""
        env = Polygon(largest(envelope).exterior)        # outer face only — a void's edge is not a wall face
        poche = self.poche() if poche is None else poche
        ring = env.exterior.buffer(50 * self.pt_per_mm)
        ext = unary_union([w for w in parts(poche) if w.intersects(ring)])
        band = env.intersection(ext).difference(env.buffer(-(wall_mm + 50) * self.pt_per_mm, join_style=2))
        inner = largest(env.difference(band))
        out = Polygon(inner.exterior)
        if voids is not None and not voids.is_empty:
            out = out.difference(voids)
        return out

    # ------------------------------------------------------------ checks
    def overlaps(self, named, min_m2=0.05):
        """Pairs of zones that overlap — an area counted twice in a schedule."""
        names = list(named)
        out = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                inter = named[names[i]].intersection(named[names[j]])
                if not inter.is_empty and self.m2(inter) >= min_m2:
                    out.append((names[i], names[j], round(self.m2(inter), 2)))
        return out

    def snap(self, poly, tol_mm=100):
        """Raster fallback: move each corner onto the nearest vector line end within
        tol_mm, so a traced outline lands on the drawing's own corners."""
        ends = []
        for dr in self.drawings():
            for s in _subpaths(dr, self.M):
                ends += s
        if not ends:
            return poly, 0
        E = np.array(ends)
        tol = tol_mm * self.pt_per_mm
        moved, out = 0, []
        for x, y in list(poly.exterior.coords)[:-1]:
            d = np.hypot(E[:, 0] - x, E[:, 1] - y)
            i = int(np.argmin(d))
            if d[i] <= tol:
                out.append(tuple(E[i]))
                moved += 1
            else:
                out.append((x, y))
        return _poly(out), moved


def shape_list(g, simplify_mm=5.0, pt_per_mm=None):
    """Polygon (with holes) -> takeoff shapes: exterior + holes as deductions."""
    out = []
    tol = (simplify_mm * pt_per_mm) if pt_per_mm else 0
    for p in parts(g):
        ext = p.exterior.simplify(tol) if tol else p.exterior
        out.append({'pts': [[round(x, 3), round(y, 3)] for x, y in list(ext.coords)[:-1]], 'deduct': False})
        for h in p.interiors:
            hh = h.simplify(tol) if tol else h
            if Polygon(hh).area > 0:
                out.append({'pts': [[round(x, 3), round(y, 3)] for x, y in list(hh.coords)[:-1]], 'deduct': True})
    return out


def shapes_area_m2(shapes, K):
    """The figure Datum will show: Σ shoelace, deductions subtracted."""
    t = 0.0
    for s in shapes:
        a = Polygon(s['pts']).area
        t += -a if s.get('deduct') else a
    return t / K


def main():
    ap = argparse.ArgumentParser(description='Inventory a drawing sheet for vector measurement.')
    ap.add_argument('pdf')
    ap.add_argument('--page', type=int, required=True, help='0-based page index')
    ap.add_argument('--scale', type=float, help='drawing scale denominator; default = stated on the sheet')
    ap.add_argument('--sheet-factor', type=float, help='paper stated / paper issued; default = worked out from the page size')
    a = ap.parse_args()
    probe = VectorSheet(a.pdf, a.page, a.scale or 100)
    sc, paper = probe.stated_scale()
    scale = a.scale or sc
    if not scale:
        sys.exit('no scale stated on the sheet — pass --scale')
    sf = a.sheet_factor or (probe.check_sheet_size(paper) if paper else 1.0)
    vs = VectorSheet(a.pdf, a.page, scale, sf)
    inv = vs.inventory()
    print(f"page {a.page}: stated {sc and f'1:{sc}'} @ {paper}; page {vs.page.rect.width:.1f} x {vs.page.rect.height:.1f} pt; "
          f"sheet factor {sf}; measuring at 1:{vs.N:g}")
    print('layers:')
    for k, v in sorted(inv['layers'].items(), key=lambda kv: -(kv[1]['fills'] + kv[1]['strokes'])):
        print(f"  {k:40s} fills {v['fills']:6d}  strokes {v['strokes']:6d}")
    print('grey filled zones (candidate area zones):')
    for z in sorted(inv['zones'], key=lambda z: -z['m2']):
        tag = f"= printed {z['printed_match']}" if z['printed_match'] else ''
        print(f"  {z['m2']:9.3f} m²  fill {z['fill'][0]:.3f}  layer '{z['layer']}'  {tag}")
    print('printed area labels:', inv['printed'])


if __name__ == '__main__':
    main()
