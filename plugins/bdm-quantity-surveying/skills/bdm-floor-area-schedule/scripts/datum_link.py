"""Find and load the datum-markup library from the bdm-standards plugin.

bdm-quantity-surveying declares bdm-standards as a dependency, so the library is
installed beside this plugin. It is located rather than copied here, so there is
one copy of the Datum format and it cannot drift.

Search order: $DATUM_MARKUP_DIR, then the sibling plugin
(<plugins>/bdm-standards/skills/datum-markup/scripts), then anywhere under
~/.claude/plugins and ~/.claude/skills.
"""
import glob, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))


def datum_dir():
    cands = []
    if os.environ.get('DATUM_MARKUP_DIR'):
        cands.append(os.environ['DATUM_MARKUP_DIR'])
    root = os.path.abspath(os.path.join(_HERE, '..', '..', '..', '..'))      # .../<plugins root>
    cands.append(os.path.join(root, 'bdm-standards', 'skills', 'datum-markup', 'scripts'))
    home = os.path.expanduser('~')
    cands += sorted(glob.glob(os.path.join(home, '.claude', 'plugins', '**', 'datum-markup', 'scripts'), recursive=True))
    cands += sorted(glob.glob(os.path.join(home, '.claude', 'skills', '**', 'datum-markup', 'scripts'), recursive=True))
    for c in cands:
        f = os.path.join(c, 'datum_markup.py')
        if os.path.exists(f):
            with open(f, encoding='utf-8') as fh:
                src = fh.read()
            if 'def bake(' in src and 'def verify(' in src:
                return c
    sys.exit('datum-markup library not found, or it is an old copy without verify() and bake(). '
             'Install / update the bdm-standards plugin, or set DATUM_MARKUP_DIR to its scripts folder.')


def load():
    d = datum_dir()
    if d not in sys.path:
        sys.path.insert(0, d)
    import datum_markup
    return datum_markup
