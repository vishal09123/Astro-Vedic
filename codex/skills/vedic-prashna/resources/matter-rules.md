# Prashna Matter Registry: Matter Houses and Classical Rules

> **Purpose**: After query decomposition (`question-decomposition.md`), the sub-question "will the event succeed" consults this registry to obtain the matter house and classical rules, populating the `matter` field in the intake plan. This table corresponds one-to-one with `MATTERS` in `scripts/prashna_rules.py`: **modifying one requires updating the other**.
>
> **Authority**: This table registers topic-specific classical rules and execution nuances. The three universal rules (`P-I.3`, `P-I.4`, `P-IV.1`) and connection checks (`M-XIV.43`) are added automatically by the judgment script; they are not duplicated here. Unregistered matters are not forced into the nearest row; set `general`, allowing the LLM to assign the matter house based on `house-meanings.md` with explicit citations (§3).
>
> **Sources**: *Shatpanchasika* (Ayer trans./comm., `P`) chapters and worked examples; *Prasna Marga* (Raman trans./comm., `M`) Chapter XVII. Mappings match Ayer's own citations in his chapter examples.

---

## 1. Default Astrological Roles per Question

1. Lagna and Lagna lord: Querent and current status of the matter;
2. A single matter house and its lord (significator / indicator planet);
3. Specific actors/roles explicitly named in the classical topic rule;
4. The Moon enters computation strictly when explicitly mandated by the topic rule, otherwise remaining background context (`moon-policy.md`).

Do not inject DK, AmK, PK, UL, AL, or other Chara Karakas. Natural Karakas serve as secondary evidence only when explicitly called by classical rules. If a query requires two independent matter houses, decompose into two sub-questions rather than conflating two houses in one ledger.

---

## 2. Matter Registry Table

"Analogical" = original classical verse belongs to another context (negotiating peace between kings, marriage matchmaking) mapped to a modern query, marked Tier B; analogical verses undergo contextual verification (`judgment-rubric.md` §1.3).

| Matter | Typical Query | Matter House | Classical Rules (Primary; Secondary) | Support Tier | Excluded Cognates | Timing Profile |
|---|---|---:|---|---|---|---|
| reconciliation | Can we get back together, reconcile, remarry? | 7 | `P-III.3~4` (analogical) | B | — | general |
| confession | Can we become a couple; will confessing succeed; formal relationship? | 7 | `P-I.4`; `M-XVII.5/15/16/17` (analogical) | B | — | general |
| resume_contact | Can communication resume after no-contact; will friction soften? | 7 | `P-III.3~4` (analogical) | B | — | general |
| meeting | Will we meet/date; will the meeting happen? | Actor's house | `P-I.4`; Romance adds `M-XVII` 4 verses | B | — | general |
| win_back | Will my proactive efforts to win them back succeed? | 1 | `P-I.4` | A | — | general |
| cohabitation_return | Will an estranged partner move back in? | 7 | `P-I.2` Nivritti & 4th house return; `P-V.1~3`, `P-III.5`, `P-II.1~2` | A | — | return |
| marriage | Will marriage take place? | 7 | `P-VII.2`; `P-VII.1`, `M-XVII` 4 verses | A | — | general |
| job_hunting | Can I find a job, secure an offer, pass the interview, get promoted? | 10 | `P-IV.3`, `P-II.1` (sign modality), `P-II.2` (aspects) | A | — | general |
| layoff | Will I be laid off/transferred; can I keep my job? | 1 | `P-I.2` Chyuti; `P-II.1` modality | A | 1st house `P-I.3` (Chyuti already evaluates Lagna occupation/aspect) | general |
| competitive_exam | Ranked selection: civil service, entrance exams | 1 | `P-II.1~2`; `P-III.1` | B | — | general |
| threshold_exam | Pass/fail threshold: driving test, licensing | 1 | `P-I.4` | A | — | general |
| lost_property | Can lost or stolen items be recovered? | 11 | `P-VI.3`; `P-V.1`, `P-II.1~2` modality | A | — | general |
| stray_pet | Can a lost pet be recovered? | 11 | Same as lost property (Ayer example: "My cattle have strayed away") | B | — | general |
| property_purchase | Can I buy a home/property; will housing issue resolve? | 4 | `P-I.2` Vriddhi; `P-II.1~2` modality, `P-I.4` | A | 4th house `P-I.3` (shares occupation/aspect with Vriddhi) | general |
| travel_materialization | Will visa, study abroad, overseas relocation succeed? | 1 | `P-I.4` | A | — | general |
| journey_safety | Will the journey be safe and smooth? | 1 | `P-II.5` | A | 1st house `P-I.3` | disabled |
| departure | Will they depart/move away; can we depart early? | 10 | `P-I.2` Pravasa; `P-II.1~2` modality; early departure adds `P-II.9` | A | 10th house `P-I.3` (Pravasa treats malefic aspect as departure) | general |
| return | Will an absentee or missing person return? | 7 | `P-V.1`; `P-V.2~3`, `P-III.5`, `P-I.2` Nivritti, `P-II.1~2` | A | — | return |
| illness | Will the patient recover from illness? | 1 | `P-IV.5`; `P-II.1~2` modality | A | — | general |
| reputation | Slandered/defamed; can reputation be preserved? | 4 | `P-I.2` Vriddhi; `P-II.1~2`, `P-IV.3` | A | 4th house `P-I.3` | general |
| negotiation | Can negotiation/settlement be reached? | 7 | `P-III.3~4` (direct coverage) | A | — | general |
| investment | Should I invest in this asset; will I lose? | 11 | `P-IV.2` (Ch.4 worked example) | B | — | general |
| recover_losses | Can business losses be made good? | 11 | `P-V.1` (Ch.5 worked example) | B | — | general |
| court_hearing | Will the lawsuit hearing convene soon? | 4 | `P-II.11` (Ch.2 worked example) | B | — | general |
| cooperation | Will the other party cooperate/collaborate? | 7 | `B-article-99` 1/7 mutual axes | B | — | general |
| wealth | Can financial prosperity/money be obtained? | 2 or 11 (per verb) | — | B | — | general |
| child_action | Concrete action regarding a child | 5 | — | B | — | general |
| general | Custom unlisted queries | LLM chooses house per §3 | — | B | — | general |
| description | Descriptive: dynamics, atmosphere, situation | LLM chooses house | — (Outputs facts only: ability, connections, keyword placement; no ledger/tiers) | B | — | disabled |

