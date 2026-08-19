---
name: monthly-report-update
description: >
  Updates an existing Monthly Report Word document (.docx) for construction/development
  projects by comparing previous and current month's supporting documents, applying all
  changes with Track Changes visible, and adding Word comments referencing the source
  document for each update. Use this skill whenever a user asks to update, roll forward,
  or refresh a monthly report, lender report, funder report, project status report, or
  progress report from one month to the next. Also trigger when the user mentions
  comparing previous vs current month documents, updating a report with track changes,
  adding source-reference comments, or any combination of: monthly project update,
  funder/lender reporting, construction progress report, cost report review, and
  programme/delay reporting. Even if the user doesn't say "monthly report" explicitly,
  trigger if they ask to update a .docx report by reviewing a folder of supporting
  documents and showing what changed.
---

# Monthly Report Update Skill

Updates an existing Monthly Report Word document to reflect current-month project status
by cross-referencing supporting documents, applying tracked changes, and annotating each
change with a Word comment citing the source.

## Why this skill exists

Lenders require monthly project reports that clearly show what changed since last month.
The funder's credit team needs to see deletions and insertions (Track Changes) so they
can assess risk movement at a glance, and they need source references (Word comments)
so they can verify each update against the underlying documents. Doing this manually is
tedious and error-prone — this skill automates the full workflow while maintaining the
professional, funder-focused tone expected in construction finance reporting.

---

## Prerequisites

This skill depends on the **docx** skill for all Word document manipulation. Before
starting any work, read the docx SKILL.md to understand the unpack → edit XML → repack
workflow, tracked changes XML patterns, and comment insertion mechanics.

---

## Workflow Overview

The process has three phases, matching how the task naturally unfolds:

1. **Review & Compare** — Read all supporting documents, identify every data change
2. **Update with Track Changes** — Edit the report XML, showing all deletions and insertions
3. **Add Source Comments** — Attach a Word comment to each tracked change citing the source

---

## Phase 1: Review & Compare

### Locate the documents

The user will provide a folder (or set of folders) containing:

- The **existing Monthly Report** (.docx) — this is the file you'll edit
- **Previous month** supporting documents (baseline for comparison)
- **Current month** supporting documents (source of new data)

Typical supporting document types include (but aren't limited to):

| Document Type | What to extract |
|---|---|
| Cost Report (e.g. RLB, WT Partnership) | Budget, variations, contingency, % complete, cost to complete, forecast |
| Progress Claim | Works completed to date, retention held, net variations, claimed amount |
| PCG Report (contractor) | Programme dates, milestones, EOT claims, site progress, key risks |
| PCG Meeting Minutes | Decisions, actions, key discussion items, attendance |
| Trade Letting Register | Number of trades, values, procurement status |
| Programme / Gantt | PC date, critical path, milestone dates |
| Fee Schedules (PM/QS/CMA) | Fee totals, monthly distribution, any changes |
| Authority / Compliance docs | DA conditions, certifications, inspections |

### Extract and compare

For each supporting document:

1. Extract key data points (use the PDF skill or pandoc for text extraction)
2. Compare against the previous month's equivalent document
3. Note every material change — dates, dollar values, percentages, status descriptions, risk items

Create a working summary of all changes before touching the report. This prevents
missed updates and ensures consistency across sections.

### What constitutes a "material change"

Focus on changes the funder cares about:

- **Cost movements** — budget, variations, contingency adequacy, cost to complete
- **Programme/delays** — PC date shifts, EOT claims (submitted vs approved), milestone slippage
- **Risk escalation** — new risks, risks that have worsened, risks that have been mitigated
- **Procurement** — trade letting progress, percentage committed, key trades outstanding
- **Contractor performance** — site progress, quality issues, resource concerns
- **Cash flow** — drawdown position, funding requirements, retention

Things that typically don't change month-to-month (project description, contract
details, development approval reference numbers) should be left alone unless the
supporting documents show an actual change.

---

## Phase 2: Update with Track Changes

### Approach: Unpack → Edit XML → Repack

Follow the docx skill's editing workflow:

```bash
# 1. Unpack the existing report
python scripts/office/unpack.py report.docx unpacked/

# 2. Edit word/document.xml (the bulk of the work)

# 3. Repack
python scripts/office/pack.py unpacked/ updated_report.docx --original report.docx
```

### Track Changes XML structure

Every change must use `<w:del>` and `<w:ins>` elements as siblings of `<w:r>`, never
as children inside a run. This is the most common mistake — getting this wrong produces
a corrupt document.

The pattern for replacing text within a paragraph:

```xml
<!-- Before: original run -->
<w:r>
  <w:rPr><!-- formatting --></w:rPr>
  <w:t>old text here</w:t>
</w:r>

<!-- After: tracked change replacing the run -->
<w:del w:id="1" w:author="Claude" w:date="2026-04-01T00:00:00Z">
  <w:r>
    <w:rPr><!-- same formatting --></w:rPr>
    <w:delText>old text here</w:delText>
  </w:r>
</w:del>
<w:ins w:id="2" w:author="Claude" w:date="2026-04-01T00:00:00Z">
  <w:r>
    <w:rPr><!-- same formatting --></w:rPr>
    <w:t>new text here</w:t>
  </w:r>
</w:ins>
```

