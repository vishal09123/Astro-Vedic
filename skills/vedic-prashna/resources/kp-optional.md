# KP Horary Independent Stack (1–249)

## System Positioning

KP Horary is an independent system strictly isolated in calculation, files, and judgment authority from the Parashari standard layer; it is not secondary evidence. Users may inspect both results separately or compare them side-by-side in Q&A, but voting scores must never be merged. It executes only when the user explicitly requests KP and personally supplies an integer between `1–249`.

Never:
- Generate a number on the user's behalf from question wording, clock minutes, or random number generators;
- Substitute the query-time clock Ascendant while claiming classical KP Horary;
- Append KP outputs into `structured_prashna.md`;
- Concurrently display both KP and Parashari conclusions and synthesize them;
- Use True Chitrapaksha in place of Krishnamurti ayanamsa;
- Use standard layer Moon ingress, Chandra Kriya, or natal Dasha timing.

---

## Classical Sources

This stack strictly derives its rules from the K.S. Krishnamurti *KP Readers*:

- Reader I, *Casting the Horoscope*: Placidus/Raphael houses, Krishnamurti ayanamsa;
- Reader III, *Predictive Stellar Astrology*: Vimshottari proportional subs, 249 divisions;
- Reader IV, *Marriage, Married Life & Children*: Cross-examination of marital and reunion semantics;
- Reader VI, *Horary Astrology*: 1–249 input, significator hierarchy, cusp sub-lord promise, house groupings for implemented topics, Ruling Planets.

Reference collection: <https://archive.org/details/kp-readers>

---

## Phase KP-0: Intake Gate

Mandatory inputs:

| Input | Requirement |
|---|---|
| Concrete Question | Single observable outcome |
| KP Number | User-provided integer `1–249` |
| Judgment Timestamp | The exact moment of analyzing the question |
| Judgment Location | Location of judgment; latitude, longitude, and IANA timezone |
| Topic | Must match an implemented topic rule |
| Observable Outcome Scope | Confirmed by user, matching the classical source scope exactly |

Currently supported topics:

| Topic | Outcome Scope | Judgment Cusp | Positive Condition | Negative Condition | Classical Source Scope |
|---|---|---:|---|---|---|
| `love-materialization` | `explicit-mutual-relationship` | 5 | 7 and 11 must both be linked | 6 or 12 linked | Whether parties establish an explicit, mutually confirmed romantic relationship |
| `business-partnership-continuity` | `business-partnership-continuity` | 7 | 5 or 11 linked | 6 or 12 linked | Whether an existing commercial partnership continues |

Topics must be chosen based on a single observable outcome. If a query touches multiple topics, return to intake for disambiguation rather than combining house groupings in a single KP chart.

### Inapplicable Intake Gate Exits

If the topic is unsupported, the outcome scope triggers fail-closed, or the location is within polar circles (|lat| ≥ 90° − obliquity, where Placidus cusps are undefined, causing `build_kp_horary.py` to exit with `[KP Inapplicable]`), do not cast a KP chart; provide three clear statements:

1. Explain in plain English why KP is currently inapplicable: lack of an authentic formula in the source texts does not mean the event will not occur;
2. Offer the standard Parashari layer instead: supported topics are listed in `matter-rules.md`, covering relationships, contact, and reconciliation;
3. Alternatively, rephrase into a supported KP question (from the table above) and confirm the observable scope before giving a number.

Present options neutrally without switching automatically or rewriting the user's question.

### Relationship Scope Gate

Confirm the user's true observable outcome verbatim without raising thresholds to fit existing formulas:

| User's Actual Desired Outcome | Outcome Scope | Current Processing |
|---|---|---|
| Establish an explicit, mutually confirmed, ongoing romantic relationship | `explicit-mutual-relationship` | Permitted into `love-materialization` |
| Only resuming casual, warm, or flirtatious interaction | `romantic-interaction-rewarming` | Fail-closed; no KP chart |
| Only resuming communication, replies, or meeting | `romantic-contact-resumption` | Fail-closed; no KP chart |
| Other party's private feelings, thoughts, or intentions | `private-feelings-or-intent` | Fail-closed; no KP chart |

If "reconnecting" and "formalizing an explicit relationship" appear together, request user clarification first; never treat them as synonyms or bypass the scope gate simply because a number was provided.

`marital-reunion` is not automatically supported. Readers IV and VI document three distinct classical contexts:
- "Reunion and resumption of domestic life" uses event significators 2, 7, 11;
- "Whether husband returns to live together" inspects the 11th cusp with 11, 7, 6 vs 12, 7, 6;
- Divorce chapters formulate reunion as 1, 5, 7, 11.

These cannot be amalgamated into a generic "7th cusp; 2/7/11 vs 6/12" promise formula. The entry remains fail-closed until disambiguated and verified against published charts.

Next Phase Gate: Valid number, supported topic, user-confirmed outcome scope, complete timestamp and coordinates, matching classical boundaries exactly.

---

## Phase KP-1: Independent Chart Generation

Execution:

```bash
python scripts/build_kp_horary.py \
  --datetime "<YYYY-MM-DD HH:MM[:SS[.ffffff]]|now>" \
  --lat <lat> --lon <lon> --tz "<IANA>" \
  --number <1-249> \
  --topic "<supported-topic>" \
  --outcome-scope "<user-confirmed-supported-scope>" \
  --question "<single observable question>" \
  --label "<kebab-case>" \
  --out-parent "<parent>"
```

