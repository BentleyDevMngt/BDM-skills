---
name: bdm-project-sandbox-setup
description: >
  Set up a BDM project's AI sandbox — create the `00_ai_sandbox` folder and
  backfill the full 17-section `Project_Summary_<Project>.md` required by the
  company CLAUDE.md §13, from what is actually in the project folder and its
  saved emails — or bring an existing summary up to that standard without
  losing anything. Every figure carries its source; anything not found is marked
  TBC and becomes a "Confirm …" action. Use when a project has no sandbox or no
  project summary, when another skill flags "summary missing", or when the user
  says "set up the sandbox", "create the project summary", "backfill the
  summary", "bring the summary to standard", "add §17", "onboard this
  project", "which projects don't have a sandbox" or "do all my projects".
  Works on one project or sweeps every live job folder. Read-only on project
  documents. NOT for routine updates to a summary (every other skill does that
  as it works), and NOT for converting project documents to markdown
  (AI_Context).
---

# BDM Project Sandbox Setup

**Revision: R2.0 · 2026-10** — skill revisions carry one decimal place: a scope change raises the whole number, a correction or refinement raises the decimal. The release history is in this skill's CHANGELOG (where it has one) and the repository CHANGELOG.

Every project-bound BDM skill starts by reading
`<project>\00_ai_sandbox\Project_Summary_*.md` (company `CLAUDE.md` §8). A
project without one leaves every skill working blind. This skill closes that
gap: it creates the sandbox and writes a complete, sourced summary from the
project folder, so the next skill that runs starts from something true.

It is the **only** skill that creates a project summary. `CLAUDE.md` §8 says
skills must never create a stub — this skill doesn't. It writes all 17 sections
from a real read of the folder and marks what it could not find.

The rules every *other* skill follows when it reads and updates the summary are
in `references/summary-rules.md`.

---

## 1. Rules that don't bend

1. **Read-only on project documents.** The only things this skill writes are the
   `00_ai_sandbox` folder (if missing), the `Project_Summary_*.md` inside it
   and, in §4 only, the backup in `00_ai_sandbox\_SS\` and
   `00_ai_sandbox\Summary_ChangeLog_Archive.md`.
   Never move, rename, copy or delete a project file. Flag misfiled things in
   §16 instead.
2. **No invented facts.** Every date, dollar figure, reference number, firm and
   person comes from a document or email you opened. Put the source path on the
   line. Not found → `TBC — not found in folder`, plus a "Confirm …" action in
   §10.
3. **Don't overwrite — except to bring a summary to standard (§4).** If a
   `Project_Summary_*.md` already exists, set-up leaves it alone and reports
   it; routine updates are every other skill's job. Restructuring an existing
   summary happens only in §4, only when the user asks for it, and only with
   a backup taken first and the completeness check passing.
4. **One sandbox per project.** Match `00_ai_sandbox` case-insensitively
   (`00_AI_sandbox` counts). Never create a second one alongside.
5. **No personal paths in the output.** Write paths relative to the project
   folder. Resolve the user's home at run time; never hard-code a user name.
6. **Internal work.** Creating a sandbox and summary is internal and
   reversible (`CLAUDE.md` §10): do it, then report. No sign-off block, no
   DRAFT marking.
7. **No AI_Context.** This skill does not convert project documents to
   markdown or OCR scans. If a project already has an `AI_Context\` folder,
   record that in §16 and leave it alone.

---

## 2. Locate the projects

Projects root, in this order:

1. A path the user gives.
2. `%USERPROFILE%\BDM\Projects - Documents` (the synced SharePoint library).
3. In a session where folders are mounted: the mounted `Projects - Documents`
   folder. If it isn't connected, ask the user to connect it — one question,
   then wait.

A project folder starts with a 6-digit BDM job number
(`202699_12 Example St, Suburb`). Skip everything else: personal and agent
folders, `_Projects Archived`, `_Project Opportunities`, `_ New Job Folder`.

**Scope.** If the user's own layer lists their active projects, use it.
Otherwise "my projects" / "all projects" means every live job folder at the
root. A project the user says is dormant or archived is skipped unless they
insist.

---

## 3. Workflow

### Step 1 — Status sweep (read-only)

For each job folder: is there a `00_ai_sandbox` (any case), and does it hold a
`Project_Summary_*.md`? Show the user a short table of the projects missing a
sandbox or a summary.

If they named one project, go straight to it. If they asked for "all", confirm
the list once — "Set up these N? (y / pick)" — then go. Don't re-ask per
project.

For each job that already has a summary, grade it in the same table:

| Grade | Test |
|---|---|
| **On standard** | `## 1.` to `## 17.` present once each, in order, and under 60 KB |
| **§17 missing** | `## 1.` to `## 16.` in order, no §17 |
| **Old layout** | its own numbering, sections missing, or a backfill supplement bolted on the end |
| **Oversized** | over 60 KB, whatever its layout — usually a long change log |

