# 📋 Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] - 2026-10-23

### Calculator Engine v1.0.1: Calculation Failures No Longer Silent; Ephemeris Warning Fixes

- **Exception isolation for auxiliary components**: Bhava Bala, special lagnas, Vargeeya, and Pushkara now catch exceptions independently. Previously, a single shared `try...except: pass` block caused subsequent calculations to silently abort without logging. Failed components now log `{'error': ...}` and populate `calc_errors`. A warning header is printed in `structured_data.md` when incomplete.
- **`check_env.py` ephemeris path check**: Now checks the actual search directories used by engine and PyJHora rather than Swiss Ephemeris package root.
- **KP precession audit**: Verified that planets and cusps share the identical Krishnamurti ayanamsa without coordinate system splitting.
- **Polar circle chart handling**: Placidus house cusps are mathematically undefined beyond the polar circles (|latitude| >= 90° - obliquity); `build_kp_horary.py` now exits with a clear explanation rather than raising uncaught exceptions.

### Calculator Engine v1.0: Second-Level Instant Precision, Lagna Parity with Desktop JHora

- **Second-level timestamps**: `calculate_full_chart` and `to_jd` now accept floating-point seconds. Charts localize once, deriving Julian Day and PyJHora wrappers (SAV, 15 divisional charts, Dasha, Shadbala, Bhava Bala, Special Lagnas, Vargeeya, Pushkara, and boundary audits) from the identical instant. Full-minute inputs maintain byte-for-byte baseline parity.
- **Prashna precision**: Full query instant is passed directly to the engine, removing selective downstream recomputation.
- **Lagna parity**: Lagna is calculated as apparent tropical ascendant minus identical ayanamsa (TRUEPOS | NONUT). Benchmark verification against desktop JHora output (2004-09-12 11:15:27 Shanghai) confirmed: Lagna delta = 0.004", ayanamsa delta = 0.002", classical planets delta <= 0.006". PyJHora divisional charts synchronized via `houses_ex` patch.
- **Polar charts**: Dig Bala uses Porphyry houses in polar regions where Placidus is undefined.
- **Operating Dasha tagging**: Compares timezone-aware `as_of` (UTC) against birth offset instead of host machine clock.
- **Provenance**: Chart metadata includes `calc_meta` (engine version, UTC calculation instant, actual ayanamsa), printed in headers of `structured_data.md` and `structured_prashna.md`.
- **Rectifier**: `--local-time` accepts seconds, reporting binary-searched sign transition boundaries down to the second.
- **Precision test suite**: Added `vedic-calculator/tests/test_engine_precision.py` (benchmark golden charts).

---

## [Unreleased] - 2026-10-21

### Prashna Follow-Up Integration with Verdict v3

- `qa_rules.md` §4 standard follow-up Q&A: voice and meaning sources match judgment rubric (`judgment-writing.md`). Follow-up questions do not alter internal tiers.
- `SKILL.md` Phase 7 updated with cross-references.

### D2 Lineage Documentation Correction

- Confirmed that `divisional_charts["D2"]` in `vedic-calculator` represents Uma Shambhu Hora (`chart_method=1`), matching desktop JHora "D-2 (US)", distinct from traditional Sun/Moon Hora.
- Reader validation rules updated to reflect US Hora parity.

### Prashna P-I.4 "Benefic Varga" Reads Shadvarga Majority

- **Preponderance calculation**: The six divisional lords (D1, D2, D3, D9, D12, D30) are evaluated per Ayer functional tags: benefic dominant = benefic varga, malefic dominant = malefic varga, equal = excluded (`judgment-rubric.md` §4.1). Sourced from *Prasna Marga* VIII.29 and XXIV.45.
- **Traditional Sun/Moon Hora**: Formula-calculated Sun/Moon Hora verifies D3/D9/D12/D30 against engine division; formula verified against *Prasna Marga* XVIII.148 worked examples.
- **Data contract**: `structured_prashna.md` includes Lagna Shadvarga table with critical shift distances.

### Prashna Verdict v3: Storytelling Narrative and Reconciliation Verses

- **`resources/judgment-writing.md` added**: Mandatory reading for Phase 6. Establishes astrologer voice, plain-language translations of classical terms, and structured narrative unfolding without mechanical template repetition.
- **Ledger-driven narrative**: Internal outcome tier provides the narrative backbone; narrative does not alter ledger scoring.

---

## [Unreleased] - 2026-10-20

### Prashna Standard Layer Rebuild: Internal Preponderance and Prasna Marga Integration

- Integrated Shatpanchasika with *Prasna Marga* Chapter XVII.
- Success ledger itemization, ability layer veto power, and qualifier evaluation separated from primary ledger sum.

