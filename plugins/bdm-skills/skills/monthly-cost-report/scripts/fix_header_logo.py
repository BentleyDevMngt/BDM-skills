"""Re-inject the Form 201 header logo that openpyxl strips on save.

BDM templates carry the logo as a page-header graphic (the '&L&G' token): the image
lives in xl/media, anchored by a vmlDrawing and a <legacyDrawingHF> element per sheet.
openpyxl does not model legacyDrawingHF, so on save it drops the media, the drawing and
the sheet .rels while leaving '&G' in the header - the logo silently vanishes.

The repair resolves the header drawing by FOLLOWING the source file's own
legacyDrawingHF relationship rather than guessing part names: Excel and LibreOffice
renumber vmlDrawing parts freely, and on a sheet that also carries cell comments the
comment drawing and the header drawing sit side by side. It then ADDS the header parts
under fresh names and MERGES the sheet rels, so parts openpyxl legitimately wrote
(comments use their own vmlDrawing + legacyDrawing) are never disturbed.
"""
import re, shutil, zipfile, sys
from xml.etree import ElementTree as ET

RELNS = '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'

def _rels(z, part):
    p = re.sub(r'([^/]+)$', r'_rels/\1.rels', part)
    if p not in z.namelist():
        return {}, p
    return {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read(p)).iter(RELNS)}, p

def _resolve(target, base='xl/worksheets/'):
    if target.startswith('/'):
        return target.lstrip('/')
    p = base + target
    while '../' in p:
        p = re.sub(r'[^/]+/\.\./', '', p, count=1)
    return p

def repair(target_file, template_file):
    tz = zipfile.ZipFile(template_file)
    zin = zipfile.ZipFile(target_file)
    items = {n: zin.read(n) for n in zin.namelist()}
    zin.close()

    # map each template sheet -> its header-footer vml part + header/footer xml
    src = {}
    for n in tz.namelist():
        if not re.match(r'xl/worksheets/sheet\d+\.xml$', n):
            continue
        s = tz.read(n).decode('utf8')
        m = re.search(r'<legacyDrawingHF\s[^>]*r:id="([^"]+)"', s)
        if not m:
            continue
        rmap, _ = _rels(tz, n)
        vml = _resolve(rmap.get(m.group(1), ''))
        if not vml or vml not in tz.namelist():
            continue
        hf = re.search(r'<headerFooter>.*?</headerFooter>', s, re.S)
        src[n] = (vml, hf.group(0) if hf else None)

    done = []
    for n in sorted(x for x in items if re.match(r'xl/worksheets/sheet\d+\.xml$', x)):
        if n not in src:
            continue
        vml, hf = src[n]
        s = items[n].decode('utf8')
        if 'legacyDrawingHF' in s:
            continue
        i = re.search(r'sheet(\d+)\.xml', n).group(1)
        if hf:
            s = re.sub(r'<headerFooter>.*?</headerFooter>', lambda _m: hf, s, flags=re.S)
        if 'xmlns:r=' not in s[:900]:
            s = s.replace('<worksheet ',
                '<worksheet xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" ', 1)

        relname = f'xl/worksheets/_rels/sheet{i}.xml.rels'
        rels = items.get(relname, b'').decode('utf8')
        rid = 'rIdHF1'
        while rels and f'Id="{rid}"' in rels:
            rid += 'x'
        newrel = (f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
                  f'officeDocument/2006/relationships/vmlDrawing" '
                  f'Target="../drawings/vmlDrawingHF{i}.vml"/>')
        rels = (rels.replace('</Relationships>', newrel + '</Relationships>') if rels else
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                + newrel + '</Relationships>')
        items[relname] = rels.encode('utf8')

        tag = f'<legacyDrawingHF r:id="{rid}"/>'          # schema order: legacyDrawing then legacyDrawingHF
        if re.search(r'<legacyDrawing\s', s):
            s = re.sub(r'(<legacyDrawing\s[^>]*/>)', r'\1' + tag, s, count=1)
        else:
            s = s.replace('</worksheet>', tag + '</worksheet>')
        items[n] = s.encode('utf8')

        items[f'xl/drawings/vmlDrawingHF{i}.vml'] = tz.read(vml)
        vrels, vrelname = _rels(tz, vml)
        if vrels:
            body = ''.join(f'<Relationship Id="{k}" Type="http://schemas.openxmlformats.org/'
                           f'officeDocument/2006/relationships/image" Target="{v}"/>'
                           for k, v in vrels.items())
            items[f'xl/drawings/_rels/vmlDrawingHF{i}.vml.rels'] = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                + body + '</Relationships>').encode('utf8')
            for v in vrels.values():
                p = _resolve(v, 'xl/drawings/')
                if p in tz.namelist():
                    items.setdefault(p, tz.read(p))
        done.append(n)

    ct = items['[Content_Types].xml'].decode('utf8')
    for ext, mime in (('png', 'image/png'), ('jpeg', 'image/jpeg'),
                      ('vml', 'application/vnd.openxmlformats-officedocument.vmlDrawing')):
        if f'Extension="{ext}"' not in ct:
            ct = ct.replace('<Default Extension="xml"',
                            f'<Default Extension="{ext}" ContentType="{mime}"/><Default Extension="xml"', 1)
    items['[Content_Types].xml'] = ct.encode('utf8')
    tz.close()

    shutil.copy(target_file, target_file + '.bak')
    with zipfile.ZipFile(target_file, 'w', zipfile.ZIP_DEFLATED) as z:
        for k, v in items.items():
            z.writestr(k, v)
    return done

if __name__ == '__main__':
    print('logo restored on:', repair(sys.argv[1], sys.argv[2]))