Intake Plan Parameters:
- Marriage: `asker` (`male` / `female`, `P-VII.1`);
- Layoff: `direction` (`occur` = will layoff happen; `prevent` = can job be saved);
- Departure: `early_departure` (`true` when asking if departure can happen early);
- Meeting: `context` (`romance` adds 4 verses) and `matter_house` (actor's house).

---

## 3. Custom and Unregistered Queries (`general`)

Decompose the question per `question-decomposition.md`. Determine which house the sub-question "will the event succeed" falls into using `house-meanings.md` §2 and §6. In the plan sheet `keywords`, specify `"word -> house -> citation"`, setting `matter: general` and `matter_house: <selected_house>`. This represents a Tier B classical evaluation.

Common targets:
- Inheritance: `general`, matter house 8 (estate of deceased, BPHS 11.9);
- Elections: `competitive_exam` (`P-III.1` Ayer note includes elections);
- Competitive intensity for a job post: `description` (6th house strife/rivals);
- Weather: Consult §5; non-monsoon weather is rejected per §6.

---

## 4. Execution Nuances

### 4.1 Relationship Matters
- `P-III.3~4` classically addresses reconciliation between kings; Ayer notes it applies to all score settlements. Reconciliation and resuming contact are analogical (Tier B); legal negotiations are directly covered (Tier A).
- Human Signs: `P-III.3~4` uses Gemini, Virgo, Libra, Aquarius (III.3 note); `P-IV.2` uses Libra, Gemini, Aquarius per verse text. Each rule uses its distinct list.
- Modality: Fixed/movable signs in `P-I.2` and `P-II.1~2` evaluate gain/loss of position, not reconciliation.
- Marriage: `P-VII.2` (a) Moon in 3, 5, 7, 11, or 6 aspected by benefics, or (b) benefics in kendras/trikonas; notes clarify benefics mean functional benefics. `P-VII.1`: Saturn in odd houses from Lagna (excluding Lagna) indicates a bride; otherwise a groom. Adds *Prasna Marga* XVII 4 verses.
- Confession / Formalizing: No dedicated classical verse; processed via `P-I.4` and *Prasna Marga* XVII marriage verses (Tier B).
- Inquiries such as "will they proactively reach out / confess" evaluate the Action Chain, whereas registry rows evaluate the binary outcome (`question-decomposition.md` §2).

### 4.2 Employment and Examinations
- `P-IV.3`: Benefics in 10, 7 grant position; malefics in 12, 11 are unfavorable. Waning Moon in Lagna is unfavorable; Moon in 10th is favorable regardless of phase.
- `P-II.1~2`: Fixed Lagna grants position; movable indicates failure. Dual signs split: first half acts as fixed, second half as movable (Bhattotpala). Benefic aspects to Lagna and Moon-lagna are favorable.
- Satisfactory Offer: `P-IV.3` second half ("benefics in 2, 5, 1 bring wealth/fame") describes remuneration and satisfaction narratively without scoring points.
- Layoffs / Transfers: Evaluated via `P-I.2` Chyuti. Movable Lagna with lord/benefic aspect and no malefics indicates change takes place; fixed Lagna indicates stability.

### 4.3 Other Topics
- Lost Articles: `P-VI.3` is primary: Full Moon or benefic in Lagna, Shirshodaya Lagna with benefic aspect, or strong benefic in 11th brings quick recovery; Bhattotpala: if none exist, recovery is remote. `P-I.5` describes recovery speed narratively.
- `P-I.2` Four Queries: Vriddhi (4th house prosperity), Pravasa (10th house departure), Nivritti (7th house return), Chyuti (1st house displacement) follow distinct rules and cannot be interchanged.
- Illness: `P-IV.5` Benefics in 1, 7, 8, 5 aspecting each other, and Moon in 3, 6, 10, 11 indicates recovery. Fixed Lagna indicates doubtful cure; movable indicates good recovery (`P-II.1~2`). Queries about relatives also read 1st house. Answers recovery potential only; never provides medical diagnosis.

---

## 5. Table Lookup Queries (No Ledger, No Tiers, No Timing)

Provides direct lookup results in `structured_prashna.md` under "Descriptive and Weather Lookup Facts":

| Query | Rule | Lookup Method |
|---|---|---|
| Taken by family or still in house? | `P-VI.1` | Fixed sign/Navamsha or vargottama Lagna: taken by kin, inside house; otherwise outsider |
| Where in the house is it hidden? | `P-VI.2` | Lagna Drekkana: threshold / middle / backyard |
| Direction and distance of lost item/person | `P-VI.4` | Kendra planets determine direction (otherwise Lagna sign); rising Navamsha index indicates relative distance |
| Category of lost item | `P-I.7`, `P-VII.13` | Rising Navamsha indicates Dhatu / Moola / Jeeva; size |
| Time lost, destination, age of taker | `P-VII.13` | Sign indicates period, direction, cache; Lagna lord indicates age |
| Rainfall during monsoon season | `P-VII.3~4` | VII.3: Venus & Saturn in 7th from Moon, or 2/3/4/8 from Lagna; VII.4: Shukla Paksha benefic in 3/2 or kendras of watery signs, or Moon in watery Lagna |
| Fetal gender (already pregnant) | `P-VII.1` | Saturn in odd houses from Lagna = male; otherwise female (Varahamihira; Lagna excluded); no medical claim |
| Whether kin is abroad | `P-VII.12`; `M-XIV.31` | Karaka (Sun father, Moon mother, Mars sibling, Jupiter child, Venus wife, Saturn servant) with benefic in 8th and aspected by benefic = abroad; otherwise local |

---

## 6. Prohibited Queries (Non-Judged)

State the rejection clearly in one sentence, offering an appropriate alternative framing without moralizing:

- Life, death, longevity, "are they still alive", safety of missing persons (`P-V.4`, `P-VII.11`);
- Mind-reading and privacy: what is someone thinking (`P-I.6`), who is being asked about (`P-VII.6~9`), private lives of others (`P-VII.10`), whether an ex still loves them, whether someone will break up with their current partner, third-party personalities (rephrase to "how will our interactions be" via `description`);
- Manipulation and spying: tracking someone's whereabouts, new partner details; "how can I make them leave their partner". Explain horary does not facilitate control or espionage; offer alternatives like "will my proactive efforts to reconcile succeed";
- Comparing mutually exclusive options A vs B in a single chart (ask user to choose preferred path);
- Interview performance evaluation ("how did I perform / what did they think of me") -> Rephrase to "will I secure this offer";
- Non-monsoon weather: Zodiac signs lack weather rulerships; classical texts provide rain indicators only for monsoon seasons (§5);
- Queries whose elements cannot project onto classical house significations (§3).
