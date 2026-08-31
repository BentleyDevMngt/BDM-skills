# Changelog

Every release of a BDM skill or plugin, newest first.

**This repository sits outside the BDM QA system** by Director decision of
2026-08-20 and raises no Change Notices — see [GOVERNANCE.md](GOVERNANCE.md) §1.
Until it is adopted, this file and the git history are the whole record. A CN
number appears here only where a change touched the controlled estate, which is
a different thing from changing this repository.

Format from adoption: `## CN-YYYY-NNN — YYYY-MM-DD` then Added / Changed /
Fixed / Retired. Until then, dated entries under `## Unreleased`.

---

## Unreleased

### Changed — distribution moves to the marketplace, and dependency resolution is repaired

**No Change Notice.** Director decision of 2026-08-20; see §1 above.

Director ruling of 2026-08-31: the `bentley-dm` marketplace is the distribution
route for BDM plugins. The packaged `.plugin` files become a fallback for cases
where the marketplace is unavailable. The reason is that an installed `.plugin`
file is a frozen copy — it never updates — whereas a marketplace with
auto-update enabled moves installed plugins to the current version on its own.

- **`dependencies` corrected from an object to an array** in
  `bdm-contract-admin`, `bdm-quantity-surveying` and `bdm-project-delivery`.
  All three declared `"dependencies": { "bdm-standards": "^0.1.0" }`, which is
  npm's shape, not Claude's. The documented schema is an array of entries. As
  written the declaration did nothing, so `bdm-standards` would not have been
  pulled in automatically despite every README saying it would be.
- **Constraint widened to `>=0.2.0`** rather than `^0.2.0`. On a `0.x` version a
  caret range stops at the next minor, so `^0.2.0` would have had to be edited
  in three manifests every time `bdm-standards` took a minor bump.
- **All four plugins raised to `0.2.0`**, in both `plugin.json` and the
  marketplace entry. Auto-update only ships a change when the version is raised,
  so from here **every push intended to reach installed accounts must carry a
  version bump in both files.** A push without one is invisible to users.
- **`scripts/validate_marketplace.py` corrected.** The validator itself
  asserted the npm object shape and raised `dependencies must be an object of
  name -> version range`, so it had been actively certifying the defect. It now
  enforces the array schema, accepts both the bare-string and `{name, version}`
  entry forms, rejects unknown fields, and skips cross-marketplace entries it
  cannot resolve.
- **`docs/INSTALL.md` rewritten** around the marketplace route, including the
  auto-update toggle, which is **off by default** for non-Anthropic
  marketplaces. The old note that the repository route required collaborator
  access no longer holds — the repository is public.

Version constraints resolve against git tags named `{plugin}--v{version}`, and
this repository carries none. For plugins referenced by relative path, as these
are, Claude falls back to the marketplace's current copy and checks the
constraint at load, so tagging is not yet blocking. It will be if a plugin is
ever moved to its own repository.

### Added — two skills carried in from the running Claude account

**No Change Notice.** Director decision of 2026-08-20; see §1 above.

The Director's Claude account ("Alfred") runs 14 BDM skills. Twelve of them already
exist in this repository. The two that do not are added here, unmodified:

- **`bdm-invoice-filing`** → `plugins/bdm-project-delivery/skills/`. Sweeps the
  mailbox for project invoices and files them under the BDM naming convention.
  Files and logs only — it never assesses, approves or registers. Staged under
  `bdm-quantity-surveying` and moved on the Director's ruling of 2026-08-31:
  filing to the job folder is delivery record-keeping, not cost control.
- **`bdm-meeting-brief`** → `plugins/bdm-project-delivery/skills/`. Builds the
  Director's pre-meeting brief. Held open: it is a stub that depends on a procedure
  file outside this repository — see the plugin README.

### Not changed — the other twelve skills

The running account copies were compared file by file against this repository before
anything was written. **On every skill that differed, this repository is the newer
side**, so nothing was overwritten:

| Skill | Account copy | This repository |
|---|---|---|
| `bdm-floor-area-schedule` | R2 — `build_live_takeoff.py` still hardcoded to one job; no `export_live_pdf.py`, no `make_fixture.py` | R3, repaired at `e3bc0f8` |
| `bdm-monthly-project-report` | carries the embedded master `.docx`; SKILL.md predates the Form 260 decision | master removed, resolves Form 260 at run time |
| `bdm-site-inspection-report` | names a live project and a personal Windows profile path | sanitised |
| `qs-initial-report` | example config names a live project, financier, developer and builder | sanitised |
| the other eight | byte-identical | byte-identical |

