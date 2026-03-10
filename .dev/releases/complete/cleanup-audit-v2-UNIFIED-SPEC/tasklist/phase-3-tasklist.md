# Phase 3 -- Structural Depth and Synthesis

Implement deep per-file profiling and evidence depth controls for high-risk decisions (M4), then synthesize static-tools, grep, and inference evidence into dependency and duplication intelligence (M5). This phase builds the analytical depth layer.

---

### T03.01 -- Implement 8-field profile generation for targeted file sets

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | AC10 requires detailed per-file profiling with 8 fields (imports, exports, size, complexity, age, churn, coupling, test-coverage) for structural analysis. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema, system-wide |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0017/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0017/evidence.md

**Deliverables:**
- Profile generator that computes all 8 fields (imports, exports, size, complexity, age, churn, coupling, test-coverage) for each file in a target set using static analysis and git history

**Steps:**
1. **[PLANNING]** Map each of the 8 fields to data sources: imports/exports from AST, size from stat, complexity from cyclomatic analysis, age/churn from git log, coupling from import graph, test-coverage from test file matching
2. **[PLANNING]** Check T02.03 static-tool cache integration for reusing AST and git results
3. **[EXECUTION]** Implement field extractors for each of the 8 profile fields
4. **[EXECUTION]** Implement profile aggregator that combines field values into the Phase-2 schema (T01.09)
5. **[EXECUTION]** Add tests validating all 8 fields are populated for a test fixture with known values
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify all 8 fields are non-null and schema-valid
7. **[COMPLETION]** Document field extraction methodology in D-0017/spec.md

**Acceptance Criteria:**
- Profile output contains all 8 fields with non-null values for each profiled file, verified by schema validation against Phase-2 schema (T01.09)
- Field values are deterministic: same file state produces identical profile across runs
- Profile generation leverages cached static-tool results from T02.03 (cache hit counter > 0 on repeated runs)
- Field extraction methodology documented in D-0017/spec.md with data source per field

**Validation:**
- Manual check: profile a test file with known import count; verify imports field matches expected value
- Evidence: D-0017/evidence.md contains full profile output for test fixture

**Dependencies:** T01.09, T02.03
**Rollback:** TBD

---

### T03.02 -- Implement file-type specific verification rules for classification decisions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | AC12 (supporting) requires that verification rules adapt to file type; configuration files need different evidence than source code files. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema, system-wide |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0018/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0018/evidence.md

**Deliverables:**
- File-type verification rule engine that applies different evidence requirements based on file extension and type classification (source, config, docs, test, binary)

**Steps:**
1. **[PLANNING]** Define file-type categories: source (.py, .ts, .js), config (.json, .yaml, .toml), docs (.md, .rst), test (test_*.py, *.test.ts), binary (images, compiled)
2. **[PLANNING]** Define evidence requirements per type: source needs import/export evidence, config needs reference evidence, docs need link validation
3. **[EXECUTION]** Implement rule engine with per-type verification rule sets
4. **[EXECUTION]** Integrate rule engine into classification pipeline so verification adapts to file type
5. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify correct rule selection for each file type category
6. **[COMPLETION]** Document verification rules per file type in D-0018/spec.md

**Acceptance Criteria:**
- Source files are verified using import/export evidence rules, verified by classification of a .py test fixture
- Config files are verified using reference evidence rules, verified by classification of a .json test fixture
- Rule engine correctly dispatches to file-type-specific rules, verified by test covering all 5 categories
- Verification rules documented in D-0018/spec.md with examples per file type

**Validation:**
- Manual check: classify a .py file and a .json file; verify different verification rules applied
- Evidence: D-0018/evidence.md contains rule dispatch log for multi-type fixture

**Dependencies:** T01.04, T03.01
**Rollback:** TBD

---

### T03.03 -- Implement signal-triggered full-file escalation for ambiguous classifications

| Field | Value |
|---|---|
| Roadmap Item IDs | R-019 |
| Why | AC17 (supporting) requires that ambiguous or low-confidence classifications trigger full-file read for deeper analysis rather than defaulting to a guess. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | performance, system-wide |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0019/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0019/evidence.md