Offer §4 for anything not on standard. Don't start it without a yes.

Also report, but don't fix:
- retired summary names still present (`PROJECT.md`, `Project_Summary.md`,
  `*_STATE.md`);
- more than one `Project_Summary_*.md` in a sandbox (e.g. a sync-conflict
  copy) — the PM decides which survives.

### Step 2 — Create the sandbox

If `00_ai_sandbox` is missing, create exactly that folder at the project root.
Nothing else goes in it at this step.

### Step 3 — Inventory the project

List the top-level folders, file counts and newest files in each, and check the
folder spine against the BDM project folder standard. Build an email digest
from the `.msg` filenames in `00_Email Communication\`
(`YYYY-MM-DD_HHMMSS_Sender_Subject.msg`). Note likely key documents by
filename: contract, decision notices, fee proposals, agreements, latest minutes,
programme, cost reports.

**Template carry-overs are not project facts.** Jobs copied from
`_ New Job Folder` still hold its stub files (old dated minutes, invoice
registers, completion certificates from the template). Ignore them as sources
and note them in §16.

### Step 4 — Read the sources

Read in this order, newest first within each group. Stop a group once the facts
it feeds are settled — don't read every file.

| Order | Where | Feeds |
|---|---|---|
| 1 | `01_Client\`, BDM fee proposal / engagement | §1 client, BDM role, fee status |
| 2 | `13_Contract Admin\00_Contract Documents\` (or legacy `13_Contract`), the live Contract Admin Register | §1 contract, §5 cost, §6 variations, §7 EOTs, §8 notices |
| 3 | `05_Consultants\` — fee proposals, consultant agreements, insurance certificates | §2 team, fees, PI expiry |
| 4 | `03_Applications & Approvals\`, `04_Statutory Authorities\` — decision notices | §1 DA/BA/authority refs, §10 open DA conditions |
| 5 | `08_Issued Reports\`, `02_Project Control\` cost reports, QS progress reports | §5 cost, §15 reports register, §3 status |
| 6 | `07_Meeting Minutes\` — latest set per series | §3 status, §10 actions, §11 decisions |
| 7 | `09_Programmes\` — latest | §4 programme |
| 8 | `06_Drawings & Specifications\` — latest revision per discipline (filenames are usually enough) | §13 drawings |
| 9 | `00_Email Communication\` — the most recent ~15–25 relevant emails, plus any whose subject names a contract, claim, approval or appointment | §3, §11, §12 contacts, gaps everywhere |

Read `.msg`, PDF, Word and Excel files with whatever readers the session has.
Never change a source file to read it, and never change Office security
settings to get a file open — log it as "read the source" and move on.

**Large sweeps:** where the session supports sub-agents, give each project its
own agent, with rules 1 and 2 above in its brief. Agents return facts with
source paths; you write the summary yourself.

### Step 5 — Write the summary

Copy `references/project_summary_template.md` and fill it.

- **Filename:** `Project_Summary_<Project_Name>.md` — the folder name with the
  job number stripped, punctuation dropped and spaces turned to underscores
  (`202699_12 Example St, Suburb` → `Project_Summary_12_Example_St_Suburb.md`).
- **Title line:** `# Project Summary — <name, suburb>`.
- **Change log** at the top: one entry recording the backfill — date, number of
  sources read, number of gaps, and "nothing moved or renamed".
