# Tajika Sixteen Yogas Overlay

## System Positioning

This layer is an optional, disabled-by-default Tajika sub-layer strictly isolated from the Parashari standard layer. It classifies contacts, collection of light, transmission of light, intervention, reception, and dignity modifiers according to the sixteen classical Yogas of *Tajika Nilakanthi*. It does not alter the internal three outcome tiers (Favorable / Balanced / Unfavorable) of the standard layer, nor does it combine voting scores with KP.

It runs only when the user explicitly requests Tajika, Itthasala, applying/separating aspects, or the 16 Yogas. Standard layer Phase 2 must be completed first to establish:

- Querent planet: Lagna lord;
- Matter planet: Lord of the single primary matter house.

Do not permanently inject natural Karakas; the Moon enters strictly according to classical rules such as Kamboola or Khallasara.

In the following circumstances, this sub-layer does not execute and does not generate `tajika_overlay.md`. State clearly in plain language why the Tajika overlay is inapplicable, relying on the standard layer as the authoritative answer, without substituting Karakas or other house lords:

- Lookup/table questions (descriptive questions, weather, fetal gender, whereabouts of relatives) and non-judgment queries: there is no matter planet;
- Descriptive questions (`matter: description`): the query asks about the situation rather than binary success/failure, so Tajika contacts have no applicable outcome;
- Querent planet and matter planet are identical: matter house is the 1st house (proactive reconciliation, job preservation/layoff defense, recovery from illness, exam success), or the matter house shares the same rashi lord as Lagna. The script rejects identical planet inputs; classical handling of identical lords remains unverified, triggering fail-closed behavior.

---

## Classical Boundaries and Sources

Primary sources:

1. *Tajika Nilakanthi*, Samjnatantra, Sodasayogadhyaya 2.3–59:
   <https://archive.org/details/tajika_nilakanthi>
2. Martin Gansten and Ola Wikander, "Sahl and the Tājika Yogas: Indian Transformations of Arabic Astrology" (2011):
   <https://doi.org/10.1080/00033790.2010.533349>
3. Balabhadra, *Hāyanaratna*, chapter 3, Martin Gansten Sanskrit-English critical edition (2020):
   <https://archive.org/details/oapen-20.500.12657-42540>

The third source provides cross-checks of the original textual tradition and worked examples cited by Nilakantha; it strictly serves the Tajika sandbox without entering the KN Rao-compatible standard layer.

Execution order is fixed as follows:

| # | Yoga | Standard Criteria |
|---:|---|---|
| 1 | Ikkavala | All 7 planets are outside cadent houses (3, 6, 9, 12) |
| 2 | Induvara | All 7 planets are inside cadent houses |
| 3 | Itthasala / Muthashila | Applying or exact aspect within deeptamsha orb |
| 4 | Isharafa / Musharipha | Past the exact aspect and separating |
| 5 | Nakta | No direct contact; faster 3rd planet separates from one and applies to the other |
| 6 | Yamaya | No direct contact; slower 3rd planet simultaneously receives application from both |
| 7 | Manau | Mars/Saturn intervenes before primary Itthasala or forms classical enclosure |
| 8 | Kamboola | Primary lords have Itthasala, Moon further applies to one or both |
| 9 | Gairikamboola | Moon in Shunyamarga, but after ingress forms future contact to a strong planet |
| 10 | Khallasara | Moon in Shunyamarga with neither Itthasala nor conjunction to primary lords |
| 11 | Radda | Receiving planet retrogrades, combusts, debilitates, or rejects the contact |
| 12 | Duphalikuttha | Primary Itthasala where faster planet is weak and slower planet is strong |
| 13 | Dutthotthadivira | Weak primary lord receives assistance from a strong 3rd planet |
| 14 | Tambira | No current contact, but faster planet forms future contact after ingress |
| 15 | Kuttha | Planets in Itthasala possess classical strength conditions |
| 16 | Durapha | Planets in Itthasala possess classical debility conditions |

These classifications represent internal Tajika semantics and must not be imported into the Parashari standard layer.

---

## Computational Contract

Execution:

```bash
python scripts/build_tajika_overlay.py \
  --datetime "<original chart 'Script Time' metadata; YYYY-MM-DD HH:MM:SS[.ffffff]>" \
  --lat <lat> --lon <lon> --tz "<IANA>" \
  --querent-lord <planet> \
  --matter-lord <planet> \
  --out-dir "<existing prashna_* directory>"
```

Adds `tajika_overlay.md` exclusively to the active Prashna directory. The standard `build_prashna_data.py` does not import this module and has no `--enable-tajika` flag. The overlay must reuse the exact second-level timestamp and actual coordinates from the standard chart.

Geometry and parameters:

