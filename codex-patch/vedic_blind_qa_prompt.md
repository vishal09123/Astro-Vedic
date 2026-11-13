# Vedic Blind Q&A Protocol v1.3: Full-Scan and Locking Specification

> **Purpose**: Sourced on top of an established `vedic-core` or `vedic-core-pro` chart audit to answer blind validation questions (e.g., "In the past N years, which year saw the highest...", or "Identify a major event in my past without my prompting").
> This protocol does not modify any Vedic skill; it acts as an additional execution layer when blind validation is explicitly requested.

## Invocation Protocol

This protocol executes by default under **User Context (UC) Isolated Blind Audit**: `user_context.md`, chat biography, and known life events may exist in the environment, but must not influence conclusion generation, candidate selection, weighting, stopping criteria, or confidence scoring. The primary goal is to enforce an exhaustive scan and prevent reverse-engineering from known biographical facts.

When the user explicitly requires proof that answers were never exposed prior to analysis, upgrade to **Zero-Leakage Blind Test** requiring a fresh session and a sanitized data package.

Recommended invocation template:

```text
Using the established vedic-core or vedic-core-pro lineage, execute the Vedic Blind Q&A Protocol v1.3.

Questions:
1. [Question 1]
2. [Question 2]

Candidate Range: [e.g. 2016-01-01 to 2026-07-24]
Metric Definition: [e.g. "Annual business income, distinct from asset appreciation or cash savings"]
Mandatory Single Choice: [yes / no]
Audit Tier: [UC Isolated Blind Audit / Zero-Leakage Blind Test]

User context is strictly isolated and does not enter chart conclusions.
Exhaustively scan all candidates within the range, displaying weighted positive/negative evidence matrices; continue scanning until range end even after locating a strong candidate.
```

---

## 1. Input Isolation

### 1.1 Audit Tiers

#### A. UC Isolated Blind Audit (Default)
- Executes in existing sessions containing user biography or prior reports.
- User Context (UC) is treated as an isolated layer: visible to the environment but strictly forbidden from serving as astrological reasoning evidence.
- If the correct answer is already known from context, record: `Answer known: Retrospective exhaustive audit; does not count as independent blind hit.`
- Known answers do not constitute stopping conditions. Exhaustive scanning of all candidates remains mandatory.
- Context must not determine search order, signal priority, stopping thresholds, or tie-breaking.

#### B. Zero-Leakage Blind Test (Explicit Request Only)
- Must be launched in a new task without inheriting conversation history, feedback, or biography.
- Uses sanitized data packages only; prompting "please forget earlier context" is not acceptable isolation.
- If an answer is leaked before candidate locking, downgrade to Retrospective Audit.

### 1.2 Whitelisted Chart Evidence

Inherit the locked core report lineage (`vedic-core` or `vedic-core-pro`). Both lineages whitelist pure chart facts, Dasha timelines, and validation data from `structured_data.md`.

For `vedic-core`:
- `p1_overview.md`;
- `p2a_planets.md` through `p2d_planets.md`;
- `p3a_d9.md`, `p3b_divisional.md`;
- `p4_houses.md`;
- `appendix.md`.

For `vedic-core-pro`:
- Corresponding technical audit files.

---

## 2. Exhaustive Candidate Scan Protocol

1. **Explicit Candidate Enumeration**: Every candidate within the defined time range (years, months, or transits) must be itemized before scoring begins.
2. **Standardized Evidence Scoring**: Evaluate each candidate against natal chart indicators, operating Vimshottari Mahadasha / Antardasha / Pratyantardasha, divisional activations (D9/D10), and major transits (Jupiter, Saturn, Rahu-Ketu).
3. **No Early Termination**: Locating a high-scoring candidate does not stop the scan; every candidate across the full range must be evaluated.
4. **Counterevidence Auditing**: Record inhibiting factors, contrary transits, and conflicting Dasha periods for each candidate.
5. **Final Candidate Locking**: Rank candidates based on net astrological convergence, outputting the primary candidate, runner-up, and specific discriminator before user feedback is revealed.
