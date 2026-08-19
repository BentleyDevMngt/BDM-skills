# bdm-standards

The foundation. House style, document QA and the shared production tooling every
BDM deliverable passes through.

**Install this first.** The other three BDM plugins declare a dependency on it,
so Claude will pull it in automatically — but if you are installing by hand, start
here.

**Version 0.1.0 — staged, not signed off.** See [GOVERNANCE.md](../../GOVERNANCE.md) §4.

---

## Skills

| Skill | Does |
| --- | --- |
| `datum-markup` | Editable markups, measurements and priced BOQ take-offs written straight into a PDF for Datum |

## Still to arrive

This plugin is deliberately thin at 0.1.0. The two skills that make it the
foundation live in the legacy `JamesBDM/bdm-plugins` repository and come across
under the next Change Note:

- `bdm-house-style` — the always-on rulebook: palette, typography, logo, layout,
  filename convention, QA checklist, template locations, working rules
- `bdm-pdf-export` — Word-faithful PDF export

Until they land, the domain plugins depend on a plugin that does not yet carry
the house style. That is a known gap, not an oversight — see the CHANGELOG.
