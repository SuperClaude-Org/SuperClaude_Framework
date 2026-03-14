---
spec_source: "portify-release-spec.md"
complexity_score: 0.65
primary_persona: architect
---

## 1. Executive summary

This roadmap delivers a bounded v2.24.1 enhancement to the CLI portify workflow so it can resolve commands, skills, and agents from multiple input forms while preserving existing behavior for current skill-directory workflows.

From an architecture perspective, the work is moderate in complexity but high in compatibility sensitivity. The central design constraint is not feature breadth; it is preserving current behavior while adding a new resolution layer, richer component modeling, and broader validation coverage without modifying `pipeline/` or `sprint/` base modules.

### Architectural priorities
1. **Preserve existing workflows first**
   - Existing skill-directory inputs must remain behaviorally identical.
   - `resolve_workflow_path()` remains unchanged and the new resolver is additive.

2. **Isolate new logic**
   - Concentrate resolution rules in a dedicated module.
   - Keep boundary conversions explicit between new `Path`-based dataclasses and legacy string-based inventory outputs.

3. **Maintain deterministic behavior**
   - Resolution precedence, ambiguity handling, and warning/error semantics must be explicit and testable.
   - Agent discovery remains O(1)-depth and synchronous.

4. **Control subprocess scope**
   - Enforce the 10-directory cap with deterministic consolidation and auditability via `resolution_log`.

### Outcome
If executed as planned, the release will:
- support all 6 target input forms,
- produce a hierarchical component model with backward-compatible flattening,
- enrich validation and artifacts,
- preserve current behavior when new features are not used,
- ship with targeted test coverage around resolution, warnings, compatibility, and edge cases.

---

## 2. Phased implementation plan with milestones

## Phase 0 — Delivery guardrails and baseline alignment

### Objectives
Establish a safe implementation envelope before code changes begin.

### Actions
1. Confirm baseline constraints from extraction:
   - No edits in `pipeline/` or `sprint/`.
   - No async code.
   - Existing skill-directory behavior remains unchanged.

2. Identify impacted surfaces:
   - `models.py`
   - new `resolution.py`
   - `discover_components.py`
   - `process.py`
   - `cli.py`
   - `config.py`
   - `validate_config.py`
   - tests

3. Freeze architectural contracts:
   - command-first policy for bare-name ambiguity
   - warning vs error behavior
   - boundary conversion rules for `Path` to `str`
   - directory cap and consolidation policy

### Milestone
- Approved implementation contract and file scope established.

### Deliverables
- Change map
- explicit compatibility checklist
- test matrix outline

### Timeline estimate
- **0.25 phase units** / **same session startup task**

---

## Phase 1 — Data model foundation

### Objectives
Introduce the new structural model without breaking existing consumers.

### Actions
1. Extend model layer to support:
   - `ResolvedTarget`
   - `CommandEntry`
   - `SkillEntry`
   - `AgentEntry`
   - `ComponentTree`
   - extended validation result fields

2. Define explicit compatibility boundaries:
   - New dataclasses use `Path`.
   - Existing flat inventory output remains string-path based.

3. Implement `ComponentTree` capabilities:
   - `component_count`
   - `total_lines`
   - `all_source_dirs`
   - `to_flat_inventory()`
   - `to_manifest_markdown()`

4. Extend validation result serialization:
   - `command_path`
   - `skill_dir`
   - `target_type`
   - `agent_count`
   - `warnings`

### Architect focus
- This phase is the structural backbone. If the model boundaries are unclear, later phases will leak compatibility complexity into CLI and process layers.

### Milestone
- New model types compile and support backward-compatible conversion.

### Deliverables
- model extensions
- compatibility conversion methods
- serialization coverage tests

### Timeline estimate
- **0.75 phase units**

---

## Phase 2 — Target resolution engine

### Objectives
Implement deterministic multi-form resolution in an isolated module.

### Actions
1. Create `resolution.py` to handle the 6 supported input forms:
   - bare command name
   - prefixed command name
   - command file path
   - skill directory path
   - skill directory name
   - `SKILL.md` path

2. Implement normalization into `ResolvedTarget`:
   - command path
   - skill directory
   - project root
   - target type
   - warnings / resolution log as needed

3. Encode resolution policy:
   - strip `sc:` prefix
   - empty/whitespace/`None` => `ERR_TARGET_NOT_FOUND`
   - empty result after prefix strip => `ERR_TARGET_NOT_FOUND`
   - same-class multi-match => `ERR_AMBIGUOUS_TARGET`
   - bare name command-first over skill

