#!/usr/bin/env python3
"""
build_certificate.py — BDM Progress Certificate builder (Python + LibreOffice).

For environments with python3, openpyxl and LibreOffice (`soffice`). On a Windows PC with
Excel and no Python, use build_certificate.ps1 instead — same config, same layout map,
same checks.

Takes the controlled template + a project/claim config (JSON) and produces:
  - the populated .xlsm (Excel recalculates on open)
  - a PDF of tabs 01-04 only (Cover, Certificate, Trade Breakdown, Cashflow), with --pdf;
    signed-off certificates only - a held certificate is never PDF'd
and verifies the net-this-claim incl GST equals the builder's tax invoice.

Layouts (see references/template_map.md):
  fixed_price -> Form 335 R6+   (335-Progress_Certificate_R6_2026-09.xlsm)
  cost_plus   -> Form 335a R1+  (335a-Progress_Certificate_Cost_Plus_R1_2026-10.xlsm)

Pre-R6 Form 335 templates are refused: the R3/R4 guards (cover cert-no, scurve() port,
unfixed-materials G88, builder's margin I56) wrote to cells that no longer exist or now
hold something else in R6.

Usage:
  python build_certificate.py --template <335 .xlsm> --config <config.json> --outdir <dir>
"""
import argparse, datetime, json, math, os, re, shutil, subprocess, sys, tempfile, zipfile
import openpyxl
from openpyxl.workbook.properties import CalcProperties

KEEP = ['01 Cover Letter', '02 Certificate', '03 Trade Breakdown', '04 Cashflow Forecast']
DROP = ['00 Project Details', 'SINGLE STAGE (3)']
EXCEL_ERRORS = ('#REF!', '#DIV/0!', '#VALUE!', '#NAME?', '#N/A', '#NUM!', '#NULL!')

LAYOUTS = {
    'fixed_price': dict(
        form='335', name_re=r'^335-Progress_Certificate_R(\d+)_', min_rev=6,
        trade_rows=range(14, 46), ps_rows=range(51, 58), var_rows=range(63, 71),
        col_value='C', col_variance=None, col_prev='E', col_todate='G', col_this='H', col_tocomplete='I',
        headers={'C13': 'CONTRACT PRICE', 'E13': 'PREV CLAIMED', 'G13': 'CLAIMED TO DATE',
                 'H13': 'THIS CLAIM', 'C50': 'PS ALLOWANCE', 'C62': 'APPROVED VALUE'},
        ret_cell='G76', trade_sub='G46', var_sub='G71', value_sub='C46',
        cert_no='F6', val_date='F5', prev_net='F27', net_incl='F40', cert_footer='B50',
        cert_labels={'B27': 'Less: Previous Net Recommendation for Payment',
                     'B40': 'Net Sum Recommended for Payment (incl GST)'}),
    'cost_plus': dict(
        form='335a', name_re=r'^335a-Progress_Certificate_Cost_Plus_R(\d+)_', min_rev=1,
        trade_rows=range(14, 46), ps_rows=range(51, 58), var_rows=range(63, 71),
        col_value='C', col_variance='D', col_prev='G', col_todate='I', col_this='J', col_tocomplete='K',
        headers={'C13': 'ORIGINAL BUDGET', 'D13': 'VARIANCE', 'E13': 'CURRENT BUDGET',
                 'G13': 'PREV CLAIMED', 'I13': 'CLAIMED TO DATE'},
        ret_cell='I76', trade_sub='I46', var_sub='I71', value_sub='C46',
        cert_no='F6', val_date='F5', prev_net='F28', net_incl='F41', cert_footer='B51',
        cert_labels={'B28': 'Less: Previous Net Recommendation for Payment',
                     'B41': 'Net Sum Recommended for Payment (incl GST)'}),
}


def _date(s):
    return s if isinstance(s, datetime.datetime) else datetime.datetime.strptime(s, "%Y-%m-%d")


def _num(v):
    return 0.0 if v in (None, '') else float(v)


def _val(item):
    return _num(item.get('value', item.get('original')))


