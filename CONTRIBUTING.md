# Contributing

How to add or revise a BDM skill. Read [GOVERNANCE.md](GOVERNANCE.md) §1 and §4
first — they say who may merge what, and why this repository is stricter than a
normal code repository in some places and deliberately lighter in others.

---

## Before you start

**No Change Note is required for work in this repository.** GOVERNANCE §1 places
the repository and the plugin distribution layer outside the BDM QA system, and
that has been true since the Director's decision of 2026-08-20. An earlier
version of this page told you to get a CN allocated before you started. That
contradicted GOVERNANCE and it is withdrawn.

What still applies: if your change also alters a **controlled BDM form** in
`BDM TEMPLATES`, or a skill's entry in Form 007 AI Skills Register, *that* work
is inside the QA system and carries a CN in the normal way. Changing the skill
here does not.

---

## Which route your change takes

| What you are changing | Route |
|---|---|
| A skill, a template inside a skill, a script, a plugin README | **Director: commit straight to `main`.** Others: branch and raise a pull request. |
| `GOVERNANCE.md`, `.claude-plugin/marketplace.json`, anything in `.github/`, anything in `scripts/` | **Pull request, always** — including the Director's own. |

The reason for the split: a self-approved pull request is not a control, it is a
ceremony, and it was costing a browser round trip on every one-line fix. What
does the controlling here is CI plus the release workflow — both run on a direct
push to `main` exactly as they do on a pull request, and a change that fails
validation never gets a version, so it never reaches anyone's machine.

The files in the second row are the ones that can break distribution for every
installed account at once. Those keep a second pair of eyes.

---

## Setting up

```bash
git clone https://github.com/BentleyDevMngt/bdm-skills.git
cd bdm-skills
```

You need Python 3.11+ to run the validator. Nothing else.

**Push access.** Install **GitHub Desktop** and sign in once. It installs a git
credential helper, so `git push` works from the command line afterwards without
storing a token by hand. Without it you will hit
`could not read Username for 'https://github.com'` and be unable to push at all.

Use GitHub Desktop to commit and push. Do **not** use its
`Branch → Merge into current branch` on a pull request: that merges locally and
bypasses CI, the pull request number and the reviewer. Merges happen on
github.com.

---

## Adding a new skill

1. Copy the template into the right plugin:

   ```bash
   cp -r templates/skill-template plugins/<plugin>/skills/<skill-name>
   ```

2. Rename the folder to lower-kebab-case. The folder name and the `name:` in
   the frontmatter **must** match exactly, or Claude will not load the skill.

3. Write the frontmatter description. This is the single most important thing
   in the file — it is all Claude sees when deciding whether to use the skill.
   A good description names the trigger phrases someone would actually type,
   states what the skill produces, and states what it is **NOT** for so it does
   not fire over a neighbouring skill.

4. Write SKILL.md. Keep it to the procedure. Push detail into `references/`
   (loaded only when needed) and determinism into `scripts/` (anything with a
   right answer — arithmetic, file manipulation, numbering — belongs in code,
   not in prose the model has to follow).

5. Add the skill's controlled template to `templates/` inside the skill folder.

6. If the skill belongs to a **new plugin**, register the plugin in
   `.claude-plugin/marketplace.json` and add it to `bdm-all`'s `dependencies`.
   That is a marketplace change, so it goes via pull request.

7. Validate and verify (below).

---

## Revising an existing skill

Change **only** what you set out to change. If you notice something else wrong,
raise it separately — mixed-scope changes cannot be reviewed properly or
reverted cleanly.

**Do not touch version numbers.** They are no longer yours to set. See below.

---

## Versions and the CHANGELOG are automatic

`.github/workflows/release.yml` runs on every push to `main`. It validates,
works out which plugins your commit actually changed, raises the patch version
of each in **both** `plugin.json` and `marketplace.json`, keeps the `bdm-all`
bundle in step, writes the CHANGELOG entry, and pushes the result back.

This exists because the old manual bump had a silent failure mode. Auto-update
only ships a change when the version is raised. Forget the bump — or raise it in
one file and not the other — and the change reached nobody, with no error
anywhere: the repository looked current while every installed account stayed on
the old skill. Nothing reported that fault; someone eventually noticed a skill
behaving like last month's.

So: raise a version by hand and you will collide with the bot. Leave them alone.

**A minor or major bump** (a breaking change, or a new plugin) is still a human
decision. Set it in the same commit and say so in the commit message; the
workflow bumps the patch from whatever it finds.

---

## Validating

```bash
python scripts/validate_marketplace.py
```

Structural only. It proves the skill will *load*. It proves nothing about
whether the skill *works*.

---

## Verifying

Structural validation is not verification. Before you push to `main` or raise a
pull request:

- **Trigger test.** Start a fresh session and type the trigger phrases from the
  description. The skill should fire. Then type a phrase from a neighbouring
  skill — this one should stay quiet.
- **Output test.** Run the skill end to end on a real (de-identified) job. Open
  the result in Word or Excel. Check it opens without a repair prompt, the
  formatting holds, and tracked changes appear where they should.
- **Figure test.** Check the numbers against the source. Totals add. Dates,
  names, form numbers and revision references are right.
- **Boundary test.** Confirm the skill holds the draft and does not issue,
  determine or approve anything.

Record what you actually did — in the commit body for a direct push, in the
pull request for everything else. Do not tick boxes in advance.

---

## Confirming it reached everyone

A change is not delivered when it is merged. It is delivered when installed
accounts have it.

1. Open the **Release** workflow run on github.com. Its summary prints the
   published version of every plugin after the run.
2. On a machine that has the plugins, open **Customize → Plugins**, click the
   plugin, and read the version line — the plugin detail page is the only place
   the installed version is visible.
3. If the two disagree after a few minutes, the account's marketplace auto-sync
   is off. Turn it on in **Add marketplace**; a stale account never self-corrects.

---

## House rules

- **Scope discipline.** One change per commit.
- **No invented figures or metrics.** If it isn't in a source document or a
  prior revision, it doesn't go in.
- **No client data.** Templates and logic only. This repository is **public** —
  anything committed here is world-readable and stays retrievable in the git
  history after any tidy-up commit.
- **Verify the date.** Confirm today's real date before stamping a filename or
  an archival suffix.
- **Line endings.** `.gitattributes` handles this. If you see a diff where every
  line changed but nothing changed, your local git is fighting it — do not
  commit that.
