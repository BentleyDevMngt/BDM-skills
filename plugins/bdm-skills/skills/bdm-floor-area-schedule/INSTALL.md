# Install — Floor Area Schedule (R1, July 2026)

New skill. Nothing to supersede.

1. In Cowork / Claude: **Settings → Capabilities → Skills → Install/Update from file**.
2. Select `bdm-floor-area-schedule_R2_2026-08.skill`.
3. Confirm. The installed skill name is `bdm-floor-area-schedule`.

## Verify

In a new session, ask: *"Can you list available skills?"* —
`bdm-floor-area-schedule` should appear.

Or trigger it: *"Prepare a floor area schedule for &lt;project&gt; from these plans."*

## Before your first run

The skill pulls two templates from
`…\BDM TEMPLATES\Working Copy\400 Quantity Surveying\`:

- `405-Floor_Area_Schedule_R1_2026-07.xlsx`
- `405a-Area_Markup_Cover_R1_2026-07.pdf`

Both were filed July 2026. If they are not there, the skill will flag it rather
than build a workbook from scratch.

## Depends on

Python: `pymupdf`, `opencv-python-headless`, `numpy`, `scipy`, `scikit-image`,
`openpyxl` — all present in the Cowork sandbox.

Also needs an embeddable sans font (Carlito, Liberation Sans or DejaVu Sans).
The PDF base-14 fonts silently drop the **m²** and em-dash glyphs, so the markup
builder refuses to run without one rather than print a schedule that reads
"1,466.3 m".

## Worked example

The pilot take-off config is held with the project, not in this skill. Read `references/config_schema.md` to see what a completed config looks
like before writing your first one.
