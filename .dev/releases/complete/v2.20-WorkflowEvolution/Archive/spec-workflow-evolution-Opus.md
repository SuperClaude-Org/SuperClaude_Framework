```yaml
---
title: "Workflow Evolution: Semantic Fidelity Gates & Cross-Boundary Validation"
version: "1.0.0"
status: draft
feature_id: FR-051
parent_feature: null
spec_type: refactoring
complexity_score: 0.65
complexity_class: moderate
target_release: v2.20
authors: [user, claude]
created: 2026-03-09
---
```

## 1. Problem Statement

The SuperClaude pipeline (spec → roadmap → tasklist → sprint execution) validates that work **looks right**, not that work **is right**. Every existing gate checks structural properties — file existence, frontmatter presence, minimum line counts, heading hierarchy — but no gate verifies that a downstream artifact **faithfully represents** its upstream source of truth.

This allows semantic drift to propagate silently: the roadmap can simplify, rename, or drop spec requirements, the tasklist can fabricate traceability IDs, and the sprint runner can complete tasks that no longer match the original intent. All gates report PASS because structural compliance is satisfied, even as semantic fidelity degrades at every handoff.

### 1.1 Evidence

| Evidence | Source | Impact |
|----------|--------|--------|
| 75% of v2.19 implementation deviations originated at roadmap generation (spec→roadmap seam) | Spec-Fidelity Gap Analysis §2.2 | Deviations propagated unchecked through tasklist into implementation |
| 29 deviations found at spec→roadmap boundary, 5 HIGH severity | Gap Analysis §2.4 | Function signatures, config fields, API contracts silently altered |
| `_cross_refs_resolve()` always returns True — cross-reference check is non-enforcing | Forensic Foundation §F-001, Gap Analysis §3.2 | MERGE_GATE semantic check is inert |
| `REFLECT_GATE` is STANDARD tier but includes semantic_checks — generic gate engine only runs semantics for STRICT | Codebase analysis of `validate_gates.py` + `pipeline/gates.py` | Validation semantic checks are silently skipped |
| Tasklist traceability IDs (R-xxx) are fabricated — don't exist in roadmap | Gap Analysis §2.6 TD-001 | Traceability field is meaningless downstream |
| Retrospective identifies PARTIAL→PASS promotion as highest priority, but next spec omits PARTIAL from status model | Forensic Foundation §F-005 | Learning loop temporally disconnected from prevention loop |
| Validation prompts exist in skill protocol refs but are not wired into CLI executor | Gap Analysis §3.6 | Conceptual validation infrastructure not connected to runtime |
| Semantic gates classified as advisory, structural gates as blocking (tasklist protocol SKILL.md lines 864-868) | Gap Analysis §3.6 | Policy-level explanation for why semantically wrong artifacts continue |

### 1.2 Scope Boundary

**In scope**:
- Spec-fidelity validation at spec→roadmap boundary (highest ROI)
- Roadmap-fidelity validation at roadmap→tasklist boundary (medium ROI)
- Gate engine fixes for existing broken/inert checks
- Normalized deviation report format as shared contract
- Retrospective-to-spec forward-constraint wiring
- Promoting semantic checks from advisory to blocking at artifact boundaries

**Out of scope**:
- Runtime/execution testing of generated code (different problem domain, requires fundamentally different infrastructure)
- Replacing LLM-as-judge validation entirely (structural+semantic hybrid is the correct approach)
- Sprint runner output↔tasklist acceptance criteria validation (depends on sprint runner architecture changes)
- Full end-to-end release fidelity audit (too token-intensive for pipeline integration; remains a manual tool)
- Changes to brainstorm, spec-panel, or adversarial stages
- Score aggregation / REVISE loop from validation reference doc (deferred to future release)

## 2. Solution Overview

Add **semantic fidelity harnesses** at the two highest-risk pipeline boundaries, fix existing broken gate checks, and wire retrospective findings into the prevention loop. Each harness is a prompt-based validation step that reads an upstream source-of-truth artifact alongside a downstream generated artifact, enumerates deviations in a normalized format, and gates on severity.

