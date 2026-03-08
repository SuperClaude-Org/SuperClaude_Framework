---
spec_source: "spec-roadmap-pipeline-reliability.md"
complexity_score: 0.72
primary_persona: analyzer
---

# 1. Executive summary

This roadmap addresses a moderate-complexity reliability issue in the roadmap pipeline: frontmatter detection is too strict, prompt outputs are insufficiently constrained, and extraction protocol parity has drifted from the source template. The failure mode is systemic because `_check_frontmatter()` is shared infrastructure, while the artifact corruption path is roadmap-specific due to executor flow and prompt behavior.

From an analyzer perspective, the critical insight is that this is not a single-bug fix. It is a **defense-in-depth reliability program** across four layers:

1. **Detection correctness** in shared gate infrastructure.
2. **Artifact sanitation** in the roadmap executor.
3. **Prompt hardening** to reduce malformed outputs at the source.
4. **Protocol parity and regression coverage** so downstream steps remain stable.

The roadmap should prioritize:
- Backward-compatible fixes first.
- Isolation of roadmap-specific behavior from shared pipeline infrastructure.
- Evidence-driven validation through unit and end-to-end tests.
- Explicit mitigation of probabilistic LLM behavior with deterministic safeguards.

## Primary objectives

1. Restore reliable YAML frontmatter detection across pipeline artifacts.
2. Prevent preamble contamination from causing gate failures.
3. Align extraction outputs with the canonical 13+ field protocol.
4. Preserve existing behavior for non-roadmap pipeline consumers.
5. Prove stability with targeted regression and end-to-end validation.

---

# 2. Phased implementation plan with milestones

## Phase 0. Baseline analysis and scope confirmation

### Goals
Establish the exact current behavior, confirm shared usage of gate logic, and identify all prompt builders and downstream consumers affected by protocol changes.

### Action items
1. Inventory all current callers and uses of:
   - `src/superclaude/cli/pipeline/gates.py`
   - `src/superclaude/cli/roadmap/executor.py`
   - `src/superclaude/cli/roadmap/prompts.py`
   - `src/superclaude/cli/roadmap/gates.py`
2. Confirm the canonical extraction frontmatter field set from:
   - `src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`
3. Trace the roadmap run sequence to verify where subprocess output is written, sanitized, embedded, and validated.
4. Capture representative failing and passing artifacts for test fixtures.

### Deliverables
- Impact map of shared vs roadmap-specific components.
- Canonical field checklist for extraction frontmatter.
- Fixture set for malformed, valid, and edge-case artifacts.

### Milestone
**M0: Verified scope and reference baseline established**

---

## Phase 1. Shared gate reliability fix

### Goals
Make `_check_frontmatter()` robust enough to find valid YAML frontmatter anywhere in the document without introducing false positives or regressions.

### Action items
1. Refactor `_check_frontmatter()` to:
   - Use a module-level compiled `_FRONTMATTER_PATTERN`.
   - Use `re.MULTILINE`.
   - Search the full document, not only byte 0.
2. Require at least one `key: value` line between `---` delimiters.
3. Parse discovered frontmatter into field names and validate all `required_fields`.
4. Ensure return semantics remain stable:
   - `(True, None)` for valid block with all required fields.
   - `(False, reason)` for missing block or missing required fields.
5. Add regression tests covering:
   - Frontmatter at top of file.
   - Frontmatter after preamble.
   - Horizontal rule only.
   - Missing required field.
   - Extra fields present.
   - Multiple delimiter blocks.
   - Shared pipeline compatibility cases.
   - Empty or malformed key-value sections.

### Deliverables
- Updated shared gate implementation.
- Full unit test coverage for frontmatter detection logic.

### Milestone
**M1: Shared frontmatter validation is correct and backward-compatible**

---

## Phase 2. Roadmap executor sanitization

### Goals
Ensure roadmap artifact files are normalized before gate validation, without expanding sanitizer behavior into unrelated pipelines.

### Action items
1. Add `_sanitize_output()` to `src/superclaude/cli/roadmap/executor.py`.
2. Implement behavior:
   - No-op if file already starts with frontmatter after whitespace stripping.
   - No-op if no valid frontmatter block is found.
   - Strip only content before the first valid frontmatter block.
3. Use atomic write strategy:
   - Write to temp file.
   - Replace original via `os.replace`.
4. Preserve UTF-8 encoding.
5. Log stripped preamble byte count.
6. Invoke sanitizer in `roadmap_run_step()`:
   - After subprocess completion.
   - Before gate validation.
