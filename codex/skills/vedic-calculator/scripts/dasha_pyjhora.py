"""
dasha_pyjhora.py - PyJHora Vimsottari Dasha wrapper
Calculates MD/AD/PD timing dates using PyJHora high-precision astronomical algorithms (deviation <= 2 days vs JHora PDF).
The old 365.25 approximation in engine.py had 6-9 days deviation.

Return format is compatible with chart['dashas'] data contract; legacy approximation entrypoint disabled.
"""

import swisseph as swe
import os
import sys
from datetime import datetime, timedelta, timezone


# Planet ID ↔ Name mapping (PyJHora convention: RAHU=7, KETU=8)
_PLANET_NAMES = {
    0: 'Sun', 1: 'Moon', 2: 'Mars', 3: 'Mercury',
    4: 'Jupiter', 5: 'Venus', 6: 'Saturn', 7: 'Rahu', 8: 'Ketu'
}

# Standard Vimsottari Dasha durations
_DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}

# Standard Vimsottari Antardasha order: from dasha lord, cycle through 9 planets
_DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']


def _setup_jhora():
    """Apply the same monkey-patches as ashtakavarga_pyjhora.py"""
    # Patch swe.calc_ut for pysweph 2.10+ compatibility
    # Sentinel must match the other 4 wrappers (_patched): using _dasha_patched caused incompatibility,
    # stacking 2 layers per chart, triggering RecursionError after ~490 charts in resident processes.
    orig_calc = swe.calc_ut
    if not getattr(orig_calc, '_patched', False):
        def patched_calc(jd, planet, flags=0):
            r = orig_calc(jd, planet, flags=flags)
            return r[0], r[1] if len(r) > 1 else 0
        patched_calc._patched = True
        swe.calc_ut = patched_calc

    # Patch swe.houses_ex
    if hasattr(swe, 'houses_ex'):
        orig_he = swe.houses_ex
        if not getattr(orig_he, '_patched', False):
            def patched_he(*a, **kw):
                # (1) PyJHora drik.ascendant() without hsys -> pyswisseph defaults to Placidus, which has no
                #     solution inside the polar circle (|lat|>66°33'). Pass b'W' (whole sign): asc is invariant to house system.
                # (2) Explicit Placidus/Koch calls (Shadbala Dig Bala's bhaava_madhya) also fail inside polar circles:
                #     Following Swiss Ephemeris docs, fall back to Porphyry (swe_houses does this internally on ERR).
                # (3) Sidereal chart requests unify to engine.calc_lagna Lagna baseline (= desktop JHora benchmark,
                #     0.004 arcsec diff vs 2026-10-23 JHora printout): apparent position tropical house - ayanamsa (TRUEPOS|NONUT).
                #     PyJHora FLG_TRUEPOS only alters houses_ex internal ayanamsa, differing from planet ayanamsa by ~9 arcsec.
                #     ARMC and placeholder elements do not subtract ayanamsa, retained as-is based on FLG_SIDEREAL native comparison.
                if len(a) < 4 and 'hsys' not in kw:
                    a = a + (b'W',)
                jd, lat, lon = a[0], a[1], a[2]
                hsys = a[3] if len(a) > 3 else kw.get('hsys', b'W')
                flags = a[4] if len(a) > 4 else kw.get('flags', 0)
                def _he(hs, fl):
                    try:
                        r = orig_he(jd, lat, lon, hs, fl)
                    except swe.Error:
                        if hs not in (b'P', b'K'):
                            raise
                        r = orig_he(jd, lat, lon, b'O', fl)
                    return r[0], r[1]
                if not flags & swe.FLG_SIDEREAL:
                    return _he(hsys, flags)
                trop_c, trop_a = _he(hsys, 0)
                sid_c, sid_a = _he(hsys, swe.FLG_SIDEREAL)
                ay = swe.get_ayanamsa_ex_ut(jd, swe.FLG_TRUEPOS | swe.FLG_NONUT)[1]
                def _fix(trop, sid):
                    return tuple((t - ay) % 360 if abs((t - s + 180) % 360 - 180) > 1 else t
                                 for t, s in zip(trop, sid))
                return _fix(trop_c, sid_c), _fix(trop_a, sid_a)
            patched_he._patched = True
            swe.houses_ex = patched_he


