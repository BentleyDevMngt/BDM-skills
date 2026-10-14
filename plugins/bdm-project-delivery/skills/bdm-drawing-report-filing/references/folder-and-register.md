# Folder standard, discipline map and register conventions

Surveyed 14 October 2026 across the live project folders in `Projects - Documents`.

## Discipline folders — the New Job Folder standard

`_ New Job Folder\06_Drawings & Specifications\` carries these. The band name is the
discipline written on the Form 207 band row.

| Standard folder | Band name on the register |
|---|---|
| `01_Architecture` | ARCHITECTURE |
| `01a_Interior Design` | INTERIOR DESIGN |
| `02_Structural Engineering` | STRUCTURAL ENGINEERING |
| `02a_Wind Engineering` | WIND ENGINEERING |
| `03_Civil Engineering` | CIVIL ENGINEERING |
| `04_Electrical` | ELECTRICAL |
| `05_Mechanical` | MECHANICAL |
| `06_Hydraulic` | HYDRAULIC |
| `07_Landscape` | LANDSCAPE |
| `08_Traffic Report` | TRAFFIC |
| `09_Acoustic Report` | ACOUSTIC |
| `10_Energy Efficency` | ENERGY EFFICIENCY *(the folder is misspelt on the master; match it, do not create a corrected twin)* |
| `11_Building Certifier` | BUILDING CERTIFIER |
| `12_Surveyor` | SURVEY |
| `13_Geotechnical Report` | GEOTECHNICAL |
| `14_Fire Engineer FER` | FIRE ENGINEER |

## Project-specific folders seen in practice

Use the project's own folder whenever one exists for the discipline:

- `01_Architecture_ BDA`, `00_Architectural Updated 4.03.25` — Nera, Chevron
- `06a_Fire Sprinklers`, `02a_Pool Engineering`, `04_Electrical\_SS_JHA` — New Earth Health Club
- `04_Electrical & Fire` — Arc Residences
- `00_Transmittals` — 187-189 Jefferson Lane (issued BDM transmittals; not the register)

## Superseded sub-folders seen in practice

`_SS` (the standard), `SS`, `ss`, `_SS_<consultant>`. Use what the discipline folder already
has; create `_SS` only where there is none.

## Issue folders seen in practice

`yyyymmdd_<Issue name>` is the convention the existing Drawing & Report Filing task uses:
`20260226_Tender Issue`, `20261001_Bathhouse Remove`, `20260929_Cooridnation Issue` (sic). Older
folders use other patterns (`Amendments 27.5.26`, `20230722_Structural Updates`). Leave existing
folders as they are; never rename them.

Loose files sitting directly in a discipline folder (zips, single PDFs) were filed by people.
They are never moved by this skill.

## The register in practice

`187-189 Jefferson Lane\06_Drawings & Specifications\00_Transmittals\
BDM_DocumentTransmittal_187-189-Jefferson-Lane_TX-001.xlsx` (30 Aug 2026) shows the form in use:

- one row per drawing, reports included (geotechnical, NatHERS, survey, waterproofing spec);
- revision labels such as `13W`, `16W`, `P1`, `C1`, `VER 1`;
- `-` where a document carries no revision;
- all 18 date columns filled in five months (20/03/26 to 28/08/26).

That last point is why the register rolls its oldest date column off rather than adding columns.
Adding columns breaks the form's one-page-wide print within months.

That file is headed **Form 326**. Form 326 was retired and replaced by Form 207 under
CN-2026-042 (August 2026), so it is the same form under its earlier number. It is an issued
transmittal, so the skill never writes to it.

## Revision labels

Record exactly what the title block shows in CURRENT ISSUE (`REV 17`, `C`, `P3`, `VER 1`). Put a
short label of 4 characters or fewer in the grid (`17`). Never normalise one consultant's scheme
into another's. Order is by issue date only.
