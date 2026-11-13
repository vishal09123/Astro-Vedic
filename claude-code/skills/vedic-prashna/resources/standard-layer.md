# Prashna Standard Layer: Classical Sources, Admission Gates, and Data Contracts

> **Purpose**: Governs the default primary layer of Vedic Horary. Any success/failure rule must first secure its source tag, operational scope, and admission status in this document before entering `SKILL.md`, the judgment rubric, or computational scripts.
>
> **Standard Layer Designation**: Classical Prashna anchored in *Shatpanchasika* as the primary text, filtered through the practical compatibility standards of K.N. Rao and Bharatiya Vidya Bhavan (BVB), with conditional inclusion of *Prasna Marga* (synthesis weighting and matrimonial chapters, §1). It must never be abbreviated as "K.N. Rao's proprietary Prashna system," nor should K.N. Rao's natal chart tools be automatically imported into question charts.

---

## 1. Source Tags and Admission Criteria

| Tag | Meaning | Standard Layer Authority |
|---|---|---|
| `K` | Direct teachings or signed case studies by K.N. Rao | Admitted, strictly within original scope |
| `P` | *Shatpanchasika* original text or verifiable translation | Admitted; topic-specific rules apply only to matching queries |
| `B` | Bhavan / *Journal of Astrology* case examples | Admitted as compatibility evidence; not represented as K.N. Rao direct quotes |
| `M` | *Prasna Marga* / Kerala tradition (B.V. Raman trans./comm.) | Conditionally admitted: verified verse-by-verse as `M-Chap.Verse`; consumes §4 whitelisted fields only; excludes longevity, death, chastity, infant mortality, omen omens, Arudha, Gulika, Thrisphuta, Yama Sukra, and remedial rituals. House/planetary meanings (§2) enter narrative, ability layer, and action chains without independent scoring. Timing sub-layer per `timing-layer.md` |
| `T` | Tajika System | Restricted exclusively to the Tajika sandbox |
| `KP` | Krishnamurti Paddhati | Restricted exclusively to the KP independent stack |
| `E` | Engineering / Product Rules | Intake, isolation, and confidence gates; never masquerades as classical doctrine |
| `U` | Unverified or generalized conjectures | Strictly barred from default judgments and timing |

Primary layer rules must satisfy:
1. Grounded in at least one `K`, `P`, `B`, or admitted `M` source;
2. Document original query scope; universalizing specific rules is prohibited;
3. Conflicts with higher-priority sources are preserved explicitly without silent harmonization;
4. Isolated `B` case studies illustrate usage but cannot establish global hard gates;
5. `E` manages workflow and uncertainty; it never invents astrological conclusions;
6. `U` data, even if calculated by the engine, is barred from the standard scoring contract.

---

## 2. Verification Matrix

