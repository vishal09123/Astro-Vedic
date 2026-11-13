#!/usr/bin/env python3
"""Prashna default standard layer formatter.

Consumes only whitelisted fields from `resources/standard-layer.md`.
Even if the shared engine calculates natal Dasha, Chara Karaka, SAV, divisional
charts, Yogas, or transits, this formatter does not read or output them.
"""

CLASSICAL_PLANETS = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"
]
NODES = ["Rahu", "Ketu"]
MOVABLE_SIGNS = {"Aries", "Cancer", "Libra", "Capricorn"}
FIXED_SIGNS = {"Taurus", "Leo", "Scorpio", "Aquarius"}
HEAD_RISING_SIGNS = {"Gemini", "Leo", "Virgo", "Libra", "Scorpio", "Aquarius"}
BACK_RISING_SIGNS = {"Aries", "Taurus", "Cancer", "Sagittarius", "Capricorn"}
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}
KENDRA_FROM = {4, 7, 10}
TRIKONA_FROM = {5, 9}
STRONG_BASIC = {"exalted", "own_sign", "moolatrikona"}
# Ability layer (M-XIV.39–40 Raman commentary: strong = own sign, exalted, friend's sign (natural friend); weak = debilitated; dusthana = 6/8/12).
# Engine's moolatrikona is a degree span within own sign, categorized under "own sign" here without separate tier.
# Natural friendship follows BPHS Naisargika table, consistent with engine.
NATURAL_FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"}, "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"}, "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"}, "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}
DUSTHANA = {6, 8, 12}
# M-XIV.40 Raman commentary: good places = kendras, trikonas, 11th house (from Lagna, same reference as dusthana).
GOOD_PLACES = {1, 4, 5, 7, 9, 10, 11}

# Descriptive questions lookup table (P-VI.4, P-VII.13 notes), provides facts only, no conclusions.
PLANET_DIRECTIONS = {
    "Sun": "East", "Venus": "Southeast", "Mars": "South", "Rahu": "Southwest",
    "Saturn": "West", "Moon": "Northwest", "Mercury": "North", "Jupiter": "Northeast",
}
SIGN_DIRECTIONS = {
    "Aries": "East", "Leo": "East", "Sagittarius": "East",
    "Taurus": "South", "Virgo": "South", "Capricorn": "South",
    "Gemini": "West", "Libra": "West", "Aquarius": "West",
    "Cancer": "North", "Scorpio": "North", "Pisces": "North",
}
DREKKANA_PLACES = ["Threshold", "Middle section", "Backyard"]
OBJECT_KINDS_ODD = ["Dhatu (Minerals/Metals)", "Moola (Vegetable/Flora)", "Jeeva (Living beings/Fauna)"]
OBJECT_KINDS_EVEN = ["Jeeva (Living beings/Fauna)", "Moola (Vegetable/Flora)", "Dhatu (Minerals/Metals)"]
NAVAMSA_SIZES = {
    "Aquarius": "Short (incl. round)", "Pisces": "Short (incl. round)",
    "Aries": "Short (incl. round)", "Taurus": "Short (incl. round)",
    "Gemini": "Medium", "Cancer": "Medium", "Sagittarius": "Medium", "Capricorn": "Medium",
    "Leo": "Long", "Scorpio": "Long", "Virgo": "Long", "Libra": "Long",
}
NIGHT_SIGNS = {"Aries", "Taurus", "Gemini", "Cancer", "Sagittarius", "Capricorn"}
HIDING_PLACES = {
    "Aries": "Walkway", "Taurus": "Cattle shed", "Gemini": "Hall/theater/battleground",
    "Cancer": "Near water", "Leo": "Forest area", "Virgo": "Near port", "Libra": "Shop/market",
    "Scorpio": "Cave", "Sagittarius": "Around temple", "Capricorn": "Near water",
    "Aquarius": "Artistic place or storage room", "Pisces": "Near water",
}
LORD_AGES = {
    "Moon": "Child", "Mars": "Over four years", "Mercury": "5–12 years",
    "Venus": "Youth up to 23", "Jupiter": "Middle aged", "Sun": "Senior",
    "Saturn": "Elderly",
}
# P-VII.12 note: "other karakas too can be handled in an identical manner"; persons & karakas per M-XIV.31.
RELATIVE_KARAKAS = {
    "Sun": "Father", "Moon": "Mother", "Mars": "Siblings",
    "Jupiter": "Children", "Venus": "Spouse", "Saturn": "Servants/subordinates"
}
# P-VII.4 note: Watery signs have dual classical views listed in parallel.
WATERY_HORASARA = {"Cancer", "Capricorn", "Scorpio", "Pisces"}

# P-I.4 note sixfold divisional charts (Lagna, Hora, Drekkana, Navamsa, Dwadasamsa, Trimsamsa).
# Hora takes traditional Sun/Moon Hora (odd signs: 1st half Leo, 2nd half Cancer; even signs inverted);
# shared engine D2 is Uma Shambhu Hora (JHora "D-2 (US)", PyJHora parivritti), distinct standard, not read.
# Other divisions use Parashara formula and cross-check Lagna against engine division; any mismatch marks unavailable.
SHADVARGA_NAMES = {
    "D1": "Lagna Rashi", "D2": "Hora (Traditional Sun/Moon)", "D3": "Drekkana",
    "D9": "Navamsa", "D12": "Dwadasamsa", "D30": "Trimsamsa",
}
TRIMSAMSA_ODD = ((5, "Aries"), (10, "Aquarius"), (18, "Sagittarius"), (25, "Gemini"), (30, "Libra"))
TRIMSAMSA_EVEN = ((5, "Taurus"), (12, "Virgo"), (20, "Pisces"), (25, "Capricorn"), (30, "Scorpio"))


