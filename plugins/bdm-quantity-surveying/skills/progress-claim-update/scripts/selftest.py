#!/usr/bin/env python3
"""
selftest.py — portable regression for the R4 extraction rules.

Fixtures are the real label layouts from the PC18 (July 2026) invoices that the R3
extractor got wrong. Run after any change to extract_totals.py:

    python3 scripts/selftest.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_totals as et

CASES = [
    ("QLD Sheet Metal — Sub-Total must not beat Invoice Total",
     "Sub-Total:  13,933.95\nGST: $ 1,393.40\nInvoice Total: $ 15,327.35", "", 15327.35),
    ("Cramers — SUB TOTAL must not beat TOTAL/BALANCE DUE",
     "SUB TOTAL: $27,517.50\nGST: $2,751.75\nTOTAL: $30,269.25\nBALANCE DUE: $30,269.25", "", 30269.25),
    ("Westera — Balance Due outranks Total (inc-GST)",
     "Subtotal: $5,737.50\nGST: $573.75\nTotal (inc-GST): $6,311.25\nBalance Due: $4,930.75", "", 4930.75),
    ("Reece — GST Total Amount is not the invoice total",
     "GST Total Amount: $87.44\nTOTAL AUD 961.88", "", 961.88),
    ("Beaumont — parenthesised credit",
     "Subtotal Ex GST $ (840.00)\nGST $ (84.00)\nTotal Inc GST $ (924.00)\nTotal Balance Owing 0.00",
     "Beaumont Tiles - CN.pdf", -924.00),
    ("PGD credit note — forced negative from filename",
     "CREDIT NOTE\nTOTAL AUD 5,200.00\nLess Credit to Invoice(s) 5,200.00\nREMAINING CREDIT 0.00",
     "Credit Note CN-0975.pdf", -5200.00),
    ("PGD invoice — payable is net of the credit already applied",
     "TOTAL AUD 16,288.00\nLess Amount Credited 5,200.00\nAMOUNT DUE AUD 11,088.00", "", 11088.00),
    ("Premium Tiling — one decimal place",
     "Subtotal excluding gst $13,057\nGST 10% $1305.7\nTotal inc. gst. $14,362.7", "", 14362.70),
    ("Bunnings — Amount non-account",
     "Amount on account : 0.00\nAmount non-account : 3,926.66\nTOTAL POWERPASS SAVINGS 57.80", "", 3926.66),
    ("Brisbane Patios — Balance Due (AUD$)",
     "Subtotal (AUD$) $54,000.00\nBalance Due (AUD$) $59,400.00", "", 59400.00),
    ("Glass Outlet — zero BALANCE must not beat TOTAL",
     "SUBTOTAL EX GST $1,465.00\nGST $146.50\nTOTAL $1,611.50\nBALANCE $0.00", "", 1611.50),
    ("Dev Objective — TOTAL INC TAX",
     "SUB TOTAL $600.00\nTOTAL INC TAX $660.00\nDue date: 20/07/2026", "", 660.00),
]

DATE_CASES = [
    ("invoice date wins over due date",
     "Invoice Date 16 Jul 2026\nDue Date: 30 Jul 2026", "16 Jul 2026"),
    ("due date alone is rejected",
     "Due Date: 30 Jul 2026\nTerms: Net 14", None),
    ("order date is rejected",
     "Order Date: 30/06/2026   Invoice Date: 02/07/2026", "02/07/2026"),
]

def main():
    fails = 0
    print("extract_total")
    for name, txt, path, exp in CASES:
        got = et.extract_total(txt, path)
        ok = got is not None and abs(got - exp) < 0.005
        fails += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: expected {exp:,.2f}, got "
              f"{'None' if got is None else format(got, ',.2f')}")
    print("extract_date_str")
    for name, txt, exp in DATE_CASES:
        got = et.extract_date_str(txt)
        ok = (got == exp) if exp else (got is None)
        fails += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: expected {exp!r}, got {got!r}")
    print("credit disposition")
    d = et.credit_note_disposition("CREDIT NOTE\nTOTAL AUD 5,200.00\n"
                                   "Less Credit to Invoice(s) 5,200.00\nREMAINING CREDIT 0.00")
    ok = d == ('applied', 0.0); fails += not ok
    print(f"  [{'PASS' if ok else 'FAIL'}] fully applied credit contributes 0.00 -> {d}")
    print("multi-document")
    md = et.is_multi_document("TAX INVOICE\nABN: 11 111 111 111\nTAX INVOICE\nABN: 22 222 222 222")
    ok = md is True; fails += not ok
    print(f"  [{'PASS' if ok else 'FAIL'}] two mastheads + two ABNs -> {md}")
    print(f"\n{'ALL PASS' if not fails else str(fails) + ' FAILURE(S)'}")
    return 1 if fails else 0

if __name__ == '__main__':
    sys.exit(main())
