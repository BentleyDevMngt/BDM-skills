---
name: meeting-minutes-update
description: Updates an existing Meeting Minutes Word document (.docx) for construction and development projects. Two modes on one rolling file: a PRE-MEETING statusing pass that pre-populates the next issue from email, interim transcripts and the project summary, marking what is new in YELLOW HIGHLIGHTING and using no tracked changes, so the chair can run the meeting from it; and a POST-MEETING pass that updates the same file from the transcript using TRACKED CHANGES and clears the highlighting, so the redline means only what the meeting changed. Also builds the first set of minutes for a new series from the current BDM template. Trigger on 'update/roll forward/refresh/draft meeting minutes' from a transcript, notes or audio transcription, and on 'status the minutes before the meeting', 'pre-meeting statusing', 'status the open items for Thursday's meeting', or 'prepare the agenda draft'. Covers design coordination, site, PCG and consultant meetings.
---

# Meeting Minutes Update Skill

**Revision: R5.0 · 2026-10** — skill revisions carry one decimal place: a scope change raises the whole number, a correction or refinement raises the decimal. The release history is in the revision history at the end of this file and the repository CHANGELOG.

Updates an existing Meeting Minutes Word document to reflect where every item
stands, applying tracked changes and maintaining the document's existing structure
and formatting. The output is a **current-status register**: every item reads as
where it stands now, and anything closed, superseded or duplicated is removed (see
Phase 2).

The skill runs in two modes on one rolling file — a **pre-meeting statusing pass**
that builds the next issue from correspondence so the redline serves as the meeting
agenda, and a **post-meeting pass** that finishes the same file from the transcript.
See **Two modes** below. It also covers building the FIRST set of minutes for a new
series from the current BDM template.

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

## Two modes

Both modes write to the **same file**: the series' working .docx carrying the next
meeting's number. The pre-meeting pass creates it; the post-meeting pass finishes it.

| | **Pre-meeting statusing pass** | **Post-meeting update pass** |
|---|---|---|
| Trigger | "status the minutes before Thursday's design meeting", "pre-meeting statusing", "prepare the agenda draft" | "update the minutes from this transcript", "roll the minutes forward" with a transcript in hand |
| Source of new information | Correspondence since the last issued minutes, interim transcripts, the project summary | The meeting transcript or notes |
| What it produces | The next issue pre-populated to current status, new text highlighted in yellow | The same file, with what the room decided added |
| How changes are marked | **Yellow highlighting on the new text. No tracked changes.** | **Tracked changes.** No highlighting |
| What the marking means | "This is new since the last issue — read it in the meeting" | "This is what the meeting changed" |

**The two passes must not both use tracked changes** (Director ruling, 19 October 2026).
Two redline layers in one file make the document too busy to read, which defeats the
purpose of putting it in front of the meeting. So:

- The **pre-meeting pass edits the text directly** and highlights what is new in yellow.
  The chair reads the yellow to see what has moved since the last issue.
- The **post-meeting pass uses tracked changes**, and **clears the yellow highlighting as
  it goes**. By the time the minutes are issued there is no highlighting left, and the
  redline carries one meaning only: what the meeting itself changed.

The post-meeting pass does not accept its own changes — accepting is the chair's act.

Phases 1 to 4 apply to both modes. The pre-meeting pass differs most in **what it is
allowed to assert**; where it differs, **The pre-meeting statusing pass** below
governs.

A pre-meeting pass is optional. A series can run post-meeting only, exactly as R3.

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

**In the pre-meeting statusing pass there is no transcript**, and input 2 is replaced
by: the correspondence received since the last issued minutes for that series, any
interim transcript dated after those minutes, and the project's
`00_ai_sandbox\Project_Summary_*.md`. The calendar event is the event for the
*upcoming* meeting. See **The pre-meeting statusing pass**.

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

## The pre-meeting statusing pass

The pass answers one question for every live item: **where does this actually stand
today, and what does the chair need to decide about it?** It runs in the day or two
before the meeting, and the file it produces is what the meeting is run from.

### The base is the last ISSUED minutes

