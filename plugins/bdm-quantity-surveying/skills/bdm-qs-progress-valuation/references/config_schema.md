# Content-map (config.json) schema for build_pv_report.py

All keys optional except where the report needs them. Money as display strings ("$35,785.77").
Every populated cell keeps the **template's own formatting** — the script never restyles cells.

```jsonc
{
  "global_replacements": {            // applied to body, tables AND header/footer
    "[Project Name]": "28 Winchester Street, Hamilton",
    "[Project Address]": "28 Winchester Street, Hamilton QLD 4007",
    "[Builder Name]": "UrbanLuxe Projects Pty Ltd",
    "[Site Inspection Date]": "05 June 2026",
    "Valuation No. [N]": "Valuation No. 11",
    "[Report Date]": "June 2026",
    "[N]": "11"
  },
  "header_replacements": { },         // optional override; defaults to global_replacements

  "table_cells": {                    // "tableIndex": [[row, col, "text"], ...]
    "1": [[0,0,"Project: 28 Winchester Street, Hamilton"], [3,0,"Net Claim This Period: $35,785.77"]],
    "6": [[1,1,"$1,536,363.64"], [1,4,"$35,785.77"]]
  },

  "para_set": { "40": "Net Sum Recommended for Payment (Excl GST):  $35,785.77" },

  "trim_rows": { "7": [3,4], "17": [2,3] },   // delete these rows (any order) BEFORE cell fills,
                                              // so no template sample rows remain (e.g. Variation
                                              // Schedule, Consultants Certificates)

  "trade_breakdown": {                // Appendix A.2 (table 22)
    "table": 22, "start_row": 2,
    "rows": [ {"desc":"Preliminaries","sv":"$113,349.44","prevd":"$108,815.00","prevpct":"96%",
               "cur":"$4,534.44","curpct":"4%","totd":"$113,349.44","totpct":"100%"} ],
    "subtotal": ["Subtotal","$1,536,363.64","$1,500,577.87","","$35,785.77","","$1,536,363.64","100%"]
  },

  "variations": {                     // Appendix A.3 (table 23)
    "table": 23, "start_row": 2,
    "rows": [ ["VA-001","Cabinetry Appliances","$5,219.40","$5,219.40","100%","$0.00","0%","$5,219.40"] ],
    "subtotal": ["Subtotal","","$9,574.40","$9,574.40","","$0.00","","$9,574.40"]
  },

  "cashflow": {                       // table 14 + native chart
    "table": 14, "start_row": 1,
    "rows": [ ["1","31/05/2025","36,000","76,766","36,000","76,766","40,766"] ],
    "chart_cats": ["31/05/2025","..."],
    "chart_forecast": [36000, 131000],
    "chart_actual":  [76766, 149796]
  },

  "consultants": {                    // table 18 (auto-expands rows)
    "table": 18, "start_row": 1,
    "rows": [ ["DAH Architecture","Architect","AAI Limited","PI","$10.00M","23/01/2027"] ]
  },

  "expired_dates": {                  // auto bold-red any Expiry < report_date (or "Not received"/"—")
    "report_date": "2026-06-08",
    "targets": [ {"table":18, "col":5}, {"table":19, "col":4} ]
  },

  "remove_notes": [ "Right-click the table of contents", "To update the chart figures",
                    "send Alfred the contractor" ],
  "trim_notes": [ {"match":"where no consultant certificates",
                   "keep":"No consultant certificates have been received during this reporting period."} ],

  "photos": {                         // from --photos (OneNote/PDF export OR a folder of images)
    "count": 16, "caption_tables": [24,25],
    "captions": ["Street frontage & elevation — 05 June 2026", "..."]
  },

  "embed_appendices": {               // annexures EMBEDDED as page-images in the body, like the template
    "appendix_b": ["28 Winchester St Hamilton- Claim 11 April.pdf"],  // ONLY the builder's claim / contractor tax invoice
    "appendix_c": { "note": "Statutory Declaration not received ... to follow under separate cover." }
                                        // or {"pdf": "StatDec.pdf"} to embed a received declaration scan
  },

  "additional_appendices": [          // OPTIONAL standalone appendices for content not always present
    { "heading": "Appendix E: Development Cost Invoices",
      "intro": "Professional fee / development-cost invoices received during this reporting period.",
      "pdfs": ["2314 Winchester Inv 15337 - QSS Professional Fees.pdf", "..."] }   // paths in --claimdir
  ],                                  // omit this key entirely when the report has no development costs


  "dev_cost_table": {                 // §2.3 development-costs table, CLONED from another table for an exact style match
    "model_table": 8,                 // table to copy the style from (8 = 2.6 Contingency: Description | Amount)
    "anchor": "tabulated below",      // inserted after the paragraph containing this text
    "header": ["Description","Amount (excl GST)"],
    "rows": [ ["Queensland Surveying Solutions (Inv 15337)","$4,765.00"] ],
    "total": ["Total (Excl GST)","$11,736.47"]
  },

  "row_bold": [                       // BOLD exactly these row indices, regular elsewhere (handles merged cells)
    { "table": 21, "bold_rows": [0,1,6,11,12,18,19,23,24] }   // Cost-to-Complete cert: title, A-E headers + section totals
  ],
  "cell_size": [                      // set every cell of a table to a point size
    { "table": 22, "size_pt": 8 },    // trade breakdown
    { "table": 23, "size_pt": 8 }     // variations
  ],
  "insert_rows": [ { "table": 8, "after_row": 2, "count": 1 } ],   // clone+insert a row before cell fills (e.g. add the
                                                                  // Professional-Fee-Overrun line to the Contingency table)
  "bold_shade_rows": [ { "table": 8, "rows": [4,5] } ],           // apply header-style bold + shading to subtotal/total rows

  "prior": {                          // PREVIOUS issued report's to-date figures — drives the carry-forward QA checks
    "net_value_to_date": 1510152.27,        // prior cert 'Net Value of Payment to Date'  (must equal this claim's 'Previous Net Recommendation')
    "construction_prev_assessed": 1500577.87,// prior §2.4 'Total Completed to Date' for Construction Works
    "prof_fees_to_date": 61515.00            // prior aggregate professional fees claimed to date
  },
  "draft": "DRAFT — FOR SENIOR PM / QS REVIEW — NOT FOR ISSUE"
}
```

## Notes
- The certified building-works figures (table 6, Appendix A certificate, trade-breakdown
  subtotal) must all reconcile to the BDM valuation workbook — never key them independently.
- This skill is **flag-free**: there is no inline-callout or comment behaviour. Items the
  reviewer must confirm (Statutory Declaration outstanding, expired PI, figures to reconcile)
  belong in the hand-over message, not on the page.
- `expired_dates` highlights automatically; you do not need to pre-mark cells.
- Body Normal paragraphs are **justified**; section breaks and page breaks are preserved (cover
  stays on its own page, TOC starts fresh).
- Trade-breakdown / variation **Subtotal** rows are auto bold + shaded. In Appendix A use `unbold`
  so only the bottom-line total is bold.
- `global_replacements` are applied at the run level AND at the XML level in phase 2, so tokens
  split across runs or buried in nested tables / text boxes (e.g. the cover `Valuation No. [N]`,
  `[Report Date]`, `[Financier / Lender Name]`) are still populated.
