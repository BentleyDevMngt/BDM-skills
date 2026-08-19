---
name: qs-initial-report
description: >-
  Draft a BDM QS Initial Report (Form 424) - the financier's pre-drawdown Initial / Costing Report - from a financier's letter of instruction and the project's Information Received folder. Trigger on 'prepare/draft/produce the initial report', 'initial costing report', 'Form 424', 'QS initial report', 'financier report', 'lender report for [project]', 'report against the developer's budget', 'cost to complete report', or when a financier instruction plus a folder of received documents is handed over for a construction loan facility. Produces a DRAFT .docx for Senior PM/QS review: populated Form 424, two-category inline FLAGS (BDM internal input prompts + Financier residual-risk), outstanding-information register, report-acceptance preconditions, and received PDF extracts embedded as appendices. NOT for monthly progress valuations (Form 425) or progress certificates (Form 335); a separate QS progress report skill covers ongoing assessments.
---

# QS Initial Report (Form 424) - draft for financier

## What this does and why

A financier instructs BDM (as Quantity Surveyor) to prepare an Initial / Costing Report
before the first construction drawdown. The report reviews approvals, design, contract,
contractor, programme, insurances and - most importantly - verifies the construction cost and
reports the whole cost-to-complete against the developer's budget, with a recommendation on
sufficiency. This skill reads the financier's letter of instruction and everything in the
project's **Information Received** folder, populates the **latest Form 424** template, embeds
the received documents as appendices, and produces a **DRAFT** report for the Senior PM / QS to
review, complete and issue.

You (Claude) do the judgement; the bundled `scripts/build_initial_report.py` does the
deterministic build (token fill, table cells, narrative, flag categorisation, appendix
embedding, DRAFT marker). Think and confirm, then let the script build.

## Authority boundary (read first)

BDM **drafts and recommends**; the Senior PM / QS or Director **decides, certifies and issues**.
- Every output stays **DRAFT** ("DRAFT - FOR SENIOR PM / QS REVIEW - NOT FOR ISSUE" on the
  cover; filename carries `DRAFT_v0.x`). Never issue, never send to the financier.
- **Never invent** figures, dates, names, areas, licence numbers or contract references. If a
  fact is not in the brief or the received documents, leave/insert a flag - do not guess.
- The cost-verification opinion, contingency adequacy, programme achievability and risk ratings
  are draft recommendations for the reviewer to confirm.

## Two-category flag system

Every report carries two clearly-distinct inline callouts:

- **FLAG - BDM** (bronze house callout): an internal **input / consideration prompt** for the
  PM/QS - a section to complete, a number to verify, a judgement to make before issue.
- **FLAG - FINANCIER** (dark-red callout): a **residual risk** to surface to the financier -
  typically a critical document requested-but-not-received, recommended as a precondition to
  the facility / first drawdown.

The script retires the template's legacy funder-specific tags (ANZ / NAB·CRER / WESTPAC) and
relabels the generic "COMPLETE" prompts to BDM. New Financier flags are added per the content
map and recoloured to the red house style automatically.

## Inputs

A financier **letter of instruction** plus a project **Information Received** folder (standing
path `…\08_Issued Reports\00_Information Received`), organised by category. Empty category
folders are a signal - those documents were requested but **not received**.

## Workflow

### 1. Confirm the project and the document directory
Resolve the project; **ask the user to confirm the Information Received directory** before
reading. Confirm the **financier** (from the instruction) and the **report revision** (first
issue = R0 / DRAFT). Don't assume the financier is a major bank - many are private funds.

