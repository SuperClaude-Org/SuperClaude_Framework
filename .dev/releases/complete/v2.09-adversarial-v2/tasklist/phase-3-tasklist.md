# Phase 3 -- Validation Gate & Execution Engine

Validate M2/M3 integration with backward compatibility regression, then build the Phase Execution Engine runtime layer: Phase Executor, artifact routing, parallel scheduler, pipeline manifest, resume, blind evaluation, plateau detection, and error policies.

---

### T03.01 -- Run backward compatibility regression against D1.2 baseline

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | V1 gate: all D1.2 baseline invocations must produce unchanged output after M2/M3 modifications to confirm zero regressions before proceeding to M4. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0017/evidence.md

**Deliverables:**
- Regression pass report confirming 100% of D1.2 baseline invocations produce output matching documented baseline (0 regressions)

**Steps:**
1. **[PLANNING]** Load backward compatibility baseline (D-0002/spec.md from T01.02)
2. **[PLANNING]** Prepare execution environment with M2/M3 modifications active
3. **[EXECUTION]** Execute each baseline invocation and capture output
4. **[EXECUTION]** Diff each output against documented expected output from baseline
5. **[VERIFICATION]** Confirm 0 regressions: all diffs are empty
6. **[COMPLETION]** Record regression results in D-0017/evidence.md

**Acceptance Criteria:**
- 100% of D1.2 baseline invocations produce output matching documented baseline
- Zero regressions detected in Mode A and Mode B outputs
- Regression report at `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0017/evidence.md` lists all invocations with pass/fail status
- Report includes diff output for any failures (expected: none)

**Validation:**
- Manual check: review regression report for any non-empty diffs
- Evidence: linkable artifact produced (D-0017/evidence.md)

**Dependencies:** T01.02 (baseline document), T02.01-T02.12 (M2/M3 modifications)
**Rollback:** N/A (validation task, non-destructive)
**Notes:** EXEMPT tier -- read-only validation task comparing outputs against baseline.

---

### T03.02 -- Run protocol correctness validation (SC-005, SC-006, SC-007)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | V1 gate: protocol correctness must be verified by running SC-005 (v0.04 variant replay catching both escaped bug classes) and SC-006/SC-007 (AD-2 and AD-5 acceptance scenario suites). |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (end-to-end protocol validation) |
| Tier | STRICT |
| Confidence | [█████████░] 86% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0018/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0018/evidence.md

**Deliverables:**
- Protocol correctness validation report: SC-005 catches both filter divergence and sentinel collision; SC-006 (AC-AD2-1 through AC-AD2-4) and SC-007 (AC-AD5-1 through AC-AD5-4) pass with >=6 of 8 AC assertions

**Steps:**
1. **[PLANNING]** Load SC-005, SC-006, SC-007 test scenarios from test scaffolding (D-0004)
2. **[PLANNING]** Prepare v0.04 variant replay data for SC-005 execution
3. **[EXECUTION]** Execute SC-005: v0.04 variant replay; verify both filter divergence and sentinel collision are caught by AD-2 or AD-5
4. **[EXECUTION]** Execute SC-006: run AC-AD2-1 through AC-AD2-4 test assertions
5. **[EXECUTION]** Execute SC-007: run AC-AD5-1 through AC-AD5-4 test assertions
6. **[VERIFICATION]** Verify SC-005 passes (both bug classes caught); verify >=6 of 8 AC assertions pass across SC-006/SC-007
7. **[COMPLETION]** Record results in D-0018/evidence.md with per-assertion pass/fail detail

