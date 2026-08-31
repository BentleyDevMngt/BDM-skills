---
name: bdm-invoice-filing
description: "Sweep the mailbox for project invoices and file them into the project's 02_Project Control\\1.0_Project Invoices\\NN_Mon YYYY folder under the BDM naming convention, with a sync log. Trigger on 'file the invoices', 'invoice sweep', 'run the invoice filing', 'file today's invoices', or as the daily scheduled invoice run. Files and logs only — never assesses, approves or registers. Never writes to the consultant fee register (Form 201), the monthly cost report or the Contract Admin Register, and never touches an accounts folder read by the progress claim. Everton Park is excluded by Director ruling. NOT for building the cost report (monthly-cost-report), the head contract progress claim (progress-claim-update) or progress certificates (Form 335)."
---

# BDM Invoice Filing

Sweep the mailbox for project invoices, file each one into its project folder under the BDM
convention, and log every action. **File and log only.** This skill never assesses, approves,
or registers an invoice — those stay a human judgement pass.

---

## 1. Scope — whose projects

Run only over the projects the operator is responsible for.

Read the operator's `CLAUDE.local.md` in `Projects - Documents\` and take the **Active projects**
list. That list is the sweep scope. If it is missing or looks stale (>60 days since edit), **stop
and ask** — do not default to the whole portfolio. Filing into another PM's project is the single
most damaging failure mode this skill has, because the shared SharePoint library means every PM
sees the result.

If two PMs are both cc'd on the same invoice, both runs will find it. Section 7 (idempotency)
is what stops it being filed twice.

---

## 2. Excluded projects — check before every run

### 202415_South Pine Rd, Everton Park — excluded entirely

**Director ruling, 30 August 2026.** Everton Park is the only project carrying an `01a_Accounts`
head-contract payment chain, where invoices move through `1.0 Received` → `2.0 Approved` →
`3.0 Paid` → `4.0 Remittance` month folders and are reconciled line-for-line against a Xero
account-transactions export by `progress-claim-update`.

Filing a second copy of those invoices into `1.0_Project Invoices` would create a parallel set
of the same documents outside the reconciled chain — the exact condition that makes a progress
claim unauditable. Everton Park invoices continue to be handled manually through the existing
accounts workflow.

**Skip the project entirely.** Do not file, do not quarantine, do not write a sync log entry
against it. Note it once in the run summary as `EXCLUDED — Everton Park (Director ruling)` so the
exclusion stays visible rather than being quietly forgotten.

If any other project acquires an `01a_Accounts` folder or a month-folder accounts structure,
**stop and ask** before sweeping it. The same reasoning will apply, but the ruling is the
Director's to make, not this skill's.

---

## 3. What counts as an invoice

**In scope — all project invoices:**

| Type | Typical sender |
|---|---|
| Consultant fees | architect, structural/civil/services engineers, planner, surveyor, certifier, town planner |
| Contractor / construction | head contractor, subcontractors, trades, early works |
| Authority & statutory | Energex, NBN, Council, Urban Utilities, QLeave |
| Supplier / hire | plant hire, traffic control, crane hire, skip bins |
| BDM's own fee invoices | outgoing to the Principal — file, but tag `[BDM-OUT]` in the log (receivable, not payable) |

**Out of scope — do not file:**

- Remittance advices, statements of account, and payment confirmations (these are not invoices)
- Overdue notices and reminders that merely re-attach an invoice already on file
- Quotes, fee proposals, and rate schedules → these belong in `Fee Proposals`, not here
- Anything for a project not in the operator's active list, or for an excluded project (§2)
- Personal, office-overhead, or non-project invoices

**Detection.** An attachment is an invoice when it carries an invoice number **and** a total
amount **and** an issuer. Subject-line keywords alone are not enough — the mailbox is full of
threads *discussing* invoices. Xero notifications (`messaging-service@post.xero.com`) are a
reliable positive; treat them as first-class.

---

## 4. Where it goes

```
<project>\02_Project Control\1.0_Project Invoices\NN_Mon YYYY\
```

`1.0_Project Invoices` is the standard — it is what the `_ New Job Folder` master template
carries. Some legacy projects still have a plain `Invoices` folder. **Do not create the
`1.0_` folder alongside a legacy `Invoices` folder** — that leaves two live destinations.
If only `Invoices` exists, stop for that project and flag it as awaiting migration.

### Month folder numbering — read before creating

The month folder is a **continuous running sequence from project start**, not a per-year reset.
The established BDM pattern is `30_Jan 2025`, `31_Feb 2025` … `40_Nov 2025`.

To pick `NN`:

1. Look in `1.0_Project Invoices` for the highest existing `NN`. Continue from it.
2. If empty, look at `05_Consultants\04_Monthly Invoices` in the same project and continue that
   project's sequence, so the two registers read consistently.
3. If neither exists, start at `01`.
4. Never renumber an existing folder.

**Month token — pin these exact three letters** (existing folders are inconsistent: `Sept`,
`June`, `March` all appear — do not copy them):

`Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec`

The month is the **invoice issue month**, not the month the email arrived. An invoice dated
28 Aug that lands on 2 Sep files under August.

---

## 5. Filename convention

```
yyyymmdd_Company_InvoiceNo.pdf
```

- **`yyyymmdd`** — the invoice **issue date** off the face of the invoice. Not the email date,
  not the due date. Eight digits.
- **`Company`** — the issuer's short name, no spaces (`JHA`, `BDA`, `Energex`, `ZonePlanning`).
  Reuse the short name already used elsewhere in that project's folders; consistency across a
  project matters more than a global list.
- **`InvoiceNo`** — **exactly as issued.** Do not force an `INV` prefix. Real numbers in this
  mailbox include `INV-1485`, `71456`, `JB018010`, `G22068-DD16`, `3056`, `300250962`. If the
  issuer writes `INV-1485`, the filename says `INV-1485`. If they write `71456`, it says `71456`.

Examples:

```
20260812_JHA_INV-1485.pdf
20260731_Energex_300250962.pdf
20260805_LeadDesign_INV-1220.pdf
```

If an invoice genuinely has no number, use `NoNum` and flag it in the log for a human to resolve.
Never invent one.

---

## 6. Hard rails

**Never:**

- Sweep an excluded project (§2).
- Delete, move, or mark-read the source email. Save a **copy** of the attachment.
- Move or copy anything **out of** `01a_Accounts` or any `NN_Month YYYY` accounts folder with
  `1.0 Received` / `2.0 Approved` / `3.0 Paid` / `4.0 Remittance` subfolders.
- Write to the consultant fee register (Form 201), the monthly cost report, the Contract Admin
  Register, or any project summary. Those are separate, judgement-bearing passes.
- Rename or reorganise files already filed by a human.
- Guess the project. Confidence below certain → quarantine.
- Overwrite an existing file. If the target name exists and the content differs, append `_b`,
  `_c` and flag it.

**Always:**

- Preserve the original PDF byte-for-byte. Rename on copy only; never re-render or re-compress.
- Write the log entry **after** the file lands, so the log reflects reality.

---

## 7. Idempotency — the duplicate guard

Before writing any file, search the **whole project folder** (not just the target month) for the
invoice number. If a file already carries that number from that issuer, do not write a second
copy. Log it as `SKIPPED — already on file at <path>`.

This is what makes the sweep safe to run daily, safe to re-run after a failure, and safe when two
PMs are cc'd on the same invoice. Match on **issuer + invoice number** — never on amount.
Equal dollar amounts are not duplicates; consultants bill equal monthly tranches routinely.

---

## 8. Quarantine

Anything that looks like an invoice but cannot be confidently placed goes to:

```
<operator's personal folder>\_Invoice_Quarantine\
```

filed as `yyyymmdd_Sender_Subject.pdf`, with a line in the run log saying why. Quarantine, not
guesswork, for:

- Project can't be identified, or matches two projects
- Invoice date or number unreadable
- Multi-project invoice covering several jobs on one document
- Project has only a legacy `Invoices` folder (awaiting migration)
- Scanned image with no extractable text

An invoice for an **excluded** project is not quarantined — it is left alone entirely (§2).

Quarantine is a queue for a human, so it must be reviewed. Report its depth in every run summary.

---

## 9. The sync log

Append to `<project>\00_ai_sandbox\Invoice_Sync_Log.md` — one section per run, plain text,
never overwritten:

```markdown
## Run 2026-08-30 06:00 — operator: Andrew Bentley

| Action | Invoice | Issuer | Filed to | Note |
|---|---|---|---|---|
| FILED | INV-1485 | JHA | 47_Aug 2026/20260812_JHA_INV-1485.pdf | |
| SKIPPED | INV-1220 | LeadDesign | 46_Jul 2026/… | already on file |
| QUARANTINED | 71456 | Cassandra Foreman | _Invoice_Quarantine | project ambiguous |

Filed 1 · Skipped 1 · Quarantined 1
```

Same audit pattern as `CAR_Sync_Log.md`. If a project has no `00_ai_sandbox`, flag it rather
than creating one.

---

## 10. Run summary

Finish with a short chat summary — not a file:

- Filed: N (grouped by project)
- Skipped as duplicates: N
- **Quarantined: N — needs your eyes**
- Projects flagged for folder migration: N
- Excluded: Everton Park (Director ruling)

Lead with the quarantine count. That is the only part needing a human, and it is the part that
silently grows if nobody looks.

---

## 11. Stop and ask

Stop rather than proceed when:

- The operator's active-project list is missing or stale
- More than 20% of the sweep lands in quarantine (the detection or scope is wrong)
- An invoice appears to relate to a project outside the operator's list
- A project not currently excluded is found to hold an `01a_Accounts` or month-folder accounts
  structure
- A target month folder would need renumbering to fit

Filing is cheap to redo and expensive to unpick across a shared library. When in doubt, quarantine
and report.