Start from the latest issued minutes for that series -- the issue the chair sent.
Roll the header to the next meeting: number, date, time and location from the Outlook
calendar event for the upcoming meeting. Never start from an earlier pre-meeting file
whose changes were never accepted; that is how redlines stack into noise.

### Attendees cannot be settled before the meeting

The calendar lists invitees. Phase 1's attendees-versus-apologies split depends on who
actually spoke, which does not exist yet. So:

- Populate the Attendees table from the calendar invitee list, with name, initials,
  company and email resolved as Phase 1 requires.
- Leave Apologies as the invite stands -- a declined invitation is an apology, a
  non-response is not.
- Say in the hand-off that attendance is provisional and is settled post-meeting.

### How the pre-meeting pass marks its work

Edit the text in place. Do not use `w:ins` or `w:del` anywhere in this pass; the
document must contain no tracked changes when it is handed to the chair.

**Highlight only what is actually new.** Apply `<w:highlight w:val="yellow"/>` to the
runs of a line that is new or reworded. A bullet carried over from the previous issue
word for word stays plain, as does an item that was not touched. Highlighting a whole
item because one bullet in it moved defeats the point — the yellow is there so the eye
lands on what changed.

**Preserve the document's own formatting.** The minutes read as a bold lead-in label
against plain body text (`PROCORE: EOT-5a is shown Open...`), with only the item title
fully bold. A rebuilt line that loses that is as bad as a wrong one, and it is easy to
do by accident:

- **Reuse a carried-over line, do not rebuild it.** Where a bullet survives word for
  word, re-use the original paragraph element so its run structure is untouched by
  construction. Rebuilding it from its text alone flattens the bold lead-in into plain
  text, or the whole line into bold.
- **Take run properties from a BODY run, never the first run in the cell.** The first
  run is the bold item title, so inheriting it makes every new line bold.
- **Split a new lead-in label into its own bold run**, with the body plain, and
  highlight both.

**The previous issue is the history.** A direct edit means the document no longer
carries the old wording, so the last issue is the only record of what an item used to
say. Two consequences, and both are obligations:

1. The pass **must not run on an unissued base** (see above). If the previous issue is
   still an unaccepted redline, the old wording is not safely recorded anywhere.
2. The hand-off **must carry a before/after for every item the pass rewrote** — the
   text as it read at the last issue, and as it now reads. Without it there is no way
   to check the pass except by opening two documents side by side.

### The evidentiary rule -- what a pre-meeting status may assert

This is the rule that matters, and it is stricter than the post-meeting pass. A
transcript is direct evidence of what was decided. Before the meeting there is no
such evidence -- only correspondence, from which a status is *inferred*. An inferred
status written as fact is an invented fact, and the rule against those is absolute.

For every item:

1. **A status may be asserted only where a dated source says it.** "Revised set
   issued 14/10 by JHA" is assertable because an email says so. "Complete" is not
   assertable from an email saying it should be done this week.
2. **Every asserted status carries its source in a Word comment** on the changed
   cell -- sender and date for an email, document and date for a transcript or
   drawing, minute reference for a carried item. A status change with no comment is
   a defect: the chair must be able to check any line in the room without leaving the
   document. See the **monthly-report-update** skill for the comment mechanics.
3. **Where the evidence is suggestive but not conclusive, state no status.** Rewrite
   the item as the question the chair should ask -- "Confirm whether the hydraulic set
   issued 14/10 supersedes item 6.2" -- or leave it as Carry and list it in the
   hand-off. A question in the document is useful; a wrong status is worse than a
   stale one.
4. **A proposed closure is marked, never made.** Closure is the chair's act, and this
   pass makes no tracked deletion the chair could reject with one click. Leave the row
   in place. Prefix the item's first line with a bold `PROPOSED CLOSE:` label,
   highlight the label and the closure wording in yellow, and attach a Word comment
   naming the dated source that supports closure. Propose it only where a dated source
   supports closure. Never propose closing an item because it merely looks old.
5. **Contradictions are surfaced, not resolved.** Where the file and the
   correspondence disagree on a date, a scope or who holds an action, carry both in
   the item and leave it for the room. Where two sources give different dates, give
   both rather than picking one.
