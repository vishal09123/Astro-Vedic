"""
vedic-calculator Environment Diagnostic Tool
Usage: python check_env.py (runs under any Python version)

This script:
1. Locates available virtual environment (venv) or suitable Python runtime
2. Validates all required dependencies
3. Executes a baseline minimal calculation (Gandhi chart, verifies SAV=337)
4. Displays clear PASS/FAIL diagnostics and remediation instructions
"""
import os, sys, subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

def find_venv_python():
    """Locate venv Python executable by priority order."""
    candidates = [
        os.path.join(SKILL_DIR, "venv", "Scripts", "python.exe"),  # Windows
        os.path.join(SKILL_DIR, "venv", "bin", "python"),          # Linux/Mac
    ]
    cwd = os.getcwd()
    candidates += [
        os.path.join(cwd, "vedic-calc-env", "Scripts", "python.exe"),
        os.path.join(cwd, "vedic-calc-env", "bin", "python"),
        os.path.join(cwd, "venv", "Scripts", "python.exe"),
        os.path.join(cwd, "venv", "bin", "python"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None

def run_python(python_exe, code):
    """Execute code with the specified Python runtime; returns (success, output)."""
    try:
        r = subprocess.run(
            [python_exe, "-c", code],
            capture_output=True, text=True, timeout=30
        )
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except Exception as e:
        return False, str(e)

def check_dependency(python_exe, name, import_code, version_code=None):
    """Check an individual dependency."""
    ok, out = run_python(python_exe, import_code)
    if not ok:
        return False, f"❌ {name}: Not installed ({out[:80]})"
    if version_code:
        ok2, ver = run_python(python_exe, version_code)
        if ok2:
            return True, f"✅ {name}: {ver}"
    return True, f"✅ {name}: OK"

def main():
    print("=" * 50)
    print("  vedic-calculator Environment Diagnostics")
    print("=" * 50)
    
    # 1. Locations
    print(f"\n📂 Skill Directory: {SKILL_DIR}")
    print(f"📂 Scripts Directory: {SCRIPT_DIR}")
    
    # 2. Find Python
    print(f"\n── Python Runtime Discovery ──")
    venv_python = find_venv_python()
    
    if venv_python:
        python_exe = venv_python
        ok, ver = run_python(python_exe, "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
        print(f"✅ Found venv: {venv_python}")
        print(f"   Python Version: {ver}")
    else:
        print(f"⬜ No local venv found")
        python_exe = sys.executable
        ok, ver = run_python(python_exe, "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
        print(f"   System Python: {python_exe} ({ver})")
        
        ok2, ver_tuple = run_python(python_exe, "import sys; print(sys.version_info[:2])")
        if "(3, 14)" in ver_tuple or "(3, 15)" in ver_tuple:
            print(f"\n{'=' * 50}")
            print(f"  ⚠️  No venv found and system Python {ver} is incompatible.")
            print(f"  pysweph requires Python 3.8 - 3.13; cannot run on {ver}.")
            print(f"\n  Remediation (setup_env.py will find 3.12/3.13 and configure venv):")
            print(f"  {python_exe} {os.path.join(SCRIPT_DIR, 'setup_env.py')}")
            print(f"{'=' * 50}")
            return
    
    # 3. Check dependencies
    print(f"\n── Dependency Verification (Using: {python_exe}) ──")
    
    deps = [
        ("pysweph (swisseph)", 
         "import swisseph as swe",
         "import swisseph as swe; print(swe.version)"),
        ("PyJHora",
         "from jhora.panchanga import drik",
         None),
        ("pytz",
         "import pytz",
         "import pytz; print(pytz.__version__)"),
        ("zoneinfo timezone database (tzdata on Windows)",
         "from zoneinfo import ZoneInfo; ZoneInfo('Asia/Kolkata')",
         None),
    ]
    
    all_ok = True
    for name, imp, ver in deps:
        ok, msg = check_dependency(python_exe, name, imp, ver)
        print(f"  {msg}")
        if not ok:
            all_ok = False
    
    # 4. Check for empty swisseph shell
    if all_ok:
        ok, out = run_python(python_exe, 
            "import swisseph as swe; v=swe.version; print(v); assert v != '0.0.0', 'empty shell'")
        if not ok:
            print(f"  ❌ swisseph is an empty stub (version=0.0.0)! Reinstall pysweph.")
            all_ok = False
    
    # 5. Ephemeris files check
    print(f"\n── Swiss Ephemeris Data Files ──")
    need = ("seas_18.se1", "semo_18.se1", "sepl_18.se1")
    ok, out = run_python(python_exe,
        "import jhora, os; print(os.path.join(os.path.dirname(jhora.__file__), 'data', 'ephe'))")
    jhora_ephe = out.splitlines()[-1].strip() if ok and out else None
    for label, ephe_dir in (("engine", os.path.join(SCRIPT_DIR, "ephe")), ("PyJHora", jhora_ephe)):
        if not ephe_dir:
            print(f"  ⚠️  Unable to locate {label} ephemeris directory")
            continue
        missing = [n for n in need if not os.path.isfile(os.path.join(ephe_dir, n))]
        if not missing:
            print(f"  ✅ {label} ephemeris complete ({len(need)} .se1 files): {ephe_dir}")
        elif all(os.path.isfile(os.path.join(ephe_dir, n + ".txt")) for n in missing):
            print(f"  ⚠️  {label} has .se1.txt files: run setup_env.py to copy to .se1")
        else:
            print(f"  ⚠️  {label} missing {', '.join(missing)}: {ephe_dir}")
    
    # 6. Minimal calculation test
    if all_ok:
        print(f"\n── Baseline Computation Test (Gandhi Chart 1869-10-02) ──")
        test_code = f"""
import sys
sys.path.insert(0, r"{SCRIPT_DIR}")
from engine import calculate_full_chart
chart = calculate_full_chart(1869, 10, 2, 7, 12, 21.6417, 69.6293, "Asia/Kolkata")
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
sav = sum(chart['sav'].get(s,0) for s in SIGNS)
lagna = chart['lagna']['sign']
dk = chart['karakas']['dk_7k']
print(f"SAV={{sav}} Lagna={{lagna}} DK_7K={{dk}}")
assert sav == 337, f"SAV={{sav}} != 337"
print("PASS")
"""
        ok, out = run_python(python_exe, test_code)
        if ok and "PASS" in out:
            for line in out.split("\n"):
                if "SAV=" in line:
                    print(f"  ✅ {line.strip()}")
                    break
            print(f"  ✅ Calculation engine verified!")
        else:
            print(f"  ❌ Calculation test failed:")
            for line in out.split("\n")[-5:]:
                print(f"     {line}")
            all_ok = False
    
    # 7. Summary
    print(f"\n{'=' * 50}")
    if all_ok:
        print(f"  🎉 Environment is fully operational!")
        print(f"  Python executable: {python_exe}")
        print(f"\n  Use in agent workflows:")
        print(f"  {python_exe} <your_script.py>")
    else:
        print(f"  ⚠️  Environment issues detected. Remediation command:")
        print(f"  {python_exe} {os.path.join(SCRIPT_DIR, 'setup_env.py')}")
    print(f"{'=' * 50}")

if __name__ == "__main__":
    main()
