# BDM Skills

Controlled Claude skills for Bentley Development Management — development
management, contract administration, quantity surveying and BDM document
standards.

> **This repository sits outside the BDM QA system.** Director decision,
> 2026-08-20. It raises no Change Notices, and the controlled location of record
> for skills remains the SharePoint library, `_AI Directory\2.0_Skills`, as
> registered in Form 007. See [GOVERNANCE.md](GOVERNANCE.md) §1 — that is the
> first thing to read here. Controlled **forms** are unaffected and remain under
> full change control in `BDM TEMPLATES`.

The intent is that this repository becomes the single source of truth for BDM
skills on adoption. It is not that yet.

---

## Status

**Staged, not yet signed off.** The 14 skills from the controlled
`_AI Directory/2.0_Skills` library are in, across four plugins at version
**0.1.0**. The leading `0.` is the point: they are here so they are under version
control and reviewable, not because they have been reviewed.

Still outstanding, deliberately:

- Director review and sign-off of each skill, after which the plugins go to
  1.0.0 and normal Change Note control begins — see GOVERNANCE §1 for what applies
  until then.
- **Merging the legacy `JamesBDM/bdm-plugins` repository** — 15 skills, of which
  10 have no counterpart here and five overlap. On some of the overlaps the
  legacy copy is the newer one. Direction of merge is decided per skill, not per
  repository, and with its author in the room.

---

## The four plugins

| Plugin | Skills | Covers |
|---|---|---|
| [`bdm-standards`](plugins/bdm-standards/README.md) | 1 | House style, QA, PDF export, markup. **The foundation — everything depends on it.** |
| [`bdm-contract-admin`](plugins/bdm-contract-admin/README.md) | 2 | AS4000 instruments — certificates, variations, EOTs, tender documents |
| [`bdm-quantity-surveying`](plugins/bdm-quantity-surveying/README.md) | 5 | Area, cost, financier reporting, progress claims |
| [`bdm-project-delivery`](plugins/bdm-project-delivery/README.md) | 6 | Monthly reporting, DA conditions, agreements, minutes, inspections |

Split by change cadence and custodian, not by subject — see
[GOVERNANCE.md](GOVERNANCE.md) §2. `bdm-standards` is thin at 0.1.0 because the
house style and PDF export skills arrive with the legacy merge.

---

## Installing

**Staff on the Claude desktop app** — install the `.plugin` bundles.
Step-by-step instructions are in [docs/INSTALL.md](docs/INSTALL.md). No GitHub
account or command line needed. Held until sign-off; do not circulate yet.

**From source**, for anyone with repository access:

```
/plugin marketplace add BentleyDevMngt/bdm-skills
/plugin install bdm-standards@bentley-dm
/plugin install bdm-quantity-surveying@bentley-dm     # pulls bdm-standards automatically
```

The marketplace is named **`bentley-dm`**, not `bdm`. The legacy repository also
declares `bdm`, and when two marketplaces share a name the second silently
overwrites the first with no error — so the name had to be unique.

The repository is private, so this route needs access on the `BentleyDevMngt`
account and a GitHub credential configured locally. Note that GitHub does not
offer read-only collaborators on a private personal repository; anyone added has
write access (GOVERNANCE §7).

Build the bundles with:

```
bash scripts/build_plugin.sh bdm-standards
bash scripts/build_plugin.sh bdm-quantity-surveying
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
│               ├── SKILL.md      frontmatter + instructions, + template_revision
│               ├── references/   detail Claude loads only when needed
│               └── scripts/      deterministic work, not left to the model
├── templates/skill-template/     copy this to start a new skill
├── scripts/validate_marketplace.py
├── GOVERNANCE.md                 who may change what, and how
├── CONTRIBUTING.md               how to add or revise a skill
└── CHANGELOG.md                  every release
```

Two names must agree or Claude will not load the skill: the folder name under
`skills/`, and the `name:` in the SKILL.md frontmatter.

---

## Ground rules

These are not style preferences. They are why the skills can be trusted.

**Skills draft; people decide.** No skill issues anything externally, binds BDM
or the Principal under contract, or determines a variation, EOT or payment.
Everything is held as a DRAFT for Director or Senior PM sign-off.

**Templates come from the controlled library, and never live here.** A skill
resolves the highest revision of its form from `BDM TEMPLATES\Working Copy` at
run time, ignoring `_Superseded`. It does not invent a layout, re-type a form
from memory, or carry its own copy. It records in `template_revision` the form
revision it was last verified against, and says so when it resolves a newer one
rather than picking it up silently.

**No invented figures.** A skill reports what the source documents say. Where a
figure, name or date cannot be verified, the skill flags it for input rather
than guessing.

**No client data, and no controlled forms, in this repository.** Skills carry
logic only. Forms live in the library; project files, claims, drawings and
correspondence stay in the job folder. CI rejects stray `.docx`, `.xlsx` and
`.pdf`, and there is no longer any folder in the repository where one is
permitted to sit.

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

**No Change Notice is raised for work in this repository** while it sits outside
the QA system. Changes are recorded in [CHANGELOG.md](CHANGELOG.md) and in the
git history. See [GOVERNANCE.md](GOVERNANCE.md) §1 for what that means and §4
for the process that applies from adoption, and
[CONTRIBUTING.md](CONTRIBUTING.md) for how to make a change.

A change that touches the **controlled estate** — a BDM form, the forms register,
the index — is a different matter and always carries a CN.

---

© Bentley Development Management. Internal use only — not licensed for
distribution outside BDM and its engaged consultants.
