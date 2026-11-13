#!/usr/bin/env python3
"""build_synastry_data.py — Cross-chart calculation engine for Vedic Synastry.

Reads two structured_data.md files → outputs synastry_data.md (pure auditable calculations, no speculative prose).
Pure standard library; system: KN Rao / Parashari; criteria: resources/aspect-policy.md.

Usage:
    python build_synastry_data.py <A_structured_data.md> <B_structured_data.md> <out_dir> [--a NameA] [--b NameB]

Output: <out_dir>/synastry_data.md
"""
import re
import os
import argparse

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
SIGN_IDX = {s: i for i, s in enumerate(SIGNS)}
SIGN_ABBR = {'Ar': 0, 'Ta': 1, 'Ge': 2, 'Cn': 3, 'Le': 4, 'Vi': 5,
             'Li': 6, 'Sc': 7, 'Sg': 8, 'Cp': 9, 'Aq': 10, 'Pi': 11}
PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
KEY_POINTS = ['Lagna', 'Moon', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']

# Graha Drishti special aspects (in addition to universal 7th house aspect, counted from occupied house)
SPECIAL_DRISHTI = {'Mars': [4, 8], 'Jupiter': [5, 9], 'Saturn': [3, 10]}
BENEFICS = {'Jupiter', 'Venus', 'Moon', 'Mercury'}
MALEFICS = {'Saturn', 'Mars', 'Rahu', 'Ketu', 'Sun'}

# Dignity mapping
DIGNITY_EN = {
    'exalted': 'Exalted', 'debilitated': 'Debilitated', 'own': 'Own Sign', 'own_sign': 'Own Sign',
    'moolatrikona': 'Moolatrikona', 'great_friend': 'Great Friend', 'friend': 'Friend', 'neutral': 'Neutral',
    'enemy': 'Enemy', 'great_enemy': 'Great Enemy',
}

# Natural planetary friendships (standard Parashari) for Graha Maitri
NATURAL = {
    'Sun':     {'friend': {'Moon', 'Mars', 'Jupiter'}, 'enemy': {'Venus', 'Saturn'}},
    'Moon':    {'friend': {'Sun', 'Mercury'}, 'enemy': set()},
    'Mars':    {'friend': {'Sun', 'Moon', 'Jupiter'}, 'enemy': {'Mercury'}},
    'Mercury': {'friend': {'Sun', 'Venus'}, 'enemy': {'Moon'}},
    'Jupiter': {'friend': {'Sun', 'Moon', 'Mars'}, 'enemy': {'Mercury', 'Venus'}},
    'Venus':   {'friend': {'Mercury', 'Saturn'}, 'enemy': {'Sun', 'Moon'}},
    'Saturn':  {'friend': {'Mercury', 'Venus'}, 'enemy': {'Sun', 'Moon', 'Mars'}},
}
SIGN_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
    'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

# 27 Nakshatras in standard canonical order
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu',
    'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta',
    'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha',
    'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada',
    'Uttara Bhadrapada', 'Revati'
]
GANA = {
    'Deva': {'Ashwini', 'Mrigashira', 'Punarvasu', 'Pushya', 'Hasta', 'Swati',
             'Anuradha', 'Shravana', 'Revati'},
    'Manushya': {'Bharani', 'Rohini', 'Ardra', 'Purva Phalguni', 'Uttara Phalguni',
                 'Purva Ashadha', 'Uttara Ashadha', 'Purva Bhadrapada', 'Uttara Bhadrapada'},
    'Rakshasa': {'Krittika', 'Ashlesha', 'Magha', 'Chitra', 'Vishakha', 'Jyeshtha',
                 'Mula', 'Dhanishta', 'Shatabhisha'},
}
NADI = {
    'Adi': {'Ashwini', 'Ardra', 'Punarvasu', 'Uttara Phalguni', 'Hasta', 'Jyeshtha',
            'Mula', 'Shatabhisha', 'Purva Bhadrapada'},
    'Madhya': {'Bharani', 'Mrigashira', 'Pushya', 'Purva Phalguni', 'Chitra', 'Anuradha',
               'Purva Ashadha', 'Dhanishta', 'Uttara Bhadrapada'},
    'Antya': {'Krittika', 'Rohini', 'Ashlesha', 'Magha', 'Swati', 'Vishakha',
              'Uttara Ashadha', 'Shravana', 'Revati'},
}

