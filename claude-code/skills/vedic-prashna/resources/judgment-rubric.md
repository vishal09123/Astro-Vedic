# Prashna Judgment Rubric: Success Ledger, Ability Layer, Action Chains, and Qualifiers

> **Purpose**: Documents how the judgment script `scripts/judge_prashna_standard.py` (rules implemented in `scripts/prashna_rules.py`) determines the internal outcome tiers `Favorable / Balanced / Unfavorable` and how the LLM consumes its output. This file corresponds one-to-one with `prashna_rules.py`: **modifying rules requires updating both files concurrently** and verifying against baseline test distributions.
>
> **Division of Roles**: The LLM decomposes the query and generates the plan sheet (`question-decomposition.md`); the script tallies points and writes `prashna_verdict.json` and `prashna_verdict.md`; the LLM consumes the resulting verdict faithfully without hand-calculating scores or overriding tiers. The internal tier appears exclusively in the technical audit section; the client-facing section explains how the matter unfolds without exposing technical tier labels (`judgment-writing.md`).

---

## 1. The Success Ledger

The sub-question "will the event succeed" is evaluated exclusively through the Success Ledger.

### 1.1 Itemization of Entries

| Slot | Content | Classical Citation |
|---|---|---|
| Topic-Specific Classical Rule | Primary and secondary rules for the topic from `matter-rules.md` | Respective verses |
| Matter House Support / Affliction | Matter House `P-I.3` (unless excluded as an identical cognate) | Ayer I.3 note: "should be used in judging all problems" |
| Ascendant Disposition | `P-I.4` (omitted if already included in topic-specific rules) | Ayer I.4: Success/failure of desired object |
| Global Chart Architecture | `P-IV.1`: Benefics in kendras/trikonas and malefics absent from kendras and 8th house brings prosperity; contrary configuration brings ruin | Ayer IV.1 ("omnibus solution") |
| Connection | Significant connection between indicator planet (matter lord) and Lagna lord per `house-meanings.md` §8 (+1); lack of connection does not score negatively; inapplicable when matter house is the 1st house | `M-XIV.43`: "Houses aspected by, conjoined with, or in kendra to Lagna or Lagna lord surely bear fruit" |

For relational queries, `M-XVII.16` (Lagna lord and 7th lord mutual exchange, exaltation, or mutual aspect) is cognate with Connection: mutual exchange and aspect are absorbed into the Connection entry; `M-XVII.16` evaluates only exaltation and Venus aspects to avoid duplicate scoring.

### 1.2 Ledger Discipline

- Cites whitelisted facts from `structured_prashna.md` only;
- Only `P` and `M` rules score points; `B` instances serve as compatibility citations; `E` manages workflow without altering scoring; `U`, `T`, and `KP` never enter this ledger;
- A single rule containing mixed benefic and malefic indications scores "mixed" (0 points); rules with internal preponderance mechanisms determine internal net direction per §3;
- **Cognates Score Once**: When two rules evaluate the identical set of occupation/aspect facts (e.g. property purchase Vriddhi vs 4th house `P-I.3`; layoff Chyuti vs 1st house `P-I.3`), retain the topic-specific rule only;
- **Inverse Cognates Exclude the Latter**: In departure queries, Pravasa requires 10th house malefic aspect for journey to materialize; 10th house `P-I.3` would penalize that malefic aspect; therefore, `P-I.3` is excluded from departure queries.

### 1.3 Contextual Verification of Analogical Verses

Analogical verses (flagged "analogical" in `matter-rules.md`, such as `M-XVII` verses applied to confessions/meetings, or `P-III.3~4` applied to reconciliation) originated in royal peace treaties or matrimonial negotiations. If the house evaluated by the rule matches a keyword with an **aligned** polarity in this query, that rule **does not enter the ledger**, and the audit section notes "inapplicable context". Example: In a "private meeting" query, "private" aligns with the 8th house; if `M-XVII.17` triggers due to an afflicted malefic in the 8th house, it is excluded. Direct verses (`M-XVII` in marriage, `P-III.3~4` in formal negotiations) do not undergo this exclusion.

### 1.4 Contextual Planetary Reclassification

Planets registered under `needed_planets` in the plan sheet (planets intrinsically required for success, such as Mars in litigation or surgery) are not penalized as malefics under `P-I.3`. All unmentioned planets follow standard Ayer functional tags.

---

## 2. Scoring and Determination: Preponderance of Factors

### 2.1 Classical Authority

