"""
Vedic Report Builder — Universal MD -> HTML Pipeline (v2)
=========================================================
Auto-detects open-source (vedic-core) vs Pro output files.
Dynamically numbers sections based on present content.

Usage:
  python report_builder.py <folder> [--name "Name"] [--lagna "Cancer"] [--lang en|cn]

Auto-detected file patterns:
  Identity:     p0_identity.md / p1_overview.md
  Planets:      p2a_planets.md ~ p2d_planets.md
  Divisional:   p3a_d9.md, p3b_divisional.md, p3c_yogas.md
  Houses:       p4a_houses.md, p4b_houses.md
  Prediction:   p5_prediction.md, p5c_topics.md
  Life:         p5a_life.md / p6a_life.md, p5b_life.md / p6b_life.md
  Blueprint:    p6c_blueprint.md
  Appendix:     appendix.md, rectification_report.md
  Career:       career_phase12.md / career_part1~3.md
  Love:         love_step1~3.md / love_part1~2.md
  Q&A:          qa_*.md

Requirements: pip install markdown
"""

import os
import sys
import re
import glob
import argparse

try:
    import markdown
except ImportError:
    print("Installing markdown...")
    os.system(f"{sys.executable} -m pip install markdown -q")
    import markdown

# -- CSS --
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@300;400;500;600&display=swap');

