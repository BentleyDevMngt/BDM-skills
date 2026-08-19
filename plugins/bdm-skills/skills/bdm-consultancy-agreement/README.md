# bdm-consultancy-agreement

Drafts a BDM **Consultancy Agreement (Form 105)** appointing a consultant to a
project, built from the consultant's own fee proposal but onto **BDM's terms**.

Built August 2026 from a structural engineering appointment on a residential project.

## What you get

| Output | Detail |
|---|---|
| **Form 105 agreement** | Populated .docx on the current controlled template — parties, recitals, Annexure 1 schedule (Items 1–14), execution block |
| **Annexure 2** | Scope, exclusions, fee stages and rate card transcribed from the consultant's proposal, with the proposal attached behind it |
| **Hand-back note** | Open commercial points, unsourced fields, and any pre-execution blockers |

Held as **DRAFT** for Director sign-off. Never issued, never PDF'd.

## Why transcribe Annexure 2 rather than just staple the proposal

Annexure 1 Items 13 and 14 give the Agreement precedence over the consultant's
proposal and over the standard conditions inside it. That precedence is worth
little if Annexure 2 is an empty box with a PDF behind it — the substance still
sits in the consultant's document, in the consultant's words. Transcribing the
scope, exclusions, fees and rates into Annexure 2 makes the Agreement the
operative instrument and the proposal the evidence.

## What's in the package

```
SKILL.md                              triggers, template source, workflow, hold rules
README.md                             this file
INSTALL.md                            how to install and verify
CHANGELOG.md                          revision history
references/form-105-idiom.md          placeholder list, XML element order, table conventions
references/verification-checklist.md  arithmetic, transcription, template-integrity checks
```

## Templates it uses

`…\BDM TEMPLATES\Working Copy\100 Development Management\`

- `105-Consultancy_Agreement_Simple_R*.docx`

Always pull the highest **R** number, not the newest file date. Ignore
`_Superseded`.

## The one thing to take away

**Consultancy agreement templates live in the BDM TEMPLATES Working Copy — and
nowhere else.** `Standard - Documents\Contracts\Consultant Agreements\` holds
historical working drafts, including an R1-era redline with live review comments
and **Aptos** as its default font. Building from it produces an off-brand
agreement carrying the wrong revision in its header. Before populating anything,
check `word/styles.xml` says **Calibri** and `word/header1.xml` shows the
revision you expected.

## Dependencies

Python: `python-docx`, `lxml`. LibreOffice (`soffice`) and `pdftoppm` for the
visual check only — the rendered PDF is a working artefact and must be deleted,
not handed over.
