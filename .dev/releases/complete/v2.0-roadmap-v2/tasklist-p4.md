# TASKLIST — sc:roadmap v2 — Phase 4: Adversarial Integration

**Parent Tasklist**: `tasklist-overview.md`
**Phase**: 4 of 7
**Task Range**: T04.01–T04.05
**Priority Wave**: P1
**Dependencies**: Phase 3 (M3: core generation pipeline for single-spec mode must work first); DEP-001: sc:adversarial skill must be available
**Tier Distribution**: STRICT: 1, STANDARD: 4, LIGHT: 0, EXEMPT: 0

---

## Phase 4: Adversarial Integration

Implement Wave 1A (sc:adversarial invocation for multi-spec and multi-roadmap modes) and the refs/adversarial-integration.md reference file. This phase enables sc:roadmap to consolidate multiple specification files and generate competing roadmap variants through adversarial debate, extending the single-spec pipeline built in Phases 1-3.

---

### T04.01 — Create refs/adversarial-integration.md reference document

**Roadmap Item ID(s):** R-018
**Why:** The adversarial integration reference documents mode detection logic, invocation patterns, return contract consumption, and error handling that Wave 1A and Wave 2 adversarial paths depend on.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0018
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0018/spec.md`

**Deliverables:**
- refs/adversarial-integration.md containing: mode detection logic, sc:adversarial invocation patterns (multi-spec and multi-roadmap), return contract consumption logic, error handling for success/partial/failed status, frontmatter population from adversarial results, divergent-specs heuristic

**Steps:**
1. **[PLANNING]** Load spec Sections 7.1 (sc:adversarial integration) and 9.5 (adversarial-integration.md spec)
2. **[PLANNING]** Confirm two invocation patterns: --compare (multi-spec) and --source --generate roadmap --agents (multi-roadmap)
3. **[EXECUTION]** Author mode detection logic: --specs → multi-spec, --multi-roadmap → multi-roadmap, both → combined
4. **[EXECUTION]** Author invocation patterns with exact sc:adversarial command formats from spec Section 7.1
5. **[EXECUTION]** Author return contract consumption: success → use merged_output_path; partial → convergence-based routing; failed → abort
6. **[EXECUTION]** Author error handling, frontmatter population rules, and divergent-specs heuristic (convergence <50% warning)
7. **[VERIFICATION]** Validate all status codes (success/partial/failed) have defined handling; verify convergence thresholds (60% and 50%)
8. **[COMPLETION]** Document contract consumption matrix

**Acceptance Criteria:**
- Documents both multi-spec and multi-roadmap invocation patterns per spec Section 7.1
- Return contract consumption handles success, partial (with convergence ≥60% and <60% branches), and failed status
- Divergent-specs heuristic warns at convergence <50%
- Frontmatter population rules for adversarial block fields documented

**Validation:**
- Manual check: Verify both invocation patterns match spec; verify all 3 status codes handled; verify convergence thresholds correct
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T01.01 (refs/ directory must exist)
**Rollback:** TBD
**Notes:** Per spec Section 9.5, this file documents how sc:roadmap CONSUMES the return contract (the schema itself is defined in SC-ADVERSARIAL-SPEC.md).

---

### T04.02 — Implement Wave 1A multi-spec consolidation via sc:adversarial

**Roadmap Item ID(s):** R-019
**Why:** Multi-spec consolidation merges multiple specification files into a unified spec before roadmap generation, enabling single-roadmap output from multiple input sources.
**Effort:** M
**Risk:** Medium
**Risk Drivers:** cross-cutting scope (multi-spec), data integrity
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0019
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0019/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0019/evidence.md`

**Deliverables:**
- Wave 1A multi-spec consolidation: invokes sc:adversarial --compare with provided spec files, handles return contract (success/partial/failed), records convergence_score in extraction.md warnings

**Steps:**
1. **[PLANNING]** Load refs/adversarial-integration.md for invocation pattern and return contract handling
2. **[PLANNING]** Confirm invocation format: `sc:adversarial --compare <spec-files> --depth <roadmap-depth> --output <roadmap-output-dir>`
3. **[EXECUTION]** Implement sc:adversarial invocation with --compare flag and spec file list from --specs argument
4. **[EXECUTION]** Implement return contract handling: success → use merged_output_path as Wave 1B input; partial ≥60% → proceed with warning; partial <60% → abort or prompt (if --interactive); failed → abort
5. **[EXECUTION]** Record convergence_score and artifacts_dir in adversarial frontmatter block
6. **[EXECUTION]** Apply divergent-specs heuristic: convergence <50% → emit warning about spec divergence
7. **[VERIFICATION]** Test with success, partial (≥60% and <60%), and failed status responses; verify correct routing
8. **[COMPLETION]** Document invocation flow and status handling matrix

