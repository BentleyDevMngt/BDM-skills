# Form 425 R2 template map (425-QS_Monthly_PV_Report_R2_2026-06.docx)

Re-verify indices if the revision changes — tables move between revisions. Indices are
0-based as returned by `python-docx` `Document.tables[i]`.

## Tables
| # | Section | Purpose | Notes |
|---|---------|---------|-------|
| 0 | Cover | Title / project / address | replace "PROGRESS VALUATION REPORT" → add "No.N"; DRAFT marker added by script |
| 1 | 1.0 Exec | Summary box (Project/Builder/Contract Sum/Adjusted/Progress/PC/Net Claim/Retention) | cells carry label + value |
| 2 | 1.0 Exec | QS Forecast Opinion (Orig Sum/Forecast Final/Cost Variance/Adjusted PC Date/Completion Opinion) | col1 = value |
| 3 | 1.0 Exec | Specific Risk Items (Report Section / Risk Item / Risk) | rows: Schedule, Cost×3, Quality×2 |
| 4 | 2.1/2.2 | Build-costs summary (Item/Orig/Forecast/Prev%/Total Comp/Net Claim/CTC) | Construction, Variations, Pending, Retention, Total |
| 5 | 2.2 Development Summary | Dev budget (Item/Orig/Approved Var/Forecast/Total Comp/This Claim/CTC) | Land, Civil, Consultants, Construction, Authority, Contingency |
| 6 | 2.4 Construction Costs | Description/Orig/Prev Assessed/Total Comp/This Claim/CTC | Construction Works, Variations, Pending, Total — **authority = valuation certificate** |
| 7 | 2.5 Variation Schedule | Var No/Description/Status/Amount | delete unused rows; last row = Total (label merged cols 0-2, amount col3) |
| 8 | 2.6 Contingency | Description/Amount | Contingency, Less Variations, Total Variations, Forecast Remaining |
| 9 | 2.7 Retention | Security Type/Rate/Max%/Max$/Held This/Held to Date | nil if no retention provision |
| 10 | 2.8 Statutory Declaration | Received/Date/Period/Notes | "No" + FINANCIER flag if outstanding |
| 11 | 2.9 Materials Off-Site | Description/Value/Location/Evidence/In Claim | usually "No materials … / $0.00 / No" |
| 12 | 3.1 Programme | Contract/Possession/Duration/Elapsed/Orig PC/Progress/EOT/Revised PC/QS Forecast PC | 2-col label:value pairs |
| 13 | 3.2 Progress | Description/% Complete/Program Date/Status | activity rows |
| 14 | 3.3 Cashflow | Month/Date/Monthly F/Actual M/Cum F/Actual Cum/Cum Variance | feeds the chart; negatives in (brackets) |
| 15 | 3.4 Construction Risk Status | Risk Item/Likelihood/Impact/Rating/Mitigation | |
| 16 | 4.1 Authority Approvals | Approval/Authority/Approval Ref/Reference/Status/Expiry | DA, Building, Plumbing, Connection Cert |
| 17 | 4.3 Consultants Certificates | Consultant/Cert Received/Date/Issues | single "none this period" row when nil |
| 18 | 4.4 Consultants Register | Name/Discipline/Insurer/Policy Type/Insured Amount/Expiry | **expand rows**; expired/not-received Expiry → bold-red |
| 19 | 4.5 Contract Insurances | Party/Insurance Type/Insurer/Policy No/Expiry/Status | Contract Works, Public Liability, WorkCover, Home Warranty |
| 20 | 5.0 Risk Assessment | Category/Risk/Rating/Action | Schedule, Cost, Quality, Approvals, Other |
| 21 | Appendix A | Progress Certificate (Cost to Complete) — A–E blocks | col1 = value; rows 2-26 |
| 22 | Appendix A.2 | Trade Breakdown (Description/Sched/Prev$/Prev%/Curr$/Curr%/Total$/Total%) | replace sample rows; data start row 2; Subtotal last |
| 23 | Appendix A.3 | Approved Variations (same columns) | data start row 2; Subtotal last |
| 24,25 | Appendix D | Photo caption grids (8 captions each) | image in para 0, caption in para 1 of each cell |

## Narrative paragraphs (by index — re-verify per revision)
20-21 Exec commentary · 35 §2.1 intro · 37 claim-received bullet · 40 Net Sum Recommended ·
45 §2.3 commentary (anchor for soft-cost table: "tabulated below") · 49 Total Value of Works ·
53 §2.6 contingency commentary · 56 §2.7 retention · 60 §2.8 Stat Dec · 64 §2.9 materials ·
68 §3.1 programme · 70 §3.2 photos line · 72 §3.3 cashflow · 87/89 §4.6 environmental ·
119 Appendix C note · 123 Appendix D photos line.

## Drafting notes to strip (remove_notes / trim_notes)
- TOC: "Right-click the table of contents below … Update Field …"  (remove)
- §3.3: "To update the chart figures: right-click the chart → Edit Data …"  (remove)
- Appendix B: "To refresh each month: send Alfred the contractor's PDF …"  (remove)
- §4.3: "Note: where no consultant certificates … delete the data rows above …"  (trim →
  keep only "No consultant certificates have been received during this reporting period.")
- §6.0: "… All tables are editable native Word tables — update the values directly …"  (trim →
  "Supporting documents for this Progress Valuation Report are attached below.")
- Appendix A: "… Replace the figures below each month …"  (trim to the descriptive first
  sentence)
- Any residual `[bracketed]` prompt text.

## Media / appendix structure
- `cover-image` (image1), `b-mark` logo (image2) — keep.
- Cashflow is a native chart (`word/charts/chart1.xml`) — update `<c:cat>` strCache + the two
  `<c:numCache>` (series 1 = Cumulative Forecast, series 2 = Actual Cumulative). Do NOT touch
  the `<c:tx>` series-title caches.
- 16 `site-photo` drawings reuse 8 media — replace each blip with a unique new image.
- `appx-b-*` / `appx-23` drawings are sample claim pages — remove; the real claim is appended
  in the compiled PDF at the Appendix B divider.
