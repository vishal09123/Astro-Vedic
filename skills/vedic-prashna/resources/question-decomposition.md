# Prashna Query Decomposition and Symbolic Extraction

> **Purpose**: Phase 2 execution. Decomposes the query into sub-questions, classifies its type, maps each operational step onto houses and planets, extracts keyword qualifiers, and compiles the plan sheet `prashna_plan.json` for the judgment script. **Decomposition is the primary workflow**: the 3-layer architecture, action chains, and general rules possess authentic textual citations (`standard-layer.md` verification matrix) and never yield to fixed table names; the matter registry provides classical topic rules (`matter-rules.md`) strictly for the binary success sub-question.
>
> **Division of Responsibility**: Query decomposition, question typing, keyword extraction, actor/matter house assignment, and determining whether keywords align with or oppose the query are qualitative decisions made by the LLM, with each cited authority documented in the plan sheet. Quantitative calculations (success ledger tallying, ability vetoes, action chains, qualifier verification) are executed deterministically by the script, never computed by hand.
>
> **Classical Sourcing**: Sourced strictly from classical Indian authorities. Western concepts of reception, mutual reception, and Tajika transfer/collection of light (Nakta, Yamaya, Itthasala) do not govern the standard layer; Tajika executes only in `tajika_overlay.md` upon explicit user request.

---

## 1. Query Decomposition Template

| Element | Question to Ask | Example: "Will they proactively ask me out for a private meeting on Nov 15?" |
|---|---|---|
| Actor | Who is expected to take action? | The other party |
| Action | What action: intent, communication, romance, physical movement, fulfilling desire? | Proactively ask out (intent + action) |
| Target | Toward whom? | The querent |
| Observable Result | What is the observable real-world result? | The two parties meet |
| Qualifiers | Time, setting, initiator, private vs public, domestic vs outside? | On Nov 15; private setting |

---

## 2. Three Query Types and Sub-Question Outlets

| Type | Query Focus | Output Protocol | Example |
|---|---|---|---|
| Event Type | Whether a concrete event materializes | Success ledger 3-tier verdict (`judgment-rubric.md` §1–§4) | Job offer, exam, meeting, home purchase |
| Action Type | Whether a specific person takes action | **Two-step response**: 1. Action chain evaluates "will they move"; 2. Success ledger evaluates "will the event succeed" (rubric §8) | Will they confess feelings? Will an ex reach out? |
| Descriptive Type | General atmosphere, dynamics, situation | `matter: description`: Script outputs objective facts (significator ability & contacts, influencing planets, keyword placements) without ledger scoring, tiers, or timing; described via 3 questions per `house-meanings.md` §7 | Will our interactions be contentious? Is competition fierce? |

Descriptive queries focus strictly on situational dynamics and observable interactions; attempting to read a third party's private mind or personality constitutes mind-reading and is rejected (§6 of `matter-rules.md`). Rephrase "what is their personality like" to "how will we interact".

A single query may combine multiple types; answer each sequentially. The example above = Action Type (proactive invitation) + Event Type (meeting materializes) + Two Qualifiers.

**Each Sub-Question Has Exactly One Outlet**:

| Sub-Question | Unique Outlet | Other Layers |
|---|---|---|
| Will someone take action? (reach out, confess, reply, visit) | Action Chain | Success ledger does not answer this question |
| Will the matter succeed? (meet successfully, reconcile, get hired) | Success Ledger + Ability Veto | Desire layer and action chains describe dynamics only |
| Are conditions satisfied? (private, at home; initiator via action chain) | Qualifier Verification (`house-meanings.md` §9) | Does not alter outcome tier |
| What are the dynamics/situation like? | Descriptive (`matter: description`) | No outcome tier |

If different layers produce conflicting answers for the same sub-question, the query was improperly decomposed; re-decompose using this section rather than presenting conflicting conclusions to the user.

---

## 3. Projection Table: Actor's Actions via Derived Houses

