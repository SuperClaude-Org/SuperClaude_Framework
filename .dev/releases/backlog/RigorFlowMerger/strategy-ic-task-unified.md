---
component: task-unified
framework: IronClaude
phase: 3
generated: 2026-03-14
evidence_source: auggie-mcp
---

# Strategy: IronClaude Task-Unified Tier System

## 1. Design Philosophy

The task-unified tier system exists to apply proportional quality overhead to task execution — STRICT tier for safety-critical changes, LIGHT/EXEMPT for trivial or read-only operations — without requiring users to manually select verification levels for every task. The core design principle is **automatic tier classification with transparent confidence scoring**, allowing users to override but defaulting to the right level of rigor.

**Why this design exists**: Before task-unified, `/sc:task` and `/sc:task-mcp` were separate commands that confused users about which to invoke and when. Merging them into a single `/sc:task` with orthogonal `--compliance` and `--strategy` flags eliminates the decision by automating it. The classification engine provides a confidence score and rationale, making the automation transparent and correctable.

**Trade-off**: Automatic classification introduces false positive risk (over-classifying a trivial change as STRICT, adding unnecessary verification overhead) and false negative risk (under-classifying a security-critical change as LIGHT, skipping required verification). The design explicitly chooses "better false positives than false negatives" — when uncertain, escalate. The skip rate target (< 12% `--skip-compliance` usage) reflects tolerance for false positives.

## 2. Execution Model

Classification is performed at command invocation time, before any tools are called, producing a machine-readable HTML comment header:

```
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: [STRICT|STANDARD|LIGHT|EXEMPT]
CONFIDENCE: [0.00-1.00]
...
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
```

**Classification decision tree** (`.claude/commands/sc/task-unified.md`, `src/superclaude/core/ORCHESTRATOR.md:152`):
1. Check `--compliance` override → use it at 100% confidence
2. Detect compound phrases (e.g., `"quick fix"` → LIGHT; `"fix security"` → STRICT) → apply with +0.15 boost
3. Score all keywords by tier weight (STRICT +0.4, EXEMPT +0.4, LIGHT +0.3, STANDARD +0.2)
4. Apply context boosters (>2 files +0.3 STRICT; security paths +0.4 STRICT; docs paths +0.5 EXEMPT)
5. Resolve conflicts: priority STRICT > EXEMPT > LIGHT > STANDARD
6. If confidence < 0.70, prompt user for confirmation

**Tier keyword tables** (`src/superclaude/skills/sc-tasklist-protocol/rules/tier-classification.md`):
- STRICT: security, authentication, authorization, database, migration, schema, refactor, breaking change, token, session, oauth, jwt
- EXEMPT: explain, search, commit, push, plan, discuss, brainstorm
- LIGHT: typo, comment, whitespace, lint, docstring, formatting, minor
- STANDARD: implement, add, create, update, fix, build, modify, change (default)

**Execution routing by tier**:
- STRICT: activate project (Serena), verify git state, load codebase context (Auggie), make changes, identify all affected files, spawn quality-engineer sub-agent for verification, run comprehensive tests
- STANDARD: load codebase context, check downstream impacts (find_referencing_symbols or grep), make changes, run affected tests
- LIGHT: quick scope check, make changes, quick sanity check
- EXEMPT: execute immediately, no verification overhead

## 3. Quality Enforcement

**Verification routing by tier** (`src/superclaude/skills/sc-tasklist-protocol/rules/tier-classification.md:76`):
- STRICT → quality-engineer sub-agent (3–5K token budget, 60s timeout)
- STANDARD → direct test execution (300–500 tokens, 30s timeout)
- LIGHT → quick sanity check (~100 tokens, 10s)
- EXEMPT → no verification (0 tokens, 0s)

**Critical path override**: Paths matching `auth/`, `security/`, `crypto/`, `models/`, `migrations/` always trigger CRITICAL verification regardless of compliance tier — a path-based safety override that cannot be suppressed by keyword classification.

