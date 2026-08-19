---
name: monthly-cost-report
description: Produce the BDM Monthly Cost Report — the consultant fee register (Form 201) rolled forward for the period. Sweeps every email and the job folder since the last report for new invoices, fee proposals and executed consultancy agreements; audits each invoice against its agreement BEFORE anything is entered; then updates the register as a DRAFT .xlsx. Trigger on "monthly cost report", "update/roll forward/prepare the cost report", "cost report for [project]", "update the fee register", "consultant fee register", "Form 201", "add [consultant]'s invoice to the register", "what have we been invoiced", or "reconcile consultant fees". Use it even when the user says "update the register" or names one invoice — a cost report is always a full-period sweep, never a single-line edit. NOT the Monthly Project Report (bdm-monthly-project-report), NOT the head contract progress claim (progress-claim-update), NOT QS lender reports (Forms 424/425) or Progress Certificates (Form 335).
---

# Monthly Cost Report

The Monthly Cost Report is the consultant fee register (Form 201) rolled forward one period. It is
how BDM answers two questions for the Principal: **what have we committed?** and **what have we
been billed?** — and, critically, **is what we've been billed what we agreed to pay?**

That third question is the reason this skill exists. A register that faithfully copies invoice
totals into cells is a transcription exercise; anyone can do that. The value is in catching the
claim that runs ahead of the agreement — a stage claimed at 100% that isn't complete, a
disbursement nobody approved, a consultant billing for scope that was omitted last month, a
percentage that doesn't match the previous claim. Those are found by reading the invoice against
the agreement, one line at a time, **before** a single number goes into the register.

## What you are producing

A **DRAFT .xlsx** — the register updated for the period, held for Director sign-off.

Never export a PDF of it. A PDF signals the document is final and issuable, and this document is
neither until Andrew or the Senior PM says so. Hand back the editable workbook only, even if a
PDF would be convenient. This holds for any interim or "for information" copy too.

## Workflow

### 1. Establish the baseline — which file, which period

Two things decide everything downstream: **which register you build on**, and **what date you
sweep from**.

