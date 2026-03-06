# Phase 1 -- Enforce Promises and Correctness

Implement all v1-promised but missing behaviors as a non-negotiable baseline (M1) and eliminate known correctness failures with locked scanner output contracts (M2). This phase establishes the foundational contract that all subsequent phases depend on.

---

### T01.01 -- Implement two-tier classification with backward mapping to v1 categories

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001 |
| Why | The v1 spec promised classification tiers but the implementation is missing backward-compatible category mapping (AC1, AC15). |
| Effort | M |
| Risk | High |
| Risk Drivers | schema, system-wide, breaking change |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0001/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0001/evidence.md

**Deliverables:**
- Two-tier classification engine that maps audit findings into risk tiers with deterministic backward mapping to v1 category labels

**Steps:**
1. **[PLANNING]** Load the unified spec sections covering AC1 and AC15; identify the v1 category taxonomy and the v2 two-tier target schema
2. **[PLANNING]** Check existing classification logic in the cleanup-audit skill for reusable patterns and confirm no conflicting tier definitions
3. **[EXECUTION]** Implement the two-tier classification function that accepts raw audit findings and assigns tier-1 (actionable) and tier-2 (informational) labels
4. **[EXECUTION]** Implement the backward mapping layer that translates v2 tiers into v1-compatible category strings (DELETE, KEEP, INVESTIGATE, REORGANIZE)
5. **[EXECUTION]** Add unit tests validating that every v2 tier output produces a valid v1 category and that round-trip mapping is lossless
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to validate classification determinism across 3 sample inputs
7. **[COMPLETION]** Record evidence of v2-to-v1 mapping correctness in D-0001/evidence.md

**Acceptance Criteria:**
- Classification function produces valid tier-1/tier-2 labels for all input finding types, verified by `uv run pytest tests/pipeline/test_classification.py` exiting 0
- No v1 category is orphaned; backward mapping covers all 4 v1 categories (DELETE, KEEP, INVESTIGATE, REORGANIZE)
- Same input always produces same tier assignment (determinism verified by running classification 3 times with identical input)
- Mapping table documented in D-0001/spec.md with explicit v2-tier -> v1-category correspondence

**Validation:**
- Manual check: classification output for a known test fixture matches expected tier and v1 category
- Evidence: D-0001/evidence.md contains mapping test results

**Dependencies:** None
**Rollback:** TBD
**Notes:** AC1 requires core action sections; AC15 requires v2-to-v1 category mapping compatibility.

---

### T01.02 -- Implement coverage tracking with per-risk-tier metrics and artifact output

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002 |
| Why | AC2 requires coverage artifacts that report per-tier metrics; current implementation lacks tier-stratified tracking. |
| Effort | S |
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
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0002/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0002/evidence.md

**Deliverables:**
- Coverage tracking module that accumulates per-risk-tier file counts and emits a coverage artifact with tier-stratified percentages

**Steps:**
1. **[PLANNING]** Load AC2 requirements and identify the coverage metric schema (files scanned, files classified, per-tier counts)
2. **[PLANNING]** Check dependency on T01.01 tier classification output format
3. **[EXECUTION]** Implement coverage accumulator that ingests classification results and maintains running per-tier tallies
4. **[EXECUTION]** Implement coverage artifact emitter that outputs a structured coverage report with tier breakdown
5. **[VERIFICATION]** Spawn quality-engineer sub-agent to validate coverage percentages sum correctly and no files are double-counted
6. **[COMPLETION]** Record sample coverage output in D-0002/evidence.md

**Acceptance Criteria:**
- Coverage artifact contains per-tier file counts and percentages, verified by inspecting output JSON schema
- Tier percentages sum to 100% (within floating-point tolerance of 0.01%)
- Running the coverage tracker twice on the same input produces identical output
- Coverage artifact schema documented in D-0002/spec.md

**Validation:**
- Manual check: coverage artifact for a 10-file test fixture shows correct tier distribution
- Evidence: D-0002/evidence.md contains sample coverage artifact

**Dependencies:** T01.01
**Rollback:** TBD

---

### T01.03 -- Implement batch-level checkpointing with progress.json persistence

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003 |
| Why | AC3 requires batch-level checkpointing so interrupted runs can resume; no checkpoint mechanism exists. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data, schema |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0003/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0003/evidence.md

**Deliverables:**
- Checkpoint writer that persists batch progress to `progress.json` after each batch completes, and a checkpoint reader that restores state on resume

