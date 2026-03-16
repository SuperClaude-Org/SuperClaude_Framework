# Phase 1 -- Pre-Sprint Setup

Validate sprint infrastructure, confirm all tool dependencies are accessible, and establish the OQ-006/OQ-008 decisions that govern scheduling and fallback policy for all downstream phases. No analysis work begins until this phase's gate criteria pass.

---

### T01.01 -- Verify Auggie MCP Connectivity to Both Repos

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001 |
| Why | Auggie MCP is the mandatory primary discovery and verification mechanism; both repos must be queryable before any analysis begins |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0001/evidence.md`

**Deliverables:**
- D-0001: Connectivity confirmation record stating both `/config/workspace/IronClaude` and `/config/workspace/llm-workflows` are queryable via Auggie MCP test query

**Steps:**
1. **[PLANNING]** Load context: identify both target repositories (`/config/workspace/IronClaude`, `/config/workspace/llm-workflows`) and Auggie MCP server endpoint
2. **[PLANNING]** Check dependencies: confirm Auggie MCP server is running and reachable
3. **[EXECUTION]** Execute a test `codebase-retrieval` query against `/config/workspace/IronClaude`; record response status and sample result
4. **[EXECUTION]** Execute a test `codebase-retrieval` query against `/config/workspace/llm-workflows`; record response status and sample result
5. **[EXECUTION]** If either query fails: apply OQ-008 multi-criteria check (timeout / 3 consecutive failures / coverage confidence <50%); activate Serena+Grep fallback if ANY criterion met; annotate fallback activation in evidence
6. **[VERIFICATION]** Manual check: both repos returned non-empty results OR fallback activation is documented with explicit annotation
7. **[COMPLETION]** Write connectivity confirmation to `artifacts/D-0001/evidence.md`; record fallback status

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0001/evidence.md` exists with `path_verified` status for both repositories recorded
- If fallback was activated, annotation is present in evidence with explicit OQ-008 criterion that triggered it
- Result is reproducible: same query on same repo returns same reachability status within session
- Connectivity status is documented with timestamp and query method used

**Validation:**
- Manual check: both `path_verified` fields present in `artifacts/D-0001/evidence.md` with non-empty status values
- Evidence: linkable artifact produced (`artifacts/D-0001/evidence.md`)

**Dependencies:** None
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier EXEMPT because this is a verification/check operation (read-only, no code modification). OQ-008 fallback criteria apply throughout all downstream phases.

---

### T01.02 -- Confirm Sprint CLI Functional with Start/End Flags

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002 |
| Why | `superclaude sprint run` with `--start`/`--end` flags is the execution mechanism; a non-functional CLI blocks all phase execution |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0002/evidence.md`

**Deliverables:**
- D-0002: CLI executor functional confirmation with no-op phase test result recorded

**Steps:**
1. **[PLANNING]** Load context: identify `superclaude sprint run` CLI location and available flags (`--start`, `--end`)
2. **[PLANNING]** Check dependencies: confirm CLI is installed and accessible in PATH
3. **[EXECUTION]** Execute a no-op phase test: `superclaude sprint run --start 1 --end 1` against a minimal test phase or dry-run mode
4. **[EXECUTION]** Record exit code, output, and any error messages
5. **[EXECUTION]** Verify `--start` and `--end` flags are accepted without error
6. **[VERIFICATION]** Manual check: CLI exits without error for no-op phase test; `--start`/`--end` flags parse correctly
7. **[COMPLETION]** Write CLI confirmation result to `artifacts/D-0002/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0002/evidence.md` exists with CLI test result recorded
- CLI accepts `--start` and `--end` flags without parse error (exit code does not indicate flag rejection)
- Test is repeatable: same CLI command produces same behavior on re-execution
- Result documents the exact CLI version or invocation path used

**Validation:**
- Manual check: `artifacts/D-0002/evidence.md` contains exit code and flag acceptance confirmation
- Evidence: linkable artifact produced (`artifacts/D-0002/evidence.md`)

**Dependencies:** None
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier EXEMPT — this is a CLI status check operation. If CLI is non-functional, all downstream execution is blocked; escalate immediately before proceeding.

---

### T01.03 -- Create artifacts/ Directory and Verify prompt.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003 |
| Why | The `artifacts/` directory is the designated output location for all 35+ sprint artifacts; `artifacts/prompt.md` is the source of LW component paths for Phase 4 |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [███████---] 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0003/evidence.md`

**Deliverables:**
- D-0003: Verification record confirming `artifacts/` directory structure exists and `artifacts/prompt.md` is readable and non-empty