def _modality(sign):
    if sign in MOVABLE_SIGNS:
        return "movable"
    if sign in FIXED_SIGNS:
        return "fixed"
    return "dual"


def _rising_type(sign):
    if sign in HEAD_RISING_SIGNS:
        return "Shirshodaya(head-rising)"
    if sign in BACK_RISING_SIGNS:
        return "Prishtodaya(back-rising)"
    return "Ubhayodaya(both-rising)"


def _distance_to_boundary(degree, span):
    remainder = degree % span
    return min(remainder, span - remainder)


def _occupants(chart, house, names):
    return [name for name in names if chart["planets"][name]["house"] == house]


def _classical_aspecting_house(chart, house):
    hits = []
    for name in CLASSICAL_PLANETS:
        data = chart["graha_drishti"].get(name, {})
        if house in data.get("aspected_houses", []):
            hits.append(name)
    return hits


def _simple_exchanges(chart):
    """Returns house lord exchange facts without consuming engine natal yoga classification."""
    pairs = []
    lords = chart["house_lords"]
    planets = chart["planets"]
    for first in range(1, 13):
        for second in range(first + 1, 13):
            first_lord = lords[first]["lord"]
            second_lord = lords[second]["lord"]
            if first_lord == second_lord:
                continue
            if (
                planets[first_lord]["house"] == second
                and planets[second_lord]["house"] == first
            ):
                pairs.append((first, second, first_lord, second_lord))
    return pairs


def _natural_role(chart, name):
    """Bhattotpala natural benefic/malefic role, fallback when Ayer criteria F1~F3 do not trigger."""
    if name in {"Jupiter", "Venus"}:
        return "Benefic"
    if name in {"Sun", "Mars", "Saturn"}:
        return "Malefic"
    if name == "Moon":
        phase = chart.get("moon_phase", {})
        return "Waxing (Undefined)" if phase.get("waxing") else "Malefic"
    if name == "Mercury":
        malefics = {"Sun", "Mars", "Saturn"}
        mercury_house = chart["planets"]["Mercury"]["house"]
        joined = [
            planet
            for planet in malefics
            if chart["planets"][planet]["house"] == mercury_house
        ]
        return "Malefic" if joined else "Benefic"
    raise ValueError(name)


def _natural_role_text(chart, name):
    role = _natural_role(chart, name)
    if role == "Waxing (Undefined)":
        return "Waxing Moon; text only specifies Full Moon as benefic"
    if name == "Mercury" and role == "Malefic":
        return "Malefic (conjoined with malefic)"
    return role


def _houses_ruled_from(planet, sign):
    """Houses ruled by planet taking sign as the 1st house."""
    base = SIGNS.index(sign)
    return {
        house
        for house in range(1, 13)
        if SIGN_LORDS[SIGNS[(base + house - 1) % 12]] == planet
    }


def _ayer_role(chart, planet, sign):
    """Ayer P-I.3 functional benefic/malefic role: planet relative to occupied/aspected sign.

    F1 Own lord is always benefic;
    F2 Rules houses 3, 12 and is debilitated -> malefic (Note Example 1: Jupiter/Capricorn);
    F3 Rules kendra and trikona and is strong (exalted/own_sign/moolatrikona) -> benefic (Note Example 2: Mars/Leo);
    Otherwise falls back to Bhattotpala natural role.
    """
    ruled = _houses_ruled_from(planet, sign)
    basic = chart.get("dignity", {}).get(planet, {}).get("basic")
    if 1 in ruled:
        return "Benefic (Own Lord)"
    if {3, 12} <= ruled and basic == "debilitated":
        return "Malefic (Note Example 1)"
    if ruled & KENDRA_FROM and ruled & TRIKONA_FROM and basic in STRONG_BASIC:
        return "Benefic (Note Example 2)"
    return f"{_natural_role(chart, planet)} (Fallback)"


def _labelled(chart, names, sign):
    return ", ".join(f"{name} {_ayer_role(chart, name, sign)}" for name in names)


