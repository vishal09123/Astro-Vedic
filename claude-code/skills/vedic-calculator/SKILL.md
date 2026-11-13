---
name: vedic-calculator
description: "Calculate a complete Vedic/Jyotish natal chart directly from birth date, exact time, and place, producing the canonical structured_data.md for downstream analysis. Use for requests such as 'calculate my Vedic chart', 'cast my birth chart', 'generate a chart from my birth details'. Also use when vedic-reader has birth details but no chart file."
---

# vedic-calculator: Vedic Astrology Natal Calculation Engine

## Language Contract

- Set `client_language` from the user's explicit language request; otherwise default to English.
- Use `client_language` for all chat replies, intake questions, confirmations, progress updates, user-visible warnings, reports, and Q&A.
- Keep canonical filenames, CLI flags, JSON keys, `structured_data.md` schema headings, technical codes, and Sanskrit/English identifiers unchanged. These are internal interoperability contracts; explain them in `client_language` when presented to the user.
- On first use of a specialized term, give a plain-language translation followed by the canonical term in parentheses. Never translate canonical identifiers inside calculations or evidence citations.
- If the user changes language mid-run, preserve the existing data and artifact lineage; switch client-facing language from that point onward unless explicitly requested otherwise.

> Based on the pysweph Swiss Ephemeris astronomical engine + PyJHora precise algorithms, directly calculating full natal chart data from birth details.
> Output format is fully compatible with vedic-reader's `structured_data.md` and can be passed directly to `vedic-core` for synthesis.

## Prerequisites

- Python 3.8 ~ 3.13 (pysweph is a C extension; Python 3.14 is currently not supported)
- Dependencies: `pysweph`, `PyJHora==4.8.6`, `pytz`, `tzdata` (timezone rules library; required on Windows for vedic-prashna)

> ⚠️ **Do not run `pip install -r requirements.txt` directly!** PyJHora has unstated runtime dependencies, and the default PyPI package lacks `.se1` ephemeris files.
> Always use `setup_env.py` for automated installation (see below).

### Automated Environment Detection

```
Checks dependency availability prior to execution (in order of priority):

  1. Check for existing venv/ in <skill_dir> or workspace root:
     - <skill_dir>/venv/
     - <workspace>/vedic-calc-env/
     - <workspace>/venv/
     Found -> run with its Python -> try `import swisseph` -> Success -> use directly.

  2. Attempt `import swisseph` in current Python:
     - Successful and swe.version != '0.0.0' -> use directly.
     - Failed or dummy stub -> proceed to setup.

  3. Automated venv creation (via setup_env.py):
     <suitable_python> <skill_dir>/scripts/setup_env.py
     The script automatically detects Python version -> creates venv -> installs in proper order -> validates SAV=337.
```

> ⚠️ `<skill_dir>` = installation path of the vedic-calculator skill.
> ⚠️ If default system Python is 3.14, `setup_env.py` searches for 3.12/3.13 to create the venv.

### ⚠️ Initial Environment Diagnostic

```
Before using vedic-calculator for the first time in a new environment, run:

  python <skill_dir>/scripts/check_env.py

This script verifies:
  ✅ venv location and Python version
  ✅ Core dependencies (pysweph, PyJHora, pytz) + zoneinfo database (tzdata on Windows)
  ✅ swisseph stub detection
  ✅ Ephemeris files (.se1)
  ✅ Minimal calculation test (SAV=337 verification)

If output shows 🎉 -> use the reported Python binary path directly.
If output shows ⚠️ -> follow instructions to run setup_env.py.
```

## Workflow

### Step 1: Collect Birth Details

Collect from user:
```
- Date of Birth (YYYY-MM-DD)
- Time of Birth (HH:MM, 24-hour format; if source includes seconds, record them; do not prompt if seconds are absent)
- Place of Birth (City name, State/Region, Country)
- Gender
- Relationship Status (Optional)
- Time Precision (Exact to minute / ±15 minutes / ±1 hour / Uncertain)
- Time Source (Birth certificate / Hospital record / Family memory / Rough estimate / Unverified)
```

⚠️ Daylight Saving Time (DST) Confirmation:
```
When birth falls during local DST periods, confirm with the user:
"Daylight saving time was in effect at your birth location. Was the provided birth time taken directly from the clock on the wall? (Usually yes).
 If your family recorded unadjusted standard time, please specify."
-> Wall clock (Default) -> standard calculation (pytz handles DST to UTC conversion accurately).
-> User states standard time -> calculate with fixed offset (e.g., 'Etc/GMT-8' instead of 'Asia/Shanghai'), noted in metadata.
```

