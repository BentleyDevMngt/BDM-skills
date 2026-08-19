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

## Portability

All fourteen skills carry no machine-specific references and will run on any
staff member's install. Audited 2026-08-19, re-checked after the repair below.

### Repaired — `bdm-floor-area-schedule`, 2026-08-20

The audit found the skill could not have run anywhere but the machine it was
written on. `build_live_takeoff.py` was a single-job working script — hardcoded
sandbox path, one project's drawings, two imports of modules that were never in
the folder — while SKILL.md documented it as a config-driven tool; and
`export_live_pdf.py`, which SKILL.md referenced twice, did not exist, so the A3
markup set could not be produced at all.

Both are fixed. The tool now reads the take-off config as documented, the
exporter is written, and a synthetic fixture (`scripts/make_fixture.py`) lets
the whole pipeline be run and checked against a hand-worked 228.0 m² without a
live job. The measurement method, the standards citations and the Form 405 tab
map are untouched. Detail in the skill's own
[CHANGELOG](skills/bdm-floor-area-schedule/CHANGELOG.md).

---

## Open — for the Director at sign-off

Carried forward from the staging commit, unresolved:
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
