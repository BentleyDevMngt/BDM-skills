---
name: bdm-meeting-brief
description: "Build Andrew's pre-meeting brief for a project meeting — closed items, open items, three things for him — from the last minutes, interim transcripts and the period's email."
---

# BDM Meeting Brief

The full procedure, including the worked reference example Andrew approved, is
at `Projects - Documents\Alfred\BDM_Meeting_Brief_Procedure_2026-08-30.md`.
**Read that file first** — it is the source of truth and Andrew edits it
directly. This skill is the short form.

## Trigger

Ad hoc when Andrew asks to be briefed on a meeting, and automatically at 06:00
Brisbane on weekdays via the scheduled task "Daily Meeting Brief (6am weekdays)".

## Steps

1. **Identify the meeting(s).** `outlook_calendar_search` for the day, Brisbane
   time, `order: oldest`, paging `nextOffset`. Keep project meetings only: at
   least one attendee other than Andrew, not cancelled, not `showAs` oof/free,
   not all-day leave. Exclude GYM and solo entries.
2. **Match to the project folder** under `Projects - Documents\<YYYYNN>_<Name>`.
   Report an unmatched meeting as such rather than guessing.
3. **Read the project state** with `device_bash` — never stage files:
   - `00_ai_sandbox\Project_Summary_*.md` (say so if older than 30 days, or absent)
   - the most recent minutes for *this meeting series* under `07_Meeting Minutes`
   - **any transcript dated after those minutes.** Workshops held between
     meetings settle real items and are never minuted. This is usually where the
     closed column comes from.
4. **Scan email** since the last minutes (or 14 days, whichever is shorter) for
   what is genuinely new: decisions, figures, dates, claims, requests awaiting
   Andrew. Ignore transmittals.
5. **Compose and send** to andrew@bdmanagement.com.au, `bodyType: html`, subject
   `Meeting Brief — <Day> <D Month YYYY>`.

## Format — locked 31 Aug 2026, do not vary

Per meeting: one heading line (time, meeting, organiser, last minutes date and
number), one line naming only the declines and the new faces, then

- **Closed since the last meeting** — table: Item | Outcome | Source
- **Open** — table: Item | Position | With
- **Three for you** — at most three, each saying what to do and why it matters
  now; the only place recommendations appear
- one italic source line

Two tables and three bullets. No preamble, no background, no closing summary.

## What stays out

- **DA conditions, draft or issued.** They are a separate subset of actions that
  begins once formal approval is received and they belong in the DA conditions
  matrix — excluded even when a condition bears on a design item under discussion.
- Background Andrew already has: project history, consultant and fee registers,
  funding and valuation activity, unchanged project-summary content.
- Full attendee lists; recitals of the last minutes.

## Verification

Before sending, check:

- Every table row names a real source — a minute number, a meeting date, a dated
  email. No figure, date, name or reference that was not actually read.
- The Outcome column says what was **decided**, not what was discussed.
- Facts and advice are separate: tables are fact, "Three for you" is advice.
- No DA conditions anywhere in the body.
- Three bullets or fewer, and none of them restates an open-table row.
- The email is addressed to Andrew alone. Nothing was written to a project
  folder, no email was replied to, no meeting response was sent.
- If there are no project meetings, the email still goes, saying exactly that.
  A missing brief must mean a failed run, never a quiet day.