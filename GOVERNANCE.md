# Governance

How BDM skills are controlled. This document is Director-owned; changes to it
require Director approval and nobody else's.

---

## 1. Why this exists

BDM skills produce documents that go to Principals, financiers and contractors —
progress certificates, QS lender reports, consultancy agreements, monthly
reports. A defect in a skill is not a software bug. It is a defect in a
deliverable that BDM has put its name to.

Three things follow from that, and they are the whole of this document:

1. Skills draft. People sign.
2. There is one controlled copy, and it is this repository.
3. Every change is traceable to a Change Note and a named approver.

### Status of this repository — read this first

**This repository and the plugin distribution layer sit OUTSIDE the BDM QA
system.** Director decision, 2026-08-20. Until it is formally adopted:

- **No Change Notice is raised for work in here.** Not for restructuring, not
  for a plugin, not for a skill edit. Changes are recorded in `CHANGELOG.md` and
  in the commit history, and nowhere in the controlled estate.
- **The controlled location of record remains the SharePoint library**,
  `Standard - Documents\_AI Directory\2.0_Skills\`. That is what Form 007 AI
  Skills Register registers, and what the register's revisions describe. Where a
  skill here is ahead of the library, the library is what is controlled and this
  copy is not.
- **Controlled forms are unaffected.** Forms remain under full change control in
  `BDM TEMPLATES`, and skills resolve them from there (§5). Nothing in this
  decision loosens control over a BDM form.

This section is the first thing to change on adoption. Everything below it
describes the regime intended to apply from that point; §4 in particular is
written in the present tense but is not yet in force.

---

## 2. Roles

| Role | Who | May |
|---|---|---|
| **Repository owner** | `BentleyDevMngt` (BDM-controlled account) | Everything. |
| **Director** | Andrew Bentley | Approve and merge any change. Approve new skills, revisions and retirements. Sole approver for GOVERNANCE.md, CHANGELOG.md, the marketplace manifest and CI. |
| **Maintainer** | Nominated Senior PM | Commit routine work direct to `main` (§4). Raise a pull request for a major update, review others' work, run verification. Cannot merge their own pull request. |
| **Contributor** | Any BDM staff member | Commit routine work direct to `main` (§4). Raise a pull request for a major update, and report defects. |

The repository does not sit on any individual employee's personal account. If a
maintainer leaves BDM their collaborator access is removed and the repository is
unaffected.

### Plugin ownership

**BDM owns every plugin in this marketplace.** Ownership does not transfer with
authorship — a skill written by a Senior PM, a consultant or anyone else is BDM's
on the same terms as any other work product. `author` in every `plugin.json`
reads Bentley Development Management, never an individual, and the `owner` of the
marketplace is BDM.

Each plugin has a named **custodian**: the person who reviews changes to it and
whose sign-off the CHANGELOG records. The custodian is accountable for the
plugin, not the owner of it.

| Plugin | Custodian | Covers |
|---|---|---|
| `bdm-standards` | Director | House style, QA, PDF export, markup. Changes rarely; everything depends on it. |
| `bdm-contract-admin` | Senior PM — contract | AS4000 instruments. Contractual output; §4's separate-reviewer rule always applies. |
| `bdm-quantity-surveying` | QS lead | Area, cost and financier reporting. |
| `bdm-project-delivery` | Senior PM — delivery | Monthly reporting, approvals, minutes, records. Moves most often. |

### Why four plugins

The split is by **change cadence and custodian**, not by subject matter. Things
that move together and are reviewed by the same person share a version number.

`bdm-standards` is the foundation: the other three declare it in `dependencies`,
so Claude installs it automatically and it cannot be missing.

A fifth entry, **`bdm-all`**, ships no skills. Its manifest is a dependency list
on the other four, so a staff member installs one thing instead of four in a
required order, and the four thereafter move as a set. It is a distribution
convenience, not a fifth product: it has no custodian of its own and the release
workflow — not a person — keeps its version and its dependency ranges in step
with its children. That dependency is
the enforceable version of "install this one first", which had previously been a
line in a README that nothing checked. CI fails if a dependency names a plugin
this marketplace does not ship.

**Known limitation.** `BentleyDevMngt` is a GitHub *user* account, not an
organisation. Three consequences, recorded here rather than glossed over:

- There is one set of account credentials, held by BDM. Continuity depends on
  those credentials being recorded in BDM's password management, not on a
  second owner (§7).
- Teams do not exist, so CODEOWNERS can only name individual usernames.
- Protected branches on private repositories require a paid plan on a user
  account.

Converting the account to an organisation removes all three and is the intended
end state. Until then, this section describes what is actually in force.

---

## 3. What a skill may and may not do

**A skill may** read project documents, extract and reconcile figures,
populate a controlled BDM form, calculate, cross-check, flag inconsistencies,
and produce a DRAFT for review.

**A skill may not:**

- issue anything to a party outside BDM;
- send correspondence on the Director's or a PM's behalf;
- determine or approve a variation, extension of time, or payment;
- bind BDM or the Principal under contract;
- alter a controlled template;
- state a figure, name or date it has not verified against a source document.

Where a task heads towards any of the above, the skill stops and flags it.
This constraint is stated in every SKILL.md, not just here.

---

## 4. Change control

> **Not yet in force in its CN form.** See §1 — this repository sits outside the
> QA system by Director decision of 2026-08-20 and raises no Change Notices.
> Step 2 below is suspended until adoption. Everything else in this section
> **is** in force, as revised by the Director's ruling of 2026-09-01 — the
> second ruling of that date, which supersedes the blast-radius routing of the
> first.

### Director's ruling, 2026-09-01 — routine work goes straight to `main`

Work goes to `main`. That is the route, for almost everything.

The first ruling of 2026-09-01 divided the routes by blast radius and kept a
pull request for the marketplace manifest, CI and this file. In practice that
still put a browser round trip in front of ordinary work and left two routes to
remember. One route is simpler, and the simple one is the one that gets used.

| Change | Route |
|---|---|
| Anything routine — a skill, a template or script inside a skill, a README, this file, the marketplace manifest, a fix | **Commit direct to `main`.** |
| A **major update** | Branch, then pull request. |

A major update is one of:

- a plugin added or retired, or a skill added or retired;
- a MAJOR or MINOR version decision — a change to how a skill is *used*, as
  distinct from a correction to how it works;
- a restructure of the release machinery itself, meaning `.github/workflows/**`
  or `scripts/**`. CI validates every other change; it cannot validate the thing
  that does the validating, and a broken release workflow is the single change
  that stops every other change reaching staff.

**What controls the routine route is CI, not a reviewer.** `validate.yml` and
`release.yml` run on a direct push to `main` exactly as they do on a pull
request, and **a change that fails validation never gets a version, so
auto-update never carries it to staff.** Broken work stops in the workflow
rather than on somebody's job. That gate is real and it runs on every route; a
pull request its own author reviews and merges is not.

Review has not gone. It moved earlier — to before the commit, where the change
is still cheap to alter, rather than to a merge button after it is written. The
commit body carries what was verified.

On a major update, maintainers still cannot merge their own work (§2).

### The path a change takes

1. **Raise.** A defect, request or Director ruling is recorded.
2. **Allocate a Change Note.** *Suspended — see §1.* Applies only where the
   change also touches a controlled BDM form or Form 007. Confirm the real date
   before dating a CN; do not rely on a session's assumed date.
3. **Branch**, for a major update. Routine work commits straight to `main`.
4. **Change.** Scope discipline is a hard rule: incidental "improvements" to
   files the change does not name are rejected.
5. **Verify.** Per CONTRIBUTING. Verification is doing it, not intending to.
6. **Review.** For a major update: pull request, Director review, CODEOWNERS.
   For routine work: the check happens before the commit, and the commit body
   records what was verified.
7. **Release.** Automatic. See below.

### Release is automated, and that is a control

`.github/workflows/release.yml` owns version numbers and the CHANGELOG. On every
push to `main` it validates, identifies the plugins the commit actually changed,
raises their patch versions in `plugin.json` and `marketplace.json` together,
keeps the `bdm-all` bundle in step, writes the CHANGELOG entry and pushes it
back.

This replaced a manual step that failed silently. Auto-update ships a change
only when the version is raised; a merge that forgot the bump reached no one
while the repository looked current, and nothing in the system reported it. A
control nobody can see failing is not a control. This one leaves a workflow run,
a version, and a commit for every delivery.

**Nobody edits a patch version by hand.** MAJOR and MINOR remain human
decisions, set in the same commit as the change that justifies them.

### Versioning

Skills and plugins use `MAJOR.MINOR.PATCH`.

- **MAJOR** — the skill's output or trigger behaviour changes in a way that
  would surprise someone who used the previous version.
- **MINOR** — new capability, backwards compatible.
- **PATCH** — a fix with no behavioural change.

PATCH is raised by the release workflow, in `plugin.json` **and**
`.claude-plugin/marketplace.json` together. CI fails if they disagree, and fails
if a dependency range is ahead of the version a plugin actually ships.

MAJOR and MINOR are set by a person, in the commit that earns them.

### Retirement

A skill that is withdrawn is removed from `marketplace.json` entirely — it does
not linger as a disabled entry. The CHANGELOG records the retirement, the CN
and the reason. Git history retains the code.

---

## 5. Templates

**Templates are not in this repository.** Settled 2026-08-20. They stay in the
SharePoint `Standard - Documents\BDM TEMPLATES` library, under the Change Note
process that already controls them, and skills resolve them at run time.

The reason is single source of truth. BDM Standards revises a form once and
every skill picks it up. A copy of a controlled form committed here would be a
second controlled copy — the exact divergence this repository exists to end
(§6). A repository that carries its own templates starts telling a different
story from the register within one revision cycle.

**Resolution rule.** Take the highest revision of `NNN-Form_Name_R*.ext` from the
relevant `Working Copy` folder. Ignore `_Superseded`. Never hardcode a path
under a person's home directory — resolve from the current user's.

**Revision pinning.** Latest-wins alone means a form revision can silently break
a skill. So each skill records in its frontmatter the revision it was last
verified against:

```yaml
template_revision: R3
```

If the resolved template is **newer** than the recorded revision, the skill says
so and asks for a check before its output is relied on. It does not refuse to
run, and it does not proceed silently. When a form is revised, the template CN
names the affected skills; each is re-tested and its `template_revision` bumped
under its own CN.

**No exceptions remain.** The last one — an embedded master in
`bdm-monthly-project-report` — closed on 2026-08-20 when the form was issued as
**Form 260 Monthly Project Report R1** under CN-2026-033. No skill in this
repository carries a controlled artefact. CI enforces it: a binary anywhere
other than a skill's `templates/` or `assets/` folder fails the build, and there
are now no such folders in the repository at all.

---

## 6. Source of truth

This repository. Where it disagrees with a copy in a shared drive, a personal
machine, or an installed local cache, this repository wins and the other copy is
stale and must be re-synced.

Historically BDM skills existed in three divergent places at once. That is the
condition this repository exists to end. Do not reintroduce a second controlled
copy.

---

## 7. Access and continuity

- The repository is owned by `BentleyDevMngt`, a BDM-controlled account.
- The account credentials and its recovery method are recorded in BDM's
  password management, accessible to at least two Directors. On a user account
  this replaces the two-owners rule, which GitHub does not support here.
- Two-factor authentication is enabled, and the recovery codes are stored with
  the credentials — not on one person's phone.
- Collaborator access is reviewed when anyone joins or leaves.

**`main` is not technically protected, and this document will not pretend it
is.** Branch protection and rulesets on a *private* repository require a paid
plan — GitHub Pro on a personal account, or Team on an organisation. The account
is on neither as at 2026-08-20, by decision.

The consequences, stated plainly so they are managed rather than assumed away:

- Any collaborator can push directly to `main`. Since the ruling of 2026-09-01
  that is the intended route for routine work (§4) rather than merely a gap — but
  it also means nothing prevents a push that should have been a major-update pull
  request. On a private repository owned by a personal account, GitHub offers no
  read-only collaborator role — write is the only level available, so "read
  access" cannot be granted at all.
- CODEOWNERS and the pull request template are **advisory**. They record who
  should review; nothing enforces that they did.
- CI runs on every push and every pull request, but cannot block a merge. What
  it does control is release: a change that fails validation never gets a
  version, so it never reaches an installed account (§4).

Until the account is converted and a paid plan taken, the major-update review
rule in §4 is a professional undertaking between named people, not a technical
control. The routine route does not rely on it: CI is the control there. Anyone
given collaborator access is to be told that in those words.

---

## 8. Security

- No credentials, tokens, API keys or connection strings in the repository.
- No client project data, personal information, or commercially sensitive
  third-party material.
- The repository is **private**. It is internal BDM intellectual property.

---

*Approved by: Director, Bentley Development Management.*
