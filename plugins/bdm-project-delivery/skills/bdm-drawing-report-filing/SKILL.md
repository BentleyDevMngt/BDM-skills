---
name: bdm-drawing-report-filing
description: "Sweep the mailbox for drawings, specifications and consultant reports issued on a project, file them into the project's 06_Drawings & Specifications discipline folder as a dated issue folder, and update that project's Form 207 document register — one row per document, current revision kept up to date — with a sync log. Trigger on 'file the drawings', 'drawing sweep', 'run the drawing and report filing', 'update the drawing register', 'update the document register', 'log this drawing issue', 'seed the register for [project]', or as the daily scheduled Drawing & Report Filing run. Files, registers and logs only — never issues a transmittal, never sends, never deletes. NOT for invoices (bdm-invoice-filing), issuing drawings to tenderers (bdm-tender-clarification), issuing a transmittal to a recipient, or meeting minutes."
type: process
template_revision: R1
template_source: 207-Document_Transmittal_R{latest}_{YYYY-MM}.xlsx (Working Copy / 200 Project Management - Pre-Contract)
issued: 2026-10
maintained_by: BDM Standards Agent
related_skills: bdm-invoice-filing, bdm-project-sandbox-setup
---

# BDM Drawing & Report Filing

**Revision: R1.0 · 2026-10** — skill revisions carry one decimal place: a scope change raises the whole number, a correction or refinement raises the decimal. The release history is in this skill's CHANGELOG (where it has one) and the repository CHANGELOG.

Find drawings and reports that consultants have issued, file each issue into its project's
`06_Drawings & Specifications` folder, and keep that project's **Form 207 document register**
current. **File, register and log only.** This skill never issues a transmittal, never sends
anything, never deletes and never overwrites.

Library name: **BDM-Drawing-Report-Filing R1.0 · 2026-10.**

---

## 1. The register — Form 207 as the master record of documents received

Director ruling, 14 October 2026: **Form 207 is the master record of information received**
on every project. Form 325 is not used for this.

- **One row per document.** A drawing, specification or report has exactly one row, in its
  discipline band. A new revision updates that row; it never adds a second one.
- **CURRENT ISSUE** (column U) is the revision on the **latest-dated** issue. Decide by date,
  never by comparing labels — `P3 → A`, `13W → 17` and `01 → C` all occur in practice.
- **The date grid** (columns C–T) records which revision arrived on which issue date. It holds
  18 issue dates. When a 19th arrives, the oldest date column drops off the live sheet. Its
  history survives in the superseded copies in `_SS` (§8).
- **STATUS** (column V) records the issue status stamped on the document — `FOR CONSTRUCTION`,
  `TENDER`, `DA`, `PRELIMINARY`, `WIP`, `FOR INFORMATION`, or `-` where none is shown.
  Anything WIP, PRELIMINARY or NOT FOR CONSTRUCTION must show it here (Form 207 note 3).
- **Revisions come from the title block, never the filename** (Form 207 note 4). Where the two
  disagree, the title block governs and the discrepancy goes in the sync log.
- **Reports go on the same register**, as rows in their discipline band — a geotechnical report
  under GEOTECHNICAL, a NatHERS assessment under ENERGY EFFICIENCY, a stormwater management plan
  under CIVIL. SHEET carries the document number. Where the report has none, use the consultant's
  job number plus a short code (`PG-13630`, `25-648`), and say so in the log.

**Where it lives:**

```
<project>\06_Drawings & Specifications\00_Register\yyyymmdd_<Project>_Document Register.xlsx
<project>\06_Drawings & Specifications\00_Register\_SS\   <- every superseded copy
```

`<Project>` is the project folder name without its number (`New Earth Health Club`). The date
is the date of the run that wrote it. Exactly one live register sits in `00_Register`; every
earlier one is in `_SS`.

**Header fields** of a register, set when it is created:

| Field | Value |
|---|---|
| CLIENT / PROJECT / ADDRESS / PROJECT NO. | From the project summary (`00_ai_sandbox\Project_Summary_*.md`) |
| ISSUED TO | `Register of documents received — BDM internal` |
| STATUS | `Live register` |
| TRANSMITTAL NO. | `REGISTER` |
| DATE | Date of the run that wrote it, updated every write |
| REASON FOR ISSUE | `Master record of documents received` |
| PREPARED BY | `Bentley Development Management` |
| DISTRIBUTION rows | Recipient 1: `Not applicable — register of documents received`; the others blank |

