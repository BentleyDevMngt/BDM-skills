# CHANGELOG — Progress Certificate Update Skill

## R2 / 2026-08 — Excel integrity gate

Issued 17 August 2026, alongside the same fix to the Floor Area Schedule, Monthly Cost Report,
Progress Claim Update and DA Conditions Matrix skills.

Form 335 is an `.xlsm` and the build preserves the template's branding, cashflow chart and macro
parts — so the original `xl/calcChain.xml` survives into the deliverable. That index names every
formula cell; static-ising the cashflow and writing certified values turns formula cells into
values while the index still names them, and Excel reports the certificate as corrupt on open.

**openpyxl ignores calcChain and LibreOffice rebuilds it silently**, so neither the openpyxl
reload nor the LibreOffice recalc in the R1 verification proves the file opens in Excel. (A plain
openpyxl `wb.save()` drops calcChain and is safe from this, but strips the branding — preserving
the branded parts is what carries the risk.)

Changes:

- **Added `scripts/validate_xlsx.py`** — Excel-strict check and repair.
- **Verification step now requires** `--repair` then `--check` before the certificate is filed or
  presented, with the openpyxl/LibreOffice caveat stated plainly.

No change to the certification logic, the AS4000 cl.37.2 basis or the tabs-01–04 PDF export.

## R1 / 2026-08 — migration baseline

Filed to the controlled skills library on 16 August 2026 under the BDM naming convention;
flattened from `_source/`, drifted Form 335 workbook removed (migration decision J3).
