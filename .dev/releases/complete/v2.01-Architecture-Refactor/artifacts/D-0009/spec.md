# D-0009 — Spec: Wave 2 Step 3 Decomposition (3a–3f)

**Task**: T02.03
**Date**: 2026-02-24
**Status**: COMPLETE
**Variant**: SKILL-DIRECT (per D-0001 updated to SKILL-AVAILABLE)

## Sub-Step Decomposition

Located in `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`, Wave 2 Step 3 (lines 154–169):

| Sub-Step | Purpose | Tool Binding | Output |
|----------|---------|-------------|--------|
| 3a | Parse agent specs from `--agents` flag | Read (refs/adversarial-integration.md) | Agent list with model, persona, instruction |
| 3b | Expand model-only agent specs | None (in-context) | Fully-specified variant configurations |
| 3c | Add debate-orchestrator if agent_count >= 3 | None (conditional logic) | Final agent list with optional orchestrator |
| 3d | Invoke sc:adversarial-protocol via Skill tool | Skill (sc:adversarial-protocol) | Structured return contract inline |
| 3e | Consume return contract with error handling | None (in-context parsing) | 3-status routing decision |
| 3f | SKILL-DIRECT primary path designation | None (no-op/abort) | Pipeline outcome |

## Key Design Decisions

- **Variant**: SKILL-DIRECT (Skill tool available per D-0001)
- **Orchestrator threshold**: >= 3 (not >= 5, per D-0006)
- **Convergence routing**: >= 0.6 PASS, >= 0.5 PARTIAL, < 0.5 FAIL
- **Error handling**: Empty/malformed response guard with fallback convergence_score: 0.5

*Artifact produced by T02.03*
