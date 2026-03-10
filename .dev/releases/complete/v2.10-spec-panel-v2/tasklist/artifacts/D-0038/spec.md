# D-0038: Rollback Plan

## Purpose

Phase-by-phase reversion steps to undo spec-panel v2 enhancements if post-release issues are discovered. Each phase can be reverted independently in reverse order.

---

## Phase 4 Rollback: Remove Correctness Focus and Pipeline Analysis

**Files affected**: `src/superclaude/commands/spec-panel.md`, `.claude/commands/sc/spec-panel.md`

**Steps**:
1. Remove the "Correctness Focus" subsection from Focus Areas (lines 263-302 approx)
2. Remove FR-14.1 through FR-14.6 (Modified Expert Behaviors Under Correctness Focus)
3. Remove FR-15.1 (State Variable Registry template)
4. Remove the "Review Heuristics" section entirely (Pipeline Dimensional Analysis: FR-17 through FR-21)
5. Remove the "Downstream Integration Wiring" table
6. Revert the Usage line to remove `--focus correctness` from the available flags
7. Run `make sync-dev` to update .claude/ copy

**Verification**: `wc -c` on spec-panel.md should return approximately 26,305 characters (Phase 2 size)

---

## Phase 2 Rollback: Remove Boundary Table and Structural Forcing Functions

**Files affected**: `src/superclaude/commands/spec-panel.md`, `.claude/commands/sc/spec-panel.md`

**Steps**:
1. Remove the "Mandatory Output Artifacts" section entirely
2. Remove the Guard Condition Boundary Table template and its subsections (Completion Criteria, Downstream Propagation)
3. Remove FR-8 (GAP Status Rule), FR-9 (Blank Behavior Rule), FR-10 (Synthesis-Blocking Gate)
4. Run `make sync-dev`

**Verification**: `wc -c` on spec-panel.md should return approximately 22,969 characters (Phase 1 size)

---

## Phase 1 Rollback: Remove Whittaker Adversarial Tester Persona

**Files affected**: `src/superclaude/commands/spec-panel.md`, `.claude/commands/sc/spec-panel.md`

**Steps**:
1. Remove the "Adversarial Testing Expert" section (James Whittaker persona, FR-2.1 through FR-2.5, FR-3)
2. Revert Expert Review Sequence from 11 experts back to 10 (remove Whittaker at position 6)
3. Update the Boundaries section: change "11 simulated experts" back to "10 simulated experts"
4. Remove the `adversarial_analysis` section from the Standard Format YAML example
5. Remove adversarial references from Structured Format and Detailed Format descriptions
6. Run `make sync-dev`

**Verification**: `wc -c` on spec-panel.md should return approximately 18,301 characters (pre-enhancement baseline)

---

## Full Rollback (All Phases)

Execute Phase 4, Phase 2, Phase 1 rollback in order. Alternative: `git revert` the commits from the feature branch.

**Git-based rollback**:
```bash
git log --oneline feature/v2.05-v2.08 -- src/superclaude/commands/spec-panel.md
# Identify commits related to spec-panel v2 enhancements
# Revert in reverse chronological order
```

---

## Traceability
- Roadmap Item: R-038
- Task: T05.03
- Deliverable: D-0038