**Deliverables:**
- Escalation trigger that detects low-confidence classification signals and initiates full-file read for deeper evidence gathering, bounded by configurable token limit

**Steps:**
1. **[PLANNING]** Define escalation signals: confidence < 0.6, conflicting evidence (import says KEEP, no references says DELETE), INVESTIGATE classification
2. **[PLANNING]** Define escalation bounds: maximum file size for full read (default: 500 lines), token budget per escalation
3. **[EXECUTION]** Implement signal detector that monitors classification confidence and evidence conflicts
4. **[EXECUTION]** Implement escalation handler that triggers full-file read and re-classification with additional evidence
5. **[EXECUTION]** Add token budget enforcement to prevent escalation from consuming excessive context
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify escalation triggers correctly and respects token bounds
7. **[COMPLETION]** Document escalation signals and bounds in D-0019/spec.md

**Acceptance Criteria:**
- Files with confidence < 0.6 trigger escalation, verified by test with low-confidence fixture
- Escalation does not exceed configured token budget, verified by token counter check
- Escalation produces updated classification with higher confidence or explicit INVESTIGATE status
- Escalation signals and bounds documented in D-0019/spec.md

**Validation:**
- Manual check: present a file with conflicting evidence; verify escalation triggers and re-classification occurs
- Evidence: D-0019/evidence.md contains escalation trigger log

**Dependencies:** T01.04, T03.01
**Rollback:** TBD
**Notes:** Token overuse in deep reads is a HIGH probability risk per roadmap; trigger-based escalation with bounded defaults mitigates this.

---

### T03.04 -- Implement tiered KEEP evidence enforcement with graduated requirements

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | AC5 requires KEEP classifications to carry evidence proportional to risk tier; high-risk KEEP needs stronger evidence than low-risk. |
| Effort | M |
| Risk | High |
| Risk Drivers | security, audit, compliance |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0020/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0020/evidence.md

**Deliverables:**
- Tiered KEEP evidence enforcer that requires 1 reference for low-risk, 2 references for medium-risk, and 3+ references for high-risk KEEP classifications

**Steps:**
1. **[PLANNING]** Define evidence tiers: low-risk KEEP requires 1 reference, medium requires 2, high requires 3+
2. **[PLANNING]** Map tier thresholds to file risk-tier output from T02.01 profiling
3. **[EXECUTION]** Implement tiered evidence gate in classification pipeline that checks reference count against risk tier
4. **[EXECUTION]** Implement escalation path for insufficient evidence: attempt additional evidence gathering before rejecting
5. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify correct enforcement at each tier boundary
6. **[COMPLETION]** Document tiered requirements in D-0020/spec.md

**Acceptance Criteria:**
- High-risk KEEP with fewer than 3 references is rejected by the gate, verified by test fixture
- Low-risk KEEP with 1 reference passes the gate, verified by test fixture
- Insufficient evidence triggers escalation before final rejection (escalation log present)
- Tiered requirements documented in D-0020/spec.md with threshold table

**Validation:**
- Manual check: submit a high-risk file with 2 references; verify rejection and escalation attempt
- Evidence: D-0020/evidence.md contains tier enforcement test log

**Dependencies:** T01.04, T02.01
**Rollback:** TBD

---

### T03.05 -- Implement environment variable key-presence matrix for configuration drift detection

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | AC7 (supporting) requires detection of env key drift between .env files, .env.example, and application code references. |
| Effort | M |
| Risk | High |
| Risk Drivers | credentials, secrets, security |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0021/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0021/evidence.md

**Deliverables:**
- Env key-presence matrix generator that cross-references keys across .env, .env.example, .env.production, and code references (process.env, os.environ) to identify drift

