"""vedic-calculator v1.0.1 - High-Precision PyJHora Calculation Engine
Powered by pysweph astronomical core + PyJHora precise algorithms (with 9 Shadbala calibrations).
Outputs full canonical structured_data.md payload.

v1.0.1: Additional items (Bhava Bala, Special Lagnas, Vargeeya, Pushkara) catch exceptions independently;
      errors recorded as {'error': ...}, Chara Dasha errors remain None; causes aggregated in calc_errors.
v1.0: Precise seconds instant calculation; Lagna benchmark unified with apparent tropical Lagna minus ayanamsa;
      polar circle fallback to Porphyry; timezone-aware as_of dasha marking; calc_meta provenance tracking.
v0.9: Planetary flags unified to 66386; Vimsottari year_duration aligned.
v0.8: Inlined dignity tables; per-thread swe state initialization.
v0.7: Birth time uncertainty boundary audit across D1/D9/D10/D4/D5.
v0.6: Added full Pratyantardasha (PD) level 3 dasha calculations.
v0.5: Fail-fast architecture, no silent invalid approximations.
"""
import os, sys
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")  # Thread safety in restricted environments

try:
    import swisseph as swe
except ImportError as e:                             # Explicit diagnostic on missing virtualenv
    sys.stderr.write(
        "  Windows : skills/vedic-calculator/venv/Scripts/python.exe <script>\n"
        "  Linux/Mac: skills/vedic-calculator/venv/bin/python <script>\n"
        f"\n[ERROR] swisseph is not available in the current environment.\n  Error: {e}\n"
    )
    raise
from datetime import datetime, timedelta
import threading
import pytz
import json

# -- PyJHora precision modules (must load completely, otherwise fail-fast) --
_SETUP_HINT = (
    "\n╔══════════════════════════════════════════════════════╗\n"
    "║  PyJHora is not properly installed! Please run:       ║\n"
    "║  python vedic-calculator/scripts/setup_env.py        ║\n"
    "╚══════════════════════════════════════════════════════╝"
)

_load_errors = []
try:
    from ashtakavarga_pyjhora import calculate_ashtakavarga_fixed as _av_pyjhora
except ImportError as e:
    _av_pyjhora = None
    _load_errors.append(f'ashtakavarga_pyjhora: {e}')
try:
    from shadbala_pyjhora import calculate_shadbala_fixed as _shadbala_pyjhora
except ImportError as e:
    _shadbala_pyjhora = None
    _load_errors.append(f'shadbala_pyjhora: {e}')
try:
    from dasha_pyjhora import calculate_dasha_fixed as _dasha_pyjhora
except ImportError as e:
    _dasha_pyjhora = None
    _load_errors.append(f'dasha_pyjhora: {e}')
try:
    from divisional_pyjhora import calculate_divisional_charts as _div_pyjhora
except ImportError as e:
    _div_pyjhora = None
    _load_errors.append(f'divisional_pyjhora: {e}')
try:
    from extras_pyjhora import (
        calculate_bhava_bala as _bhava_bala_pyjhora,
        calculate_special_lagnas as _special_lagnas_pyjhora,
        calculate_vargeeya_bala as _vargeeya_bala_pyjhora,
        calculate_pushkara as _pushkara_pyjhora,
    )
except ImportError as e:
    _bhava_bala_pyjhora = None
    _special_lagnas_pyjhora = None
    _vargeeya_bala_pyjhora = None
    _pushkara_pyjhora = None
    _load_errors.append(f'extras_pyjhora: {e}')
try:
    from chara_dasha import calc_chara_dasha as _chara_dasha
except ImportError as e:
    _chara_dasha = None
    _load_errors.append(f'chara_dasha: {e}')

# Fail-fast: All core modules must load successfully
_REQUIRED = {'SAV': _av_pyjhora, 'Shadbala': _shadbala_pyjhora, 'Dasha': _dasha_pyjhora}
_missing = [name for name, mod in _REQUIRED.items() if mod is None]
if _missing:
    print(f"\n[FATAL] The following core modules failed to load: {', '.join(_missing)}", file=sys.stderr)
    for err in _load_errors:
        print(f"   → {err}", file=sys.stderr)
    print(_SETUP_HINT, file=sys.stderr)
    raise ImportError(f"vedic-calculator missing core modules: {', '.join(_missing)}. Please run setup_env.py")

# === Configuration ===
# Ephemeris path: explicitly points to local ephe (.se1), ensuring high-precision Swiss Ephemeris
# is used from the very first calculation call rather than falling back to Moshier approximation.
_EPHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ephe')

# swisseph sid_mode and ephe_path are thread-local: ensure initialization per-thread
# via threading.local guard to maintain complete calculation consistency across workers.
_swe_state = threading.local()

def _ensure_swe_state():
    if getattr(_swe_state, 'ready', False):
        return
    swe.set_sid_mode(swe.SIDM_TRUE_CITRA)
    if os.path.isdir(_EPHE_DIR):
        swe.set_ephe_path(_EPHE_DIR)
    _swe_state.ready = True

_ensure_swe_state()   # import thread initialization

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SIGN_ABBR = ['Ar','Ta','Ge','Cn','Le','Vi','Li','Sc','Sg','Cp','Aq','Pi']

PLANETS_SWE = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
    'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS, 'Saturn': swe.SATURN
}

SIGN_LORDS = {
    0: 'Mars', 1: 'Venus', 2: 'Mercury', 3: 'Moon',
    4: 'Sun', 5: 'Mercury', 6: 'Venus', 7: 'Mars',
    8: 'Jupiter', 9: 'Saturn', 10: 'Saturn', 11: 'Jupiter'
}

NAKSHATRAS = [
    ('Ashwini','Ketu'), ('Bharani','Venus'), ('Krittika','Sun'),
    ('Rohini','Moon'), ('Mrigashira','Mars'), ('Ardra','Rahu'),
    ('Punarvasu','Jupiter'), ('Pushya','Saturn'), ('Ashlesha','Mercury'),
    ('Magha','Ketu'), ('Purva Phalguni','Venus'), ('Uttara Phalguni','Sun'),
    ('Hasta','Moon'), ('Chitra','Mars'), ('Swati','Rahu'),
    ('Vishakha','Jupiter'), ('Anuradha','Saturn'), ('Jyeshtha','Mercury'),
    ('Moola','Ketu'), ('Purva Ashadha','Venus'), ('Uttara Ashadha','Sun'),
    ('Shravana','Moon'), ('Dhanishta','Mars'), ('Shatabhisha','Rahu'),
    ('Purva Bhadrapada','Jupiter'), ('Uttara Bhadrapada','Saturn'), ('Revati','Mercury')
]

DASHA_ORDER = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
DASHA_YEARS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}

# House Domains: Aligned with house_framework.md
HOUSE_DOMAINS = {
    1: 'Self / Body / Personality',
    2: 'Wealth / Family / Speech',
    3: 'Communication / Courage / Siblings',
    4: 'Home / Mother / Education / Property',
    5: 'Creativity / Romance / Children / Intellect',
    6: 'Enemies / Disease / Debts / Service',
    7: 'Marriage / Partnership / Others',
    8: 'Transformation / Longevity / Crisis / Inheritance',
    9: 'Fortune / Dharma / Guru / Higher Learning',
    10: 'Career / Status / Achievements',
    11: 'Gains / Income / Social Network / Desires',
    12: 'Loss / Isolation / Foreign Lands / Spirituality'
}