Look in `{project}\05_Consultants\04_Monthly Cost Report\` for period folders named
`NN_{Month} YYYY`. The highest-numbered folder holds the last issued report. Read it and note:
- the register's own "as at" date (cell A3 on both visible sheets)
- what was already recorded as invoiced, per line
- the period covered

**Build on the most recent register file, not a fresh template.** The user edits these — print
scale, fit-to-page, print title rows, horizontal centring, margins, manual page breaks, the notes
block layout. A rebuild from the template silently discards all of it and the user has to redo
the work. If the user has just handed you a file, that file is the base. If they haven't, the
newest register in the newest period folder is the base.

Only build from the controlled template when there is **no** prior register — a project's first
cost report. Then take the highest revision of `201-Consultant_Fee_Register_R*.xlsx` from
`Standard - Documents\BDM TEMPLATES\Working Copy\200 Project Management - Pre-Contract\`.
See `references/register-mechanics.md` for the block structure.

**Sweep from the last report's date**, not from the start of the project. If you can't establish
it, say so and ask rather than guessing a window — a wrong start date silently drops invoices.

### 2. Sweep for everything new

Three passes. Run them all — each catches things the others miss.

**Pass A — the job folder.** Walk the whole project tree, filtered to files modified since the
last report. You are looking for:
- `05_Consultants\04_Monthly Cost Report\_Invoices\` — filed consultant invoices
- `05_Consultants\02_ Fee Proposals\` — new or superseded fee proposals
- `05_Consultants\03_ Consultant Agreements\` — newly executed agreements (often in
  per-discipline subfolders)
- `02_Project Control\` — the BDM fee proposal and any BDM invoices
- anywhere else an invoice may have landed — do a filename sweep for `*invoice*` and `*INV-*`,
  because invoices get saved in the wrong folder routinely

**Pass B — the project email folder.** `00_Email Communication\` holds `.msg` files named
`yyyy-mm-dd_hhmmss_Sender_Subject`. Filter by the date prefix. Read the bodies of anything that
looks like an invoice, a fee proposal, a signed agreement, a Docusign completion, or a scope
change. Docusign "Completed" emails are how you confirm execution; "Viewed" is not execution.

**Pass C — Outlook.** The job folder is always behind the mailbox. Search Outlook directly:
- by **project reference** — the exact string used in invoice subjects, with the right dash
  character (an en-dash in an address will not match a hyphen)
- by **consultant sender domain**, not by keyword — keyword search is too noisy
- for **BDM's own invoices**, which are the ones most often missing from the folder

`references/invoice-sweep.md` has the full method for finding BDM's own Xero invoices, which
behave differently from consultants' and are easy to miss entirely.

Assemble a candidate list before you evaluate anything. Then state plainly what you found and,
just as importantly, what you looked for and did **not** find — "no other consultant has
invoiced" is a finding, and only means something if you say where you looked.

### 3. Audit each invoice against its agreement — before populating anything

This is the step that must not be skipped or reordered. For every invoice in the candidate list,
find the governing document — the executed consultancy agreement, or where none exists, the fee
proposal the parties are working to — and read the claim against it.

`references/compliance-checks.md` is the full checklist. The core of it:

- **Does the claimed amount exist in the agreement?** Match the line to a stage, a schedule item,
  or an approved variation. A line with no home in the agreement is a flag, not a rounding issue.
- **Does the cumulative claim exceed the stage?** Consultants bill cumulatively against a contract
  sum. Check this claim's "previous claims" against what the register already records — a mismatch
  means either a missed invoice or a re-claim.
- **Is the percentage complete supportable?** A stage claimed at 100% should correspond to a
  deliverable actually received. Check the drawings register, the correspondence, the meeting
  minutes.
- **Is scope claimed that has been omitted or was never engaged?** If a discipline was omitted by
  notice, or a service was listed as "optional / not engaged", it must not appear as a claim.
- **Are disbursements approved and on-terms?** Pass-through costs, admin percentages and
  inspection fees need to trace to a clause or a written instruction.
- **Do the descriptions match the agreement's own wording?** Transposed or renamed line items are
  common and cause the wrong thing to be paid later even when this month's amount is right.
- **GST** — the register runs excluding GST. Proposals frequently quote GST-inclusive figures.
  Convert, and note where you did.

Report the audit **before** the numbers go in, as a short table: invoice, governing document,
what's claimed, whether it accords, and the exception if not. Where a claim doesn't accord,
**do not quietly adjust it** — record what was claimed, flag the exception, and let the Director
decide. Your job is to surface it, not to settle it.

If a governing document can't be found for an invoice, that is itself the finding. Say so.

### 4. Populate the register

Now, and only now, enter the figures. The conventions that make the register readable and
auditable:

**Approved Fee (column D)** is the fee in the executed agreement, or where none is executed, the
consultant's fee proposal. Carry unexecuted and proposal-only amounts so the register shows total
exposure — but flag their status. A register that only shows signed fees understates what the
project will cost.

**Variations / Disbursements (column E)** carries movements against the approved fee. Book an
omission as a **negative variation against the original line**, never by deleting or overwriting
the line — the audit trail is the point. Disbursements go here too.

**Never adjust the Approved Fee to make a claim fit.** If a consultant has out-claimed a stage,
the register should show it: approved fee unchanged, invoiced higher, remaining negative. That
negative is the flag. Raising the approved fee is a fee variation, and a fee variation is the
Director's decision, not yours. This applies to BDM's own fee lines too — arguably most of all.

**Fees Invoiced (columns H and I)** — H is total invoiced to date, I is what was invoiced before
this period. The register computes "this month" from the difference, so getting the split right
matters more than it looks. Decide the period cut-off explicitly and apply it consistently; if
the register's title month and the invoices in it disagree, say so rather than silently picking one.

**Status goes in cell comments, not in the cell text.** Do not append `[SIGNED]`, `[UNEXECUTED]`,
`[NOT APPOINTED]` or similar to descriptions — repeated down a column it becomes unreadable noise
on a client-facing document. Instead:
- comment on the **Consultant** cell of each block for engagement status: agreement reference,
  execution state, insurance issues, lapsed validity
- comment on a **Stage** cell only where that line has its own qualification: omitted, claimed,
  not quoted, hourly, a disbursement

Keep descriptions clean and use the consultant's own wording from the agreement.

**Notes** at the foot of the breakdown carry the period's narrative — what changed, what's
outstanding, what needs a decision. This is where the audit exceptions live in the document
itself, so a reader who never sees your chat message still finds them.

`references/register-mechanics.md` covers the sheet structure, formulas, and the openpyxl traps
that will silently corrupt the file if you don't know them. Read it before writing to the workbook
— two of those traps produce a file that looks perfect and is wrong.

### 5. Verify before you hand it back

Run `scripts/verify_register.py` against the output and the base file. It checks the things that
have actually gone wrong in practice: block subtotals reconciling to the grand total, the invoiced
columns adding up, print settings preserved against the base, the header logo intact and its
relationships resolving, comments present, and no leftover bracketed status text.

Then run `scripts/validate_xlsx.py --repair` followed by `--check` on the saved register. This
catches what `verify_register.py` cannot see: a **stale `xl/calcChain.xml`**. calcChain is a
precomputed index naming every formula cell, and rolling the register forward turns formula cells
into values constantly — Excel walks the index on open, finds entries with no formula, and reports
the file as corrupt. **openpyxl ignores calcChain and LibreOffice rebuilds it silently**, so the
register can pass every other check and still be dead in Excel. `--check` must print CLEAN.

Then sanity-check the story: does the movement since last period equal the invoices you found?
If not, find out why before sending.

### 6. Deliver

- Save to `05_Consultants\04_Monthly Cost Report\NN_{Month} YYYY\` as
  `yyyymmdd_{Project}_Consultant Fee Register_{Month YYYY}.xlsx`
- File any invoice you obtained into `_Invoices\` as `yyyymmdd_Company_invoice-number.pdf`,
  dated from the invoice itself, not the email
- Supersede cleanly — one live version per period
- Report: what changed, the audit exceptions, what's still outstanding, and what needs a decision

Lead your write-up with the exceptions, not the totals. The Director can read a total off the
spreadsheet; what they need from you is the thing they'd otherwise miss.

## Judgement calls worth getting right

**Inference vs. fact.** You will often have an amount but not the line detail — a Xero reminder
without the PDF, an invoice whose stage allocation you're deducing from the amount. Enter it, but
say in the comment and in your report that the allocation is inferred and name what would confirm
it. Never present an inference as read-from-source.

**Consultants engaged before BDM.** Fee proposals issued to the Principal or via the architect
before BDM's appointment are common. They belong in the register — the cost is real — but they sit
on nobody's agreement and their validity periods have usually lapsed. Carry them, flag them, and
recommend they be confirmed in writing before they're relied on.

**Scope that's quoted only partly.** A consultant who has priced concept design only is not a
consultant with a small fee; they're an open commitment. Show the unquoted phases as a line with
no fee and a comment, so the gap is visible rather than implied by absence.

**Nil findings are findings.** "No other consultant has invoiced this period" is worth stating,
with where you checked.

## Bundled resources

- `references/register-mechanics.md` — Form 201 sheet structure, block layout, formulas, and the
  openpyxl failure modes. Read before editing any register workbook.
- `references/compliance-checks.md` — the full invoice-vs-agreement audit checklist with the
  exception patterns seen in practice.
- `references/invoice-sweep.md` — how to find every invoice, including BDM's own Xero invoices.
- `scripts/fix_header_logo.py` — re-injects the header logo that openpyxl strips on every save.
  Run after any save. Not optional; the logo vanishes silently otherwise.
- `scripts/verify_register.py` — the pre-delivery *content* check.
- `scripts/validate_xlsx.py` — the pre-delivery *file integrity* check. Run `--repair` then
  `--check` on every saved register. Catches the stale calcChain that makes Excel call the file
  corrupt and that openpyxl and LibreOffice both miss. Not optional.
