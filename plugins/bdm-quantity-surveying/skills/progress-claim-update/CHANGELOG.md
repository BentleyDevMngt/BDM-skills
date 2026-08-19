# CHANGELOG — Progress Claim Update Skill

## R5 / 2026-08 — Excel integrity gate

Issued 17 August 2026.

R4 closed the gap between "the workbook is self-consistent" and "the workbook matches Xero".
R5 closes a different one: **"the recalc is green" and "the file opens in Excel" are not the
same statement.**

Rolling a claim forward converts formula cells to values, leaving `xl/calcChain.xml` naming
cells that no longer hold a formula. Excel walks that index on open and reports the file as
corrupt. The Phase 10 LibreOffice recalc cannot detect this — **LibreOffice rebuilds calcChain
silently**, and openpyxl ignores it.

Changes:

- **Added `scripts/validate_xlsx.py`** — Excel-strict check and repair.
- **Phase 10 now requires** `--repair` then `--check` after the recalc, and says explicitly
  that a green recalc is not evidence the file opens in Excel.
- Prerequisites note the same caveat against LibreOffice.

No change to the reconciliation gate, the extractor or the CTD logic.

## R4 / v2.0 (July 2026) — reconciliation gate; extraction rebuilt

Written after the PC18 (July 2026) production run. The R3 draft passed every internal
check and still overstated the month by **$84,476.50**. The checks proved the workbook was
self-consistent; nothing proved it matched Xero.

### New — `scripts/reconcile.py` (mandatory gate)
Matches CTD Breakdown rows against the Xero export on (date, amount), so it does not
depend on supplier-name parsing. Exits non-zero on any variance. Reports: in-claim-not-in-
Xero (duplicates), in-Xero-not-in-claim (omissions), right-amount-wrong-date, rows carried
from the prior claim, rows dated after the export ends, cover-wiring assertions, and
manual journals sitting in the CTD.

Verified on the real July data: **v0.2 (the flawed draft) → VARIANCE $83,415.00, exit 1;
v3.2 (corrected) → RECONCILED, 89 rows / $668,709.43 both sides, exit 0.**

### New — `scripts/extract_totals.py`
Scored candidates with prefix rejection, replacing the first-match-wins regex list.
Hand-verified 20-invoice sample: **R3 scored 4/20, R4 scores 20/20.** Fixes:
- `Sub-Total:` / `SUB TOTAL:` beating `TOTAL:` (QLD Sheet Metal $15,327.35 read as $13,933.95;
  Cramers $30,269.25 read as $27,517.50; Westera $4,930.75 read as $5,737.50)
- `GST Total Amount:` read as the invoice total (Reece $961.88 read as $87.44)
- `$0.55` returned for an $11,787.70 invoice
- credit notes read as positive or zero (Beaumont −$924.00 → $0.00; PGD CN-0975 → +$5,200.00)
- one-decimal amounts (`$14,362.7`) not matched at all
- `Amount non-account` (Bunnings) and `Balance Due (AUD$)` (Brisbane Patios) not matched
- due dates winning over invoice dates — six rows dated past the period end
- `credit_applied_on_face()` / `credit_note_disposition()` stop a credit being taken twice
  where the invoice is already net of it
- `is_multi_document()` flags PDFs holding more than one supplier's paperwork (JDP INV-4123
  was 11 pages with another trade's dockets at pp8–9)

### New — `scripts/workbook_ops.py`
- `rebuild_subtotals()` spans the whole sheet for the grand-total row. The R3 rule applied
  to it reduced `=SUBTOTAL(9,E7:E908)` to `=SUBTOTAL(9,E911:E912)` — reading zero — and
  every other check still passed.
- `capture_row_formulas()` / `make_remapper()` / `restore_row_formulas()` for the ~18
  cross-row formulas openpyxl moves but never rewrites
- `zero_and_mark()` — neutralise a row instead of deleting it; no shift, no repair, audit
  trail intact
- `freeze_external_links()` / `cached_external_values()` — Detail Sheet N96 held a live
  link to the Xero workbook; openpyxl strips the cached value and `recalc.py` then refuses