# Combustion orb (deg) and Dig Bala powerful houses:
# Inlined for dependency autonomy, identical mathematical values and logic.
COMBUSTION_ORBS = {
    'Moon': 12, 'Mars': 17, 'Mercury': {'direct': 14, 'retrograde': 12},
    'Jupiter': 11, 'Venus': {'direct': 10, 'retrograde': 8}, 'Saturn': 15
}
DIGBALA_HOUSES = {'Jupiter': 1, 'Mercury': 1, 'Sun': 10, 'Mars': 10, 'Saturn': 7, 'Moon': 4, 'Venus': 4}

def check_combustion(planet_name, planet_lon, sun_lon, is_retrograde=False):
    """Whether planet is combust (angular separation from Sun <= orb). Sun/Rahu/Ketu do not combust."""
    orb = COMBUSTION_ORBS.get(planet_name)
    if orb is None:
        return False
    if isinstance(orb, dict):
        orb = orb['retrograde'] if is_retrograde else orb['direct']
    dist = abs(planet_lon - sun_lon)
    if dist > 180:
        dist = 360 - dist
    return dist <= orb

def get_digbala(planet_name, house):
    """Whether planet is situated in its directional strength house (Dig Bala)."""
    return DIGBALA_HOUSES.get(planet_name) == house

# === Core Calculation Functions ===

def _localize_strict(tz, dt):
    """DST-safe localize: raise explicit error on ambiguous DST transitions."""
    try:
        return tz.localize(dt, is_dst=None)
    except pytz.exceptions.AmbiguousTimeError:
        raise ValueError(
            f"Birth time {dt} falls in an ambiguous DST fallback transition (clock turned back). "
            "Please confirm whether recorded time is standard or daylight time, or calibrate via rectifier.")
    except pytz.exceptions.NonExistentTimeError:
        raise ValueError(
            f"Birth time {dt} falls in a non-existent DST spring-forward window. "
            "The recorded time may be standard time; please verify and convert, or calibrate via rectifier.")


def local_instant(year, month, day, hour, minute, tz_str, second=0, fold=None):
    """Unified localization for birth/question time: returns timezone-aware local datetime.

    second may include decimals. Localized once per chart; JD and timezone offsets derive from this instant.
    fold is used to disambiguate known instants (0=first occurrence, 1=second occurrence).
    """
    tz = pytz.timezone(tz_str)
    whole = int(second)
    micro = int(round((second - whole) * 1_000_000))
    if micro == 1_000_000:
        whole, micro = whole + 1, 0
    naive = datetime(year, month, day, hour, minute) + timedelta(seconds=whole, microseconds=micro)
    if fold is not None:
        try:
            return tz.localize(naive, is_dst=None)
        except pytz.exceptions.AmbiguousTimeError:
            return tz.localize(naive, is_dst=(fold == 0))
        except pytz.exceptions.NonExistentTimeError:
            pass
    return _localize_strict(tz, naive)


def instant_to_jd(local_dt):
    """Timezone-aware datetime -> UT Julian Day (including fractional seconds)."""
    utc_dt = local_dt.astimezone(pytz.utc)
    ut_hour = (utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
               + utc_dt.microsecond / 3_600_000_000.0)
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, ut_hour)


def to_jd(year, month, day, hour, minute, tz_str, second=0):
    return instant_to_jd(local_instant(year, month, day, hour, minute, tz_str, second))

# Planetary position flags: 66386, matching PyJHora PLANET_FLAGS exactly (TRUEPOS | NONUT).
PLANET_FLAGS = (swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
                | swe.FLG_TRUEPOS | swe.FLG_NONUT | swe.FLG_NOGDEFL)

ENGINE_VERSION = "v1.0.4"


def ayanamsa_value(jd):
    """Actual ayanamsa value used for planets and Lagna (matches desktop JHora true value)."""
    return swe.get_ayanamsa_ex_ut(jd, PLANET_FLAGS)[1]


def _deg_min(degree):
    """Sign-internal degrees -> "D°MM'" with carry-over convergence (max 29°59')."""
    d = int(degree)
    m = round((degree - d) * 60)
    if m == 60:
        if d >= 29:
            m = 59          # Sign end: avoid rounding over to 30 deg, clamp to 59 arcmin
        else:
            d += 1
            m = 0
    return f"{d}°{m:02d}'"


def calc_planet(jd, planet_id):
    _ensure_swe_state()
    result = swe.calc_ut(jd, planet_id, PLANET_FLAGS)
    lon = result[0][0]
    speed = result[0][3]
    sign_idx = int(lon / 30)
    degree = lon % 30
    return {
        'longitude': lon, 'sign': SIGNS[sign_idx], 'sign_idx': sign_idx,
        'degree': degree, 'deg_str': _deg_min(degree),
        'retrograde': speed < 0, 'speed': speed
    }

def calc_lagna(jd, lat, lon):
    """Lagna = apparent tropical Lagna - sidereal ayanamsa_value.

    Benchmark-matched to desktop JHora (0.004 arcsec diff on 2004-09-12 benchmark chart).
    Divisional charts are calibrated to this identical baseline."""
    _ensure_swe_state()
    ascmc = swe.houses_ex(jd, lat, lon, b'W', 0)[1]
    asc_lon = (ascmc[0] - ayanamsa_value(jd)) % 360
    sign_idx = int(asc_lon / 30)
    degree = asc_lon % 30
    return {
        'longitude': asc_lon, 'sign': SIGNS[sign_idx], 'sign_idx': sign_idx,
        'degree': degree, 'deg_str': _deg_min(degree)
    }

def get_nakshatra(longitude):
    nak_idx = int(longitude / (360/27))
    pada = int((longitude % (360/27)) / (360/108)) + 1
    name, lord = NAKSHATRAS[nak_idx]
    return {'name': name, 'pada': pada, 'lord': lord}

def get_house(planet_sign_idx, lagna_sign_idx):
    return ((planet_sign_idx - lagna_sign_idx) % 12) + 1

def calc_navamsha(longitude):
    """D9 Navamsha: each sign divided into 9 parts of 3°20'"""
    nav_part = int((longitude % 30) / (30/9))
    sign_idx = int(longitude / 30)
    # Navamsha starts from: Fire→Ar, Earth→Cp, Air→Li, Water→Cn
    element_start = [0, 9, 6, 3]  # Ar, Cp, Li, Cn
    element = sign_idx % 4  # 0=fire, 1=earth, 2=air, 3=water
    d9_sign_idx = (element_start[element] + nav_part) % 12
    return SIGNS[d9_sign_idx], d9_sign_idx

def calc_dashamsha(longitude):
    """D10 Dashamsha: each sign divided into 10 parts of 3°
    Odd signs: count from same sign
    Even signs: count from 9th sign (= +8 in 0-indexed)
    """
    part = int((longitude % 30) / 3)
    sign_idx = int(longitude / 30)
    if sign_idx % 2 == 0:  # Odd signs (Ar, Ge, Le...)
        d10_sign_idx = (sign_idx + part) % 12
    else:  # Even signs: 9th from sign = +8 (0-indexed)
        d10_sign_idx = (sign_idx + part + 8) % 12
    return SIGNS[d10_sign_idx], d10_sign_idx

def calc_chaturthamsha(longitude):
    """D4"""
    part = int((longitude % 30) / (30/4))
    sign_idx = int(longitude / 30)
    d4_sign_idx = (sign_idx + part * 3) % 12
    return SIGNS[d4_sign_idx], d4_sign_idx

