# Installing the `bdm-tender-clarification` skill

Self-contained skill package. Once installed, George can draft a BDM **Tender Clarification** (Form 218) for a live tender — close-date extensions, tenderer RFI responses, and/or supplementary drawing issues — as Word + signature-ready PDF plus a cover email draft.

## What's in here

- `SKILL.md` — description, triggers, the locked company standard, and the full process.
- `scripts/next_tc.py` — scans a project's tender RFI folder → next TC number, suggested subfolder name, and the latest TC to clone.
- `scripts/build_tc.py` — fills a Form 218 from a config JSON (clone-and-fill, dynamic section renumbering, optional signature/author swap).
- `scripts/example_config.json` — a worked example (160 Pacific Parade TC-04).
- `scripts/pdf_export.sh` — shim to `bdm-pdf-export` for the Word-faithful PDF.

## Install (one of two paths)

### Option A — Cowork install button
If you received this as a `.skill` file, open it in Cowork and press **Save skill**. Start a new session and George will pick it up.

### Option B — drop into the Claude skills folder
Copy the whole `bdm-tender-clarification` folder into:
`C:\Users\James Gill\AppData\Roaming\Claude\local-agent-mode-sessions\skills-plugin\<...>\skills\`
alongside the other BDM skills (`bdm-pdf-export`, `bdm-standards`, etc.). Restart Cowork.

## Verify

In a new session: "Can you list available skills?" — `bdm-tender-clarification` should appear. Or trigger it: "Extend the tender close for <project> to <date>."

## Company standard baked in

- **Numbering** restarts at TC-01 per tender (auto-increments from the highest existing TC).
- **Saves** to the project's `12_Tender Documents/Tender/RFI/RFI<NN> - TC<NN>_<Descriptor>/`, working copy in the sandbox.
- **Builds** by cloning the project's latest TC and flagging if its layout is older than the current Form 218 revision.
- **Always** Word + PDF + cover email; cc client/Superintendent; **signature of the PM creating the TC** at 2.25 cm; referenced drawings filed alongside with refs read off the file — never invented.

## Depends on

- `bdm-pdf-export` (for the Word-faithful PDF) — already installed.
- A signature PNG per PM in their personal folder (James → `Projects - Documents\George\JG_signature.png`).
- Python: `python-docx`; `poppler-utils` (`pdftoppm`) and LibreOffice for the PDF — all present in the Cowork sandbox.