### Step 2: Coordinate Resolution

Convert city name to:
- Latitude (`lat`, float, positive=North)
- Longitude (`lon`, float, positive=East)
- Timezone identifier (`tz_str`, e.g., "Asia/Kolkata", "America/New_York", "Asia/Shanghai")

Common references:
```
New Delhi:  28.6139, 77.2090,  "Asia/Kolkata"
Mumbai:     19.0760, 72.8777,  "Asia/Kolkata"
London:     51.5074, -0.1278,  "Europe/London"
New York:   40.7128, -74.0060, "America/New_York"
Beijing:    39.9042, 116.4074, "Asia/Shanghai"
Singapore:   1.3521, 103.8198, "Asia/Singapore"
Tokyo:      35.6762, 139.6503, "Asia/Tokyo"
```

### Step 3: Run Engine

Create and execute calculation script in workspace:

```python
import sys, os

SCRIPTS_DIR = r"<absolute_path_to_vedic-calculator_scripts>"
sys.path.insert(0, SCRIPTS_DIR)

from engine import calculate_full_chart
from transit import calc_transit
from formatter import format_structured_data

# Calculate natal chart
chart = calculate_full_chart(
    year=YYYY, month=MM, day=DD, 
    hour=HH, minute=MM,
    lat=LAT, lon=LON, 
    tz_str="TIMEZONE",
    uncertainty_minutes=1,
    second=0,
)

# Calculate current transits
transit = calc_transit(
    chart['lagna']['sign_idx'],
    chart['planets']['Moon']['sign_idx'],
    "TIMEZONE"
)

# Metadata
meta = {
    'dob': 'YYYY-MM-DD',
    'time': 'HH:MM',
    'place': 'City, Country',
    'lat': LAT, 'lon': LON,
    'time_precision': 'Exact to minute',
    'time_source': 'Birth Certificate'
}

# User context
user_info = {
    'gender': 'Male/Female/Other',
    'relationship': 'Single/In Relationship/Married'
}

# Generate structured_data.md
md = format_structured_data(chart, transit, meta, user_info)
with open("structured_data.md", 'w', encoding='utf-8') as f:
    f.write(md)

# SAV Verification
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
sav_total = sum(chart['sav'].get(s, 0) for s in SIGNS)
print(f"✅ SAV total: {sav_total}")
assert sav_total == 337, f"SAV FAILED: {sav_total} != 337"
```

### Step 4: Verification Checklist

Every calculation must satisfy:
1. `structured_data.md` generated with UTF-8 encoding.
2. SAV total equals exactly 337.
3. Rahu and Ketu are exactly 180°00' opposite.
4. Ascendant degree and sign match local sidereal time.
5. Vimshottari Dasha spans 120 years across 9 MDs, 81 ADs, and 729 PDs with continuous `[start, end)` boundaries.

## Technical Specifications

- Ayanamsa: **True Chitrapaksha (TRUE_CITRA)** (Lahiri system, difference < 1′)
- Node Mode: **Mean Node**
- Astronomical Kernel: `pysweph` (Swiss Ephemeris C-bindings)
- SAV / BAV: Native PyJHora (`ashtakavarga_pyjhora.py`)
- Dasha Calculation: Native PyJHora MD/AD/PD (`dasha_pyjhora.py`) with continuous intervals
- Shadbala: PyJHora + 9 classical corrections (`shadbala_pyjhora.py`)
- Divisional Charts: 15 charts D1 through D60 (`divisional_pyjhora.py`)
- Neecha Bhanga: Complete Phaladeepika 7.26–30 implementation with evidence tiers
- Chara Karakas: 7 Karakas (KN Rao standard) + 8 Karakas reference
- Error Policy: **Fail-Fast** on missing dependencies or ephemeris errors

## Downstream Ecosystem Integration

```
Path 1 (Calculation First - Recommended):
  User birth info -> vedic-calculator -> structured_data.md -> vedic-reader (past event validation) -> vedic-core

Path 2 (PDF Import + Calculation):
  User chart PDF -> reader extracts birth details -> calculator generates canonical structured_data.md
  -> PDF cross-check -> reader -> core

Path 3 (Fallback):
  Incomplete birth details -> reader extraction mode with degradation notes -> core
```