An issued transmittal (for example `00_Transmittals\..._TX-001.xlsx`) is an issued document, not
the register. Never adopt one as the register, and never write to one.

---

## 2. Scope — which projects

The scope is whatever the caller gives: the scheduled task prompt names it. Run by hand, the
scope is the **Active projects** list in the operator's `CLAUDE.local.md` in `Projects - Documents\`.
If neither exists, **stop and ask**.

Never sweep `_Projects Archived`, `_Project Opportunities` or `_ New Job Folder`.

There is **no Everton Park exclusion** here. That ruling protects the progress claim's payment
chain and has nothing to do with drawings.

---

## 3. Getting the original files

The Microsoft 365 connector can find and read emails, but it **cannot download attachments**.
Never file from connector text. The originals come from the archived emails: each project's
`00_Email Communication\` holds every email as a `.msg` file named
`yyyy-mm-dd_hhmmss_Sender_Subject.msg`. These are the byte-for-byte source.

1. **Install the reader** on the linked computer at the start of every run (the shell does not
   persist): `pip install --break-system-packages -q extract-msg olefile openpyxl`. Then check
   `which pdftotext pdftoppm tesseract`. If the install fails, stop and notify — file nothing.
2. **Find candidates.** Search Outlook for mail since the last run. The last run is the most recent
   `## Run` heading in any project's `00_ai_sandbox\Drawing_Sync_Log.md`, and the search goes back
   one extra day; §7 makes the overlap safe. Look for drawing, transmittal, issue, revision, report,
   specification, consultants' domains, and attachments named like sheet numbers. Then scan each
   in-scope project's `.msg` files dated since then with `extract_msg`.
3. **Cloud-only files.** A `.msg` that fails with `[Errno 22] Invalid argument` is a OneDrive
   placeholder. Stage it with `device_stage_files` on its Windows path to download it, then read it.
   Do the same for a register or sync log that fails this way. Stage only what you need.
4. **Not archived yet.** An email with no matching `.msg` is listed as `awaiting archive` and left
   un-categorised, so the next run picks it up.
5. **Download links** (Aconex, Dropbox, WeTransfer, SharePoint) cannot be fetched from here. Log
   them as `link only — needs manual download`, with the link, and leave the email un-categorised.

Write files from the attachment bytes directly. Never re-render or re-compress a PDF. Check that
the written file's md5 matches the attachment bytes.

---

## 4. What counts

**File and register:**

| Type | Examples |
|---|---|
| Drawings | Architectural, interior, structural, civil, services, landscape, fire sprinkler, shop drawings |
| Specifications | Project specification, finishes schedule, door/window schedules issued as documents |
| Consultant reports | Geotechnical, traffic, acoustic, NatHERS/energy, fire engineering (FER), stormwater management, wind, survey |
| Design certificates | Form 15 / Form 16 issued with a drawing set — a row under that discipline |

**File, but do not register as a row:**

- The consultant's **transmittal** PDF. File it in the issue folder. Use it to cross-check sheet
  numbers and revisions, but the title block governs.
- **CAD files** (`.dwg`, `.rvt`, `.ifc`). File them in the issue folder; the PDF is what gets registered.
- **Zip files.** Keep the zip, and extract its contents into the same issue folder.

**Out of scope — leave alone:** invoices (bdm-invoice-filing), fee proposals, quotes, minutes, RFIs
and their responses, BDM's own markups, BDM's own transmittals, signature images, documents for
another project, and an issue already on file (§7).

**Detection.** A PDF is a drawing when its text carries a sheet number **and** a revision **and**
a title block (project name or consultant). A PDF is a report when it carries a document title,
a consultant, and a revision or issue date. A subject line alone is not enough. If there is no
text layer, OCR page 1:
`pdftoppm -r 200 -png -f 1 -l 1 x.pdf w/x; tesseract w/x-1.png -`. Read the title block from that.

**Multi-sheet PDFs.** One PDF often carries a whole set. Read every page, and register every
sheet it contains.

---

## 5. Where it goes

```
<project>\06_Drawings & Specifications\<discipline folder>\yyyymmdd_<Issue name>\
```

- **Discipline folder.** Use the project's **existing** sub-folder for that discipline. Folder
  names vary between projects (`01_Architecture`, `01_Architecture_ BDA`, `06a_Fire Sprinklers`,
  `02a_Pool Engineering`), and the project's own name wins.
  - If none exists, create the New Job Folder standard name (`references/folder-and-register.md`),
    but only if no near-match exists.
  - If a near-match exists, or the discipline has no standard folder, quarantine and flag.
  - Never create a second folder for a discipline.
