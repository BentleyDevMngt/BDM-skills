# bdm-drawing-report-filing

Sweeps the mailbox for drawings, specifications and consultant reports, files each issue into
the project's `06_Drawings & Specifications` discipline folder, and keeps the project's
**Form 207 document register** current: one row per document, latest revision in CURRENT ISSUE.
**Files, registers and logs only** — it never issues a transmittal and never sends anything.

Library name **BDM-Drawing-Report-Filing R1.0 · 2026-10**. Built October 2026 from a Director
request to extend the daily Drawing & Report Filing scheduled task so that the register is
updated on every receipt.

## What you get

| Output | Detail |
|---|---|
| **Filed issues** | `06_Drawings & Specifications\<discipline>\yyyymmdd_<Issue name>\`, originals byte-for-byte |
| **Document register** | `06_Drawings & Specifications\00_Register\yyyymmdd_<Project>_Document Register.xlsx` (Form 207), superseded copies in `_SS` |
| **Sync log** | `00_ai_sandbox\Drawing_Sync_Log.md`, appended never overwritten |
| **Project summary** | §13 Drawings register updated in the same pass |
| **Quarantine** | Anything it cannot place, held in the operator's folder for review |
| **Run summary** | Chat summary led by what needs a person |

## What makes it safe

**One route into the register.** Every write goes through `scripts/register_207.py`. It reads
the register into a data model, applies the issue, and re-renders the sheet from it. It never
overwrites its input, refuses to write when the register disagrees with an incoming revision,
and validates the result before it replaces the live copy.

**It never double-files.** Matching is on consultant, sheet number, revision and issue date,
never on filename, because consultants re-send sets under new names. Safe to run daily.

**It never deletes.** Superseded registers and fully superseded issue folders move to `_SS`.
Folders a person filed are listed, not moved.

**It never guesses.** Unreadable revisions, ambiguous projects and register conflicts are
quarantined for a person.

## What's in the package

```
SKILL.md                              scope, conventions, procedure, rails
README.md                             this file
INSTALL.md                            install and first-run steps
CHANGELOG.md                          revision history
references/folder-and-register.md     discipline map, folder survey, register conventions
scripts/register_207.py               read / new / apply / validate the Form 207 register
```

## Template

Form 207 Document Transmittal, resolved at run time from `BDM TEMPLATES\Working Copy\200 Project
Management - Pre-Contract\` (latest revision). Verified against **R1 (2026-08)**.