7. Add tests for:
   - Clean file.
   - File with preamble.
   - File with no frontmatter.
   - Atomic rewrite success path.
   - Encoding preservation.
   - Large-file behavior up to 10MB.

### Deliverables
- Sanitizer implementation with atomic rewrite semantics.
- Executor integration.
- Sanitizer-specific tests.

### Milestone
**M2: Roadmap artifacts are normalized before validation**

---

## Phase 3. Prompt hardening for all roadmap steps

### Goals
Reduce malformed LLM outputs at the source by making output constraints explicit, recent, and uniform across all roadmap prompt builders.

### Action items
1. Update all 7 `build_*_prompt()` functions to append `<output_format>` blocks.
2. Ensure each output block includes:
   - Explicit requirement to start immediately with `---`.
   - Explicit prohibition on introductory text.
   - Minimal valid template showing expected first lines.
3. Place the output constraint at the end of each prompt.
4. Keep token impact within NFR limits:
   - No more than +200 tokens per prompt function.
5. Add prompt tests/checks verifying:
   - Presence of `<output_format>`.
   - Required negative/positive instructions.
   - End-of-prompt placement.

### Deliverables
- Hardened prompt builders across all roadmap steps.
- Prompt-structure validation tests.

### Milestone
**M3: Prompt contracts are explicit, consistent, and recency-optimized**

---

## Phase 4. Extraction protocol parity and downstream compatibility

### Goals
Align extraction output with the source protocol template and ensure downstream consumers continue to operate correctly.

### Action items
1. Expand `build_extract_prompt()` to require the canonical frontmatter fields:
   - `spec_source`
   - `generated`
   - `generator`
   - `functional_requirements`
   - `nonfunctional_requirements`
   - `total_requirements`
   - `complexity_score`
   - `complexity_class`
   - `domains_detected`
   - `risks_identified`
   - `dependencies_identified`
   - `success_criteria_count`
   - `extraction_mode`
2. Ensure prompt body requests structured sections for:
   - Functional requirements
   - Non-functional requirements
   - Complexity assessment with rationale
   - Architectural constraints
   - Risk inventory
   - Dependency inventory
   - Success criteria
   - Open questions
3. Update `EXTRACT_GATE` required fields to match the expanded protocol.
4. Keep executor-populated fields out of the LLM contract:
   - Example: `pipeline_diagnostics`
5. Review `generate` step consumption of extraction artifacts and adjust if needed so expanded extraction does not cause drift or dead fields.
6. Add parity tests asserting:
   - Prompt field list matches protocol template.
   - Gate required fields match prompt contract.
   - Executor injects runtime-only fields.
   - Downstream roadmap generation continues to parse extraction artifacts successfully.

### Deliverables
- Protocol-aligned extraction prompt.
- Updated extract gate.
- Compatibility coverage for generate/downstream steps.

### Milestone
**M4: Extraction protocol is canonical and downstream-safe**

---

## Phase 5. End-to-end validation and release readiness

### Goals
Demonstrate that the full roadmap pipeline completes without frontmatter failures and without regressions in shared behavior.

### Action items
1. Run targeted unit suites for:
   - Gate validation
   - Sanitizer behavior
   - Prompt hardening
   - Protocol parity
2. Run full roadmap pipeline scenario:
   - `superclaude roadmap run <spec> --depth deep --agents opus:architect,haiku:analyzer`
3. Inspect all generated `.md` artifacts for:
   - Immediate frontmatter start.
   - No preamble contamination.
   - Required field completeness.
4. Run regression checks for other pipeline commands sharing `_check_frontmatter()`.
5. Record evidence for each success criterion.

### Deliverables
- End-to-end validation report.
- Regression evidence for shared pipeline commands.
- Release decision: pass / blocked / conditional pass.

### Milestone
**M5: Reliability fix validated end-to-end and ready for merge**

---

# 3. Risk assessment and mitigation strategies

## Risk 1. Shared gate regression in non-roadmap pipelines
- **Severity:** High
- **Probability:** Low to medium
- **Why it matters:** `_check_frontmatter()` is shared infrastructure, so an overfitted fix could break unrelated commands.
- **Mitigation:**
  1. Preserve existing success semantics.
  2. Use backward-compatible regex logic.
  3. Add regression fixtures from other pipeline consumers.
  4. Keep roadmap-specific sanitization out of shared pipeline code.
- **Validation evidence:**
  - Existing passing fixtures still pass.
  - Shared pipeline regression suite remains green.

