# CHANGELOG — Da Conditions Matrix

## R2 / 2026-08 — Excel integrity gate

Issued 17 August 2026. First CHANGELOG for this skill; R1 was the migration baseline of
16 August 2026.

Writing conditions into the master template turns template formula cells into values, which
leaves `xl/calcChain.xml` — the precomputed index of formula cells — naming cells that no
longer hold one. Excel walks it on open and reports the matrix as corrupt.

The R1 verification checklist ended at "**File opens cleanly** — reload via openpyxl with no
warnings". That check cannot detect this: **openpyxl ignores calcChain, and LibreOffice
rebuilds it silently**.

Changes:

- **Added `scripts/validate_xlsx.py`** — Excel-strict check and repair. This skill previously
  shipped no scripts at all.
- **Verification checklist item 8 added** — the matrix must return CLEAN from
  `validate_xlsx.py --check` before it is declared done. Item 7 reworded so the openpyxl
  reload is no longer mistaken for proof that Excel will open the file.

No change to the condition parsing, the dropdown lists or the tab structure.

## R1 / 2026-08 — migration baseline

Filed to the controlled skills library on 16 August 2026 under the BDM naming convention.
