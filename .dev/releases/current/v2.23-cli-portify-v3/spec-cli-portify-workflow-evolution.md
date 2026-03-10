---
title: "sc:cli-portify Workflow Evolution — Replace Code Generation with Spec-Driven Planning"
version: "1.1.0"
status: reviewed
feature_id: FR-060
parent_feature: cli-portify-protocol
spec_type: refactoring
complexity_score: 0.60
complexity_class: moderate
target_release: v2.20
authors: [user, claude]
created: 2026-03-09
---

# FR-060: sc:cli-portify Workflow Evolution

## 1. Problem Statement

The current `sc:cli-portify` protocol attempts to one-shot complex code generation across 12+ interdependent Python files (Phase 3) and wire them into the CLI infrastructure (Phase 4) based solely on a pipeline specification. This approach:

1. **Bypasses the project's own planning infrastructure** — does not use `sc:brainstorm` for gap analysis, `sc:spec-panel` for expert review, or `sc:roadmap` for milestone planning
2. **Is high-risk one-shot execution** — generating 12+ files with cross-file dependencies from templates has no incremental validation or recovery loop
3. **Produces the wrong deliverable** — outputs code directly instead of a reviewed specification that feeds the existing planning → implementation pipeline
4. **Lacks specification quality validation** — no expert panel review before committing to code generation, missing the gap/edge-case analysis that brainstorm and spec-panel provide

### 1.1 Evidence

| Evidence | Source | Impact |
|----------|--------|--------|
| Forensic analysis identifies seam failures as primary failure habitat | `forensic-foundation-validated.md` F-006 | Spec→code is the highest-risk seam; skipping spec review amplifies this |
| "Structural validation is systematically mistaken for semantic correctness" | `forensic-foundation-validated.md` F-001 | Template-based code generation validates structure but not semantic correctness |
| Phase 3 generates 12+ files with no incremental gate between files | `refactoring-spec-cli-portify.md` §2.4 | Single failure mid-generation can leave inconsistent partial output |
| No standardized spec template exists for release specifications | Backlog v4.0 research | Each spec uses ad-hoc structure, making quality inconsistent |

### 1.2 Scope Boundary

**In scope**:
- Replace Phase 3 (Code Generation) and Phase 4 (Integration) with spec synthesis + review phases
- Create a general-purpose release spec template
- Integrate automated brainstorm (multi-persona gap analysis) into the workflow
- Integrate spec-panel review (two passes: focus + critique) into the workflow
- Update the protocol skill, refs, and command shim accordingly

**Out of scope**:
- Modifying Phase 0 (Prerequisites), Phase 1 (Workflow Analysis), or Phase 2 (Pipeline Specification)
- Implementing the full v4.0 Spec Generator Framework
- Changes to `sc:brainstorm` or `sc:spec-panel` command definitions
- Changes to the pipeline/ or sprint/ infrastructure modules
- Building a replacement code generation system

## 2. Solution Overview

Replace the code generation phases with a spec-driven planning pipeline that produces a reviewed release specification as its deliverable. The spec is then consumed by a human → `sc:roadmap` → `sc:tasklist` → implementation workflow.

### 2.1 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Spec template scope | General-purpose release spec | Portify-specific template; Full v4.0 template system | Reusable across workflows without over-engineering; v4.0 is future work |
| Brainstorm integration | Embedded multi-persona behavioral patterns (Option C) | Interactive Socratic dialogue; Guided self-review; Direct sc:brainstorm invocation | Non-interactive keeps the pipeline automatable; embedding avoids fragile inter-skill coupling |
| Spec panel configuration | Convergent loop: focus+critique with max 3 iterations | Single-pass critique; Two-pass without loop; User-configurable per invocation | Convergence guarantees NFR-060.5 compliance; additive-only constraint prevents introduction of new issues |
| Code generation fate | Removed entirely | Move to separate command; Keep as optional Phase | Clean separation of planning from execution; the roadmap→implement path handles it |
| `--dry-run` behavior | Keep same (Phases 0-2 only) | Extend to include spec synthesis | Consistent with current behavior; user already expects analysis-only output |
| Template location | `src/superclaude/examples/release-spec-template.md` | In skill templates/; In shared templates/ | Examples directory is the canonical location for reusable reference files |
| Placeholder sentinel | `{{SC_PLACEHOLDER:name}}` | `{PLACEHOLDER}`; `__PLACEHOLDER__` | Unique sentinel avoids collision with legitimate template content in specs about templates |
| Quality score formula | `overall = mean(clarity, completeness, testability, consistency)` | Weighted average; Minimum of dimensions | Simple arithmetic mean is transparent and auditable; no dimension is structurally more important |
| CRITICAL finding disposition | Incorporate OR justify-dismiss (both count as "addressed") | Must incorporate (no dismissal); User override only | Allows handling false positives without bypassing quality gates |
| Incorporation constraint | Additive-only (append/extend, no rewrites) | Full rewrite allowed; Conservative rewrite | Prevents incorporation from introducing new issues that trigger convergence loops |

### 2.2 Workflow / Data Flow

**Current (v2.18)**:
```
Phase 0: Prerequisites → api-snapshot.yaml
    ↓
Phase 1: Workflow Analysis → portify-analysis.md + .yaml
    ↓ (user review)
Phase 2: Pipeline Specification → portify-spec.md + .yaml
    ↓ (user approval)
Phase 3: Code Generation → 12+ Python files         ← REMOVED
    ↓
Phase 4: Integration → main.py patch, tests, summary  ← REMOVED
```