**Steps:**
1. **[PLANNING]** Define the `progress.json` schema: batch_id, status, files_processed, files_remaining, last_updated timestamp
2. **[PLANNING]** Identify checkpoint write points in the audit pipeline (after each batch completion)
3. **[EXECUTION]** Implement checkpoint writer that atomically writes `progress.json` after each batch
4. **[EXECUTION]** Implement checkpoint reader that loads `progress.json` on startup and skips already-processed batches
5. **[EXECUTION]** Add tests for interrupted-resume scenario (write checkpoint, simulate interruption, verify resume skips completed batches)
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to validate atomic write and resume correctness
7. **[COMPLETION]** Document progress.json schema in D-0003/spec.md

**Acceptance Criteria:**
- File `progress.json` is written after each batch with valid JSON matching the defined schema
- Resume from checkpoint skips already-completed batches and continues from the next pending batch
- Checkpoint write is atomic (no partial writes observed under simulated interruption)
- Schema documented in D-0003/spec.md with field descriptions and example

**Validation:**
- Manual check: interrupt a 3-batch run after batch 1, resume, verify only batches 2-3 execute
- Evidence: D-0003/evidence.md contains resume test log

**Dependencies:** None
**Rollback:** TBD

---

### T01.04 -- Implement evidence-gated DELETE and KEEP classification rules

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | AC4 and AC5 require that DELETE entries carry zero-reference evidence and KEEP entries carry reference evidence; current rules lack evidence gating. |
| Effort | M |
| Risk | High |
| Risk Drivers | security, audit, data, breaking change |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0004/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0004/evidence.md

**Deliverables:**
- Evidence gate that prevents DELETE classification unless zero-reference evidence is attached, and prevents high-tier KEEP without reference evidence

**Steps:**
1. **[PLANNING]** Load AC4 (DELETE evidence) and AC5 (KEEP evidence) requirements from the unified spec
2. **[PLANNING]** Map evidence types to classification actions: zero-reference -> DELETE eligible, has-references -> KEEP required
3. **[EXECUTION]** Implement evidence gate in the classification pipeline that blocks DELETE without zero-reference proof
4. **[EXECUTION]** Implement KEEP evidence enforcement for tier-1 and tier-2 files requiring reference documentation
5. **[EXECUTION]** Add test cases: file with references must not be classified DELETE; file with zero references must carry evidence artifact
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify no evidence-less DELETE or KEEP entries pass the gate
7. **[COMPLETION]** Document evidence gate rules in D-0004/spec.md

**Acceptance Criteria:**
- No DELETE entry exists in output without an attached zero-reference evidence record, verified by scanning output for DELETE entries lacking evidence fields
- Tier-1 and tier-2 KEEP entries include at least one reference evidence record
- Evidence gate rejects attempts to classify a referenced file as DELETE (test case exits with expected rejection)
- Evidence gate rules documented in D-0004/spec.md with decision tree

**Validation:**
- Manual check: attempt to classify a file with 3 known references as DELETE; verify rejection
- Evidence: D-0004/evidence.md contains gate rejection test log

**Dependencies:** T01.01
**Rollback:** TBD

---

### T01.05 -- Implement 10% stratified consistency validation pass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | AC6 requires a 10% sample validation pass to verify classification consistency; no validation sampling exists. |
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
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0005/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0005/evidence.md

**Deliverables:**
- Validation sampler that selects a stratified 10% sample of classified files and re-runs classification to measure consistency rate

**Steps:**
1. **[PLANNING]** Define stratified sampling strategy: proportional representation of each tier in the 10% sample
2. **[PLANNING]** Identify consistency metric: percentage of sampled files where re-classification matches original
3. **[EXECUTION]** Implement stratified sampler that selects 10% of classified files with tier-proportional distribution
4. **[EXECUTION]** Implement consistency checker that re-classifies sampled files and compares to original classification
5. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify sample size meets 10% threshold and consistency rate is reported
6. **[COMPLETION]** Document sampling methodology and consistency formula in D-0005/spec.md

**Acceptance Criteria:**
- Validation sample contains at least 10% of total classified files, verified by count comparison
- Consistency rate is computed and reported as a percentage in the validation output artifact
- Stratified sampling ensures each tier is represented proportionally (no tier has 0 samples if it has files)
- Sampling methodology documented in D-0005/spec.md

**Validation:**
- Manual check: for a 100-file audit, validation sample contains at least 10 files with proportional tier representation
- Evidence: D-0005/evidence.md contains sample validation output

**Dependencies:** T01.01, T01.02
**Rollback:** TBD

---

### Checkpoint: Phase 1 / Tasks T01.01-T01.05

