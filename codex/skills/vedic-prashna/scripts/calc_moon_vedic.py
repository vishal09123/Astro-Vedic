#!/usr/bin/env python3
"""calc_moon_vedic.py — Prashna Moon Vedic motion calculation (sandboxed)

Calculates the three sets of Moon facts required by the standard layer (whole-sign Parashari, no orb):
- moon_position: Current Moon sign, Nakshatra, and house position
- moon_contacts: Whole-sign conjunctions and Graha Drishti aspects
- moon_strength_factors: Moon phase (paksha), tithi, D1 dignity, and house

Does not generate success/failure verdicts or event timing windows. Lack of direct contact
is never labeled "Void of Course" and cannot trigger a global rejection. Nakshatra lord serves
as a descriptive / question verification aid, not a fixed significator.

Sandbox constraints (vedic-prashna/SKILL.md):
- Resides strictly in vedic-prashna/scripts/, never in shared vedic-calculator.
- Reuses basic engine tools in read-only mode, preserving second-level precision.
- Appended to prashna_*/structured_prashna.md by build_prashna_data.py.
"""
import argparse
import json
import sys
from pathlib import Path

# --- Reuse shared vedic-calculator (read-only) ---
_HERE = Path(__file__).resolve().parent            # vedic-prashna/scripts/
_CALC = _HERE.parent.parent / "vedic-calculator" / "scripts"
if str(_CALC) not in sys.path:
    sys.path.insert(0, str(_CALC))

from engine import (                                # noqa: E402
    get_house,
)
from prashna_time import calculate_prashna_chart, parse_local_datetime  # noqa: E402
from format_prashna_standard import tithi_facts  # noqa: E402


# Special Graha Drishti according to engine.calc_graha_drishti
SPECIAL_DRISHTI = {'Mars': [4, 8], 'Jupiter': [5, 9], 'Saturn': [3, 10]}
DRISHTI_PLANETS = [
    'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'
]


# ---------------------------------------------------------------------------
# Contact detection (whole-sign placement + Graha Drishti, no orb)
# ---------------------------------------------------------------------------
def _planets_aspecting_sign(planets, lagna_sign_idx, target_sign_idx):
    """Planets aspecting target sign via Graha Drishti (excluding Moon itself and conjunctions)."""
    target_house = get_house(target_sign_idx, lagna_sign_idx)
    hits = []
    for name in DRISHTI_PLANETS:
        p = planets.get(name)
        if not p or name == 'Moon':
            continue
        src_house = p['house']
        angles = [7] + SPECIAL_DRISHTI.get(name, [])
        for a in angles:
            if ((src_house - 1 + (a - 1)) % 12) + 1 == target_house:
                hits.append({
                    'planet': name, 'from_sign': p['sign'],
                    'from_house': src_house, 'aspect_angle': a,
                })
                break
    return hits


def _planets_colocated_with(planets, target_sign_idx):
    """Planets colocated in target sign (excluding Moon itself)."""
    hits = []
    for name in DRISHTI_PLANETS:
        p = planets.get(name)
        if not p or name == 'Moon':
            continue
        if p['sign_idx'] == target_sign_idx:
            hits.append({'planet': name, 'sign': p['sign'], 'house': p['house']})
    return hits


# ---------------------------------------------------------------------------
# Core compute
# ---------------------------------------------------------------------------
def compute(chart, dt_local, tz_str):
    """Output Moon observation data for chart + query datetime + tz."""
    moon = chart['planets']['Moon']
    planets = chart['planets']
    lagna_sign_idx = chart['lagna']['sign_idx']
    moon_sign_idx = moon['sign_idx']
    moon_house = moon['house']
    moon_nak = moon['nakshatra']

    # Moon current contacts: Record astrological facts without success/failure verdicts
    conj = _planets_colocated_with(planets, moon_sign_idx)
    aspecting = _planets_aspecting_sign(planets, lagna_sign_idx, moon_sign_idx)

    moon_position = {
        'moon_sign': moon['sign'],
        'moon_nakshatra': moon_nak['name'],
        'moon_pada': moon_nak['pada'],
        'moon_nakshatra_lord': moon_nak['lord'],
        'moon_house': moon_house,
    }
    moon_contacts = {
        'conjunctions': conj,
        'graha_drishti_planets': [h['planet'] for h in aspecting],
        'graha_drishti_details': aspecting,
    }
    tithi, full_moon_window = tithi_facts(
        planets['Sun']['longitude'], moon['longitude']
    )
    moon_strength_factors = {
        'paksha': chart.get('moon_phase', {}),
        'tithi': tithi,
        'full_moon_window': full_moon_window,
        'dignity': chart.get('dignity', {}).get('Moon', {}),
        'house': moon_house,
    }

    return {
        'moon_position': moon_position,
        'moon_contacts': moon_contacts,
        'moon_strength_factors': moon_strength_factors,
    }


