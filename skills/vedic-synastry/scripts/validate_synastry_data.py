#!/usr/bin/env python3
"""validate_synastry_data.py — Lightweight verification before cross-chart synastry calculation.

Verifies that two structured_data.md files satisfy minimum synastry criteria and internal consistency.
Reuses the parser from build_synastry_data.py.

Usage: python validate_synastry_data.py <A_structured_data.md> <B_structured_data.md>
Exit codes: 0 All passed / 1 Issues found / 2 Argument error
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_synastry_data import Chart, PLANETS  # noqa: E402


def check_one(c):
    """Return (hard_check_list[(ok, msg)], soft_warning_list[str])."""
    issues = []
    n = len([p for p in PLANETS if p in c.planets])
    issues.append((n == 9, f"Planet completeness {n}/9"))
    issues.append((c.lagna_idx is not None, f"Lagna parsed ({c.lagna_sign})"))
    
    # Ra-Ke opposition check (must be 6 signs apart)
    ra, ke = c.planets.get('Rahu'), c.planets.get('Ketu')
    if ra and ke and ra['sidx'] is not None and ke['sidx'] is not None:
        diff = (ra['sidx'] - ke['sidx']) % 12
        issues.append((diff == 6, f"Ra-Ke opposition (separated by {diff} signs)"))
    else:
        issues.append((False, "Ra-Ke parsing failed"))
    issues.append((c.moon_nak is not None, f"Moon Nakshatra ({c.moon_nak} pada {c.moon_pada})"))

    # Soft warnings: missing fields degrade specific layers but do not block calculation
    warns = []
    if not c.ul:
        warns.append("UL missing → UL/D9 capacity layer degraded")
    if not c.dk:
        warns.append("DK missing → Darakaraka partnership layer degraded")
    if not c.dasha_md:
        warns.append("Dasha current status missing → Timing Layer (Layer 3) degraded")
    return issues, warns


def main():
    if len(sys.argv) < 3:
        print("Usage: python validate_synastry_data.py <A.md> <B.md>")
        sys.exit(2)

    ok_all = True
    for label, path in (('A', sys.argv[1]), ('B', sys.argv[2])):
        if not os.path.exists(path):
            print(f"❌ File does not exist: {path}")
            ok_all = False
            continue
        c = Chart(path, label)
        issues, warns = check_one(c)
        print(f"=== Chart {label}: {os.path.basename(path)} ===")
        for ok, msg in issues:
            print(f"  {'✅' if ok else '❌'} {msg}")
            if not ok:
                ok_all = False
        for w in warns:
            print(f"  ⚠️  {w}")

    print("\nResult:", "✅ Passed, ready for build_synastry_data.py"
          if ok_all else "❌ Hard issues found; fix before synastry analysis")
    sys.exit(0 if ok_all else 1)


if __name__ == '__main__':
    main()
