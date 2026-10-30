---
name: progress-certificate-update
description: >-
  Build a BDM Progress Certificate (Form 335 fixed price; Form 335a cost plus) in
  response to a builder's progress claim — BDM's certifying instrument as Superintendent under
  AS4000 cl.37.2. Use this skill whenever someone asks to "do/produce/draft the progress
  certificate", "certify claim NN", "Form 335 for [project]", "progress certificate for
  [project]", or drags a builder's claim schedule + tax invoice + statutory declaration into the
  session and asks to certify or assess the claim. Also trigger on "assess the claim", "roll the
  certificate forward", "next progress certificate", or any mention of certifying a
  head-contract progress claim. This produces the CERTIFICATE (BDM → builder); it is the
  companion to progress-claim-update, which produces the builder's CLAIM. Trigger even if the
  word "Form 335" isn't used — a builder claim plus "certify" or "progress payment" is enough.
---

# Progress Certificate (Form 335 / 335a) — update / roll-forward

**Revision: R3.1 · 2026-10** — skill revisions carry one decimal place: a scope change raises the whole number, a correction or refinement raises the decimal. The release history is in this skill's CHANGELOG (where it has one) and the repository CHANGELOG.

R3.0 maps Form 335 R6 (CN-2026-049), branches on contract type and adds an Excel COM builder for Windows PCs. It was written on 15 October 2026 and ported into this repository on 29 October 2026.

R3.1 builds cost-plus certificates on Form 335a R1, released on 30 October 2026 under CN-2026-055. R3.0 stopped and flagged a cost-plus claim because 335a had not been released.

## What this does and why

When a builder lodges a progress claim, BDM (as Superintendent) must issue a Progress
Certificate under AS4000 cl.37.2 stating the amount BDM recommends for payment. This skill
rolls the previous certificate forward onto the new claim, populates the controlled form,
verifies the numbers tie to the builder's tax invoice, and produces the certificate (Excel) for
the Senior QS or Director to review, sign and issue. The PDF follows sign-off, not the build.

You (Claude) do the judgement — reading the project folder and the claim documents, mapping
trades, checking variations against the CAR, deciding the certified position. The bundled
builder does the deterministic build, the verification and, after sign-off, the PDF. Keep that
division: think and confirm, then let the builder build.

## Authority boundary (read first)

BDM **drafts and recommends**; the Senior QS or Director **certifies and issues**. So:
- Every output is held for sign-off, never issued. Do **not** write "DRAFT" on the certificate —
  no DRAFT revision, status, header, footer or `_DRAFT` filename suffix (`bdm-house-style` § 13.6).
  The signatory line follows the user's own standing rule (some users sign at preparation);
  absent one, leave it as a placeholder.
- **No PDF of a certificate awaiting sign-off.** A PDF reads as an issued instrument. The
  builders write the `.xlsm` only; the tabs-01–04 PDF is produced with `-Pdf` / `--pdf` once
  the Senior QS or Director has signed off and asked for it (company CLAUDE.md §10).
- Default the certified amounts to the **claimed** amounts, then flag any line where you
  believe the Superintendent should certify less — but never reduce a claim yourself without
  being asked. The reviewer adjusts. **Variations are the exception** — they certify at the
  CAR position (step 4a).
- Never invent figures, dates, retention rates or contract references. If a number isn't in
  the documents or the project folder, ask one sharp question or flag it — don't guess.

## Inputs (usually dragged in from email)

1. Builder's **claim schedule** (.xlsx) — trade breakdown, this-claim and to-date amounts.
2. Builder's **tax invoice** (.pdf) — the payment-claim total; the certificate must tie to it.
3. Signed **statutory declaration** (.pdf) — supporting; filed alongside, not a figure source.

If the prior certificate or Payment Schedule isn't already in the project folder, ask for it.

## Project summary (company CLAUDE.md §8, §13)