| Citation | Classical Principle |
|---|---|
| Ayer I.4, III.4, IV.5 notes; I.2 note | Mixed configurations within a verse resolve by preponderance ("preponderance of benefic influence will decide the issue", §3) |
| `M-XIV.98` | "If the influences are mixed, then prediction must be made according to the predominating factor." |
| `M-XVII` notes (Raman marital examples) | "the majority of factors are against the marriage being happy"; "The minus points are more in evidence" |
| Ayer I.3 note | House support/affliction "should be used in judging all problems" |
| Ayer III.2 note | When positive and negative forces are evenly balanced, "the result will be undecided" |

### 2.2 Numerical Execution

1. Each ledger entry represents one item of evidence: Favorable = +1, Unfavorable = −1, Mixed or Directionless = 0;
2. Equal weighting: Topic rules and universal rules carry equal weight (+1/−1);
3. Net Sum: Sum > 0 = **Favorable**; Sum < 0 = **Unfavorable**; Sum == 0 = **Balanced** (§4);
4. Strength Designation:
   - Favorable with zero negative entries = **Smooth**; with negative entries = **With Obstacles**;
   - Unfavorable with zero positive entries = **Definitive**; with positive entries = **With Turning Points**;
   - Single active entry in ledger = **Single Evidence**;
   - Overridden by Ability Veto = **Incapacitated**;
5. Obstacles and Turning Points must cite the specific opposing ledger entries;
6. Verses resolving favorably via internal preponderance (§3) are described narratively as "materializing after initial difficulties".

---

## 3. Internal Preponderance Computation (Implementation Protocol)

Classical verses explicitly resolving internal mixtures via preponderance are restricted to three instances:

| Rule | Textual Authority | Scope Houses | Favorable Resolution |
|---|---|---|---|
| `P-I.4` | "succeeds with difficulty … preponderance of benefic influence will decide the issue" | 1st House row; Shadvarga totals scored as an independent sub-entry | Succeeds |
| `P-III.4` | "mixed placements will tend to continue the tension …, a preponderance of benefic influence leading to prospective resolution" | Kendras (1, 4, 7, 10) | Tending toward resolution |
| `P-IV.5` | "a preponderance of favourable influence should be looked for eventual recovery" | 1, 7, 8, 5; Moon in 3, 6, 10, 11 | Eventual recovery |

Computation counts the total number of benefic vs malefic tags across occupations and aspects for the designated houses (F1 lord counts as benefic; Rahu/Ketu and waxing/waning unassigned do not count). More benefics = Favorable (with difficulty); more malefics = Unfavorable; equal = Mixed.

---

## 4. Balanced Verdict (Neutral Tier)

Assigned when:
- **Evenly Balanced**: Sum = 0, with opposing active entries or mixed entries;
- **Chart Gives No Direction**: Sum = 0 because all rule conditions were unmet (no rules triggered); states clearly: "The chart provides no definitive indication under classical rules for this matter", and timing is disabled;
- **Dual Interpretations**: Classical texts present conflicting commentaries (e.g. Gemini as Shirshodaya, Sun in `P-II.9`, 4th house return). Compute net sums under both readings: if tiers match, use that tier; if they diverge, mark "Balanced (Dual Commentary)" and present both trajectories.

---

## 5. The Ability Layer: Veto Power Only

Indicator Planet = Matter House Lord. Evaluated via the "Lord Ability and Connections" table:

- Classical Basis: `M-XIV.39` (significator weak and in 6/8/12 yields failure; "no need to ask if it will be obtained"), `M-XIV.40` (strong in bad house brings event without enjoyment; weak in good house brings partial gains), `M-XIV.30` (multiple afflictions destroy house indications).
- Afflictions: Debilitated; in 6/8/12 (excluding own sign per `M-XIV.42`); combust; retrograde; aspected/occupied by malefics without benefic assistance. Combustion or retrogradation alone counts as an affliction, not standalone incapacity.
- Mitigations: Conjunction or aspect from benefics; exalted, own sign, or natural friend's sign; debilitated planet occupying an auspicious kendra/trikona (1, 4, 5, 7, 9, 10, 11 per `M-XIV.40`).
- Contextual Deductions: `needed_planets` aspecting the indicator do not count as malefic afflictions; occupying a house that aligns with query keywords (e.g. 8th house in a private meeting) does not count as an affliction.
- **Severely Afflicted** (3+ afflictions, or 2 afflictions without mitigation) -> Regardless of ledger sum, the internal tier is forced to **Unfavorable**, with strength labeled **Incapacitated**;
- 1–2 afflictions or mitigated afflictions are labeled "Compromised Capacity" and enter narrative without vetoing the ledger tier;
- Strength or normal status never adds points (+0): operational capacity shows ability to act, not guaranteed event fruition.

