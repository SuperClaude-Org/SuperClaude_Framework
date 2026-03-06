# Phase 4 -- Validation and Budget Controls

Merge findings and run stratified revalidation for consistency (M6), implement practical budget governance with predictable degradation behavior (M7), and deliver operator-facing reliability and output usability guarantees (M8). This phase ensures quality, resilience, and usability.

---

### T04.01 -- Implement cross-phase deduplication and consolidation of audit findings

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027 |
| Why | AC18 (supporting) requires findings from surface, structural, and cross-cutting phases to be deduplicated and merged into a single consolidated view. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | across, system-wide |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0027/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0027/evidence.md

**Deliverables:**
- Consolidation engine that deduplicates findings across phases using file-path keying, merges evidence from multiple phases, and resolves conflicting classifications by highest-confidence-wins rule

**Steps:**
1. **[PLANNING]** Define dedup key: file_path is primary key; findings for same file across phases are merged
2. **[PLANNING]** Define conflict resolution: when phases disagree on classification, highest-confidence classification wins
3. **[EXECUTION]** Implement dedup engine that groups findings by file_path and merges evidence records
4. **[EXECUTION]** Implement conflict resolver that selects highest-confidence classification and logs conflicts
5. **[EXECUTION]** Output consolidated findings with merged evidence and conflict resolution log
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify no duplicate file entries in output and conflicts resolved correctly
7. **[COMPLETION]** Document consolidation rules in D-0027/spec.md

**Acceptance Criteria:**
- Consolidated output has exactly one entry per file path, verified by uniqueness check
- Conflicting classifications are resolved by highest confidence, verified by test with conflicting fixture
- Evidence from all phases is merged into the consolidated entry (no evidence loss)
- Consolidation rules documented in D-0027/spec.md

**Validation:**
- Manual check: consolidate findings with 2 conflicting classifications for same file; verify highest-confidence wins
- Evidence: D-0027/evidence.md contains consolidation log with conflict resolutions

**Dependencies:** T03.06, T03.07, T03.08
**Rollback:** TBD

---

### T04.02 -- Implement stratified 10% spot-check validation with re-classification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028 |
| Why | AC6 requires a stratified 10% validation pass on consolidated findings to measure classification consistency. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | audit, compliance |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0028 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0028/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0028/evidence.md

**Deliverables:**
- Post-consolidation spot-check validator that samples 10% of consolidated findings stratified by tier, re-classifies them independently, and reports consistency rate

**Steps:**
1. **[PLANNING]** Define stratified sampling: proportional to tier distribution in consolidated findings
2. **[PLANNING]** Define consistency metric: percentage of sampled files where re-classification matches consolidated classification
3. **[EXECUTION]** Implement stratified sampler drawing from consolidated output (reuse T01.05 sampling logic)
4. **[EXECUTION]** Implement independent re-classification of sampled files using fresh evidence gathering
5. **[EXECUTION]** Compute and report consistency rate with per-tier breakdown
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify sample size >= 10% and consistency rate computation correctness
7. **[COMPLETION]** Document validation methodology in D-0028/spec.md

**Acceptance Criteria:**
- Sample size is >= 10% of consolidated findings, verified by count comparison
- Re-classification uses independent evidence gathering (not cached results from original classification)
- Consistency rate is reported with per-tier breakdown (e.g., "Tier-1: 95%, Tier-2: 88%")
- Validation methodology documented in D-0028/spec.md

**Validation:**
- Manual check: verify sample contains proportional tier representation and consistency rate is computed
- Evidence: D-0028/evidence.md contains validation report with consistency rates

**Dependencies:** T04.01, T01.05
**Rollback:** TBD

---

### T04.03 -- Add consistency-rate language and calibration framing to validation output

| Field | Value |
|---|---|
| Roadmap Item IDs | R-029 |
| Why | AC6 (quality extension) requires that validation output uses consistency-rate language rather than accuracy claims to prevent misleading interpretation. |
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
| Deliverable IDs | D-0029 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0029/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0029/evidence.md

