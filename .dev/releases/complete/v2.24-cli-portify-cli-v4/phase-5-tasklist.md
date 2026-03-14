# Phase 5 -- Core Content Generation

Deliver the core design intelligence of the pipeline: workflow analysis, pipeline design, and spec synthesis. These are Claude-assisted steps that depend on the subprocess platform from Phase 4 (M3 gate).

### T05.01 -- Implement analyze-workflow Step (Step 3)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | Step 3 reads discovered components via @path references and produces portify-analysis.md with behavioral flow, step boundaries, and programmatic spectrum classification. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (system-wide analysis) |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0023/spec.md

**Deliverables:**
1. `analyze_workflow` step implementation in `src/superclaude/cli/cli_portify/steps/analyze_workflow.py` producing `portify-analysis.md` (<400 lines) with 5 required sections: behavioral flow, step boundaries, programmatic spectrum classification, dependency/parallel groups, gate requirements; includes data flow diagram with arrow notation and 5 YAML frontmatter fields

**Steps:**
1. **[PLANNING]** Load component inventory (D-0015) to identify all discovered components for @path references
2. **[PLANNING]** Review SC-003 gate criteria: 5 required sections, data flow diagram, 5 YAML frontmatter fields
3. **[EXECUTION]** Construct analyze-workflow prompt using prompt builder (D-0018) with @path references to discovered components
4. **[EXECUTION]** Execute Claude subprocess via PortifyProcess (D-0017) with --add-dir scoping
5. **[EXECUTION]** Parse output and verify portify-analysis.md is <400 lines with required sections
6. **[VERIFICATION]** Run SC-003 STRICT gate: verify 5 required sections present, data flow diagram exists, 5 YAML frontmatter fields populated
7. **[COMPLETION]** Log step timing and gate result to diagnostics

**Acceptance Criteria:**
- `portify-analysis.md` exists with <400 lines
- STRICT gate SC-003 passes: 5 required sections (behavioral flow, step boundaries, programmatic spectrum classification, dependency/parallel groups, gate requirements), data flow diagram with arrow notation, 5 YAML frontmatter fields
- Step uses @path references to component inventory from Step 2
- Step executes via PortifyProcess with correct --add-dir scoping

**Validation:**
- `uv run pytest tests/cli_portify/test_analyze_workflow.py -v` exits 0 (using mock harness)
- Evidence: linkable artifact produced at D-0023/spec.md

**Dependencies:** T03.02, T04.01, T04.02, T04.05
**Rollback:** TBD (if not specified in roadmap)

---

### T05.02 -- Implement design-pipeline Step (Step 4) with Dry-Run and Review Gate

| Field | Value |
|---|---|
| Roadmap Item IDs | R-019 |
| Why | Step 4 produces the pipeline specification, implements --dry-run halt point, and adds user review gate. This is the last stop before synthesis. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (pipeline design + dry-run + review gate) |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0024, D-0025, D-0047 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0024/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0025/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0047/spec.md

**Deliverables:**
1. `design_pipeline` step implementation in `src/superclaude/cli/cli_portify/steps/design_pipeline.py` producing `portify-spec.md` with: step graph, domain models, prompt builder specs, gate criteria with semantic checks, pure-programmatic steps as runnable Python code, executor loop, Click CLI integration
2. `--dry-run` halt logic: emits `dry_run` contract with phases 3-4 marked `skipped` (SC-011)
3. User review gate: stderr prompt, `y`/`n` response, `USER_REJECTED` status on `n`

**Steps:**
1. **[PLANNING]** Load portify-analysis.md (D-0023) as input for pipeline design
2. **[PLANNING]** Review SC-004 gate criteria: `step_mapping_count`, `model_count`, `gate_definition_count` frontmatter
3. **[EXECUTION]** Construct design-pipeline prompt with @path reference to analysis artifact
4. **[EXECUTION]** Execute Claude subprocess and parse portify-spec.md output
5. **[EXECUTION]** Implement --dry-run check: if active, emit dry_run contract with phases 3-4 marked skipped, halt execution
6. **[EXECUTION]** Implement user review gate: prompt on stderr, continue on `y`, halt with USER_REJECTED on `n`
7. **[VERIFICATION]** Run SC-004 STRICT gate: verify step_mapping_count, model_count, gate_definition_count frontmatter present
8. **[COMPLETION]** Log step timing, gate result, and review decision

