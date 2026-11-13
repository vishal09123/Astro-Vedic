# Prashna Timing Layer (`timing-layer`)

> **Purpose**: Appends an indicatively timed classical window to favorable or pending verdicts after the standard layer judgment is established.
> The timing layer does not enter the rule ledger, does not alter internal 3-tier verdicts, and does not upgrade or downgrade outcomes based on timing distance.
>
> **Prerequisites**: `standard-layer.md`, `judgment-rubric.md`.

---

## 1. Scope & Entrance Gate

- Sourced strictly from classical authorities: *Prasna Marga* XIV.81, 82, 85 (BV Raman translation/commentary, prefix `M`) and *Shatpanchasika* V.5 (NC Iyer translation, prefix `P`).
- Presentation by internal tier:
  - **Favorable**: State timing as: "Approximately...";
  - **Pending**: State conditionally as: "If matters proceed smoothly, approximately...";
  - **Unfavorable**: Do not generate timing; do not run the script. State what structural conditions must change before inquiring anew.

---

## 2. Four Classical Timing Candidates

| Code | rule_id | Algorithm | Role |
|------|---------|-----------|------|
| T1 | `P-V.5` | Count houses from Lagna to the first house with classical grahas; house count * 12 days | Primary timing for return / arrival queries |
| T2 | `M-XIV.85` | Count houses from matter house to its lord's house (inclusive); lord in houses 7-12 gives days, in houses 1-6 gives months | Primary timing for all other queries |
| T3 | `M-XIV.85` | Moon's next ingress into the sign occupied by the matter house lord | Ingress trigger day |
| T4 | `M-XIV.82` | Time unit of rising Navamsa lord * that lord's Navamsa ordinal in sign | Reference only |

**T1 (`P-V.5`)**
- "Count the number of rasis from the lagna to the house first occupied by a planet; multiply the number by twelve... days for the person to arrive."
- Graha in Lagna counts as 1. Counts classical 7 grahas only; Rahu and Ketu are excluded.
- Used strictly for return / arrival queries.

**T2 (`M-XIV.85`)**
- House span = `((lord_house - matter_house) mod 12) + 1`, inclusive.
- Classical text states lord in visible hemisphere operates quickly, in invisible hemisphere operates slowly. Days vs. months division follows Raman's commentary convention.

**T3 (`M-XIV.85`)**
- "When the Moon next transits the sign occupied by the lord of the concerned Bhava."
- If the Moon already occupies that sign at query time, take the next re-entry.
- If the matter lord is the Moon itself, this candidate is omitted as self-referential.

**T4 (`M-XIV.82`)**
- Unit of rising Navamsa lord * lord's Navamsa ordinal within its sign.
- Sourced from Brihat Jataka units cited in Raman's commentary (Sun=6 months, Moon=48 min, Mars=1 week, Mercury=2 months, Jupiter=1 month, Venus=0.5 months, Saturn=1 year).
- Kept strictly as secondary reference.
