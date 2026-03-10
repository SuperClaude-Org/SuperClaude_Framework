---
spec_source: "spec-roadmap-remediate.md"
generated: "2026-03-09T12:00:00Z"
generator: "claude-opus-4-6-extraction-agent"
functional_requirements: 32
nonfunctional_requirements: 14
total_requirements: 46
complexity_score: 0.72
complexity_class: "complex"
domains_detected: 5
risks_identified: 5
dependencies_identified: 6
success_criteria_count: 8
extraction_mode: "full"
pipeline_diagnostics: {elapsed_seconds: 108.0, started_at: "2026-03-09T19:44:11.178326+00:00", finished_at: "2026-03-09T19:45:59.193841+00:00"}
---

## Functional Requirements

- **FR-001**: Parse merged validation report (`validate/reflect-merged.md` or `validate/merged-validation-report.md`) to extract finding counts by severity (BLOCKING, WARNING, INFO) after the existing validation step completes. (§2.2)
- **FR-002**: Print a brief terminal summary of validation findings grouped by severity with finding IDs and descriptions. (§2.2)
- **FR-003**: Present an interactive user prompt with four options: `[1] BLOCKING only`, `[2] BLOCKING + WARNING`, `[3] All`, `[n] Skip remediation`. (§2.2)
- **FR-004**: When user selects `n`, end the pipeline and save state as `validated-with-issues`. (§2.2)
- **FR-005**: When user selects 1, 2, or 3, continue to the remediate step with the selected severity scope. Mark findings outside the chosen scope as SKIPPED. (§2.2)
- **FR-006**: When 0 BLOCKING and 0 WARNING findings exist, skip the user prompt entirely. If also 0 INFO, proceed to certify with a no-op. If INFO findings exist, skip remediation and proceed to certify. (§2.2)
- **FR-007**: Parse merged validation reports into structured `Finding` dataclass objects with fields: id, severity, dimension, description, location, evidence, fix_guidance, files_affected, status, agreement_category. (§2.3.1)
- **FR-008**: Filter findings based on user-selected scope: Option 1 filters to BLOCKING only; Option 2 to BLOCKING + WARNING; Option 3 to all findings with fix guidance. (§2.3.2)
- **FR-009**: Implement zero-findings guard: when filtering produces 0 actionable findings, emit `remediation-tasklist.md` with `actionable: 0` and all entries SKIPPED, then certify produces `certified: true` vacuously. (§2.3.2)
- **FR-010**: Always mark findings with NO_ACTION_REQUIRED or OUT_OF_SCOPE status as SKIPPED regardless of user selection. (§2.3.2)
- **FR-011**: Group actionable findings by their primary target file for agent batching. All findings for a single file go to one agent. (§2.3.3)
- **FR-012**: Run remediation agents targeting different files in parallel. (§2.3.3)
- **FR-013**: For cross-file findings, include the finding in both agents' prompts with file-specific fix guidance and a note that the other file's fix is handled separately. (§2.3.3, §2.3.4)
- **FR-014**: Construct agent prompts with: target file path, per-finding details (id, severity, description, location, evidence, fix_guidance), and constraints section. (§2.3.4)
- **FR-015**: Enforce editable file constraint: remediation agents may ONLY edit `roadmap.md`, `extraction.md`, `test-strategy.md`. (§2.3.5)
- **FR-016**: Emit `remediation-tasklist.md` with YAML frontmatter (type, source_report, source_report_hash, generated, total_findings, actionable, skipped) and per-finding status entries grouped by severity. (§2.3.6)
- **FR-017**: Present the remediate step as a single Step to `execute_pipeline()` with Step ID `remediate`, output file `remediation-tasklist.md`, and `REMEDIATE_GATE`. (§2.3.7)
- **FR-018**: Internally manage remediation orchestration: parse → filter → group → snapshot → spawn → collect → rollback-on-failure. (§2.3.7)
- **FR-019**: Use `ClaudeProcess` directly for internal agent spawning (not `execute_pipeline()`), matching `validate_executor.py` pattern. (§2.3.7)
- **FR-020**: Implement `REMEDIATE_GATE` with required frontmatter fields, min 10 lines, STRICT enforcement, and semantic checks for non-empty values and all-actionable-have-status. (§2.3.7)
- **FR-021**: Before spawning agents, snapshot all target files to `<file>.pre-remediate` for rollback capability. (§2.3.8)
- **FR-022**: On ANY agent failure (non-zero exit or timeout): halt remaining agents, rollback all files from snapshots, mark failed and cross-file findings as FAILED, set step status to FAIL, halt pipeline. (§2.3.8)
- **FR-023**: On full success: delete `.pre-remediate` snapshots and set all targeted findings to FIXED. (§2.3.8)
- **FR-024**: Implement a single-agent scoped certification review that receives only relevant sections surrounding each finding's location (not full file content). (§2.4.2)
- **FR-025**: Emit `certification-report.md` with YAML frontmatter (findings_verified, findings_passed, findings_failed, certified, certification_date) and a per-finding results table with PASS/FAIL and justification. (§2.4.3)
- **FR-026**: On all findings passing certification, update state to `certified: true`, `tasklist_ready: true`. Pipeline completes successfully. (§2.4.4)
- **FR-027**: On some findings failing certification, update state to `certified-with-caveats`. Pipeline completes without looping. (§2.4.4)
- **FR-028**: Implement `CERTIFY_GATE` with required frontmatter fields, min 15 lines, STRICT enforcement, and semantic checks for non-empty values and per-finding table presence. (§2.4.5)
- **FR-029**: Extend `.roadmap-state.json` with new step entries for `remediate` and `certify` including all specified metadata fields. (§3.1)
- **FR-030**: Support `--resume` for new steps: skip validate→remediate if gate passes; verify `source_report_hash` for stale tasklist detection; skip certify if gate passes. (§3.2)
- **FR-031**: Implement fallback parser for individual reflect reports when merged report is unavailable, with deduplication via location-match (same file, within 5 lines) and severity-resolution (higher severity wins). (§OQ-003)
- **FR-032**: Handle user prompt in `execute_roadmap()` (not inside `execute_pipeline()`) to preserve the non-interactive contract of `execute_pipeline()`. (§2.5)

