---
name: vedic-prashna
description: "Cast and interpret a question-time Vedic Prashna chart for one concrete question using the exact asking time and place. The Shatpanchasika-rooted classical standard layer runs first; Tajika contact and KP 1-249 remain isolated optional stacks. Use for 'Prashna', 'horary chart', 'cast a chart for this question', 'will this specific matter work out'. Not for natal life-trend analysis."
---

# Vedic Prashna: Vedic Horary Chart Analysis Engine

## Language Contract

- Set `client_language` from the user's explicit language request; otherwise default to English.
- Use `client_language` for all chat replies, intake questions, confirmations, progress updates, user-visible warnings, judgments, reports, and Q&A.
- Keep canonical filenames, CLI flags, JSON keys, `structured_prashna.md` and optional-stack schema headings, technical codes, and Sanskrit/English identifiers unchanged.
- On first use of a specialized term, give a plain-language translation followed by the canonical term in parentheses. Never translate canonical identifiers inside calculations or evidence citations.
- If the user changes language mid-run, preserve the existing stack boundaries, data, and artifact lineage; switch client-facing language from that point onward unless explicitly requested otherwise.

## Scope & Positioning

Constructs an independent horary chart cast for the exact moment and location a concrete inquiry arises.
The primary standard layer is rooted in classical *Shatpanchasika*, filtered through the practical compatibility standards of KN Rao and the Bharatiya Vidya Bhavan, with selective inclusion of congruent principles from *Prasna Marga*.
It is strictly an independent horary discipline: natal Jaimini tools, 120-year Dashas, full divisional charts, and Ashtakavarga matrices are never imported into the horary layer.

**Division of Responsibility**:
- The Language Model decomposes the inquiry, extracts keywords, maps the matter house and the actor, and generates the query plan (`prashna_plan.json`).
- The Python adjudication engine (`judge_prashna_standard.py` via `prashna_rules.py`) audits classical ledger rules, capacity vetos, action chains, and qualifier conditions, deriving an internal 3-tier verdict (Favorable / Pending / Unfavorable).
- The Language Model renders the human-readable judgment reading explaining how events unfold based on chart geometry and the audited verdict.
- Favorable or pending inquiries receive an indicative timing overlay grounded in classical texts; unfavorable inquiries receive no timing.

---

## Required Resources

Read sequentially for every horary reading:
1. `resources/question-decomposition.md`: Query decomposition, the 3 question types, derived houses, keyword mapping, plan schema, gates.
2. `resources/house-meanings.md`: House/sign significations, actor mappings, connection criteria, qualifier verifications.
3. `resources/matter-rules.md`: Matter registry, classical topic rules, lookup queries, out-of-scope boundaries.
4. `resources/judgment-rubric.md`: Adjudication rubric and ledger mechanics.
5. `resources/judgment-writing.md`: Structure and protocol for client-facing readings.
6. `resources/moon-policy.md`: Moon usage and boundaries.

---

## Strict Sandbox Constraints

1. Read-only reuse of `vedic-calculator/scripts/engine.py`; never add Prashna, Tajika, KP, or void-of-course fields to the shared engine.
2. Standard output generated exclusively by `scripts/format_prashna_standard.py`; never invoke natal `formatter.py`.
3. Never modify other skills (core, love, career, synastry, rectifier).
4. Artifacts isolated in `prashna_<yyyymmdd_HHMMSS>_<label>/`:
   `structured_prashna.md`, `prashna_plan.json`, `prashna_verdict.json`, `prashna_verdict.md`, and `prashna_judgment_<label>.md`.
   Timing overlay adds `timing_overlay.md`; Tajika adds `tajika_overlay.md`. KP writes exclusively to `kp_horary_<yyyymmdd_HHMMSS>_<label>/`.
5. Never access `user_context.md`.
6. Tajika and KP run in complete isolation; standard builder and judgment scripts never import them.
7. Follow-up Q&A reuses the active query chart without cross-contaminating historical runs.

---

## Standard Layer Exclusions

The following natal features are strictly excluded from the standard horary layer:
- Chara Karakas (AK, AmK, DK, etc.), Upapada Lagna (UL), Arudha Lagna (AL).
- SAV / BAV Ashtakavarga, Shadbala, Bhava Bala.
- Full D9, D10, D4, D5 natal divisional charts.
- Natal yoga pre-scanning (house tables use Ayer functional dignities calculated from occupied/aspected signs).
- 120-year Vimshottari or Chara Dashas.
- Natal transits, Sade Sati, double transit.
- Western aspects or orbs.
- Natal Neecha Bhanga tiers or Pushkara modifications.

Only the rising Navamsa (sign and ordinal), Lagna Drekkana, and the 6-fold Shadvarga table lords are utilized per classical *Shatpanchasika* rules.

---

## Phase 0: Input & Intake Gates

| Input | Standard Protocol |
|-------|-------------------|
| Specific Question | Single observable outcome or descriptive interaction state. Multi-part questions must be decomposed. |
| Query Instant | Taken from message timestamp when asked in chat (preserving seconds and fractions). If the user explicitly provides a time, use it. |
| Query Location | City name or coordinates; must resolve to a valid IANA timezone. Lookup coordinates via `locations.md`. |

---

## Phase 1: Casting the Chart

```bash
python scripts/build_prashna_data.py \
  --datetime "<YYYY-MM-DD HH:MM[:SS[.ffffff]][+HH:MM]|now>" \
  --lat <lat> --lon <lon> --tz "<IANA>" \
  --question "<single observable question>" \
  --label "<kebab-case>" --out-parent "<parent>"
```

Subsequent scripts reuse the exact `Script Time` recorded in `structured_prashna.md` metadata.

---

## Phase 2: Query Decomposition & Planning

Per `resources/question-decomposition.md`:
1. Deconstruct actors, actions, targets, and qualifiers; classify question into Event, Action, or Descriptive type.
2. Apply derived houses for actions of third parties (e.g., partner's initiative = derived 3rd from 7th = natal 9th house).
3. Map keywords to houses and planets with classical references.
4. Write `prashna_plan.json` into the query directory.

---

## Phase 3: Adjudication

```bash
python scripts/judge_prashna_standard.py \
  --datetime "<confirmed_script_time>" \
  --lat <lat> --lon <lon> --tz "<IANA>" \
  --plan <prashna_dir>/prashna_plan.json \
  --out-dir <prashna_dir>
```

Outputs:
- `prashna_verdict.json`: Computational record of classical rule scores, capacity vetos, action chains, and sensitivity checks.
- `prashna_verdict.md`: Markdown ledger breakdown for verification.

---

## Phase 4: Timing Overlay (When Favorable or Pending)

For favorable or pending outcomes, run the timing overlay:

```bash
python scripts/build_timing_overlay.py \
  --datetime "<confirmed_script_time>" \
  --lat <lat> --lon <lon> --tz "<IANA>" \
  --matter-house <house> \
  --mode <general|return> \
  --verdict <favorable|pending> \
  --out-dir <prashna_dir>
```

Writes `timing_overlay.md` without modifying the core standard verdict.

---

## Phase 5: Client-Facing Reading

Render `prashna_judgment_<label>.md` following `resources/judgment-writing.md`:
1. **Core Reading**: Clear narrative describing the progression of events and practical outcome.
2. **Action Chain & Conditions**: Detailed breakdown of underlying dynamics and necessary conditions.
3. **Indicative Timing**: Indicative timing window (if favorable/pending).
4. **Verification Appendix**: Technical data summary strictly separated in the technical verification appendix.