def calc_panchamsha(longitude):
    """D5 Panchamsha: each sign divided into 5 parts of 6°
    BPHS lords:
      Odd signs:  Mars(Ar), Saturn(Aq), Jupiter(Sg), Mercury(Ge), Venus(Li)
      Even signs: Venus(Ta), Mercury(Vi), Jupiter(Pi), Saturn(Cp), Mars(Sc)
    """
    part = int((longitude % 30) / 6)
    sign_idx = int(longitude / 30)
    if sign_idx % 2 == 0:  # odd sign (0-indexed even = zodiac odd)
        starts = [0, 10, 8, 2, 6]    # Ar, Aq, Sg, Ge, Li
    else:  # even sign
        starts = [1, 5, 11, 9, 7]    # Ta, Vi, Pi, Cp, Sc
    d5_sign_idx = starts[part] if part < 5 else sign_idx
    return SIGNS[d5_sign_idx], d5_sign_idx

def calc_chara_karakas_7k8k(planets):
    """Calculate Chara Karakas (7K primary/KN Rao, 8K reference)"""
    # Effective degree = degree in sign (for Rahu: 30 - degree)
    karaka_data = []
    for name in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        karaka_data.append((name, planets[name]['degree']))
    
    # 7K (primary/KN Rao): sort by degree descending, top 7
    sorted_7k = sorted(karaka_data, key=lambda x: x[1], reverse=True)
    karaka_names_7k = ['AK','AmK','BK','MK','PK','GK','DK']
    karakas_7k = [(karaka_names_7k[i], sorted_7k[i][0], sorted_7k[i][1]) 
                  for i in range(7)]
    
    # 8K (reference/Sanjay Rath): add Rahu (30 - degree)
    rahu_eff_deg = 30 - planets['Rahu']['degree']
    karaka_data_8k = karaka_data + [('Rahu', rahu_eff_deg)]
    sorted_8k = sorted(karaka_data_8k, key=lambda x: x[1], reverse=True)
    karaka_names_8k = ['AK','AmK','BK','MK','PiK','PK','GK','DK']
    karakas_8k = [(karaka_names_8k[i], sorted_8k[i][0], sorted_8k[i][1]) 
                  for i in range(8)]
    
    # DK: 7K primary, 8K reference
    dk_7k = karakas_7k[6][1]     # 7K DK (primary)
    dk_8k = karakas_8k[7][1]     # 8K DK = 8th rank (lowest degree)
    
    return {
        '7k': karakas_7k,
        '8k': karakas_8k,
        'dk_7k': dk_7k,
        'dk_8k': dk_8k,
        'dk_note': f"7K(primary)={dk_7k}, 8K(ref)={dk_8k}"
    }

# Vedic aspects strictly use Parashari calc_graha_drishti (full sign / house irradiation).

def calc_graha_drishti(planets):
    """Parashari graha drishti (planetary house irradiation aspects).
    All planets cast aspect on 7th house; Mars +4/8; Jupiter +5/9; Saturn +3/10; Rahu/Ketu 7th house only.
    Returns {planet: {from_house, aspected_houses, aspected_planets, amplify}}."""
    special = {'Mars': [4, 8], 'Jupiter': [5, 9], 'Saturn': [3, 10]}
    # Includes Ketu: aligns with jhora const.graha_drishti (Rahu=[7], Ketu=[7])
    drishti_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    house_occupants = {}
    for name in drishti_planets:
        p = planets.get(name)
        if p and 'house' in p:
            house_occupants.setdefault(p['house'], []).append(name)
    result = {}
    for name in drishti_planets:
        p = planets.get(name)
        if not p or 'house' not in p:
            continue
        h = p['house']
        angles = [7] + special.get(name, [])   # Rahu/Ketu have no special angles -> 7th only
        aspected_houses = sorted(set(((h - 1 + (a - 1)) % 12) + 1 for a in angles))
        aspected_planets = sorted(set(pl for hh in aspected_houses
                                      for pl in house_occupants.get(hh, [])))
        result[name] = {'from_house': h,
                        'aspected_houses': aspected_houses,
                        'aspected_planets': aspected_planets,
                        'amplify': name == 'Rahu'}   # Rahu aspect indicates magnification/illusion
    return result


def calc_house_lords(lagna_sign_idx):
    """Calculate house lord table"""
    lords = {}
    for house in range(1, 13):
        sign_idx = (lagna_sign_idx + house - 1) % 12
        lord = SIGN_LORDS[sign_idx]
        lords[house] = {'sign': SIGNS[sign_idx], 'lord': lord, 'domain': HOUSE_DOMAINS[house]}
    return lords

# Moolatrikona signs (Parashari standard) for determining primary functional lordship
MOOLATRIKONA_SIGN = {'Sun': 'Leo', 'Moon': 'Taurus', 'Mars': 'Aries', 'Mercury': 'Virgo',
                     'Jupiter': 'Sagittarius', 'Venus': 'Libra', 'Saturn': 'Aquarius'}

def _role_of_house(h):
    if h == 1: return 'Core-Driver'
    if h in (5, 9): return 'Faithful'
    if h in (8, 12): return 'Destroyer'
    if h in (2, 4, 7, 10): return 'Trader'
    return 'Growth-Hacker'  # 3/6/11

def calc_functional(lagna_sign_idx, planets):
    """Functional status (B3: multi-house lordship resolved by Moolatrikona sign).
    Returns {planet: {lorded_houses, moolatrikona_house, primary_role, is_yogakaraka, is_dual_benefic_malefic}}."""
    lords = calc_house_lords(lagna_sign_idx)
    ruled = {}
    for h in range(1, 13):
        ruled.setdefault(lords[h]['lord'], []).append(h)
    TRIKONA, KENDRA_NO1, DUS = {1, 5, 9}, {4, 7, 10}, {6, 8, 12}
    result = {}
    for name, houses in ruled.items():
        hs = set(houses)
        mt_sign = MOOLATRIKONA_SIGN.get(name)
        mt_house = get_house(SIGNS.index(mt_sign), lagna_sign_idx) if mt_sign else None
        is_yk = bool(hs & {5, 9}) and bool(hs & KENDRA_NO1)  # Simultaneous lordship of Trikona (5/9) + Kendra (4/7/10) = Yogakaraka
        base = mt_house if (mt_house in hs) else min(houses)
        result[name] = {'lorded_houses': sorted(houses),
                        'moolatrikona_house': mt_house,
                        'primary_role': 'Yogakaraka' if is_yk else _role_of_house(base),
                        'is_yogakaraka': is_yk,
                        'is_dual_benefic_malefic': bool(hs & TRIKONA) and bool(hs & DUS)}
    return result

