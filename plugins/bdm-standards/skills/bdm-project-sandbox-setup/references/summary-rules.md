# Project summary rules — for every BDM skill that works on a project

These rules implement the company `CLAUDE.md` §8 (sandbox first) and §13 (project
summary standard), which live at the root of `Projects - Documents` and win over
this file if the two ever disagree.

Every project-bound skill in the BDM plugins carries a short copy of the
"Project summary" block below. This file is the long form and the one to change
first; when it changes, update the copies in the same commit.

---

## Where the summary lives

`<project folder>\00_ai_sandbox\Project_Summary_<Project_Name>.md`

- Match the sandbox folder case-insensitively (`00_ai_sandbox` and `00_AI_sandbox`
  are the same folder).
- Match the summary with the wildcard `Project_Summary_*.md`. There is exactly
  **one** per sandbox.
- Retired names — `PROJECT.md`, `Project_Summary.md`, `*_STATE.md` — are not read
  as the summary. Report one if you find it.

## Before you start

1. **Read the summary.** Use it to orient: parties, references, phase, current
   status, open actions and the project's own conventions (§17). §17 overrides a
   skill's default naming or numbering where the two differ.
2. **Missing summary or sandbox:** say so in your hand-back and carry on from the
   source documents. **Never create a stub.** Creating a summary is the job of
   `bdm-project-sandbox-setup` only, because a stub that looks like a summary is
   worse than none.
3. **Two summaries in one sandbox** (for example a sync-conflict copy): flag it,
   treat neither as reliable, and work from the source documents.
4. **Stale summary** (last change-log entry more than 30 days old, or contradicted
   by a newer document): say so, and prefer the newer document.

## Figures come from the source, not the summary

The summary is an index to the project, not an authority. Any contract sum,
certified or claimed amount, retention figure, date, reference number, party
name or clause that goes into a skill's output is **checked against the document
it came from** before it is used. Where the summary and the source disagree, the
source wins, the output uses the source, and the summary is corrected in the
update step below with a note of the conflict.

## Before you finish

Update the summary in the same pass:

1. **Change log** — one dated line at the top (newest first): what this run
   produced, its file path relative to the project folder, and its status
   (DRAFT — held for sign-off, or filed).
2. **Sections the run changed** — only those. Typical: §3 status, §5 cost,
   §6 variations, §7 EOTs, §10 actions, §11 decisions, §13 drawings,
   §15 issued reports. Put the source path on each changed line.
3. **Don't rewrite** sections the run did not touch, don't reformat the file,
   and don't delete another person's entries.
4. **No summary to update:** skip this step and flag it. Don't create one.

Updating the summary is internal and reversible: do it, then report it. It is
not issuing anything.

## The block each skill carries

```markdown
## Project summary (company CLAUDE.md §8, §13)

- **Before you start:** read `00_ai_sandbox\Project_Summary_*.md` (sandbox folder
  matched case-insensitively) for parties, references, status and the project's
  own conventions (§17). Missing → say so and work from the source documents;
  never create a stub (that is `bdm-project-sandbox-setup`'s job). Two summaries
  → flag it and rely on neither.
- **Figures come from the source:** any sum, date, reference or party that goes
  into the output is checked against the document it came from. If the summary
  disagrees, the source wins and the summary is corrected below.
- **Before you finish:** update the summary in the same pass — a dated
  change-log line at the top (what this run produced, where, status), plus only
  the sections this run changed, each with its source. No summary → skip and flag.
```
