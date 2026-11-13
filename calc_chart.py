import sys, os
from pathlib import Path

# Resolve scripts directory relative to this file
REPO_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = REPO_ROOT / "skills" / "vedic-calculator" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from engine import calculate_full_chart
from transit import calc_transit
from formatter import format_structured_data

# Calculate natal chart
chart = calculate_full_chart(
    year=2003, month=6, day=12,
    hour=17, minute=27,
    lat=15.4317, lon=75.6260,
    tz_str="Asia/Kolkata",
    uncertainty_minutes=1,
    second=0,
)

# Calculate current transits
transit = calc_transit(
    chart['lagna']['sign_idx'],
    chart['planets']['Moon']['sign_idx'],
    "Asia/Kolkata"
)

# Meta information
meta = {
    'dob': '2003-06-12',
    'time': '17:27',
    'place': 'Gadag, Karnataka',
    'lat': 15.4317, 'lon': 75.6260,
    'time_precision': 'Exact to the minute',
    'time_source': 'Not asked'
}

# User info
user_info = {
    'gender': 'Not provided',
    'relationship': 'Not provided'
}

# Generate structured_data.md
md = format_structured_data(chart, transit, meta, user_info)
output_path = REPO_ROOT / "structured_data.md"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(md)

# SAV validation
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
sav_total = sum(chart['sav'].get(s, 0) for s in SIGNS)
print(f"✅ SAV total: {sav_total}")
assert sav_total == 337, f"SAV FAILED: {sav_total} != 337"

# Print key data for verification
print(f"✅ Lagna: {chart['lagna']['sign']} {chart['lagna']['deg_str']}")
print(f"✅ Moon: {chart['planets']['Moon']['sign']} {chart['planets']['Moon']['deg_str']}")
print(f"✅ Ayanamsa: {chart['ayanamsa']}")
print(f"✅ Planet count: {len(chart['planets'])}")

# Check Rahu-Ketu 180 degree separation
rahu_lon = chart['planets']['Rahu']['longitude']
ketu_lon = chart['planets']['Ketu']['longitude']
diff = abs(rahu_lon - ketu_lon)
if diff > 180:
    diff = 360 - diff
print(f"✅ Rahu-Ketu diff: {diff:.1f}°")

# Dasha info
dasha_count = len(chart['dashas'])
ad_count = sum(len(d['antardashas']) for d in chart['dashas'])
pd_count = sum(len(ad['pratyantardashas']) for d in chart['dashas'] for ad in d['antardashas'])
print(f"✅ Dashas: {dasha_count} MD, {ad_count} AD, {pd_count} PD")

# Print calc_errors if any
if chart.get('calc_errors'):
    print(f"⚠️ Calc errors: {chart['calc_errors']}")
else:
    print("✅ No calculation errors")

print(f"\n✅ Chart calculation complete! Output written to {output_path}")