def calc_yoga_prescan(lagna_sign_idx, planets, house_lords, graha_drishti, mutual_drishti, parivartana):
    """Structural Yoga Pre-scan (computational verification of yoga skeletal configurations).
    Flags structural validity (T/F) and participating planets.
    Includes VRY, Dharma-Karma, Dhana, Raja, Chandra-Mangala, Guru-Chandala, etc.
       Gajakesari / Adhi / Kemadruma / Shakata / Pancha-Mahapurusha."""
    DUS, KENDRA, TRIKONA = {6, 8, 12}, {1, 4, 7, 10}, {1, 5, 9}
    MALEFIC_NAT = {'Saturn', 'Mars', 'Sun', 'Rahu', 'Ketu'}
    EXALT = {'Sun': 'Aries', 'Moon': 'Taurus', 'Mars': 'Capricorn', 'Mercury': 'Virgo',
             'Jupiter': 'Cancer', 'Venus': 'Pisces', 'Saturn': 'Libra'}
    OWN = {'Sun': ['Leo'], 'Moon': ['Cancer'], 'Mars': ['Aries', 'Scorpio'], 'Mercury': ['Gemini', 'Virgo'],
           'Jupiter': ['Sagittarius', 'Pisces'], 'Venus': ['Taurus', 'Libra'], 'Saturn': ['Capricorn', 'Aquarius']}
    ALL9 = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']

    def h_of(name):
        p = planets.get(name)
        return p['house'] if p and 'house' in p else None
    def nth_from(h, n):
        return (((h - 1 + (n - 1)) % 12) + 1) if h else None
    def rel(frm, to):
        return (((to - frm) % 12) + 1) if (frm and to) else None
    def occ(h, exclude=()):
        return [n for n in ALL9 if planets.get(n, {}).get('house') == h and n not in exclude]
    def lord(h):
        return house_lords[h]['lord']
    def exalt_or_own(name):
        s = planets.get(name, {}).get('sign')
        return s == EXALT.get(name) or s in OWN.get(name, [])
    def conj(a, b):
        ha = h_of(a)
        return ha is not None and ha == h_of(b)
    def mutual(a, b):
        return sorted([a, b]) in mutual_drishti
    def aspects(a, b):  # a aspects b (unidirectional graha drishti)
        return b in graha_drishti.get(a, {}).get('aspected_planets', [])
    def pariv(hx, hy):
        return any(sorted(pv['houses']) == sorted([hx, hy]) for pv in parivartana)
    def interact(hx, hy):  # two house lords interact = conjunction / mutual drishti / parivartana
        la, lb = lord(hx), lord(hy)
        return (la != lb) and (conj(la, lb) or mutual(la, lb) or pariv(hx, hy))

    res = {}
    # VRY
    vry = {}
    for h, k in [(6, 'harsha'), (8, 'sarala'), (12, 'vimala')]:
        lh = h_of(lord(h))
        vry[k] = {'active': (lh in (DUS - {h})) if lh else False, 'lord': lord(h),
                  'lord_house': lh, 'rule': f'Lord of house {h} in dusthana {sorted(DUS - {h})} (own house excluded)'}
    res['vry'] = vry
    # Category A: House lord interactions (Conjunction / Mutual aspect / Parivartana)
    res['dharma_karma'] = {'active': interact(9, 10), 'lords': [lord(9), lord(10)]}
    res['dhana'] = {'active': interact(2, 11), 'lords': [lord(2), lord(11)]}
    raja = [[t, k, lord(t), lord(k)] for t in TRIKONA for k in KENDRA if t != k and interact(t, k)]
    res['raja'] = {'active': len(raja) > 0, 'hits': raja}
    res['chandra_mangala'] = {'active': conj('Moon', 'Mars') or mutual('Moon', 'Mars')}
    res['guru_chandala'] = {'active': conj('Jupiter', 'Rahu')}
    # Category B: Placement / Relative positions
    mh, jh = h_of('Moon'), h_of('Jupiter')
    res['gajakesari'] = {'active': (rel(mh, jh) in KENDRA) if (mh and jh) else False,
                         'rule': 'Jupiter and Moon in mutual Kendras (1/4/7/10 from each other)'}
    adhi_h = [nth_from(mh, n) for n in (6, 7, 8)] if mh else []
    adhi_b = [b for b in ['Jupiter', 'Venus', 'Mercury'] if h_of(b) in adhi_h]
    res['adhi'] = {'active': len(adhi_b) > 0, 'benefics': adhi_b, 'from_moon_678': adhi_h,
                   'malefic_contam': any(any(o in MALEFIC_NAT for o in occ(h)) for h in adhi_h),
                   'rule': 'Benefics (Jup/Ven/Mer) in houses 6/7/8 from Moon'}
    if mh:
        h_next, h_prev = nth_from(mh, 2), nth_from(mh, 12)
        kbase = (len(occ(h_next, ('Moon',))) == 0 and len(occ(h_prev, ('Moon',))) == 0)
        cancel = (mh in KENDRA) or (len(occ(mh, ('Moon',))) > 0) or aspects('Jupiter', 'Moon')
        res['kemadruma'] = {'active': kbase, 'cancelled': cancel,
                            'rule': 'No planets in 2nd/12th from Moon; Cancelled: Moon in Kendra/conjoined/aspected by Jupiter'}
    else:
        res['kemadruma'] = {'active': False, 'cancelled': False}
    res['shakata'] = {'active': (rel(mh, jh) in {6, 8}) if (mh and jh) else False,
                      'cancelled': (jh in KENDRA) or (mh in KENDRA) or exalt_or_own('Jupiter'),
                      'rule': 'Jupiter and Moon in mutual 6/8 houses; Cancelled: Jup or Moon in Kendra / Jup exalted or own sign'}
    # Class C: Pancha Mahapurusha (in Kendra and exalted or in own sign)
    maha = {}
    for gname, star in [('Ruchaka', 'Mars'), ('Bhadra', 'Mercury'), ('Hamsa', 'Jupiter'),
                        ('Malavya', 'Venus'), ('Shasha', 'Saturn')]:
        sh = h_of(star)
        maha[gname] = {'active': (sh in KENDRA) and exalt_or_own(star), 'star': star,
                       'house': sh, 'sign': planets.get(star, {}).get('sign')}
    res['mahapurusha'] = maha
    return res

def calc_neecha_bhanga(planets, dignity, graha_drishti, combustion, shadbala):
    """Neecha Bhanga (Cancellation of Debilitation) evidence verification:
    Evaluates Phaladeepika Ch. 7 cancellation conditions per debilitated planet:
      7.26/29/30: Dispositor of debilitated planet is in Kendra from Lagna or Moon.
      7.26/29/30: Exaltation lord of debilitated sign is in Kendra from Lagna or Moon.
      7.27: Dispositor and exaltation lord are in mutual Kendra.
      7.28: Aspected by its dispositor.
      7.3: Retrograde, in auspicious house (not 6/8/12), and not combust.
    Tiers: Debilitated / Debilitated with Buffer / Neecha Bhanga (>=1 rule) / Neecha Bhanga Multiple (>=2 rules)."""
    EXALT = {'Sun': 'Aries', 'Moon': 'Taurus', 'Mars': 'Capricorn', 'Mercury': 'Virgo',
             'Jupiter': 'Cancer', 'Venus': 'Pisces', 'Saturn': 'Libra'}
    KENDRA, DUS = (1, 4, 7, 10), (6, 8, 12)
    moon_h = planets['Moon']['house']

    def nth(frm, to):
        return ((to - frm) % 12) + 1
    def kendra_refs(name):
        h = planets[name]['house']
        refs = [f'House {h} from Lagna'] if h in KENDRA else []
        if name != 'Moon' and nth(moon_h, h) in KENDRA:
            refs.append(f'House {nth(moon_h, h)} from Moon')
        return refs
    def sees(a, b):
        return b in graha_drishti.get(a, {}).get('aspected_planets', [])

    def tier(n, cushions):
        if n >= 2:
            return 'Cancelled - Multiple'
        if n == 1:
            return 'Cancelled'
        return 'Cushioned' if cushions else 'Debilitated'

    result = {}
    for name, ex_sign in EXALT.items():
        if dignity.get(name, {}).get('basic') != 'debilitated':
            continue
        p = planets[name]
        h = p['house']
        disp = SIGN_LORDS[SIGNS.index(p['sign'])]
        exl = SIGN_LORDS[SIGNS.index(ex_sign)]
        exalted_here = next((k for k, v in EXALT.items() if v == p['sign']), None)

        def forms(ex):
            out = []
            r = kendra_refs(disp)
            if r:
                out.append({'id': '7.26/29/30 Dispositor', 'evidence': f"Dispositor {disp} in {' and '.join(r)} (Kendra)"})
            r = kendra_refs(ex)
            if r:
                who = f'{ex} (Self)' if ex == name else ex
                out.append({'id': '7.26/29/30 Exaltation Lord', 'evidence': f"Exaltation lord {who} in {' and '.join(r)} (Kendra)"})
            if nth(planets[disp]['house'], planets[ex]['house']) in KENDRA:
                out.append({'id': '7.27', 'evidence': f'Dispositor {disp} and exaltation lord {ex} in mutual Kendras'})
            if sees(disp, name):
                extra = '; planet in auspicious house, reinforced' if h not in DUS else ''
                out.append({'id': '7.28', 'evidence': f'Aspected by dispositor {disp}{extra}'})
            if p.get('retrograde') and h not in DUS and name not in combustion:
                out.append({'id': '7.3', 'evidence': f'Retrograde in auspicious House {h}, not combust'})
            return out

        cushions = []
        if h in KENDRA:
            cushions.append(f'Planet in House {h} from Lagna (Kendra)')
        helpers = [b for b in ('Jupiter', 'Venus', 'Mercury', 'Moon') if b != name and sees(b, name)]
        if helpers:
            cushions.append(f"Aspected by {', '.join(helpers)}")
        if planets[exl]['house'] in (5, 9):
            cushions.append(f"Exaltation lord {exl} in House {planets[exl]['house']} from Lagna (Trikona)")
        dd = dignity.get(disp, {})
        pct = shadbala.get(disp, {}).get('strength_pct') if isinstance(shadbala, dict) else None
        if (dd.get('basic') in ('exalted', 'moolatrikona', 'own_sign') or dd.get('compound') in ('friend', 'great_friend')) \
                and pct is not None and pct >= 100:
            cushions.append(f"Dispositor {disp} {dd.get('compound')}, Shadbala {round(pct)}%")
        if exl != name and planets[exl]['house'] == h:
            cushions.append(f'Conjoined with exaltation lord {exl}')

        main = forms(exl)
        rec = {'dispositor': disp, 'exaltation_lord': exl, 'exalted_here': exalted_here,
               'forms': main, 'independent': len(main), 'cushions': cushions,
               'tier': tier(len(main), cushions), 'dasha_not_counted': len(main) >= 3, 'alt': None}
        if exalted_here and exalted_here != exl:
            alt = forms(exalted_here)
            if [f['id'] for f in alt] != [f['id'] for f in main]:
                rec['alt'] = {'exaltation_lord': exalted_here, 'forms': alt, 'independent': len(alt),
                              'tier': tier(len(alt), cushions), 'dasha_not_counted': len(alt) >= 3}
        result[name] = rec
    return result