### Changed — pipeline rules
- **One payment produces exactly one CTD row.** The R3 amount-based dedup was disabled by
  bad extraction (SEQ Crane invoice $2,438.15 vs payment $2,482.29 — no match, both posted).
- **Prior-claim duplicate check** on (date, amount) and invoice number. R3 only
  de-duplicated within the current month. Surfaced SiteSec $1,061.50 and Superior Steel $426.00.
- **Cover F28 assertion** — must be `='Detail Sheet'!H80`. Two PC18 drafts had it wrong in
  two different ways; one put $7.5m on the face of the claim.
- **Manual Journal segregation** — Everton carried $143,792.49 of 2025 year-end accruals,
  never reversed, one supporting a claimed line with no payment behind it.
- **Case-insensitive statement/sub-doc matching** — `STATEMENT` missed `Statement-9443605...`;
  $7,608.98 of supplier statements were counted as invoices.
- **Supplier-name normalisation before the Summary and Unpaid tabs**, which are name-keyed
  and client-facing. Rename in both or neither.
- **Re-scan the accounts folder immediately before build** — invoices get revised mid-claim.
- **Near-duplicate block detection** (Doyles ×2; Australis / Australian Safety Rail).

### Config (202415 Everton)
Four new blocks proposed pending sign-off (Brisbane Patios & Decks, Australian Safety Rail,
JDP Concreting, Harvey Norman); new Xero aliases; `duplicate_blocks_to_consolidate`;
`known_accruals` recording the two unresolved 2025 journals; `superseded_documents`
recording the withdrawn JDP INV-4123.

### Still open
- #9 sandbox timeout on 150+ PDFs (run with `--no-cache`, clean `/tmp`)
- #12 intermittent OneDrive BadZipFile (atomic save + retry in code)
- `build_claim.py` still carries its own legacy `extract_total` / `extract_date_str`; the
  R4 modules are the ones to call. Retiring the legacy copies is the next change.

---

# CHANGELOG — Progress Claim Update Skill

## R3 / v1.6 (June 2026) — old manual workarounds built into code

The conversation-history workarounds from the Everton runs are now in `build_claim.py`,
so the monthly run no longer depends on Alfred hand-patching. Bug numbers map to the
"Outstanding bugs" table below.

- **#1 Stale cache invalidation** — cache auto-invalidates when any file in the month
  folder is newer than the cache (`os.walk` mtime check) before load.
- **#2 Multi-service supplier (Viking)** — `map_with_service_type()` resolves the service
  scope (Electrical/Mechanical/Plumbing/Hydraulic/Temp Power) from supplier+desc+path via
  `service_type_map` before block mapping, so scopes no longer collapse into one block.
- **#3 / #4 Xero orphan dedup** — before flagging an orphan, suppress it if the payment
  ex-GST equals a single filed invoice (name variation, e.g. JF Chatfeild vs Jesse
  Chatfield) or the sum of one supplier's filed invoices (statement payment). Verified:
  Claim 17 false orphans 49 -> 44.
- **#5 Unpaid budget codes** — (R2) resolved supplier -> block -> code with Paid-section
  keyword fallback. Verified 30/30 unpaid rows coded.
- **#6 Paid-section self-reference formula rewrite** — already present (rewrites Paid rows
  incl. non-"Subtotal" supplier rows); confirmed.
- **#7 Allocation self-check** — any paid invoice whose supplier keywords don't overlap its
  destination CTD section name now raises a WARN for review (non-fatal). On Claim 17 it
  correctly flagged the S&A stair proformas mis-allocating to 'BBC Painting'.
- **#8 Supplier from parent folder** — generic/numeric filenames (PlastaTrade
  '12401_667966.PDF') fall back to the parent folder name, '(Due ...)' stripped.
- **#10 Filename normalisation** — strips '(REVISED ...)', trailing uuid8 and '(n)' from
  the template basename.
- **#11 Hex-colour repair** — 4-char hex truncated by the OneDrive mount (C00000 -> C000)
  is right-padded back to 6 before PatternFill.