**Steps:**
1. **[PLANNING]** Load context: identify expected `artifacts/` directory path and `artifacts/prompt.md` location
2. **[PLANNING]** Check dependencies: confirm write access to the output directory
3. **[EXECUTION]** Create `artifacts/` directory structure if it does not exist
4. **[EXECUTION]** Check that `artifacts/prompt.md` exists at the expected path
5. **[EXECUTION]** Verify `artifacts/prompt.md` is non-empty and readable; record file size or line count
6. **[VERIFICATION]** Direct test: `ls artifacts/prompt.md` exits 0; file is non-empty
7. **[COMPLETION]** Write verification result (directory path, prompt.md line count) to `artifacts/D-0003/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0003/evidence.md` exists confirming `artifacts/prompt.md` is readable with recorded line count
- `artifacts/` directory exists and is writable for subsequent phase artifact writes
- Verification is repeatable: same check produces same result on re-run within session
- Evidence records the exact path and file size/line count of `artifacts/prompt.md`

**Validation:**
- Direct test: `ls artifacts/prompt.md` exits 0 and file size > 0
- Evidence: linkable artifact produced (`artifacts/D-0003/evidence.md`)

**Dependencies:** None
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier STANDARD — create + verify operation. If `artifacts/prompt.md` is missing, Phase 4 LW strategy extraction is blocked; escalate immediately.

---

### T01.04 -- Record Dependency Readiness State Document

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | A documented dependency health record prevents ambiguous sprint start conditions and provides a gate artifact for the Phase 1 gate criteria |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [███████---] 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0004/spec.md`

**Deliverables:**
- D-0004: Dependency readiness document at `artifacts/D-0004/spec.md` covering all 5 dependencies: Auggie MCP, IronClaude repo access, llm-workflows repo access, prompt/source documents, downstream command expectations

**Steps:**
1. **[PLANNING]** Load context: identify all 5 dependencies listed in roadmap (Auggie MCP, IronClaude repo, llm-workflows repo, prompt/source documents, `/sc:roadmap`/`/sc:tasklist` command expectations)
2. **[PLANNING]** Check dependencies: gather results from T01.01 (Auggie MCP connectivity) and T01.03 (artifacts/prompt.md) as inputs
3. **[EXECUTION]** For each dependency, record: Name, Status (Ready/Degraded/Unavailable), Evidence source (task ID or observation), and Notes
4. **[EXECUTION]** For any Degraded or Unavailable dependency, record the fallback or blocker resolution path
5. **[EXECUTION]** Summarize overall sprint readiness: Ready / Blocked (with blocking dependency named)
6. **[VERIFICATION]** Direct test: document contains all 5 dependency rows with non-empty Status fields
7. **[COMPLETION]** Write dependency readiness document to `artifacts/D-0004/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0004/spec.md` exists with all 5 dependency rows, each containing Name, Status, Evidence source, and Notes
- Any Degraded or Unavailable dependency has an explicit fallback or blocker resolution path recorded
- Document is reproducible: same observation on same system produces same Status values
- Sprint readiness summary (Ready/Blocked) is present at the end of the document

**Validation:**
- Direct test: count rows in dependency table equals 5; Status field is non-empty for all rows
- Evidence: linkable artifact produced (`artifacts/D-0004/spec.md`)

**Dependencies:** T01.01, T01.03
**Rollback:** TBD (if not specified in roadmap)

---

### T01.05 -- Resolve OQ-006: Executor Parallelism Capability

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | OQ-006 determines whether Phase 3 and Phase 4 (IC/LW strategy extraction) can run concurrently; ambiguous result defaults to sequential execution |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0005/notes.md`

**Deliverables:**
- D-0005: OQ-006 decision record at `artifacts/D-0005/notes.md` stating whether Phase 3/4 parallelism is confirmed or defaulted to sequential

**Steps:**
1. **[PLANNING]** Load context: review `superclaude sprint run` CLI documentation or T01.02 evidence for parallelism support
2. **[PLANNING]** Identify the decision criteria: confirmed parallelism → Phase 3/4 concurrent; ambiguous or unsupported → Phase 3 then Phase 4 sequentially
3. **[EXECUTION]** Test or inspect whether the CLI executor supports concurrent phase execution
4. **[EXECUTION]** Apply default rule: if result is ambiguous, default to sequential execution
5. **[VERIFICATION]** Manual check: decision record states one of two outcomes with rationale
6. **[COMPLETION]** Write OQ-006 decision to `artifacts/D-0005/notes.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0005/notes.md` exists with OQ-006 decision (Confirmed-Parallel or Default-Sequential) and rationale
- Decision applies the roadmap default rule: ambiguous result → sequential
- Decision is stable: same test conditions produce same decision
- Decision is referenced in Phase 3 and Phase 4 tasklist files where scheduling is declared