- **`yyyymmdd`** is the **consultant's issue date**. Take it from the transmittal, else the title
  block, else the email date. Using the email date is flagged in the log.
- **`<Issue name>`** is short and comes from the consultant's own words: the transmittal's reason
  for issue or the email subject (`DD Issue`, `For Construction`, `Coordination Issue`,
  `Rev C Amendments`). Correct obvious typos; no characters Windows rejects.
- **Same issue arriving twice** (same consultant, same issue date): file into the existing folder.
  Never create `_b`.
- **Filenames are kept as received.** If a name already exists with different content, append `_b`
  and flag it. Never overwrite.

---

## 6. Updating the register

All register writes go through `scripts/register_207.py`. Never edit the sheet any other way,
and never with Excel automation. The script reads the register into a data model, applies the
issue and re-renders every row from it. That is what keeps bands, borders, merges and the print
area right however many rows are added.

1. **Find the live register** in `00_Register`. If there is none:
   - the first receipt creates one from the **latest** Form 207 in `Working Copy\200 Project
     Management - Pre-Contract\` with `register_207.py new <form207.xlsx> <changes.json> <out.xlsx>`;
   - if that template is newer than `template_revision` above, say so in the run summary and ask
     for a check.
2. **Check it is not open.** A `~$` lock file beside the register means someone has it open. Skip
   the register write for that project, file the documents anyway, and flag `register open —
   not updated`. The next run catches up.
3. **Write `changes.json`.** Add one `received` entry per issue, with discipline (the band name in
   capitals, e.g. `ARCHITECTURE`, `STRUCTURAL ENGINEERING`), consultant short name, consultant job
   number, issue date, and one item per sheet: sheet number, title, revision exactly as the title
   block shows, a grid label of 4 characters or fewer where the revision is longer (`REV 17` → `17`),
   and status. The script's docstring shows the format.
   - **On an existing register, reuse its band names exactly.** Run `register_207.py read` first.
     If the register says `STRUCTURAL · EDGE`, write `STRUCTURAL` and `EDGE`. A band is matched on
     discipline **and** consultant, so a different spelling creates a second band.
   - A genuine change of consultant (say a new electrical engineer) does get its own band. The
     old band stays, as the record of what that consultant issued.
4. **Run** `register_207.py apply <live.xlsx> changes.json <new.xlsx>`. The new file is
   `yyyymmdd_<Project>_Document Register.xlsx` with today's date. If one with today's date already
   exists from an earlier run, save as `..._b.xlsx`.
5. **Read the report it prints.**
   - **`conflicts`:** the register already shows a different revision for that sheet on that date.
     The script writes nothing. Flag for a person; never resolve it yourself.
   - **`older_issue`:** an issue older than the current one. It goes in the grid only; CURRENT ISSUE
     is unchanged.
   - **`title_changed`, `dropped_dates`, `new_bands`:** log them.
   - **`validate.problems`:** if this is non-empty, the new file is not used. Leave the old register
     live, move the failed file to the operator's quarantine, and flag it.
6. **Supersede the old register.** Move the previous live file into `00_Register\_SS\`. Move it;
   never delete it.

---

## 7. Idempotency — the duplicate guard

Before filing, check the project's `Drawing_Sync_Log.md` and the register.

- If the same sheet at the same revision on the same issue date is already registered, and the
  file is already in that issue folder, log `SKIPPED — already on file` and do nothing else.
- The script reports these as `already`.

Match on **consultant + sheet number + revision + issue date**. Never on filename alone:
consultants re-send the same set under new filenames.

This is what makes the run safe to repeat daily, safe after a failure, and safe when two PMs are
copied on the same issue.

---

## 8. Superseded files — `_SS`

Superseded material is moved into `_SS`, never left beside the current file and never deleted.

- **Registers:** every superseded register goes to `00_Register\_SS\`, always (§6).
- **Issue folders:** when every sheet in an earlier issue folder now has a later revision on the
  register, that folder is fully superseded.
  - Move it into `<discipline folder>\_SS\` **only if this skill filed it** (it appears in the sync
    log). Use the existing `_SS`, `SS` or `ss` sub-folder if there is one; otherwise create `_SS`.
  - A fully superseded folder filed by a person is listed in the run summary as an `_SS candidate`.
    It is not moved.
  - A partly superseded folder stays where it is. The register shows which sheets in it are current.

---

## 9. Same pass — the project summary and AI_Context

- **Project summary §13 Drawings register.** Update that project's `Project_Summary_*.md`: for each
  discipline touched, set the current issue folder, its date and the register path. Internal and
  reversible work — do it and report it (company `CLAUDE.md` §8). If no summary exists, skip it
  and flag; never create a stub.
- **`AI_Context` staleness.** If `00_ai_sandbox\AI_Context\` holds a converted copy of a sheet that
  has just been superseded, flag it in the log and run summary as `AI_Context stale — re-convert`.
  Re-conversion belongs to `bdm-project-sandbox-setup`, not this skill.

---

## 10. Marking the email

For every email whose attachments were FILED or SKIPPED as already on file, add the Outlook category
**Orange Category** with `outlook_modify_labels`, keeping any existing categories. That is the
visual confirmation that it has been dealt with.

Do not categorise emails that were quarantined, awaiting archive, link only, or out of scope.

---

## 11. Quarantine

Anything that looks like a drawing or report but cannot be placed with confidence goes to:

```
<operator's personal folder>\_Drawing_Quarantine\yyyymmdd_Sender_Subject\
```

