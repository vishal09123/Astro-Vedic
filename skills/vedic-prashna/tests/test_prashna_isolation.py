"""
Prashna isolation regression test: ensures sandboxed architectural boundaries are preserved.
Seven isolation assertions + timing sub-layer test cases + standard layer test cases.
Must pass 100% green before any release.

Corresponds to SKILL.md and resources/timing-layer.md.
"""
import os
import re
import sys
from pathlib import Path

SKILLS_ROOT = Path(os.environ.get("VEDIC_SKILLS_ROOT") or Path(__file__).resolve().parents[2])
PRASHNA_ROOT = SKILLS_ROOT / "vedic-prashna"


# ---------------------------------------------------------------------------
# Assertion 1: Shared engine.py / formatter.py outputs contain no alien keys
# ---------------------------------------------------------------------------
FORBIDDEN_ENGINE_KEYS = [
    "tajika",
    "ithasala",
    "kp_",
    "sub_lord",
    "sublord",
    "void_of_course",
    "kambula",
    "kamboola",
    "ishraga",
    "muthashila",
    "manau",
]


def test_engine_no_alien_fields() -> None:
    hits = []
    for fname in ("engine.py", "formatter.py"):
        path = SKILLS_ROOT / "vedic-calculator" / "scripts" / fname
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for key in FORBIDDEN_ENGINE_KEYS:
            if key in text:
                hits.append(f"{fname}: {key}")
    assert not hits, (
        "RED: Shared engine output contains foreign astrology system keys — violates boundary #1.\n"
        f"Hits: {hits}"
    )


# ---------------------------------------------------------------------------
# Assertion 2: Main system skill rule files contain no Prashna foreign terms
# ---------------------------------------------------------------------------
GUARDED_SKILLS = [
    "vedic-core",
    "vedic-core-pro",
    "vedic-love",
    "vedic-career",
    "vedic-synastry",
    "vedic-rectifier",
    "vedic-reader",
]

FORBIDDEN_TERMS = [
    "prashna",
    "tajika",
    "ithasala",
    "sub-lord",
    "sub_lord",
    "sublord",
    "chandra kriya",
]