:root {
  --parchment: #f8f4ec; --parchment-deep: #f0eadb;
  --brown: #5a4636; --brown-light: #7a6652; --brown-muted: #9c8b7a;
  --gold: #b59540; --gold-soft: #d4c07a; --gold-line: #c9a94e;
  --text: #3d352c; --text-light: #5a4e42; --text-muted: #8a7d70;
  --border: #ddd3c2; --border-light: #e8e0d2;
  --table-head-bg: #ede6d8; --table-stripe: #f4efe5;
}
@page { size: A4; margin: 22mm 20mm 24mm 20mm; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 14px; line-height: 1.85; color: var(--text);
  background: var(--parchment);
  max-width: 780px; margin: 0 auto; padding: 48px 56px;
  box-shadow: 0 1px 30px rgba(74,55,40,0.1);
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
@media print {
  body { background: var(--parchment); box-shadow: none; padding: 0; max-width: none; font-size: 10.5pt; }
  .no-print { display: none; }
  .section-header, thead th { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  table { font-size: 8pt !important; }
}

.cover {
  page-break-after: always; min-height: 100vh;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  position: relative; padding: 80px 20px 60px; text-align: center;
}
.cover-top {
  color: var(--gold); font-family: 'Inter', sans-serif;
  font-size: 10px; font-weight: 600;
  letter-spacing: 4px; text-transform: uppercase; margin-bottom: 40px;
}
.cover h1 {
  font-family: "Crimson Pro", Georgia, serif;
  font-size: 52px; font-weight: 700;
  color: var(--brown); line-height: 1.3; margin-bottom: 6px;
  border-bottom: none; padding-bottom: 0;
}
.cover .cover-accent {
  font-family: "Crimson Pro", Georgia, serif;
  font-size: 28px; font-weight: 400; color: var(--gold);
  letter-spacing: 6px; margin-bottom: 12px;
}
.cover .cover-ornament {
  width: 60px; height: 1px; background: var(--gold-line); margin: 28px auto;
}
.cover .subtitle {
  font-size: 14px; color: var(--text-muted); font-weight: 400;
  letter-spacing: 1px; margin-bottom: 0;
}
.cover-meta {
  margin-top: auto; padding-top: 0; width: 100%; text-align: left;
  border-top: 1px solid var(--border-light); padding-top: 24px;
}
.cover-meta-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 6px 40px;
  font-size: 12px; color: var(--text-muted);
}
.cover-meta-grid div { display: flex; gap: 8px; align-items: baseline; padding: 4px 0; }
.cover-meta-grid dt { font-weight: 500; color: var(--brown-muted); font-size: 11px; min-width: 55px; flex-shrink: 0; }
.cover-meta-grid dd { margin: 0; color: var(--text-light); }

.toc { page-break-after: always; padding: 40px 0; }
.toc h2 {
  font-family: "Crimson Pro", Georgia, serif; font-size: 22px; color: var(--brown);
  margin-bottom: 24px; padding-bottom: 10px; border-bottom: 1px solid var(--border);
  font-weight: 600;
}
.toc-list { list-style: none; }
.toc-list li {
  padding: 8px 0; border-bottom: 1px dashed var(--border-light);
  display: flex; justify-content: space-between; align-items: center;
  font-size: 14px;
}
.toc-section { font-weight: 500; color: var(--brown); }
.toc-list li.toc-part {
  background: var(--parchment-deep); color: var(--brown); padding: 10px 16px;
  margin: 4px -16px; border-radius: 3px; border: none; border-bottom: none;
  font-weight: 600; font-size: 14px;
}

.section { page-break-before: always; }
.section:first-of-type { page-break-before: auto; }
.section-header {
  border-left: 3px solid var(--gold-line);
  color: var(--brown); padding: 12px 22px; margin: 0 0 28px;
}
.section-header .section-number {
  color: var(--gold); font-family: 'Inter', sans-serif;
  font-size: 10px; font-weight: 600; letter-spacing: 3px; text-transform: uppercase;
}
.section-header h2 {
  font-family: "Crimson Pro", Georgia, serif; font-size: 21px; font-weight: 700;
  margin-top: 2px; border: none; color: var(--brown) !important; padding-bottom: 0;
}

h1 {
  font-family: "Crimson Pro", Georgia, serif; font-size: 22px; color: var(--brown);
  margin: 32px 0 14px; font-weight: 600;
}
h2 {
  font-family: "Crimson Pro", Georgia, serif; font-size: 18px; color: var(--brown);
  margin: 28px 0 12px; font-weight: 600;
}
h3 {
  font-size: 15px; font-weight: 600; color: var(--brown);
  margin: 22px 0 8px; padding-left: 10px;
  border-left: 2px solid var(--gold-line);
}
h4 { font-size: 14px; font-weight: 600; color: var(--brown-light); margin: 16px 0 6px; }
p { margin: 0 0 12px; text-align: justify; }

table {
  width: 100%; border-collapse: collapse; margin: 10px 0 20px;
  font-size: 12px; line-height: 1.5;
}
thead th {
  background: var(--table-head-bg); color: var(--brown);
  padding: 7px 10px; text-align: left;
  font-weight: 600; font-size: 11px;
  border-bottom: 1.5px solid var(--gold-line);
}
tbody td { padding: 6px 10px; border-bottom: 1px solid var(--border-light); vertical-align: top; }
tbody tr:nth-child(even) { background: var(--table-stripe); }

table:has(th:nth-child(10)) { font-size: 10px; }
table:has(th:nth-child(10)) th,
table:has(th:nth-child(10)) td { padding: 4px 3px; text-align: center; white-space: nowrap; }
table:has(th:nth-child(10)) th:first-child,
table:has(th:nth-child(10)) td:first-child { text-align: left; font-weight: 600; }

blockquote {
  border-left: 2px solid var(--gold-line);
  background: var(--parchment-deep);
  padding: 10px 16px; margin: 14px 0; border-radius: 0 3px 3px 0;
  color: var(--text-light); font-size: 13px;
}
blockquote strong { color: var(--brown); font-style: normal; }

ul, ol { margin: 6px 0 14px 22px; }
li { margin-bottom: 3px; }

strong { color: var(--brown); }
code {
  background: var(--parchment-deep); padding: 1px 4px; border-radius: 2px;
  font-size: 12px; color: var(--brown-light);
  font-family: 'Inter', monospace;
}
pre {
  background: #3d352c; color: #ede6d8; padding: 14px 18px; border-radius: 4px;
  margin: 14px 0; font-size: 11px; line-height: 1.6; overflow-x: auto; white-space: pre-wrap;
}
pre code { background: transparent; border: none; color: inherit; padding: 0; }
hr { border: none; border-top: 1px dashed var(--border-light); margin: 24px 0; }

.page-break { page-break-before: always; }
.footer-note {
  margin-top: 30px; padding-top: 14px; border-top: 1px solid var(--border-light);
  font-size: 10px; color: var(--text-muted); text-align: center;
}
"""

# -- Section Registry --
# Format: (priority, key, group, sub, en_title, patterns)
SECTION_REGISTRY = [
    # -- Identity / Overview --
    (5,  "identity",    "G0", "",     "Identity Overview",
     ["p0_identity.md", "p1_overview.md"]),

    # -- Planets --
    (15, "planets_a",   "G1", "A",   "Planets (Sun/Moon)",
     ["p2a_planets.md"]),
    (17, "planets_b",   "G1", "B",   "Planets (Mars/Mercury)",
     ["p2b_planets.md"]),
    (19, "planets_c",   "G1", "C",   "Planets (Jupiter/Venus)",
     ["p2c_planets.md"]),
    (21, "planets_d",   "G1", "D",   "Planets (Sa/Ra/Ke + Summary)",
     ["p2d_planets.md"]),
    (23, "planets",     "G1", "",    "Planetary Audit (P1-P12)",
     ["02_planets.md", "p2_planets.md", "planets.md"]),

    # -- Divisional / D9 / Yogas --
    (28, "d9",          "G2", "A",   "D9 Navamsha Analysis",
     ["p3a_d9.md"]),
    (30, "divisional",  "G2", "B",   "Divisional Cross-Analysis",
     ["p3b_divisional.md", "p3_divisional.md", "03_d9.md"]),
    (32, "yogas",       "G2", "C",   "Yoga Audit",
     ["p3c_yogas.md"]),

    # -- Houses --
    (38, "houses_a",    "G3", "A",   "House Diagnostics (1-6)",
     ["p4a_houses.md"]),
    (40, "houses_b",    "G3", "B",   "House Diagnostics (7-12)",
     ["p4b_houses.md"]),
    (42, "houses",      "G3", "",    "House Diagnostics",
     ["04_houses.md", "p4_houses.md", "houses.md"]),

    # -- Prediction (Pro only) --
    (45, "prediction",  "G4", "",    "Dynamic Prediction",
     ["p5_prediction.md"]),
    (47, "topics",      "G4", "B",   "Cross-Topic Audit",
     ["p5c_topics.md"]),

    # -- Life Architecture / Ten Themes --
    (50, "life",        "G5", "",    "Life Architecture",
     ["p5a_life.md", "p6a_life.md", "05_life.md", "p5_life.md", "life.md"]),
    (55, "life2",       "G5", "cont","Life Architecture",
     ["p5b_life.md", "p6b_life.md", "05b_life.md", "life2.md"]),
    (57, "blueprint",   "G5", "",    "Life Blueprint",
     ["p6c_blueprint.md"]),

    # -- Appendix --
    (58, "appendix",    "appendix", "",  "Technical Appendix",
     ["appendix.md"]),
    (59, "rectify",     "appendix", "",  "Birth Time Rectification",
     ["rectification_report.md", "rectification_scan.md"]),

    # -- Career --
    (60, "career1",     "G6", "",    "Career — Portrait & Narrative",
     ["career_part1.md", "career_phase12.md", "career_phase1_2.md"]),
    (65, "career2",     "G6", "cont","Career — Strategy",
     ["career_part2.md", "career_phase3.md"]),
    (67, "career3a",    "G6", "cont","Career — Precision Synthesis",
     ["career_phase4a.md"]),
    (68, "career3b",    "G6", "cont","Career — Final Strategy",
     ["career_part3.md", "career_phase4b.md", "career_phase4.md"]),
    (69, "career3c",    "G6", "cont","Career — Risk & Advice",
     ["career_phase4c.md"]),
    (70, "career",      "G6", "",    "Career Architecture",
     ["02_career.md", "06_career.md", "career.md"]),

    # -- Love --
    (80, "love1",       "G7", "",    "Love — Pattern & Partner Profile",
     ["love_part1.md", "love_step1.md"]),
    (85, "love2",       "G7", "cont","Love — Timing Windows",
     ["love_step2.md"]),
    (88, "love3",       "G7", "cont","Love — Advice & Risk",
     ["love_part2.md", "love_step3.md"]),
    (90, "love",        "G7", "",    "Love & Marriage",
     ["03_love.md", "07_love.md", "love.md"]),
]

GROUP_TITLES_EN = {
    "G0": "Core Theme",
    "G1": "Planetary Audit",
    "G2": "Divisional Analysis",
    "G3": "House Diagnostics",
    "G4": "Dynamic Prediction",
    "G5": "Life Architecture",
    "G6": "Career Analysis",
    "G7": "Love & Relationship",
    "appendix": "Technical Appendix",
}

EN_ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
            "XI", "XII", "XIII", "XIV", "XV"]

def en_part_label(n):
    """Part I, Part II, ..."""
    return f"Part {EN_ROMAN[n-1]}" if 1 <= n <= len(EN_ROMAN) else f"Part {n}"


def make_section_title(group, sub, base_title, part_num, lang="en"):
    """Generate display title for a section."""
    if group == "appendix":
        return f"Appendix: {base_title}"

    label = en_part_label(part_num)

    if sub == "cont":
        return f"{label} (cont.): {base_title}"
    elif sub:
        return f"{label}{sub}: {base_title}"
    else:
        return f"{label}: {base_title}"


def find_files(folder):
    """Scan folder and map existing files to registry items."""
    found = {}
    actual_files = set(os.listdir(folder))
    actual_lower = {f.lower(): f for f in actual_files}

    for priority, key, group, sub, en_title, patterns in SECTION_REGISTRY:
        for pat in patterns:
            matched_name = actual_lower.get(pat.lower())
            if matched_name:
                fpath = os.path.join(folder, matched_name)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        found[key] = (priority, group, sub, en_title, f.read())
                    break
                except Exception as e:
                    print(f"  Warning: Cannot read {fpath}: {e}")

    # Special handling: merge individual topic files if combined p5c_topics.md is missing
    if "topics" not in found:
        topic_pattern = re.compile(r"^p5c_topic_.*\.md$", re.IGNORECASE)
        topic_files = sorted([f for f in actual_files if topic_pattern.match(f)])
        if topic_files:
            combined = []
            for tf in topic_files:
                fpath = os.path.join(folder, tf)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        combined.append(f.read().strip())
                except Exception as e:
                    print(f"  Warning: Cannot read {fpath}: {e}")
            if combined:
                found["topics"] = (47, "G4", "B", "Cross-Topic Audit", "\n\n---\n\n".join(combined))

    # Special handling: merge Q&A files
    qa_pattern = re.compile(r"^qa_.*\.md$", re.IGNORECASE)
    qa_files = sorted([f for f in actual_files if qa_pattern.match(f)])
    if qa_files:
        combined = []
        for qf in qa_files:
            fpath = os.path.join(folder, qf)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    combined.append(f.read().strip())
            except Exception as e:
                print(f"  Warning: Cannot read {fpath}: {e}")
        if combined:
            found["qa"] = (100, "appendix", "", "Q&A", "\n\n---\n\n".join(combined))

    return found


def detect_package(found, lang="en", brand=None):
    """Detect which skill packages are present."""
    has_core = any(v[1].startswith("G") for v in found.values() if v[1] in ("G0","G1","G2","G3","G4","G5"))
    has_career = any(v[1] == "G6" for v in found.values())
    has_love = any(v[1] == "G7" for v in found.values())
    has_qa = "qa" in found
    has_rectify = "rectify" in found

    if brand == "pro":
        is_pro = True
    elif brand == "open":
        is_pro = False
    else:
        is_pro = "prediction" in found or "blueprint" in found

    version = "Pro" if is_pro else "Open Source"

    parts = []
    part_labels = ("Core", "Career", "Love", "Rectification", "Q&A")
    if has_core:    parts.append(part_labels[0])
    if has_career:  parts.append(part_labels[1])
    if has_love:    parts.append(part_labels[2])
    if has_rectify: parts.append(part_labels[3])
    if has_qa:      parts.append(part_labels[4])

    pkg = " + ".join(parts)
    return pkg, f"{version} | {pkg} Complete Reading", version


# -- HTML builders --

def build_cover(name, lagna, gender, status, pkg, desc, lang="en"):
    top = "DATA-DRIVEN VEDIC ASTROLOGY"
    title = "Vedic Astrology"
    accent = "Complete Reading"
    L = ["Client", "Lagna", "Profile", "Package", "System", "Software", "Dasha", "Metrics"]

    return f"""
<div class="cover">
  <div class="cover-top">{top}</div>
  <h1>{title}</h1>
  <div class="cover-accent">{accent}</div>
  <div class="cover-ornament"></div>
  <div class="subtitle">{desc}</div>
  <div class="cover-meta">
    <div class="cover-meta-grid">
      <div><dt>{L[0]}</dt><dd>{name or '—'}</dd></div>
      <div><dt>{L[4]}</dt><dd>Parashari Jyotish (KN Rao)</dd></div>
      <div><dt>{L[1]}</dt><dd>{lagna or '—'}</dd></div>
      <div><dt>{L[5]}</dt><dd>PyJHora | True Chitrapaksha (Lahiri, diff &lt; 1')</dd></div>
      <div><dt>{L[2]}</dt><dd>{gender or '—'} · {status or '—'}</dd></div>
      <div><dt>{L[6]}</dt><dd>Vimsottari Dasha (3-Tier High Precision)</dd></div>
      <div><dt>{L[3]}</dt><dd>{pkg}</dd></div>
      <div><dt>{L[7]}</dt><dd>SAV 337 / Shadbala / Pushkara / Drishti</dd></div>
    </div>
  </div>
</div>"""


def build_toc(sections, lang="en"):
    toc_title = "Table of Contents"
    items = []
    for title, _ in sections:
        items.append(f'<li><span class="toc-section">{title}</span></li>')
    return f"""
<div class="toc">
  <h2>{toc_title}</h2>
  <ul class="toc-list">{"".join(items)}</ul>
</div>"""


def ensure_table_newlines(text):
    """Ensure newline before markdown tables for parser consistency."""
    lines = text.split("\n")
    out = []
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and i > 0:
            prev = lines[i-1].strip()
            if prev and not prev.startswith("|"):
                out.append("")
        out.append(line)
    return "\n".join(out)


def clean_markdown(text):
    text = re.sub(r"^# .*\n", "", text, count=1)
    text = re.sub(r"^> .*?\n\n", "", text, flags=re.DOTALL)
    text = text.replace("---", '<hr class="page-break">')
    return ensure_table_newlines(text)


def build_section(num_str, title, content, lang="en"):
    cleaned = clean_markdown(content)
    body = markdown.markdown(cleaned, extensions=["tables", "fenced_code"])
    return f"""
<div class="section">
  <div class="section-header">
    <div class="section-number">SECTION {num_str}</div>
    <h2>{title}</h2>
  </div>
  {body}
</div>"""


def main():
    parser = argparse.ArgumentParser(description="Vedic Report Builder — MD -> HTML")
    parser.add_argument("folder", help="Path to client analysis folder")
    parser.add_argument("--name", default="", help="Client name")
    parser.add_argument("--lagna", default="", help="Lagna sign")
    parser.add_argument("--gender", default="", help="Gender")
    parser.add_argument("--status", default="", help="Relationship status")
    parser.add_argument("--lang", default="en", choices=["en", "cn"], help="Language (default: en)")
    parser.add_argument("--brand", default=None, choices=["pro", "open"], help="Override branding")
    parser.add_argument("--include", default=None, help="Filter sections (e.g. 'core', 'career', 'love')")
    parser.add_argument("-o", "--output", default=None, help="Output HTML path")
    args = parser.parse_args()

    folder = os.path.abspath(args.folder)
    if not os.path.isdir(folder):
        print(f"Error: {folder} is not a directory")
        sys.exit(1)

    parts_dir = os.path.join(folder, "parts")
    search_dir = parts_dir if os.path.isdir(parts_dir) else folder
    print(f"  Scanning: {search_dir}\n")

    found = find_files(search_dir)

    if not found:
        print(f"\nError: No MD files found in {search_dir}")
        sys.exit(1)

    if args.include:
        include_set = set(args.include.lower().split(","))
        group_map = {
            "core":    {"G0", "G1", "G2", "G3", "G4", "G5"},
            "career":  {"G6"},
            "love":    {"G7"},
            "rectify": set(),
            "qa":      set(),
        }
        allowed_groups = set()
        allowed_keys = set()
        for g in include_set:
            g = g.strip()
            if g in group_map:
                allowed_groups |= group_map[g]
            if g == "rectify":
                allowed_keys.add("rectify")
            if g == "qa":
                allowed_keys.add("qa")
        if "core" in include_set:
            allowed_groups.add("appendix")
        found = {k: v for k, v in found.items()
                 if v[1] in allowed_groups or k in allowed_keys}
        print(f"  Filter: --include {args.include} -> {len(found)} sections")

    lang = args.lang
    pkg, desc, version = detect_package(found, lang, brand=args.brand)
    print(f"\n  Version: {version}")
    print(f"  Package: {pkg} | Language: {lang}")

    ordered_items = sorted(found.items(), key=lambda x: x[1][0])

    group_to_part = {}
    next_part = 1
    for key, (priority, group, sub, en_title, content) in ordered_items:
        if group == "appendix":
            continue
        if group not in group_to_part:
            group_to_part[group] = next_part
            next_part += 1

    sections = []
    sec_num = 1
    for key, (priority, group, sub, en_title, content) in ordered_items:
        part_num = group_to_part.get(group, 0)
        title = make_section_title(group, sub, en_title, part_num, lang)
        sections.append((title, content))
        sec_num += 1

    cover = build_cover(args.name, args.lagna, args.gender, args.status, pkg, desc, lang)
    toc = build_toc(sections, lang)

    sections_html = []
    for i, (title, content) in enumerate(sections, 1):
        num_str = f"{i:02d}"
        sections_html.append(build_section(num_str, title, content, lang))

    footer = """<div class="footer-note">
  Generated using traditional Vedic astrological methods (Parashari Jyotish | KN Rao School).<br>
  Every claim backed by quantified planetary metrics. For self-reflection and strategic contemplation only.<br>
  &copy; Data-Driven Vedic Astrology</div>"""

    html_lang = "en"
    html_title = f"Vedic Astrology Reading — {args.name}" if args.name else "Vedic Astrology Reading"
    html = f"""<!DOCTYPE html>
<html lang="{html_lang}"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_title}</title>
<style>{CSS}</style></head>
<body>{cover}{toc}{"".join(sections_html)}{footer}</body></html>"""

    out = args.output or os.path.join(folder, "report.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    size = os.path.getsize(out) / 1024
    print(f"\n  [OK] Output: {out} ({size:.0f} KB)")
    print(f"  -> Open in browser -> Ctrl+P -> Save as PDF")
    print(f"\n  Sections: {len(sections)}")
    for title, _ in sections:
        print(f"    * {title}")


if __name__ == "__main__":
    main()
