# House Diagnostic Framework

> Purpose: Core reference for Step 3 (House Diagnostics) in `vedic-core`.
> Systematic audit for each house: Executive Lord Audit + Occupant Graha Audit + Aspect (Graha Drishti) Audit + Hardware Capacity (SAV) + Divisional Cross-Check.

---

## Divisional Stability Prerequisite

Before relying on D9, D10, D4, or D5 house placements, internal divisional lords, or dispositors, verify the `divisional_boundary_audit` in `structured_data.md`:
- Planetary sign placements (Vargottama, sign dignity, Karakamsha sign) remain valid and are not degraded by Ascendant boundary shifts.
- Placements derived from the divisional Ascendant (divisional house placements, internal divisional house lords, dispositor houses) are flagged if the divisional boundary is sensitive.

## Divisional Chart Separation Rule (Mandatory across all Varga charts: D9/D10/D4/D5/D7/D12...)

All divisional statements must strictly separate two distinct analytical tracks; never conflate them:

- **Track A — Internal Divisional Lords**: Derived from the **divisional chart's own Ascendant**. Data is read directly from the `Internal Divisional Lords & Dignity (Track A)` section in `structured_data.md`.
  Format: `D10-L10=Saturn, Saturn in D10-House N`. Note: `D10-L10` is governed by the D10 Ascendant, **never** by natal D1 L10.
- **Track B — Cross-Chart Projection**: Natal planets retaining their **D1 house rulership role** projected into divisional houses.
  Format: `Natal L2/L11 Jupiter occupies D10 House 9` — always explicitly label `L*` as D1 perspective.

**The Four Strict Prohibitions**:
1. Stating "X is the lord of House Y" without specifying chart context.
2. Writing `L* occupies D*-H*` without explicitly stating that `L*` represents natal D1 identity.
3. Jumping directly from D1 house rulerships to divisional conclusions.
4. Conflating D1 dignity with internal divisional dignity.

**Arbitration**: Discrepancies between Track A and Track B are presented side by side, never artificially averaged.

---

## The Four Diagnostic Dimensions

### 1. The Manager (House Lord)
- P1 Functional Role (P1 functional status).
- Destination (Resident house placement).
- Dignity (Compound dignity).
- Execution Potency (Shadbala percentage).
- Conjunctions and aspects to the lord (synthesized per `synthesis.md`).

### 2. The Occupants (Resident Grahas)
- Natural benefic vs. malefic attributes.
- Multiple occupants indicate high activity, complex focus, or energetic tension.

### 3. Aspects (Graha Drishti focused on the House)
- Benefic aspects provide structural protection, baseline recovery, and external support.
- Malefic aspects introduce friction, structural discipline, pressure, or urgency.
- **Synthesis Rule**: Benefics set the outcome floor; malefics dictate the friction texture during manifestation. Never average them out.

### 4. Hardware Capacity (SAV) — Auxiliary Dimension
⚠️ **SAV Reading Rule**: Always read SAV points from the mapped **House Mapping** table in `structured_data.md`. Never read from unmapped raw sign tables. Format: `House N (Sign) SAV=X`.
- SAV > 32: Surplus capacity (rich foundational resources).
- SAV 26-32: Balanced capacity (steady operations).
- SAV 20-25: Strained capacity (demands conscious exertion).
- SAV < 20: Deficient capacity (structural vulnerability).
- *Dusthana Rule (Houses 6, 8, 12)*: Low SAV can act as a natural firewall against catastrophic escalation (a thief entering an empty house). High SAV in a dusthana provides abundant fuel for disruptive events.

---

## House Archetype Ratings

- **Founder Mode**: Strong lord + benefic occupants + benefic aspects -> High personal agency and autonomous sovereignty.
- **Founder with Friction**: Strong lord + malefic aspects -> High autonomy, achieved through intense operational friction.
- **Manager Mode**: Moderate lord + balanced aspects -> Steady, structured execution.
- **Figurehead Mode**: Weak lord + benefic rescue -> external patronage while lacking internal structural stamina.
- **Drift Mode**: Weak lord + no benefic aspects + malefic pressure -> Instability, absence of grounding.

---

## 12-House Quick Reference

