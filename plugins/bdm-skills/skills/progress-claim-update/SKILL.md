---
name: progress-claim-update
description: Rolls a Head Contract Progress Claim Excel workbook forward by one month for a construction or development project. Reads the month's accounts folder (`NN_{Month} YYYY` with 1.0 Received / 2.0 Approved / 3.0 Paid / 4.0 Remittance subfolders), reconciles the CTD Breakdown line-for-line against the Xero account-transactions export, and rebuilds CTD Breakdown, Summary, Unpaid Invoices, Detail Sheet and Progress Claim cover. Use when the user asks to update, roll forward, build, prepare, run or refresh a progress claim, head contract claim, monthly claim, PC NN, or claim NN. Also trigger when they reference an accounts month folder by name, ask to process invoices into a claim file, reconcile Xero payments to filed invoices, or refresh CTD Breakdown / Summary / Unpaid Invoices / Detail Sheet from a folder of new invoices — even if "progress claim" isn't said explicitly.
---

# Progress Claim Update Skill — R4

Rolls a Head Contract Progress Claim workbook forward by one month and **proves the
result against the bank** before releasing it. The user reviews and signs off the draft.

---

## Read this first: what R4 changed and why

The R3 pipeline produced a PC18 (July 2026) draft in which every internal check passed
and the month was still overstated by **$84,476.50**. The checks proved the workbook was
self-consistent. Nothing proved it matched Xero.

R4 adds one non-negotiable control and repairs the extraction defects that made it
necessary. On the July sample the old money extraction scored **4/20** against
hand-verified answers; the R4 extractor scores **20/20**.

**The control: `scripts/reconcile.py` must return RECONCILED before any draft is issued.**
It compares the CTD Breakdown against the Xero export transaction by transaction, on
(date, amount), so it does not depend on supplier-name parsing — which is precisely what
fails. Run it; if it reports a variance, fix the claim, not the tolerance.

---

## When to trigger

- "Update the progress claim for [project]" · "Run the monthly claim" · "Do the [Month] claim"
- "Build claim NN" · "Roll the head contract claim forward"
- "Process the [Month] accounts folder into a claim"
- Any mention of an `NN_Month YYYY` accounts folder plus the word "claim"

---

## Inputs required

Gather with `AskUserQuestion` anything the user hasn't given:

1. **Project code** — e.g. `202415`
2. **Target month folder** — `NN_{Month} {YYYY}`
3. **Previous claim file** — the **issued** Claim N-1, not a prior draft of Claim N.
   Ask which version was issued; do not assume the highest version number is it. On PC18
   the file in the Alfred working folder was `DRAFT_v0.6` while the issued claim was `v2`
   in `13_Contract\02_Progress Claims\BDM Claim No.NN`. Verify by checksum against the
   contract-folder copy where possible.
4. **Claim number**
5. **Period start and end** — the start is normally the day after the prior claim's
   period end. Check the prior claim's CTD for anything dated inside the new period; it
   may already have been claimed.
6. **New-supplier budget codes** — propose, never assume (see Phase 6).

---

## Prerequisites

- **xlsx** skill — read its SKILL.md for the openpyxl patterns and the mandatory recalc step
- **pdf** skill for text extraction; `pdftoppm` + `tesseract` for image-only PDFs
- LibreOffice headless for recalculation — note it rebuilds `xl/calcChain.xml` silently, so a
  clean recalc is NOT evidence the file opens in Excel; `scripts/validate_xlsx.py` is

---

## The pipeline

### 1. Configuration
Load `projects/{code}_{name}.yaml`. If absent, create from `projects/_template.yaml`.

### 2. Folder discovery — and re-scan immediately before build
Scan `1.0 Received` (Received), `2.0 Approved` (Approved), `3.0 Paid` (Paid),
`4.0 Remittance` (excluded).

**Re-list the folder again immediately before building.** Invoices get revised and re-filed
mid-claim. On PC18, JDP INV-4123 sat in Received at $53,317.17 and was later replaced by a
revised invoice in Paid at $29,007.17 — a $24,310 difference in a file with the same name.
Compare mtimes and sizes against the first scan and report anything that moved.

OneDrive placeholders: if `pdftotext` returns "Invalid argument", prompt the user to
right-click the month folder → "Always keep on this device", then retry.

### 3. Extraction — use `scripts/extract_totals.py`
Do **not** hand-roll money or date regexes. That module encodes the following, each of
which cost money in July:

- **Scored candidates, not first-match-wins.** `Balance Due` (the payable) outranks
  `Invoice Total`, which outranks a bare `TOTAL`.
- **Prefix rejection.** A candidate is discarded if preceded by `SUB`, `GST`, `FREIGHT`,
  `LESS`, `RETENTION`, `POWERPASS SAVINGS` and similar. `Sub-Total:` beating `TOTAL:` is
  what turned QLD Sheet Metal's $15,327.35 into $13,933.95, and `GST Total Amount:` is
  what turned Reece's $961.88 into $87.44.
