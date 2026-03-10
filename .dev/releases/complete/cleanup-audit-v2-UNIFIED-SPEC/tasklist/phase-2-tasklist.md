# Phase 2 -- Profile and Batch Infrastructure

Build robust Phase-0 profiling and manifest generation as the substrate for all subsequent analysis phases. This phase implements domain/risk-tier profiling, monorepo-aware batch decomposition, and dry-run estimation (M3).

---

### T02.01 -- Implement domain and risk-tier profiling for repository file sets

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | AC13 requires automated domain/risk-tier profiling to drive batch planning and analysis depth decisions. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | audit, system-wide |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0011/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0011/evidence.md

**Deliverables:**
- Profiler that classifies repository files by domain (frontend, backend, infra, docs, test) and assigns risk tiers based on path patterns and file characteristics

**Steps:**
1. **[PLANNING]** Define domain classification rules: path patterns (src/api -> backend, src/components -> frontend, docs/ -> docs, tests/ -> test, infra/ -> infra)
2. **[PLANNING]** Define risk-tier assignment rules: security paths -> high, config files -> medium, docs -> low
3. **[EXECUTION]** Implement domain classifier using path-pattern matching with configurable rules
4. **[EXECUTION]** Implement risk-tier assigner that combines path patterns with file characteristics (size, age, import count)
5. **[EXECUTION]** Output profile as structured JSON with domain, risk_tier, and confidence per file
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to validate profiling determinism and coverage
7. **[COMPLETION]** Document profiling rules in D-0011/spec.md

**Acceptance Criteria:**
- Every file in the repository receives exactly one domain label and one risk tier, verified by checking output has no null fields
- Profiling is deterministic: same repository state produces identical profile output across runs
- Profile output matches AC13 schema with domain, risk_tier, and confidence fields
- Profiling rules documented in D-0011/spec.md with examples per domain

**Validation:**
- Manual check: profile a test repository with known domain distribution; verify domain assignments match expectations
- Evidence: D-0011/evidence.md contains profile output for test repository

**Dependencies:** T01.01, T01.08
**Rollback:** TBD
**Notes:** Mis-tiering cascades downstream; conservative defaults applied per roadmap risk mitigation.

---

### T02.02 -- Implement monorepo-aware batch decomposition with segment isolation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | AC20 (supporting) requires batch decomposition that respects monorepo segment boundaries for isolated analysis. |
| Effort | L |
| Risk | High |
| Risk Drivers | system-wide, multi-tenant, performance |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0012/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0012/evidence.md

**Deliverables:**
- Batch decomposer that detects monorepo segments (packages/, apps/, services/) and creates isolated batches per segment with configurable batch size limits

**Steps:**
1. **[PLANNING]** Define monorepo segment detection: look for package.json/Cargo.toml/go.mod at directory roots, workspace config patterns
2. **[PLANNING]** Define batch sizing rules: max files per batch, segment isolation (no cross-segment batches)
3. **[EXECUTION]** Implement segment detector that identifies monorepo boundaries from workspace configuration files
4. **[EXECUTION]** Implement batch decomposer that splits files into segment-isolated batches respecting size limits
5. **[EXECUTION]** Add manifest output: list of batches with segment, file count, estimated token cost
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify no cross-segment contamination and batch size compliance
7. **[COMPLETION]** Document decomposition rules and manifest format in D-0012/spec.md

**Acceptance Criteria:**
- Batches never contain files from different monorepo segments, verified by checking segment field consistency within each batch
- Batch sizes do not exceed configured maximum, verified by count check
- Monorepo detection correctly identifies segment boundaries in a multi-package test fixture
- Decomposition rules and manifest format documented in D-0012/spec.md

**Validation:**
- Manual check: decompose a 3-package monorepo fixture; verify 3 isolated batch groups with correct file assignments
- Evidence: D-0012/evidence.md contains decomposition manifest for test fixture