**Proposed (v2.20)**:
```
Phase 0: Prerequisites → api-snapshot.yaml                [UNCHANGED]
    ↓
Phase 1: Workflow Analysis → portify-analysis.md + .yaml  [UNCHANGED]
    ↓ (user review)
Phase 2: Pipeline Specification → portify-spec.md + .yaml [UNCHANGED]
    ↓ (user approval)
Phase 3: Release Spec Synthesis                            [NEW]
    ├─ 3a: Template instantiation from release-spec-template.md
    ├─ 3b: Populate from Phase 1 analysis + Phase 2 spec
    ├─ 3c: Automated brainstorm (multi-persona gap analysis)
    └─ 3d: Incorporate brainstorm findings into spec
    → portify-release-spec.md (draft)
    ↓ (automatic)
Phase 4: Spec Panel Review (Convergent Loop)                [NEW]
    ├─ 4a: First pass — sc:spec-panel --focus correctness,architecture
    ├─ 4b: Incorporate focus findings (additive-only: append/extend, no rewrites)
    ├─ 4c: Critique pass — sc:spec-panel --mode critique
    ├─ 4d: Incorporate critique findings + quality score
    ├─ 4e: CRITICAL check — if unaddressed CRITICAL findings remain:
    │       loop back to 4a (max 3 iterations, then escalate to user)
    └─ 4f: Record iteration count + final quality scores
    → portify-release-spec.md (reviewed) + panel-report.md
    ↓ (user review gate)
DELIVERABLE: Reviewed release spec → human approves → sc:roadmap
```

## 3. Functional Requirements

### FR-060.1: Phase 3 — Release Spec Synthesis

**Description**: Generate a complete release specification by instantiating the release-spec-template.md with content derived from Phase 1 (analysis) and Phase 2 (pipeline specification), then running an automated brainstorm pass to identify gaps.

**Entry criteria**: Phase 2 contract validates (status: completed, all blocking checks passed, step_mapping contains ≥1 entry).

**Sub-steps**:

**3a. Template instantiation**: Load `src/superclaude/examples/release-spec-template.md`. Create a working copy at `{work_dir}/portify-release-spec.md`.

**3b. Content population**: Fill template sections from Phase 1 and Phase 2 outputs:

| Template Section | Source |
|-----------------|--------|
| 1. Problem Statement | Derive from source workflow's purpose + why portification is needed |
| 2. Solution Overview | Phase 2 pipeline architecture (step graph, executor design) |
| 2.2 Workflow | Phase 1 data flow diagram, adapted for the target pipeline |
| 3. Functional Requirements | One FR per generated pipeline step from Phase 2 step_mapping |
| 4. Architecture | Phase 2 module_plan (new files), Phase 0 prerequisites (modified files) |
| 4.5 Data Models | Phase 2 model designs (Config, Status, Result, MonitorState) |
| 4.6 Implementation Order | Phase 2 module dependency order |
| 5.2 Gate Criteria | Phase 2 gate_definitions |
| 5.3 Phase Contracts | Phase 1+2 contract schemas |
| 6. NFRs | Standard portification NFRs (sync execution, gate signatures, runner-authored truth) |
| 7. Risk Assessment | Derived from Phase 1 classification confidence scores + unsupported patterns |
| 8. Test Plan | Structural test plan from Phase 2 pattern coverage matrix |
| 10. Downstream Inputs | Themes for sc:roadmap, tasks for sc:tasklist |

**3c. Automated brainstorm**: Apply `sc:brainstorm` behavioral patterns (multi-persona: architect + analyzer + backend) against the draft spec as a non-interactive automated pass. This is NOT an invocation of the `sc:brainstorm` command (which is interactive/Socratic); instead, the cli-portify protocol embeds the brainstorm behavioral patterns directly — cycling through each persona to analyze the draft spec for gaps. The brainstorm:
- Explores gaps in the populated spec sections
- Identifies edge cases not covered by the analysis
- Flags ambiguities in requirements or architecture
- Checks cross-section consistency
- Outputs a structured gap analysis appended as `## Brainstorm Gap Analysis` section in the draft spec
- Each finding uses the format: `{gap_id, description, severity(high|medium|low), affected_section, persona}`

**Expected output**: The brainstorm MUST produce a `## Brainstorm Gap Analysis` section. If no gaps are identified, the section contains a summary stating "No gaps identified by [personas]. Spec coverage assessed as complete." with `gaps_identified: 0` in the contract. Zero gaps is a valid outcome — it does not block the pipeline.

**3d. Gap incorporation**: Review brainstorm findings and incorporate actionable ones into the relevant spec sections. Mark incorporated findings. Leave unresolvable items in Open Items (Section 11).

**Acceptance Criteria**:
- [ ] Draft spec follows release-spec-template.md structure completely
- [ ] All template sections populated (no `{{SC_PLACEHOLDER:*}}` values remain)
- [ ] Every Phase 2 step_mapping entry has a corresponding FR in Section 3
- [ ] Brainstorm gap analysis section present (zero gaps is valid; section states coverage assessment)
- [ ] If gaps identified, actionable findings incorporated into relevant sections

**Dependencies**: Phase 2 contract, release-spec-template.md

### FR-060.2: Phase 4 — Spec Panel Review (Convergent Loop)

**Description**: Run the generated release spec through `sc:spec-panel` behavioral patterns in a convergent review loop to ensure quality before human review. Like Phase 3's brainstorm, this embeds spec-panel behavioral patterns directly rather than invoking the `sc:spec-panel` command.

**Entry criteria**: Phase 3 produces a complete draft spec with brainstorm section present.

**Sub-steps**:

**4a. Focus pass**: Apply `sc:spec-panel` behavioral patterns with `--focus correctness,architecture` against `portify-release-spec.md`. This pass:
- Applies Fowler (architecture), Nygard (reliability/failure modes), Whittaker (adversarial), Crispin (testing) expert analysis
- Produces guard condition boundary tables for any guard conditions in the spec
- Validates pipeline dimensional analysis for multi-stage data flows
- Produces state variable registry if spec contains mutable state

