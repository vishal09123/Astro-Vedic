"""
Vedic Rectifier — Time Scanner (swisseph version)
=============================================
Scans birth time across ±N minutes to output minute-by-minute Lagna, D9, and D10 transitions.
Uses identical astronomical ephemeris (swisseph) and Ayanamsa (True Chitra) as vedic-calculator engine.py,
guaranteeing Lagna degree and D9/D10 boundaries match the primary natal chart.

Usage:
  # Recommended: Supply local birth date/time; converts to UTC based on --tz (handles DST and day rollover automatically)
  python time_scan.py --local-date 1995-05-06 --local-time 02:30 --lat 31.23 --lon 121.47 --tz Asia/Shanghai
  # Legacy usage: Direct UTC input
  python time_scan.py --date 2000-01-01 --time 10:30 --lat 28.61 --lon 77.21 --range 60 --tz Asia/Kolkata

Dependencies: pip install pyswisseph pytz
"""

import swisseph as swe
import pytz
import argparse
import calendar
import sys
import os
from datetime import datetime, timedelta

# === Synchronized configuration with engine.py ===
swe.set_sid_mode(swe.SIDM_TRUE_CITRA)
PLANET_FLAGS = (swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
                | swe.FLG_TRUEPOS | swe.FLG_NONUT | swe.FLG_NOGDEFL)

# Reuse vedic-calculator's Vimsottari Dasha module
_HERE = os.path.dirname(os.path.abspath(__file__))
_CALC_SCRIPTS = os.path.normpath(os.path.join(_HERE, '..', '..', 'vedic-calculator', 'scripts'))
if os.path.isfile(os.path.join(_CALC_SCRIPTS, 'dasha_pyjhora.py')):
    sys.path.insert(0, _CALC_SCRIPTS)
try:
    from dasha_pyjhora import calculate_dasha_fixed
    _HAS_DASHA = True
    _DASHA_ERR = None
except Exception as _e:
    _HAS_DASHA = False
    _DASHA_ERR = str(_e)

SIGNS = ['Ar', 'Ta', 'Ge', 'Cn', 'Le', 'Vi', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi']
SIGNS_FULL = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
              'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# 27 Nakshatras: Moon crossing triggers a change in Vimshottari starting lord
NAKSHATRAS = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
              'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'P.Phalguni', 'U.Phalguni',
              'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula',
              'P.Ashadha', 'U.Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
              'P.Bhadra', 'U.Bhadra', 'Revati']


# === Core Astronomical Functions ===

def calc_sidereal_asc(jd, lat, lon):
    """Calculate sidereal Ascendant degree (0-360)."""
    ascmc = swe.houses_ex(jd, lat, lon, b'W', 0)[1]
    ayanamsa = swe.get_ayanamsa_ex_ut(jd, swe.FLG_TRUEPOS | swe.FLG_NONUT)[1]
    return (ascmc[0] - ayanamsa) % 360


def deg_to_sign(deg):
    """Absolute degree → (sign_abbr, full_sign_name, deg_in_sign)."""
    sign_idx = int(deg / 30) % 12
    deg_in_sign = deg % 30
    return SIGNS[sign_idx], SIGNS_FULL[sign_idx], deg_in_sign


def calc_d9(asc_deg):
    """Lagna absolute degree → D9 (Navamsha) sign."""
    sign = int(asc_deg / 30) % 12
    deg_in_sign = asc_deg % 30
    nav_part = int(deg_in_sign / (30.0 / 9))  # 0-8

    element = sign % 4  # 0=Fire, 1=Earth, 2=Air, 3=Water
    start_signs = [0, 9, 6, 3]  # Ar, Cp, Li, Cn
    d9_sign = (start_signs[element] + nav_part) % 12
    return SIGNS[d9_sign], SIGNS_FULL[d9_sign]


def calc_d10(asc_deg):
    """Lagna absolute degree → D10 (Dashamsha) sign."""
    sign = int(asc_deg / 30) % 12
    deg_in_sign = asc_deg % 30
    das_part = int(deg_in_sign / 3.0)  # 0-9
    if das_part > 9:
        das_part = 9

    is_odd = (sign % 2 == 0)  # Ar=0 (odd), Ta=1 (even)
    if is_odd:
        d10_sign = (sign + das_part) % 12
    else:
        d10_sign = (sign + das_part + 8) % 12
    return SIGNS[d10_sign], SIGNS_FULL[d10_sign]