**Dependencies:** T02.01
**Rollback:** TBD

---

### T02.03 -- Implement static-tool orchestration layer with result caching

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | AC12 (supporting) requires static-tool results as evidence inputs; orchestration and caching prevent redundant invocations. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | performance, cache |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0013/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0013/evidence.md

**Deliverables:**
- Orchestration layer that invokes static analysis tools (grep, AST parsers, import resolvers) per batch and caches results keyed by file content hash

**Steps:**
1. **[PLANNING]** Identify static tools to orchestrate: grep for pattern search, AST parsing for import/export analysis, file-stat for metadata
2. **[PLANNING]** Define caching strategy: content-hash keyed cache with TTL, invalidation on file change
3. **[EXECUTION]** Implement tool orchestrator that dispatches static tool invocations per batch with parallel execution
4. **[EXECUTION]** Implement content-hash cache that stores and retrieves tool results, skipping re-invocation for unchanged files
5. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify cache hit/miss behavior and result correctness
6. **[COMPLETION]** Document orchestration pipeline and caching strategy in D-0013/spec.md

**Acceptance Criteria:**
- Static tools are invoked once per unique file content; repeated runs with unchanged files show cache hits, verified by cache hit counter
- Orchestration produces structured results per file (imports, exports, references, metadata) matching expected schema
- Cache invalidation correctly triggers re-invocation when file content changes, verified by modifying a test file and re-running
- Orchestration pipeline documented in D-0013/spec.md

**Validation:**
- Manual check: run orchestration twice on same files; verify second run shows 100% cache hits
- Evidence: D-0013/evidence.md contains cache hit/miss statistics

**Dependencies:** T02.01
**Rollback:** TBD

---

