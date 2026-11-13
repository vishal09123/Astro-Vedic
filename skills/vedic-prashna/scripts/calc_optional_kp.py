#!/usr/bin/env python3
"""Independent KP horary data engine using the classical 1–249 mode.

The module is intentionally separate from the Parashari Prashna builder. It uses:
- Krishnamurti ayanamsa;
- a 1–249 querent number to set the nirayana Ascendant;
- Placidus cusps derived from that Ascendant and the judgment-place latitude;
- planets at the judgment time;
- the KP significator order documented in K.S. Krishnamurti's Readers;
- question-specific house groups rather than a blanket 6/8/12 rule.

Timing is source-scoped to the independent horary Moon balance,
Dasha/Bhukti/Antara/Shookshma, Ruling-Planet intersection and the Moon/Sun/Jupiter
transit scale printed in Reader VI.  It never borrows the standard-layer Moon
ingress or a natal chart's Dasha.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import math
import sys
from datetime import datetime, timedelta, timezone as datetime_timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CALC = _HERE.parent.parent / "vedic-calculator" / "scripts"
if str(_CALC) not in sys.path:
    sys.path.insert(0, str(_CALC))

from engine import (  # noqa: E402
    DASHA_ORDER,
    DASHA_YEARS,
    NAKSHATRAS,
    SIGNS,
)
import swisseph as swe  # noqa: E402
from prashna_time import local_datetime_to_jd, parse_local_datetime  # noqa: E402


NAK_SPAN = 360.0 / 27.0
TOTAL_YEARS = float(sum(DASHA_YEARS.values()))
VIMSHOTTARI_YEAR_DAYS = 365.2425
PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
}
SEVEN_PLANETS = tuple(PLANET_IDS)
NODES = ("Rahu", "Ketu")
ALL_KP_PLANETS = SEVEN_PLANETS + NODES
KP_ASPECT_ANGLES = (0, 30, 45, 60, 90, 120, 135, 180)
KP_ORBS = {
    "Sun": 15.0,
    "Moon": 15.0,
    "Mars": 7.0,
    "Mercury": 7.0,
    "Jupiter": 9.0,
    "Venus": 7.0,
    "Saturn": 9.0,
    # Reader VI prints Uranus 7°, but Uranus is outside this nine-graha stack.
}
SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}
WEEKDAY_LORDS = {
    0: "Moon",
    1: "Mars",
    2: "Mercury",
    3: "Jupiter",
    4: "Venus",
    5: "Saturn",
    6: "Sun",
}
WEEKDAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

# Reader VI explicitly excludes Rahu and Ketu from the horary retrograde
# rejection rule. Their normal zodiacal motion is opposite to that of the
# seven visible planets; it is not treated as a temporary retrograde station.
RETROGRADE_FILTER_PLANETS = frozenset(
    {"Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
)

TOPIC_RULES = {
    "love-materialization": {
        "outcome_scope": "explicit-mutual-relationship",
        "judgment_cusp": 5,
        "positive_houses": (7, 11),
        "positive_match": "all",
        "negative_houses": (6, 12),
        "negative_match": "any",
        "source": (
            "KSK Reader VI, 'Will my Love Affairs Materialise?': "
            "5th cusp sub-lord's star lord; 7 and 11 promise, "
            "6 or 12 deny"
        ),
    },
    "business-partnership-continuity": {
        "outcome_scope": "business-partnership-continuity",
        "judgment_cusp": 7,
        "positive_houses": (5, 11),
        "positive_match": "any",
        "negative_houses": (6, 12),
        "negative_match": "any",
        "source": (
            "KSK Reader VI, number 156 'Business and Partnership': "
            "7th cusp sub-lord; 5 or 11 continue, 6 or 12 break"
        ),
    },
}

KP_OUTCOME_SCOPES = {
    "explicit-mutual-relationship": {
        "topic": "love-materialization",
        "supported": True,
        "definition": "Whether both parties establish an explicit, committed, ongoing romantic partnership",
        "excluded_outcomes": (
            "Contact resumption only",
            "Atmosphere rewarming only",
            "Ambiguity resumption only",
            "Secret feelings or intentions of the other party",
        ),
    },
    "romantic-interaction-rewarming": {
        "topic": None,
        "supported": False,
        "definition": "Whether both parties resume relaxed, flirtatious, or warm interactions",
    },
    "romantic-contact-resumption": {
        "topic": None,
        "supported": False,
        "definition": "Whether both parties re-establish contact, replies, or meetings",
    },
    "private-feelings-or-intent": {
        "topic": None,
        "supported": False,
        "definition": "Secret feelings, thoughts, or intentions of the other party",
    },
    "business-partnership-continuity": {
        "topic": "business-partnership-continuity",
        "supported": True,
        "definition": "Whether existing commercial partnership will continue",
        "excluded_outcomes": (
            "Single reply only",
            "Secret intentions of counterparty",
            "Commencing unestablished partnership",
        ),
    },
}

_SIGN_BOUNDARIES = tuple(index * 30.0 for index in range(12))
_STAR_BOUNDARIES = tuple(index * NAK_SPAN for index in range(27))
SIGNIFICATOR_LEVEL_RANK = {
    "A_star_of_occupant": 1,
    "A_star_of_node_agent": 1,
    "B_occupant": 2,
    "C_star_of_owner": 3,
    "D_owner": 4,
}


def validate_outcome_scope(topic: str, outcome_scope: str) -> dict:
    """Fail closed when the observable outcome is outside a sourced KP topic."""
    if topic not in TOPIC_RULES:
        raise ValueError(f"Unsupported KP topic: {topic}")
    if outcome_scope not in KP_OUTCOME_SCOPES:
        raise ValueError(f"Unknown KP outcome scope: {outcome_scope}")
    scope = KP_OUTCOME_SCOPES[outcome_scope]
    if not scope["supported"]:
        raise ValueError(
            f"KP outcome scope '{outcome_scope}' is not source-validated; "
            "do not substitute love-materialization or another supported topic"
        )
    if scope["topic"] != topic:
        raise ValueError(
            f"KP outcome scope '{outcome_scope}' belongs to topic "
            f"'{scope['topic']}', not '{topic}'"
        )
    return deepcopy(scope)


def _normalise_signed(angle: float) -> float:
    return (angle + 180.0) % 360.0 - 180.0


def _circular_distance(a: float, b: float) -> float:
    return abs(_normalise_signed(a - b))


def _sign_of(longitude: float) -> str:
    return SIGNS[int((longitude % 360.0) / 30.0) % 12]


def _sign_lord(longitude: float) -> str:
    return SIGN_LORDS[_sign_of(longitude)]


def _star_index(longitude: float) -> int:
    return min(26, int((longitude % 360.0) / NAK_SPAN))


def _star_lord(longitude: float) -> str:
    return NAKSHATRAS[_star_index(longitude)][1]


def _sub_boundaries() -> tuple[float, ...]:
    boundaries = []
    for nak_index, (_, star_lord) in enumerate(NAKSHATRAS):
        current = nak_index * NAK_SPAN
        boundaries.append(current)
        start_index = DASHA_ORDER.index(star_lord)
        for offset in range(9):
            lord = DASHA_ORDER[(start_index + offset) % 9]
            current += NAK_SPAN * DASHA_YEARS[lord] / TOTAL_YEARS
            boundaries.append(current % 360.0)
    return tuple(sorted(set(round(value % 360.0, 12) for value in boundaries)))


_SUB_BOUNDARIES = _sub_boundaries()


def _sub_lord(longitude: float) -> str:
    longitude %= 360.0
    nak_index = _star_index(longitude)
    star_lord = NAKSHATRAS[nak_index][1]
    offset_in_nak = longitude - nak_index * NAK_SPAN
    start_index = DASHA_ORDER.index(star_lord)
    cumulative = 0.0
    for offset in range(9):
        lord = DASHA_ORDER[(start_index + offset) % 9]
        span = NAK_SPAN * DASHA_YEARS[lord] / TOTAL_YEARS
        if offset_in_nak < cumulative + span - 1e-10:
            return lord
        cumulative += span
    return DASHA_ORDER[(start_index + 8) % 9]


def _ordered_lords(first_lord: str) -> tuple[str, ...]:
    start = DASHA_ORDER.index(first_lord)
    return tuple(DASHA_ORDER[(start + offset) % 9] for offset in range(9))


def _split_angular_segment(
    start: float,
    end: float,
    first_lord: str,
) -> list[dict]:
    current = start
    result = []
    span = end - start
    for index, lord in enumerate(_ordered_lords(first_lord)):
        child_end = (
            end
            if index == 8
            else current + span * DASHA_YEARS[lord] / TOTAL_YEARS
        )
        result.append({"lord": lord, "start": current, "end": child_end})
        current = child_end
    return result


def _vimshottari_path(longitude: float, depth: int = 4) -> list[dict]:
    """Return the KP star/sub/sub-sub/sub-sub-sub path at a longitude.

    Reader III divides every parent period in Vimshottari proportions, starting
    from the parent lord.  The same construction therefore supplies both the
    zodiacal KP levels and the current horary Moon period chain.
    """
    if not 1 <= depth <= 4:
        raise ValueError("depth must be between 1 and 4")
    longitude %= 360.0
    star_index = _star_index(longitude)
    star_start = star_index * NAK_SPAN
    star_end = star_start + NAK_SPAN
    star_lord = NAKSHATRAS[star_index][1]
    path = [
        {
            "level": "mahadasha",
            "lord": star_lord,
            "start_longitude": star_start,
            "end_longitude": star_end,
        }
    ]
    parent_start = star_start
    parent_end = star_end
    parent_lord = star_lord
    for level in ("bhukti", "antara", "shookshma")[: depth - 1]:
        children = _split_angular_segment(parent_start, parent_end, parent_lord)
        selected = None
        for index, child in enumerate(children):
            # KP number segments use their exact starting boundary.  When a
            # computed longitude is indistinguishable from an interior start,
            # select the segment beginning there (the right-hand segment).
            if index and math.isclose(
                longitude,
                child["start"],
                rel_tol=0.0,
                abs_tol=1e-10,
            ):
                selected = child
                break
            if child["start"] <= longitude < child["end"]:
                selected = child
                break
        if selected is None and math.isclose(
            longitude,
            children[-1]["end"],
            rel_tol=0.0,
            abs_tol=1e-10,
        ):
            # A longitude just below the parent end can round to that end at a
            # deeper subdivision.  It still belongs to the final child.
            selected = children[-1]
        if selected is None:
            raise ValueError(
                "Longitude fell outside a contiguous Vimshottari subdivision"
            )
        path.append(
            {
                "level": level,
                "lord": selected["lord"],
                "start_longitude": selected["start"],
                "end_longitude": selected["end"],
            }
        )
        parent_start = selected["start"]
        parent_end = selected["end"]
        parent_lord = selected["lord"]
    return path


def _distance_to_boundaries(longitude: float, boundaries: tuple[float, ...]) -> float:
    return min(_circular_distance(longitude, boundary) for boundary in boundaries)


def _format_degree(longitude: float) -> str:
    within_sign = longitude % 30.0
    degree = int(within_sign)
    minutes_float = (within_sign - degree) * 60.0
    minute = int(minutes_float)
    second = int(round((minutes_float - minute) * 60.0))
    if second == 60:
        second = 0
        minute += 1
    if minute == 60:
        minute = 0
        degree += 1
    return f"{degree}°{minute:02d}'{second:02d}\""


def build_number_table() -> list[dict]:
    """Build the 249 sign/star/sub segments described in Reader III/VI."""
    segments = []
    for nak_index, (nak_name, star_lord) in enumerate(NAKSHATRAS):
        current = nak_index * NAK_SPAN
        start_index = DASHA_ORDER.index(star_lord)
        for offset in range(9):
            sub_lord = DASHA_ORDER[(start_index + offset) % 9]
            sub_end = current + NAK_SPAN * DASHA_YEARS[sub_lord] / TOTAL_YEARS
            split_points = [current]
            sign_boundary = (math.floor(current / 30.0) + 1) * 30.0
            while sign_boundary < sub_end - 1e-10:
                split_points.append(sign_boundary)
                sign_boundary += 30.0
            split_points.append(sub_end)
            for start, end in zip(split_points, split_points[1:]):
                segments.append(
                    {
                        "number": len(segments) + 1,
                        "start_lon": start % 360.0,
                        "end_lon": end % 360.0 if end < 360.0 else 360.0,
                        "sign": _sign_of(start),
                        "sign_lord": _sign_lord(start),
                        "nakshatra": nak_name,
                        "star_lord": star_lord,
                        "sub_lord": sub_lord,
                    }
                )
            current = sub_end
    if len(segments) != 249:
        raise RuntimeError(f"KP number table must contain 249 segments, got {len(segments)}")
    return segments


NUMBER_TABLE = build_number_table()


def _ayanamsa_for_mode(jd: float, mode: int) -> float:
    swe.set_sid_mode(mode)
    value = swe.get_ayanamsa_ut(jd)
    # The shared Parashari engine uses True Citra. Restore it so importing this
    # independent module cannot silently mutate the standard stack.
    swe.set_sid_mode(swe.SIDM_TRUE_CITRA)
    return value


def _asc_for_armc(armc: float, latitude: float, obliquity: float) -> float:
    return swe.houses_armc(armc % 360.0, latitude, obliquity, b"P")[1][0] % 360.0


def _solve_armc_for_asc(target_asc: float, latitude: float, obliquity: float) -> float:
    """Solve ARMC for a requested tropical Ascendant."""
    best = min(
        range(360),
        key=lambda armc: _circular_distance(
            _asc_for_armc(float(armc), latitude, obliquity), target_asc
        ),
    )
    armc = float(best)
    for _ in range(20):
        current = _asc_for_armc(armc, latitude, obliquity)
        error = _normalise_signed(current - target_asc)
        if abs(error) < 1e-9:
            break
        step = 1e-4
        next_asc = _asc_for_armc(armc + step, latitude, obliquity)
        derivative = _normalise_signed(next_asc - current) / step
        if abs(derivative) < 1e-8:
            raise RuntimeError("Could not solve Placidus ARMC for requested KP Ascendant")
        armc = (armc - error / derivative) % 360.0
    solved = _asc_for_armc(armc, latitude, obliquity)
    if _circular_distance(solved, target_asc) > 1e-6:
        raise RuntimeError("KP Ascendant solver did not converge")
    return armc


def _house_of(longitude: float, cusps: list[float]) -> int:
    longitude %= 360.0
    for index, start in enumerate(cusps):
        end = cusps[(index + 1) % 12]
        span = (end - start) % 360.0
        offset = (longitude - start) % 360.0
        if offset < span or math.isclose(offset, 0.0, abs_tol=1e-9):
            return index + 1
    raise RuntimeError(f"Could not assign longitude {longitude} to a Placidus house")


def _position_record(name: str, longitude: float, speed: float | None = None) -> dict:
    period_path = _vimshottari_path(longitude)
    record = {
        "name": name,
        "longitude": longitude % 360.0,
        "position": _format_degree(longitude),
        "sign": _sign_of(longitude),
        "sign_lord": _sign_lord(longitude),
        "nakshatra": NAKSHATRAS[_star_index(longitude)][0],
        "star_lord": _star_lord(longitude),
        "sub_lord": _sub_lord(longitude),
        "sub_sub_lord": period_path[2]["lord"],
        "sub_sub_sub_lord": period_path[3]["lord"],
        "boundary_distance_arcmin": {
            "sign": round(_distance_to_boundaries(longitude, _SIGN_BOUNDARIES) * 60.0, 4),
            "star": round(_distance_to_boundaries(longitude, _STAR_BOUNDARIES) * 60.0, 4),
            "sub": round(_distance_to_boundaries(longitude, _SUB_BOUNDARIES) * 60.0, 4),
        },
    }
    if speed is not None:
        record["speed"] = speed
        record["retrograde"] = speed < 0
    return record


def _kp_aspect(a: dict, b: dict) -> dict | None:
    """Reader VI pp.60-61 aspect/orb policy used for node agency."""
    if a["name"] not in KP_ORBS or b["name"] not in KP_ORBS:
        return None
    separation = abs(_normalise_signed(a["longitude"] - b["longitude"]))
    angle = min(KP_ASPECT_ANGLES, key=lambda value: abs(separation - value))
    error = abs(separation - angle)
    orb_limit = (KP_ORBS[a["name"]] + KP_ORBS[b["name"]]) / 2.0
    if error > orb_limit + 1e-9:
        return None
    return {
        "angle": angle,
        "separation_deg": round(separation, 6),
        "distance_from_exact_deg": round(error, 6),
        "orb_limit_deg": round(orb_limit, 6),
        "kind": "conjunction" if angle == 0 else "aspect",
    }


def _planet_positions(jd: float, ayanamsa: float) -> list[dict]:
    positions = []
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    for name, planet_id in PLANET_IDS.items():
        tropical = swe.calc_ut(jd, planet_id, flags)[0]
        positions.append(
            _position_record(name, tropical[0] - ayanamsa, speed=float(tropical[3]))
        )
    rahu = swe.calc_ut(jd, swe.MEAN_NODE, flags)[0]
    rahu_lon = (rahu[0] - ayanamsa) % 360.0
    positions.append(_position_record("Rahu", rahu_lon, speed=float(rahu[3])))
    positions.append(_position_record("Ketu", rahu_lon + 180.0, speed=float(rahu[3])))
    return positions


def _node_agents(records: dict[str, dict], node_name: str) -> list[dict]:
    """Return the source-stable portions of Reader VI's node-agency order.

    The printed order is: conjoined planet(s), constellation lord, aspecting
    planet(s), sign lord.  The Readers print no Rahu/Ketu orb, so the two
    contact-dependent slots remain unresolved.  Constellation- and sign-lord
    agency are nevertheless deterministic and must not be silently collapsed
    to sign lord alone.
    """
    node = records[node_name]
    candidates = (
        {
            "planet": node["star_lord"],
            "priority": 2,
            "agency": "constellation_lord",
        },
        {
            "planet": node["sign_lord"],
            "priority": 4,
            "agency": "sign_lord",
        },
    )
    result = []
    seen = set()
    for item in candidates:
        if item["planet"] == node_name:
            continue
        if item["planet"] not in seen:
            seen.add(item["planet"])
            result.append(item)
    return result


def _add_signification(
    target: dict,
    house: int,
    level: str,
    via: str,
    *,
    rank: int | None = None,
    represented_level: str | None = None,
) -> None:
    key = str(house)
    target.setdefault(key, [])
    if rank is None:
        rank = SIGNIFICATOR_LEVEL_RANK[level]
    item = {"level": level, "rank": rank, "via": via}
    if represented_level is not None:
        item["represented_level"] = represented_level
    if item not in target[key]:
        target[key].append(item)


def _build_significators(
    planet_records: list[dict], cusps: list[dict]
) -> tuple[dict[str, dict], dict[str, list[dict]]]:
    records = {record["name"]: record for record in planet_records}
    owners = {cusp["house"]: cusp["sign_lord"] for cusp in cusps}
    owned_houses = {
        planet: [house for house, owner in owners.items() if owner == planet]
        for planet in SEVEN_PLANETS
    }
    significations: dict[str, dict] = {planet: {} for planet in ALL_KP_PLANETS}

    for planet in ALL_KP_PLANETS:
        record = records[planet]
        star_lord = record["star_lord"]
        star_record = records[star_lord]
        _add_signification(
            significations[planet],
            star_record["house"],
            "A_star_of_occupant",
            f"star lord {star_lord} occupies house {star_record['house']}",
        )
        _add_signification(
            significations[planet],
            record["house"],
            "B_occupant",
            f"{planet} occupies house {record['house']}",
        )
        for house in owned_houses.get(star_lord, []):
            _add_signification(
                significations[planet],
                house,
                "C_star_of_owner",
                f"star lord {star_lord} owns house {house}",
            )
        for house in owned_houses.get(planet, []):
            _add_signification(
                significations[planet],
                house,
                "D_owner",
                f"{planet} owns house {house}",
            )

    base_significations = deepcopy(significations)
    for node in NODES:
        agents = _node_agents(records, node)
        records[node]["agent_planets"] = [item["planet"] for item in agents]
        records[node]["agent_details"] = agents
        records[node]["contact_agent_policy"] = (
            "conjunction/aspect slots fail closed because the Readers print "
            "no Rahu/Ketu orb; constellation- and sign-lord slots are operative"
        )
        for agent_record in agents:
            agent = agent_record["planet"]
            for house, evidence in base_significations[agent].items():
                for item in evidence:
                    _add_signification(
                        significations[node],
                        int(house),
                        "NODE_AGENT",
                        (
                            f"{node} represents {agent} through "
                            f"{agent_record['agency']} (priority "
                            f"{agent_record['priority']}): {item['via']}"
                        ),
                        rank=item["rank"],
                        represented_level=item["level"],
                    )

    # A planet deposited in a node's star must receive the results represented
    # by that node. Reader VI explicitly judges Sun in Rahu's star through the
    # planet represented by Rahu. The previous implementation stopped at the
    # node's occupied house and silently dropped the represented houses.
    for planet in ALL_KP_PLANETS:
        star_lord = records[planet]["star_lord"]
        if star_lord not in NODES:
            continue
        represented = [
            (house, dict(item))
            for house, evidence in list(significations[star_lord].items())
            for item in list(evidence)
            if item["level"] == "NODE_AGENT"
        ]
        for house, item in represented:
            _add_signification(
                significations[planet],
                int(house),
                "A_star_of_node_agent",
                (
                    f"star lord {star_lord} acts through its agent: "
                    f"{item['via']}"
                ),
                rank=1,
                represented_level=item.get("represented_level"),
            )

    by_house: dict[str, list[dict]] = {str(house): [] for house in range(1, 13)}
    for planet, houses in significations.items():
        for house, evidence in houses.items():
            best = min(item["rank"] for item in evidence)
            by_house[house].append(
                {
                    "planet": planet,
                    "best_rank": best,
                    "evidence": evidence,
                }
            )
    for items in by_house.values():
        items.sort(key=lambda item: (item["best_rank"], item["planet"]))
    return significations, by_house


def _ruling_planets(
    dt_local: datetime,
    jd: float,
    latitude: float,
    longitude: float,
    timezone: str,
    ayanamsa: float,
    records: dict[str, dict],
) -> dict:
    tropical_cusps, tropical_ascmc = swe.houses(jd, latitude, longitude, b"P")
    del tropical_cusps
    judgment_asc = (tropical_ascmc[0] - ayanamsa) % 360.0
    moon = records["Moon"]
    civil_midnight_jd = local_datetime_to_jd(
        dt_local.replace(hour=0, minute=0, second=0, microsecond=0),
        timezone,
    )
    sunrise_result, sunrise_times = swe.rise_trans(
        civil_midnight_jd,
        swe.SUN,
        swe.CALC_RISE,
        (longitude, latitude, 0.0),
        0.0,
        0.0,
        swe.FLG_SWIEPH,
    )
    if sunrise_result != 0:
        raise ValueError(
            "KP day lord requires a local sunrise, but no sunrise was found "
            "for the judgment date and location"
        )
    sunrise_jd = sunrise_times[0]
    before_sunrise = jd < sunrise_jd
    effective_weekday = (dt_local.weekday() - int(before_sunrise)) % 7

    ordered = [
        {"planet": _star_lord(judgment_asc), "role": "Asc_star_lord"},
        {"planet": _sign_lord(judgment_asc), "role": "Asc_sign_lord"},
        {"planet": moon["star_lord"], "role": "Moon_star_lord"},
        {"planet": moon["sign_lord"], "role": "Moon_sign_lord"},
        {"planet": WEEKDAY_LORDS[effective_weekday], "role": "day_lord"},
    ]
    base_planets = {item["planet"] for item in ordered}
    for node in NODES:
        represented = [
            planet
            for planet in records[node].get("agent_planets", [])
            if planet in base_planets
        ]
        if represented:
            ordered.append(
                {
                    "planet": node,
                    "role": f"node_agent_of_{'_'.join(represented)}",
                }
            )

    deduplicated = []
    seen = set()
    for item in ordered:
        if item["planet"] not in seen:
            seen.add(item["planet"])
            deduplicated.append(item)

    accepted = []
    rejected = []
    for item in deduplicated:
        planet_record = records[item["planet"]]
        star_lord = planet_record["star_lord"]
        if (
            star_lord in RETROGRADE_FILTER_PLANETS
            and records[star_lord].get("retrograde", False)
        ):
            rejected.append(
                {
                    **item,
                    "reason": f"deposited in retrograde star lord {star_lord}",
                }
            )
        else:
            accepted.append(item)
    return {
        "judgment_ascendant": _position_record("Judgment Asc", judgment_asc),
        "ordered": deduplicated,
        "accepted": accepted,
        "rejected": rejected,
        "day_rule": {
            "basis": "local sunrise to next local sunrise",
            "civil_date_sunrise_jd_ut": sunrise_jd,
            "judgment_before_sunrise": before_sunrise,
            "effective_weekday": WEEKDAY_NAMES[effective_weekday],
            "day_lord": WEEKDAY_LORDS[effective_weekday],
        },
        "retrograde_filter_scope": sorted(RETROGRADE_FILTER_PLANETS),
        "node_retrograde_policy": (
            "Rahu/Ketu are not rejected as retrograde star lords"
        ),
        "node_ruling_agent_scope": (
            "constellation/sign-lord agency active; conjunction/aspect slots "
            "fail closed because no node orb is printed"
        ),
        "source": "KSK Reader VI, Ruling Planets",
    }


def _evaluate_topic(
    topic: str,
    cusps: list[dict],
    planet_records: list[dict],
    significations: dict[str, dict],
) -> dict:
    rule = TOPIC_RULES[topic]
    cusp = cusps[rule["judgment_cusp"] - 1]
    records = {record["name"]: record for record in planet_records}
    cusp_sub_lord = cusp["sub_lord"]
    cusp_sub_lord_record = records[cusp_sub_lord]

    # Reader VI's rule is not "let every A/B/C/D house of the cusp sub-lord
    # vote." It asks whether the cusp sub-lord is deposited in the
    # constellation of a planet which signifies the topic houses. Therefore
    # the operative source is that constellation lord's significator chain.
    source_significator = cusp_sub_lord_record["star_lord"]
    source_significations = significations[source_significator]
    houses = {int(house) for house in source_significations}
    positive = sorted(houses.intersection(rule["positive_houses"]))
    negative = sorted(houses.intersection(rule["negative_houses"]))

    def condition_met(required_houses: tuple[int, ...], match: str) -> bool:
        required = set(required_houses)
        if match == "all":
            return required.issubset(houses)
        if match == "any":
            return bool(required.intersection(houses))
        raise ValueError(f"Unsupported topic match mode: {match}")

    positive_condition_met = condition_met(
        rule["positive_houses"],
        rule["positive_match"],
    )
    negative_condition_met = condition_met(
        rule["negative_houses"],
        rule["negative_match"],
    )
    if positive_condition_met and not negative_condition_met:
        directional_status = "positive_only"
    elif negative_condition_met and not positive_condition_met:
        directional_status = "negative_only"
    elif positive_condition_met and negative_condition_met:
        directional_status = "mixed"
    else:
        directional_status = "unsupported"

    position_sub_lord = cusp_sub_lord_record["sub_lord"]
    retrograde_checks = []
    blocked_by = []
    for role, planet in (
        ("cusp_sub_lord", cusp_sub_lord),
        ("constellation_lord", source_significator),
        ("position_sub_lord", position_sub_lord),
    ):
        record = records[planet]
        temporary_retrograde_applies = planet in RETROGRADE_FILTER_PLANETS
        is_blocking = temporary_retrograde_applies and record.get(
            "retrograde", False
        )
        retrograde_checks.append(
            {
                "role": role,
                "planet": planet,
                "temporary_retrograde_applies": temporary_retrograde_applies,
                "retrograde": bool(record.get("retrograde", False)),
                "blocking": is_blocking,
            }
        )
        if is_blocking and planet not in blocked_by:
            blocked_by.append(planet)

    # A node in any operative star/agent link can represent
    # conjoined/aspecting planets as well as its sign lord. Until that contact
    # policy is source-locked, a directional result traversing such a node is
    # incomplete rather than a safe promise/denial.
    node_agency_incomplete = (
        source_significator in NODES
        or records[source_significator]["star_lord"] in NODES
        or any(
            item["level"] in {"NODE_AGENT", "A_star_of_node_agent"}
            for evidence in source_significations.values()
            for item in evidence
        )
    )
    if node_agency_incomplete:
        status = "incomplete_node_agency"
    elif directional_status == "positive_only":
        status = (
            "positive_indication_blocked"
            if blocked_by
            else "promised_candidate"
        )
    elif directional_status == "negative_only":
        status = (
            "negative_indication_blocked"
            if blocked_by
            else "denied_candidate"
        )
    elif directional_status == "mixed":
        status = "mixed_with_retrograde_block" if blocked_by else "mixed"
    else:
        status = "unsupported"

    relevant_evidence = {
        str(house): source_significations[str(house)]
        for house in sorted(set(positive + negative))
    }
    return {
        "topic": topic,
        "judgment_cusp": rule["judgment_cusp"],
        "cusp_sub_lord": cusp_sub_lord,
        "cusp_sub_lord_star_lord": source_significator,
        "star_lord_signifies": sorted(houses),
        "directional_evidence": relevant_evidence,
        "position_sub_lord": position_sub_lord,
        "position_sub_lord_house": records[position_sub_lord]["house"],
        "positive_hits": positive,
        "negative_hits": negative,
        "positive_condition": {
            "required_houses": list(rule["positive_houses"]),
            "match": rule["positive_match"],
            "met": positive_condition_met,
        },
        "negative_condition": {
            "required_houses": list(rule["negative_houses"]),
            "match": rule["negative_match"],
            "met": negative_condition_met,
        },
        "directional_status": directional_status,
        "retrograde_gate": {
            "checks": retrograde_checks,
            "blocked_by": blocked_by,
            "status": "blocked" if blocked_by else "clear",
        },
        "node_agency_incomplete": node_agency_incomplete,
        "status": status,
        "source_rule": rule["source"],
        "scope_note": (
            "Source-scoped mechanical candidate. Node contact agency is "
            "fail-closed and final KP judgment remains experimental."
        ),
    }


def _split_time_period(
    start: datetime,
    end: datetime,
    first_lord: str,
) -> list[dict]:
    total_seconds = (end - start).total_seconds()
    current = start
    result = []
    for index, lord in enumerate(_ordered_lords(first_lord)):
        child_end = (
            end
            if index == 8
            else current
            + timedelta(
                seconds=total_seconds * DASHA_YEARS[lord] / TOTAL_YEARS
            )
        )
        result.append({"lord": lord, "start": current, "end": child_end})
        current = child_end
    return result


def _current_horary_periods(dt_local: datetime, moon_longitude: float) -> dict:
    """Map the horary Moon's KP levels to dated period intervals."""
    path = _vimshottari_path(moon_longitude)
    mahadasha = path[0]
    mahadasha_days = DASHA_YEARS[mahadasha["lord"]] * VIMSHOTTARI_YEAR_DAYS
    elapsed_fraction = (
        moon_longitude % 360.0 - mahadasha["start_longitude"]
    ) / NAK_SPAN
    mahadasha_start = dt_local - timedelta(
        days=mahadasha_days * elapsed_fraction
    )
    records = []
    for item in path:
        start_fraction = (
            item["start_longitude"] - mahadasha["start_longitude"]
        ) / NAK_SPAN
        end_fraction = (
            item["end_longitude"] - mahadasha["start_longitude"]
        ) / NAK_SPAN
        records.append(
            {
                "level": item["level"],
                "lord": item["lord"],
                "start": mahadasha_start
                + timedelta(days=mahadasha_days * start_fraction),
                "end": mahadasha_start
                + timedelta(days=mahadasha_days * end_fraction),
            }
        )
    balance = records[0]["end"] - dt_local
    return {
        "moon_longitude": moon_longitude % 360.0,
        "moon_star": NAKSHATRAS[_star_index(moon_longitude)][0],
        "current": records,
        "mahadasha_balance_days": round(balance.total_seconds() / 86400.0, 6),
        "year_basis_days": VIMSHOTTARI_YEAR_DAYS,
        "source": "KSK Reader VI: horary Moon balance and conjoined periods",
    }