Nine skills carry a stale `scripts/__pycache__/` in the running account. Ignored here
by `.gitignore`; not imported.


### Changed — repository restructured into four plugins

**No Change Notice.** Director decision of 2026-08-20 places this repository and the
plugin layer outside the QA system until formally adopted, so work here is recorded
in this file and in git, and nowhere in the controlled estate. The CN-2026-034 draft
raised for this work was withdrawn; the number returns to the pool.

Director decisions of 2026-08-20. The single `bdm-skills` plugin is retired as a
container; its 14 skills are redistributed, unchanged, across four plugins split
by change cadence and custodian rather than by subject:

| Plugin | Skills | Custodian |
|---|---|---|
| `bdm-standards` | 1 | Director |
| `bdm-contract-admin` | 2 | Senior PM — contract |
| `bdm-quantity-surveying` | 5 | QS lead |
| `bdm-project-delivery` | 6 | Senior PM — delivery |

- **No skill was edited.** Every file moved with `git mv`; the tracked-file list
  before and after differs only by the four new `plugin.json` and `README.md`
  pairs replacing the one they supersede.
- **The three domain plugins declare `dependencies: {"bdm-standards": "^0.1.0"}`.**
  Claude installs the foundation automatically, so "install this one first" is
  enforced rather than being a line in a README. CI now fails if a dependency
  names a plugin the marketplace does not ship — verified with a negative test.
- **Marketplace renamed `bdm` → `bentley-dm`.** The legacy `JamesBDM/bdm-plugins`
  marketplace also declares `bdm`, and where two marketplaces share a name the
  second silently overwrites the first with no error and no way to qualify an
  install. The name had to be unique.
- **Templates: SharePoint resolution confirmed as policy** (GOVERNANCE §5),
  matching the rule already set in CN-2026-033 — a skill never carries its own
  copy of a controlled form; it resolves the highest revision from `Working Copy`
  at run time, ignoring `_Superseded`. Added revision pinning: a skill records
  the revision it was last verified against and says so when it resolves a newer
  one, rather than picking it up silently.
- **The last embedded master is gone.** `bdm-monthly-project-report` carried
  `assets/BDM_Monthly_Project_Report_MASTER_R1_2026-08.docx` because the form had
  no number. It was issued into the controlled library as **Form 260 Monthly
  Project Report R1** under CN-2026-033 on 2026-08-20; the copy here is deleted
  and the skill resolves Form 260 at run time, pinned to R1 in its frontmatter.
  No skill in this repository now carries a controlled artefact, and there is no
  `assets/` or `templates/` folder left for one to hide in.
- **GOVERNANCE §7 corrected.** It claimed `main` was protected by pull request
  and Code Owner review. It is not — branch protection on a private repository
  needs a paid plan, and the account is on none by decision. The section now
  states what is actually in force, including that GitHub offers no read-only
  collaborator on a private personal repository, so any collaborator has write
  access to `main`.
- **CI now reports package conformance** against the CN-2026-033 convention
  (SKILL.md + README.md + INSTALL.md + CHANGELOG.md) as warnings. 3 of 14
  conform today; CN-2026-033 records the estate as largely non-conformant and
  brings each skill up at its next revision, so this warns rather than fails.

### Added

- Repository scaffold: marketplace manifest, governance, contribution process,
  pull request template, CODEOWNERS, structural validator and CI.
- `.gitattributes` normalising line endings, which the legacy repository lacked.
- `bdm-skills` plugin at 0.1.0 — the 14 skills from `_AI Directory/2.0_Skills`,
  staged under version control ahead of Director review.
- A README per plugin — what it covers, its custodian, and what is outstanding.
- `scripts/build_plugin.sh` — builds a distributable `.plugin` bundle, with the
  structural checks the Claude CLI validator makes. Bundles go to `dist/`, which
  is ignored; release bundles are built from the release tag.
- `docs/INSTALL.md` — install and use instructions for staff on the Claude
  desktop app. **Held, not circulated**, pending sign-off.

### Notes

- **0.1.0 means staged, not signed off.** No skill in this release has been
  reviewed. Change Note control begins when the repository is adopted into the
  QA system, and the plugins go to 1.0.0.
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
- `plugins/bdm-quantity-surveying/skills/progress-claim-update/projects/` carries a config
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
