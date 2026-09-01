#!/usr/bin/env python3
"""Raise the version of every plugin touched by a range of commits.

Why this exists
---------------
Auto-update only ships a change when the version is raised. A merge to `main`
that edits a SKILL.md but forgets the version bump reaches no one, silently:
the repository looks current, every installed account stays on the old skill,
and nothing anywhere reports a fault. That failure mode was the single most
disruptive thing about the old process, and it was left to a human to remember
in two files at once.

So the bump is no longer a human step. `.github/workflows/release.yml` runs
this after a merge to `main`. It reads which files the merge actually changed,
raises the patch version of each affected plugin in BOTH `plugin.json` and the
`marketplace.json` entry, keeps the `bdm-all` bundle in step, and writes the
CHANGELOG line.

Usage
-----
    python scripts/bump_versions.py --base <sha> --head <sha> [--dry-run]

Exit codes: 0 = done (bumped, or nothing to bump), 1 = error.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"
PLUGINS = ROOT / "plugins"
CHANGELOG = ROOT / "CHANGELOG.md"
BUNDLE = "bdm-all"

# A change to one of these inside a plugin is bookkeeping, not a change to what
# the plugin does. Bumping on these would make the workflow bump itself.
IGNORED_LEAVES = {".claude-plugin/plugin.json"}

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def run(*args: str) -> str:
    return subprocess.run(
        args, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout


def changed_files(base: str, head: str) -> list[str]:
    out = run("git", "diff", "--name-only", f"{base}..{head}")
    return [line.strip() for line in out.splitlines() if line.strip()]


def plugins_touched(files: list[str]) -> set[str]:
    touched: set[str] = set()
    for f in files:
        parts = f.split("/")
        if len(parts) < 3 or parts[0] != "plugins":
            continue
        name = parts[1]
        leaf = "/".join(parts[2:])
        if leaf in IGNORED_LEAVES:
            continue
        if not (PLUGINS / name).is_dir():
            continue          # deleted plugin; nothing to bump
        if name == BUNDLE:
            continue          # the bundle follows its children, never leads
        touched.add(name)
    return touched


def bump_patch(version: str) -> str:
    m = SEMVER.match(version or "")
    if not m:
        raise SystemExit(f"ERROR  version '{version}' is not major.minor.patch")
    major, minor, patch = (int(g) for g in m.groups())
    return f"{major}.{minor}.{patch + 1}"


def load(path: Path) -> collections.OrderedDict:
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=collections.OrderedDict)


DRY_RUN = False


def save(path: Path, data) -> None:
    """Write JSON, or report the intent when --dry-run is in force."""
    if DRY_RUN:
        print(f"  [dry-run] would write {path.relative_to(ROOT)}")
        return
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    global DRY_RUN
    DRY_RUN = args.dry_run

    files = changed_files(args.base, args.head)
    touched = plugins_touched(files)
    if not touched:
        print("No plugin content changed — nothing to release.")
        return 0

    manifest = load(MANIFEST)
    entries = {e.get("name"): e for e in manifest.get("plugins", [])}

    new_versions: dict[str, str] = {}
    for name in sorted(touched):
        pjson_path = PLUGINS / name / ".claude-plugin" / "plugin.json"
        if not pjson_path.is_file():
            print(f"WARN  {name}: no plugin.json; skipped")
            continue
        pjson = load(pjson_path)
        new = bump_patch(pjson.get("version", ""))
        pjson["version"] = new
        save(pjson_path, pjson)
        if name in entries:
            entries[name]["version"] = new
        else:
            print(f"WARN  {name}: not listed in marketplace.json")
        new_versions[name] = new
        print(f"  {name}  ->  {new}")

    if not new_versions:
        print("Nothing bumped.")
        return 0

    # The bundle must move too, or an installed account sees no version change
    # on bdm-all and never re-resolves the set.
    bundle_path = PLUGINS / BUNDLE / ".claude-plugin" / "plugin.json"
    if bundle_path.is_file():
        bundle = load(bundle_path)
        for dep in bundle.get("dependencies", []):
            if isinstance(dep, dict) and dep.get("name") in new_versions:
                dep["version"] = f">={new_versions[dep['name']]}"
        bundle_new = bump_patch(bundle.get("version", ""))
        bundle["version"] = bundle_new
        save(bundle_path, bundle)
        if BUNDLE in entries:
            entries[BUNDLE]["version"] = bundle_new
        print(f"  {BUNDLE}  ->  {bundle_new}  (bundle follows its children)")

    save(MANIFEST, manifest)

    # CHANGELOG. Kept deliberately plain: what moved, to what, on what date.
    # Narrative belongs in the commit body, which is where a reviewer reads it.
    subject = run("git", "log", "-1", "--pretty=%s", args.head).strip()
    lines = [f"- **{n} {v}** — {subject}" for n, v in sorted(new_versions.items())]
    block = f"### Released {date.today().isoformat()}\n\n" + "\n".join(lines) + "\n\n"

    text = CHANGELOG.read_text(encoding="utf-8")
    marker = "## Unreleased\n"
    if marker in text:
        head, _, tail = text.partition(marker)
        text = head + marker + "\n" + block + tail.lstrip("\n")
    else:
        text = text.rstrip("\n") + "\n\n## Unreleased\n\n" + block
    if DRY_RUN:
        print("\n--dry-run: nothing written. CHANGELOG entry would read:\n")
        print(block.rstrip())
    else:
        CHANGELOG.write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