- **Parenthesised and signed negatives.** `(924.00)` is minus $924.00.
- **Credit notes forced negative**, from the document text or the filename (`- CN.pdf`,
  `CN-0975`).
- **Zero never wins** while a non-zero candidate exists — a paid invoice shows
  `BALANCE $0.00` beside its real total.
- **Invoice date, never due date.** `Due Date` / `Order Date` / `Delivery Date` are
  rejected. July produced six rows dated after the period end because due dates won.
- **`is_multi_document()`** flags a PDF holding more than one supplier's paperwork. JDP
  INV-4123 was an 11-page file with another trade's dockets at pages 8–9; a single-page
  read of a multi-document file is not a read of the invoice. Anything flagged goes to
  the audit log for manual confirmation.
- **Credits already netted on the face of an invoice.** `credit_applied_on_face()` and
  `credit_note_disposition()` stop the same credit being taken twice: Performance Garage
  Doors invoice INV-0880-1B reads TOTAL $16,288.00 less credit $5,200.00 = AMOUNT DUE
  $11,088.00, and Xero paid $11,088.00. Posting the payable **and** the matching credit
  note double-deducts. Where a credit note reports nil remaining credit against a named
  invoice, it contributes zero; where it was refunded (Beaumont Tiles, visible in Xero as
  −$924.00) it contributes its full negative value.

Sub-document and statement matching is **case-insensitive**. `STATEMENT` as a
case-sensitive pattern missed `Statement-9443605...`, and three supplier statements were
counted as invoices alongside the invoices they summarised ($7,608.98).

### 4. Xero cross-check
Parse `*Account_Transactions*.xlsx`. **Xero is authoritative for payment status, amount
and date.**

**One payment produces exactly one CTD row.** Before inserting an invoice row, check
whether a payment already represents it; before raising an orphan, check whether a filed
invoice already does. The R3 dedup was amount-based and therefore disabled by bad
extraction — SEQ Crane's invoice parsed at $2,438.15 against a Xero payment of $2,482.29,
no match, so both went in. Amount matching is a helper, not the control. The control is
Phase 9.

Orphans (paid, no invoice on file) are inserted red `#FFC7CE` with
`{Supplier} - INVOICE TBC; Xero CC payment - CHASE SUPPLIER`.

**Segregate `Manual Journal` rows.** They are cost, not cash, and the CTD never reverses
them — Everton carried $143,792.49 of 2025 year-end accruals undetected for a year, one of
which supports a claimed line with no payment behind it. Report them separately so
cost-to-date and payments-to-date are distinguishable, and flag any accrual with no
matching later payment.

### 5. Prior-claim duplicate check
Compare this month's filed invoices against the **prior claim's CTD** on (date, amount)
and on invoice number. R3 only de-duplicated within the current month. This check is what
surfaced SiteSec $1,061.50 and Superior Steel $426.00 on PC18.

Rows legitimately carried from the prior claim (already claimed, dated inside the new
period) are excluded from the reconciliation variance and reported in their own bucket.

### 6. Supplier mapping and new blocks
Resolve supplier → CTD block via the config map, with `service_type_map` first for
multi-service suppliers (Viking).

**Normalise supplier names before they reach the Summary or the Unpaid Invoices tab.**
Those tabs are keyed by name and the Unpaid schedule goes to the client. July shipped
`Allsafe Colsulting`, `Build Connection BENTDEVE`, `ElectricalPC05` and
`Statement-9443605 BENTLEY DEVELOPMENT MANAGEMENT PTY LTD`. If you rename in one place you
must rename in both — the Summary `SUMIF` matches the Unpaid tab's column A exactly.

For genuinely new suppliers, propose a code with the scope evidence behind it and get
sign-off before committing. Check first whether a block already exists: the R3 run flagged
nine new suppliers of which five already had blocks and had simply been misread off
filenames.

**Detect near-duplicate blocks.** Everton carries both `Doyles Trade Centre Subtotal` and
`Doyles Trade Centre - Framing materials Subtotal`, and both `Australis (Edge Protection)`
and `Australian Safety Rail` for one supplier. Totals stay right; the trade reads as two
lines. Flag for consolidation.

### 7. Workbook build — use `scripts/workbook_ops.py`
- **Zero and mark, do not delete.** `zero_and_mark()` neutralises a row in place. Deleting
  shifts every row below it and breaks both the SUBTOTAL ranges and the ~18 cross-row
  formulas above.
- **If you must insert:** `capture_row_formulas()` before, `make_remapper()` +
  `restore_row_formulas()` after. openpyxl moves cells but never rewrites formula text.
- **`rebuild_subtotals()` after any structural change.** It spans the whole sheet for the
  grand-total row and only the block for supplier subtotals. Applying the block rule to
  the grand total reduced `=SUBTOTAL(9,E7:E908)` to `=SUBTOTAL(9,E911:E912)` on a PC18
  draft — reading zero. Nothing downstream uses it, so every other check passed.