def abort(msg):
    raise SystemExit("ABORT: " + msg)


# ---------------------------------------------------------------- preflight
def preflight(template, cfg):
    if not cfg.get('contract_form'):
        abort("'contract_form' is mandatory and has no default. Read the EXECUTED contract and set it, "
              "e.g. 'Amended AS4000-1997'. A silent default put the wrong edition on two issued certificates.")
    ctype = cfg.get('contract_type')
    if ctype not in LAYOUTS:
        abort("'contract_type' must be 'fixed_price' or 'cost_plus' (got %r). Read it off the executed contract." % ctype)
    L = LAYOUTS[ctype]
    name = os.path.basename(template)
    m = re.match(L['name_re'], name)
    if not m:
        if ctype == 'cost_plus':
            abort("cost_plus needs the controlled Form 335a. Form 335 has no VARIANCE / CURRENT BUDGET "
                  "columns, so a cost-plus claim cannot be certified on it. Template given: " + name)
        abort("fixed_price needs Form 335 (335-Progress_Certificate_R6+). Template given: " + name)
    if int(m.group(1)) < L['min_rev']:
        abort("Form %s R%s is older than the R%d layout this builder maps. Use the latest Working Copy revision."
              % (L['form'], m.group(1), L['min_rev']))
    if re.search(r'[\\/]Drafts for Review[\\/]', template):
        abort("Form %s at this path is an unreleased draft (Drafts for Review). Build from the "
              "released form in Working Copy. Hold the certificate and tell the user." % L['form'])
    if cfg.get('builders_margin') is not None:
        abort("'builders_margin' is not supported from R6: the template has no margin row (old I56 is now a "
              "provisional-sum row). Carry margin as a trade line exactly as the builder claims it.")
    if 'DRAFT' in cfg['output_basename']:
        abort("output_basename must not carry DRAFT (CLAUDE.md s5).")
    for key, rows in (('trades', 'trade_rows'), ('provisional_sums', 'ps_rows'), ('variations', 'var_rows')):
        if len(cfg.get(key) or []) > len(L[rows]):
            abort("%d %s; template holds %d. Extend the template (template change) and flag."
                  % (len(cfg[key]), key, len(L[rows])))
    for v in cfg.get('variations') or []:
        st = v.get('car_status')
        if not st:
            abort("variation %r has no car_status. Every variation line is checked against the CAR (SKILL.md step 4a)." % v.get('desc'))
        if st != 'Approved' and (_num(v.get('todate')) or _val(v)):
            abort("variation %r is %s in the CAR but carries a value or claimed-to-date. Pending/rejected certify at nil."
                  % (v.get('desc'), st))
    return L


def check_layout(wb, L):
    tb, c = wb['03 Trade Breakdown'], wb['02 Certificate']
    for coord, want in L['headers'].items():
        got = str(tb[coord].value or '').strip()
        if got != want:
            abort("LAYOUT MISMATCH: 03!%s reads %r, expected %r. Update references/template_map.md before building." % (coord, got, want))
    for coord, want in L['cert_labels'].items():
        got = str(c[coord].value or '').strip()
        if got != want:
            abort("LAYOUT MISMATCH: 02!%s reads %r, expected %r." % (coord, got, want))


def check_branding_survived(template_path, built_path):
    """openpyxl re-saves can silently drop embedded images (7 logos, ~19 KB lost from one
    register). Compare xl/media/ before and after; any loss fails the build."""
    def media(path):
        with zipfile.ZipFile(path) as z:
            return sorted(n for n in z.namelist() if n.startswith('xl/media/'))
    try:
        before, after = media(template_path), media(built_path)
    except Exception as e:
        return ["branding check could not run: %s" % e]
    lost = [n for n in before if n not in after]
    return (["LOST EMBEDDED IMAGE: %s" % n for n in lost] +
            (["openpyxl dropped %d of %d embedded images - do NOT issue this file; rebuild by "
              "XML-editing the template and re-zipping ([Content_Types].xml first)." % (len(lost), len(before))]
             if lost else []))


