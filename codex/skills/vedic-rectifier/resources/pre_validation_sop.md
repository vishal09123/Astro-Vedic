# Pre-Validation Reading SOP (`pre_validation_sop`)

> Unified protocol for blind testing and pre-validation readings, shared between `vedic-reader` (Step 5: Pre-validation Reading) and `vedic-rectifier` (Step 5: External Validation).

---

### Step 5: Pre-Validation Reading (Blind Testing Protocol)

**⚠️ Mandatory Gate: Pre-validation is the core tool for verifying birth time precision — the hit rate directly determines the usable divisional chart tier and the analytical confidence rating.**

Formulate 3–5 **declarative statements** derived from structural chart data to verify the birth time baseline before proceeding to comprehensive life synthesis.

**Design Principle: Strong signals only.** Select facts with short derivation chains, strong multi-layer support, and immediate verification value. Avoid unfalsifiable statements (temperament descriptions, body marks, vague medical forecasts). Prioritize structural facts the user can answer decisively with "accurate" or "inaccurate".

---

## 1. Core Analytical Principles

1. **Scan the entire chart for strongest signals**: Articulate domains where planetary signals converge unambiguously.
2. **Omit weak signals**: Better 3 accurate hits out of 3 statements than 2 hits out of 5 statements.
3. **Derivation visibility**: The visible derivation chain in the prompt is at most 2 steps: `[Data Anchor] -> [Concrete Conclusion]`.
4. **Skip contradictions**: If signals on a topic conflict (e.g., high SAV but debilitated lord), skip that domain.
5. **Tri-Axial Settlement for Chronological Events (Category F)**:
   - **Domain Axis**: Which life area is activated?
   - **Form Axis**: What structural category of event manifests (initiation, consolidation, elevation, restructuring, disruption)?
   - **Time Axis**: Which Mahadasha / Antardasha / Pratyantardasha window governs?

---

## 2. Multi-Method Convergence Mandate

Every topic has multiple analytical layers (house lord, natural Karaka, Chara Karaka, Arudha Lagna, house occupancy). Audit all applicable layers:
- **Convergent (Multiple layers align)**: Strong signal -> Select, and weave layers into a single cohesive statement.
- **Primary Layer Strong, Auxiliary Unconfirmed**: Usable (lack of confirmation != negation).
- **Divergent Layers**: Do not select; report as contradictory.
- **Auxiliary Only (AL or natural symbol alone)**: Forbidden as an independent basis.
- **Constant Methodology across Candidate Charts**: When differentiating candidate charts, apply the exact same derivation rules to every candidate.

---

## 3. Candidate Categories for Pre-Validation

### High-Hit Rate Categories (>= 85% - Preferred)
- **A. Parental Dynamics / Household**: Sun condition -> father figure; Moon condition -> mother figure; 4th/9th house afflictions -> foundational household atmosphere.
- **B. Educational Attainment**: 5th lord + Jupiter status (high vs. strained academic progress; do not guess specific majors).
- **C. Distant Relocation**: 4th lord in 12th house, or nodes in 4th/9th/12th converging with dispositors -> living away from birthplace.

### Moderate-Hit Rate Categories (60% - 75% - Usable when Strong)
- **D. Childhood Economic Atmosphere**: 2nd house SAV + 2nd lord + Saturn.
- **E. Siblings**: 3rd lord condition.
- **F. Chronological Turning Points**: Major Dasha x Antardasha milestones (MD x AD).

### Conditional Categories
- **G. Node Focal Points**: When Rahu/Ketu connect decisively to dispositors and divisional themes.
- **H. Relationship Status**: Used strictly when the querent has not disclosed relationship status.

---

## 4. Permanent Prohibitions

- ❌ **Physical Marks & Scars** (Historically unviable; 8% hit rate).
- ❌ **Disease Prognostication** (High risk of false alarm).
- ❌ **Vague Personality Traits** (Barnum effect; unfalsifiable).

---

## 5. Chronological Timing Event Rules

1. **Resolution**: MD x AD resolution for multi-year intervals; Pratyantardasha (PD) required only for verified monthly inquiries.
2. **Channel Hierarchy**:
   - Channel 1: House rulership (Primary - unique to chart).
   - Channel 2: Resident house activation (Primary - unique to chart).
   - Channel 3: Natural Karaka (Auxiliary - universal symbol).
   - Channel 4: Chara Karaka (Auxiliary - confirmatory).
   At least one primary channel (Channel 1 or 2) must point to the event.
3. **No Age Presumptions**: Base timing strictly on Dasha intervals, never on conventional age scripts (e.g., assuming college graduation at 22).
4. **Anti-Truism Filter**: Never frame statements so broadly that any random peer would answer yes (e.g., "a major life transition between 2020 and 2024").

---

## 6. Output Template & Feedback Protocol

Output statements as numbered Markdown items with derivation notes formatted in blockquotes:

```markdown
Before proceeding to full synthesis, let us verify several chronological and structural anchors to confirm birth time accuracy:

**1.** [Structural fact regarding parents, education, relocation, or baseline condition]

> Derivation: [Planetary placement, house lord status, and dignity]

**2.** [Structural fact or node dispositor chain]

> Derivation: [Planetary placement and aspects]

**3.** Between [YYYY] and [YYYY], you experienced [specific event category: relocation, career change, educational milestone].

> Derivation: [MD-AD interval and house activation]

Please respond to each point: **Accurate / Inaccurate / Partially Accurate**
```

### Feedback Evaluation Matrix
- **>= 4/5 Accurate**: High Confidence -> Proceed to full synthesis.
- **3/5 Accurate**: Moderate Confidence -> Proceed; suggest fine-tuning if D10/D5 divisional precision is critical.
- **<= 2/5 Accurate**: Low Confidence -> Flag potential birth time discrepancy; strongly recommend birth time rectification.
