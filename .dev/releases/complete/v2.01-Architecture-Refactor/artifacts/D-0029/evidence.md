# D-0029 — Evidence: Pseudo-CLI Invocation Conversion

**Task**: T05.03
**Date**: 2026-02-24
**Status**: COMPLETE
**Tier**: STANDARD

## Conversions Performed

### 1. sc-roadmap-protocol/SKILL.md line 113

**Before**: `Invoke \`sc:adversarial-protocol\` directly for multi-spec consolidation:`
**After**: `Invoke Skill \`sc:adversarial-protocol\` for multi-spec consolidation:`
**Glossary Rule**: "Invoke" → Skill tool (D-0027)

### 2. sc-roadmap-protocol/SKILL.md line 157

**Before**: `Invoke \`sc:adversarial-protocol\` directly via Skill tool:`
**After**: `Invoke Skill \`sc:adversarial-protocol\` directly:`
**Glossary Rule**: "Invoke" → Skill tool — moved "Skill" into the verb binding position for consistency with other patterns in the file

### 3. sc-adversarial-protocol/SKILL.md line 1582

**Before**: `Any command can invoke sc:adversarial and consume the return contract:`
**After**: `Any command can invoke Skill sc:adversarial-protocol and consume the return contract:`
**Glossary Rule**: "Invoke" → Skill tool. Also corrected bare `sc:adversarial` to full protocol name `sc:adversarial-protocol`

### 4. sc-adversarial-protocol/SKILL.md line 1583

**Before**: `1. Call sc:adversarial with appropriate flags`
**After**: `1. Invoke Skill sc:adversarial-protocol with appropriate flags`
**Glossary Rule**: "Call" → "Invoke Skill" (standardized verb). Also corrected bare `sc:adversarial` to full protocol name

## Patterns NOT Converted (Intentionally Retained)

| Pattern | Location | Reason |
|---------|----------|--------|
| "Do NOT invoke this skill directly" | 4 SKILL.md files (lines 17-27) | User-facing warning, not an invocation instruction |
| `dispatch:` YAML config blocks | sc-adversarial-protocol (multiple) | Structured config, not prose invocation |
| "When invoked by another command" | sc-adversarial-protocol line 341 | Passive voice describing being called, not calling |
| "Dynamic Loading: Load tools only when needed" | sc-pm-protocol line 164 | Design principle, not invocation instruction |
| "Load Test Specifications" (section heading) | sc-validate-tests-protocol line 68 | Section header, not invocation instruction |

## Validation

**Grep check**: `grep -rn "Invoke sc:" src/superclaude/skills/` — **zero matches** (bare "Invoke sc:" without tool binding)

**Remaining "invoke" patterns**: All either include explicit Skill tool binding or are user-facing warnings ("Do NOT invoke this skill directly")

## Files Modified

1. `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` — 2 conversions (lines 113, 157)
2. `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` — 2 conversions (lines 1582, 1583)

## No Behavioral Change

All conversions are invocation clarity improvements only. No pipeline logic, routing, or behavioral semantics were changed. The conversions make explicit what was previously implicit — the Skill tool is the mechanism for all skill invocations.

*Artifact produced by T05.03*