**Steps:**
1. **[PLANNING]** Define env file discovery: locate all .env* files in repository root and subdirectories
2. **[PLANNING]** Define code reference patterns: `process.env.KEY`, `os.environ["KEY"]`, `os.getenv("KEY")`
3. **[EXECUTION]** Implement env file parser that extracts key names (not values) from each .env* file
4. **[EXECUTION]** Implement code reference scanner that finds env key references in source files using grep patterns
5. **[EXECUTION]** Generate presence matrix: key x source (env, env.example, env.production, code) with present/absent markers
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify no secret values appear in matrix output (keys only)
7. **[COMPLETION]** Document matrix format and drift detection rules in D-0021/spec.md

**Acceptance Criteria:**
- Matrix output contains only key names, never secret values, verified by scanning output for value patterns
- Drift detection identifies keys present in code but missing from .env.example, verified by test fixture
- Drift detection identifies keys in .env but never referenced in code, verified by test fixture
- Matrix format documented in D-0021/spec.md with drift category definitions

**Validation:**
- Manual check: scan a fixture with 3 drift scenarios (missing from example, unused in code, missing from env); verify all detected
- Evidence: D-0021/evidence.md contains matrix output for test fixture

**Dependencies:** T01.06
**Rollback:** TBD
**Notes:** Critical Path Override: Yes -- env/credential paths require maximum verification. Non-disclosure policy: never output secret values.

---

### Checkpoint: Phase 3 / Tasks T03.01-T03.05

**Purpose:** Validate structural depth profiling and evidence enforcement before synthesis tasks.
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/CP-P03-T01-T05.md
**Verification:**
- 8-field profile generation produces valid output for test fixtures with all fields populated
- Tiered KEEP evidence enforcement correctly gates at each risk tier boundary
- Env key-presence matrix outputs keys only (no secret values) and detects all drift scenarios
**Exit Criteria:**
- Tasks T03.01-T03.05 completed with passing verification
- Critical path override tasks (T03.05) verified with no secret leakage
- Escalation handler (T03.03) tested with token budget enforcement

---

### T03.06 -- Build 3-tier dependency graph with confidence labels from static and grep evidence

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | AC12 requires a dependency graph with confidence-tiered edges combining static imports, grep references, and inferred relationships. |
| Effort | L |
| Risk | High |
| Risk Drivers | system-wide, across, breaking change |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0022/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0022/evidence.md

**Deliverables:**
- 3-tier dependency graph: Tier-A (static import, high confidence), Tier-B (grep reference, medium confidence), Tier-C (inferred, low confidence) with edges labeled by confidence tier

**Steps:**
1. **[PLANNING]** Define tier classification: Tier-A = AST-resolved imports, Tier-B = grep string matches, Tier-C = co-occurrence/naming inference
2. **[PLANNING]** Define graph output format: adjacency list with edge attributes (source, target, tier, confidence, evidence_type)
3. **[EXECUTION]** Implement Tier-A edge builder using AST import/export analysis from T02.03 cache
4. **[EXECUTION]** Implement Tier-B edge builder using grep pattern matching for string references
5. **[EXECUTION]** Implement Tier-C edge builder using co-occurrence and naming convention inference
6. **[EXECUTION]** Merge all tiers into unified graph with confidence labels and emit as structured output
7. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify graph has valid nodes, no self-loops, and correct tier labels
8. **[COMPLETION]** Document graph format and tier definitions in D-0022/spec.md

**Acceptance Criteria:**
- Graph output contains nodes for all profiled files with edges labeled by confidence tier (A/B/C)
- Tier-A edges are backed by AST evidence (import statement location), verified by spot-checking 3 edges
- Tier-C edges never promote to DELETE classification (policy enforcement), verified by classification pipeline integration test
- Graph format and tier definitions documented in D-0022/spec.md

**Validation:**
- Manual check: inspect graph for a known import relationship; verify Tier-A edge with correct source location
- Evidence: D-0022/evidence.md contains graph statistics (node count, edge count per tier)

**Dependencies:** T02.03, T03.01
**Rollback:** TBD
**Notes:** False deletes from low-confidence links is a MEDIUM/HIGH risk; Tier-C never promotes to DELETE per roadmap mitigation.

---