def _iter_shookshma_periods(
    current_periods: dict,
    *,
    horizon_years: float = 12.0,
):
    judgment_time = current_periods["current"][0]["start"]
    current_md = current_periods["current"][0]
    limit = current_md["end"] + timedelta(
        days=horizon_years * VIMSHOTTARI_YEAR_DAYS
    )
    md_lord = current_md["lord"]
    md_start = current_md["start"]
    md_end = current_md["end"]
    while md_start < limit:
        for bhukti in _split_time_period(md_start, md_end, md_lord):
            for antara in _split_time_period(
                bhukti["start"], bhukti["end"], bhukti["lord"]
            ):
                for shookshma in _split_time_period(
                    antara["start"], antara["end"], antara["lord"]
                ):
                    yield {
                        "mahadasha": md_lord,
                        "bhukti": bhukti["lord"],
                        "antara": antara["lord"],
                        "shookshma": shookshma["lord"],
                        "start": shookshma["start"],
                        "end": shookshma["end"],
                    }
        next_index = (DASHA_ORDER.index(md_lord) + 1) % 9
        md_lord = DASHA_ORDER[next_index]
        md_start = md_end
        md_end = md_start + timedelta(
            days=DASHA_YEARS[md_lord] * VIMSHOTTARI_YEAR_DAYS
        )


