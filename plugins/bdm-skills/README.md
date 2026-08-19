# bdm-skills

BDM's development management, contract administration and quantity surveying
skills, packaged as a single Claude plugin.

**Version 0.1.0 — staged, not signed off.** Nothing here has been reviewed. The
plugin is built so it can be reviewed as a whole and so the install path is
proven; it is not for distribution until the Director signs off and it goes to
1.0.0. See [GOVERNANCE.md](../../GOVERNANCE.md) §4.

---

## What it covers

| Skill | Produces | Form |
| --- | --- | --- |
| `bdm-consultancy-agreement` | Consultancy agreement from a consultant's fee proposal | 105 |
| `bdm-floor-area-schedule` | Floor area schedule, live take-off tool, A3 markup PDF | 405 / 405a |
| `bdm-monthly-project-report` | Client-side monthly report to the Principal | — |
| `bdm-qs-progress-valuation` | Financier's monthly drawdown report | 425 |
| `bdm-site-inspection-report` | Site inspection record from a OneNote export | 331 |
| `bdm-tender-clarification` | Tender clarification and addenda | — |
| `da-conditions-matrix` | DA conditions matrix from a Council decision notice | 240 |
| `datum-markup` | Drawing markup | — |
| `meeting-minutes-update` | Meeting minutes, rolled forward or first issue | — |
| `monthly-cost-report` | Consultant fee register for the period | 201 |
| `monthly-report-update` | Lender / funder monthly report, tracked changes | — |
| `progress-certificate-update` | Progress certificate as Superintendent, AS4000 cl.37.2 | 335 |
| `progress-claim-update` | Head contract progress claim, rolled forward | — |
| `qs-initial-report` | Financier's pre-drawdown initial / costing report | 424 |

Every one of them drafts and holds. None issues, and none signs.

---

## Known defects — blocking 1.0.0

Found on the portability audit of 2026-08-19, before packaging. Thirteen of the
fourteen skills carry no machine-specific references and will run on any staff
member's install. One will not:

**`bdm-floor-area-schedule`** — two faults, both in the live take-off tool:

1. `scripts/build_live_takeoff.py` is a working script from a single job, not a
   general tool. It hardcodes a sandbox session path, the source PDF for 79
   Seagull Avenue, that drawing's clip rectangle, its level-to-page map and its
   `plates/*.npy` masks, and it imports two modules (`takeoff`, `dawson_lines`)
   that are not in the folder. SKILL.md documents it as taking a `takeoff.json`
   argument. The two disagree, and the script will fail on first run for anyone.
2. `scripts/export_live_pdf.py` is referenced twice in SKILL.md and does not
   exist, so the third deliverable — the A3 markup PDF — cannot be produced.

The Form 405 workbook path and the validator are unaffected. The decision for
the Director is whether to repair the take-off tool before release or hold this
skill out of the 1.0.0 bundle and ship the other thirteen.

Also carried forward from the staging commit, unresolved:
`skills/progress-claim-update/projects/` holds a config file for a named live
job (202415 South Pine Rd). It is retained so the skill still works, but
per-project configuration probably does not belong in a skills repository.

---

## Installing

Staff install instructions are in [docs/INSTALL.md](../../docs/INSTALL.md).
Do not circulate them until the plugin is released.

## Building the bundle

```
bash scripts/build_plugin.sh
```

Writes `bdm-skills.plugin` — a zip of this directory — to `dist/`. The bundle is
a build output and is not committed; build it from the release tag.
