---
name: skill-template
description: >
  One paragraph, and the most important thing in this file — it is all Claude
  sees when deciding whether to use this skill. Say what it produces, then list
  the phrases someone would actually type, then say what it is NOT for.
  Pattern - "Draft a BDM <deliverable> (Form NNN) from <inputs>. Trigger on
  'prepare/draft the <thing>', '<thing> for [project]', 'Form NNN', or whenever
  <input documents> are handed over with a request to <do the thing>. Produces
  a DRAFT .docx held for Director sign-off — never issued. NOT for <neighbouring
  deliverable> (use <other-skill>) or <another one>."
---

# <Skill name>

<One or two sentences: what this produces and who it is for.>

## When this fires

<The situations that should invoke it. Then, explicitly, the situations that
should not — naming the sibling skill that handles each instead. Boundaries
stop skills stealing each other's work.>

## Inputs

| Input | Required | Notes |
|---|---|---|
| | | |

<What to do when a required input is missing: ask, do not assume. Name the
specific thing you need.>

## Controlled template

- **Form:** <NNN — Name>
- **Revision:** <RN, YYYY-MM>
- **Location:** `templates/<file>`

Fill this form. Do not rebuild it, retype it from memory, or pick up a newer
revision without a Change Note.

## Procedure

1. **Locate and read the inputs.** <...>
2. **Extract and reconcile.** <...>
3. **Populate the form.** <...>
4. **Cross-check.** <Totals add. Dates, names and references match the source.>
5. **Flag what could not be verified.** <Inline, visibly. Do not guess.>
6. **Save as DRAFT.** <Naming convention.>

Anything with a single right answer — arithmetic, numbering, file
manipulation — belongs in `scripts/`, not in these instructions.

## Verification before handing over

- [ ] Every figure traces to a source document
- [ ] Totals add and reconcile to the source
- [ ] Dates, names, form number and revision are correct
- [ ] The file opens cleanly in the target application
- [ ] Tracked changes appear where they should
- [ ] Anything unverified is flagged, not guessed

## Boundaries

This skill produces a **DRAFT** and holds it. It does not issue the document,
send it to any external party, or determine or approve a variation, extension
of time or payment. If the task heads that way, stop and flag it for Director
sign-off.

## References

- `references/<file>.md` — <loaded only when needed>
