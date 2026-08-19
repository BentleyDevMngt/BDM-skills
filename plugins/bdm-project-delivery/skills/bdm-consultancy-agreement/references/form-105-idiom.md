# Form 105 — placeholders and XML idiom

## Placeholders in the controlled template

Cover table: `[Project name and address]`, `[BDM project number]`,
`[Consultant discipline — e.g. Surveying, Civil Engineering]`, `[Consultant name]`,
`[Agreement date]`, `[Draft  ·  For Execution  ·  Executed]`

Parties: `[Principal entity — full legal name]`, `[Principal ACN]`,
`[Principal registered office address]`, `[Principal postal address]`,
`[Consultant entity — full legal name]`, `[Consultant ABN]`, `[Consultant office address]`

Body / Annexure 1: `[date to be inserted]`,
`[Site address — e.g. Lot X on RPXXXXX, Street, Suburb]`, `[Project name / site address]`,
`[Key personnel and roles — to fill]`, `[Project Title]`,
`[Principal payment-notification email]`

Annexure 2: `[Insert Consultant’s proposal: scope of services + fees]`

Note the em-dashes and curly apostrophes — match them exactly, and HTML-escape when
substituting into XML.

## Editing method

`unzip` → `merge_runs.py` → edit `word/document.xml` → `zip -Xr` → `validate.py --original`.
python-docx will not preserve the header graphics and table shading; edit the XML.

## Element order (schema-enforced — validation fails otherwise)

`<w:pPr>`: keepNext, pBdr, **spacing, then ind**, jc
`<w:rPr>`: rFonts, b, bCs, i, iCs, smallCaps, color, **spacing**, sz, szCs

## Run properties — inherit, don't specify

The controlled template carries **no** `w:rFonts` in `document.xml`; Calibri comes from
`styles.xml`. Emit runs without `rFonts` so they inherit. If you find yourself writing
`w:ascii="Aptos"`, you are on the wrong template.

Any `<w:t>` with leading or trailing spaces needs `xml:space="preserve"`.

## Section heading (matches EXECUTION / ANNEXURE headings)

```xml
<w:p><w:pPr><w:keepNext/>
  <w:pBdr><w:bottom w:val="single" w:sz="8" w:space="4" w:color="0F1721"/></w:pBdr>
  <w:spacing w:before="320" w:after="100"/></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/><w:smallCaps/><w:color w:val="0F1721"/>
    <w:spacing w:val="36"/></w:rPr><w:t>HEADING</w:t></w:r></w:p>
```

## Table conventions

Table width 9412 dxa; column widths must sum to it. Cell margins top/bottom 80, left/right
140. Cell borders: top and bottom `single sz=4 D9D9D9`, left and right `none FFFFFF`.

- Header row: `<w:tblHeader/>`, fill `0F1721`, runs bold white at `sz 16`.
- First-column / TOTAL row emphasis: fill `F4F4F1`, bold. Per the R3 brand standard gold
  is accent-only — never a fill behind white text or a table header.
- Give the first column enough width for its longest label; `TOTAL` bold needs ~1250 dxa.
