# bdm-invoice-filing

Sweeps the mailbox for project invoices and files them into the project folder under
the BDM convention, with an audit log. **Files and logs only** — it never assesses,
approves, or registers anything.

Built August 2026 from a Director request to make invoice capture a standard company
procedure rather than a per-PM habit.

## What you get

| Output | Detail |
|---|---|
| **Filed invoices** | Copied to `02_Project Control\1.0_Project Invoices\NN_Mon YYYY\` as `yyyymmdd_Company_InvoiceNo.pdf` |
| **Sync log** | `00_ai_sandbox\Invoice_Sync_Log.md` — every file, skip and quarantine, appended never overwritten |
| **Quarantine queue** | Anything it can't place with confidence, held in the operator's personal folder for human review |
| **Run summary** | Chat summary led by the quarantine count |

## The three things that make it safe

**It never guesses.** An attachment is an invoice only where it carries a number, a
total and an issuer. Anything ambiguous is quarantined, not filed. A sweep putting more
than 20% of items in quarantine stops on the basis that the detection is wrong.

**It never double-files.** Before writing, the whole project folder is searched for the
invoice number. Matching is on issuer plus number — never on amount, because consultants
bill equal monthly tranches and equal amounts are not duplicates. This is what makes the
sweep safe to run daily and safe when two PMs are copied on the same invoice.

**It never touches the payment chain.** The consultant fee register, monthly cost report,
Contract Admin Register and project summaries are all off-limits, as is any accounts
folder reconciled by `progress-claim-update`. Everton Park, the only project carrying
that structure, is excluded outright by Director ruling.

## Why filing is separate from registering

An invoice arriving in a folder is a filing act. An invoice entering the fee register is
a commercial act — it asserts the invoice is valid, within the agreement, and payable.
Collapsing the two would mean an automated sweep quietly making commercial assertions
nobody reviewed. `monthly-cost-report` does the registering, after a human audit against
the consultancy agreement. This skill only puts the document where that audit can find it.

## What's in the package

```
SKILL.md                              scope, exclusions, conventions, rails
README.md                             this file
INSTALL.md                            install and first-run steps
CHANGELOG.md                          revision history
references/folder-and-naming.md       the folder standard, month numbering and migration state
```

## Companion procedure

`Form 060 — Invoice Filing Procedure` in `BDM TEMPLATES` is the staff-facing document.
The skill is the execution; the procedure is the governance. Keep them in step.