6. **No invented dates.** Do not put a target date on a new or rewritten item unless
   a source gives one. An empty date cell the chair fills in the meeting is correct;
   a plausible date is not.

### New items before a meeting

Correspondence since the last minutes routinely raises matters never minuted. Add
them as new items in the owning section with the next number, phrased as the live
issue, with the source comment. This is the main value of the pass: the meeting opens
with the new matters already on the page in the right sections, instead of being
remembered, or not.

### Relationship to the daily meeting brief

The statusing pass and the daily meeting brief read the same sources -- the last
minutes, interim transcripts and the period's correspondence. They are not duplicates
and neither replaces the other:

- The **minutes** carry fact: where each item stands, and its source.
- The **brief** carries judgement: the three things for the Director, the portfolio
  note.

Recommendations do not go in the minutes. Where both run for the same meeting, the
brief's "Three for you" stays in the brief.

### Hand-off note for a pre-meeting pass

In addition to the standard hand-off, list:

- A **before/after for every item rewritten** — as it read at the last issue, as it
  now reads. This is mandatory: the document itself no longer holds the old wording.
- Every item with **no new information** since the last issued minutes, so the chair
  can carry or close it in the room.
- Every item rewritten as a **question** rather than a status, and what evidence fell
  short.
- Every **proposed closure**, as a block the chair can scan.
- Any **contradiction** between the file and the correspondence.
- That **attendance is provisional**.

### The post-meeting pass on the same file

After the meeting, run the post-meeting pass on that same file:

- **Clear every yellow highlight** as part of this pass. The highlighting has done its
  job once the meeting has been held, and highlighting left in an issued set of minutes
  is a defect. Removing it is a formatting change, not tracked content.
- Apply the transcript pass as **tracked changes** over the text as it stands. There is
  no pre-meeting redline to work around, because the pre-meeting pass left none.
- Settle attendees and apologies from the transcript, per Phase 1.
- Where the room **confirmed** what the pre-meeting pass recorded, leave the text as it
  stands and add nothing -- it already says the right thing. Only the highlight comes off.
- Where the room **decided differently**, correct it as a tracked change, so the chair
  sees exactly what the meeting altered.
- **Settle every `PROPOSED CLOSE:` item.** Where the room confirmed the closure, delete
  the whole row as a tracked row deletion (Phase 2 rule 2). Where it did not,
  tracked-delete the `PROPOSED CLOSE:` label and record what the room decided. No
  `PROPOSED CLOSE:` label survives into the issued minutes.
- **Reject-all must reproduce the document as it went into the meeting** -- that is, the
  pre-meeting text with the highlighting removed. Verify it per Phase 4.

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

**The pre-meeting file is named for the meeting it is for.** It carries the **next**
meeting's number and date in that folder's own naming pattern -- `No.15` while `No.14`
is the latest issued. It gets no `_DRAFT` suffix and no DRAFT marking of any kind:
company file §5 (15/9/26) prohibits both, and the file needs neither. It is
identifiable as not-yet-issued three ways -- it carries a number that has not been
issued, it is a .docx carrying yellow highlighting where issued minutes are a PDF, and
§10 holds it until the chair sends it. Considered and confirmed by the Director,
18 October 2026.

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
- **Pre-meeting pass:** every asserted status carries a Word comment naming a dated
  source; nothing is asserted that a source does not say; no target date invented;
  every proposed closure is a `PROPOSED CLOSE:` label on a row left in place,
  highlighted, with a comment naming its dated source; attendance flagged as provisional
- **Pre-meeting pass:** the document contains **no `w:ins` or `w:del` at all**; every
  new or reworded line carries a yellow highlight; **no carried-over or untouched line
  is highlighted**; the hand-off carries the before/after for every rewritten item
- **Formatting, checked as well as text:** every carried-over line keeps the bold
  pattern it had in the previous issue, and no new body line is bold end to end. Compare
  run properties against the base, not just the words -- a text-only comparison passes a
  document in which every rebuilt line has silently gone bold
- **Post-meeting pass:** every yellow highlight has been cleared; the changes are
  tracked and not accepted; no `PROPOSED CLOSE:` label survives; reject-all reproduces
  the document as it went into the meeting