## Risk 2. False positive match of markdown horizontal rules
- **Severity:** High
- **Probability:** Low
- **Why it matters:** A false positive would let invalid artifacts pass or strip the wrong content.
- **Mitigation:**
  1. Require at least one `key: value` line in the matched block.
  2. Test files containing horizontal rules but no YAML.
  3. Prefer strict field parsing after regex discovery.
- **Validation evidence:**
  - Horizontal-rule-only fixtures fail validation.
  - Mixed markdown fixtures do not misclassify.

## Risk 3. Sanitizer removes legitimate content
- **Severity:** High
- **Probability:** Low
- **Why it matters:** Over-aggressive sanitation could destroy meaningful artifact data.
- **Mitigation:**
  1. Strip only before the first valid frontmatter block.
  2. No-op when no valid frontmatter exists.
  3. Use atomic write to preserve original on failure.
  4. Log stripped byte count for diagnosability.
- **Validation evidence:**
  - Input/output fixture comparisons.
  - Recovery-safe temp file behavior.
  - Idempotence tests.

## Risk 4. Prompt hardening does not fully eliminate preambles
- **Severity:** Medium
- **Probability:** Medium
- **Why it matters:** LLM compliance is probabilistic; prompts alone are not sufficient.
- **Mitigation:**
  1. Treat prompt hardening as additive, not primary control.
  2. Keep gate and sanitizer as deterministic safeguards.
  3. Measure actual artifact cleanliness in E2E runs.
- **Validation evidence:**
  - Prompt tests pass.
  - Sanitizer usage rate trends downward over time.
  - E2E artifacts remain clean even with occasional preambles.

## Risk 5. Protocol parity changes break generate or later steps
- **Severity:** Medium
- **Probability:** Medium
- **Why it matters:** Expanded extraction output changes the contract consumed downstream.
- **Mitigation:**
  1. Update both prompt and gate in the same change set.
  2. Validate against protocol template as source of truth.
  3. Review generate-step assumptions explicitly.
  4. Add downstream compatibility tests.
- **Validation evidence:**
  - Generate step parses expanded extraction without failure.
  - Full 8-step pipeline completes.

## Risk 6. Runtime diagnostics field ownership becomes ambiguous
- **Severity:** Medium
- **Probability:** Low
- **Why it matters:** If LLM and executor both attempt to own the same metadata, artifacts become inconsistent.
- **Mitigation:**
  1. Separate LLM-authored fields from executor-authored fields.
  2. Document runtime-only field injection in executor flow.
  3. Test that executor appends/injects diagnostics consistently.
- **Validation evidence:**
  - Extraction prompt excludes runtime-only fields.
  - Executor test confirms `pipeline_diagnostics` injection behavior.

---

# 4. Resource requirements and dependencies

## Engineering resources

### Primary roles
1. **Analyzer / backend-oriented implementer**
   - Shared gate logic
   - Executor sequencing
   - test strategy design
2. **QA / quality engineer**
   - Fixture design
   - regression coverage
   - end-to-end pipeline validation
3. **Documentation/protocol reviewer**
   - field parity review against source template
   - prompt contract consistency

### Estimated effort by phase
1. Phase 0: 0.5 day
2. Phase 1: 1.0 day
3. Phase 2: 0.5-1.0 day
4. Phase 3: 0.5 day
5. Phase 4: 0.5-1.0 day
6. Phase 5: 0.5 day

**Total estimated effort:** 3.5-4.5 engineering days

## Technical dependencies

1. **Python stdlib `re`**
   - Required for multiline frontmatter discovery and parsing.
2. **Python stdlib `os`**
   - Required for atomic replace.
3. **Python stdlib `pathlib.Path`**
   - Required for file handling.
4. **Python stdlib `logging`**
   - Required for sanitizer observability.
5. **Canonical protocol template**
   - `src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`
6. **Claude subprocess integration**
   - Artifact production path must remain stable enough for post-process sanitation.

## Test and validation resources

1. Unit test fixtures for malformed and valid artifacts.
2. Large artifact sample near 10MB for NFR confirmation.
3. At least one real roadmap spec for end-to-end validation.
4. Baseline artifact samples from current failing behavior.

## Operational prerequisites

1. Ability to run targeted pytest suites with UV.
2. Access to sample roadmap pipeline outputs.
3. Stable local environment for end-to-end subprocess execution.

---

# 5. Success criteria and validation approach

## Success criteria