def _timing_event_houses(topic_result: dict) -> list[int]:
    if topic_result["directional_status"] == "positive_only":
        return list(TOPIC_RULES[topic_result["topic"]]["positive_houses"])
    if topic_result["directional_status"] == "negative_only":
        return list(TOPIC_RULES[topic_result["topic"]]["negative_houses"])
    return sorted(
        set(TOPIC_RULES[topic_result["topic"]]["positive_houses"])
        | set(TOPIC_RULES[topic_result["topic"]]["negative_houses"])
    )


def _transit_targets(ruling_planets: list[str]) -> list[dict]:
    accepted = set(ruling_planets)
    return [
        {
            "start_longitude": item["start_lon"],
            "end_longitude": item["end_lon"],
            "sign_lord": item["sign_lord"],
            "star_lord": item["star_lord"],
            "sub_lord": item["sub_lord"],
        }
        for item in NUMBER_TABLE
        if item["sign_lord"] in accepted
        and item["star_lord"] in accepted
        and item["sub_lord"] in accepted
    ]


def _longitude_in_targets(longitude: float, targets: list[dict]) -> bool:
    longitude %= 360.0
    return any(
        item["start_longitude"] - 1e-9
        <= longitude
        < item["end_longitude"] - 1e-9
        for item in targets
    )


