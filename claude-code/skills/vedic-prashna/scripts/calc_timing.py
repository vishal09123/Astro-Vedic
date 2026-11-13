#!/usr/bin/env python3
"""calc_timing.py — Prashna timing overlay pure functions (sandboxed, standard library only)

Four classical timing candidates; sources, applicable matter types, and boundaries in resources/timing-layer.md:

  T1  P-V.5     Return/arrival queries: Count houses from Lagna to the first house containing a classical graha
                (graha in Lagna = 1); house count * 12 days.
  T2  M-XIV.85  Count houses from matter house to its lord's house (inclusive); lord in houses 7-12 gives days,
                in houses 1-6 gives months (days/months division is Raman's commentary convention).
  T3  M-XIV.85  Moon's next ingress into the sign occupied by the matter lord.
  T4  M-XIV.82  Time unit of rising Navamsa lord (XIV.81) * that lord's Navamsa ordinal within its sign (reference only).

Does not import engine, Tajika, or KP; planetary data is passed in by build_timing_overlay.py.
Does not generate success/failure verdicts; multiple candidates are listed side by side without averaging or voting.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


SEVEN_GRAHAS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
NAVAMSA_SPAN = 30.0 / 9.0

# M-XIV.81 Raman commentary citing Brihat Jataka: (amount per unit, unit label, Sanskrit name)
PERIOD_UNITS = {
    "Sun": (6, "months", "Ayana"),
    "Moon": (48, "minutes", "Kshana"),
    "Mars": (1, "weeks", "Vasara"),
    "Mercury": (2, "months", "Rithu"),
    "Jupiter": (1, "months", "Masa"),
    "Venus": (0.5, "months", "Ardha"),
    "Saturn": (1, "years", "Sama"),
}

VERDICT_PREFIX = {"favorable": "Approximately", "pending": "If progression proceeds smoothly, approximately"}

_J2000 = 2451545.0
_J2000_UTC = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# T1–T4
# ---------------------------------------------------------------------------
def t1_return_days(planet_houses: dict) -> dict:
    """P-V.5: Count houses from Lagna to the first house with classical grahas * 12 days."""
    for count in range(1, 13):
        names = [n for n in SEVEN_GRAHAS if planet_houses.get(n) == count]
        if names:
            return {
                "rule_id": "P-V.5",
                "count": count,
                "planets": names,
                "days": count * 12,
            }
    raise ValueError("No classical grahas found in any house: planet_houses missing data")


def t2_house_lord_count(matter_house: int, lord: str, lord_house: int) -> dict:
    """M-XIV.85: Count houses from matter house to lord house, inclusive."""
    visible = lord_house >= 7
    return {
        "rule_id": "M-XIV.85",
        "matter_house": matter_house,
        "lord": lord,
        "lord_house": lord_house,
        "count": ((lord_house - matter_house) % 12) + 1,
        "unit": "days" if visible else "months",
        "hemisphere": "visible hemisphere (houses 7-12)" if visible else "invisible hemisphere (houses 1-6)",
        "pace": "faster" if visible else "slower",
    }


def navamsa_ordinal(degree_in_sign: float) -> int:
    """Navamsa ordinal of planet in sign (1-9)."""
    return min(int(degree_in_sign / NAVAMSA_SPAN), 8) + 1


def t4_navamsa_lord_period(lord: str, lord_degree_in_sign: float) -> dict:
    """M-XIV.82: Rising Navamsa lord unit * lord's Navamsa ordinal in sign."""
    ordinal = navamsa_ordinal(lord_degree_in_sign)
    amount, unit, name = PERIOD_UNITS[lord]
    return {
        "rule_id": "M-XIV.82",
        "lord": lord,
        "navamsa_ordinal": ordinal,
        "unit_name": name,
        "per_unit": amount,
        "unit": unit,
        "value": ordinal * amount,
    }


def next_sign_entry(
    longitude_at,
    jd_start: float,
    target_sign_idx: int,
    step_days: float = 0.25,
    max_days: float = 32.0,
    tolerance_days: float = 1.0 / 86400.0,
) -> float:
    """M-XIV.85 T3: JD(UT) of Moon's next entry into target sign."""
    def in_target(jd):
        return int((longitude_at(jd) % 360.0) / 30.0) == target_sign_idx

    prev_jd, prev_in = jd_start, in_target(jd_start)
    while prev_jd - jd_start < max_days:
        jd = prev_jd + step_days
        now_in = in_target(jd)
        if now_in and not prev_in:
            lo, hi = prev_jd, jd
            while hi - lo > tolerance_days:
                mid = (lo + hi) / 2.0
                if in_target(mid):
                    hi = mid
                else:
                    lo = mid
            return hi
        prev_jd, prev_in = jd, now_in
    raise ValueError(f"No ingress into sign_idx={target_sign_idx} found within {max_days} days")