**4b. Focus incorporation**: Review focus findings. "Incorporate" means: modify the relevant spec section text to address the finding (append clarifications, add missing definitions, tighten guard conditions). Incorporation MUST be additive-only — extend or append to spec sections, do not rewrite existing content. This prevents introducing new issues during incorporation.
- CRITICAL findings: MUST be addressed — either (a) incorporated into spec or (b) documented with a written justification for dismissal in the panel report. Both count as "addressed."
- MAJOR findings: incorporated into spec body.
- MINOR findings: go to Open Items if not immediately actionable.

**4c. Critique pass**: Apply `sc:spec-panel` behavioral patterns with `--mode critique` against the updated spec. This pass:
- Runs the full 11-expert panel in review sequence
- Produces quality scores (clarity, completeness, testability, consistency)
- Generates prioritized improvement recommendations

**4d. Critique incorporation**: Incorporate critique findings using the same additive-only rule. Record quality scores in spec frontmatter. Append full panel report as `panel-report.md`.

**4e. Convergence check**: After 4d, check for unaddressed CRITICAL findings. If any remain:
- Loop back to 4a with a maximum of **3 iterations** total
- Each iteration appends to the same `panel-report.md` (versioned sections: "Iteration 1", "Iteration 2", etc.)
- If CRITICAL findings persist after 3 iterations, escalate to user with a summary of unresolvable findings and set `status: partial`

**4f. Finalization**: Record final iteration count, quality scores, and `downstream_ready` status.

**Behavioral interface contract**: Phase 4 expects the following from spec-panel behavioral patterns:
- Focus pass MUST produce findings categorized as CRITICAL/MAJOR/MINOR with fields: `{finding_id, severity, expert, location, issue, recommendation}`
- Critique pass MUST produce quality scores as `{clarity: float, completeness: float, testability: float, consistency: float}`
- `overall` score is computed as `mean(clarity, completeness, testability, consistency)` — the arithmetic mean of the four dimension scores

**Acceptance Criteria**:
- [ ] Focus pass produces findings for correctness and architecture dimensions
- [ ] CRITICAL/MAJOR focus findings addressed (incorporated or justified-dismissed)
- [ ] Critique pass produces quality scores across 4 dimensions
- [ ] Final spec has no unaddressed CRITICAL findings (max 3 convergence iterations)
- [ ] `panel-report.md` artifact produced alongside final spec
- [ ] Spec frontmatter updated with quality scores and iteration count

**Dependencies**: FR-060.1 (Phase 3 output)

### FR-060.3: Remove Code Generation (Old Phase 3)

**Description**: Remove the code generation phase entirely from the protocol. All references to Phase 3 code generation in `SKILL.md`, `refs/code-templates.md` usage in the behavioral flow, and the template-based file generation logic are removed.

**Acceptance Criteria**:
- [ ] SKILL.md Phase 3 section replaced with Release Spec Synthesis
- [ ] SKILL.md Phase 4 section replaced with Spec Panel Review
- [ ] No behavioral instructions reference code file generation
- [ ] `refs/code-templates.md` no longer loaded by any phase (file preserved for reference but not active)

**Dependencies**: None — this is a deletion

### FR-060.4: Remove Integration Phase (Old Phase 4)

**Description**: Remove the integration phase (main.py patching, import verification, structural test generation, summary writing) from the protocol.

**Acceptance Criteria**:
- [ ] SKILL.md Phase 4 (old integration) replaced with Spec Panel Review
- [ ] No behavioral instructions reference main.py patching
- [ ] No behavioral instructions reference structural test generation
- [ ] Return contract updated to reflect spec output instead of code output

**Dependencies**: None — this is a deletion

### FR-060.5: Updated Return Contract

**Description**: The return contract changes to reflect spec output instead of code output.

```yaml
return_contract:
  contract_version: "2.20"  # schema version for downstream compatibility
  output_directory: <path>
  status: <success|partial|failed>
  failure_phase: <null|0|1|2|3|4>
  failure_type: <null|prerequisite_failed|analysis_incomplete|spec_invalid|
                 brainstorm_failed|brainstorm_empty|panel_review_failed|
                 convergence_exhausted>
  spec_file: <path to portify-release-spec.md>
  panel_report: <path to panel-report.md>
  quality_scores:
    clarity: <float 0-10>
    completeness: <float 0-10>
    testability: <float 0-10>
    consistency: <float 0-10>
    overall: <float 0-10>  # = mean(clarity, completeness, testability, consistency)
  source_step_count: <int>  # Phase 2 step_mapping entries (pipeline steps only)
  spec_fr_count: <int>      # total FRs in Section 3, including brainstorm-originated
  api_snapshot_hash: <string>
  resume_command: <string|null>
  resume_phase: <int|null>
  resume_substep: <string|null>  # e.g., "3c", "4a" for sub-step-level resume
  convergence_iterations: <int>  # number of Phase 4 review iterations (1-3)
  phase_timing:
    phase_3_seconds: <float|null>
    phase_4_seconds: <float|null>
  warnings: [<strings>]
  phase_contracts: [<paths to .yaml files>]
  downstream_ready: <true|false>  # true if overall quality >= 7.0
```

**Resume behavior**: When `resume_phase` and `resume_substep` are populated:
- Resume re-runs from the specified sub-step, preserving all prior phase artifacts
- Phase 3 resume: if `resume_substep=3c`, the populated spec from 3b is preserved and brainstorm re-runs
- Phase 4 resume: if `resume_substep=4a`, the draft spec from Phase 3 is preserved and review re-runs
- On user rejection at Phase 4 gate: user may (a) edit the spec manually and resume from Phase 4 (`resume_substep=4a`), (b) resume from Phase 3 to regenerate, or (c) abandon the portification

**Quality score computation**: `overall = mean(clarity, completeness, testability, consistency)`. If panel review fails mid-execution, quality scores are set to `0.0` (not null) and `downstream_ready` is `false`.

