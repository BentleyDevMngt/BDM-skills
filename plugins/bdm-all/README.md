# bdm-all

A bundle. It ships no skills of its own — its manifest is a dependency list on
the four BDM plugins:

- `bdm-standards`
- `bdm-contract-admin`
- `bdm-quantity-surveying`
- `bdm-project-delivery`

## Why it exists

Installing the four separately meant four trips through Discover in a required
order, because the other three depend on `bdm-standards`. Staff got the order
wrong, or stopped after two, and then had a partial toolset with no signal that
anything was missing.

Installing `bdm-all` resolves the dependency graph in one action and the four
arrive together. They also **update** together: when the release workflow raises
a plugin's version it raises this bundle's too, so an installed account sees one
version change and pulls the whole consistent set.

## Maintaining it

Do not hand-edit the version or the dependency ranges. `.github/workflows/release.yml`
rewrites both on every merge to `main` that touches a plugin. CI fails if a range
here is ahead of the version that plugin actually ships.