def _state(jd, lat, lon):
    """Return state dict at jd for binary search."""
    asc_deg = calc_sidereal_asc(jd, lat, lon)
    moon_lon = swe.calc_ut(jd, swe.MOON, PLANET_FLAGS)[0][0]
    return {'sign': deg_to_sign(asc_deg)[0], 'd9': calc_d9(asc_deg)[0], 'd10': calc_d10(asc_deg)[0],
            'nak': int(moon_lon / (360.0 / 27)) % 27}


def _switch_jd(jd_lo, jd_hi, key, lat, lon):
    """Binary search exact ingress second within [jd_lo, jd_hi]."""
    lo_val = _state(jd_lo, lat, lon)[key]
    for _ in range(24):
        mid = (jd_lo + jd_hi) / 2.0
        if _state(mid, lat, lon)[key] == lo_val:
            jd_lo = mid
        else:
            jd_hi = mid
    return jd_hi


def scan(
    date_str,
    time_str,
    lat,
    lon,
    range_min=30,
    tz_name='UTC',
    endpoint_start=None,
    endpoint_end=None,
    include_pd=False,
):
    """Scan time window and output minute-by-minute transitions and two-point Dasha endpoints."""
    parts = date_str.split('-')
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    hms = [int(x) for x in time_str.split(':')]
    h, m, s = hms[0], hms[1], (hms[2] if len(hms) > 2 else 0)

    ut_hour = h + m / 60.0 + s / 3600.0
    base_jd = swe.julday(year, month, day, ut_hour)
    base_utc = datetime(year, month, day, h, m, s)

    def _local_clock(jd):
        utc = base_utc + timedelta(days=jd - base_jd)
        return utc_to_local(utc.replace(microsecond=0), tz_name).strftime('%H:%M:%S')

    results = []
    prev_sign = None
    prev_d9 = None
    prev_d10 = None
    prev_nak = None

    for delta in range(-range_min, range_min + 1):
        jd = base_jd + delta / 1440.0

        asc_deg = calc_sidereal_asc(jd, lat, lon)
        sign, sign_full, deg_in_sign = deg_to_sign(asc_deg)
        d9, d9_full = calc_d9(asc_deg)
        d10, d10_full = calc_d10(asc_deg)
        moon_lon = swe.calc_ut(jd, swe.MOON, PLANET_FLAGS)[0][0]
        nak_idx = int(moon_lon / (360.0 / 27)) % 27
        moon_nak = NAKSHATRAS[nak_idx]

        markers = []
        if prev_sign and sign != prev_sign:
            markers.append(f"★ LAGNA Ingress→{sign_full} @{_local_clock(_switch_jd(jd - 1 / 1440.0, jd, 'sign', lat, lon))}")
        if prev_d9 and d9 != prev_d9:
            markers.append(f"◆ D9 Ingress→{d9_full} @{_local_clock(_switch_jd(jd - 1 / 1440.0, jd, 'd9', lat, lon))}")
        if prev_d10 and d10 != prev_d10:
            markers.append(f"◇ D10 Ingress→{d10_full} @{_local_clock(_switch_jd(jd - 1 / 1440.0, jd, 'd10', lat, lon))}")
        if prev_nak is not None and nak_idx != prev_nak:
            markers.append(f"⚠️ Moon Cross-Nak→{moon_nak} @{_local_clock(_switch_jd(jd - 1 / 1440.0, jd, 'nak', lat, lon))} "
                           "[Dasha lord jump; segment must be split here]")

        results.append({
            'delta': delta, 'asc_deg': asc_deg, 'sign': sign, 'sign_full': sign_full,
            'deg_in_sign': deg_in_sign, 'd9': d9, 'd9_full': d9_full,
            'd10': d10, 'd10_full': d10_full, 'moon_nak': moon_nak,
            'markers': ' '.join(markers),
        })

        prev_sign, prev_d9, prev_d10, prev_nak = sign, d9, d10, nak_idx

    dasha_endpoints = {}
    if _HAS_DASHA:
        first_offset = -range_min if endpoint_start is None else endpoint_start
        last_offset = range_min if endpoint_end is None else endpoint_end
        labels_and_offsets = [
            ('Segment Start (%+dmin)' % first_offset, first_offset),
            ('Segment End (%+dmin)' % last_offset, last_offset),
        ]
        for label, dmin in labels_and_offsets:
            utc_dt = base_utc + timedelta(minutes=dmin)
            local_dt = utc_to_local(utc_dt, tz_name)
            tz_offset = local_dt.utcoffset().total_seconds() / 3600.0
            try:
                dasha_endpoints[label] = calculate_dasha_fixed(
                    local_dt.year, local_dt.month, local_dt.day,
                    local_dt.hour, local_dt.minute, lat, lon, tz_offset,
                    include_pd=include_pd, second=local_dt.second)
            except Exception as e:
                dasha_endpoints[label] = [{'error': str(e)}]
    else:
        dasha_endpoints['_error'] = 'calculate_dasha_fixed could not be imported: %s' % _DASHA_ERR

    return results, dasha_endpoints