**Acceptance Criteria**:
- [ ] Return contract emitted on every invocation including failures
- [ ] Quality scores populated from spec-panel output (0.0 on failure)
- [ ] `downstream_ready` computed from overall quality threshold (>= 7.0)
- [ ] `spec_file` and `panel_report` paths correct
- [ ] `contract_version` field present
- [ ] `resume_substep` populated on resumable failures
- [ ] `phase_timing` populated for completed phases

### FR-060.6: Updated `--dry-run` Behavior

**Description**: `--dry-run` continues to execute Phases 0-2 only and emit contracts without proceeding to spec synthesis or panel review. This is unchanged from current behavior.

**Acceptance Criteria**:
- [ ] `--dry-run` stops after Phase 2
- [ ] Phase 0-2 contracts emitted
- [ ] No spec synthesis or panel review executed

### FR-060.7: Release Spec Template

**Description**: A general-purpose release spec template at `src/superclaude/examples/release-spec-template.md` that provides standardized structure for all release specifications across the project.

**Acceptance Criteria**:
- [ ] Template covers: frontmatter, problem statement, solution overview, functional requirements, architecture, interface contracts, NFRs, risk assessment, test plan, migration, downstream inputs, open items
- [ ] Template includes usage instructions
- [ ] Template works for new feature, refactoring, portification, and infrastructure specs
- [ ] Conditional sections clearly marked

**Dependencies**: None — template already created

## 4. Architecture

### 4.1 New Files

| File | Purpose | Dependencies |
|------|---------|-------------|
| `src/superclaude/examples/release-spec-template.md` | General-purpose release spec template | None |

### 4.2 Modified Files

| File | Change | Rationale |
|------|--------|-----------|
| `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` | Replace Phase 3 (Code Generation) with Release Spec Synthesis; Replace Phase 4 (Integration) with Spec Panel Review; Update return contract; Update boundaries | Core refactoring |
| `src/superclaude/skills/sc-cli-portify-protocol/refs/pipeline-spec.md` | Add section on how Phase 2 output feeds into spec template population | Phase 2→3 bridge |
| `src/superclaude/commands/cli-portify.md` | Update description to reflect spec-output (not code-output); Remove `--skip-integration` flag | Flag no longer applicable |
| `src/superclaude/skills/sc-cli-portify-protocol/decisions.yaml` | Add decisions for brainstorm integration model, panel configuration, template scope | Record design decisions |

### 4.3 Removed Sections

| Target | Reason | Migration |
|--------|--------|-----------|
| SKILL.md §Phase 3: Code Generation | Replaced by spec synthesis | Content informs template population logic in new Phase 3 |
| SKILL.md §Phase 4: Integration | Replaced by spec panel review | Not needed; integration happens post-roadmap |
| SKILL.md §Code Generation Principles | No longer applicable | Preserved in `refs/code-templates.md` for reference |
| Command `--skip-integration` flag | No integration phase exists | Remove from command shim and argument table |

### 4.4 Module Dependency Graph

```
commands/cli-portify.md
  └── invokes: skills/sc-cli-portify-protocol/SKILL.md
                  ├── Phase 0: refs/analysis-protocol.md (prerequisites)
                  ├── Phase 1: refs/analysis-protocol.md (workflow analysis)
                  ├── Phase 2: refs/pipeline-spec.md (pipeline specification)
                  ├── Phase 3: examples/release-spec-template.md (spec synthesis)
                  │             └── uses: sc:brainstorm behavioral patterns
                  └── Phase 4: (spec panel review)
                                ├── uses: sc:spec-panel --focus correctness,architecture
                                └── uses: sc:spec-panel --mode critique
```

### 4.5 Phase 3 Output Schema

```yaml
# portify-spec-synthesis.yaml (Phase 3 contract)
phase: 3
status: completed
spec_file: portify-release-spec.md
template_used: release-spec-template.md
sections_populated: <int>  # out of total template sections
brainstorm_findings:
  gaps_identified: <int>
  gaps_incorporated: <int>
  gaps_deferred: <int>  # moved to Open Items
  personas_consulted: [architect, analyzer, backend]
```

### 4.6 Phase 4 Output Schema

```yaml
# portify-panel-review.yaml (Phase 4 contract)
phase: 4
status: completed
convergence_iterations: <int>  # 1-3
focus_pass:
  findings_critical: <int>
  findings_major: <int>
  findings_minor: <int>
  incorporated: <int>
  justified_dismissed: <int>  # CRITICAL findings dismissed with justification
  deferred: <int>
critique_pass:
  quality_scores:
    clarity: <float 0-10>
    completeness: <float 0-10>
    testability: <float 0-10>
    consistency: <float 0-10>
    overall: <float 0-10>  # = mean(clarity, completeness, testability, consistency)
  findings_critical: <int>
  findings_major: <int>
  findings_minor: <int>
  incorporated: <int>
panel_report_file: panel-report.md
downstream_ready: <bool>  # overall >= 7.0
```

### 4.7 Implementation Order

```
1. release-spec-template.md           — already created, no deps
2. SKILL.md Phase 3 rewrite           — depends on template
   SKILL.md Phase 4 rewrite           — [parallel with Phase 3 rewrite]
3. SKILL.md return contract update     — depends on 2
   SKILL.md boundaries update          — [parallel with contract]
4. commands/cli-portify.md update      — depends on 3 (remove --skip-integration)
5. refs/pipeline-spec.md addendum      — depends on 2 (Phase 2→3 bridge)
6. decisions.yaml update               — depends on all above (records decisions)
7. .claude/ sync (make sync-dev)       — depends on all above
```

## 5. Interface Contracts

### 5.1 CLI Surface (Updated)

