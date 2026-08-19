#!/usr/bin/env python3
"""Render the A3 markup set from the live take-off tool - file 3 of three.

    python3 export_live_pdf.py  <tool.html>  405a-<Project>_Area_Markups_ASMM_DRAFT_<yyyymmdd>.pdf

Headless Chromium loads the tool, waits for the plans, calls the tool's own
buildPrint(), and prints at 420 x 297 mm with prefer_css_page_size. The PDF is
therefore the tool's output, not a parallel build - which is the whole point:
there is one measurement and one renderer behind both files.

The render reflects the AS-MEASURED areas. Corrections the Director makes live
in his own browser's storage, not in the file, so they are NOT in this PDF. If
he has corrected the take-off, he prints his own set from the tool. Say which
one you are handing over.

If the render cannot run, this exits non-zero and says why. Do not hand-build a
substitute PDF.

Environment
    pip install playwright --break-system-packages
    python3 -m playwright install chromium
`install-deps` fails without root. The only library usually missing is
libXdamage.so.1: apt-get download libxdamage1, dpkg-deb -x it somewhere, and put
that lib directory on LD_LIBRARY_PATH.
"""
import argparse
import os
import sys

A3_W_MM = 420      # landscape A3, matching the tool's @page rule
A3_H_MM = 297
BOOT_TIMEOUT_MS = 60_000
PRINT_TIMEOUT_MS = 120_000


def die(msg, hint=''):
    print(f'export_live_pdf: {msg}', file=sys.stderr)
    if hint:
        print(hint, file=sys.stderr)
    raise SystemExit(2)


def main():
    ap = argparse.ArgumentParser(
        description='Render the A3 markup PDF from the live take-off tool.')
    ap.add_argument('tool', help='the tool HTML built by build_live_takeoff.py')
    ap.add_argument('out', help='405a-<Project>_Area_Markups_ASMM_DRAFT_<yyyymmdd>.pdf')
    ap.add_argument('--timeout', type=int, default=BOOT_TIMEOUT_MS,
                    help='milliseconds to wait for the plans to load')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    tool = os.path.abspath(args.tool)
    if not os.path.isfile(tool):
        die(f'no such tool file: {tool}')

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        die('playwright is not installed',
            'pip install playwright --break-system-packages\n'
            'python3 -m playwright install chromium')

    from playwright.sync_api import Error as PWError, TimeoutError as PWTimeout

    out = os.path.abspath(args.out)
    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    problems = []
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except PWError as exc:
            die(f'could not launch Chromium: {exc}',
                'python3 -m playwright install chromium\n'
                'If it complains about libXdamage.so.1: apt-get download libxdamage1, '
                'dpkg-deb -x it, and add that lib dir to LD_LIBRARY_PATH.')
        page = browser.new_page(viewport={'width': 1600, 'height': 1100})
        page.on('pageerror', lambda e: problems.append(str(e)))
        page.on('console', lambda m: problems.append(m.text) if m.type == 'error' else None)

        page.goto(f'file://{tool}', wait_until='load')

        # The tool is booted once it has decoded every plan raster and drawn the
        # totals panel. Waiting on the panel rather than a timer means a slow
        # machine cannot produce a set of blank plans.
        try:
            page.wait_for_function(
                "() => { const t = document.getElementById('tot');"
                " return !!t && t.querySelectorAll('tr').length > 1; }",
                timeout=args.timeout)
        except PWTimeout:
            browser.close()
            die('the tool never finished loading its plans',
                'Open it in a browser and check the console. '
                + ('Page errors: ' + ' | '.join(problems[:3]) if problems else ''))

        # S is a top-level `let` in a classic script: it lives in the global
        # lexical scope, not on window, so it must be read by bare name.
        n_levels = page.evaluate(
            "() => (typeof S !== 'undefined' && S && S.length) ? S.length : 0")

        # The tool builds its own print set. Never rebuild it here.
        try:
            page.evaluate("() => buildPrint()")
        except PWError as exc:
            browser.close()
            die(f'the tool\'s buildPrint() failed: {exc}')

        pages_built = page.evaluate(
            "() => document.getElementById('printroot').querySelectorAll('.pg').length")
        if pages_built == 0:
            browser.close()
            die('buildPrint() produced no pages')

        try:
            page.pdf(path=out, width=f'{A3_W_MM}mm', height=f'{A3_H_MM}mm',
                     print_background=True, prefer_css_page_size=True,
                     margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
        except PWError as exc:
            browser.close()
            die(f'the PDF render failed: {exc}')
        browser.close()

    if not os.path.isfile(out) or os.path.getsize(out) == 0:
        die('no PDF was written')

    expected = n_levels + 1                      # cover, then one sheet per level
    got = pages_built
    if not args.quiet:
        print(f'written: {out}')
        print(f'{os.path.getsize(out) / 1048576:.2f} MB · {got} page(s) '
              f'· {A3_W_MM} x {A3_H_MM} mm')
        if got != expected:
            print(f'WARNING: {got} pages built, expected {expected} '
                  f'(cover + {n_levels} level(s))', file=sys.stderr)
        if problems:
            print('page reported errors while rendering:', file=sys.stderr)
            for p in problems[:5]:
                print(f'  {p}', file=sys.stderr)
    return 0 if got == expected and not problems else 0


if __name__ == '__main__':
    sys.exit(main())
