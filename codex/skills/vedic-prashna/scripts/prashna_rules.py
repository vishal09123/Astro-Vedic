"""prashna_rules.py — Prashna standard layer judgment rules, matter registry,
success ledger, ability veto, action chains, and qualifiers.

Judgment rules are implemented exclusively in this module (rebuilt 2026-10-29).
The LLM is responsible for query decomposition (generating the plan sheet);
this module reads only chart facts and plan sheet counts, never the raw query text.
Skill documentation (judgment-rubric.md, matter-rules.md) details methodology and citations,
corresponding 1:1 with this file.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import format_prashna_standard as F

P7 = F.CLASSICAL_PLANETS
MOV, FIX = F.MOVABLE_SIGNS, F.FIXED_SIGNS
HEAD_I4 = {"Gemini", "Leo", "Virgo", "Libra", "Scorpio", "Aquarius"}  # P-I.4 Shirshodaya
BACK_I4 = {"Aries", "Taurus", "Cancer", "Sagittarius", "Capricorn"}  # P-I.4 Prishtodaya; Pisces Ubhayodaya
HEAD_VI3 = {"Leo", "Virgo", "Libra", "Scorpio", "Aquarius"}  # P-VI.3 Ayer note list, omits Gemini
HUMAN_III3 = {"Gemini", "Virgo", "Libra", "Aquarius"}  # P-III.3 note
HUMAN_IV2 = {"Gemini", "Libra", "Aquarius"}  # P-IV.2 text
KENDRA, TRIKONA = (1, 4, 7, 10), (5, 9)
FAV, UNF = ("fav", "fav_d"), ("unf", "unf_lean")
DIRECTION_TEXT = {
    "fav": "Favorable",
    "fav_d": "Favorable (Benefic dominant, after difficulty)",
    "unf": "Unfavorable",
    "unf_lean": "Unfavorable (Malefic dominant)",
    "mixed": "Mixed",
    "none": "No Direction"
}


def score(direction):
    return 1 if direction in FAV else -1 if direction in UNF else 0


def _d(good, bad):
    return "mixed" if good and bad else "fav" if good else "unf" if bad else "none"


def _count(good, bad):
    """Rubric §4.1: Internal preponderance: more benefics = favorable (after difficulty); more malefics = unfavorable; equal = mixed."""
    return "fav_d" if good > bad else "unf_lean" if bad > good else "mixed"


# ---------------------------------------------------------------------------
# Chart Facts
# ---------------------------------------------------------------------------
class Facts:
    """Read-only view of chart facts. Functional roles calculated relative to occupied/aspected sign."""

    def __init__(self, chart, needed=()):
        self.chart = chart
        self.lsign = chart["lagna"]["sign"]
        self.ldeg = chart["lagna"]["degree"]
        self.house = {n: chart["planets"][n]["house"] for n in P7}
        self.basic = {n: chart["dignity"][n]["basic"] for n in P7}
        self.waxing = bool(chart["moon_phase"]["waxing"])
        self.needed = set(needed)  # Contextually required significators; not penalized as malefics under P-I.3

    def sign(self, h):
        return self.chart["house_lords"][h]["sign"]

    def lord(self, h):
        return self.chart["house_lords"][h]["lord"]

    def role(self, planet, sign):
        return F._ayer_role(self.chart, planet, sign)

    def cls(self, planet, sign):
        r = self.role(planet, sign)
        return "B" if r.startswith("Benefic") else "M" if r.startswith("Malefic") else "U"

    def occ(self, h):
        return [(n, self.cls(n, self.sign(h))) for n in F._occupants(self.chart, h, P7)]

    def asp(self, h):
        return [(n, self.cls(n, self.sign(h))) for n in F._classical_aspecting_house(self.chart, h)]

    def both(self, h):
        return self.occ(h) + self.asp(h)

    def sees(self, a, b):
        return F._sees(self.chart, a, b)

    def mutual(self, a, b):
        return self.sees(a, b) and self.sees(b, a)

    def text(self, h, cols=("occ", "asp")):
        """Evidence prose: house, sign, occupants, and aspects with functional tags."""
        parts = []
        if "occ" in cols:
            o = F._occupants(self.chart, h, P7)
            parts.append("Occupying " + (F._labelled(self.chart, o, self.sign(h)) if o else "—"))
        if "asp" in cols:
            a = F._classical_aspecting_house(self.chart, h)
            parts.append("Aspecting " + (F._labelled(self.chart, a, self.sign(h)) if a else "—"))
        return f"House {h} {self.sign(h)}: " + "; ".join(parts)


def _any(pairs, c):
    return any(k == c for _, k in pairs)


def _bm(pairs):
    return sum(k == "B" for _, k in pairs), sum(k == "M" for _, k in pairs)


def _half(f):
    """Dual signs: first half acts as fixed, second half as movable (P-II.1~2 note citing Bhattotpala)."""
    if f.lsign in FIX:
        return "fixed"
    if f.lsign in MOV:
        return "movable"
    return "fixed" if f.ldeg < 15 else "movable"


# ---------------------------------------------------------------------------
# Ledger Entry
# ---------------------------------------------------------------------------
@dataclass
class Entry:
    rule_id: str
    level: str  # A / B / B (Analogical) / B (Universal)
    reason: str  # Applicability justification
    direction: str
    evidence: str
    alt: str | None = None  # Secondary commentary direction for dual interpretations (rubric §2.4)
    note: str = ""
    houses: frozenset = frozenset()  # Houses evaluated when triggered (for contextual verification)
    excluded: str = ""  # Reason for exclusion (inapplicable context, etc.); scores 0 when non-empty

    @property
    def score(self):
        return 0 if self.excluded else score(self.direction)


# ---------------------------------------------------------------------------
# Classical Rules
# ---------------------------------------------------------------------------
def p_i3(f, h):
    """P-I.3: Matter house supported by own lord or benefics is strengthened, by malefics is afflicted."""
    pairs = [(n, k) for n, k in f.both(h) if not (k == "M" and n in f.needed)]
    b, m = _bm(pairs)
    skipped = [n for n, k in f.both(h) if k == "M" and n in f.needed]
    note = f"Required significator {', '.join(skipped)} not counted as malefic (contextual reading)" if skipped else ""
    return _d(b > 0, m > 0), f.text(h), note


def six_majority(f):
    good, bad, verdict = F._shadvarga_majority(f.chart, f.lsign, f.ldeg)
    return {"Benefic dominant": "B", "Malefic dominant": "M"}.get(verdict, "T"), f"Shadvarga lords Benefic {good} / Malefic {bad} ({verdict})"


def p_i4(f):
    """P-I.4: (1) Lagna occupied by benefics or falls in benefic varga (Shadvarga majority); (2) Shirshodaya sign."""
    occ = f.occ(1)
    v, vtext = six_majority(f)
    c1 = _d(_any(occ, "B") or v == "B", _any(occ, "M") or v == "M")
    c2 = "fav" if f.lsign in HEAD_I4 else "unf" if f.lsign in BACK_I4 else "mixed"
    ev = f"Lagna {f.lsign} {f.ldeg:.2f}° ({'Shirshodaya' if c2 == 'fav' else 'Prishtodaya' if c2 == 'unf' else 'Ubhayodaya'}); {f.text(1)}; {vtext}"
    if c1 == "fav" and c2 == "fav":
        return "fav", ev
    if c1 == "unf" and c2 == "unf":
        return "unf", ev
    b, m = _bm(f.both(1))
    return _count(b + (v == "B"), m + (v == "M")), ev


def p_iv1(f):
    """P-IV.1: Benefics in kendras/trikonas and malefics absent from kendras/8th house brings prosperity; contrary brings ruin."""
    good = any(_any(f.occ(h), "B") for h in KENDRA + TRIKONA)
    bad = any(_any(f.occ(h), "M") for h in KENDRA + (8,))
    ev = "; ".join(f.text(h, ("occ",)) for h in (1, 4, 7, 10, 5, 9, 8))
    return _d(good, bad) if good or bad else "none", ev


def p_iv3(f):
    """P-IV.3: Benefics in 10, 7 grant position; malefics in 12, 11 are unfavorable; waning Moon in Lagna is bad, Moon in 10 is good."""
    fav = _any(f.occ(7), "B") or any(k == "B" for n, k in f.occ(10) if n != "Moon") or f.house["Moon"] == 10
    unf = _any(f.occ(11), "M") or _any(f.occ(12), "M") or (f.house["Moon"] == 1 and not f.waxing)
    ev = "; ".join(f.text(h, ("occ",)) for h in (10, 7, 11, 12)) + f"; Moon in house {f.house['Moon']}, {'waxing' if f.waxing else 'waning'} Moon"
    return _d(fav, unf), ev


def p_iv3_fame(f):
    """P-IV.3 second half: Benefics in 2, 5, 1 grant wealth and fame."""
    fav = any(_any(f.occ(h), "B") for h in (2, 5, 1))
    return ("fav" if fav else "none"), "; ".join(f.text(h, ("occ",)) for h in (2, 5, 1))


II1_GOOD = {
    "position": "fixed", "residence": "fixed", "reputation": "fixed", "lost_property": "fixed",
    "illness": "movable", "travel": "movable", "return": "movable", "change": "movable"
}
II1_NOTE = {
    "position": "Fixed sign gains position, movable loses",
    "residence": "Fixed sign gains residence",
    "reputation": "Fixed sign preserves reputation, movable suffers dishonor",
    "lost_property": "Fixed sign temporarily misplaced/not lost, movable difficult to recover",
    "illness": "Fixed sign difficult to cure, movable easy to cure",
    "travel": "Movable sign trip materializes, fixed sign fails to depart",
    "return": "Movable sign traveler on the way (favorable); fixed sign does not return",
    "change": "Movable sign change materializes"
}


def p_ii1(f, kind):
    """P-II.1~2 note: Movable vs fixed sign modality; dual sign first half acts fixed, second half movable."""
    like = _half(f)
    ev = f"Lagna {f.lsign} {f.ldeg:.2f}° ({F._modality(f.lsign)}{', treated as ' + ('1st' if f.ldeg < 15 else '2nd') + ' half' if f.lsign not in MOV | FIX else ''})"
    return ("fav" if like == II1_GOOD[kind] else "unf"), ev, II1_NOTE[kind]


def p_ii2(f):
    """P-II.2: Benefics aspecting Lagna and Moon-lagna are auspicious, malefics inauspicious, mixed aspects balanced."""
    mh = f.house["Moon"]
    pairs = f.asp(1) + (f.asp(mh) if mh != 1 else [])
    b, m = _bm(pairs)
    return _d(b > 0, m > 0), f.text(1, ("asp",)) + ("" if mh == 1 else "; Moon-lagna " + f.text(mh, ("asp",)))


def p_ii5(f):
    """P-II.5: Movable Lagna with benefics favors travelers; with malefics harms them. Fixed Lagna with malefics still grants safe return."""
    occ = f.occ(1)
    if f.lsign in MOV:
        return _d(_any(occ, "B"), _any(occ, "M")), f.text(1, ("occ",))
    if f.lsign in FIX and _any(occ, "M"):
        return "fav", f.text(1, ("occ",))
    return "none", f.text(1, ("occ",))


def p_ii9(f):
    """P-II.9: Movable Lagna occupied by Sun/Saturn/Mercury/Venus indicates prompt departure; retrograde indicates otherwise.
    Dual commentary: Sun exempt from retrogradation check (reading 1), or Sun excluded overall (reading 2)."""
    if f.lsign not in MOV:
        return "none", "none", f"Lagna {f.lsign} not movable sign"
    def read(names):
        on = [n for n in names if f.house[n] == 1]
        if not on:
            return "none"
        return "unf" if all(f.chart["planets"][n].get("retrograde") for n in on) else "fav"
    on = [n for n in ("Sun", "Saturn", "Mercury", "Venus") if f.house[n] == 1]
    return read(("Sun", "Saturn", "Mercury", "Venus")), read(("Saturn", "Mercury", "Venus")), \
        f"Lagna {f.lsign} (movable); named planets occupying Lagna: {', '.join(on) or '—'}"


def p_ii11(f):
    """P-II.11: Sun and Moon in 4th house delay hearing; Mercury, Jupiter, and Venus in 4th hasten hearing."""
    on = {n for n in P7 if f.house[n] == 4}
    d = "unf" if {"Sun", "Moon"} <= on else "fav" if {"Mercury", "Jupiter", "Venus"} <= on else "none"
    return d, f.text(4, ("occ",))


def p_iii1(f):
    """P-III.1: Benefics in 10, 1, 7 bring victory; 9th house judged by functional role: malefics bring defeat, benefics victory."""
    fav = any(_any(f.occ(h), "B") for h in (10, 1, 7, 9))
    return _d(fav, _any(f.occ(9), "M")), "; ".join(f.text(h, ("occ",)) for h in (10, 1, 7, 9))


def p_iii34(f):
    """P-III.3~4: Human sign rising with benefics, benefics in 12/11/kendras, human Lagna aspected by benefics brings reconciliation."""
    human = f.lsign in HUMAN_III3
    fav = (human and _any(f.occ(1), "B")) or any(_any(f.occ(h), "B") for h in (11, 12) + KENDRA) \
        or (human and _any(f.asp(1), "B"))
    unf = any(f.sign(h) in MOV and _any(f.occ(h), "M") for h in range(1, 13)) \
        or any(_any(f.occ(h), "M") and _any(f.asp(h), "M") for h in KENDRA + (11, 12))
    ev = f"Lagna {f.lsign}{' (human sign)' if human else ''}; " + "; ".join(f.text(h) for h in (1, 4, 7, 10, 11, 12))
    used = frozenset(h for h in (11, 12) if _any(f.occ(h), "B"))
    if fav and unf:
        return _count(*_bm([x for h in KENDRA for x in f.both(h)])), ev, used
    return _d(fav, unf), ev, used


def p_iv2(f):
    """P-IV.2: Benefics in 3/5/11/7 bring gains, malefics losses; benefics in human signs (Libra, Gemini, Aquarius) also auspicious."""
    hs = (3, 5, 11, 7)
    fav = any(_any(f.both(h), "B") for h in hs) or any(k == "B" and f.chart["planets"][n]["sign"] in HUMAN_IV2
                                                      for h in range(1, 13) for n, k in f.occ(h))
    unf = any(_any(f.both(h), "M") for h in hs)
    return _d(fav, unf), "; ".join(f.text(h) for h in hs)


def p_iv5(f):
    """P-IV.5: Benefics in Lagna/7/8/5 mutually aspecting, Moon in 3/6/10/11 brings recovery; contrary configuration brings death."""
    hs = (1, 7, 8, 5)
    mg = f.house["Moon"] in (3, 6, 10, 11)
    occ = [x for h in hs for x in f.occ(h) if x[0] != "Moon"]
    ben = [n for n, k in occ if k == "B"]
    mutual = len(ben) >= 2 and all(f.mutual(a, b) for i, a in enumerate(ben) for b in ben[i + 1:])
    bo, mo = _any(occ, "B"), _any(occ, "M")
    ev = "; ".join(f.text(h) for h in hs) + f"; Moon in house {f.house['Moon']}"
    if bo and mutual and not mo and mg:
        return "fav", ev
    if mo and not bo and not mg:
        return "unf", ev
    b, m = _bm([x for h in hs for x in f.both(h)])
    return _count(b + mg, m + (not mg)), ev


def p_v1(f, person):
    """P-V.1: Planets in 5/2/3 indicate absentee returns; benefics in these houses indicate lost property recovered."""
    hs = (5, 2, 3)
    hit = any(f.occ(h) for h in hs) if person else any(_any(f.occ(h), "B") for h in hs)
    return ("fav" if hit else "none"), "; ".join(f.text(h, ("occ",)) for h in hs)


def p_v2(f):
    """P-V.2: House 7 or 6 occupied, Jupiter in kendra, Mercury/Venus in trikona: absentee returns.
    Dual commentary: either satisfied vs all satisfied."""
    conds = [bool(f.occ(7) or f.occ(6)), f.house["Jupiter"] in KENDRA,
             f.house["Mercury"] in TRIKONA or f.house["Venus"] in TRIKONA]
    ev = f"House 6/7 occupied: {'yes' if conds[0] else 'no'}; Jupiter in house {f.house['Jupiter']}; Mercury in {f.house['Mercury']}, Venus in {f.house['Venus']}"
    return ("fav" if any(conds) else "none"), ("fav" if all(conds) else "none"), ev


def p_v3(f):
    """P-V.3: Moon in 8th house and kendras free of malefics indicates safe return."""
    ok = f.house["Moon"] == 8 and f.basic["Moon"] != "debilitated" and not any(_any(f.occ(h), "M") for h in KENDRA)
    return ("fav" if ok else "none"), f"Moon in house {f.house['Moon']} ({f.basic['Moon']}); Kendras occupied by malefics: " \
        f"{'yes' if any(_any(f.occ(h), 'M') for h in KENDRA) else 'no'}", frozenset({8}) if ok else frozenset()


def p_iii5(f):
    """P-III.5: Jupiter or Venus in 2nd or 3rd from Lagna: distant person arrives quickly."""
    ok = f.house["Jupiter"] in (2, 3) or f.house["Venus"] in (2, 3)
    return ("fav" if ok else "none"), f"Jupiter in house {f.house['Jupiter']}; Venus in house {f.house['Venus']}"


def p_vi3(f):
    """P-VI.3: Full Moon or benefic in Lagna, Shirshodaya Lagna aspected by benefic, or strong benefic in 11th brings quick recovery."""
    strong11 = any(k == "B" and f.basic[n] in F.STRONG_BASIC for n, k in f.occ(11))
    fullwin = F.tithi_facts(f.chart["planets"]["Sun"]["longitude"], f.chart["planets"]["Moon"]["longitude"])[1]
    a = (fullwin and f.house["Moon"] == 1) or _any(f.occ(1), "B")
    rising = _any(f.asp(1), "B")
    read = lambda heads: "fav" if a or (f.lsign in heads and rising) or strong11 else "unf"
    ev = f"Lagna {f.lsign}; {f.text(1)}; Strong benefic in 11th: {'yes' if strong11 else 'no'}; Full Moon window: {'yes' if fullwin else 'no'}"
    alt = read(HEAD_VI3 | {"Gemini"}) if f.lsign == "Gemini" else None
    return read(HEAD_VI3), alt, ev


def p_vii1(f, asker):
    """P-VII.1: Saturn in odd house from Lagna (excl. Lagna) indicates bride, otherwise groom."""
    bride = f.house["Saturn"] in (3, 5, 7, 9, 11)
    return ("fav" if bride == (asker == "male") else "unf"), f"Saturn in house {f.house['Saturn']}"


def p_vii2(f):
    """P-VII.2: Moon in 3/5/7/11/6 aspected by benefics, or benefics in kendras/trikonas brings marriage."""
    mh = f.house["Moon"]
    a = mh in (3, 5, 7, 11, 6) and _any(f.asp(mh), "B")
    b = any(_any(f.occ(h), "B") for h in KENDRA + TRIKONA)
    return ("fav" if a or b else "unf"), f"Moon in house {mh}: " + f.text(mh, ("asp",)) + "; Benefics in kendras/trikonas: " + ("yes" if b else "no")


def chyuti(f):
    """P-I.2 Chyuti (Lagna): Movable sign aspected/occupied by own lord or benefics without malefics confirms change; fixed sign maintains status."""
    b, m = _bm(f.both(1))
    if f.lsign in MOV:
        d = "fav" if b and not m else "unf"
    elif f.lsign in FIX:
        d = "unf"
    else:
        d = "fav" if b > m else "unf" if m > b else "mixed"
    return d, f"Lagna {f.lsign} ({F._modality(f.lsign)}); {f.text(1)}"


def vriddhi(f):
    """P-I.2 Vriddhi (4th House): Supported by own lord or benefics without affliction brings prosperity."""
    b, m = _bm(f.both(4))
    return _d(b > 0, m > 0), f.text(4)


def pravasa(f):
    """P-I.2 Pravasa (10th House): Movable sign aspected by malefics materializes journey; aspected by benefics/own lord prevents it."""
    b, m = _bm(f.asp(10))
    return ("fav" if f.sign(10) in MOV and m and not b else "unf"), f.text(10, ("asp",))


def nivritti(f):
    """P-I.2 Nivritti (7th House): Movable sign aspected by own lord or benefics returns, by malefics does not."""
    if f.sign(7) not in MOV:
        return "none", f"House 7 {f.sign(7)} not movable sign"
    b, m = _bm(f.asp(7))
    return _d(b > 0, m > 0), f.text(7, ("asp",))


def return_4th(f):
    """P-I.2 Absentee return evaluated via 4th house. Dual commentary: text (planet in 4th) vs note (4th lord occupies/aspects 4th)."""
    lord = f.lord(4)
    a = "fav" if f.occ(4) else "none"
    b = "fav" if f.house[lord] == 4 or 4 in f.chart["graha_drishti"].get(lord, {}).get("aspected_houses", []) else "unf"
    return a, b, f.text(4) + f"; 4th lord {lord} in house {f.house[lord]}"


def x5(f):
    """M-XVII.5: Benefics in 7th house are auspicious."""
    return ("fav" if _any(f.occ(7), "B") else "none"), f.text(7, ("occ",))


def x15(f):
    """M-XVII.15: Afflicted Moon in even house and waning fails; Moon in 8th brings obstacles."""
    mh = f.house["Moon"]
    aff = any(k == "M" for n, k in f.occ(mh) if n != "Moon") or _any(f.asp(mh), "M")
    if mh == 8:
        return "unf", f"Moon in house 8", frozenset({8})
    d = "unf" if aff and mh % 2 == 0 and not f.waxing else "none"
    return d, f"Moon in house {mh} ({'even' if mh % 2 == 0 else 'odd'} house), {'afflicted' if aff else 'unafflicted'}, {'waxing' if f.waxing else 'waning'} Moon", frozenset()


def x16(f, with_link):
    """M-XVII.16: Lagna lord and 7th lord, or with Venus mutual exchange, exaltation, mutual aspect brings success.
    with_link=False: removes exchange/aspect already scored under Connection (D2), leaving exaltation and Venus."""
    l1, l7 = f.lord(1), f.lord(7)
    def swap(a, b):
        return f.chart["planets"][a]["sign"] in [s for s, q in F.SIGN_LORDS.items() if q == b] and \
            f.chart["planets"][b]["sign"] in [s for s, q in F.SIGN_LORDS.items() if q == a]
    ok, why = False, []
    for b in (l7, "Venus"):
        if b == l1:
            continue
        link = swap(l1, b) or f.mutual(l1, b)
        if link and (with_link or b == "Venus"):
            ok = True; why.append(f"{l1}–{b} mutual exchange or aspect")
        for p in (l1, b):
            if f.basic[p] == "exalted":
                ok = True; why.append(f"{p} exalted")
    return ("fav" if ok else "none"), f"Lagna lord {l1}, 7th lord {l7}: " + (", ".join(dict.fromkeys(why)) or "Condition not met")


def x17(f):
    """M-XVII.17: Afflicted malefic in 8th aspected by malefic and debilitated/enemy sign fails; in 6th fails via illness/strife."""
    for h in (8, 6):
        for n, k in f.occ(h):
            if k == "M" and f.basic[n] in ("debilitated", "enemy", "great_enemy") and _any(f.asp(h), "M"):
                return "unf", f.text(h) + f" ({n} {f.basic[n]})", frozenset({h})
    return "none", "No afflicted debilitated/enemy malefic in house 6 or 8", frozenset()


# ---------------------------------------------------------------------------
# Matter Registry (Maps 1:1 with matter-rules.md)
# ---------------------------------------------------------------------------
@dataclass
class Matter:
    house: int | None  # None = dynamically chosen from plan sheet (actor house for meeting, etc.)
    level: str
    rules: tuple
    has_i4: bool = False
    timing: str = "general"  # general / return / none


MATTERS = {
    "reconciliation": Matter(7, "B", ("III34*", "PI3")),
    "confession": Matter(7, "B", ("I4", "PI3", "X5*", "X15*", "X16*", "X17*"), has_i4=True),
    "resume_contact": Matter(7, "B", ("III34*", "PI3")),
    "meeting": Matter(None, "B", ("I4", "PI3"), has_i4=True),
    "win_back": Matter(1, "A", ("I4", "PI3"), has_i4=True),
    "cohabitation_return": Matter(7, "A", ("NIV", "R4", "V1P", "V2", "V3", "III5", "II1:return"), timing="return"),
    "marriage": Matter(7, "A", ("VII2", "VII1", "PI3", "X5", "X15", "X16", "X17")),
    "job_hunting": Matter(10, "A", ("IV3", "II1:position", "II2", "PI3")),
    "layoff": Matter(1, "A", ("CHY", "II1:change")),
    "competitive_exam": Matter(1, "B", ("II1:position", "II2", "III1", "PI3")),
    "threshold_exam": Matter(1, "A", ("I4", "PI3"), has_i4=True),
    "lost_property": Matter(11, "A", ("VI3", "V1O", "II1:lost_property", "PI3")),
    "stray_pet": Matter(11, "B", ("VI3", "V1O", "II1:lost_property", "PI3")),
    "property_purchase": Matter(4, "A", ("VRI", "II1:residence", "I4"), has_i4=True),
    "travel_materialization": Matter(1, "A", ("I4", "PI3"), has_i4=True),
    "journey_safety": Matter(1, "A", ("II5",), timing="none"),
    "departure": Matter(10, "A", ("PRA", "II1:travel")),
    "return": Matter(7, "A", ("V1P", "V2", "V3", "III5", "NIV", "R4", "II1:return"), timing="return"),
    "illness": Matter(1, "A", ("IV5", "II1:illness", "PI3")),
    "reputation": Matter(4, "A", ("VRI", "II1:reputation", "IV3F")),
    "negotiation": Matter(7, "A", ("III34", "PI3")),
    "investment": Matter(11, "B", ("IV2", "PI3")),
    "recover_losses": Matter(11, "B", ("V1O", "PI3")),
    "court_hearing": Matter(4, "B", ("II11", "PI3")),
    "cooperation": Matter(7, "B", ("PI3",)),
    "wealth": Matter(None, "B", ("PI3",)),
    "child_action": Matter(5, "B", ("PI3",)),
    "general": Matter(None, "B", ("PI3",)),
    "description": Matter(None, "B", (), timing="none"),
}
LOVE_EXTRA = ("X5*", "X15*", "X16*", "X17*")
ANALOGY = {"III34*", "X5*", "X15*", "X16*", "X17*"}
RULE_NAMES = {
    "PI3": "P-I.3", "I4": "P-I.4", "II1": "P-II.1", "IV1": "P-IV.1", "IV3": "P-IV.3", "IV3F": "P-IV.3 (Houses 2/5/1)",
    "II2": "P-II.2", "II5": "P-II.5", "II9": "P-II.9", "II11": "P-II.11", "III1": "P-III.1", "III34": "P-III.3~4",
    "III5": "P-III.5", "IV2": "P-IV.2", "IV5": "P-IV.5", "V1P": "P-V.1", "V1O": "P-V.1", "V2": "P-V.2", "V3": "P-V.3",
    "VI3": "P-VI.3", "VII1": "P-VII.1", "VII2": "P-VII.2", "CHY": "P-I.2 Chyuti", "VRI": "P-I.2 Vriddhi",
    "PRA": "P-I.2 Pravasa", "NIV": "P-I.2 Nivritti", "R4": "P-I.2 Return 4th House", "X5": "M-XVII.5", "X15": "M-XVII.15",
    "X16": "M-XVII.16", "X17": "M-XVII.17", "S4": "M-XIV.43",
}


# ---------------------------------------------------------------------------
# Intake Plan
# ---------------------------------------------------------------------------
@dataclass
class Plan:
    """Model-generated intake plan sheet (`question-decomposition.md` §7)."""
    matter: str
    matter_house: int | None = None
    context: str = ""  # "love": meeting query adds M-XVII 4 verses
    actor: int | None = None  # Actor house for action-oriented queries
    needed_planets: tuple = ()  # Contextually required significators for event success
    keywords: tuple = ()  # ({"word", "houses", "planets", "polarity", "source"}, ...)
    qualifiers: tuple = ()  # ("private", "public", "at_home", "away", "initiative", or keyword word, ...)
    location: str = "city"  # city / exact (sensitivity audit window)
    asker: str = ""  # Marriage query: male / female
    direction: str = "occur"  # occur / prevent (for layoffs: "will layoff occur" vs "can job be retained")
    early_departure: bool = False  # Departure query asking if early departure can occur
    time_scope: dict | None = None  # Time scope bounds (does not alter judgment)

    @classmethod
    def from_dict(cls, d):
        p = cls(**{k: (tuple(v) if isinstance(v, list) else v) for k, v in d.items()})
        p.validate()
        return p

    def validate(self):
        if self.matter not in MATTERS:
            raise ValueError(f"Plan matter not in registry: {self.matter}; custom queries use 'general' with matter_house")
        if MATTERS[self.matter].house is None and not self.house_of_matter():
            raise ValueError(f"{self.matter} requires matter_house (or actor house)")
        fixed = MATTERS[self.matter].house
        if fixed is not None and self.matter_house not in (None, fixed):
            raise ValueError(f"{self.matter} has fixed matter house {fixed}, cannot accept matter_house={self.matter_house}; "
                             "for third-party or derived houses, use 'general' with projected matter_house")
        bad = [p for p in self.needed_planets if p not in P7]
        if bad:
            raise ValueError(f"needed_planets accepts classical 7 planets only: {bad}")
        for k in self.keywords:
            if k.get("polarity") not in ("aligned", "opposite"):
                raise ValueError(f"Keyword {k.get('word')} polarity must be 'aligned' or 'opposite'")
            if not k.get("source"):
                raise ValueError(f"Keyword {k.get('word')} missing classical source citation")
        if self.matter == "marriage" and self.asker not in ("male", "female"):
            raise ValueError("Marriage query requires asker ('male' or 'female')")
        if self.matter == "description" and self.qualifiers:
            raise ValueError("Descriptive queries do not evaluate qualifiers")
        if "initiative" in self.qualifiers and not self.actor:
            raise ValueError("Qualifier 'initiative' requires actor house")
        if self.location not in ("city", "exact"):
            raise ValueError("location must be 'city' or 'exact'")
        ts = self.time_scope
        if ts is not None:
            if not isinstance(ts, dict) or ts.get("kind") not in ("range", "meaningless", "unlimited"):
                raise ValueError("time_scope.kind must be 'range', 'meaningless', or 'unlimited'")
            if ts["kind"] == "range":
                if not ts.get("label"):
                    raise ValueError("time_scope 'range' requires label")
                try:
                    date.fromisoformat(str(ts.get("until")))
                except ValueError:
                    raise ValueError("time_scope 'range' requires until (YYYY-MM-DD)") from None

    def house_of_matter(self):
        """Fixed registry house takes precedence; matter_house for variable topics."""
        return MATTERS[self.matter].house or self.matter_house or self.actor

    def role_houses(self):
        """Houses explicitly identified with aligned polarity in keywords."""
        return {h for k in self.keywords if k["polarity"] == "aligned" for h in k.get("houses", ())}


# ---------------------------------------------------------------------------
# Success Ledger Construction
# ---------------------------------------------------------------------------
@dataclass
class Options:
    d2_link: bool = True  # Connection entered into ledger (S4)
    d3_need: bool = True  # Contextual reading of P-I.3 and ability layer
    d4_context: bool = True  # Contextual verification of analogical verses


def _entry(code, f, plan, h, opts):
    """Generate a single ledger entry from a rule code."""
    base = code.rstrip("*")
    kind = code.split(":")[1] if ":" in code else ""
    level = "B (Analogical)" if code in ANALOGY else MATTERS[plan.matter].level
    name = RULE_NAMES.get(base.split(":")[0], base)
    houses, alt, note = frozenset(), None, ""
    if base == "PI3":
        d, ev, note = p_i3(f, h)
        reason = f"Matter house {h} support / affliction"
    elif base == "I4":
        d, ev = p_i4(f); reason = "General accomplishment of desired object"
    elif base == "IV3":
        d, ev = p_iv3(f); reason = "Position (10/7 benefics; 11/12 malefics; Moon)"
    elif base == "IV3F":
        d, ev = p_iv3_fame(f); reason = "Wealth and fame (2/5/1 benefics)"
    elif base.startswith("II1"):
        d, ev, note = p_ii1(f, kind); reason = f"Movable/fixed sign ({kind})"
        if kind == "change" and plan.direction == "prevent":
            d = {"fav": "unf", "unf": "fav"}.get(d, d); note += "; Asking to retain, inverted direction"
    elif base == "II2":
        d, ev = p_ii2(f); reason = "Benefic/malefic aspects to Lagna and Moon-lagna"
    elif base == "II5":
        d, ev = p_ii5(f); reason = "Safety on the journey"
    elif base == "II9":
        d, alt, ev = p_ii9(f); reason = "Early departure"; note = "Dual commentary: Sun included or not" if alt != d else ""
    elif base == "II11":
        d, ev = p_ii11(f); reason = "Speed of court hearing (by named planets)"
    elif base == "III1":
        d, ev = p_iii1(f); reason = "Victory in competition"
    elif base == "III34":
        d, ev, houses = p_iii34(f); reason = "Reconciliation (royal peace treaties, extended by Ayer to settlement of scores)"
    elif base == "III5":
        d, ev = p_iii5(f); reason = "Absentee returns quickly (by named planets)"
    elif base == "IV2":
        d, ev = p_iv2(f); reason = "Investment gain/loss"
    elif base == "IV5":
        d, ev = p_iv5(f); reason = "Recovery from illness"
    elif base == "V1P":
        d, ev = p_v1(f, True); reason = "Absentee returns (planets in 5/2/3)"
    elif base == "V1O":
        d, ev = p_v1(f, False); reason = "Lost property recovered (benefics in 5/2/3)"
    elif base == "V2":
        d, alt, ev = p_v2(f); reason = "Absentee returns (6/7 occupied, Jupiter kendra, Mercury/Venus trikona)"
        note = "Dual commentary: either vs all" if alt != d else ""
    elif base == "V3":
        d, ev, houses = p_v3(f); reason = "Moon in 8th house returns safely"
    elif base == "VI3":
        d, alt, ev = p_vi3(f); reason = "Lost property recovery speed"; note = "Dual commentary: Gemini Shirshodaya" if alt not in (None, d) else ""
    elif base == "VII1":
        d, ev = p_vii1(f, plan.asker); reason = f"Gains bride or groom ({plan.asker} asking)"
    elif base == "VII2":
        d, ev = p_vii2(f); reason = "Marriage negotiation success"
    elif base == "CHY":
        d, ev = chyuti(f); reason = "Change (layoff, transfer, job change)"
        if plan.direction == "prevent":
            d = {"fav": "unf", "unf": "fav"}.get(d, d); note = "Asking to retain, inverted direction"
    elif base == "VRI":
        d, ev = vriddhi(f); reason = "Prosperity (4th house)"
    elif base == "PRA":
        d, ev = pravasa(f); reason = "Departure (10th house)"
    elif base == "NIV":
        d, ev = nivritti(f); reason = "Return (7th house)"
    elif base == "R4":
        d, alt, ev = return_4th(f); reason = "Absentee return 4th house"; note = "Dual commentary: text vs note" if alt != d else ""
    elif base == "X5":
        d, ev = x5(f); reason = "Benefics in 7th house are auspicious"
    elif base == "X15":
        d, ev, houses = x15(f); reason = "Afflicted Moon in even house and waning, or in 8th house"
    elif base == "X16":
        d, ev = x16(f, with_link=not opts.d2_link); reason = "Lagna lord and 7th lord or Venus mutual exchange, exaltation, aspect"
        if opts.d2_link:
            note = "Mutual exchange/aspect absorbed into M-XIV.43 connection entry"
    elif base == "X17":
        d, ev, houses = x17(f); reason = "Afflicted malefics in 8th or 6th house"
    else:
        raise KeyError(code)
    if alt == d:
        alt = None
    e = Entry(name, level, reason, d, ev, alt=alt, note=note, houses=houses)
    if opts.d4_context and code in ANALOGY and score(d) != 0:
        clash = (houses - {1, h}) & plan.role_houses()
        if clash:
            e.excluded = f"Inapplicable context: house(s) {', '.join(map(str, sorted(clash)))} evaluated by this verse have distinct query role"
    return e


def link_entry(f, h):
    """S4 Connection (M-XIV.43, D2): Lagna lord conjoined, aspecting, mutual exchange, or mutual 4/10 with matter lord is favorable."""
    l1, lm = f.lord(1), f.lord(h)
    if h == 1 or l1 == lm:
        return None
    kinds = F._relation(f.chart, l1, lm)
    return Entry("M-XIV.43", "B (Universal)", f"Connection between matter lord and Lagna lord (House {h} lord {lm})",
                 "fav" if kinds else "none", f"{l1}–{lm}: {', '.join(kinds) or 'None'}")


def build_ledger(chart, plan, opts=Options()):
    f = Facts(chart, plan.needed_planets if opts.d3_need else ())
    m = MATTERS[plan.matter]
    h = plan.house_of_matter()
    codes = list(m.rules)
    if plan.matter == "meeting" and plan.context == "love":
        codes += list(LOVE_EXTRA)
    if plan.matter == "departure" and plan.early_departure:
        codes.append("II9")
    entries = [_entry(c, f, plan, h, opts) for c in codes]
    if not m.has_i4:
        d, ev = p_i4(f)
        entries.append(Entry("P-I.4", "B (Universal)", "General accomplishment of desired object", d, ev))
    d, ev = p_iv1(f)
    entries.append(Entry("P-IV.1", "B (Universal)", "Global kendra/trikona benefic/malefic disposition (omnibus solution)", d, ev))
    if opts.d2_link:
        e = link_entry(f, h)
        if e:
            entries.append(e)
    return entries


def _tier(entries, reading=0):
    """reading=0 uses primary reading; reading=1 uses secondary commentary for dual views."""
    dirs = [(e.alt if reading and e.alt else e.direction) for e in entries if not e.excluded]
    s = sum(score(x) for x in dirs)
    nz = [x for x in dirs if score(x)]
    if not nz and "mixed" not in dirs:
        return "Balanced", "Chart Gives No Direction", 0
    if s == 0:
        return "Balanced", "Evenly Balanced", 0
    pos, neg = any(score(x) > 0 for x in dirs), any(score(x) < 0 for x in dirs)
    if len(nz) == 1:
        return ("Favorable" if s > 0 else "Unfavorable"), "Single Evidence", s
    if s > 0:
        return "Favorable", "With Resistance" if neg else "Smooth", s
    return "Unfavorable", "With Turning Points" if pos else "Definite", s


# ---------------------------------------------------------------------------
# Ability Layer (Rubric §2.1)
# ---------------------------------------------------------------------------
def ability(chart, house, plan, opts=Options()):
    """Formatter ability table verdict with contextual deductions applied."""
    planet, factors, rescue, verdict = F._lord_ability(chart, house)
    out, dropped = [], []
    needed = set(plan.needed_planets) if opts.d3_need else set()
    roles = plan.role_houses() if opts.d3_need else set()
    for x in factors:
        if x.startswith("Aspected/occupied by malefic ("):
            names = [n for n in x[len("Aspected/occupied by malefic ("):x.index(")")].split(", ") if n not in needed]
            if not names:
                dropped.append(x + " (required significator, converted to supply)"); continue
            if len(names) < len(x[len("Aspected/occupied by malefic ("):x.index(")")].split(", ")):
                x = f"Aspected/occupied by malefic ({', '.join(names)}), no benefic"
        if x.startswith("Placed in house ") and int(x[len("Placed in house "):]) in roles:
            dropped.append(x + " (contextually identified house, matched indication)"); continue
        out.append(x)
    if len(out) >= 3 or (len(out) == 2 and not rescue):
        v = "Severely Afflicted"
    elif out:
        v = "Compromised Capacity"
    else:
        v = "Strong" if {"Exalted", "Own sign", "Natural friend sign"} & set(rescue) else "Normal"
    return {"house": house, "planet": planet, "factors": out, "dropped": dropped, "rescue": rescue,
            "verdict": v, "formatter_verdict": verdict}


# ---------------------------------------------------------------------------
# Qualifiers (Rubric §2.3; house-meanings §4)
# ---------------------------------------------------------------------------
WATERY = {"Cancer", "Scorpio", "Pisces", "Capricorn"}


def hidden_or_public(chart, h, context):
    """Hidden vs public qualifier: 1. XXVIII.19 in romance context; 2. Placement in 10th (public) or 4/8/12 (private); 3. Hemispheres."""
    f = Facts(chart)
    steps = []
    planets = chart["planets"]
    lord = f.lord(h)
    if context == "love":
        moon, saturn = "Moon", "Saturn"
        dark = (planets[moon]["sign"] in ("Capricorn", "Aquarius") or f.sees(saturn, moon)
                or f.house[moon] == f.house[saturn] or f.house[moon] == 4 or planets[moon]["sign"] in WATERY)
        lit = f.sees("Sun", moon) or f.house["Sun"] == f.house[moon]
        steps.append(("M-XXVIII.19", "public" if lit else "private" if dark else None,
                      f"Moon in {planets[moon]['sign']} house {f.house[moon]}; Saturn {'aspects' if f.sees(saturn, moon) else 'does not aspect'} Moon; "
                      f"Sun {'aspects/conjoins Moon' if lit else 'does not aspect/conjoin Moon'}"))
    where = f.house[lord]
    if where == 10 or where in (4, 8, 12):
        s2 = "public" if where == 10 else "private"
        basis = f"Significator {lord} placed in house {where} -> {s2}"
    else:
        pub = f.lord(10) != lord and bool(F._relation(chart, lord, f.lord(10)))
        priv_h = [x for x in (4, 8, 12) if f.lord(x) != lord and F._relation(chart, lord, f.lord(x))]
        s2 = "public" if pub and not priv_h else "private" if priv_h and not pub else None
        basis = f"Significator {lord} placed in house {where}; connection to 10th lord: {'yes' if pub else 'no'}; connection to houses {', '.join(map(str, priv_h)) or '—'} lords"
    steps.append(("M-XIV.47; House Meanings", s2, basis))
    steps.append(("M-XIV.118–120", "public" if f.house[lord] >= 7 else "private", f"Significator placed in house {f.house[lord]}"))
    decided = next((s for s in steps if s[1]), steps[-1])
    return decided[1], steps


def at_home(chart):
    """XXVIII.5: Planets aspecting Lagna in own sign = at home; in another's sign = away."""
    f = Facts(chart)
    hits = F._classical_aspecting_house(chart, 1)
    own = [n for n in hits if F.SIGN_LORDS[chart["planets"][n]["sign"]] == n]
    other = [n for n in hits if n not in own]
    res = "at_home" if own and not other else "away" if other and not own else ("dual" if own else None)
    return res, f"Aspecting Lagna: own sign {', '.join(own) or '—'}; other sign {', '.join(other) or '—'}"


