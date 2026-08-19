#!/usr/bin/env python3
"""
extract_totals.py — R4 replacement for the money/date extraction in build_claim.py.

Written after the PC18 (July 2026) production run, where the previous single-pass
regex list scored 4/20 on a hand-verified sample: it read ex-GST subtotals as gross
totals, read a GST figure as an invoice total, returned $0.55 for an $11,787.70
invoice, and treated two credit notes as positive costs.

Design rules:
  1. Candidates are SCORED, not first-match-wins. The final-payable label beats the
     invoice total, which beats a bare "TOTAL".
  2. Every candidate is rejected if the text immediately before it marks it as
     something other than the payable figure (SUB TOTAL, GST TOTAL, FREIGHT, LESS,
     RETENTION, POWERPASS SAVINGS ...). This is what "Sub-Total:" defeating
     "TOTAL:" cost us in July.
  3. Parenthesised and signed amounts are parsed as negatives; credit notes are
     forced negative.
  4. A zero candidate never wins while a non-zero candidate exists (a paid-in-full
     invoice shows BALANCE $0.00 alongside its real TOTAL).
"""
from __future__ import annotations
import os, re

# --- money -----------------------------------------------------------------
def parse_money(s):
    """Parse a currency string. (1,234.56) and -1,234.56 both yield negatives."""
    if s is None:
        return None
    raw = str(s)
    neg = ('(' in raw and ')' in raw) or raw.strip().startswith('-')
    cleaned = re.sub(r'[()\s$,]', '', raw).lstrip('-')
    try:
        v = float(cleaned)
    except ValueError:
        return None
    return -v if neg else v


# --- credit notes ----------------------------------------------------------
_CREDIT_TEXT = ('credit note', 'creditnote', 'adjustment note', 'tax credit note')

def is_credit_note(txt: str = '', rel_path: str = '') -> bool:
    head = (txt or '')[:1500].lower()
    name = os.path.basename(rel_path or '').lower()
    if any(m in head for m in _CREDIT_TEXT):
        return True
    if any(m in name for m in _CREDIT_TEXT):
        return True
    # filenames like "Beaumont Tiles - CN.pdf" / "CN-0975.pdf"
    base = os.path.basename(rel_path or '')
    if re.search(r'(?:^|[^A-Za-z])CN(?:[-_ ]?\d|\.[a-z]{3}$|$)', base, re.I):
        return True
    # a document whose payable figure is bracketed/negative is a credit by nature
    return bool(re.search(r'Total\s+Inc\w*\s*(?:GST|TAX)\s*\$?\s*\(', txt or '', re.I))


# --- totals ----------------------------------------------------------------
# (label regex, score).  Higher score wins.  The amount must follow the label
# with only whitespace / $ / ( between them.
_LABELS = [
    (r'Balance\s+Due\s*(?:\(\s*AUD\s*\$?\s*\))?\s*[:\s]',       100),
    (r'Amount\s+Due(?:\s+AUD)?\s*[:\s]',                         98),
    (r'Invoice\s+Total(?:\s+AUD)?\s*[:\s]',                      96),
    (r'TOTAL\s+AUD\s*[:\s]?',                                    95),
    (r'Total\s+Inc(?:l|luding)?\.?\s*(?:GST|TAX)\s*[:\s]?',      95),
    (r'TOTAL\s+INC\s+TAX\s*[:\s]?',                              95),
    (r'Total\s+inc\.?\s*gst\.?\s*[:\s]?',                        95),
    (r'Total\s*\(\s*inc[- ]?GST\s*\)\s*[:\s]',                   95),
    (r'Total\s*\(\s*AUD\s*\$?\s*\)\s*[:\s]?',                    90),
    (r'Amount\s+non-?account\s*[:\s]',                           85),
    (r'GRAND\s+TOTAL\s*[:\s]?',                                  80),
    (r'Total\s+Amount\s*[:\s]',                                  60),
    (r'TOTAL\s*[:\s]',                                           50),
]
_AMT = r'\$?\s*(\(?-?[\d,]+\.\d{1,2}\)?)'

# text immediately preceding a label that disqualifies it as the payable figure
_BAD_PREFIX = re.compile(
    r'(sub|gst|freight|weight|retention|deposit|less|remaining|powerpass|'
    r'savings|discount|paid|credit\s+to)\W{0,4}$', re.I)