The approach follows the **correct validation layering principle**: each artifact is validated against its immediate upstream source of truth (roadmap against spec, tasklist against roadmap), not against the original spec. This preserves clean layering and prevents validation-layer coupling.

### 2.1 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Spec-fidelity placement | New step in roadmap generation pipeline (after test-strategy) | Extend validate pipeline; add to merge step prompt | Generation pipeline owns roadmap quality; validate pipeline checks holistic readiness. Mixing concerns would blur responsibility. Placing after test-strategy means we don't waste tokens on test-strategy if spec-fidelity fails. |
| Tasklist fidelity placement | New subcommand `superclaude tasklist validate` | Embed in tasklist skill protocol; add to sprint runner pre-check | CLI subcommand is testable, composable, and doesn't require skill protocol changes. Sprint runner shouldn't own upstream validation. |
| Deviation report format | Structured markdown with YAML frontmatter + table rows | JSON output; Python dataclass serialization | Markdown is consistent with all existing pipeline artifacts. YAML frontmatter enables gate checking. Table format is human-readable and LLM-parseable. |
| Gate blocking on HIGH severity | Block if `high_severity_count > 0` | Block on total count threshold; score-based threshold | Binary on HIGH severity is unambiguous, deterministic from frontmatter, and matches the finding that HIGH deviations are the ones that cause downstream failures. |
| REFLECT_GATE tier fix | Promote to STRICT | Add special STANDARD+semantic mode to gate engine | Promoting to STRICT is a one-line change; modifying the gate engine adds complexity for one consumer. |
| Retrospective constraint wiring | Convention-based file inclusion in extract prompt | Database of retrospective findings; structured constraint format | File-based approach requires zero new infrastructure, follows existing pattern of file-based pipeline inputs, and is immediately testable. |

### 2.2 Workflow / Data Flow

**Current pipeline (no semantic fidelity checks):**
```
SPEC ──→ extract ──→ generate×2 ──→ diff ──→ debate ──→ score ──→ merge ──→ test-strategy
                                                                              ↓
                                                                    [auto-validate]
                                                                    reflect ──→ merge-report
```

**After this change:**
```
SPEC ──→ extract ──→ generate×2 ──→ diff ──→ debate ──→ score ──→ merge ──→ test-strategy
   │                                                                          ↓
   │                                                               spec-fidelity ← NEW
   │                                                               [SPEC_FIDELITY_GATE]
   └──────────────────────────────────(spec file passed to fidelity step)──────┘
                                                                          ↓
                                                                [auto-validate]
                                                                reflect (STRICT) ← FIXED
                                                                      ↓
                                                                merge-report

ROADMAP ──→ sc:tasklist ──→ TASKLIST_BUNDLE
                               ↓
                    tasklist validate ← NEW CLI subcommand
                    [TASKLIST_FIDELITY_GATE]
```

**Retrospective wiring:**
```
Prior release retrospective.md ──→ extract prompt (as "known issues" context)
                                        ↓
                                   EXTRACTION (now aware of prior failures)
```

## 3. Functional Requirements

### FR-051.1: Spec-Fidelity Harness (Post-Roadmap)

**Description**: Add a pipeline step after test-strategy that compares the merged roadmap against the original spec, enumerating deviations in a normalized format and blocking on HIGH-severity findings.