def keyword_qualifier(chart, h, kw):
    """Generic qualifier verification."""
    f = Facts(chart)
    lord = f.lord(h)
    links = []
    for x in kw.get("houses", ()):
        if f.house[lord] == x:
            links.append(f"Significator placed in house {x}")
        elif f.lord(x) != lord and F._relation(chart, lord, f.lord(x)):
            links.append(f"{lord}–{f.lord(x)} (House {x} lord): {', '.join(F._relation(chart, lord, f.lord(x)))}")
    for p in kw.get("planets", ()):
        if p != lord and F._relation(chart, lord, p):
            links.append(f"{lord}–{p}: {', '.join(F._relation(chart, lord, p))}")
    if not links:
        return "Not Established", "No connection"
    weak = [x for x in kw.get("houses", ()) if F._lord_ability(chart, x)[3] == "Severely Afflicted"]
    return ("Established but Weak" if weak else "Established"), "; ".join(links) + (f"; House {', '.join(map(str, weak))} lord Severely Afflicted" if weak else "")


def qualifiers(chart, plan, chain):
    h = plan.house_of_matter()
    out = []
    kws = {k["word"]: k for k in plan.keywords}
    for q in plan.qualifiers:
        if q in ("private", "public"):
            res, steps = hidden_or_public(chart, h, plan.context)
            out.append({"name": q, "result": "Established" if res == q else "Not Established",
                        "basis": "; ".join(f"{s[0]}: {s[2]} -> {s[1] or 'undecided'}" for s in steps)})
        elif q in ("at_home", "away"):
            res, ev = at_home(chart)
            out.append({"name": q, "result": "Established" if res == q else "Dual Commentary" if res == "dual" else "Not Established", "basis": ev})
        elif q == "initiative":
            v = chain["verdict"] if chain else None
            r = {"Favorable (Action Expected)": "Established", "Favorable (Arrested in Thought/Speech)": "Established", "Willing but Incapacitated": "Established but Weak"}.get(v, "Not Established")
            out.append({"name": q, "result": r, "basis": f"Action chain (Actor house {plan.actor}): {v}"})
        elif q in kws:
            r, ev = keyword_qualifier(chart, h, kws[q])
            out.append({"name": q, "result": r, "basis": ev})
        else:
            raise ValueError(f"Qualifier {q} is neither built-in ('private', 'public', 'at_home', 'away', 'initiative') nor in keywords")
    return out