def _transit_longitude(at: datetime, planet: str) -> float:
    utc = at.astimezone(datetime_timezone.utc)
    hour = (
        utc.hour
        + utc.minute / 60.0
        + utc.second / 3600.0
        + utc.microsecond / 3_600_000_000.0
    )
    jd = swe.julday(utc.year, utc.month, utc.day, hour, swe.GREG_CAL)
    ayanamsa = _ayanamsa_for_mode(jd, swe.SIDM_KRISHNAMURTI)
    tropical = swe.calc_ut(jd, PLANET_IDS[planet], swe.FLG_SWIEPH)[0][0]
    return (tropical - ayanamsa) % 360.0


def _first_target_transit(
    start: datetime,
    end: datetime,
    planet: str,
    targets: list[dict],
) -> dict | None:
    if not targets or end <= start:
        return None
    step = {
        "Moon": timedelta(hours=1),
        "Sun": timedelta(hours=6),
        "Jupiter": timedelta(days=1),
    }[planet]
    left = start
    left_inside = _longitude_in_targets(_transit_longitude(left, planet), targets)
    if left_inside:
        return {
            "planet": planet,
            "entry": left,
            "already_inside_at_window_start": True,
        }
    while left < end:
        right = min(end, left + step)
        right_inside = _longitude_in_targets(
            _transit_longitude(right, planet), targets
        )
        if not left_inside and right_inside:
            low = left
            high = right
            for _ in range(24):
                if (high - low).total_seconds() <= 60:
                    break
                middle = low + (high - low) / 2
                if _longitude_in_targets(
                    _transit_longitude(middle, planet), targets
                ):
                    high = middle
                else:
                    low = middle
            return {
                "planet": planet,
                "entry": high.replace(second=0, microsecond=0),
                "already_inside_at_window_start": False,
            }
        left = right
        left_inside = right_inside
    return None