def extract_total(txt: str, rel_path: str = ''):
    """Return the payable total (negative for credit notes), or None."""
    if not txt:
        return None
    cands = []
    for lab, score in _LABELS:
        for m in re.finditer(lab + r'\s*' + _AMT, txt, re.IGNORECASE):
            before = txt[max(0, m.start() - 16):m.start()]
            if _BAD_PREFIX.search(before):
                continue
            v = parse_money(m.group(1))
            if v is None:
                continue
            cands.append((score, m.start(), v))
    if not cands:
        return None
    nonzero = [c for c in cands if abs(c[2]) > 0.005]
    pool = nonzero or cands
    best = max(pool, key=lambda c: (c[0], -c[1]))   # highest score, earliest occurrence
    val = best[2]
    if is_credit_note(txt, rel_path) and val > 0:
        val = -val
    return round(val, 2)


# --- dates -----------------------------------------------------------------
MONTHS = 'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
_D1 = r'(\d{1,2}\s+(?:' + MONTHS + r')\w*\s+\d{2,4})'
_D2 = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'

def extract_date_str(txt: str):
    """Invoice date only. 'Due Date' and 'Order Date' are explicitly rejected —
    July produced six rows dated after the claim period because due dates won."""
    if not txt:
        return None
    for pat in (r'Invoice\s+Date[:\s\n]+' + _D1, r'Invoice\s+Date[:\s\n]+' + _D2,
                r'(?<!Due\s)(?<!Order\s)Date[:\s]+' + _D1,
                r'(?<!Due\s)(?<!Order\s)Date[:\s]+' + _D2,
                _D1, _D2):
        for m in re.finditer(pat, txt, re.IGNORECASE):
            before = txt[max(0, m.start() - 12):m.start()].lower()
            if 'due' in before or 'order' in before or 'ship' in before or 'deliver' in before:
                continue
            return m.group(1).strip()
    return None


# --- multi-document detection ---------------------------------------------
def is_multi_document(txt: str) -> bool:
    """True when one PDF holds more than one supplier's paperwork — JDP INV-4123
    was an 11-page file with another trade's dockets stapled in at pages 8-9."""
    if not txt:
        return False
    mastheads = len(re.findall(r'TAX\s+INVOICE', txt, re.I))
    abns = set(re.findall(r'A\.?B\.?N\.?[:\s]*([\d\s]{11,14})', txt, re.I))
    return mastheads > 1 and len({a.replace(' ', '') for a in abns}) > 1


# --- credits already netted on the face of a document ----------------------
_CREDIT_APPLIED = [
    r'Less\s+Amount\s+Credited\s*' + _AMT,
    r'Less\s+Credit\s+to\s+Invoice\(?s?\)?\s*' + _AMT,
    r'Less\s+Credit\s+Note\s*' + _AMT,
]
_CREDIT_REMAINING = [
    r'REMAINING\s+CREDIT\s*' + _AMT,
    r'Credit\s+Amount\s*' + _AMT,
    r'Total\s+Balance\s+Owing\s*' + _AMT,
]

def credit_applied_on_face(txt: str):
    """Amount already deducted on an invoice ('Less Amount Credited 5,200.00').

    PC18 lesson: Performance Garage Doors invoice INV-0880-1B shows TOTAL AUD
    $16,288.00 less a credit of $5,200.00 = AMOUNT DUE $11,088.00, and Xero paid
    $11,088.00. Posting the invoice at its payable figure AND the matching credit
    note as a separate -$5,200.00 double-deducts. Where this returns a value, the
    matching credit note must be suppressed.
    """
    if not txt:
        return None
    for pat in _CREDIT_APPLIED:
        m = re.search(pat, txt, re.IGNORECASE)
        if m:
            v = parse_money(m.group(1))
            if v:
                return abs(v)
    return None


def credit_note_disposition(txt: str):
    """For a credit note, decide what it contributes to cost-to-date.

    Returns ('applied', 0.0) when the note has been fully applied against an
    invoice (remaining credit nil) — the invoice already carries the reduction.
    Returns ('open', value) when the credit is still to be taken up, or was
    refunded (Beaumont Tiles: refunded and visible in Xero as -$924.00).
    """
    if not txt:
        return ('open', None)
    face = extract_total(txt)
    for pat in _CREDIT_REMAINING:
        m = re.search(pat, txt, re.IGNORECASE)
        if m:
            rem = parse_money(m.group(1))
            if rem is not None and abs(rem) < 0.005:
                # nil remaining. If the note also names the invoice it was applied
                # to, it is already netted; a refund shows as money received.
                if re.search(r'Less\s+Credit\s+to\s+Invoice', txt, re.I):
                    return ('applied', 0.0)
                if re.search(r'Amount\s+Paid\s+By\s+Credit\s+card', txt, re.I):
                    return ('refunded', face)
    return ('open', face)