# ---------------------------------------------------------------------------
# Format as Markdown section
# ---------------------------------------------------------------------------
def format_moon_section(moon_data):
    position = moon_data['moon_position']
    contacts = moon_data['moon_contacts']
    strength = moon_data['moon_strength_factors']
    lines = []

    lines.append("## Moon Observation Facts (Standard Layer Input)\n")

    lines.append("### Moon Current Placement & Strength Facts\n")
    lines.append("```")
    lines.append(
        f"Moon: {position['moon_sign']} · "
        f"{position['moon_nakshatra']} (pada {position['moon_pada']}) · "
        f"House {position['moon_house']}"
    )
    lines.append(
        f"Nakshatra Lord: {position['moon_nakshatra_lord']} "
        "(descriptive context aid, not a fixed significator)"
    )
    phase = strength.get('paksha', {})
    dignity = strength.get('dignity', {})
    phase_text = "waxing" if phase.get('waxing') else "waning"
    lines.append(
        f"Moon Phase: {phase_text} · Sun–Moon Separation "
        f"{phase.get('sun_moon_diff', 'n/a')}°"
    )
    tithi = strength.get('tithi')
    if tithi is not None:
        paksha_name = "Shukla Paksha" if tithi <= 15 else "Krishna Paksha"
        paksha_day = tithi if tithi <= 15 else tithi - 15
        lines.append(
            f"Tithi: {tithi} ({paksha_name} day {paksha_day}) · Full Moon Window (P-I.5, "
            f"Shukla 10 to Krishna 5): {'Yes' if strength.get('full_moon_window') else 'No'}"
        )
    lines.append(
        f"D1 Dignity: basic={dignity.get('basic', 'n/a')} · "
        f"compound={dignity.get('compound', 'n/a')}"
    )
    lines.append("```\n")

    lines.append("**Current Contact Set** (Vedic whole-sign: conjunctions + Graha Drishti, no orb)\n")
    if contacts['conjunctions']:
        for c in contacts['conjunctions']:
            lines.append(f"- Conjunction: **{c['planet']}** (same sign, House {c['house']})")
    else:
        lines.append("- Conjunction: None")
    if contacts['graha_drishti_details']:
        for a in contacts['graha_drishti_details']:
            lines.append(f"- Graha Drishti: **{a['planet']}** (from House {a['from_house']}, {a['aspect_angle']}th aspect)")
    else:
        lines.append("- Graha Drishti Aspect: None")
    lines.append("")

    if not contacts['conjunctions'] and not contacts['graha_drishti_details']:
        lines.append(
            "> **Interpretation Boundary**: Absence of direct contact does not independently determine outcome; "
            "synthesize with topic rules and matter house/lord evidence.\n"
        )
    else:
        lines.append(
            "> **Interpretation Boundary**: Contacts identify planetary connections; "
            "significance depends on matter rules and does not determine outcome in isolation.\n"
        )

    lines.append("### Interpretation Entry Point\n")
    lines.append(
        "For semantic mapping see `resources/moon-policy.md`. Standard layer does not compute Moon ingress; "
        "Moon ingress trigger day (M-XIV.85) is computed by timing overlay build_timing_overlay.py.\n"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Prashna Moon Vedic motion standalone CLI")
    ap.add_argument(
        "--datetime",
        required=True,
        help='"YYYY-MM-DD HH:MM[:SS[.ffffff]]" or "now"',
    )
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--tz", required=True)
    ap.add_argument("--json", action="store_true", help="Output JSON instead of Markdown")
    args = ap.parse_args()

    try:
        dt = parse_local_datetime(args.datetime, args.tz)
    except Exception as exc:
        ap.error(str(exc))
    chart = calculate_prashna_chart(dt, args.lat, args.lon, args.tz)
    data = compute(chart, dt, args.tz)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_moon_section(data))


if __name__ == "__main__":
    main()