4. Implement command-to-skill resolution:
   - parse `## Activation`
   - extract `Skill sc:<name>-protocol`
   - missing referenced skill => `ERR_BROKEN_ACTIVATION`

5. Implement reverse skill-to-command heuristic:
   - strip `sc-`
   - strip `-protocol`
   - resolve `<name>.md`
   - missing command => warning only

6. Add performance measurement around `resolve_target()`:
   - verify sub-1-second expectation

### Architect focus
- Keep this phase pure and deterministic.
- Do not mix discovery, CLI parsing, or subprocess concerns into the resolver.
- Resolution must produce stable semantics independent of downstream pipeline behavior.

### Milestone
- All 6 input forms resolve correctly with explicit error/warning behavior.

### Deliverables
- new resolver module
- ambiguity/error handling
- timing coverage
- edge-case tests

### Timeline estimate
- **1.0 phase units**

---

## Phase 3 — Component discovery and hierarchical assembly

### Objectives
Build the component tree and agent discovery on top of resolved targets.

### Actions
1. Update discovery flow to assemble:
   - Tier 0: command
   - Tier 1: skill and nested refs/rules/templates/scripts
   - Tier 2: referenced/manual agents

2. Implement agent extraction from `SKILL.md` using the 6 required regex classes:
   - backtick-agent notation
   - YAML arrays
   - spawn/delegate/invoke verbs
   - `uses` references
   - model-parenthetical patterns
   - `agents/` path patterns

3. Implement CLI agent injection behavior:
   - `--include-agent`
   - deduplicate by name
   - manual override precedence
   - ignore empty strings

4. Handle missing agents non-fatally:
   - `found=False`
   - emit warnings
   - continue pipeline

5. Support standalone modes:
   - standalone command => no skill
   - standalone skill => no command
   - multi-skill command => primary only, warn on secondary references

### Architect focus
- Preserve one-way discovery depth.
- Avoid recursive expansion in this release; it would alter scope and risk profile.
- Keep missing references observable but non-fatal when specified by requirements.

### Milestone
- `ComponentTree` accurately represents resolved workflows and agents.

### Deliverables
- discovery refactor
- agent extraction
- missing-agent warning path
- standalone and multi-skill handling

### Timeline estimate
- **1.0 phase units**

---

## Phase 4 — Process integration and subprocess scoping

### Objectives
Integrate tree-derived source directories into the existing process without changing base modules.

### Actions
1. Extend `PortifyProcess` to accept `additional_dirs`.
2. Derive `--add-dir` values from `ComponentTree.all_source_dirs`.
3. Deduplicate directories.
4. Enforce cap of 10 directories.
5. Apply consolidation strategy:
   - use `os.path.commonpath()`
   - prefer meaningful parent consolidation
   - if still over cap, select top 10 by component count
6. Record decisions in `resolution_log`.

### Architect focus
- This is a containment boundary, not a feature expansion point.
- The main risk is over-broad subprocess scope or unstable argument generation.
- Deterministic consolidation is more important than aggressive completeness here.

### Milestone
- Process integration works with legacy behavior preserved when `additional_dirs=None`.

### Deliverables
- process parameter extension
- directory cap logic
- consolidation audit trail
- compatibility tests for unchanged v2.24 behavior

### Timeline estimate
- **0.5 phase units**

---

## Phase 5 — CLI and configuration integration

### Objectives
Expose new capabilities without disrupting current CLI usage patterns.

### Actions
1. Update CLI input contract from workflow-path-only behavior to generalized target input.
2. Add override options:
   - `--commands-dir`
   - `--skills-dir`
   - `--agents-dir`

3. Add optional artifact output:
   - `--save-manifest`

4. Ensure config loading passes through new directory overrides and related settings.

5. Preserve compatibility:
   - existing skill-directory inputs must resolve identically
   - legacy flows must continue to work without new flags

### Architect focus
- CLI is the highest user-visible risk area.
- Minimize surprise by preserving existing success paths and keeping new behavior additive.

### Milestone
- CLI accepts new target forms and override flags with stable behavior.

### Deliverables
- CLI wiring
- config passthrough
- manifest save path
- help text and argument tests

### Timeline estimate
- **0.5 phase units**

---

## Phase 6 — Validation pipeline and artifact enrichment

### Objectives
Upgrade validation and reporting to reflect new resolution behavior.

### Actions
1. Add validation checks for:
   - command-to-skill link validity
   - referenced agent existence

2. Introduce required error/warning codes:
   - `ERR_TARGET_NOT_FOUND`
   - `ERR_AMBIGUOUS_TARGET`
   - `ERR_BROKEN_ACTIVATION`
   - `WARN_MISSING_AGENTS`

