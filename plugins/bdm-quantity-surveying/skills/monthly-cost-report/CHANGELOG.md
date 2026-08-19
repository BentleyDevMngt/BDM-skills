# CHANGELOG — BDM Monthly Cost Report

## R2 / 2026-08 — packaging fix, 19 August 2026 (no revision bump)

Preventative. The `description:` field measured **1,021 characters against the platform's 1,024
limit** — three characters of headroom, so any later edit to the description would have made the
package silently un-installable. Trimmed to **979** (45 characters of headroom).

Five phrases shortened, none of them trigger text:

- "the whole job folder" → "the job folder"
- "newly signed fee proposals" → "fee proposals"
- "against its own agreement" → "against its agreement"
- "Use it even when the user only says" → "Use it even when the user says"
- "NOT the client-facing Monthly Project Report" → "NOT the Monthly Project Report"

All ten trigger phrases retained. **Nothing below the frontmatter changed** — the instructional
body, all three references and all three scripts (including `validate_xlsx.py`) are byte-identical
to the original R2 package. Packaging-only, so the revision is unchanged per migration decision J1.
Outgoing package archived to `_SS\monthly-cost-report_R2_2026-08_superseded-2026-08-19.skill`.


## R2 / 2026-08 — Excel integrity gate

Issued 17 August 2026. Same root cause as the Floor Area Schedule R2 issue: a stale
`xl/calcChain.xml` makes Excel report a rolled-forward register as corrupt, and neither
openpyxl nor LibreOffice can see it.

Changes:

- **Added `scripts/validate_xlsx.py`** — Excel-strict check and repair.
- **`verify_register.py` now calls it** as a fourth check block, `Excel package integrity
  (calcChain, dimension, namespaces)`, so the existing pre-delivery run catches the defect
  without anyone remembering a new command. It reports; `--repair` fixes.
- **`references/register-mechanics.md` gains failure mode 4**, documenting the trap and why
  the register can pass every content check and still not open.
- Step 5 of the workflow now requires `--repair` then `--check` on the saved register.

No change to the audit logic, the register mechanics or the Form 201 layout.

## R1 / 2026-08 — first issue

Authored by Andrew Bentley, August 2026. Filed to the controlled skills library on
16 August 2026 under the BDM naming convention.

Produces the **Monthly Cost Report** — the consultant fee register (Form 201) rolled
forward for the period. Sweeps every email and the whole job folder since the last report
for new invoices, newly signed fee proposals and executed consultancy agreements; audits
each invoice against its own agreement **before** anything is entered; then updates the
register as a DRAFT `.xlsx`.

### Contents at first issue

| File | Purpose |
|---|---|
| `SKILL.md` | The skill |
| `references/invoice-sweep.md` | Period sweep — where invoices and agreements are found |
| `references/compliance-checks.md` | Invoice-against-agreement audit before entry |
| `references/register-mechanics.md` | Form 201 sheet structure and update mechanics |
| `scripts/verify_register.py` | Pre-delivery check on the register |
| `scripts/fix_header_logo.py` | Re-injects the Form 201 header logo after a save |

### Notes on filing

- Source template is the controlled Form 201 in
  `Standard - Documents\BDM TEMPLATES\Working Copy\200 Project Management - Pre-Contract\`.
  The skill pulls the current revision rather than bundling a copy, so no template drift.
- `fix_header_logo.py` addresses the known openpyxl defect — every openpyxl save strips
  the `&G` header image and it must be re-injected.
- Checked at filing: no client or project data, no hardcoded user paths, no build
  artefacts.

This entry records the filing only. It is not a design record — the skill's own rationale
sits in `SKILL.md` and its references.