def test_shared_rules_no_prashna_terms() -> None:
    offenders = []
    for skill in GUARDED_SKILLS:
        skill_root = SKILLS_ROOT / skill
        if not skill_root.exists():
            continue
        for path in skill_root.rglob("*.md"):
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for term in FORBIDDEN_TERMS:
                if term in text:
                    rel = path.relative_to(SKILLS_ROOT)
                    offenders.append(f"{rel}: '{term}'")
    assert not offenders, (
        "RED: Main system skill files contain Prashna/alien terminology — violates boundary #2.\n"
        f"Hits:\n  " + "\n  ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Assertion 3: Prashna outputs are physically isolated
# ---------------------------------------------------------------------------
def test_prashna_products_in_isolated_dir() -> None:
    build_script = PRASHNA_ROOT / "scripts" / "build_prashna_data.py"
    if not build_script.exists():
        return

    text = build_script.read_text(encoding="utf-8", errors="ignore")
    code = re.sub(r'"""[\s\S]*?"""', '', text)
    code = re.sub(r"'''[\s\S]*?'''", '', code)
    code = re.sub(r'#[^\n]*', '', code)

    assert "prashna_" in code, (
        "RED: build_prashna_data.py does not contain 'prashna_' isolated directory prefix — violates boundary #3."
    )

    assert "structured_prashna.md" in code, (
        "RED: build_prashna_data.py does not contain 'structured_prashna.md' — violates boundary #3."
    )

    forbidden_writes = re.findall(r"structured_data\.md", code)
    assert not forbidden_writes, (
        "RED: build_prashna_data.py references structured_data.md — violates boundary #3."
    )


# ---------------------------------------------------------------------------
# Assertion 4: Main system scripts must not reverse import Prashna modules
# ---------------------------------------------------------------------------
PRASHNA_SANDBOX_MODULES = [
    "calc_moon_vedic",
    "calc_optional_tajika",
    "calc_optional_kp",
    "calc_timing",
    "build_prashna_data",
    "build_timing_overlay",
    "vedic_prashna",
]


def test_no_reverse_import_from_prashna() -> None:
    guarded_skills = [
        "vedic-core", "vedic-core-pro", "vedic-love", "vedic-career",
        "vedic-synastry", "vedic-rectifier", "vedic-reader", "vedic-calculator",
    ]
    offenders = []
    for skill in guarded_skills:
        skill_root = SKILLS_ROOT / skill
        if not skill_root.exists():
            continue
        for path in skill_root.rglob("*.py"):
            if "__pycache__" in str(path):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for mod in PRASHNA_SANDBOX_MODULES:
                pattern = rf"^\s*(?:from\s+{re.escape(mod)}\b|import\s+{re.escape(mod)}\b)"
                if re.search(pattern, text, re.MULTILINE):
                    rel = path.relative_to(SKILLS_ROOT)
                    offenders.append(f"{rel}: import '{mod}'")
            if "vedic-prashna" in text and re.search(r"sys\.path|import", text):
                for line in text.split("\n"):
                    line_lower = line.lower()
                    if "vedic-prashna" in line_lower and (
                        "sys.path" in line_lower or "importlib" in line_lower
                    ):
                        rel = path.relative_to(SKILLS_ROOT)
                        offenders.append(f"{rel}: sys.path/importlib refers 'vedic-prashna'")
                        break
    assert not offenders, (
        "RED: Main system skill scripts reverse import Prashna sandbox modules — violates boundary #4.\n"
        f"Hits:\n  " + "\n  ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Assertions 5, 6, 7: Timing sub-layer, standard layer, Tajika, KP isolation
# ---------------------------------------------------------------------------
def _imports(path: Path, modules) -> list:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [
        f"{path.name}: import '{mod}'"
        for mod in modules
        if re.search(
            rf"^\s*(?:from\s+{re.escape(mod)}\b|import\s+{re.escape(mod)}\b)",
            text, re.MULTILINE,
        )
    ]


def test_standard_builder_no_timing_import() -> None:
    offenders = []
    for name in ("build_prashna_data.py", "format_prashna_standard.py",
                 "calc_moon_vedic.py", "prashna_time.py"):
        offenders += _imports(PRASHNA_ROOT / "scripts" / name,
                              ("calc_timing", "build_timing_overlay"))
    assert not offenders, (
        "RED: Standard layer script imports timing sub-layer — timing runs independently.\n"
        f"Hits:\n  " + "\n  ".join(offenders)
    )


def test_standard_builder_no_optional_stack_import() -> None:
    offenders = []
    for name in ("build_prashna_data.py", "format_prashna_standard.py",
                 "calc_moon_vedic.py", "prashna_time.py"):
        offenders += _imports(PRASHNA_ROOT / "scripts" / name,
                              ("calc_optional_tajika", "calc_optional_kp",
                               "build_tajika_overlay", "build_kp_horary"))
    for name in ("calc_optional_tajika.py", "build_tajika_overlay.py"):
        offenders += _imports(PRASHNA_ROOT / "scripts" / name,
                              ("calc_optional_kp", "build_kp_horary"))
    for name in ("calc_optional_kp.py", "build_kp_horary.py"):
        offenders += _imports(PRASHNA_ROOT / "scripts" / name,
                              ("calc_optional_tajika", "build_tajika_overlay",
                               "format_prashna_standard", "calc_moon_vedic"))
    assert not offenders, (
        "RED: Standard layer imports Tajika/KP or Tajika/KP cross-import — optional stacks run isolated.\n"
        f"Hits:\n  " + "\n  ".join(offenders)
    )


def test_timing_no_optional_stack_import() -> None:
    offenders = []
    for name in ("calc_timing.py", "build_timing_overlay.py"):
        offenders += _imports(PRASHNA_ROOT / "scripts" / name,
                              ("calc_optional_tajika", "calc_optional_kp",
                               "build_tajika_overlay", "build_kp_horary"))
    assert not offenders, (
        "RED: Timing sub-layer imports Tajika/KP.\n"
        f"Hits:\n  " + "\n  ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Worked Example: Timing sub-layer Raman commentary & Moon entry search
# ---------------------------------------------------------------------------
def test_timing_worked_examples() -> None:
    scripts = str(PRASHNA_ROOT / "scripts")
    if not (PRASHNA_ROOT / "scripts" / "calc_timing.py").exists():
        return
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import calc_timing as ct

    # M-XIV.82 Raman commentary: rising Navamsa is Leo, Sun in 5th Navamsa -> 5 * 6 = 30 months
    t4 = ct.t4_navamsa_lord_period("Sun", 14.0)
    assert (t4["navamsa_ordinal"], t4["value"], t4["unit"]) == (5, 30, "months"), t4
    assert ct.navamsa_ordinal(0.0) == 1 and ct.navamsa_ordinal(29.99) == 9

    # M-XIV.85 Raman commentary: 7th lord Sun in 6th house (invisible hemisphere), inclusive span 12 -> 12 months
    t2 = ct.t2_house_lord_count(7, "Sun", 6)
    assert (t2["count"], t2["unit"]) == (12, "months"), t2
    assert ct.t2_house_lord_count(7, "Moon", 9)["unit"] == "days"

    # P-V.5: Planets in Lagna count as 1; Rahu/Ketu excluded
    assert ct.t1_return_days({"Rahu": 1, "Saturn": 3, "Sun": 5})["days"] == 36
    assert ct.t1_return_days({"Moon": 1})["days"] == 12

    # T3: Synthetic Moon search
    lon0, rate = 100.0, 13.2
    lon_at = lambda jd: (lon0 + rate * jd) % 360.0  # noqa: E731
    for target in (4, 3, 2):
        entry = ct.next_sign_entry(lon_at, 0.0, target)
        expected = ((target * 30.0 - lon0) % 360.0 or 360.0) / rate
        assert abs(entry - expected) < 2.0 / 86400.0, (target, entry, expected)
        assert int(lon_at(entry) / 30.0) == target
        assert int(lon_at(entry - 2.0 / 86400.0) / 30.0) != target


# ---------------------------------------------------------------------------
# Worked Example: Standard layer Ayer functional role, tithi, and tables
# ---------------------------------------------------------------------------
def test_standard_worked_examples() -> None:
    scripts = str(PRASHNA_ROOT / "scripts")
    if not (PRASHNA_ROOT / "scripts" / "format_prashna_standard.py").exists():
        return
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import format_prashna_standard as fs

    def chart(basic, waxing=True):
        planets = {name: {"house": 1} for name in fs.CLASSICAL_PLANETS}
        return {
            "planets": planets,
            "moon_phase": {"waxing": waxing},
            "dignity": {name: {"basic": value} for name, value in basic.items()},
        }

    # Note Example 1: Jupiter for Capricorn rules 3, 12 and is debilitated -> malefic; exalted falls back to natural benefic
    assert fs._ayer_role(chart({"Jupiter": "debilitated"}), "Jupiter", "Capricorn") == "Malefic (Note Example 1)"
    assert fs._ayer_role(chart({"Jupiter": "exalted"}), "Jupiter", "Capricorn") == "Benefic (Fallback)"
    # Note Example 2: Mars for Leo rules 4, 9, must be strong to be benefic; exalted -> benefic, friend sign -> fallback malefic
    assert fs._ayer_role(chart({"Mars": "exalted"}), "Mars", "Leo") == "Benefic (Note Example 2)"
    assert fs._ayer_role(chart({"Mars": "friend"}), "Mars", "Leo") == "Malefic (Fallback)"
    # Saturn exalted in Libra: rules 4, 5 for Libra -> benefic
    assert fs._ayer_role(chart({"Saturn": "exalted"}), "Saturn", "Libra") == "Benefic (Note Example 2)"
    # Own sign lord is always benefic
    assert fs._ayer_role(chart({"Saturn": "debilitated"}), "Saturn", "Aquarius") == "Benefic (Own Lord)"
    assert fs._ayer_role(chart({"Moon": "neutral"}, waxing=False), "Moon", "Aries") == "Malefic (Fallback)"

    # Tithi Full Moon window: Waxing 10th to Waning 5th (108° <= diff < 240°)
    for diff, expected in ((107.9, (9, False)), (108.0, (10, True)),
                           (239.9, (20, True)), (240.0, (21, False))):
        assert fs.tithi_facts(350.0, (350.0 + diff) % 360.0) == expected, diff

    # P-VI.4 Distance: first half distance from 1st Navamsa, second half from middle 5th
    assert fs._navamsa_number(0.0) == 1 and fs._navamsa_number(14.9) == 5
    assert fs._navamsa_number(15.0) == 5 and fs._navamsa_number(29.99) == 9
    # P-I.7: Odd signs 1/4/7 Dhatu, even signs 1/4/7 Jeeva
    assert fs.OBJECT_KINDS_ODD[0].startswith("Dhatu")
    assert fs.OBJECT_KINDS_EVEN[0].startswith("Jeeva")

    # P-I.4 Note Shadvarga: Virgo 30° -> Mercury, Sun, Venus, Mercury, Sun, Mars
    signs = fs._shadvarga_signs("Virgo", 29.99)
    lords = [fs.SIGN_LORDS[signs[k]] for k in ("D1", "D2", "D3", "D9", "D12", "D30")]
    assert lords == ["Mercury", "Sun", "Venus", "Mercury", "Sun", "Mars"], signs
    # Traditional Hora: odd sign 1st half Sun (Leo), even sign 1st half Moon (Cancer)
    assert fs._shadvarga_signs("Aries", 3.0)["D2"] == "Leo"
    assert fs._shadvarga_signs("Taurus", 3.0)["D2"] == "Cancer"
    # Majority critical boundary
    ch = chart({})
    base = fs._shadvarga_majority(ch, "Aries", 0.5)[2]
    crit = fs._shadvarga_critical(ch, "Aries", 0.5)
    assert crit is not None and crit > 0
    inside = [fs._shadvarga_majority(ch, "Aries", x)[2] for x in (0.5 + crit - 1e-6, max(0.0, 0.5 - crit + 1e-6))]
    outside = [fs._shadvarga_majority(ch, "Aries", x)[2] for x in (0.5 + crit + 1e-6, 0.5 - crit - 1e-6) if 0 <= x < 30]
    assert inside == [base, base], (base, crit, inside)
    assert any(v != base for v in outside), (base, crit, outside)

    # Ability and Desire Layer Facts (Pisces Lagna worked chart structure)
    order = fs.SIGNS[11:] + fs.SIGNS[:11]
    lords = {h: {"sign": order[h - 1], "lord": fs.SIGN_LORDS[order[h - 1]]} for h in range(1, 13)}
    where = {"Sun": (8, "Libra"), "Moon": (3, "Taurus"), "Mars": (5, "Cancer"),
             "Mercury": (8, "Libra"), "Jupiter": (5, "Cancer"), "Venus": (8, "Libra"),
             "Saturn": (1, "Pisces"), "Rahu": (12, "Aquarius"), "Ketu": (6, "Leo")}
    retro = {"Mercury", "Venus", "Saturn"}
    sight = {"Sun": [2], "Moon": [9], "Mars": [8, 11, 12], "Mercury": [2],
             "Jupiter": [9, 11, 1], "Venus": [2], "Saturn": [3, 7, 10]}
    pisces = {
        "lagna": {"sign": "Pisces"},
        "house_lords": lords,
        "planets": {n: {"house": h, "sign": s, "retrograde": n in retro} for n, (h, s) in where.items()},
        "dignity": {n: {"basic": b} for n, b in {
            "Sun": "debilitated", "Moon": "exalted", "Mars": "debilitated", "Mercury": "neutral",
            "Jupiter": "exalted", "Venus": "own_sign", "Saturn": "enemy"}.items()},
        "combustion": {"Venus": {"distance": 7.0}},
        "graha_drishti": {n: {"from_house": where[n][0], "aspected_houses": hs} for n, hs in sight.items()},
        "moon_phase": {"waxing": False},
    }
    planet, factors, rescue, verdict = fs._lord_ability(pisces, 7)
    assert (planet, verdict) == ("Mercury", "Compromised Capacity"), (factors, rescue, verdict)
    assert factors == ["Placed in house 8", "Retrograde"] and "Natural friend sign" in rescue and "Aspected/occupied by benefic" in rescue, (factors, rescue)
    assert fs._lord_ability(pisces, 3)[3] == "Severely Afflicted"
    _, f8, _, v8 = fs._lord_ability(pisces, 8)
    assert "Placed in house 8" not in f8 and f8[:2] == ["Combust", "Retrograde"] and v8 == "Severely Afflicted", (f8, v8)
    assert "Placed in house 8" in fs._lord_ability(pisces, 3)[1]
    assert fs._lord_ability(pisces, 1)[1] == ["Aspected/occupied by malefic (Mars), no benefic"]
    assert fs._lord_links(pisces, 7)[3] == "Mutual 4/10 relationship"
    assert fs._lord_links(pisces, 2)[3] == "Same house"
    assert fs._relation(pisces, "Mars", "Mercury") == ["Mars aspects Mercury", "Mutual 4/10 relationship"]

    start, move, point, weak, verdict = fs._action_chain(pisces, 7)
    assert fs._derived(7, 3) == 9 and fs._derived(7, 10) == 4 and fs._derived(7, 11) == 5
    assert start == ["Initiative lord Mars–Mercury: Mars aspects Mercury, Mutual 4/10 relationship", "Mars–Mercury: Mars aspects Mercury"], start
    assert move == "Actor lord Mercury directly" and not weak and verdict == "Favorable (Action Expected)", (move, weak, verdict)
    assert point == ["Mercury–Jupiter: Mutual 4/10 relationship", "Mars–Jupiter: Same house",
                     "Bridged via Mars (Mars–Jupiter: Same house; Mars–Mercury: Mars aspects Mercury)"], point


# ---------------------------------------------------------------------------
# Worked Example: Second-level exact chart calculation
# ---------------------------------------------------------------------------
def test_exact_second_chart() -> None:
    calc = SKILLS_ROOT / "vedic-calculator" / "scripts"
    scripts = PRASHNA_ROOT / "scripts"
    if not (calc / "engine.py").exists() or not (scripts / "prashna_time.py").exists():
        return
    for p in (str(calc), str(scripts)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import io
    import contextlib
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            import engine
            import prashna_time as pt
            import format_prashna_standard as fs
    except ImportError as e:
        raise AssertionError(f"Missing dependency: {e}")

    zone, lat, lon = ZoneInfo("Asia/Shanghai"), 22.555, 113.883

    def chart(dt):
        with contextlib.redirect_stdout(io.StringIO()):
            return pt.calculate_prashna_chart(dt, lat, lon, "Asia/Shanghai")

    c = chart(datetime(2026, 10, 21, 14, 0, 50, tzinfo=zone))
    got = tuple(c["divisional_charts"][k]["Lagna"]["sign"] for k in ("D3", "D9", "D12", "D30"))
    assert got == ("Virgo", "Cancer", "Virgo", "Capricorn"), got
    meta = c.get("calc_meta") or {}
    assert meta.get("instant_utc") == "2026-10-21T06:00:50.000000Z", meta
    text = "\n".join(fs._shadvarga_lines(c))
    assert "unavailable" not in text and "Total" in text, text

    lo = datetime(2026, 10, 21, 14, 0, 0, tzinfo=zone)
    hi = datetime(2026, 10, 21, 14, 1, 30, tzinfo=zone)

    def degree(t):
        return engine.calc_lagna(pt.local_datetime_to_jd(t, "Asia/Shanghai"), lat, lon)["degree"]

    assert degree(lo) < 20.0 < degree(hi)
    for _ in range(30):
        mid = lo + (hi - lo) / 2
        if degree(mid) < 20.0:
            lo = mid
        else:
            hi = mid
    for t in (hi - timedelta(seconds=0.2), hi + timedelta(seconds=0.2)):
        text = "\n".join(fs._shadvarga_lines(chart(t)))
        assert "unavailable" not in text, (t, text)


# ---------------------------------------------------------------------------
# Worked Example: Judgment Engine
# ---------------------------------------------------------------------------
def test_judge_worked_example() -> None:
    calc = SKILLS_ROOT / "vedic-calculator" / "scripts"
    scripts = PRASHNA_ROOT / "scripts"
    if not (scripts / "prashna_rules.py").exists():
        raise AssertionError("Missing prashna_rules.py")
    for p in (str(calc), str(scripts)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import io
    import contextlib
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    with contextlib.redirect_stdout(io.StringIO()):
        import prashna_time as pt
        import prashna_rules as pr

    dt = datetime(2026, 10, 28, 15, 24, 0, 696168, tzinfo=ZoneInfo("Asia/Shanghai"))
    def chart(x):
        with contextlib.redirect_stdout(io.StringIO()):
            return pt.calculate_prashna_chart(x, 30.27, 120.15, "Asia/Shanghai")
    base = chart(dt)
    variants = [("-60s", chart(dt - timedelta(seconds=60))), ("+60s", chart(dt + timedelta(seconds=60)))]
    plan = pr.Plan.from_dict({
        "matter": "meeting", "matter_house": 7, "context": "love", "actor": 7,
        "keywords": [{"word": "private", "houses": [8, 12, 4], "polarity": "aligned", "source": "M-XIV.20"},
                     {"word": "partner_initiative", "houses": [9], "planets": ["Mars"], "polarity": "aligned", "source": "M-XIV.5"}],
        "qualifiers": ["private", "initiative"], "location": "city"})
    v = pr.judge(base, plan, variants=variants)
    got = [(e["rule_id"], e["direction"], bool(e["excluded"])) for e in v["ledger"]]
    assert got == [("P-I.4", "mixed", False), ("P-I.3", "unf", False), ("M-XVII.5", "none", False),
                   ("M-XVII.15", "none", False), ("M-XVII.16", "fav", False), ("M-XVII.17", "unf", True),
                   ("P-IV.1", "mixed", False), ("M-XIV.43", "fav", False)], got
    assert v["sum"] == 1 and (v["tier"], v["strength"]) == ("Favorable", "With Resistance"), (v["sum"], v["tier"], v["strength"])
    assert v["branches"] == [] and v["sensitive"][0]["rules"] == ["P-I.4"], v["sensitive"]
    assert v["chain"]["verdict"] == "Favorable (Action Expected)"
    assert [(q["name"], q["result"]) for q in v["qualifiers"]] == [("private", "Established"), ("initiative", "Established")], v["qualifiers"]
    ab = v["ability"]
    assert (ab["planet"], ab["factors"], ab["verdict"]) == ("Mercury", ["Retrograde"], "Compromised Capacity"), ab
    assert ab["dropped"] == ["Placed in house 8 (contextually identified house, matched indication)"], ab["dropped"]

    # All 3 option switches off = baseline frozen ledger
    off = pr.judge(base, plan, pr.Options(d2_link=False, d3_need=False, d4_context=False), variants)
    assert off["sum"] == -1 and (off["tier"], off["strength"]) == ("Unfavorable", "With Turning Points"), (off["sum"], off["tier"])
    assert off["sensitive"][0]["tier"] == "Balanced · Evenly Balanced", off["sensitive"]
    assert off["ability"]["factors"] == ["Placed in house 8", "Retrograde"], off["ability"]

    # Prerequisite verification test
    pub = pr.Plan.from_dict({"matter": "general", "matter_house": 7, "context": "love", "qualifiers": ["public"],
                             "keywords": [{"word": "public", "houses": [10], "polarity": "aligned", "source": "M-XIV.12"}]})
    pv = pr.judge(base, pub)
    q = pv["qualifiers"][0]
    assert (q["name"], q["result"]) == ("public", "Not Established") and "Significator Mercury placed in house 8 -> private" in q["basis"], q
    assert pv["condition_failed"] == ["public"] and pv["timing"] == "none", (pv["condition_failed"], pv["timing"])
    assert v["condition_failed"] == [] and v["timing"] == "general", (v["condition_failed"], v["timing"])

    import format_prashna_standard as F
    assert base["dignity"]["Venus"]["basic"] == "moolatrikona", base["dignity"]["Venus"]
    assert F._lord_ability(base, 8)[2] == ["Own sign"], F._lord_ability(base, 8)

    mars = F._lord_ability(base, 2)
    assert mars[1] == ["Debilitated"] and mars[2] == ["Aspected/occupied by benefic", "Weak but in good place (house 5)"], mars
    assert not any(r.startswith("Weak but in good place") for r in F._lord_ability(base, 6)[2])

    desc = pr.Plan.from_dict({"matter": "description", "matter_house": 7, "context": "love",
                              "keywords": [{"word": "quarrel", "houses": [6], "planets": ["Mars"], "polarity": "aligned",
                                            "source": "M-XIV.117; 6th house strife"}]})
    dv = pr.judge(base, desc, variants=variants)
    assert dv["ledger"] == [] and (dv["tier"], dv["timing"], dv["sensitive"]) == ("Description", "none", []), dv
    inf = [(r["at"], r["how"], r["planet"], r["hits"]) for r in dv["describe"]["influences"]]
    assert inf == [("House 7", "Aspecting", "Saturn", ["None"]),
                   ("Significator Mercury placed in house 8", "Same house", "Sun", ["quarrel (aligned)"]),
                   ("Significator Mercury placed in house 8", "Same house", "Venus", ["None"]),
                   ("Significator Mercury placed in house 8", "Aspecting", "Mars", ["quarrel (aligned)"])], inf
    assert dv["describe"]["M-XIV.117"]["result"] == "Not Established", dv["describe"]["M-XIV.117"]

    # Intake plan validation
    assert pr.Plan.from_dict({"matter": "lost_property", "matter_house": 11}).house_of_matter() == 11
    for bad in ({"matter": "meeting", "matter_house": 7, "keywords": [{"word": "private", "houses": [8], "polarity": "aligned"}]},
                {"matter": "meeting", "matter_house": 7, "qualifiers": ["initiative"]},
                {"matter": "description", "matter_house": 7, "qualifiers": ["private"]},
                {"matter": "lost_property", "matter_house": 4},
                {"matter": "non_existent_topic"}):
        try:
            pr.Plan.from_dict(bad)
        except ValueError:
            continue
        raise AssertionError(f"Plan should have been rejected: {bad}")

    # Time scope validation
    lost = {"matter": "lost_property", "matter_house": 11}
    scoped = pr.Plan.from_dict({**lost, "time_scope": {"kind": "range", "label": "tonight", "until": "2026-10-28"}})
    assert pr.judge(base, scoped) == pr.judge(base, pr.Plan.from_dict(lost))
    assert pr.Plan.from_dict({**lost, "time_scope": {"kind": "unlimited"}}).time_scope["kind"] == "unlimited"
    for ts in ({"kind": "soon"}, {"kind": "range", "label": "tonight"}, {"kind": "range", "until": "2026-10-28"},
               {"kind": "range", "label": "tonight", "until": "tonight"}, "tonight"):
        try:
            pr.Plan.from_dict({**lost, "time_scope": ts})
        except ValueError:
            continue
        raise AssertionError(f"time_scope should have been rejected: {ts}")


def test_known_instant_text() -> None:
    """Daylight saving boundaries and ISO string format round-tripping."""
    calc = SKILLS_ROOT / "vedic-calculator" / "scripts"
    scripts = PRASHNA_ROOT / "scripts"
    if not (calc / "engine.py").exists() or not (scripts / "prashna_time.py").exists():
        return
    for p in (str(calc), str(scripts)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import io
    import contextlib
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            import build_prashna_data as builder
            import judge_prashna_standard as judge
            import prashna_time as pt
    except ImportError as e:
        raise AssertionError(f"Missing dependency: {e}")

    zone, paris = "Europe/London", "Europe/Paris"
    first = pt.parse_local_datetime("2026-10-25 01:30:30+01:00", zone)
    second = pt.parse_local_datetime("2026-10-25 01:30:30.5+00:00", zone)
    assert (first.fold, second.fold) == (0, 1), (first, second)
    now = pt.parse_local_datetime("now", zone)
    for dt in (second, now):
        assert pt.parse_local_datetime(pt.instant_text(dt), zone).isoformat() == dt.isoformat(), dt

    for text, tz in (("2026-10-25 01:30:30", zone), ("2026-03-29 02:30:00", paris),
                     ("2026-10-25 01:30:30+05:00", zone), ("2026-03-29 02:30:00+01:00", paris)):
        try:
            pt.parse_local_datetime(text, tz)
        except Exception:
            continue
        raise AssertionError(f"Should have been rejected: {text} {tz}")

    header = builder.build_prashna_header(second, 51.51, -0.13, zone, "q", "t", 24.0, None)
    assert "Script Time: 2026-10-25 01:30:30.500000+00:00" in header, header

    def utcs(dt, lat, lon, tz):
        _, variants = judge.charts(dt, lat, lon, tz, "city")
        return [c["calc_meta"]["instant_utc"] for _, c in variants]

    got = utcs(second, 51.51, -0.13, zone)
    assert got == ["2026-10-25T01:29:30.500000Z", "2026-10-25T01:31:30.500000Z"], got
    edge = pt.parse_local_datetime("2026-03-29 01:59:30+01:00", paris)
    got = utcs(edge, 48.86, 2.35, paris)
    assert got == ["2026-03-29T00:58:30.000000Z", "2026-03-29T01:00:30.000000Z"], got


def _run(name, fn):
    try:
        fn()
        print(f"[PASS] {name}")
        return True
    except AssertionError as e:
        print(f"[FAIL] {name}\n{e}\n")
        return False


if __name__ == "__main__":
    results = [
        _run("engine_no_alien_fields", test_engine_no_alien_fields),
        _run("shared_rules_no_prashna_terms", test_shared_rules_no_prashna_terms),
        _run("prashna_products_in_isolated_dir", test_prashna_products_in_isolated_dir),
        _run("no_reverse_import_from_prashna", test_no_reverse_import_from_prashna),
        _run("standard_builder_no_timing_import", test_standard_builder_no_timing_import),
        _run("timing_no_optional_stack_import", test_timing_no_optional_stack_import),
        _run("standard_builder_no_optional_stack_import",
             test_standard_builder_no_optional_stack_import),
        _run("timing_worked_examples", test_timing_worked_examples),
        _run("standard_worked_examples", test_standard_worked_examples),
        _run("exact_second_chart", test_exact_second_chart),
        _run("judge_worked_example", test_judge_worked_example),
        _run("known_instant_text", test_known_instant_text),
    ]
    if all(results):
        print("\n[GREEN] All 7 isolation assertions, timing sub-layer, standard layer, and judgment tests PASSED.")
        sys.exit(0)
    else:
        print("\n[RED] Isolation assertions failed.")
        sys.exit(1)