- 7 classical grahas participate; Rahu/Ketu do not participate;
- Aspects: 0°, 60°, 90°, 120°, 180°;
- 60°, 90°, 120° aspects evaluate bilateral branches;
- Deeptamsha orbs: Sun 15°, Moon 12°, Mars 8°, Mercury 7°, Jupiter 9°, Venus 7°, Saturn 9°;
- The applying faster planet transmits light; the contact boundary uses the **faster planet's own deeptamsha orb**; never average the two planetary orbs. Ingress candidates also evaluate the moving planet's own deeptamsha;
- Retrogradation is handled via signed relative velocity, then resolved by specific Yogas like Radda/Durapha;
- 60°/120° are harmonious/friendly aspects; 0°/90°/180° are challenging/inimical aspects;
- Itthasala indicates contact is actively forming; challenging aspects must never be translated as "smooth, unhindered success";
- Kamboola dignity uses the 16 cross-tiers of Uttama / Madhyama / Sama / Adhama;
- Dignity inputs are restricted to D1 sign dignity, TNK Hadda, Drekkana, Navamsha, and relevant houses;
- Khallasara strictly requires complete Shunyamarga conditions, not merely lack of Moon contacts.

---

## Consumption Rules

| Configuration | Permitted Phrasing | Prohibited Phrasing |
|---|---|---|
| Friendly Itthasala | Favorable, smooth approaching/connecting trend between parties | Unilaterally altering standard layer to Favorable based on this alone |
| Inimical Itthasala | Contact is forming, but accompanied by tension, conflict, or friction | Translating "contact exists" into "smooth success" |
| Isharafa | Contact has already passed its peak and is separating | Automatically equating to permanent failure |
| Nakta / Yamaya | Possibility of mediation via an intermediary or third-party collection of light | Doubling scores when direct primary contact already exists |
| Manau | Mars/Saturn pre-emptive blockage candidate | Asserting guaranteed blockage without verifying precedence order |
| Kamboola | Graded reinforcement of primary contact by the Moon | Claiming "strongest" without displaying the 16-tier dignity rank |
| Gairikamboola / Tambira | Future contact candidate following sign ingress | Treating as an already realized contact |
| Khallasara | Internal Tajika deficiency correction for Kamboola | Equating to Parashari void-of-course or global veto |
| Radda | Receiving planet rejects/reverses contact; preserves order of success-then-spoil | Flattening all weakness into an identical statement of failure |
| Duphalikuttha / Dutthotthadivira | Strength asymmetry in primary contact or 3rd-planet rescue | Overriding more specific Radda results |
| Kuttha / Durapha | Operational capacity or debility of Itthasala participants | Treating as global chart fortune independent of contact |

If the primary lords have no contact, write strictly:

> This Tajika overlay detected no direct primary lord contact within deeptamsha orb; proceeding to check classical conditions such as Nakta, Yamaya, and Tambira. This sub-layer does not alter the standard layer conclusion.

`tajika_overlay.md` is the human-readable judgment sheet for this sub-layer, presenting:

1. Original timestamp and location;
2. A plain-language summary understandable without jargon;
3. Meaning of direct contacts, mediation, or resistance;
4. Whether timing is available and why;
5. Complete 16 Yogas table with inspectable breakdown.

Never output raw boolean dumps, never present Sanskrit Yoga names without plain English explanations, and never generate standard-layer 3-tier verdicts (Favorable / Balanced / Unfavorable). The plain-language section must avoid raw deeptamsha degrees, untranslated codes, or bare aspects without real-world meaning; these belong strictly to the collapsible technical audit section.

---

## Timing Protocol

Only when primary lords form direct Itthasala is the classical proportional candidate `degree difference × 12 days` permitted. This formula is documented in the Hindi commentary to *Tajika Nilakanthi* 2.5–6; *Hāyanaratna* 3.3 cites *Tajikayogasudhanidhi* 6.35, providing the canonical worked example of Sun in Leo 2° / Mars in Scorpio 16°, `14° × 12 = 168 days`. One must explicitly state:

- This is a classical symbolic candidate, not an astronomical guarantee;
- It belongs strictly to the Tajika sub-layer;
- It does not enter the Parashari standard layer;
- When no direct primary Itthasala exists, timing is marked `unavailable`;
- Derived from a different system than the standard timing layer (`timing-layer.md`), they do not calibrate each other; the primary answer relies on standard judgment sheet §IV.

---

## Verification Gates

Although the implementation covers all 16 Yogas, it remains marked `experimental_pending_published_example_suite` until publication regressions are satisfied:

- 0°/60°/90°/120°/180° bilateral branches;
- applying, exact, post-exact, and Isharafa;
- direct/retrograde signed velocities;
- Ikkavala/Induvara boundary conditions;
- Nakta/Yamaya/Manau precedence order;
- Kamboola 16 tiers, Shunyamarga, Gairikamboola, Khallasara;
- Radda and Durapha precedence order;
- Duphalikuttha / Dutthotthadivira / Tambira / Kuttha;
- Identical lords, Moon as primary lord, sign/Hadda/Drekkana/Navamsha boundaries;
- Fixed published chart regressions;
- `degree diff × 12 days` positive and negative examples.

Regression chart Journal of Astrology article 153 (1994-06-11 18:45 IST) reproduces Scorpio 20°08′ Lagna, Mars Aries 20°02′, and Saturn Aquarius 18°30′, verifying the Mars-Saturn Tajik sextile. *Hāyanaratna* 3.3 Sun-Mars `14° × 12 = 168 days` verifies the faster planet's deeptamsha orb and timing formula.