**Deliverables:**
- Updated validation output template that uses "consistency rate" (not "accuracy"), includes calibration notes, and states explicit limitations

**Steps:**
1. **[PLANNING]** Define required language: "consistency rate" replaces "accuracy"; add calibration disclaimer
2. **[PLANNING]** Draft calibration notes: explain that consistency measures self-agreement, not ground-truth accuracy
3. **[EXECUTION]** Update validation output template to use consistency-rate language throughout
4. **[EXECUTION]** Add calibration notes section with limitations disclaimer to validation report format
5. **[VERIFICATION]** Review output template for any remaining "accuracy" language; verify absence
6. **[COMPLETION]** Document language guidelines in D-0029/spec.md

**Acceptance Criteria:**
- Validation output uses "consistency rate" and never uses "accuracy", verified by text search
- Calibration notes section is present in validation report explaining methodology limitations
- Output template matches updated format with consistency-rate language
- Language guidelines documented in D-0029/spec.md

**Validation:**
- Manual check: search validation output for "accuracy"; verify zero matches
- Evidence: D-0029/evidence.md contains updated template sample

**Dependencies:** T04.02
**Rollback:** TBD

---

### T04.04 -- Produce coverage and validation output artifacts per AC2 and AC6

| Field | Value |
|---|---|
| Roadmap Item IDs | R-030 |
| Why | AC2 and AC6 require persistent output artifacts for coverage metrics and validation results that can be reviewed post-audit. |
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
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0030/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0030/evidence.md

**Deliverables:**
- Coverage artifact (JSON) and validation artifact (JSON) emitted at standard paths with schema-validated structure

**Steps:**
1. **[PLANNING]** Define coverage artifact schema: total_files, profiled_files, per_tier_counts, coverage_percentage
2. **[PLANNING]** Define validation artifact schema: sample_size, consistency_rate, per_tier_rates, calibration_notes
3. **[EXECUTION]** Implement coverage artifact emitter that writes schema-validated JSON
4. **[EXECUTION]** Implement validation artifact emitter that writes schema-validated JSON
5. **[VERIFICATION]** Validate emitted artifacts against their schemas; verify both files are written
6. **[COMPLETION]** Document artifact schemas in D-0030/spec.md

**Acceptance Criteria:**
- Coverage artifact is emitted as valid JSON at the standard path, verified by JSON parse
- Validation artifact is emitted as valid JSON at the standard path, verified by JSON parse
- Both artifacts pass schema validation against their defined schemas
- Artifact schemas documented in D-0030/spec.md

**Validation:**
- Manual check: verify both JSON files exist and parse successfully after a complete audit run
- Evidence: D-0030/evidence.md contains sample artifact content

**Dependencies:** T01.02, T04.02
**Rollback:** TBD

---

### T04.05 -- Implement directory assessment blocks for large directories exceeding threshold

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031 |
| Why | AC16 requires that directories exceeding a size threshold receive aggregate assessment blocks rather than per-file analysis. |
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
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0031/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0031/evidence.md

**Deliverables:**
- Directory assessment block generator that aggregates per-file findings into directory-level summaries for directories exceeding configurable file count threshold (default: 50 files)

**Steps:**
1. **[PLANNING]** Define threshold: directories with > 50 files receive aggregate assessment instead of per-file report entries
2. **[PLANNING]** Define aggregate metrics: file count, tier distribution, dominant classification, risk summary
3. **[EXECUTION]** Implement directory size detector and aggregate assessment block generator
4. **[EXECUTION]** Integrate assessment blocks into final report, replacing individual file entries for large directories
5. **[VERIFICATION]** Run on test fixture with a 100-file directory; verify aggregate block is emitted instead of 100 individual entries
6. **[COMPLETION]** Document threshold and aggregate format in D-0031/spec.md