Governed by: *Prasna Marga* marriage queries read the woman via Lagna and the **man via 7th house** (`M-XVII.8–9`); house, lord, and significator follow identical principles, with Raman demonstrating derived counting from the 7th house (`M-XIV.116` note). Therefore, **another person's actions are judged using that person's house as the 1st house, counting n houses from there**.

| Action | Derived House from Actor | Classical Significator | Source |
|---|---:|---|---|
| Intent, initiative, courage to speak | 3rd | Mars (courage) | `M-XIV.5`; `M-XIV.31` |
| Speech, communication, messages | 2nd | Mercury (speech) | `M-XIV.4`; `M-XIV.31` |
| Romance, mutual attraction | 7th (counterpart from actor's view) | Venus (pleasure, spouse) | `M-XIV.9`; `M-XIV.31` |
| Practical execution, taking action | 10th | — | `M-XIV.12` (all activities) |
| Obtaining desires | 11th | — | `M-XIV.13` |
| Official approval, superiors, hiring | 10th | Sun (sovereign) | `M-XIV.12`; `M-XIV.90` |
| Examination, study, test performance | 2nd (learning), 5th (intellect, memory) | Mercury, Jupiter | `M-XIV.4`, `M-XIV.7`; `M-XIV.31` |

Derived houses are computed automatically in `structured_prashna.md`. Example: Other party (7th house) -> 2nd from 7th = natal 8th, 3rd = natal 9th, 7th = natal 1st, 10th = natal 4th, 11th = natal 5th. Employer (10th house) -> 2nd = natal 11th, 3rd = natal 12th, 7th = natal 4th, 10th = natal 7th, 11th = natal 8th. The original house significations remain active; narrative includes both layers.

---

## 4. Keyword Extraction

Identify all words in the user's phrasing that **directly name a house or planetary signification** per `house-meanings.md` §6, recording:

1. Word -> House & Planet (source);
2. Polarity: **Aligned** or **Conflicting** relative to the query;
3. Sub-question addressed: Does it pertain to whether the event succeeds, or whether an actor takes initiative (Action chains process initiative planet Mars independently without adding it to `needed_planets`).

Do not invent unstated keywords. If uncertain, treat as unmentioned (default interpretation).

---

## 5. Intake Plan `prashna_plan.json`

Written to the current `prashna_*` directory prior to running `scripts/judge_prashna_standard.py` (SKILL Phase 3).

| Field | Required | Content |
|---|---|---|
| `matter` | Yes | Matter name from `matter-rules.md` §2; custom queries use `general`; descriptive queries use `description` |
| `matter_house` | For meeting, wealth, general, description | Matter house (meeting uses actor's house) |
| `context` | Optional | `romance`: Meeting queries add XVII verses; enables rank 1 visibility order |
| `actor` | For Action type | Actor's house (other party = 7, employer = 10, etc.) |
| `needed_planets` | Optional | Planets intrinsically required for success (Mars for competition/surgery; Sun for official hiring; Mercury/Jupiter for exams). Excluded from malefic penalties in `P-I.3` |
| `keywords` | Optional | Array of `{"word", "houses", "planets", "polarity": "aligned" / "conflicting", "source"}` |
| `qualifiers` | Optional | Explicit prerequisites: `private`, `public`, `at_home`, `outside`, `proactive`, or words from `keywords`. Failure answers: "Under this condition, it cannot materialize." |
| `location` | Optional | `city` (default) / `exact`: Configures input sensitivity window |
| `asker` | For marriage queries | `male` / `female` |
| `direction` | Layoff queries | `occur` (will layoff happen) / `prevent` (can job be saved) |
| `early_departure` | Travel queries | `true` when asking if departure can happen early |
| `time_scope` | For Event/Action types | Horizon within which the query is meaningful: `{"kind": "scope", "label": "tonight", "until": "YYYY-MM-DD"}`, `{"kind": "meaningless"}`, or `{"kind": "unlimited"}` |

Example ("Will they proactively ask me out for a private one-on-one meeting on Nov 15?"):

```json
{
  "matter": "meeting",
  "matter_house": 7,
  "context": "romance",
  "actor": 7,
  "keywords": [
    {"word": "private", "houses": [8, 12, 4], "planets": [], "polarity": "aligned", "source": "M-XIV.20 Randhra; M-XXVII.15–16; M-XIV.6"},
    {"word": "other_proactive", "houses": [9], "planets": ["Mars"], "polarity": "aligned", "source": "M-XIV.5, M-XIV.31; M-XVII.8–9 derived"}
  ],
  "qualifiers": ["private", "proactive"],
  "location": "city",
  "time_scope": {"kind": "scope", "label": "Nov 15", "until": "2026-11-15"}
}
```

---

## 6. Worked Query Decomposition Examples

| Question | Real-world Determining Factors -> Astrological Indicators | Response Architecture |
|---|---|---|
| Will they confess feelings proactively? | Affection -> Venus, 7th lord connection to Lagna; Courage to speak -> 9th lord (derived 3rd), Mars; Means of expression -> 8th lord (derived 2nd), Mercury; Execution -> 4th lord (derived 10th); Obstacles -> Afflictions to 7th house and lord | Action Type: Action chain answers "will they confess"; `confession` success ledger answers "will relationship formalize" |
| Will an ex proactively contact me? | Initiative -> 9th lord, Mars; Communication -> 8th lord, Mercury; Targeted toward querent -> Connection to Lagna lord | Action Type: Action chain answers "will they reach out"; `resume_contact` success ledger answers "will relations soften" |
| Will we reconcile; is there still a chance? | Bridge between parties -> Lagna lord connecting to 7th lord, Venus bridging; Who moves first -> Action chains for both sides; Resolving grievances -> `P-III.3~4`; Resistance -> 6th (strife), 12th (separation), Saturn (delay) | Event Type: `reconciliation` success ledger determines tier; both action chains and resistance enter narrative |
| Can I secure the job offer? | Qualifications -> Lagna & lord capacity (`M-XIV.3`); Employer intent -> 10th lord connection to Lagna lord, employer action chain; Position/authority -> 10th house, Sun; Remuneration -> 11th & 2nd; Competition -> 6th house | Event Type: `job_hunting` success ledger determines tier; `needed_planets` includes Sun |
| Will I pass the civil service exam? | Knowledge/performance -> 2nd, 5th, Mercury, Jupiter; Competition -> 6th; Public post -> 10th, Sun; Selection -> 11th | Event Type: `competitive_exam` success ledger determines tier |
| Will the meeting occur; will they invite me? | Will they invite -> Action chain; Will meeting occur -> Success ledger; Setting -> Qualifiers | Action Type + Event Type: Two-step response |

---

## 7. Custom and Unregistered Queries

**General Paradigm**: Query decomposition maps persons, actions, targets, and conditions onto houses and planets. Once projected, the evaluation applies universal rules (`P-I.3`, `P-I.4`, `P-IV.1`, connections, ability layer, qualifier gates); the matter registry provides topic verses for common questions. As long as elements project onto houses, the query can be answered:

1. **Direct Projection**: Binary outcomes use registry or `general`; situational dynamics use `description`;
2. **Indirect Projection with Human Core**: Identify the underlying human concern. (Example: "Will it rain tomorrow" cannot project onto human affairs; "Will weather disrupt my outdoor event" projects onto `general`);
3. **Inapplicable**: Reject per `matter-rules.md` §6 with a clear reason and alternative formulation.

---

## 8. Clarification and Intake Gates

- **Vague Queries** ("How is my luck", "Tell me about my love life"): Ask user for their single most urgent question with 2-3 concrete examples;
- **Multiple Questions**: One chart answers one question; ask user to choose one;
- **Hypothetical Questions** ("What if I do X"): Rephrase as "If I execute X, will Y result?";
- **Already Occurred Events**: If the outcome is already known, do not cast charts to deduce past events;
- **Binary A/B Choice**: User selects their preferred option, rephrased as "If I execute A, will it succeed?";
- **Repeated Inquiries**: Follow `qa_rules.md` §1;
- **Harm/Extreme Queries**: Provide safety/crisis resources immediately; do not cast a chart.