# Varna (by element: Water=Brahmin > Fire=Kshatriya > Earth=Vaishya > Air=Shudra)
_VARNA = {'Brahmin': {'Cancer', 'Scorpio', 'Pisces'}, 'Kshatriya': {'Aries', 'Leo', 'Sagittarius'},
          'Vaishya': {'Taurus', 'Virgo', 'Capricorn'}, 'Shudra': {'Gemini', 'Libra', 'Aquarius'}}
VARNA_OF = {s: v for v, ss in _VARNA.items() for s in ss}

# Vashya (Whole sign grouping)
VASHYA_OF = {
    'Aries': 'Quad', 'Taurus': 'Quad', 'Sagittarius': 'Quad', 'Capricorn': 'Quad',
    'Gemini': 'Human', 'Virgo': 'Human', 'Libra': 'Human', 'Aquarius': 'Human',
    'Cancer': 'Water', 'Pisces': 'Water', 'Leo': 'Wild', 'Scorpio': 'Insect',
}

# Yoni (Nakshatra animal symbols) + Inimical pairs
NAK_YONI = {
    'Ashwini': 'Horse', 'Bharani': 'Elephant', 'Krittika': 'Goat', 'Rohini': 'Snake',
    'Mrigashira': 'Snake', 'Ardra': 'Dog', 'Punarvasu': 'Cat', 'Pushya': 'Goat',
    'Ashlesha': 'Cat', 'Magha': 'Rat', 'Purva Phalguni': 'Rat', 'Uttara Phalguni': 'Cow',
    'Hasta': 'Buffalo', 'Chitra': 'Tiger', 'Swati': 'Buffalo', 'Vishakha': 'Tiger',
    'Anuradha': 'Deer', 'Jyeshtha': 'Deer', 'Mula': 'Dog', 'Purva Ashadha': 'Monkey',
    'Uttara Ashadha': 'Mongoose', 'Shravana': 'Monkey', 'Dhanishta': 'Lion',
    'Shatabhisha': 'Horse', 'Purva Bhadrapada': 'Lion', 'Uttara Bhadrapada': 'Cow', 'Revati': 'Elephant',
}
YONI_BITTER = {frozenset(p) for p in [
    ('Cow', 'Tiger'), ('Elephant', 'Lion'), ('Horse', 'Buffalo'),
    ('Dog', 'Deer'), ('Snake', 'Mongoose'), ('Cat', 'Rat'), ('Monkey', 'Goat'),
]}


def sign_index(s):
    """Sign name/abbreviation → 0-11 index, tolerant matching."""
    if not s:
        return None
    s = s.strip()
    if s in SIGN_IDX:
        return SIGN_IDX[s]
    if s in SIGN_ABBR:
        return SIGN_ABBR[s]
    for full, i in SIGN_IDX.items():
        if full.lower().startswith(s.lower()[:3]):
            return i
    return None


def norm_nak(name):
    """Normalize Nakshatra name, handling spelling variations."""
    if not name:
        return None
    n = re.sub(r'[^a-z]', '', name.lower())
    for std in NAKSHATRAS:
        if re.sub(r'[^a-z]', '', std.lower()) == n:
            return std
    for std in NAKSHATRAS:
        if re.sub(r'[^a-z]', '', std.lower())[:6] == n[:6]:
            return std
    return None


def gana_of(nak):
    for g, members in GANA.items():
        if nak in members:
            return g
    return None


def nadi_of(nak):
    for nd, members in NADI.items():
        if nak in members:
            return nd
    return None