```
/sc:cli-portify --workflow <skill-name-or-path> [--name <cli-name>] [--output <dir>] [--dry-run]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--workflow` | string | required | Skill directory path or sc-* name to portify |
| `--name` | string | derived | CLI subcommand name (kebab-case) |
| `--output` | path | `src/superclaude/cli/<derived>/` | Output directory for spec artifacts |
| `--dry-run` | flag | false | Execute Phases 0-2 only |

**Removed**: `--skip-integration` (no integration phase)

### 5.2 Phase Gate Sequence

| Phase Transition | Gate Type | Condition |
|-----------------|-----------|-----------|
| Phase 0 → Phase 1 | Automatic | Prerequisites contract valid |
| Phase 1 → Phase 2 | User review | User approves analysis |
| Phase 2 → Phase 3 | User approval | User approves pipeline spec; step_mapping ≥1 entry |
| Phase 3 → Phase 4 | Automatic | Draft spec populated (no `{{SC_PLACEHOLDER:*}}` values) AND brainstorm section present |
| Phase 4 → Deliverable | User review | User approves final reviewed spec; 0 unaddressed CRITICAL findings |

**User rejection at Phase 4 gate**: If the user rejects the reviewed spec, they may:
1. **Edit and re-review**: Manually edit the spec, then resume from Phase 4 (`resume_substep=4a`) to re-run the panel review
2. **Regenerate**: Resume from Phase 3 to regenerate the spec from scratch
3. **Abandon**: End the portification with `status: failed, failure_type: null` (user-initiated)

## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-060.1 | Spec synthesis (Phase 3) should complete in reasonable time | ≤10 min | Wall clock from Phase 2 approval to draft spec |
| NFR-060.2 | Panel review (Phase 4) should complete in reasonable time | ≤15 min | Wall clock for both passes |
| NFR-060.3 | Generated spec must score ≥7.0/10 overall to be downstream-ready | ≥7.0 | spec-panel quality scores |
| NFR-060.4 | Template instantiation must leave no `{{SC_PLACEHOLDER:name}}` values | 0 remaining | Regex search for `\{\{SC_PLACEHOLDER:.*?\}\}` |
| NFR-060.5 | All CRITICAL panel findings must be addressed before user review | 0 unaddressed CRITICAL | Finding count (addressed = incorporated OR justified-dismissed) |
| NFR-060.6 | Phase 4 convergence loop must terminate | ≤3 iterations | Iteration counter; escalate to user if exceeded |

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Brainstorm pass produces low-value findings | Medium | Low | Multi-persona approach + structured gap checklist ensures breadth; low-value findings simply not incorporated |
| Brainstorm finds zero gaps | Low | None | Zero gaps is a valid outcome; pipeline continues; recorded in contract for auditability |
| Spec-panel passes take too long / consume too many tokens | Low | Medium | Two focused passes rather than one exhaustive pass; correctness+architecture focus narrows scope |
| Populated spec is too generic / not useful for roadmap | Low | High | Template sections directly map to Phase 1+2 outputs; concrete content, not boilerplate |
| Users skip Phase 4 review, accept spec blindly | Medium | Medium | Quality scores in frontmatter make quality visible; downstream_ready flag gates progression |
| refs/code-templates.md becomes orphaned/stale | Low | Low | File preserved for reference; no active phase loads it; can be cleaned up later |
| Phase 4 convergence loop doesn't converge (CRITICAL findings persist) | Low | Medium | Max 3 iterations; additive-only incorporation prevents introducing new issues; escalate to user after 3 iterations |
| Focus incorporation introduces new issues | Medium | High | Additive-only constraint: incorporation appends/extends but never rewrites existing spec content |
| Brainstorm/spec-panel behavioral contract changes silently | Medium | Medium | Behavioral interface contracts defined in FR-060.1 and FR-060.2 specify expected output formats |

## 8. Test Plan

### 8.1 Validation Checks (Self-Validation)

| Check | Phase | Blocks? |
|-------|-------|---------|
| Draft spec has no remaining `{{SC_PLACEHOLDER:*}}` values | 3 | Yes |
| Every Phase 2 step_mapping has a corresponding FR | 3 | Yes |
| Phase 2 step_mapping has ≥1 entry | 3 (entry) | Yes |
| Brainstorm gap analysis section exists | 3 | Yes |
| If brainstorm gaps found, actionable findings incorporated | 3 | Yes |
| Focus pass produces findings for correctness dimension | 4 | Yes |
| Focus pass produces findings for architecture dimension | 4 | Yes |
| Critique pass produces quality scores for all 4 dimensions | 4 | Yes |
| No unaddressed CRITICAL findings in final spec (after ≤3 iterations) | 4 | Yes |
| Return contract emitted with all fields populated (quality_scores ≥ 0.0) | 4 | Yes |
| `overall` = `mean(clarity, completeness, testability, consistency)` | 4 | Yes |

### 8.2 Manual / E2E Tests

| Scenario | Steps | Expected Outcome |
|----------|-------|-----------------|
| Full portify run | `/sc:cli-portify --workflow sc-adversarial` | Phases 0-4 complete; reviewed spec produced; panel-report.md exists; quality scores in return contract |
| Dry run | `/sc:cli-portify --workflow sc-adversarial --dry-run` | Phases 0-2 only; no spec synthesis; no panel review |
| Low-quality spec recovery | Introduce intentional gaps in Phase 2 output | Brainstorm catches gaps; panel flags them; spec updated before user review |
| Downstream handoff | Take reviewed spec → `/sc:roadmap` | Roadmap successfully generated from spec content |
| Zero brainstorm gaps | Provide comprehensive Phase 2 output | Brainstorm section states "No gaps identified"; pipeline continues; gaps_identified=0 in contract |
| Phase 3 brainstorm timeout | Simulate brainstorm failure mid-execution | Return contract emitted with failure_type=brainstorm_failed; resume_substep=3c |
| Phase 4 user rejection | User rejects at Phase 4 gate | resume_command populated; user can re-invoke from Phase 4 or Phase 3 |
| Convergence loop | Inject spec that produces CRITICAL findings on focus pass | Loop iterates ≤3 times; CRITICAL findings resolved or escalated to user |
| Boundary: quality at threshold | Spec producing overall=7.0 exactly | downstream_ready=true (>= is inclusive) |
| Boundary: quality below threshold | Spec producing overall=6.9 | downstream_ready=false |
| Panel failure mid-review | Simulate panel timeout during Phase 4 | Quality scores set to 0.0; downstream_ready=false; failure_type=panel_review_failed |