| Rule | Source | Scope | Admission Status |
|---|---|---|---|
| Cast chart for exact query timestamp and location | `P/K/B` | Universal | Core |
| Lagna / Lagna lord represents querent and current state of the matter | `P-I.2~4/B` | Universal | Core |
| Matter house strengthened by its lord or benefics, weakened by malefics | `P-I.3` | All Houses | Core; benefics/malefics per §2.1 |
| General undertakings evaluated via Lagna, varga, rising mode, and aspects | `P-I.4` | General Undertakings | Conditionally Admitted |
| "Falls in a benefic's varga" evaluates Shadvarga: Lagna, Hora, Drekkana, Navamsha, Dwadashamsha, Trimsamsha (`P-I.4` note); six lords evaluated per §2.1 functional tags; majority benefics = favorable, majority malefics = unfavorable, equal = neutral. Counting method sourced from *Prasna Marga* `M-VIII.29` note and `M-XXIV.45`. Traditional Sun/Moon Hora (`M-XVIII.148` note). Data per §4 item 2 | `P-I.4` note; `M-VIII.29` note, `M-XXIV.45`, `M-XVIII.148` note | General Undertakings | Adopted (Implementation Standard) |
| Mixed configurations indicate success with difficulty: (1)(2) one met one unmet, mixed planets in Shirshodaya Lagna, Pisces rising; decided by preponderance of benefic influence; single weaknesses do not veto | `P-I.4` & notes | General Undertakings | Core; preponderance counted per `judgment-rubric.md` §3 |
| Lagna, Sun, Moon movable/fixed "snapshot" | `K` | K.N. Rao snapshot method | Limited secondary evidence; author notes it is not universally definitive |
| 1st house = one party, 7th house = other party | `B-article-99` | Mutual / Negotiation cases | Admitted for Tier B topics |
| Lagna, Lagna lord, Moon, and nakshatra verify if chart reflects query | `B-article-153` | Missing person case | Soft validation candidate only |
| Moon is highest-weighted significator for all topics | `U` | — | Barred |
| Moon without conjunction / Graha Drishti = "void" or "failure" | Unsupported | — | Barred |
| Moon nakshatra lord is universal significator for all topics | `B` single case | — | Barred from global hard gate |
| Chandra Kriya = 60 lunar actions | `M-VIII.63~65` | Kerala Module | Disambiguation boundary only |
| Moon ingress equals Dasha shift | `U` | — | Barred |
| Next Moon ingress into matter lord's sign = nearest trigger date | `M-XIV.85` | Timing Sub-Layer | Strictly in `timing-layer.md`; not in rule ledger |
| Chara Karakas (DK, UL, AL) used in default Prashna | `U` | — | Barred |
| SAV / BAV used in default Prashna | `U` | — | Barred |
| Divisional charts restricted to Lagna Shadvarga lords and rising Navamsha; full natal D2/D3/D9/D12/D30 life readings barred | `P-I.4`, `P-I.7`, `P-VI.1~2`, `P-VI.4`, `P-VII.13` / `U` | General / Lookup / Others | These two items retained only |
| Natal divisional charts (D10, D4, D5) | `U` | — | Barred |
| 120-year Vimshottari / Chara Dasha calculated from question chart | Conflicted with `K/M` | — | Barred |
| *Prasna Marga* annual / monthly Prasna Dasa | `M-VI.39, 65~67` | Kerala | Omitted: Measures annual flow rather than event dates; requires Thrisphuta/Gulika |
| House count / Navamsha count timing formulas | `M-XIV.81~82, 85`, `P-V.5` | Timing Sub-Layer | Strictly in `timing-layer.md`; does not alter tiers |
| Fixed Lagna grants position (Sthana labha); movable denies; dual mixed (first half fixed, second half movable per Bhattotpala *Prasnagyana*); benefic aspects to Lagna and Moon-lagna favorable, malefic unfavorable, mixed if both | `P-II.1~2` & notes | Gain/loss of position; expanded by Ayer to jobs, residence, journeys, lost items, illness, reputation | Primary for jobs/exams (`matter-rules.md` §4.2); secondary modality for other topics |
| Benefics in 10, 7 grant position; in 2, 5, 1 bring fame/wealth; malefics in 12, 11 unfavorable; waning Moon in Lagna unfavorable, Moon in 10th favorable regardless of phase | `P-IV.3` | Position; Fame & Wealth | Primary for job hunting; Lagna clause requires waning Moon; 10th house clause holds in all phases |
| Benefics in 10, 1, 7 bring victory; Mars/Saturn in 9th defeat; Mercury/Jupiter/Venus in 9th victory | `P-III.1` | Warfare; Ayer notes competitive efforts | Secondary for competitive exams, Tier B |
| Human sign rising with benefics, benefics in 12/11, or kendra/human Lagna aspected by benefics brings reconciliation; malefics in dual signs cause strife; mixed factors bring stalemate, resolved by benefic preponderance | `P-III.3~4` & notes | Peace between kings; negotiations | Primary Tier A for negotiations; analogical Tier B for reconciliation |
| Functional benefic/malefic: F1 own lord always benefic; F2 rules 3 & 12 from house and debilitated = malefic; F3 rules kendra & trikona from house and strong = benefic; fallback = Bhattotpala natural benefic/malefic | `P-I.3` note Rules 1/2 & examples | All `P` rules calling benefics/malefics | Adopted; verses naming specific planets without Ayer notes use named planets |
| D1 dignity, afflictions, combustion | `P-I.3` & notes | Planetary delivery capacity | Secondary; does not determine tier alone |
| Chyuti (Lagna movable, aspected by lord/benefic, no malefics = change occurs; fixed = no change; dual = preponderance); Vriddhi (4th house aspected by lord/benefic unspoiled = prosperity); Pravasa (10th house movable aspected by malefic = departure); Nivritti (7th house movable aspected by lord/benefic = return) | `P-I.2` & notes | Career shifts/layoffs, property, travel, return; slander | Primary rules for respective matters, Tier A |
| Full Moon in Lagna aspected by Jupiter/Venus, or strong benefic in 11th = quick recovery of lost articles | `P-I.5` & notes | Lost property, missing persons | Evaluates speed only; recovery itself judged via `P-VI.3` |
| Rising Navamsha odd/even determines Dhatu / Moola / Jeeva | `P-I.7` & table | Object attributes | Lookup query, no outcome tier |
| Benefics in kendras/trikonas and malefics absent from kendras and 8th house = comprehensive prosperity; reverse = failure | `P-IV.1` & notes | General Outlook | Universal Architecture Rule: Integrated into every success ledger |
| Benefics in 3, 5, 11, 7 grant gain, malefics loss; benefics in human signs auspicious; aspect equals occupation | `P-IV.2` & notes | Investments | Investment queries, Tier B |
| Benefics in 1, 7, 8, 5 aspecting each other and Moon in 3, 6, 10, 11 = recovery; malefics there and Moon elsewhere = opposite; mixed = benefic preponderance | `P-IV.5` & notes | Illness recovery | Primary for illness, Tier A |
| Planets in 5, 2, 3 bring return of absentees; benefics bring lost articles; Jupiter/Venus brings rapid return | `P-V.1` | Return, Lost Property, Business losses | Primary for return (A); secondary for lost items; recovery of losses (B) |
| Planets in 7 or 6, Jupiter in kendra or Mercury/Venus in trikona = return; Moon in 8th with kendras free of malefics = safe return; Moon & benefics must not be weak | `P-V.2~3` & notes | Return from distance | Secondary for return; "weak" = D1 debilitated |
| Jupiter or Venus in 2nd/3rd from Lagna = rapid arrival | `P-III.5` & notes | Return | Secondary for return; named planets |
| Movable Lagna with Sun/Saturn/Mercury/Venus occupied = rapid departure; retrograde denies | `P-II.9` & notes | Early departure | Secondary for early departure; named planets |
| Sun and Moon in 4th denies; Mercury, Jupiter, Venus in 4th convenes rapidly | `P-II.11` & notes | Court hearing | Court hearing queries, Tier B |
| Fixed sign / Navamsha / vargottama Lagna = taken by kin, inside house; Drekkana determines hiding spot | `P-VI.1~2` & notes | Lost property description | Lookup query, no outcome tier |
| Full Moon or benefic in Lagna, Shirshodaya Lagna aspected by benefic, or strong benefic in 11th = quick recovery; none = remote | `P-VI.3` & notes | Recovery of lost property | Primary for lost property; Gemini dual commentary |
| Kendra planets indicate direction; rising Navamsha indicates distance | `P-VI.4` & notes | Direction/distance of lost items | Lookup query |
| Saturn in odd houses from Lagna (excluding Lagna) = male fetus / eligible bride; otherwise female / groom | `P-VII.1` & notes | Fetal gender; marriage | Primary for fetal gender (A); secondary for marriage |
| Moon in 3, 5, 7, 11, 6 aspected by benefics, or benefics in kendras/trikonas = marriage takes place | `P-VII.2` & notes | Marriage materialization | Primary for marriage, Tier A |
| Monsoon rain indicators | `P-VII.3~4` & notes | Monsoon weather | Weather lookup table |
| Sun with benefic in 8th aspected by benefic = father abroad | `P-VII.12` & notes | Kin whereabouts | Primary for father (A); other kin (B) |
| Navamsha determines object, Drekkana thief, sign time/direction, Lagna lord age | `P-VII.13` & notes | Lost property details | Lookup query |
| Mind-reading, privacy, life/death | `P-I.6`, `P-VII.6~11`, `P-V.4` | Unethical queries | Excluded (Category C) |
| Global assumption that retrograde equals failure | `U` | — | Barred; evaluated per explicit topic rules |
| Houses 3, 6, 8, 12 uniformly categorized as identical obstacles | Conflicted with `P` | — | Barred |
| Lagna lord must connect with matter lord | Specific `B/P` topics | — | Barred from universal hard gate; scored +1 when connected per `M-XIV.43` |
| Matter lord must form closed loop with natural Karaka | `U` | — | Barred |
| 3-tier verdict (Favorable / Balanced / Unfavorable) via ledger preponderance | Ayer notes, `M-XIV.98`, `M-XVII` notes + `E` contract | Universal | Tiers appear in technical audit section only; narrative conveys motion |
| 24-hour / 3-month arbitrary re-cast thresholds | `U/E` | — | Removed |
| Chart stability under time/location perturbation | `E` | Universal | Input sensitivity audit: Technical audit only, zero tier alteration |

