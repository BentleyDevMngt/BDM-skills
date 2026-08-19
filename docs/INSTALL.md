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

1. Save the `.plugin` files somewhere you can find them, such as your Downloads
   folder.
2. Open the Claude desktop app and start a new chat.
3. Attach a `.plugin` file to the chat, the same way you would attach any other
   file. **Do `bdm-standards` first.**
4. The file appears as a card showing what is inside it, with a button to
   install. Press it.
5. Repeat for each of the others you need.

That is the whole job — they stay installed, you do not repeat this each time.

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

Updates come as a new `.plugin` file for whichever plugin changed. Install it
the same way and it replaces the previous version. Watch for the notice that
goes out with it — it will carry a Change Note number telling you what changed
and why.

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

## Alternative: installing from the repository

For anyone with read access to `BentleyDevMngt/bdm-skills` on GitHub and a git
credential configured, the plugin can be installed from source instead, which
picks up changes as they are pushed:

```
/plugin marketplace add BentleyDevMngt/bdm-skills
/plugin install bdm-standards@bentley-dm
/plugin install bdm-project-delivery@bentley-dm
```

The domain plugins declare a dependency on `bdm-standards`, so it comes along
automatically. The marketplace is `bentley-dm`, not `bdm`.

This route needs the account to have added you as a collaborator first. For
most staff the plugin file above is the simpler path.