## 9. Migration & Rollout

- **Breaking changes**: Yes — `--skip-integration` flag removed; output is a spec file, not generated code
- **Backwards compatibility**: Not applicable — cli-portify has not been used in production; this is a pre-release refactoring
- **Rollback plan**: Git revert to v2.18 SKILL.md; the Phase 0-2 flow is unchanged

## 10. Downstream Inputs

### For sc:roadmap
- **Input**: `portify-release-spec.md` — the reviewed release specification
- **Themes**: Pipeline module implementation (12+ files), gate criteria implementation, executor design, testing harness, CLI integration
- **Milestone structure**: Derive from implementation order (Section 4.7 of the generated spec): models → gates → prompts → config → executor → integration

### For sc:tasklist
- **Input**: Roadmap milestones generated from the release spec
- **Task granularity**: Each FR in the spec maps to one or more tasklist items
- **Dependencies**: Implementation order from Section 4.6 of the generated spec defines task dependencies

## 11. Open Items

1. **Progress observability**: NFR time targets (≤10min, ≤15min) have no real-time progress indicator. Consider adding phase progress events or a progress bar mechanism. (Hightower)
2. **Brainstorm enrichment mapping**: The structured format for how brainstorm findings map back to specific spec sections could be more formally defined beyond the `affected_section` field. (Hohpe)
3. **Template sentinel robustness**: The `{{SC_PLACEHOLDER:name}}` sentinel is robust against most collisions but should be validated against real template content when the template is finalized. (Whittaker)

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| Portification | Converting an inference-based workflow into a programmatic CLI pipeline |
| Release spec | A complete specification document that feeds into sc:roadmap for implementation planning |
| Automated brainstorm | Non-interactive multi-persona gap analysis applying sc:brainstorm behavioral patterns (not invoking the command) |
| Panel review | Expert specification review applying sc:spec-panel behavioral patterns |
| Focus pass | Spec-panel review targeting specific dimensions (correctness, architecture) |
| Critique pass | Spec-panel review in critique mode producing actionable findings and quality scores |
| Gate | An automatic or user-driven checkpoint between phases that must pass before the pipeline continues |
| Contract | A YAML file emitted by each phase recording its status, outputs, and metadata for downstream consumption |
| Behavioral patterns | The decision-making logic and expert analysis methodology defined in a skill's SKILL.md, applied inline rather than via command invocation |
| Downstream-ready | A spec whose `overall` quality score ≥ 7.0, eligible for consumption by sc:roadmap |
| Convergence loop | Phase 4's mechanism for re-running review passes until CRITICAL findings are resolved (max 3 iterations) |
| Additive-only incorporation | Constraint that spec modifications during finding incorporation must append/extend, never rewrite existing content |

## Appendix B: Reference Documents

| Document | Relevance |
|----------|-----------|
| `refactoring-spec-cli-portify.md` (v2.18) | Prior spec defining the current Phase 0-4 architecture |
| `spec-roadmap-validate.md` (v2.19) | Peer spec showing quality bar for new feature specs |
| `forensic-foundation-validated.md` (v2.20) | Diagnostic identifying why bugs survive the workflow — motivates this refactoring |
| `src/superclaude/commands/brainstorm.md` | Brainstorm command definition — behavioral patterns used in Phase 3 |
| `src/superclaude/commands/spec-panel.md` | Spec-panel command definition — behavioral patterns used in Phase 4 |
| `src/superclaude/examples/release-spec-template.md` | Template created by this work |
| `.dev/releases/backlog/v.4.0-Spec-generator-framework/UNIFIED_SPEC_GENERATOR_SPECIFICATION.md` | Future template system design — this work is a lightweight precursor |


# Appendix C: Forensic Foundation: Why Bugs Survive the SuperClaude Workflow

**Classification**: Diagnostic only — no fixes proposed
**Pipeline scope**: brainstorm → spec-panel → adversarial → roadmap → tasklist → CLI runner
**Sources**: Four peer artifacts compared under blind adversarial review; original three analyses treated as co-equal peers relative to the prior merged foundation

---

## Executive Summary

<!-- Source: Base (original, modified) — adjusted per Change #1 to preserve evidentiary hierarchy and unresolved conflicts -->
The strongest supported conclusion across the compared analyses is this:

**The pipeline validates that work looks right, not that work is right.**

Across the workflow, structural confidence accumulates faster than independent evidence. The system is highly effective at producing artifacts that are well-formed, reviewable, and consumable by downstream stages. It is materially weaker at proving that those artifacts are semantically correct, operationally trustworthy, and faithfully preserved across handoffs.

This does **not** fully resolve whether the failure system is best explained as a category error, a multi-factor process gap, or misallocated rigor. The evidence supports a more careful statement: the pipeline over-weights document quality, internal agreement, and process conformance relative to runtime truth and boundary fidelity.

---

## Part I: Validated Findings

These findings are supported by strong evidence across multiple compared artifacts and survived adversarial challenge.

### F-001: Structural Validation Is Systematically Mistaken for Semantic Correctness

<!-- Source: Base (original) -->
The pipeline’s gates primarily check structural properties. Content quality sits in the gap between what was deliberately excluded (LLM-evaluating-LLM) and what was never replaced by an independent semantic or runtime validator.

