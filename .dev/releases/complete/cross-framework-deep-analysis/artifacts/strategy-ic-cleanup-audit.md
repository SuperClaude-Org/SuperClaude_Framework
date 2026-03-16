---
component: cleanup-audit
framework: IronClaude
phase: 3
generated: 2026-03-14
evidence_source: auggie-mcp
---

# Strategy: IronClaude Cleanup-Audit CLI

## 1. Design Philosophy

The cleanup-audit component exists to produce evidence-backed cleanup recommendations without modifying any repository files. The core design principle is **read-only audit with mandatory evidence** — every DELETE or INVESTIGATE recommendation must be backed by a grep-verified reference count, preventing false positives driven by LLM speculation.

**Why this design exists**: Automated dead code detection and cleanup suggestions are high-risk operations. A false DELETE recommendation on a live file could corrupt a codebase. The three-pass escalation structure (surface scan → structural analysis → cross-cutting comparison) was designed to begin with coarse-grained classification (cheap Haiku agents) and escalate to deeper analysis only where warranted, controlling token and time costs while maintaining evidence quality.

**Trade-off**: The three-pass structure imposes sequential dependencies: Pass 2 requires Pass 1 results; Pass 3 requires Pass 2 outputs. This prevents full parallelism and means a failure in Pass 1 blocks all downstream passes. Benefit: each pass's output is independently reviewable, and the incremental checkpoint design enables resume-from-checkpoint on session interruption.

## 2. Execution Model

Execution is managed by `execute_cleanup_audit(config: CleanupAuditConfig)` (`src/superclaude/cli/cleanup_audit/executor.py:54`), which iterates over steps built by `_build_steps(config)` under supervision of a `SignalHandler` (SIGINT/SIGTERM) and an `OutputMonitor` tracking output byte growth.

**Pipeline structure** (6 discrete steps per audit pass):
- G-001: Surface scan (Haiku agent) — classifies files DELETE/REVIEW/KEEP with grep evidence
- G-002: Structural analysis (Sonnet agent) — produces mandatory 8-field per-file profiles
- G-003: Cross-cutting comparison (Sonnet agent) — duplication matrices with overlap percentages
- G-004: Consolidation — merges pass outputs into unified findings
- G-005: Validation — spot-check sampling (10% of findings, stratified by tier)
- G-006: Report generation

Each step is supervised by `CleanupAuditProcess` (`src/superclaude/cli/cleanup_audit/process.py:22`), which extends `_PipelineClaudeProcess` and writes output to NDJSON files. The `OutputMonitor` detects stalled processes (zero byte growth) and `error_max_turns` signals from the NDJSON stream.

**Classification engine**: `classify_finding()` (`src/superclaude/cli/audit/classification.py:110`) is a pure-Python deterministic function that maps `(has_references, is_test_or_config, is_temporal_artifact)` inputs to a `(V2Tier, V2Action, V1Category, confidence)` result. The two-tier system (Tier-1 actionable: DELETE/INVESTIGATE; Tier-2 informational: KEEP/REORGANIZE) maps deterministically to legacy v1 categories via `TIER_TO_V1_MAP`.

**Dependency graph**: `build_dependency_graph()` (`src/superclaude/cli/audit/dependency_graph.py:198`) constructs a 3-tier graph: Tier-A (AST-resolved imports, confidence 0.95), Tier-B (grep text matching, confidence 0.70), Tier-C (co-occurrence inference, confidence 0.40). Dead code detection (`detect_dead_code()`) then identifies files with zero Tier-A and zero Tier-B importers that are not entry points or framework hooks (`src/superclaude/cli/audit/dead_code.py:108`).

## 3. Quality Enforcement

**Mandatory evidence per finding**: Every agent-produced recommendation must include grep-verified evidence. The audit-validator agent (`src/superclaude/agents/audit-validator.md`) independently re-tests 10% of findings by running grep from scratch, verifying that the primary agent actually read the file and that grep claims match reality.