def jd_to_local(jd: float, tz: str) -> datetime:
    """JD(UT) -> local datetime rounded to nearest second."""
    utc = _J2000_UTC + timedelta(days=jd - _J2000)
    return (utc + timedelta(microseconds=500_000)).replace(microsecond=0).astimezone(ZoneInfo(tz))


# ---------------------------------------------------------------------------
# Format as timing_overlay.md
# ---------------------------------------------------------------------------
def _fmt_number(value) -> str:
    return f"{value:g}"


def format_timing_section(data: dict) -> str:
    prefix = VERDICT_PREFIX[data["verdict"]]
    primary = data["primary"]
    t3 = data["t3"]
    t4 = data["t4"]

    if primary["rule_id"] == "P-V.5":
        primary_text = f"{prefix} returns / arrives in {primary['days']} days"
    else:
        primary_text = (
            f"{prefix} event manifests within {primary['count']} {primary['unit']} "
            f"({primary['pace']} pace)"
        )
    t4_text = f"{_fmt_number(t4['value'])} {t4['unit']}"
    if t4["lord"] == "Moon":
        t4_text += " (Moon unit is 48 minutes, usually too short for gradual matters)"

    lines = ["# Timing Overlay (Prashna)\n"]
    lines.append(f"> Query Time: {data['judgment_time']} ({data['judgment_timezone']})")
    lines.append(f"> Standard Layer Internal Tier: {'Favorable' if data['verdict'] == 'favorable' else 'Pending'}"
                 "; this file does not alter that conclusion.\n")

    lines.append("## Plain Language Summary\n")
    lines.append(f"- **Primary Window**: {primary_text}.")
    if t3:
        lines.append(f"- **Next Ingress Trigger**: Around {t3['local_time']}.")
    lines.append(f"- **Secondary Reference**: Another classical formula indicates {t4_text} (reference only).")
    lines.append("- Several classical calculation traditions are shown side by side without averaging.\n")

    lines.append("## Calculation Breakdown\n")
    lines.append("| Candidate | rule_id | Input | Result | Role |")
    lines.append("|---|---|---|---|---|")
    if primary["rule_id"] == "P-V.5":
        lines.append(
            f"| T1 | P-V.5 | Count from Lagna to first house with grahas: house {primary['count']} "
            f"({', '.join(primary['planets'])}) | {primary['count']} × 12 = "
            f"{primary['days']} days | Primary Timing (Return/Arrival) |"
        )
    else:
        lines.append(
            f"| T2 | M-XIV.85 | House {primary['matter_house']} lord {primary['lord']} in "
            f"house {primary['lord_house']}, {primary['hemisphere']}; inclusive span "
            f"{primary['count']} houses | {primary['count']} {primary['unit']}, "
            f"pace {primary['pace']} | Primary Timing |"
        )
    if t3:
        already = "; Moon already in sign at query time, taking next re-entry" if t3["already_in"] else ""
        lines.append(
            f"| T3 | M-XIV.85 | Moon's next ingress into {t3['lord']}'s sign {t3['sign']}{already} | "
            f"{t3['local_time']} | Ingress Trigger |"
        )
    else:
        lines.append(
            "| T3 | M-XIV.85 | Matter lord is Moon; self-referential ingress omitted | N/A | — |"
        )
    lines.append(
        f"| T4 | M-XIV.82 | Rising Navamsa {t4['navamsa_sign']}, lord {t4['lord']} in Navamsa "
        f"{t4['navamsa_ordinal']}; unit {t4['unit_name']} = "
        f"{_fmt_number(t4['per_unit'])} {t4['unit']} | {t4['navamsa_ordinal']} × "
        f"{_fmt_number(t4['per_unit'])} = {t4_text} | Reference |"
    )
    lines.append("")

    lines.append("## Boundaries\n")
    lines.append("- Runs only when standard layer tier is favorable or pending; unfavorable queries receive no timing.")
    lines.append("- T2 day/month division follows Raman's commentary convention.")
    lines.append("- T4 is for reference only; do not compromise or average with primary timing.")
    lines.append(
        "- Never uses 120-year Vimshottari, Chara Dasha, or transits for query charts; "
        "never imports Tajika or KP timing stacks."
    )
    return "\n".join(lines) + "\n"
