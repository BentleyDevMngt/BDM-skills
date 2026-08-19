# qs-initial-report

BDM skill: draft a QS Initial Report (Form 424) for a financier from a letter of
instruction and the project's "Information Received" folder. Produces a DRAFT .docx
for Senior PM / QS review with inline reviewer FLAGS, an outstanding-information
register and report-acceptance preconditions.

- `SKILL.md` — the playbook (workflow, authority boundary, requested-not-received logic).
- `scripts/build_initial_report.py` — deterministic builder (token fill, table cells,
  flag curation, DRAFT marker). Driven by a JSON content map authored per project.
- `references/template_map.md` — Form 424 table/placeholder map.
- `references/config_schema.md` — content-map JSON schema with examples.
- pilot config — held with the project, not in this skill.

Build: `python scripts/build_initial_report.py --template <424.docx> --config <map.json> --out <DRAFT.docx>`
