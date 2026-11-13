# Prashna Q&A and Follow-Up Rules

> Follow-up questions continue using the original chart rather than picking favorable answers by casting at new timestamps. Computational and judgment authorities across Standard, Tajika, and KP remain strictly isolated; cross-stack comparisons present findings side-by-side without combining scores.

---

## 1. Classifying Follow-Up vs New Query

A follow-up must remain centered on the exact same observable outcome as the original chart:

- Clarifying terminology, source support tiers, input stability, or specific evidence citations;
- Detailing driving forces, resistances, turning points, realistic conditions, and timing layers;
- Elucidating the 3-layer architecture: operational capacity (ability layer), current planetary engagement (desire layer), and environment (success ledger);
- **Adding qualifiers to the original result**: initiator, private vs public, domestic vs external, or specific day constraints (§4);
- Explaining Tajika Yogas or KP promise/gate mechanisms;
- Comparing why generated Standard, Tajika, and KP findings align or diverge.

The following represent a new query, requiring return to `SKILL.md Phase 0`:

- The target person, desired outcome, or action to be taken has changed;
- New material facts fundamentally alter the semantics of the outcome;
- Transitioning from an observable outcome to mind-reading private motives or long-term multi-year trends;
- Jumping from the original matter to an independent topic.

Adding qualifiers does not cast a new chart: asking "will we meet" followed by "only if they initiate" or "only if private" addresses the same observable event (the meeting). Update the plan sheet and rerun the judgment script on the **same chart**.

**Do Not Repeatedly Cast Charts for the Same Question**: If the question, objective, and real-world facts remain unchanged, requests to re-cast at a new moment must be answered: "Because neither the query nor real-world circumstances have changed, casting again would merely be fishing for answers; we adhere to the original chart cast upon your first clear query." This is an operational intake gate, not a classical omen, and must never be interpreted as "the matter will fail".

**Different Phrasings of the Same Relationship Count as the Same Question**: For the same individual, asking "will they reply", "can we reconcile", and "will my pursuit work" uses the first chart; "will they contact" reads the action chain, while "can we reconcile" reads the success ledger. Re-casting is justified only when real-world circumstances fundamentally change (e.g., they made contact, reunited, or definitively parted).

**Classification Correction (Sole Exception)**: If the initial run categorized the matter under an incorrect topic, re-run judgment on the **same chart** with an updated plan sheet, marking the audit section "Classification Correction" with explicit rationale.

---

## 2. Resolving the Current Chart

Resolve a single unambiguous directory:
- Standard / Tajika: `prashna_<yyyymmdd_HHMMSS>_<label>/`
- KP: `kp_horary_<yyyymmdd_HHMMSS>_<label>/`

If multiple directories exist in the session and reference is ambiguous, ask the user to specify; never guess across all folders.

Correcting erroneous input (e.g. invalid coordinates or missing seconds) invalidates downstream artifacts and rebuilds using original query timestamps; this is error correction, not a second horary query.

---

## 3. Four Q&A Routing Modes

| Mode | Permitted Inputs | Output Authority |
|---|---|---|
| Standard Follow-up | Current `structured_prashna.md`, `prashna_judgment_*.md`, `timing_overlay.md`, same-directory Standard Q&A | Explains standard ledger, internal tiers, and timing sub-layer |
| Tajika Follow-up | Standard files above + `tajika_overlay.md` | Explains contact dynamics; cannot alter standard 3-tier verdict |
| KP Follow-up | Current `structured_kp.md/json`, `kp_judgment_*.md`, same-directory KP Q&A | Explains KP promise, Ruling Planets, gates, timing; cannot read standard directory |
| Cross-Stack Comparison | Explicitly linked Standard directory and KP directory | Side-by-side explanation; no voting or combined conclusions |

Prohibited across all modes:
- Reading `user_context.md`;
- Unselected external Prashna or KP directories;
- Artifacts from `core`, `love`, `career`, `synastry`, or `rectifier`;
- Generating natal-style Dashas, SAV, divisional charts, or transits from horary charts.

---

## 4. Standard and Tajika Follow-Up Guidelines

### Standard Follow-up
Explain how the matter unfolds using the judgment sheet's `rule_id` and audit sections (ability layer, desire layer, qualifiers). Ground every assertion in whitelisted fields. Support tiers A/B reflect textual coverage, not probabilistic percentages, and do not dictate the internal tier. Never speak internal technical tier names directly to the user.

Adopt the empathetic, professional voice of `judgment-writing.md` §1. When technical terms first appear, provide plain English equivalents immediately. Source house/planet meanings exclusively from `house-meanings.md`.