### T03.07 -- Implement cross-boundary dead code candidate detection logic

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | AC12 (supporting) requires identification of dead code candidates that span module boundaries using dependency graph evidence. |
| Effort | M |
| Risk | High |
| Risk Drivers | across, breaking change, system-wide |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0023/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0023/evidence.md

**Deliverables:**
- Dead code candidate detector that identifies exported symbols with zero cross-boundary importers using the 3-tier dependency graph

**Steps:**
1. **[PLANNING]** Define dead code candidate criteria: exported symbol with 0 Tier-A importers and 0 Tier-B references across module boundaries
2. **[PLANNING]** Define exclusion rules: entry points, framework hooks, dynamic imports marked as safe
3. **[EXECUTION]** Implement candidate detector that queries the dependency graph for zero-importer exports
4. **[EXECUTION]** Apply exclusion rules to filter false positives (entry points, framework convention exports)
5. **[EXECUTION]** Output candidate list with evidence: export location, searched boundaries, exclusion reasons for filtered items
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify no false positives from entry points or framework hooks
7. **[COMPLETION]** Document detection criteria and exclusion rules in D-0023/spec.md

**Acceptance Criteria:**
- Dead code candidates have zero Tier-A importers across all module boundaries, verified by graph query
- Entry points and framework hooks are excluded from candidates, verified by test with known entry point fixture
- Each candidate includes evidence (export location, boundary search scope), not just a file name
- Detection criteria and exclusion rules documented in D-0023/spec.md

**Validation:**
- Manual check: verify a known unused export appears in candidates; verify a known entry point is excluded
- Evidence: D-0023/evidence.md contains candidate list with evidence for test fixture

**Dependencies:** T03.06
**Rollback:** TBD

---

### T03.08 -- Build duplication matrix with consolidation threshold recommendations

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | AC12 (supporting) requires detection of code duplication with actionable consolidation thresholds. |
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
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0024/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0024/evidence.md

**Deliverables:**
- Duplication matrix showing file pairs with similarity scores above threshold, with consolidation recommendations for pairs above 80% similarity

**Steps:**
1. **[PLANNING]** Define similarity metric: structural similarity based on shared import sets and export overlap
2. **[PLANNING]** Define consolidation thresholds: >80% similarity = consolidate recommended, >60% = investigate, <60% = ignore
3. **[EXECUTION]** Implement pairwise similarity calculator using shared import/export sets from profile data
4. **[EXECUTION]** Generate matrix of file pairs above 60% threshold with similarity score and recommendation
5. **[VERIFICATION]** Run matrix generator on test fixture with known duplicate files; verify correct similarity scores
6. **[COMPLETION]** Document similarity metric and thresholds in D-0024/spec.md

**Acceptance Criteria:**
- Matrix correctly identifies known duplicate file pairs with similarity > 80%, verified against test fixture
- Consolidation recommendations are assigned based on threshold (>80% = consolidate, >60% = investigate)
- Matrix output includes file pair, similarity score, and recommendation, not just file names
- Similarity metric and thresholds documented in D-0024/spec.md

**Validation:**
- Manual check: verify a known duplicate pair appears with >80% similarity and consolidate recommendation
- Evidence: D-0024/evidence.md contains matrix output for test fixture

**Dependencies:** T03.01, T03.06
**Rollback:** TBD

---

### T03.09 -- Implement minimal docs audit for broken references and temporal staleness

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | AC14 requires a minimal documentation audit that checks for broken cross-references and temporally stale content. |
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
| Deliverable IDs | D-0025 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0025/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0025/evidence.md

**Deliverables:**
- Minimal docs auditor that scans markdown files for broken internal references (links to non-existent files) and flags docs with last-modified date older than configurable threshold (default: 365 days)

**Steps:**
1. **[PLANNING]** Define broken reference detection: parse markdown links, verify target file existence
2. **[PLANNING]** Define staleness threshold: last git-modified date > 365 days from current date
3. **[EXECUTION]** Implement markdown link parser that extracts internal file references from `[text](path)` patterns
4. **[EXECUTION]** Implement staleness checker using `git log --follow` for last-modified date per doc file
5. **[VERIFICATION]** Run auditor on test docs with known broken links and stale files; verify detection
6. **[COMPLETION]** Document audit rules in D-0025/spec.md

