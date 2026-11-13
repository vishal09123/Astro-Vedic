#!/usr/bin/env python3
"""Export a compact, copyable personal chart card.

This adapter reads an already-generated ``structured_data.md`` and only
selects fields that are useful to text skills. It never calls an
ephemeris library and never calculates a chart. The canonical structured
data file remains unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


PLANETS = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
)


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def cells(line: str) -> list[str]:
    return [clean(cell) for cell in line.strip().strip("|").split("|")]


def table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        row = cells(line)
        if not row or all(re.fullmatch(r"[-:\s]+", cell) for cell in row):
            continue
        rows.append(row)
    return rows


def section(text: str, pattern: str) -> str:
    match = re.search(
        rf"(?ms)^\s*{pattern}\s*$\n(.*?)(?=^\s*#{{2,}}\s|\Z)",
        text,
    )
    return match.group(1) if match else ""


def metadata(text: str) -> dict[str, str]:
    body = section(text, r"##\s*Metadata")
    fence = re.search(r"(?ms)```(?:text|yaml|markdown)?\s*\n?(.*?)```", body)
    source = fence.group(1) if fence else body
    result: dict[str, str] = {}
    for line in source.splitlines():
        match = re.match(r"^\s*([^:：]+?)\s*[:：]\s*(.+?)\s*$", line.strip("`"))
        if match:
            result[clean(match.group(1))] = clean(match.group(2))
    return result


def meta_value(meta: dict[str, str], *names: str) -> str:
    folded = {key.casefold(): value for key, value in meta.items()}
    for name in names:
        if name.casefold() in folded:
            return folded[name.casefold()]
    compact = {re.sub(r"[\s_-]", "", key.casefold()): value for key, value in meta.items()}
    for name in names:
        key = re.sub(r"[\s_-]", "", name.casefold())
        if key in compact:
            return compact[key]
    return ""


def canonical_planet(value: str) -> str | None:
    value = clean(value).casefold()
    aliases = {
        "asc": "Lagna",
        "ascendant": "Lagna",
        "lagna": "Lagna",
        "sun": "Sun",
        "moon": "Moon",
        "mars": "Mars",
        "mercury": "Mercury",
        "jupiter": "Jupiter",
        "venus": "Venus",
        "saturn": "Saturn",
        "rahu": "Rahu",
        "ketu": "Ketu",
    }
    if value in aliases:
        return aliases[value]
    for name in ("Lagna",) + PLANETS:
        if value == name.casefold() or value.startswith(name.casefold() + " "):
            return name
    if "north node" in value:
        return "Rahu"
    if "south node" in value:
        return "Ketu"
    return None


def parse_planets(text: str) -> dict[str, list[str]]:
    body = section(text, r"###\s*(?:Planetary Positions|Planets)")
    result: dict[str, list[str]] = {}
    for row in table_rows(body):
        if not row:
            continue
        name = canonical_planet(row[0])
        if name:
            result[name] = row[1:5]
    return result


def parse_moon_nakshatra(text: str) -> tuple[str, str]:
    body = section(text, r"###\s*Nakshatra")
    for row in table_rows(body):
        if row and canonical_planet(row[0]) == "Moon":
            return (row[1] if len(row) > 1 else "", row[2] if len(row) > 2 else "")
    match = re.search(
        r"(?im)^\s*Moon\s+Nakshatra(?:/Pada)?\s*[:：]\s*([^;/；]+?)\s*(?:[/；,]\s*(?:Pada\s*[:：]?\s*)?(\d+))?\s*$",
        text,
    )
    return (match.group(1).strip(), (match.group(2) or "").strip()) if match else ("", "")


def parse_ul(text: str) -> tuple[str, str]:
    body = section(text, r"###\s*Special Points")
    for row in table_rows(body):
        if row and row[0].casefold().startswith("ul"):
            return (row[1] if len(row) > 1 else "", row[2] if len(row) > 2 else "")
    match = re.search(
        r"(?im)^\s*UL(?:\s*\([^\n)]*\))?\s*[:：]\s*([A-Za-z]+)(?:\s*[；;,]\s*(\d+)\s*(?:House|H)?)?",
        text,
    )
    return (match.group(1), match.group(2) or "") if match else ("", "")


def parse_dk(text: str) -> str:
    match = re.search(r"(?im)^\s*DK\s*=\s*([^\n]+)", text)
    if match:
        return clean(match.group(1))
    body = section(text, r"###\s*Chara Karakas")
    for row in table_rows(body):
        if len(row) > 2 and row[1].casefold() == "dk":
            return row[2]
    return ""


def parse_current_dasha(text: str) -> tuple[str, str, str]:
    status = re.search(r"(?ms)^Current Status\s*[:：]\s*\n?```(.*?)```", text)
    if status:
        body = status.group(1)
        md_match = re.search(
            r"(?im)^\s*Mahadasha\s*:\s*([^\n]+?)\s*$", body
        )
        ad_match = re.search(
            r"(?im)^\s*Antardasha\s*:\s*([^\n]+?)\s*$", body
        )
        pd_match = re.search(
            r"(?im)^\s*Pratyantardasha\s*:\s*([^\n]+?)\s*$", body
        )
        md = clean(md_match.group(1)) if md_match else ""
        ad = clean(ad_match.group(1)) if ad_match else ""
        pd = clean(pd_match.group(1)) if pd_match else ""
        if md or ad or pd:
            return md, ad, pd

    md_body = section(text, r"###\s*Vimsottari Dasha")
    md = ""
    for row in table_rows(md_body):
        if len(row) >= 4 and "current" in " ".join(row[:2]).casefold():
            md = f"{row[1]} ({row[2]} to {row[3]})"
            break
    ad = ""
    for line in text.splitlines():
        if not line.startswith("|") or "current" not in line.casefold():
            continue
        row = cells(line)
        if len(row) >= 4 and ("←" in line or "current" in row[0].casefold()):
            ad = f"{row[1]} ({row[2]} to {row[3]})"
            break
    return md, ad, ""


def parse_current_transit(text: str) -> tuple[str, list[tuple[str, str, str]]]:
    match = re.search(
        r"(?ms)^\s*##\s*Current Transit Positions.*?\s*$\n(.*?)(?=^\s*##\s|\Z)",
        text,
    )
    body = match.group(1) if match else ""
    date_match = re.search(
        r"(?im)^\s*>?\s*Extraction Timestamp\s*[:：]\s*(\d{4}-\d{2}-\d{2})",
        body,
    )
    date = date_match.group(1) if date_match else ""
    slow = re.search(
        r"(?ms)^\s*###\s*Slow Planet Transits\s*$\n(.*?)(?=^\s*###\s|\Z)", body
    )
    if not slow:
        return date, []
    rows: list[tuple[str, str, str]] = []
    for row in table_rows(slow.group(1)):
        if len(row) >= 3 and row[0] in {"Saturn", "Jupiter", "Rahu", "Ketu"}:
            rows.append((row[0], row[1], row[2]))
    return date, rows


def infer_house_system(planets: dict[str, list[str]]) -> str:
    signs = {
        "aries": 0, "taurus": 1, "gemini": 2, "cancer": 3,
        "leo": 4, "virgo": 5, "libra": 6, "scorpio": 7,
        "sagittarius": 8, "capricorn": 9, "aquarius": 10, "pisces": 11,
    }
    lagna = planets.get("Lagna", [""])[0].casefold()
    if lagna not in signs:
        return "Unconfirmed (Not specified in source data)"
    comparable = matches = 0
    for name in PLANETS:
        row = planets.get(name, [])
        if len(row) < 2 or row[0].casefold() not in signs:
            continue
        house_match = re.search(r"\d+", row[1])
        if not house_match:
            continue
        comparable += 1
        expected = (signs[row[0].casefold()] - signs[lagna]) % 12 + 1
        matches += expected == int(house_match.group(0))
    if comparable >= 5 and matches / comparable >= 0.8:
        return "Whole Sign (Verified via D1 Sign-to-House mapping)"
    return "Unconfirmed (Not specified in source data)"


def display_row(name: str, row: list[str] | None) -> str:
    row = row or []
    values = [(row[index] if len(row) > index else "—") or "—" for index in range(4)]
    if values[3].casefold() in {"r", "retrograde"}:
        values[3] = "Retrograde"
    return f"{name}: " + "; ".join(values[:3]) + (f"; {values[3]}" if values[3] != "—" else "")


def display_lagna(row: list[str] | None) -> str:
    row = row or []
    sign = (row[0] if len(row) > 0 else "") or "—"
    house = (row[1] if len(row) > 1 else "") or "—"
    degree = (row[2] if len(row) > 2 else "") or "—"
    house = house if house.upper().startswith("H") else f"H{house}"
    return f"Lagna: {sign}; {house}; {degree} (Ascendant)"


def build_card(text: str, label: str, include_birth: bool = False) -> str:
    meta = metadata(text)
    planets = parse_planets(text)
    moon_name, moon_pada = parse_moon_nakshatra(text)
    ul_sign, ul_house = parse_ul(text)
    md, ad, pd = parse_current_dasha(text)
    transit_date, transits = parse_current_transit(text)
    ayanamsa = meta_value(meta, "Ayanamsa", "ayanamsa_method") or "Not provided"
    precision = meta_value(meta, "Effective Precision", "Time Precision") or "Not provided"
    source = meta_value(meta, "Reading Method", "Data Source") or "Calculated Chart Data"
    lines = [
        "Personal Chart Card Version: person-card-v1",
        f"Subject Label: {label}",
        f"Zodiac Baseline: Sidereal; Ayanamsa: {ayanamsa}",
        f"House System: {infer_house_system(planets)}",
        f"Data Precision: {precision}",
        f"Data Source: {source}",
    ]
    if include_birth:
        date = meta_value(meta, "Birth Date", "birth date")
        time = meta_value(meta, "Birth Time", "birth time")
        place = meta_value(meta, "Birth Place", "Location", "birth place")
        if date or time or place:
            lines.append("Birth Details: " + "; ".join(value for value in (date, time, place) if value))
    lines.append("")
    lines.append(display_lagna(planets.get("Lagna")))
    for name in PLANETS:
        lines.append(display_row(name, planets.get(name)))
    lines.append(f"Moon Nakshatra/Pada: {moon_name or 'Not provided'} / {moon_pada or 'Not provided'}")
    ul = ul_sign or "Not provided"
    if ul_house:
        ul += f"; H{ul_house}"
    lines.append(f"UL: {ul}")
    lines.append(f"DK: {parse_dk(text) or 'Not provided'}")
    lines.append(
        f"Current MD/AD/PD: {md or 'Not provided'} / {ad or 'Not provided'} / {pd or 'Not provided'}"
    )
    if transits:
        lines.append(f"Current Transits (Extraction Date: {transit_date or 'Not provided'}):")
        lines.extend(f"{planet}: {sign}; {house}" for planet, sign, house in transits)
        if transit_date:
            lines.append(
                f"Time Rule: The above transits reflect a static snapshot on {transit_date}; only when the session date is "
                f"{transit_date} may they be taken as real-time transits. For other dates, re-run Calc."
            )
    lines.append("Note: This card is compiled from calculated chart data and does not independently cast or refresh ephemeris data.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize structured_data.md into a compact personal chart card. Read-only.")
    parser.add_argument("structured_data", type=Path)
    parser.add_argument("--label", default="Subject", help="Subject label, default: Subject")
    parser.add_argument("--include-birth", action="store_true", help="Include birth date, time, and location")
    parser.add_argument("-o", "--output", type=Path, help="Output file path; prints to stdout if omitted")
    args = parser.parse_args(argv)
    try:
        text = args.structured_data.read_text(encoding="utf-8-sig")
    except OSError as exc:
        print(f"Error: Unable to read {args.structured_data}: {exc}", file=sys.stderr)
        return 2
    card = build_card(text, args.label, include_birth=args.include_birth)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(card, encoding="utf-8")
    else:
        sys.stdout.write(card)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