def _lord_ability(chart, house):
    """Ability layer facts: afflictions, mitigations, and capacity verdict of house lord.
    Does not enter ledger sum; used exclusively for veto power and narrative explanation.

    Afflictions (M-XIV.39–40; M-XIV.30):
    Debilitated, in houses 6/8/12, combust, retrograde, aspected/occupied by malefics without benefics.
    Lord occupying own house is not counted as placed in 6/8/12 (M-XIV.42).
    Mitigations: Benefic conjunction/aspect; exalted, own sign, natural friend's sign (debilitated planet excluded);
    debilitated but in good place (M-XIV.40).
    Verdict: 3+ afflictions, or 2 afflictions without mitigation -> Severely Afflicted;
    1–2 afflictions -> Compromised Capacity; 0 afflictions -> Strong or Normal.
    """
    planet = chart["house_lords"][house]["lord"]
    data = chart["planets"][planet]
    where, sign = data["house"], data["sign"]
    basic = chart.get("dignity", {}).get(planet, {}).get("basic")
    others = [name for name in _occupants(chart, where, CLASSICAL_PLANETS) if name != planet]
    others += [name for name in _classical_aspecting_house(chart, where) if name != planet]
    roles = [_ayer_role(chart, name, sign) for name in others]
    malefics = [name for name, role in zip(others, roles) if role.startswith("Malefic")]
    malefic = bool(malefics)
    benefic = any(role.startswith("Benefic") for role in roles)
    factors = []
    if basic == "debilitated":
        factors.append("Debilitated")
    if where in DUSTHANA and where != house:
        factors.append(f"Placed in house {where}")
    if planet in chart.get("combustion", {}):
        factors.append("Combust")
    if data.get("retrograde"):
        factors.append("Retrograde")
    if malefic and not benefic:
        factors.append(f"Aspected/occupied by malefic ({', '.join(malefics)}), no benefic")
    strong = basic in STRONG_BASIC or (basic != "debilitated" and SIGN_LORDS[sign] in NATURAL_FRIENDS[planet])
    rescue = []
    if benefic:
        rescue.append("Aspected/occupied by benefic")
    if strong:
        rescue.append("Exalted" if basic == "exalted" else "Own sign" if basic in {"own_sign", "moolatrikona"} else "Natural friend sign")
    if basic == "debilitated" and where in GOOD_PLACES:
        rescue.append(f"Weak but in good place (house {where})")
    if len(factors) >= 3 or (len(factors) == 2 and not rescue):
        verdict = "Severely Afflicted"
    elif factors:
        verdict = "Compromised Capacity"
    else:
        verdict = "Strong" if strong else "Normal"
    return planet, factors, rescue, verdict


def _lord_links(chart, house):
    """Desire layer facts: planets conjoined/aspecting house lord (and houses ruled from Lagna), and link to Lagna lord."""
    lagna_sign = chart["lagna"]["sign"]
    planets = chart["planets"]
    planet = chart["house_lords"][house]["lord"]
    where = planets[planet]["house"]

    def with_rule(names):
        return ", ".join(
            f"{name} (rules {', '.join(map(str, sorted(_houses_ruled_from(name, lagna_sign)))) or '—'})"
            if name in CLASSICAL_PLANETS else name
            for name in names
        ) or "—"

    joined = [n for n in _occupants(chart, where, CLASSICAL_PLANETS + NODES) if n != planet]
    aspecting = [n for n in _classical_aspecting_house(chart, where) if n != planet]
    first_lord = chart["house_lords"][1]["lord"]
    if planet == first_lord:
        link = "Lagna lord itself"
    else:
        link = ", ".join(_relation(chart, first_lord, planet)) or "None"
    return planet, with_rule(joined), with_rule(aspecting), link


def _sees(chart, a, b):
    """True if a's Graha Drishti falls on the house where b is located."""
    where = chart["planets"][b]["house"]
    return where in chart["graha_drishti"].get(a, {}).get("aspected_houses", [])


def _relation(chart, a, b):
    """M-XIV.43 Connections: same house; aspect; mutual exchange; mutual 4/10 relationship."""
    if a == b:
        return ["Same planet"]
    planets = chart["planets"]
    kinds = []
    if planets[a]["house"] == planets[b]["house"]:
        kinds.append("Same house")
    ab, ba = _sees(chart, a, b), _sees(chart, b, a)
    if ab and ba:
        kinds.append("Mutual aspect")
    elif ab or ba:
        kinds.append(f"{a} aspects {b}" if ab else f"{b} aspects {a}")
    if SIGN_LORDS[planets[a]["sign"]] == b and SIGN_LORDS[planets[b]["sign"]] == a:
        kinds.append("Mutual exchange")
    if (planets[b]["house"] - planets[a]["house"]) % 12 in (3, 9):
        kinds.append("Mutual 4/10 relationship")
    return kinds


def _touches(chart, karaka, planet):
    """Karaka bridging check: karaka conjoined with planet or aspects planet."""
    if karaka == planet:
        return "Same planet directly"
    if chart["planets"][karaka]["house"] == chart["planets"][planet]["house"]:
        return "Same house"
    return f"{karaka} aspects {planet}" if _sees(chart, karaka, planet) else ""


def _derived(actor, n):
    """The nth house taking actor house as 1st house (derived house)."""
    return (actor + n - 2) % 12 + 1


def _action_chain(chart, actor):
    """Action chain: evaluates whether actor will act; does not enter ledger sum.

    1. Initiative: Derived 3rd lord connects with actor lord, or Mars touches actor lord (M-XIV.5, 31, 43);
    2. Action: Derived 10th lord connects with actor lord or is identical planet (M-XIV.12);
    3. Directed at querent: Actor lord, initiative lord, or action lord connects with Lagna lord, or bridged via Mars (M-XIV.43);
    4. Capacity: Actor lord or initiative lord is Severely Afflicted (M-XIV.39).
    """
    lord = lambda house: chart["house_lords"][house]["lord"]
    rel = lambda a, b: ", ".join(_relation(chart, a, b))
    first, doer = lord(1), lord(actor)
    starter, mover = lord(_derived(actor, 3)), lord(_derived(actor, 10))
    pair = lambda a, b: f"Actor lord {b} directly" if a == b else (f"{a}–{b}: {rel(a, b)}" if rel(a, b) else "")
    start = [f"Initiative lord {pair(starter, doer)}"] if pair(starter, doer) else []
    if doer == "Mars":
        start.append("Actor lord is Mars directly")
    elif _touches(chart, "Mars", doer):
        start.append(f"Mars–{doer}: {_touches(chart, 'Mars', doer)}")
    move = pair(mover, doer)
    point = [f"{p} is Lagna lord directly" if p == first else f"{p}–{first}: {rel(p, first)}"
             for p in dict.fromkeys((doer, starter, mover)) if rel(p, first)]
    to_first, to_doer = _touches(chart, "Mars", first), _touches(chart, "Mars", doer)
    if to_first and to_doer and "Mars" not in (first, doer) and doer != first:
        point.append(f"Bridged via Mars (Mars–{first}: {to_first}; Mars–{doer}: {to_doer})")
    weak = [f"House {h} lord" for h in dict.fromkeys((actor, _derived(actor, 3)))
            if _lord_ability(chart, h)[3] == "Severely Afflicted"]
    if not start:
        verdict = "No Initiative in Chart"
    elif not point:
        verdict = "Initiative not Directed at Querent"
    elif weak:
        verdict = "Willing but Incapacitated"
    else:
        verdict = "Favorable (Action Expected)" if move else "Favorable (Arrested in Thought/Speech)"
    return start, move, point, weak, verdict


