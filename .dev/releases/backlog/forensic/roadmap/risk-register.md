---
feature: /sc:forensic + sc:forensic-protocol
risk_register_version: 1.0.0
date: 2026-02-26
classification: implementation risks
---

# Risk Register — /sc:forensic Implementation

This register identifies risks to the successful implementation of the `/sc:forensic` command and `sc:forensic-protocol` skill. Risks are rated by probability (1-5), impact (1-5), and assigned a mitigation strategy.

**Rating key**: Probability × Impact = Exposure score. Exposure >= 15: High. 8-14: Medium. 1-7: Low.

---

## Risk Catalog

### R-01: /sc:adversarial Protocol Integration Failures

**Category**: External dependency
**Probability**: 3 (possible — adversarial command exists but integration with forensic-specific schemas is untested)
**Impact**: 5 (blocks Phases 2 and 3b, making the core validation pipeline non-functional)
**Exposure**: 15 — HIGH

**Description**: The `/sc:forensic` pipeline delegates hypothesis validation (Phase 2) and fix validation (Phase 3b) to the existing `/sc:adversarial` command. Integration risks include: the adversarial command does not accept the expected `--compare` flags for the large number of finding files, the output artifact paths diverge from expected locations, or the adversarial 5-step pipeline returns non-standard output that the forensic orchestrator cannot parse.

**Mitigation**:
- M6 requires that `/sc:adversarial` is verified operational before Phase 2/3b integration tests run
- The three-level fallback chain (P-011, M1-T6) provides degradation paths that bypass adversarial failures at runtime: retry with `--depth quick`, then Sonnet scoring agent, then direct passthrough
- E2E test T-M9-6 includes a test for adversarial failure → fallback chain execution
- Build the Phase 2/3b invocation patterns as parameterized templates so the command string can be adjusted without protocol changes if adversarial command interface changes

**Residual risk after mitigation**: Medium (fallback chain protects runtime; interface mismatch still blocks full functionality)

---

### R-02: Model Tier Unavailability (Haiku/Sonnet/Opus)

**Category**: Runtime environment
**Probability**: 2 (unlikely in normal usage but possible during account limits or API changes)
**Impact**: 4 (degrades pipeline quality; Opus unavailability breaks orchestrator and adversarial coordination)
**Exposure**: 8 — MEDIUM

**Description**: The pipeline has strict model tier assignments (Haiku for recon, Sonnet for analysis, Opus for orchestration and adversarial debate). Claude Code does not currently expose which model is used by Task sub-agents, meaning tier assignment is "best-effort" prompt hinting. If a higher tier is unavailable (e.g., Opus capacity limits during peak hours), the orchestrator and adversarial debate agents fall back to an unspecified lower tier.

**Mitigation**:
- P-013 (M0-T5) adds `requested_tier` and `actual_tier` tracking with `tier_source: "best-effort"` to make this visible
- The final report includes a "Model Tier Compliance" section so users can see when tier assignments were not honored
- Prompt hinting strategies (persona-based model preference language) are the current best-available enforcement mechanism
- Document in SKILL.md that tier assignment is best-effort and the system degrades gracefully

**Residual risk after mitigation**: Low (observability is added; actual enforcement is runtime-dependent)

---

### R-03: Token Budget Overruns in Orchestrator Phases

**Category**: Resource management
**Probability**: 4 (likely for large codebases with many domains or hypotheses)
**Impact**: 3 (degrades final report completeness; may cause orchestrator to miss critical information)
**Exposure**: 12 — MEDIUM

**Description**: The orchestrator token budget is strictly capped (~8,000 tokens total across all phases). For large codebases that generate 10 domains, many surviving hypotheses, and complex fix proposals, the orchestrator synthesis phases (particularly Phase 6 at 2,000-3,000 tokens) may hit overflow conditions. The overflow actions (truncate descriptions, omit rejected-hypotheses section) reduce information but prevent failure.

