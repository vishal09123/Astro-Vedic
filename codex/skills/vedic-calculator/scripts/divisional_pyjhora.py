"""
divisional_pyjhora.py - PyJHora divisional chart calculation wrapper
Supports all standard divisional charts (D1-D60)
# Uses charts.divisional_chart(chart_method=1) — JHora Traditional Parasara
"""


def calculate_divisional_charts(year, month, day, hour, minute, lat, lon, tz_offset,
                                 chart_factors=None, second=0):
    """
    Calculates divisional charts with PyJHora, 100% consistent with JHora desktop.

    Returns:
        dict: {'D9': {planet: {'sign':..., 'sign_idx':..., 'degree':...}, ...}, ...}
    """
    import sys
    import os
    import swisseph as swe

    pyjhora_path = None
    try:
        import jhora as _jh
        pyjhora_path = os.path.dirname(os.path.dirname(_jh.__file__))
    except ImportError:
        import site
        for sp in site.getsitepackages():
            if os.path.exists(os.path.join(sp, 'jhora')):
                pyjhora_path = sp
                break
    if pyjhora_path is None:
        raise ImportError("jhora package not found")
    if pyjhora_path not in sys.path:
        sys.path.insert(0, pyjhora_path)
    swe.set_ephe_path(os.path.join(pyjhora_path, 'jhora', 'data', 'ephe'))

    for fn_name in ['calc_ut', 'calc']:
        orig = getattr(swe, fn_name)
        if not hasattr(orig, '_patched'):
            def make_patch(o):
                def p(jd, planet, flags=0):
                    r = o(jd, planet, flags=flags)
                    return (r[0], r[1]) if len(r) == 3 else r
                p._patched = True
                return p
            setattr(swe, fn_name, make_patch(orig))
    if hasattr(swe, 'houses_ex'):
        orig_he = swe.houses_ex
        if not hasattr(orig_he, '_patched'):
            def patch_he(*a, **kw):
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
            patch_he._patched = True
            swe.houses_ex = patch_he

    from jhora import const
    from jhora.panchanga import drik
    from jhora.panchanga.drik import Place
    from jhora.horoscope.chart import charts

    drik.set_ayanamsa_mode('TRUE_CITRA')
    const._DEFAULT_AYANAMSA_MODE = 'TRUE_CITRA'
    const._use_true_nodes_for_rahu_ketu = False

    # Fix: drik.dhasavarga() defaults set_rahu_ketu_as_true_nodes=True,
    # which overrides our const._use_true_nodes_for_rahu_ketu=False.
    # Wrap it to force None so it reads from const instead.
    if not hasattr(drik.dhasavarga, '_mean_node_patched'):
        _orig_dhasavarga = drik.dhasavarga
        def _dhasavarga_mean_node(jd, place, divisional_chart_factor=1,
                                   set_rahu_ketu_as_true_nodes=None, **kw):
            return _orig_dhasavarga(jd, place, divisional_chart_factor=divisional_chart_factor,
                                    set_rahu_ketu_as_true_nodes=set_rahu_ketu_as_true_nodes, **kw)
        _dhasavarga_mean_node._mean_node_patched = True
        drik.dhasavarga = _dhasavarga_mean_node

    local_hour = hour + minute / 60.0 + second / 3600.0
    jd_local = swe.julday(year, month, day, local_hour)
    place = Place('birth_place', lat, lon, tz_offset)

    SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    PLANET_MAP = {'L': 'Lagna', 0: 'Sun', 1: 'Moon', 2: 'Mars', 3: 'Mercury',
                  4: 'Jupiter', 5: 'Venus', 6: 'Saturn', 7: 'Rahu', 8: 'Ketu'}

    if chart_factors is None:
        chart_factors = [1, 2, 3, 4, 5, 7, 9, 10, 12, 16, 20, 24, 27, 30, 60]

    result = {}
    for dcf in chart_factors:
        key = f'D{dcf}'
        try:
            # Ensure Mean Node consistency
            const._use_true_nodes_for_rahu_ketu = False

            pp = charts.divisional_chart(jd_local, place,
                    divisional_chart_factor=dcf, chart_method=1)

            chart_data = {}
            for entry in pp:
                p_id = entry[0]
                sign_idx = int(entry[1][0])
                degree = entry[1][1] if len(entry[1]) > 1 else 0
                p_name = PLANET_MAP.get(p_id, str(p_id))
                chart_data[p_name] = {
                    'sign': SIGNS[sign_idx],
                    'sign_idx': sign_idx,
                    'degree': round(degree, 4) if isinstance(degree, float) else degree,
                }
            result[key] = chart_data
        except Exception as e:
            result[key] = {'error': str(e)}

    return result