**Acceptance Criteria:**
- Directories exceeding 50 files produce a single assessment block instead of per-file entries, verified by output inspection
- Assessment block contains file count, tier distribution, and dominant classification
- Directories below threshold still produce per-file entries (threshold enforcement is directional)
- Threshold and aggregate format documented in D-0031/spec.md

**Validation:**
- Manual check: audit a fixture with a 100-file directory; verify single assessment block in report
- Evidence: D-0031/evidence.md contains assessment block sample

**Dependencies:** T04.01
**Rollback:** TBD

---

### Checkpoint: Phase 4 / Tasks T04.01-T04.05

**Purpose:** Validate consolidation, validation, and output artifact generation before budget control implementation.
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/CP-P04-T01-T05.md
**Verification:**
- Consolidated output has unique file entries with merged evidence and resolved conflicts
- Validation output uses consistency-rate language with calibration notes
- Coverage and validation JSON artifacts are schema-valid
**Exit Criteria:**
- Tasks T04.01-T04.05 completed with passing verification
- No STRICT-tier task has unresolved sub-agent findings
- Directory assessment blocks tested with large-directory fixture

---

### T04.06 -- Implement token budget accounting and enforcement with per-phase tracking

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032 |
| Why | AC9 requires budget accounting that tracks token consumption per phase and enforces configurable limits. |
| Effort | M |
| Risk | High |
| Risk Drivers | performance, latency, system-wide |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0032/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0032/evidence.md

**Deliverables:**
- Budget accounting module that tracks token consumption per phase, compares against configurable limits, and triggers enforcement actions at threshold crossings

**Steps:**
1. **[PLANNING]** Define budget schema: total_budget, per_phase_limits, current_consumption, remaining, enforcement_thresholds (75%, 90%, 100%)
2. **[PLANNING]** Define enforcement actions: 75% = warn, 90% = degrade, 100% = halt phase
3. **[EXECUTION]** Implement token counter that tracks consumption per operation and aggregates per phase
4. **[EXECUTION]** Implement threshold enforcement that triggers warn/degrade/halt at configured percentages
5. **[EXECUTION]** Add budget status output to progress.json checkpoint data
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify threshold enforcement triggers correctly at 75%, 90%, and 100%
7. **[COMPLETION]** Document budget schema and enforcement rules in D-0032/spec.md

**Acceptance Criteria:**
- Token consumption is tracked per phase and recorded in progress.json, verified by checkpoint inspection
- Enforcement triggers at configured thresholds: warn at 75%, degrade at 90%, halt at 100%, verified by test
- Budget accounting is accurate within 5% of actual token usage, verified by comparison with external token counter
- Budget schema and enforcement rules documented in D-0032/spec.md

**Validation:**
- Manual check: run audit with low budget; verify warning at 75% and degradation at 90%
- Evidence: D-0032/evidence.md contains budget enforcement log

**Dependencies:** T01.03, T02.05
**Rollback:** TBD

---

### T04.07 -- Implement degradation sequence with ordered capability reduction

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033 |
| Why | AC9 (supporting) requires a deterministic degradation sequence that progressively reduces analysis depth as budget pressure increases. |
| Effort | M |
| Risk | High |
| Risk Drivers | performance, system-wide |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0033/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0033/evidence.md

**Deliverables:**
- Degradation sequence handler that reduces capabilities in order: (1) skip duplication matrix, (2) reduce validation sample to 5%, (3) skip Tier-C graph edges, (4) reduce profile to 4 core fields, (5) emit minimum viable report

**Steps:**
1. **[PLANNING]** Define degradation levels in order of activation: L1 skip duplication, L2 reduce validation, L3 skip Tier-C, L4 reduce profile, L5 minimum viable report
2. **[PLANNING]** Map degradation levels to budget thresholds from T04.06
3. **[EXECUTION]** Implement degradation handler that activates levels progressively as budget pressure increases
4. **[EXECUTION]** Ensure each degradation level produces a valid (reduced) output, not a broken output
5. **[EXECUTION]** Log which degradation levels were activated and what was skipped
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify each degradation level produces valid output and logs correctly
7. **[COMPLETION]** Document degradation sequence in D-0033/spec.md

