#!/usr/bin/env python3
"""Prove a restructured project summary lost nothing.

Usage:
    python check_restructure.py OLD.md NEW.md [ARCHIVE.md ...]

OLD      the summary as it was (the _SS backup copy)
NEW      the restructured summary
ARCHIVE  any file older change-log entries were moved into

Three checks:

1. FACTS (hard gate). Every dollar figure, date, percentage and reference
   number in OLD must appear somewhere in NEW or an ARCHIVE. Any missing
   fact fails the check (exit code 1).
2. STRUCTURE (hard gate). NEW has the 17 numbered sections "## 1." to
   "## 17." exactly once each, in order.
3. LINES (advisory). Each non-blank line of OLD is looked for in NEW and
   the ARCHIVEs after normalising whitespace and markdown. Lines not found
   word for word are listed with the closest match, for a person to check.
   Headings are excluded: renaming them is the point of the exercise.

Standard library only. Read-only: it never writes to any file.
"""
import difflib
import re
import sys
from pathlib import Path

FACT_PATTERNS = [
    r"\$\s?\d[\d,]*(?:\.\d+)?(?:\s?[mk]\b)?",          # $1,234.56  $2.5m
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",                    # 15/6/26
    r"\b\d{4}-\d{2}-\d{2}\b",                          # 2026-10-20
    r"\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s\d{2,4}\b",
    r"\b\d+(?:\.\d+)?\s?%",                            # 5%  2.5 %
    r"\b[A-Z]{1,6}[-_]?\d{1,6}(?:[-/.]\d+)*\b",        # VO-012  EOT05  DA-1234/2025  MCU22
]
FACT_RE = re.compile("|".join(f"(?:{p})" for p in FACT_PATTERNS), re.IGNORECASE)


def norm(s: str) -> str:
    s = s.replace(" ", " ")
    s = re.sub(r"[*_`>|#]", " ", s)           # markdown emphasis, tables, quotes
    s = re.sub(r"^\s*(?:[-+]|\d+[.)])\s+", " ", s)  # list markers
    return re.sub(r"\s+", " ", s).strip().lower()


def fact_key(f: str) -> str:
    return re.sub(r"\s+", "", f).lower()


def facts(text: str) -> set:
    return {fact_key(m.group(0)) for m in FACT_RE.finditer(text)}


def is_noise(line: str) -> bool:
    t = line.strip()
    return (not t or t.startswith("#") or re.fullmatch(r"[|:\-\s]+", t) is not None
            or t in ("---", "***") or t.startswith("<!--") or t.endswith("-->"))


def main(argv) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    old_p, new_p, arch_ps = Path(argv[1]), Path(argv[2]), [Path(a) for a in argv[3:]]
    old = old_p.read_text(encoding="utf-8", errors="replace")
    new = new_p.read_text(encoding="utf-8", errors="replace")
    archives = [p.read_text(encoding="utf-8", errors="replace") for p in arch_ps]
    after = "\n".join([new] + archives)
    ok = True

    # 1. Facts
    missing = sorted(facts(old) - facts(after))
    print(f"FACTS     {len(facts(old))} distinct figures/dates/references in OLD; "
          f"{len(missing)} missing from NEW + archive")
    for f in missing:
        ok = False
        ctx = next((l.strip() for l in old.splitlines() if fact_key(f) in fact_key(l)), "")
        print(f"  MISSING  {f}    <- {ctx[:110]}")

    # 2. Structure
    heads = [int(m.group(1)) for m in re.finditer(r"^## (\d{1,2})\.", new, re.M)]
    if heads != list(range(1, 18)):
        ok = False
        print(f"STRUCTURE FAIL  numbered sections found in order: {heads} (need 1..17 once each)")
    else:
        print("STRUCTURE 17 sections, once each, in order")

    # 3. Lines (advisory)
    after_norm = norm(after)
    after_lines = [norm(l) for l in after.splitlines() if not is_noise(l)]
    old_lines = [l for l in old.splitlines() if not is_noise(l)]
    unmatched = [l for l in old_lines if norm(l) and norm(l) not in after_norm]
    print(f"LINES     {len(old_lines)} content lines in OLD; "
          f"{len(unmatched)} not found word for word (advisory — check by hand)")
    for l in unmatched[:200]:
        best = difflib.get_close_matches(norm(l), after_lines, n=1, cutoff=0.0)
        score = difflib.SequenceMatcher(None, norm(l), best[0]).ratio() if best else 0
        print(f"  CHECK    {l.strip()[:100]}")
        print(f"           closest ({score:.0%}): {best[0][:100] if best else '-'}")
    if len(unmatched) > 200:
        print(f"  ... {len(unmatched) - 200} more not shown")

    kb = lambda s: len(s.encode("utf-8")) // 1024
    print(f"SIZE      OLD {kb(old)} KB -> NEW {kb(new)} KB"
          + (f" + archive {sum(kb(a) for a in archives)} KB" if archives else ""))
    print("RESULT    " + ("PASS" if ok else "FAIL — do not replace the summary until fixed"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
