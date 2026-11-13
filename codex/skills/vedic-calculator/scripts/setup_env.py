#!/usr/bin/env python3
"""
setup_env.py — vedic-calculator Automated Environment Setup Script
Cross-platform (Windows / macOS / Linux); creates venv and installs dependencies in strict order.

Usage:
  python setup_env.py              # Creates venv/ alongside scripts/
  python setup_env.py --target /path/to/dir   # Specify custom venv location

Installation sequence:
  1. pysweph>=2.10.3.5     — Swiss Ephemeris C module (active community fork with cp38~cp313 wheels)
  2. PyJHora dependencies   — numpy, geocoder, geopy, requests, timezonefinder, python-dateutil
  3. PyJHora==4.8.6        — SAV/BAV + Shadbala + Divisional charts
  4. pytz>=2024.1          — Timezones
  5. tzdata                — Timezone database (required on Windows for zoneinfo)
  6. Ephemeris data fix    — Copies bundled .se1 files to PyJHora's package directory
"""

import subprocess
import sys
import os
import platform
import shutil
import argparse


# ── Configuration ────────────────────────────────────
REQUIRED_PACKAGES = [
    # (Package, Version constraint, Extra pip arguments)
    # Installation sequence is critical!
    ("pysweph", ">=2.10.3.5", []),
    ("pytz", ">=2024.1", []),
    ("numpy", "", []),
    ("geocoder", "", []),
    ("geopy", "", []),
    ("requests", "", []),
    ("timezonefinder", "", []),
    ("python-dateutil", "", []),
    ("PyJHora", "==4.8.6", []),
    ("tzdata", "", []),
]

MIN_PYTHON = (3, 8)
MAX_PYTHON = (3, 13)
VENV_DIR_NAME = "venv"


# ── Utility Functions ────────────────────────────────

def log(msg, level="INFO"):
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERR": "❌"}
    print(f"  {icons.get(level, '·')} {msg}")