- **Before you start:** read `00_ai_sandbox\Project_Summary_*.md` (sandbox folder
  matched case-insensitively) for parties, references, status and the project's
  own conventions (§17). Missing → say so and work from the source documents;
  never create a stub (that is `bdm-project-sandbox-setup`'s job). Two summaries
  → flag it and rely on neither.
- **Figures come from the source:** any sum, date, reference or party that goes
  into the output is checked against the document it came from. If the summary
  disagrees, the source wins and the summary is corrected below.
- **Before you finish:** update the summary in the same pass — a dated
  change-log line at the top (what this run produced, where, status), plus only
  the sections this run changed, each with its source. No summary → skip and flag.

## Workflow

### 1. Identify the project, claim number and contract type
Resolve the project from the request and the claim schedule. Read the claim schedule to get
the claim number, "work completed to" date, contract sum, and the this-claim / to-date totals.
Read the **contract type** off the executed contract (Project Summary §1 first): **fixed price**
(lump sum) or **cost plus**. Confirm the claim number, project and contract type with the user
before building.

### 2. Pick the form by contract type

| Contract type | Form | Template |
|---|---|---|
| Fixed price | **Form 335**, R6 or later | latest `335-Progress_Certificate_R*.xlsm` in `…\BDM TEMPLATES\Working Copy\300 Project Management - Contract Delivery\` |
| Cost plus | **Form 335a**, R1 or later | `335a-Progress_Certificate_Cost_Plus_R*.xlsm` in the same Working Copy folder |

**Cost plus — Form 335a.** Form 335a R1 (Cost Plus) was released on 30 October 2026 under
CN-2026-055 and sits beside Form 335 in the same Working Copy folder. It keeps ORIGINAL BUDGET,
VARIANCE and CURRENT BUDGET on '03 Trade Breakdown' and the "Plus: Variance Adjustments
(cost-plus)" line on '02 Certificate'. Give each trade line its `variance` (config_schema.md).
- Do **not** certify a cost-plus claim on Form 335 R6. R6 has no VARIANCE or CURRENT BUDGET
  columns and no variance-adjustment row, so the budget movement has nowhere to go. The builders
  refuse the pairing either way.
- Do **not** build from a copy in `Drafts for Review\`. Both builders refuse a template there.

Highest revision wins; ignore `_Superseded`. Form 335 earlier than R6 is refused — the cell map
below is R6's. **Cloud-only trap:** a newly revised template can arrive as a OneDrive
placeholder that won't open (BadZipFile / wrong size). If so, ask the user to open it once in
Excel, or drag it into the chat.

### 3. Gather the project specifics (read the project folder — do NOT hard-code)
Per BDM standing rule, read the project's own folder rather than assuming. Sources:
- `00_ai_sandbox\Project_Summary_*.md` — **start here for orientation:** parties, contract form
  and type, retention basis, programme dates and **§17 Project conventions & gotchas**. Take the
  contract sum and the prior certified/net figures from the contract and the prior certificate
  below, not the summary.
- The **prior certificate / Payment Schedule** — previously certified to-date (per line) and
  the previous net recommendation (drives the roll-forward).
- The executed **contract** — retention rule, contract form (e.g. Amended AS4000-1997 vs
  AS4000-2024) and contract type. Confirm the clause/timeframe if the contract is amended.

Review what you find with the user, especially the **retention basis** (R6's default is 10% of
value to date capped at 5% of the Contract Sum — confirm it against the contract, don't assume
it) and the **contract form** wording.

### 4. Assemble the config
Write a JSON config (schema in `references/config_schema.md`) capturing `contract_type`,
`contract_form`, project details, the trade / provisional-sum / variation lines, retention rule,
certificate number, valuation and issue dates, the previous net recommendation, invoice total,
and cashflow dates and actuals.

**Roll-forward rule — Form 335 R6 columns** (full map in `references/template_map.md`):

| Column | Heading | Set to |
|---|---|---|
| C | CONTRACT PRICE / PS ALLOWANCE / APPROVED VALUE | trade price; PS allowance; **CAR approved value** for a variation |
| E | PREV CLAIMED | the **prior certificate's claimed to date** for that line |
| G | CLAIMED TO DATE | this claim's certified-to-date |
| H | THIS CLAIM | computes `=G−E` |
| I | TO COMPLETE | computes `=C−G` |

Read the prior certificate's to-date from the right column: **G** on an R6 certificate, **I**
on R5 or earlier. The certificate's **previous net recommendation** (`02 Certificate!F27`) = the
prior certificate's net ex GST.

**First certificate on an existing project (bootstrap):** if there is no prior Form 335 (e.g.
the previous claim was certified via a QS report / Payment Schedule), reconstruct "previously
certified" from the prior builder claim schedule's previous-claim column plus the Payment
Schedule net. Flag that the prior figure is reconstructed.

**Builder's margin.** R6 has no margin row (R5's `I56` is now a provisional-sum row). Carry the
margin as a trade line exactly as the builder claims it. The builders refuse a `builders_margin`
key, because writing it would overwrite a provisional-sum formula.

### 4a. Cross-check every variation line against the CAR (mandatory)

**Do not certify a variation line off the builder's claim.** The builder's claim states the
builder's view of each variation's status; the **Contract Admin Register (CAR)** states BDM's
determination. Where they differ, the CAR governs.

For every variation line in the claim:

1. Open the project's CAR (`bdm-contract-admin-register`) and find the matching VO number.
2. Compare **status** (Approved / Rejected / Pending / Superseded) and **approved value**.
3. Certify the **CAR** position: column C = the CAR approved value, `car_status` = the CAR status.
4. List every mismatch in the hand-back, with both figures.

A pending or rejected variation certifies at **$0** regardless of what the claim shows. The
builders abort if a non-approved line carries a value. A superseding CSA carries the
**restated** value, not a delta. Pending variations paid on account go in `02!F22` by hand,
only on the reviewer's instruction.

> This is not a theoretical control. On one certificate **5 of 17 variation lines** carried
> the wrong status straight off the builder's claim — including one claimed at **$50,589
> approved** that the register showed as **REJECTED, $0**.

If the project has no CAR, or the CAR is stale, **say so and stop**. Do not certify variations
against an unverified register.

### 5. Build — straight into the claim folder

Save the certificate **directly in its regular project folder** (CLAUDE.md §8, locked 1/9/26),
not in `00_ai_sandbox`: `13_Contract Admin\01_Main Contract\03_Payment Claims\PC to Builder\<claim folder>\`.
**Follow the claim-folder naming the project already uses** (e.g. `30_August EOM`,
`PC010 - September 2026`) — don't create a parallel `PC 0NN (Month YYYY)` folder. Saving there is
not issuing; the certificate stays held under §10 until signed and sent.

> The old `13_Contract\04_Progress Claims\` path was retired in May 2026. Never overwrite
> existing project files — the builders refuse to overwrite an existing output.

**On a Windows PC with Excel and no Python: use the PowerShell / Excel COM builder.** Without
Python, `pdftoppm` or LibreOffice, `build_certificate.py` cannot run.
```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_certificate.ps1 `
  -Template "<latest 335 .xlsm>" -Config "<config.json>" -OutDir "<claim folder>"
```
- Excel opens the template with macros force-disabled, calculation set to manual while writing,
  then recalculates once and saves. Excel writes its own calcChain, so the stale-calcChain trap
  (`_Skills_Index.md`, workbook rule) does not arise. A build takes about 30 seconds.
- **Keep every `.ps1` ASCII-only.** Windows PowerShell 5.1 reads a BOM-less script as ANSI, so
  an em dash, curly quote or `·` in a string literal arrives corrupted.
- All cell writes go through the `SetV` / `SetF` helpers in the script. A plain
  `$range.Value2 = $x` inside a loop fails once it has seen a string and then a number — PowerShell
  caches the COM binding per line.
- Put the config in a temp folder, not the project folder.

**With Python, openpyxl and LibreOffice (e.g. a cloud sandbox):**
```
python scripts/build_certificate.py --template <latest 335 .xlsm> --config <config.json> --outdir "<claim folder>"
```
This path re-saves through openpyxl, so it carries the embedded-image check below. **Then run
the Excel integrity check** — openpyxl ignores calcChain and LibreOffice rebuilds it silently, so
neither proves the certificate opens in Excel:
```
python3 scripts/validate_xlsx.py --repair  <certificate>.xlsm
python3 scripts/validate_xlsx.py --check   <certificate>.xlsm     # must print CLEAN
```

Both builders check the template's column headings against the map before writing, populate
tabs 00–04, write the THIS CLAIM / TO COMPLETE formulas on every line, verify the math, and print
a JSON report. They write **no PDF** unless passed `-Pdf` / `--pdf` (tabs 01–04 only), which is
for a certificate already signed off. Require `"PASS": true` (ties to the invoice,
sheet agrees with the independent calculation, zero formula errors in the print areas). Then
copy the source claim schedule, invoice and stat dec into the same claim folder if they aren't
already there.

### 6. Review the rendered output
Look at the pages before reporting done (BDM verify-before-done). Render each tab's print area
to PNG in a temp folder — through Excel COM on Windows (`Range.CopyPicture` into a temporary
chart, `Chart.Export`), or from a temp LibreOffice conversion on the Python path — read the
images, then remove them. No preview PDF is left beside the held certificate. Confirm the certificate summary equals the
invoice, the trade sub-totals tie, THIS CLAIM is populated, the cashflow chart plots actuals
only for claimed months, and the contract-form references are right.

### 7. Log it and hold it
Update the project's CAR if any variation status was found out of line (`bdm-contract-admin-register`).
Record the held certificate where the user's own layer says held work is recorded. Never send.

### 8. Clean up the skill's own working files
Delete the scratch artefacts the skill created — the config JSON, render previews, any
intermediates — leaving only the deliverables (`.xlsm` and source docs) in the claim folder.
Only ever delete files **the skill created**; never project documents or the source claim
files. (Both builders remove their own temp folders.)

### 9. Present
Give clickable links to the `.xlsm` and the claim folder and list every judgement call and flag.
State that the PDF is held until the certificate is signed off.

## Template defects the builders correct (Form 335 R6)

- **THIS CLAIM hard-coded `0`.** R6 ships `=G−E` only on rows 14, 51 and 63; the other 46 input
  rows hold a literal `0`, so THIS CLAIM and its sub-totals under-report. Both builders write
  `=G−E` and `=C−G` on every input row.
- **Valuation date `=TODAY()`.** `02!F5` (and the signature date `F47`, which follows it) would
  roll forward every time the file is opened. The builders write the valuation date as a value.
- **Provisional sums don't reach the certificate.** Sub-total row 75 and `02!F12/F20/F21` take
  trades + variations only. The builders warn when a PS carries a claimed-to-date. Raise it with
  the reviewer — don't patch it in the form.

Report all three to the template owner for the next Form 335 revision. They are template
defects, not certificate judgements.

**Retired with R6.** The R3/R4 guards — cover-letter cert no. from `02!A4`, `scurve()` macro
port, cashflow cumulative SUM, "INPUT DATES" highlight, and the unfixed-materials `02!F28` rewrite —
acted on cells R6 no longer has. The unfixed-materials lesson stands for any revision that brings
that row back: prior unfixed materials must be added back. Left unfixed, that defect
over-certified one draft by **$1,533,071.32 ex GST**.

## Writing the workbook safely

**Excel COM path:** Excel saves the file, so branding, drawings and calcChain survive. Nothing
extra to check.

**openpyxl path:** run `validate_xlsx.py --check` (step 5) and **never let openpyxl re-save a branded BDM workbook without checking what
survived.** An openpyxl round-trip can silently drop embedded images — seven logos and roughly
19 KB were lost from one register this way. `build_certificate.py` compares `xl/media/` before
and after and **fails the build** if anything was dropped. When it fails, do not re-run and hope:
rebuild by editing the XML directly and re-zipping (`[Content_Types].xml` first in the archive;
`pageSetup` after `pageMargins`).

## Cashflow tab notes

R6's `04 Cashflow Forecast` takes inputs straight on the tab — there is no `CashflowInput` tab and
no macro. The builders fill the month column from `cashflow.start`, the forecast monthly from the
BDM S-curve `total · (x − 0.016x² + 0.016x − (1/3.021)(6x³ − 9x² + 3x))` with the cumulative
floored to $1,000 (x = month i of n), the actual monthly for claimed months **only**, and the
re-forecast monthly where supplied. Unclaimed months stay blank so the chart breaks the line
rather than dropping to zero. The tab holds 21 months; a longer programme needs the template
extended — the builders abort and say so.

## Flags to raise every time

Contract type and the form and revision used;
retention basis used; **contract form / edition confirmed against the executed contract**
(mandatory — the builders abort without it); **every CAR mismatch, with both figures**; how the
builder's margin is carried; any certified-vs-claimed delta; any PS carrying a claimed amount;
any source that was OneDrive cloud-only and couldn't be read; and the held-for-signature status,
with the PDF held until sign-off.
Scope is **head-contract** progress certificates.

## Reference files
- `references/template_map.md` — Form 335 R6 and Form 335a cell maps, roll-forward columns, cashflow layout.
- `references/config_schema.md` — the JSON config schema with a worked example.
- `scripts/build_certificate.ps1` — Excel COM builder (Windows, no Python).
- `scripts/build_certificate.py` — Python + LibreOffice builder.
- `scripts/validate_xlsx.py` — Excel-strict calcChain check and repair (Python path).
- `CHANGELOG.md` — revision history.