class Chart:
    """Parse structured_data.md and extract fields required for synastry."""

    def __init__(self, path, label):
        self.label = label
        with open(path, encoding='utf-8') as f:
            self.text = f.read()
        self.planets = {}
        self.lagna_sign = None
        self.lagna_idx = None
        self.moon_nak = None
        self.moon_pada = None
        self.ul = None
        self.dk = None
        self.house_lords = {}
        self.dignity = {}
        self.dasha_md = None
        self.dasha_ad = None
        self._parse()

    def _deg_to_lon(self, sidx, deg_str):
        m = re.search(r"(\d+)\D+(\d+)", deg_str)
        if not m or sidx is None:
            return None
        d, mi = int(m.group(1)), int(m.group(2))
        return sidx * 30 + d + mi / 60.0

    def _parse(self):
        t = self.text
        # Planetary positions: | Name | Sign | House | deg°min' | D/R |
        for m in re.finditer(
                r"^\|\s*(\w+)\s*\|\s*([A-Za-z]+)\s*\|\s*(\d+)\s*\|\s*([\d°'\".\s]+?)\s*\|\s*([DR—\-]+)\s*\|",
                t, re.M):
            name, sign, house, deg_str, retro = m.groups()
            if name == 'Lagna':
                self.lagna_sign = sign
                self.lagna_idx = sign_index(sign)
            if name in PLANETS or name == 'Lagna':
                sidx = sign_index(sign)
                self.planets[name] = {
                    'sign': sign, 'sidx': sidx, 'house': int(house),
                    'lon': self._deg_to_lon(sidx, deg_str),
                    'retro': retro.strip() == 'R',
                }
        # Nakshatra table: | Moon | Nak | Pada | Lord |
        for m in re.finditer(r"^\|\s*Moon\s*\|\s*([A-Za-z ]+?)\s*\|\s*(\d)\s*\|", t, re.M):
            nk = norm_nak(m.group(1))
            if nk:
                self.moon_nak = nk
                self.moon_pada = int(m.group(2))
                break
        # Special Points UL: | UL (Upapada Lagna) | Sign | House | ... |
        m = re.search(r"\|\s*UL[^|]*\|\s*([A-Za-z]+)\s*\|\s*(\d+)\s*\|", t)
        if m:
            si = sign_index(m.group(1))
            self.ul = {'sign': m.group(1), 'sidx': si, 'house': int(m.group(2))}
        # DK = Planet
        m = re.search(r"DK\s*=\s*([A-Za-z]+)", t)
        if m:
            self.dk = m.group(1)
        # House Lords: | h | domain | lord | lord_house |
        for m in re.finditer(r"^\|\s*(\d{1,2})\s*\|\s*[^|]+\|\s*([A-Za-z]+)\s*\|\s*(\d+)\s*\|", t, re.M):
            h = int(m.group(1))
            if 1 <= h <= 12 and h not in self.house_lords:
                self.house_lords[h] = {'lord': m.group(2), 'lord_house': int(m.group(3))}
        # Dignity: | Planet | Sign | Lord | Compound | |
        for m in re.finditer(
                r"^\|\s*(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn)\s*\|\s*[A-Za-z]+\s*\|\s*[A-Za-z]+\s*\|\s*([^|]+?)\s*\|",
                t, re.M):
            self.dignity[m.group(1)] = m.group(2).strip()
        # Dasha Current Status
        m = re.search(r"Mahadasha:\s*([A-Za-z]+)\s*\(([^)]+)\)", t)
        if m:
            span = [x.strip() for x in m.group(2).split('~')]
            self.dasha_md = {'planet': m.group(1), 'start': span[0], 'end': span[-1]}
        m = re.search(r"Antardasha:\s*([A-Za-z]+)-([A-Za-z]+)\s*\(([^)]+)\)", t)
        if m:
            span = [x.strip() for x in m.group(3).split('~')]
            self.dasha_ad = {'planet': m.group(2), 'md': m.group(1),
                             'start': span[0], 'end': span[-1]}

    def dignity_of(self, planet):
        v = self.dignity.get(planet, '—')
        return DIGNITY_EN.get(v, v)

    def role_of(self, planet):
        """Which houses this planet lords in its own chart."""
        return [h for h, info in self.house_lords.items() if info['lord'] == planet]


