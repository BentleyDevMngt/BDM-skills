# TROUBLESHOOTING — Progress Claim Update Skill

Common errors and fixes encountered during the Claim 16 May 2026 production run.

## 1. Safety check fails: "Missing sheet: Advnaced Payments"

**Cause:** The template's tab was renamed to "Advanced Payments" (typo corrected) but
the YAML / safety check still expects the old "Advnaced Payments" spelling.

**Fix:** The script tolerates both spellings as of v1.4. If you see this error,
ensure your `scripts/build_claim.py` includes the tolerance check in `safety_check()`:

```python
for sheet in LB['sheets']:
    if sheet in wb.sheetnames:
        continue
    if sheet == 'Advnaced Payments' and 'Advanced Payments' in wb.sheetnames:
        continue
    if sheet == 'Advanced Payments' and 'Advnaced Payments' in wb.sheetnames:
        continue
    issues.append(f'Missing sheet: {sheet}')
```

## 2. "Colors must be aRGB hex values" — ValueError on draft banner

**Cause:** The YAML `draft_banner_font: C00000` was truncated to `C000` (4 chars)
by the OneDrive sync layer when bash read the file. openpyxl rejects 4-char hex.

**Fix:** Open the YAML in a text editor, confirm the value is 6 chars (`C00000`), and
re-save. If the bash mount still shows 4 chars, the OneDrive cloud-only file isn't
hydrated locally — right-click → "Always keep on this device".

## 3. Output filename has the template path repeated / mangled

**Cause:** Template name like `818_SouthPineRd_ProgressClaim_15 - REVISED 30-04-2026-59b36bad.xlsx`
passes through into the output filename construction.

**Fix:** v1.4 strips `_Claim{NN}_{Month}{YYYY}_DRAFT_v{X}` and leading project code,
but messy template names (REVISED dates, UUIDs) still pass through. Rename the
template to a clean basename before running, OR post-process the output filename
manually:

```python
shutil.move(messy_output, clean_output)
```

## 4. Bash sandbox 45-second timeout during `--no-cache` extraction

**Cause:** 150+ PDFs × ~0.3s each + OCR fallbacks for image PDFs can exceed 45s in
the Cowork sandbox.

**Workaround:** Run extraction in chunks, saving cache progressively:

```python
# /tmp/extract_chunk.py
# Pass start_idx and end_idx as CLI args. Each invocation processes a batch
# and appends to cache. Re-invoke until all PDFs processed.
```

Then run the build phase with `--cache-path /tmp/fresh_cache.json` (no `--no-cache`).

## 5. Output xlsx reads as corrupted zip

**Cause:** OneDrive sync occasionally serves files back with corrupted bytes after a
fresh save (the "BadZipFile" error).

**Fix:** The script already does atomic save (write to /tmp, verify zip integrity,
shutil.move to destination). If the OneDrive-side copy is corrupted after the move,
retry the save. The /tmp copy from before the move should still be valid as a fallback.

## 6. Skill produces output but no terminal output (exit 0)

**Cause:** The bash subprocess capture in the Cowork sandbox sometimes loses stdout
when the python script triggers many subprocess calls (pdftotext × 150).

**Fix:** Use `PYTHONUNBUFFERED=1` and redirect to a file rather than piping:

```bash
PYTHONUNBUFFERED=1 python3 -u scripts/build_claim.py [args] > /tmp/skill_run.log 2>&1
```

Then `cat /tmp/skill_run.log` to see the actual output.

## 7. Plasta Masta / multi-supplier monthly statement creating duplicate orphan rows

**Cause:** Xero shows one payment to "Plaster Masta" for the supplier's monthly
statement, but the project folder has all the individual invoices that the statement
covers. The skill flags the statement as orphan AND inserts the individual invoices.