- **All 17 sections present**, in order. A section that doesn't apply yet gets
  one line saying why (e.g. pre-contract → §6–§8 "N/A — no head contract
  administered by BDM"). Keep the heading.
- **Tailor to the engagement.** QS / lender-side jobs: §1 lender and drawdown
  basis, §5 from the latest QS progress report, §15 lists the QS reports.
  DM / pre-contract: weight §2 team, §4 programme to DA/BA milestones, §9
  feasibility risks.
- **§10** gets a "Confirm …" action for every important gap (contract sum, DA
  ref, PI expiry, client contact …), owner = the PM.
- **Conflicting figures** between two documents: record both with sources, put
  the conflict in §9 and a "Confirm …" in §10. Don't pick one.
- **Multi-contract jobs:** one summary; split §5–§7 by contract with a
  sub-heading each.
- **§16 folder gap flags:** empty `01_Client\`, services drawings under
  `05_Consultants\`, deliverables parked in `00_ai_sandbox\` that have a regular
  home (`CLAUDE.md` §8), pre-standard folder names, template carry-overs. Flag
  only — no moves.
- **§17 conventions:** record the folder and file naming the project actually
  uses (claim folder pattern, report naming, variation numbering) so later
  skills follow it. Contract quirks only where a document shows them. §17.2
  dated notes carry the date.
- Plain English, Australian spelling, short lines. Write UTF-8.

Write the file into `00_ai_sandbox\`. Re-open it once and check: 17 headings
present, no `[placeholder]` brackets left, the template's HOW TO FILL comment
removed, every $ figure and date has a source.

**Near-empty project** (only template carry-overs): still create the sandbox
and a summary — §1 from the folder name, everything else `TBC`, and §3 says
"No project documents filed yet as at <date>."

**Retired summary present but no standard one:** use the retired file as a
source, write the standard file, and flag the retired one for the PM to remove.
Don't delete it.

### Step 6 — Report back

One table, one line per project:

| Project | Sandbox | Summary | Sources read | Gaps | Top flag |
|---|---|---|---|---|---|

Then a short "What to do next": the two or three gaps the PM should close first
(usually contract sum, client contact, consultant PI expiry). Link each summary
file. Keep it short.

---

## 4. Bring an existing summary to standard

Use when the user asks, or says yes to the offer in Step 1. One job at a time
unless they ask for a batch; a batch still runs each job through every step.

This is a restructure, not a rewrite. **Every fact, figure, date, name,
source path and note in the old summary survives** — in the new summary or,
for old history only, in the archive. Nothing is summarised, reworded,
corrected or dropped. Where the old summary is wrong or contradicts a
document, leave the text as it is and flag it in §9 and §10.

### Step A — Back up

Copy the summary, unchanged, to
`00_ai_sandbox\_SS\Project_Summary_<Name>_superseded_<yyyy-mm-dd>.md`
(create `_SS` if missing; confirm today's real date). Work from the original;
the copy is the comparison baseline and the way back.

### Step B — Map the old content to the 17 sections

Go through the old file top to bottom and assign every block to one section
of `references/project_summary_template.md`:

- Old numbered or named sections → the section with the same subject, whatever
  their old number. A "backfill supplement" or "§2 / §13 / §15 (new columns)"
  block bolted on the end goes into its proper section.
- Two blocks on the same subject (e.g. a contacts table and a "key contacts
  directory") → both go in that section, one after the other. Merge rows only
  where they are identical.
- Content that fits nowhere → §17.2 dated notes, keeping its date, or §16.
- Agent or operator notes that are project knowledge → §17.

### Step C — Move old history to the archive

Change-log entries older than 90 days, and §11 / email-log entries beyond the
most recent ~12, move **word for word**, newest first, into a working archive
file in the same temp folder as Step E's working summary. On PASS they are
added to the top of `00_ai_sandbox\Summary_ChangeLog_Archive.md`, above
anything already there, so the file stays newest first (never name it to start with `Project_Summary_`). Nothing else
goes in the archive. §16 gets a pointer line to it.

### Step D — Fill the gaps

A section with no old content gets its heading and is filled from the folder
by the §3 Step 4 source order, with the same rules: every fact sourced, not
found → `TBC — not found in folder` and a "Confirm …" action in §10. §17 gets
the project's naming and numbering conventions as the folder shows them.

### Step E — Write, then check before replacing

Write the restructured summary to a working file in a temp folder outside the
project folders (`CLAUDE.md` §8 — scratch never goes in a job folder), then run
the skill's checker:

```
python <this skill>/scripts/check_restructure.py <_SS backup> <working summary> <working archive>
```

- **FACTS** must show 0 missing and **STRUCTURE** must pass, or the result is
  FAIL — fix the working file and run it again. Never replace the summary on
  a FAIL.
- **LINES** is advisory: read every listed line and confirm it is present in
  another form (re-ordered table cells, a merged row). Put anything genuinely
  missing back.
- No Python on the machine: do the three checks by hand and say so in the
  report.

On PASS — and only then — copy the working summary over
`Project_Summary_<Name>.md`, add the working archive to the top of
`Summary_ChangeLog_Archive.md`, clear the temp folder, and add a change-log line at the top: "Brought to the 17-section
standard — backup `_SS\…`, n entries archived, n sections filled, n gaps,
check PASS."

### Step F — Report

| Project | Grade before | Size before → after (+ archive) | Sections filled | Gaps | Check | Lines to review |
|---|---|---|---|---|---|---|

Then the "Confirm …" actions the PM should close first. The PM reviews the
restructured summary before it is relied on for a certificate, claim or report.

---

## 5. Revision control

| Rev | Date | Change |
|---|---|---|
| R2 | 2026-10-20 | Bring-to-standard mode (§4): back up to `_SS`, map every block of an existing summary to the 17 sections, archive change-log and log entries older than 90 days / beyond ~12 to `Summary_ChangeLog_Archive.md`, fill missing sections with sources or TBC, and replace only when `scripts/check_restructure.py` passes (facts, structure; lines advisory). Step 1 grades existing summaries. Rules 1 and 3 amended for §4 only (Director, 2026-10-20). |
| R1 | 2026-10-20 | First issue in the BDM repo. Summary-only port of the sandbox setup skill (create sandbox + 17-section backfill to `CLAUDE.md` §13). AI_Context build, monthly AI_Context audit, PowerShell/Node scripts, ProjectHub reads and `bdm-house-style` dependency deliberately left out (Director, 2026-10-20). Adds `references/summary-rules.md`, the shared read-first / update-after rules carried by every project-bound skill. |
