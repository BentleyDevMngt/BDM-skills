# BDM Monthly Project Report

Produces the client-side Monthly Project Report to the Principal — six pages: cover,
a three-page body numbered 1.0 to 7.0, and Annexures A and B.

Supersedes `bdm-project-status-report` (R3), whose one-page Project Summary Report
format is retired.

## The rule that governs everything

The report **synthesises existing project information and creates none of its own**.
Every statement traces to a named source with version and date. A figure with no source
becomes an action in Annexure B. Conflicts between sources are reported, not resolved.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The skill |
| Form 260 (in `BDM TEMPLATES\Working Copy\200 Project Management - Pre-Contract\`) | The controlled master. Resolved at run time, never carried here. |
| `references/source-to-section-map.md` | Intake checklist — which document feeds which section |
| `references/template_map.md` | Word structure, tables, placeholders, typography |
| `scripts/tracked_changes.py` | lxml helper for tracked-change insert/delete pairs |
| `CHANGELOG.md` | What changed and why |

## Not this skill

- Monthly report to a **financier / lender** → `monthly-report-update`
- QS Initial or Progress Valuation → `qs-initial-report` / `bdm-qs-progress-valuation`
- Progress Certificate → `progress-certificate-update`
- Meeting minutes → `meeting-minutes-update`

The distinction is audience: this report is for the **Principal**.
