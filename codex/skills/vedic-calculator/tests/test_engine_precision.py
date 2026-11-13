"""calculator engine v1.0 precision regression test suite.
Verification benchmarks:
  - Desktop JHora printout (PDF, 2004-09-12 11:15:27 Shanghai, True Chitra, Mean Node);
  - Meeus Julian Day manual calculation;
  - Parashara divisional formulae (D9/D10) and tz database DST rules.

Run: python tests/test_engine_precision.py
"""
import io
import sys
import contextlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
with contextlib.redirect_stdout(io.StringIO()):
    import engine
swe = engine.swe


def _arcsec(a, b):
    return abs(((a - b + 180.0) % 360.0) - 180.0) * 3600.0


def _chart(*args, **kw):
    with contextlib.redirect_stdout(io.StringIO()):
        return engine.calculate_full_chart(*args, **kw)


def _dms(sign_start, d, m, s):
    return sign_start + d + m / 60.0 + s / 3600.0


# Desktop JHora printout values verified against nakshatras
DESKTOP = {
    "Lagna": _dms(210, 7, 0, 38.50),
    "Sun": _dms(120, 25, 48, 5.43),
    "Moon": _dms(90, 26, 39, 42.79),
    "Mars": _dms(120, 26, 56, 14.73),
    "Mercury": _dms(120, 8, 13, 11.32),
    "Jupiter": _dms(150, 3, 17, 40.94),
    "Venus": _dms(90, 11, 44, 32.27),
    "Saturn": _dms(90, 0, 36, 38.53),
}
DESKTOP_AYANAMSA = 23 + 54 / 60 + 24.90 / 3600


def test_desktop_gold_chart():
    c = _chart(2004, 9, 12, 11, 15, 31 + 6 / 60, 121 + 22 / 60, "Asia/Shanghai", second=27)
    assert _arcsec(c["lagna"]["longitude"], DESKTOP["Lagna"]) <= 0.5, c["lagna"]
    assert abs(c["ayanamsa"] - DESKTOP_AYANAMSA) * 3600 <= 0.5, c["ayanamsa"]
    for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        assert _arcsec(c["planets"][name]["longitude"], DESKTOP[name]) <= 0.5, name
    # PyJHora divisional charts share identical Lagna baseline with D1 (<=0.36 arcsec)
    d1 = c["divisional_charts"]["D1"]["Lagna"]
    assert d1["sign"] == c["lagna"]["sign"]
    assert abs(d1["degree"] - c["lagna"]["degree"]) * 3600 <= 0.5
    assert c["divisional_charts"]["D9"]["Lagna"]["sign"] == "Virgo"   # Desktop Navamsa column Vi


def test_second_default_is_minute_path():
    as_of = datetime(2026, 1, 1, tzinfo=timezone.utc)
    a = _chart(1990, 8, 15, 10, 30, 39.9042, 116.4074, "Asia/Shanghai", as_of=as_of)
    b = _chart(1990, 8, 15, 10, 30, 39.9042, 116.4074, "Asia/Shanghai", second=0, as_of=as_of)
    assert repr(a) == repr(b)


def test_jd_seconds_and_dst():
    # Meeus: 2026-10-21 0h UT = 2461334.5; Local 14:00:50 (UTC+8) = 06:00:50 UT
    jd = engine.to_jd(2026, 10, 21, 14, 0, "Asia/Shanghai", second=50)
    assert abs(jd - (2461334.5 + 21650 / 86400)) < 1e-8, jd
    # China 1988 DST (4-10 to 9-11 UTC+9): 14:00:50 -> 05:00:50 UT
    jd = engine.to_jd(1988, 7, 1, 14, 0, "Asia/Shanghai", second=50)
    assert abs(jd - swe.julday(1988, 7, 1, 5 + 50 / 3600)) < 1e-8, jd
    # Fractional seconds
    jd = engine.to_jd(2026, 12, 31, 23, 59, "UTC", second=59.5)
    assert abs(jd - swe.julday(2026, 12, 31, 23 + 59 / 60 + 59.5 / 3600)) < 1e-8


