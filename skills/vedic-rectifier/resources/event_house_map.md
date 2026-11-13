# Event-to-House Mapping Table

> Purpose: Used by `vedic-rectifier` Step 3 for event categorization and house attribution.
> Principle: Every event type carries **one primary house** + relevant Karakas; secondary houses are listed strictly as **supporting houses**.
> House Rulership Provenance: Strictly derived from `vedic-core/resources/house_framework.md` 12-house reference.

---

## Primary and Supporting Houses: Why One Primary House

Attributing an event to multiple houses dilutes analytical differentiation: any Dasha lord matches something, rendering candidate charts indistinguishable. Therefore:

1. **Only the Primary House yields a Strong Match (✅✅)**.
2. **Supporting Houses offer confirmation only**: If the primary house aligns, a matching supporting house reinforces narrative coherence without inflating quantitative scores. If the primary house misses, supporting houses yield at most a Weak Match (⚠️) and cannot overturn candidate rankings.
3. **No Cumulative Scoring across Houses**: A single event matching both primary and supporting houses counts as one match.
4. **Evaluate Distinctive Indicators Only**: If a house yields identical indications across candidate charts, record as `Indifferent / No Distinction`.

---

## Core Event Mapping Registry

| Event Type | Primary House | Supporting Houses | Relevant Karaka | Relevant Graha | Classical Provenance |
|------------|---------------|-------------------|-----------------|----------------|----------------------|
| Marriage / Engagement | **7** | 2 (family expansion) | DK (7K) | Venus | House 7: Spouse / union (BPHS 11.8) |
| Romantic Relationship | **5** | 7 | PK | Venus | House 5: Romance / emotional bonds (Raman); House 7: Kama |
| Separation / Divorce | **6 / 8** | 7th lord afflicted | — | Mars, Saturn | House 8: Mangalya; House 6: 12th from 7th (loss of union) |
| Serious Crisis / Loss of Spouse | **7** | 2 (8th from 7th), 8 | DK | 7th lord, Venus, Jupiter | House 7: Partner; House 8: Crisis / sudden change |
| Promotion / Employment | **10** | 11 (gains) | AmK | Sun | House 10: Status, profession (BPHS 11.11) |
| Resignation / Career Exit | **10** | 12 (renunciation / loss) | — | — | House 12: Loss of position (Prasna Marga XIV.14) |
| Enterprise / Startup | **10** | 7 (trade), 3 (initiative) | AmK | Mars | House 10: Enterprise; House 7: Commerce; House 3: Courage |
| Academic Exam / Graduation | **5** | 4, 2 | — | Mercury, Jupiter | House 5: Intellect; House 4: Foundational education |
| Competitive Examination | **6** | 10, 11 | — | Mars, Saturn | House 6: Competition, rivalry, conquest of obstacles |
| Institutional / Civil Service Role | **6 + 10** | 11 | AmK | Sun, Saturn | House 6: Employment; House 10: Executive status |
| Scholarship / Grant Receipt | **11** | 2, 9 | — | Jupiter | House 11: Gains, cash flow, institutional grants |
| Relocation / Moving House | **4** | 3 (local), 12 (distant) | — | Moon | House 4: Residence, domestic foundation |
| Real Estate Acquisition | **4** | D4 cross-check | — | Mars (property) | House 4: Fixed assets, lands (BPHS 11.5) |
| Severe Illness / Hospitalization | **6** | 8 (chronic illness) | — | 6th lord | House 6: Acute illness; House 8: Chronic affliction |
| Surgical Intervention | **8** | 6 (trauma / wounds) | — | Mars (scalpel / incisions) | House 8: Vulnerability; House 6: Instruments, incisions |
| Accident / Sudden Physical Trauma | **8** | — | — | Mars, 8th lord | House 8: Sudden hazard, physical vulnerability |
| Demise of Father | **9** | 2nd from 9th (Maraka) | — | Sun | House 9: Father, lineage mentor |
| Demise of Mother | **4** | 2nd from 4th (Maraka) | — | Moon | House 4: Mother, emotional maternal origin |
| Birth of Child | **5** | — | PK | Jupiter | House 5: Progeny, creative fruit |
| Major Financial Windfall | **2 / 11** | — | — | Jupiter | House 2: Accumulated wealth; House 11: Realized gains |
| Major Capital Loss | **12** | 8 | — | 12th lord | House 12: Expenditure, depletion of reserves |
| Litigation / Legal Dispute | **6** | — | GK | — | House 6: Adversaries, litigation, formal disputes |
| Relocation Abroad / Emigration | **12 / 9** | 10 (foreign posting), 7 | — | Rahu | House 12: Foreign settlement; House 9: Foreign journey |
| Professional Award / Public Honor | **10 / 11** | — | AmK | Sun, Jupiter | House 10: Public fame, social distinction; House 11: Honor |

---

## Static Biographical Facts Mapping

| Biographical Fact | House | House Lord | Natural Karaka | Karaka / Divisional | Supporting Indications | Decisive Pivot |
|-------------------|-------|------------|----------------|---------------------|------------------------|----------------|
| Loss of Father in Youth | 9 | 9th lord | Sun | — | Severely Afflicted | Yes |
| Loss of Mother in Youth | 4 | 4th lord | Moon | — | Severely Afflicted | Yes |
| Siblings Present / Only Child | 3 (younger), 11 (elder) | 3rd/11th lord | Mars | — | Afflicted = only child | No |
| Marriage / Divorce Status | 7 | 7th lord | Venus | DK, D9 | Afflicted = divorce | No |
| Children Present | 5 | 5th lord | Jupiter | PK | Strong = children | No |
| Leadership Authority | 10 | 10th lord | Sun, Saturn | AmK, D10 | Strong = executive command | No |
| Chronic Illness Diagnosed | 6, 8 | 6th/8th lord, Lagna lord | — | — | Afflicted | No |

- **Afflicted**: Conjoined or aspected (Graha Drishti) by Saturn, Mars, Rahu, or Ketu; combust, debilitated; house lord in 6, 8, or 12.
- **Strong**: Exalted or in own sign, free from malefic affliction.

---

## Match Evaluation Standards

### Strong Match (✅✅)
```
Mahadasha / Antardasha lord = House lord of the Primary House.
Example: Marriage during Venus Dasha where Venus is the 7th lord.
```

### Moderate Match (✅)
```
- Dasha lord occupies the event's Primary House.
- Dasha lord aspects the event's Primary House via classical Graha Drishti.
- Dasha lord = Natural Karaka for the event (e.g., Venus for marriage, Mars for surgery).
```

### Weak Match (⚠️)
```
- Dasha lord connects only to supporting houses.
- Indirect association via mutual aspect with the house lord.
```

### No Match (❌)
```
Dasha lord carries no classical connection to the event house, lord, or Karaka.
```
