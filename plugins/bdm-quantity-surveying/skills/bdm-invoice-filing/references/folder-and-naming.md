# Folder standard, month numbering and migration state

Surveyed 30 August 2026 across 35 project folders in `Projects - Documents`.

## The standard

```
<project>\02_Project Control\1.0_Project Invoices\NN_Mon YYYY\yyyymmdd_Company_InvoiceNo.pdf
```

`_ New Job Folder` — the master new-job template — carries `1.0_Project Invoices`. That
is what makes it the standard rather than a preference.

## Migration state at issue

| State | Count | Meaning |
|---|---|---|
| `1.0_Project Invoices` present | 9 | Compliant, sweepable |
| `Invoices` only | 24 | Legacy — skipped until renamed |
| Neither present | 2 | `202301_145 Hedges Ave`, `202305_NAVINI, Bilinga` |

Full list: `Projects - Documents\Alfred\Invoice_Folder_Migration_List_2026-08-30.md`.

Every one of these folders was empty at survey. The migration is a folder rename only —
no files move.

**Never create `1.0_Project Invoices` alongside an existing `Invoices` folder.** Two live
destinations in one project is worse than one wrong destination, because neither is
complete and nobody can tell which to trust.

## Month numbering

Continuous from project start, never reset per year. The established pattern:

```
05_Consultants\04_Monthly Invoices\30_Jan 2025
                                   31_Feb 2025
                                   ...
                                   40_Nov 2025
```

Resolution order for the next `NN`: highest existing in `1.0_Project Invoices` → continue
the project's `04_Monthly Invoices` sequence → start at `01`. Never renumber an existing
folder.

Month tokens are pinned to `Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec`. Existing
folders contain `Sept`, `June` and `March`; do not propagate them.

The month is the **invoice issue month**, not the arrival month.

## Invoice numbers seen in practice

`INV-1485` · `71456` · `JB018010` · `G22068-DD16` · `3056` · `300250962` · `INV-0221` ·
`55024569`

There is no common format. Record what the issuer wrote. `NoNum` plus a flag where an
invoice genuinely carries none.

## Where invoices actually lived before this skill

- `00_Email Communication\` — as `.msg` message files, the de facto archive
- `05_Consultants\04_Monthly Invoices\NN_Mon YYYY\` — consultant fees on some projects
- `05_Consultants\05_Construction Invoices\` — Nera only
- `01a_Accounts\NN_Month YYYY\` — Everton Park only, and excluded

The `1.0_Project Invoices` folders were empty across the portfolio. This is a new filing
location, not an automation of an existing habit — which is why the back-capture question
is open rather than assumed.