# ---------------------------------------------------------------------------
# Judgment Engine
# ---------------------------------------------------------------------------
def action_chain(chart, actor):
    start, move, point, weak, verdict = F._action_chain(chart, actor)
    return {"actor": actor, "start": start, "move": move, "point": point, "weak": weak, "verdict": verdict}


def _core(chart, plan, opts):
    """Construct ledger, ability layer, and tiers (including dual commentary and vetoes)."""
    entries = build_ledger(chart, plan, opts)
    ab = ability(chart, plan.house_of_matter(), plan, opts)
    tier, strength, total = _tier(entries)
    branches = []
    if any(e.alt for e in entries if not e.excluded):
        t2 = _tier(entries, 1)
        if t2[:2] != (tier, strength):
            branches = [f"{tier} · {strength}", f"{t2[0]} · {t2[1]}"]
            tier, strength = "Balanced", "Dual Commentary"
    if ab["verdict"] == "Severely Afflicted":
        tier, strength = "Unfavorable", "Incapacitated"
    return entries, ab, tier, strength, total, branches


# ---------------------------------------------------------------------------
# Descriptive Matter Evaluation
# ---------------------------------------------------------------------------
def influences(chart, plan, h):
    """Itemize all planets conjoined with or aspecting the matter house and significator placement."""
    f = Facts(chart)
    lord = f.lord(h)
    places = [(h, f"House {h}")]
    if f.house[lord] != h:
        places.append((f.house[lord], f"Significator {lord} placed in house {f.house[lord]}"))
    rows = []
    for x, at in places:
        for how, names in (("Same house", F._occupants(chart, x, P7 + F.NODES)), ("Aspecting", F._classical_aspecting_house(chart, x))):
            for n in names:
                if n == lord:
                    continue
                rules = sorted(F._houses_ruled_from(n, f.lsign)) if n in P7 else []
                hits = [f"{k['word']} ({k['polarity']})" for k in plan.keywords
                        if n in k.get("planets", ()) or set(rules) & set(k.get("houses", ()))]
                rows.append({"at": at, "how": how, "planet": n, "rules": rules,
                             "label": F._ayer_role(chart, n, f.sign(x)) if n in P7 else "No Tag",
                             "dignity": f.basic.get(n, "—"), "combust": n in chart.get("combustion", {}),
                             "retro": n in P7 and bool(chart["planets"][n].get("retrograde")),
                             "hits": hits or ["None"]})
    return rows