**Acceptance Criteria:**
- Degradation activates in defined order (L1 through L5), verified by log inspection under budget pressure
- Each degradation level produces valid (reduced) output, not errors or missing sections
- Degradation log records which levels activated and what capabilities were skipped
- Degradation sequence documented in D-0033/spec.md with level definitions

**Validation:**
- Manual check: trigger L3 degradation via budget constraint; verify Tier-C edges skipped and output valid
- Evidence: D-0033/evidence.md contains degradation activation log

**Dependencies:** T04.06, T03.06, T03.08
**Rollback:** TBD

---

### T04.08 -- Implement degrade-priority override allowing operators to protect specific capabilities

| Field | Value |
|---|---|
| Roadmap Item IDs | R-034 |
| Why | AC9 (supporting) requires operators to override default degradation order by marking capabilities as protected from degradation. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | system-wide |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0034 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0034/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0034/evidence.md

**Deliverables:**
- Override handler that accepts a list of protected capabilities via config and reorders the degradation sequence to skip protected items

**Steps:**
1. **[PLANNING]** Define override schema: list of capability names that should not be degraded
2. **[PLANNING]** Define reordering logic: protected capabilities skip their degradation level; next non-protected level activates instead
3. **[EXECUTION]** Implement override parser that reads protected capabilities from config
4. **[EXECUTION]** Integrate override into degradation handler from T04.07; reorder sequence to skip protected items
5. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify protected capabilities are preserved under budget pressure
6. **[COMPLETION]** Document override schema and behavior in D-0034/spec.md

**Acceptance Criteria:**
- Protected capability (e.g., duplication matrix) is not degraded even under budget pressure, verified by test
- Non-protected capabilities degrade in adjusted order when protected items are skipped
- Override configuration is validated at startup (invalid capability names rejected)
- Override schema and behavior documented in D-0034/spec.md

**Validation:**
- Manual check: protect duplication matrix; trigger degradation; verify matrix preserved while validation sample is reduced
- Evidence: D-0034/evidence.md contains override behavior test log

**Dependencies:** T04.07
**Rollback:** TBD

---

### T04.09 -- Add budget realism caveats to dry-run and report outputs

| Field | Value |
|---|---|
| Roadmap Item IDs | R-035 |
| Why | AC19 (supporting) requires that budget estimates include realism caveats acknowledging estimation uncertainty. |
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
| Deliverable IDs | D-0035 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0035/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0035/evidence.md

**Deliverables:**
- Budget caveat section added to dry-run output and final report that states estimation methodology limitations and expected variance range

**Steps:**
1. **[PLANNING]** Draft caveat language: estimates are based on file count heuristics, actual token usage may vary by 20-50%
2. **[PLANNING]** Identify insertion points: dry-run estimate output and final report budget section
3. **[EXECUTION]** Add caveat section to dry-run output template
4. **[EXECUTION]** Add caveat section to final report budget section
5. **[VERIFICATION]** Verify caveat language appears in both dry-run and report output
6. **[COMPLETION]** Document caveat language in D-0035/spec.md

**Acceptance Criteria:**
- Dry-run output includes budget realism caveat section, verified by text search
- Final report includes budget realism caveat section, verified by text search
- Caveat states estimation methodology and expected variance range
- Caveat language documented in D-0035/spec.md

**Validation:**
- Manual check: run dry-run; verify caveat section present in output
- Evidence: D-0035/evidence.md contains caveat section sample

**Dependencies:** T02.05, T04.06
**Rollback:** TBD

---

### T04.10 -- Implement report depth modes with summary, standard, and detailed output levels

