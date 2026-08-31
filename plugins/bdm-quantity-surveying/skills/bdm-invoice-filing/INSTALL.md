# Install — Invoice Filing (R1, August 2026)

New skill. Nothing to supersede.

1. In Cowork / Claude: **Settings → Capabilities → Skills → Install/Update from file**.
2. Select `bdm-invoice-filing_R1_2026-08.skill`.
3. Confirm. The installed skill name is `bdm-invoice-filing`.

## Verify

In a new session, ask: *"Can you list available skills?"* — `bdm-invoice-filing`
should appear.

Or trigger it: *"Run the invoice sweep."*

## Before your first run

Three preconditions. The skill will stop and flag rather than guess if any are missing.

**1. Your active-project list must exist and be current.** The skill reads the
**Active projects** list from your `CLAUDE.local.md` in `Projects - Documents\` and
sweeps only those projects. If the file is absent or more than sixty days stale, the
skill stops. Do not skip this — an out-of-date list is how invoices end up filed into
another PM's project on the shared library.

**2. The projects you sweep must carry `1.0_Project Invoices`.** Twenty-four legacy
projects still hold a plain `Invoices` folder and are skipped until migrated. The
migration list is at
`Projects - Documents\Alfred\Invoice_Folder_Migration_List_2026-08-30.md`.

**3. Everton Park stays excluded.** `202415_South Pine Rd, Everton Park` is excluded by
Director ruling because its `01a_Accounts` chain is reconciled against Xero by the
progress claim. Do not re-enable it locally.

## Recommended first week

Run it in report-only mode — ask for the sweep but tell it to report rather than file —
and review what lands in quarantine before letting it write. The quarantine depth in the
first week is the honest measure of whether the detection rules fit your mailbox.

## Scheduling

The skill is the shareable standard. The **schedule is not** — scheduled tasks are stored
per-user on each machine and run only while the Claude desktop app is open. Each PM creates
their own daily task calling this skill. A task due while the app was closed runs on next
launch.