def local_to_utc(local_date, local_time, tz_name):
    """Convert local birth date/time to UTC string tuple."""
    fmt = "%Y-%m-%d %H:%M:%S" if local_time.count(':') == 2 else "%Y-%m-%d %H:%M"
    naive = datetime.strptime(f"{local_date} {local_time}", fmt)
    try:
        local_dt = pytz.timezone(tz_name).localize(naive, is_dst=None)
    except pytz.exceptions.AmbiguousTimeError:
        raise ValueError(f"{naive} falls during a DST transition repeated hour; specify DST status.")
    except pytz.exceptions.NonExistentTimeError:
        raise ValueError(f"{naive} falls during a DST gap hour (skipped clock time).")
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt.strftime("%Y-%m-%d"), utc_dt.strftime("%H:%M:%S" if naive.second else "%H:%M")


def utc_to_local(utc_dt, tz_name):
    """Convert naive UTC datetime to aware local datetime in target timezone."""
    return pytz.utc.localize(utc_dt).astimezone(pytz.timezone(tz_name))


def _base_label(date_str, time_str, tz_name):
    label = f"{date_str} {time_str} UTC"
    if tz_name is None:
        return label
    fmt = "%Y-%m-%d %H:%M:%S" if time_str.count(':') == 2 else "%Y-%m-%d %H:%M"
    local_dt = utc_to_local(datetime.strptime(f"{date_str} {time_str}", fmt), tz_name)
    offset = local_dt.utcoffset().total_seconds() / 3600.0
    dst = ", Summer Time / DST" if local_dt.dst() else ""
    clock = '%Y-%m-%d %H:%M:%S' if time_str.count(':') == 2 else '%Y-%m-%d %H:%M'
    return f"{label} (= Local {local_dt.strftime(clock)}, {tz_name} UTC{offset:+g}{dst})"


def print_results(results, date_str, time_str, lat, lon, tz_name=None):
    """Print formatted scan results."""
    print(f"# Time Scan Results")
    print(f"# Baseline: {_base_label(date_str, time_str, tz_name)} | Coordinates: ({lat}, {lon})")
    print(f"# Engine: swisseph + True Chitra Ayanamsa; Lagna basis identical to calc engine v1.0")
    print(f"# Ingress timestamp @HH:MM:SS determined by binary search in local clock time")
    print(f"# Range: {results[0]['delta']:+d} ~ {results[-1]['delta']:+d} minutes")
    print()
    print(f"{'Offset':>7} | {'Lagna Deg':>10} | {'Sign':>12} | {'Deg in Sign':>11} | {'D9':>4} | {'D10':>4} | Markers")
    print("-" * 80)

    for r in results:
        marker_str = f"  {r['markers']}" if r['markers'] else ""
        is_base = " ← Baseline" if r['delta'] == 0 else ""
        print(f"{r['delta']:+5d}min | {r['asc_deg']:9.2f}° | {r['sign_full']:>12} | {r['deg_in_sign']:10.2f}° | {r['d9']:>4} | {r['d10']:>4} |{marker_str}{is_base}")