**Acceptance Criteria**:
- [ ] New prompt builder `build_spec_fidelity_prompt(spec_content: str, roadmap_content: str) -> str` in `roadmap/prompts.py`
- [ ] Prompt instructs model to compare every function signature, data model, gate criteria, CLI option, and NFR in spec against roadmap representation
- [ ] Prompt requires model to quote both spec and roadmap text for each deviation
- [ ] Prompt requires structured output with YAML frontmatter containing `high_severity_count`, `medium_severity_count`, `low_severity_count`, `total_deviations`
- [ ] Prompt requires deviation table with columns: `ID`, `Severity`, `Source Pair`, `Deviation`, `Spec Quote`, `Roadmap Quote`, `Impact`, `Recommended Correction`
- [ ] New gate `SPEC_FIDELITY_GATE` in `roadmap/gates.py` with enforcement tier STRICT
- [ ] Gate blocks if `high_severity_count > 0` (via semantic check on frontmatter value)
- [ ] New step `spec-fidelity` added to `_build_steps()` in `roadmap/executor.py` after test-strategy
- [ ] Step receives `spec_file` and `roadmap.md` (merge output) as inputs
- [ ] Step timeout: 600 seconds (comparable to merge step, may need full spec reading)
- [ ] Step retry_limit: 1
- [ ] Output file: `{output_dir}/spec-fidelity.md`
- [ ] Existing `--no-validate` flag skips only the validate pipeline, not spec-fidelity (spec-fidelity is a generation quality gate)

**Dependencies**: FR-051.4 (deviation report format)

### FR-051.2: Tasklist-Fidelity Validation

**Description**: Add a CLI subcommand `superclaude tasklist validate` that compares a tasklist bundle against its source roadmap, checking deliverable coverage, signature preservation, traceability ID validity, and dependency chain correctness.

**Acceptance Criteria**:
- [ ] New prompt builder `build_tasklist_fidelity_prompt(roadmap_content: str, tasklist_content: str) -> str` in a new or existing prompts module
- [ ] Prompt checks: every roadmap deliverable appears in tasklist, function signatures/dependencies preserved, traceability IDs reference real roadmap items, dependency chains match roadmap ordering
- [ ] Prompt requires same normalized deviation report format as FR-051.1
- [ ] New gate `TASKLIST_FIDELITY_GATE` with enforcement tier STRICT
- [ ] Gate blocks if `high_severity_count > 0`
- [ ] New CLI subcommand `superclaude tasklist validate <output-dir>` with options for `--roadmap-file` and `--tasklist-dir`
- [ ] Output file: `{output_dir}/tasklist-fidelity.md`
- [ ] Subcommand returns exit code 1 if HIGH-severity deviations found
- [ ] Can be invoked standalone or wired into future pipeline automation

**Dependencies**: FR-051.4 (deviation report format)

### FR-051.3: Gate Engine Fixes

**Description**: Fix existing broken or inert gate checks that undermine validation reliability.

**Acceptance Criteria**:
- [ ] `REFLECT_GATE` in `validate_gates.py` promoted from `STANDARD` to `STRICT` enforcement tier so semantic checks actually execute
- [ ] `_cross_refs_resolve()` in `roadmap/gates.py` changed from always-return-True to actual validation: extract heading anchors, find cross-references, return False if any reference targets a non-existent heading
- [ ] Existing tests updated to reflect STRICT enforcement behavior for REFLECT_GATE
- [ ] New tests added for `_cross_refs_resolve()` with both passing and failing inputs
- [ ] No regression in existing gate behavior for other gates

**Dependencies**: None

### FR-051.4: Normalized Deviation Report Format

**Description**: Define a shared deviation report format used by all fidelity harnesses, enabling consistent parsing, severity-based gating, deduplication, and audit trail generation.

**Acceptance Criteria**:
- [ ] YAML frontmatter schema:
  ```yaml
  source_pair: "spec→roadmap"  # or "roadmap→tasklist"
  high_severity_count: 0
  medium_severity_count: 0
  low_severity_count: 0
  total_deviations: 0
  upstream_file: "path/to/upstream"
  downstream_file: "path/to/downstream"
  ```
- [ ] Deviation table schema (markdown):
  ```
  | ID | Severity | Deviation | Upstream Quote | Downstream Quote | Impact | Recommended Correction |
  ```
- [ ] Severity definitions documented in prompt:
  - HIGH: Functional requirement missing, signature changed, constraint dropped, API contract broken
  - MEDIUM: Requirement simplified, parameter renamed, non-functional requirement softened
  - LOW: Formatting difference, section reordering, clarification added