def _compute_kp_timing(
    dt_local: datetime,
    records: dict[str, dict],
    topic_result: dict,
    significators_by_house: dict[str, list[dict]],
    ruling_planets: dict,
) -> dict:
    moon_periods = _current_horary_periods(
        dt_local, records["Moon"]["longitude"]
    )
    event_houses = _timing_event_houses(topic_result)
    event_significators = sorted(
        {
            item["planet"]
            for house in event_houses
            for item in significators_by_house[str(house)]
        }
    )
    accepted_ruling_planets = [
        item["planet"] for item in ruling_planets["accepted"]
    ]
    period_lords = [
        planet
        for planet in accepted_ruling_planets
        if planet in event_significators
    ]
    base = {
        "source": (
            "KSK Reader VI: horary Moon balance; event significators ∩ "
            "Ruling Planets; Moon/Sun/Jupiter transit scale"
        ),
        "moon_periods": moon_periods,
        "event_houses": event_houses,
        "event_significators": event_significators,
        "accepted_ruling_planets": accepted_ruling_planets,
        "period_lords": period_lords,
        "period_candidates": [],
        "transit": {
            "status": "not_searched",
            "targets": [],
        },
        "scope_note": (
            "Independent KP horary timing only; never imported into the "
            "Parashari standard layer."
        ),
    }
    if topic_result["node_agency_incomplete"]:
        return {
            **base,
            "status": "blocked_node_agency",
            "reason": (
                "The operative promise path crosses node agency whose "
                "conjunction/aspect orb remains unspecified in the Readers."
            ),
        }
    if topic_result["directional_status"] != "positive_only":
        return {
            **base,
            "status": "not_authorized_without_positive_promise",
            "reason": (
                "A materialization date is not authorized unless the "
                "topic-specific promise is positive-only."
            ),
        }
    if topic_result["retrograde_gate"]["blocked_by"]:
        return {
            **base,
            "status": "blocked_temporary_retrograde",
            "reason": (
                "The direction remains positive, but Reader VI does not "
                "authorize materialization while an operative lord is "
                "temporarily retrograde."
            ),
        }
    if not period_lords:
        return {
            **base,
            "status": "no_rp_significator_intersection",
            "reason": "No accepted Ruling Planet is an event significator.",
        }

    candidates = []
    for period in _iter_shookshma_periods(moon_periods):
        if period["end"] <= dt_local:
            continue
        if all(
            period[level] in period_lords
            for level in ("mahadasha", "bhukti", "antara", "shookshma")
        ):
            candidate = dict(period)
            candidate["start"] = max(period["start"], dt_local)
            candidates.append(candidate)
            if len(candidates) == 5:
                break
    base["period_candidates"] = candidates
    if not candidates:
        return {
            **base,
            "status": "no_four_level_period_within_horizon",
            "reason": (
                "No Dasha/Bhukti/Antara/Shookshma interval wholly governed "
                "by the RP-significator intersection was found in 12 years."
            ),
        }

    targets = _transit_targets(accepted_ruling_planets)
    serialised_targets = [
        {
            **item,
            "start_longitude": round(item["start_longitude"], 8),
            "end_longitude": round(item["end_longitude"], 8),
        }
        for item in targets
    ]
    base["transit"]["targets"] = serialised_targets
    transit_result = None
    selected_scale = None
    for candidate in candidates:
        delay_days = (candidate["start"] - dt_local).total_seconds() / 86400.0
        if delay_days <= 31.0:
            selected_scale = "Moon"
        elif delay_days < VIMSHOTTARI_YEAR_DAYS:
            selected_scale = "Sun"
        else:
            selected_scale = "Jupiter"
        transit_result = _first_target_transit(
            candidate["start"],
            candidate["end"],
            selected_scale,
            targets,
        )
        if transit_result:
            transit_result["period"] = candidate
            break
    if transit_result:
        base["transit"] = {
            "status": "candidate",
            "scale_planet": selected_scale,
            "entry": transit_result["entry"],
            "already_inside_at_window_start": transit_result[
                "already_inside_at_window_start"
            ],
            "period": transit_result["period"],
            "targets": serialised_targets,
        }
        return {
            **base,
            "status": "candidate",
            "warning": (
                "Source-scoped KP candidate; precision remains bounded by "
                "the published-example suite and the selected transit scale."
            ),
        }
    base["transit"]["status"] = "no_entry_in_candidate_periods"
    base["transit"]["scale_planet"] = selected_scale
    return {
        **base,
        "status": "period_candidate_without_transit_entry",
        "reason": (
            "Four-level period candidates exist, but Moon/Sun/Jupiter did "
            "not enter an RP-governed sign/star/sub segment inside them."
        ),
    }


