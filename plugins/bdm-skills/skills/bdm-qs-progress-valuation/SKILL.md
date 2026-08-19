---
name: bdm-qs-progress-valuation
description: "Draft a BDM QS Monthly Progress Valuation Report (Form 425) - the financier's monthly drawdown report - from a building contractor's progress claim, the BDM valuation workbook, a site inspection and project documents. Trigger on 'prepare/draft the progress valuation report', 'monthly PV report', 'Form 425', 'QS progress report', 'progress valuation No.N', 'financier/lender monthly report', or when a builder's claim plus valuation workbook plus site photos are handed over for a monthly drawdown. Produces a DRAFT .docx and compiled PDF for Senior PM/QS review: a faithfully populated Form 425 (every cell keeps the template's own font and size) with native tables (Cost-to-Complete certificate, trade breakdown, variations), an S-curve cashflow chart, captioned site photos, bold-red expired insurance/approval dates, and the contractor's claim embedded as appendices. NOT for the Initial/Costing Report (Form 424 - use qs-initial-report) or the Progress Certificate (Form 335 - use progress-certificate-update)."
---

# QS Monthly Progress Valuation Report (Form 425) — draft for financier

## What this does and why

Each month the building contractor submits a progress claim. BDM (as QS) inspects the site,
assesses the claim against the trade breakdown, and reports the certified value, cost-to-
complete, programme, insurances and risks to the financier so the next drawdown can be
released. This skill reads the contractor's claim, the BDM valuation workbook (the authority
for the certified figures), the site inspection (photos + notes) and the project documents,
**populates the latest Form 425 working copy faithfully**, appends the supporting documents,
and produces a **DRAFT** for the Senior PM / QS to review, complete and issue.

You (Claude) do the judgement and author a JSON content map; the bundled
`scripts/build_pv_report.py` does the deterministic build.

## Faithful to the baseline template (the golden rule)

The output must look like the template with the data dropped in — **no structural or
formatting deviation**. The build script's `set_cell` always **preserves each template cell's
own run formatting** (font, size, alignment); never restyle cells, never swap fonts, never add
decorative tables or callouts. Populate placeholders, trim sample rows, embed the chart/photos,
strip the template's drafting notes — nothing else. This skill carries **no flag / comment /
callout behaviour**: items the reviewer must confirm are raised in the hand-over message, not
on the page.

## Authority boundary (read first)

BDM **drafts and recommends**; the Senior PM / QS or Director **decides, certifies and issues**.
- Every output stays **DRAFT** (a DRAFT marker is written to the cover; filename carries
  `_DRAFT`; never issue, never send to the financier).
- **Never invent** figures, dates, names, contract references or percentages. The certified
  building-works figures come **only** from the BDM valuation workbook / payment certificate.

## Always start from the template working copy

Do **not** roll forward the previous month's report. Pull the **latest**
`425-QS_Monthly_PV_Report_R*.docx` from the BDM templates working-copy location (highest
revision; ignore `_Superseded`). If a freshly-revised template won't open (BadZipFile /
cloud-only), ask the user to drag it into the chat. `references/template_map.md` maps every
table, placeholder and appendix; re-check the indices if the revision has changed.

## Inputs

For the reporting period (`…\08_Issued Reports\Progress Report\PRNN_<Mon><YY>`):
- **BDM valuation workbook** `…_PV NN_Bldg_<Mon> <YY>.xlsm` — authority for the certified
  figures (Cost to Complete sheet, Trade Summary, Cashflow).
- **Builder's progress claim** + tax invoice + **Statutory Declaration** (missing Stat Dec is
  a residual risk for the hand-over note) + the consultant fee invoices submitted with it.