def test_dst_nonexistent_and_ambiguous():
    for args in ((2026, 3, 8, 2, 30), (2026, 11, 1, 1, 30)):
        try:
            engine.local_instant(*args, "America/New_York", 30)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{args} should have raised an error")
    # Known instant disambiguated via fold: 0=first (EDT -4), 1=second (EST -5)
    first = engine.local_instant(2026, 11, 1, 1, 30, "America/New_York", 30, fold=0)
    second = engine.local_instant(2026, 11, 1, 1, 30, "America/New_York", 30, fold=1)
    assert first.utcoffset() == timedelta(hours=-4) and second.utcoffset() == timedelta(hours=-5)
    # Non-existent instants with fold should still raise an error
    try:
        engine.local_instant(2026, 3, 8, 2, 30, "America/New_York", 30, fold=0)
    except ValueError:
        pass
    else:
        raise AssertionError("Non-existent instant should raise an error")


def _d9_sign(lon):
    return engine.SIGNS[(9 * int(lon / 30) + int((lon % 30) / (30 / 9))) % 12]


def test_lagna_basis_consistent_with_pyjhora_vargas():
    # Boundary case verification: 2026-10-21 21:18 Shenzhen Baoan
    cases = [(2026, 10, 21, 21, 18), (2026, 10, 21, 16, 58), (2026, 10, 21, 14, 0)]
    for y, mo, d, h, mi in cases:
        c = _chart(y, mo, d, h, mi, 22.555, 113.883, "Asia/Shanghai")
        lagna = c["lagna"]
        d1 = c["divisional_charts"]["D1"]["Lagna"]
        assert d1["sign"] == lagna["sign"], (h, mi, d1, lagna["sign"])
        assert abs(d1["degree"] - lagna["degree"]) * 3600 <= 0.5, (h, mi)
        edge = min(lagna["degree"] % (30 / 9), (30 / 9) - lagna["degree"] % (30 / 9)) * 3600
        if edge > 0.5:
            assert c["divisional_charts"]["D9"]["Lagna"]["sign"] == _d9_sign(lagna["longitude"]), (h, mi)


def test_houses_patch_keeps_armc_and_matches_engine():
    _chart(2000, 1, 1, 12, 0, 28.6139, 77.209, "Asia/Kolkata")      # houses_ex patch applied
    jd = engine.to_jd(2000, 1, 1, 12, 0, "Asia/Kolkata")
    trop_c, trop_a = swe.houses_ex(jd, 28.6139, 77.209, b'P', 0)
    sid_c, sid_a = swe.houses_ex(jd, 28.6139, 77.209, b'P', swe.FLG_SIDEREAL | swe.FLG_TRUEPOS)
    assert _arcsec(sid_a[0], engine.calc_lagna(jd, 28.6139, 77.209)["longitude"]) <= 1e-6
    assert abs(sid_a[2] - trop_a[2]) < 1e-9          # ARMC does not subtract ayanamsa
    assert sid_c[0] == trop_c[0]                      # placeholder preserved


def test_rectifier_scan_uses_same_lagna():
    """Verify rectifier time_scan inline Lagna calculation matches engine formula."""
    scan_dir = Path(__file__).resolve().parents[2] / "vedic-rectifier" / "scripts"
    if not (scan_dir / "time_scan.py").exists():
        return
    sys.path.insert(0, str(scan_dir))
    with contextlib.redirect_stdout(io.StringIO()):
        import time_scan
    for args in ((2004, 9, 12, 11, 15, "Asia/Shanghai", 27), (1988, 7, 1, 14, 0, "Asia/Shanghai", 50),
                 (1969, 7, 20, 22, 56, "America/New_York", 0)):
        jd = engine.to_jd(*args)
        a = time_scan.calc_sidereal_asc(jd, 31.1, 121.4)
        b = engine.calc_lagna(jd, 31.1, 121.4)["longitude"]
        assert _arcsec(a, b) < 1e-6, (args, a, b)