| Validates | Does NOT Validate |
|-----------|-------------------|
| File exists | Content is correct |
| File is non-empty | Content is complete |
| File has ≥N lines | Content is internally consistent |
| YAML frontmatter has required keys | Frontmatter values are semantically valid |
| Heading hierarchy has no gaps | Content under headings is relevant |
| Bulleted/numbered items exist | Items are actionable or feasible |
| Convergence score is in [0.0, 1.0] | Convergence reflects genuine agreement |
| Tasks have proper ID format | Tasks will produce working software |
| Subprocess exit code is 0 | Subprocess accomplished its goal |

<!-- Source: Variant 3, Section F-001 / code-level evidence — merged per Change #2 -->
Concrete examples support this claim:
- `_cross_refs_resolve()` in `roadmap/gates.py` scans references but is effectively non-failing.
- `_has_actionable_content()` can pass on the basis of minimal bullet presence rather than meaningful actionability.
- `_convergence_score_valid()` checks parseability and range, not semantic relationship to the debate.

### F-002: Confidence Inflates Across Stages Through Proxy Stacking

<!-- Source: Variant 2, confidence-signal table — merged per Change #3 -->
Each stage emits a confidence artifact that later stages treat as a trustworthy summary. The problem is not that these signals are numerically wrong; it is that they measure proxies that are easy to misread as evidence.

| Confidence Signal | What It Actually Measures | What It Is Often Taken to Mean | Gap |
|-------------------|--------------------------|--------------------------------|-----|
| Panel score: 8.6/10 | Document structure and apparent reviewability | The spec will work when implemented | Document quality ≠ implementation quality |
| Expert approval | Simulated persona agreement | Expert validation | Simulated approval ≠ external judgment |
| Convergence: 0.72 | Internal model agreement across debate roles | Design robustness or truth | Self-agreement ≠ correctness |
| Tasklist quality: 100% | Task description quality | Execution quality | Description quality ≠ behavioral success |
| Gate PASS | Structural compliance | Output correctness | Structural validity ≠ semantic correctness |
| Pass rate: 97.4% | Completion against process criteria | Feature completeness | Process completion ≠ working software |

### F-003: The Adversarial Stage Is Better at Design Critique Than Runtime Falsification

<!-- Source: Base (original, modified) — sharpened with retained opposing strengths -->
The adversarial stage can expose contradictions, scope ambiguity, and architecture-level disagreements inside the text of a plan. It cannot verify implementation behavior because no implementation exists yet at the point of debate.

| The Adversarial Stage Can Catch | It Cannot Catch |
|--------------------------------|-----------------|
| Logical contradictions in spec text | Implementation bugs in generated code |
| Missing requirements visible in text | Missing error handling in real code paths |
| Architectural inconsistencies | LLM output variability at runtime |
| Scope ambiguity | Whether prompts produce correct output |
| Conceptual risk gaps | Whether gates catch real failures |
| Process workflow issues | Whether mocks represent production reality |

It also has a secondary loss mode: even when the debate identifies useful conclusions, incorporation downstream is partial. Evidence from the compared artifacts repeatedly cited that roughly 10–15% of adversarial conclusions were simplified or dropped without systematic downstream tracking.

### F-004: Tests Systematically Exclude the Highest-Risk Boundary

<!-- Source: Variant 3 evidence chains + Variant 4 seam framing — merged per Changes #2 and #4 -->
The most failure-prone boundary is the one between executor logic and actual Claude CLI subprocess behavior. That is the place where signal parsing, formatting variability, monitoring assumptions, and timing behavior interact. The compared analyses consistently show that this boundary is mocked, hand-crafted, or otherwise bypassed rather than exercised directly.

Representative evidence cited across the source analyses includes:
- executor-loop tests that mock subprocess interaction,
- status-determination tests that use hand-crafted result files,
- mitigations aimed at signal handling that still mandate mocked subprocesses,
- diagnostic harnesses whose names imply end-to-end scope while their actual tests stay at subcomponent level.

### F-005: Retrospective Findings Fail to Become Immediate Forward Constraints

<!-- Source: Base (original) -->
The clearest evidence chain concerns `PARTIAL → PASS` promotion:
1. A retrospective identifies the bug and rates it as highest priority.
2. The next spec reproduces the same status-fidelity gap.
3. Chronology shows the retrospective post-dates the spec, so incorporation was structurally impossible on that cycle.

This is not merely “a missed lesson.” It shows a timing disconnect between discovery and prevention: the workflow learns backward while planning forward.

### F-006: Seam Failures Are a Primary Failure Habitat

<!-- Source: Variant 4 seam analysis — merged per Change #4 -->
The strongest boundary-centered reading is that many important defects are introduced or hidden at handoffs rather than inside any single artifact in isolation. High-risk seams include:
- spec → prompt,
- extract → generate,
- adversarial → merge,
- roadmap → tasklist,
- tasklist → CLI runner,
- runner → monitor/gates,
- retrospective → next spec.

This seam-centered framing is important because it explains why each local stage can look healthy while the cross-stage system still leaks critical constraints.

---

## Part II: Strongly Supported but Not Fully Resolved Theories

These theories are well-supported, but adversarial review did not justify promoting all of them to fully settled findings.

### T-001: The System May Contain a Category Error

<!-- Source: Variant 2 category-error framing — merged per Change #3, preserved as theory not finding -->
One strong interpretation is that the pipeline uses textual analysis to validate artifacts whose ultimate quality depends on execution behavior. Under that reading, document-quality methods are necessary but insufficient, and the workflow is being asked to answer a question it was not built to answer.

This theory was retained as a theory rather than a finding because the compared artifacts do not prove that this is the single governing cause. A more modest reading is that document-quality validation has been over-weighted relative to runtime proof.

### T-002: Misallocated Rigor Explains More Than Lack of Rigor

