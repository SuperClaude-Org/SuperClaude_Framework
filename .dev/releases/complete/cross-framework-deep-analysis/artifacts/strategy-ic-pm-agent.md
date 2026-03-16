---
component: pm-agent
framework: IronClaude
phase: 3
generated: 2026-03-14
evidence_source: auggie-mcp
---

# Strategy: IronClaude PM Agent

## 1. Design Philosophy

The PM Agent exists to reduce wrong-direction work and post-implementation rework through three orthogonal quality patterns: pre-execution confidence gating, post-implementation evidence validation, and cross-session error learning. The core design decision is to implement these as **importable Python classes** rather than pure Markdown behavioral prompts, enabling testability via pytest fixtures and programmatic integration.

**Why this design exists**: The original SuperClaude skill system placed PM Agent behavior in a Markdown SKILL.md file, requiring full file reads (35K–40K tokens) and relying on Claude to follow the behavioral protocol without verification. The Python implementation (`src/superclaude/pm_agent/`) makes each pattern independently testable, composable via pytest fixtures (`src/superclaude/pytest_plugin.py:1`), and token-efficient (pre-execution check costs 100–200 tokens vs. 5K–50K tokens of incorrect implementation).

**Trade-off**: The Python-based patterns require a pip-installed `superclaude` package, creating a deployment dependency. The Markdown agent definition (`.claude/agents/pm-agent.md`) remains as a complementary layer for Claude Code integration, creating dual representations of the same behavioral protocol that must be kept synchronized.

## 2. Execution Model

The PM Agent operates as a meta-layer above specialist agents, with three distinct trigger paths:

**Path 1 — Pre-execution (ConfidenceChecker)**:
`ConfidenceChecker.assess(context: dict) -> float` (`src/superclaude/pm_agent/confidence.py:42`) runs 5 weighted checks:
1. No duplicate implementations (25%) — `_no_duplicates(context)`
2. Architecture compliance (25%) — `_architecture_compliant(context)`
3. Official documentation verified (20%) — `_has_official_docs(context)`
4. Working OSS implementations referenced (15%) — `_has_oss_reference(context)`
5. Root cause identified (15%) — `_root_cause_identified(context)`

Score thresholds: ≥0.90 → proceed; 0.70–0.89 → present alternatives; <0.70 → stop and ask.

**Path 2 — Post-implementation (SelfCheckProtocol)**:
`SelfCheckProtocol.validate(implementation: dict) -> (bool, list[str])` (`src/superclaude/pm_agent/self_check.py:64`) runs 4 mandatory questions: tests passing with evidence, requirements met, assumptions verified, evidence provided. Additionally detects 7 hallucination red flags including uncertainty language (`probably`, `maybe`, `should work`) and "complete" status with failing tests (`src/superclaude/pm_agent/self_check.py:212`).

**Path 3 — Error learning (ReflexionPattern)**:
`ReflexionPattern.get_solution(error_info) -> Optional[dict]` (`src/superclaude/pm_agent/reflexion.py:76`) performs smart lookup using Mindbase semantic search (primary) or grep-based text search (fallback) against `docs/memory/solutions_learned.jsonl`. Cache hit returns known solution at 0 tokens; cache miss triggers investigation and `record_error()` persists the new solution to dual storage (JSONL + Mindbase).

**Token budget**: `TokenBudgetManager.LIMITS = {simple: 200, medium: 1000, complex: 2500}` — static constants ensuring deterministic allocation (`src/superclaude/pm_agent/token_budget.py:17`).

**Pytest integration**: Auto-loaded via `pyproject.toml` `entry-points.pytest11`. Fixtures (`confidence_checker`, `self_check_protocol`, `reflexion_pattern`, `token_budget`, `pm_context`) are available without explicit import in any test that installs the package (`src/superclaude/pytest_plugin.py:1`).

## 3. Quality Enforcement

**Pre-execution gate**: The 90% confidence threshold enforces that implementation cannot begin until sufficient context has been gathered. Reported ROI: 25–250x token savings (spending 100–200 tokens on confidence check to save 5K–50K tokens of misdirected work).

