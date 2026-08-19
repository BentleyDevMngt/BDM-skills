# Progress Claim Update Skill — Shareable Package

A monthly Head Contract Progress Claim automation pipeline for construction projects
under BDM Director / SPM authority. Reads a month's accounts folder + the prior
Claim N-1 xlsx → produces a draft Claim N for review and issue.

**Contractor-side use case** — built for BDM running Head Contract claims as
contractor. The skill produces the contractor's claim to the principal/client.

## Files in this package

| File | Purpose |
|---|---|
| `SKILL.md` | Skill definition for Claude — trigger phrases, inputs, 9-phase workflow |
| `README.md` | This file |
| `CHANGELOG.md` | Version history + outstanding bugs (read before sharing) |
| `TROUBLESHOOTING.md` | Common errors and fixes |
| `scripts/build_claim.py` | Main pipeline (single Python entry point, ~1200 lines) |
| `projects/_template.yaml` | Starter config for new projects |
| `projects/202415_south_pine_rd.yaml` | Worked example (BDM project 202415, pilot project) |
| `memory/feedback_xero_orphan_dedup.md` | Standing rule on Xero name-mismatch + statement dedup |
| `memory/feedback_viking_service_type_split.md` | Standing rule on multi-service suppliers |
| `memory/feedback_quarantine_unallocated_costs.md` | Standing rule on quarantining unallocable costs |

## Quick start

### Install (Cowork)

Either:
- Save the .skill file via the Cowork "Save skill" button (loads SKILL.md into
  Alfred's skill library), then drop the memory files into your `memory/` directory.
- Or extract the zip and copy the directory to your skills folder.

### Install (Claude Code)

Place the unpacked `progress-claim-update/` folder under your `.claude/skills/`
directory. Drop the memory files into your project's memory directory.

### Per-project setup

1. Copy `projects/_template.yaml` to `projects/{your_project_code}_{short_name}.yaml`.
2. Fill the `project:` block (code, name, folder paths, contract sum).
3. Pre-populate `supplier_to_ctd_block` mapping from your project's CTD Breakdown tab.
   The 202415 example has 60+ entries — start with whatever you can copy from your
   current claim's supplier rows.
4. First run will identify any new suppliers it can't map; approve their codes and
   they'll be added to `new_ctd_blocks` for future runs.

### Run for a month

```bash
python3 scripts/build_claim.py \
  --project {CODE} \
  --config projects/{CODE}_{short}.yaml \
  --month-folder "{folder_root}/{accounts_subfolder}/NN_{Month} YYYY" \
  --claim-template "{path to prior Claim N-1 xlsx}" \
  --output-dir "{your Alfred working folder}/{project subfolder}" \
  --claim-no {N} \
  --period-start DD/MM/YYYY \
  --period-end DD/MM/YYYY \
  --no-cache
```

### Re-run for the same claim (e.g. invoices arrived after first run)

Same command + `--draft-version 0.2` (or 0.3, etc.). Idempotent — each run is a fresh
snapshot from the current folder state.

### Start a new project

1. Copy `projects/_template.yaml`
2. Fill in `project:` block (code, name, folder paths, contract sum)
3. Run first month; approve new-supplier codes when prompted
4. Approved codes get baked into `new_ctd_blocks` for future runs

## What the skill DOES NOT do

- Issue the claim to the client
- Email or distribute the file
- Apply variations to over-claim positions (Director / SPM signs these off)
- Chase orphan-payment suppliers (Director / SPM action)
- Verify amounts against subcontract POs (Director / SPM review)

The skill produces a clean DRAFT for human review. The watermark on the cover reads
`— DRAFT v{X} — Alfred prepared, for issue by Andrew/SPM` until you remove it at issue.

## Maintenance

### When the claim template structure changes
Update the `load_bearing` block in the per-project YAML AND the constants in
`build_claim.py`. The skill's safety self-check will refuse to run if the structure
doesn't match.

### When a new supplier appears
First run will flag it. After approval, add to `new_ctd_blocks` in the project YAML so
subsequent runs treat it as known.

### When Xero uses a new legal-entity name
If a Xero transaction shows up as orphan but you can match it to a filed invoice
manually, add an alias to `xero_aliases` in the project YAML.

### When an image-only PDF can't be auto-parsed (Carilla, AFS, etc.)
After OCR fallback fails, add a `manual_overrides` entry to the project YAML with the
verified total / date / invoice no. Future runs use the override automatically.

### When a multi-service supplier appears (Viking-style)
Add a `service_type_map` block to the project YAML mapping service keywords to the
relevant CTD subtotal section. See the Viking example in
`projects/202415_south_pine_rd.yaml`.

## Known limitations

1. **OneDrive hydration** — if files aren't downloaded locally, the skill stops and
   asks the user to right-click → "Always keep on this device". Doesn't auto-trigger
   hydration.
2. **OCR reliability** — Carilla MYOB scans and AFS scanned invoices have manual
   overrides because OCR is unreliable. Future suppliers with scanned invoices may
   need similar overrides.
3. **Supplier name fuzz matching** — works on keyword overlap, not perfect. The
   `xero_aliases` map closes gaps where legal vs trading names differ.
4. **Single project per run** — the skill processes one project's month folder at a
   time. For multi-project monthly batch, wrap with a shell loop.
5. **45-second sandbox timeout** — `--no-cache` full re-extraction of 150+ PDFs
   sometimes exceeds the Cowork bash sandbox's 45s timeout. Workaround: chunked
   extraction wrapper (see TROUBLESHOOTING.md).
6. **Other outstanding bugs** — see CHANGELOG.md for the full list of issues
   identified during the Claim 16 May 2026 production run that need fixing before
   handing the skill to non-developers self-serve.

## Authority boundaries

Per BDM standing rule: Alfred drafts, doesn't commit. The Director or SPM reviews each
draft before issue. The "DRAFT v{X} — Alfred prepared, for issue by Andrew/SPM"
watermark stays visible until the human issues the final claim.

## Origin

Built during the Claim 16 May 2026 pilot for 818 South Pine Road, Everton Park
(project 202415). Andrew (Director, BDM) and Alfred iterated through 13 versions
(v0.1 → v1.3) to solve the structural problems of rolling a multi-tab Excel Progress
Claim forward each month with formula integrity, alphabetical insertion, dedup, and
Xero reconciliation. A second production run on the same project surfaced eight
further correctness bugs and four operational fragility issues, captured in
CHANGELOG.md.

This skill bakes in all 9 structural fixes plus the per-project configuration learned
during the pilot. The memory files document standing rules established during the
production run.