**Validation sampling**: `_stratified_sample()` (`src/superclaude/cli/audit/spot_check.py:49`) selects proportional samples from each tier with minimum 1 per populated tier, seeded at `42` for reproducibility.

**Conservative bias**: `classify_finding()` defaults to REVIEW rather than DELETE when `has_references=True`. The INVESTIGATE action (confidence 0.60) is used for ambiguous cases. The design explicitly biases toward false negatives (missed deletions) over false positives (incorrect deletes), because the cost of an incorrect DELETE recommendation exceeds the cost of a missed opportunity.

**Trade-off**: The conservative bias means the audit will under-report deletable code in highly inter-referenced codebases, producing REVIEW recommendations that require human judgment. This is intentional but creates noise in large codebases.

## 4. Error Handling Strategy

**Signal handling**: `SignalHandler` installs SIGINT/SIGTERM handlers that set `shutdown_requested = True`. The executor polls this flag between steps and sets outcome to `INTERRUPTED` if set (`src/superclaude/cli/cleanup_audit/executor.py:74`).

**Stall detection**: `OutputMonitor` tracks output byte growth. Zero-growth detection beyond a configurable threshold signals a stalled process, enabling the executor to terminate and report the step as failed.

**Diagnostic collection**: On step failure, `DiagnosticCollector` bundles process state, output artifacts, and error logs into a structured diagnostic bundle (`src/superclaude/cli/cleanup_audit/diagnostics.py`). `FailureClassifier` categorizes the failure (agent error, max-turns, stall, gate failure) for actionable reporting.

**Trade-off**: The diagnostic chain adds overhead on failure paths but is essential for debugging long-running multi-agent pipelines where the root cause of failure may be buried in NDJSON output streams.

## 5. Extension Points

- `--pass surface|structural|cross-cutting|all` — run only selected audit passes; each pass is independently executable (`src/superclaude/cli/cleanup_audit/commands.py:24`).
- `--focus infrastructure|frontend|backend|all` — restricts file scope for each pass.
- `--batch-size N` — controls files-per-agent-invocation; allows tuning for token budget vs. parallelism.
- Pluggable analyzer: `ToolOrchestrator.__init__(analyzer=)` accepts a custom static analysis function, enabling replacement of the default analysis without modifying the orchestrator.
- `permissionMode: plan` on `audit-validator` enforces read-only constraint on the validation agent, preventing accidental modifications during spot-checking.

## 6. System Qualities

**Maintainability**: The audit is strictly read-only — no file modification occurs during any pass. This eliminates a class of bugs where an audit tool accidentally modifies what it is auditing. The 6-step pipeline is discrete; each step writes to a named output file reviewable independently.

**Weakness**: The three-pass structure has implicit data dependencies (Pass 2 reads Pass 1 output paths). These dependencies are not formally declared in a dependency graph — they are encoded in the prompt builders. A step reordering would not be detected by the executor.

**Checkpoint Reliability**: Incremental step writes and the `OutputMonitor` provide byte-level visibility into step progress. The `--pass` flag allows re-running a specific failed pass without repeating earlier passes. However, there is no formal state file equivalent to `.roadmap-state.json`; resume relies on the user correctly specifying `--pass` to restart from the right point.

**Extensibility**: Three audit passes are modular and can run independently. The classification engine (`classify_finding`) is a pure function with no side effects, making it testable and substitutable without executor changes.

**Weakness**: The classification function's decision tree is hard-coded with fixed confidence values (0.90 for DELETE, 0.95 for KEEP test/config, etc.). Calibrating these thresholds for different codebase types requires modifying the source file.

**Operational Determinism**: `classify_finding()` is deterministic — same inputs always produce same output. The stratified sampler uses `seed=42` by default, making spot-check sample selection reproducible. `build_dependency_graph()` produces a deterministic graph for a given set of file analyses.

**Weakness**: The LLM-driven passes (G-001 surface scan, G-002 structural) are non-deterministic. Two runs against the same codebase may produce different per-file classifications from the Haiku/Sonnet agents, even though the Python-side classification engine is deterministic.