**Post-implementation anti-hallucination**: The 7 red-flag detection in `SelfCheckProtocol._detect_hallucinations()` specifically targets LLM failure modes: claims without evidence, complete status with failing tests, uncertainty language in descriptions, ignored errors/warnings.

**Error recurrence prevention**: `ReflexionPattern` targets <10% error recurrence rate via solution reuse rate >90%. Cache hits cost 0 tokens and return immediately, making this the lowest-cost quality gate in the system.

**Trade-off**: The `_architecture_compliant()` and `_root_cause_identified()` methods in `ConfidenceChecker` are documented as placeholder implementations (`src/superclaude/pm_agent/confidence.py:162`). They check for specific dict keys (`architecture_check_complete`, etc.) rather than performing actual architectural analysis. This means a caller that sets these keys to `True` without doing real checks can bypass the confidence gate.

## 4. Error Handling Strategy

**STOP-and-ask protocol**: Confidence <0.70 triggers an explicit stop — the pattern is designed to halt work, not to proceed with low confidence. This is enforced behaviorally (via the pm-agent.md agent definition) but not enforced programmatically (the Python class returns a score; the caller decides what to do with it).

**Dual storage fallback**: ReflexionPattern primary storage (Mindbase) failing falls back to grep-based text search on the JSONL file, then to `None` (no solution found). Fallback to `None` triggers investigation, not failure — the pattern degrades gracefully by discovering root cause rather than blocking work.

**Session persistence**: JSONL storage (`docs/memory/solutions_learned.jsonl`) survives session resets. Serena MCP provides additional session memory for the pm-agent.md agent definition layer.

**Trade-off**: JSONL-based error storage is not deduplicated automatically. Over time, the solutions file may accumulate similar entries with different wording. The Mindbase semantic search mitigates this by matching semantically similar errors, but the JSONL file itself grows unboundedly.

## 5. Extension Points

- `ReflexionPattern(memory_dir=)` — configurable storage path per project or per session.
- `TokenBudgetManager(complexity='simple|medium|complex')` — three budget levels for different task complexity.
- `SelfCorrectionEngine(repo_path=)` — configurable repo root for correction context.
- pytest plugin auto-loading via `entry-points.pytest11` — zero-configuration fixture availability after package install.
- Placeholder methods (`_architecture_compliant`, `_root_cause_identified`) in `ConfidenceChecker` are explicitly designed for extension — the docstrings specify what a real implementation should do.

## 6. System Qualities

**Maintainability**: Three orthogonal patterns (confidence, self-check, reflexion) are independently usable. No pattern depends on another's implementation. Each is a single Python class with a clearly scoped responsibility.

**Weakness**: The pm-agent.md agent definition and the Python implementation represent the same behavioral protocol in two different formats. Changes to one do not automatically propagate to the other. A developer could update the Markdown behavioral spec without updating the Python implementation, or vice versa, silently diverging the two.

**Checkpoint Reliability**: Error solutions persist to JSONL and survive session reset. This is the only PM Agent data that crosses session boundaries automatically. ConfidenceChecker and SelfCheckProtocol results are ephemeral — they exist only for the duration of a single session.

**Extensibility**: The three patterns are designed for independent extension. The placeholder methods in ConfidenceChecker identify exactly where real implementation is expected. The pytest plugin auto-loading mechanism enables new fixtures to be added without test file changes.

**Weakness**: The current `assess()` implementation treats `_architecture_compliant()` and similar checks as boolean flags in the context dict. Real architectural compliance checking (e.g., verifying that a proposed solution uses the project's existing tech stack) requires integration with project analysis tools that are not yet implemented.

**Operational Determinism**: `TokenBudgetManager.LIMITS` are static constants — deterministic allocation for a given complexity level. `classify_finding()` in the classification engine is deterministic. However, the Mindbase semantic search used in `get_solution()` may return different matches on different runs if the index has been updated between sessions.