---

## Cover email (BDM standing rule)

When finalising any project meeting minutes, also draft a concise cover email for
the **meeting chair / organiser** (read it off the calendar `organizer` field -- not
always the same person) to send out with the minutes attached. List the key actions
and a review-by date. Address it from the chair, To the attendees, Cc apologies and
the principal/client.

---

## Revision history

- **R5.0 · 2026-10** — Director ruling, 19 October 2026, on the Nera PCG No.63 worked
  example. **The pre-meeting pass no longer uses tracked changes.** It edits the text
  directly and highlights what is new in yellow; the post-meeting pass keeps tracked
  changes and clears the highlighting as it runs. Two redline layers in one file made the
  document too busy to read in a meeting, which was the point of producing it. The
  tracked-change author split of R4 is withdrawn as unnecessary — the redline now means
  one thing only. Added the rule that only genuinely new or reworded lines are
  highlighted, never a whole item or a carried-over bullet. Because a direct edit
  destroys the previous wording, the hand-off must now carry a before/after for every
  rewritten item, and the prohibition on running against an unissued base becomes
  load-bearing rather than advisory. Amended in place the same day, before adoption,
  after the Nera draft came back with every rebuilt line bold: carried-over lines are
  now re-used rather than rebuilt, run properties are taken from a body run rather than
  the cell's first (bold) run, a new lead-in label gets its own bold run, and
  verification compares formatting as well as text. Amended again in place on
  29 October 2026, before adoption, after the scheduled pre-meeting run stopped on this
  draft: the mode table no longer says the pass tracks every change; a proposed closure
  is now a highlighted `PROPOSED CLOSE:` label with a source comment, on a row left in
  place, instead of a tracked row deletion (Director ruling, 29 October 2026); the
  post-meeting pass settles each one; and the pre-meeting file is identified by its
  highlighting, not by live tracked changes.
- **R4.0 · 2026-10** — Director decisions, 18 October 2026. Added the **pre-meeting
  statusing pass**: the next issue is pre-populated from correspondence, interim
  transcripts and the project summary before the meeting, and the redline serves as
  the meeting agenda. One rolling file carries both passes, separated by tracked-change
  author (`BDM Status (pre-meeting)` / `BDM Minutes Update`) so the layers stay
  filterable in Word and never stack into noise. Added the evidentiary rule for
  pre-meeting status — a status may be asserted only where a dated source says it,
  every assertion carries a Word comment naming that source, inconclusive evidence
  becomes a question for the chair rather than a status, proposed closures must trace
  to a dated source, contradictions are surfaced rather than resolved, and no target
  date is invented. Attendance is provisional until the post-meeting pass. A `_DRAFT`
  suffix was considered and ruled out: company file §5 prohibits it, and the
  next-meeting number plus the .docx/PDF distinction already carry the meaning.
  Recorded the boundary with the daily meeting brief — minutes carry fact, the brief
  carries judgement.
- **R3.0 · 2026-10** — Director ruling, 13 October 2026, on New Earth DDM No.05. The
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
- **R2.0 · 2026-09** — Director instruction, 1 September 2026. Phase 4 verification is
  now programmatic, not visual: the PDF/image render step is removed, and no render
  output or scratch file may be written into the project folder. Added the six-check
  tracked-changes audit (including the deleted-final-paragraph-mark rule that
  destroyed the New Earth DDM No.03 redline on accept), the accept/reject simulation
  and the paragraph diff. Added a "Where the minutes are saved" section: the project's
  `07_Meeting Minutes\<N.0_Series>\` folder, never `00_ai_sandbox`, filename ending
  `_DRAFT` until sign-off.
- **R1.0 · 2026-06** — First BDM-customised revision. Added: pull attendees/invitees
  (names + emails) from the Outlook calendar as the source of truth for the attendee
  block; Form 230 template-currency rule for design meetings (replaces the generic
  T218 skeleton); first-meeting fresh-build path; cover email from the chair/organiser
  (not hard-coded to James); DRAFT-until-signed and email-populated consistency checks.
- *Baseline* — original (unversioned) installed skill: transcript-driven tracked-
  changes update of an existing minutes .docx.
