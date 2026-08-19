#!/usr/bin/env python3
"""Geometry helpers for measuring floor areas off a vector PDF drawing set.

The whole method rests on one idea: an architect's PDF is not a picture, it is
vector linework with attributes.  Wall poche, balcony hatch and dimension text
all carry distinguishable stroke colours and fill greys, so areas can be
isolated by *selecting the right linework* rather than by tracing pixels.

Import this module from a take-off script:

    from takeoff_geometry import Drawing
    dw = Drawing('plans.pdf', dpi=300)
    dw.set_scale(1, 100, sheet_scale_factor=2)     # 1:100 @ A1 issued at A3
    img, envelope = dw.plate(page_index=2)         # GBA plate, outside face
    feca = dw.offset_inward(envelope, wall_mm=203)

CLI:
    python3 takeoff_geometry.py plans.pdf --list          # page inventory
    python3 takeoff_geometry.py plans.pdf --greys 2       # stroke greys on a page
"""
import argparse, sys

import numpy as np

try:
    import cv2
    import pymupdf
    from scipy import ndimage
except ImportError as e:
    sys.exit(f'missing dependency ({e}).  pip install pymupdf opencv-python-headless scipy '
             'scikit-image --break-system-packages')


class Drawing:
    """A vector drawing set opened for measurement."""

    def __init__(self, pdf_path, dpi=300, clip=None):
        self.doc = pymupdf.open(pdf_path)
        self.dpi = dpi
        self.clip = clip            # (x0, x1, y0, y1) in raster px — crops off the title block
        self.px_per_m = None

    # ---------------------------------------------------------------- scale
    def set_scale(self, ratio_num=1, ratio_den=100, sheet_scale_factor=1):
        """1:100 drawn, issued at half size (A1 -> A3) => sheet_scale_factor=2.

        Returns px per metre at the configured dpi.  ALWAYS verify this against
        figured dimensions before measuring anything — see verify_scale().
        """
        pt_per_m = 1000.0 / (ratio_den / ratio_num) / 25.4 * 72.0 / sheet_scale_factor
        self.px_per_m = pt_per_m * self.dpi / 72.0
        return self.px_per_m

    def verify_scale(self, measured_px_per_m):
        """Compare a measured px/m against the theoretical value.

        Adopt the theoretical value when they agree; investigate when they do
        not.  Anything worse than about 0.5% means the sheet has been scaled on
        issue and every area will be wrong by the square of the error.
        """
        if not self.px_per_m:
            raise RuntimeError('call set_scale() first')
        err = abs(measured_px_per_m - self.px_per_m) / self.px_per_m
        return {'theoretical': self.px_per_m, 'measured': measured_px_per_m,
                'error_pct': round(err * 100, 4), 'pass': err < 0.005}

    def m2(self, mask):
        """Area of a boolean mask in m²."""
        if not self.px_per_m:
            raise RuntimeError('call set_scale() first')
        return round(float(np.count_nonzero(mask)) / self.px_per_m ** 2, 1)

    # ------------------------------------------------------------ rasterise
    def rgb(self, page_index, dpi=None):
        pm = self.doc[page_index].get_pixmap(dpi=dpi or self.dpi)
        return np.frombuffer(pm.samples, dtype=np.uint8).reshape(
            pm.height, pm.width, pm.n)[:, :, :3].copy()

    def ink(self, page_index, thr=150, chroma_max=40):
        """Black/grey linework only — drops the red DA approval stamp and colour notes."""
        img = self.rgb(page_index)
        g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        chroma = np.max(img, 2).astype(int) - np.min(img, 2).astype(int)
        return img, ((g < thr) & (chroma < chroma_max)).astype(np.uint8)

    # ------------------------------------------------------- layer selection
    def stroke_greys(self, page_index, round_to=3):
        """Inventory of stroke greys on a page, by count.

        Architects draw each layer at a consistent grey.  The balcony / terrace
        hatch is normally its own value — find it here, then pull it with
        layer_mask().  Never assume a value: check it on every project.
        """
        counts = {}
        for d in self.doc[page_index].get_drawings():
            c = d.get('color')
            if d['type'] != 's' or not c:
                continue
            if max(c) - min(c) > 0.02:      # not grey
                continue
            counts[round(c[0], round_to)] = counts.get(round(c[0], round_to), 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: -kv[1]))

    def layer_mask(self, page_index, grey, tol=0.006):
        """Raster mask of every stroke drawn at a given grey value."""
        p = self.doc[page_index]
        out = pymupdf.open()
        np_ = out.new_page(width=p.rect.width, height=p.rect.height)
        sh = np_.new_shape()
        n = 0
        for x in p.get_drawings():
            c = x.get('color')
            if x['type'] != 's' or not c:
                continue
            if max(abs(c[0] - grey), abs(c[1] - grey), abs(c[2] - grey)) > tol:
                continue
            self._emit(sh, x)
            n += 1
        sh.finish(color=(0, 0, 0), width=0.3)
        sh.commit()
        pm = np_.get_pixmap(dpi=self.dpi)
        a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)[:, :, :3]
        return (cv2.cvtColor(a, cv2.COLOR_RGB2GRAY) < 200).astype(np.uint8), n

    def struct_mask(self, page_index, min_width=0.30):
        """Structural linework only — wall poche fills and heavy black strokes.

        Use this where the floor plate merges into site paving (typically the
        ground floor): the structure alone gives a sealable boundary.
        """
        p = self.doc[page_index]
        out = pymupdf.open()
        np_ = out.new_page(width=p.rect.width, height=p.rect.height)
        sh = np_.new_shape()
        for x in p.get_drawings():
            if x['type'] in ('f', 'fs'):
                c = x.get('fill')
                if c and max(c) < 0.80 and (max(c) - min(c)) < 0.05:
                    self._emit(sh, x)
            elif x['type'] == 's':
                c, w = x.get('color'), x.get('width') or 0
                if c and max(c) < 0.05 and w >= min_width:
                    self._emit(sh, x)
        sh.finish(color=(0, 0, 0), width=0.5)
        sh.commit()
        pm = np_.get_pixmap(dpi=self.dpi)
        a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)[:, :, :3]
        return (cv2.cvtColor(a, cv2.COLOR_RGB2GRAY) < 200).astype(np.uint8)

    @staticmethod
    def _emit(sh, x):
        for it in x['items']:
            if it[0] == 'l':
                sh.draw_line(it[1], it[2])
            elif it[0] == 're':
                sh.draw_rect(it[1])
            elif it[0] == 'qu':
                sh.draw_quad(it[1])
            elif it[0] == 'c':
                sh.draw_bezier(it[1], it[2], it[3], it[4])

    # --------------------------------------------------------- the envelope
    def plate(self, page_index, close=9, open_k=51, thr=150, clip=None, extra_seeds=()):
        """Isolate the floor plate to the OUTSIDE face of the external walls (= GBA).

        Method: seal the linework with a morphological close, flood-fill the
        space *outside* the building from a corner of the clip, and keep the
        enclosed remainder.  extra_seeds lets you flood additional outside
        regions (courtyards, site paving that reads as inside).
        """
        clip = clip or self.clip
        if clip is None:
            raise RuntimeError('set a clip box so the title block is excluded')
        x0, x1, y0, y1 = clip
        img, ink = self.ink(page_index, thr=thr)
        m = np.zeros_like(ink)
        m[y0:y1, x0:x1] = 1
        ink *= m
        ink = cv2.morphologyEx(ink, cv2.MORPH_CLOSE,
                               cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close, close)))
        free = (1 - ink).astype(np.uint8)
        ff = free.copy()
        cv2.floodFill(ff, np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8), (x0 + 2, y0 + 2), 2)
        for (sx, sy) in extra_seeds:
            if ff[sy, sx] == 1:
                cv2.floodFill(ff, np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8), (sx, sy), 2)
        s = (ff != 2).astype(np.uint8)
        s[:y0] = 0
        s[y1:] = 0
        s[:, :x0] = 0
        s[:, x1:] = 0
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_k, open_k))
        s = cv2.morphologyEx(s, cv2.MORPH_OPEN, k)
        s = cv2.morphologyEx(s, cv2.MORPH_CLOSE, k)
        s = ndimage.binary_fill_holes(s).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(s, 8)
        order = np.argsort(-st[1:, 4]) + 1
        return img, (lab == order[0]).astype(np.uint8)

    def wall_thickness_mm(self, page_index, envelope, samples=400):
        """Median external wall thickness, measured from the poche.

        Measure it — do not assume 200 mm.  Basement walls are usually much
        thicker than the levels above and the difference is worth 40–60 m².
        """
        struct = self.struct_mask(page_index)
        edge = envelope - cv2.erode(envelope, np.ones((3, 3), np.uint8))
        ys, xs = np.nonzero(edge)
        if len(xs) == 0:
            return None
        step = max(1, len(xs) // samples)
        dist = cv2.distanceTransform(struct, cv2.DIST_L2, 5)
        vals = [dist[ys[i], xs[i]] * 2 for i in range(0, len(xs), step) if dist[ys[i], xs[i]] > 0]
        if not vals:
            return None
        return round(float(np.median(vals)) / self.px_per_m * 1000, 0)

    def offset_inward(self, envelope, wall_mm):
        """FECA = the envelope offset inward by the external wall thickness."""
        px = int(round(wall_mm / 1000.0 * self.px_per_m))
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * px + 1, 2 * px + 1))
        return cv2.erode(envelope, k)

    def roofed(self, area_mask, slab_above):
        """UCA test — the part of a balcony that sits under the slab above.

        At the top level use the roof outline instead.  A level that is set back
        leaves the balcony below open to the sky: that area is GBA, not GFA, and
        getting it wrong is the single largest error in most take-offs.
        """
        return (area_mask > 0) & (slab_above > 0)

    def segment(self, page_index, mask, seeds, core_seeds=()):
        """Split a floor plate into apartments by wall-constrained region growing.

        Seed each apartment from its LIVING room label and the core separately.
        Always check the result visually against the plan before using it.
        """
        from skimage.segmentation import watershed
        _, ink = self.ink(page_index)
        elev = cv2.GaussianBlur((ink * 255).astype(np.float32), (5, 5), 0)
        mk = np.zeros(mask.shape, np.int32)
        pts = list(seeds) + list(core_seeds)
        for i, (x, y) in enumerate(pts, 1):
            if mask[y, x]:
                cv2.circle(mk, (x, y), 9, i, -1)
        mk[mask == 0] = 0
        return watershed(elev, markers=mk, mask=(mask > 0)), len(seeds), len(core_seeds)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--list', action='store_true', help='page inventory')
    ap.add_argument('--greys', type=int, metavar='PAGE', help='stroke-grey inventory for a page')
    ap.add_argument('--dpi', type=int, default=300)
    a = ap.parse_args()
    dw = Drawing(a.pdf, dpi=a.dpi)
    if a.list:
        for i, p in enumerate(dw.doc):
            txt = ' '.join(p.get_text().split())[:90]
            print(f'{i:3d}  {p.rect.width:7.1f} x {p.rect.height:7.1f} pt   {txt}')
    if a.greys is not None:
        for g, n in dw.stroke_greys(a.greys).items():
            print(f'  grey {g:.3f}   {n:6d} strokes')


if __name__ == '__main__':
    main()