**Validation:**
- Manual check: `artifacts/D-0005/notes.md` contains decision keyword (Confirmed-Parallel or Default-Sequential)
- Evidence: linkable artifact produced (`artifacts/D-0005/notes.md`)

**Dependencies:** T01.02
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier EXEMPT — this is a planning/decision resolution task, no code or analysis artifacts produced.

---

### T01.06 -- Resolve OQ-008: Auggie MCP Unavailability Definition

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | OQ-008 establishes the exact multi-criteria trigger for Auggie MCP fallback across all 9 phases; must be recorded before analysis begins |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0006/notes.md`

**Deliverables:**
- D-0006: OQ-008 decision record at `artifacts/D-0006/notes.md` confirming the merged multi-criteria definition and fallback activation rules

**Steps:**
1. **[PLANNING]** Load context: roadmap specifies the merged multi-criteria definition — Auggie is "unavailable" if ANY of: (a) timeout, (b) 3 consecutive query failures, (c) coverage confidence <50%
2. **[PLANNING]** Confirm the default: fallback activates on first ANY condition met
3. **[EXECUTION]** Record the three criteria explicitly with their measurable thresholds
4. **[EXECUTION]** Record the fallback: Serena MCP + Grep/Glob; annotate all fallback-derived claims
5. **[EXECUTION]** Record the downstream impact: Phase 7 flags unverified citations; re-run verification if Auggie is restored
6. **[VERIFICATION]** Manual check: three criteria with measurable thresholds are present in the decision record
7. **[COMPLETION]** Write OQ-008 decision to `artifacts/D-0006/notes.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0006/notes.md` exists with all three unavailability criteria, their measurable thresholds, and fallback activation rule
- Fallback tool chain (Serena MCP + Grep/Glob) is explicitly named
- Decision record is stable: criteria do not change across sessions
- Downstream impact (Phase 7 citation flagging) is documented

**Validation:**
- Manual check: three criteria with thresholds and fallback chain present in `artifacts/D-0006/notes.md`
- Evidence: linkable artifact produced (`artifacts/D-0006/notes.md`)

**Dependencies:** None
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier EXEMPT — this is a planning/decision recording task. The content is derived directly from roadmap text (no inference required).

---

### T01.07 -- Create Phase Tasklist Files and tasklist-index.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | Phase tasklist files and index are the execution control plane for the sprint; their existence is required before any phase can be dispatched via CLI |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [███████---] 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0007/evidence.md`

**Deliverables:**
- D-0007: Verification record confirming `phase-{1..9}-tasklist.md` and `tasklist-index.md` are present and non-empty in TASKLIST_ROOT

**Steps:**
1. **[PLANNING]** Load context: identify TASKLIST_ROOT and expected file names (`phase-1-tasklist.md` through `phase-9-tasklist.md`, `tasklist-index.md`)
2. **[PLANNING]** Check dependencies: confirm TASKLIST_ROOT is writable (from T01.03)
3. **[EXECUTION]** Verify each expected phase file exists in TASKLIST_ROOT with non-empty content
4. **[EXECUTION]** Verify `tasklist-index.md` exists in TASKLIST_ROOT with Phase Files table present
5. **[EXECUTION]** Record file count and any missing files
6. **[VERIFICATION]** Direct test: count of phase files = 9; `tasklist-index.md` contains Phase Files table
7. **[COMPLETION]** Write verification result to `artifacts/D-0007/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0007/evidence.md` exists with list of 10 files (9 phase files + index) confirmed present
- All 10 files are non-empty (size > 0)
- File list is reproducible: same directory scan produces same results on re-run
- Evidence records the exact file names and sizes verified

**Validation:**
- Direct test: `ls .dev/releases/current/cross-framework-deep-analysis/phase-*-tasklist.md | wc -l` equals 9
- Evidence: linkable artifact produced (`artifacts/D-0007/evidence.md`)

**Dependencies:** None
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 1

**Purpose:** Gate verification that all Phase 1 pre-sprint infrastructure is confirmed before any analysis begins.
**Checkpoint Report Path:** `.dev/releases/current/cross-framework-deep-analysis/checkpoints/CP-P01-END.md`

**Verification:**
- Both repos queryable via Auggie MCP (or fallback activated and documented in D-0001)
- `superclaude sprint run` CLI executes no-op phase without error (D-0002)
- `artifacts/prompt.md` is readable and non-empty; `artifacts/` directory exists (D-0003)

**Exit Criteria:**
- Dependency readiness document at `artifacts/D-0004/spec.md` contains all 5 dependencies with non-empty Status fields
- OQ-006 decision recorded at `artifacts/D-0005/notes.md` (Confirmed-Parallel or Default-Sequential)
- OQ-008 multi-criteria definition recorded at `artifacts/D-0006/notes.md` with three criteria and fallback chain