**Acceptance Criteria:**
- Broken internal links are detected and listed with source file and target path, verified by test fixture
- Stale docs (>365 days since last modification) are flagged with last-modified date
- Auditor produces a checklist of broken references suitable for manual remediation
- Audit rules documented in D-0025/spec.md

**Validation:**
- Manual check: scan test docs with 2 broken links and 1 stale doc; verify all 3 findings
- Evidence: D-0025/evidence.md contains audit output for test fixture

**Dependencies:** None
**Rollback:** TBD

---

### T03.10 -- Implement dynamic-import-safe classification policy with KEEP:monitor default

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | AC17 (supporting) requires that files accessed via dynamic imports are not falsely classified as DELETE; KEEP:monitor is the safe default. |
| Effort | M |
| Risk | High |
| Risk Drivers | breaking change, across |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0026 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0026/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0026/evidence.md

**Deliverables:**
- Dynamic import detector that identifies files loaded via `import()`, `require()` with variables, `__import__`, and `importlib`, and assigns KEEP:monitor classification to prevent false DELETE

**Steps:**
1. **[PLANNING]** Define dynamic import patterns: `import(variable)`, `require(variable)`, `__import__()`, `importlib.import_module()`, glob imports
2. **[PLANNING]** Define KEEP:monitor classification semantics: file is retained but flagged for manual review
3. **[EXECUTION]** Implement dynamic import detector using grep and AST patterns for each supported language
4. **[EXECUTION]** Integrate detector into classification pipeline: files matching dynamic import patterns receive KEEP:monitor
5. **[EXECUTION]** Add tests: file referenced only via dynamic import must not be classified DELETE
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify no dynamic-import files appear as DELETE candidates
7. **[COMPLETION]** Document detection patterns and classification policy in D-0026/spec.md

**Acceptance Criteria:**
- Files referenced via dynamic imports are classified KEEP:monitor, verified by test with dynamic import fixture
- Dynamic import patterns cover JavaScript (`import()`), Python (`__import__`, `importlib`), and variable `require()`
- No dynamic-import file appears in DELETE candidates, verified by scanning output
- Detection patterns and policy documented in D-0026/spec.md

**Validation:**
- Manual check: present a file loaded only via `import()` expression; verify KEEP:monitor classification
- Evidence: D-0026/evidence.md contains classification output for dynamic import fixtures

**Dependencies:** T03.06, T03.07
**Rollback:** TBD
**Notes:** Dynamic import false positives is a MEDIUM/HIGH risk per roadmap; KEEP:monitor default prevents false deletes.

---

### Checkpoint: Phase 3 / Tasks T03.06-T03.10

**Purpose:** Validate synthesis layer (dependency graph, dead code detection, duplication matrix, dynamic import safety) before consolidation phase.
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/CP-P03-T06-T10.md
**Verification:**
- 3-tier dependency graph has valid nodes, correct tier labels, and no self-loops
- Dead code candidates exclude known entry points and framework hooks
- Dynamic-import files are classified KEEP:monitor, never DELETE
**Exit Criteria:**
- Tasks T03.06-T03.10 completed with passing verification
- Tier-C edges verified to never promote to DELETE in classification pipeline
- Duplication matrix tested with known duplicate fixture

---

### Checkpoint: End of Phase 3

**Purpose:** Gate for Phase 4 entry. All M4 (structural depth) and M5 (cross-reference synthesis) deliverables must be complete.
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/CP-P03-END.md
**Verification:**
- All 10 tasks (T03.01-T03.10) completed with passing verification
- 8-field profile, 3-tier dependency graph, and dead code detection produce consistent results on shared test fixture
- Critical path override tasks (T03.05) verified with no secret leakage
**Exit Criteria:**
- Evidence artifacts exist for D-0017 through D-0026
- No STRICT-tier task has unresolved quality-engineer findings
- Synthesis outputs (graph, dead code candidates, duplication matrix) cross-validated for consistency