def quarrel_117(chart):
    """M-XIV.117: Moon or Venus conjoined with malefic in 7th or 4th house indicates strife with women."""
    f = Facts(chart)
    hits = []
    for x in (4, 7):
        occ = dict(f.occ(x))
        bad = [n for n, k in occ.items() if k == "M" and n not in ("Moon", "Venus")]
        who = [n for n in ("Moon", "Venus") if n in occ]
        if who and bad:
            hits.append(f"{', '.join(who)} and {', '.join(bad)} conjoined in house {x}")
    return ("Established", "; ".join(hits)) if hits else ("Not Established", "No Moon/Venus conjoined with malefic in house 4 or 7")


def describe(chart, plan):
    h = plan.house_of_matter()
    f = Facts(chart)
    l1, lm = f.lord(1), f.lord(h)
    link = "Lagna lord itself" if l1 == lm else ", ".join(F._relation(chart, l1, lm)) or "None"
    return {
        "matter": "description", "matter_house": h, "level": "B", "ledger": [], "sum": 0,
        "tier": "Description", "strength": "No Tier", "branches": [], "sensitive": [],
        "ability": ability(chart, h, plan), "chain": action_chain(chart, plan.actor) if plan.actor else None,
        "qualifiers": [], "condition_failed": [], "timing": "none",
        "describe": {"link": f"{l1}–{lm}: {link}", "influences": influences(chart, plan, h),
                     "keywords": [dict(zip(("word", "result", "basis"), (k["word"], *keyword_qualifier(chart, h, k))))
                                  for k in plan.keywords],
                     "M-XIV.117": dict(zip(("result", "basis"), quarrel_117(chart)))},
    }