---

## 2.1 Functional Benefic/Malefic Baseline (Ayer Formulation)

Ayer defines functional roles in `P-I.3` note via Rule 1 (own lord always functional benefic), Rule 2, and worked examples, falling back to Bhattotpala natural benefic/malefic:

| Order | Condition (Counting houses from occupied/aspected sign S) | Label | Source |
|---:|---|---|---|
| F1 | Planet is lord of sign S | Benefic (Lord) | I.3 text + note Rule 1; applies to malefics and dusthana lords |
| F2 | Planet rules both 3rd and 12th from S and is debilitated | Malefic (Ex. 1) | Note Example 1: Jupiter relative to Capricorn |
| F3 | Planet rules both a kendra (4/7/10) and trikona (5/9) from S and is strong | Benefic (Ex. 2) | Note Example 2: Mars relative to Leo, "provided he is strong" |
| Fallback | All other combinations | Natural nature + (Fallback) | Same note: Bhattotpala natural status |

- Reference point is the sign S occupied or aspected; the same planet against different signs holds different labels.
- Fallback: Mercury conjoined Sun/Mars/Saturn is malefic; Moon is malefic when waning, and "Waxing Unassigned" when waxing (Full Moon is benefic for I.5 and VI.3). Rahu/Ketu carry no labels.
- "Strong Benefic" in I.5 and VI.3: D1 `exalted`, `own_sign`, or `moolatrikona`.