def calculate_dasha_fixed(
    year, month, day, hour, minute, lat, lon, tz_offset, include_pd=True, second=0,
    as_of=None,
):
    """Calculate Vimsottari Dasha using PyJHora's precise algorithm.
    
    Args:
        year, month, day: Birth date
        hour, minute: Birth time (local)
        lat, lon: Birth coordinates
        tz_offset: Timezone offset in hours (e.g., 8.0 for Asia/Shanghai)
        include_pd: Whether to calculate the 729 Pratyantardasha rows. Keep the
            default ``True`` for canonical chart generation. Endpoint scans that
            only need MD/AD may set it to ``False`` and request PD later for the
            specific event windows that require month/day resolution.
    
    Returns:
        List of dasha dicts compatible with engine.py format:
        [{'planet': str, 'start': 'YYYY-MM', 'end': 'YYYY-MM', 'years': float,
          'is_current': bool, 'antardashas': [
              {'planet': str, 'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD',
               'is_current': bool, 'pratyantardashas': [...]}
          ]}, ...]

        All intervals are interpreted as [start, end); AD and PD boundaries are taken directly from PyJHora
        L2/L3 return values without 365.25 day approximation reversal.
    """
    _setup_jhora()

    # Set ephemeris path
    from jhora.panchanga import drik
    ephe_dir = os.path.join(
        os.path.dirname(os.path.dirname(drik.__file__)), 'data', 'ephe'
    )
    if os.path.isdir(ephe_dir):
        swe.set_ephe_path(ephe_dir)

    # Configure ayanamsa (same as ashtakavarga_pyjhora)
    from jhora import const
    from jhora.panchanga.drik import Place
    from jhora.horoscope.dhasa.graha import vimsottari

    drik.set_ayanamsa_mode('TRUE_CITRA')
    const._DEFAULT_AYANAMSA_MODE = 'TRUE_CITRA'
    const._use_true_nodes_for_rahu_ketu = False

    # Create Place and JD (local time, same as ashtakavarga)
    place = Place('birth_place', lat, lon, tz_offset)
    local_hour = hour + minute / 60.0 + second / 3600.0
    jd_local = swe.julday(year, month, day, local_hour)

    # PyJHora vimsottari.year_duration is module-global, initialized to mean sidereal year (const.sidereal_year),
    # and only get_vimsottari_dhasa_bhukthi(L2) updates it to true sidereal year; this function calls L1 then L2,
    # so the first chart uses mean year while subsequent charts use lingering true year -> final MD end drift
    # by ~5 hours. Explicitly align beforehand to ensure identical year duration across L1 and L2.
    vimsottari.year_duration = drik.dhasa_year_duration(jd=jd_local, place=place)

    # ── 1. Get Mahadasha start dates ──
    md_dict = vimsottari.vimsottari_mahadasa(jd_local, place)
    # md_dict: OrderedDict {planet_id: start_jd}

    # ── 2. Get Antardasha and optional Pratyantardasha entries ──
    # Fail fast: silently returning an empty sub-period table would let downstream
    # analysis fabricate month-level precision from MD/AD alone.
    _, ad_entries = vimsottari.get_vimsottari_dhasa_bhukthi(
        jd_local, place, dhasa_level_index=2  # ANTARA level
    )
    pd_entries = []
    if include_pd:
        _, pd_entries = vimsottari.get_vimsottari_dhasa_bhukthi(
            jd_local, place, dhasa_level_index=3  # PRATYANTARA level
        )

    def _entry_datetime(entry_date):
        y, m, d, fractional_hour = entry_date
        return datetime(int(y), int(m), int(d)) + timedelta(hours=float(fractional_hour))

    # Build antardasha lookup: {md_planet_id: [(ad_id, start_datetime), ...]}
    ad_lookup = {}
    for entry in ad_entries:
        md_id, ad_id = entry[0]
        ad_lookup.setdefault(md_id, []).append((ad_id, _entry_datetime(entry[1])))

    # Build PD lookup: {(md_id, ad_id): [(pd_id, start_datetime), ...]}
    pd_lookup = {}
    for entry in pd_entries:
        md_id, ad_id, pd_id = entry[0]
        pd_lookup.setdefault((md_id, ad_id), []).append(
            (pd_id, _entry_datetime(entry[1]))
        )

    # ── 3. Build output ──
    # Dasha boundaries derive from jd_local (UT + birth tz_offset wall-clock time); current must use same offset.
    # Avoid machine-local datetime.now(): changing machines shifts markers near boundary dates.
    # as_of must be timezone-aware (defaults to current UTC).
    if as_of is None:
        as_of = datetime.now(timezone.utc)
    if as_of.tzinfo is None:
        raise ValueError("as_of must be a timezone-aware datetime")
    now = as_of.astimezone(timezone.utc).replace(tzinfo=None) + timedelta(hours=tz_offset)
    md_items = list(md_dict.items())
    dashas = []

    for i, (pid, start_jd) in enumerate(md_items):
        planet = _PLANET_NAMES.get(pid, f'P{pid}')
        years = _DASHA_YEARS.get(planet, 0)

        ad_list = ad_lookup.get(pid, [])
        if len(ad_list) != 9:
            raise RuntimeError(
                f"PyJHora returned {len(ad_list)} AD rows for {planet}; expected 9"
            )

        # Use the L2 table as the canonical MD boundary source so the parent MD
        # and its first/last AD share one exact [start,end) boundary.  PyJHora's
        # separate L1 and L2 calls can differ by minutes or hours after many
        # cycles; mixing them creates a false one-day overlap after date-only
        # formatting even though every individual level is internally valid.
        start_dt = ad_list[0][1]
        start_str = start_dt.strftime('%Y-%m')

        # End date = next MD's first L2 row, or the final L1 duration fallback.
        if i + 1 < len(md_items):
            next_pid = md_items[i + 1][0]
            next_ad_list = ad_lookup.get(next_pid, [])
            if len(next_ad_list) != 9:
                raise RuntimeError(
                    f"PyJHora returned {len(next_ad_list)} AD rows for next MD; expected 9"
                )
            end_dt = next_ad_list[0][1]
        else:
            # Last dasha end uses PyJHora's configured dasha-year duration.
            # Do not substitute a civil-year or 365.25 approximation.
            year_duration = drik.dhasa_year_duration(jd=jd_local, place=place)
            end_jd = start_jd + float(years) * year_duration
            ey, em, ed, eh = swe.revjul(end_jd)
            end_dt = datetime(int(ey), int(em), int(ed)) + timedelta(hours=float(eh))
        end_str = end_dt.strftime('%Y-%m')

        is_current = start_dt <= now < end_dt

        # Build antardashas
        antardashas = []
        for j, (ad_id, ad_start_dt) in enumerate(ad_list):
            ad_planet = _PLANET_NAMES.get(ad_id, f'P{ad_id}')
            # End = next antardasha's start
            if j + 1 < len(ad_list):
                ad_end_dt = ad_list[j + 1][1]
            else:
                ad_end_dt = end_dt
            ad_is_current = ad_start_dt <= now < ad_end_dt

            pd_list = pd_lookup.get((pid, ad_id), [])
            if include_pd and len(pd_list) != 9:
                raise RuntimeError(
                    f"PyJHora returned {len(pd_list)} PD rows for "
                    f"{planet}-{ad_planet}; expected 9"
                )

            pratyantardashas = []
            for k, (pd_id, pd_start_dt) in enumerate(pd_list):
                pd_planet = _PLANET_NAMES.get(pd_id, f'P{pd_id}')
                pd_end_dt = pd_list[k + 1][1] if k + 1 < len(pd_list) else ad_end_dt
                pratyantardashas.append({
                    'planet': pd_planet,
                    'start': pd_start_dt.strftime('%Y-%m-%d'),
                    'end': pd_end_dt.strftime('%Y-%m-%d'),
                    'start_time': pd_start_dt.strftime('%Y-%m-%d %H:%M'),
                    'end_time': pd_end_dt.strftime('%Y-%m-%d %H:%M'),
                    'is_current': pd_start_dt <= now < pd_end_dt,
                })

            antardashas.append({
                'planet': ad_planet,
                'start': ad_start_dt.strftime('%Y-%m-%d'),
                'end': ad_end_dt.strftime('%Y-%m-%d'),
                'start_time': ad_start_dt.strftime('%Y-%m-%d %H:%M'),
                'end_time': ad_end_dt.strftime('%Y-%m-%d %H:%M'),
                'is_current': ad_is_current,
                'pratyantardashas': pratyantardashas,
            })

        dashas.append({
            'planet': planet,
            'start': start_str,
            'end': end_str,
            'years': round(years, 1),
            'is_current': is_current,
            'antardashas': antardashas,
        })

    return dashas