- [ ] Gate semantic check function `_high_severity_count_zero(content: str) -> bool` that parses frontmatter and returns True only if `high_severity_count` is 0
- [ ] Format documented in a reference file accessible to prompt builders

**Dependencies**: None

### FR-051.5: Retrospective Forward-Constraint Wiring

**Description**: Wire retrospective findings from prior releases into the extraction prompt, breaking the temporal disconnect between discovery and prevention.

**Acceptance Criteria**:
- [ ] `build_extract_prompt()` in `roadmap/prompts.py` accepts optional `retrospective_content: str | None` parameter
- [ ] When retrospective content is provided, the extraction prompt includes a section: "Known Issues from Prior Releases" with the retrospective text and instruction to flag any spec requirements that touch areas where prior failures occurred
- [ ] `RoadmapConfig` extended with optional `retrospective_file: Path | None` field
- [ ] `_build_steps()` passes retrospective content to extract prompt when file exists
- [ ] CLI `roadmap run` accepts optional `--retrospective` flag pointing to a retrospective file
- [ ] If retrospective file doesn't exist, extraction proceeds normally (no error, no change to behavior)

**Dependencies**: None

## 4. Architecture

### 4.1 New Files

| File | Purpose | Dependencies |
|------|---------|-------------|
| `src/superclaude/cli/tasklist/__init__.py` | Tasklist CLI module init | None |
| `src/superclaude/cli/tasklist/commands.py` | `superclaude tasklist validate` CLI surface | tasklist/executor.py |
| `src/superclaude/cli/tasklist/executor.py` | Tasklist fidelity validation executor | pipeline/executor.py, pipeline/gates.py |
| `src/superclaude/cli/tasklist/prompts.py` | Tasklist fidelity prompt builder | Deviation report format |
| `src/superclaude/cli/tasklist/gates.py` | TASKLIST_FIDELITY_GATE definition | pipeline/models.py |
| `tests/roadmap/test_spec_fidelity.py` | Tests for spec-fidelity harness | roadmap/gates.py, roadmap/executor.py |
| `tests/tasklist/test_tasklist_fidelity.py` | Tests for tasklist fidelity validation | tasklist/ module |
| `tests/roadmap/test_gate_fixes.py` | Tests for gate engine fixes | roadmap/gates.py, validate_gates.py |

### 4.2 Modified Files

| File | Change | Rationale |
|------|--------|-----------|
| `src/superclaude/cli/roadmap/gates.py` | Fix `_cross_refs_resolve()` to actually validate; add `SPEC_FIDELITY_GATE` constant; add `_high_severity_count_zero()` semantic check | F-001 fix: non-enforcing check becomes enforcing; new gate for spec-fidelity step |
| `src/superclaude/cli/roadmap/validate_gates.py` | Promote `REFLECT_GATE` from STANDARD to STRICT | Fix: semantic checks on REFLECT_GATE are currently silently skipped |
| `src/superclaude/cli/roadmap/executor.py` | Add spec-fidelity step to `_build_steps()`; pass retrospective to extract step | FR-051.1 and FR-051.5 integration |
| `src/superclaude/cli/roadmap/prompts.py` | Add `build_spec_fidelity_prompt()`; extend `build_extract_prompt()` with optional retrospective parameter | New prompt for fidelity check; retrospective wiring |
| `src/superclaude/cli/roadmap/models.py` | Add `retrospective_file: Path | None` to `RoadmapConfig` | FR-051.5 config support |
| `src/superclaude/cli/roadmap/commands.py` | Add `--retrospective` option to `roadmap run`; register tasklist group | CLI surface for new features |
| `src/superclaude/cli/main.py` | Register `tasklist` command group | CLI entry point for tasklist validate |

### 4.3 Module Dependency Graph