3. Enrich `component-inventory.md`:
   - Command section
   - Agents section
   - Cross-Tier Data Flow
   - Resolution Log
   - extended frontmatter

4. Ensure result objects expose extended metadata through `to_dict()`.

### Architect focus
- Validation should encode system invariants, not only user messaging.
- Artifacts should improve traceability for debugging and future v2.25 expansion.

### Milestone
- Validation and generated artifacts reflect the full resolved component graph.

### Deliverables
- validation extensions
- richer artifact output
- error/warning contract tests

### Timeline estimate
- **0.5 phase units**

---

## Phase 7 — Verification, compatibility proof, and release hardening

### Objectives
Prove backward compatibility and close release risk.

### Actions
1. Build test coverage for:
   - all 6 input forms
   - empty and whitespace targets
   - prefix-only `sc:`
   - ambiguous targets
   - broken activation links
   - reverse-resolution warnings
   - missing agent warnings
   - manual include-agent precedence
   - directory cap and consolidation
   - standalone command/skill cases
   - multi-skill warning path

2. Verify non-functional requirements:
   - no `pipeline/` or `sprint/` changes
   - no async syntax
   - existing tests pass unchanged
   - `additional_dirs=None` preserves current behavior
   - resolution under 1 second

3. Execute regression validation on prior skill-directory workflows.

4. Perform release readiness review against success criteria.

### Architect focus
- This phase is essential because the dominant risk is not local correctness; it is behavioral regression across existing flows.

### Milestone
- All new and existing tests pass, with explicit proof of compatibility constraints.

### Deliverables
- full test pass
- regression evidence
- release checklist completion

### Timeline estimate
- **0.75 phase units**

---

## 3. Risk assessment and mitigation strategies

## High-priority risks

### 1. Backward-compatibility regression
- **Severity:** High
- **Why it matters:** Existing users depend on skill-directory-based flows.
- **Mitigation:**
  1. Preserve `resolve_workflow_path()` unchanged.
  2. Route legacy skill-directory inputs through a compatibility-safe path.
  3. Add regression tests comparing old and new behavior for identical inputs.
  4. Validate that `PortifyProcess(additional_dirs=None)` matches v2.24 behavior exactly.

### 2. Resolution ambiguity or unstable precedence
- **Severity:** High
- **Why it matters:** Ambiguity directly affects determinism and user trust.
- **Mitigation:**
  1. Encode precedence centrally in `resolution.py`.
  2. Test same-class ambiguity separately from cross-class command-first precedence.
  3. Return descriptive, typed errors rather than silent fallback behavior.

## Medium-priority risks

### 3. Agent extraction misses real references
- **Severity:** Medium
- **Mitigation:**
  1. Implement all 6 required regex classes.
  2. Add corpus-style tests covering each pattern.
  3. Provide `--include-agent` as an escape hatch.
  4. Treat missing agents as warnings, not fatal failures.

### 4. Directory cap/consolidation broadens subprocess scope too far
- **Severity:** Medium
- **Mitigation:**
  1. Cap at 10 directories.
  2. Use `os.path.commonpath()` conservatively.
  3. Record consolidation logic in `resolution_log`.
  4. Prefer deterministic top-10-by-component-count fallback over ad hoc selection.

### 5. CLI contract drift confuses current users
- **Severity:** Medium
- **Mitigation:**
  1. Keep current usage forms working.
  2. Add explicit help text for all accepted target types.
  3. Test both new and legacy invocation patterns.

## Lower-priority but notable risks

### 6. Non-standard project layout causes root detection failure
- **Severity:** Low to Medium
- **Mitigation:**
  1. Support explicit overrides via `--commands-dir`, `--skills-dir`, `--agents-dir`.
  2. Emit actionable error messages suggesting these flags.
  3. Test at least one non-standard path scenario.

### 7. Frontmatter parsing failures in source documents
- **Severity:** Low
- **Mitigation:**
  1. Gracefully degrade to convention-based discovery.
  2. Avoid making frontmatter a hard dependency for basic resolution.

---

## 4. Resource requirements and dependencies

## Engineering resources

### Required roles
1. **Primary implementer**
   - Python CLI and dataclass modeling
   - path resolution and parsing
   - compatibility-focused refactoring

2. **Reviewer / release validator**
   - regression review
   - CLI/UX review
   - artifact and validation semantics check

3. **QA support**
   - edge-case scenario validation
   - timing and compatibility confirmation

## Technical dependencies

### Internal dependencies
1. `models.py`
2. `discover_components.py`
3. `process.py`
4. `validate_config.py`
5. `cli.py`
6. `config.py`

