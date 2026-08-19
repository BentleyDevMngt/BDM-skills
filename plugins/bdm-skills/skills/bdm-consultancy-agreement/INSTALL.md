# Install — Consultancy Agreement (R1, August 2026)

New skill. Nothing to supersede.

1. In Cowork / Claude: **Settings → Capabilities → Skills → Install/Update from file**.
2. Select `bdm-consultancy-agreement_R1_2026-08.skill`.
3. Confirm. The installed skill name is `bdm-consultancy-agreement`.

## Verify

In a new session, ask: *"Can you list available skills?"* —
`bdm-consultancy-agreement` should appear.

Or trigger it: *"Prepare a consultancy fee agreement for &lt;consultant&gt; on &lt;project&gt;."*

## Before your first run

The skill pulls one template from
`…\BDM TEMPLATES\Working Copy\100 Development Management\`:

- `105-Consultancy_Agreement_Simple_R2_2026-06.docx` (R2 current as at Aug 2026)

Select by highest **R** number. If it is not there, the skill will flag it rather
than fall back to a look-alike file in another folder.

## What it will ask you

The contracting **Principal** — full legal name, ACN, registered office. Consultant
proposals are routinely addressed to the PM or the wrong group entity, so the skill
sources this from BDM's own records and asks if the sources disagree. It will not
guess a party name into a contract.

## What it will not do

Issue, send, execute, or produce a PDF. It drafts to the project's `00_ai_sandbox`
and holds. Sign-off and issue stay with the Director or the Senior PM.

## Depends on

Python: `python-docx`, `lxml` — present in the Cowork sandbox.
LibreOffice and `pdftoppm` for the internal render check only.