### Rectifier `time_scan.py`: Named IANA Timezone Parameters

- `--tz` parameter requires IANA timezone strings (e.g. `Asia/Shanghai`) rather than fixed numeric offsets, ensuring proper daylight saving time calculations.

---

## [Unreleased] - 2026-10-11

### Prashna Negative Counting and Topic Modality

- Formalized negative counting rules for outcome ledgers.
- Modality rules (movable vs fixed) aligned with classical topic requirements.

---

## [Unreleased] - 2026-10-10

### Prashna Preponderance and Classical Verse Corrections

- Evaluated mixed configurations via classical verse preponderance rules.
- Added `tzdata` dependency for cross-platform Windows timezone handling.
- Codex Patch v1.2.0: Rectifier balanced-weight methodology.
- Prashna auxiliary layer boundaries: Tajika non-execution conditions and KP eligibility gates.
- Ayer functional benefic/malefic role criteria implemented across all standard questions.
- Rectifier calibration methodology updated with `calibration_quiz.md`.
- Timing sub-layer enabled for Favorable and Balanced tiers, disabled for Unfavorable.
- `vedic-core` Step 4.5: User context wording adjustments without altering astrological conclusions.

---

## [Unreleased] - 2026-09-04

### Calculator Engine v0.9: Baseline Ephemeris and Vimshottari Timeline Parity

- Standardized Swiss Ephemeris configuration.
- Parivartana Yoga 3-category classification: Dainya criteria corrected to single-sided dusthana lordship.
- Repository structure refactored: Canonical root moved to `skills/`.
- `skill_sync.py` updated to retain ephemeris data files.

---

## [Unreleased] - 2026-09-03

### Synchronizer and Pipeline Maintenance

- Added `skill_sync.py` for automated platform and local installation synchronization.
- Anchored artifact fingerprinting: `source_commit` tracks canonical source files rather than build commits.

---

## [Unreleased] - 2026-08-28

### Multi-Platform and Architecture Hardening

- Implemented Pratyantardasha timeline auditing.
- Added Codex Patch layer (`codex-patch/`).
- Sandboxed and isolated `vedic-prashna` directory structure.
- Cleaned legacy cross-platform duplicates.

---

## [v8.0] - 2026-07-12

### ✨ Added `vedic-prashna` (Question-Time / Horary Astrological Engine)

- Shatpanchasika-rooted classical Prashna standard layer.
- Complete isolation from natal chart pipeline.
- Optional Tajika and KP 1-249 reading stacks.
- Question-time calculation engine with exact second precision.

---

## [v7.0] - 2026-06-18

### ✨ Added `vedic-synastry` (Two-Chart Relationship Comparison Engine)

- Parashari mutual activation analysis across four life frameworks: Romantic, Business, Friendship, Family.
- Ashtakoota 36-point lunar mansion screening layer.
- Upapada Lagna and Darakaraka capacity diagnostics.
- Shared Dasha timeline convergence and transits.

---

## [v6.1] - 2026-06-08

### Calculation Hardening and Precision Verifications

- Fixed Shadbala percentage computation in formatter.
- Corrected Sun Ishta/Kashta Phala calculation.
- Calculator Engine v0.5: Fail-fast architecture removing silent fallbacks.
- Verified precision against desktop astrology benchmarks across 24 test charts.
- Formatter outputs complete Vimshottari Antardasha timelines.

---

## [v6.0] - 2026-06-07

### ✨ Added `vedic-calculator` (Native Swiss Ephemeris Calculation Engine)

- Full Vedic natal chart calculation from birth date, time, and geographic coordinates.
- Swiss Ephemeris offline planetary positions and house cusps.
- Divisional charts D1 through D60.
- Shadbala, Bhava Bala, and Ashtakavarga computation.
- Complete 120-year Vimshottari and Chara Dasha schedules.
- Standardized `structured_data.md` contract generation.

---

## [v5.0.1] - 2026-05-24

- Enhanced reader data extraction and pre-validation heuristics.
- Hardened rectifier search algorithms.

---

## [v5.0] - 2026-05-22

- Added `report_builder.py` HTML generation engine.
- Established 16-point validation rules in `vedic-reader`.

---

## [v4.0] - [v4.9] - 2026-05-10 to 2026-05-14

- Core natal life area synthesis (10 life dimensions).
- P1-P12 planet and house diagnostic auditing.
- Dedicated career and relationship interpretation engines.

---

## [v1.x] - [v3.0] - 2026-05-04 to 2026-05-06

- Initial release of core Vedic astrology prompt suites and interpretation frameworks.