with a line in the run summary saying why. Quarantine — never guess — when:

- the project cannot be identified, or more than one project matches;
- the discipline folder is ambiguous (§5);
- the sheet number or revision cannot be read, even after OCR;
- the register shows a conflict (§6);
- the register failed validation.

---

## 12. The sync log

Append to `<project>\00_ai_sandbox\Drawing_Sync_Log.md`. One section per run, never overwritten,
written **after** the files land:

```markdown
## Run 2026-10-15 05:00 — operator: Andrew Bentley — originals from archived .msg

| Action | Consultant | Issue | Sheets | Filed to | Register | Note |
|---|---|---|---|---|---|---|
| FILED | BDA | 20261013_For Construction | A2.201 C, A2.300 A | 01_Architecture/20261013_For Construction | updated | A2.201 was B |
| SKIPPED | Hydro Co | 20260929_Coordination Issue | 2 sheets | — | already | already on file |
| QUARANTINED | Soil Pty | — | — | _Drawing_Quarantine | — | project ambiguous |

Register: 00_Register/20261015_New Earth Health Club_Document Register.xlsx (previous moved to _SS)
Filed 1 · Skipped 1 · Quarantined 1 · Sheets registered 2
```

If a project has no `00_ai_sandbox`, flag it rather than creating one.

---

## 13. Seeding a register (run by hand only, never scheduled)

"Seed the register for <project>" builds the first register from what is already in that project's
`06_Drawings & Specifications`.

- Read every issue folder in date order, and every loose PDF.
- Run them through §6 as if they had just arrived, using each folder's `yyyymmdd` as the issue date.
- Anything with no readable date or revision is listed for a person.
- Seeding moves no files and categorises no email.
- Show the result to the operator before it becomes the live register.

---

## 14. Run summary

Finish with a short summary in chat — not a file. Lead with what needs a person:

- **Quarantined: N — needs your eyes**
- Conflicts on a register: N
- Awaiting archive / link only: N
- Registers not updated because they were open: N
- AI_Context stale: N
- `_SS` candidates (filed by a person): N
- Filed: N issues, N sheets registered (by project)
- Skipped as already on file: N

For a scheduled run, send a push notification only when one of the first six lines is non-zero,
or when the run failed.

---

## 15. Hard rails

**Never:**

- issue, send or forward anything, or fill in a transmittal to a recipient — the register is
  BDM's internal record;
- delete anything — supersede by moving to `_SS`;
- overwrite a file, a register or a sync log entry;
- write to a register by any route other than `register_207.py`;
- write to an issued transmittal, the Contract Admin Register, a fee register or a cost report;
- move or rename files a person filed;
- move, delete or mark-read the source email (adding the category is the only change);
- write into `BDM TEMPLATES` — read the latest Form 207 from it and nothing more;
- guess a project, discipline, sheet number or revision.

**Always:**

- keep originals byte-for-byte;
- write the log after the file lands, so the log reflects what happened.

---

## 16. Stop and ask

Stop rather than proceed when:

- there is no scope (§2);
- more than 20% of the sweep lands in quarantine — the detection or the scope is wrong;
- the Form 207 template cannot be found, or is newer than `template_revision` and nobody has checked it;
- a register fails validation two runs running on the same project;
- the linked computer cannot be reached — file nothing, and notify.

Filing is cheap to redo and expensive to unpick across a shared library. When in doubt,
quarantine and report.