1. **Full pipeline completion**
   - The roadmap pipeline completes all 8 steps without frontmatter-related failures.
2. **Clean artifacts**
   - Final artifact `.md` files begin with YAML frontmatter and contain no preamble text.
3. **Protocol-complete extraction**
   - Extraction frontmatter contains the full required 13+ field set.
4. **Green targeted test suite**
   - All unit tests for gate logic, sanitizer logic, prompt hardening, and protocol parity pass.
5. **No shared-pipeline regressions**
   - Other consumers of `_check_frontmatter()` continue to validate correctly.

## Validation approach

### A. Unit validation
1. Gate logic tests:
   - Discovery anywhere in file.
   - Required-field enforcement.
   - False-positive rejection.
2. Sanitizer tests:
   - No-op cases.
   - Strip cases.
   - Atomic rewrite path.
   - encoding preservation.
3. Prompt tests:
   - Output block presence.
   - Start-with-frontmatter instruction.
   - No-preamble prohibition.
   - placement at end.
4. Protocol parity tests:
   - Prompt fields vs template.
   - Gate fields vs prompt contract.
   - executor-only fields excluded from LLM request.

### B. Integration validation
1. Run roadmap pipeline on representative spec input.
2. Confirm each intermediate artifact is frontmatter-clean.
3. Confirm extraction artifact includes expanded field set.
4. Confirm downstream generate step still succeeds.

### C. Regression validation
1. Re-run tests for other shared pipeline commands.
2. Validate existing passing artifacts continue to pass.
3. Confirm no new false negatives introduced by stricter pattern matching.

### D. Observability checks
1. Review sanitizer logs for stripped byte counts.
2. Confirm sanitation occurs only when needed.
3. Use log evidence to distinguish LLM behavior issues from executor/gate issues.

---

# 6. Timeline estimates per phase

## Recommended schedule

### Phase 0. Baseline analysis and scope confirmation
- **Estimate:** 0.5 day
- **Exit criteria:** Impact map, canonical field list, and fixture plan complete.

### Phase 1. Shared gate reliability fix
- **Estimate:** 1.0 day
- **Exit criteria:** `_check_frontmatter()` updated and unit coverage complete.

### Phase 2. Roadmap executor sanitization
- **Estimate:** 0.5-1.0 day
- **Exit criteria:** `_sanitize_output()` integrated with atomic rewrite and tests.

### Phase 3. Prompt hardening for all roadmap steps
- **Estimate:** 0.5 day
- **Exit criteria:** All prompt builders include valid end-positioned output constraints.

### Phase 4. Extraction protocol parity and downstream compatibility
- **Estimate:** 0.5-1.0 day
- **Exit criteria:** Extract prompt, gate, and downstream consumer alignment verified.

### Phase 5. End-to-end validation and release readiness
- **Estimate:** 0.5 day
- **Exit criteria:** Full pipeline run passes and shared regression evidence is recorded.

## Overall timeline
- **Best case:** 3.5 days
- **Expected:** 4 days
- **Buffer-inclusive:** 4.5 days

---

# Recommended implementation ordering

1. **Phase 1 first** — fixes the shared validation defect at its root.
2. **Phase 2 second** — adds deterministic cleanup for roadmap-specific contamination.
3. **Phase 3 third** — reduces malformed outputs upstream.
4. **Phase 4 fourth** — restores protocol integrity and downstream stability.
5. **Phase 5 last** — confirms the system behaves correctly as a whole.

This ordering minimizes risk because it first repairs core validation logic, then constrains artifact quality, then aligns protocol contracts. It avoids the common failure pattern of changing prompts before deterministic validators and consumers are ready.

---

# Analyzer recommendations

1. **Do not collapse gate and sanitizer into one layer.**
   - Shared validation and roadmap-specific repair solve different problems and should remain separated.

2. **Treat protocol template parity as a release gate, not a documentation task.**
   - Drift between prompt, gate, and template is a direct source of runtime failures.

3. **Require evidence for backward compatibility.**
   - Because `_check_frontmatter()` is shared infrastructure, regression proof is mandatory.

4. **Track sanitizer invocation frequency after rollout.**
   - If sanitizer usage remains high, the root cause is still prompt or subprocess behavior, not just validation.

5. **Explicitly review `generate` step assumptions during implementation.**
   - The extraction expansion is likely safe, but analyzer review should verify the actual consumer contract rather than assume compatibility.

6. **Preserve defense in depth.**
   - Prompt compliance, sanitation, and validation should all remain in place even if one layer appears sufficient in testing.