**Acceptance Criteria:**
- `portify-spec.md` exists with `step_mapping_count`, `model_count`, `gate_definition_count` YAML frontmatter fields (SC-004)
- `--dry-run` halts after Step 4 and emits correct `dry_run` contract with phases 3-4 marked `skipped` (SC-011)
- User review gate prompts on stderr, accepts `y`/`n`, halts with `USER_REJECTED` status on `n`
- Step uses @path reference to portify-analysis.md from Step 3

**Validation:**
- `uv run pytest tests/cli_portify/test_design_pipeline.py -v` exits 0 (testing dry-run and review gate paths)
- Evidence: linkable artifact produced at D-0024/spec.md, D-0025/spec.md, D-0047/spec.md

**Dependencies:** T05.01, T02.03
**Rollback:** TBD (if not specified in roadmap)

---

### T05.03 -- Implement synthesize-spec Step (Step 5) with Sentinel Scan

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | Step 5 populates the release-spec-template.md from prior outputs, eliminates all {{SC_PLACEHOLDER:*}} sentinels, and retries on gate failure with specific placeholder names. |
| Effort | L |
| Risk | High |
| Risk Drivers | migration (template population), cross-cutting scope (all prior outputs), rollback (partial output re-run policy) |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0026, D-0027 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0026/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0027/spec.md

**Deliverables:**
1. `synthesize_spec` step implementation in `src/superclaude/cli/cli_portify/steps/synthesize_spec.py` that: verifies `release-spec-template.md` exists (fail-fast if missing per Recommendation #5), populates all template sections from Phase 1-2 outputs via @path, includes step consolidation mapping table (12 logical to 7 actual)
2. SC-003 self-validation: sentinel scan for remaining `{{SC_PLACEHOLDER:*}}` sentinels; on gate failure, retry prompt includes specific remaining placeholder names; resume policy: prefer re-running over trusting partially gated output

**Steps:**
1. **[PLANNING]** Verify `release-spec-template.md` exists (fail-fast if missing per Recommendation #5)
2. **[PLANNING]** Load portify-analysis.md (D-0023) and portify-spec.md (D-0024) as @path inputs
3. **[EXECUTION]** Construct synthesize-spec prompt with @path references to all prior artifacts
4. **[EXECUTION]** Execute Claude subprocess to populate template sections
5. **[EXECUTION]** Implement SC-003 sentinel scan: regex `\{\{SC_PLACEHOLDER:[^}]+\}\}` on output
6. **[EXECUTION]** On sentinel scan failure: construct retry prompt with specific remaining placeholder names
7. **[VERIFICATION]** Run SC-005 STRICT gate: zero remaining sentinels, 7 FRs with consolidation mapping
8. **[COMPLETION]** Log synthesis result, retry count, and gate outcome

**Acceptance Criteria:**
- Synthesized spec contains zero `{{SC_PLACEHOLDER:*}}` sentinels remaining (SC-005)
- Template `release-spec-template.md` is validated at startup; missing template triggers immediate fail-fast with clear error message
- Step consolidation mapping table (12 logical to 7 actual) is present in output
- Resume policy: on partial output, prefer re-running `synthesize-spec` over trusting partially gated output

**Validation:**
- `uv run pytest tests/cli_portify/test_synthesize_spec.py -v` exits 0 (testing sentinel scan, retry, template missing)
- Evidence: linkable artifact produced at D-0026/spec.md and D-0027/spec.md

**Dependencies:** T05.01, T05.02
**Rollback:** Re-run synthesize-spec (prefer re-run over trust per roadmap)
**Notes:** Risk: High due to R-1 (output truncation) and R-7 (partial output on resume). Template existence gated at startup per Recommendation #5.

---

### Checkpoint: End of Phase 5

**Purpose:** Verify all three core content generation artifacts are produced and gated successfully before quality amplification begins.
**Checkpoint Report Path:** .dev/releases/current/v2.24-cli-portify-cli-v4/checkpoints/CP-P05-END.md
**Verification:**
- portify-analysis.md passes SC-003 STRICT gate (5 sections, data flow diagram, 5 frontmatter fields)
- portify-spec.md passes SC-004 STRICT gate (step_mapping_count, model_count, gate_definition_count)
- Synthesized spec passes SC-005 STRICT gate (zero sentinels, 7 FRs with mapping)
**Exit Criteria:**
- All three artifacts generated and gated successfully (M4 criterion)
- --dry-run halts after design-pipeline with correct contract semantics
- Retry logic for unresolved placeholders is working and bounded