# ---------------------------------------------------------------- population
def write_block(tb, L, rows, items, is_var):
    for i, r in enumerate(rows):
        it = items[i] if i < len(items) else None
        desc = ''
        if it:
            desc = it.get('desc', '')
            if is_var and it.get('ref'):
                desc = "%s - %s" % (it['ref'], desc)
        tb['A%d' % r] = desc
        tb['%s%d' % (L['col_value'], r)] = _val(it) if it else 0
        tb['%s%d' % (L['col_prev'], r)] = _num(it.get('prev')) if it else 0
        tb['%s%d' % (L['col_todate'], r)] = _num(it.get('todate')) if it else 0
        # R6 ships THIS CLAIM hard-coded 0 on most rows - restore the formula on every row
        tb['%s%d' % (L['col_this'], r)] = '=%s%d-%s%d' % (L['col_todate'], r, L['col_prev'], r)
        if L['col_variance']:
            tb['%s%d' % (L['col_variance'], r)] = _num(it.get('variance')) if it else 0
            tb['E%d' % r] = '=C%d+D%d' % (r, r)
            tb['%s%d' % (L['col_tocomplete'], r)] = '=E%d-%s%d' % (r, L['col_todate'], r)
        else:
            tb['%s%d' % (L['col_tocomplete'], r)] = '=%s%d-%s%d' % (L['col_value'], r, L['col_todate'], r)


def scurve_monthly(total, n):
    """Monthly forecast from the BDM S-curve, x = month i / n (end of month).
    Cumulative floored to $1,000 except the final month, which lands on the total."""
    out, prev = [], 0.0
    for i in range(1, n + 1):
        x = i / n
        y = x - 0.016 * x * x + 0.016 * x - (1 / 3.021) * (6 * x ** 3 - 9 * x * x + 3 * x)
        cum = total * y if i == n else math.floor(total * y / 1000) * 1000
        out.append(round(cum - prev, 2))
        prev = cum
    return out