**Fix (in progress — see CHANGELOG v2.0 bug #4):** Before flagging a Xero payment as
orphan, sum the supplier's filed invoices (by supplier_to_ctd_block). If the Xero
amount equals the sum within $1 tolerance, suppress the orphan flag. Workaround:
manually delete the duplicate RED orphan row from CTD post-build.

## 8. JF Chatfeild / Jesse Chatfield duplicates

**Cause:** Xero shows `JF Chatfeild`; invoice file says `Jesse Chatfield (Carpentry)`.
Skill creates two entries for the same payment.

**Fix:** Add to YAML `xero_aliases`:

```yaml
xero_aliases:
  jf chatfeild: jesse chatfield
```

Future runs will recognise as same supplier.

## 9. Viking Group invoices floating uncategorised in CTD

**Cause:** Viking Group bills across Plumbing, Electrical, Mechanical, Hydraulic and
Temp Power. The supplier name alone doesn't tell the skill which section to use.
Generic supplier "Viking Group" doesn't match any specific CTD subtotal.

**Fix:** Add a `service_type_map` block to the project YAML:

```yaml
service_type_map:
  Viking Group:
    Electrical: Viking - TH Electrical Subtotal
    Mechanical: Viking - Mechanical Subtotal
    Plumbing: Viking TH Plumbing Subtotal
    Hydraulic: Viking TH Plumbing Subtotal
    Temp Power: Viking - Temp Power Subtotal
```

The skill should look up the Xero description for service keywords and resolve to the
specific block before inserting. (As of v1.4 the lookup is partially implemented in
`_infer_orphan_block` — see CHANGELOG v2.0 bug #2 for the full fix.)

## 10. Summary self-reference SUMIF formulas broken after row insertion

**Cause:** openpyxl `insert_rows` shifts cells but doesn't update formula text. A
formula `=SUMIF(...,Summary!B99,...)` at row 100 stays referencing B99 after a row
inserts above it.

**Fix:** Apply this regex sweep across the Paid section after all insertions:

```python
import re
for r in range(paid_section_first_row, paid_section_end + 1):
    for col in ('C', 'D', 'E'):
        val = sm.cell(r, ord(col)-ord('A')+1).value
        if isinstance(val, str) and re.search(r"Summary!B\d+", val):
            new = re.sub(r"Summary!B\d+", f"Summary!B{r}", val)
            sm.cell(r, ord(col)-ord('A')+1).value = new
```

The v1.4 in-flight patch applies this only to the Unpaid section. v2.0 will apply to
both. Workaround: run the regex as a post-processing step on the output.

## 11. Unpaid section budget codes missing → reconciliation gap

**Cause:** The skill's Unpaid section rebuild writes supplier + amount but leaves
column F blank for new entries. The Detail Sheet N SUMIF therefore misses them.

**Fix:** Look up the code from the supplier's matching Paid section row, or from
`supplier_to_ctd_block` → `new_ctd_blocks` chain. Workaround: post-process to fill
codes per the lookup mapping.

## 12. CTD insertion lands rows in clearly-wrong sections

**Cause:** The skill's alphabetical insertion logic put Viking Group rows inside "The
Building Connection Group" section because there's no validation that the destination
section actually matches the supplier.

**Fix (in progress — see CHANGELOG v2.0 bug #7):** Add a sanity check: if the
resolved supplier doesn't match the destination section name (keyword overlap), abort
the insertion and prompt for review. Workaround: post-process by reading the
yellow-highlighted CTD rows, identifying mismatches by name vs section, and moving
them with `insert_rows`/`delete_rows`.

## 13. Stale cache loaded by default — missing recent invoices

**Cause:** The skill defaults to loading the cache if present. If the cache was
populated during a pilot or prior run and new invoices have arrived since, those new
invoices are silently missed.

**Fix:** Always pass `--no-cache` for the first run of any month. Bug #1 in
CHANGELOG v2.0 will make this default behaviour.

## When all else fails

Read CHANGELOG.md for the full list of identified bugs. Check the audit log markdown
file the skill produces — it lists invoice counts, orphan transactions, and
reconciliation totals which can help triangulate where the issue is.

If reconciliation gap is non-zero, walk the Summary tab rows looking for items where
column F (budget code) is blank. Those items are in Summary E96 but not in Detail
Sheet N80. Sum them — they should equal the gap.


## 9. reconcile.py reports a variance — what to do

Do not adjust the tolerance. The gate is the point. Work the buckets in order:

- **In the claim but not in Xero** — almost always a double count: a filed invoice and its
  Xero orphan both posted for the same payment. Neutralise the invoice row with
  `workbook_ops.zero_and_mark()`, keeping the Xero-derived row (Xero is authoritative for
  amount and date).
- **Paid in Xero but not in the claim** — a missed payment. Insert it, then re-run
  `rebuild_subtotals()`.
- **Right amount, wrong date** — informational. The claim uses invoice dates, Xero uses
  payment dates. No effect on the total.
- **Carried from the prior claim** — already claimed; excluded from the variance
  automatically when `--prior` is supplied.
- **Dated after the Xero export ends** — cannot be reconciled against that export. Either
  obtain a current export or record it as a Director-accepted exception.

## 10. recalc.py refuses: "workbook links to another workbook"

The Everton template holds `='[1]Construction Costs Transactions'!$O$646` at Detail Sheet
N96. openpyxl strips the cached value on save; LibreOffice then writes `#NAME?` and deletes
every external link. Call `workbook_ops.cached_external_values()` on the SOURCE file before
editing, then `freeze_external_links()` before saving. Never pass `--force`.

## 11. The CTD grand total reads zero after a rebuild

`rebuild_subtotals()` must span the whole sheet for the grand-total row. If you rebuilt
ranges by hand, check the row whose label is `Total` — it should read
`=SUBTOTAL(9,E7:E{last})`, not a two-row range. Nothing downstream consumes it, so this
does not show up in any other check.

## 12. A supplier appears twice in the Summary

Two CTD blocks for one supplier (Doyles; Australis / Australian Safety Rail). Totals are
correct because both blocks carry the same budget code, but the trade reads as two lines.
Consolidate per `duplicate_blocks_to_consolidate` in the project YAML.
