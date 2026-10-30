# progress-certificate-update — R3.1 · 2026-10

Builds a BDM Progress Certificate from a builder's progress claim — BDM's certifying instrument
as Superintendent under AS4000 cl.37.2. Fixed price uses **Form 335 R6**; cost plus uses
**Form 335a R1** (released 30 October 2026, CN-2026-055). Companion to `progress-claim-update`, which builds the builder's claim.

## What you get
- The populated `.xlsm`, saved straight into the project's existing claim folder.
- No PDF while the certificate is held. Once it is signed off, `-Pdf` / `--pdf` produces a PDF of
  **tabs 01–04 only** (Cover, Certificate, Trade Breakdown, Cashflow).
- A check that the net incl GST equals the builder's tax invoice and the sheet agrees with an
  independent calculation.

## How it works
`SKILL.md` is the workflow: identify the project, claim no. and contract type; pick the form;
read the project folder (parties, retention basis, contract form, prior net); cross-check every
variation against the CAR; assemble a JSON config; run a builder.

Windows PC with Excel, no Python:
```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_certificate.ps1 `
  -Template "<Working Copy\300 ...\335-Progress_Certificate_R6_2026-09.xlsm>" `
  -Config "<config.json>" -OutDir "<claim folder>"
```
Python + openpyxl + LibreOffice:
```
python scripts/build_certificate.py --template <335 R6 .xlsm> --config <config.json> --outdir <claim folder>
python3 scripts/validate_xlsx.py --repair <certificate>.xlsm && python3 scripts/validate_xlsx.py --check <certificate>.xlsm
```
Both print a JSON report; it must show `"PASS": true`. On the Python path `--check` must also print
CLEAN. Add `-Pdf` / `--pdf` only for a certificate already signed off.

## Roll-forward in one line (Form 335 R6)
Column E (prev claimed) := the prior certificate's claimed to date (G on R6, I on R5 and earlier);
column G := this claim's certified-to-date; H = G − E. Variations: column C = the CAR approved
value. The certificate's previous net (`02!F27`) = the prior certificate's net ex GST.

## Files
- `SKILL.md` — triggers, workflow, guardrails.
- `scripts/build_certificate.ps1` — Excel COM builder (ASCII-only).
- `scripts/build_certificate.py` — Python builder.
- `scripts/validate_xlsx.py` — Excel-strict calcChain check and repair (Python path).
- `references/template_map.md` — Form 335 R6 and 335a R1 cell maps.
- `references/config_schema.md` — config fields and worked example.
- `CHANGELOG.md` — revision history.

## Scope / limits
- Head-contract progress certificates.
- Held for Senior QS / Director sign-off; never issued by the skill. No DRAFT marking.
- Up to 32 trade lines, 7 provisional sums, 8 variations and 21 cashflow months — beyond that the
  template needs extending, and the builders abort and say so.
