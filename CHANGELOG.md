# Changelog

Every release of a BDM skill or plugin, newest first. Each entry carries its
Change Note number. See [GOVERNANCE.md](GOVERNANCE.md) for the change process.

Format: `## CN-YYYY-NNN — YYYY-MM-DD` then Added / Changed / Fixed / Retired.

---

## Unreleased

### Added

- Repository scaffold: marketplace manifest, governance, contribution process,
  pull request template, CODEOWNERS, structural validator and CI.
- `.gitattributes` normalising line endings, which the legacy repository lacked.
- `bdm-skills` plugin at 0.1.0 — the 14 skills from `_AI Directory/2.0_Skills`,
  staged under version control ahead of Director review.
- `plugins/bdm-skills/README.md` — what the plugin covers, and the defects
  blocking 1.0.0.
- `scripts/build_plugin.sh` — builds a distributable `.plugin` bundle, with the
  structural checks the Claude CLI validator makes. Bundles go to `dist/`, which
  is ignored; release bundles are built from the release tag.
- `docs/INSTALL.md` — install and use instructions for staff on the Claude
  desktop app. **Held, not circulated**, pending sign-off.

### Notes

- **0.1.0 means staged, not signed off.** No skill in this release has been
  reviewed. Change Note control begins at 1.0.0.
- Skill folders take their name from the SKILL.md frontmatter, not the source
  folder, because Claude requires the two to match. Source revision numbers
  (`_R2_2026-08`) are therefore not in the paths; git history carries them
  instead.
- Packaged `.skill` bundles and the `_SS` staging folders were not brought in —
  they are build outputs, and source is what belongs under version control.
- Excluded: `__pycache__`, `.pyc`, and `_Variance_Log_2026-08-19.docx` (not part
  of any skill).
- Deferred to the review phase: reconciliation with `JamesBDM/bdm-plugins`,
  inconsistent `bdm-` prefixing across skill names, and whether these 14 stay as
  one plugin or split by domain.
- `plugins/bdm-skills/skills/progress-claim-update/projects/` carries a config
  file for a named live job (202415 South Pine Rd). Retained so the skill still
  works; flagged for a decision on whether per-project config belongs in a
  skills repository at all.
- Portability audit before packaging, 2026-08-19: 13 of the 14 skills carried no
  machine-specific references. `bdm-floor-area-schedule` did not — since repaired,
  see Fixed below. All 14 are now clean.

### Changed

- CI accepts controlled binaries in a skill's `assets/` folder as well as
  `templates/`, matching how the incoming skills are actually laid out.

### Fixed

- **`bdm-floor-area-schedule` — the live take-off tool made general, and the PDF
  exporter written.** `scripts/build_live_takeoff.py` was a working script from
  one job wearing a tool's documentation: hardcoded sandbox path, one project's
  drawings, clip and page map, and imports of two modules that were never in the
  folder, against a SKILL.md that documented a `takeoff.json` argument. It now
  reads the config, with the raster inputs in a new `live` block and the previous
  hardcoded values as defaults. `scripts/export_live_pdf.py`, referenced twice in
  SKILL.md and missing entirely, is written — headless Chromium calling the tool's
  own `buildPrint()` at 420 × 297 mm, failing loudly rather than substituting a
  hand-built PDF. The builder's name is out of the interface, the markup cover
  reconciles NSA and Apts from the config instead of printing dashes, and the
  status block prints `open_items` instead of seven bullets belonging to one job.
  Added `scripts/make_fixture.py` — a synthetic drawing set measuring 228.0 m² by
  hand — and verified the whole pipeline against it from a clean directory. The
  measurement method, standards citations and Form 405 tab map are unchanged. See
  the skill's CHANGELOG, R3.