def test_polar_chart_computes():
    c = _chart(1980, 12, 21, 12, 0, 69.6492, 18.9553, "Europe/Oslo")   # Tromso, within polar circle
    assert c["shadbala"] and "Sun" in c["shadbala"]


def test_current_dasha_independent_of_machine_clock():
    c_utc = _chart(2000, 1, 1, 12, 0, 39.9042, 116.4074, "Asia/Shanghai",
                   as_of=datetime(2022, 2, 11, 14, 47, tzinfo=timezone.utc))
    c_sh = _chart(2000, 1, 1, 12, 0, 39.9042, 116.4074, "Asia/Shanghai",
                  as_of=datetime(2022, 2, 11, 22, 47, tzinfo=timezone(timedelta(hours=8))))
    cur = lambda c: [(d["planet"], [a["planet"] for a in d["antardashas"] if a["is_current"]])
                     for d in c["dashas"] if d["is_current"]]
    assert cur(c_utc) == cur(c_sh) and cur(c_utc), cur(c_utc)
    try:
        _chart(2000, 1, 1, 12, 0, 39.9042, 116.4074, "Asia/Shanghai", as_of=datetime(2022, 2, 11))
    except ValueError:
        pass
    else:
        raise AssertionError("Naive as_of without timezone should raise error")


def test_calc_meta():
    c = _chart(2026, 10, 21, 14, 0, 22.555, 113.883, "Asia/Shanghai", second=50.25)
    meta = c["calc_meta"]
    assert meta["engine_version"] == engine.ENGINE_VERSION
    assert meta["instant_utc"] == "2026-10-21T06:00:50.250000Z", meta
    assert meta["ayanamsa"] == c["ayanamsa"] == engine.ayanamsa_value(engine.to_jd(2026, 10, 21, 14, 0, "Asia/Shanghai", 50.25))
    assert "transits" not in c
    assert c["calc_errors"] == {}, c["calc_errors"]


def test_failures_are_reported_not_swallowed():
    """Errors in optional modules are recorded in calc_errors without aborting remainder."""
    def boom(*a, **kw):
        raise RuntimeError("simulated failure")
    saved = (engine._bhava_bala_pyjhora, engine._chara_dasha)
    engine._bhava_bala_pyjhora, engine._chara_dasha = boom, boom
    try:
        c = _chart(1990, 8, 15, 10, 30, 39.9042, 116.4074, "Asia/Shanghai")
    finally:
        engine._bhava_bala_pyjhora, engine._chara_dasha = saved
    assert c["bhava_bala"] == {"error": "RuntimeError: simulated failure"}, c["bhava_bala"]
    assert c["special_lagnas"] and "error" not in c["special_lagnas"]      # subsequent items calculated
    assert c["vargeeya_bala"] and c["pushkara"] and "error" not in c["pushkara"]
    assert c["chara_dasha"] is None
    assert set(c["calc_errors"]) == {"bhava_bala", "chara_dasha"}, c["calc_errors"]
    with contextlib.redirect_stdout(io.StringIO()):
        from formatter import format_structured_data
        md = format_structured_data(c, None, {"dob": "1990-08-15", "time": "10:30", "place": "Beijing",
                                              "lat": 39.9042, "lon": 116.4074}, {"gender": "female"})
    assert "Calculation Incomplete" in md and "chara_dasha" in md and "Chara Dasha Timeline" not in md


