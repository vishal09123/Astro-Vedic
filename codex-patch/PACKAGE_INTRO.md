# Vedic Skill Suite — Codex Execution Enhancement Package v1.3.0

This patch does not modify any Vedic skill files. Unless instructed otherwise, standard execution treats the selected `SKILL.md` as the sole canonical source of truth for methodology and workflow.

This layer is specifically designed for Codex to prevent common execution failure modes:

- Partial reading of `SKILL.md` or executing from memory;
- Skipping or reordering D1, D9, D10 or other divisional phases;
- Arbitrarily expanding birth-time uncertainty windows or candidate pools;
- Verifying only a favored candidate instead of recomputing the full candidate matrix;
- Reverse-engineering chart explanations from `user_context`, causing conclusions to overfit user life history;
- Early stopping upon finding a single favorable indicator without scanning for counterevidence;
- Failure to select between Standard and Pro core versions before generating reports, or mixing artifacts between versions;
- Treating the skill workflow as an inflexible program, refusing explicit operator directions to re-run, overwrite, or reset;
- Reports overburdened with technical jargon or stripped of explanatory depth;
- Excessive boilerplate disclaimers ("for reference only", "depends on reality", "weigh pros and cons") that obscure actual astrological conclusions;
- Analyst drafts loaded with abstract nouns ("structure, capacity, energy, lessons") without concrete real-world manifestation or memorable chart-specific judgments.

## What this package provides

### 1. Full-Lifecycle Execution Discipline

The global `AGENTS.md` acts as a streamlined router: it requires Codex to read the selected Vedic skill completely to EOF, identify current phase and gates, and load task-specific modules (UC firewall, rectification, blind QA, client voice, normal QA, output routing, or analyst editing).

When both `vedic-core` and optional `vedic-core-pro` are installed, a new natal core analysis selects the version before writing its first core artifact: follows operator specification, or asks once if unspecified. Once selected, all downstream runs, QA, blind questions, and packaging inherit that lineage without mixing.

No arbitrary quotas: questionnaire rounds, candidate cutoffs, sections, and paragraphs adapt to evidence density and task requirements rather than rigid artificial minimums.

When the skill mandates AI interpretation, synthesis, or strongest-signal selection, all required scans and tables are completed, serving as auditable inputs to professional astrological judgment rather than mechanical vote-counting.

### 2. Operator Scheduling Authority

Skills represent default standard procedures, not reasons to refuse explicit operator directions. Subject to system safety and technical limits, the operator may direct steps to be supplemented, re-run, skipped, replaced, or reset.

The operator defines the relationship between new and prior runs:
- Supplement: both runs coexist for specified purposes;
- Supersede: prior affected scores, conclusions, and downstream artifacts are invalidated, making the new run authoritative;
- Reset: restarts from a named checkpoint, preserving only operator-approved materials.

### 3. User Context (UC) Evidence Firewall

`user_context.md`, chat biography, feedback, and known real-world facts cannot substitute for chart evidence.

This rule enforces four separate boundaries:
- Recording facts is an administrative log, not chart evidence;
- Read permissions follow the active skill phase;
- Permission to read does not permit generating or weighting chart conclusions from UC;
- Only after chart conclusions are locked may authorized UC be used for ethical checks, tone calibration, real-world option mapping, or post-hoc verification.

Chart judgments must be independently reproducible after deleting all UC data.

### 4. Client Readability and Professional Voice

Technical precision and client readability are separated into distinct layers:
- Core technical tables maintain strict astrological rigor;
- Client-facing sections provide clear, empathetic, and definitive astrological judgments;
- Answers are delivered directly before introducing necessary caveats;
- Stock boilerplate disclaimers are removed;
- Abstract astrological mechanisms are translated into observable life manifestations.

### 5. Artifact and Output Routing

Manages artifact paths and formats across normal QA (`qa_<topic>.md`), comprehensive analyst reports, blind QA artifacts, and standalone HTML presentation files.
