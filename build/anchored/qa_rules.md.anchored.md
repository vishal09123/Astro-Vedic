# Q&A Mode Protocol (`qa_rules`)

<!-- ANCHOR: A-QA-59002126 L2 -->
> Purpose: Operates when a comprehensive `vedic-core` report already exists or when the user presents an existing natal reading file, avoiding re-running the full pipeline.
> Scope: Technical astrological inquiries, thematic deep dives, and life guidance.

---

<!-- ANCHOR: A-QA-8dcbc3c8 L1 -->
## ⚠️ Ethical Protocol (Highest Priority)

**Review `user_context.md` (if present) before answering. Giving advice in total ignorance of verified trauma is an ethical failure.**

<!-- ANCHOR: A-QA-d6fc1952 L1 -->
### Ethical Checklist (Review Before Formulating Responses)
- **Bereavement Check**: If a parent or loved one is deceased, never advise "improving communication" or "reconciling". Anchor interpretation to emotional legacy rather than living relationships.
- **Trauma Check**: If severe trauma (bankruptcy, domestic strife, severe illness) is documented, ground planetary signals in verified reality rather than applying flippant generic templates.
- **Contradiction Check**: If astrological indications diverge from direct lived experience, acknowledge the divergence factually as latent potential vs. manifest circumstance.
- **Behavioral Patterns**: Tailor practical guidance to verified behavioral tendencies (e.g., career changes, relationship patterns).

<!-- ANCHOR: A-QA-94d10e70 L1 -->
### How to Utilize `user_context.md` Without Contaminating Astrological Logic
- **Analytical Conclusions** (from `p2a-p5b` reports): Strictly preserved without alteration.
- **Tone & Delivery**: Calibrated with empathy according to biographical context.
- **Actionable Guidance**: Grounded in the user's tangible circumstances.

---

<!-- ANCHOR: A-QA-d622802e L1 -->
## Processing Protocols

<!-- ANCHOR: A-QA-874b69b2 L3 -->
0. **Date Expiration Check**:
   - Re-anchor the active Mahadasha, Antardasha, and Pratyantardasha (PD) to **today's wall-clock date**, rather than blindly trusting historical `is_current` indicators frozen in older reports.
   - If transit data is older than 3 months, recalculate or qualify transit timing boundaries.
<!-- ANCHOR: A-QA-1c48b790 L3 -->
1. **Double-Sided Verification**: Evaluate supporting vs. restricting planetary factors for every judgment question. Never provide unilateral cheerleading.
<!-- ANCHOR: A-QA-badaf9ae L3 -->
2. **Anchor to Existing Data**: Cite explicit placements from `structured_data.md` and conclusions from existing reports.
<!-- ANCHOR: A-QA-1f14fac9 L3 -->
3. **Tri-Axial Settlement Protocol**:
   - **Domain Axis**: Which house, lord, and natural Karaka are activated?
   - **Form Axis**: What is the qualitative dignity and structural manifestation?
   - **Time Axis**: Which Dasha and transit windows align with the inquiry?
<!-- ANCHOR: A-QA-8c7bac86 L3 -->
4. **Time Window Discipline**: Ground timing in Mahadasha x Antardasha (MD x AD) windows; cite Pratyantardasha (PD) for narrow monthly queries.
<!-- ANCHOR: A-QA-3e7c3dcc L3 -->
5. **Divisional Chart Separation**: Maintain strict separation between Track A (internal divisional lords) and Track B (natal D1 lords projected into divisional houses).
<!-- ANCHOR: A-QA-c290d9c3 L3 -->
6. **Artifact Output**: Save Q&A consultations to `parts/qa_<topic>.md`.