**Mitigation**:
- P-012 (M1-T7) establishes the per-phase overflow policy table with soft targets, hard stops, and deterministic truncation actions — prevents undefined overflow behavior
- `budget_status` field in `progress.json` makes token budget state observable
- Phase 6 overflow action (omit rejected-hypotheses) drops the least-critical section first
- Advise users targeting large codebases to use `--depth quick` to reduce adversarial debate token costs
- NFR-001 (90% token reduction from original) is realistic for small-to-medium codebases; for very large codebases (51+ files, 10 domains), the orchestrator may still approach its limit

**Residual risk after mitigation**: Low (overflow actions are deterministic and non-failing)

---

### R-04: MCP Server Unavailability (Serena, Context7, Sequential)

**Category**: Runtime environment
**Probability**: 2 (occasional; servers can be unavailable or timeout)
**Impact**: 3 (degrades agent capability; Serena unavailability forces fallback from symbol-level edits to whole-file edits)
**Exposure**: 6 — LOW

**Description**: Several pipeline phases depend on MCP servers: Phase 1 agents use Serena for symbol lookup and Context7 for framework patterns; Phase 4a uses Serena `replace_symbol_body` for surgical edits. If Serena is unavailable, the fallback is the Edit tool (whole-function replacement rather than symbol-level). If Context7 is unavailable, the fallback is WebSearch for documentation.

**Mitigation**:
- P-014 (M0-T7) adds MCP activation precondition to all agent templates with explicit fallback chain: Serena → Edit tool, Context7 → WebSearch/WebFetch
- The fallback tools are verified to be in the `allowed-tools` contract
- Agents are instructed to fall back gracefully rather than fail if MCP tools are unavailable
- The `--no-mcp` flag (from CLAUDE.md FLAGS.md) can be passed to force native-tool-only execution if MCP reliability is a concern

**Residual risk after mitigation**: Low (fallback chain is defined and contractually valid)

---

### R-05: Non-Deterministic Phase 0 Domain Discovery

**Category**: Correctness
**Probability**: 3 (possible; LLM outputs are inherently non-deterministic)
**Impact**: 4 (domain definition drives all downstream work; different domains across runs produce incomparable results)
**Exposure**: 12 — MEDIUM

**Description**: Phase 0 generates investigation domains by having the Opus orchestrator read 3 JSON summaries. The domain generation is an LLM synthesis step that may produce different domain boundaries, names, or counts on different runs. This creates two problems: (1) resuming after Phase 0 requires stable domain IDs, and (2) comparing results across runs is difficult if domains change.

**Mitigation**:
- P-009 (M0-T3) addresses the ID stability problem: domain IDs are hash-based on `(domain_name, sorted(files_in_scope))`, not position-based. Even if domain names shift slightly between runs, the domain's file scope determines its ID.
- The checkpoint protocol persists `investigation-domains.json` so resume operations reuse the original Phase 0 output
- The domain count heuristic (M0-T6) bounds the range to prevent extreme variability
- `--focus` hints anchor some domains, reducing variability for the most critical investigation areas
- Document in SKILL.md that domain generation is an LLM synthesis step and results may vary across fresh runs (but are stable within a single run session via checkpoint)

**Residual risk after mitigation**: Medium (hash-based IDs solve the resume problem; domain content variability across fresh runs is acceptable and documented)

---

### R-06: Adversarial Protocol Convergence Failure

**Category**: Quality
**Probability**: 2 (rare; convergence threshold is tunable)
**Impact**: 3 (Phase 2 or Phase 3b cannot produce a ranked output; pipeline must fall back)
**Exposure**: 6 — LOW

**Description**: The adversarial debate protocol has a convergence threshold (default 0.80). If debate rounds do not reach convergence within the configured depth, the adversarial command may produce an inconclusive output. This is more likely with contradictory hypotheses or fix proposals where genuine expert disagreement exists.

