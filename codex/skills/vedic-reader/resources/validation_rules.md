# 16 Mathematical Verification Rules

> Purpose: Executed by reader in Step 2 to guarantee mathematical integrity of extracted data.
> Any failed check -> annotate issue -> request user confirmation only on low-confidence data.

---

## D1 Fundamental Checks

### Check 1: SAV Total = 337
If SAV data is present, the sum across all 12 signs/houses must equal exactly 337.

### Check 2: BAV Row Constants
Row sums for each planet in the Bhinnashtakavarga matrix must match exact constants:
```
Sun=48, Moon=49, Mars=39, Mercury=54,
Jupiter=56, Venus=52, Saturn=39, Lagna=49
```

### Check 3: Planetary Completeness
All 9 grahas + Lagna must be identified (neither more nor less).

### Check 4: Degree Uniqueness
No two distinct bodies can have identical longitudes unless in exact conjunction (which must be explicitly flagged).

### Check 5: Rahu-Ketu Opposition
Rahu and Ketu in D1 must be separated by 180°00' (±1° tolerance in manual charts, exact 180.0° in computational engine).

### Check 6: Retrograde Marking
- Sun and Moon are never retrograde.
- Rahu and Ketu are always retrograde in Mean Node mode.
- All retrograde planets must carry the `(R)` indicator.

### Check 6b: Combustion Detection
Check separation between each planet and the Sun; mark combustion using classical critical thresholds:
```
Moon    < 12°  -> Combust
Mars    < 17°  -> Combust
Mercury < 14°  -> Combust (< 12° when retrograde)
Jupiter < 11°  -> Combust
Venus   < 10°  -> Combust (< 8° when retrograde)
Saturn  < 15°  -> Combust
```
- Distance = shortest arc of longitudinal difference: `min(diff, 360 - diff)`.
- Combust planet -> annotate in `structured_data.md` pre-analysis as `[Combust, Sun separation X°]`.
- **Delayed Compensation Note**: Venus and Saturn recover upon major Dasha transition; annotate `[Delayed Compensation Potential]`.

### Check 6c: Planetary War Detection (Graha Yuddha)
Check whether any two classical planets (excluding Sun, Moon, Rahu, Ketu) have longitudinal separation < 1°:
```
Separation < 1° -> Planetary War
Victor = Planet with lower longitude (compare Shadbala if difference < 0.1°)
Defeated = Loses functional strength / internal conflict
```
- Annotate in pre-analysis: `[Graha Yuddha, with X distance Y°, Victor/Defeated]`.

### Check 7: Ayanamsa Consistency
Matches user-declared system (canonical standard is True Chitrapaksha / Lahiri).

### Check 7b: Lagna Sensitive Degree Inspection
```
Sandhi Check:
  Lagna degree within 0°-1° or 29°-30° -> Annotate [Sandhi - Ambiguous Identity]
  Meaning: Ascendant on sign cusp; foundational identity expression oscillates.

Gandanta Check:
  Lagna near 0° juncture between Water and Fire signs:
    Cancer 29°~30° / Leo 0°~1°
    Scorpio 29°~30° / Sagittarius 0°~1°
    Pisces 29°~30° / Aries 0°~1°
  -> Annotate [Gandanta - Karmic Knot]
  Meaning: Birth on a psychic transition threshold; deep life transformation theme.
```

### Check 7c: Moon Phase Determination (Paksha)
```
Calculation: Moon longitude - Sun longitude (add 360° if negative)
  Difference 0°~180°   = Waxing (Shukla Paksha) -> Moon functions as Natural Benefic
  Difference 180°~360° = Waning (Krishna Paksha) -> Moon functions as Natural Malefic

Subdivisions:
  Difference > 150° = Near Full Moon (Purnima window, Moon at peak strength)
  Difference < 30°  = Near New Moon (Amavasya, dark Moon, lowest strength)
```
- Annotate in pre-analysis: `[Waxing/Waning, Sun separation X°]`.
- Directly affects Moon's natural benefic/malefic status in P1 audit.

### Check 7d: Divisional Input Stability
Recalculate Ascendants of D1, D9, D10, D4, and D5 across the birth time uncertainty window (minute-by-minute); read directly from calculator's `divisional_boundary_audit`:
- Ascendant unchanged throughout window -> `✅ Stable`.
- Ascendant changes sign within window -> `⚠️ Boundary Sensitive`, listing candidate signs and time offset to first transition.
- Unaudited / historical data -> `⚠️ Unaudited`.
- Birth certificates affect source confidence, not mathematical boundary stability.

---

## Nakshatra Checks

### Check 8: Nakshatra-Longitude Consistency
Each Nakshatra spans exactly 13°20' (13.3333°), beginning from Ashwini (0° Aries).
Formula: `Absolute Longitude / 13.3333 = Nakshatra Index (0-26)`.
Pada = `(Degree within Nakshatra / 3.3333) + 1` (integer 1-4).

---

## Chara Karaka Checks

### Check 9: Chara Karaka Degree Ordering
Must be sorted strictly by degree within sign in descending order:
`AK (Highest) > AmK > BK > MK > PK > GK > DK (Lowest)`
Note: Evaluated on degrees within sign (0°-30°), not absolute 360° longitude.
Rahu is calculated inversely (30° - degree) and only included in 8-Karaka reference stacks.

---

## Dasha Hierarchy and Continuity Checks

### Check 10: MD/AD/PD Completeness and Duration Constants
```
Sun=6y, Moon=10y, Mars=7y, Rahu=18y, Jupiter=16y,
Saturn=19y, Mercury=17y, Ketu=7y, Venus=20y
Total = 120 Years
```
The computational path must satisfy:
```
Mahadashas (MD) = 9
Antardashas (AD) = 81
Pratyantardashas (PD) = 729
Every interval seamlessly continuous via [start, end) without gaps or overlaps.
```

---

## Divisional Chart Checks

### Check 11: D9 Formula Cross-Verification
D9 placement must match D1 Pada mapping with 100% mathematical consistency.

### Check 12: Rahu-Ketu Divisional Pairing Reference

```
★ = Mandatory   ○ = Optional

Chart  Rahu-Ketu Rule     Domain                 Verification
─────────────────────────────────────────────────────────────
D1  ★  Opposite Signs     Root Natal Chart       100% verified
D9  ★  Opposite Signs     Navamsa (Marriage)     100% verified
D10 ★  Opposite Signs     Dasamsa (Career)       100% verified
D4  ★  Opposite Signs     Chaturthamsa (Assets)  100% verified
D5  ★  Same Sign (⚠️!)    Panchamsha (Power)     100% verified
D2  ○  Same Sign†         Hora (Wealth)          40/40 verified
D3  ○  Opposite Signs     Drekkana (Siblings)    Verified
D7  ○  Opposite Signs     Saptamsha (Children)   Verified
D12 ○  Opposite Signs     Dwadasamsa (Parents)   Verified
```

**⚠️ Special Note on D5 Same-Sign Rule**:
In D5 (Panchamsha), Rahu and Ketu occupy the **same sign**, not opposite signs.
This is not an error: the 5-fold divisional division mathematically maps 180° opposing points into the identical 60°/12 harmonic sector. Do not "correct" D5 Rahu-Ketu to opposite houses!