- **Site inspection** OneNote/PDF export (photos + the PM's assessment).
- Project standing documents for approvals, insurances and the consultants register.

## Quality assurance — automatic checks & balances (carry-forward safety)

Every build runs `qa_checks` and writes a `<output>_QA.txt` log (PASS / FAIL per check). If any
check fails the log prints **REVIEW REQUIRED** — do not issue until every check passes. The
checks catch the exact class of error found in the historical audit (a variation double-counted
in one claim, a figure not carried forward, a reclassified soft cost).

**Internal consistency (automatic, from the built certificate):**
- Adjusted Contract Sum = Original + Approved Variations
- Total Value of Works = Contract Works Complete + Variation Works Complete
- Net Sum This Claim = Net Value to Date − Previous Net Recommendation
- GST = 10% of Net Sum This Claim;  NET SUM INCL GST = Net × 1.10
- Trade-breakdown subtotal = Contract Works Complete to Date

**Carry-forward continuity (needs the `prior` block — last month's to-date figures):**
- Previous Net Recommendation (this claim) = prior **Net Value of Payment to Date**
- Construction "Previously Assessed" = prior **Total Completed to Date**
- "Professional fees previously claimed to date" = prior **professional-fee aggregate**

**Cross-table reconciliation (automatic):**
- Contingency: Total Drawdown = Σ of the "Less:" variation/overrun rows
- Contingency: Forecast Remaining = Contingency − Total Drawdown
- Development Summary: the Approved-Variations column nets to ~0 (every variation/overrun is funded from contingency, so the budget total is unchanged)

Populate `prior` each month from the previous issued report (see `references/config_schema.md`).
Extend the checks as needed — they are cheap insurance against carry-forward error.

## Variations: building-contract vs development-level

Keep two variation streams separate, or they will not reconcile (this caused a real error on
Winchester where a $20,492 civil works variation was lumped into "building variations"):

- **Building-contract variations** (the head contractor's approved VAs) belong in the
  **Progress Certificate (Appendix A)**, **§2.4 Construction Costs** and **§2.5 Variation
  Schedule**. These three must always agree and match the certificate.
- **Development-level variations** that are NOT in the building contract (e.g. a civil works
  spend with no separate budget line) belong on their **own line in the §2.2 Development
  Summary** (Approved-Variations column) and as a **separate "Less:" line in §2.6
  Contingency** — never folded into the building figure. Add a `bold_shade`d **Total row** to
  the §2.2 Development Summary (insert_rows) so total approved variations are visible against
  contingency use.

So §2.4/§2.5 may legitimately show a smaller figure (building only) than the development-wide
total in §2.2/§2.6 — the contingency table itemises each stream. The reconciliation QA checks
above verify the contingency arithmetic ties out.

## Workflow

1. **Confirm** project, reporting period (claim No. N, month), financier and borrower; confirm
   the period folder before reading.
2. **Reconcile the template** (latest working copy); check `references/template_map.md` indices.
3. **Read the valuation workbook** (authority): original/adjusted contract sum, approved
   variations, total value of works, previous net recommendation, net sum this claim, GST, cost
   to complete, % complete; the full trade breakdown; the cashflow series for the S-curve.
4. **Read** the claim, Statutory Declaration (received?), consultant fee invoices, site-
   inspection date, the PM's assessment and the photos; the approvals, contract insurances and
   consultant PI (note any expired / not-received policies → bold-red date).
5. **Author the JSON content map** (schema in `references/config_schema.md`):
   `global_replacements`, `table_cells`, `para_set`, `trade_breakdown`, `variations`,
   `cashflow`, `consultants`, `dev_cost_table`, `expired_dates`, `trim_rows`, `remove_notes`,
   `trim_notes`, `row_bold`, `cell_size`, `photos`, `embed_appendices`,
   `additional_appendices` (optional), `insert_rows`, `bold_shade_rows`, **`prior`** (carry-forward base), `draft`. Then:
   ```
   python scripts/build_pv_report.py --template "<latest 425 R2.docx>" \
     --config "<map.json>" --photos "<OneNote.pdf | photo folder>" \
     --claimdir "<period>/Builder Claim" \
     --out "<period>/<Project>_PV Report NN_DRAFT.docx" --pdf
   ```
6. **The script** preserves template formatting, strips the template's drafting notes (TOC
   "update field", chart "Edit Data", the "send Alfred" note, "Note: where no consultant
   certificates… delete the rows…" → keep only the clean note), trims sample rows, renders any
   expiry date earlier than the report date in bold red, embeds the S-curve chart and captioned
   site photos, and removes the `@@APPENDIX_B` markers.
7. **Appendices** — embedded as page-images in the body, like the template:
   - **Appendix A** (Cost-to-Complete certificate + trade breakdown + variations) is native — populated from the workbook.
   - **Appendix B: Contractor's Claim & Tax Invoice** — `embed_appendices.appendix_b` carries ONLY the builder's
     progress-claim documents (claim cover / schedule / contractor tax invoice). Do **not** put consultant or
     development-cost invoices here.
   - **Appendix C: Statutory Declaration** — `embed_appendices.appendix_c` (a covering note when outstanding, or the scan).
   - **Appendix D: Site Photographs** — from `--photos` (OneNote/PDF export OR a folder of images).
   - **Optional extra annexures** — use `additional_appendices` for content that is **not always present** (e.g.
     development-cost / consultant-fee invoices). Each entry is a `{heading, intro, pdfs}` block and becomes its own
     standalone appendix (e.g. "Appendix E: Development Cost Invoices") on a new page. Omit the key entirely when the
     report has no such costs. After the build, refresh the Word TOC (F9) so any new appendix appears.
8. **Verify before done** (BDM standing rule): net sum, GST and incl-GST tie to the
   certificate; adjusted contract sum = original + approved variations; trade-breakdown
   subtotal = certified contract works; every date/name/claim-number correct; **no
   `[placeholder]`, no drafting note, no template sample data, no formatting deviation**; expired
   dates bold-red; photos embedded; DRAFT marker present; file opens cleanly; **the `_QA.txt` log shows all checks PASS**. Look at the
   rendered pages before reporting done.
9. **File, clean up, present** the DRAFT (with `_DRAFT` in the name); in the hand-over message
   list every judgement call, every requested-not-received item (Statutory Declaration,
   WorkCover / Home Warranty, expired consultant PI) and any figure to reconcile.


## Risk-rating colour (BDM standing drafting rule)

Every risk-rating value in the report is colour-coded by the rating word: **LOW = green `1A4A2A`, MEDIUM = amber `9D7B5B`, HIGH = red `B91C1C`** (bold). This is applied automatically by `colour_risk_ratings(d)` in `scripts/build_pv_report.py` (whole-cell exact match, so prose is untouched) and covers §1.0 Specific Risk Items, §3.4 Construction Risk Status (incl. Likelihood/Impact) and §5.0 Risk Assessment. Verification: confirm the rating cells render in the correct colours before reporting done.