**Compound phrase overrides** prevent misclassification of common patterns:
- `"quick fix"` → LIGHT (overrides "fix" → STANDARD)
- `"minor auth change"` → STRICT ("auth" security wins over "minor" LIGHT modifier)
- `"fix security"` → STRICT (security always wins)

**Trade-off**: STRICT tier verification requires Sequential MCP and Serena MCP, and explicitly disallows fallback (`MCP Requirements: Required: Sequential, Serena; Fallback Allowed: No`). If these servers are unavailable, a STRICT task cannot proceed. This is a deliberate safety choice — incomplete verification of security-critical changes is more dangerous than blocking the task.

## 4. Error Handling Strategy

**Low-confidence handling**: Classification confidence < 0.70 triggers a user prompt: "Override with `--compliance [tier]`". Execution does not begin until the user confirms or overrides. This prevents silent misclassification of ambiguous tasks.

**STRICT MCP unavailability**: If Sequential or Serena MCP is unavailable for a STRICT task, the task is blocked — not degraded. The error message informs the user which servers are unavailable and that `--skip-compliance` is available as an escape hatch.

**Override tracking**: All `--compliance` overrides are logged for feedback calibration. High override rates for specific keyword patterns indicate classification errors and trigger keyword table adjustments.

**`--skip-compliance` escape hatch**: Available when users need to bypass all compliance enforcement (e.g., exploration, formatting, documentation updates that the classifier incorrectly elevates). Skip rate target < 12% indicates the classification is accurate enough to rarely require bypassing.

**Trade-off**: The escape hatch creates a potential security hole — `--skip-compliance` on a truly STRICT task skips all verification. The design accepts this as a user-choice override with the implicit assumption that a developer who explicitly uses `--skip-compliance` on a security change accepts responsibility for the risk.

## 5. Extension Points

- `--compliance` flag: user can force any tier regardless of auto-classification
- `--force-strict` override: escalate to STRICT without providing rationale
- `--skip-compliance` escape hatch: bypass all compliance
- `--parallel` / `--delegate`: enable parallel sub-agent execution for large STRICT tasks
- Tier keyword tables in `tier-classification.md`: editable YAML-like structures; new keywords and compound phrases can be added without code changes
- Confidence threshold (0.70): not currently user-configurable; hardcoded in the classification algorithm

## 6. System Qualities

**Maintainability**: Orthogonal `--compliance` and `--strategy` dimensions mean that compliance tier (quality) and execution strategy (orchestration) can be changed independently without affecting the other dimension. Keyword tables are in a separate `tier-classification.md` file, editable without modifying the command definition.

**Weakness**: The classification algorithm is documented in multiple places (ORCHESTRATOR.md, task-unified.md, tier-classification.md, SKILL.md). Changes to keyword tables or booster weights must be propagated to all copies, creating synchronization risk between source files and dev copies.

**Checkpoint Reliability**: The classification header is emitted as the first output before any tools are called, making it machine-parseable for telemetry and A/B testing. Confidence scoring is transparent and logged.

**Extensibility**: Tier keyword tables are designed to be extended with new compound phrases or keyword entries. The classification priority ordering (STRICT > EXEMPT > LIGHT > STANDARD) provides a clear conflict resolution rule for new keywords.

**Weakness**: The keyword-scoring approach cannot handle context-dependent semantics. "Update" is STANDARD by default, but "update authentication token expiry" should be STRICT. Only the compound phrase overrides handle multi-keyword interactions; single-keyword scoring misses semantic context.

**Operational Determinism**: Priority ordering STRICT > EXEMPT > LIGHT > STANDARD resolves classification conflicts deterministically. Compound phrase matching is prefix-checked before keyword scoring. The same task description produces the same tier classification on every invocation.

**Weakness**: Confidence scores are computed from keyword matches and context boosters, not from semantic understanding of the task. A task with high keyword matches but actually trivial impact will receive high confidence in an elevated tier, creating over-classification that the user must manually override.
