# plugins/

One directory per plugin. Each must be listed in
`../.claude-plugin/marketplace.json` or CI will fail.

```
<plugin-name>/
├── .claude-plugin/plugin.json
├── README.md
└── skills/<skill-name>/SKILL.md
```

Empty for now — skills are being migrated in under controlled Change Notes.
See [../GOVERNANCE.md](../GOVERNANCE.md).