def _signature(entries, ab):
    return [(e.rule_id, e.direction, e.alt, bool(e.excluded)) for e in entries], ab["verdict"] == "Severely Afflicted"


def judge(chart, plan, opts=Options(), variants=()):
    """Judge a Prashna chart. Internal outcome tiers determined exclusively from given asking instant."""
    if plan.matter == "description":
        return describe(chart, plan)
    entries, ab, tier, strength, total, branches = _core(chart, plan, opts)
    base = _signature(entries, ab)
    sensitive = []
    for label, vc in variants:
        ve, vab, vt, vs, _, _ = _core(vc, plan, opts)
        if base[1] and vab["verdict"] == "Severely Afflicted":
            continue
        if _signature(ve, vab) != base:
            names = {e.rule_id for e in entries} | {e.rule_id for e in ve}
            changed = sorted(n for n in names
                             if [(e.direction, e.alt, bool(e.excluded)) for e in entries if e.rule_id == n]
                             != [(e.direction, e.alt, bool(e.excluded)) for e in ve if e.rule_id == n])
            if (vab["verdict"] == "Severely Afflicted") != (ab["verdict"] == "Severely Afflicted"):
                changed.append("Ability Veto")
            sensitive.append({"at": label, "rules": changed, "tier": f"{vt} · {vs}"})
    chain = action_chain(chart, plan.actor) if plan.actor else None
    m = MATTERS[plan.matter]
    qs = qualifiers(chart, plan, chain)
    failed = [q["name"] for q in qs if q["result"] == "Not Established"]
    return {
        "matter": plan.matter, "matter_house": plan.house_of_matter(), "level": m.level,
        "ledger": [e.__dict__ | {"score": e.score, "houses": sorted(e.houses)} for e in entries],
        "sum": total, "tier": tier, "strength": strength, "branches": branches, "sensitive": sensitive,
        "ability": ab, "chain": chain, "qualifiers": qs, "condition_failed": failed,
        "timing": "none" if tier == "Unfavorable" or strength == "Chart Gives No Direction" or m.timing == "none" or failed
        else m.timing,
    }