**Mitigation**:
- The three-level fallback chain (P-011, M1-T6) handles adversarial failures explicitly
- The `--convergence` threshold passed to adversarial invocations is configurable
- `--depth` controls the number of debate rounds; `--depth deep` allows more rounds to reach convergence
- If convergence fails at all three levels, the direct passthrough (Level 3) preserves pipeline forward progress

**Residual risk after mitigation**: Low (fallback chain handles this case)

---

### R-07: Worktree Isolation Failures in Phase 4

**Category**: Correctness
**Probability**: 3 (possible when multiple implementation agents run in parallel)
**Impact**: 4 (file-level conflicts between Agent 4a and Agent 4b can corrupt the working tree)
**Exposure**: 12 — MEDIUM

**Description**: Phase 4 runs Agent 4a (code fix specialist) and Agent 4b (regression test creator) in parallel. Without worktree isolation, both agents write to the same working directory simultaneously. Agent 4a edits source files; Agent 4b writes new test files. File conflict risk is low (different directories) but not zero, especially if test files reference source files being modified.

**Mitigation**:
- NFR-008 recommends (SHOULD) git worktree isolation for Phase 4 parallel execution
- T-M7-2 documents worktree isolation as a recommended pattern in the agent prompt template
- In practice, Agent 4a and 4b work in different directories (source files vs test files), minimizing actual conflict
- If worktree isolation is not available, the pipeline can run Agent 4a and 4b sequentially at the cost of parallel performance
- The `changes-manifest.json` and `new-tests-manifest.json` provide an explicit record of all touched files for post-execution conflict detection

**Residual risk after mitigation**: Low (NFR-008 SHOULD is appropriate; hard MUST would be over-constraining)

---

### R-08: Resume Safety — Stale Target Detection Gaps

**Category**: Resume correctness
**Probability**: 3 (possible; users commonly modify code between pipeline runs)
**Impact**: 3 (stale artifacts produce misleading results; hypotheses from original run may not apply to modified code)
**Exposure**: 9 — MEDIUM

**Description**: The resume protocol reads artifacts from a previous run (possibly hours or days earlier) and continues from the last checkpoint. If the target codebase was modified between the original run and the resume, Phase 1 findings (which analyzed the original code) may describe bugs that no longer exist, or miss new bugs introduced in the interim.

**Mitigation**:
- P-008 (M1-T13) adds `target_paths` (required) and `git_head_or_snapshot` (optional) to `progress.json` for stale-target detection
- Resume validation step 3 (M3-T2) compares current target paths against persisted paths; warns on divergence
- Resume validation step 4 compares current git HEAD against `git_head_or_snapshot`; warns if different
- Warnings are non-blocking (user can proceed) but explicit: "Warning: target codebase has changed since original run. Results may not reflect current state."
- Users should run fresh (not resume) after significant code changes

**Residual risk after mitigation**: Medium (warnings are emitted; stale-result risk cannot be fully eliminated without mandatory re-execution)

---

### R-09: Spec Amendment Integration Complexity

**Category**: Process
**Probability**: 3 (likely; 22 proposals touching many sections of a 1700+ line spec)
**Impact**: 3 (incomplete or incorrect amendments produce a divergent spec that implementers cannot follow)
**Exposure**: 9 — MEDIUM

**Description**: M0 and M1 require integrating 22 proposals into the forensic-spec.md. P-001 (the Section 17 normativity integration) must be done first and mechanically (verbatim copy) to avoid introducing new inconsistencies. Subsequent proposals touch overlapping sections (e.g., schemas Section 9 is modified by P-006, P-007, P-009, P-010, P-021). The cross-proposal interaction risks introducing contradictions or numbering collisions.

**Mitigation**:
- The spec amendment checklist (`spec-amendments-checklist.md`) orders all 22 proposals by implementation priority and documents exactly which sections each proposal touches
- P-001 is executed first and independently (verbatim move, no paraphrasing) to establish the true baseline
- Each subsequent proposal references specific section numbers to update, reducing ambiguity
- After all amendments are applied, a cross-reference review verifies that every FR, schema, and section reference is consistent
- The implementation priority tiers in the verdicts file define a safe execution order that minimizes cross-proposal interference