**Acceptance Criteria:**
- Correctly invokes sc:adversarial --compare with --depth mapped from sc:roadmap --depth
- Handles all 3 return statuses: success → proceed, partial ≥60% → proceed with warning, partial <60% → abort/prompt, failed → abort
- convergence_score recorded in roadmap.md frontmatter adversarial block
- Divergent-specs warning emitted at convergence <50% per FR-003

**Validation:**
- Manual check: Verify invocation command format; verify all status paths handled; verify convergence recording
- Evidence: linkable artifact produced (evidence.md with status handling test matrix)

**Dependencies:** T04.01 (refs/adversarial-integration.md), T03.04 (single-spec pipeline must work first)
**Rollback:** TBD
**Notes:** Per roadmap risk R-004, adversarial debate + convergence thresholds mitigate incoherent unified spec risk. Per risk R-006, explicit convergence thresholds prevent silent quality degradation.

---

### T04.03 — Implement Wave 1A multi-roadmap generation via sc:adversarial

**Roadmap Item ID(s):** R-020
**Why:** Multi-roadmap generation produces competing roadmap variants using different model/persona configurations and merges the best elements, improving roadmap quality through adversarial diversity.
**Effort:** M
**Risk:** Medium
**Risk Drivers:** cross-cutting scope (multi-roadmap), system-wide
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0020
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0020/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0020/evidence.md`

**Deliverables:**
- Wave 2 multi-roadmap generation: invokes sc:adversarial --source --generate roadmap --agents with expanded agent specs, handles merged output, records adversarial metadata in frontmatter

**Steps:**
1. **[PLANNING]** Load refs/adversarial-integration.md for multi-roadmap invocation pattern
2. **[PLANNING]** Confirm invocation format: `sc:adversarial --source <spec> --generate roadmap --agents <agent-specs> --depth <roadmap-depth> --output <dir>`
3. **[EXECUTION]** Implement agent spec expansion: model-only agents inherit primary persona from Wave 1B (e.g., opus → opus:security)
4. **[EXECUTION]** Implement sc:adversarial invocation with --generate roadmap flag and expanded agent specs
5. **[EXECUTION]** Implement orchestrator addition when agent count ≥5 (per spec FR-004)
6. **[EXECUTION]** Handle return contract: success → use unified-roadmap.md for Wave 3-4; partial/failed → same routing as T04.02
7. **[VERIFICATION]** Test with 2-agent and 5+ agent configurations; verify orchestrator triggers at ≥5; verify persona expansion
8. **[COMPLETION]** Document agent expansion rules and invocation flow

**Acceptance Criteria:**
- Model-only agents correctly expand using primary persona from Wave 1B domain analysis
- sc:adversarial invoked with --generate roadmap flag and correctly formatted agent specs
- Orchestrator agent added when agent count ≥5 to coordinate adversarial debate rounds
- Agent count enforced in 2-10 range per spec FR-004

**Validation:**
- Manual check: Verify agent expansion logic; verify orchestrator trigger at ≥5; verify 2-10 range enforcement
- Evidence: linkable artifact produced (evidence.md with agent expansion examples)

**Dependencies:** T04.01 (refs/adversarial-integration.md), T04.02 (multi-spec path must work), T02.04 (domain classification for persona inheritance)
**Rollback:** TBD
**Notes:** Per spec FR-004, orchestrator at ≥5 agents prevents combinatorial explosion. Per spec FR-009, --depth flag maps to sc:adversarial --depth for debate round control.

---

### T04.04 — Implement agent specification parsing

**Roadmap Item ID(s):** R-021
**Why:** Agent specification parsing converts the model:persona:"instruction" format into structured agent configs, supporting model-only, mixed, and full specification patterns.
**Effort:** S
**Risk:** Low
**Risk Drivers:** model (keyword match — refers to AI model identifier, not database model)
**Tier:** STRICT
**Confidence:** [█████░░░░░] 52%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) (3-5K tokens, 60s timeout)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7 | Fallback Allowed: No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0021
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0021/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0021/evidence.md`

**Deliverables:**
- Agent specification parser handling 3 formats: model-only (e.g., "opus"), model:persona (e.g., "opus:architect"), and model:persona:"instruction" (full spec)