**Purpose:** Validate that M1 core promise enforcement (classification, coverage, checkpointing, evidence gates, validation) is functional before proceeding to correctness fixes.
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/CP-P01-T01-T05.md
**Verification:**
- Two-tier classification produces valid output with backward mapping for test fixtures
- Coverage tracker emits per-tier metrics and checkpoint persistence works across simulated interruption
- Evidence gates reject invalid DELETE/KEEP entries in automated tests
**Exit Criteria:**
- All 5 tasks (T01.01-T01.05) marked completed with passing verification
- No STRICT-tier task has unresolved sub-agent findings
- Evidence artifacts exist for D-0001 through D-0005

---

### T01.06 -- Implement real credential scanning with safe redaction in output

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | AC7 requires credential scanning that distinguishes real secrets from template placeholders, with safe redaction to prevent secret leakage. |
| Effort | M |
| Risk | High |
| Risk Drivers | credentials, secrets, security, compliance |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0006/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0006/evidence.md

**Deliverables:**
- Credential scanner that detects real secrets (API keys, tokens, passwords) while ignoring template placeholders, with output-scrub redaction layer

**Steps:**
1. **[PLANNING]** Define credential detection patterns: API key formats, token patterns, password strings, env var values
2. **[PLANNING]** Define template placeholder patterns to exclude: `${VAR}`, `<YOUR_KEY>`, `xxx`, `placeholder`
3. **[EXECUTION]** Implement credential scanner with regex-based detection for common secret formats
4. **[EXECUTION]** Implement template placeholder filter that marks detected patterns as non-secret
5. **[EXECUTION]** Implement output-scrub redaction layer that replaces secret values with `[REDACTED]` in all output artifacts
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify no secret values appear in any output artifact
7. **[COMPLETION]** Document detection patterns and redaction policy in D-0006/spec.md

**Acceptance Criteria:**
- Scanner detects real API keys and tokens in test fixtures while ignoring `${PLACEHOLDER}` patterns, verified by test suite
- No secret value appears in any output artifact; output-scrub verified by grepping output for known test secret patterns
- Template placeholders (e.g., `<YOUR_API_KEY>`, `${DB_PASSWORD}`) are correctly classified as non-secret
- Detection patterns and redaction policy documented in D-0006/spec.md

**Validation:**
- Manual check: scan a fixture file containing 3 real secrets and 3 templates; verify 3 detections and 3 exclusions
- Evidence: D-0006/evidence.md contains scan results with redacted output

**Dependencies:** None
**Rollback:** TBD
**Notes:** Critical Path Override: Yes -- credential handling paths require maximum verification.

---

### T01.07 -- Implement gitignore inconsistency detection between .gitignore and tracked files

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | AC8 requires flagging files that are tracked by git but match .gitignore patterns, indicating configuration drift. |
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
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0007/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0007/evidence.md

**Deliverables:**
- Gitignore inconsistency checker that compares tracked files against .gitignore patterns and flags mismatches

**Steps:**
1. **[PLANNING]** Identify git commands needed: `git ls-files` for tracked files, parse `.gitignore` for patterns
2. **[PLANNING]** Define inconsistency types: tracked-but-ignored, ignored-but-referenced
3. **[EXECUTION]** Implement checker that loads `.gitignore` patterns, lists tracked files, and identifies matches
4. **[EXECUTION]** Add output formatting: list of inconsistent files with their matching `.gitignore` pattern
5. **[VERIFICATION]** Run checker against a test repository with known gitignore inconsistencies; verify detection
6. **[COMPLETION]** Document checker output format in D-0007/spec.md

**Acceptance Criteria:**
- Checker identifies files that are tracked by git but match a `.gitignore` pattern, verified against test fixture
- Output lists each inconsistent file with the matching pattern
- Checker runs without error on repositories with no `.gitignore` file (empty result, no crash)
- Output format documented in D-0007/spec.md

**Validation:**
- Manual check: run checker on a test repo with 2 known inconsistencies; verify both detected
- Evidence: D-0007/evidence.md contains checker output

**Dependencies:** None
**Rollback:** TBD

---

### T01.08 -- Define and enforce Phase-1 simplified scanner output schema

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | AC11 requires locked scanner output contracts; Phase-1 needs a simplified schema as the baseline contract. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema, breaking change |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0008/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0008/evidence.md

**Deliverables:**
- JSON schema definition for Phase-1 scanner output with validation function that rejects non-conforming output

**Steps:**
1. **[PLANNING]** Extract required fields from AC11: file path, classification, evidence, confidence, tier
2. **[PLANNING]** Define JSON schema with required and optional fields, types, and constraints
3. **[EXECUTION]** Write the JSON schema document for Phase-1 scanner output
4. **[EXECUTION]** Implement schema validation function that accepts scanner output and returns pass/fail with error details
5. **[EXECUTION]** Add tests with valid and invalid scanner output fixtures
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify schema covers all AC11 required fields
7. **[COMPLETION]** Document schema in D-0008/spec.md

