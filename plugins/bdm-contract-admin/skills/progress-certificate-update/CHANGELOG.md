# progress-certificate-update — changelog

## R3.1 · 2026-10 — cost plus on Form 335a (30 October 2026)

Form 335a R1 (Cost Plus) was released on 30 October 2026 under CN-2026-055, after the Director
approved the form number the same day. R3.0 stopped and flagged every cost-plus claim because
there was no controlled cost-plus form; R3.1 builds it on 335a. The 335a cell map written in R3
was re-verified against the released file and needed no change. Only the wording moved: SKILL.md
step 2 and the flags list, template_map.md, config_schema.md (a cost-plus worked example) and the
builders' Drafts-for-Review refusal message. Both builders still refuse a template in
`Drafts for Review\`, and refuse a cost-plus claim on Form 335.

Tested on 30 October 2026: the Excel COM builder on Form 335a R1 2026-10 with a cost-plus claim
(PASS, ties to $69,300, variance adjustments 3,000, adjusted contract sum 363,000). The Python
builder is still unrun.

## R3.0 · 2026-10 — ported into BentleyDevMngt/BDM-skills (29 October 2026)

R3 was written in JamesBDM/bdm-plugins (`956ab65`, bdm-contract-admin 2.1.0) and never reached
this repository, which carried R2.0 · 2026-08 — a line that predates Form 335 R6. This port takes
R3 as written (below), together with the JamesBDM R2 content this repository never received: the
CAR cross-check (step 4a), mandatory `contract_form`, the embedded-image check, the current
`13_Contract Admin` filing path and no DRAFT marking. It keeps this repository's additions: the
revision line, the project summary block, the rule that the contract sum and prior figures come
from the contract and prior certificate rather than the summary, and `validate_xlsx.py` with its
check on the Python path. The pilot stays unnamed.

One change to R3: **the PDF is opt-in.** Both builders write the `.xlsm` only; `-Pdf` / `--pdf`
exports tabs 01–04 for a certificate already signed off. A certificate awaiting sign-off is never
PDF'd (company CLAUDE.md; Director rule 29/7/26). R3 and R2.0 both wrote a PDF on every build.

Tested on 29 October 2026: the Excel COM builder against a scratch copy of Form 335 R6
(2026-09), with and without `-Pdf`. The Python builder is still unrun — no Python on the PC used.

## R3 · 2026-10 (15 October 2026) — JamesBDM/bdm-plugins, `bdm-contract-admin` 2.1.0

Driver: Form 335 R6 released 25 September 2026 under CN-2026-049. R2 mapped the R4/R5 layout and
would have crashed on R6 (no `CashflowInput` tab) or written into the wrong cells.

- **Form 335 R6 cell map.** On '03 Trade Breakdown': value C, prev claimed E, claimed to date G,
  this claim H, to complete I (VARIANCE and CURRENT BUDGET removed). On '02 Certificate': previous
  net F27, net ex GST F28, GST F39, net incl GST F40, signature date F47, footer B50. Roll-forward
  is now E := prior certificate's G. Variations take the CAR approved value in column C.
- **Contract-type branch.** `contract_type` is mandatory. Fixed price → Form 335 R6+. Cost plus →
  Form 335a once released. Until then the skill flags that there is no controlled cost-plus form,
  and the builders refuse a template under `Drafts for Review\`. The 335a draft layout is mapped
  and tested, ready for release.
- **New Excel COM builder `scripts/build_certificate.ps1`** for Windows PCs with no Python. It is
  ASCII-only. Tested on 15/10/26 against the R6 template and a scratch copy of the 335a draft: both
  PASS, and seven abort paths were checked.
- **`build_certificate.py`** brought onto the same layout map, preflight and checks. Not run on
  this PC (no Python) — the first run in a Python environment should be watched.
- **Guards.** New: THIS CLAIM / TO COMPLETE formulas restored on every row (R6 ships 46 rows
  hard-coded 0). New: a layout fingerprint check before writing. New: a non-approved variation
  carrying value aborts the build. New: a warning when a provisional sum carries a claim (R6's PS
  block doesn't feed the certificate). Retired: the R3/R4 guards for cells R6 no longer has.
  `builders_margin` was removed, because R6 has no margin row and writing `I56` would overwrite a
  PS formula.
- **Verification** now includes variations, and checks the sheet's own net incl GST against the
  independent calculation.
- **Filing** brought into line with CLAUDE.md §8 (1/9/26): the certificate saves straight into the
  project's existing claim folder, not `00_ai_sandbox`.
- **Cashflow** rewritten for R6's on-tab inputs (month, forecast monthly, actual monthly,
  re-forecast).

## R2 · 2026-08 — JamesBDM/bdm-plugins

CAR cross-check (step 4a), mandatory `contract_form`, builder's-margin roll-forward, unfixed
materials guard, embedded-image check. No DRAFT marking (15/9/26, `2c84b3d`).

## R1 — JamesBDM/bdm-plugins

First issue: Form 335 R4 roll-forward, `scurve()` port, tabs 01–04 PDF.

## Earlier history in BentleyDevMngt/BDM-skills

### R2.0 / 2026-08 — Excel integrity gate

Issued 17 August 2026. Added `scripts/validate_xlsx.py` and made `--repair` then `--check` a
condition of filing: the build preserved the template's parts, so a stale `xl/calcChain.xml`
survived and Excel reported the certificate as corrupt. Carried into R3.0 for the Python path.

### R1.0 / 2026-08 — migration baseline

Filed to the controlled skills library on 16 August 2026 under the BDM naming convention;
flattened from `_source/`, drifted Form 335 workbook removed (migration decision J3).