<!-- Source: Variant 4 core framing -->
Another strong theory is that the process is not weak because it is shallow; it is weak because its strongest rigor is concentrated in the wrong places: formatting, artifact shape, internal agreement, and planning decomposition rather than external truth and live-path verification.

### T-003: Schema Drift Can Propagate Silently Through Passing Gates

<!-- Source: Variant 3 and Variant 1 -->
A recurring example is extract-schema drift: the operational contract thins, the gate adapts to the thin contract, and downstream stages continue with less information while PASS signals remain green. This appears strongly evidenced in at least one important case, though broader generalization remains a theory.

### T-004: Prior Synthesis Can Itself Become a Lossy Compression Layer

<!-- Source: adversarial comparison itself -->
The prior merged foundation artifact was useful, but the comparison confirmed that starting from a synthesis can silently inherit previous losses. This is why the prior foundation was treated as a peer artifact rather than an authority during this run.

---

## Part III: Unresolved Conflicts That Should Not Be Flattened

<!-- Source: Variant 1 unresolved conflicts structure + Variant 4 plural framing — merged per Change #5 -->

### UC-001: Is the failure system monocausal or multi-causal?
- **Monocausal reading**: the deepest problem is a category mismatch between document validation and implementation quality.
- **Multi-causal reading**: several mechanisms co-occur — proxy inflation, seam loss, schema drift, mock-boundary exclusion, and retrospective disconnect.
- **Current verdict**: unresolved. The evidence is strongest for a multi-mechanism failure ecology, but not strong enough to eliminate the monocausal framing entirely.

### UC-002: Does convergence carry any truth-bearing signal?
- **Lower-value view**: convergence mostly shows the model agreeing with itself.
- **Weak-signal view**: convergence has internal process value but should not be treated as correctness evidence.
- **Current verdict**: unresolved. The safer conclusion is that convergence is structurally interesting and epistemically weak.

### UC-003: Is the architecture fundamentally flawed or incompletely defended?
- **Architecture-flaw reading**: the pipeline was built for the wrong validation problem.
- **Incomplete-defense reading**: the architecture is coherent but missing independent verification at critical seams.
- **Current verdict**: unresolved. The compared evidence supports both readings better than a forced single answer.

---

## Part IV: Hidden Assumptions Surfaced by the Adversarial Comparison

<!-- Source: Variant 1 hidden assumptions + shared assumption analysis — merged per Change #6 -->

### A-001: Structural validity is too weak to serve as a serious proxy for correctness
All compared artifacts assume this. It is strongly supported, but the exact strength of correlation between structure and quality was not empirically measured here.

### A-002: The highest-risk failures cluster at seams rather than only within stages
This assumption is strongly supported by repeated examples, but it remains an inference about failure distribution across the workflow.

### A-003: Some form of stronger external or runtime verification would improve trustworthiness
All artifacts imply this, but none proves which kind of verification would be sufficient, tractable, or free from new failure modes.

### A-004: The observed failures generalize beyond the examined releases
The evidence base spans several releases and related implementation artifacts, but full generalization remains an assumption.

---

## Part V: Strongest Evidence Chains

### Evidence Chain 1: PARTIAL→PASS propagation failure
1. Retrospective records `PARTIAL` being silently promoted to `PASS` and rates it as high priority.
2. The next spec omits `PARTIAL` from the relevant status model.
3. Chronology shows the retrospective came after the spec, making immediate incorporation impossible.
4. Therefore the learning loop is temporally disconnected from the spec-prevention loop.

### Evidence Chain 2: Schema drift through passing gates
1. Protocol expectations remain richer.
2. Operational prompts request a thinner schema.
3. Gates validate the thinner schema and still report PASS.
4. Downstream stages consume degraded inputs without escalation.
5. Therefore PASS reflects satisfaction of a weakened contract, not preservation of protocol richness.

### Evidence Chain 3: Mock-boundary exclusion
1. Highest-risk failures occur at the executor ↔ subprocess boundary.
2. Tests that should exercise this boundary use mocks or hand-crafted files.
3. The resulting green tests validate harness logic more than live interaction.
4. Therefore testing structurally excludes the very place where important failures emerge.

### Evidence Chain 4: Structural-gate bug propagation across layers
1. A brittle frontmatter-position assumption exists in one validation layer.
2. Equivalent assumptions are duplicated in adjacent semantic checks.
3. Fixing one layer leaves homologous failures alive elsewhere.
4. Therefore shared assumptions can survive local fixes and keep failure blast radius wide.

### Evidence Chain 5: Spec-to-implementation drift without detection
1. Implementations grow beyond their original specs.
2. APIs, formats, defaults, and subsystems change materially.
3. Tests continue validating against the spec’s intended contract rather than the drifted implementation reality.
4. Therefore spec drift can widen without an active detection mechanism.

---

## Part VI: Boundary Map — Where Failure Is Most Likely Introduced or Hidden

1. **Spec → Prompt**: full requirements compress into summarized task language.
2. **Extract → Generate**: thin schemas propagate as if complete.
3. **Adversarial → Merge**: findings can be simplified or dropped without tracking.
4. **Roadmap → Tasklist**: rich constraints become operational metadata.
5. **Tasklist → CLI Runner**: execution receives reduced context and structural acceptance criteria.
6. **Runner → Gates/Monitor**: structural compliance can substitute for semantic truth.
7. **Retrospective → Next Spec**: lessons arrive too late to constrain the already-written next cycle.
8. **Spec → Implementation**: drift can grow while official validation still points at the older contract.

---

## Methodological Note

This artifact was produced from a deep, blind adversarial comparison of four artifacts, including one prior synthesis and three original peer analyses. In accordance with the user’s instruction, the original three analyses were treated as co-equal peers and the prior synthesis was not granted authority by title, tone, or apparent comprehensiveness.