def house_from(sign_idx, lagna_idx):
    if sign_idx is None or lagna_idx is None:
        return None
    return ((sign_idx - lagna_idx) % 12) + 1


# ========== Cross-Chart Calculations ==========

def overlay(src, dst):
    """src planets mapped into dst houses (1-12 from dst Lagna)."""
    rows = []
    for p in PLANETS:
        if p not in src.planets:
            continue
        sp = src.planets[p]
        h = house_from(sp['sidx'], dst.lagna_idx)
        dig = src.dignity_of(p)
        roles = src.role_of(p)
        roles_str = ', '.join(f"L{x}" for x in roles) if roles else ''
        rows.append({
            'planet': p, 'sign': sp['sign'], 'house_in_dst': h,
            'dignity': dig, 'roles': roles_str, 'retro': sp['retro'],
        })
    return rows


def cross_aspects(a, b):
    """Full-sign Conjunction and Opposition with orb in degrees."""
    rows = []
    tight = 5.0
    for an in PLANETS:
        ap = a.planets.get(an)
        if not (ap and ap['sidx'] is not None and ap['lon'] is not None):
            continue
        for bn in PLANETS:
            bp = b.planets.get(bn)
            if not (bp and bp['sidx'] is not None and bp['lon'] is not None):
                continue
            sdiff = (bp['sidx'] - ap['sidx']) % 12
            if sdiff in (0, 6):
                d = abs(ap['lon'] - bp['lon'])
                if d > 180:
                    d = 360 - d
                od = d if sdiff == 0 else abs(d - 180)
                kind = 'Conjunction' if sdiff == 0 else 'Opposition'
                tier = 'Tight' if od < tight else ('Moderate' if od < 12 else 'Whole Sign')
                rows.append({
                    'a': an, 'b': bn, 'kind': kind, 'tier': tier,
                    'orb': f"{od:.2f}° ({tier})", 'sign': ap['sign'] if sdiff == 0 else f"{ap['sign']}↔{bp['sign']}",
                })
    return rows


def same_house_resonance(a, b):
    """Check if both charts place the same planet in the exact same natal house."""
    rows = []
    for p in PLANETS:
        pa, pb = a.planets.get(p), b.planets.get(p)
        if pa and pb and pa['house'] == pb['house']:
            rows.append({'planet': p, 'house': pa['house']})
    return rows


def drishti_to_points(src, dst):
    """src planetary aspects projected onto dst key points (Lagna, Moon, Venus, etc.)."""
    hits = []
    if dst.lagna_idx is None:
        return hits
    for an in PLANETS:
        ap = src.planets.get(an)
        if not ap or ap['sidx'] is None:
            continue
        aspects = [7] + SPECIAL_DRISHTI.get(an, [])
        aspected_houses = {((ap['sidx'] + asp - 1) % 12) + 1 for asp in aspects}
        nature = 'Benefic' if an in BENEFICS else 'Malefic'
        dig = src.dignity_of(an)

        for kp in KEY_POINTS:
            if kp == 'Lagna':
                kp_sign = dst.lagna_sign
                kp_h = 1
            else:
                kp_p = dst.planets.get(kp)
                if not kp_p or kp_p['sidx'] is None:
                    continue
                kp_sign = kp_p['sign']
                kp_h = house_from(kp_p['sidx'], dst.lagna_idx)
            if kp_h in aspected_houses:
                hits.append({
                    'a': an, 'point': f"{kp} ({kp_sign})",
                    'nature': nature, 'dignity': dig,
                    'dst_house': kp_h,
                })
    return hits