### 2. Reconcile the template (always latest)
Pull the **latest** `424-QS_Initial_Report_R*.docx` from
`…\BDM TEMPLATES\Working Copy\400 Quantity Surveying\` (highest revision; ignore `_Superseded`).
Also read `421-Documents_Required_Initial_Report_R*.docx` (master documents-required list).
Cloud-only trap: if a freshly-revised template won't open (BadZipFile), ask the user to drag it
into the chat. `references/template_map.md` maps every table, placeholder and appendix.

### 3. Read the financier brief
Extract the explicit scope items and the funder-specific conditions (e.g. "no funding table -
report against the developer's budget only", "whole cost-to-complete to be captured", "payment
prior to release", conflict-of-interest confirmation). These shape §3.1 and the preconditions.

### 4. Read everything in Information Received and map it to the report
Walk every category folder. For each section pull the facts (parties, ABNs, contract sum, form
of contract, QBCC licence/class/MR, areas, geotech class, programme, approvals, budget). Record
received vs not-received against the Form 421 list. Decide per section: **populate**, **BDM
flag** (input/judgement needed), or **requested-not-received** (Financier flag + register +
precondition).

### 5. Write the content map (JSON) and build
Author a JSON content map (schema in `references/config_schema.md`):
`global_replacements`, `table_cells`, `para_set`, `flags` (BDM/FINANCIER adds; funder tags
retired), `appendices` (PDF sources + page extracts, or a not-received note), `draft`. Then:
```
python scripts/build_initial_report.py --template "<latest 424.docx>" \
  --config "<map.json>" --infodir "<project>/08_Issued Reports/00_Information Received" \
  --out "<project>/00_ai_sandbox/Initial Report/DRAFT_QS_Initial_Report_<Project>_v0.1.docx"
```
Stage working files in the active project's `00_ai_sandbox`.

### 6. Appendices (Form 425 convention + embed the PDFs)
Appendices are restructured to match Form 425: Heading 2 "Appendix A: …" sub-headings, with the
received PDF **extracts embedded one page per Word page** (rasterised at 150 dpi). 424's titles
say "Extract of …" - embed short docs in full (licence, decision notice, instruction) and a
sensible page-extract of large ones (drawings, contract); never the full 200-page contract. For
a not-received appendix, the script writes a one-line note pointing to the register / Financier
flag. Map: A Letter of Instruction · B Design Documents · C Building Contract · D Cost
Verification Estimate · E Insurances · F Builder's Details & Licence · G Cashflow · H
Environmental · I Authority Approvals.

### 7. Requested-not-received logic (do not skip)
For every document requested but not received: mark the **Outstanding Information Register**
(Table 17 - Received / N/A / Critical / Not Critical); for each **critical** item set the
**Report Acceptance Precondition** (Table 2) to **No**, add a **FLAG - FINANCIER** at the
section, and state in §1 / §3.1 that the report is subject to receipt and the financier should
require it as a precondition to the facility / first drawdown.

### 8. Verify before done (BDM standing rule)
Open the built .docx: every figure ties to source; cost variance correct vs ±10%; development
budget totals add; dates/names/ABNs/licence numbers match; register + preconditions reflect the
empty folders; both flag styles present and correct; appendix pages embedded; DRAFT marker
present; file opens cleanly. Never report done before looking.

### 9. File, clean up, present
Leave the DRAFT in the sandbox `Initial Report` sub-folder; only delete scratch the skill
created. Do not write into `01_Initial Report` - that is the reviewer's call on issue. Present
the DRAFT and list every judgement call, every requested-not-received item, and every Financier
residual-risk flag.

## Flags to raise every time
Cost-verification opinion + basis; contingency adequacy; programme achievability; each
requested-not-received item and its criticality; conflict-of-interest confirmation; whether a
funding table was provided; any OneDrive cloud-only source that couldn't be read; DRAFT status.

## Reference files
- `references/template_map.md` - Form 424 tables, placeholders, appendices, flag styles.
- `references/config_schema.md` - content-map JSON schema (incl. flags + appendices) with examples.


## Risk-rating colour (BDM standing drafting rule)

Every risk-rating value is colour-coded by the rating word: **LOW = green `1A4A2A`, MEDIUM = amber `9D7B5B`, HIGH = red `B91C1C`** (bold), applied automatically by `colour_risk_ratings(doc)` in `scripts/build_initial_report.py` (whole-cell exact match). Covers the Specific Risk Items (Risk Level) and Risk Assessment (Rating) tables. This overrides any template cell colour so the palette is consistent across all BDM reports. Verify the rating cells render correctly before reporting done.
