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

---

## 2. Roles

| Role | Who | May |
|---|---|---|
| **Repository owner** | `BentleyDevMngt` (BDM-controlled account) | Everything. |
| **Director** | Andrew Bentley | Approve and merge any change. Approve new skills, revisions and retirements. Sole approver for GOVERNANCE.md, CHANGELOG.md, the marketplace manifest and CI. |
| **Maintainer** | Nominated Senior PM | Raise pull requests, review others' work, run verification. Cannot merge their own work. |
| **Contributor** | Any BDM staff member | Raise pull requests and report defects. |

The repository does not sit on any individual employee's personal account. If a
maintainer leaves BDM their collaborator access is removed and the repository is
unaffected.

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

Every change to a controlled skill follows the same path.

1. **Raise.** A defect, request or Director ruling is recorded.
2. **Allocate a Change Note.** The next CN number from the MasterRegister.
   Confirm the real date before dating the CN — do not rely on a session's
   assumed date.
3. **Branch.** `cn-YYYY-NNN-short-description` off `main`.
4. **Change.** Only what the CN describes. Scope discipline is a hard rule:
   incidental "improvements" to files the CN does not name are rejected.
5. **Verify.** Per the pull request checklist. Verification is doing it, not
   intending to.
6. **Review.** Pull request, Director review, CODEOWNERS enforced.
7. **Merge and record.** Squash to `main`; CHANGELOG.md updated with the CN.

### Versioning

Skills and plugins use `MAJOR.MINOR.PATCH`.

- **MAJOR** — the skill's output or trigger behaviour changes in a way that
  would surprise someone who used the previous version.
- **MINOR** — new capability, backwards compatible.
- **PATCH** — a fix with no behavioural change.

A version is bumped in `plugin.json` **and** `.claude-plugin/marketplace.json`
together. CI fails if they disagree.

### Retirement

A skill that is withdrawn is removed from `marketplace.json` entirely — it does
not linger as a disabled entry. The CHANGELOG records the retirement, the CN
and the reason. Git history retains the code.

---

## 5. Templates

Skills fill controlled BDM forms. The form itself is controlled in the BDM
template library, not here; a skill carries a copy for the revision it was
built and tested against.

When a form is revised, the skills that fill it are **not** automatically
updated. The template revision CN identifies the affected skills, and each is
re-tested and re-issued under its own CN. A skill silently picking up a new form
revision is a defect, not a convenience.

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
- `main` is protected: no direct pushes, pull request and Code Owner review
  required, CI must pass.

---

## 8. Security

- No credentials, tokens, API keys or connection strings in the repository.
- No client project data, personal information, or commercially sensitive
  third-party material.
- The repository is **private**. It is internal BDM intellectual property.

---

*Approved by: Director, Bentley Development Management.*