def key_point_interactions(a, b):
    """Where a's key points fall in b's houses."""
    pts = ['Lagna', 'Moon', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu', 'UL', 'DK']
    rows = []
    if b.lagna_idx is None:
        return rows
    for kp in pts:
        if kp == 'Lagna':
            sidx = a.lagna_idx
        elif kp == 'UL':
            sidx = a.ul['sidx'] if a.ul else None
        elif kp == 'DK':
            dk = a.dk
            ap = a.planets.get(dk) if dk else None
            sidx = ap['sidx'] if ap else None
        else:
            ap = a.planets.get(kp)
            sidx = ap['sidx'] if ap else None
        if sidx is None:
            continue
        h = house_from(sidx, b.lagna_idx)
        label = kp if kp != 'DK' else f'DK ({a.dk})'
        rows.append({'point': label, 'house_in_b': h})
    return rows


def ashtakoota(a, b):
    """Ashtakoota 8 Factors → Tiers + Modern Dimensions.

    KN Rao principle: Screening tool, not final arbitrator.
    Based on both partners' Moon Sign + Nakshatra.
    """
    am = a.planets.get('Moon')
    bm = b.planets.get('Moon')
    if not (am and bm):
        return []
    asign, bsign = am['sign'], bm['sign']
    anak, bnak = a.moon_nak, b.moon_nak
    out = []

    def add(item, tier, dim):
        out.append({'item': item, 'tier': tier, 'dim': dim})

    # Varna
    va, vb = VARNA_OF.get(asign), VARNA_OF.get(bsign)
    if va and vb:
        add('Varna', 'Supportive (Same layer)' if va == vb else 'Neutral', 'Mental Alignment')
    
    # Vashya
    wa, wb = VASHYA_OF.get(asign), VASHYA_OF.get(bsign)
    if wa and wb:
        add('Vashya', 'Supportive (Same group)' if wa == wb else 'Neutral', 'Direction of Attraction')
    
    # Tara
    if anak in NAKSHATRAS and bnak in NAKSHATRAS:
        ai, bi = NAKSHATRAS.index(anak), NAKSHATRAS.index(bnak)

        def ausp(frm, to):
            return (((to - frm) % 27) + 1) % 9 not in (3, 5, 7)
        t1, t2 = ausp(ai, bi), ausp(bi, ai)
        add('Tara', 'Supportive' if (t1 and t2) else ('Constraining' if not (t1 or t2) else 'Neutral'), 'Relationship Stability')
    
    # Yoni
    ya, yb = NAK_YONI.get(anak), NAK_YONI.get(bnak)
    if ya and yb:
        if ya == yb:
            tier = 'Supportive (Same)'
        elif frozenset({ya, yb}) in YONI_BITTER:
            tier = 'Constraining (Inimical)'
        else:
            tier = 'Neutral'
        add('Yoni', tier, 'Intimacy Style')
    
    # Graha Maitri
    la, lb = SIGN_LORDS.get(asign), SIGN_LORDS.get(bsign)
    if la and lb:
        if la == lb:
            tier = 'Supportive (Same Lord)'
        else:
            a_f = lb in NATURAL.get(la, {}).get('friend', set())
            b_f = la in NATURAL.get(lb, {}).get('friend', set())
            a_e = lb in NATURAL.get(la, {}).get('enemy', set())
            b_e = la in NATURAL.get(lb, {}).get('enemy', set())
            if a_f and b_f:
                tier = 'Supportive (Mutual Friends)'
            elif a_e or b_e:
                tier = 'Constraining (Inimical)'
            else:
                tier = 'Neutral'
        add('Graha Maitri', tier, 'Spiritual & Mental Harmony')
    
    # Gana
    ga, gb = gana_of(anak), gana_of(bnak)
    if ga and gb:
        if ga == gb:
            tier = f'Supportive (Same {ga})'
        elif 'Rakshasa' in (ga, gb):
            tier = f'Constraining ({ga}×{gb})'
        else:
            tier = f'Neutral ({ga}×{gb})'
        add('Gana', tier, 'Temperament & Conflict Dynamics')
    
    # Bhakoot
    rel = (bm['sidx'] - am['sidx']) % 12 + 1
    if rel in (6, 8, 2, 12, 5, 9):
        tier = f'Constraining (Relative {rel} dosha)'
    elif rel in (1, 7, 3, 11):
        tier = f'Supportive (Relative {rel})'
    else:
        tier = f'Neutral (Relative {rel})'
    add('Bhakoot', tier, 'Emotional Rhythm & Family')
    
    # Nadi
    na, nb = nadi_of(anak), nadi_of(bnak)
    if na and nb:
        add('Nadi', 'Constraining (Same Nadi dosha)' if na == nb else f'Supportive (Distinct Nadi {na}/{nb})', 'Deep Biological Compatibility')
    return out


def dasha_overlap(a, b):
    """Dasha overlap and trigger clues."""
    lines = []
    if a.dasha_md:
        ad = f" / AD {a.dasha_ad['planet']}" if a.dasha_ad else ''
        lines.append(f"{a.label}: MD {a.dasha_md['planet']} ({a.dasha_md['start']}~{a.dasha_md['end']}){ad}")
    if b.dasha_md:
        ad = f" / AD {b.dasha_ad['planet']}" if b.dasha_ad else ''
        lines.append(f"{b.label}: MD {b.dasha_md['planet']} ({b.dasha_md['start']}~{b.dasha_md['end']}){ad}")
    
    notes = []
    for src, dst, tag in ((a, b, f"{a.label}→{b.label}"), (b, a, f"{b.label}→{a.label}")):
        for lvl in ('dasha_md', 'dasha_ad'):
            d = getattr(src, lvl)
            if not d:
                continue
            pl = d['planet']
            p = src.planets.get(pl)
            if p and dst.lagna_idx is not None:
                h = house_from(p['sidx'], dst.lagna_idx)
                if h in (1, 5, 7, 8, 11):
                    notes.append(f"{tag}: {pl} ({lvl[-2:].upper()}) placed in partner's House {h} (relationship relevant)")
    return lines, notes


# ========== Markdown Output Builder ==========

def build(a, b):
    L = []
    L.append("# synastry_data.md (Cross-Chart Computation Results - Pure Data, No Speculation)\n")
    L.append(f"- Partner A = {a.label} (Lagna {a.lagna_sign})")
    L.append(f"- Partner B = {b.label} (Lagna {b.lagna_sign})")
    L.append(f"- A Moon: {a.moon_nak} pada {a.moon_pada} | B Moon: {b.moon_nak} pada {b.moon_pada}")
    L.append(f"- A UL: {a.ul['sign'] if a.ul else '—'} | A DK: {a.dk or '—'}")
    L.append(f"- B UL: {b.ul['sign'] if b.ul else '—'} | B DK: {b.dk or '—'}\n")

    L.append("## 1. Lunar Screening (Ashtakoota 8 Factors - Screening Only, No Definitive Verdict)\n")
    ks = ashtakoota(a, b)
    if ks:
        L.append("| Factor | Tier | Modern Dimension |")
        L.append("|--------|------|------------------|")
        for r in ks:
            L.append(f"| {r['item']} | {r['tier']} | {r['dim']} |")
        L.append("> Doshas do not veto; structural relationship capacity is governed by Layer 0/2/3 (see koota-policy.md).\n")
    else:
        L.append("(Moon Nakshatra / sign missing; lunar layer unavailable)\n")

    L.append(f"## 2. House Overlay: A ({a.label}) Planets → B Houses\n")
    L.append("| A Planet | Sign | House in B | A Dignity | A Ruled Houses |")
    L.append("|----------|------|------------|-----------|----------------|")
    for r in overlay(a, b):
        L.append(f"| {r['planet']} | {r['sign']} | {r['house_in_dst']} | {r['dignity']} | {r['roles'] or '—'} |")
    L.append("")
    
    L.append(f"## 3. House Overlay: B ({b.label}) Planets → A Houses\n")
    L.append("| B Planet | Sign | House in A | B Dignity | B Ruled Houses |")
    L.append("|----------|------|------------|-----------|----------------|")
    for r in overlay(b, a):
        L.append(f"| {r['planet']} | {r['sign']} | {r['house_in_dst']} | {r['dignity']} | {r['roles'] or '—'} |")
    L.append("")

    L.append("## 4. Cross-Chart Aspects (Full-Sign Conjunction / Opposition + Degrees)\n")
    ca = cross_aspects(a, b)
    if ca:
        L.append("| A Planet | B Planet | Relationship | Degrees |")
        L.append("|----------|----------|--------------|---------|")
        for r in ca:
            L.append(f"| {r['a']} | {r['b']} | {r['kind']} | {r['orb']} |")
    L.append("")

    L.append("## 4b. Same-House Resonance (Both Placed Same Planet in Same House)\n")
    res = same_house_resonance(a, b)
    if res:
        L.append("| Planet | Shared Natal House |")
        L.append("|--------|-------------------|")
        for r in res:
            L.append(f"| {r['planet']} | House {r['house']} |")
    else:
        L.append("(None)")
    L.append("")

    L.append("## 5. Graha Drishti Hits on Partner's Key Points\n")
    L.append(f"### {a.label} Planetary Aspects → {b.label} Points")
    L.append("| A Planet | Hit Point | Nature | Dignity |")
    L.append("|----------|-----------|--------|---------|")
    for r in drishti_to_points(a, b):
        L.append(f"| {r['a']} | {r['point']} | {r['nature']} | {r['dignity']} |")
    L.append("")
    
    L.append(f"### {b.label} Planetary Aspects → {a.label} Points")
    L.append("| B Planet | Hit Point | Nature | Dignity |")
    L.append("|----------|-----------|--------|---------|")
    for r in drishti_to_points(b, a):
        L.append(f"| {r['a']} | {r['point']} | {r['nature']} | {r['dignity']} |")
    L.append("")

    L.append("## 6. Key Point House Placement\n")
    L.append(f"### {a.label} Points → B Houses")
    L.append("| Point | House in B |")
    L.append("|-------|------------|")
    for r in key_point_interactions(a, b):
        L.append(f"| {r['point']} | House {r['house_in_b']} |")
    L.append("")
    
    L.append(f"### {b.label} Points → A Houses")
    L.append("| Point | House in A |")
    L.append("|-------|------------|")
    for r in key_point_interactions(b, a):
        L.append(f"| {r['point']} | House {r['house_in_b']} |")
    L.append("")

    L.append("## 7. Dasha Timing Materials\n")
    lines, notes = dasha_overlap(a, b)
    for ln in lines:
        L.append(f"- {ln}")
    if notes:
        L.append("\nTrigger Clues:")
        for n in notes:
            L.append(f"- {n}")
    L.append("")

    L.append("## 8. Data Confidence & Completeness\n")
    L.append(f"- A Planet Parsing: {len([p for p in PLANETS if p in a.planets])}/9 | "
             f"B Planet Parsing: {len([p for p in PLANETS if p in b.planets])}/9")
    L.append(f"- A Moon Nakshatra: {'Present' if a.moon_nak else 'Missing'} | B Moon Nakshatra: {'Present' if b.moon_nak else 'Missing'}")
    L.append("- Interpretive weight follows D1 directional overlay > UL·DK > D9 > Dasha > Lunar Screening (see interpretation-rubric.md)")
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser(description="Cross-chart calculation engine for Vedic Synastry")
    ap.add_argument('a_path', help="Path to Partner A structured_data.md")
    ap.add_argument('b_path', help="Path to Partner B structured_data.md")
    ap.add_argument('out_dir', help="Output directory for synastry_data.md")
    ap.add_argument('--a', default='Partner A', help="Label for Partner A")
    ap.add_argument('--b', default='Partner B', help="Label for Partner B")
    args = ap.parse_args()

    a = Chart(args.a_path, args.a)
    b = Chart(args.b_path, args.b)
    md = build(a, b)
    os.makedirs(args.out_dir, exist_ok=True)
    out = os.path.join(args.out_dir, 'synastry_data.md')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"[ok] {out}")
    print(f"  A={args.a} planets {len([p for p in PLANETS if p in a.planets])}/9, "
          f"B={args.b} planets {len([p for p in PLANETS if p in b.planets])}/9")


if __name__ == '__main__':
    main()