## Non-Functional Requirements

- **NFR-001**: Agent execution timeout of 300 seconds per remediation agent. (§2.3.4)
- **NFR-002**: Single retry on agent failure, consistent with other pipeline steps. (§2.3.4)
- **NFR-003**: Context isolation: each agent subprocess receives only its prompt and `--file` inputs. No `--continue`, `--session`, or `--resume` flags. (§5.1)
- **NFR-004**: Pure prompts: all prompt builders must be pure functions with no I/O, no subprocess calls, no side effects. (§5.1)
- **NFR-005**: Atomic writes: all file writes must use tmp + `os.replace()` pattern. (§5.1)
- **NFR-006**: No new subprocess abstractions: reuse existing `ClaudeProcess` from `pipeline.process`. (§5.1)
- **NFR-007**: Unidirectional imports: `remediate_*` and `certify_*` modules may import from `pipeline.models` and `roadmap.models`, but NOT vice versa. (§5.1)
- **NFR-008**: Steps 10-11 (remediate + certify) must add ≤30% wall-clock time relative to steps 1-9 in the same run. (SC-006)
- **NFR-009**: `.roadmap-state.json` schema must remain backward-compatible — new fields are additive only. (SC-008)
- **NFR-010**: Model inheritance: remediation agents inherit model from parent pipeline config (same as validation agents). (§2.3.4)
- **NFR-011**: Certification agent receives only relevant sections (not full file content) to keep token cost low. (§2.4.2)
- **NFR-012**: No automatic remediation loop — single pass remediate, then certify, then done. User stays in control. (§2.4.4, §5.2)
- **NFR-013**: Remediation agents must preserve existing YAML frontmatter structure and markdown heading hierarchy. (§2.3.4)
- **NFR-014**: `execute_pipeline()` non-interactive contract must be preserved — user prompts handled externally. (§2.5)

## Complexity Assessment

**Score: 0.72** | **Class: complex**

**Scoring Rationale**:

| Factor | Score | Weight | Contribution |
|--------|-------|--------|-------------|
| Multi-agent orchestration (parallel remediation agents, batching by file) | 0.85 | 0.20 | 0.170 |
| State management (resume, hash validation, status lifecycle) | 0.75 | 0.15 | 0.113 |
| Error handling (rollback semantics, cross-file failure propagation) | 0.80 | 0.15 | 0.120 |
| Report parsing (multiple formats, fallback, deduplication) | 0.70 | 0.15 | 0.105 |
| Pipeline integration (new steps, gates, non-interactive contract) | 0.65 | 0.15 | 0.098 |
| Interactive prompt logic (tiered selection, zero-findings guard) | 0.50 | 0.10 | 0.050 |
| Certification (single-agent, structured output) | 0.45 | 0.10 | 0.045 |
| **Weighted Total** | | | **0.701** |

Rounded to **0.72** accounting for cross-cutting concerns (cross-file findings create coupling between agent batching, rollback, and certification logic).

The feature is complex because it introduces multi-agent orchestration with transactional rollback semantics, multi-format report parsing with deduplication, and pipeline state extensions — all within strict architectural constraints inherited from the existing pipeline.

## Architectural Constraints

1. **Context isolation**: Agent subprocesses receive only prompt + `--file` inputs; no `--continue`, `--session`, or `--resume` flags. (§5.1)
2. **Pure prompt functions**: All prompt builders (`remediate_prompts.py`, `certify_prompts.py`) must be pure functions — no I/O, subprocess calls, or side effects. (§5.1)
3. **Unidirectional imports**: `remediate_*` and `certify_*` modules may import from `pipeline.models` and `roadmap.models`, but NOT the reverse direction. (§5.1)
4. **Atomic file writes**: All writes use `tmp + os.replace()` pattern. (§5.1)
5. **No new subprocess abstractions**: Must reuse existing `ClaudeProcess` from `pipeline.process`. (§5.1)
6. **Editable file allowlist**: Remediation agents may ONLY edit `roadmap.md`, `extraction.md`, `test-strategy.md`. (§5.2)
7. **Non-interactive `execute_pipeline()`**: User prompts must be handled in `execute_roadmap()`, not inside `execute_pipeline()`. (§2.5)
8. **Internal dispatch for remediate**: `remediate_executor.py` uses `ClaudeProcess` directly, NOT `execute_pipeline()`, matching `validate_executor.py` pattern. (§2.3.7)
9. **Certify via `execute_pipeline()`**: Certify step runs as a standard single Step via `execute_pipeline()`. (§2.5)
10. **Backward-compatible state schema**: `.roadmap-state.json` changes must be additive only. (SC-008)
11. **No automatic loop**: Single-pass remediate → certify → done. No auto-retry cycle. (§5.2)

## Risk Inventory

1. **R-001** [Medium severity] **Remediation agent introduces new issues** — Probability: Medium, Impact: Medium. *Mitigation*: Certification step catches regressions; user can re-run full `roadmap validate` for comprehensive re-assessment.
2. **R-002** [High severity] **Report format changes break parser** — Probability: Low, Impact: High. *Mitigation*: Parser tests against multiple known formats (reflect-merged, merged-validation-report, individual reflect-* reports); graceful degradation with fallback parsing path.
3. **R-003** [Medium severity] **Cross-file findings cause conflicting edits** — Probability: Low, Impact: Medium. *Mitigation*: Batch-by-file strategy eliminates concurrent edits to the same file; cross-file fix guidance is scoped per-agent.
4. **R-004** [Low severity] **User interrupts during remediation** — Probability: Low, Impact: Low. *Mitigation*: Resume support picks up from last completed step; `.pre-remediate` snapshots enable manual rollback.
5. **R-005** [Low severity] **Certification agent is too lenient** — Probability: Medium, Impact: Low. *Mitigation*: Gate criteria enforce structured output format; user retains ability to re-run full adversarial validation.

## Dependency Inventory

