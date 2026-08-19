# Skill template

Starting point for a new BDM skill.

```bash
cp -r templates/skill-template plugins/<plugin>/skills/<skill-name>
```

Then rename the folder and set `name:` in the frontmatter to match it exactly —
they must agree or the skill will not load. Delete any of `scripts/`,
`references/` or `templates/` you do not use.

See [../../CONTRIBUTING.md](../../CONTRIBUTING.md).