Still open: **#9** (45s sandbox timeout on 150+ PDFs — run with `--no-cache` and a clean
`/tmp`; per-PDF checkpoint is the proper fix) and **#12** (intermittent OneDrive BadZipFile
— atomic save + retry already in code). Note: the LibreOffice recalc step needs a writable
`/tmp/build_claim_recalc`; a stale dir owned by another user will error 0x507 — clear it.

---

# CHANGELOG — Progress Claim Update Skill

## R2 / v1.5 (June 2026) — PC17 production run, 818 South Pine Road, Everton Park

**FIX (critical) — Summary Unpaid 'Budget Code' (col F) now populated.**
Received/Approved invoices carry no budget code, so the prior build left col F blank;
the Detail Sheet 'Actual to Date' SUMIF (which reaches both Paid and Unpaid sections by
code) then picked up $0 of unpaid — dropping ~$348k of received work from the claim and
making 'Actual to Date' fall month-on-month. Each unpaid supplier's code is now resolved
(supplier -> CTD block via map_supplier -> code via _block_to_code, with a keyword
fallback against the live Paid section). Verified on Claim 17: 30/30 unpaid rows coded.

- Confirmed Xero orphan adds flow into CTD correctly (red 'INVOICE TBC; CHASE' rows).
- Config (202415): added aliases (Carilla Carpentry<->Williams, Ace Post & Beam,
  QLD Sheet Metal, Kangaroo<->R&R Windows, JF Chatfeild<->Jesse Chatfield); new blocks
  (Superior Steel 04-4.5.S, PT Brace, QLD Sheet Metal - Roofing); sub-doc pattern '- VO'
  (Carilla variation dockets); June manual_overrides for scanned invoices.

### Logged for R3 (documented, not yet coded)
- Strip prior-month CTD highlight fills on rollover; keep only this month's paid-yellow +
  orphan-red (visual check that every payment landed).
- Advanced Payments tab -> single-line-per-code mirroring the Detail Sheet (Revised Value /
  Balance-to-Finish reference columns).
