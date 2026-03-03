# Batch 1: Approach Artifacts Analysis

**Analysis date**: 2026-02-24
**Analyst**: claude-opus-4-6
**Source directory**: `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/`
**Files analyzed**: 3

---

## File 1: `approach-1-empirical-probe-first.md`

### Metadata
- **Author**: claude-opus-4-6 (system-architect persona)
- **Date**: 2026-02-23
- **Status**: PROPOSAL -- Pending approval before execution
- **Length**: 879 lines

### Summary

This document proposes an empirical validation strategy before committing to any sprint-spec changes. The core philosophy is "probe before rewrite": rather than modifying the 450-line sprint specification based on untested assumptions about `claude -p` behavior, spend 1-2 hours and ~$25-35 in API calls to empirically test whether `claude -p` can reliably invoke the sc:adversarial pipeline.

**Key components**:

1. **Three invocation strategies tested in parallel**:
   - S1: System-prompt injection (`--append-system-prompt` with full SKILL.md content) -- expected highest reliability
   - S2: Project-scoped command (`/project:sc:adversarial`) -- medium expected reliability
   - S3: Direct slash command (`/sc:adversarial`) -- lowest expected reliability (per GitHub Issue #837)

2. **13 test cases (T01-T13)** organized in 4 phases:
   - Phase 1: Smoke test (T01) -- confirm `claude -p` is functional
   - Phase 2: Strategy selection (T02-T04) -- test all three strategies in parallel
   - Phase 3: Deep validation (T05-T10, T12-T13) -- behavioral adherence scoring (20-point rubric), artifact production checks, multi-round debate verification, return contract validation, model differentiation, cost measurement, context pressure, error handling
   - Phase 4: Reliability test (T11) -- 10 identical runs of best strategy

3. **Three sequential decision gates**:
   - Gate 1 (Strategy Viability): at least one strategy produces artifacts
   - Gate 2 (Behavioral Quality): >=14/20 adherence, >=4/6 artifacts, multi-round debate, cost <$3
   - Gate 3 (Reliability): >=80% success rate across 10 runs (70-79% = add retry wrapper)

4. **Sprint-spec changes**: Proposes new Task 0.0A replacing original Task 0.0, modifications to Epic 1 Task 1.3 if probe succeeds, and unchanged Fallback-Only Sprint Variant if probe fails.

5. **Risk analysis**: 7 risks identified (A-G) covering unreliable success rates, mixed strategy results, cost unpredictability, SKILL.md size limits, CLI availability, and behavioral drift over time.

### Purpose

This artifact serves as a **risk-de-risking plan**. It ensures that no sprint implementation effort is wasted on an approach that might not work. It is the most conservative of the three approaches -- it defers all implementation decisions until empirical evidence is collected.

### Cross-References
- References GitHub Issues **#837** (slash commands broken in `-p` mode) and **#1048** (behavioral instruction adherence)
- References `sprint-spec.md` (the main sprint specification)
- References `sc-adversarial/SKILL.md` and `sc-roadmap/SKILL.md` (the two skill files involved)
- References `tasklist/evidence/` directory for all test output artifacts
- The probe fixtures (`spec-minimal.md`, `variant-a.md`, `variant-b.md`, `expected-schema.yaml`) are defined but not yet created
- Appendix B defines the `return-contract.yaml` JSON Schema used by T08
- Decision gate outcomes feed into Approaches 2 and 3 (determines viability of `claude -p` path)

---

## File 2: `approach-2-claude-p-proposal.md`

### Metadata
- **Author**: claude-opus-4-6 (system-architect persona)
- **Date**: 2026-02-23
- **Status**: PROPOSAL
- **Length**: 718 lines
- **Supersedes**: Skill tool invocation path (Task 0.0 primary path)

### Summary

This document proposes committing to `claude -p` as the primary invocation mechanism for the sc:adversarial pipeline, with the existing Task-agent fallback demoted to secondary status. Unlike Approach 1 (which probes first), this approach argues the evidence already strongly favors `claude -p` and designs the full implementation.

**Key arguments for commitment**:

1. The Skill tool has no callable API -- it is a conversational dispatch mechanism
2. Cross-skill invocation is architecturally blocked (cannot invoke sc:adversarial from within running sc:roadmap)
3. The fallback protocol is already the de-facto path (SKILL.md line 141 already acknowledges this)
4. `claude -p` provides genuine process isolation with separate context windows

**Core design**:

1. **Invocation pattern**: Raw prompt with SKILL.md injected via `--append-system-prompt`, NOT slash command invocation. The full command template uses `-p` for the task prompt, `--append-system-prompt` for behavioral instructions, `--allowedTools` for tool whitelist, `--max-budget-usd` for cost control, `--output-format json` for structured output, and `--dangerously-skip-permissions` for autonomous execution.

2. **Parameter configuration**: Model selection mapped from `--depth` flag (sonnet for quick/standard, opus for deep), budget mapped similarly ($1/$2/$5), timeout via Bash `timeout` command (300s default, 600s for deep).

3. **Output handling**: Primary validation is the file-based `return-contract.yaml`, not the JSON stdout. JSON output provides supplementary metadata (cost, duration, error status).

4. **Environment handling**: `CLAUDECODE` environment variable must be unset before invocation and restored after to prevent nested session detection.

5. **Error detection**: 8 error conditions mapped with detection methods and handling strategies.

**Sprint-spec modifications**: 14 specific changes across all 3 Epics, including Task 0.0 replacement (simplified to 3 lightweight tests), Task 1.3 complete rewrite (new sub-steps 3d-i through 3d-iv), new verb glossary entry, new reference file (`refs/headless-invocation.md`), optional `invocation_method` field in return contract schema.

**Risk analysis**: 6 risks (R-NEW-1 through R-NEW-6) with a comparison table showing `claude -p` vs. Task-agent fallback across 7 dimensions.

### Purpose

This artifact is a **complete implementation specification** for the `claude -p` approach. It provides the exact command templates, parameter mappings, error handling logic, and sprint-spec rewrites needed to implement the headless invocation path. It assumes `claude -p` will work and designs everything around that assumption, with the Task-agent fallback as a safety net.

### Cross-References
- References GitHub Issues **#837** and **#1048** (same as Approach 1)
- References `sprint-spec.md`, `sc-roadmap/SKILL.md`, `sc-adversarial/SKILL.md`, `adversarial-integration.md`
- References `tasklist-P6.md` (the phase 6 tasklist)
- Proposes creation of new file `refs/headless-invocation.md`
- Task 3.1 adds `invocation_method` field to return contract schema (shared concept with Approach 3)
- Section 5 provides the exact Wave 2 Step 3d rewrite text ready for insertion into SKILL.md
- Section 9 lists 4 open decision points for sprint planning

---

## File 3: `approach-3-hybrid-dual-path.md`

### Metadata
- **Author**: (implied claude-opus-4-6, not explicitly stated)
- **Date**: 2026-02-23
- **Status**: PROPOSAL (not yet accepted)
- **Length**: 1121 lines (longest of the three)

### Summary

This document proposes a hybrid architecture where both `claude -p` (Path A) and an enhanced Task-agent pipeline (Path B) are treated as first-class citizens with a runtime routing layer selecting the optimal path. Neither is "primary" or "fallback" -- the return contract is the abstraction boundary that makes the choice invisible to downstream consumers.

**Four problems addressed**:

1. **Environment portability**: `claude -p` is not universally available; Task agents are
2. **Mid-pipeline fragility**: If headless crashes mid-pipeline, artifacts are wasted without recovery
3. **Quality tiering misalignment**: `--depth` should influence invocation strategy, not just debate rounds
4. **Future-proofing**: Third path (native Skill tool API) should slot in without consumer changes

**Core architecture**:

1. **Runtime routing decision tree**: 4-step process -- user override check, binary availability check, execution probe, depth-based routing. Introduces `--invocation-mode` flag (`headless`/`inline`/`auto`).

2. **Path A (claude -p headless)**: Same invocation pattern as Approach 2 but activated conditionally for `--depth standard|deep` only. Quick depth routes to Path B (overhead not justified for single-round debate).

3. **Path B (enhanced Task-agent pipeline)**: Upgraded from the current 3-step compressed fallback (F1, F2/3, F4/5) to a full 5-step pipeline (F1-F5 + FC). Each Task agent receives its instructions inline from SKILL.md sections, not by reference. Real convergence tracking replaces the 0.5 sentinel. Includes multi-round debate with configurable rounds based on `--depth`.

4. **Mid-pipeline fallover**: If headless crashes partway, artifact inventory determines the resume point. 5 resume scenarios mapped (all steps present, steps 1-3 present, step 1 only, variants only, nothing). Produces `invocation_method: "headless+task_agent"` in the return contract.

5. **Return contract as universal interface**: The architectural centerpiece. 5 invariants defined: schema identity, consumer ignorance, quality equivalence, third-path readiness, convergence score consistency. New 10th field `invocation_method` (enum: headless/task_agent/headless+task_agent/skill). `fallback_mode` field deprecated in favor of `invocation_method`.

**Sprint-spec modifications**: Task 0.0 replaced with "Invocation Capability Probe" (probes both paths), Epic 1 Task T02.03 rewritten with routing + two execution branches, 4 new verb glossary entries, return contract schema v2 with 10th field.

**Risk analysis**: 6 risks (R1-R6) covering maintenance complexity, testing burden, behavioral drift between paths, `claude -p` reliability, mid-pipeline fallover complexity, and token cost overhead.

**Verification plan**: 6 test specifications (V1-V6) covering each path independently, routing logic, mid-pipeline fallover, output quality comparison, and schema consistency.

### Purpose

This artifact is the **most architecturally sophisticated** of the three approaches. It provides a comprehensive dual-path system with graceful degradation, runtime routing, mid-pipeline recovery, and future extensibility. It is also the most complex to implement and maintain.

### Cross-References
- References `tasklist-P6.md` (the phase 6 tasklist) for current sprint spec structure
- References `sc-adversarial/SKILL.md` with specific line numbers for section extraction (lines 411-749, 753-856, 1049-1299)
- References GitHub Issue **#1048** (behavioral instruction adherence in headless mode)
- Appendix A provides explicit comparison table with Approaches 1 and 2 across 10 dimensions
- Shares the `invocation_method` return contract field concept with Approach 2
- Shares the `--append-system-prompt` injection pattern with Approach 2
- The `--invocation-mode` flag is unique to Approach 3

---

## Cross-File Relationships

### Shared Concepts Across All Three Approaches

| Concept | Approach 1 | Approach 2 | Approach 3 |
|---------|------------|------------|------------|
| `claude -p` invocation | Tested empirically (3 strategies) | Committed as primary | Runtime-routed (Path A) |
| `--append-system-prompt` | Tested as Strategy S1 | Used as sole mechanism | Used for Path A |
| Task-agent fallback | Unchanged from current spec | Demoted to secondary | Upgraded to full 5-step (Path B) |
| Return contract schema | 9 fields (validated in T08) | 9+1 fields (invocation_method) | 9+1 fields (invocation_method) |
| Convergence tracking | Not addressed (fallback uses 0.5) | Real in headless, enhanced in fallback | Real in both paths |
| `CLAUDECODE` env handling | Not addressed | Documented (save/unset/restore) | Implied via Approach 2 pattern |
| GitHub #837, #1048 | Central motivation | Central motivation | Central motivation |

### Decision Flow Between Approaches

The three approaches form a decision tree:

1. **Start with Approach 1** (empirical probe) to determine `claude -p` viability
2. **If probe succeeds** (Gates 1-3 pass): implement either Approach 2 (simpler, primary/fallback model) or Approach 3 (more robust, dual-path model)
3. **If probe fails** (any gate fails): fall back to Task-agent-only variant (already defined in sprint spec, enhanced by Approach 3's Path B upgrades)

### Key Architectural Difference

- **Approach 1**: Does not prescribe an architecture. It is a validation methodology.
- **Approach 2**: Prescribes a primary/fallback hierarchy. `claude -p` is the intended path; Task agents are the safety net.
- **Approach 3**: Prescribes a peer architecture with runtime routing. Both paths are legitimate depending on context. Includes mid-pipeline recovery that neither Approach 1 nor 2 addresses.

### Complexity vs. Robustness Tradeoff

| Dimension | Approach 1 | Approach 2 | Approach 3 |
|-----------|------------|------------|------------|
| Sprint complexity | Low (probe only) | Medium | High |
| Implementation risk | Lowest (defers decisions) | Medium | Highest (most code paths) |
| Robustness | N/A (validation only) | Good (fallback covers CLI absence) | Best (mid-pipeline recovery, depth routing) |
| Maintenance burden | None (one-time probe) | Medium (2 paths) | Medium-High (2 peer paths + router) |
| Quality floor (no `claude -p`) | ~70% (current fallback) | ~85-90% (enhanced fallback) | ~85-90% (enhanced Path B) |
| Quality ceiling (with `claude -p`) | ~95% (if probe passes) | ~95% | ~95% |
