# Contributing

How to add or revise a BDM skill. Read [GOVERNANCE.md](GOVERNANCE.md) first —
it explains why this process is stricter than a normal code repository.

---

## Before you start

Get the change agreed and a **Change Note number** allocated. Work without a CN
does not get merged. If you are unsure whether something needs a CN: a change to
anything under `plugins/` does; a typo in this file does not.

---

## Setting up

```bash
git clone https://github.com/BDMANAGEMENT/bdm-skills.git
cd bdm-skills
git checkout -b cn-2026-0NN-short-description
```

You need Python 3.11+ to run the validator. Nothing else.

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

6. Register the plugin in `.claude-plugin/marketplace.json` if it is new.

7. Validate and verify (below).

---

## Revising an existing skill

Change **only** what the Change Note describes. If you notice something else
wrong, raise it separately — do not fold it in. Mixed-scope pull requests are
rejected because they cannot be reviewed properly or reverted cleanly.

Bump the version in `plugin.json` and `marketplace.json` together, and add the
CHANGELOG entry.

---

## Validating

```bash
python scripts/validate_marketplace.py
```

This is structural only. It proves the skill will *load*. It proves nothing
about whether the skill *works*.

---

## Verifying

Structural validation is not verification. Before you raise the pull request:

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

Record what you actually did in the pull request. Do not tick boxes in advance.

---

## Raising the pull request

Push the branch and open a pull request against `main`. Fill in the template
honestly — an unchecked box with an explanation is far more useful than a
checked box that isn't true.

Director review is required. CI must pass. Merges are squashed so `main` reads
one commit per Change Note.

---

## House rules

- **Scope discipline.** Change what the CN says, nothing else.
- **No invented figures or metrics.** If it isn't in a source document or a
  prior revision, it doesn't go in.
- **No client data.** Templates and logic only.
- **Verify the date.** Confirm today's real date before stamping a CN, a
  filename or an archival suffix.
- **Line endings.** `.gitattributes` handles this. If you see a diff where every
  line changed but nothing changed, your local git is fighting it — do not
  commit that.