**Acceptance Criteria:**
- JSON schema defines all required fields (file_path, classification, evidence, confidence, tier) with correct types
- Schema validation function rejects output missing required fields, verified by test with incomplete fixture
- Schema validation function accepts well-formed output, verified by test with complete fixture
- Schema definition documented in D-0008/spec.md with field descriptions

**Validation:**
- Manual check: validate a known-good scanner output against schema; verify acceptance
- Evidence: D-0008/evidence.md contains validation test results

**Dependencies:** T01.01
**Rollback:** TBD

---

### T01.09 -- Extend scanner schema to Phase-2 full profile alignment

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | AC11 (extended) requires the full profile schema that includes all 8 profiling fields for structural analysis depth. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema, breaking change |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0009/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0009/evidence.md

**Deliverables:**
- Extended JSON schema adding 8-field profile (imports, exports, size, complexity, age, churn, coupling, test-coverage) to the Phase-1 base schema

**Steps:**
1. **[PLANNING]** Identify the 8 profiling fields from the spec: imports, exports, size, complexity, age, churn, coupling, test-coverage
2. **[PLANNING]** Determine backward compatibility: Phase-2 schema must be a superset of Phase-1 schema
3. **[EXECUTION]** Extend JSON schema with 8 additional profile fields as optional (Phase-1 output remains valid)
4. **[EXECUTION]** Update validation function to accept both Phase-1 and Phase-2 output
5. **[EXECUTION]** Add tests verifying Phase-1 output passes Phase-2 validation and Phase-2 output includes all 8 fields
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify backward compatibility and field completeness
7. **[COMPLETION]** Document extended schema in D-0009/spec.md

**Acceptance Criteria:**
- Extended schema includes all 8 profile fields with correct types, verified by schema inspection
- Phase-1 output (without profile fields) still passes Phase-2 schema validation (backward compatible)
- Phase-2 output with all 8 fields passes validation, verified by test with complete fixture
- Extended schema documented in D-0009/spec.md with field descriptions and backward compatibility notes

**Validation:**
- Manual check: validate Phase-1 output against Phase-2 schema; verify acceptance
- Evidence: D-0009/evidence.md contains backward compatibility test results

**Dependencies:** T01.08
**Rollback:** TBD

---

### T01.10 -- Implement batch failure and retry handling policy

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | AC18 (partial) requires that batch failures are handled gracefully with retry logic and minimum viable output on cascading failure. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | data, rollback |
| Tier | STANDARD |
| Confidence | [███████░░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0010/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0010/evidence.md

**Deliverables:**
- Batch failure handler with configurable retry count (default: 2), FAILED status marking, and minimum viable report output on cascading failure

**Steps:**
1. **[PLANNING]** Define retry policy: max retries, backoff strategy, FAILED status conditions
2. **[PLANNING]** Define minimum viable report: what sections are emitted when batches fail
3. **[EXECUTION]** Implement retry handler wrapping batch execution with configurable retry count
4. **[EXECUTION]** Implement FAILED status marking and minimum viable report emitter for cascading failures
5. **[VERIFICATION]** Test with simulated batch failure: verify retry attempts, FAILED marking, and minimum viable report output
6. **[COMPLETION]** Document retry policy and failure handling in D-0010/spec.md

**Acceptance Criteria:**
- Batch failure triggers up to 2 retry attempts before marking as FAILED, verified by test log showing retry count
- FAILED batches are recorded in `progress.json` with failure reason
- Cascading failure (all batches fail) produces a minimum viable report with error summary section
- Retry policy documented in D-0010/spec.md

**Validation:**
- Manual check: simulate 3 consecutive batch failures; verify 2 retries per batch and FAILED status in progress.json
- Evidence: D-0010/evidence.md contains failure handling test log

**Dependencies:** T01.03
**Rollback:** TBD

---

### Checkpoint: End of Phase 1

**Purpose:** Gate for Phase 2 entry. All M1 (spec promises) and M2 (correctness/schema) deliverables must be complete and verified.
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/CP-P01-END.md
**Verification:**
- All 10 tasks (T01.01-T01.10) completed with passing verification at their respective tier levels
- Credential scanning (T01.06) critical path override verification passed with no secret leakage
- Scanner schema (T01.08, T01.09) validated with Phase-1 and Phase-2 fixtures
**Exit Criteria:**
- Evidence artifacts exist for D-0001 through D-0010
- No STRICT-tier task has unresolved quality-engineer findings
- Batch checkpointing (T01.03) and retry handling (T01.10) tested with interrupt/failure scenarios
