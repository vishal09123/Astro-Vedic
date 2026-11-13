#!/usr/bin/env python3
"""judge_prashna_standard.py — Prashna standard layer judgment script.

Reads the intake plan sheet, calculates the success ledger, internal outcome tier,
ability layer veto, action chains, and qualifier results.
Outputs prashna_verdict.json and prashna_verdict.md.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CALC = _HERE.parent.parent / "vedic-calculator" / "scripts"
if str(_CALC) not in sys.path:
    sys.path.insert(0, str(_CALC))

from prashna_rules import DIRECTION_TEXT, Plan, judge  # noqa: E402
from prashna_time import calculate_prashna_chart, format_wall_time, parse_local_datetime, shift_seconds  # noqa: E402

WINDOW = {"city": 60, "exact": 30}


def charts(dt, lat, lon, tz, location):
    with contextlib.redirect_stdout(io.StringIO()):
        base = calculate_prashna_chart(dt, lat, lon, tz)
        w = WINDOW[location]
        variants = [(f"-{w}s", calculate_prashna_chart(shift_seconds(dt, -w), lat, lon, tz)),
                    (f"+{w}s", calculate_prashna_chart(shift_seconds(dt, w), lat, lon, tz))]
    return base, variants


def render(v, plan, dt):
    """Render judgment markdown audit section."""
    L = ["## Judgment (judge_prashna_standard.py)\n", f"Query Instant: {format_wall_time(dt)}; Matter: {v['matter']}, "
         f"Matter House: {v['matter_house']}, Support Tier: {v['level']}.\n"]
    if plan.keywords:
        L.append("**Intake Keywords**: " + "; ".join(
            f"{k['word']} → House(s) {', '.join(map(str, k.get('houses', ()))) or '—'}"
            f"{'; ' + ', '.join(k.get('planets', ())) if k.get('planets') else ''} ({k['polarity']}, {k['source']})"
            for k in plan.keywords) + (f"; Required Significators: {', '.join(plan.needed_planets)}" if plan.needed_planets else "") + "\n")
    if v["matter"] == "description":
        return "\n".join(L + render_describe(v))
    L.append("| rule_id | Level | Reason | Evidence | Direction | Score |")
    L.append("|---|---|---|---|---|---:|")
    for e in v["ledger"]:
        d = DIRECTION_TEXT[e["direction"]] + (f"; Alt: {DIRECTION_TEXT[e['alt']]}" if e["alt"] else "")
        extra = "; ".join(x for x in (e["note"], e["excluded"]) if x)
        L.append(f"| `{e['rule_id']}` | {e['level']} | {e['reason']} | {e['evidence']}{' (' + extra + ')' if extra else ''} | "
                 f"{'Excluded' if e['excluded'] else d} | {e['score']:+d} |")
    L.append(f"\n**Total**: {v['sum']:+d}\n")
    L.append(f"**Internal Tier**: {v['tier']} · {v['strength']}" + (f" (Branches: {' / '.join(v['branches'])})" if v["branches"] else "") + "\n")
    ab = v["ability"]
    L.append(f"**Ability Layer**: Significator {ab['planet']} (House {ab['house']} lord), Afflictions: {', '.join(ab['factors']) or 'None'}, "
             f"Mitigations: {', '.join(ab['rescue']) or 'None'} → {ab['verdict']}"
             + (f"; Contextual deductions: {'; '.join(ab['dropped'])}" if ab["dropped"] else "") + "\n")
    for q in v["qualifiers"]:
        L.append(f"**Qualifier · {q['name']}**: {q['result']} ({q['basis']})\n")
    if v["chain"]:
        c = v["chain"]
        L.append(f"**Action Chain**: Actor House {c['actor']}; (1) Initiative: {'; '.join(c['start']) or '—'}; (2) Action: {c['move'] or '—'}; "
                 f"(3) Directed at Querent: {'; '.join(c['point']) or '—'}; (4) Severely Afflicted: {', '.join(c['weak']) or '—'} → {c['verdict']}"
                 " (does not enter ledger)\n")
    if v["sensitive"]:
        L.append("**Input Sensitivity** (does not alter tier): " + "; ".join(f"At {s['at']}: {', '.join(s['rules'])} change, tier becomes {s['tier']}"
                                                                              for s in v["sensitive"])
                 + ". Recorded for audit only.\n")
    why = f" (Prerequisite(s) {', '.join(v['condition_failed'])} not established)" if v["condition_failed"] else ""
    L.append(f"**Timing Sub-Layer**: {'Disabled' + why if v['timing'] == 'none' else 'Enabled, --mode ' + v['timing']}\n")
    return "\n".join(L)


def render_describe(v):
    """Descriptive query audit section: facts on influences, keyword hits, M-XIV.117."""
    d, ab = v["describe"], v["ability"]
    L = ["**Descriptive Query**: No success ledger, outcome tiers, or timing generated (`judgment-writing.md` §4).\n",
         f"**Significator**: {ab['planet']} (House {ab['house']} lord), Afflictions: {', '.join(ab['factors']) or 'None'}, "
         f"Mitigations: {', '.join(ab['rescue']) or 'None'} → {ab['verdict']}; Link to Lagna lord: {d['link']}\n",
         "| Position | Mode | Planet | Houses Ruled from Lagna | Functional Tag | D1 Dignity | Combustion/Retrograde | Keyword Hits |",
         "|---|---|---|---|---|---|---|---|"]
    for r in d["influences"]:
        cr = ", ".join(x for x, on in (("Combust", r["combust"]), ("Retrograde", r["retro"])) if on) or "—"
        L.append(f"| {r['at']} | {r['how']} | {r['planet']} | {', '.join(map(str, r['rules'])) or '—'} | {r['label']} | "
                 f"{r['dignity']} | {cr} | {'; '.join(r['hits'])} |")
    if not d["influences"]:
        L.append("| — | — | No conjoined or aspecting planets | — | — | — | — | — |")
    for k in d["keywords"]:
        L.append(f"\n**Keyword Hit · {k['word']}**: {k['result']} ({k['basis']})")
    m = d["M-XIV.117"]
    L.append(f"\n**`M-XIV.117`** (Moon or Venus with malefic in 7th/4th house): {m['result']} ({m['basis']})\n")
    if v["chain"]:
        c = v["chain"]
        L.append(f"**Action Chain**: Actor House {c['actor']}; (1) Initiative: {'; '.join(c['start']) or '—'}; (2) Action: {c['move'] or '—'}; "
                 f"(3) Directed at Querent: {'; '.join(c['point']) or '—'}; (4) Severely Afflicted: {', '.join(c['weak']) or '—'} → {c['verdict']}\n")
    L.append("**Timing Sub-Layer**: Disabled (Descriptive Query)\n")
    return L


def main():
    ap = argparse.ArgumentParser(description="Prashna Standard Layer Judgment")
    ap.add_argument("--datetime", required=True)
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--tz", required=True)
    ap.add_argument("--plan", required=True, help="Intake plan prashna_plan.json")
    ap.add_argument("--out-dir", required=True, help="Target prashna_* directory")
    a = ap.parse_args()
    out = Path(a.out_dir)
    if not (out / "structured_prashna.md").exists():
        ap.error(f"{out} does not contain structured_prashna.md; run build_prashna_data.py first")
    plan = Plan.from_dict(json.loads(Path(a.plan).read_text(encoding="utf-8")))
    dt = parse_local_datetime(a.datetime, a.tz)
    base, variants = charts(dt, a.lat, a.lon, a.tz, plan.location)
    v = judge(base, plan, variants=variants)
    (out / "prashna_verdict.json").write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "prashna_verdict.md").write_text(render(v, plan, dt), encoding="utf-8")
    if v["matter"] == "description":
        print(f"[OK] Descriptive Query: No tier assigned, facts output\n     {out / 'prashna_verdict.md'}")
        return
    print(f"[OK] Verdict: {v['tier']} · {v['strength']} (Total {v['sum']:+d})"
          + (f"; Action Chain: {v['chain']['verdict']}" if v["chain"] else "")
          + f"\n     {out / 'prashna_verdict.md'}")


if __name__ == "__main__":
    main()
