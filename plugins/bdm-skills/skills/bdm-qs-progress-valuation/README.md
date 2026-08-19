# bdm-qs-progress-valuation

Drafts a BDM **QS Monthly Progress Valuation Report (Form 425)** — the financier's monthly
drawdown report — from a building contractor's progress claim, the BDM valuation workbook, a
site inspection and the project documents.

- **SKILL.md** — when to trigger, the "faithful to the baseline template" golden rule, the
  authority boundary, the workflow and the verification checklist.
- **scripts/build_pv_report.py** — deterministic build from the latest 425 template + a JSON
  content map. Every populated cell **keeps the template's own font and size** (no formatting
  deviation). Fills all native tables, the Cost-to-Complete certificate, trade breakdown and
  variations, the S-curve cashflow chart, captioned site photos, bold-red expired dates; strips
  the template's drafting notes; and (with `compile_appendices`) appends the contractor's claim
  after the appendix dividers. Output is always a **DRAFT** for Senior PM / QS review.
- **references/template_map.md** — every table, paragraph, drafting note and media element.
- **references/config_schema.md** — the content-map JSON schema with examples.

Flag-free: the report carries no inline callouts or comments. Items the reviewer must confirm
go in the hand-over message. Always start from the **latest template working copy** — never roll
forward last month's report.
