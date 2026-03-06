# Phase 5 -- Extensions and Final Acceptance

Add opt-in depth for documentation quality and cross-run suppression workflows (M9), then validate the full v2 contract against AC1-AC20 with benchmark repos (M10). This is the final phase gating release readiness.

---

### T05.01 -- Implement full docs audit pass with 5-section output via --pass-docs flag

| Field | Value |
|---|---|
| Roadmap Item IDs | R-040 |
| Why | AC14 (extended) requires an opt-in full documentation audit that produces 5 sections: broken refs, staleness, coverage gaps, orphaned docs, and style inconsistencies. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | across, system-wide |
| Tier | STANDARD |
| Confidence | [███████░░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0040 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0040/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0040/evidence.md

**Deliverables:**
- Full docs audit pass activated by `--pass-docs` flag that produces 5-section output: (1) broken references, (2) temporal staleness, (3) coverage gaps, (4) orphaned docs, (5) style inconsistencies

**Steps:**
1. **[PLANNING]** Define 5 sections: broken refs (extends T03.09), staleness (extends T03.09), coverage gaps (docs for undocumented exports), orphaned docs (docs with no code referent), style inconsistencies (heading format, link conventions)
2. **[PLANNING]** Define `--pass-docs` flag handler that activates full docs pass
3. **[EXECUTION]** Implement coverage gap detector: find exported symbols without corresponding documentation
4. **[EXECUTION]** Implement orphaned docs detector: find doc files with no code referent
5. **[EXECUTION]** Implement style inconsistency checker: heading hierarchy, link format, code block conventions
6. **[VERIFICATION]** Run full docs pass on test fixture with known issues in all 5 categories; verify all detected
7. **[COMPLETION]** Document 5-section output format in D-0040/spec.md

**Acceptance Criteria:**
- `--pass-docs` flag activates full docs audit producing all 5 sections, verified by output section count
- Coverage gaps section identifies exported symbols without documentation, verified by test fixture
- Orphaned docs section identifies doc files with no corresponding code, verified by test fixture
- 5-section output format documented in D-0040/spec.md

**Validation:**
- Manual check: run `--pass-docs` on fixture with known issues in each category; verify 5-section output
- Evidence: D-0040/evidence.md contains 5-section output sample

**Dependencies:** T03.09
**Rollback:** TBD

---

### T05.02 -- Implement known-issues registry with load, match, and output functionality

| Field | Value |
|---|---|
| Roadmap Item IDs | R-041 |
| Why | AC20 (supporting) requires a registry of known issues that suppresses repeated findings across audit runs. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data, schema |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0041 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0041/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0041/evidence.md

**Deliverables:**
- Known-issues registry that loads a persistent JSON registry, matches current findings against registered patterns, and suppresses matched findings with ALREADY_TRACKED status

**Steps:**
1. **[PLANNING]** Define registry schema: issue_id, pattern (file path glob + classification), created_date, last_matched, ttl_days
2. **[PLANNING]** Define matching algorithm: glob pattern match on file path + classification type
3. **[EXECUTION]** Implement registry loader that reads persistent JSON registry file
4. **[EXECUTION]** Implement matcher that compares current findings against registry entries and marks matches as ALREADY_TRACKED
5. **[EXECUTION]** Implement registry updater that timestamps last_matched for matched entries
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify matching accuracy and suppression behavior
7. **[COMPLETION]** Document registry schema and matching algorithm in D-0041/spec.md

**Acceptance Criteria:**
- Registered patterns suppress matching findings with ALREADY_TRACKED status, verified by test
- Registry file is updated with last_matched timestamp for matched entries, verified by file inspection
- Non-matching findings are not suppressed, verified by test with non-matching fixture
- Registry schema and matching algorithm documented in D-0041/spec.md

**Validation:**
- Manual check: register a pattern, run audit with matching finding; verify suppression
- Evidence: D-0041/evidence.md contains registry match test log

**Dependencies:** T04.01
**Rollback:** TBD

---

### T05.03 -- Implement TTL and LRU lifecycle rules for known-issues registry entries

| Field | Value |
|---|---|
| Roadmap Item IDs | R-042 |
| Why | AC20 (supporting) requires that registry entries expire after a configurable TTL and LRU eviction prevents unbounded registry growth. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data, schema |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0042 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0042/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0042/evidence.md

**Deliverables:**
- Lifecycle manager that expires registry entries exceeding TTL (default: 90 days), evicts least-recently-matched entries when registry exceeds max size (default: 500), and logs eviction events

**Steps:**
1. **[PLANNING]** Define TTL policy: entries not matched within ttl_days are expired and removed
2. **[PLANNING]** Define LRU eviction: when registry exceeds max_entries (500), evict least-recently-matched entries
3. **[EXECUTION]** Implement TTL expiration check that runs on registry load
4. **[EXECUTION]** Implement LRU eviction that removes least-recently-matched entries when limit exceeded
5. **[EXECUTION]** Log all eviction events with entry details for audit trail
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify TTL expiration and LRU eviction at boundaries
7. **[COMPLETION]** Document lifecycle rules in D-0042/spec.md

**Acceptance Criteria:**
- Entries exceeding TTL are removed on next registry load, verified by test with expired entry
- LRU eviction removes least-recently-matched entries when registry exceeds 500, verified by test at boundary
- Eviction events are logged with entry details, verified by log inspection
- Lifecycle rules documented in D-0042/spec.md

**Validation:**
- Manual check: add entry with TTL=-1 (already expired); load registry; verify entry removed
- Evidence: D-0042/evidence.md contains eviction test log

**Dependencies:** T05.02
**Rollback:** TBD

---

### T05.04 -- Integrate ALREADY_TRACKED section into final report output

| Field | Value |
|---|---|
| Roadmap Item IDs | R-043 |
| Why | AC1 (supporting) requires the final report to include a section listing findings suppressed by the known-issues registry. |
| Effort | S |
| Risk | Low |
| Risk Drivers | (none matched) |
| Tier | LIGHT |
| Confidence | [███████░░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Quick sanity check |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0043 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0043/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0043/evidence.md

**Deliverables:**
- ALREADY_TRACKED report section that lists suppressed findings with their registry entry IDs and matched patterns

**Steps:**
1. **[PLANNING]** Define section format: table with columns finding_path, registry_entry_id, matched_pattern, suppressed_classification
2. **[PLANNING]** Identify insertion point in report: after main findings sections, before validation section
3. **[EXECUTION]** Implement ALREADY_TRACKED section renderer using data from T05.02 matching results
4. **[EXECUTION]** Integrate section into report completeness checker (T04.13) as optional section (present only when registry is active)
5. **[VERIFICATION]** Verify section appears in report when registry matches exist and is absent when no matches
6. **[COMPLETION]** Document section format in D-0043/spec.md

**Acceptance Criteria:**
- ALREADY_TRACKED section appears in report when registry matches exist, verified by output inspection
- Section lists each suppressed finding with registry entry ID and matched pattern
- Section is absent when no registry matches exist (not an empty section)
- Section format documented in D-0043/spec.md

**Validation:**
- Manual check: run audit with active registry containing 2 matches; verify section lists both
- Evidence: D-0043/evidence.md contains section sample

**Dependencies:** T05.02, T04.13
**Rollback:** TBD

---

### T05.05 -- Build AC1-AC20 automated validation suite covering all acceptance criteria

| Field | Value |
|---|---|
| Roadmap Item IDs | R-044 |
| Why | Final acceptance requires automated validation of all 20 acceptance criteria to confirm complete v2 contract compliance. |
| Effort | L |
| Risk | High |
| Risk Drivers | compliance, audit, system-wide, end-to-end |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0044 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0044/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0044/evidence.md

**Deliverables:**
- Test suite with one or more test cases per AC (AC1-AC20) that can be run via `uv run pytest` to validate complete v2 contract compliance

**Steps:**
1. **[PLANNING]** Map each AC (AC1-AC20) to specific testable assertions derived from the unified spec
2. **[PLANNING]** Identify test fixtures needed: small repo, medium repo, known-dead-code repo, monorepo
3. **[EXECUTION]** Implement test cases for AC1-AC10 covering classification, coverage, checkpointing, evidence gates, validation, credentials, gitignore, budget, report depth, schema
4. **[EXECUTION]** Implement test cases for AC11-AC20 covering scanner schema, dependency graph, profiling, docs audit, v1 mapping, directory assessment, dynamic imports, anti-lazy, dry-run, concurrency
5. **[EXECUTION]** Create test fixtures with known expected outcomes for deterministic validation
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify all 20 ACs have at least one test case and all tests pass
7. **[COMPLETION]** Document AC-to-test mapping in D-0044/spec.md

**Acceptance Criteria:**
- Test suite contains at least one test case per AC (AC1-AC20), verified by counting test markers
- All tests pass on a clean run: `uv run pytest tests/cleanup_audit_v2/ -v` exits 0
- Test fixtures are self-contained and do not require external repositories
- AC-to-test mapping documented in D-0044/spec.md

**Validation:**
- Manual check: `uv run pytest tests/cleanup_audit_v2/ -v` exits 0 with all 20+ tests passing
- Evidence: D-0044/evidence.md contains full test output

**Dependencies:** T01.01-T04.13 (all prior tasks)
**Rollback:** TBD

---

### Checkpoint: Phase 5 / Tasks T05.01-T05.05

**Purpose:** Validate optional extensions and AC validation suite before benchmark runs.
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/CP-P05-T01-T05.md
**Verification:**
- Full docs audit produces 5-section output for test fixture
- Known-issues registry correctly suppresses, expires, and evicts entries
- AC1-AC20 validation suite passes on clean run
**Exit Criteria:**
- Tasks T05.01-T05.05 completed with passing verification
- No STRICT-tier task has unresolved sub-agent findings
- ALREADY_TRACKED section correctly present/absent based on registry state

---

### T05.06 -- Execute benchmark runs on small, medium, and known-dead-code repositories

| Field | Value |
|---|---|
| Roadmap Item IDs | R-045 |
| Why | AC9, AC12, AC17 require benchmark validation on repositories of varying size and characteristics to confirm real-world performance. |
| Effort | L |
| Risk | High |
| Risk Drivers | performance, end-to-end, system-wide |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0045 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0045/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0045/evidence.md

**Deliverables:**
- Benchmark results for 3 repository tiers: small (<50 files), medium (50-500 files), known-dead-code (repo with confirmed dead code for detection accuracy measurement)

**Steps:**
1. **[PLANNING]** Identify or create 3 benchmark repositories: small fixture, medium fixture, known-dead-code fixture with documented expected findings
2. **[PLANNING]** Define benchmark metrics: completion time, token usage, dead code detection accuracy, false positive rate
3. **[EXECUTION]** Run full audit on small repository; record metrics
4. **[EXECUTION]** Run full audit on medium repository; record metrics
5. **[EXECUTION]** Run full audit on known-dead-code repository; compare findings against expected dead code list
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify benchmark metrics are within acceptable ranges and dead code detection accuracy
7. **[COMPLETION]** Document benchmark results in D-0045/spec.md

**Acceptance Criteria:**
- Small repo audit completes without errors, verified by exit status and report completeness check
- Medium repo audit completes within budget constraints (or degrades gracefully), verified by budget log
- Known-dead-code repo audit detects at least 80% of documented dead code entries, verified by comparison
- Benchmark results documented in D-0045/spec.md with metrics per repository

**Validation:**
- Manual check: compare known-dead-code findings against documented expected list; verify >= 80% detection
- Evidence: D-0045/evidence.md contains benchmark metric tables

**Dependencies:** T05.05
**Rollback:** TBD

---

### T05.07 -- Validate concurrent-run isolation to prevent cross-run data contamination

| Field | Value |
|---|---|
| Roadmap Item IDs | R-046 |
| Why | AC20 requires that concurrent audit runs on the same repository do not contaminate each other's data or output. |
| Effort | M |
| Risk | High |
| Risk Drivers | data, multi-tenant, across |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0046 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0046/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0046/evidence.md

**Deliverables:**
- Concurrent-run isolation test that launches 2 audit instances simultaneously on the same repository and verifies output isolation (no cross-contamination of progress.json, results, or cache)

**Steps:**
1. **[PLANNING]** Define isolation boundaries: separate progress.json paths, separate output directories, separate cache namespaces
2. **[PLANNING]** Define contamination detection: compare outputs of concurrent runs; they must be identical to sequential runs
3. **[EXECUTION]** Implement run ID generation for unique namespacing of progress, output, and cache files
4. **[EXECUTION]** Launch 2 concurrent audit instances with different run IDs on same repository
5. **[EXECUTION]** Compare outputs: each run's results must match a sequential single-run result
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify no cross-contamination between concurrent runs
7. **[COMPLETION]** Document isolation mechanism in D-0046/spec.md

**Acceptance Criteria:**
- Concurrent runs produce identical output to sequential runs on same input, verified by diff
- Progress.json files are independently maintained per run (no cross-write), verified by file inspection
- Cache entries are namespaced per run ID, verified by cache key inspection
- Isolation mechanism documented in D-0046/spec.md

**Validation:**
- Manual check: launch 2 concurrent runs; verify output files are independent and cache is isolated
- Evidence: D-0046/evidence.md contains concurrent-run comparison results

**Dependencies:** T01.03, T02.03
**Rollback:** TBD

---

### T05.08 -- Document non-determinism sources and known limitations in final report

| Field | Value |
|---|---|
| Roadmap Item IDs | R-047 |
| Why | AC6 (quality extension) requires transparent documentation of sources of non-determinism and known limitations in audit output. |
| Effort | S |
| Risk | Low |
| Risk Drivers | (none matched) |
| Tier | LIGHT |
| Confidence | [███████░░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Quick sanity check |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0047 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0047/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0047/evidence.md

**Deliverables:**
- Limitations section in final report documenting known sources of non-determinism (LLM classification variance, git history dependency, dynamic import detection limits) and their impact on result reliability

**Steps:**
1. **[PLANNING]** Catalog non-determinism sources: LLM output variance, git history availability, dynamic import pattern coverage, Tier-C inference confidence
2. **[PLANNING]** Assess impact of each source on result reliability
3. **[EXECUTION]** Write limitations section with per-source description, impact assessment, and mitigation notes
4. **[EXECUTION]** Integrate section into final report template between validation results and appendix
5. **[VERIFICATION]** Verify section is present in final report and covers all identified sources
6. **[COMPLETION]** Document limitations catalog in D-0047/spec.md

**Acceptance Criteria:**
- Limitations section lists at least 3 non-determinism sources with impact descriptions
- Section is integrated into final report template at the correct position
- Each limitation includes mitigation notes (what the audit does to reduce impact)
- Limitations catalog documented in D-0047/spec.md

**Validation:**
- Manual check: verify limitations section present in a generated report with all identified sources
- Evidence: D-0047/evidence.md contains limitations section sample

**Dependencies:** T04.10
**Rollback:** TBD

---

### T05.09 -- Produce final release readiness decision record for v2 acceptance

| Field | Value |
|---|---|
| Roadmap Item IDs | R-048 |
| Why | AC completion evidence requires a formal decision record documenting whether all acceptance criteria are met and the release is ready. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | compliance, audit |
| Tier | STANDARD |
| Confidence | [███████░░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0048 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0048/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0048/evidence.md

**Deliverables:**
- Release readiness decision record documenting: AC1-AC20 pass/fail status, benchmark results summary, known limitations acknowledgment, and go/no-go recommendation with evidence links

**Steps:**
1. **[PLANNING]** Define decision record template: AC matrix (pass/fail per AC), benchmark summary, limitations acknowledgment, recommendation
2. **[PLANNING]** Gather evidence links from D-0044 (test suite results) and D-0045 (benchmark results)
3. **[EXECUTION]** Populate AC matrix with pass/fail status from T05.05 validation suite results
4. **[EXECUTION]** Compile benchmark summary from T05.06 results and known limitations from T05.08
5. **[EXECUTION]** Write go/no-go recommendation based on AC pass rate and benchmark outcomes
6. **[VERIFICATION]** Verify decision record references all 20 ACs and all benchmark repositories
7. **[COMPLETION]** Finalize decision record in D-0048/spec.md

**Acceptance Criteria:**
- Decision record contains pass/fail status for all 20 ACs (AC1-AC20), verified by AC count
- Benchmark results summary includes all 3 repository tiers, verified by section inspection
- Go/no-go recommendation is explicitly stated with supporting evidence links
- Decision record finalized in D-0048/spec.md

**Validation:**
- Manual check: verify decision record lists all 20 ACs and includes go/no-go recommendation
- Evidence: D-0048/evidence.md contains final decision record

**Dependencies:** T05.05, T05.06, T05.07, T05.08
**Rollback:** TBD

---

### Checkpoint: End of Phase 5

**Purpose:** Final acceptance gate. All v2 deliverables must be complete, validated, and benchmarked.
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/CP-P05-END.md
**Verification:**
- All 9 tasks (T05.01-T05.09) completed with passing verification
- AC1-AC20 automated validation suite passes completely
- Benchmark runs on all 3 repository tiers completed with acceptable metrics
**Exit Criteria:**
- Evidence artifacts exist for D-0040 through D-0048
- Release readiness decision record contains go/no-go recommendation
- No STRICT-tier task has unresolved quality-engineer findings
