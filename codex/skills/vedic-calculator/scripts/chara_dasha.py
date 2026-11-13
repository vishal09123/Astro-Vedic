"""Chara Dasha (K.N. Rao method) implementation.

Rules reference: JHora "Chara dasa of K.N.Rao" dual-chart golden benchmark cross-verification (2026-07-03,
same birth data UT 1:30 and 2:30 across 2 charts with 24 total Mahadasha checkpoints, 24/24 exact match):
  1. Starting sign = Lagna sign;
  2. Progression direction = 9th house sign-footedness:
     Odd-footed {Ar,Ta,Ge,Li,Sc,Sg} -> Direct / Zodiacal (forward),
     Even-footed {Cn,Le,Vi,Cp,Aq,Pi} -> Indirect / Reverse (backward);
  3. Duration (years) = Count from sign in its own footedness direction to sign occupied by its lord, count - 1;
     Lord in own sign = 12 years;
     Dual-lord signs Scorpio (Mars/Ketu) and Aquarius (Saturn/Rahu): take max(years) between both co-lords;
  4. Year length = Sidereal solar year (approx 365.2564 days).

Note: PyJHora KN_RAO duration deviates from JHora for Sg/Aq/Pi (8/1/9 vs 7/2/8),
so we use our own verified duration logic; ascendant also has slight calibration differences,
so this module strictly expects verified engine calculation outputs.
v1 outputs Mahadasha level (sufficient for dual-system cross validation).
"""

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Odd-footed (forward count) / Even-footed (reverse count) grouping
ODD_FOOTED = {0, 1, 2, 6, 7, 8}       # Ar Ta Ge Li Sc Sg
# Sign lords (planet names consistent with engine); Sc/Aq have co-lords
SIGN_LORDS = {
    0: ['Mars'], 1: ['Venus'], 2: ['Mercury'], 3: ['Moon'],
    4: ['Sun'], 5: ['Mercury'], 6: ['Venus'], 7: ['Mars', 'Ketu'],
    8: ['Jupiter'], 9: ['Saturn'], 10: ['Saturn', 'Rahu'], 11: ['Jupiter'],
}
SIDEREAL_YEAR_DAYS = 365.256363


def _count(from_sign, to_sign, forward):
    """Count houses from from_sign to to_sign (inclusive of both ends)."""
    if forward:
        return ((to_sign - from_sign) % 12) + 1
    return ((from_sign - to_sign) % 12) + 1


def _duration_years(sign, planet_signs):
    """Single sign duration in years (KN Rao method). planet_signs: {planet_name: sign_idx}"""
    forward = sign in ODD_FOOTED
    years = []
    for lord in SIGN_LORDS[sign]:
        lord_sign = planet_signs[lord]
        if lord_sign == sign:
            years.append(12)
        else:
            years.append(_count(sign, lord_sign, forward) - 1)
    return max(years)


def calc_chara_dasha(lagna_sign_idx, planet_signs, birth_jd_ut):
    """KN Rao Chara Dasha Mahadasha timeline (one full cycle of 12 signs).

    Args:
        lagna_sign_idx: Lagna sign index from engine (0=Aries)
        planet_signs: {planet_name: sign_idx}, engine true positions (9 grahas including Rahu/Ketu)
        birth_jd_ut: Birth UT Julian Day (from engine to_jd)
    Returns:
        {'method': ..., 'direction': 'forward'/'reverse', 'mahadashas': [
            {'sign','start_jd','end_jd','years'} ...]}
    """
    ninth = (lagna_sign_idx + 8) % 12
    forward = ninth in ODD_FOOTED
    step = 1 if forward else -1

    seq = [(lagna_sign_idx + step * i) % 12 for i in range(12)]
    mds, jd = [], birth_jd_ut
    for s in seq:
        yrs = _duration_years(s, planet_signs)
        end = jd + yrs * SIDEREAL_YEAR_DAYS
        mds.append({'sign': SIGNS[s], 'sign_idx': s,
                    'start_jd': jd, 'end_jd': end, 'years': yrs})
        jd = end
    return {'method': 'Chara Dasha (K.N. Rao)',
            'direction': 'forward' if forward else 'reverse',
            'mahadashas': mds}


if __name__ == '__main__':
    # Golden benchmark self-test: JHora dual-chart (1990-08-15 Shanghai coordinates)
    import swisseph as swe
    planet_signs_common = {'Sun': 3, 'Moon': 1, 'Mars': 0, 'Mercury': 4,
                           'Jupiter': 3, 'Venus': 3, 'Saturn': 8,
                           'Rahu': 9, 'Ketu': 3}
    # Chart A: UT 2:30 -> Lagna Libra(6); JHora: Li9 Sc8 Sg7 Cp1 Aq2 Pi8 Ar12 Ta2 Ge2 Cn2 Le1 Vi1
    # Chart B: UT 1:30 -> Lagna Virgo(5); JHora: Vi1 Li9 Sc8 Sg7 Cp1 Aq2 Pi8 Ar12 Ta2 Ge2 Cn2 Le1
    expects = {
        6: [('Libra',9),('Scorpio',8),('Sagittarius',7),('Capricorn',1),('Aquarius',2),
            ('Pisces',8),('Aries',12),('Taurus',2),('Gemini',2),('Cancer',2),('Leo',1),('Virgo',1)],
        5: [('Virgo',1),('Libra',9),('Scorpio',8),('Sagittarius',7),('Capricorn',1),('Aquarius',2),
            ('Pisces',8),('Aries',12),('Taurus',2),('Gemini',2),('Cancer',2),('Leo',1)],
    }
    jd = swe.julday(1990, 8, 15, 2.5)
    ok = 0
    for lagna, exp in expects.items():
        res = calc_chara_dasha(lagna, planet_signs_common, jd)
        got = [(m['sign'], m['years']) for m in res['mahadashas']]
        match = got == exp
        ok += match
        print(f"Lagna={SIGNS[lagna]} {res['direction']}: {'PASS 12/12' if match else 'FAIL'}")
        if not match:
            for g, e in zip(got, exp):
                print(' ', g, 'vs', e, '' if g == e else '<<<')
    print('Golden benchmark verification:', f'{ok}/2 charts passed')