1. **v2.20-WorkflowEvolution** — Pipeline infrastructure foundation. Provides `execute_pipeline()`, `ClaudeProcess`, `GateCriteria`, `SemanticCheck`, step model, `_auto_invoke_validate()` pattern, `_build_steps()`, `_save_state()`, `_apply_resume()`. (§spec frontmatter, §2.3.7, §2.5)
2. **`ClaudeProcess`** (from `pipeline.process`) — Subprocess abstraction for spawning Claude agents. Reused directly; no new abstractions allowed. (§5.1)
3. **`GateCriteria` / `SemanticCheck`** (from pipeline infrastructure) — Gate definition framework for `REMEDIATE_GATE` and `CERTIFY_GATE`. (§2.3.7, §2.4.5)
4. **`pipeline.models` / `roadmap.models`** — Existing model modules from which new modules may import (unidirectional). (§5.1)
5. **`validate_executor.py`** — Existing validation executor that returns structured finding counts. Serves as architectural pattern for `remediate_executor.py`. (§2.3.7, §4.2)
6. **`execute_roadmap()`** (from `executor.py`) — Main orchestration function to be extended with user prompt and new step wiring. (§2.5, §4.2)

## Success Criteria

1. **SC-001**: `roadmap run` completes all 12 steps (extract through certify) without manual intervention when user approves remediation at the interactive prompt. Acceptance: end-to-end integration test passes.
2. **SC-002**: ≥90% of BLOCKING findings receive PASS in the certification report. Measurement: `findings_passed / findings_verified` where severity is BLOCKING. Acceptance: ≥0.90 ratio.
3. **SC-003**: Certification correctly identifies unfixed findings — no false passes. Acceptance: test with deliberately unfixed findings verifies they are reported as FAIL.
4. **SC-004**: `--resume` correctly skips completed remediation/certification steps. Acceptance: resume from each possible state (post-validate, post-remediate, post-certify) behaves correctly, including stale hash detection.
5. **SC-005**: No edits to files outside the allowed set (`roadmap.md`, `extraction.md`, `test-strategy.md`). Acceptance: integration test verifies no other files modified after remediation.
6. **SC-006**: Steps 10-11 (remediate + certify) add ≤30% wall-clock time relative to steps 1-9. Acceptance: timing measurement in integration test shows ≤1.3x overhead.
7. **SC-007**: `remediation-tasklist.md` accurately reflects all findings and their final status (FIXED, FAILED, SKIPPED). Acceptance: parser round-trip test validates output matches expected format.
8. **SC-008**: `.roadmap-state.json` schema remains backward-compatible. Acceptance: existing consumers (tasklist generation, status queries) continue to function with new additive fields present.

## Open Questions

1. **OQ-NEW-001**: What happens if the user presses Ctrl+C during the remediation agent execution (between snapshot and completion)? The spec describes rollback on agent failure but doesn't explicitly address SIGINT handling. Are `.pre-remediate` snapshots cleaned up or left for manual recovery?

2. **OQ-NEW-002**: The spec defines three editable files (`roadmap.md`, `extraction.md`, `test-strategy.md`), but doesn't specify behavior if a finding's `files_affected` references a file outside this set (e.g., a finding referencing `debate-transcript.md`). Should such findings be silently SKIPPED, or should the parser emit a warning?

3. **OQ-NEW-003**: The `source_report_hash` field in `remediation-tasklist.md` is used for stale detection during `--resume`, but the spec doesn't define which hash algorithm is used. SHA-256 is mentioned once in §3.2 but not formally specified in the frontmatter schema.

4. **OQ-NEW-004**: The deduplication logic for fallback parsing (§OQ-003) uses "within 5 lines" as the proximity threshold, but section references (e.g., "§3.1") require resolving section boundaries to line numbers. How is this resolution performed? Is there an existing utility, or does the parser need to scan the target file?

5. **OQ-NEW-005**: The spec states the certify step runs via `execute_pipeline([certify_step])` (§2.5), but the remediate step uses internal dispatch. If remediate fails and the pipeline halts (§2.3.8), does the certify step's gate need to handle the case where `certification-report.md` doesn't exist (vs. exists but has failures)?

6. **OQ-NEW-006**: The `Finding.agreement_category` field (BOTH_AGREE, ONLY_A, ONLY_B, CONFLICT) comes from the adversarial validation's multi-agent consensus. How should findings with CONFLICT agreement be treated during remediation — should conflicting fix guidance be flagged to the user, or does the merged report already resolve conflicts?

7. **OQ-NEW-007**: The spec mentions `schema_version: 2` in `.roadmap-state.json` (§3.1) but doesn't state whether this is bumped from the current version or is the existing version. If bumped, backward compatibility (SC-008) requires migration logic for consumers reading version 1.
