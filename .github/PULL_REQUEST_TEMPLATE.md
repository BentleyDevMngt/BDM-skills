<!--
Pull requests are for MAJOR UPDATES only (GOVERNANCE §4, ruling of 2026-09-01):
a plugin or skill added or retired, a MAJOR or MINOR version decision, or a
restructure of .github/workflows/ or scripts/.

Routine work — a skill, a template or script inside a skill, a README,
GOVERNANCE.md, the marketplace manifest, a fix — commits straight to `main`.
If that is what this is, close this and push it.
-->

## Change Note

**CN reference:** CN-YYYY-NNN
*(Every merged change to a controlled skill carries a Change Note number from the
MasterRegister. If this PR has no CN, say why.)*

**Type:** new skill / revision / fix / retirement / repo housekeeping

## What changed

<!-- One paragraph. What a reviewer needs to know, not a file list. -->

## Why

<!-- The defect, request or ruling that prompted it. -->

## Verification

Tick only what you have actually done. Do not tick in advance.

- [ ] `python scripts/validate_marketplace.py` passes locally
- [ ] Skill triggered correctly on its stated trigger phrases in a live session
- [ ] Skill did **not** trigger on the phrases listed under "NOT for" in its description
- [ ] Output opens cleanly in the target application (Word / Excel / PDF)
- [ ] Figures, dates, names and form references in any produced document are correct
- [ ] Version bumped in `plugin.json` **and** `.claude-plugin/marketplace.json`
- [ ] `CHANGELOG.md` updated

## Sign-off

- [ ] This change does **not** issue anything externally, bind BDM or the Principal
      under contract, or determine a variation, EOT or payment without Director approval.

**Prepared by:**
**Director sign-off:** *(required before merge)*
