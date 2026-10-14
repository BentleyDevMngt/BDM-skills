# CHANGELOG — Drawing & Report Filing Skill

## R1 / October 2026 — first issue

Built from a Director request (14 October 2026) to extend the daily Drawing & Report Filing
scheduled task, which already filed drawing attachments into dated issue folders and marked the
email orange, so that the project document register is updated on every receipt.

### Rulings it rests on

- **Form 207 is the master record of documents received** (Director, 14 Oct 2026). Form 325 was
  reviewed and found too thin for the purpose. It has no issue history, no consultant, a fixed
  number of rows per discipline, and stale project data left in the controlled template.
- **One row per document, current revision kept up to date** (Director, 14 Oct 2026).
- **Placement in `bdm-project-delivery`**, alongside `bdm-invoice-filing`, consistent with the
  31 Aug 2026 ruling that filing project correspondence into the job folder is delivery
  record-keeping.

### What went into it

- **Originals from the archived `.msg` files**, not the mail connector. The connector cannot
  download attachments, as the invoice task found.
- **A register script** (`register_207.py`) that re-renders the sheet from a data model.
  - Hand-inserting rows and columns is what corrupts registers.
  - Tested on the blank Form 207 R1 and on the live 187-189 Jefferson Lane transmittal, whose
    18 date columns are full.
  - Tested for new, update, older-issue, idempotent re-run, conflict refusal and roll-over.
  - Output reopens cleanly and every XML part parses. It has not been opened in Excel itself.
- **Roll-over at 18 issue dates.** The oldest date column drops off and its history stays in
  the `_SS` copies. This departs from Form 207 note 2 ("do not overwrite an existing column").
  It was chosen because adding columns breaks the one-page-wide print within months.
- **Current issue by date, never by label.**
- **Reports on the same register**, as rows in their discipline band, as the Jefferson Lane
  register already does.
- **`_SS` supersession** for registers always, and for fully superseded issue folders this skill
  filed. Folders a person filed are only listed.

### Known open items at issue

- Form 207 is worded for outgoing transmittals: "ISSUED TO", "REASON FOR ISSUE", the DISTRIBUTION
  block, and note 2. A Form 207 R2 with register wording would remove the workarounds in SKILL.md
  §1. That is a template Change Note, not this skill's to make.
- Form 207 R1 carries no BDM logo in its header.
- Back-capture of existing drawings is by hand-run seeding only (§13).
- Whether "Orange Category" is the exact name of the existing Outlook category is to be confirmed
  on the first live run.
