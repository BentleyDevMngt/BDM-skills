# Form 201 register mechanics

How the workbook is built, and the failure modes that silently corrupt it.

## Contents
- [Sheets](#sheets)
- [Block layout](#block-layout)
- [Formulas](#formulas)
- [Cashflow columns](#cashflow-columns)
- [openpyxl failure modes](#openpyxl-failure-modes) ← read this before writing
- [Stale calcChain — the corrupt-file trap](#4-a-stale-xlcalcchainxml-makes-excel-call-the-file-corrupt) ← and this
- [Adding rows to a block](#adding-rows-to-a-block)
- [Cell comments](#cell-comments)
- [Print settings](#print-settings)

## Sheets

Three visible sheets. Older revisions (R3 and earlier) also carry `Controls` and `Calc` —
veryHidden leftovers from a feasibility model, referenced by nothing. Leave them alone.

| Sheet | Role |
|---|---|
| Cover Letter | Transmittal to the Principal. Date, addressee, project, period, total. |
| Professional Fees Summary | One row per discipline block, all formulas pointing at the Breakdown. |
| Professional Fees Breakdown | The data sheet. Everything is entered here. |

The Summary holds no data of its own — every cell is a reference to a Breakdown row. If a Summary
row reads zero when the Breakdown shows a figure, the reference is pointing at the wrong row.
That is the single most common defect after a structural edit, and it is invisible unless you
reconcile the block subtotals against the grand total.

## Block layout

The Breakdown is a stack of discipline blocks starting at row 9. Each block is:

```
row N        data row 1   ← discipline in col A, consultant in col B, stage in col C
row N+1      data row 2   ← col A and B empty; only col C onward
...
row N+d      spare row    (blank, inside the subtotal range so rows can be added later)
row N+d+1    Total row    ← "Total" in col C, SUBTOTAL formulas
row N+d+2    blank separator
```

So a block with `d` data rows occupies `d + 3` rows. After the last block comes one blank row,
then the grand TOTAL row.

Columns:

| Col | Contents |
|---|---|
| A | Discipline (first data row of the block only) |
| B | Consultant (first data row only) |
| C | Stage / line description |
| D | Approved Fee |
| E | Variation / Disbursements |
| F | Total (`=D+E`) |
| G | narrow spacer |
| H | Fees invoiced — total to date |
| I | Fees invoiced — previous |
| J | This month (`=H-I`) |
| K | Remaining (`=F-H`) |
| L | narrow spacer |
| M..AT | Cashflow forecast, one column per month |
| AU | Cashflow total (`=SUM(M:AT)`) |
| AX | Check (`=K-AU`) |

## Formulas

Per data row:
```
F{r} = D{r}+E{r}
J{r} = +H{r}-I{r}
K{r} = +F{r}-H{r}
AU{r} = SUM(M{r}:AT{r})
AX{r} = K{r}-AU{r}
```

Per block Total row, over `first:spare` (inclusive of the spare row):
```
= SUBTOTAL(9, {col}{first}:{col}{spare})
```

Grand TOTAL row, over the whole data area:
```
= SUBTOTAL(9, {col}8:{col}{GTOT-1})
```

`SUBTOTAL(9, …)` ignores nested SUBTOTALs, which is why the grand total can span every block
without double-counting the block totals. Preserve this — a plain `SUM` will double.

Summary row *i* maps to block *i*: columns A and B reference the block's **first data row**;
columns C, D, E, G, H, I, J reference the block's **Total row**.

## Cashflow columns

`M2:AT2` are period indices, `M3:AT3` are month dates, `M4:AT4` mirror the grand total row. Set
M3 to the project's first month and fill monthly across. Leaving the forecast unpopulated is fine
— it is a separate exercise needing a baselined programme — but say so in the notes rather than
leaving a reader to assume nil spend.

## openpyxl failure modes

Three traps. Each produces a file that opens without error and is wrong.

### 1. The header logo is stripped on every save

BDM templates carry the logo as a **page-header graphic** — the `&L&G` token in `<oddHeader>`.
The image lives in `xl/media/`, anchored by a `vmlDrawing` and a `<legacyDrawingHF>` element per
sheet, wired through the sheet `.rels`.

openpyxl does not model `legacyDrawingHF`. On save it drops the media, the drawings and the sheet
rels — but **keeps the `&G` token**. The workbook opens fine, looks right on screen, and prints
with no logo on any page.

Run `scripts/fix_header_logo.py <output.xlsx> <source.xlsx>` after **every** save. The source is
whichever file you took the logo from — the base register or the template.

Do not check branding by exporting a PDF through LibreOffice: it does not render header images at
all, so even a perfect file exports logo-less. Verify by inspecting the zip parts instead.

### 2. `unmerge_cells()` wipes cells

openpyxl's `unmerge_cells()` resets every non-top-left cell in the range to `None`. Register
templates carry merged note rows at the foot (`B{r}:H{r}` or `C{r}:H{r}`).

If you write new block data into rows that are still covered by an old merge and unmerge
afterwards, the unmerge **erases what you just wrote**. This has eaten an entire block's Total row
— the Breakdown looked fine, and the Summary quietly read $0 for that discipline.

Unmerge the old note ranges **first**, immediately after loading, before writing anything.

### 3. Cell comments and the header logo collide

Comments are written as `xl/comments*.xml` + a comments `vmlDrawing` + a `legacyDrawing` relation.
The header logo needs its own `vmlDrawing` + `legacyDrawingHF` relation. Both live in the same
part namespace, and Excel renumbers the parts freely on save — so on a sheet with comments, the
comment drawing and the header drawing sit side by side under unpredictable names.

A logo repair that overwrites `vmlDrawing{N}.vml` by name, or replaces the sheet rels wholesale,
**deletes every comment**. The bundled `fix_header_logo.py` avoids this: it resolves the header
drawing by following the source file's own `legacyDrawingHF` relationship, writes it under a fresh
name, and merges the rels rather than replacing them. Use it rather than writing your own.

Schema order matters too: `legacyDrawing` must precede `legacyDrawingHF` in the worksheet XML.

### 4. A stale `xl/calcChain.xml` makes Excel call the file corrupt

**This is the failure mode that has actually shipped, twice.**

`xl/calcChain.xml` is a precomputed index naming every cell that holds a formula. Rolling the
register forward turns formula cells into hard values constantly — and the index still names
them. Excel walks the chain on open, finds an entry pointing at a cell with no formula, and
reports unreadable content.

The reason it gets through: **openpyxl ignores calcChain entirely, and LibreOffice rebuilds it
silently on convert.** So the register passes an openpyxl load, passes a LibreOffice recalc,
passes `verify_register.py`'s content checks — and is still dead when the Director opens it.

Two related package defects travel with it:

- **stale `<dimension ref>`** — append rows past the declared used range and the sheet
  under-reports its extent;
- **orphaned shared formulas** — overwrite the master cell of an `<f t="shared" ref=".." si="N">`
  group and every dependent cell references an `si` with no master.

**Fix, and it is not optional:**

```bash
python scripts/validate_xlsx.py --repair  register.xlsx    # drops the stale calcChain
python scripts/validate_xlsx.py --check   register.xlsx    # must print CLEAN
```

`--repair` deletes `xl/calcChain.xml` along with its content-type override and its workbook
relationship. Excel rebuilds it on open; the file is smaller and correct. Cell values, formulas,
styles, drawings and media are untouched. `verify_register.py` now calls this check automatically,
but run `--repair` yourself before delivery — the verifier reports the defect, it does not fix it.

**Never certify a register off openpyxl or LibreOffice alone.**

## Adding rows to a block

openpyxl's `insert_rows()` does **not** adjust formulas. After inserting, rewrite every formula in
the affected area rather than trusting what shifted.

The reliable sequence:

1. Load the base workbook.
2. Unmerge the old note ranges (trap 2).
3. Capture a data-row style to copy onto new rows.
4. `insert_rows()` **bottom-up** so earlier row numbers stay valid while you work.
5. Apply the captured style to each new row.
6. Rewrite the whole data area from row 9 — values, per-row formulas, block subtotals, grand total.
7. Repoint every Summary row at its block's new first-data and Total rows.
8. Rewrite the notes and re-merge them.
9. Update print areas; shift manual page breaks by the number of rows inserted above them.
10. Save, then run the logo repair, then verify.

If the block count changes, the Summary needs a row inserting or deleting too — and its blank and
TOTAL rows move. Copy the styling from an adjacent Summary row onto any inserted row.

## Cell comments

```python
from openpyxl.comments import Comment
c = Comment(text, "BDM")
c.width, c.height = 380, 190      # block-level; ~340 x 120 for line-level
cell.comment = c
```

Size them — the default is small enough to truncate anything useful. Author as "BDM".

## Print settings

The user tunes these and expects them preserved: `page_setup.scale`, `orientation`,
`fitToHeight`/`fitToWidth`, `sheet_properties.pageSetUpPr.fitToPage`, `print_title_rows`,
`print_options.horizontalCentered`, `page_margins`, `print_area`, and manual `row_breaks`.

openpyxl preserves most of these across a load/save, but **print areas must be updated by hand**
when the content grows, and **manual page breaks must be shifted** by the rows inserted above
them. Verify against the base file before delivering — `verify_register.py` does this.