def populate(wb, cfg, L, warnings):
    d = wb['00 Project Details']
    pd = cfg['project']
    for k, v in {
        'C8': pd['name'], 'C9': pd['address'], 'C10': pd['principal'], 'C11': pd['contractor'],
        'C12': pd.get('client', pd['principal']), 'C13': pd.get('development_type', ''),
        'C14': pd.get('stage', 'Construction'), 'C15': cfg['contract_sum'],
        'C19': cfg.get('revision', ''), 'C20': cfg.get('status', ''),
        'C21': cfg.get('signatory', 'For and on Behalf of'), 'C22': cfg.get('reviewer', '[Reviewer]'),
        'C25': pd.get('builder_contact', ''), 'C26': pd.get('builder_address', ''),
        'C27': pd.get('builder_email', ''),
    }.items():
        d[k] = v
    d['C18'] = _date(cfg['issue_date'])

    tb = wb['03 Trade Breakdown']
    write_block(tb, L, L['trade_rows'], cfg['trades'], False)
    write_block(tb, L, L['ps_rows'], cfg.get('provisional_sums') or [], False)
    write_block(tb, L, L['var_rows'], cfg.get('variations') or [], True)

    ret = cfg['retention']
    rate = ret['rate']
    if ret.get('cap_pct') is not None:
        cap = ret['cap_pct']
        tb[L['ret_cell']] = "=-MIN((%s+%s)*%s,%s*%s)" % (L['trade_sub'], L['var_sub'], rate, L['value_sub'], cap)
        tb['A76'] = "Less Cash Retention (%g%% of value to date capped at %g%% of Contract Sum)" % (rate * 100, cap * 100)
    else:
        tb[L['ret_cell']] = "=-(%s+%s)*%s" % (L['trade_sub'], L['var_sub'], rate)
        tb['A76'] = "Less Cash Retention (%g%% of value to date)" % (rate * 100)

    c = wb['02 Certificate']
    c[L['cert_no']] = cfg['cert_no']
    c[L['val_date']] = _date(cfg['valuation_date'])          # replaces the template's =TODAY()
    c[L['prev_net']] = -abs(cfg['previous_net'])

    cf_form = cfg['contract_form']
    cl = wb['01 Cover Letter']
    cl['B19'] = ('="Pursuant to cl.37.2 of the General Conditions of the ' + cf_form +
                 ' Contract, Bentley Development Management issues Progress Certificate No. "'
                 '&TEXT(\'02 Certificate\'!F6,"00")&" for "&\'00 Project Details\'!C11'
                 '&" relating to "&\'00 Project Details\'!C8&"."')
    cl['B39'] = 'BENTLEY DEVELOPMENT MANAGEMENT  -  SUPERINTENDENT UNDER ' + cf_form.upper()
    cl['B42'] = ('This Certificate is issued under ' + cf_form + ' cl.37.2. The Superintendent '
                 'is required to issue this Progress Certificate within the time stated in the '
                 'Contract of receipt of the Claim.')
    c[L['cert_footer']] = ('Issued under ' + cf_form + " cl.37.2. Superintendent must issue within the time "
                           "stated in the Contract of receipt of the Builder's Progress Claim.")

    # 04 Cashflow (R6): A month, B forecast monthly, C actual monthly, D re-forecast monthly
    cf = wb['04 Cashflow Forecast']
    for r in range(12, 33):
        for col in 'ABCD':
            cf['%s%d' % (col, r)] = None
    cfo = cfg.get('cashflow') or {}
    if cfo.get('start') and cfo.get('finish'):
        s0, f0 = _date(cfo['start']), _date(cfo['finish'])
        n = (f0.year - s0.year) * 12 + f0.month - s0.month + 1
        if n > 21:
            abort("programme runs %d months; 04 Cashflow holds 21 (rows 12-32). Extend the template and flag." % n)
        total = cfo.get('total', cfg['contract_sum'])
        act = {a['month']: a['monthly'] for a in cfo.get('actuals', [])}
        ref = {a['month']: a['monthly'] for a in cfo.get('reforecast', [])}
        for i, monthly in enumerate(scurve_monthly(total, n)):
            r = 12 + i
            y, mth = divmod(s0.month - 1 + i, 12)
            md = datetime.datetime(s0.year + y, mth + 1, 1)
            cf['A%d' % r], cf['B%d' % r] = md, monthly
            ym = md.strftime('%Y-%m')
            if ym in act:
                cf['C%d' % r] = act[ym]
            if ym in ref:
                cf['D%d' % r] = ref[ym]
        cf['D75'] = s0
        cf['D75'].number_format = 'd mmmm yyyy'
        cf['D76'] = "%d months" % n
    else:
        warnings.append('cashflow.start / finish not supplied - 04 Cashflow left blank.')


# ---------------------------------------------------------------- verification
def verify_python(cfg):
    trades, variations = cfg['trades'], cfg.get('variations') or []
    td = sum(_num(t.get('todate')) for t in trades)
    vtd = sum(_num(v.get('todate')) for v in variations)
    value = sum(_val(t) for t in trades)
    ret = cfg['retention']
    base = (td + vtd) * ret['rate']
    if ret.get('cap_pct') is not None:
        base = min(base, value * ret['cap_pct'])
    net_to_date = td + vtd - base
    net_this = net_to_date - abs(cfg['previous_net'])
    incl = round(net_this * 1.1, 2)
    inv = cfg.get('invoice_total')
    return {'trade_value': value, 'trade_to_date': td, 'variations_to_date': vtd,
            'retention': -base, 'net_to_date': net_to_date, 'net_this_claim_excl': net_this,
            'net_this_claim_incl': incl, 'invoice_total': inv,
            'ties_to_invoice': inv is None or abs(incl - inv) < 0.5}


