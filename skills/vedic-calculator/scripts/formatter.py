"""structured_data.md Formatter - Outputs canonical Vedic chart markdown in pure English."""

KARAKA_DESC = {
    'AK': 'Atmakaraka (Soul Indicator)',
    'AmK': 'Amatyakaraka (Career/Action Indicator)',
    'BK': 'Bhatrikaraka (Siblings/Guru Indicator)',
    'MK': 'Matrikaraka (Mother Indicator)',
    'PiK': 'Pitrikaraka (Father Indicator)',
    'PK': 'Putrakaraka (Children/Creativity Indicator)',
    'GK': 'Gnatikaraka (Obstacles/Rivals Indicator)',
    'DK': 'Darakaraka (Spouse/Partner Indicator)'
}

BAV_ROW_SUMS = {'Sun': 48, 'Moon': 49, 'Mars': 39, 'Mercury': 54, 'Jupiter': 56, 'Venus': 52, 'Saturn': 39}
SIGN_ABBR = ['Ar', 'Ta', 'Ge', 'Cn', 'Le', 'Vi', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi']
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
# 27 Nakshatra lords (Vimsottari cycle repeated 3 times), for independent verification
NAK_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'] * 3
P9 = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']

def format_structured_data(chart, transit_data, meta, user_info):
    """
    chart: Return value of calculate_full_chart()
    transit_data: Return value of calc_transit()
    meta: dict with keys: dob, time, place, lat, lon, time_precision, time_source
    user_info: dict with keys: gender, relationship
    """
    lines = []
    
    # === Meta Information ===
    lines.append("## Meta Information\n")
    lines.append("```")
    lines.append(f"Date of Birth: {meta['dob']}")
    lines.append(f"Time of Birth: {meta['time']}")
    lines.append(f"Place of Birth: {meta['place']} ({meta['lon']}, {meta['lat']})")
    lines.append(f"Time Precision: {meta.get('time_precision', 'Exact to the minute')}")
    lines.append(f"Time Source: {meta.get('time_source', 'Not asked')}")
    lines.append(f"Effective Precision: {meta.get('effective_precision', '±1 minute')}")
    lines.append(f"Validation Track: Track 1 - Standard")
    lines.append(f"Calculation Engine: vedic-calculator direct computation")
    lines.append(f"Ayanamsa: True Chitrapaksha (Lahiri, diff < 1') ({chart['ayanamsa']:.4f}°)")
    if chart.get('calc_meta'):
        cm = chart['calc_meta']
        lines.append(f"Calculation Provenance: engine {cm['engine_version']} | Instant UTC {cm['instant_utc']}"
                     f" | Actual Ayanamsa {cm['ayanamsa']:.6f}° (Planets and Lagna synchronized)")
    if chart.get('calc_errors'):
        failed = '; '.join(f"{k} ({v})" for k, v in chart['calc_errors'].items())
        lines.append(f"Calculation Incomplete: ⚠️ {failed} - Missing data; do not extrapolate mentally")
    if chart.get('dst_info'):
        di = chart['dst_info']
        if di['is_dst']:
            lines.append(f"Daylight Saving Time: ⚠️ Birth occurred during local DST (wall-clock time, UTC offset {di['utc_offset']}). If birth record is standard time, declare and recalculate.")
        else:
            lines.append(f"Daylight Saving Time: No (UTC offset {di['utc_offset']})")
    lines.append(f"Node Mode: Mean Node")
    lines.append("```\n")
    
    # === User Information ===
    lines.append("## User Information\n")
    lines.append("```")
    lines.append(f"Gender: {user_info.get('gender', '[Pending]')}")
    lines.append(f"Relationship Status: {user_info.get('relationship', '[Pending]')}")
    lines.append("```\n")
    
    # === D1 Natal Data ===
    lines.append("## D1 Natal Data\n")
    
    # Planetary Positions
    lines.append("### Planetary Positions")
    lines.append("| Planet | Sign | House | Longitude | Motion |")
    lines.append("|--------|------|-------|-----------|--------|")
    l = chart['lagna']
    lines.append(f"| Lagna | {l['sign']} | 1 | {l['deg_str']} | — |")
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        p = chart['planets'][name]
        r = 'R' if p['retrograde'] else 'D'
        lines.append(f"| {name} | {p['sign']} | {p['house']} | {p['deg_str']} | {r} |")
    lines.append("")
    
    # Chara Karakas (7K Primary - KN Rao System)
    lines.append("### Chara Karakas")
    lines.append("| Rank | Karaka | Planet | Degrees | Description |")
    lines.append("|------|--------|--------|---------|-------------|")
    for i, (k, planet, deg) in enumerate(chart['karakas']['7k']):
        desc = KARAKA_DESC.get(k, '')
        lines.append(f"| {i+1} | {k} | {planet} | {deg:.1f}° | {desc} |")
    lines.append("")
    lines.append("> KN Rao 7K System: 7 planets from Sun to Saturn ranked by longitude within sign.\n")
    
    # DK (Spouse Indicator)
    lines.append("### DK (Spouse Indicator)")
    lines.append("```")
    lines.append(f"DK = {chart['karakas']['dk_7k']} (7K Primary)")
    lines.append(f"8K Reference DK = {chart['karakas']['dk_8k']}")
    lines.append("```\n")
    
    # Nakshatra
    lines.append("### Nakshatra")
    lines.append("| Planet | Nakshatra | Pada | Nakshatra Lord |")
    lines.append("|--------|-----------|------|----------------|")
    nak = chart['lagna']['nakshatra']
    lines.append(f"| Lagna | {nak['name']} | {nak['pada']} | {nak['lord']} |")
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        nak = chart['planets'][name]['nakshatra']
        lines.append(f"| {name} | {nak['name']} | {nak['pada']} | {nak['lord']} |")
    lines.append("")
    
    # Special Points (AL/UL)
    sp = chart.get('special_points', {})
    if sp:
        lines.append("### Special Points")
        lines.append("| Point | Sign | House | Description |")
        lines.append("|-------|------|-------|-------------|")
        if 'AL' in sp:
            lines.append(f"| AL (Arudha Lagna) | {sp['AL']['sign']} | {sp['AL']['house']} | External Image / Worldly Perception |")
        if 'UL' in sp:
            lines.append(f"| UL (Upapada Lagna) | {sp['UL']['sign']} | {sp['UL']['house']} | Marriage / Partnership House |")
        lines.append("")
    
    # === Quantitative Data ===
    lines.append("## Quantitative Data\n")
    
    # Shadbala
    lines.append("### Shadbala")
    lines.append("| Planet | Rupas | Percentage | Rank | Strength | IshtaPhala | KashtaPhala | Baseline (calc) | Data Source / Verification |")
    lines.append("|--------|-------|------------|------|----------|------------|-------------|-----------------|----------------------------|")
    sb = chart['shadbala']
    if 'error' not in sb:
        sb_items = []
        for name, val in sb.items():
            if isinstance(val, dict) and 'total_rupas' in val:
                sb_items.append((name, val))
        sb_items.sort(key=lambda x: x[1].get('strength_pct', 0), reverse=True)
        for rank, (name, val) in enumerate(sb_items, 1):
            rupas = round(val['total_rupas'], 2)
            pct = round(val.get('strength_pct', 0), 2)
            strength = 'Strong' if pct >= 150 else ('Moderate' if pct >= 100 else 'Weak')
            ishta = round(val.get('ishta_phala', 0), 2)
            kashta = round(val.get('kashta_phala', 0), 2)
            baseline = f"{rupas} / {pct}%"
            lines.append(
                f"| {name} | {rupas} | {pct}% | {rank} | {strength} | "
                f"{ishta} | {kashta} | {baseline} | calc |"
            )
    lines.append("")
    lines.append("> Source: vedic-calculator engine (PyJHora + 9 bug corrections)")
    lines.append("> If importing JHora PDF for same birth time, compare Shadbala row-by-row; PDF values take precedence if discrepant.")
    lines.append("> Strong: >=150% | Moderate: 100-149% | Weak: <100%\n")
    
    # SAV
    lines.append("### SAV (Sarvashtakavarga)\n")
    lines.append("#### Raw Values (by Sign, for Verification)")
    lines.append("| " + " | ".join(SIGN_ABBR) + " | Total |")
    lines.append("|" + "----|" * 12 + "-------|")
    sav_vals = [chart['sav'].get(s, 0) for s in SIGNS]
    total = sum(sav_vals)
    lines.append("| " + " | ".join(str(v) for v in sav_vals) + f" | {total} |")
    lines.append("")
    
    lines.append("#### House Mapping (by House, for Core/Career/Love Analysis)")
    lines.append(f"> Lagna Sign: {chart['lagna']['sign']}\n")
    lines.append("| " + " | ".join(f"House {h}" for h in range(1, 13)) + " |")
    lines.append("|" + "--------|" * 12)
    house_vals = [str(chart['sav_by_house'][h]['value']) for h in range(1, 13)]
    lines.append("| " + " | ".join(house_vals) + " |")
    lines.append("")
    
    # BAV
    lines.append("### BAV (Bhinnashtakavarga)")
    lines.append("| Planet | " + " | ".join(SIGN_ABBR) + " | Row Sum |")
    lines.append("|--------|" + "----|" * 12 + "---------|")
    for pname in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        bav_row = chart['bav'].get(pname, {})
        vals = [bav_row.get(s, 0) for s in SIGNS]
        row_sum = sum(vals)
        lines.append(f"| {pname} | " + " | ".join(str(v) for v in vals) + f" | {row_sum} |")
    lines.append("")
    
    # Dasha
    lines.append("### Vimsottari Dasha")
    lines.append("> Date boundaries computed by PyJHora native MD/AD/PD; all intervals interpreted as [start, end).")
    lines.append("> Month-level questions require Pratyantardasha (PD); MD/AD only provides background/stage windows.\n")
    lines.append("| Dasha | Planet | Start | End | Years |")
    lines.append("|-------|--------|-------|-----|-------|")
    current_dasha = None
    next_dasha = None
    found_current = False
    for d in chart['dashas']:
        marker = '→ Current' if d['is_current'] else ''
        lines.append(f"| {marker} | {d['planet']} | {d['start']} | {d['end']} | {d['years']} |")
        if d['is_current']:
            current_dasha = d
            found_current = True
        elif found_current and next_dasha is None:
            next_dasha = d
    lines.append("")
    
    # Chara Dasha (K.N. Rao)
    if chart.get('chara_dasha'):
        import swisseph as _swe
        cd = chart['chara_dasha']
        direction_str = 'Direct' if cd['direction'] == 'forward' else 'Reverse'
        lines.append(f"### Chara Dasha Timeline (K.N. Rao, {direction_str})")
        lines.append("> Independent secondary timing system (Jaimini Rashi Dasha, KN Rao method).")
        lines.append("> Validated against JHora gold standard. Dual-system cross-validation:")
        lines.append("> When both Vimsottari and Chara Dasha point to the same theme window, confidence is upgraded.")
        lines.append("")
        lines.append("| Sign Dasha | Start | End | Years |")
        lines.append("|------------|-------|-----|-------|")
        import datetime as _dt
        _today_jd = _swe.julday(_dt.date.today().year, _dt.date.today().month, _dt.date.today().day, 12.0)
        for md in cd['mahadashas']:
            y1, m1, d1, _ = _swe.revjul(md['start_jd'])
            y2, m2, d2, _ = _swe.revjul(md['end_jd'])
            marker = ' ← Current' if md['start_jd'] <= _today_jd < md['end_jd'] else ''
            lines.append(f"| {md['sign']} | {y1:04d}-{m1:02d}-{d1:02d} | {y2:04d}-{m2:02d}-{d2:02d} | {md['years']} |{marker}")
        lines.append("")

    # Antardasha
    for d in chart['dashas']:
        if 'antardashas' in d:
            label = 'Current' if d['is_current'] else ('Next' if d == next_dasha else '')
            label_str = f" ({label})" if label else ""
            lines.append(f"### {d['planet']} Mahadasha Antardashas{label_str}")
            lines.append("| Antardasha | Start | End |")
            lines.append("|------------|-------|-----|")
            for ad in d['antardashas']:
                marker = ' ← Current' if ad.get('is_current') else ''
                lines.append(f"| {d['planet']}-{ad['planet']} | {ad['start']} | {ad['end']} |{marker}")
            lines.append("")

    # Pratyantardasha
    for d in chart['dashas']:
        if not d.get('antardashas'):
            continue
        lines.append(f"### {d['planet']} Mahadasha Pratyantardashas (Level 3)")
        lines.append("| Level 3 Dasha | Start | End |")
        lines.append("|---------------|-------|-----|")
        for ad in d['antardashas']:
            for pd in ad.get('pratyantardashas', []):
                marker = ' ← Current' if pd.get('is_current') else ''
                path = f"{d['planet']}-{ad['planet']}-{pd['planet']}"
                lines.append(f"| {path} | {pd['start']} | {pd['end']} |{marker}")
        lines.append("")
    
    # Current Dasha Status Summary
    if current_dasha:
        lines.append("Current Dasha Status:")
        lines.append("```")
        lines.append(f"Mahadasha: {current_dasha['planet']} ({current_dasha['start']} ~ {current_dasha['end']})")
        current_ad_info = None
        if 'antardashas' in current_dasha:
            for ad in current_dasha['antardashas']:
                if ad.get('is_current'):
                    current_ad_info = ad
                    break
        if current_ad_info:
            lines.append(f"Antardasha: {current_dasha['planet']}-{current_ad_info['planet']} ({current_ad_info['start']} ~ {current_ad_info['end']})")
            current_pd_info = next(
                (pd for pd in current_ad_info.get('pratyantardashas', []) if pd.get('is_current')),
                None,
            )
            if current_pd_info:
                lines.append(
                    f"Pratyantardasha: {current_dasha['planet']}-{current_ad_info['planet']}-"
                    f"{current_pd_info['planet']} ({current_pd_info['start']} ~ {current_pd_info['end']})"
                )
        lines.append("```\n")

    # === Pre-Analysis ===
    lines.append("## Pre-Analysis (Computed by Calculator, Referenced by Core)\n")
    
    # Compound Dignity
    lines.append("### Planetary Dignity (Compound Dignity / Panchadha Maitri)")
    lines.append("| Planet | Sign | Dispositor | Compound Dignity | Description |")
    lines.append("|--------|------|------------|------------------|-------------|")
    SIGN_LORDS_MAP = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
        'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
        'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    }
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        p = chart['planets'][name]
        dig = chart['dignity'].get(name, {})
        lord = SIGN_LORDS_MAP.get(p['sign'], '?')
        compound = dig.get('compound', '-')
        lines.append(f"| {name} | {p['sign']} | {lord} | {compound} | |")
    lines.append("")

    # Neecha Bhanga
    nb = chart.get('neecha_bhanga') or {}
    if nb:
        lines.append("### Cancellation of Debilitation (Neecha Bhanga - Audited)")
        lines.append("> Cancellation rules follow Phaladeepika 7.26-30, 7.3. Cushions provide narrative context without adding to rule count.")
        lines.append("| Debilitated Planet | Dispositor | Exaltation Lord | Cancellation Rules (Evidence) | Independent Rules | Cushions | Tier | Exclude Debilitation in Dasha | Exaltation Lord Alternative |")
        lines.append("|--------------------|------------|-----------------|-------------------------------|-------------------|----------|------|------------------------------|-----------------------------|")
        for name, r in nb.items():
            forms = '; '.join(f"{f['id']}: {f['evidence']}" for f in r['forms']) or '—'
            alt = r.get('alt')
            alt_s = (f"{alt['exaltation_lord']}: {alt['independent']} rules, {alt['tier']}"
                     f"{', Dasha uncounted' if alt['dasha_not_counted'] else ''}") if alt else '—'
            lines.append(f"| {name} | {r['dispositor']} | {r['exaltation_lord']} | {forms} | {r['independent']} | "
                         f"{'; '.join(r['cushions']) or '—'} | {r['tier']} | {'Yes' if r['dasha_not_counted'] else 'No'} | {alt_s} |")
        lines.append("")

    # Graha Drishti
    lines.append("### Graha Drishti (Vedic Planetary Aspects - House Projections)")
    lines.append("> ⚠️ Parashari graha drishti (planet-to-house projections). Vedic aspects are full-sign house projections, not Western degree orbs.")
    lines.append("| Planet | House | Aspected Houses | Aspected Planets |")
    lines.append("|--------|-------|-----------------|------------------|")
    gd = chart.get('graha_drishti', {})
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        if name in gd:
            i = gd[name]
            ah = '/'.join(str(x) for x in i['aspected_houses'])
            ap = '/'.join(i['aspected_planets']) or '—'
            tag = ' (Amplified)' if i.get('amplify') else ''
            lines.append(f"| {name}{tag} | House {i['from_house']} | Houses {ah} | {ap} |")
    lines.append("")

    # Functional Roles
    fn = chart.get('functional', {})
    if fn:
        lines.append("### Functional Roles (P1 Primary Role - MT Sign Determines Lordship)")
        lines.append("> ⚠️ Primary functional role is determined by Moolatrikona (MT) sign lordship.")
        lines.append("| Planet | Lorded Houses | MT House | Primary Role | Yogakaraka | Dual Benefic/Malefic |")
        lines.append("|--------|---------------|----------|--------------|------------|----------------------|")
        for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            if name in fn:
                v = fn[name]
                lh = '/'.join(str(x) for x in v['lorded_houses'])
                yk = 'Yes' if v['is_yogakaraka'] else '—'
                dl = 'Yes' if v['is_dual_benefic_malefic'] else '—'
                lines.append(f"| {name} | {lh} | {v['moolatrikona_house']} | {v['primary_role']} | {yk} | {dl} |")
        lines.append("")

    # Structural Yoga Prescan
    yp = chart.get('yoga_prescan', {})
    if yp:
        lines.append("### Structural Yoga Prescan")
        lines.append("> ⚠️ Structural skeletal condition audit (Active = True/False + participating planets). Strength, cancellation nuances, and qualitative assessments are evaluated downstream by the analysis model.")
        lines.append("| Yoga | Structure Active | Participants / Notes |")
        lines.append("|------|------------------|----------------------|")
        vry = yp.get('vry', {})
        for key, en_name in [('harsha', 'VRY-Harsha (Lord 6)'), ('sarala', 'VRY-Sarala (Lord 8)'), ('vimala', 'VRY-Vimala (Lord 12)')]:
            v = vry.get(key, {})
            lines.append(f"| {en_name} | {'Active' if v.get('active') else 'Inactive'} | Lord {v.get('lord','')} in House {v.get('lord_house','')} |")
        def yrow(key, en_name, note=''):
            v = yp.get(key, {})
            lines.append(f"| {en_name} | {'Active' if v.get('active') else 'Inactive'} | {note} |")
        dk = yp.get('dharma_karma', {}).get('lords', ['', ''])
        yrow('dharma_karma', 'Dharma-Karma', f"Lord 9 ({dk[0]}) & Lord 10 ({dk[1]}) interaction")
        dh = yp.get('dhana', {}).get('lords', ['', ''])
        yrow('dhana', 'Dhana', f"Lord 2 ({dh[0]}) & Lord 11 ({dh[1]}) interaction")
        yrow('raja', 'Raja', f"{len(yp.get('raja', {}).get('hits', []))} Trikona × Kendra lord interaction pair(s)")
        yrow('chandra_mangala', 'Chandra-Mangala', 'Moon-Mars conjunction or mutual aspect')
        yrow('guru_chandala', 'Guru-Chandala', 'Jupiter-Rahu conjunction')
        yrow('gajakesari', 'Gajakesari', 'Jupiter & Moon in mutual Kendras')
        ad = yp.get('adhi', {})
        yrow('adhi', 'Adhi', f"Benefics {ad.get('benefics', [])} in houses {ad.get('from_moon_678', [])} from Moon" + (' (Malefic contamination)' if ad.get('malefic_contam') else ''))
        km = yp.get('kemadruma', {})
        lines.append(f"| Kemadruma | {'Active' if km.get('active') else 'Inactive'} | {'Cancelled' if km.get('cancelled') else 'Uncancelled'} |")
        sk = yp.get('shakata', {})
        lines.append(f"| Shakata | {'Active' if sk.get('active') else 'Inactive'} | {'Cancelled' if sk.get('cancelled') else 'Uncancelled'} |")
        for g, v in yp.get('mahapurusha', {}).items():
            lines.append(f"| Mahapurusha-{g} ({v.get('star')}) | {'Active' if v.get('active') else 'Inactive'} | House {v.get('house')} ({v.get('sign')}) |")
        lines.append("")

    # Yoga Relationships: Mutual Aspects / Parivartana
    md_pairs = chart.get('mutual_drishti', [])
    pv = chart.get('parivartana', [])
    lines.append("### Yoga Relationships: Mutual Aspects / Parivartana")
    lines.append("> Mutual aspect requires bidirectional projection. Planetary exchange requires reciprocal dispositorship.")
    lines.append(f"- **Mutual Aspect Pairs (Bidirectional)**: {(', '.join(' + '.join(p) for p in md_pairs)) if md_pairs else 'None'}")
    if pv:
        lines.append("- **Exchange Pairs (Parivartana)**:")
        for x in pv:
            lines.append(f"  - House {x['houses'][0]} ↔ House {x['houses'][1]} ({x['lords'][0]} ↔ {x['lords'][1]}, {x['type']})")
    else:
        lines.append("- **Exchange Pairs (Parivartana)**: None")
    lines.append("")

    # House Lords
    lines.append("### House Lords Table")
    lines.append("| House | Domain | Lord | Lord's House |")
    lines.append("|-------|--------|------|--------------|")
    for h in range(1, 13):
        info = chart['house_lords'][h]
        lines.append(f"| {h} | {info['domain']} | {info['lord']} | {info.get('lord_house','?')} |")
    lines.append("")
    
    # === Divisional Charts (Vargas) ===
    lines.append("## Divisional Charts (Vargas)\n")
    lines.append("### Divisional Reliability Declaration")
    lines.append("```")
    boundary_audit = chart.get('divisional_boundary_audit', {})
    if boundary_audit.get('status') == 'ok':
        span = boundary_audit.get('uncertainty_minutes', 0)
        lines.append(f"Boundary Audit Range: ±{span} minutes around reported time, scanned minute-by-minute")
        audited = boundary_audit.get('charts', {})
        for key in ('D1', 'D9', 'D10', 'D4', 'D5'):
            item = audited.get(key, {})
            base = item.get('base_sign', '—')
            observed = '→'.join(item.get('observed_signs', [])) or 'Unavailable'
            if item.get('stable'):
                lines.append(f"{key:<3} ✅ Stable across audit interval (Lagna={base})")
            else:
                lines.append(f"{key:<3} ⚠️ Boundary sensitive (Lagna={observed}); divisional house conclusions must be conditional")
    else:
        lines.append("D1  ⚠️ Calculated directly; time uncertainty boundary audit pending")
        lines.append("D9  ⚠️ Calculated directly; divisional input stability unverified")
        lines.append("D10 ⚠️ Calculated directly; divisional input stability unverified")
        lines.append("D4  ⚠️ Calculated directly; divisional input stability unverified")
        lines.append("D5  ⚠️ Calculated directly; divisional input stability unverified")
    lines.append("```\n")
    lines.append("> Direct calculation reflects mathematical reproducibility for the exact timestamp. Source reliability differs from mathematical divisional stability. Boundary-sensitive divisional charts require conditional interpretation.")
    lines.append("")
    
    # D9
    lines.append("### D9 Navamsha")
    lines.append("| Planet | D9 Sign | D9 House | Vargottama | D9 Dignity | D9 Dispositor |")
    lines.append("|--------|---------|----------|------------|------------|---------------|")
    d9l = chart['d9']['Lagna']
    lines.append(f"| Lagna | {d9l[0]} | 1 | — | — | — |")
    D9_DIG_LABEL = {'exalted': 'Exalted', 'own': 'Own Sign', 'debilitated': 'Debilitated',
                    'friend': 'Friend', 'enemy': 'Enemy', 'neutral': 'Neutral'}
    d9dig = chart.get('d9_dignity', {})
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        sign, sidx = chart['d9'][name]
        d9_house = ((sidx - chart['d9']['Lagna'][1]) % 12) + 1
        varg = 'Yes' if chart['vargottama'].get(name, False) else 'No'
        dd = d9dig.get(name, {})
        dlab = D9_DIG_LABEL.get(dd.get('dignity'), '—')
        disp = dd.get('dispositor', '—')
        lines.append(f"| {name} | {sign} | {d9_house} | {varg} | {dlab} | {disp} |")
    lines.append("> D9 dignity and dispositors are verified lookups directly from the calculation engine.")
    lines.append("")

    # Pushkara
    pk = chart.get('pushkara')
    if pk and 'error' not in pk:
        nav = ', '.join(pk.get('pushkara_navamsa', [])) or 'None'
        bhaga = ', '.join(pk.get('pushkara_bhaga', [])) or 'None'
        lines.append(f"Pushkara Navamsa (Nourishing Zone): {nav}")
        lines.append(f"Pushkara Bhaga (Exact Degree of Nourishment): {bhaga}")
        lines.append("")

    # D10
    lines.append("### D10 Dasamsha")
    lines.append("| Planet | D10 Sign | D10 House |")
    lines.append("|--------|----------|-----------|")
    d10l = chart['d10']['Lagna']
    lines.append(f"| Lagna | {d10l[0]} | 1 |")
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        sign, sidx = chart['d10'][name]
        d10_house = ((sidx - chart['d10']['Lagna'][1]) % 12) + 1
        lines.append(f"| {name} | {sign} | {d10_house} |")
    lines.append("")
    
    # D4
    lines.append("### D4 Chaturthamsha")
    lines.append("| Planet | D4 Sign | D4 House |")
    lines.append("|--------|---------|----------|")
    d4l = chart['d4']['Lagna']
    lines.append(f"| Lagna | {d4l[0]} | 1 |")
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        sign, sidx = chart['d4'][name]
        d4_house = ((sidx - chart['d4']['Lagna'][1]) % 12) + 1
        lines.append(f"| {name} | {sign} | {d4_house} |")
    lines.append("")
    
    # D5
    lines.append("### D5 Panchamsha")
    lines.append("| Planet | D5 Sign | D5 House |")
    lines.append("|--------|---------|----------|")
    d5l = chart['d5']['Lagna']
    lines.append(f"| Lagna | {d5l[0]} | 1 |")
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        sign, sidx = chart['d5'][name]
        d5_house = ((sidx - chart['d5']['Lagna'][1]) % 12) + 1
        lines.append(f"| {name} | {sign} | {d5_house} |")
    lines.append("")

    # Internal Divisional House Lords & Dignities
    vi = chart.get('varga_internal', {})
    if vi:
        lines.append("### Internal Divisional House Lords & Dignities")
        lines.append("> Line A = House lords derived from divisional chart Lagna itself (D*-L*). Line B = Natal house lords mapped into divisional chart.")
        DIG = {'exalted': 'Exalted', 'own': 'Own Sign', 'debilitated': 'Debilitated', 'friend': 'Friend', 'enemy': 'Enemy', 'neutral': 'Neutral'}
        GRAHA = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        for dv in ['D9', 'D10', 'D4', 'D5']:
            v = vi.get(dv)
            if not v:
                continue
            hl = v['house_lords']
            dg = v['dignity']
            lords_str = " ".join(f"{dv}-L{h}={hl[h]['lord']}@H{hl[h]['lord_house']}" for h in range(1, 13))
            dig_str = " ".join(f"{n}={DIG.get(dg[n]['dignity'],'?')}/Dispositor:{dg[n]['dispositor']}" for n in GRAHA if n in dg)
            lines.append(f"**{dv}** Lagna={v['lagna_sign']} ({dv}-Lagna Lord={v['lagna_lord']})")
            lines.append(f"  House Lords (Line A): {lords_str}")
            lines.append(f"  Divisional Dignities: {dig_str}")
        lines.append("")

    # === Verification Results ===
    lines.append("## Verification Results\n")
    sav_total = sum(chart['sav'].get(s, 0) for s in SIGNS)
    sav_ok = '✅' if sav_total == 337 else '❌'
    
    # BAV Row Sum Check
    bav_ok = '✅'
    bav_detail = ''
    for pname, expected in BAV_ROW_SUMS.items():
        row = chart['bav'].get(pname, {})
        actual = sum(row.get(s, 0) for s in SIGNS)
        if actual != expected:
            bav_ok = '❌'
            bav_detail += f'{pname}:{actual}≠{expected} '
    
    # Ra-Ke 180°
    ra_lon = chart['planets']['Rahu']['longitude']
    ke_lon = chart['planets']['Ketu']['longitude']
    ra_ke_diff = abs(ra_lon - ke_lon)
    if ra_ke_diff > 180:
        ra_ke_diff = 360 - ra_ke_diff
    ra_ke_ok = '✅' if abs(ra_ke_diff - 180) < 0.01 else '❌'
    
    # Combustion
    comb_list = list(chart['combustion'].keys()) if chart['combustion'] else []
    comb_str = ', '.join(comb_list) if comb_list else 'None'
    
    # Moon Phase
    phase = chart['moon_phase']
    phase_name = 'Waxing (Shukla Paksha)' if phase['waxing'] else 'Waning (Krishna Paksha)'
    phase_str = f"{phase_name} (Dist from Sun {phase['sun_moon_diff']}°)"

    # Vimsottari Hierarchy & Continuity
    md_count = len(chart.get('dashas', []))
    ad_count = sum(len(md.get('antardashas', [])) for md in chart.get('dashas', []))
    pd_count = sum(
        len(ad.get('pratyantardashas', []))
        for md in chart.get('dashas', [])
        for ad in md.get('antardashas', [])
    )
    dasha_continuous = True
    all_ads = [
        ad
        for md in chart.get('dashas', [])
        for ad in md.get('antardashas', [])
    ]
    dasha_continuous &= all(
        all_ads[i]['end_time'] == all_ads[i + 1]['start_time']
        for i in range(len(all_ads) - 1)
    )
    for md in chart.get('dashas', []):
        ads = md.get('antardashas', [])
        dasha_continuous &= all(ads[i]['end_time'] == ads[i + 1]['start_time'] for i in range(len(ads) - 1))
        for ad in ads:
            pds = ad.get('pratyantardashas', [])
            dasha_continuous &= bool(pds)
            dasha_continuous &= all(pds[i]['end_time'] == pds[i + 1]['start_time'] for i in range(len(pds) - 1))
            if pds:
                dasha_continuous &= pds[0]['start_time'] == ad['start_time']
                dasha_continuous &= pds[-1]['end_time'] == ad['end_time']
    dasha_ok = '✅' if (md_count, ad_count, pd_count) == (9, 81, 729) and dasha_continuous else '❌'

    # Independent calculations for verification checks
    P = chart.get('planets', {})
    body_count = len([p for p in P9 if p in P]) + (1 if chart.get('lagna') else 0)
    body_ok = '✅' if body_count == 10 else '❌'

    lons = [round(P[p]['longitude'], 6) for p in P9 if p in P]
    uniq_ok = '✅' if len(lons) == len(set(lons)) else '❌'

    retro_ok = '✅' if (
        all(isinstance(P.get(p, {}).get('retrograde'), bool) for p in P9)
        and P.get('Rahu', {}).get('retrograde') and P.get('Ketu', {}).get('retrograde')
    ) else '❌'

    sun_lon = P.get('Sun', {}).get('longitude')
    comb_ok = '❌' if sun_lon is None else '✅'
    if sun_lon is not None:
        for p in comb_list:
            if p == 'Sun' or p not in P:
                comb_ok = '❌'
                break
            _d = abs(P[p]['longitude'] - sun_lon)
            if _d > 180:
                _d = 360 - _d
            if _d > 17:
                comb_ok = '❌'
                break

    ay = chart.get('ayanamsa')
    aya_ok = '✅' if isinstance(ay, (int, float)) and 22.0 <= ay <= 25.0 else '❌'

    # Nakshatra ↔ Degrees: independently recomputed
    nak_ok = '✅'
    for p in P9:
        if p not in P:
            nak_ok = '❌'
            break
        nk = P[p].get('nakshatra') or {}
        _lon = P[p]['longitude']
        if (nk.get('pada') != int((_lon % (360/27)) / (360/108)) + 1
                or nk.get('lord') != NAK_LORDS[int(_lon / (360/27))]):
            nak_ok = '❌'
            break

    # Chara Karaka: independent descending sort
    try:
        _k7 = sorted(['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'],
                     key=lambda n: P[n]['degree'], reverse=True)
        karaka_ok = '✅' if chart.get('karakas', {}).get('dk_7k') == _k7[6] else '❌'
    except (KeyError, TypeError):
        karaka_ok = '❌'

    # D9 cross-check
    d9 = chart.get('d9', {})
    d9_ok = '✅'
    _d9_lons = {p: P[p]['longitude'] for p in P9 if p in P}
    if chart.get('lagna'):
        _d9_lons['Lagna'] = chart['lagna']['longitude']
    for p in P9 + ['Lagna']:
        if p not in _d9_lons or p not in d9:
            d9_ok = '❌'
            break
        _lon = _d9_lons[p]
        if d9[p][1] != (9 * int(_lon / 30) + int((_lon % 30) / (30/9))) % 12:
            d9_ok = '❌'
            break

    # Ra-Ke in D9: 180° separation
    try:
        rake_d9_ok = '✅' if (d9['Ketu'][1] - d9['Rahu'][1]) % 12 == 6 else '❌'
    except (KeyError, TypeError, IndexError):
        rake_d9_ok = '❌'

    lines.append("```")
    lines.append(f" 1. SAV={sav_total}                       {sav_ok}")
    lines.append(f" 2. BAV Row Constants            {bav_ok} {bav_detail}")
    lines.append(f" 3. Planet Completeness (10)     {body_ok} {body_count}/10")
    lines.append(f" 4. Longitude Uniqueness         {uniq_ok}")
    lines.append(f" 5. Ra-Ke 180° Separation        {ra_ke_ok}")
    lines.append(f" 6. Retrograde Markers Complete  {retro_ok}")
    lines.append(f" 6b. Combustion Detection        {comb_ok} [{comb_str}]")
    if isinstance(ay, (int, float)):
        lines.append(f" 7. Ayanamsa Consistency        {aya_ok} True Chitra {ay:.4f}°")
    else:
        lines.append(f" 7. Ayanamsa Consistency        {aya_ok} True Chitra")
    lines.append(f" 7c. Moon Phase                  {phase_str}")
    lines.append(f" 8. Nakshatra-Degree Check       {nak_ok}")
    lines.append(f" 9. Chara Karaka Ordering        {karaka_ok}")
    lines.append(f"10. Vimsottari Hierarchy         {dasha_ok} MD={md_count}/AD={ad_count}/PD={pd_count} Continuous={dasha_continuous}")
    lines.append(f"11. D9 Formula Cross-Check       {d9_ok} (Independent longitude recomputation)")
    lines.append(f"12. Ra-Ke Divisional Check       {rake_d9_ok} (D9 6-sign separation)")
    lines.append("```\n")
    
    # === Transit Data ===
    if transit_data:
        lines.append("## Current Transit Positions (Transit Data)\n")
        lines.append(f"> Data Source: vedic-calculator direct computation")
        lines.append(f"> Extracted Timestamp: {transit_data['date']}\n")
        
        lines.append("### Slow Planet Transits")
        lines.append("| Planet | Transit Sign | Transit House (from Lagna) | Cycle / Notes |")
        lines.append("|--------|--------------|----------------------------|---------------|")
        for name in ['Saturn', 'Jupiter', 'Rahu', 'Ketu']:
            t = transit_data['planets'][name]
            lines.append(f"| {name} | {t['sign']} | {t['house']} | {t['cycle']} |")
        lines.append("")
        
        lines.append("### Sade Sati Assessment")
        lines.append("```")
        ss = transit_data['sade_sati']
        lines.append(f"Natal Moon Sign: {ss['moon_sign']}")
        lines.append(f"Transit Saturn Sign: {ss['saturn_sign']}")
        lines.append(f"Relative Position: {ss['position']}")
        lines.append(f"Sade Sati Status: {ss['status']}")
        lines.append("```\n")
        
        lines.append("### Double Transit Trigger Check (Saturn-Jupiter Double Transit)")
        lines.append("```")
        lines.append(f"Saturn Transit Aspect Coverage (Houses): {transit_data['saturn_covers']}")
        lines.append(f"Jupiter Transit Aspect Coverage (Houses): {transit_data['jupiter_covers']}")
        lines.append(f"Double Transit Activated Houses: {transit_data['double_transit']}")
        lines.append("```")

        if transit_data.get('future_ingress'):
            lines.append("")
            lines.append("### Future Ingress Table (Astronomical Calculation, Next 5 Years)")
            lines.append("> ⚠️ Dates reflect actual astronomical ingresses. Retrograde crossings are listed chronologically.")
            lines.append("")
            lines.append("| Date | Planet | Ingress Transition |")
            lines.append("|------|--------|--------------------|")
            for ev in transit_data['future_ingress']:
                lines.append(f"| {ev['date']} | {ev['planet']} | {ev['from_sign']} → {ev['to_sign']} |")
            lines.append("")

    return '\n'.join(lines)