**Steps:**
1. **[PLANNING]** Load spec FR-004 agent spec format definition and parsing rule
2. **[PLANNING]** Confirm parsing rule: split on comma for agent list, split each on colon (max 3 segments), first = model, second = persona or quoted instruction, third = instruction
3. **[EXECUTION]** Implement comma-separated agent list splitting
4. **[EXECUTION]** Implement per-agent colon-splitting with 3-segment max: model (required), persona (optional, unquoted), instruction (optional, quoted)
5. **[EXECUTION]** Implement quoted-second-segment detection: if second segment is quoted → instruction (no persona)
6. **[EXECUTION]** Implement validation: agent count 2-10 range, all models validated against known list
7. **[VERIFICATION]** Test all 3 formats: model-only, model:persona, model:persona:"instruction"; test edge cases: quoted second segment, mixed formats in single list
8. **[COMPLETION]** Document parsing rules and test results with examples

**Acceptance Criteria:**
- Handles model-only, model:persona, and model:persona:"instruction" formats correctly
- Quoted second segment detected as instruction (not persona) per spec FR-004 parsing rule
- Agent count enforced: 2-10 range
- Mixed formats in a single --agents list handled correctly (e.g., opus:architect,sonnet,gpt52:security)

**Validation:**
- Manual check: Verify all 3 format examples from spec parse correctly; verify quoted detection; verify 2-10 range
- Evidence: linkable artifact produced (evidence.md with parsing test results)

**Dependencies:** T02.02 (model validation), T04.01 (adversarial integration reference)
**Rollback:** TBD
**Notes:** Tier conflict: "model" keyword matches STRICT (data category) but refers to AI model identifier in this context. Classification maintained as STRICT due to keyword priority rule. Confirmation recommended to verify appropriate tier.

---

### Checkpoint: Phase 4 / Tasks 01-04

**Purpose:** Validate adversarial reference doc and all invocation paths before interactive flag implementation.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P04-T01-T04.md`
**Verification:**
- refs/adversarial-integration.md is complete with both invocation patterns
- Multi-spec consolidation handles success/partial/failed status correctly
- Agent specification parsing handles all 3 format variations

**Exit Criteria:**
- Both adversarial invocation paths tested with mock responses
- Agent expansion logic verified with model-only and mixed format inputs
- Return contract consumption logic handles all convergence threshold branches

---

### T04.05 — Implement --interactive flag propagation to sc:adversarial

**Roadmap Item ID(s):** R-022
**Why:** The --interactive flag enables user approval at convergence thresholds and decision points during adversarial debate, providing human oversight for critical consolidation decisions.
**Effort:** XS
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0022
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0022/spec.md`

**Deliverables:**
- --interactive flag propagation from sc:roadmap to sc:adversarial invocations, enabling user prompts at convergence thresholds and decision points

**Steps:**
1. **[PLANNING]** Load spec FR-003 and FR-005 for --interactive behavior in multi-spec and combined modes
2. **[PLANNING]** Confirm propagation points: Wave 1A (multi-spec) and Wave 2 (multi-roadmap) adversarial invocations
3. **[EXECUTION]** Implement --interactive flag forwarding to sc:adversarial --compare invocation
4. **[EXECUTION]** Implement --interactive flag forwarding to sc:adversarial --generate invocation
5. **[VERIFICATION]** Verify flag appears in both invocation commands when --interactive is set; verify absent when not set
6. **[COMPLETION]** Document flag propagation points

**Acceptance Criteria:**
- --interactive flag propagated to sc:adversarial in both multi-spec and multi-roadmap invocations
- When --interactive not set, partial convergence <60% causes abort (not prompt)
- When --interactive set, partial convergence <60% prompts user for approval
- Flag propagation documented in refs/adversarial-integration.md invocation patterns

**Validation:**
- Manual check: Verify flag appears in invocation commands when set; verify abort vs prompt behavior at <60% convergence
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T04.02 (multi-spec invocation), T04.03 (multi-roadmap invocation)
**Rollback:** TBD
**Notes:** None.

---

### Checkpoint: End of Phase 4

**Purpose:** Final gate for adversarial integration; confirms multi-spec, multi-roadmap, and interactive modes are functional.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P04-END.md`
**Verification:**
- Multi-spec consolidation invokes sc:adversarial correctly with all status paths handled
- Multi-roadmap generation with agent expansion and orchestrator trigger works
- --interactive flag propagates to both adversarial invocation paths

**Exit Criteria:**
- All 5 tasks (T04.01-T04.05) marked complete with evidence artifacts
- Both adversarial modes functional with correct return contract handling
- Phase 7 dependency (adversarial integration for combined mode) confirmed available

---

**End of Phase 4** | Tasks: 5 | Deliverables: 5 (D-0018–D-0022) | Tier Distribution: STRICT: 1, STANDARD: 4, LIGHT: 0, EXEMPT: 0
