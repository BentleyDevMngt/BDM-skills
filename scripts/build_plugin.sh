#!/usr/bin/env bash
# Build a distributable .plugin bundle from a plugin directory.
#
#   bash scripts/build_plugin.sh [plugin-name]
#
# Defaults to bdm-skills. Writes dist/<name>.plugin — a zip of the plugin
# directory, with sync artefacts and build outputs excluded. The bundle is a
# build output: it is not committed, and release bundles are built from the
# release tag so the version in plugin.json is the version in the file.
set -euo pipefail

PLUGIN="${1:-bdm-skills}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/plugins/$PLUGIN"
DIST="$ROOT/dist"

[ -d "$SRC" ] || { echo "no such plugin: $SRC" >&2; exit 1; }
[ -f "$SRC/.claude-plugin/plugin.json" ] || { echo "missing $PLUGIN/.claude-plugin/plugin.json" >&2; exit 1; }

# Structure check — the same things the Claude CLI validator looks for.
python3 - "$SRC" <<'PY'
import json, os, re, sys
src = sys.argv[1]
man = json.load(open(os.path.join(src, ".claude-plugin", "plugin.json"), encoding="utf-8"))
fail = []
name = man.get("name", "")
if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
    fail.append(f"plugin name not kebab-case: {name!r}")
if not re.fullmatch(r"\d+\.\d+\.\d+", man.get("version", "")):
    fail.append(f"version not semver: {man.get('version')!r}")
skills = os.path.join(src, "skills")
if not os.path.isdir(skills):
    fail.append("no skills/ directory")
else:
    for d in sorted(os.listdir(skills)):
        p = os.path.join(skills, d)
        if not os.path.isdir(p):
            continue
        sm = os.path.join(p, "SKILL.md")
        if not os.path.isfile(sm):
            fail.append(f"{d}: no SKILL.md")
            continue
        head = open(sm, encoding="utf-8", errors="replace").read(4000)
        fm = re.match(r"^---\n(.*?)\n---", head, re.S)
        if not fm:
            fail.append(f"{d}: SKILL.md has no frontmatter")
            continue
        body = fm.group(1)
        fn = re.search(r"^name:\s*[\"']?([^\"'\n]+)", body, re.M)
        if not fn:
            fail.append(f"{d}: frontmatter has no name")
        elif fn.group(1).strip() != d:
            fail.append(f"{d}: frontmatter name {fn.group(1).strip()!r} != folder name")
        if not re.search(r"^description:", body, re.M):
            fail.append(f"{d}: frontmatter has no description")
if fail:
    print("FAILED:")
    for f in fail:
        print("  -", f)
    sys.exit(1)
n = len([d for d in os.listdir(skills) if os.path.isdir(os.path.join(skills, d))])
print(f"OK — {name} {man['version']}, {n} skill(s)")
PY

mkdir -p "$DIST"
TMP="$(mktemp -d)"
OUT="$TMP/$PLUGIN.plugin"
( cd "$SRC" && zip -qr "$OUT" . \
    -x "*.DS_Store" "Thumbs.db" "desktop.ini" \
       "*__pycache__/*" "*.pyc" "*.pyo" "~\$*" )
mv "$OUT" "$DIST/$PLUGIN.plugin"
rm -rf "$TMP"

echo "built  $DIST/$PLUGIN.plugin"
unzip -l "$DIST/$PLUGIN.plugin" | tail -1