```
pipeline/
├── models.py          ← GateCriteria, Step, StepResult, SemanticCheck (unchanged)
├── gates.py           ← gate_passed() (unchanged)
└── executor.py        ← execute_pipeline() (unchanged)

roadmap/
├── models.py          ← RoadmapConfig + retrospective_file (MODIFIED)
├── gates.py           ← SPEC_FIDELITY_GATE (NEW), _cross_refs_resolve (FIXED), _high_severity_count_zero (NEW)
├── validate_gates.py  ← REFLECT_GATE tier promotion (MODIFIED)
├── executor.py        ← spec-fidelity step, retrospective wiring (MODIFIED)
├── prompts.py         ← build_spec_fidelity_prompt (NEW), build_extract_prompt extended (MODIFIED)
├── validate_executor.py  (unchanged)
├── validate_prompts.py   (unchanged)
└── commands.py        ← --retrospective flag (MODIFIED)

tasklist/               ← NEW MODULE
├── __init__.py
├── commands.py        ← superclaude tasklist validate
├── executor.py        ← execute_tasklist_validate()
├── prompts.py         ← build_tasklist_fidelity_prompt()
└── gates.py           ← TASKLIST_FIDELITY_GATE
```

### 4.5 Data Models

```python
# Extension to RoadmapConfig (models.py)
@dataclass
class RoadmapConfig(PipelineConfig):
    spec_file: Path = Path(".")
    agents: list[AgentSpec] = field(default_factory=lambda: [
        AgentSpec("opus", "architect"),
        AgentSpec("haiku", "architect"),
    ])
    depth: Literal["quick", "standard", "deep"] = "standard"
    output_dir: Path = Path(".")
    retrospective_file: Path | None = None  # NEW

# Deviation report frontmatter schema (enforced by prompt, validated by gate)
# Not a Python dataclass — it's a prompt contract for LLM output
# YAML frontmatter fields:
#   source_pair: str           # "spec→roadmap" | "roadmap→tasklist"
#   high_severity_count: int
#   medium_severity_count: int
#   low_severity_count: int
#   total_deviations: int
#   upstream_file: str
#   downstream_file: str

# New semantic check function (gates.py)
def _high_severity_count_zero(content: str) -> bool:
    """Returns True (passes) only if high_severity_count is 0."""
    match = re.search(r"high_severity_count:\s*(\d+)", content)
    if not match:
        return False  # Missing field = fail
    return int(match.group(1)) == 0
```

### 4.6 Implementation Order

```
1. FR-051.4: Deviation report format         — No dependencies; defines shared contract
   FR-051.3: Gate engine fixes               — [parallel with step 1] No dependencies
2. FR-051.1: Spec-fidelity harness           — Depends on 1 (format + fixed gates)
   FR-051.5: Retrospective wiring            — [parallel with step 2] Independent
3. FR-051.2: Tasklist-fidelity validation    — Depends on 1 (format); independent of 2
4. Integration testing & documentation       — Depends on all above
```

## 5. Interface Contracts

### 5.1 CLI Surface

**Extended command:**
```
superclaude roadmap run <spec-file> [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--retrospective` | Path | None | Path to retrospective file from prior release; included in extraction prompt as known-issues context |

**New command:**
```
superclaude tasklist validate <output-dir> [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output-dir` | Path (positional) | required | Directory containing tasklist bundle |
| `--roadmap-file` | Path | `{output-dir}/../roadmap.md` | Path to source roadmap |
| `--tasklist-dir` | Path | `{output-dir}` | Directory containing tasklist phase files |
| `--model` | str | "" | Model override |
| `--max-turns` | int | 100 | Max Claude turns |
| `--debug` | bool | False | Enable debug output |

### 5.2 Gate Criteria