def _same_instant(local, utc):
    """Verify two charts for the identical instant match across all positions and boundary audit."""
    assert _arcsec(local["lagna"]["longitude"], utc["lagna"]["longitude"]) <= 1e-6, (local["lagna"], utc["lagna"])
    for name, planet in utc["planets"].items():
        assert _arcsec(local["planets"][name]["longitude"], planet["longitude"]) <= 1e-6, name
    assert local["divisional_boundary_audit"] == utc["divisional_boundary_audit"]


def test_dst_edge_minutes_compute():
    # Boundary audit across DST transition edges verified against UTC counterparts.
    paris, beijing, new_york = (48.86, 2.35), (39.90, 116.40), (40.71, -74.01)
    cases = [
        ((2010, 3, 28, 1, 59), paris, "Europe/Paris", (2010, 3, 28, 0, 59)),            # CET before spring forward
        ((2010, 10, 31, 3, 0), paris, "Europe/Paris", (2010, 10, 31, 2, 0)),            # CET after fall back
        ((1988, 4, 17, 1, 59), beijing, "Asia/Shanghai", (1988, 4, 16, 17, 59)),        # China 1988 spring DST, CST
        ((1988, 9, 11, 2, 0), beijing, "Asia/Shanghai", (1988, 9, 10, 18, 0)),          # China 1988 autumn DST, CST
        ((2015, 11, 1, 2, 0), new_york, "America/New_York", (2015, 11, 1, 7, 0)),       # US autumn DST, EST
    ]
    for wall, place, tz, utc in cases:
        _same_instant(_chart(*wall, *place, tz), _chart(*utc, *place, "UTC"))


def test_known_instant_around_dst_switch():
    # Real-time charts have exact instants: ambiguous hour resolved via fold.
    london, paris = (51.51, -0.13), (48.86, 2.35)
    cases = [
        ((2026, 10, 25, 1, 30), london, "Europe/London", 0, (2026, 10, 25, 0, 30)),     # First occurrence, BST
        ((2026, 10, 25, 1, 30), london, "Europe/London", 1, (2026, 10, 25, 1, 30)),     # Second occurrence, GMT
        ((2026, 10, 25, 0, 59), london, "Europe/London", 0, (2026, 10, 24, 23, 59)),    # Before transition, BST
        ((2026, 10, 25, 2, 0), london, "Europe/London", 0, (2026, 10, 25, 2, 0)),       # After transition, GMT
        ((2026, 3, 29, 1, 59), paris, "Europe/Paris", 0, (2026, 3, 29, 0, 59)),         # Before spring-forward, CET
        ((2026, 3, 29, 3, 0), paris, "Europe/Paris", 0, (2026, 3, 29, 1, 0)),           # After spring-forward, CEST
    ]
    for wall, place, tz, fold, utc in cases:
        _same_instant(_chart(*wall, *place, tz, second=30, fold=fold), _chart(*utc, *place, "UTC", second=30))
    # Manual input without fold raises error on ambiguous hour
    try:
        _chart(2026, 10, 25, 1, 30, *london, "Europe/London")
    except ValueError:
        pass
    else:
        raise AssertionError("Ambiguous hour without fold should raise error")


TESTS = [test_desktop_gold_chart, test_second_default_is_minute_path, test_jd_seconds_and_dst,
         test_dst_nonexistent_and_ambiguous, test_lagna_basis_consistent_with_pyjhora_vargas,
         test_houses_patch_keeps_armc_and_matches_engine, test_rectifier_scan_uses_same_lagna,
         test_polar_chart_computes,
         test_current_dasha_independent_of_machine_clock, test_calc_meta,
         test_failures_are_reported_not_swallowed,
         test_dst_edge_minutes_compute, test_known_instant_around_dst_switch]

if __name__ == "__main__":
    failed = 0
    for t in TESTS:
        try:
            t()
            print(f"[PASS] {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"[FAIL] {t.__name__}: {e}")
    print("[GREEN] engine precision regression tests passed." if not failed else f"[RED] {failed} tests failed.")
    sys.exit(1 if failed else 0)