### External/runtime dependencies
1. Click
2. Python `re`
3. Python `os.path.commonpath()`

## Architectural dependency handling plan
1. **Model changes first**
   - establish stable types before wiring logic

2. **Resolution isolated second**
   - keep resolution independent from CLI parsing and subprocess handling

3. **Discovery/process in parallel**
   - once model contracts are stable

4. **CLI/config after internals settle**
   - avoid rework from changing internal interfaces

5. **Validation/tests last but mandatory**
   - verify end-to-end semantics once wiring is complete

## Artifact requirements
1. Enriched `component-inventory.md`
2. Optional manifest markdown via `--save-manifest`
3. extended validation result payloads
4. test evidence for compatibility and performance

---

## 5. Success criteria and validation approach

## Success criteria mapping

### Functional acceptance
1. Bare-name resolution works.
2. `sc:`-prefixed resolution works identically after normalization.
3. Skill path and `SKILL.md` path resolve correctly.
4. Nonexistent/empty targets return `ERR_TARGET_NOT_FOUND`.
5. Ambiguous same-class matches return `ERR_AMBIGUOUS_TARGET`.
6. Broken activation link returns `ERR_BROKEN_ACTIVATION`.
7. Component tree contains correct command, skill, and agent structure.
8. Agent extraction covers all 6 required regex families.
9. Manual `--include-agent` entries override duplicates correctly.
10. Missing agents remain warnings and do not fail the pipeline.
11. Flat inventory output remains backward-compatible.
12. Existing tests pass unchanged.

## Validation approach

### Validation stream A — unit validation
1. Resolver tests for all input forms and failure modes
2. model conversion tests
3. regex extraction tests
4. directory consolidation tests

### Validation stream B — integration validation
1. CLI invocation tests with new and legacy inputs
2. validation result shape tests
3. manifest and inventory artifact tests
4. process invocation tests with and without `additional_dirs`

### Validation stream C — regression validation
1. existing suite passes unchanged
2. old skill-directory flows match prior behavior
3. no changes under restricted directories:
   - `pipeline/`
   - `sprint/`

### Validation stream D — non-functional verification
1. resolution timing under 1 second
2. grep/static proof of no `async def` / `await`
3. diff proof of no forbidden base-module changes
4. subprocess directory cap respected

## Release gate
Do not mark the release complete until all of the following are true:
1. all new tests pass,
2. all existing tests pass,
3. backward-compatibility evidence is recorded,
4. directory cap behavior is deterministic and logged,
5. warning/error semantics are stable and documented through tests.

---

## 6. Timeline estimates per phase

## Recommended sequence
1. Phase 0 — Guardrails and baseline
2. Phase 1 — Data model foundation
3. Phase 2 — Target resolution engine
4. Phase 3 — Component discovery and assembly
5. Phase 4 — Process integration
6. Phase 5 — CLI/config integration
7. Phase 6 — Validation/artifact enrichment
8. Phase 7 — Verification and release hardening

## Phase-by-phase estimate
1. **Phase 0:** 0.25 phase units
2. **Phase 1:** 0.75 phase units
3. **Phase 2:** 1.0 phase units
4. **Phase 3:** 1.0 phase units
5. **Phase 4:** 0.5 phase units
6. **Phase 5:** 0.5 phase units
7. **Phase 6:** 0.5 phase units
8. **Phase 7:** 0.75 phase units

## Aggregate estimate
- **Total:** approximately **5.25 phase units**
- Practical execution shape:
  - **Session 1:** Phases 0-2
  - **Session 2:** Phases 3-5
  - **Session 3:** Phases 6-7

## Milestone checkpoints
1. **Checkpoint A:** Models + resolver stable
2. **Checkpoint B:** Component tree + process integration stable
3. **Checkpoint C:** CLI + validation + artifacts stable
4. **Checkpoint D:** Regression and NFR proof complete

---

## Recommended implementation order

1. **Start with the model boundary**
   - Avoids leaking compatibility logic everywhere else.

2. **Implement resolution next**
   - It is the core architectural addition and highest semantic risk.

3. **Then build discovery and process integration**
   - These should consume stable resolved contracts.

4. **Wire CLI/config only after internals are stable**
   - Prevents repetitive interface churn.

5. **Finish with validation and regression proof**
   - This release succeeds or fails on compatibility evidence, not only feature completion.

---

## Architect recommendation

The roadmap should be executed as a **compatibility-first incremental delivery**, not as a broad refactor. The key to success is keeping the new resolution system isolated, explicit, and exhaustively tested at the boundaries. The biggest release risk is silent behavior drift in existing workflows, so every major milestone should be validated against backward-compatible expectations before proceeding.