---

## 6. The Desire Layer: Planetary Engagement (Zero Scoring)

Governed by `M-XIV.33`, `M-XIV.47`, `M-XIV.48`, `M-XIV.21`, `M-XIV.43`. Evaluates what the matter lord is actively doing via 5 steps: Identity, location of activity, companions (houses ruled, nature), dignity/state, and bridges to querent. Sourced for narrative explanation and qualifier verification; never scores points in the ledger.

---

## 7. Qualifiers

Evaluated by script from plan sheet `qualifiers`:
- Essential Prerequisites: If verified as **Not Established**, client-facing text states: "Under this specific condition, it cannot materialize." The internal tier reflects the ledger, but **timing is completely disabled** (D13: providing a date for an event that cannot happen under the requested condition is contradictory).

---

## 8. Action Chains: Two-Step Response for Action Queries

When asking "will a specific person take action" (reach out, confess, invite), a single net sum cannot simultaneously answer "will they act" and "will the event succeed":

**Step 1: Will they act? -> Action Chain**. Evaluated from actor's perspective via derived houses:
1. Intent: Derived 3rd lord connects with actor's lord, or Mars conjoins/aspects actor's lord (`M-XIV.5`, `M-XIV.31`);
2. Action: Derived 10th lord connects with actor's lord, or is the identical planet (`M-XIV.12`);
3. Direction toward Querent: Actor's lord, intent lord, or action lord connects with Lagna lord, or Mars bridges both (`M-XIV.43`);
4. Capacity: Neither actor's lord nor intent lord is Severely Afflicted in ability table (`M-XIV.39`);
5. Execution: Derived 11th lord strength enters narrative description (`M-XIV.13`).

Outcomes:
- **Favorable (Action Expected)**: (1), (3), and (2) satisfied, (4) uninhibited;
- **Favorable (Arrested in Thought/Speech)**: (1) and (3) satisfied, (2) not satisfied;
- **Willing but Incapacitated**: (1) and (3) satisfied, (4) afflicted;
- **Initiative not Directed at Querent**: (1) satisfied, (3) not satisfied;
- **No Initiative in Chart**: (1) not satisfied.

**Step 2: Will the event succeed? -> Success Ledger** (§1–§4). Evaluates whether the ultimate outcome materializes (reconciliation, harmonious meeting).

---

## 9. Correct Application of `P-I.3`

Evaluates whether the matter house is occupied or aspected by its own lord, benefics, or malefics. Planetary functional roles follow Ayer's criteria. It represents a single piece of evidence (+1 / −1 / 0) within the ledger and never exerts standalone veto power.

---

## 10. Factors Excluded from the Success Ledger

The following are astrological facts, not independent rules, and never alter ledger scores independently:
- Moon without whole-sign conjunctions or Graha Drishti;
- Moon not connecting with the matter lord;
- Retrogression, combustion, or debilitation of uninvolved planets;
- Lack of closed loops with natural Karakas;
- Low Ashtakavarga scores, unactivated divisional charts, or unrelated natal Dashas.

---

## 11. Moon Policies

The Moon serves as rule input only when explicitly mandated by topic classical verses; otherwise it provides background context only (`moon-policy.md`).

---

## 12. Timing Sub-Layer

Invoked only after the 3-tier verdict is determined (`timing-layer.md`):
- Favorable: Timing enabled ("Approximately...");
- Balanced: Timing enabled conditionally ("If progress continues smoothly, approximately...");
- Unfavorable, Incapacitated, Directionless, or Failed Qualifier: Timing is disabled.

---

## 13. Input Sensitivity Audits (Zero Tier Alteration)

The judgment is bound strictly to the given query timestamp. The script re-evaluates the chart at ±60 seconds (or ±30 seconds for exact coordinates). Any alterations in ledger items or ability vetoes are noted strictly in the technical audit section as "Input Sensitivity"; they never alter the primary verdict or enter the client-facing section.

---

## 14. Verification Checklist

- [ ] Does every keyword in the plan sheet cite an authentic classical source with verified polarity?
- [ ] Does the audit section display ledger entries, net sum, internal tier, ability layer, and qualifiers completely?
- [ ] Does the client-facing narrative match the internal tier without exposing technical tier labels?
- [ ] Are action-oriented queries answered in two distinct steps, with action chains kept out of ledger tallies?
- [ ] Is timing withheld for Unfavorable verdicts, Incapacitated statuses, and failed prerequisites?
