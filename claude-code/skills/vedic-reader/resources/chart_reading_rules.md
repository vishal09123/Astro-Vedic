### South Indian Chart Reading Rules

**Core Structure**: The South Indian chart features **fixed signs and moving houses**. The 12 signs occupy permanent positions on the chart grid.

```
South Indian Fixed Sign Layout (Never Changes):
+------+------+------+------+
|  Pi  |  Ar  |  Ta  |  Ge  |
|Pisces|Aries |Taurus|Gemini|
+------+------+------+------+
|  Aq  |             |  Cn  |
|Aquar |             |Cancer|
+------+             +------+
|  Cp  |             |  Le  |
|Capri |             | Leo  |
+------+------+------+------+
|  Sg  |  Sc  |  Li  |  Vi  |
|Sagit |Scorp |Libra |Virgo |
+------+------+------+------+
```

**Key**: Locate the **As** or **Asc** mark -> that box's fixed sign is the Ascendant (Lagna).
**Counting Direction**: Beginning from the Lagna sign box, count **clockwise**: House 1 -> House 2 -> ... -> House 12.

```
Example: Lagna in Cancer (2nd box down on right):
House 1=Cn -> House 2=Le -> House 3=Vi -> House 4=Li
-> House 5=Sc -> House 6=Sg -> House 7=Cp -> House 8=Aq
-> House 9=Pi -> House 10=Ar -> House 11=Ta -> House 12=Ge
```

### North Indian Chart Reading Rules

**Core Structure**: The North Indian chart features **fixed houses and moving signs** (opposite of South Indian style).

```
Diamond Layout (Fixed Houses):

       12  |  2
    11     | 1   | 3
           |ASC  |
    10     |     | 4
        9  | 7   | 5
        8  |  6

House 1 = Top center diamond (Ascendant, permanent position).
Numbers inside boxes = Sign numerals (1=Aries, 2=Taurus ... 12=Pisces).
```

**Counting Direction**: **Counter-clockwise!**

**Reading Sequence**:
1. Check the numeral/abbreviation in House 1 -> this identifies the Ascendant sign.
2. Follow houses 1 through 12 in a **counter-clockwise direction**, reading resident planets.
3. Box numerals denote zodiac signs, not house numbers.
4. Output extracted planetary placements for verification.

### Planetary Abbreviation Glossary

| Planet | Common Abbreviations | Sanskrit Names |
|--------|---------------------|----------------|
| Sun    | Su, Sy              | Surya          |
| Moon   | Mo, Ch              | Chandra        |
| Mars   | Ma, Ku              | Kuja, Mangal   |
| Mercury| Me, Bu              | Budha          |
| Jupiter| Ju, Gu              | Guru           |
| Venus  | Ve, Sk              | Shukra         |
| Saturn | Sa, Sh              | Shani          |
| Rahu   | Ra                  | Rahu           |
| Ketu   | Ke                  | Ketu           |
| Lagna  | As, Asc, Lg         | Lagna          |

**Retrograde Indicators (Critical)**:
- Indicated by **(R)**, **Rx**, or underlined glyphs.
- Retrograde status significantly modifies planetary strength and results.
- Must be recorded accurately in `structured_data.md`.

### Special Sensitive Points (AL / UL Required)

| Abbr | Sanskrit Name | Extraction Priority | Downstream Usage |
|------|---------------|---------------------|------------------|
| AL   | Arudha Lagna  | **Mandatory**       | core Section 8 (social standing/image) |
| UL   | Upapada Lagna | **Mandatory**       | love (marriage & partner manifestation) |
| GL   | Ghatika Lagna | Optional / Reference | — |
| HL   | Hora Lagna    | Optional / Reference | — |
| SL   | Sree Lagna    | Optional / Reference | — |
| PP   | Pranapada     | Optional / Reference | — |
| BB   | Bhrigu Bindu  | Optional / Reference | — |
| Md/Gk| Mandi/Gulika  | Optional / Reference | — |
| A2-A12| House Arudhas | Optional / Reference| — |

> **AL/UL Extraction Rules**:
> - If marked on chart image/PDF -> record residing sign.
> - If missing -> compute via BPHS formula from house lords and positions.
> - When computational engine is available -> obtain directly from `special_points['AL']` / `special_points['UL']`.