### T02.04 -- Implement auto-config generation for cold-start repository audits

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | AC13 requires that cold-start runs (no pre-existing config) generate a usable configuration automatically from repository profiling. |
| Effort | S |
| Risk | Low |
| Risk Drivers | (none matched) |
| Tier | STANDARD |
| Confidence | [███████░░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0014/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0014/evidence.md

**Deliverables:**
- Auto-config generator that produces a default audit configuration from profiling output when no user config exists

**Steps:**
1. **[PLANNING]** Define default config template: batch size, analysis depth, report mode, budget limits based on repository size
2. **[PLANNING]** Define cold-start detection: check for absence of `.cleanup-audit.json` or equivalent config file
3. **[EXECUTION]** Implement config generator that uses profiling output (T02.01) to populate default values
4. **[EXECUTION]** Write generated config to standard location and log config generation event
5. **[VERIFICATION]** Run audit on a repository with no config file; verify config is generated and audit completes
6. **[COMPLETION]** Document auto-config rules in D-0014/spec.md

**Acceptance Criteria:**
- Cold-start run with no pre-existing config file generates a valid configuration, verified by successful audit completion
- Generated config contains all required fields (batch_size, depth, report_mode, budget) with values derived from profiling
- Config generation is logged with the generated values for transparency
- Auto-config rules documented in D-0014/spec.md

**Validation:**
- Manual check: run audit on a clean test repo with no config; verify config file generated and audit completes
- Evidence: D-0014/evidence.md contains generated config and audit completion log

**Dependencies:** T02.01
**Rollback:** TBD

---

### T02.05 -- Implement dry-run mode that outputs profile and token estimates without executing audit

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | AC19 requires a dry-run mode that returns estimates only, enabling operators to assess cost before committing to a full run. |
| Effort | S |
| Risk | Low |
| Risk Drivers | (none matched) |
| Tier | STANDARD |
| Confidence | [███████░░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0015/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0015/evidence.md

**Deliverables:**
- Dry-run executor that runs profiling and batch planning but stops before analysis, outputting estimated token cost, batch count, and expected runtime

**Steps:**
1. **[PLANNING]** Define dry-run output schema: file_count, batch_count, estimated_tokens, estimated_runtime, domain_distribution
2. **[PLANNING]** Identify the pipeline cutoff point: after profiling and batch planning, before analysis execution
3. **[EXECUTION]** Implement `--dry-run` flag handler that executes profiling + batch planning only
4. **[EXECUTION]** Implement estimate calculator that computes token cost from batch count and average batch complexity
5. **[VERIFICATION]** Run dry-run on a test repository; verify no analysis artifacts are produced and estimates are output
6. **[COMPLETION]** Document dry-run output format in D-0015/spec.md

**Acceptance Criteria:**
- Dry-run mode produces estimates without executing analysis phases, verified by absence of classification output
- Estimate output includes file_count, batch_count, estimated_tokens, and domain_distribution fields
- Dry-run completes in under 10% of full audit runtime (profiling only, no analysis)
- Dry-run output format documented in D-0015/spec.md

**Validation:**
- Manual check: run `--dry-run` on test repo; verify estimate output and no analysis artifacts
- Evidence: D-0015/evidence.md contains dry-run output

**Dependencies:** T02.01, T02.02
**Rollback:** TBD

---

### Checkpoint: Phase 2 / Tasks T02.01-T02.05

**Purpose:** Validate that profiling infrastructure, batch decomposition, caching, and dry-run estimation are functional before structural depth implementation.
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/CP-P02-T01-T05.md
**Verification:**
- Domain/risk-tier profiling produces deterministic output for test fixtures
- Monorepo batch decomposition maintains segment isolation
- Dry-run mode outputs estimates without producing analysis artifacts
**Exit Criteria:**
- Tasks T02.01-T02.05 completed with passing verification
- No STRICT-tier task has unresolved sub-agent findings
- Profiling and batch infrastructure tested with monorepo and single-repo fixtures

---

### T02.06 -- Implement manifest completeness gate that blocks analysis if profiling coverage is insufficient

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | AC2 (quality extension) requires a gate ensuring profiling covers all repository files before analysis begins. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | audit, compliance |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0016/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0016/evidence.md

**Deliverables:**
- Manifest completeness gate that compares profiled file count against total repository file count and blocks analysis if coverage is below threshold (default: 95%)

**Steps:**
1. **[PLANNING]** Define completeness threshold: 95% of tracked files must be profiled before analysis proceeds
2. **[PLANNING]** Identify files that should be excluded from completeness check (binary files, vendor directories)
3. **[EXECUTION]** Implement manifest gate that counts profiled files vs total eligible files and computes coverage percentage
4. **[EXECUTION]** Implement gate enforcement: block analysis start if coverage < threshold; log missing files
5. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify gate blocks correctly at below-threshold and passes at above-threshold
6. **[COMPLETION]** Document gate rules and threshold in D-0016/spec.md

**Acceptance Criteria:**
- Gate blocks analysis when profiling coverage is below 95%, verified by test with 90% coverage fixture
- Gate passes analysis when profiling coverage is at or above 95%, verified by test with 100% coverage fixture
- Missing files are logged when gate blocks, enabling diagnosis
- Gate rules and threshold documented in D-0016/spec.md

**Validation:**
- Manual check: run gate with 90% profiled fixture; verify block and missing file log
- Evidence: D-0016/evidence.md contains gate pass/block test results

**Dependencies:** T02.01, T02.02
**Rollback:** TBD

---

### Checkpoint: End of Phase 2

**Purpose:** Gate for Phase 3 entry. All M3 profiling and batch infrastructure deliverables must be complete.
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/CP-P02-END.md
**Verification:**
- All 6 tasks (T02.01-T02.06) completed with passing verification
- Manifest completeness gate blocks at below-threshold and passes at above-threshold
- Static-tool caching demonstrates correct hit/miss behavior
**Exit Criteria:**
- Evidence artifacts exist for D-0011 through D-0016
- No STRICT-tier task has unresolved quality-engineer findings
- Auto-config cold-start and dry-run tested on independent test fixtures