**Acceptance Criteria:**
- SC-005 passes: both escaped bug classes (filter divergence + sentinel collision) caught by AD-2 or AD-5
- SC-006 passes: >=3 of 4 AC-AD2 assertions pass (shared assumption extraction)
- SC-007 passes: >=3 of 4 AC-AD5 assertions pass (taxonomy coverage gate)
- Results documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0018/evidence.md` with per-assertion detail

**Validation:**
- Manual check: review per-assertion results; verify >=6 of 8 total AC assertions pass
- Evidence: linkable artifact produced (D-0018/evidence.md)

**Dependencies:** T02.07-T02.12 (M3 protocol improvements)
**Rollback:** N/A (validation task, non-destructive)

---

### T03.03 -- Measure Step 1 overhead delta for M3 additions (NFR-004)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-019 |
| Why | V1 gate: Step 1 overhead with shared assumption extraction enabled must be <=10% above baseline (NFR-004 compliance). |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (overhead measurement) |
| Tier | STANDARD |
| Confidence | [████████░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0019/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0019/evidence.md

**Deliverables:**
- Overhead measurement report: Step 1 execution time/tokens with and without shared assumption extraction, showing delta <=10%

**Steps:**
1. **[PLANNING]** Define measurement methodology: baseline Step 1 time/tokens vs Step 1 with AD-2 enabled
2. **[PLANNING]** Select representative debate input for consistent measurement
3. **[EXECUTION]** Measure Step 1 baseline: time and token count without shared assumption extraction
4. **[EXECUTION]** Measure Step 1 with AD-2: time and token count with shared assumption extraction enabled
5. **[VERIFICATION]** Calculate delta percentage; verify delta <=10% (NFR-004 compliance)
6. **[COMPLETION]** Record measurements and delta in D-0019/evidence.md

**Acceptance Criteria:**
- Overhead delta measured as `(AD2_tokens - baseline_tokens) / baseline_tokens * 100`
- Measured delta <=10% (NFR-004 compliance)
- Measurement report at `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0019/evidence.md` includes baseline, AD-2, and delta values
- Measurement uses representative debate input (not trivial/edge case)

**Validation:**
- Manual check: verify delta calculation and NFR-004 compliance
- Evidence: linkable artifact produced (D-0019/evidence.md)

**Dependencies:** T02.07 (shared assumption extraction)
**Rollback:** N/A (measurement task, non-destructive)

---

### T03.04 -- Implement Phase Executor translating phase config to Mode A/B invocation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | The Phase Executor is the core runtime: it translates each phase configuration into a Mode A (compare) or Mode B (generate) invocation, scoped to an isolated phase output directory. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (system-wide execution path), multi-file |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0020/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0020/evidence.md

**Deliverables:**
- Phase Executor that reads phase config (type, agents, dependencies), translates to Mode A or Mode B invocation with isolated output directory, and executes

**Steps:**
1. **[PLANNING]** Define translation rules: `generate` phase type -> Mode B invocation; `compare` phase type -> Mode A invocation
2. **[PLANNING]** Define output directory isolation: each phase gets `<pipeline_output>/<phase_id>/` directory
3. **[EXECUTION]** Implement config-to-invocation translator: extract phase type, agent list, and output path
4. **[EXECUTION]** Implement invocation dispatcher: call existing Mode A/B code paths with phase-specific parameters
5. **[EXECUTION]** Implement output directory creation and scoping: all phase artifacts written to isolated directory
6. **[VERIFICATION]** Test: single-phase pipeline (`--pipeline "generate:opus:architect"`) produces identical output to direct Mode B invocation
7. **[COMPLETION]** Document executor translation rules and output structure in D-0020/spec.md

**Acceptance Criteria:**
- Single-phase pipeline (`--pipeline "generate:opus:architect"`) produces output identical to direct Mode B invocation
- Phase output directory is isolated: `<pipeline_output>/<phase_id>/` contains all phase artifacts
- `compare` phase type correctly invokes Mode A; `generate` phase type correctly invokes Mode B
- Translation rules documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0020/spec.md`

**Validation:**
- Manual check: compare single-phase pipeline output to direct Mode B invocation; verify identical results
- Evidence: linkable artifact produced (D-0020/spec.md)

**Dependencies:** T02.03 (DAG builder), T02.06 (dry-run render)
**Rollback:** Remove Phase Executor; revert to direct Mode A/B invocation only

---

