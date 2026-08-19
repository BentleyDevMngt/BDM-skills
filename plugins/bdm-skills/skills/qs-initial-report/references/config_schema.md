# Content-map JSON schema (build_initial_report.py)

Authored by Claude after reading the brief + Information Received; applied deterministically.
Only what you put in the map reaches the document - nothing is invented.

```jsonc
{
  // 1. GLOBAL tokens only - same meaning everywhere (body + text boxes + headers/footers).
  "global_replacements": {
    "[Project Name]": "[Project Name]",
    "[Financier / Lender Name]": "[Financier / Lender Name]",
    "[Entity name / ACN]": "[Entity name / ACN]",
    "[Builder name / ABN]": "[Builder name / ABN]",
    "[Report Date]": "To confirm on issue",
    "[0X]": "R0 (DRAFT)"
  },

  // 2. Context-specific cells (figures/dates/statuses sharing a placeholder). 0-based row/col.
  "table_cells": [
    {"table": 1, "row": 5, "col": 1, "text": "$1,488,392 (excl. GST)"},
    {"table": 17, "row": 4, "col": 3, "text": "x"}        // BA = Critical
  ],

  // 3. Narrative paragraphs you have substantiated (matched by a unique anchor substring).
  "para_set": [
    {"anchor": "The proposed development comprises", "text": "The proposed development ..."}
  ],

  // 4. TWO-CATEGORY flags.
  "flags": {
    "retire_funder_tags": true,        // drop ANZ/NAB/CRER/WESTPAC flags (default true)
    "relabel_complete_to_bdm": true,   // template "FLAG - COMPLETE" prompts become "FLAG - BDM"
    "add": [
      // kind "BDM"  -> bronze internal input/consideration prompt
      {"anchor_heading": "Development Budget", "kind": "BDM",
       "body": "Nil consultant/PM fees in the budget - QS to add cost-to-complete + QS fees."},
      // kind "FINANCIER" -> dark-red residual-risk callout (auto-recoloured)
      {"anchor_heading": "Project Insurances", "kind": "FINANCIER",
       "body": "Residual risk: no insurances provided. Recommend the Financier require ..."}
    ]
  },

  // 5. APPENDICES - Form 425 convention (Heading 2 "Appendix X:") + embedded PDF extracts.
  //    `sources[].pdf` is RELATIVE to --infodir. `pages`: "all" | "1-6" | "1,3,5".
  //    Use `note` (and no sources) for a not-received appendix.
  "appendices": [
    {"letter": "A", "title": "Letter of Instruction",
     "sources": [{"pdf": "Financier Instruction/Instructions for QS.pdf", "pages": "all"}]},
    {"letter": "B", "title": "Extract of Design Documents (site plans, floor plans, elevations)",
     "sources": [{"pdf": "Drawings/7._Contract_Drawings.pdf", "pages": "1-6"}]},
    {"letter": "D", "title": "Cost Verification Estimate",
     "note": "[QS to complete - independent elemental estimate. Refer Section 3.3.]"}
  ],

  // 6. DRAFT marker (on by default).
  "draft": {"mark": true, "cover_table": 0,
            "line": "DRAFT - FOR SENIOR PM / QS REVIEW - NOT FOR ISSUE"}
}
```

## Authoring rules
- Never put an invented figure in the map. If unknown, omit the cell and leave/insert a flag.
- `global_replacements` ONLY for one-meaning-project-wide tokens; everything numeric/date-like
  goes in `table_cells` or `para_set`.
- Verify totals yourself (development budget, variance %); the script does not calculate.
- Flag taxonomy: **BDM** = something the PM/QS must do/confirm before issue; **FINANCIER** =
  a residual risk to surface, usually a critical requested-not-received item recommended as a
  precondition to the facility. Pair Financier flags with Table 17 (register) + Table 2
  (preconditions = No) + a §1/§3.1 precondition sentence in `para_set`.
- Appendices: embed short docs in full; page-extract large ones (drawings, contract). The build
  needs `--infodir` set to the Information Received folder so relative PDF paths resolve.