| Gate | Tier | Frontmatter | Min Lines | Semantic Checks |
|------|------|-------------|-----------|-----------------|
| `SPEC_FIDELITY_GATE` | STRICT | `high_severity_count`, `medium_severity_count`, `low_severity_count`, `total_deviations`, `source_pair`, `upstream_file`, `downstream_file` | 30 | `_high_severity_count_zero`, `_frontmatter_values_non_empty` |
| `TASKLIST_FIDELITY_GATE` | STRICT | Same as above | 30 | `_high_severity_count_zero`, `_frontmatter_values_non_empty` |
| `REFLECT_GATE` (modified) | STRICT (was STANDARD) | Unchanged | Unchanged | Existing checks now actually execute |

### 5.3 Deviation Report Contract

```yaml
---
source_pair: "spec→roadmap"
high_severity_count: 2
medium_severity_count: 5
low_severity_count: 3
total_deviations: 10
upstream_file: "spec-roadmap-validate.md"
downstream_file: "roadmap.md"
---

## Deviation Report

| ID | Severity | Deviation | Upstream Quote | Downstream Quote | Impact | Recommended Correction |
|----|----------|-----------|----------------|------------------|--------|----------------------|
| D-001 | HIGH | Missing config field `validate_dir` | "ValidateConfig includes validate_dir: Path" | Field absent from roadmap data model section | Implementation will lack typed path accessor | Add field to roadmap data model section |
| D-002 | MEDIUM | Parameter renamed | "`build_reflect_prompt(agent: str, ...)`" | "`build_reflect_prompt(roadmap: str, ...)`" | Agent-specific prompting not available | Restore `agent` parameter |

## Summary

- **HIGH**: {count} — blocking deviations requiring correction before downstream consumption
- **MEDIUM**: {count} — significant simplifications that may cause downstream issues
- **LOW**: {count} — minor differences unlikely to affect implementation
```

## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-051.1 | Spec-fidelity step execution time | ≤120 seconds per run | Wall-clock time of step |
| NFR-051.2 | Tasklist-fidelity validation time | ≤120 seconds per run | Wall-clock time of subcommand |
| NFR-051.3 | No regression in existing pipeline execution time | ≤5% increase in total pipeline time (excluding new step) | Comparison of pipeline time with/without spec-fidelity step |
| NFR-051.4 | Gate fix backward compatibility | All existing passing tests continue to pass | `uv run pytest tests/roadmap/` |
| NFR-051.5 | Deviation report parseability | Gate can extract severity counts from 100% of well-formed reports | Unit tests with varied report formats |

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LLM produces inconsistent deviation counts (frontmatter says 0 HIGH but table contains HIGH rows) | MEDIUM | MEDIUM | Gate checks frontmatter only; prompt emphasizes consistency requirement; add semantic check that cross-validates count vs table |
| Spec-fidelity step increases pipeline time significantly for large specs | LOW | LOW | 600s timeout with retry; specs >100KB could be summarized before comparison |
| `_cross_refs_resolve()` fix causes existing valid roadmaps to fail MERGE_GATE | MEDIUM | MEDIUM | Test against existing artifacts in `.dev/releases/complete/`; add warning-only mode initially if needed |
| Retrospective wiring biases extraction toward prior failures, missing new risks | LOW | LOW | Prompt frames retrospective as "areas to watch" not "requirements to add"; extraction retains its own analysis independence |
| Tasklist fidelity check requires reading multiple phase files, increasing token cost | LOW | MEDIUM | Concatenate tasklist-index.md with phase files into single input; limit to index + 2 most relevant phases |
| REFLECT_GATE promotion to STRICT causes existing valid validation reports to fail | MEDIUM | MEDIUM | Run REFLECT_GATE against existing validation artifacts before deploying; `_frontmatter_values_non_empty` is the only semantic check and should pass for well-formed reports |

## 8. Test Plan

