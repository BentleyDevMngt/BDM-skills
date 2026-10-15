# Install — Floor Area Schedule (R4, October 2026)

Ships in the **bdm-quantity-surveying** plugin, which depends on **bdm-standards**
(for the Datum library). Installing or updating the plugins from the BDM marketplace
is the whole install — auto-update carries R4 once the release is published.

## Verify

In a new session: *"Prepare a floor area schedule for <project> from these plans."*
The skill should fire and describe two deliverables — the Form 405 workbook and the
405a markup PDF that opens live in Datum.

Then run the fixture:

```bash
python3 scripts/make_fixture.py /tmp/fx                                         # FIXTURE OK
python3 scripts/build_405a.py  /tmp/fx/testbed_takeoff.json /tmp/fx/405a-Testbed.pdf   # read-back clean
```

## Before your first run

The skill pulls two templates from
`…\BDM TEMPLATES\Working Copy\400 Quantity Surveying\`:

- `405-Floor_Area_Schedule_R*.xlsx`
- `405a-Area_Markup_Cover_R*.pdf`

If they are not there, the skill flags it rather than building a workbook from
scratch.

## Depends on

See README — Python packages, an embeddable font, bdm-standards, and Node +
Playwright for the bake. Without the bake the 405a still opens fully in Datum;
the markups then show in other viewers only after it has been saved from Datum.
