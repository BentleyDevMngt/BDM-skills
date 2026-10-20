---
name: meeting-minutes-update
description: >-
  Updates an existing Meeting Minutes Word document (.docx) for construction and
  development projects by reviewing a meeting transcript or notes, then applying all
  changes with Track Changes visible. Also builds the first set of minutes for a new
  meeting series from the current BDM template. Use whenever a user asks to update,
  roll forward, refresh, or draft meeting minutes from a transcript, meeting notes,
  audio transcription, or discussion summary. Covers design coordination, site, PCG
  and consultant meetings.
---

# Meeting Minutes Update Skill

**Revision: R3 · 2026-10** (check this against the latest package in
`Alfred\_Skills\meeting-minutes-update\` — filename carries the revision, e.g.
`meeting-minutes-update_R1_2026-06.skill`. If your installed copy shows an older
revision, reinstall the latest.)

Updates an existing Meeting Minutes Word document to reflect the latest meeting
discussion by reviewing a transcript or notes, applying tracked changes, updating
action items, and maintaining the document's existing structure and formatting.
The output is a **current-status register**: every item reads as where it stands
now, and anything closed, superseded or duplicated is removed (see Phase 2). Also
covers building the FIRST set of minutes for a new series from the current BDM
template.

## Why this skill exists

Construction and development projects run on meeting minutes. Design coordination
meetings, PCG meetings, and site meetings generate action items across multiple
disciplines (Architecture, Structural, Mechanical, Hydraulic, etc.) that must be
tracked from meeting to meeting. Updating minutes manually is slow and error-prone
-- items get missed, actions aren't closed out, and attendee lists go stale. This
skill automates the full workflow: read the transcript, identify what changed, and
produce an updated Word document with Track Changes so reviewers can see exactly
what was added, removed, or modified.

---

## Prerequisites

This skill depends on the **docx** skill for all Word document manipulation. Before
starting any work, read the docx SKILL.md to understand the unpack -> edit XML ->
repack workflow, tracked changes XML patterns, and validation mechanics.

---

## Inputs

The user will provide:

1. **Existing meeting minutes** (.docx) -- the document to update. If this is the
   FIRST meeting of a series and no prior minutes exist, build a fresh set from the
   current BDM template (see "Template currency" below).
2. **Meeting transcript or notes** -- the source of new information.
3. **The Outlook calendar event** for the meeting -- the authoritative source of
   attendee/invitee NAMES and EMAIL ADDRESSES (see Phase 1). Do not hand-key
   attendees from a garbled auto-transcript when the calendar invite is available.

The transcript/notes can come in various formats:
- A .docx file containing a typed or auto-transcribed meeting record
- A .txt or .md file with discussion notes
- Text pasted directly into the conversation
- An email thread summarising what was discussed
- Previous meeting minutes (for cross-referencing what's changed)

If the format isn't immediately clear, extract the text using pandoc or the
appropriate skill (PDF skill for .pdf, etc.) and work from the extracted content.

### Template currency (BDM)

Before drafting or rolling forward, confirm the current template revision in the
BDM Working Copy templates folder:
`C:\Users\<user>\BDM\Standard - Documents\BDM TEMPLATES\Working Copy`.

- **Design coordination meetings** -> `230-Design_Meeting_Minutes` (use the highest
  Rn in `200 Project Management - Pre-Contract\`; ignore anything under `_Superseded`).
- Pull the latest revision and reconcile against it. Do NOT use the generic
  `T218_Meeting Minutes` skeleton in the New Job Folder for a design meeting -- it is
  the old generic form and has been superseded by Form 230 for design meetings.

---

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

## Workflow Overview

The process has four phases:

1. **Analyse** -- Pull attendees from the calendar, read the existing minutes and
   transcript, map discussions to sections
2. **Plan changes** -- Build a change list before touching any XML
3. **Apply with Track Changes** -- Edit the document XML with proper tracked change markup
4. **Validate and deliver** -- Repack, validate, and verify the output

---

## Phase 1: Analyse

### Pull attendees and apologies from the Outlook calendar (do this FIRST)

Auto-transcription mangles names and never carries email addresses or initials, so
the meeting's Outlook calendar event is the source of truth for the attendee block.

1. Find the event with `outlook_calendar_search` -- query on the meeting subject
   (e.g. "New Earth - Design Development Meeting") with `afterDateTime` /
   `beforeDateTime` bracketing the meeting date. If the exact subject returns
   nothing, broaden the query (project short name, or "Design Development").
2. From the returned event take: `organizer`, the full `attendees` email list, the
   `start`/`end` (convert from UTC to local AEST for the TIME field), and `location`.
3. Resolve each email to a Name / Initials / Company:
   - Derive the company from the email domain (e.g. `@jhaengineers.com.au` -> JHA
     Engineering Services, `@studioworkshop.com.au` -> Studio Workshop,
     `@edgece.com` -> Edge, `@axiscertifiers.com.au` -> Axis Certifiers,
     `@spectrafire.com.au` -> Spectra Fire, `@bdmanagement.com.au` -> BDM).
   - Derive the display name from the email and confirm against the transcript
     speakers; carry initials (first + surname).
4. **Split attendees vs apologies using the transcript.** The calendar lists
   *invitees*, not who actually attended. Anyone who spoke / joined in the transcript
   is an Attendee; an invitee who did not appear (or was explicitly noted as an
   apology) goes in Apologies. Anyone who attended **in part** is an Attendee, not an
   apology (Director ruling, 13 October 2026). If attendance is genuinely unclear,
   flag for the user rather than guessing.
   - Auto-transcripts mislabel speakers: two people sharing a device appear under
     one name, and a person addressed by name who answers may be logged under
     someone else. Read who is *addressed* as well as who is labelled, and confirm
     doubtful attendees with the chair.
   - An invitee on the calendar who never featured in the meeting (for example a
     second contact at a consultant) is left off both lists unless the chair says
     otherwise -- do not list a name you cannot complete.
5. If the calendar tool is unavailable, fall back to the meeting invite email in the
   project's email folder, then to the transcript -- and flag any name/email left
   unconfirmed.

### Read the existing minutes

Unpack and extract the full text of the existing minutes:

```bash
python scripts/office/unpack.py minutes.docx unpacked/
pandoc --track-changes=all minutes.docx -o minutes.md
```

Identify the document's structure:
- Header section (project name, meeting number, date, time, location)
- Attendee and apology tables
- Discipline/topic sections (e.g. General, Approvals, Architecture, Structural, Civil, Electrical, Mechanical, Hydraulic, Landscaping, Fire Engineering, Program)
- Action item tables within each section (typically: Item Number, Description, Action/Responsibility, Date)
- Any existing strikethroughs or tracked changes from previous updates

### Read the transcript

Extract the full transcript text. For construction design meetings, the transcript
typically flows through disciplines in order, with discussion jumping between topics.
Key things to extract:

- **Who attended** (and who was absent compared to previous meetings) -- reconcile
  against the calendar attendee list from the step above
- **Items discussed** -- map each discussion point to the relevant section in the minutes
- **Decisions made** -- these become updates to existing items or new items
- **New action items** -- with responsible party and any target dates mentioned
- **Closed items** -- actions confirmed as complete or no longer relevant
- **Status updates** -- items that are ongoing but have new information

### Build a change map

Before touching any XML, create a structured summary:

```
HEADER CHANGES:
- Date: [old] -> [new]
- Attendees to add: [names, roles, companies, emails -- from calendar]
- Attendees to remove to apologies: [names]
- Apologies to move to attendees: [names]

SECTION CHANGES:
[Section Name]:
  - Item X.Y: [Close/Update/No change] -- [summary of what changed]
  - New item X.Z: [description] -- [responsible party]
  ...
```

This prevents missed updates and gives you a clear checklist to work through.

---

## Phase 2: Plan Changes

### The minutes are a current-status register, not a history (Director ruling, 13 October 2026)

Each issue of the minutes states **where every live item stands now**. It is not a
diary of how the item got there. The previous issue is the history; the redline is
the record of what changed. In practice:

1. **Rewrite, don't append.** When an item is discussed, replace its description
   with one current-status entry. Never add "Update 12 October 2026 --" bullets on
   top of the old text. The old wording is tracked-deleted and the new wording
   tracked-inserted, so the reviewer still sees the change.
2. **Closed or superseded items come out.** Delete the whole row as a tracked row
   deletion (`w:trPr/w:del`). It shows struck once in this redline and is gone when
   the changes are accepted. Do not carry a "Closed." prefix or a "Closed" date
   into the next issue -- and any row the previous issue already marked Closed or
   Superseded is deleted now.
3. **One item per topic.** Where the same topic sits in two sections (rooftop plant
   under Architecture and Mechanical; the booster under Electrical and Hydraulic;
   a programme date under General and Programme), keep it in the section that owns
   the decision, fold the other's live content into it, and delete the duplicate.
4. **Past events and past dates come out.** A meeting that has been held, a document
   that has been issued, a milestone that has passed -- remove it. The Programme
   section carries live key dates only; the General programme item points to it
   rather than repeating it.
5. **Items not discussed** stay as they are -- do not invent a status. But list
   every one carrying a past due date in the hand-off, so the chair can close or
   carry it.
6. **Keep it tight.** Bullets, one operative sentence each. Measure the description
   word count against the previous issue; a meeting with many new items may run a
   little longer, but the minutes should not grow just because items accumulate.
7. **Post-meeting information** goes in only when sourced (for example a consultant's
   email that afternoon), labelled "Post meeting --", and named in the hand-off.
8. **Every cross-reference resolves.** After deletions and merges, check that each
   "refer x.x" points to an item still in the accepted document.

### Action item status logic

For each existing action item, decide from the transcript:

- **Close** -- complete, superseded, past, or duplicated elsewhere. Tracked row
  deletion (rule 2).
- **Rewrite** -- discussed with new information. Replace the description with its
  current status (rule 1); update the action initials and the date to match.
- **Carry** -- not discussed. Leave untouched; flag it in the hand-off if its date
  has passed (rule 5).
- **New** -- a topic not covered by any existing item. Add a new row with the next
  number in that section.

### Numbering convention

Follow the existing document's numbering scheme. Typically:
- Major sections: 1.0, 2.0, 3.0, etc.
- Items within sections: 1.1, 1.2, 1.3, etc.
- Sub-items: 1.1a, 1.1b or indented rows under the parent

When adding new items, use the next available number in that section. When adding
sub-items to an existing item, follow whatever pattern the document already uses.

---

## Phase 3: Apply with Track Changes

(See the docx skill for the full unpack -> edit XML -> repack workflow and the
tracked-change XML patterns -- del/ins must be siblings of w:r at the paragraph
level; use w:delText inside w:del; for inserted/deleted table rows place w:ins/w:del
inside w:trPr after w:trHeight; keep every w:id unique; copy run properties from the
text being replaced. These patterns are unchanged.)

**Replacing a cell's content safely (the rewrite in rule 1).** Diff the old and new
paragraphs. Keep paragraphs whose text is unchanged; tracked-delete the old ones;
tracked-insert the new ones in position. The cell's **last** original paragraph must
never have its paragraph mark deleted: if its text goes, wrap its runs in `w:del`,
leave its mark alone, and put the final new text inside it as an inserted run, with
any other new paragraphs inserted before it. If nothing new follows it, delete the
mark of the paragraph *before* it instead, so that paragraph joins the last one when
changes are accepted. Build new paragraph properties from a clean copy taken before
the deletion pass.

**Fresh (first-meeting) build:** there are no prior items to track, so a clean
issue is appropriate -- no tracked changes required. Populate the current Form 230
template and follow the BDM filename convention.

---

## Phase 4: Validate and Deliver

Repack with validation (`scripts/office/pack.py ... --original minutes.docx`).

**Verify programmatically, not visually.** Do NOT render the document to PDF or
images as a review step, and never write render output, scratch files or intermediate
artefacts into the project folder -- they are not a deliverable, they clutter the
job folder, and the shell cannot delete them again afterwards. Anything of that kind
stays in the session workspace.

Run these six checks on the packed file:

1. No duplicate revision `w:id`.
2. **No table cell whose FINAL paragraph mark carries `<w:del>`** -- excluding rows
   that are themselves deleted (`w:trPr/w:del`). This is the check that matters. A
   deleted final paragraph mark makes Word eat the cell when the reviewer accepts
   changes, and the whole row at the end of a table. LibreOffice does not reproduce
   it, so a render or an accept-changes script will show a clean document that Word
   destroys. To replace a cell's content safely, insert the new paragraphs AFTER the
   cell's current last paragraph, THEN apply the deletions -- so no deleted paragraph
   is ever the cell's final one -- and build every new `pPr` from a pristine snapshot
   taken before the deletion pass.
3. No paragraph marked both inserted and deleted.
4. The revision mark is the first child of `rPr` (schema order).
5. No `w:t` inside `w:del`, and no `w:delText` outside one.
6. Every row in a table has the same cell count.

Then **simulate accept-all and reject-all** independently of LibreOffice -- drop
`w:del`, unwrap `w:ins`, merge paragraphs whose mark is deleted -- and confirm on
both passes: row count, cell count per row, the full item-number sequence, the
attendee and apology lists, and the header fields. Accept must yield the new
meeting; reject must reproduce the previous minutes exactly.

Finally, **diff the paragraph text against the previous minutes**: every paragraph of
the prior issue must still be present, retained as struck text. Only header and date
cells where the old and new text now share one paragraph may differ.

`validate.py --author` only compares text; it will pass a document Word will destroy.

---

## Where the minutes are saved (BDM)

Minutes file into the project's own meeting-minutes folder, in the subfolder for that
meeting series where the project uses one:

`Projects - Documents\<project>\07_Meeting Minutes\<N.0_Series>\`

for example `3.0_Sales Meeting`, `2.0_PCG Meetings`, `4.0_Design Meetings`. Where the
project keeps its minutes flat in `07_Meeting Minutes\`, follow that. The series
file lives with its series. Read that folder before saving -- the prior issues are the
only reliable guide to the folder and the naming this project actually uses, and they
override any general assumption about where a draft belongs.

**Do NOT save minutes to `00_ai_sandbox`.** The sandbox is for one-off drafts and
working files, not for an ongoing numbered series.

**Filename -- follow the prior issues in that folder, with no `_DRAFT`:**

`YYYYMMDD_<Project short name>_<Series> Meeting Minutes No.NN.docx`

for example `20261012_New Earth_Design Development Meeting Minutes No.05.docx`

- The date prefix is the meeting date, matching the prior issues in that folder.
- **No DRAFT marking** -- not on the filename, footer, header or a watermark. The
  company file (§5, 15 September 2026) prohibits it, and the Director removes it.
  The minutes are held for sign-off as a process, not a label: they are not sent
  until the chair issues them.
- Never PDF the minutes before sign-off. A PDF reads as an issued instrument.

**Before overwriting, re-read the live file.** The chair may have opened, renamed or
edited the draft since it was saved. Stage it, diff it against what you saved, and
fold any edits in. Edits made without track changes are to be treated as
instructions and carried into the tracked rebuild.

**After saving, confirm the save held.** OneDrive can sync an older copy back over a
fresh save, and SharePoint adds its own properties to the file, so the file's hash
changes. Wait for the sync to settle, then compare the hash of `word/document.xml`
inside the saved file with the one you built. If it does not match, save again.

---

## Tone and Language

Write as the project Superintendent or meeting chair -- professional, concise, and
factual. Meeting minutes record decisions and actions, not opinions or discussion
summaries. Match the technical detail level of the existing items.

---

## Consistency Checks (Final Pass)

Before delivering, verify:

- Meeting number and date in the header match the new meeting
- **Every attendee and apology has a NAME, INITIALS, COMPANY and EMAIL populated
  from the Outlook calendar** -- no blank email cells, no [placeholder] text
- All attendees who spoke in the transcript are in the Attendees table; invitees who
  did not attend are in Apologies (or removed if no longer on the project)
- New item numbers follow the existing sequence without duplicates
- **No closed, superseded, duplicated or past-dated item survives the accepted view**
  (Phase 2 rules 2 to 4); every "refer x.x" resolves
- Items not discussed that carry a past date are listed in the hand-off
- Responsibility initials match names in the attendee list
- Items confirmed as closed are deleted as tracked rows, not left marked "Closed"
- No stale references to the previous meeting's date remain
- For updates: Track Changes are NOT accepted -- leave them visible for review
- No DRAFT marking anywhere in the document or the filename (company file §5)
- Saved into the project's `07_Meeting Minutes\` folder (series subfolder where used),
  not into `00_ai_sandbox`, and the save confirmed by hash after OneDrive sync
- No render output, scratch or intermediate files left anywhere in the project folder

---

## Cover email (BDM standing rule)

When finalising any project meeting minutes, also draft a concise cover email for
the **meeting chair / organiser** (read it off the calendar `organizer` field -- not
always the same person) to send out with the minutes attached. List the key actions
and a review-by date. Address it from the chair, To the attendees, Cc apologies and
the principal/client.

---

## Revision history

- **R3 · 2026-10** — Director ruling, 13 October 2026, on New Earth DDM No.05. The
  minutes are a current-status register: discussed items are rewritten to their
  current status rather than appended to; closed, superseded, duplicated and
  past-dated items are removed as tracked row deletions; the programme lives in one
  section; items not discussed with past dates are listed for the chair; length is
  measured against the previous issue; cross-references are checked. Added the safe
  cell-replacement method for those rewrites. Attendance: part attendance counts as
  attended; guidance on mislabelled transcript speakers. DRAFT marking and the
  `_DRAFT` filename removed to match company file §5. Added the re-read-before-overwrite
  and confirm-after-sync steps. Save location allows a flat `07_Meeting Minutes\`
  where the project uses one.
- **R2 · 2026-09** — Director instruction, 1 September 2026. Phase 4 verification is
  now programmatic, not visual: the PDF/image render step is removed, and no render
  output or scratch file may be written into the project folder. Added the six-check
  tracked-changes audit (including the deleted-final-paragraph-mark rule that
  destroyed the New Earth DDM No.03 redline on accept), the accept/reject simulation
  and the paragraph diff. Added a "Where the minutes are saved" section: the project's
  `07_Meeting Minutes\<N.0_Series>\` folder, never `00_ai_sandbox`, filename ending
  `_DRAFT` until sign-off.
- **R1 · 2026-06** — First BDM-customised revision. Added: pull attendees/invitees
  (names + emails) from the Outlook calendar as the source of truth for the attendee
  block; Form 230 template-currency rule for design meetings (replaces the generic
  T218 skeleton); first-meeting fresh-build path; cover email from the chair/organiser
  (not hard-coded to James); DRAFT-until-signed and email-populated consistency checks.
- *Baseline* — original (unversioned) installed skill: transcript-driven tracked-
  changes update of an existing minutes .docx.
