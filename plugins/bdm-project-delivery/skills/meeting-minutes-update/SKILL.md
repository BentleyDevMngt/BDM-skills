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

**Revision: R1 · 2026-06** (check this against the latest package in
`Alfred\_Skills\meeting-minutes-update\` — filename carries the revision, e.g.
`meeting-minutes-update_R1_2026-06.skill`. If your installed copy shows an older
revision, reinstall the latest.)

Updates an existing Meeting Minutes Word document to reflect the latest meeting
discussion by reviewing a transcript or notes, applying tracked changes, updating
action items, and maintaining the document's existing structure and formatting. Also
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
   apology) goes in Apologies. If attendance is genuinely unclear, flag for the user
   rather than guessing.
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

### Action item status logic

For each existing action item in the minutes, determine its status based on the
transcript discussion:

- **Close** -- Item confirmed complete or no longer relevant. Apply strikethrough
  to the entire row's text content using tracked deletion, or mark with a status
  indicator depending on the document's existing convention.
- **Update** -- Item discussed with new information. Add the new information as a
  tracked insertion, either appending to the existing description or adding a new
  sub-item row.
- **No change** -- Item not discussed or confirmed as ongoing with no new info.
  Leave untouched.
- **New** -- Discussion raised a topic not covered by any existing item. Add a new
  row with the next sequential item number.

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

**Fresh (first-meeting) build:** there are no prior items to track, so a clean
issue is appropriate -- no tracked changes required. Populate the current Form 230
template, mark the document DRAFT FOR REVIEW, and follow the BDM filename
convention.

---

## Phase 4: Validate and Deliver

Repack with validation (`scripts/office/pack.py ... --original minutes.docx`), then
convert to PDF/images and review each page to confirm: track changes visible (for
updates), table formatting intact, new rows in the correct sections, attendee /
apology block correct (names AND emails populated from the calendar), and no
formatting corruption.

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
- New item numbers follow the existing sequence without gaps or duplicates
- Responsibility initials match names in the attendee list
- Items confirmed as closed are properly marked
- No stale references to the previous meeting's date remain
- For updates: Track Changes are NOT accepted -- leave them visible for review
- Document is visibly marked DRAFT until the user signs it off (BDM drafting rule)

---

## Cover email (BDM standing rule)

When finalising any project meeting minutes, also draft a concise cover email for
the **meeting chair / organiser** (read it off the calendar `organizer` field -- not
always the same person) to send out with the minutes attached. List the key actions
and a review-by date. Address it from the chair, To the attendees, Cc apologies and
the principal/client.

---

## Revision history

- **R1 · 2026-06** — First BDM-customised revision. Added: pull attendees/invitees
  (names + emails) from the Outlook calendar as the source of truth for the attendee
  block; Form 230 template-currency rule for design meetings (replaces the generic
  T218 skeleton); first-meeting fresh-build path; cover email from the chair/organiser
  (not hard-coded to James); DRAFT-until-signed and email-populated consistency checks.
- *Baseline* — original (unversioned) installed skill: transcript-driven tracked-
  changes update of an existing minutes .docx.
