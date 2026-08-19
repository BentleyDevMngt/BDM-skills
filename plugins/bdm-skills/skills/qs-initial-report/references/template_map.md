# Form 424 - template map (R1, 2026-06)

Source: `…\BDM TEMPLATES\Working Copy\400 Quantity Surveying\424-QS_Initial_Report_R1_2026-06.docx`.
Always re-confirm against the live latest revision - table indices shift if rows are added.

## Document structure (headings)
1.0 Executive Summary -> Project Snapshot, Report Acceptance Preconditions, Cost Verification
Opinion, Specific Risk Items, Disclosures, Statement of Limitations
2.0 Project Description -> 2.1 Overview, 2.2 Building Area Analysis, 2.3 Contracting Parties
3.0 Cost Verification & Budget -> 3.1 Report Basis, 3.2 Development Budget, 3.3 Independent
Cost Verification, 3.4 PC & Provisional Sums, 3.5 Contingency, 3.6 Cashflow
4.0 Construction & Contract -> 4.1 Contract, 4.2 Contractor Capability, 4.3 Licence & QBCC,
4.4 Programme, 4.5 Insurances, 4.6 Site Conditions & Land Survey
5.0 Design & Approvals -> 5.1 Design Documentation, 5.2 Outstanding Information Register,
5.3 Consultants, 5.4 Authority Approvals, 5.5 Statutory & Design Compliance,
5.6 Geotechnical & Environmental, 5.7 Valuation, 5.8 Pre-Sales
6.0 Risk Assessment | 7.0 Appendices (A-I)

## Tables (index -> purpose -> key cells, 0-based row/col)
| # | Purpose | Notes |
|---|---|---|
| 0 | Cover banner | DRAFT marker prepended here. |
| 1 | Project Snapshot (10x2) | Project, Borrower, Contractor, Financier, Form of Contract, Contract Sum, BDM Estimate, Cost Variance, Date for PC, Report Revision+Issue (row 9). |
| 2 | **Report Acceptance Preconditions** (5x3) | rows 1-4 = DA / Contractor appointed / Building Contract provided / Site inspection. Col1=Status (Yes/No), Col2=Refer. Set **No** for critical gaps. |
| 3 | Exec cost-verification (3x2) | Contract Sum, BDM Estimate, Variance (within/outside +/-10%). |
| 4 | **Specific Risk Items** (14x3) | rows 1-13: Item / Current Status / Risk Level (LOW/MEDIUM/HIGH coloured). |
| 5 | Building Area Analysis (5x4) | Stage / FECA / UCA / Total GFA; last row Total. |
| 6 | Contracting Parties (4x2) | Borrower / Contractor / Superintendent / Financier. |
| 7 | **Development Budget** (8x3) | rows 1-7: Land, Infra/Authority, Construction, Prof/Consultant, Other Soft, Contingency, Total. Col1=Budget, Col2=Comment. Totals must add. |
| 8 | Cost Verification (4x4) | Building Works / Contingency / Total: Builder vs BDM Estimate vs Variance%. |
| 9 | PC & Provisional Sums (4x4) | Item / Qty-Rate / Total / % of Contract. |
| 10 | Construction Contract particulars (15x2) | form, sum, parties, security, DLP, insurances, LDs, dates. |
| 11 | Contractor (4x2) | Contractor / Licence Address / ABN / Contact. |
| 12 | QBCC Licence (5x2) | Licence No / Class / Status / Conditions / Max Revenue. |
| 13 | Programme (4x4) | Stage / Duration / Start / Date for PC. |
| 14 | Project Insurances - Contractor (5x4) | Contract Works / Public Liability / WorkCover / Home Warranty. |
| 15 | Consultant PI (6x4) | Discipline / Company / Cover-Insurer / Expiry. |
| 16 | Design Documentation (13x2) | discipline -> Prepared By. |
| 17 | **Outstanding Information Register** (16x5) | 15 doc rows. Cols 1-4: Received / N/A / Critical / Not Critical. Template pre-ticks Received; **move the [x]** per project. |
| 18 | Authority Approvals (5x2) | DA / BA / Expiry vs programme / Onerous conditions / Further approvals. |
| 19 | Risk Assessment (6x4) | Area / Risk / Rating (L/M/H) / Refer. |

## Inline FLAG callouts - two categories (applied by the skill)
- **FLAG - BDM** = bronze house callout (fill F4F4F1, left bar + small-caps label 9D7B5B):
  internal **input / consideration prompt** for the PM/QS. The template's "FLAG - COMPLETE"
  prompts are relabelled to BDM at build time.
- **FLAG - FINANCIER** = dark-red callout (fill F8ECEC, bar + label A33A3A): a **residual risk**
  to surface to the financier. Created by cloning the bronze callout and recolouring shd/pBdr/
  label run.
- Legacy funder-specific tags (ANZ / NAB·CRER / WESTPAC) are **retired** by the build.

## The requested-not-received chain
Empty Information-Received folder -> Table 17 (mark Critical / Not Critical, or N/A) -> if
Critical, Table 2 precondition = **No** -> narrative in 1.0 / 3.1 states "subject to receipt;
financier to require as a precondition to the facility / first drawdown" -> add a
**FLAG - FINANCIER** at the section.

## Appendices (Form 425 convention - applied by the skill)
7.0 Appendices is a plain A-I list in the template. The build restructures it to the 425
pattern: Heading 2 "Appendix X: Title", with received PDF **extracts embedded one page per Word
page** (rasterised 150 dpi). Not-received appendices get a one-line note. Standard map:
A Letter of Instruction · B Design Documents · C Building Contract · D Cost Verification
Estimate · E Insurances · F Builder's Details & Licence · G Cashflow · H Environmental ·
I Authority Approvals.