Never alter outcome tiers in follow-ups: verdicts follow the original audit ledger. If an error is discovered in applied rules or houses, treat it as error correction: invalidate downstream artifacts, correct the plan sheet, re-run judgment (`SKILL.md Phase 3`), and regenerate the judgment sheet with an explanation.

**User Supplements Constraints**: If the user adds prerequisites (e.g. "must be initiated by the other person", "only counts if private"), update `prashna_plan.json` and re-run judgment on the same chart. If an essential prerequisite is not established, state: "Under this specific condition, it cannot materialize."

**Questions on Action, Initiative, and Connection**: Read the existing `structured_prashna.md` tables for derived houses, action chains, and planetary bridges directly without re-casting. Derived actions count from that person's house.

**When Users Propose Alternative Interpretations**:
1. If their interpretation identifies an omitted keyword or wrong matter house in the ledger -> Treat as correction, update plan sheet, and re-run judgment;
2. If grounded in texts but belonging to the descriptive layers (ability, desire, action chain) -> Explain what it signifies and why it does not alter the binary outcome tier;
3. If ungrounded or conflicting with classical texts -> Clarify the authentic classical reading objectively without pandering to alter verdicts.

### Tajika Overlay Follow-up
When explicitly requested, execute:

```bash
python scripts/build_tajika_overlay.py \
  --datetime "<original chart 'Script Time'; YYYY-MM-DD HH:MM:SS[.ffffff]>" \
  --lat <original lat> --lon <original lon> --tz "<original IANA>" \
  --querent-lord <Lagna lord> --matter-lord <matter house lord> \
  --out-dir "<current prashna_* directory>"
```

Do not overwrite `structured_prashna.md`. Inapplicable for table lookup queries, descriptive queries, or when querent and matter lords are identical.

---

## 5. KP Follow-Up and Subsequent Activation

KP follow-ups reuse the original KP number, timestamp, coordinates, and topic. The conclusion of `love-materialization` addresses only whether an explicit, confirmed romantic relationship forms, never casual reconnecting or flirting.

If the user requests KP after a Standard chart:
1. User personally provides an integer `1–249`;
2. Record the exact timestamp and coordinates at the start of evaluating the KP query;
3. Confirm the observable outcome scope;
4. If scope matches a supported topic, generate in an independent `kp_horary_*` directory; otherwise exit per `kp-optional.md`.

---

## 6. Comprehensive Cross-Stack Follow-Up

When the user asks for a holistic comparison across systems, present in structured columns:

```markdown
## Standard Layer
<Support tier, internal outcome tier & strength, rule ledger summary, ability layer & qualifier results>

## Tajika Layer
<Direct contacts, mediation / assistance / blockage, timing status; independent of standard timing>

## KP Layer
<Independent promise status, positive/negative house linkages, gates, timing status>

## Alignments and Divergences
- Alignments: <Itemized points>
- Divergences: <Itemized points>
- Boundaries: Systems do not combine votes. The Standard layer provides the classical baseline; KP remains independent. Timing estimates originate from distinct traditions and do not calibrate each other.
```

---

## 7. Timing Inquiries

- Standard Layer: Timing is provided only for Favorable or Balanced tiers via `timing_overlay.md`; Unfavorable tiers (including ability vetoes) receive no timing.
- Fixed Date Queries: The timing sub-layer identifies planetary rhythm and the nearest activation date; it cannot certify an exact calendar date. Explain this neutrally without shifting tiers.
- Horizons: Reuses `time_scope`. If asking "what about next week", evaluate against existing candidates.
- Tajika: Shows `degree difference × 12 days` strictly when direct primary Itthasala exists.
- KP: Candidate dates appear strictly when positive promise, retrograde clearance, and complete Ruling Planets/period/transit intersections are met.

---

## 8. Q&A Documentation

Single-stack Q&A is recorded in `qa_<short_topic>.md` inside the respective directory:

```markdown
# Q&A: <Topic>

**Associated Chart**: <Directory Name>
**Timestamp**: <YYYY-MM-DD HH:MM:SS>
**Type**: [Clarification / Elaboration / Extension]
**Target System**: [Standard / Tajika / KP]

## Question
<User Question>

## Answer
<Plain English Explanation>

## Citations
- <File> §<Section>: <Field or Conclusion>
```

---

## 9. Verification Checklist

- [ ] Is the current chart directory uniquely resolved?
- [ ] Is the original chart reused rather than taking a new clock time?
- [ ] Do single-stack inquiries read only permitted files?
- [ ] Are Standard, Tajika, and KP presented without combined voting?
- [ ] Is timing withheld for Unfavorable tiers, and are timings kept strictly isolated across stacks?
- [ ] Are supplementary user constraints processed by updating `prashna_plan.json` and re-running judgment?
- [ ] Is `user_context.md` completely excluded from reading?