| Field | Value |
|---|---|
| Roadmap Item IDs | R-036 |
| Why | AC10 requires configurable report depth so operators can choose between concise summaries and detailed per-file analysis. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | system-wide |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0036 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0036/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0036/evidence.md

**Deliverables:**
- Report depth controller that generates 3 output levels: summary (tier counts + top findings), standard (per-section findings with evidence), detailed (per-file profiles + full evidence chains)

**Steps:**
1. **[PLANNING]** Define depth levels: summary = tier counts + top 10 findings, standard = section-level findings, detailed = per-file profiles
2. **[PLANNING]** Define depth flag: `--depth summary|standard|detailed` with default `standard`
3. **[EXECUTION]** Implement report renderer with 3 depth modes sharing the same consolidated data
4. **[EXECUTION]** Implement depth flag parser and routing to appropriate renderer
5. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify each depth mode produces valid output conforming to its schema
6. **[COMPLETION]** Document depth modes in D-0036/spec.md

**Acceptance Criteria:**
- Summary mode produces report with tier counts and top 10 findings only, verified by section count
- Detailed mode produces per-file profiles with full evidence chains, verified by checking file-level entries
- Standard mode is the default when no `--depth` flag is provided
- Depth modes documented in D-0036/spec.md with output examples

**Validation:**
- Manual check: generate reports at all 3 depth levels; verify each has appropriate detail level
- Evidence: D-0036/evidence.md contains sample output at each depth level

**Dependencies:** T04.01, T04.04
**Rollback:** TBD

---

### Checkpoint: Phase 4 / Tasks T04.06-T04.10

**Purpose:** Validate budget controls, degradation logic, and report depth modes before resume and anti-lazy implementation.
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/CP-P04-T06-T10.md
**Verification:**
- Budget accounting tracks token consumption accurately and triggers enforcement at thresholds
- Degradation sequence activates in defined order and produces valid reduced output
- Report depth modes produce correct output at all 3 levels
**Exit Criteria:**
- Tasks T04.06-T04.10 completed with passing verification
- Override handler tested with protected capability under budget pressure
- Budget realism caveats present in both dry-run and report output

---

### T04.11 -- Implement resume semantics that recover interrupted audit runs from checkpoint data

| Field | Value |
|---|---|
| Roadmap Item IDs | R-037 |
| Why | AC3 requires resume capability that reliably recovers interrupted runs without re-processing completed work. |
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
| Deliverable IDs | D-0037 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0037/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0037/evidence.md

**Deliverables:**
- Resume controller that reads progress.json, identifies the last completed phase/batch, and resumes execution from the next pending unit, merging partial results with completed results

**Steps:**
1. **[PLANNING]** Define resume entry points: phase-level resume (skip completed phases) and batch-level resume (skip completed batches within a phase)
2. **[PLANNING]** Define result merging: combine partial results from interrupted phase with completed phase results
3. **[EXECUTION]** Implement resume controller that reads progress.json from T01.03 and determines resume point
4. **[EXECUTION]** Implement result merger that combines partial and completed results without duplication
5. **[EXECUTION]** Add tests: interrupt after phase 2, resume, verify phases 1-2 results preserved and phases 3+ execute
6. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify resume produces identical final output to uninterrupted run
7. **[COMPLETION]** Document resume semantics in D-0037/spec.md

**Acceptance Criteria:**
- Resume skips completed phases and batches, verified by execution log showing no re-processing
- Resumed run produces identical final output to an uninterrupted run on the same input, verified by diff
- Result merger handles partial phase results without duplication or loss
- Resume semantics documented in D-0037/spec.md

**Validation:**
- Manual check: interrupt a 3-phase run after phase 1; resume; verify phase 1 not re-executed and final output matches uninterrupted run
- Evidence: D-0037/evidence.md contains resume test comparison

**Dependencies:** T01.03, T04.01
**Rollback:** TBD

---

### T04.12 -- Implement anti-lazy distribution and consistency guards for classification output

