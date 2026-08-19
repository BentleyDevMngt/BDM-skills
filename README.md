# BDM Skills

Controlled Claude skills for Bentley Development Management — development
management, contract administration, quantity surveying and BDM document
standards.

This repository is the **single source of truth** for BDM skills. A skill that
is not here is not controlled, and its output must not be issued.

---

## Status

**Staged, not yet signed off.** The 14 skills from the controlled
`_AI Directory/2.0_Skills` library are in, as a single `bdm-skills` plugin at
version **0.1.0**. The leading `0.` is the point: they are here so they are
under version control and reviewable, not because they have been reviewed.

Still outstanding, deliberately:

- Director review and sign-off of each skill, after which the plugin goes to
  1.0.0 and normal Change Note control begins.
- Reconciliation with the legacy `JamesBDM/bdm-plugins` repository, which holds
  overlapping but not identical versions of several of these skills, plus nine
  others not in this library.
- Whether these 14 stay as one plugin or split by domain. One plugin for now,
  so the grouping is not prejudged ahead of that review.

---

## Installing

**Staff on the Claude desktop app** — install the `bdm-skills.plugin` bundle.
Step-by-step instructions are in [docs/INSTALL.md](docs/INSTALL.md). No GitHub
account or command line needed. Held until sign-off; do not circulate yet.

**From source**, for anyone with repository access:

```
/plugin marketplace add BentleyDevMngt/bdm-skills
/plugin install bdm-skills@bdm
```

The repository is private, so this route needs read access on the
`BentleyDevMngt` account and a GitHub credential configured locally.

Build the bundle with:

```
bash scripts/build_plugin.sh
```

---

## Layout

```
bdm-skills/
├── .claude-plugin/
│   └── marketplace.json          the plugin index Claude reads
├── plugins/
│   └── <plugin-name>/
│       ├── .claude-plugin/
│       │   └── plugin.json       name, version, description
│       ├── README.md             what the plugin covers
│       └── skills/
│           └── <skill-name>/
│               ├── SKILL.md      frontmatter + instructions
│               ├── references/   detail Claude loads only when needed
│               ├── scripts/      deterministic work, not left to the model
│               └── templates/    the controlled BDM form the skill fills
├── templates/skill-template/     copy this to start a new skill
├── scripts/validate_marketplace.py
├── GOVERNANCE.md                 who may change what, and how
├── CONTRIBUTING.md               how to add or revise a skill
└── CHANGELOG.md                  every release, by Change Note
```

Two names must agree or Claude will not load the skill: the folder name under
`skills/`, and the `name:` in the SKILL.md frontmatter.

---

## Ground rules

These are not style preferences. They are why the skills can be trusted.

**Skills draft; people decide.** No skill issues anything externally, binds BDM
or the Principal under contract, or determines a variation, EOT or payment.
Everything is held as a DRAFT for Director or Senior PM sign-off.

**Templates come from the controlled library.** A skill fills the current
controlled BDM form. It does not invent a layout, re-type a form from memory,
or silently update to a newer revision without a Change Note.

**No invented figures.** A skill reports what the source documents say. Where a
figure, name or date cannot be verified, the skill flags it for input rather
than guessing.

**No client data in this repository.** Skills carry templates and logic only.
Project files, claims, drawings and correspondence stay in the job folder. CI
rejects stray `.docx`, `.xlsx` and `.pdf` outside a `templates/` folder.

---

## Validating locally

```bash
python scripts/validate_marketplace.py
```

Checks that the manifest parses, every listed plugin exists, versions agree
between `marketplace.json` and each `plugin.json`, every skill has SKILL.md
frontmatter with a matching name and a usable description, and that no plugin
directory has been left out of the manifest. CI runs the same script on every
push and pull request, plus JSON, Python-compile, line-ending and stray-document
checks.

---

## Change control

Every change to a controlled skill carries a Change Note number from the
MasterRegister and is recorded in [CHANGELOG.md](CHANGELOG.md). See
[GOVERNANCE.md](GOVERNANCE.md) for who may approve what, and
[CONTRIBUTING.md](CONTRIBUTING.md) for how to make the change.

---

© Bentley Development Management. Internal use only — not licensed for
distribution outside BDM and its engaged consultants.