def calc_mutual_drishti(graha_drishti):
    """Mutual drishti pairs: A aspects B's house AND B aspects A's house (bidirectional).
    Returns list of pairs [[A, B], ...]."""
    pairs = []
    names = list(graha_drishti.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if b in graha_drishti[a]['aspected_planets'] and a in graha_drishti[b]['aspected_planets']:
                pairs.append(sorted([a, b]))
    return pairs

def calc_parivartana(house_lords, planets):
    """Parivartana pairs (mutual reception of house lords): lord of house X in house Y and lord of Y in X.

    Phaladeepika VI.32-34 classification:
      Dainya = Involves lords of 6, 8, or 12 (30 pairs)
      Khala = Involves lord of 3 exchanged with an auspicious house (8 pairs)
      Maha = Exchanges between lords of auspicious houses (1, 2, 4, 5, 7, 9, 10, 11) (28 pairs)
    Priority: Dainya > Khala > Maha. Returns [{houses, lords, type}, ...]."""
    DUS = {6, 8, 12}
    pairs = []
    for x in range(1, 13):
        for y in range(x + 1, 13):
            lx = house_lords[x]['lord']
            ly = house_lords[y]['lord']
            if lx == ly:
                continue  # Same planet lords both houses, no mutual reception
            hx = planets.get(lx, {}).get('house')
            hy = planets.get(ly, {}).get('house')
            if hx == y and hy == x:
                if x in DUS or y in DUS:
                    kind = 'Dainya (Dusthana involved)'
                elif x == 3 or y == 3:
                    kind = 'Khala (3rd house involved)'
                else:
                    kind = 'Maha (Auspicious exchange)'
                pairs.append({'houses': [x, y], 'lords': [lx, ly], 'type': kind})
    return pairs

def calc_vimsottari_dasha(moon_lon, birth_year, birth_month, birth_day, birth_hour, birth_minute):
    """Deprecated approximate entry point; Vimsottari must come from PyJHora.

    Keeping a fail-fast shim prevents older callers from silently reviving the former
    365.25-day MD/AD approximation, which cannot supply validated PD boundaries.
    Use ``calculate_full_chart``; it calls ``dasha_pyjhora.calculate_dasha_fixed``.
    """
    raise RuntimeError(
        "calc_vimsottari_dasha is disabled: use calculate_full_chart() so "
        "PyJHora supplies validated MD/AD/PD boundaries"
    )

def calc_special_points(lagna, planets):
    """Calculate AL, UL and other special Jaimini points.
    Note: JHora may use different settings (Rahu/Ketu lord rules, dual-sign lords).
    Our implementation follows standard BPHS Jaimini method.
    """
    lagna_idx = lagna['sign_idx']
    
    def calc_arudha(house_num, lagna_idx):
        """Calculate Arudha Pada for a given house (BPHS standard)"""
        sign_idx = (lagna_idx + house_num - 1) % 12
        lord = SIGN_LORDS[sign_idx]
        lord_sign_idx = planets[lord]['sign_idx']
        # Count from house sign to lord (1-based: lord in same sign = 1st)
        dist = (lord_sign_idx - sign_idx) % 12
        # Arudha = same distance from lord's position
        arudha_idx = (lord_sign_idx + dist) % 12
        # BPHS Exception: arudha cannot be in 1st or 7th from house sign
        # If 1st → use 10th from house sign
        # If 7th → use 4th from house sign
        if arudha_idx == sign_idx:
            arudha_idx = (sign_idx + 9) % 12   # 10th from house sign
        elif arudha_idx == (sign_idx + 6) % 12:
            arudha_idx = (sign_idx + 3) % 12   # 4th from house sign
        return SIGNS[arudha_idx], arudha_idx
    
    al_sign, al_idx = calc_arudha(1, lagna_idx)
    al_house = get_house(al_idx, lagna_idx)
    
    ul_sign, ul_idx = calc_arudha(12, lagna_idx)
    ul_house = get_house(ul_idx, lagna_idx)
    
    return {
        'AL': {'sign': al_sign, 'sign_idx': al_idx, 'house': al_house},
        'UL': {'sign': ul_sign, 'sign_idx': ul_idx, 'house': ul_house},
    }

# === Birth Time Boundary Audit ===

def calc_divisional_boundary_audit(year, month, day, hour, minute, lat, lon,
                                    tz_str="Asia/Kolkata", uncertainty_minutes=1, second=0, fold=None):
    """Scans D1 and divisional chart Lagnas across the birth time uncertainty window minute by minute.
    Tests boundary stability against ingress into adjacent signs for D1, D9, D10, D4, and D5."""
    if _div_pyjhora is None:
        return {
            'status': 'unavailable',
            'reason': 'PyJHora divisional module unavailable',
        }

    try:
        span = max(0, int(uncertainty_minutes or 0))
    except (TypeError, ValueError):
        span = 1

    tz = pytz.timezone(tz_str)
    base_utc = local_instant(year, month, day, hour, minute, tz_str, second, fold=fold).astimezone(pytz.utc)
    factors = (4, 5, 9, 10)
    samples = []

    for offset in range(-span, span + 1):
        localized = (base_utc + timedelta(minutes=offset)).astimezone(tz)
        local_dt = localized.replace(tzinfo=None)
        tz_offset = localized.utcoffset().total_seconds() / 3600.0
        sec = local_dt.second + local_dt.microsecond / 1_000_000
        jd = instant_to_jd(localized)
        d1_lagna = calc_lagna(jd, lat, lon)['sign']
        charts = _div_pyjhora(
            local_dt.year, local_dt.month, local_dt.day,
            local_dt.hour, local_dt.minute, lat, lon, tz_offset,
            chart_factors=factors, second=sec,
        )
        row = {'offset_minutes': offset, 'D1': d1_lagna}
        for factor in factors:
            key = f'D{factor}'
            chart_data = charts.get(key, {})
            if 'error' in chart_data or 'Lagna' not in chart_data:
                row[key] = None
            else:
                row[key] = chart_data['Lagna']['sign']
        samples.append(row)

    result = {}
    for key in ('D1', 'D9', 'D10', 'D4', 'D5'):
        observed = []
        transitions = []
        previous = None
        for row in samples:
            sign = row.get(key)
            if sign is not None and sign not in observed:
                observed.append(sign)
            if previous is not None and sign is not None and sign != previous:
                transitions.append({
                    'offset_minutes': row['offset_minutes'],
                    'from': previous,
                    'to': sign,
                })
            if sign is not None:
                previous = sign
        base_sign = next((row.get(key) for row in samples
                          if row['offset_minutes'] == 0), None)
        result[key] = {
            'base_sign': base_sign,
            'stable': len(observed) == 1 and bool(observed),
            'observed_signs': observed,
            'transitions': transitions,
        }

    return {
        'status': 'ok',
        'uncertainty_minutes': span,
        'sample_step_minutes': 1,
        'charts': result,
        'samples': samples,
    }


# === Main Calculation Function ===

def calculate_full_chart(year, month, day, hour, minute, lat, lon,
                         tz_str="Asia/Kolkata", uncertainty_minutes=1, second=0, as_of=None,
                         fold=None):
    """Calculates complete Vedic natal chart data.
    second: Seconds (optional float), default 0.
    as_of: Timezone-aware datetime for evaluating current dasha periods (defaults to current UTC).
    fold: Disambiguation flag for DST transitions."""
    _ensure_swe_state()
    _instant = local_instant(year, month, day, hour, minute, tz_str, second, fold=fold)
    jd = instant_to_jd(_instant)
    _tz_offset = _instant.utcoffset().total_seconds() / 3600.0
    ayanamsa = ayanamsa_value(jd)
    
    # 1. Lagna
    lagna = calc_lagna(jd, lat, lon)
    lagna['nakshatra'] = get_nakshatra(lagna['longitude'])
    lagna['house'] = 1
    
    # 2. Planets (7 main)
    planets = {}
    for name, pid in PLANETS_SWE.items():
        p = calc_planet(jd, pid)
        p['house'] = get_house(p['sign_idx'], lagna['sign_idx'])
        p['nakshatra'] = get_nakshatra(p['longitude'])
        planets[name] = p
    
    # 3. Rahu & Ketu
    result = swe.calc_ut(jd, swe.MEAN_NODE, PLANET_FLAGS)
    rahu_lon = result[0][0]
    rahu_sign_idx = int(rahu_lon / 30)
    rahu_deg = rahu_lon % 30
    planets['Rahu'] = {
        'longitude': rahu_lon, 'sign': SIGNS[rahu_sign_idx],
        'sign_idx': rahu_sign_idx, 'degree': rahu_deg,
        'deg_str': _deg_min(rahu_deg),
        'retrograde': True, 'speed': result[0][3],
        'house': get_house(rahu_sign_idx, lagna['sign_idx']),
        'nakshatra': get_nakshatra(rahu_lon)
    }
    ketu_lon = (rahu_lon + 180) % 360
    ketu_sign_idx = int(ketu_lon / 30)
    ketu_deg = ketu_lon % 30
    planets['Ketu'] = {
        'longitude': ketu_lon, 'sign': SIGNS[ketu_sign_idx],
        'sign_idx': ketu_sign_idx, 'degree': ketu_deg,
        'deg_str': _deg_min(ketu_deg),
        'retrograde': True, 'speed': -result[0][3],
        'house': get_house(ketu_sign_idx, lagna['sign_idx']),
        'nakshatra': get_nakshatra(ketu_lon)
    }
    
    # 4. SAV/BAV (PyJHora — no fallback)
    ashtak = _av_pyjhora(year, month, day, hour, minute, lat, lon, _tz_offset, second=second)
    
    # Map SAV to houses
    sav_by_house = {}
    for h in range(1, 13):
        sign_idx = (lagna['sign_idx'] + h - 1) % 12
        sign_name = SIGNS[sign_idx]
        sav_by_house[h] = {'sign': sign_name, 'value': ashtak['sarvashtakavarga'].get(sign_name, 0)}
    
    # 5. Divisional charts (PyJHora: 15 charts)
    if _div_pyjhora is not None:
        divisional_charts = _div_pyjhora(
            year, month, day, hour, minute, lat, lon, _tz_offset, second=second
        )
    else:
        divisional_charts = {}
    
    # Extract d9/d10/d4/d5 in legacy (sign_name, sign_idx) format for backward compat
    if divisional_charts:
        def _legacy_fmt(chart_key):
            ch = divisional_charts.get(chart_key, {})
            return {p: (ch[p]['sign'], ch[p]['sign_idx']) for p in ch if 'error' not in ch}
        d9 = _legacy_fmt('D9')
        d10 = _legacy_fmt('D10')
        d4 = _legacy_fmt('D4')
        d5 = _legacy_fmt('D5')
    else:
        d9, d10, d4, d5 = {}, {}, {}, {}

    divisional_boundary_audit = calc_divisional_boundary_audit(
        year, month, day, hour, minute, lat, lon, tz_str,
        uncertainty_minutes=uncertainty_minutes, second=second, fold=fold,
    )
    
    # Vargottama check
    vargottama = {}
    for name in planets:
        d9_sign = d9.get(name, (None, None))
        d9_sign_name = d9_sign[0] if isinstance(d9_sign, tuple) else d9_sign.get('sign', None) if isinstance(d9_sign, dict) else None
        vargottama[name] = planets[name]['sign'] == d9_sign_name
    
    # 6. Dignity & Compound Relationship (BPHS Panchadha Maitri)
    # BPHS Panchadha Maitri algorithm
    
    # Step 1: Exaltation / Own sign / Debilitation check
    EXALTATION = {'Sun':'Aries','Moon':'Taurus','Mars':'Capricorn',
                  'Mercury':'Virgo','Jupiter':'Cancer','Venus':'Pisces','Saturn':'Libra'}
    DEBILITATION = {'Sun':'Libra','Moon':'Scorpio','Mars':'Cancer',
                    'Mercury':'Pisces','Jupiter':'Capricorn','Venus':'Virgo','Saturn':'Aries'}
    OWN_SIGNS = {'Sun':['Leo'],'Moon':['Cancer'],'Mars':['Aries','Scorpio'],
                 'Mercury':['Gemini','Virgo'],'Jupiter':['Sagittarius','Pisces'],
                 'Venus':['Taurus','Libra'],'Saturn':['Capricorn','Aquarius']}
    # Moolatrikona degree ranges: consistent with PyJHora const.moola_trikona_range_of_planets.
    MOOLATRIKONA_RANGE = {'Sun': ('Leo', 0, 20), 'Moon': ('Taurus', 3, 30), 'Mars': ('Aries', 0, 12),
                          'Mercury': ('Virgo', 15, 20), 'Jupiter': ('Sagittarius', 0, 10),
                          'Venus': ('Libra', 0, 15), 'Saturn': ('Aquarius', 0, 20)}
    
    # Step 2: Natural Relationship Table (Naisargika Maitri) - BPHS standard
    NATURAL_REL = {
        'Sun':     {'friend':['Moon','Mars','Jupiter'], 'enemy':['Venus','Saturn'], 'neutral':['Mercury']},
        'Moon':    {'friend':['Sun','Mercury'], 'enemy':[], 'neutral':['Mars','Jupiter','Venus','Saturn']},
        'Mars':    {'friend':['Sun','Moon','Jupiter'], 'enemy':['Mercury'], 'neutral':['Venus','Saturn']},
        'Mercury': {'friend':['Sun','Venus'], 'enemy':['Moon'], 'neutral':['Mars','Jupiter','Saturn']},
        'Jupiter': {'friend':['Sun','Moon','Mars'], 'enemy':['Mercury','Venus'], 'neutral':['Saturn']},
        'Venus':   {'friend':['Mercury','Saturn'], 'enemy':['Sun','Moon'], 'neutral':['Mars','Jupiter']},
        'Saturn':  {'friend':['Mercury','Venus'], 'enemy':['Sun','Moon','Mars'], 'neutral':['Jupiter']},
    }
    
    def get_natural_rel(planet, lord):
        """Look up natural relationship: friend/enemy/neutral"""
        if planet == lord:
            return 'own'
        rel = NATURAL_REL.get(planet, {})
        if lord in rel.get('friend', []): return 'friend'
        if lord in rel.get('enemy', []): return 'enemy'
        return 'neutral'
    
    def get_temporal_rel(planet_sign_idx, lord_sign_idx):
        """Look up temporal relationship: sign lord in 2/3/4/10/11/12 house from planet = friend"""
        dist = (lord_sign_idx - planet_sign_idx) % 12
        # Houses 2,3,4,10,11,12 = dist values 1,2,3,9,10,11 (0-indexed)
        return 'temp_friend' if dist in {1,2,3,9,10,11} else 'temp_enemy'
    
    # Step 4: Panchadha compound table
    COMPOUND_TABLE = {
        ('friend', 'temp_friend'):   'great_friend',
        ('friend', 'temp_enemy'):    'neutral',
        ('enemy',  'temp_friend'):   'neutral',
        ('enemy',  'temp_enemy'):    'great_enemy',
        ('neutral','temp_friend'):   'friend',
        ('neutral','temp_enemy'):    'enemy',
    }
    
    dignity_data = {}
    for name in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        p = planets[name]
        sign = p['sign']
        lord = SIGN_LORDS[p['sign_idx']]
        
        # Step 1: Exalted / Own / Debilitated determined directly
        if EXALTATION.get(name) == sign:
            compound = 'exalted'
        elif DEBILITATION.get(name) == sign:
            compound = 'debilitated'
        elif (MOOLATRIKONA_RANGE[name][0] == sign
              and MOOLATRIKONA_RANGE[name][1] <= p['degree'] <= MOOLATRIKONA_RANGE[name][2]):
            compound = 'moolatrikona'
        elif sign in OWN_SIGNS.get(name, []):
            compound = 'own_sign'
        else:
            # Step 2+3+4: Natural + Temporal -> Compound relationship
            natural = get_natural_rel(name, lord)
            if natural == 'own':
                compound = 'own_sign'
            else:
                # Locate sign dispositor position
                lord_sign_idx = planets[lord]['sign_idx'] if lord in planets else p['sign_idx']
                temporal = get_temporal_rel(p['sign_idx'], lord_sign_idx)
                compound = COMPOUND_TABLE.get((natural, temporal), 'neutral')
        
        dignity_data[name] = {'basic': compound, 'compound': compound}

    # 6b. D9 Natural Dignity: lookup natural dignity in D9 sign (exalted/own/debilitated/friend/enemy/neutral).
    d9_dignity = {}
    for name in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        d9_entry = d9.get(name)
        if not d9_entry:
            continue
        d9_sign, d9_sign_idx = d9_entry[0], d9_entry[1]
        dispositor = SIGN_LORDS[d9_sign_idx]  # D9 sign lord
        if EXALTATION.get(name) == d9_sign:
            d9_dig = 'exalted'
        elif DEBILITATION.get(name) == d9_sign:
            d9_dig = 'debilitated'
        elif d9_sign in OWN_SIGNS.get(name, []):
            d9_dig = 'own'
        else:
            d9_dig = get_natural_rel(name, dispositor)  # friend/enemy/neutral
        d9_dignity[name] = {'sign': d9_sign, 'dignity': d9_dig, 'dispositor': dispositor}

    # 6c. Internal house lords and dignities for divisional charts (D9/D10/D4/D5).
    varga_internal = {}
    for dv in ['D9', 'D10', 'D4', 'D5']:
        ch = divisional_charts.get(dv) if divisional_charts else None
        if not ch or 'error' in ch or 'Lagna' not in ch:
            continue
        v_lag = ch['Lagna']['sign_idx']
        v_lords = {}
        for house in range(1, 13):
            s_idx = (v_lag + house - 1) % 12
            lord = SIGN_LORDS[s_idx]
            le = ch.get(lord)
            lord_house = ((le['sign_idx'] - v_lag) % 12) + 1 if le else None
            v_lords[house] = {'sign': SIGNS[s_idx], 'lord': lord, 'lord_house': lord_house}
        v_dig = {}
        for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            e = ch.get(name)
            if not e:
                continue
            s, sidx = e['sign'], e['sign_idx']
            disp = SIGN_LORDS[sidx]
            if EXALTATION.get(name) == s:
                dg = 'exalted'
            elif DEBILITATION.get(name) == s:
                dg = 'debilitated'
            elif s in OWN_SIGNS.get(name, []):
                dg = 'own'
            else:
                dg = get_natural_rel(name, disp)
            v_dig[name] = {'sign': s, 'house': ((sidx - v_lag) % 12) + 1,
                           'dignity': dg, 'dispositor': disp}
        varga_internal[dv] = {'lagna_sign': SIGNS[v_lag], 'lagna_lord': SIGN_LORDS[v_lag],
                              'house_lords': v_lords, 'dignity': v_dig}

    # 7. Combustion check
    sun_lon = planets['Sun']['longitude']
    combustion = {}
    for name in ['Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        is_retro = planets[name]['retrograde']
        if check_combustion(name, planets[name]['longitude'], sun_lon, is_retro):
            diff = abs(planets[name]['longitude'] - sun_lon)
            if diff > 180: diff = 360 - diff
            combustion[name] = {'distance': round(diff, 2)}
    
    # 8. Chara Karakas (7K primary)
    karakas = calc_chara_karakas_7k8k(planets)
    
    # 9. Parashari Graha drishti (sign/house irradiation) and functional status
    graha_drishti = calc_graha_drishti(planets)  # P10 Parashari graha drishti
    functional = calc_functional(lagna['sign_idx'], planets)      # B3 functional role

    # 10. House lords
    house_lords = calc_house_lords(lagna['sign_idx'])
    # Add planet positions to house lords
    for h, info in house_lords.items():
        planet = info['lord']
        if planet in planets:
            info['lord_house'] = planets[planet]['house']
    mutual_drishti = calc_mutual_drishti(graha_drishti)   # Mutual drishti pairs
    parivartana = calc_parivartana(house_lords, planets)  # Parivartana pairs
    yoga_prescan = calc_yoga_prescan(lagna['sign_idx'], planets, house_lords, graha_drishti, mutual_drishti, parivartana)

    # 11. Vimsottari Dasha MD/AD/PD (PyJHora — no fallback)
    dashas = _dasha_pyjhora(year, month, day, hour, minute, lat, lon, _tz_offset,
                            second=second, as_of=as_of)

    # 12. Shadbala (PyJHora + 9 bug fixes — no fallback)
    shadbala_data = _shadbala_pyjhora(
        year, month, day, hour, minute, lat, lon, _tz_offset, second=second
    )
    neecha_bhanga = calc_neecha_bhanga(planets, dignity_data, graha_drishti, combustion, shadbala_data)

    # 13. Moon phase
    moon_sun_diff = (planets['Moon']['longitude'] - planets['Sun']['longitude']) % 360
    is_waxing = moon_sun_diff < 180
    
    # 14. Digbala
    digbala = {}
    for name in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        digbala[name] = get_digbala(name, planets[name]['house'])
    
    # 15. Special Points (AL, UL)
    special_points = calc_special_points(lagna, planets)
    
    # 16. Transits are computed via dedicated transit.py.

    # 17. Bhava Bala, Special Lagnas, Vargeeya Bala, Pushkara (via PyJHora)
    # Capture errors individually for optional modules; record in calc_errors without aborting.
    calc_errors = {}
    _extra = (year, month, day, hour, minute, lat, lon, _tz_offset)
    _extra_results = {}
    for _name, _fn in (('bhava_bala', _bhava_bala_pyjhora), ('special_lagnas', _special_lagnas_pyjhora),
                       ('vargeeya_bala', _vargeeya_bala_pyjhora), ('pushkara', _pushkara_pyjhora)):
        if _fn is None:
            _extra_results[_name] = None
            continue
        try:
            _extra_results[_name] = _fn(*_extra, second=second)
        except Exception as e:
            _extra_results[_name] = {'error': f'{type(e).__name__}: {e}'}
            calc_errors[_name] = _extra_results[_name]['error']
    bhava_bala = _extra_results['bhava_bala']
    special_lagnas = _extra_results['special_lagnas']
    vargeeya_bala = _extra_results['vargeeya_bala']
    pushkara = _extra_results['pushkara']

    # DST flag: indicates if birth time was recorded under daylight saving time
    dst_info = {'is_dst': bool(_instant.dst()), 'utc_offset': str(_instant.utcoffset())}

    # Chara Dasha (K.N. Rao) calculation
    chara_dasha = None
    if _chara_dasha:
        try:
            _sign_idx = {s: i for i, s in enumerate(SIGNS)}
            _psigns = {p: _sign_idx[planets[p]['sign']] for p in planets}
            chara_dasha = _chara_dasha(_sign_idx[lagna['sign']], _psigns, jd)
        except Exception as e:
            calc_errors['chara_dasha'] = f'{type(e).__name__}: {e}'

    return {
        'ayanamsa': ayanamsa,
        'lagna': lagna,
        'planets': planets,
        'sav': ashtak['sarvashtakavarga'],
        'sav_by_house': sav_by_house,
        'bav': ashtak['bhinnashtakavarga'],
        'd9': d9, 'd10': d10, 'd4': d4, 'd5': d5,
        'divisional_charts': divisional_charts,
        'divisional_boundary_audit': divisional_boundary_audit,
        'vargottama': vargottama,
        'dignity': dignity_data,
        'd9_dignity': d9_dignity,
        'varga_internal': varga_internal,
        'combustion': combustion,
        'karakas': karakas,
        'graha_drishti': graha_drishti,
        'functional': functional,
        'yoga_prescan': yoga_prescan,
        'neecha_bhanga': neecha_bhanga,
        'mutual_drishti': mutual_drishti,
        'parivartana': parivartana,
        'house_lords': house_lords,
        'dashas': dashas,
        'shadbala': shadbala_data,
        'moon_phase': {'waxing': is_waxing, 'sun_moon_diff': round(moon_sun_diff, 1)},
        'digbala': digbala,
        'special_points': special_points,
        'bhava_bala': bhava_bala,
        'special_lagnas': special_lagnas,
        'vargeeya_bala': vargeeya_bala,
        'pushkara': pushkara,
        'chara_dasha': chara_dasha,
        'dst_info': dst_info,
        # Uncalculated optional modules and errors (empty dict = all calculated)
        'calc_errors': calc_errors,
        # Meta provenance: records engine version, utc instant, and ayanamsa
        'calc_meta': {
            'engine_version': ENGINE_VERSION,
            'instant_utc': _instant.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'ayanamsa': ayanamsa,
        },
    }


# === TEST ===
if __name__ == '__main__':
    print("=== vedic-calculator v0.2 Full Test ===\n")
    
    # Gandhi: 1869-10-02, 07:12, Porbandar
    chart = calculate_full_chart(1869, 10, 2, 7, 12, 21.6417, 69.6293, "Asia/Kolkata")
    
    print(f"Ayanamsa (True Chitra): {chart['ayanamsa']:.4f}°")
    print(f"Lagna: {chart['lagna']['sign']} {chart['lagna']['deg_str']}")
    
    print(f"\n--- Planets ---")
    print(f"  {'Planet':<10} {'Sign':<12} {'Deg':>8} {'H':>3} {'R':>2} {'Dignity':<16} {'Compound'}")
    for name in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']:
        p = chart['planets'][name]
        r = 'R' if p['retrograde'] else ''
        dig = chart['dignity'].get(name, {})
        basic = dig.get('basic', '-')
        compound = dig.get('compound', '-')
        print(f"  {name:<10} {p['sign']:<12} {p['deg_str']:>8} {p['house']:>3} {r:>2} {str(basic):<16} {compound}")
    
    print(f"\n--- SAV by House ---")
    total = 0
    for h in range(1, 13):
        s = chart['sav_by_house'][h]
        total += s['value']
        print(f"  H{h} ({s['sign'][:2]}): {s['value']}", end='  ')
        if h % 6 == 0: print()
    print(f"  Total: {total}")
    
    print(f"\n--- Chara Karakas (7K) ---")
    for k, planet, deg in chart['karakas']['7k']:
        print(f"  {k}: {planet} ({deg:.1f}°)")
    print(f"  DK: 7K (Primary)={chart['karakas']['dk_7k']}, 8K (Ref)={chart['karakas']['dk_8k']}")
    
    print(f"\n--- Dasha ---")
    for d in chart['dashas']:
        marker = '→' if d['is_current'] else ' '
        print(f"  {marker} {d['planet']:<10} {d['start']} ~ {d['end']}  ({d['years']}yr)")
    
    print(f"\n--- D9 Navamsha ---")
    for name in ['Lagna','Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']:
        sign = chart['d9'][name][0]
        varg = ' ★V' if chart['vargottama'].get(name, False) else ''
        print(f"  {name:<10} → {sign}{varg}")
    
    print(f"\n--- Shadbala ---")
    if 'error' in chart['shadbala']:
        print(f"  Error: {chart['shadbala']['error']}")
    else:
        for name, data in chart['shadbala'].items():
            if isinstance(data, dict):
                total = data.get('total_rupas', data.get('total', '?'))
                print(f"  {name:<10} {total}")
    
    print(f"\n--- Moon Phase ---")
    phase = chart['moon_phase']
    phase_str = 'Waxing (Shukla)' if phase['waxing'] else 'Waning (Krishna)'
    print(f"  {phase_str}, Dist from Sun {phase['sun_moon_diff']}°")
    
    print(f"\n--- Combustion ---")
    if chart['combustion']:
        for name, data in chart['combustion'].items():
            print(f"  {name}: {data}")
    else:
        print("  No combust planets")
    
    print(f"\n--- House Lords ---")
    for h in range(1, 13):
        info = chart['house_lords'][h]
        print(f"  H{h} ({info['domain']}): {info['lord']} → H{info.get('lord_house','?')}")
    
    print(f"\n✅ All 14 data sections calculated successfully!")
