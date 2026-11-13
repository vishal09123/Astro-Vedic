# Inter-Chart Planetary Contacts and Aspect Rules (`aspect-policy`)

> Analytical foundation for Layer 2 ("Directional Overlay") in Vedic Synastry.
> Framework: Pure Parashari / KN Rao methodology. Exclusively uses classical Vedic criteria; no Western astrological techniques.
> Data Source: Both natal charts' D1 planetary positions, house lords, compound dignities, and Graha Drishti aspect matrices from `structured_data.md`.

---

## 0. Strict Directionality

All inter-chart contacts must be articulated directionally. Person A -> Person B and Person B -> Person A are **computed and stated separately; never merged**:

```
Person A's [Planet] ([P1 Role / Karaka]) -> Person B's [House N / Point]
  What Person A projects | How Person B experiences it
```

Hierarchy of criteria: **Whole-Sign House Placement > Graha Drishti Aspect > Degree Closeness**.
Degree proximity calibrates intensity but never creates or negates an aspect independently.

---

## 1. Whole-Sign House Overlays (Primary Criterion - Highest Weight)

Person A's planet in Person B's sign = falling into Person B's corresponding house (counted from Person B's Lagna sign):
- **Significance**: Person A introduces that planetary energy directly into Person B's specific life domain, activating that house's affairs.
- **Calculation**: `Person B House = (Person A Sign Index - Person B Lagna Sign Index) mod 12 + 1`.
- **Interpretation**: Combines Person B's house domain + Person A's planetary functional role/Karaka + Person A's natal dignity.
- **Critical House Activations**: Overlays into Person B's 1st, 4th, 5th, 7th, 8th, 11th, or 12th houses represent major structural interactions.

---

## 2. Graha Drishti (Vedic Special Aspects - Secondary Criterion)

Classical whole-sign Graha Drishti; **not** Western degree-orb aspects. Person A's planetary gaze falling on Person B's house/point = Person A focuses energy on Person B's domain:

| Planet | Aspected Houses (Counted from Resident House) |
|--------|-----------------------------------------------|
| All Grahas | 7th House (Opposite sign) |
| Mars       | Additional 4th and 8th Houses |
| Jupiter    | Additional 5th and 9th Houses |
| Saturn     | Additional 3rd and 10th Houses |
| Rahu/Ketu  | 7th House (Conservative standard) |

- **Natural Malefics** (Saturn, Mars, Rahu): Introduce pressure, friction, discipline, or urgency.
- **Natural Benefics** (Jupiter, Venus, Moon): Introduce protection, nourishment, expansion, and relief.
- Functional role in the home chart modifies the expression (e.g., an exalted Saturn provides stabilizing endurance, whereas a debilitated Saturn imposes anxious restriction).
