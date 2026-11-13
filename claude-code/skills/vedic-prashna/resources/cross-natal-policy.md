# Cross-Natal Policy (`cross-natal-policy`)

## Status

Cross-natal horary integration is **disabled by default**:

`disabled_pending_source_and_example_rebuild`

Historical approaches that used natal Dasha, SAV, or divisional charts to upgrade or downgrade Prashna verdicts failed to satisfy the requisite empirical controls, source boundaries, and sandboxed regression gates. It is therefore revoked and must not be simulated or invoked.

---

## Active Protocol

When a user requests "judging this horary chart against my natal birth chart":

1. Maintain the independent Prashna horary judgment; do not read any natal files.
2. Inform the user that cross-natal integration is currently disabled to prevent methodological contamination.
3. Do not invoke `build_prashna_data.py --cross-natal` (parameter does not exist).
4. Never modify horary outcomes using natal Dasha, SAV, divisional charts, or transit data.
5. If the user wishes to examine natal life trends, route them to `vedic-core`, keeping the results strictly separate.