**Residual risk after mitigation**: Low (the checklist and ordering reduce integration complexity to a linear process)

---

### R-10: Test Infrastructure for Mock Agent Framework

**Category**: Testing
**Probability**: 3 (moderate; mock LLM agent infrastructure is non-trivial to build)
**Impact**: 3 (without good mocks, E2E tests are slow, expensive, or impossible to run in CI)
**Exposure**: 9 — MEDIUM

**Description**: The E2E tests in M9 require simulating the behavior of 12+ distinct sub-agents across 7 phases without making real LLM API calls. Building a mock agent framework that produces schema-conforming output for all 9 artifact types is significant infrastructure work. If mocks are incomplete or produce invalid artifacts, test coverage is unreliable.

**Mitigation**:
- Use the existing pytest plugin infrastructure (`src/superclaude/pytest_plugin.py`) as the base for test fixtures
- Create `tests/forensic/fixtures/` with pre-built sample artifacts for each schema (valid and invalid variants)
- Use mock Task agents that read from fixture files rather than spawning real sub-agents
- Leverage the schema definitions in `schemas.md` to generate test fixtures programmatically
- Prioritize unit tests (individual schema validation, checkpoint logic, phase transition logic) over full E2E tests where mock complexity is high
- Accept that some E2E scenarios may require a real `/sc:adversarial` invocation (document this as an integration test requiring a connected environment)

**Residual risk after mitigation**: Medium (mock framework complexity is real; mitigated by phasing unit tests before E2E tests)

---

## Risk Summary Matrix

| ID | Risk | Probability | Impact | Exposure | Priority |
|----|------|-------------|--------|----------|----------|
| R-01 | Adversarial integration failures | 3 | 5 | 15 | HIGH |
| R-02 | Model tier unavailability | 2 | 4 | 8 | MEDIUM |
| R-03 | Orchestrator token overruns | 4 | 3 | 12 | MEDIUM |
| R-04 | MCP server unavailability | 2 | 3 | 6 | LOW |
| R-05 | Non-deterministic domain discovery | 3 | 4 | 12 | MEDIUM |
| R-06 | Adversarial convergence failure | 2 | 3 | 6 | LOW |
| R-07 | Phase 4 worktree conflicts | 3 | 4 | 12 | MEDIUM |
| R-08 | Resume stale-target gaps | 3 | 3 | 9 | MEDIUM |
| R-09 | Spec amendment integration complexity | 3 | 3 | 9 | MEDIUM |
| R-10 | Mock agent test infrastructure | 3 | 3 | 9 | MEDIUM |

---

## Risk Response Plan

**R-01 (HIGH — adversarial integration)**: Validate `/sc:adversarial` is fully operational in a pre-M6 check. Build a minimal integration smoke-test in M6 before implementing the full protocol. If integration cannot be validated, implement the three-level fallback chain (M1-T6) first so the pipeline can function without adversarial debate.

**R-03 (MEDIUM — token overruns)**: Implement token budget overflow policy (M1-T7) before any phase-specific content. Add a `--verbose-orchestrator` flag (not in spec, to be evaluated) that lifts soft targets if users explicitly accept higher token costs for richer output.

**R-05 (MEDIUM — domain non-determinism)**: The hash-based domain ID (M0-T3) is the primary mitigation. Additionally, checkpoint Phase 0 output before any subsequent phase reads it, so resume always reuses the original domain generation even if re-run would produce different domains.

**R-09 (MEDIUM — spec amendments)**: Execute M0 and M1 as sequential, reviewable steps with the spec-amendments-checklist.md as a tracking document. Review the amended spec after each tier of amendments is complete before proceeding to the next tier.

**R-10 (MEDIUM — test infrastructure)**: Start building fixture files during M2 (alongside schema definitions) so they are available for use in M3-M8 tests. Do not wait until M9 to invest in test infrastructure.