- BDM brand formatting on output tabs (Calibri, navy #0F1721 headers) + Logo Files logo on
  a fixed OneCellAnchor.
- Cross-month Xero orphan reconciliation (clear an orphan once its invoice is filed).
- Default output to the project PC17 / 00_ai_sandbox folder.

---

# CHANGELOG — Progress Claim Update Skill

## v1.3 (May 2026) — Pilot complete

Built during a 13-iteration pilot on Claim 16 for 818 South Pine Road, Everton Park
(project 202415). All 9 structural fixes baked into `scripts/build_claim.py`.

- v0.1–v0.2: initial build with hard-coded I values
- v0.3–v0.4: alphabetical insertion, inline placement, highlighting
- v0.5–v0.6: top-down processing with running offset (fixed self-reference formula bug)
- v0.7: amount-based dedup (replacing fragile invoice-number matching)
- v0.8: unmerge cells before insertion (fixes Summary B87:E87 silent-write-skip bug)
- v0.9: re-run with current folder state
- v1.0: auto-add Summary Unpaid rows for new suppliers
- v1.1: Detail Sheet I switched to formulas so trace is visible
- v1.2: Unpaid Invoices = current-month snapshot only
- v1.3: Xero orphan cross-check (red rows for credit-card payments without filed invoices)

## v1.4 (in-flight patches, May 2026 production run for Claim 16)

The first true production run on the same project surfaced additional issues.
Patches applied in-session:

- Safety check tolerates either `Advnaced Payments` (typo, original template) or
  `Advanced Payments` (corrected spelling) — backward / forward compatibility.
- Xero report filename pattern widened from `Account_Transactions*.xlsx` to
  `*Account_Transactions*.xlsx` to catch prefixed names like
  `23-04-26 to 28-05-26_Account_Transactions (1).xlsx`.
- Output filename construction strips prior `_Claim{NN}_{Month}{YYYY}_DRAFT_v{X}`
  suffix and leading project code so re-running on a previous draft doesn't produce
  double-stacked filenames.
- YAML for project 202415 enriched with: Plasta Masta carpentry materials cladding
  mapping, BBC / S&A / Site Sec aliases, Viking Mechanical CTD block, Bespoke
  Engineering Solutions / Pest Management mappings.

## Outstanding bugs — must fix before share-ready (v2.0 milestone)

Eight correctness bugs identified during the production run that need proper fixes
in the skill itself (rather than workaround patches in each monthly run):

| # | Bug | Impact | Fix sketch |
|---|---|---|---|
| 1 | Stale cache loaded by default — no invalidation when month folder is newer than cache | Misses recently-arrived invoices | Invalidate cache if cache mtime < any month folder mtime; default behaviour. Or: just default `--no-cache` to True. |
| 2 | Multi-service supplier (Viking) dumped into a generic block — no service-type split | Mechanical / Electrical invoices go uncategorised in Detail Sheet N | Implement `service_type_map` resolution in `parse_invoice` / `_infer_orphan_block`. Memory: `feedback_viking_service_type_split.md` |
| 3 | Xero orphan flag fires when filed invoice exists under a name variation | False orphans (JF Chatfeild vs Jesse Chatfield) | Single-invoice amount equality check before flagging orphan. Memory: `feedback_xero_orphan_dedup.md` |
| 4 | Xero orphan flag fires for a statement payment when individual invoices are filed | False orphans (Plasta Masta monthly statement vs individual invoices) | Sum-of-invoices amount equality check before flagging orphan. Memory: `feedback_xero_orphan_dedup.md` |
| 5 | Summary Unpaid section rebuild omits budget codes | Detail Sheet N misses unpaid items → reconciliation gap | Look up code from matching Paid section row (or supplier_to_ctd_block → code via new_ctd_blocks) when building Unpaid rows. |
| 6 | Summary self-reference formula rewriter only covers Unpaid section, not Paid | Broken SUMIFs after row insertions in Paid section | Apply the same regex rewrite (`Summary!B\d+` → `Summary!B{r}`) to all Paid section rows after insertion. |
| 7 | CTD insertion target lands rows in clearly-wrong sections | Viking invoices placed in Building Connection Group section | Sanity check: if normalised supplier doesn't match destination section name, abort and prompt for review. |
| 8 | Supplier extracted from filename only — generic invoice-number filenames in named subfolders fail | PlastaTrade entries got supplier "12401 666478" | Fallback to parent folder name when filename is purely numeric / generic. |

## Operational fragility — annoying, fixable (v1.5 milestone)

| # | Issue | Workaround we used | Proper fix |
|---|---|---|---|
| 9 | `--no-cache` extraction exceeds 45s Cowork sandbox timeout on 150+ PDFs | Chunked extraction wrapper script | Per-PDF checkpoint to cache; resume from last checkpoint on next call. |
| 10 | Output filename construction sometimes doesn't strip messy template names | Manual rename post-build | Aggressive normalisation: strip ALL `(REVISED...)`, `(...UUID)` suffixes from template basename. |
| 11 | YAML hex color truncated via the OneDrive bash mount (`C00000` → `C000`) | Patched /tmp YAML | Validate hex colors are 6 or 8 chars; auto-pad with leading zero if 4 chars. |
| 12 | OneDrive sometimes serves files back as corrupted bytes (BadZipFile) | Atomic save + zip integrity verify | Already in code; document for users that intermittent OneDrive sync glitches need a retry. |

## Skill maturity verdict

As of the v1.4 in-flight patches, the skill is suitable for **Alfred-internal use only** —
Andrew runs it with Alfred catching the edge cases. Not yet share-ready for SPMs / PMs
to use self-serve. See README.md "Known limitations" and the eight correctness bugs
above.

**Path to v2.0 (share-ready):**

1. Fix bugs #1–#8 (correctness).
2. Fix issues #9–#12 (operational).
3. Add a self-check phase that flags suspicious allocations.
4. Add interactive prompts for new suppliers (currently TODO in code).
5. Test against a second BDM project (e.g. David Street Burpengary) to confirm it
   isn't 202415-specific.
6. Add a guided review mode that walks the user through material changes before save.
7. Write a one-page SPM/PM user guide.
