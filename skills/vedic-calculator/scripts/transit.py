"""Transit calculation module - Computes current planetary transits, Sade Sati, and double transits."""
import swisseph as swe
from datetime import datetime
import pytz

from engine import PLANET_FLAGS, _ensure_swe_state

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

def calc_transit(lagna_sign_idx, moon_sign_idx, tz_str="Asia/Kolkata"):
    """Compute current transit data."""
    _ensure_swe_state()
    flags = PLANET_FLAGS

    now = datetime.now(pytz.timezone(tz_str))
    utc = now.astimezone(pytz.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, 
                     utc.hour + utc.minute / 60.0)
    
    # Slow-moving planet transits
    slow_planets = {
        'Saturn': (swe.SATURN, '~2.5 yrs/sign'),
        'Jupiter': (swe.JUPITER, '~1 yr/sign'),
        'Rahu': (swe.MEAN_NODE, '~1.5 yrs/sign')
    }
    
    transit = {}
    for name, (pid, cycle) in slow_planets.items():
        result = swe.calc_ut(jd, pid, flags)
        lon = result[0][0]
        sign_idx = int(lon / 30)
        house = ((sign_idx - lagna_sign_idx) % 12) + 1
        transit[name] = {
            'sign': SIGNS[sign_idx], 'sign_idx': sign_idx,
            'house': house, 'cycle': cycle
        }
    
    # Ketu = 180° opposite Rahu
    rahu_idx = transit['Rahu']['sign_idx']
    ketu_idx = (rahu_idx + 6) % 12
    transit['Ketu'] = {
        'sign': SIGNS[ketu_idx], 'sign_idx': ketu_idx,
        'house': ((ketu_idx - lagna_sign_idx) % 12) + 1,
        'cycle': 'Opposite Rahu (180°)'
    }
    
    # Sade Sati
    saturn_idx = transit['Saturn']['sign_idx']
    relative = (saturn_idx - moon_sign_idx) % 12
    if relative == 11:
        sade_sati = 'Phase 1 (Rising)'
        position = '12th from Moon (1 house before)'
    elif relative == 0:
        sade_sati = 'Phase 2 (Peak)'
        position = 'Moon house (1st from Moon)'
    elif relative == 1:
        sade_sati = 'Phase 3 (Setting)'
        position = '2nd from Moon (1 house after)'
    else:
        sade_sati = 'Inactive'
        position = 'Non-Sade Sati'
    
    sade_sati_data = {
        'moon_sign': SIGNS[moon_sign_idx],
        'saturn_sign': transit['Saturn']['sign'],
        'position': position,
        'status': sade_sati
    }
    
    # Double Transit (Saturn-Jupiter Double Transit)
    saturn_house = transit['Saturn']['house']
    jupiter_house = transit['Jupiter']['house']
    
    # Saturn aspects: Conjunction (1st), 3rd, 7th, 10th
    saturn_covers = set()
    for offset in [0, 2, 6, 9]:
        saturn_covers.add(((saturn_house - 1 + offset) % 12) + 1)
    
    # Jupiter aspects: Conjunction (1st), 5th, 7th, 9th
    jupiter_covers = set()
    for offset in [0, 4, 6, 8]:
        jupiter_covers.add(((jupiter_house - 1 + offset) % 12) + 1)
    
    double_transit = sorted(saturn_covers & jupiter_covers)
    
    return {
        'planets': transit,
        'sade_sati': sade_sati_data,
        'saturn_covers': sorted(saturn_covers),
        'jupiter_covers': sorted(jupiter_covers),
        'double_transit': double_transit,
        'future_ingress': future_ingress_table(jd, years=5),
        'date': now.strftime('%Y-%m-%d')
    }


def future_ingress_table(jd_start, years=5):
    """Compute sidereal (True Chitra) sign ingresses for Saturn, Jupiter, and Rahu over N years.

    Calculated via astronomical ephemeris to replace approximate recall.
    Retrograde re-crossings are chronologically reported.
    Returns: [{'planet', 'date', 'from_sign', 'to_sign'}, ...] sorted by date
    """
    _ensure_swe_state()
    flags = PLANET_FLAGS
    bodies = {'Saturn': swe.SATURN, 'Jupiter': swe.JUPITER, 'Rahu': swe.MEAN_NODE}
    events = []
    jd_end = jd_start + years * 365.25
    for name, pid in bodies.items():
        step = 5.0
        prev_idx = int(swe.calc_ut(jd_start, pid, flags)[0][0] / 30)
        jd = jd_start + step
        while jd <= jd_end:
            idx = int(swe.calc_ut(jd, pid, flags)[0][0] / 30)
            if idx != prev_idx:
                lo, hi = jd - step, jd  # Binary search to 0.01 day
                while hi - lo > 0.01:
                    mid = (lo + hi) / 2
                    if int(swe.calc_ut(mid, pid, flags)[0][0] / 30) == prev_idx:
                        lo = mid
                    else:
                        hi = mid
                y, m, d, _ = swe.revjul(hi)
                events.append({'planet': name, 'date': f'{y:04d}-{m:02d}-{d:02d}',
                               'from_sign': SIGNS[prev_idx], 'to_sign': SIGNS[idx]})
                prev_idx = idx
            jd += step
    return sorted(events, key=lambda e: e['date'])

if __name__ == '__main__':
    # Test with Virgo Lagna, Cancer Moon
    t = calc_transit(5, 3)  # Virgo=5, Cancer=3
    print(f"Transit date: {t['date']}")
    for name, data in t['planets'].items():
        print(f"  {name}: {data['sign']} (H{data['house']})")
    print(f"Sade Sati: {t['sade_sati']['status']}")
    print(f"Double Transit: {t['double_transit']}")