ACTION_KARAKAS = [
    ("Mars", "Courage/Initiative"), ("Mercury", "Speech/Intellect"), ("Venus", "Affection"),
    ("Sun", "Authority/Ruler"), ("Jupiter", "Wisdom")
]


def _chain_lines(chart):
    lagna_sign = chart["lagna"]["sign"]
    lord = lambda house: chart["house_lords"][house]["lord"]
    lines = ["### Actor Perspective (Derived Houses) and Action Chain\n"]
    lines.append(
        "> Taking the actor's house as Lagna, evaluate derived houses (M-XVII.8–9, M-XIV.116 note): "
        "2nd for speech, 3rd for initiative, 7th for partner/object of affection, 10th for action, 11th for fruition. "
        "Action chains evaluate whether the actor acts; they do not score in the ledger (`judgment-rubric.md` §2.5).\n"
    )
    lines.append("| Actor | Speech (Derived 2nd) | Initiative (Derived 3rd) | Affection Object (Derived 7th) | Action (Derived 10th) | Fruition (Derived 11th) |")
    lines.append("|---|---|---|---|---|---|")
    cell = lambda h: f"House {h} ({lord(h)} · {_lord_ability(chart, h)[3]})"
    for actor in range(2, 13):
        lines.append(
            f"| House {actor} ({lord(actor)}) | "
            + " | ".join(cell(_derived(actor, n)) for n in (2, 3, 7, 10, 11)) + " |"
        )
    lines.append("")
    lines.append("| Actor | (1) Initiative | (2) Action | (3) Directed at Querent | (4) Severely Afflicted | Action Chain Verdict |")
    lines.append("|---|---|---|---|---|---|")
    for actor in range(2, 13):
        start, move, point, weak, verdict = _action_chain(chart, actor)
        lines.append(
            f"| House {actor} | {'; '.join(start) or '—'} | {move or '—'} | "
            f"{'; '.join(point) or '—'} | {', '.join(weak) or '—'} | {verdict} |"
        )
    lines.append("")
    lines.append(
        "> Karaka Bridging: When a natural Karaka conjoins or aspects both parties, it bridges them. "
        "Applies only to Karakas relevant to the requested action (`question-decomposition.md`).\n"
    )
    lines.append("| Karaka (Signification) | Touched House Lords (Conjunction/Aspect) | Houses Bridged with Lagna Lord |")
    lines.append("|---|---|---|")
    first = lord(1)
    for karaka, meaning in ACTION_KARAKAS:
        touched = []
        for planet in dict.fromkeys(lord(h) for h in range(1, 13)):
            how = _touches(chart, karaka, planet)
            if how and how != "Same planet directly":
                houses = ", ".join(map(str, sorted(_houses_ruled_from(planet, lagna_sign))))
                touched.append(f"{planet} (rules {houses}; {how})")
        if karaka == first:
            bridged = "Lagna lord itself"
        elif not _touches(chart, karaka, first):
            bridged = "— (Does not touch Lagna lord)"
        else:
            bridged = ", ".join(
                f"House {h} ({lord(h)})" for h in range(2, 13)
                if lord(h) not in (first, karaka) and _touches(chart, karaka, lord(h))
            ) or "—"
        lines.append(f"| {karaka} ({meaning}) | {', '.join(touched) or '—'} | {bridged} |")
    lines.append("")
    return lines


def _lord_lines(chart):
    lines = ["### House Lord Ability and Connections\n"]
    lines.append(
        "> Ability Layer: Afflictions and mitigations per M-XIV.39–40 and M-XIV.30. "
        "A lord in own house is not penalized for occupying 6/8/12 (M-XIV.42). "
        "Combustion or retrogradation alone is an affliction, not standalone incapacity; "
        "multiple afflictions without mitigation yield 'Severely Afflicted'. "
        "This table does not enter ledger sum; 'Severely Afflicted' serves solely as an ability veto.\n"
    )
    lines.append("| House | Lord | Lord Placement (Sign) | D1 Dignity | Afflictions | Mitigations | Capacity Verdict |")
    lines.append("|---:|---|---|---|---|---|---|")
    dignity = chart.get("dignity", {})
    for house in range(1, 13):
        planet, factors, rescue, verdict = _lord_ability(chart, house)
        data = chart["planets"][planet]
        lines.append(
            f"| {house} | {planet} | House {data['house']} ({data['sign']}) | "
            f"{dignity.get(planet, {}).get('basic', '—')} | {', '.join(factors) or '—'} | "
            f"{', '.join(rescue) or '—'} | {verdict} |"
        )
    lines.append("")
    lines.append(
        "> Desire Layer: Facts on conjunctions, aspects, and connections to Lagna lord per M-XIV.33/47/48 and M-XIV.43. "
        "Does not enter ledger sum.\n"
    )
    lines.append("| House | Lord | Conjoined Planets (Houses Ruled) | Aspecting Planets (Houses Ruled) | Connection to Lagna Lord |")
    lines.append("|---:|---|---|---|---|")
    for house in range(1, 13):
        planet, joined, aspecting, link = _lord_links(chart, house)
        lines.append(f"| {house} | {planet} | {joined} | {aspecting} | {link} |")
    lines.append("")
    return lines


