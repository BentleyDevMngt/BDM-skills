# bdm-quantity-surveying

Quantity surveying and cost control — area measurement, financier reporting and
the money that flows through a job.

Depends on [`bdm-standards`](../bdm-standards/README.md).

**Version 0.1.0 — staged, not signed off.** Every skill here drafts and holds.
See [GOVERNANCE.md](../../GOVERNANCE.md) §4.

---

## Skills

| Skill | Produces | Form |
| --- | --- | --- |
| `bdm-floor-area-schedule` | Floor area schedule, live take-off tool and A3 markup PDF | 405 / 405a |
| `qs-initial-report` | Financier's pre-drawdown initial / costing report | 424 |
| `bdm-qs-progress-valuation` | Financier's monthly drawdown report | 425 |
| `progress-claim-update` | Head contract progress claim, rolled forward | — |
| `monthly-cost-report` | Consultant fee register for the period | 201 |

## Notes

`bdm-floor-area-schedule` carries `scripts/make_fixture.py` — a synthetic 1:100
drawing set measuring 228.0 m² by hand. Run it before trusting any change to the
take-off pipeline; it exercises the workbook, the live tool and the PDF export
end to end without a live job.

`progress-claim-update/projects/` holds a config file for a named live job
(202415 South Pine Rd). Retained so the skill still works, but per-project
configuration probably does not belong in a skills repository — open for the
Director at sign-off.