def save_results(results, date_str, time_str, lat, lon, filepath, dasha_ep=None, event_dates=None,
                 tz_name=None):
    """Save results as Markdown document."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Time Scan Results\n\n")
        f.write(f"> Baseline: {_base_label(date_str, time_str, tz_name)}\n")
        f.write(f"> Coordinates: ({lat}, {lon})\n")
        f.write(f"> Engine: swisseph + True Chitra Ayanamsa\n\n")
        f.write(f"| Offset | Lagna Deg | Sign & Degrees | D9 | D10 | Markers |\n")
        f.write(f"|--------|-----------|----------------|----|-----|---------|\n")

        for r in results:
            base = " ← Baseline" if r['delta'] == 0 else ""
            marker = r['markers'] + base
            f.write(f"| {r['delta']:+5d}min | {r['asc_deg']:.2f}° | "
                    f"{r['sign_full']} {r['deg_in_sign']:.1f}° | "
                    f"{r['d9']} | {r['d10']} | {marker} |\n")

        f.write("\n## Two-Point Dasha (Segment Start / End; AD dates in local timezone)\n")
        f.write("> Evaluates MD/AD timeline at segment start and segment end against major life events.\n")
        if dasha_ep is None or '_error' in (dasha_ep or {}):
            err = (dasha_ep or {}).get('_error', 'Two-point Dasha unavailable')
            f.write("⚠️⚠️ **DASHA_UNAVAILABLE**: " + err + "\n")
        else:
            for label, dashas in dasha_ep.items():
                f.write(f"\n### {label}\n")
                f.write(_fmt_dasha(dashas) + "\n")

        if event_dates:
            f.write("\n## Event Date MD/AD/PD Discrepancy Audit\n")
            f.write("> Audits event timing consistency across candidate boundaries.\n\n")
            f.write(_fmt_event_date_audit(dasha_ep or {}, event_dates) + "\n")

    print(f"\nSaved to: {filepath}")


def _fmt_dasha(dashas):
    if not dashas or (isinstance(dashas, list) and dashas and isinstance(dashas[0], dict) and 'error' in dashas[0]):
        return "  [Dasha calculation failed: %s]" % (dashas[0].get('error') if dashas else 'empty')
    lines = []
    for d in dashas:
        cur = ' ← Current' if d.get('is_current') else ''
        lines.append(f"  {d['planet']:<8} {d['start']} ~ {d['end']}{cur}")
        if d.get('is_current'):
            for a in d.get('antardashas', []):
                lines.append(f"      └ AD {a['planet']:<8} starts {a['start']}")
    return '\n'.join(lines)


def _parse_period_date(value):
    return datetime.strptime(value[:10], '%Y-%m-%d').date()


def _event_probe_dates(value):
    value = value.strip()
    if len(value) == 10:
        return [datetime.strptime(value, '%Y-%m-%d').date()]
    if len(value) == 7:
        year, month = map(int, value.split('-'))
        last = calendar.monthrange(year, month)[1]
        return [datetime(year, month, 1).date(), datetime(year, month, last).date()]
    raise ValueError(f'Event date must be YYYY-MM-DD or YYYY-MM: {value}')


def _active_triplet(dashas, probe_date):
    for md in dashas or []:
        for ad in md.get('antardashas', []):
            for pd in ad.get('pratyantardashas', []):
                if _parse_period_date(pd['start']) <= probe_date < _parse_period_date(pd['end']):
                    return f"{md['planet']}/{ad['planet']}/{pd['planet']}"
    return 'Not found (Outside timeline or PD missing)'


def _fmt_event_date_audit(dasha_ep, event_dates):
    if not dasha_ep or '_error' in dasha_ep:
        return '⚠️ PD_AUDIT_UNAVAILABLE: Two-point Dasha unavailable.'
    labels = list(dasha_ep.keys())
    if len(labels) < 2:
        return '⚠️ PD_AUDIT_UNAVAILABLE: Requires both Segment Start and Segment End timelines.'
    rows = [
        '| Event Date | Segment Start MD/AD/PD | Segment End MD/AD/PD | Stability |',
        '|------------|------------------------|----------------------|-----------|',
    ]
    for raw in event_dates:
        probes = _event_probe_dates(raw)
        endpoint_values = []
        for label in labels[:2]:
            values = [_active_triplet(dasha_ep[label], probe) for probe in probes]
            endpoint_values.append(values[0] if len(set(values)) == 1 else f"{values[0]} → {values[-1]}")
        stable = 'Consistent throughout' if endpoint_values[0] == endpoint_values[1] and '→' not in endpoint_values[0] else 'Boundary sensitive / Candidate discrepancy'
        rows.append(f"| {raw} | {endpoint_values[0]} | {endpoint_values[1]} | {stable} |")
    return '\n'.join(rows)


def print_dasha_endpoints(dasha_ep, event_dates=None):
    print("\n## Two-Point Dasha (Segment Start / End; AD dates in local timezone)")
    if '_error' in dasha_ep:
        print("\n" + "=" * 60)
        print("⚠️ DASHA_UNAVAILABLE: " + dasha_ep['_error'])
        print("=" * 60)
        return
    for label, dashas in dasha_ep.items():
        print(f"\n### {label}")
        print(_fmt_dasha(dashas))
    if event_dates:
        print("\n## Event Date MD/AD/PD Discrepancy Audit")
        print(_fmt_event_date_audit(dasha_ep, event_dates))


def main():
    parser = argparse.ArgumentParser(description='Vedic Rectifier Time Scanner (swisseph)')
    parser.add_argument('--date', help='Birth date YYYY-MM-DD (UTC); pair with --time')
    parser.add_argument('--time', help='Birth time HH:MM or HH:MM:SS (UTC); pair with --date')
    parser.add_argument('--local-date', help='Local birth date YYYY-MM-DD; recommended, auto-converted via --tz')
    parser.add_argument('--local-time', help='Local birth time HH:MM or HH:MM:SS; pair with --local-date')
    parser.add_argument('--lat', required=True, type=float, help='Birthplace latitude')
    parser.add_argument('--lon', required=True, type=float, help='Birthplace longitude')
    parser.add_argument('--range', type=int, default=30, help='Scan range in ±minutes (default: 30)')
    parser.add_argument('--tz', required=True, help='Birthplace IANA timezone name (e.g. Asia/Kolkata)')
    parser.add_argument('--save', help='Path to save output Markdown table')
    parser.add_argument('--events', nargs='*', help='Event dates (YYYY-MM-DD or YYYY-MM) to audit against Dasha')
    parser.add_argument('--segment', nargs=2, type=int, metavar=('START', 'END'),
                        help='Generate two-point Dasha for a specific segment offset window')
    parser.add_argument('--include-pd', action='store_true', help='Include level 3 Pratyantardasha (PD)')

    args = parser.parse_args()

    if args.local_date and args.local_time:
        try:
            date_str, time_str = local_to_utc(args.local_date, args.local_time, args.tz)
        except ValueError as e:
            print(f"❌ Timezone conversion error: {e}")
            sys.exit(1)
    elif args.date and args.time:
        date_str, time_str = args.date, args.time
    else:
        print("❌ Error: Must provide either (--local-date and --local-time) or (--date and --time).")
        sys.exit(1)

    ep_start, ep_end = (args.segment[0], args.segment[1]) if args.segment else (None, None)
    results, dasha_ep = scan(
        date_str, time_str, args.lat, args.lon,
        range_min=args.range, tz_name=args.tz,
        endpoint_start=ep_start, endpoint_end=ep_end,
        include_pd=args.include_pd
    )

    if args.save:
        save_results(results, date_str, time_str, args.lat, args.lon, args.save,
                     dasha_ep=dasha_ep, event_dates=args.events, tz_name=args.tz)
    else:
        print_results(results, date_str, time_str, args.lat, args.lon, tz_name=args.tz)
        print_dasha_endpoints(dasha_ep, event_dates=args.events)


if __name__ == '__main__':
    main()