def _soffice(args):
    env = dict(os.environ, HOME=tempfile.gettempdir())
    subprocess.run(['soffice', '--headless', '--calc'] + args, check=True, env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def recalc_and_pdf(xlsm_path, pdf_path, L):
    """Recalc via LibreOffice and, when pdf_path is given (--pdf), export tabs 01-04 only to PDF.
    Returns (errors, sheet_net_incl).
    Errors are counted inside each sheet's print columns only: 04's hidden chart feed (J:L)
    holds #N/A on purpose. All intermediates live in a private temp dir, always removed."""
    tmp = tempfile.mkdtemp()
    try:
        _soffice(['--convert-to', 'xlsx', '--outdir', tmp, xlsm_path])
        recalced = os.path.join(tmp, os.path.splitext(os.path.basename(xlsm_path))[0] + '.xlsx')
        vals = openpyxl.load_workbook(recalced, data_only=True)
        errors = []
        for name in KEEP:
            ws = vals[name]
            max_col = 8 if name == '04 Cashflow Forecast' else ws.max_column
            for row in ws.iter_rows(max_col=max_col):
                for c in row:
                    if isinstance(c.value, str) and c.value in EXCEL_ERRORS:
                        errors.append("%s!%s=%s" % (name, c.coordinate, c.value))
        sheet_incl = vals['02 Certificate'][L['net_incl']].value
        wb = openpyxl.load_workbook(recalced)
        for name in KEEP:
            ws, vs = wb[name], vals[name]
            for row in ws.iter_rows():
                for c in row:
                    if isinstance(c.value, str) and c.value.startswith('='):
                        c.value = vs[c.coordinate].value
        for name in DROP:
            if name in wb.sheetnames:
                del wb[name]
        wb.active = 0
        core = os.path.join(tmp, 'core.xlsx')
        wb.save(core)
        if pdf_path:
            _soffice(['--convert-to', 'pdf', '--outdir', tmp, core])
            shutil.move(os.path.join(tmp, 'core.pdf'), pdf_path)
        return errors, sheet_incl
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--template', required=True)
    ap.add_argument('--config', required=True)
    ap.add_argument('--outdir', required=True,
                    help="the claim folder in the project's regular payment-claims folder")
    ap.add_argument('--pdf', action='store_true',
                    help="also export the tabs 01-04 PDF - only for a certificate already signed off")
    a = ap.parse_args()

    cfg = json.load(open(a.config, encoding='utf-8'))
    L = preflight(a.template, cfg)
    os.makedirs(a.outdir, exist_ok=True)
    base = cfg['output_basename']
    xlsm = os.path.join(a.outdir, base + '.xlsm')
    pdf = os.path.join(a.outdir, base + '.pdf') if a.pdf else None
    for out in (xlsm, pdf):
        if out and os.path.exists(out):
            abort("output exists, will not overwrite: " + out)

    wb = openpyxl.load_workbook(a.template, keep_vba=True)
    check_layout(wb, L)
    warnings = []
    populate(wb, cfg, L, warnings)
    if any(_num(p.get('todate')) for p in cfg.get('provisional_sums') or []):
        warnings.append("provisional sums carry a claimed-to-date, but the PS block does not feed the "
                        "certificate (subtotal row 75 = trades + variations only). Confirm with the reviewer.")
    wb.calculation = CalcProperties(fullCalcOnLoad=True)
    wb.save(xlsm)

    branding = check_branding_survived(a.template, xlsm)
    chk = verify_python(cfg)
    errors, sheet_incl = recalc_and_pdf(xlsm, pdf, L)
    agree = sheet_incl is not None and abs(float(sheet_incl) - chk['net_this_claim_incl']) < 0.5

    print(json.dumps({
        'xlsm': xlsm, 'pdf': pdf, 'form': '%s (%s)' % (L['form'], cfg['contract_type']),
        'formula_errors': errors[:20], 'error_count': len(errors),
        'branding_check': branding or 'all embedded images preserved',
        'warnings': warnings, 'verification': chk, 'net_this_claim_incl_sheet': sheet_incl,
        'sheet_agrees_with_calc': agree,
        'car_crosscheck': 'REQUIRED before issue - see SKILL.md step 4a',
        'PASS': chk['ties_to_invoice'] and agree and not errors and not branding,
    }, indent=2, default=str))
    if errors or not chk['ties_to_invoice'] or not agree or branding:
        sys.exit(1)


if __name__ == '__main__':
    main()