def _json_safe(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_safe(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_safe(child) for child in value]
    return value


def compute(
    dt_local: datetime,
    latitude: float,
    longitude: float,
    timezone: str,
    number: int,
    topic: str,
) -> dict:
    if not math.isfinite(latitude) or not -90.0 <= latitude <= 90.0:
        raise ValueError("latitude must be a finite value between -90 and 90")
    if not math.isfinite(longitude) or not -180.0 <= longitude <= 180.0:
        raise ValueError("longitude must be a finite value between -180 and 180")
    if not 1 <= number <= 249:
        raise ValueError("KP horary number must be between 1 and 249")
    if topic not in TOPIC_RULES:
        raise ValueError(f"Unsupported KP topic: {topic}")

    jd = local_datetime_to_jd(dt_local, timezone)
    kp_ayanamsa = _ayanamsa_for_mode(jd, swe.SIDM_KRISHNAMURTI)
    true_citra = _ayanamsa_for_mode(jd, swe.SIDM_TRUE_CITRA)
    number_record = dict(NUMBER_TABLE[number - 1])
    nirayana_asc = number_record["start_lon"]
    tropical_asc = (nirayana_asc + kp_ayanamsa) % 360.0
    obliquity = swe.calc_ut(jd, swe.ECL_NUT)[0][0]
    # KP Readers mandate Placidus house system; Placidus is undefined within the polar circle (|lat| >= 90 - obliquity).
    # Cannot substitute house systems without departing from KP; fail-closed.
    if abs(latitude) >= 90.0 - obliquity:
        raise ValueError(
            f"Judgment latitude {latitude:.4f} deg is within polar circle (|lat| >= {90.0 - obliquity:.2f} deg). "
            "Placidus house system used by KP is undefined here; KP fails closed; use standard layer instead."
        )
    armc = _solve_armc_for_asc(tropical_asc, latitude, obliquity)
    tropical_cusps = swe.houses_armc(armc, latitude, obliquity, b"P")[0]
    cusp_longitudes = [
        (tropical_cusps[house] - kp_ayanamsa) % 360.0 for house in range(1, 13)
    ]
    # Cusp 1 is defined by the user's number, not by the numerical residue of
    # the ARMC solver.  Placidus cusp 7 is its exact opposition.
    cusp_longitudes[0] = nirayana_asc % 360.0
    cusp_longitudes[6] = (nirayana_asc + 180.0) % 360.0

    cusp_records = []
    for house, cusp_longitude in enumerate(cusp_longitudes, start=1):
        record = _position_record(f"Cusp {house}", cusp_longitude)
        record["house"] = house
        if house == 1:
            record["number_boundary_policy"] = (
                "The 1–249 number selects the following segment at its exact start; "
                "this is deterministic, not input sensitivity."
            )
        elif house == 7:
            record["number_boundary_policy"] = (
                "Placidus cusp 7 is exactly opposite the number-defined cusp 1; "
                "an exact anti-Asc sign boundary is deterministic, not time sensitivity."
            )
        cusp_records.append(record)

    planet_records = _planet_positions(jd, kp_ayanamsa)
    for record in planet_records:
        record["house"] = _house_of(record["longitude"], cusp_longitudes)

    significations, significators_by_house = _build_significators(
        planet_records, cusp_records
    )
    records_by_name = {record["name"]: record for record in planet_records}
    ruling_planets = _ruling_planets(
        dt_local,
        jd,
        latitude,
        longitude,
        timezone,
        kp_ayanamsa,
        records_by_name,
    )
    topic_result = _evaluate_topic(
        topic,
        cusp_records,
        planet_records,
        significations,
    )
    timing = _json_safe(
        _compute_kp_timing(
            dt_local,
            records_by_name,
            topic_result,
            significators_by_house,
            ruling_planets,
        )
    )

    sensitive_points = []
    for record in cusp_records + planet_records:
        if (
            record["name"] in {"Cusp 1", "Cusp 7"}
            and "number_boundary_policy" in record
        ):
            continue
        if min(record["boundary_distance_arcmin"].values()) <= 5.0:
            sensitive_points.append(
                {
                    "name": record["name"],
                    "boundary_distance_arcmin": record["boundary_distance_arcmin"],
                }
            )

    return {
        "mode": "KP classical horary 1–249",
        "number": number,
        "outcome_scope": {
            "id": TOPIC_RULES[topic]["outcome_scope"],
            **validate_outcome_scope(topic, TOPIC_RULES[topic]["outcome_scope"]),
        },
        "number_segment": number_record,
        "judgment_time": dt_local.isoformat(),
        "judgment_timezone": timezone,
        "judgment_location": {"latitude": latitude, "longitude": longitude},
        "ayanamsa": {
            "mode": "Swiss Ephemeris SIDM_KRISHNAMURTI",
            "value_deg": kp_ayanamsa,
            "true_citra_difference_arcmin": round(
                _circular_distance(kp_ayanamsa, true_citra) * 60.0, 6
            ),
        },
        "house_system": "Placidus; number-derived nirayana Ascendant",
        "node_mode": (
            "Mean Node; constellation- and sign-lord agency active in Reader "
            "VI order; conjunction/aspect slots fail closed because no node "
            "orb is printed"
        ),
        "horary_ascendant": _position_record("Horary Asc", nirayana_asc),
        "house_cusps": cusp_records,
        "planets": planet_records,
        "significations_by_planet": significations,
        "significators_by_house": significators_by_house,
        "topic_result": topic_result,
        "ruling_planets": ruling_planets,
        "sensitivity": {
            "threshold_arcmin": 5.0,
            "sensitive_points": sensitive_points,
            "all_points_include_raw_boundary_distances": True,
        },
        "timing": timing,
        "production_status": (
            "experimental_node_contact_source_gap"
            if topic_result["node_agency_incomplete"]
            else "experimental_validated_candidate_pending_full_published_example_suite"
        ),
    }


def format_kp_section(data: dict) -> str:
    topic = data["topic_result"]
    timing = data["timing"]
    outcome_scope = data["outcome_scope"]
    question_lines = [f"- Question: {data['question']}"] if data.get("question") else []
    lines = [
        "# KP Horary Independent Stack (1–249)",
        "",
        "> This document is independent of the Parashari standard layer and does not vote with standard verdicts.",
        f"> Current Status: {data['production_status']}.",
        "",
        "## Input and Technical Parameters",
        "",
        *question_lines,
        (
            f"- Observable Outcome Scope: **{outcome_scope['definition']}** "
            f"({outcome_scope['id']})"
        ),
        (
            "- Excluded from this question type: "
            + "; ".join(outcome_scope.get("excluded_outcomes", ()))
        ),
        f"- Judgment Instant: {data['judgment_time']} ({data['judgment_timezone']})",
        (
            f"- Judgment Location: {data['judgment_location']['latitude']}, "
            f"{data['judgment_location']['longitude']}"
        ),
        f"- Horary Number: **{data['number']}**",
        (
            f"- Number Ascendant: {data['number_segment']['sign']} "
            f"{_format_degree(data['number_segment']['start_lon'])}; "
            f"{data['number_segment']['star_lord']} star / "
            f"{data['number_segment']['sub_lord']} sub"
        ),
        f"- Ayanamsa: {data['ayanamsa']['mode']}",
        f"- House System: {data['house_system']}",
        "",
        "## Topic-Specific Promise Verification",
        "",
        f"- Topic: **{topic['topic']}**",
        f"- Judgment Cusp: {topic['judgment_cusp']}",
        f"- Cusp Sub-Lord: {topic['cusp_sub_lord']}",
        (
            f"- Cusp Sub-Lord Star Lord: "
            f"{topic['cusp_sub_lord_star_lord']}"
        ),
        f"- Significator Houses: {topic['star_lord_signifies']}",
        (
            f"- Position Sub-Lord: {topic['position_sub_lord']} "
            f"located in House {topic['position_sub_lord_house']}"
        ),
        f"- Positive House Hits: {topic['positive_hits']}",
        f"- Negative House Hits: {topic['negative_hits']}",
        (
            "- Positive Condition: "
            f"{topic['positive_condition']['match']} "
            f"{topic['positive_condition']['required_houses']}; "
            f"met={topic['positive_condition']['met']}"
        ),
        (
            "- Negative Condition: "
            f"{topic['negative_condition']['match']} "
            f"{topic['negative_condition']['required_houses']}; "
            f"met={topic['negative_condition']['met']}"
        ),
        f"- Directional Status: {topic['directional_status']}",
        (
            f"- Retrograde Materialization Gate: "
            f"{topic['retrograde_gate']['status']} "
            f"({topic['retrograde_gate']['retrograde_planets']})"
        ),
        (
            "- Node Agency Completeness: "
            + (
                "Incomplete; conjunction/aspect agency not enabled, fails closed"
                if topic["node_agency_incomplete"]
                else "Operative promise path does not traverse node agency"
            )
        ),
        f"- Mechanical Status: **{topic['status']}**",
        f"- Source Rule: {topic['source_rule']}",
        "",
        "## Cusps Table (1–12)",
        "",
        "| House | Longitude | Sign | Star Lord | Sub Lord | Nearest Sub Boundary |",
        "|---:|---|---|---|---|---|",
    ]
    for cusp in data["cusps"]:
        nearest = cusp["sub_boundary_distance"]
        nearest_str = f"{nearest['minutes_to_boundary']:.2f}' to {nearest['direction']}"
        lines.append(
            f"| {cusp['house']} | {_format_degree(cusp['longitude'])} | "
            f"{cusp['sign']} | {cusp['star_lord']} | {cusp['sub_lord']} | {nearest_str} |"
        )
    lines.extend(
        [
            "",
            "## Ruling Planets Audit",
            "",
            f"- Day Lord (from sunrise): "
            f"{data['ruling_planets']['day_rule']['day_lord']} (day shifts at local sunrise)",
            (
                "- Accepted: "
                + " / ".join(data["ruling_planets"]["accepted_planets"])
                or "None"
            ),
            (
                "- Filtered out by retrograde star lord: "
                + " / ".join(data["ruling_planets"]["filtered_out_by_star_lord_retrograde"])
                or "None"
            ),
            "- Node Retrograde Policy: Natural retrograde motion of Rahu/Ketu does not trigger star-lord elimination.",
            "- Node Agent: Star lord and sign lord enabled per Reader VI sequence; conjunction/aspect slots fail closed due to undefined classical orb.",
            "",
            "## Boundaries and Timing",
            "",
            (
                f"- Difference between True Chitra and KP ayanamsa: "
                f"{data['ayanamsa']['difference_arcmin']:.3f}'"
            ),
            (
                "- Sensitive points within 5': "
                + " / ".join(item["name"] for item in data["sensitivity"]["sensitive_points"])
                or "None"
            ),
            f"- Timing Status: **{timing['status']}**",
            (
                "- Horary Moon Current Chain: "
                + " / ".join(
                    f"{item['level']}={item['lord']}"
                    for item in timing["moon_periods"]["current"]
                )
            ),
            (
                "- Significator and Ruling Planets Intersection: "
                + ("/".join(timing["period_lords"]) or "None")
            ),
            (
                "- Four-level Period Candidates: "
                + (
                    "; ".join(
                        (
                            f"{item['mahadasha']}-{item['bhukti']}-"
                            f"{item['antara']}-{item['shookshma']} "
                            f"{item['start']} -> {item['end']}"
                        )
                        for item in timing["period_candidates"][:3]
                    )
                    or "None"
                )
            ),
            (
                "- Transit Candidates: "
                + (
                    f"{timing['transit']['scale_planet']} "
                    f"into {timing['transit']['sign']} "
                    f"({timing['transit']['entry']}); "
                    f"RP={timing['transit']['sign_lord_is_rp']}"
                    if timing["transit"]["status"] == "candidate"
                    else timing["transit"]["status"]
                )
            ),
            (
                "- Timing Authority Boundary: Independently utilizes horary Moon balance, "
                "RP intersection, and Moon/Sun/Jupiter stratification; does not borrow standard Moon "
                "ingress or natal Dasha."
            ),
        ]
    )
    return "\n".join(lines) + "\n\n\n"def format_kp_judgment(data: dict) -> str:
    """Render a human-readable judgment without merging KP into Parashari."""
    topic = data["topic_result"]
    timing = data["timing"]
    outcome_scope = data["outcome_scope"]
    topic_language = {
        "love-materialization": {
            "name": "Whether romantic interaction materializes into an explicit relationship",
            "positive_requirement": (
                "Both explicit partnership and desired outcome conditions must be met simultaneously"
            ),
            "negative_requirement": (
                "Either discord/friction or withdrawal/separation constitutes a negative verdict"
            ),
            "positive": {
                7: "Conditions support establishing explicit partnership",
                11: "Conditions support achieving the desired relationship outcome",
            },
            "negative": {
                6: "Disagreements, friction, or disparity obstruct materialization",
                12: "Estrangement, withdrawal, or depletion obstruct materialization",
            },
        },
        "business-partnership-continuity": {
            "name": "Whether business partnership can continue",
            "positive_requirement": (
                "Continued commitment or partnership returns constitutes a positive indication"
            ),
            "negative_requirement": (
                "Liability conflicts or withdrawal/termination constitutes a negative indication"
            ),
            "positive": {
                5: "Conditions support continued investment and maintenance of partnership",
                11: "Conditions support realizing partnership objectives and returns",
            },
            "negative": {
                6: "Disputes, competition, or liability conflicts obstruct continuation",
                12: "Withdrawal, attrition, or termination conditions obstruct continuation",
            },
        },
    }[topic["topic"]]
    status_labels = {
        "promised_candidate": "Positive Materialization Candidate",
        "denied_candidate": "Negative / Denied Candidate",
        "mixed": "Mixed",
        "unsupported": "Query Type Not Promising Under Rules",
        "positive_indication_blocked": "Positive candidate temporarily blocked by retrograde gate",
        "negative_indication_blocked": "Negative candidate temporarily blocked by retrograde gate",
        "mixed_with_retrograde_block": "Mixed and blocked by retrograde gate",
        "incomplete_node_agency": "Node agency chain incomplete; fails closed",
    }
    directional_labels = {
        "positive_only": "Full positive condition met, explicit negative condition not met",
        "negative_only": "Full positive condition not met, explicit negative condition met",
        "mixed": "Both positive and negative full conditions met",
        "unsupported": "Neither positive nor negative full conditions met",
    }
    positive = " / ".join(map(str, topic["positive_hits"])) or "None"
    negative = " / ".join(map(str, topic["negative_hits"])) or "None"
    positive_meanings = "; ".join(
        topic_language["positive"][house] for house in topic["positive_hits"]
    ) or "No conditions supporting outcome materialization were hit"
    negative_meanings = "; ".join(
        topic_language["negative"][house] for house in topic["negative_hits"]
    ) or "No conditions obstructing outcome materialization were hit"
    positive_condition_met = topic["positive_condition"]["met"]
    negative_condition_met = topic["negative_condition"]["met"]
    positive_condition_text = (
        "Fully Met" if positive_condition_met else "Not Fully Met"
    )
    negative_condition_text = (
        "Met" if negative_condition_met else "Not Met"
    )
    sensitive = " / ".join(
        item["name"] for item in data["sensitivity"]["sensitive_points"]
    ) or "None"
    accepted_ruling_planets = (
        " / ".join(timing["accepted_ruling_planets"]) or "None"
    )
    period_candidates = "; ".join(
        (
            f"{item['mahadasha']}-{item['bhukti']}-"
            f"{item['antara']}-{item['shookshma']} "
            f"{item['start']} -> {item['end']}"
        )
        for item in timing["period_candidates"][:3]
    ) or "None"
    transit = timing["transit"]
    transit_reading = (
        f"{transit['scale_planet']} entered candidate window at {transit['entry']}"
        if transit["status"] == "candidate"
        else transit["status"]
    )
    timing_boundary = (
        "Positive promise, four-level period, and transit entry all satisfied simultaneously; "
        "operates strictly as a KP experimental stack candidate, not a standard-layer date."
        if timing["status"] == "candidate"
        else (
            "KP event timing conditions are not fully authorized for this chart; "
            "do not improvise dates or borrow from other stacks."
        )
    )
    plain_status = {
        "promised_candidate": (
            "Currently trending towards materialization. Full positive conditions met, explicit negative conditions unmet; "
            "this is a directional assessment, not a 100% guarantee."
        ),
        "denied_candidate": (
            "Currently trending against materialization. Full positive conditions unmet, and at least one explicit "
            "negative condition has been satisfied."
        ),
        "mixed": (
            "Rules cannot currently resolve: both full positive and negative conditions are met, "
            "and classical texts provide no priority rule for this question type."
        ),
        "unsupported": (
            "Rules cannot currently determine: neither positive nor negative full conditions are met."
        ),
        "positive_indication_blocked": (
            "Direction originally favored materialization, but key planets remain under temporary retrograde block; "
            "positive conditions cannot yet be treated as capable of landing."
        ),
        "negative_indication_blocked": (
            "Direction originally disfavored materialization, but negative outcome is also temporarily blocked by retrogradation; "
            "this does not turn it positive, but indicates the negative event has not landed."
        ),
        "mixed_with_retrograde_block": (
            "Both positive and negative conditions met, with key planets additionally blocked by retrogradation; "
            "no priority rule available."
        ),
        "incomplete_node_agency": (
            "Critical judgment chain traverses Rahu/Ketu, while classical texts omit required node orbs. "
            "To avoid inventing rules, evaluation halts here without declaring yes or no."
        ),
    }[topic["status"]]
    plain_timing = {
        "candidate": (
            "KP identifies a positive outcome, four-level period, and transit entry; "
            "the timing below represents a candidate window, not a guarantee."
        ),
        "blocked_node_agency": (
            "Critical chain traverses unclosed Rahu/Ketu agency rules; timing output disabled."
        ),
        "blocked_temporary_retrograde": (
            "Key planet retrograde block has not lifted; timing output disabled."
        ),
        "not_authorized_without_positive_promise": (
            "Outcome is not purely positive; KP rules do not permit calculating timing."
        ),
        "no_rp_significator_intersection": (
            "No intersection between ruling planets and significators; no ruling period lord available."
        ),
        "no_four_level_period_within_horizon": (
            "No four-level period matching all ruling lords was found within search horizon."
        ),
        "period_candidate_without_transit_entry": (
            "Period candidate found, but no matching transit entry; cannot pinpoint date."
        ),
    }[timing["status"]]
    reason = {
        "promised_candidate": (
            f"{topic_language['positive_requirement']}: this chart {positive_condition_text}; "
            f"{topic_language['negative_requirement']}: this chart {negative_condition_text}."
        ),
        "denied_candidate": (
            f"{topic_language['positive_requirement']}: this chart {positive_condition_text}; "
            f"{topic_language['negative_requirement']}: this chart {negative_condition_text}."
        ),
        "mixed": (
            "Both positive and negative full conditions are met; classical sources specify no priority."
        ),
        "unsupported": (
            "Neither positive nor negative full conditions are met; no definitive direction can be forced."
        ),
        "positive_indication_blocked": (
            "Positive conditions met, negative conditions unmet, but gate is temporarily blocked by retrogradation."
        ),
        "negative_indication_blocked": (
            "Positive conditions unmet, negative conditions met, but negative gate is also temporarily blocked by retrogradation."
        ),
        "mixed_with_retrograde_block": (
            "Both conditions met, and materialization gate remains blocked by retrogradation."
        ),
        "incomplete_node_agency": (
            "Critical chain traverses node agency without sufficient classical parameters; halts to avoid rule invention."
        ),
    }[topic["status"]]
    reality = {
        "promised_candidate": positive_meanings,
        "denied_candidate": negative_meanings,
        "mixed": (
            "Neither side can be declared primary; the rules lack an authorized resolution clause here."
        ),
        "unsupported": (
            "Evidence is insufficient to yield a directional verdict; partial hits do not satisfy full conditions."
        ),
        "positive_indication_blocked": (
            f"{positive_meanings}, but cannot yet be regarded as capable of landing."
        ),
        "negative_indication_blocked": (
            f"{negative_meanings}, but negative outcome has not yet landed."
        ),
        "mixed_with_retrograde_block": (
            "No priority rule exists, and materialization gates remain blocked."
        ),
        "incomplete_node_agency": (
            "No authority to declare outcome; remains failed-closed pending primary sources."
        ),
    }[topic["status"]]
    lines = [
        f"# KP Independent Reading Sheet (Research Validation): {data.get('question', 'No Question Attached')}",
        "",
        "## 1. Summary",
        "",
        f"**Current Trend**: {plain_status}",
        "",
        f"**Key Rationale**: {reason}",
        "",
        f"**Practical Meaning**: {reality}.",
        "",
        f"**Timing Availability**: {plain_timing}",
        "",
        (
            f"**Scope**: This chart addresses only '{outcome_scope['definition']}', excluding: "
            + "; ".join(outcome_scope.get("excluded_outcomes", ()))
            + "."
        ),
        "",
        (
            "**Usage Guidelines**: Answers strictly according to KP rules; does not vote with standard layer or Tajika."
        ),
        "",
        "## 2. Input Configuration",
        "",
        f"- Judgment Instant: {data['judgment_time']} ({data['judgment_timezone']})",
        (
            f"- Judgment Location: {data['judgment_location']['latitude']}, "
            f"{data['judgment_location']['longitude']}"
        ),
        f"- Horary Number: {data['number']}",
        f"- Question Type: {topic_language['name']}",
        f"- Confirmed Observable Outcome: {outcome_scope['definition']}",
        "",
        "## 3. Rationale Breakdown",
        "",
        (
            f"- Positive Conditions: {positive_condition_text}. {positive_meanings}."
        ),
        (
            f"- Negative Conditions: {negative_condition_text}. {negative_meanings}."
        ),
        f"- Adjudication Rationale: {reason}",
        (
            "- Evaluates concrete materialization, not private thoughts or fleeting moods."
        ),
        "",
        "## 4. Timing Evaluation",
        "",
        f"- Timing Conclusion: {plain_timing}",
        (
            "- Candidate timing is shown only when the outcome is purely positive and retrogradation, node agency, period, and transit criteria all pass."
        ),
        "",
        "## 5. Technical Appendix",
        "",
        f"- Original Topic: {topic['topic']}",
        f"- Outcome Scope ID: {outcome_scope['id']}",
        f"- Judgment Cusp: {topic['judgment_cusp']}",
        f"- Cusp Sub-Lord: {topic['cusp_sub_lord']}",
        f"- Star Lord: {topic['cusp_sub_lord_star_lord']}",
        f"- Supporting House Hits: {positive}",
        f"- Obstructing House Hits: {negative}",
        (
            "- Positive Condition: "
            f"{topic['positive_condition']['match']} "
            f"{topic['positive_condition']['required_houses']}; "
            f"met={topic['positive_condition']['met']}"
        ),
        (
            "- Negative Condition: "
            f"{topic['negative_condition']['match']} "
            f"{topic['negative_condition']['required_houses']}; "
            f"met={topic['negative_condition']['met']}"
        ),
        f"- Mechanical Status: {topic['status']}",
        f"- Directional Status: {topic['directional_status']}",
        (
            f"- Status Translation: {status_labels.get(topic['status'], topic['status'])}; "
            f"{directional_labels.get(topic['directional_status'], topic['directional_status'])}"
        ),
        f"- Star-lord Significator Houses: {topic['star_lord_signifies']}",
        f"- Source Rule: {topic['source_rule']}",
        f"- Temporary Retrograde Gate: {topic['retrograde_gate']['status']}",
        (
            "- Rahu/Ketu Rule Completeness: "
            + (
                "Critical path traverses unclosed node contact agency; inference halted"
                if topic["node_agency_incomplete"]
                else "Critical path does not traverse unclosed node agency"
            )
        ),
        f"- Timing Mechanical Status: {timing['status']}",
        (
            "- Four-level Period Chain: "
            + " / ".join(
                f"{item['level']}={item['lord']}"
                for item in timing["moon_periods"]["current"]
            )
        ),
        (
            "- Event Lords and Ruling Lords Intersection: "
            + ("/".join(timing["period_lords"]) or "None")
        ),
        f"- Accepted Ruling Planets: {accepted_ruling_planets}",
        f"- Four-level Period Candidates: {period_candidates}",
        f"- Transit Entry: {transit_reading}",
        f"- Sensitive Points within 5': {sensitive}",
        f"- {timing_boundary}",
        (
            "- This sheet interprets KP 1–249 horary results independently. It does not modify "
            "structured_prashna.md nor translate KP states into standard internal tiers (Favorable / Balanced / Unfavorable)."
        ),
        f"- Research Validation Status: {data['production_status']}.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent KP 1–249 horary engine")
    parser.add_argument(
        "--datetime",
        required=True,
        help='"YYYY-MM-DD HH:MM[:SS[.ffffff]]" or "now"',
    )
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--tz", required=True)
    parser.add_argument("--number", type=int, required=True)
    parser.add_argument("--topic", choices=tuple(TOPIC_RULES), required=True)
    parser.add_argument(
        "--outcome-scope",
        choices=tuple(KP_OUTCOME_SCOPES),
        required=True,
        help="User-confirmed observable outcome; unsupported scopes fail closed",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        validate_outcome_scope(args.topic, args.outcome_scope)
    except ValueError as exc:
        parser.error(str(exc))
    dt = parse_local_datetime(args.datetime, args.tz)
    data = compute(dt, args.lat, args.lon, args.tz, args.number, args.topic)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_kp_section(data), end="")


if __name__ == "__main__":
    main()
