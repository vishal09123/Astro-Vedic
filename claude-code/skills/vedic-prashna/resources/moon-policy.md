# Moon Current Facts: Standard Layer Consumption Boundaries

> **Purpose**: Consumes the Moon position, lunar phase, and current whole-sign contacts output by `calc_moon_vedic.py`.
> Moon data alone does not determine the core directional outcome tier (favorable / unfavorable). Moon ingress trigger dates only belong to the timing sub-layer (`timing-layer.md`).

---

## 1. Classical Source Standing

The Moon has specific contextual uses in different Prashna topic domains, but our classical baseline does not support the following global assertions:

- "The Moon is the highest-weighted significator for all questions";
- "The Moon must connect with the matter house lord, otherwise the matter fails";
- "The Moon nakshatra lord is a fixed 4th significator for every question";
- "No conjunction and no Graha Drishti equates to void-of-course".

`B-article-153` checked whether a missing person chart reflected the query using Lagna, Lagna lord, Moon, and its nakshatra; this is a single case from Bhavan and serves only as a **soft validation candidate**, never to be elevated into a global hard gate.

---

## 2. Data Contract

By default, `structured_prashna.md` contains three sets of Moon data:

### `moon_position`

| Field | Purpose |
|---|---|
| moon_sign / moon_house | Current D1 placement |
| moon_nakshatra / moon_pada | Descriptive; consumed only when topic rules or soft validation explicitly require it |
| moon_nakshatra_lord | Descriptive; not a fixed universal significator |

### `moon_contacts`

| Field | Purpose |
|---|---|
| conjunctions | Planets sharing the same whole sign / rashi with the Moon |
| graha_drishti_planets | Planets casting classical 7-graha whole-sign Graha Drishti onto the Moon |
| graha_drishti_details | Source house and aspect type |

### `moon_strength_factors`

| Field | Purpose |
|---|---|
| paksha | Waxing/waning status and Sun-Moon distance facts |
| tithi | 1 to 30; computed from unrounded Sun and Moon longitudes |
| full_moon_window | Whether within the full moon window of `P-I.5` notes (Shukla 10th to Krishna 5th tithi); reserved solely for `P-I.5` and `P-VI.3` |
| dignity | D1 dignity status |
| house | House occupied by the Moon |

These fields produce directional evidence only when explicit `rule_id` and `scope_match` conditions exist in the applicable rule ledger.

---

## 3. Order of Consumption

1. First obtain the topic's classical method and support tier from `matter-rules.md`;
2. Read the specific `P` topic rules explicitly applicable to the query category;
3. When topic rules explicitly utilize the Moon, apply it strictly per the original rule;
4. Only when query verification of the `B-article-153` type is required may the nakshatra be used for soft validation;
5. In all other circumstances, treat the Moon merely as current psychological/situational background without adding it to the primary rule weighting.

When the Moon acts as a benefic/malefic in rules, follow `standard-layer.md` §2.1: waning Moon is malefic; waxing Moon is situational. The Lagna clause of `P-IV.3` holds only for a waning Moon, while its 10th house clause holds regardless of phase. The full moon window is reserved strictly for `P-I.5` and `P-VI.3`.

Contacts with the Moon are not automatically favorable; one must specify whom it contacts and why that planet is meaningful within the applicable rules for this question. A Moon without contacts is merely a neutral fact, never an automatic negative score.

---

## 4. Chandra Kriya Disambiguation Boundary

In *Prasna Marga* VIII.63–65 and Appendix IV, Chandra Kriya refers to 60 distinct lunar actions computed from the exact arc traversed by the Moon within its nakshatra—it does NOT mean "Moon void of contacts".

The standard layer:
- Does not compute Chandra Kriya;
- Does not borrow Tajika Khallasara or Western Void-of-Course concepts;
- Does not blend this Kerala technique into the standard K/P/B baseline;
- Retains this explanation to prevent spurious "void-of-course" fields from contaminating data.

---

## 5. Timing Boundaries

The standard layer does not calculate arbitrary Moon ingresses. The timing sub-layer calculates the instant the Moon next enters the sign occupied by the matter house lord per `M-XIV.85`, serving as the nearest trigger date (see `timing-layer.md`). Outside of this, one must never:
- Fabricate Vimshottari Dasha/Antardasha transitions for Prashna timing;
- Declare an event date in isolation from the favorable/neutral tier status;
- Enter timing dates into the rule ledger or use them to alter the 3-tier judgment.

---

## 6. Judgment Phrasing Protocol

When topic significance exists:
> `[rule_id]` explicitly evaluates the Moon; the Moon's `<placement / contact / phase>` in this chart constitutes `<favorable / unfavorable / mixed>` evidence for this rule.

When only contextual background exists:
> The Moon currently occupies `<sign / house>`, with / without whole-sign contacts to `<planet>`. No classical source permits promoting this fact into an independent success/failure rule, so it is recorded solely as background context.

---

## 7. Verification Checklist

- [ ] Was the topic support tier and applicable `rule_id` identified first?
- [ ] Does every Moon-based judgment explain why the original rule requires it?
- [ ] Is the nakshatra lord excluded from being universally applied to all questions?
- [ ] Is "no contacts" excluded from being scored as a global negative or invalidating the chart?
- [ ] Does Moon ingress appear strictly in the timing sub-layer, never in the rule ledger?
- [ ] Are Chandra Kriya, Tajika, and Western Void-of-Course concepts completely absent?