### T03.05 -- Implement artifact routing between dependent phases

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | Dependent phases must receive artifacts from upstream phases: `merged_output` and `all_variants` paths must be resolved and passed as inputs to consuming phases. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (inter-phase data flow) |
| Tier | STRICT |
| Confidence | [█████████░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0021/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0021/evidence.md

**Deliverables:**
- Artifact routing system that resolves `merged_output` and `all_variants` path references between dependent phases and passes resolved paths as inputs to consuming phases

**Steps:**
1. **[PLANNING]** Define artifact path resolution: how `merged_output` and `all_variants` map to filesystem paths in phase output directories
2. **[PLANNING]** Define routing contract: which phase types produce which artifact types (generate -> merged_output + all_variants; compare -> merged_output)
3. **[EXECUTION]** Implement path resolver: given phase ID and artifact type, compute filesystem path from phase output directory
4. **[EXECUTION]** Implement routing logic: before executing a phase, resolve all dependency artifacts and inject as input parameters
5. **[VERIFICATION]** Test: 2-phase pipeline (`generate -> compare`) correctly passes phase 1 merged output as phase 2 variant input
6. **[COMPLETION]** Document routing contract and path resolution in D-0021/spec.md

**Acceptance Criteria:**
- 2-phase pipeline (`generate -> compare`) correctly passes phase 1 merged output as phase 2 variant input
- Path resolution handles both `merged_output` and `all_variants` artifact types
- Missing dependency artifacts produce descriptive error before phase execution begins
- Routing contract documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0021/spec.md`

**Validation:**
- Manual check: run 2-phase pipeline; verify artifact paths are correctly resolved and passed
- Evidence: linkable artifact produced (D-0021/spec.md)

**Dependencies:** T03.04 (Phase Executor)
**Rollback:** Remove artifact routing; phases cannot chain outputs

---

### Checkpoint: Phase 3 / Tasks T03.01-T03.05

**Purpose:** Verify V1 validation gate passed and core execution engine (executor + artifact routing) is functional before parallel scheduling and enhancement features.
**Checkpoint Report Path:** .dev/releases/current/2.09-adversarial-v2/tasklist/checkpoints/CP-P03-T01-T05.md

**Verification:**
- V1 regression and protocol correctness validation passed (T03.01, T03.02)
- Phase Executor produces correct output for single-phase pipeline (T03.04)
- Artifact routing works for 2-phase pipeline (T03.05)

**Exit Criteria:**
- V1 gate passed: 0 regressions, >=6/8 AC assertions, overhead <=10%
- Phase Executor and artifact routing produce correct outputs for 1-phase and 2-phase pipelines
- All deliverables D-0017 through D-0021 produced

---

### T03.06 -- Implement parallel phase scheduler with topological sort

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | Phases at the same dependency level must execute concurrently up to `--pipeline-parallel N` limit, using topological sort for execution ordering. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | performance (parallel execution), cross-cutting scope (system-wide scheduling) |
| Tier | STRICT |
| Confidence | [█████████░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0022/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0022/evidence.md

**Deliverables:**
- Parallel phase scheduler using topological sort for execution ordering with concurrent execution capped at `--pipeline-parallel N`

**Steps:**
1. **[PLANNING]** Review DAG builder output (T02.03) for level grouping information
2. **[PLANNING]** Define concurrency model: phases at same level execute in parallel; `--pipeline-parallel N` caps concurrent count
3. **[EXECUTION]** Implement topological sort producing execution levels from DAG
4. **[EXECUTION]** Implement parallel dispatcher: launch phases within a level concurrently up to N limit
5. **[EXECUTION]** Implement synchronization: wait for all phases in a level to complete before advancing to next level
6. **[VERIFICATION]** Test: 2-phase parallel `generate -> compare` produces correct artifacts with no race conditions
7. **[COMPLETION]** Document scheduler algorithm and concurrency model in D-0022/spec.md

**Acceptance Criteria:**
- 2-phase parallel pipeline produces correct artifacts with no race conditions in artifact routing
- `--pipeline-parallel N` correctly limits concurrent phase execution (default N=3)
- Topological sort respects dependency edges: dependent phases never execute before their dependencies complete
- Scheduler algorithm documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0022/spec.md`

**Validation:**
- Manual check: run parallel pipeline; verify execution order and artifact correctness
- Evidence: linkable artifact produced (D-0022/spec.md)

**Dependencies:** T03.04 (Phase Executor), T03.05 (artifact routing)
**Rollback:** Remove parallel scheduler; fall back to sequential phase execution

---

### T03.07 -- Implement pipeline manifest (pipeline-manifest.yaml)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | The pipeline manifest tracks execution state: created at pipeline start, updated after each phase with return contract values and checksums, enabling resume and audit. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [█████████░] 86% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0023/spec.md

**Deliverables:**
- Pipeline manifest (`pipeline-manifest.yaml`) created at pipeline start, updated after each phase with return contract, status, and artifact checksums

**Steps:**
1. **[PLANNING]** Define manifest schema: pipeline ID, creation timestamp, phase list with status/return contract/checksums
2. **[PLANNING]** Define update protocol: after each phase completes, append return contract and compute artifact checksums
3. **[EXECUTION]** Implement manifest creation at pipeline start with initial phase list (all status: pending)
4. **[EXECUTION]** Implement post-phase manifest update: set status to completed/failed, record return contract, compute checksums
5. **[VERIFICATION]** Test: after 3-phase execution, manifest contains all phase results, statuses, and convergence scores
6. **[COMPLETION]** Document manifest schema in D-0023/spec.md

**Acceptance Criteria:**
- `pipeline-manifest.yaml` is created at pipeline start with all phases listed as pending
- After 3-phase execution, manifest contains: all phase results, statuses (completed/failed), convergence scores, and artifact checksums
- Manifest schema is YAML-parseable and machine-readable
- Schema documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0023/spec.md`

**Validation:**
- Manual check: verify manifest after 3-phase pipeline contains complete per-phase data
- Evidence: linkable artifact produced (D-0023/spec.md)

**Dependencies:** T03.04 (Phase Executor)
**Rollback:** Remove manifest generation; resume functionality (T03.08) becomes unavailable

---

### T03.08 -- Implement `--pipeline-resume` from manifest checkpoint

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | Pipeline resume reads the manifest, validates artifact checksums, and re-executes from the first incomplete phase, avoiding redundant re-execution of completed phases. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | data integrity (checksum validation), cross-cutting scope |
| Tier | STRICT |
| Confidence | [█████████░] 86% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0024/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0024/evidence.md

**Deliverables:**
- `--pipeline-resume` flag implementation that reads manifest, validates checksums of completed phases, and re-executes from first incomplete phase

**Steps:**
1. **[PLANNING]** Define resume algorithm: read manifest, validate completed phase checksums, identify first incomplete phase
2. **[PLANNING]** Define checksum validation: which files are checksummed (artifact files only, not SKILL.md or system state)
3. **[EXECUTION]** Implement manifest reader for resume: parse phase list and status
4. **[EXECUTION]** Implement checksum validator: compute checksums of completed phase artifacts and compare to manifest
5. **[EXECUTION]** Implement resume dispatcher: skip validated phases, re-execute from first incomplete phase
6. **[VERIFICATION]** Test: resume from phase 2 of 3 skips phase 1 (checksum valid) and re-executes phases 2-3
7. **[COMPLETION]** Document resume algorithm and checksum validation in D-0024/spec.md

**Acceptance Criteria:**
- Resume from phase 2 of 3 skips phase 1 (checksum valid) and re-executes phases 2-3
- Invalid checksum triggers re-execution of the affected phase and all downstream phases
- Missing manifest file produces descriptive error: "No pipeline manifest found at <path>"
- Resume algorithm documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0024/spec.md`

**Validation:**
- Manual check: interrupt pipeline at phase 2; resume; verify phase 1 skipped and phases 2-3 re-execute
- Evidence: linkable artifact produced (D-0024/spec.md)

**Dependencies:** T03.07 (pipeline manifest)
**Rollback:** Remove resume functionality; pipelines must run from start

---

### T03.09 -- Implement blind evaluation (`--blind`) with metadata stripping

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | Blind evaluation strips model-name metadata from artifacts before compare phases receive variants, ensuring unbiased evaluation (SC-003). |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data integrity (metadata must be completely stripped) |
| Tier | STRICT |
| Confidence | [█████████░] 86% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0025 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0025/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0025/evidence.md

**Deliverables:**
- Blind evaluation implementation: `--blind` flag triggers metadata stripping in artifact routing, removing model-name references before compare phase receives variants

**Steps:**
1. **[PLANNING]** Identify all metadata fields containing model names in variant artifacts
2. **[PLANNING]** Define stripping rules: which fields/patterns to remove or anonymize
3. **[EXECUTION]** Implement metadata stripper: scan artifact content for model-name patterns and remove/replace
4. **[EXECUTION]** Integrate stripper into artifact routing (T03.05): apply before passing artifacts to compare phases when `--blind` is active
5. **[VERIFICATION]** Test SC-003: merged output after `--blind` pipeline contains zero model-name references
6. **[COMPLETION]** Document stripping rules and integration point in D-0025/spec.md

**Acceptance Criteria:**
- SC-003 passes: merged output contains zero model-name references after `--blind` pipeline
- Stripping applies only when `--blind` flag is active; without flag, metadata is preserved
- Stripping covers: file content model references, metadata headers, attribution comments
- Stripping rules documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0025/spec.md`

**Validation:**
- Manual check: run `--blind` pipeline; grep merged output for known model names; verify zero matches
- Evidence: linkable artifact produced (D-0025/spec.md)

**Dependencies:** T03.05 (artifact routing)
**Rollback:** Remove blind evaluation; metadata remains in artifacts

---

### T03.10 -- Implement convergence plateau detection (`--auto-stop-plateau`)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | Convergence plateau detection halts pipeline execution when convergence delta <5% for 2 consecutive compare phases, preventing wasteful additional rounds (SC-004). |
| Effort | M |
| Risk | Low |
| Risk Drivers | performance (optimization feature) |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0026 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0026/spec.md

**Deliverables:**
- Convergence plateau detection: `--auto-stop-plateau` flag monitors convergence delta across compare phases and triggers warning + halt when delta <5% for 2 consecutive phases

**Steps:**
1. **[PLANNING]** Define plateau detection algorithm: track convergence score per compare phase; compute delta between consecutive phases
2. **[PLANNING]** Define halt behavior: warning message, manifest update, clean pipeline termination
3. **[EXECUTION]** Implement convergence tracking: after each compare phase, record convergence score in manifest
4. **[EXECUTION]** Implement plateau check: after second+ compare phase, compute delta; if <5% for 2 consecutive, trigger halt
5. **[VERIFICATION]** Test SC-004: synthetic 3-phase pipeline with plateau triggers warning and halt on phase 3
6. **[COMPLETION]** Document detection algorithm in D-0026/spec.md

**Acceptance Criteria:**
- SC-004 passes: synthetic 3-phase pipeline with convergence plateau triggers warning and halt on phase 3
- `--auto-stop-plateau` flag enables detection; without flag, pipeline runs all phases regardless of delta
- Warning message includes: current delta, threshold (5%), consecutive count, recommendation to review
- Algorithm documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0026/spec.md`

**Validation:**
- Manual check: run synthetic pipeline with plateau; verify warning and halt at correct phase
- Evidence: linkable artifact produced (D-0026/spec.md)

**Dependencies:** T03.04 (Phase Executor), T03.07 (pipeline manifest)
**Rollback:** Remove plateau detection; pipelines always run all phases

---

### T03.11 -- Implement error policies (halt-on-failure + continue mode)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027 |
| Why | Pipeline error handling: halt-on-failure marks dependents as skipped (default); `--pipeline-on-error continue` leaves parallel branches running. Minimum variant constraint requires compare phases to have >=2 inputs. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (error handling across all phases) |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0027/spec.md

**Deliverables:**
- Error policy implementation: halt-on-failure (default) marks dependents as skipped in manifest; `--pipeline-on-error continue` keeps parallel branches running; minimum variant constraint (>=2) for compare phases

**Steps:**
1. **[PLANNING]** Define error policy behavior: halt-on-failure propagation vs continue-mode branch isolation
2. **[PLANNING]** Define minimum variant constraint: compare phase requires >=2 variant inputs
3. **[EXECUTION]** Implement halt-on-failure: on phase failure, mark all dependent phases as "skipped" in manifest
4. **[EXECUTION]** Implement continue mode: on phase failure, mark dependents as skipped but allow independent branches to continue
5. **[EXECUTION]** Implement minimum variant check: before compare phase execution, verify >=2 variant inputs; fail gracefully if not met
6. **[VERIFICATION]** Test: failed phase marks dependents as skipped; continue mode leaves parallel branches running
7. **[COMPLETION]** Document error policies in D-0027/spec.md

**Acceptance Criteria:**
- Failed phase in halt-on-failure mode marks all dependent phases as "skipped" in manifest
- `--pipeline-on-error continue` allows parallel branches to complete when one branch fails
- Compare phase with <2 variant inputs produces descriptive error and marks phase as failed
- Error policies documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0027/spec.md`

**Validation:**
- Manual check: trigger phase failure; verify dependent marking and continue-mode behavior
- Evidence: linkable artifact produced (D-0027/spec.md)

**Dependencies:** T03.04 (Phase Executor), T03.06 (parallel scheduler)
**Rollback:** Remove error policies; pipeline aborts entirely on any failure

---

### Checkpoint: End of Phase 3

**Purpose:** Verify V1 gate passed, Phase Execution Engine is complete with all features (executor, routing, parallel, manifest, resume, blind, plateau, errors), and M4 is ready for M5 integration.
**Checkpoint Report Path:** .dev/releases/current/2.09-adversarial-v2/tasklist/checkpoints/CP-P03-END.md

**Verification:**
- V1 regression: 0 regressions against baseline (T03.01)
- Phase Executor + artifact routing + parallel scheduler produce correct multi-phase outputs (T03.04-T03.06)
- Pipeline manifest, resume, blind evaluation, plateau detection, and error policies all functional (T03.07-T03.11)

**Exit Criteria:**
- All 11 Phase 3 tasks completed with deliverables D-0017 through D-0027 produced
- SC-003 (blind) and SC-004 (plateau) pass
- Pipeline manifest tracks execution state correctly across all execution modes