def find_python():
    """Find a Python interpreter matching versions 3.8 to 3.13."""
    v = sys.version_info
    if MIN_PYTHON <= (v.major, v.minor) <= MAX_PYTHON:
        return sys.executable

    # Windows: py launcher
    if platform.system() == "Windows":
        for minor in range(MAX_PYTHON[1], MIN_PYTHON[1] - 1, -1):
            try:
                result = subprocess.run(
                    ["py", f"-3.{minor}", "--version"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return f"py -3.{minor}"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

    # Unix: python3.xx
    for minor in range(MAX_PYTHON[1], MIN_PYTHON[1] - 1, -1):
        name = f"python3.{minor}"
        if shutil.which(name):
            return name

    # Generic python3
    if shutil.which("python3"):
        try:
            result = subprocess.run(
                ["python3", "-c", "import sys; print(sys.version_info.minor)"],
                capture_output=True, text=True, timeout=5
            )
            minor = int(result.stdout.strip())
            if MIN_PYTHON[1] <= minor <= MAX_PYTHON[1]:
                return "python3"
        except Exception:
            pass

    return None


def get_venv_python(venv_dir):
    """Return Python executable path within venv."""
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        return os.path.join(venv_dir, "bin", "python")


def get_venv_pip(venv_dir):
    """Return pip executable path within venv."""
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        return os.path.join(venv_dir, "bin", "pip")


def run_cmd(cmd, desc=""):
    """Run command and check return code."""
    if isinstance(cmd, str):
        cmd = cmd.split()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        log(f"{desc} failed: {result.stderr[-500:]}", "ERR")
        return False
    return True


def create_venv(python_cmd, venv_dir):
    """Create virtual environment."""
    log(f"Creating venv: {venv_dir}")
    cmd = python_cmd.split() + ["-m", "venv", venv_dir]
    return run_cmd(cmd, "Create venv")


def install_packages(venv_dir):
    """Install dependencies in strict required sequence."""
    pip = get_venv_pip(venv_dir)
    
    # Upgrade pip first
    py = get_venv_python(venv_dir)
    run_cmd([py, "-m", "pip", "install", "--upgrade", "pip"], "Upgrade pip")

    for pkg_name, version_spec, extra_args in REQUIRED_PACKAGES:
        pkg_str = f"{pkg_name}{version_spec}"
        log(f"Installing {pkg_str} {' '.join(extra_args)}")
        cmd = [pip, "install", pkg_str] + extra_args
        if not run_cmd(cmd, f"Install {pkg_name}"):
            return False
    
    # Fix missing ephemeris data in PyJHora
    fix_ephemeris_data(venv_dir)
    return True


def fix_ephemeris_data(venv_dir):
    """Ensure PyJHora has access to .se1 Swiss Ephemeris data files.
    
    Copies from bundled scripts/ephe/ directory (offline priority).
    """
    py = get_venv_python(venv_dir)
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    bundled_ephe = os.path.join(scripts_dir, "ephe")
    
    fix_code = f"""
import os, sys, shutil, glob

try:
    import jhora
    jhora_ephe = os.path.join(os.path.dirname(jhora.__file__), 'data', 'ephe')
except ImportError:
    print('SKIP: jhora not installed')
    sys.exit(0)

if glob.glob(os.path.join(jhora_ephe, '*.se1')):
    print('OK: .se1 files already exist')
    sys.exit(0)

SE1_NAMES = ['seas_18.se1', 'semo_18.se1', 'sepl_18.se1']

# Priority 1: Copy from bundled scripts/ephe/ (offline, most reliable)
bundled = r'{bundled_ephe}'
if os.path.isdir(bundled):
    os.makedirs(jhora_ephe, exist_ok=True)
    copied = []
    for name in SE1_NAMES:
        for src_name in (name, name + '.txt'):
            src = os.path.join(bundled, src_name)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(jhora_ephe, name))
                copied.append(name)
                break
    if copied:
        for f in copied:
            print(f'Copied (bundled): {{f}}')
        sys.exit(0)

# Priority 2: Copy from pysweph package
try:
    import swisseph as swe
    swe_dir = os.path.dirname(swe.__file__)
    for d in [os.path.join(swe_dir, 'data'), os.path.join(swe_dir, 'ephe'), swe_dir]:
        if os.path.isdir(d):
            se1 = glob.glob(os.path.join(d, '*.se1'))
            if se1:
                os.makedirs(jhora_ephe, exist_ok=True)
                for f in se1:
                    shutil.copy2(f, os.path.join(jhora_ephe, os.path.basename(f)))
                    print(f'Copied (pysweph): {{os.path.basename(f)}}')
                sys.exit(0)
except ImportError:
    pass

# Priority 3: Download from Swiss Ephemeris official site
BASE_URL = 'https://www.astro.com/ftp/swisseph/ephe'
try:
    import urllib.request
    os.makedirs(jhora_ephe, exist_ok=True)
    for name in SE1_NAMES:
        dst = os.path.join(jhora_ephe, name)
        if not os.path.exists(dst):
            url = f'{{BASE_URL}}/{{name}}'
            print(f'Downloading: {{name}}...')
            urllib.request.urlretrieve(url, dst)
            print(f'Downloaded: {{name}}')
except Exception as e:
    print(f'WARN: Could not download .se1 files: {{e}}')
    print('SAV may use Moshier fallback (slightly less precise but functional)')
"""
    result = subprocess.run([py, "-c", fix_code], capture_output=True, text=True, timeout=120)
    if result.stdout.strip():
        for line in result.stdout.strip().split('\n'):
            log(line, "OK" if "Copied" in line or "OK" in line or "Downloaded" in line else "INFO")


def validate(venv_dir):
    """Validate installation and calculations."""
    py = get_venv_python(venv_dir)
    
    checks = [
        ("swisseph", "import swisseph as swe; print(swe.version)"),
        ("jhora", "import jhora; print('OK')"),
        ("pytz", "import pytz; print('OK')"),
        ("zoneinfo", "from zoneinfo import ZoneInfo; ZoneInfo('Asia/Kolkata'); print('OK')"),
    ]
    
    all_ok = True
    for name, code in checks:
        result = subprocess.run(
            [py, "-c", code], capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            log(f"{name}: {result.stdout.strip()}", "OK")
        else:
            log(f"{name}: Import failed", "ERR")
            all_ok = False
    
    if not all_ok:
        return False
    
    # SAV=337 Validation
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    test_code = f"""
import sys, io
sys.path.insert(0, r'{scripts_dir}')
_real_stdout = sys.stdout
sys.stdout = io.StringIO()
from ashtakavarga_pyjhora import calculate_ashtakavarga_fixed
sys.stdout = _real_stdout
r = calculate_ashtakavarga_fixed(2002, 12, 11, 20, 47, 25.4333, 119.0, 8.0)
total = sum(r['sarvashtakavarga'].values())
print(f'SAV_RESULT={{total}}')
"""
    result = subprocess.run([py, "-c", test_code], capture_output=True, text=True, timeout=60)
    sav_ok = "SAV_RESULT=337" in result.stdout
    if result.returncode == 0 and sav_ok:
        log("SAV=337 Validation Passed", "OK")
    else:
        log(f"SAV Validation Failed (got: {result.stdout.strip()}, err: {result.stderr[-300:]})", "ERR")
        return False
    
    return True


# ── Main ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="vedic-calculator Environment Setup")
    parser.add_argument("--target", default=None, help="Target venv directory (default: venv alongside scripts)")
    args = parser.parse_args()

    print("\n🔧 vedic-calculator Environment Setup\n")

    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(scripts_dir)
    venv_dir = args.target or os.path.join(skill_dir, VENV_DIR_NAME)

    venv_py = get_venv_python(venv_dir)
    if os.path.exists(venv_py):
        log(f"Found existing venv: {venv_dir}")
        if validate(venv_dir):
            log("Environment is already configured and validated", "OK")
            print(f"\n✅ Python: {venv_py}")
            return 0
        else:
            log("Existing venv validation failed; reinstalling dependencies", "WARN")
            if not install_packages(venv_dir):
                return 1
            if validate(venv_dir):
                log("Reinstallation validated successfully", "OK")
                print(f"\n✅ Python: {venv_py}")
                return 0
            return 1

    python_cmd = find_python()
    if not python_cmd:
        log(f"Python {MIN_PYTHON[1]}~{MAX_PYTHON[1]} not found. Please install Python 3.12 or 3.13.", "ERR")
        log("Download: https://www.python.org/downloads/", "ERR")
        return 1
    log(f"Using Python: {python_cmd}")

    if not create_venv(python_cmd, venv_dir):
        return 1

    if not install_packages(venv_dir):
        return 1

    if not validate(venv_dir):
        return 1

    print(f"\n✅ Environment setup completed successfully!")
    print(f"   Python executable: {venv_py}")
    print(f"   Usage: {venv_py} your_script.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