### 8.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| `test_high_severity_count_zero_passes` | `tests/roadmap/test_gate_fixes.py` | Semantic check passes when high_severity_count is 0 |
| `test_high_severity_count_zero_fails` | `tests/roadmap/test_gate_fixes.py` | Semantic check fails when high_severity_count > 0 |
| `test_high_severity_count_missing_fails` | `tests/roadmap/test_gate_fixes.py` | Semantic check fails when field is absent |
| `test_cross_refs_resolve_valid` | `tests/roadmap/test_gate_fixes.py` | Fixed cross-ref check passes for valid references |
| `test_cross_refs_resolve_invalid` | `tests/roadmap/test_gate_fixes.py` | Fixed cross-ref check fails for dangling references |
| `test_cross_refs_resolve_no_refs` | `tests/roadmap/test_gate_fixes.py` | Cross-ref check passes when no references exist |
| `test_reflect_gate_is_strict` | `tests/roadmap/test_gate_fixes.py` | REFLECT_GATE enforcement tier is STRICT |
| `test_reflect_gate_semantic_checks_execute` | `tests/roadmap/test_gate_fixes.py` | Semantic checks actually run at STRICT tier |
| `test_spec_fidelity_gate_criteria` | `tests/roadmap/test_spec_fidelity.py` | SPEC_FIDELITY_GATE has correct frontmatter fields and tier |
| `test_spec_fidelity_prompt_includes_both_artifacts` | `tests/roadmap/test_spec_fidelity.py` | Prompt builder includes both spec and roadmap content |
| `test_spec_fidelity_prompt_deviation_format` | `tests/roadmap/test_spec_fidelity.py` | Prompt specifies normalized deviation report format |
| `test_build_steps_includes_spec_fidelity` | `tests/roadmap/test_spec_fidelity.py` | `_build_steps()` includes spec-fidelity step after test-strategy |
| `test_spec_fidelity_step_inputs` | `tests/roadmap/test_spec_fidelity.py` | Step receives spec_file and roadmap.md as inputs |
| `test_extract_prompt_without_retrospective` | `tests/roadmap/test_spec_fidelity.py` | Extract prompt unchanged when no retrospective provided |
| `test_extract_prompt_with_retrospective` | `tests/roadmap/test_spec_fidelity.py` | Extract prompt includes retrospective content when provided |
| `test_roadmap_config_retrospective_field` | `tests/roadmap/test_spec_fidelity.py` | RoadmapConfig accepts and stores retrospective_file |
| `test_tasklist_fidelity_gate_criteria` | `tests/tasklist/test_tasklist_fidelity.py` | TASKLIST_FIDELITY_GATE has correct fields and tier |
| `test_tasklist_fidelity_prompt_includes_both` | `tests/tasklist/test_tasklist_fidelity.py` | Prompt includes roadmap and tasklist content |

### 8.2 Integration Tests

| Test | Validates |
|------|-----------|
| `test_spec_fidelity_blocks_on_high_deviation` | Full step execution with gate: HIGH severity → pipeline halt |
| `test_spec_fidelity_passes_clean_roadmap` | Full step execution with gate: 0 HIGH → pipeline continues |
| `test_pipeline_includes_spec_fidelity_step` | End-to-end dry-run shows spec-fidelity in step plan |
| `test_retrospective_file_missing_no_error` | Pipeline runs normally when retrospective file doesn't exist |
| `test_reflect_gate_strict_enforcement` | REFLECT_GATE with invalid semantic content → gate fails |
| `test_cross_refs_resolve_in_merge_gate` | MERGE_GATE with dangling cross-reference → gate fails |

### 8.3 Manual / E2E Tests

| Scenario | Steps | Expected Outcome |
|----------|-------|-----------------|
| Spec-fidelity catches real deviation | 1. Run `roadmap run` on spec with known complex requirements 2. Inspect spec-fidelity.md | Report lists deviations between spec and roadmap with correct severity |
| Retrospective wiring affects extraction | 1. Create retrospective.md noting prior PARTIAL→PASS bug 2. Run `roadmap run --retrospective retrospective.md` 3. Inspect extraction.md | Extraction includes note about PARTIAL status handling |
| Tasklist fidelity validates real bundle | 1. Run `tasklist validate` on existing v2.19 artifacts | Report correctly identifies fabricated traceability IDs |

## 9. Migration & Rollout

