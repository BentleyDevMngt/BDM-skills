# plugins/

One directory per plugin. Each must be listed in
`../.claude-plugin/marketplace.json` or CI will fail.

```
<plugin-name>/
├── .claude-plugin/plugin.json
├── README.md
└── skills/<skill-name>/SKILL.md
```

One plugin so far: [`bdm-skills`](bdm-skills/README.md), at 0.1.0 — the 14
skills staged from `_AI Directory/2.0_Skills`, not yet reviewed. Remaining
skills are migrated in under controlled Change Notes. See
[../GOVERNANCE.md](../GOVERNANCE.md).

Build a distributable bundle with `bash ../scripts/build_plugin.sh <name>`.
