# Installing the BDM skills in Claude

For BDM staff using the **Claude desktop app**. You do not need a GitHub
account, git, or the command line.

> **Not yet released.** These instructions are held pending Director sign-off.
> Do not circulate them or the plugin file until the plugin reaches 1.0.0.

---

## What you are installing

Four plugins. Together they teach Claude how BDM does its recurring work —
monthly reports, progress claims and certificates, QS lender reports,
consultancy agreements, DA conditions matrices, area schedules, meeting minutes,
site inspections and tender clarifications.

| Plugin | Who needs it |
| --- | --- |
| **bdm-standards** | **Everyone. Install this one first** — the others build on it |
| **bdm-contract-admin** | Anyone administering a head contract as Superintendent |
| **bdm-quantity-surveying** | Anyone doing areas, cost reports, claims or financier reports |
| **bdm-project-delivery** | Anyone running a job month to month — reports, minutes, approvals |

Take the ones that match your work. If you are unsure, take all four; nothing
breaks by having a skill you never use.

Once installed you do not have to do anything special. You ask for the work the
way you would ask a person — "draft the progress certificate for claim 14",
"roll the monthly report forward" — and Claude picks up the right method itself.

---

## Installing it

BDM distributes these through a **marketplace** — a catalogue Claude reads
straight from the BDM repository. You add the catalogue once, install the
plugins once, and after that updates arrive on their own.

**Step 1 — add the marketplace.** In the Claude desktop app, go to
**Customize → Plugins → Add marketplace** and enter:

```
BentleyDevMngt/bdm-skills
```

The marketplace is named **`bentley-dm`**. Adding it installs nothing on its
own — it only tells Claude where the plugins live.

**Step 2 — install the plugins.** Open the `bentley-dm` marketplace and install
**`bdm-standards` first**. Then install whichever of the other three match your
work. They each declare `bdm-standards` as a dependency, so it is pulled in
automatically if you skip ahead.

**Step 3 — turn on auto-update.** This is the step that saves you repeating all
of the above. Go to **Plugins → Marketplaces → `bentley-dm`** and choose
**Enable auto-update**.

> Auto-update is **off by default** for marketplaces outside Anthropic's own.
> If you skip this step the plugins stay frozen at the version you installed and
> you will not be told there is a newer one.

**Step 4 — restart Claude.** Plugins load at start-up.

To check it worked, ask Claude: *"which skills do I have?"* You should see the
BDM skills listed.

---

## Using it

Just describe the work. A few that will trigger:

- "Draft the progress certificate for claim 14 on Seagull Ave"
- "Roll the monthly cost report forward for August"
- "Build the DA conditions matrix from this decision notice"
- "Write up the site inspection from this OneNote export"
- "Prepare a consultancy agreement for the structural engineer's fee proposal"

Claude will usually ask you a question or two before it starts. Answer them —
the answers are what keep the output on BDM's standards rather than generic.

**Everything these skills produce is a draft.** They are built to prepare work
and hand it back, never to issue it. Nothing goes to a client, a financier, a
consultant or a builder until the responsible Senior PM or the Director has
read it and signed it off. Check the numbers, dates and names before anything
leaves the office — the skill has followed the method, but it has not verified
the facts of your job.

---

## Updating

**With auto-update on, there is nothing to do.** Claude refreshes the
marketplace shortly after each session starts and moves your plugins to the
current version. You may be prompted to reload, or the new version loads next
time you start.

A change reaches you only when the plugin's **version number is raised**. That
is BDM's job, not yours — but it means if you are told a change went out and you
do not see it, the version bump is the first thing to check.

Change Notes still go out for anything that touches the controlled estate. The
plugin arriving quietly is not a substitute for reading the notice.

---

## If something goes wrong

- **The file will not install.** Check you are on the current Claude desktop
  app; plugin support needs a recent version.
- **Claude ignores the skill.** Say what you want more directly, naming the
  document — "use the BDM monthly project report skill". If it still does not
  fire, that is worth reporting; the trigger wording may need work.
- **The output looks wrong.** Stop and report it rather than correcting it
  yourself and moving on. A skill producing wrong output produces it for
  everyone, and it cannot be fixed if nobody says so.

Report both to Andrew Bentley, with the project, what you asked for and what
came back.

---

## Alternative: the packaged plugin files

If the marketplace route is unavailable to you, each plugin can also be handed
out as a `.plugin` file: attach it to a new chat in the Claude desktop app and
press Install, `bdm-standards` first.

**This route does not auto-update.** An installed `.plugin` file is a frozen
copy with no link to the repository — it stays exactly as it was until someone
sends you a new file and you install it again. Use it only where the
marketplace will not work.

Claude Code users can do the same from the command line:

```
/plugin marketplace add BentleyDevMngt/bdm-skills
/plugin install bdm-standards@bentley-dm
/plugin install bdm-project-delivery@bentley-dm
```

Then `/plugin` → **Marketplaces** → `bentley-dm` → **Enable auto-update**.