- **Breaking changes**: Yes — `_cross_refs_resolve()` fix may cause previously-passing MERGE_GATE to fail for roadmaps with dangling cross-references. REFLECT_GATE promotion to STRICT may cause previously-passing validation reports to fail if `_frontmatter_values_non_empty` check was silently skipped.
- **Backwards compatibility**: Existing `roadmap run` and `roadmap validate` CLI invocations continue to work without changes. New spec-fidelity step adds ~60-120s to pipeline time. `--retrospective` flag is optional with no default.
- **Rollback plan**: Gate fixes are isolated to specific gate definitions; reverting is a one-line tier change. Spec-fidelity step can be disabled by removing it from `_build_steps()`. Tasklist validation is a new subcommand with no impact on existing flows.

## 10. Downstream Inputs

### For sc:roadmap
- New step in pipeline topology: `spec-fidelity` after `test-strategy`
- Pipeline now produces `spec-fidelity.md` as an artifact
- Pipeline blocks if HIGH-severity spec-fidelity deviations found

### For sc:tasklist
- New standalone validation subcommand: `superclaude tasklist validate`
- Produces `tasklist-fidelity.md` as an artifact
- Can be integrated into future automated tasklist generation pipelines

## 11. Open Items

| Item | Question | Impact | Resolution Target |
|------|----------|--------|-------------------|
| Cross-ref strictness | Should `_cross_refs_resolve()` fix be warning-first (log but don't block) for one release cycle before becoming blocking? | Medium — existing roadmaps may have dangling refs | Before implementation begins |
| Tasklist module location | Should tasklist validation live under `cli/tasklist/` (new module) or `cli/roadmap/` (extend existing)? | Low — organizational, not functional | During Phase 3 implementation |
| Deviation count cross-validation | Should gate verify that frontmatter counts match actual table row counts? | Medium — prevents LLM count inconsistency | During Phase 2 implementation |

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| Fidelity harness | A repeatable, automated validation wrapper that compares a downstream artifact against its upstream source of truth, emits normalized deviation findings, and gates on severity |
| Semantic gate | A gate check that validates content meaning/correctness, not just structural properties like file existence or line count |
| Seam | A handoff boundary between pipeline stages where information can be lost, simplified, or distorted |
| Deviation report | A normalized markdown document listing differences between an upstream and downstream artifact, with severity classifications |
| Proxy stacking | The accumulation of confidence signals that each measure a proxy for quality, creating compound false confidence |

## Appendix B: Reference Documents

| Document | Relevance |
|----------|-----------|
| `.dev/releases/current/v2.20-WorkflowEvolution/adversarial-forensic-validation/forensic-foundation-validated.md` | Primary diagnostic source (Weight 1.0) — validated findings F-001 through F-006 directly inform this spec's problem statement and solution design |
| `.dev/releases/current/v2.20-WorkflowEvolution/Archive/spec-fidelity-gap-analysis-merged.md` | Solution source (Weight 0.75) — Solutions A-D, gap map, and deviation report contract directly adopted into this spec |
| `.dev/releases/current/v2.20-WorkflowEvolution/Archive/05-workflow-meta-analysis.md` | Stage-by-stage analysis (Weight 0.5) — confidence inflation analysis and category error theory inform scope decisions |
| `.dev/releases/current/v2.20-WorkflowEvolution/Archive/adversarial-forensic-foundation/adversarial/refactor-plan.md` | Structural reference (Weight 0.4) — findings/theories/conflicts taxonomy influenced spec organization |
| `src/superclaude/skills/sc-roadmap-protocol/refs/validation.md` | Existing validation prompts not yet wired into CLI — Solution C from gap analysis |
| `src/superclaude/cli/pipeline/gates.py` | Generic gate engine — understanding of tier enforcement behavior informed FR-051.3 |
| `src/superclaude/cli/roadmap/validate_gates.py` | REFLECT_GATE definition — the STANDARD tier bug informed FR-051.3 |