Key rules:

- **Preserve `<w:rPr>` formatting** — copy the original run's formatting block into both
  the deletion and insertion runs, otherwise you'll lose bold, font size, colour etc.
- **Use unique sequential IDs** — each `w:id` must be unique across the document. Use odd
  numbers for deletions and even for insertions to keep them paired and easy to track.
- **Set the date** to the current reporting month (e.g. first of the month).
- **Use "Claude" as author** unless the user specifies otherwise.
- **Replace entire `<w:r>` blocks** — don't try to surgically edit `<w:t>` content inside
  a run. Replace the whole run with a del/ins pair. This avoids the nesting trap.

### Handling edge cases

These came up repeatedly during development and are worth calling out:

1. **Text split across multiple `<w:t>` elements** — A single run may contain multiple
   `<w:t>` tags (e.g. due to `<w:lastRenderedPageBreak/>`). Merge all text into one
   `<w:delText>` when creating the deletion.

2. **Cover page date fields** — Cover pages often have runs containing both label text
   ("Date: ") and value text ("February 2026") in the same `<w:r>`. You need to close
   the first run after the label, then add the del/ins pair as siblings.

3. **`mc:Choice` / `mc:Fallback` blocks** — Some documents have compatibility markup
   with the same content at different indent levels. Both need updating.

4. **Unicode characters vs XML entities** — The unpacker converts smart quotes and
   en-dashes to XML entities (`&#x2019;`, `&#x2013;`). When searching for text to
   replace, match the entity form, not the Unicode character.

5. **Contractual dates vs reporting dates** — Don't change dates that are contractual
   (e.g. "Original Contract Date: 6th February 2026") — only change dates that refer
   to the reporting period or current status.

### What NOT to change

- Headings, section order, formatting, table structure
- Contractual/original dates and references (DA numbers, contract sums, etc.)
- Content that is still current and accurate
- Boilerplate text that doesn't vary month-to-month

---

## Phase 3: Add Source-Reference Comments

After all tracked changes are in place, add a Word comment to each insertion explaining
where the data came from. This is critical for funder due diligence — they need to be
able to trace every update back to a source document.

### Comment format

Keep comments concise and consistent:

```
Source: [Document Name], [Section/Page if helpful]
```

Examples:
- `Source: RLB Cost Report V008 – Executive Summary`
- `Source: PCG Report #4 – Programme & Progress section`
- `Source: Progress Claim #08_R1 – Summary page`
- `Source: PCG Meeting Minutes #4 – Item 3.2`
- `Source: Trade Letting Register – Updated 26/03/2026`

### Comment XML mechanics

Use the docx skill's `comment.py` script to create comment entries, then add markers
in `document.xml` anchored to the corresponding `<w:ins>` element:

```xml
<w:commentRangeStart w:id="300"/>
<w:ins w:id="102" w:author="Claude" w:date="...">
  <w:r><w:rPr>...</w:rPr><w:t>new text</w:t></w:r>
</w:ins>
<w:commentRangeEnd w:id="300"/>
<w:r>
  <w:rPr><w:rStyle w:val="CommentReference"/></w:rPr>
  <w:commentReference w:id="300"/>
</w:r>
```

Use comment IDs starting at 300 (or higher) to avoid collisions with tracked change IDs.

### Mapping comments to changes

Build a mapping table before inserting markers — for each comment, record:

- Comment ID (e.g. 300)
- The `w:id` of the `<w:ins>` element it should anchor to
- The source document reference text

This prevents mismatched markers, which are difficult to debug after the fact.

---

## Tone and Language

Write as an independent client-side Project Manager / Superintendent — not as an
advocate for the contractor. The audience is a lender's credit team who needs to
quickly assess:

- Is the project on track?
- Is their security position protected?
- Are costs under control?
- What risks need their attention?

Use concise, contractual, professional language. Avoid unnecessary adjectives or
contractor-friendly spin. If the programme is behind, say so directly. If contingency
is being eroded, flag it. The funder trusts this report because it's independent.

---

## Consistency Checks (Final Pass)

Before delivering, verify:

- All dates in the report align with the current reporting month
- Dollar figures are consistent across sections (e.g. "works completed" figure matches
  between the cost section and the progress section)
- Risk commentary reflects current status (no stale February language left in a March report)
- Percentage complete figures are consistent with cost data
- EOT / programme dates match across all references
- No orphaned references to the previous month remain unless still relevant

---

## Output

Deliver the updated .docx file with:

1. **Track Changes visible** — do NOT accept changes; leave them for funder review
2. **Word comments** on each tracked change citing the source document
3. **Clean validation** — run the docx skill's `validate.py` to confirm no corruption

The file should be ready to open in Word, review the tracked changes, and send to
the funder with a brief cover email summarising key updates and risks.


## Risk-rating colour (BDM standing drafting rule)

When inserting or updating any risk rating in the report (tracked changes), colour the rating word per the **BDM standing rule: LOW = green `1A4A2A`, MEDIUM = amber `9D7B5B`, HIGH = red `B91C1C`** (bold) — set the `<w:color w:val>` on the inserted run, the same mechanism used for dashboard badges in the bdm-project-status-report skill. Keep ratings consistent with this palette across the whole report.