- **`freeze_external_links()`** before saving. Call `cached_external_values()` on the
  source first. The Everton template holds one at Detail Sheet N96; openpyxl strips its
  cached value and `recalc.py` then refuses to run.
- Summary reaches the CTD only through columns **D (match), E (debit), F (credit)**.
  Columns G/H/I feed nothing outside the tab.
- Unpaid Invoices is a pure snapshot of this month's Received + Approved. No roll-forward.
- Detail Sheet: new H = prior J; I = `=MAX(0,Q{r}-H{r})` except the Builders Margin row.
- Preserve QUARANTINE markers across rolls.

### 8. Cover
Claim No, period, and the linked formulas. **`F28` ("less previous progress claims") must
be `='Detail Sheet'!H80`.** Two different PC18 drafts had it wrong in two different ways —
hardcoded to cumulative cash received, and pointed at `I80` (this period), which put
$7.5m on the face of the claim. It is the highest-consequence cell on the cover.

Any departure from H80 is a payment determination and belongs to the Director, not the
pipeline. If the user directs an override, record the instruction and the date in the
draft banner.

### 9. RECONCILIATION GATE — mandatory
```bash
python3 scripts/reconcile.py \
    --claim  <draft xlsx> \
    --xero   <Account_Transactions xlsx> \
    --period-start DD/MM/YYYY --period-end DD/MM/YYYY \
    --prior  <issued prior claim xlsx>
```
Reports, and exits non-zero on any variance:

- CTD total vs Xero total for the period, and the row counts behind them
- **In the claim but not in Xero** — duplicates and unsupported costs
- **Paid in Xero but not in the claim** — omissions
- Right amount, wrong date (informational; no effect on the total)
- Carried from the prior claim (excluded from the variance)
- Dated after the Xero export ends — cannot be reconciled; needs Director confirmation
- Cover wiring assertions (F28 = H80, F22 = J80, F31 = F29 + F30)
- Manual journals sitting in the CTD

**Do not issue a draft that has not returned RECONCILED.** If an item is genuinely outside
the Xero data — a paid invoice dated after the export cut-off, for instance — record it as
an accepted exception with the Director's instruction, in the audit log and on the banner.

### 10. Structural self-check and recalc
Sheets present; Detail Sheet R79 Builders Margin code; R80 totals; CTD R9 multi-pay;
cover labels. Then LibreOffice recalc and verify: cover F22 = Detail Sheet J80, F31 =
F29 + F30, J80 = sum of J9:J79, no `#VALUE!`/`#REF!`/`#NAME?`.

A green recalc proves the formulas evaluate, not that they are right. That is Phase 9's job.

Then run `scripts/validate_xlsx.py --repair` and `--check` on the saved workbook. Rolling a claim
forward converts formula cells to values, which leaves **`xl/calcChain.xml`** naming cells that no
longer hold a formula — Excel walks that index on open and reports the file as corrupt. **The
LibreOffice recalc above cannot detect this**: LibreOffice rebuilds calcChain silently and openpyxl
ignores it, so a green recalc is not evidence the file opens in Excel. `--check` must print CLEAN
before the draft is issued.

### 11. Outputs
1. **DRAFT claim** — `{project}_{base}_Claim{NN}_{Month}{YYYY}_DRAFT_v{version}.xlsx`
2. **Audit log** (.md) — invoice counts by status; new suppliers and their codes; orphans
   classified true / name-mismatch / statement; over-claim positions; reclassified items;
   sub-documents and statements excluded; multi-document PDFs flagged; unparsed items;
   manual journals; **the full reconciliation report from Phase 9**
3. **Reconciliation verdict** stated at the top of the hand-back, with the variance figure

Save to the project's `00_ai_sandbox`, or to the claim folder if the user directs it.

---

## Watch-outs to surface every run

1. **Reconciliation variance** — first, always, with the figure
2. **Over-claim positions** (J > F) — need variations to the revised contract sum before issue
3. **Orphan payments** — the chase list, with the largest named
4. **Prior-claim duplicates**
5. **Manual journals / accruals** with no matching payment
6. **New suppliers** and their proposed codes
7. **Multi-document or unparsed PDFs** needing manual confirmation
8. **Credit notes** and whether each was refunded or already applied
9. **Items dated outside the claim period**
10. **Near-duplicate CTD blocks**
11. **Quarantined items** awaiting close-out

---

## Authority boundaries (BDM standing rule)

The skill produces a DRAFT for Director / Senior PM review. It does **not** issue the
claim, email or distribute it, commit to amounts, certify completion, or approve
over-claim positions.

The Director or Senior PM reviews the draft, approves variations for over-claim positions,
rules on the treatment of any shortfall or previous-claims override, chases the orphan
list, resolves disputed Received items, and issues the final claim.

Draft banner: `— DRAFT v{X} — Alfred prepared, for issue by Andrew/SPM — Period {start} –
{end}. CTD reconciled to Xero {from} – {to}, variance {n}.` Record any accepted exception
and the instruction behind it.

---

## Known issues

See `TROUBLESHOOTING.md` and `CHANGELOG.md`.
