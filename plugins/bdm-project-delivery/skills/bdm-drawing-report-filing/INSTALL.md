# Install — Drawing & Report Filing (R1, October 2026)

New skill. Nothing to supersede.

It ships in the `bdm-project-delivery` plugin. Updating that plugin, or `bdm-all`, installs it.
As a stand-alone package: **Settings → Capabilities → Skills → Install/Update from file**, select
`bdm-drawing-report-filing_R1_2026-10.skill`, and confirm. The installed name is
`bdm-drawing-report-filing`.

## Verify

In a new session ask *"Run the drawing sweep for New Earth, report only."*

## Before the first scheduled run

1. **The scheduled task must be able to reach the computer.** It files into the project folders
   through the linked computer, so the task needs `Projects - Documents` attached as a folder,
   with "Require this computer" on.
2. **Point the task at the skill.** Its prompt should say to load and follow
   `bdm-drawing-report-filing`, give the scope (which projects), and name the operator's
   quarantine folder. The skill holds the procedure; the prompt should not restate it.
3. **Decide on seeding.** Registers are created at the first receipt after go-live, so a project's
   register starts with only what arrives from then on. To start from what is already on file,
   run "seed the register for <project>" by hand, project by project, and review each result.

## Recommended first week

Run it report-only — sweep, but report instead of filing — and look at what it would quarantine.
Then let it file, but check the first few registers in Excel before trusting it unattended.