---

## 3. Query Support Tiers

### Tier A: Dedicated Topic Rules in `P`
Subject to specific classical verses in `matter-rules.md`. Evaluated alongside universal rules in the ledger with equal weighting.

### Tier B: Universal House/Lord Rules or Bhavan Examples
Evaluated using:
- Lagna and Lagna lord;
- Single primary matter house and its lord;
- `P-I.3` house support/affliction;
- Universal rules `P-I.4` and `P-IV.1`;
- Connection (`M-XIV.43`);
- Ability and Desire layers (`judgment-rubric.md` §5, §6);
- Verified `B` case examples as secondary evidence.

Labeled "General Classical Judgment"; this reflects classical textual coverage, not probabilistic accuracy.

### Tier C: Query Unmapped to Classical House Significations
Halt judgment. Clarify or inform the user that the standard layer cannot process the query.

---

## 4. Standard Layer Data Whitelist

Whitelisted in `structured_prashna.md`:
1. D1 Lagna, longitude, sign modality, boundary distance;
2. Rising Navamsha sign and index; Lagna Shadvarga lords table (`P-I.4` note: Lagna, Sun/Moon Hora, Drekkana, Navamsha, Dwadashamsha, Trimsamsha);
3. D1 7-graha positions; Rahu/Ketu positions as neutral facts;
4. 12 houses, lords, occupant planets;
5. 7-graha whole-sign Graha Drishti with §2.1 functional tags;
6. D1 dignities, specific combustion states, retrogradation facts;
7. Moon phase, tithi, full moon window, position, whole-sign contacts; nakshatra for descriptive context;
8. Mutual aspects and sign exchanges (Parivartana);
9. Lookup facts for descriptive and weather topics (§5.1);
10. Timing sub-layer pointers (timing details recorded in `timing_overlay.md`);
11. Derived factual tables: Lord Ability & Connections, Derived Perspectives & Action Chains, Planetary Bridges.

Strictly barred from default horary outputs:
- Chara Karakas (AK, AmK, BK, MK, PK, GK, DK, UL, AL);
- SAV / BAV, Shadbala, Bhava Bala;
- Full D9, D10, D4, D5 or other divisional charts;
- Natal yoga prescans, engine functional P1 tags;
- 120-year Vimshottari or Chara Dasha;
- Natal transits, Sade Sati, double transit;
- Tajika or KP fields (unless explicitly switched to their isolated sandboxes).

---

## 5. Judgment Contract

Evaluated deterministically via script (`judge_prashna_standard.py`), outputting the Success Ledger:
- `rule_id`: Classical citation;
- `level`: A / B / B (analogical) / B (universal environment);
- `reason`: Application rationale;
- `evidence`: Cites whitelisted facts only;
- `direction`: Favorable / Unfavorable / Mixed / Directionless;
- `score`: +1 / −1 / 0.

---

## 6. Classical Textual Anchors

- [*Shatpanchasika*, V. Subrahmanya Sastri translation](https://archive.org/details/dli.ministry.22678)
- K.N. Rao, ["The Case of Sanjay Dutt and Punishment"](https://www.journalofastrology.com/article.php?article_id=60)
- K.N. Rao, ["Eternal India 17"](https://www.journalofastrology.com/article.php?article_id=150)
- K.N. Rao, ["Precarious Prediction: World Cup Football Final 2014"](https://www.journalofastrology.com/article.php?article_id=476)
- *Journal of Astrology*, ["Nuke Deal: Governments Meeting with the Left"](https://www.journalofastrology.com/article.php?article_id=99)
- G.N. Saxena, ["Case Study of a Prediction – Missing Persons"](https://www.journalofastrology.com/article.php?article_id=153)
- [*Prasna Marga*, B.V. Raman translation](https://archive.org/details/PrasnaMargaBVR)
- *Shatpanchasika*, V.A.K. Ayer translation (*Indian Horary*)
