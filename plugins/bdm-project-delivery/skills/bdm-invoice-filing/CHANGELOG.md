# CHANGELOG — Invoice Filing Skill

## R2 / October 2026 — scanned PDFs

Folded in from the Director's personal copy of the skill ahead of the move to the BDM Team
workspace (27 October 2026), so the plugin is the single controlled copy.

- **Scanned PDFs are filed, not quarantined.** A PDF with no text layer is read as an image
  (page 1, or later pages if page 1 is a cover sheet) and filed byte-for-byte like any other
  invoice. Multi-page scans are never split.
- **Quarantine reason narrowed** from "no extractable text" to "unreadable even when viewed
  as an image".

## R1 / August 2026 — first issue

Built from a Director request (30 August 2026) to turn ad-hoc invoice capture into a
standard company procedure that could be shared across staff.

### What went into it

- **The folder standard, resolved from the folders themselves.** The portfolio carried
  two competing names — `Invoices` on 24 projects, `1.0_Project Invoices` on 9. The
  `_ New Job Folder` master template carries `1.0_Project Invoices`, which settled it as
  the forward standard and made the other 24 a migration list rather than a choice.
- **Continuous month numbering.** The brief proposed `01_Aug 2026`. The established
  pattern in `05_Consultants\04_Monthly Invoices` is a continuous sequence from project
  start (`30_Jan 2025` … `40_Nov 2025`), so the skill continues each project's existing
  sequence rather than resetting. Month tokens are pinned to three letters because
  existing folders carry `Sept`, `June` and `March` inconsistently.
- **Invoice numbers recorded as issued.** The brief proposed an `INV'n'` element. Actual
  numbers in the mailbox include `INV-1485`, `71456`, `JB018010`, `G22068-DD16`, `3056`
  and `300250962`. No prefix is forced and no number is ever invented.
- **Idempotency on issuer plus number, never amount.** Consultants bill equal monthly
  tranches; equal amounts are not duplicates. This carries forward the amount-matching
  lesson from the progress claim work.
- **The Everton Park exclusion.** Director ruling, 30 August 2026 — see below.
- **Quarantine over guesswork,** with a 20% stop threshold on the basis that a sweep
  filling the quarantine has the wrong detection or the wrong scope.
- **The register boundary.** Filing is a filing act; registering asserts an invoice is
  valid and payable. The skill files and logs, and writes to no register.

### Everton Park — excluded

`202415_South Pine Rd, Everton Park` is the only project holding an `01a_Accounts`
head-contract payment chain, reconciled line-for-line against a Xero account-transactions
export by `progress-claim-update`. A second copy of those invoices filed outside the
reconciled chain is the condition that makes a claim unauditable. The project is skipped
entirely — not filed, not quarantined, not logged — and named in each run summary so the
exclusion stays visible.

Any other project that acquires the same structure triggers a stop-and-ask rather than an
automatic exclusion. The reasoning generalises; the ruling does not.

### Known open items at issue

- Whether historical invoices already filed under `05_Consultants\04_Monthly Invoices` are
  back-captured, or the standard applies forward only.
- Whether BDM's own outgoing fee invoices belong in this folder, being receivables.
- Confirmation of the month-folder starting number per project at go-live.
- The 24-project folder migration is listed but not executed.