def _navamsa_number(degree):
    return min(int(degree // (30 / 9)), 8) + 1


def _shadvarga_signs(sign, degree):
    """Signs of each of the 6 divisional charts when Lagna falls at degree in sign."""
    si = SIGNS.index(sign)
    odd = si % 2 == 0
    trimsamsa = TRIMSAMSA_ODD if odd else TRIMSAMSA_EVEN
    return {
        "D1": sign,
        "D2": "Leo" if (degree < 15) == odd else "Cancer",
        "D3": SIGNS[(si + 4 * min(int(degree // 10), 2)) % 12],
        "D9": SIGNS[(si + (0, 8, 4)[si % 3] + _navamsa_number(degree) - 1) % 12],
        "D12": SIGNS[(si + min(int(degree // 2.5), 11)) % 12],
        "D30": next(s for bound, s in trimsamsa if degree < bound),
    }


def _shadvarga_cuts(sign):
    """Cut-off degrees within the sign for each of the 6 divisional charts."""
    trimsamsa = TRIMSAMSA_ODD if SIGNS.index(sign) % 2 == 0 else TRIMSAMSA_EVEN
    return {
        "D1": [],
        "D2": [15.0],
        "D3": [10.0, 20.0],
        "D9": [k * 30 / 9 for k in range(1, 9)],
        "D12": [k * 2.5 for k in range(1, 12)],
        "D30": [float(bound) for bound, _ in trimsamsa[:-1]],
    }


def _shadvarga_majority(chart, sign, degree):
    """Count functional benefic/malefic roles of divisional lords relative to Lagna sign."""
    roles = [_ayer_role(chart, SIGN_LORDS[s], sign) for s in _shadvarga_signs(sign, degree).values()]
    good = sum(role.startswith("Benefic") for role in roles)
    bad = sum(role.startswith("Malefic") for role in roles)
    return good, bad, "Benefic dominant" if good > bad else "Malefic dominant" if bad > good else "Equal"


def _shadvarga_critical(chart, sign, degree):
    """Degrees Lagna must move within the sign before Shadvarga majority flips."""
    base = _shadvarga_majority(chart, sign, degree)[2]
    cuts = sorted({c for values in _shadvarga_cuts(sign).values() for c in values})
    found = []
    for c in (c for c in cuts if c > degree):
        if _shadvarga_majority(chart, sign, c + 1e-9)[2] != base:
            found.append(c - degree)
            break
    for c in (c for c in reversed(cuts) if c <= degree):
        if _shadvarga_majority(chart, sign, c - 1e-9)[2] != base:
            found.append(degree - c)
            break
    return min(found) if found else None


def _shadvarga_lines(chart):
    lagna = chart["lagna"]
    sign, degree = lagna["sign"], lagna["degree"]
    signs = _shadvarga_signs(sign, degree)
    lines = ["### Lagna Shadvarga Lords (`P-I.4` Note)\n"]
    engine_charts = chart.get("divisional_charts", {})
    problems = []
    for key in ("D3", "D9", "D12", "D30"):
        entry = engine_charts.get(key)
        if not entry:
            problems.append(f"{key} missing (engine did not supply this division)")
        elif "error" in entry:
            problems.append(f"{key} error ({entry['error']})")
        elif "Lagna" not in entry:
            problems.append(f"{key} missing Lagna entry")
        elif entry["Lagna"]["sign"] != signs[key]:
            edge = min(abs(degree - c) for c in _shadvarga_cuts(sign)[key] + [0.0, 30.0])
            problems.append(
                f"{key} mismatch (engine {entry['Lagna']['sign']} / formula {signs[key]}; "
                f"Lagna {sign} {degree:.4f}°, boundary distance {edge:.4f}°)"
            )
    if problems:
        lines.append(
            f"- Shadvarga unavailable: {'; '.join(problems)}. Formula mismatches are not manually interpolated; "
            "`P-I.4` omits varga factor in this chart."
        )
        lines.append("")
        return lines
    lines.append("| Division | Sign | Lord | Functional Role of Lord to Lagna Sign | Distance to Sub-Division Boundary |")
    lines.append("|---|---|---|---|---|")
    for key, cuts in _shadvarga_cuts(sign).items():
        lord = SIGN_LORDS[signs[key]]
        edge = f"{min(abs(degree - c) for c in cuts):.3f}°" if cuts else "See Lagna distance to sign boundary"
        lines.append(
            f"| {SHADVARGA_NAMES[key]} | {signs[key]} | {lord} | "
            f"{_ayer_role(chart, lord, sign)} | {edge} |"
        )
    good, bad, majority = _shadvarga_majority(chart, sign, degree)
    critical = _shadvarga_critical(chart, sign, degree)
    critical_text = (
        f"{critical:.3f}°" if critical is not None else "Unchanged within sign (boundary only)"
    )
    lines.append("")
    lines.append(f"- Total: Benefic {good}, Malefic {bad}, Excluded {6 - good - bad} → **{majority}**")
    lines.append(f"- Shadvarga majority critical shift distance: {critical_text}")
    lines.append(
        "- Scope restriction: Sourced exclusively for `P-I.4` ('falls in a benefic's varga'): "
        "Benefic dominant = benefic varga, Malefic dominant = malefic varga, Equal = excluded; "
        "do not expand into D2, D3, D9, D12, D30 life readings."
    )
    lines.append("")
    return lines


def tithi_facts(sun_longitude, moon_longitude):
    """Tithi computation using unrounded longitudinal difference; Full Moon window per P-I.5 note (Tithi 10 to 20)."""
    elongation = (moon_longitude - sun_longitude) % 360.0
    tithi = int(elongation // 12.0) + 1
    return tithi, 10 <= tithi <= 20


def _house_from(start_house, target_house):
    return (target_house - start_house) % 12 + 1


def _watery_mantreswara(sign, degree):
    if sign in {"Cancer", "Pisces"}:
        return True
    return sign == "Capricorn" and degree >= 15


def _yes(flag):
    return "yes" if flag else "no"


def _descriptive_facts(chart, d9_lagna):
    """Descriptive lookup tables (P-VI.1~4, P-VII.13, P-I.7), absentee location (P-VII.12), and weather (P-VII.3~4)."""
    lagna = chart["lagna"]
    planets = chart["planets"]
    sign = lagna["sign"]
    degree = lagna["degree"]
    lines = []

    lines.append("### Descriptive and Weather Lookup Facts\n")
    lines.append(
        "> Consumed exclusively for lookup queries (`matter-rules.md` §5). "
        "Descriptive outputs do not enter internal outcome tiers. Dual classical views are presented in parallel.\n"
    )

    lines.append("**P-VI.1~2 Lost Article Inside House and Location**\n")
    if d9_lagna:
        d9_sign = d9_lagna["sign"]
        lines.append(
            f"- Lagna fixed sign: {_yes(sign in FIXED_SIGNS)}; rising Navamsa fixed sign: "
            f"{_yes(d9_sign in FIXED_SIGNS)}; vargottama (Lagna sign = rising Navamsa sign): "
            f"{_yes(sign == d9_sign)}"
        )
    else:
        lines.append(
            f"- Lagna fixed sign: {_yes(sign in FIXED_SIGNS)}; rising Navamsa unavailable, "
            "VI.1 reads Lagna only"
        )
    drekkana = min(int(degree // 10), 2)
    lines.append(
        f"- Lagna in drekkana #{drekkana + 1} (10° segments) → Hiding spot in house: "
        f"{DREKKANA_PLACES[drekkana]} (used only when VI.1 indicates 'inside house')"
    )
    lines.append("")

    lines.append("**P-VI.4 Direction and Distance**\n")
    kendra_planets = [
        name
        for name in CLASSICAL_PLANETS + ["Rahu"]
        if planets[name]["house"] in {1, 4, 7, 10}
    ]
    lagna_direction = SIGN_DIRECTIONS[sign]
    listed = ", ".join(
        f"{name} (House {planets[name]['house']}, {PLANET_DIRECTIONS[name]})"
        for name in kendra_planets
    )
    lines.append(
        f"- Planets in kendras (incl. Rahu; Ketu omitted in text): {listed or 'None'}"
    )
    lines.append(f"- Lagna sign direction: {lagna_direction}")
    if not kendra_planets:
        lines.append(f"- Direction interpretation: No planets in kendras, read by Lagna sign → {lagna_direction}")
    elif len(kendra_planets) == 1:
        only = kendra_planets[0]
        lines.append(
            f"- Direction interpretation: Single planet in kendra: text reads {PLANET_DIRECTIONS[only]}; "
            f"note reads {lagna_direction}; dual views presented in parallel"
        )
    else:
        directions = sorted({PLANET_DIRECTIONS[name] for name in kendra_planets})
        lines.append(
            f"- Direction interpretation: {len(kendra_planets)} planets in kendras, read by planets → "
            f"{' / '.join(directions)}"
        )
    number = _navamsa_number(degree)
    first_half = degree < 15
    offset = number - 1 if first_half else number - 5
    lines.append(
        f"- Lagna in {'first' if first_half else 'second'} half of sign, rising Navamsa ordinal #{number}, "
        f"offset from {'1st' if first_half else 'middle 5th'} Navamsa is {offset} units → Distance reading {offset} "
        "(relative distance scale 0–4)"
    )
    lines.append("")

    lines.append("**P-I.7, P-VII.13 Articles and Persons**\n")
    odd_sign = SIGNS.index(sign) % 2 == 0
    kinds = OBJECT_KINDS_ODD if odd_sign else OBJECT_KINDS_EVEN
    lines.append(
        f"- Article classification (I.7, Lagna in {'odd' if odd_sign else 'even'} sign Navamsa #{number}): "
        f"{kinds[(number - 1) % 3]}"
    )
    if d9_lagna:
        lines.append(
            f"- Article size (VII.13 note, rising Navamsa {d9_lagna['sign']}): "
            f"{NAVAMSA_SIZES[d9_lagna['sign']]}"
        )
    lines.append(
        f"- Theft timeframe (Lagna {sign}): {'Night' if sign in NIGHT_SIGNS else 'Day'}"
    )
    lines.append(f"- Direction of removal (Lagna {sign}): {lagna_direction}")
    lines.append(f"- Concealment place (Lagna {sign}): {HIDING_PLACES[sign]}")
    lagna_lord = SIGN_LORDS[sign]
    lines.append(
        f"- Age of taker / missing person (Lagna lord {lagna_lord}): {LORD_AGES[lagna_lord]}"
    )
    lines.append("")

    lines.append("**P-VII.12 Absentee Location (Karaka conjoined with and aspected by benefic in 8th house = away, else local)**\n")
    eighth = chart["house_lords"][8]["sign"]
    with_b = [n for n in _occupants(chart, 8, CLASSICAL_PLANETS) if _ayer_role(chart, n, eighth).startswith("Benefic")]
    asp_b = [n for n in _classical_aspecting_house(chart, 8) if _ayer_role(chart, n, eighth).startswith("Benefic")]
    for name, who in RELATIVE_KARAKAS.items():
        if planets[name]["house"] != 8:
            lines.append(f"- {who} ({name}): Placed in house {planets[name]['house']}, not in 8th → Local")
            continue
        comp = [n for n in with_b if n != name]
        seen = [n for n in asp_b if n != name]
        lines.append(
            f"- {who} ({name}): In 8th house; conjoined benefics {', '.join(comp) or 'None'}; "
            f"aspecting benefics {', '.join(seen) or 'None'} → {'Away' if comp and seen else 'Local'}"
        )
    lines.append("")

    lines.append("**P-VII.3~4 Weather Facts**\n")
    moon_house = planets["Moon"]["house"]
    sun_house = planets["Sun"]["house"]
    venus_house = planets["Venus"]["house"]
    saturn_house = planets["Saturn"]["house"]
    lines.append(f"- Waxing Moon: {_yes(chart.get('moon_phase', {}).get('waxing'))}")
    lines.append(
        f"- VII.3(a): Venus in house #{_house_from(moon_house, venus_house)} from Moon; "
        f"Saturn in house #{_house_from(moon_house, saturn_house)} from Moon, "
        f"house #{_house_from(sun_house, saturn_house)} from Sun"
    )
    lines.append(
        f"- VII.3(b): Venus in house #{venus_house} from Lagna; Saturn in house #{saturn_house}"
    )
    rain_houses = (3, 2, 1, 4, 7, 10)
    rain_planets = [
        name
        for name in CLASSICAL_PLANETS
        if planets[name]["house"] in rain_houses
    ]
    if rain_planets:
        for name in rain_planets:
            planet = planets[name]
            lines.append(
                f"- VII.4(a): {name} in house {planet['house']} {planet['sign']}, "
                f"{_ayer_role(chart, name, planet['sign'])}; Watery Horasara: "
                f"{_yes(planet['sign'] in WATERY_HORASARA)}; Mantreswara: "
                f"{_yes(_watery_mantreswara(planet['sign'], planet['degree']))}"
            )
    else:
        lines.append("- VII.4(a): No classical planets in houses 3, 2, or kendras")
    moon = planets["Moon"]
    lines.append(
        f"- VII.4(b): Moon in Lagna: {_yes(moon_house == 1)}; Moon sign {moon['sign']} Watery "
        f"Horasara: {_yes(moon['sign'] in WATERY_HORASARA)}; Mantreswara: "
        f"{_yes(_watery_mantreswara(moon['sign'], moon['degree']))}"
    )
    lines.append("")
    return lines


def format_standard_layer(chart):
    lagna = chart["lagna"]
    planets = chart["planets"]
    d9_lagna = chart.get("divisional_charts", {}).get("D9", {}).get("Lagna")
    lines = []

    lines.append("## Prashna Default Standard Layer Data\n")
    lines.append(
        "> Source Contract: Shatpanchasika-rooted classical Prashna, screened via KN Rao / Bhavan compatibility. "
        "Provides facts only; success/failure conclusions are not generated in this data layer."
    )
    lines.append(
        "> Consult `resources/standard-layer.md` before interpretation.\n"
    )

    lines.append("### Lagna and Rising Navamsa\n")
    lines.append("| Item | Value | Scope / Restriction |")
    lines.append("|---|---|---|")
    gemini_note = (
        "; P-VI.3 note list omits Gemini, dual commentary presented"
        if lagna["sign"] == "Gemini"
        else ""
    )
    lines.append(
        f"| Lagna | {lagna['sign']} {lagna['deg_str']} | "
        f"{_modality(lagna['sign'])}; {_rising_type(lagna['sign'])}{gemini_note} |"
    )
    lines.append(
        f"| Lagna Distance to Sign Boundary | {_distance_to_boundary(lagna['degree'], 30):.3f}° | "
        "Input sensitivity fact; does not invalidate chart |"
    )
    lines.append(
        f"| Lagna Distance to Navamsa Boundary | "
        f"{_distance_to_boundary(lagna['degree'], 30 / 9):.3f}° | "
        "Input sensitivity fact |"
    )
    if d9_lagna:
        lines.append(
            f"| Rising Navamsa | {d9_lagna['sign']} {d9_lagna['degree']:.4f}° "
            f"(Navamsa #{_navamsa_number(lagna['degree'])} of sign) | "
            "Used for P-I.7, P-VI.1, P-VI.4, P-VII.13 only; do not expand into full D9 reading |"
        )
    else:
        lines.append("| Rising Navamsa | unavailable | Do not manually interpolate |")
    lines.append("")
    lines.extend(_shadvarga_lines(chart))

    lines.append("### D1 Classical Planets\n")
    lines.append(
        "| Planet | Sign | Degree | House | Nakshatra | Motion | D1 Dignity | Combustion | "
        "Natural Role (Bhattotpala Fallback) |"
    )
    lines.append("|---|---|---:|---:|---|---|---|---|---|")
    combustion = chart.get("combustion", {})
    dignity = chart.get("dignity", {})
    for name in CLASSICAL_PLANETS:
        planet = planets[name]
        nak = planet.get("nakshatra", {})
        combustion_text = (
            f"yes, Sun dist {combustion[name]['distance']}°"
            if name in combustion
            else "no"
        )
        lines.append(
            f"| {name} | {planet['sign']} | {planet['deg_str']} | {planet['house']} | "
            f"{nak.get('name', '—')} p{nak.get('pada', '—')} | "
            f"{'R' if planet.get('retrograde') else 'D'} | "
            f"{dignity.get(name, {}).get('basic', '—')} | {combustion_text} | "
            f"{_natural_role_text(chart, name)} |"
        )
    lines.append("")

    lines.append("### Nodes Facts\n")
    lines.append(
        "> Rahu/Ketu do not carry P-I.3 functional benefic/malefic tags; default layer retains positions only.\n"
    )
    lines.append("| Node | Sign | Degree | House | Nakshatra |")
    lines.append("|---|---|---:|---:|---|")
    for name in NODES:
        planet = planets[name]
        nak = planet.get("nakshatra", {})
        lines.append(
            f"| {name} | {planet['sign']} | {planet['deg_str']} | {planet['house']} | "
            f"{nak.get('name', '—')} p{nak.get('pada', '—')} |"
        )
    lines.append("")

    lines.append("### 12 Houses, Lords, and Support / Affliction Facts\n")
    lines.append(
        "> Core input for P-I.3. 6th house and dusthanas must be interpreted by question semantics.\n"
    )
    lines.append(
        "> Functional tags follow Ayer P-I.3 criteria relative to the house sign: Benefic (Own Lord) = own lord; "
        "Malefic (Note Example 1) = rules 3, 12 and debilitated; Benefic (Note Example 2) = kendra+trikona and strong; "
        "otherwise (Fallback) to Bhattotpala natural role.\n"
    )
    lines.append(
        "| House | Sign | Lord | Lord House | Occupants (Functional Tags) | Nodes | Aspects to House (Functional Tags) |"
    )
    lines.append("|---:|---|---|---:|---|---|---|")
    for house in range(1, 13):
        lord = chart["house_lords"][house]
        sign = lord["sign"]
        classical_here = (
            _labelled(chart, _occupants(chart, house, CLASSICAL_PLANETS), sign) or "—"
        )
        nodes_here = ", ".join(_occupants(chart, house, NODES)) or "—"
        aspects = _labelled(chart, _classical_aspecting_house(chart, house), sign) or "—"
        lines.append(
            f"| {house} | {lord['sign']} | {lord['lord']} | {lord['lord_house']} | "
            f"{classical_here} | {nodes_here} | {aspects} |"
        )
    lines.append("")

    lines.append("### Graha Drishti (Classical Planetary Aspects)\n")
    lines.append(
        "> Whole-sign Parashari Graha Drishti; does not use Western orbs or applying/separating aspects.\n"
    )
    lines.append("| Planet | From House | Aspected Houses | Aspected Planets |")
    lines.append("|---|---:|---|---|")
    for name in CLASSICAL_PLANETS:
        data = chart["graha_drishti"][name]
        aspected_planets = [
            other
            for other in CLASSICAL_PLANETS
            if planets[other]["house"] in data["aspected_houses"]
        ]
        lines.append(
            f"| {name} | {data['from_house']} | "
            f"{', '.join(map(str, data['aspected_houses']))} | "
            f"{', '.join(aspected_planets) or '—'} |"
        )
    lines.append("")

    mutual = [
        pair
        for pair in chart.get("mutual_drishti", [])
        if all(name in CLASSICAL_PLANETS for name in pair)
    ]
    exchanges = _simple_exchanges(chart)
    lines.append("### Derived Structural Facts\n")
    lines.append(
        f"- Mutual Aspects: {'; '.join(' ↔ '.join(pair) for pair in mutual) or 'None'}"
    )
    if exchanges:
        for first, second, first_lord, second_lord in exchanges:
            lines.append(
                f"- House Lord Exchange: House {first} lord {first_lord} ↔ "
                f"House {second} lord {second_lord}"
            )
    else:
        lines.append("- House Lord Exchange: None")
    lines.append(
        "- Scope restriction: Records connection structures only; do not apply natal Yoga categories.\n"
    )

    lines.extend(_lord_lines(chart))
    lines.extend(_chain_lines(chart))
    lines.extend(_descriptive_facts(chart, d9_lagna))

    lines.append("### Timing Boundary\n")
    lines.append(
        "> This file contains zero timing predictions. When the standard layer yields Favorable or Balanced, "
        "the timing sub-layer runs separately (`resources/timing-layer.md`). Unfavorable verdicts receive no timing. "
        "Natal 120-year Vimshottari, Chara Dasha, and transits are never used as Prashna event timing.\n"
    )
    return "\n".join(lines)