| Field | Value |
|---|---|
| Roadmap Item IDs | R-038 |
| Why | AC18 (supporting) requires guards that detect and flag suspiciously uniform classification distributions (e.g., all KEEP) indicating lazy analysis. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | audit, compliance |
| Tier | STANDARD |
| Confidence | [███████░░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0038 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0038/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0038/evidence.md

**Deliverables:**
- Anti-lazy guard that flags batches where a single classification exceeds configurable uniformity threshold (default: 90%) and triggers re-analysis of flagged batches

**Steps:**
1. **[PLANNING]** Define uniformity threshold: if >90% of files in a batch receive the same classification, flag as suspicious
2. **[PLANNING]** Define re-analysis trigger: flagged batches are re-processed with elevated analysis depth
3. **[EXECUTION]** Implement distribution checker that computes per-batch classification distribution
4. **[EXECUTION]** Implement re-analysis trigger for batches exceeding uniformity threshold
5. **[VERIFICATION]** Test with a batch of 50 files all classified KEEP; verify flagging and re-analysis trigger
6. **[COMPLETION]** Document guard rules in D-0038/spec.md

**Acceptance Criteria:**
- Batches with >90% uniform classification are flagged, verified by test with all-KEEP fixture
- Flagged batches trigger re-analysis with elevated depth, verified by execution log
- Non-uniform batches (diverse classification) pass without flagging
- Guard rules documented in D-0038/spec.md

**Validation:**
- Manual check: submit a 50-file batch with 48 KEEP and 2 DELETE; verify flagging
- Evidence: D-0038/evidence.md contains guard trigger log

**Dependencies:** T04.01
**Rollback:** TBD

---

### T04.13 -- Implement final report section completeness checks per AC1 and AC16

| Field | Value |
|---|---|
| Roadmap Item IDs | R-039 |
| Why | AC1 and AC16 require that the final report contains all mandated sections; completeness must be verified before output. |
| Effort | M |
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
| Deliverable IDs | D-0039 |

**Artifacts (Intended Paths):**
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0039/spec.md
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0039/evidence.md

**Deliverables:**
- Report completeness checker that validates the final report contains all mandated sections (per AC1) and directory assessments (per AC16) before allowing output

**Steps:**
1. **[PLANNING]** Define mandated sections list from AC1: executive summary, findings by tier, action items, coverage metrics, validation results, dependency graph summary
2. **[PLANNING]** Define AC16 requirement: large directories have assessment blocks
3. **[EXECUTION]** Implement section presence checker that scans final report for each mandated section heading
4. **[EXECUTION]** Implement directory assessment checker that verifies large dirs have blocks (from T04.05)
5. **[VERIFICATION]** Spawn quality-engineer sub-agent to verify completeness check catches missing sections
6. **[COMPLETION]** Document mandated sections in D-0039/spec.md

**Acceptance Criteria:**
- Completeness check fails when any mandated section is missing, verified by test with incomplete report
- Completeness check passes when all sections are present, verified by test with complete report
- Directory assessments for large directories are verified as present
- Mandated sections list documented in D-0039/spec.md

**Validation:**
- Manual check: remove one section from a complete report; verify completeness check fails
- Evidence: D-0039/evidence.md contains pass/fail test results

**Dependencies:** T04.05, T04.10
**Rollback:** TBD

---

### Checkpoint: End of Phase 4

**Purpose:** Gate for Phase 5 entry. All M6 (consolidation/validation), M7 (budget controls), and M8 (reporting/resume) deliverables must be complete.
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/CP-P04-END.md
**Verification:**
- All 13 tasks (T04.01-T04.13) completed with passing verification
- Resume semantics produce identical output to uninterrupted runs
- Budget controls enforce thresholds correctly and degradation produces valid reduced output
**Exit Criteria:**
- Evidence artifacts exist for D-0027 through D-0039
- No STRICT-tier task has unresolved quality-engineer findings
- Report completeness checker validates all mandated sections
