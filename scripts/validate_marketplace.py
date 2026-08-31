#!/usr/bin/env python3
"""Structural validation for the BDM skills marketplace.

Checks, in order:
  1. marketplace.json parses and carries the required keys.
  2. Every plugin listed has a real directory and a matching plugin.json.
  3. Plugin versions agree between marketplace.json and plugin.json.
  4. Every skill folder has a SKILL.md with valid YAML frontmatter.
  5. Frontmatter carries name + description; name matches the folder.
  6. Descriptions are within the length Claude actually reads.
  7. No plugin directory is orphaned (present on disk, absent from the manifest).
  8. Every declared plugin dependency resolves to a plugin in this marketplace.
  9. Each skill carries the CN-2026-033 package set (warning only).

Exit code 0 = pass, 1 = fail.

    python scripts/validate_marketplace.py              # this repository
    python scripts/validate_marketplace.py <repo-root>  # audit another checkout
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"
PLUGINS_DIR = ROOT / "plugins"

DESC_MIN = 40
DESC_MAX = 1024
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Minimal YAML frontmatter reader — top-level scalar keys only.

    Deliberately dependency-free so CI needs no pip install.
    """
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    data: dict[str, str] = {}
    key = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1] in (" ", "\t") and key:          # continuation line
            data[key] = (data[key] + " " + raw.strip()).strip()
            continue
        if ":" not in raw:
            continue
        key, _, value = raw.partition(":")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        data[key] = value
    return data


def check_skill(skill_dir: Path, plugin_name: str) -> None:
    label = f"{plugin_name}/{skill_dir.name}"
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        err(f"{label}: no SKILL.md")
        return

    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        err(f"{label}: SKILL.md has no parseable YAML frontmatter")
        return

    name = fm.get("name")
    if not name:
        err(f"{label}: frontmatter missing 'name'")
    else:
        if name != skill_dir.name:
            err(f"{label}: frontmatter name '{name}' does not match folder name")
        if not NAME_RE.match(name):
            err(f"{label}: name '{name}' is not lower-kebab-case")

    desc = fm.get("description")
    if not desc:
        err(f"{label}: frontmatter missing 'description' — Claude cannot route to this skill")
    else:
        if len(desc) < DESC_MIN:
            warn(f"{label}: description is only {len(desc)} chars; triggering will be unreliable")
        if len(desc) > DESC_MAX:
            err(f"{label}: description is {len(desc)} chars, over the {DESC_MAX} limit")

    body = text[text.find("\n---", 3) + 4:]
    if len(body.strip()) < 200:
        warn(f"{label}: SKILL.md body is very short ({len(body.strip())} chars)")


def main() -> int:
    declared_deps: dict[str, object] = {}
    if not MANIFEST.is_file():
        err(f"missing {MANIFEST.relative_to(ROOT)}")
        return report()

    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        err(f"marketplace.json is not valid JSON: {exc}")
        return report()

    for key in ("name", "description", "owner", "plugins"):
        if key not in manifest:
            err(f"marketplace.json missing required key '{key}'")

    listed: set[str] = set()
    for entry in manifest.get("plugins", []):
        pname = entry.get("name", "<unnamed>")
        listed.add(pname)

        if not NAME_RE.match(pname):
            err(f"{pname}: plugin name is not lower-kebab-case")

        source = entry.get("source")
        if not source:
            err(f"{pname}: manifest entry has no 'source'")
            continue

        pdir = (ROOT / source.lstrip("./")).resolve()
        if not pdir.is_dir():
            err(f"{pname}: source '{source}' does not exist")
            continue

        pjson = pdir / ".claude-plugin" / "plugin.json"
        if not pjson.is_file():
            err(f"{pname}: no .claude-plugin/plugin.json")
            continue

        try:
            plugin = json.loads(pjson.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            err(f"{pname}: plugin.json is not valid JSON: {exc}")
            continue

        if plugin.get("name") != pname:
            err(f"{pname}: plugin.json name '{plugin.get('name')}' disagrees with the manifest")
        if plugin.get("dependencies") is not None:
            declared_deps[pname] = plugin.get("dependencies")
        if entry.get("version") and plugin.get("version") != entry.get("version"):
            err(
                f"{pname}: version mismatch — manifest {entry.get('version')} "
                f"vs plugin.json {plugin.get('version')}"
            )

        skills_dir = pdir / "skills"
        if not skills_dir.is_dir():
            warn(f"{pname}: no skills/ directory")
            continue
        found = [d for d in sorted(skills_dir.iterdir()) if d.is_dir()]
        if not found:
            warn(f"{pname}: skills/ is empty")
        for skill_dir in found:
            check_skill(skill_dir, pname)
            # CN-2026-033 package convention. A warning, not an error: that
            # notice records the estate as largely non-conformant and brings
            # each skill up at its next revision, so failing CI here would
            # block every unrelated change.
            missing = [n for n in ("README.md", "INSTALL.md", "CHANGELOG.md")
                       if not (skill_dir / n).is_file()]
            if missing:
                warn(f"{pname}/{skill_dir.name}: package incomplete — "
                     f"missing {', '.join(missing)} (CN-2026-033)")

    if PLUGINS_DIR.is_dir():
        for pdir in sorted(PLUGINS_DIR.iterdir()):
            if pdir.is_dir() and pdir.name not in listed:
                err(f"{pdir.name}: plugin directory on disk is not listed in marketplace.json")

    # 8. Every declared dependency resolves to a plugin this marketplace ships.
    #    Claude auto-installs dependencies; one naming a plugin that is not here
    #    fails at install time on someone else's machine, not ours.
    #    The schema is an ARRAY of entries, each either a bare plugin-name
    #    string or {"name": ..., "version": <semver range>}. It is NOT the npm
    #    object-of-name-to-range shape; this validator asserted that shape until
    #    2026-08-31 and so passed three manifests whose dependency declarations
    #    Claude ignored entirely.
    for pname, deps in declared_deps.items():
        if isinstance(deps, dict):
            err(f"{pname}: dependencies is an object; the schema is an array of "
                f"names or {{name, version}} entries")
            continue
        if not isinstance(deps, list):
            err(f"{pname}: dependencies must be an array")
            continue
        for dep in deps:
            if isinstance(dep, str):
                dep_name, dep_range = dep, None
            elif isinstance(dep, dict):
                dep_name = dep.get("name")
                dep_range = dep.get("version")
                if not isinstance(dep_name, str) or not dep_name.strip():
                    err(f"{pname}: a dependency entry has no 'name'")
                    continue
                if dep_range is not None and (
                    not isinstance(dep_range, str) or not dep_range.strip()
                ):
                    err(f"{pname}: dependency '{dep_name}' has an empty version range")
                unknown = set(dep) - {"name", "version", "marketplace"}
                if unknown:
                    err(f"{pname}: dependency '{dep_name}' has unknown "
                        f"field(s) {', '.join(sorted(unknown))}")
            else:
                err(f"{pname}: a dependency entry is neither a string nor an object")
                continue
            if isinstance(dep, dict) and dep.get("marketplace"):
                continue  # resolved in another marketplace; not ours to check
            if dep_name not in listed:
                err(f"{pname}: depends on '{dep_name}', which this marketplace does not ship")
            if dep_name == pname:
                err(f"{pname}: depends on itself")

    return report()


def report() -> int:
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"FAIL  {e}")
    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK — marketplace valid ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
