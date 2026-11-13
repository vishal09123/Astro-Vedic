# Codex Distribution

This directory provides the Codex native distributions for all 8 `vedic-*` skills (including `agents/openai.yaml` metadata).

## Recommended Codex Patch Installation

This directory contains the skill engines. The skills can function independently; to obtain full execution safeguards and routing in Codex, install the patches from `codex-patch/` in the repository root.

```bash
# 1. Install 8 skills
cp -r codex/skills/vedic-* ~/.codex/skills/

# 2. Install codex-patch (recommended)
cp -r codex-patch/vedic_*.md ~/.codex/
# See codex-patch/README.md for instructions on merging AGENTS.md without overwriting existing ~/.codex/AGENTS.md
```

Detailed installation and usage instructions: **`codex-patch/README.md`** (repository root).
