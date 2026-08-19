# Form 405 — Floor Area Schedule: tab and cell map

Template: `405-Floor_Area_Schedule_R*.xlsx` in
`…\BDM TEMPLATES\Working Copy\400 Quantity Surveying\` — always pull the highest
revision. Nine tabs, BDM branded, every formula wrapped in `IFERROR` so an
unstarted template shows blanks rather than `#DIV/0!`.

Companion: `405a-Area_Markup_Cover_R*.pdf` — the A3 markup cover sheet, produced
by `scripts/build_markups.py`.

---

## 1 · Summary — the one page that leaves the office

| Block | Rows | Notes |
|---|---|---|
| Header | 1–3 | Logo (A1), title (E1), project · address · DA ref (E2) |
| Intro | 5–7 | A5 form banner, A6 project line, **A7 states both authorities and the ±2% grade** |
| Areas by level | 9–16 | Cols: Level · FECA · UCA · **GFA (FECA+UCA · AIQS)** · **GBA (PCA / API / REIA)** · NSA · Apts. Row 16 = TOTAL |
| **Basis note** | **17** | **The GBA definition and its authority, quoted. Do not delete this row** |
| Apartment mix | 18–25 | Type · No. · % of total · Avg NSA · NSA range |
| Headline metrics | 27–37 | D28 total NSA · D30 NSA/GBA efficiency · D31 GFA (AIQS) · **D32 GBA (PCA / API / REIA)** · D33 planning GFA · D34 site area · D35 site cover · D36 plot ratio · D37 car spaces |
| Caveat | 39 | Pre-issue checks — site area, hand-check, architect's schedule, numbering |
| Pointer | 41 | The tabs behind the page |

Row 17 and the D31/D32 labels are the reference qualification. A Summary tab
that reports GBA without naming the Property Council / API / REIA *Glossary of
Property Terms* is incomplete.

## 2 · Level Schedule
Rows 9–13 the source block (drawings, approval, measurement basis, scale
verification, status). Row 15 headers, 16–21 levels, 22 TOTAL.
Columns: B FECA · C UCA · D GFA (=B+C) · E GBA · F unroofed balcony ·
**G planning-scheme GFA** · H apts · I enclosed-area GFA.
Rows 24–38 key ratios. Rows 40–44 the basis notes.

## 3 · Area by Category
Row 9 headers, 10–14 levels, 15 TOTAL.
Columns: B apartments · C core & circulation · D common amenity · E plant &
services · F car park & bike · G less light well · **H FECA (=SUM B:G)** ·
I balcony roofed (UCA) · J balcony unroofed · K external wall band ·
**L GBA (=H−G+I+J+K)**. Rows 17–25 explain what each category contains.

Every row must tie. This tab is the bridge between the segmentation and the
level schedule, and it is where a mis-classification shows up.

## 4 · Apartment Schedule
Rows 10–27 units, 28 TOTAL. Apt · Level · Position · Beds · Baths · Study ·
Media · Internal NSA · Balcony · TOTAL NSA (=H+N(I)).
Rows 30–37 reconcile apartments + core − light well = FECA, level by level.

## 5 · NSA & Revenue
Rows 10–27 units, 28 TOTAL. **Columns G and H are the blank rate columns** —
gold tinted, deliberately empty. This schedule measures area; it does not set
price. Rows 30–37 NSA summary and efficiency. Rows 39–45 NSA by level.

## 6 · Unit Mix
Grouped by bedroom count. Percentages reference the total cell, not a hard-coded
apartment count.

## 7 · Site & Parking
Site width / depth / area / max projection / site cover / plot ratios; bay
counts and ratios. Row 19 records how the site boundary was derived and whether
it is confirmed.

## 8 · Basis of Measurement
The audit trail. Sections:
1. Source and scale · 2. Definitions (AIQS / ASMM) · 3. Method ·
4. **Reliability table — item / confidence / note** · 5. Exclusions and open
items · 6. Recommended next step · **7. Standing of these definitions** —
the authority table from `references/measurement_standards.md`, plus the closing
statement of which GBA definition was used and any qualification.

Section 7 is the part a reader turns to when a figure is challenged. It is
generic — carry it forward verbatim.

## 9 · Verification
Twenty numbered checks: # · Check · Expected · Measured / found · Result.
Rows 9–28. Row 30 lists what was **not** verified.

Fill every row. A check that could not be closed is recorded as
`NOT VERIFIED — <what would close it>`, never left blank and never marked PASS.

---

## Filing and naming

- Working file → `…\00_ai_sandbox\<project>\`
- Final → the project's contract admin or feasibility folder
- Workbook: `<Project>_Floor_Area_Schedule_ASMM_DRAFT_<yyyymmdd>.xlsx`
- Markups: `<Project>_Area_Markups_ASMM_DRAFT_<yyyymmdd>.pdf`
- Config: `<project>_takeoff.json` — keep it; it is the measurement record and
  makes the next revision a re-run rather than a re-measure.