Outputs:

```text
kp_horary_<yyyymmdd_HHMMSS>_<label>/
├── structured_kp.md
├── structured_kp.json
└── kp_judgment_<label>.md
```

Do not run `build_prashna_data.py` and do not read `structured_prashna.md`. `structured_kp.md` must display the verbatim question, KP number, and topic to prevent misapplication outside context, along with plain-language outcome scopes. Retain seconds and fractional seconds for the timestamp; never truncate `now` to whole minutes.

Technical baseline:
1. Divide each nakshatra into 9 subs using Vimshottari proportions;
2. Subdivide across sign boundaries, yielding 249 sign/star/sub segments;
3. Set the start of the user's number zone as the Nirayana Ascendant;
4. Convert to tropical Ascendant using Krishnamurti ayanamsa;
5. Compute Placidus cusps for the latitude, subtracting Krishnamurti ayanamsa;
6. Planetary positions calculated for the judgment timestamp; Rahu/Ketu use Mean Node;
7. The 1st cusp placed at the exact zone start is definitional and not subject to boundary sensitivity.

---

## Phase KP-2: Significator Chain

Construct the 4-tier significator hierarchy for every planet:

| Grade | Rule |
|---|---|
| A | Planet in star of house occupant |
| B | Planet occupying the house |
| C | Planet in star of house owner |
| D | Planet owning the house |

Node representation is maintained in Reader VI order:
1. Conjoined planet;
2. Lord of constellation occupied by node;
3. Planet aspecting the node;
4. Lord of sign occupied by node.

Currently items 2 and 4 are deterministically enabled. Items 1 and 3 remain fail-closed to avoid fabricated or arbitrary orbs for Rahu/Ketu until published regressions are closed.

`NODE_AGENT` is an agency source tag, not a fabricated 5th strength grade; its output inherits the represented evidence's A/B/C/D grade.

---

## Phase KP-3: Cusp Sub-Lord Promise

1. Read the judgment cusp for the topic;
2. Identify the sub-lord of that cusp;
3. Identify the constellation lord of that sub-lord;
4. Retrieve the full significator houses of that constellation lord;
5. Apply the `all` / `any` criteria to the positive/negative house groups without relaxing "simultaneously linked" into "hits any";
6. Check the temporary retrograde materialization gate for the cusp sub-lord, constellation lord, and positional sub-lord.

Mechanical states:

| Full Conditions | State |
|---|---|
| Positive fully satisfied, negative not satisfied | `promised_candidate` |
| Positive not satisfied, negative satisfied | `denied_candidate` |
| Both positive and negative conditions fully satisfied | `mixed` |
| Neither positive nor negative conditions satisfied | `unsupported` |

If blocked by a temporary-retrograde gate, retain direction but output `positive_indication_blocked`, `negative_indication_blocked`, or `mixed_with_retrograde_block`; never treat an unmaterialized negative event as a positive promise.

If the operative promise chain passes through Rahu/Ketu via incomplete node agency, output `incomplete_node_agency` rather than asserting promise or denial.

---

## Phase KP-4: Ruling Planets

Identify Ruling Planets in canonical sequence:
1. Asc star lord at judgment time;
2. Asc sign lord;
3. Moon star lord;
4. Moon sign lord;
5. Day lord (sunrise to next sunrise, not civil midnight);
6. Rahu/Ketu representing base RPs via verified agency.

If an RP is situated in the star of a retrograde planet (Mars, Mercury, Jupiter, Venus, Saturn), reject it. Nodes are exempt from this retrograde filter per Reader VI.

---

## Phase KP-5: Boundaries and Timing

Output angular minute distance to nearest:
- sign boundary;
- star boundary;
- sub boundary.

Distances ≤ 5′ are flagged as boundary sensitive (excluding the definitional 1st cusp).

Timing operates strictly when `directional_status` is `positive_only`, temporary-retrograde gates are clear, and operative paths do not traverse incomplete node agency:
1. Calculate Mahadasha balance from Moon's nakshatra traversal;
2. Recursively determine Bhukti / Antara / Shookshma via Vimshottari proportions;
3. Intersect event house significators with accepted Ruling Planets;
4. Search for 4-level period windows where all lords belong to this intersection;
5. Use Moon transit for events within a month, Sun for up to a year, Jupiter for multiple years;
6. Transiting planet must enter sign/star/sub jointly ruled by the Ruling Planets.

Timing states: `candidate`, `blocked_node_agency`, `blocked_temporary_retrograde`, `not_authorized_without_positive_promise`, `no_rp_significator_intersection`, `no_four_level_period_within_horizon`, `period_candidate_without_transit_entry`.

This is KP-exclusive timing. Never borrow standard layer Moon ingress, natal Dasha, or inject it into Parashari sheets.

---

## Phase KP-6: Human-Readable Judgment Sheet

Each execution generates `kp_judgment_<label>.md`, containing:
1. Question, KP number, topic, exact timestamp, and coordinates;
2. A plain-language summary readable without astrology jargon, key support, resistance, and timing authorization;
3. Real-world meaning of positive/negative house linkages followed by technical appendix of cusp, sub-lord, star-lord, and houses;
4. Retrograde and node agency gates;
5. Ruling Planets / period / transit timing status;
6. Clear disclaimer that KP results are not converted into Parashari 3-tier verdicts.

The initial summary section must prioritize clear English explanations without technical jargon; raw codes and tables belong strictly in the technical appendix.