| House | Core Domain | Divisional | Key Event Correlates | Classical Provenance |
|-------|-------------|------------|----------------------|----------------------|
| 1 | Self / Physical Vitality / Identity | — | Physical health, personal vitality | BPHS 11.3, Phaladeepika 1.10 (deha) |
| 2 | Wealth / Speech / Family Assets | D4 | Cash flow, accumulated capital | Phaladeepika 1.10, Prasna Marga XIV.4 |
| 3 | Initiative / Siblings / Courage | — | New technical skills, short travel | BPHS 11.4, Phaladeepika 1.11 |
| 4 | Home / Real Estate / Emotional Base | D4 | Property acquisition, relocation | BPHS 11.5, Phaladeepika 1.11 (sukha) |
| 5 | Intellect / Romance / Progeny | D5 | Creative projects, romance, children | BPHS 11.6, Phaladeepika 1.12 |
| 6 | Competition / Acute Health / Service | — | Litigation, work stress, acute illness | Phaladeepika 1.13 (roga, shatru) |
| 7 | Partnership / Marriage / Trade | D9 | Marriage, commercial contracts | BPHS 11.8, Phaladeepika 1.13 (kama) |
| 8 | Vulnerability / Crisis / Unearned Gains| — | Surgeries, inheritance, sudden trials | BPHS 11.9, Phaladeepika 1.14 |
| 9 | Dharma / Wisdom / Long Journeys | — | Higher learning, foreign journeys, mentors | BPHS 11.10, Phaladeepika 1.14 |
| 10 | Career / Status / Public Standing | D10 | Promotions, executive leadership | BPHS 11.11, Phaladeepika 1.15 |
| 11 | Realized Gains / Social Networks | — | Major income expansion, allies | BPHS 11.12, Prasna Marga XIV.13 |
| 12 | Expenditure / Distant Lands / Solitude| — | Foreign residence, hospitalization | BPHS 11.13, Phaladeepika 1.16 |

---

## Vimshottari Dasha Rules & Positive/Negative Standards

### Positive Criteria (Requires >= 2 to be positive)
1. P1 Functional Benefic (Yogakaraka, Core-Driver, Faithful).
2. Dignity >= Friend (Own sign, Moolatrikona, Exalted, Great Friend).
3. Shadbala >= 120%.
4. Placed in auspicious houses (1st, 4th, 5th, 7th, 9th, 10th).
5. Vargottama or directional strength (Dig Bala).

### Negative Criteria (Any single condition flags structural risk)
1. P1 Functional Malefic (6th, 8th, or 12th lord).
2. Afflicted dignity (combust, debilitated without cancellation).
3. Placed in dusthanas (6th, 8th, 12th) without VRY redemption.
4. Shadbala < 100%.
5. Tight conjunction with natural malefics (< 5°).

### Order of Adjudication (Sequential First-Hit Protocol)
1. **Crisis Window**: Positive = 0 AND Negative >= 2 -> Strict caution, acute structural friction.
2. **Challenging Window**: Positive < 2 AND Negative >= 1 -> Significant trials in governed domains.
3. **Mixed Window**: Positive >= 2 AND Negative >= 1 -> Growth coupled with substantial friction.
4. **Favorable Window**: Positive >= 2 AND Negative = 0 -> Smooth elevation and manifest progress.
5. **Neutral / Baseline Window**: Positive < 2 AND Negative = 0 -> Steady baseline operations.

---

## Time Window Discipline

1. **Resolution Standard**: Major life events require at least Mahadasha x Antardasha (MD x AD) resolution. Broad Mahadasha periods represent background trends, not pinpoint event moments. Narrower monthly windows require native Pratyantardasha (PD) validation.
2. **Dual-System Verification**: Cross-verify Dasha windows with Chara Dasha when present in `structured_data.md`.
3. **Double-Sided Reviews**: Historical Dasha retrospectives must objectively articulate both constructive and challenging manifestations.

---

## Badhaka (Obstacle) Audit

- Movable Signs (Aries, Cancer, Libra, Capricorn) -> Badhaka House is the 11th.
- Fixed Signs (Taurus, Leo, Scorpio, Aquarius) -> Badhaka House is the 9th.
- Dual Signs (Gemini, Virgo, Sagittarius, Pisces) -> Badhaka House is the 7th.
The Badhakesh (lord of the Badhaka house) highlights structural bottlenecks and unseen complications in its resident house.

## Maraka (Mortality / Transition) Audit
The 2nd and 7th house lords function as Marakas, evaluated primarily for physical vitality and health crises.

## Sade Sati (Saturn 7.5-Year Cycle)
Evaluated strictly through the three phases of transit Saturn relative to the natal Moon sign:
- Phase 1 (12th from Moon): Anxiety, anticipation, domestic pressures.
- Phase 2 (Moon sign transit): Peak emotional discipline, intense psychological restructuring.
- Phase 3 (2nd from Moon): Resolution, financial adjustment, integration.
Modified by Moon's natal Shadbala and Saturn's functional benefic status.
