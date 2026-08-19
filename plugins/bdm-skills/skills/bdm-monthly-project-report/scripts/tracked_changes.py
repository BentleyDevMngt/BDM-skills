#!/usr/bin/env python3
"""
Tracked-changes helper for rolling a BDM Project Summary Report forward.

Works on an UNPACKED word/document.xml (see the docx skill's unpack.py).
Uses lxml so namespaces and run structure are handled correctly, avoiding the
regex traps (runs with <w:lastRenderedPageBreak/>, text split across <w:t>, etc).

Two operations:
  Doc.repl(old_visible, new, occ=1, new_color=None)
      Replace the occ-th ORIGINAL run whose visible <w:t> text == old_visible with a
      tracked <w:del>(original) + <w:ins>(new) pair, preserving the run's <w:rPr>.
      Pass new_color to recolour a dashboard badge (e.g. trend/rating) in the insertion.
      Runs already inside <w:del>/<w:ins> are skipped, so it is safe on a second pass.

  Doc.amend(substr, new_full)
      Find a run already inside <w:ins> whose text CONTAINS substr and replace its text
      with new_full. Use this to EXTEND a previous insertion on a v0.2 pass — the text
      stays a tracked insertion.

Palette: green 1A4A2A | amber 9D7B5B | red B91C1C | grey 5C5A55 | ink 0F1721
Author defaults to "Alfred"; set DATE to the report issue date.

Example:
    from tracked_changes import Doc
    d = Doc("unpacked/word/document.xml")
    d.repl("Report Period: April 2026   ·   Issue Date: 4 May 2026",
           "Report Period: May 2026   ·   Issue Date: 8 June 2026")
    d.repl("→ Stable", "↑ Worsening", occ=1, new_color="B91C1C")
    d.amend("expenditure to date $1.82M",
            "… expenditure to date $1.82M. Contract-works insurance updated to add financier.")
    d.save()
"""
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def w(t): return f'{{{W}}}{t}'

AUTHOR = 'Alfred'
DATE = '2026-06-08T00:00:00Z'   # set to the report issue date
_id = [2000]


class Doc:
    def __init__(self, path):
        self.path = path
        self.tree = etree.parse(path)
        self.root = self.tree.getroot()

    def save(self):
        self.tree.write(self.path, xml_declaration=True, encoding='UTF-8', standalone=True)
        # sanity
        etree.parse(self.path)

    def _runtext(self, r):
        return ''.join(t.text or '' for t in r.findall(w('t')))

    def repl(self, old, new, occ=1, new_color=None, must=True):
        old = old.strip()
        hits = []
        for r in self.root.iter(w('r')):
            p = r.getparent()
            if p is not None and p.tag in (w('del'), w('ins')):
                continue
            if self._runtext(r).strip() == old:
                hits.append(r)
        if len(hits) < occ:
            if must:
                raise SystemExit(f"repl NOT FOUND (occ {occ}, have {len(hits)}): {old[:70]!r}")
            return False
        r = hits[occ - 1]
        parent = r.getparent()
        idx = list(parent).index(r)
        rpr = r.find(w('rPr'))
        i1, i2 = _id[0], _id[0] + 1
        _id[0] += 2

        deln = etree.Element(w('del'))
        deln.set(w('id'), str(i1)); deln.set(w('author'), AUTHOR); deln.set(w('date'), DATE)
        delr = etree.fromstring(etree.tostring(r))
        for t in delr.findall(w('t')):
            t.tag = w('delText')
        deln.append(delr)

        insn = etree.Element(w('ins'))
        insn.set(w('id'), str(i2)); insn.set(w('author'), AUTHOR); insn.set(w('date'), DATE)
        insr = etree.Element(w('r'))
        if rpr is not None:
            rpr2 = etree.fromstring(etree.tostring(rpr))
            if new_color is not None:
                c = rpr2.find(w('color'))
                if c is not None:
                    c.set(w('val'), new_color)
            insr.append(rpr2)
        nt = etree.SubElement(insr, w('t'))
        nt.set(XMLSPACE, 'preserve')
        nt.text = new
        insn.append(insr)

        parent.remove(r)
        parent.insert(idx, deln)
        parent.insert(idx + 1, insn)
        return True

    def amend(self, substr, new_full, must=True):
        for ins in self.root.iter(w('ins')):
            for r in ins.findall(w('r')):
                ts = r.findall(w('t'))
                if substr in ''.join(t.text or '' for t in ts):
                    ts[0].text = new_full
                    ts[0].set(XMLSPACE, 'preserve')
                    for extra in ts[1:]:
                        r.remove(extra)
                    return True
        if must:
            raise SystemExit(f"amend NOT FOUND: {substr[:50]!r}")
        return False
