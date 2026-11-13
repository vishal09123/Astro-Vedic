#!/usr/bin/env python3
"""Source-scoped Tajika sixteen-yoga overlay for Prashna.

The implementation follows Tajika Nilakanthi, Samjnatantra,
Sodasayogadhyaya 2.3-59.  It remains isolated from the Parashari standard
layer: no result produced here can alter the standard-layer internal tiers ``Favorable / Balanced / Unfavorable``.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CALC = _HERE.parent.parent / "vedic-calculator" / "scripts"
if str(_CALC) not in sys.path:
    sys.path.insert(0, str(_CALC))

from prashna_time import (  # noqa: E402
    calculate_prashna_chart,
    parse_local_datetime,
)


TAJIKA_PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
TAJIKA_ORBS = {
    "Sun": 15.0,
    "Moon": 12.0,
    "Mars": 8.0,
    "Mercury": 7.0,
    "Jupiter": 9.0,
    "Venus": 7.0,
    "Saturn": 9.0,
}
SIGN_LORDS = (
    "Mars",
    "Venus",
    "Mercury",
    "Moon",
    "Sun",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Saturn",
    "Jupiter",
)
SIGN_NAMES = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

# TNK 2.33-38: Hadda/term rulers.  Each tuple is (upper degree, ruler).
HADDA = (
    ((6, "Jupiter"), (12, "Venus"), (20, "Mercury"), (25, "Mars"), (30, "Saturn")),
    ((8, "Venus"), (14, "Mercury"), (22, "Jupiter"), (27, "Saturn"), (30, "Mars")),
    ((6, "Mercury"), (12, "Venus"), (17, "Jupiter"), (24, "Mars"), (30, "Saturn")),
    ((7, "Mars"), (13, "Venus"), (19, "Mercury"), (26, "Jupiter"), (30, "Saturn")),
    ((6, "Jupiter"), (11, "Venus"), (18, "Saturn"), (24, "Mercury"), (30, "Mars")),
    ((7, "Mercury"), (17, "Venus"), (21, "Jupiter"), (28, "Mars"), (30, "Saturn")),
    ((6, "Saturn"), (14, "Mercury"), (21, "Jupiter"), (28, "Venus"), (30, "Mars")),
    ((7, "Mars"), (11, "Venus"), (19, "Mercury"), (24, "Jupiter"), (30, "Saturn")),
    ((12, "Jupiter"), (17, "Venus"), (21, "Mercury"), (26, "Mars"), (30, "Saturn")),
    ((7, "Mercury"), (14, "Jupiter"), (22, "Venus"), (26, "Saturn"), (30, "Mars")),
    ((7, "Mercury"), (13, "Venus"), (20, "Jupiter"), (25, "Mars"), (30, "Saturn")),
    ((12, "Venus"), (16, "Jupiter"), (19, "Mercury"), (28, "Mars"), (30, "Saturn")),
)

# Traditional Chaldean decan sequence used by TNK's Drekkana instructions.
_DECCAN_ORDER = ("Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter")

# Sextile, square and trine can perfect on either side of the slower planet.
_ASPECT_BRANCHES = (
    (0.0, 0, "conjunction", "hostile"),
    (60.0, 60, "sextile", "friendly"),
    (300.0, 60, "sextile", "friendly"),
    (90.0, 90, "square", "hostile"),
    (270.0, 90, "square", "hostile"),
    (120.0, 120, "trine", "friendly"),
    (240.0, 120, "trine", "friendly"),
    (180.0, 180, "opposition", "hostile"),
)

_YOGA_ORDER = (
    "ikkavala",
    "induvara",
    "itthasala",
    "isharafa",
    "nakta",
    "yamaya",
    "manau",
    "kamboola",
    "gairikamboola",
    "khallasara",
    "radda",
    "duphalikuttha",
    "dutthotthadivira",
    "tambira",
    "kuttha",
    "durapha",
)


def _normalise_signed(angle: float) -> float:
    return (angle + 180.0) % 360.0 - 180.0


def _pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def _planet_sign_idx(record: dict) -> int:
    if "sign_idx" in record:
        return int(record["sign_idx"]) % 12
    return int((float(record["longitude"]) % 360.0) // 30.0)


def _planet_degree(record: dict) -> float:
    if "degree" in record:
        return float(record["degree"]) % 30.0
    return float(record["longitude"]) % 30.0


def _hadda_lord(sign_idx: int, degree: float) -> str:
    for upper, lord in HADDA[sign_idx]:
        if degree < upper or math.isclose(degree, upper, abs_tol=1e-9):
            return lord
    return HADDA[sign_idx][-1][1]


def _drekkana_lord(longitude: float) -> str:
    decan_index = int((longitude % 360.0) // 10.0)
    return _DECCAN_ORDER[decan_index % len(_DECCAN_ORDER)]


def _navamsa_sign_idx(longitude: float) -> int:
    sign_idx = int((longitude % 360.0) // 30.0)
    degree = longitude % 30.0
    part = min(8, int(degree / (30.0 / 9.0)))
    if sign_idx in {0, 4, 8}:  # movable start Aries
        start = 0
    elif sign_idx in {1, 5, 9}:  # fixed start Capricorn
        start = 9
    elif sign_idx in {2, 6, 10}:  # dual start Libra
        start = 6
    else:  # watery start Cancer
        start = 3
    return (start + part) % 12


def _authority(chart: dict, planet: str) -> dict:
    """Return the four TNK Kamboola authority classes."""
    record = chart["planets"][planet]
    longitude = float(record["longitude"]) % 360.0
    sign_idx = _planet_sign_idx(record)
    degree = _planet_degree(record)
    basic = (
        chart.get("dignity", {})
        .get(planet, {})
        .get("basic", "neutral")
    )
    reasons = []
    if basic in {"exalted", "own", "own_sign", "moolatrikona"}:
        tier = "uttama"
        reasons.append(f"sign_{basic}")
    elif basic in {"debilitated", "enemy", "great_enemy"}:
        tier = "adhama"
        reasons.append(f"sign_{basic}")
    else:
        if _hadda_lord(sign_idx, degree) == planet:
            reasons.append("own_hadda")
        if _drekkana_lord(longitude) == planet:
            reasons.append("own_drekkana")
        if SIGN_LORDS[_navamsa_sign_idx(longitude)] == planet:
            reasons.append("own_navamsa")
        tier = "madhyama" if reasons else "sama"
    return {
        "tier": tier,
        "reasons": reasons,
        "sign_dignity": basic,
        "hadda_lord": _hadda_lord(sign_idx, degree),
        "drekkana_lord": _drekkana_lord(longitude),
        "navamsa_lord": SIGN_LORDS[_navamsa_sign_idx(longitude)],
    }


def _strength_profile(chart: dict, planet: str) -> dict:
    record = chart["planets"][planet]
    authority = _authority(chart, planet)
    house = record.get("house")
    strong_reasons = []
    weak_reasons = []
    if authority["tier"] in {"uttama", "madhyama"}:
        strong_reasons.extend(authority["reasons"])
    if house in {1, 4, 7, 10}:
        strong_reasons.append(f"kendra_house_{house}")
    elif house in {2, 5, 8, 11}:
        strong_reasons.append(f"panaphara_house_{house}")
    if authority["tier"] == "adhama":
        weak_reasons.extend(authority["reasons"])
    if house in {6, 8, 12}:
        weak_reasons.append(f"weak_house_{house}")
    speed = float(record.get("speed", 0.0))
    if bool(record.get("retrograde", speed < 0)):
        weak_reasons.append("retrograde")
    if abs(speed) < 1e-8:
        weak_reasons.append("stationary")
    if planet in chart.get("combustion", {}):
        weak_reasons.append("combust_lost_rays")
    if weak_reasons:
        status = "weak"
    elif strong_reasons:
        status = "strong"
    else:
        status = "neutral"
    return {
        "status": status,
        "authority": authority,
        "strong_reasons": strong_reasons,
        "weak_reasons": weak_reasons,
    }


def _nearest_aspect(relative_longitude: float) -> tuple[float, int, str, str, float]:
    candidates = []
    for branch, canonical, name, quality in _ASPECT_BRANCHES:
        error = _normalise_signed(relative_longitude - branch)
        candidates.append((abs(error), branch, canonical, name, quality, error))
    _, branch, canonical, name, quality, error = min(candidates, key=lambda item: item[0])
    return branch, canonical, name, quality, error


def _contact(planets: dict, a: str, b: str) -> dict | None:
    """Return the nearest in-deeptamsha Tajika contact for a pair."""
    pa, pb = planets[a], planets[b]
    speed_a = float(pa.get("speed", 0.0))
    speed_b = float(pb.get("speed", 0.0))
    if abs(speed_a) >= abs(speed_b):
        faster, slower = a, b
        fast, slow = pa, pb
        fast_speed, slow_speed = speed_a, speed_b
    else:
        faster, slower = b, a
        fast, slow = pb, pa
        fast_speed, slow_speed = speed_b, speed_a

    relative_longitude = (float(fast["longitude"]) - float(slow["longitude"])) % 360.0
    branch, canonical, aspect_name, quality, error = _nearest_aspect(relative_longitude)
    distance = abs(error)
    # Samjnatantra 2.4 and the worked examples preserved in Hayanaratna
    # 3.3 make the swifter planet the giver of light.  Its own deeptamsha
    # is therefore the operative boundary; averaging the two planets'
    # orbs incorrectly rejects the published Sun–Mars 14° example.
    orb_limit = TAJIKA_ORBS[faster]
    if distance > orb_limit + 1e-9:
        return None

    relative_speed = fast_speed - slow_speed
    trend = error * relative_speed
    exact_tolerance = 1.0 / 60.0
    if distance <= exact_tolerance:
        motion_state = "perfected"
        yoga = "itthasala_perfected"
        eta_days = 0.0
    elif trend < -1e-8:
        motion_state = "applying"
        yoga = "itthasala"
        eta_days = -error / relative_speed if abs(relative_speed) > 1e-10 else None
    elif trend > 1e-8:
        motion_state = "separating"
        yoga = "recent_perfection" if distance < 1.0 else "isharafa"
        eta_days = None
    else:
        motion_state = "stationary_relative"
        yoga = "indeterminate"
        eta_days = None

    return {
        "pair": [a, b],
        "faster": faster,
        "slower": slower,
        "aspect_angle": canonical,
        "aspect_branch": branch,
        "aspect_name": aspect_name,
        "quality": quality,
        "motion_state": motion_state,
        "yoga": yoga,
        "distance_from_exact_deg": round(distance, 6),
        "signed_error_deg": round(error, 6),
        "orb_limit_deg": round(orb_limit, 6),
        "orb_basis": f"{faster} own deeptamsha",
        "relative_speed_deg_per_day": round(relative_speed, 9),
        "linear_eta_days": round(eta_days, 4) if eta_days is not None and eta_days >= 0 else None,
        "retrograde": {
            a: bool(pa.get("retrograde", speed_a < 0)),
            b: bool(pb.get("retrograde", speed_b < 0)),
        },
    }


def _all_contacts(planets: dict) -> dict[tuple[str, str], dict]:
    available = [planet for planet in TAJIKA_PLANETS if planet in planets]
    contacts: dict[tuple[str, str], dict] = {}
    for index, a in enumerate(available):
        for b in available[index + 1 :]:
            record = _contact(planets, a, b)
            if record:
                contacts[_pair_key(a, b)] = record
    return contacts


def _is_applying(record: dict | None) -> bool:
    return bool(record and record["yoga"] in {"itthasala", "itthasala_perfected"})


def _is_separating(record: dict | None) -> bool:
    return bool(record and record["yoga"] in {"recent_perfection", "isharafa"})


def _global_house_yogas(planets: dict) -> tuple[dict, dict]:
    houses = [planets[p].get("house") for p in TAJIKA_PLANETS if p in planets]
    complete = len(houses) == 7 and all(isinstance(house, int) for house in houses)
    ikkavala = complete and all(house not in {3, 6, 9, 12} for house in houses)
    induvara = complete and all(house in {3, 6, 9, 12} for house in houses)
    return (
        {
            "present": ikkavala,
            "houses": houses,
            "source_rule": "TNK-2.3 Ikkavala",
            "input_complete": complete,
        },
        {
            "present": induvara,
            "houses": houses,
            "source_rule": "TNK-2.3 Induvara",
            "input_complete": complete,
        },
    )


def _nakta_candidates(planets, contacts, querent_lord, matter_lord, primary):
    if primary is not None:
        return []
    q_speed = abs(float(planets[querent_lord].get("speed", 0.0)))
    m_speed = abs(float(planets[matter_lord].get("speed", 0.0)))
    candidates = []
    for mediator in TAJIKA_PLANETS:
        if mediator in {querent_lord, matter_lord} or mediator not in planets:
            continue
        if abs(float(planets[mediator].get("speed", 0.0))) <= max(q_speed, m_speed):
            continue
        q_contact = contacts.get(_pair_key(querent_lord, mediator))
        m_contact = contacts.get(_pair_key(matter_lord, mediator))
        if (_is_separating(q_contact) and _is_applying(m_contact)) or (
            _is_separating(m_contact) and _is_applying(q_contact)
        ):
            candidates.append(
                {
                    "mediator": mediator,
                    "querent_contact": q_contact,
                    "matter_contact": m_contact,
                    "source_rule": "TNK-2.11-13 Nakta",
                }
            )
    return candidates


def _yamaya_candidates(planets, contacts, querent_lord, matter_lord, primary):
    if primary is not None:
        return []
    q_speed = abs(float(planets[querent_lord].get("speed", 0.0)))
    m_speed = abs(float(planets[matter_lord].get("speed", 0.0)))
    candidates = []
    for collector in TAJIKA_PLANETS:
        if collector in {querent_lord, matter_lord} or collector not in planets:
            continue
        if abs(float(planets[collector].get("speed", 0.0))) >= min(q_speed, m_speed):
            continue
        q_contact = contacts.get(_pair_key(querent_lord, collector))
        m_contact = contacts.get(_pair_key(matter_lord, collector))
        if _is_applying(q_contact) and _is_applying(m_contact):
            candidates.append(
                {
                    "collector": collector,
                    "querent_contact": q_contact,
                    "matter_contact": m_contact,
                    "source_rule": "TNK-2.14-16 Yamaya",
                }
            )
    return candidates


def _manau_candidates(contacts, querent_lord, matter_lord, primary):
    if not _is_applying(primary):
        return []
    primary_eta = primary.get("linear_eta_days")
    faster = primary["faster"]
    slower = primary["slower"]
    candidates = []
    for interferer in ("Mars", "Saturn"):
        if interferer in {querent_lord, matter_lord}:
            continue
        fast_contact = contacts.get(_pair_key(faster, interferer))
        slow_contact = contacts.get(_pair_key(slower, interferer))
        if not fast_contact:
            continue
        eta = fast_contact.get("linear_eta_days")
        precedes = (
            _is_applying(fast_contact)
            and eta is not None
            and (primary_eta is None or eta <= primary_eta)
        )
        enclosure = (
            fast_contact["aspect_angle"] == 0
            and fast_contact["yoga"] in {
                "itthasala",
                "itthasala_perfected",
                "recent_perfection",
            }
            and slow_contact is not None
        )
        if precedes or enclosure:
            candidates.append(
                {
                    "interferer": interferer,
                    "variant": "prior_prohibition" if precedes else "deeptamsha_enclosure",
                    "faster_contact": fast_contact,
                    "slower_contact": slow_contact,
                    "precedes_primary": precedes,
                    "source_rule": "TNK-2.17-21 Manau",
                }
            )
    return candidates


def _shunyamarga(chart: dict, planet: str, contacts: dict) -> dict:
    if planet not in chart.get("planets", {}):
        return {
            "present": False,
            "input_complete": False,
            "authority": None,
            "other_contacts": [],
            "source_rule": "TNK-2.39 Shunyamarga",
        }
    authority = _authority(chart, planet)
    other_contacts = [
        record
        for pair, record in contacts.items()
        if planet in pair
    ]
    present = authority["tier"] == "sama" and not other_contacts
    return {
        "present": present,
        "input_complete": True,
        "authority": authority,
        "other_contacts": other_contacts,
        "source_rule": "TNK-2.39 Shunyamarga",
    }


def _future_ingress_candidates(
    chart: dict,
    moving_planet: str,
    exclude: set[str],
) -> list[dict]:
    record = chart["planets"][moving_planet]
    longitude = float(record["longitude"]) % 360.0
    degree = longitude % 30.0
    boundary_distance = 30.0 - degree
    if boundary_distance > TAJIKA_ORBS[moving_planet]:
        return []
    next_sign = (_planet_sign_idx(record) + 1) % 12
    ingress = next_sign * 30.0
    candidates = []
    moving_speed = float(record.get("speed", 0.0))
    if moving_speed <= 0:
        return []
    for target in TAJIKA_PLANETS:
        if target == moving_planet or target in exclude or target not in chart["planets"]:
            continue
        target_record = chart["planets"][target]
        if _planet_sign_idx(target_record) != next_sign:
            continue
        profile = _strength_profile(chart, target)
        if profile["status"] != "strong":
            continue
        target_offset = (float(target_record["longitude"]) - ingress) % 360.0
        orb_limit = TAJIKA_ORBS[moving_planet]
        if target_offset <= orb_limit + 1e-9:
            candidates.append(
                {
                    "moving_planet": moving_planet,
                    "target": target,
                    "next_sign": SIGN_NAMES[next_sign],
                    "distance_to_ingress_deg": round(boundary_distance, 6),
                    "target_offset_from_ingress_deg": round(target_offset, 6),
                    "orb_limit_deg": round(orb_limit, 6),
                    "orb_basis": f"{moving_planet} own deeptamsha",
                    "target_strength": profile,
                }
            )
    return candidates


def _radda_candidate(chart: dict, contact: dict | None, role: str, querent: str, matter: str):
    if not _is_applying(contact):
        return None
    receiver = contact["slower"]
    profile = _strength_profile(chart, receiver)
    reasons = [
        reason
        for reason in profile["weak_reasons"]
        if reason in {
            "retrograde",
            "stationary",
            "combust_lost_rays",
            "sign_debilitated",
            "sign_enemy",
            "sign_great_enemy",
        }
    ]
    if not reasons:
        return None
    receiver_house = chart["planets"][receiver].get("house")
    other = contact["faster"]
    other_house = chart["planets"][other].get("house")
    sequence = "rejected_contact"
    if receiver_house in {3, 6, 9, 12} and other_house in {1, 4, 7, 10}:
        if receiver == querent and other == matter:
            sequence = "success_then_failure"
        elif receiver == matter and other == querent:
            sequence = "failure_then_success"
    return {
        "role": role,
        "contact_pair": contact["pair"],
        "receiver": receiver,
        "reasons": reasons,
        "sequence": sequence,
        "source_rule": "TNK-2.46-47 Radda",
    }


def _contact_modifier_inputs(primary, nakta, yamaya, manau, kamboola_contacts):
    records = [("primary", primary)]
    for name, items in (("nakta", nakta), ("yamaya", yamaya)):
        for index, item in enumerate(items, start=1):
            records.extend(
                (
                    (f"{name}_{index}_querent_leg", item["querent_contact"]),
                    (f"{name}_{index}_matter_leg", item["matter_contact"]),
                )
            )
    for index, item in enumerate(manau, start=1):
        records.extend(
            (
                (f"manau_{index}_fast_leg", item["faster_contact"]),
                (f"manau_{index}_slow_leg", item["slower_contact"]),
            )
        )
    for index, record in enumerate(kamboola_contacts, start=1):
        records.append((f"kamboola_{index}", record))
    return records


def compute(chart: dict, querent_lord: str, matter_lord: str) -> dict:
    """Compute all sixteen source-scoped Tajika yoga classifications."""
    if querent_lord == matter_lord:
        raise ValueError("querent_lord and matter_lord must be different planets")
    for planet in (querent_lord, matter_lord):
        if planet not in TAJIKA_PLANETS:
            raise ValueError(f"{planet!r} is not a supported Tajika planet")
        if planet not in chart.get("planets", {}):
            raise ValueError(f"{planet!r} is missing from chart data")

    planets = chart["planets"]
    contacts = _all_contacts(planets)
    primary = contacts.get(_pair_key(querent_lord, matter_lord))
    ikkavala, induvara = _global_house_yogas(planets)
    nakta = _nakta_candidates(planets, contacts, querent_lord, matter_lord, primary)
    yamaya = _yamaya_candidates(planets, contacts, querent_lord, matter_lord, primary)
    manau = _manau_candidates(contacts, querent_lord, matter_lord, primary)

    kamboola_contacts = []
    kamboola_grades = []
    if (
        "Moon" in planets
        and "Moon" not in {querent_lord, matter_lord}
        and _is_applying(primary)
    ):
        moon_tier = _authority(chart, "Moon")["tier"]
        for target in (querent_lord, matter_lord):
            record = contacts.get(_pair_key("Moon", target))
            if _is_applying(record):
                kamboola_contacts.append(record)
                target_tier = _authority(chart, target)["tier"]
                kamboola_grades.append(
                    {
                        "target": target,
                        "moon_tier": moon_tier,
                        "target_tier": target_tier,
                        "grade": f"{moon_tier}_{target_tier}",
                    }
                )

    moon_shunya = _shunyamarga(chart, "Moon", contacts)
    moon_primary_contacts = (
        [
            contacts.get(_pair_key("Moon", target))
            for target in (querent_lord, matter_lord)
            if target != "Moon"
        ]
        if "Moon" in planets
        else []
    )
    moon_has_primary_itthasala_or_conjunction = any(
        record
        and (
            _is_applying(record)
            or record["aspect_angle"] == 0
        )
        for record in moon_primary_contacts
    )
    khallasara_present = (
        "Moon" in planets
        and "Moon" not in {querent_lord, matter_lord}
        and moon_shunya["present"]
        and not moon_has_primary_itthasala_or_conjunction
    )

    gairikamboola_candidates = []
    if "Moon" in planets and _is_applying(primary) and moon_shunya["present"]:
        gairikamboola_candidates = _future_ingress_candidates(
            chart,
            "Moon",
            {querent_lord, matter_lord},
        )

    modifier_contacts = _contact_modifier_inputs(
        primary, nakta, yamaya, manau, kamboola_contacts
    )
    radda_candidates = []
    seen_radda = set()
    for role, record in modifier_contacts:
        candidate = _radda_candidate(
            chart, record, role, querent_lord, matter_lord
        )
        if candidate:
            key = (
                tuple(sorted(candidate["contact_pair"])),
                candidate["receiver"],
                tuple(candidate["reasons"]),
                candidate["sequence"],
            )
            if key not in seen_radda:
                seen_radda.add(key)
                radda_candidates.append(candidate)

    q_strength = _strength_profile(chart, querent_lord)
    m_strength = _strength_profile(chart, matter_lord)
    faster_strength = (
        _strength_profile(chart, primary["faster"]) if _is_applying(primary) else None
    )
    slower_strength = (
        _strength_profile(chart, primary["slower"]) if _is_applying(primary) else None
    )
    duphalikuttha_present = bool(
        _is_applying(primary)
        and faster_strength["status"] == "weak"
        and slower_strength["status"] == "strong"
    )

    dutthotthadivira_candidates = []
    for weak_primary, profile in (
        (querent_lord, q_strength),
        (matter_lord, m_strength),
    ):
        if profile["status"] != "weak":
            continue
        for helper in TAJIKA_PLANETS:
            if helper in {querent_lord, matter_lord} or helper not in planets:
                continue
            helper_profile = _strength_profile(chart, helper)
            helper_contact = contacts.get(_pair_key(weak_primary, helper))
            if helper_profile["status"] == "strong" and (
                _is_applying(helper_contact)
                or (
                    helper_contact
                    and helper_contact["aspect_angle"] == 0
                    and helper_contact["yoga"] == "recent_perfection"
                )
            ):
                dutthotthadivira_candidates.append(
                    {
                        "weak_primary": weak_primary,
                        "helper": helper,
                        "contact": helper_contact,
                        "helper_strength": helper_profile,
                        "source_rule": "TNK-2.49 Dutthotthadivira",
                    }
                )

    tambira_candidates = []
    if primary is None:
        for moving in (querent_lord, matter_lord):
            tambira_candidates.extend(
                _future_ingress_candidates(
                    chart,
                    moving,
                    {querent_lord, matter_lord},
                )
            )

    kuttha_candidates = []
    durapha_candidates = []
    for role, record in modifier_contacts:
        if not _is_applying(record):
            continue
        for planet in record["pair"]:
            profile = _strength_profile(chart, planet)
            if profile["status"] == "strong":
                kuttha_candidates.append(
                    {
                        "role": role,
                        "planet": planet,
                        "profile": profile,
                        "source_rule": "TNK-2.51-54 Kuttha",
                    }
                )
            if profile["status"] == "weak":
                durapha_candidates.append(
                    {
                        "role": role,
                        "planet": planet,
                        "profile": profile,
                        "radda_has_result_priority": any(
                            item["receiver"] == planet
                            and _pair_key(*item["contact_pair"]) == _pair_key(*record["pair"])
                            for item in radda_candidates
                        ),
                        "source_rule": "TNK-2.55-59 Durapha",
                    }
                )

    classical_timing = {
        "status": "unavailable",
        "source_rule": (
            "TNK-2.5-6 Hindi commentary; Hayanaratna 3.3 "
            "quoting Tajikayogasudhanidhi 6.35"
        ),
        "scope": "direct querent-lord/matter-lord Itthasala only",
    }
    if _is_applying(primary):
        classical_timing = {
            "status": "candidate",
            "source_rule": (
                "TNK-2.5-6 Hindi commentary; Hayanaratna 3.3 "
                "quoting Tajikayogasudhanidhi 6.35"
            ),
            "scope": "direct querent-lord/matter-lord Itthasala only",
            "degree_difference": primary["distance_from_exact_deg"],
            "candidate_days": round(primary["distance_from_exact_deg"] * 12.0, 4),
            "warning": (
                "Classical degree-difference scale; not an ephemeris guarantee "
                "and never imported into the Parashari standard layer."
            ),
        }

    yogas = {
        "ikkavala": ikkavala,
        "induvara": induvara,
        "itthasala": {
            "present": _is_applying(primary),
            "contact": primary if _is_applying(primary) else None,
            "source_rule": "TNK-2.4-9 Itthasala",
        },
        "isharafa": {
            "present": bool(primary and primary["yoga"] == "isharafa"),
            "contact": primary if primary and primary["yoga"] == "isharafa" else None,
            "source_rule": "TNK-2.10 Isharafa",
        },
        "nakta": {"present": bool(nakta), "candidates": nakta, "source_rule": "TNK-2.11-13"},
        "yamaya": {"present": bool(yamaya), "candidates": yamaya, "source_rule": "TNK-2.14-16"},
        "manau": {"present": bool(manau), "candidates": manau, "source_rule": "TNK-2.17-21"},
        "kamboola": {
            "present": bool(kamboola_contacts),
            "moon_contacts": kamboola_contacts,
            "grades": kamboola_grades,
            "source_rule": "TNK-2.22-38 Kamboola",
        },
        "gairikamboola": {
            "present": bool(gairikamboola_candidates),
            "candidates": gairikamboola_candidates,
            "moon_shunyamarga": moon_shunya,
            "source_rule": "TNK-2.39-44 Gairikamboola",
        },
        "khallasara": {
            "present": khallasara_present,
            "moon_shunyamarga": moon_shunya,
            "moon_primary_contacts": [
                record for record in moon_primary_contacts if record
            ],
            "source_rule": "TNK-2.45 Khallasara",
            "scope_note": "Kamboola modifier only; no standard-layer authority.",
        },
        "radda": {
            "present": bool(radda_candidates),
            "candidates": radda_candidates,
            "source_rule": "TNK-2.46-47 Radda",
        },
        "duphalikuttha": {
            "present": duphalikuttha_present,
            "faster_strength": faster_strength,
            "slower_strength": slower_strength,
            "source_rule": "TNK-2.48 Duphalikuttha",
        },
        "dutthotthadivira": {
            "present": bool(dutthotthadivira_candidates),
            "candidates": dutthotthadivira_candidates,
            "source_rule": "TNK-2.49 Dutthotthadivira",
        },
        "tambira": {
            "present": bool(tambira_candidates),
            "candidates": tambira_candidates,
            "source_rule": "TNK-2.50 Tambira",
        },
        "kuttha": {
            "present": bool(kuttha_candidates),
            "candidates": kuttha_candidates,
            "source_rule": "TNK-2.51-54 Kuttha",
        },
        "durapha": {
            "present": bool(durapha_candidates),
            "candidates": durapha_candidates,
            "source_rule": "TNK-2.55-59 Durapha",
        },
    }

    return {
        "scope": "Tajika Nilakanthi sixteen-yoga classifier; isolated experimental overlay",
        "source_basis": [
            "Tajika Nilakanthi, Samjnatantra 2.3-59",
            (
                "Balabhadra, Hayanaratna chapter 3 (Gansten 2020 critical "
                "Sanskrit-English edition)"
            ),
        ],
        "primary_pair": {
            "querent_lord": querent_lord,
            "matter_lord": matter_lord,
            "contact": primary,
            "querent_strength": q_strength,
            "matter_strength": m_strength,
        },
        "yoga_order": list(_YOGA_ORDER),
        "yogas": yogas,
        # Stable top-level aliases retained for existing artifact consumers.
        "nakta": nakta,
        "yamaya": yamaya,
        "manau": manau,
        "kamboola": yogas["kamboola"],
        "gairikamboola": yogas["gairikamboola"],
        "khallasara": yogas["khallasara"],
        "radda": yogas["radda"],
        "duphalikuttha": yogas["duphalikuttha"],
        "dutthotthadivira": yogas["dutthotthadivira"],
        "tambira": yogas["tambira"],
        "kuttha": yogas["kuttha"],
        "durapha": yogas["durapha"],
        "all_in_orb_contacts": list(contacts.values()),
        "config": {
            "planets": list(TAJIKA_PLANETS),
            "aspects_deg": [0, 60, 90, 120, 180],
            "orbs": TAJIKA_ORBS,
            "pair_orb_formula": "swifter planet's own deeptamsha",
            "hadda": "TNK-2.33-38",
            "nodes": "excluded",
            "retrograde": "included in geometry; evaluated by yoga-specific rules",
        },
        "deferred_yogas": [],
        "timing": classical_timing,
        "production_status": "experimental_pending_published_example_suite",
        "verdict_authority": "none; this overlay does not change the standard-layer verdict",
    }


def _format_contact(record: dict | None) -> str:
    if not record:
        return "No contact within current deeptamsha"
    aliases = {
        "itthasala": "Itthasala / Muthashila (applying)",
        "itthasala_perfected": "Itthasala / Muthashila (exact aspect)",
        "recent_perfection": "Recent perfection (within 1 deg)",
        "isharafa": "Isharafa / Musharipha (separating)",
        "indeterminate": "Relative motion indeterminate",
    }
    quality = {
        "friendly": "Friendly Aspect",
        "hostile": "Inimical Aspect",
    }[record["quality"]]
    return (
        f"{record['faster']}–{record['slower']} {record['aspect_name']} "
        f"({record['aspect_angle']} deg), {aliases[record['yoga']]}; {quality}; "
        f"Separation from exact: {record['distance_from_exact_deg']:.3f} deg / "
        f"Orb limit: {record['orb_limit_deg']:.3f} deg"
    )


def format_tajika_section(data: dict) -> str:
    primary = data["primary_pair"]
    timing = data["timing"]
    active_yogas = [
        name for name in data["yoga_order"] if data["yogas"][name]["present"]
    ]
    contact = primary["contact"]
    if not contact:
        contact_reading = (
            "The two indicator planets do not currently form a recognized direct approach; "
            "this indicates non-direct progression and does not by itself mean failure."
        )
    elif contact["yoga"] in {"itthasala", "itthasala_perfected"}:
        contact_reading = (
            "The two indicator planets are directly applying towards each other; "
            + (
                "the dynamic is harmonious, but requires real-world action to materialize."
                if contact["quality"] == "friendly"
                else "the approach carries friction; contact does not automatically guarantee ease."
            )
        )
    elif contact["yoga"] == "recent_perfection":
        contact_reading = "The two indicator planets have just crossed exact perfection; peak contact has passed but separation is incomplete."
    elif contact["yoga"] == "isharafa":
        contact_reading = "The two indicator planets are separating, indicating direct contact has passed its peak."
    else:
        contact_reading = "Contact status is indeterminate; geometric facts retained."

    plain_process_notes = []
    technical_process_notes = []
    if data["nakta"]:
        plain_process_notes.append(
            "A third factor bridges the interaction between the two sides"
        )
        technical_process_notes.append("Nakta: third-planet transmission candidate present")
    if data["yamaya"]:
        plain_process_notes.append(
            "A third factor simultaneously connects both sides, forming a potential coordination point"
        )
        technical_process_notes.append("Yamaya: third-planet collection candidate present")
    if data["dutthotthadivira"]["present"]:
        plain_process_notes.append(
            "Additional assistance supports the weaker party to continue interaction"
        )
        technical_process_notes.append(
            "Dutthotthadivira: weaker primary planet receives assistance"
        )
    if data["manau"]:
        plain_process_notes.append(
            "Stress or conflict intervenes before direct connection can establish"
        )
        technical_process_notes.append("Manau: Mars/Saturn intervention candidate")
    if data["radda"]["present"]:
        plain_process_notes.append(
            "The receiving side exhibits hesitation, retraction, or recovery after obstacle"
        )
        technical_process_notes.append("Radda: receiving planet retraction candidate")
    if data["duphalikuttha"]["present"]:
        plain_process_notes.append(
            "Asymmetric capacity; the stronger side must take on greater progression effort"
        )
        technical_process_notes.append(
            "Duphalikuttha: faster planet weak, slower planet strong"
        )
    if data["durapha"]["present"]:
        plain_process_notes.append(
            "A participating party currently lacks capacity to sustain contact"
        )
        technical_process_notes.append("Durapha: participating planet shows functional disability")
    if data["kamboola"]["present"]:
        plain_process_notes.append(
            "Current conditions provide additional momentum to direct contact"
        )
        technical_process_notes.append("Kamboola: Moon provides graduated reinforcement")
    if data["khallasara"]["present"]:
        plain_process_notes.append(
            "Current conditions do not sustain the interaction, providing no extra momentum"
        )
        technical_process_notes.append(
            "Khallasara: Shunyamarga condition active, modifying Kamboola"
        )
    if data["kuttha"]["present"]:
        plain_process_notes.append(
            "Participating planet exhibits strong real-world capacity"
        )
        technical_process_notes.append("Kuttha: participating planet has strong conditions")
    if data["gairikamboola"]["present"] or data["tambira"]["present"]:
        plain_process_notes.append(
            "New contact opportunities may emerge after conditions shift"
        )
        technical_process_notes.append(
            "Gairikamboola/Tambira: future contact candidate after ingress"
        )

    if not contact:
        if data["dutthotthadivira"]["present"]:
            plain_summary = (
                "Direct natural approach is not currently present, but auxiliary factors assist the weaker party. "
                "Progress requires appropriate communication channels or environmental intermediaries."
            )
        elif data["nakta"] or data["yamaya"]:
            plain_summary = (
                "Direct approach is absent, but reconnecting pathways exist via third parties, messages, or shared environments."
            )
        elif data["gairikamboola"]["present"] or data["tambira"]["present"]:
            plain_summary = (
                "Direct momentum is not yet formed; contact opportunities may arise following future shifts in conditions."
            )
        else:
            plain_summary = (
                "Direct momentum is absent, and no substitute mechanisms were identified. This describes current process, not permanent failure."
            )
    elif contact["yoga"] in {"itthasala", "itthasala_perfected"}:
        plain_summary = (
            "Direct approach or reconnection trend is present. "
            + (
                "Progress is relatively coordinated, though real-world follow-through is essential."
                if contact["quality"] == "friendly"
                else "However, contact carries friction; reaching out does not automatically imply smooth relation."
            )
        )
    elif contact["yoga"] == "recent_perfection":
        plain_summary = (
            "A peak contact point was recently crossed; focus should remain on recent interactions rather than treating them as unstarted."
        )
    elif contact["yoga"] == "isharafa":
        plain_summary = (
            "Parties are moving away from peak contact; dynamic may quiet down, but this does not signify definitive conclusion."
        )
    else:
        plain_summary = "Current contact direction is indeterminate; process facts retained."

    timing_reading = (
        (
            f"Classical ratio candidate of approximately {timing['candidate_days']} days present; "
            "belongs strictly to the Tajika sub-layer, not an astronomical guarantee."
        )
        if timing["status"] == "candidate"
        else "No direct applying primary contact; this sub-layer does not permit timing output."
    )

    lines = [
        "# Tajika Sub-Layer Technical Sheet: Interaction Dynamics and Obstacles",
        "",
        "> This sub-layer explains how parties interact or meet obstacles; it does not alter standard-layer verdicts.",
        "",
    ]
    if data.get("judgment_time"):
        lines.extend(
            [
                "## Input",
                "",
                (
                    f"- Instant: {data['judgment_time']} "
                    f"({data['judgment_timezone']})"
                ),
                (
                    f"- Location: {data['judgment_location']['latitude']}, "
                    f"{data['judgment_location']['longitude']}"
                ),
                "",
            ]
        )
    lines.extend(
        [
        "## Summary",
        "",
        f"**Verdict**: {plain_summary}",
        "",
        f"**Direct Approach**: {contact_reading}",
        "",
        f"**Process Factors / Obstacles**: "
        f"{'; '.join(plain_process_notes) if plain_process_notes else 'No additional assistance or interference detected.'}",
        "",
        f"**Timing**: {timing_reading}",
        "",
        (
            "**Usage Guidelines**: Treat this as process explanation. Technical terms should not be conflated with success or failure."
        ),
        "",
        "## Technical Audit",
        "",
        f"- Active Yogas: {' / '.join(active_yogas) or 'None'}",
        (
            "- Process Corrections: "
            + (
                "; ".join(technical_process_notes)
                if technical_process_notes
                else "None"
            )
        ),
        "- Authority Boundary: Explains contact dynamics only; does not generate or alter standard-layer internal tiers (Favorable / Balanced / Unfavorable).",
        "",
        "## Primary Planet Pair",
        "",
        f"- Querent Lord: **{primary['querent_lord']}**",
        f"- Matter Lord: **{primary['matter_lord']}**",
        f"- Current Relationship: {_format_contact(primary['contact'])}",
        "",
        "## Sixteen Yogas Table",
        "",
        "| # | Yoga | Status |",
        "|---:|---|---|",
        ]
    )
    for index, name in enumerate(data["yoga_order"], start=1):
        record = data["yogas"][name]
        lines.append(f"| {index} | {name} | {'Present' if record['present'] else 'Absent'} |")

    lines.extend(["", "## Detection Details", ""])
    details = []
    if data["nakta"]:
        details.append(
            "- Nakta: "
            + "; ".join(item["mediator"] for item in data["nakta"])
        )
    if data["yamaya"]:
        details.append(
            "- Yamaya: "
            + "; ".join(item["collector"] for item in data["yamaya"])
        )
    if data["manau"]:
        details.append(
            "- Manau: "
            + "; ".join(
                f"{item['interferer']} / {item['variant']}"
                for item in data["manau"]
            )
        )
    if data["gairikamboola"]["present"]:
        details.append(
            "- Gairikamboola: "
            + "; ".join(
                f"{item['moving_planet']} ingresses into {item['next_sign']} before contacting {item['target']}"
                for item in data["gairikamboola"]["candidates"]
            )
        )
    if data["duphalikuttha"]["present"]:
        details.append(
            f"- Duphalikuttha: Faster planet {primary['contact']['faster']} weak, slower planet {primary['contact']['slower']} strong"
        )
    if data["dutthotthadivira"]["present"]:
        details.append(
            "- Dutthotthadivira: "
            + "; ".join(
                f"Weaker primary {item['weak_primary']} assisted by {item['helper']} ({_format_contact(item['contact'])})"
                for item in data["dutthotthadivira"]["candidates"]
            )
        )
    if data["tambira"]["present"]:
        details.append(
            "- Tambira: "
            + "; ".join(
                f"{item['moving_planet']} ingresses into {item['next_sign']} before contacting {item['target']}"
                for item in data["tambira"]["candidates"]
            )
        )
    if data["kuttha"]["present"]:
        details.append(
            "- Kuttha: "
            + "; ".join(
                f"{item['planet']} ({item['role']})"
                for item in data["kuttha"]["candidates"]
            )
        )
    lines.extend(details or ["- No additional authorized yoga details beyond primary pair."])

    lines.extend(["", "## Key Corrections", ""])
    if data["kamboola"]["present"]:
        grades = " / ".join(item["grade"] for item in data["kamboola"]["grades"])
        lines.append(f"- Kamboola: Present; Grades {grades}")
    else:
        lines.append("- Kamboola: Absent")
    lines.append(
        "- Khallasara: "
        + (
            "Active; Moon satisfies Shunyamarga and no Itthasala/conjunction with primaries; modifies Kamboola"
            if data["khallasara"]["present"]
            else "Inactive"
        )
    )
    if data["radda"]["present"]:
        lines.append(
            "- Radda: "
            + "; ".join(
                f"{item['receiver']} {item['reasons']} / {item['sequence']}"
                for item in data["radda"]["candidates"]
            )
        )
    else:
        lines.append("- Radda: Absent")
    if data["durapha"]["present"]:
        lines.append(
            "- Durapha: "
            + "; ".join(
                f"{item['planet']} {item['profile']['weak_reasons']}"
                for item in data["durapha"]["candidates"]
            )
        )
    else:
        lines.append("- Durapha: Absent")

    lines.extend(["", "## Timing and Boundary", ""])
    if timing["status"] == "candidate":
        lines.append(
            f"- TNK Primary Itthasala Candidate: approx **{timing['candidate_days']} days** "
            f"(arc diff {timing['degree_difference']} deg x 12); classical ratio candidate, not astronomical guarantee."
        )
    else:
        lines.append("- No authorized TNK primary Itthasala timing for this chart.")
    lines.extend(
        [
            "- Rahu/Ketu do not participate in this sub-layer.",
            "- This sheet does not generate or alter standard-layer internal tiers (Favorable / Balanced / Unfavorable).",
            f"- Production status: {data['production_status']}.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Tajika sixteen-yoga overlay calculator")
    parser.add_argument(
        "--datetime",
        required=True,
        help='"YYYY-MM-DD HH:MM[:SS[.ffffff]]" or "now"',
    )
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--tz", required=True)
    parser.add_argument("--querent-lord", required=True, choices=TAJIKA_PLANETS)
    parser.add_argument("--matter-lord", required=True, choices=TAJIKA_PLANETS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    dt = parse_local_datetime(args.datetime, args.tz)
    chart = calculate_prashna_chart(dt, args.lat, args.lon, args.tz)
    result = compute(chart, args.querent_lord, args.matter_lord)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_tajika_section(result), end="")


if __name__ == "__main__":
    main()
