#!/usr/bin/env python3
"""build_prashna_data.py — Prashna chart generation pipeline

Invokes calculate_full_chart from shared vedic-calculator/scripts/engine.py (at question instant),
and uses Prashna-dedicated whitelisted formatter to assemble structured_prashna.md, writing into
an isolated directory: prashna_<yyyymmdd_HHMMSS>_<label>/.

Sandbox constraints (vedic-prashna/SKILL.md):
  1. Read-only reuse of shared engine; never invoke natal formatter or modify shared code.
  2. Artifact named structured_prashna.md (strictly distinct from natal structured_data.md).
  3. Artifact output to prashna_<yyyymmdd_HHMMSS>_<label>/ isolated subdirectory (never root).
  4. Never include alien Tajika/KP fields in the standard layer.

Standard Layer Defaults:
  - Whitelisted fields strictly per resources/standard-layer.md.
  - Omits natal Dasha, Chara Karaka, SAV/BAV, divisional charts, Yogas, or transits.
  - Does not compute timing; timing overlay for favorable/pending outcomes is written
    by independent build_timing_overlay.py (resources/timing-layer.md), not imported here.

Usage:
    python build_prashna_data.py \\
        --datetime "2026-07-11 15:30:24.125"  # Query instant (local tz), or "now" \\
        --lat 30.667 --lon 104.067            # Location (degrees, positive=N/E) \\
        --tz "Asia/Shanghai"                  # Location timezone \\
        --question "Should I accept this offer?" \\
        --label offer-decide                  # Question short label (a-z0-9-, 1-30) \\
        [--out-parent .]                      # Output parent directory (default CWD)
"""
import argparse
import re
import sys
from pathlib import Path


# --- Reuse shared vedic-calculator (read-only) ---
_HERE = Path(__file__).resolve().parent           # vedic-prashna/scripts/
_CALC_SCRIPTS = _HERE.parent.parent / "vedic-calculator" / "scripts"
if not _CALC_SCRIPTS.exists():
    raise RuntimeError(
        f"[FATAL] Shared vedic-calculator/scripts not found: {_CALC_SCRIPTS}\n"
        f"Prashna requires shared engine per sandbox constraint #1. Check directory layout."
    )
if str(_CALC_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_CALC_SCRIPTS))

from format_prashna_standard import format_standard_layer  # noqa: E402
from prashna_time import (  # noqa: E402
    calculate_prashna_chart,
    datetime_slug,
    format_wall_time,
    instant_text,
    parse_local_datetime,
)

# Sandboxed Moon Vedic motion computation (see calc_moon_vedic.py)
from calc_moon_vedic import compute as compute_moon_vedic  # noqa: E402
from calc_moon_vedic import format_moon_section            # noqa: E402

LABEL_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,29}$")


def parse_args():
    ap = argparse.ArgumentParser(description="Prashna Horary Chart Builder")
    ap.add_argument(
        "--datetime",
        required=True,
        help='Query instant, format "YYYY-MM-DD HH:MM[:SS[.ffffff]][+HH:MM]", or "now"',
    )
    ap.add_argument("--lat", type=float, required=True, help="Query latitude (positive=N)")
    ap.add_argument("--lon", type=float, required=True, help="Query longitude (positive=E)")
    ap.add_argument("--tz", required=True, help='Query timezone, e.g. "Asia/Shanghai"')
    ap.add_argument("--question", required=True, help="Specific question (single decidable query)")
    ap.add_argument("--label", required=True,
                    help="Short question label (kebab-case, 1-30 chars [a-z0-9-])")
    ap.add_argument("--out-parent", default=".",
                    help="Parent directory for output subdirectory (default CWD)")
    args = ap.parse_args()

    if not LABEL_RE.match(args.label):
        ap.error(f"--label must match {LABEL_RE.pattern}: received {args.label!r}")

    try:
        args.dt = parse_local_datetime(args.datetime, args.tz)
    except Exception as exc:
        ap.error(str(exc))
    return args


def build_prashna_header(
    dt, lat, lon, tz, question, label, chart_ayanamsa, dst_info, calc_meta=None
):
    lines = []
    lines.append("## Metadata\n")
    lines.append("```")
    lines.append("Chart Type: Prashna (Horary) — independent domain, separate from natal")
    lines.append(f"Query Date: {dt.strftime('%Y-%m-%d')}")
    lines.append(f"Query Time: {format_wall_time(dt)}")
    lines.append(f"Script Time: {instant_text(dt)}")
    lines.append(f"Query Location: ({lon:.3f}, {lat:.3f})")
    lines.append(f"Timezone: {tz}")
    lines.append("Time Precision: Seconds preserved; fractional seconds preserved from input/system")
    lines.append("Chart Method: vedic-calculator direct Prashna Kundali calculation")
    lines.append(f"Ayanamsa: True Chitrapaksha (Lahiri) ({chart_ayanamsa:.4f}°)")
    if calc_meta:
        lines.append(
            f"Provenance: engine {calc_meta['engine_version']} | UTC instant {calc_meta['instant_utc']}"
            f" | Ayanamsa {calc_meta['ayanamsa']:.6f}° (matching Lagna and planets)"
        )
    if dst_info and dst_info.get('is_dst'):
        lines.append(
            f"Daylight Saving: ⚠️ Active DST in effect (UTC offset {dst_info['utc_offset']})"
        )
    lines.append("Node Mode: Mean Node")
    lines.append("Standard Layer: Shatpanchasika-rooted + KN Rao/Bhavan compatibility")
    lines.append("Timing Layer: Favorable/pending outcomes computed via build_timing_overlay.py")
    lines.append("```\n")

    lines.append("## Query Details\n")
    lines.append("```")
    lines.append(f"Question: {question}")
    lines.append(f"Short Label: {label}")
    lines.append("Querent Background: [Horary analysis phase forbids reading background]")
    lines.append("Matter Category: [Decomposed during judgment plan, see resources/matter-rules.md]")
    lines.append("```\n")
    return "\n".join(lines)


def main():
    args = parse_args()

    # 1. Cast chart (reuse shared engine, read-only)
    chart = calculate_prashna_chart(args.dt, args.lat, args.lon, args.tz)

    # 2. Format standard layer via Prashna-dedicated formatter
    data_section = format_standard_layer(chart)

    # 3. Assemble Prashna header
    head = build_prashna_header(
        args.dt, args.lat, args.lon, args.tz, args.question, args.label,
        chart['ayanamsa'], chart.get('dst_info'), chart.get('calc_meta'),
    )

    # 4. Moon observation facts (sandboxed calculation)
    moon_data = compute_moon_vedic(chart, args.dt, args.tz)
    moon_section = format_moon_section(moon_data)

    final_md = head + "\n" + data_section + "\n\n---\n\n" + moon_section

    # 5. Write to isolated subdirectory
    subdir_name = f"prashna_{datetime_slug(args.dt)}_{args.label}"
    base_dir = Path(args.out_parent).resolve() / subdir_name
    out_dir, n = base_dir, 1
    while (out_dir / "structured_prashna.md").exists():
        n += 1
        out_dir = base_dir.with_name(f"{subdir_name}_{n}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "structured_prashna.md"
    out_path.write_text(final_md, encoding='utf-8')

    print(f"[OK] Prashna chart generated:")
    print(f"     Directory: {out_dir}")
    print(f"     File: structured_prashna.md")
    print(
        f"     Query Instant: {args.dt.strftime('%Y-%m-%d')} "
        f"{format_wall_time(args.dt)} ({args.tz})"
    )
    print(f"     Question: {args.question}")


if __name__ == "__main__":
    main()
