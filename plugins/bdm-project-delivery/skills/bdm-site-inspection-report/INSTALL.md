# Installing the `bdm-site-inspection-report` skill

Self-contained skill package. Once installed, George can turn a OneNote site-visit export into a finished BDM Site Inspection Record (Form 331), Word + PDF.

## What's in here

- `SKILL.md` — description, triggers, and the full process.
- `scripts/stitch_photos.py` — rebuilds clean photos from a OneNote "Export to PDF" (OneNote slices each photo into strips).
- `scripts/build_report.py` — fills the latest Form 331 from a config JSON + stitched photos.
- `scripts/example_config.json` — a worked example ([Project Name]).

## Install (one of two paths)

### Option A — Cowork install button
If you received this as a `.skill` file, open it in Cowork and press **Save skill**. Start a new session and George will pick it up.

### Option B — drop into the Claude skills folder
Copy the whole `bdm-site-inspection-report` folder into:
`C:\Users\<user>\AppData\Roaming\Claude\local-agent-mode-sessions\skills-plugin\<...>\skills\`
alongside the other BDM skills (`bdm-pdf-export`, `bdm-standards`, etc.). Restart Cowork.

## Verify

In a new session: "Can you list available skills?" — `bdm-site-inspection-report` should appear. Or trigger it: "Write up a site inspection report for <project> from this OneNote."

## Depends on

- `bdm-pdf-export` (for the Word-faithful PDF) — already installed.
- Python: `python-docx`, `pillow`; `poppler-utils` (`pdfimages`, `pdftoppm`). All present in the Cowork sandbox.
