# Adversarial Debate Transcript: Execution Mode Annotation (Q8)

## Debate Protocol
- **Format**: 3-variant adversarial debate across 5 dimensions
- **Rounds**: 2 rounds per dimension (opening + rebuttal)
- **Convergence threshold**: 70% agreement per dimension

---

## Dimension 1: Accuracy

### Round 1 -- Opening Arguments

**Advocate-Auto (A)**:
The heuristics for detecting Python-executable phases are narrow and well-defined. The signal set is:
1. All tasks in phase classified EXEMPT (already computed by tier classification)
2. Step text contains backtick-quoted shell commands
3. No steps involve `Edit`, `Write`, `MultiEdit` operations on source code
4. Phase description matches validation/gate keywords

These signals are already partially computed during tier classification. The marginal accuracy cost is low. In the v2.24.5 corpus, Phase 0 matches all four signals with no ambiguity. The heuristics are conservative -- they only fire when ALL signals align, producing low false-positive rates.

False negatives (missing a Python-executable phase) are benign: the phase simply runs in Claude mode, which is a superset of Python mode capabilities. No harm, only missed optimization.

**Advocate-Manual (B)**:
Heuristic accuracy is unknowable without a large corpus of roadmaps. The v2.24.5 Phase 0 is a single data point -- cherry-picked to be the obvious case. Real-world roadmaps will contain:
- EXEMPT phases that require Claude judgment ("review results and determine if...")
- Phases with shell commands embedded in explanatory text, not as executable steps
- Phases where some tasks are shell-executable but others require reasoning

The accuracy claim of "~90%" is an estimate with no validation data. Manual annotation has 100% precision when applied -- the only failure mode is omission, which is a workflow problem, not an accuracy problem.

**Advocate-Hybrid (C)**:
Both sides overstate their case. Auto's accuracy is plausible for the obvious cases but unproven for edge cases. Manual's "100% when applied" is tautological and ignores the real-world omission rate.

Hybrid captures Auto's detection accuracy for obvious cases while providing a review checkpoint that catches false positives. The `--dry-run` presentation makes accuracy errors visible before they cause harm.

### Round 1 -- Scoring Matrix

| Criterion | Auto (A) | Manual (B) | Hybrid (C) |
|-----------|----------|------------|------------|
| Precision (avoiding false positives) | 7/10 | 10/10 | 9/10 |
| Recall (catching all python phases) | 8/10 | 5/10 | 8/10 |
| F1 balance | 7.5/10 | 6.7/10 | 8.5/10 |

### Round 2 -- Rebuttals

**A rebuts B**: Manual's "100% precision when applied" masks the critical failure mode: omission. In practice, roadmap authors will forget the annotation for most phases because it is a new, unfamiliar metadata field. The effective recall of Manual approaches 0% for casual users. A system that never fires is not accurate -- it is absent.

**B rebuts A**: The "benign false negative" argument is only true if Python mode is purely an optimization. If execution_mode affects how the sprint executor routes tasks (e.g., skipping Claude API calls, using subprocess directly), then a false positive is not benign -- it could skip reasoning that the phase actually requires. The safety cost of a false positive is asymmetric.

**C rebuts both**: A's false-negative-is-benign argument holds only if Python mode is optional optimization. B's omission problem is real. Hybrid addresses both: detection reduces omissions, review prevents false positives.

### Dimension 1 Convergence: 65%
- Agreement: All three agree that obvious cases (like Phase 0) are detectable. All agree that edge cases exist.
- Disagreement: Whether heuristic accuracy is "good enough" without review. Whether omission rate matters.

---

## Dimension 2: Safety

### Round 1 -- Opening Arguments

**Advocate-Auto (A)**:
The safety risk of auto-annotation is bounded by the conservative heuristic design. The heuristics require ALL signals to align -- any single non-EXEMPT task, any non-shell step, any code-modification step disqualifies the phase. This is a conjunction, not a disjunction. The false positive rate for a 4-signal conjunction is the product of individual false positive rates.

Furthermore, the sprint executor should validate execution_mode before executing. If a phase marked `python` contains steps that fail in Python mode, the executor errors out and falls back to Claude mode. Defense in depth.

**Advocate-Manual (B)**:
"Defense in depth" assumes the sprint executor has fallback logic for execution_mode misclassification. This does not exist today -- it would need to be built. Auto is proposing to build two systems (heuristic detection + executor fallback) instead of one (manual annotation).

The safety-critical scenario: a phase says "Run `uv run pytest` and if tests fail, analyze the failures to determine root cause." The heuristic sees: EXEMPT tier, backtick shell command, no file modifications. It annotates `python`. But the second clause ("analyze failures to determine root cause") requires Claude reasoning. Python mode would execute the shell command but skip the analysis, producing incomplete results silently.

**Advocate-Hybrid (C)**:
B's scenario is the strongest argument against Auto. It is also the strongest argument FOR Hybrid -- the `--dry-run` review would surface this exact case for human judgment. The provisional annotation `execution_mode: python (auto-detected)` explicitly invites scrutiny.

Safety is not about eliminating all risk -- it is about making risks visible and controllable. Hybrid makes detection risks visible. Manual makes them invisible (because omission is invisible).

### Round 1 -- Scoring Matrix

| Criterion | Auto (A) | Manual (B) | Hybrid (C) |
|-----------|----------|------------|------------|
| Worst-case failure severity | 4/10 | 8/10 | 7/10 |
| Defense in depth | 5/10 | 9/10 | 8/10 |
| Risk visibility | 3/10 | 7/10 | 9/10 |

### Round 2 -- Rebuttals

**A rebuts B**: The "analyze failures" scenario is a misclassification of the task's tier. A task that requires reasoning should be classified STANDARD or STRICT, not EXEMPT. If the tier classifier correctly identifies it as non-EXEMPT, the heuristic never fires. The safety risk is really a tier classification accuracy problem, not an execution_mode detection problem.

**B rebuts A**: Tier classification is also heuristic-based. Compounding two heuristic systems (tier + execution_mode) multiplies the error probability. Each heuristic layer adds uncertainty. Manual annotation is a single decision with no compounding.

**C rebuts both**: A's argument that tier classification catches the error is valid but assumes tier classification is accurate -- which is itself an open question. B's compounding argument is mathematically correct but practically overstated -- the heuristics are correlated, not independent. Hybrid acknowledges both uncertainties and provides a review checkpoint.

### Dimension 2 Convergence: 60%
- Agreement: All agree that false positives (marking a judgment-requiring phase as `python`) are the primary safety risk. All agree that some form of human oversight is desirable for safety-critical decisions.
- Disagreement: Whether the conjunction of heuristics is sufficient safety, or whether explicit review is required.

---

## Dimension 3: User Control

### Round 1 -- Opening Arguments

**Advocate-Manual (B)**:
Manual annotation gives users complete control. The roadmap is the single source of truth for execution intent. Users declare what they mean, and the system respects it. No surprises, no overrides needed.

This aligns with the SuperClaude principle of explicit over implicit. The framework already has explicit tier overrides, explicit persona activation, explicit MCP flags. Execution mode should follow the same pattern.

**Advocate-Auto (A)**:
"Complete control" is theoretical. In practice, users want the system to do the right thing without manual intervention. The tier classification system is already automatic -- users do not manually annotate every task with STRICT/STANDARD/LIGHT/EXEMPT. They trust the generator. Execution mode should work the same way.

Users who want control can override: `--no-auto-execution-mode` disables detection; manual annotations in the roadmap override auto-detection. The override mechanism preserves control for users who want it.

**Advocate-Hybrid (C)**:
Hybrid gives users informed control. Instead of choosing between "system decides" and "user decides," Hybrid presents the system's recommendation and lets the user ratify or override. This is the UX pattern used in IDEs (suggested imports, auto-completions) and is well-understood.

### Round 1 -- Scoring Matrix

| Criterion | Auto (A) | Manual (B) | Hybrid (C) |
|-----------|----------|------------|------------|
| Default user control | 4/10 | 10/10 | 8/10 |
| Override mechanism | 7/10 | 10/10 | 9/10 |
| Discoverability | 6/10 | 3/10 | 8/10 |

### Round 2 -- Rebuttals

**B rebuts A**: The analogy to tier classification is flawed. Tier classification is a well-understood, extensively documented system with 40+ keywords, compound phrase overrides, and context boosters (see tier-classification.md). It has been refined over multiple releases. Execution mode detection would be a brand-new heuristic with no track record. Users trust tier classification because it has been validated. Execution mode detection has not.

**A rebuts B**: Manual annotation requires users to know about execution_mode, understand what it means, and remember to annotate it. This is a discoverability problem. Most users will never discover the feature because it requires proactive learning. Auto-detection surfaces the capability without requiring user knowledge.

**C rebuts both**: Both are right. Manual has a discoverability problem. Auto has a trust problem. Hybrid solves both: the `--dry-run` output teaches users about execution_mode (discoverability) while giving them control over the final decision (trust).

### Dimension 3 Convergence: 70%
- Agreement: All agree that override mechanisms are necessary regardless of the approach. All agree that discoverability matters.
- Disagreement: Whether users should opt-in (Manual) or opt-out (Auto) of execution mode annotation.

---

## Dimension 4: Workflow Friction

### Round 1 -- Opening Arguments

**Advocate-Auto (A)**:
Zero additional friction. The generator already performs tier classification, effort estimation, and risk assessment. Adding execution_mode detection is one more pass over the same data. No roadmap schema changes. No new authoring steps. No new review gates.

For the v2.24.5 pipeline, this means: write roadmap (same as today) -> run generator (adds execution_mode) -> run sprint. One step, zero friction delta.

**Advocate-Manual (B)**:
The friction is minimal and well-justified. Adding `execution_mode: python` to a phase heading is a single line of metadata. The roadmap already contains phase objectives, milestones, task tables, and exit criteria. One more metadata line is negligible.

The friction argument is overstated because the annotation is rare. Most phases are NOT Python-executable. Only validation gates and shell-only phases qualify. A typical roadmap might have 0-1 such phases out of 5-7 total.

**Advocate-Hybrid (C)**:
Hybrid adds the `--dry-run` review step, which is already part of the recommended workflow. The friction is: review `--dry-run` output, look for `(auto-detected)` markers, confirm or override. This is 30 seconds of work for a typical roadmap.

The friction is justified by the safety benefit. And it is amortized: once a user confirms annotations for their first roadmap, they understand the system and can skip review for subsequent runs.

### Round 1 -- Scoring Matrix

| Criterion | Auto (A) | Manual (B) | Hybrid (C) |
|-----------|----------|------------|------------|
| Authoring friction | 10/10 | 7/10 | 10/10 |
| Review friction | 5/10 | 10/10 | 7/10 |
| Learning curve | 8/10 | 4/10 | 6/10 |

### Round 2 -- Rebuttals

**B rebuts A**: Zero friction is not free. It comes at the cost of transparency. When the generator silently adds execution_mode, the user does not know it happened. They cannot reason about the tasklist because a hidden decision was made. This is friction displaced, not eliminated -- it surfaces later as debugging friction when something goes wrong.

**A rebuts B**: Debugging friction is speculative. The execution_mode annotation is visible in the generated tasklist. Users who read their tasklists (which they should) will see it. The annotation is not hidden -- it is just not manually authored.

**C**: Both are making reasonable points. The real friction question is: does the user population actually read generated tasklists in detail? If yes, Auto's transparency argument holds. If no, Hybrid's explicit review step is necessary.

### Dimension 4 Convergence: 75%
- Agreement: All agree that friction should be minimized. All agree that some transparency mechanism is needed.
- Disagreement: Whether silent annotation (Auto) or explicit review (Hybrid) better serves transparency.

---

## Dimension 5: Maintainability

### Round 1 -- Opening Arguments

**Advocate-Manual (B)**:
Zero maintenance cost. No heuristic code to maintain, no edge cases to handle, no regression tests to write. The roadmap schema gains one optional field. The generator gains one passthrough mapping. Total: ~5 lines of code.

As the project evolves, new phase patterns will emerge. Manual annotation handles them automatically -- the human adapts. Heuristics require code changes for every new pattern.

**Advocate-Auto (A)**:
The heuristic is built on signals that are already computed (tier classification) or trivially extracted (shell command detection via regex). The incremental maintenance cost is low:
- Tier distribution: already computed
- Shell command detection: simple regex on backtick content
- Keyword matching: extends existing keyword infrastructure

The heuristic code is ~30-50 lines. It has clear unit tests. It changes only when the definition of "Python-executable phase" changes, which is rare.

**Advocate-Hybrid (C)**:
Hybrid has the same maintenance cost as Auto (same heuristics) plus the `--dry-run` presentation logic (minimal). The confirmation UI is ~10 additional lines. Total: ~40-60 lines.

The key maintainability question is: how often do the heuristics break? If execution_mode semantics are stable (and they should be -- it is a binary choice), the heuristics change rarely. If new execution modes are added (e.g., `execution_mode: docker`), all three approaches need updates.

### Round 1 -- Scoring Matrix

| Criterion | Auto (A) | Manual (B) | Hybrid (C) |
|-----------|----------|------------|------------|
| Code maintenance | 6/10 | 10/10 | 5/10 |
| Schema stability | 8/10 | 6/10 | 8/10 |
| Adaptation to new patterns | 5/10 | 9/10 | 6/10 |

### Round 2 -- Rebuttals

**A rebuts B**: Manual's "zero maintenance" ignores the documentation and education maintenance cost. Every new user needs to learn about execution_mode, understand when to use it, and remember to annotate it. This is ongoing human maintenance, which is harder to track and control than code maintenance.

**B rebuts A and C**: Code that does not exist cannot have bugs. The simplest system is the most maintainable. Heuristics are tech debt that accumulates over time as edge cases multiply. Today's "~30-50 lines" becomes tomorrow's "200 lines with 15 special cases."

### Dimension 5 Convergence: 70%
- Agreement: All agree that the heuristic is relatively simple today. All agree that future expansion (new execution modes) would require changes to any approach.
- Disagreement: Whether heuristic maintenance cost is bounded or grows over time.

---

## Cross-Dimension Convergence Summary

| Dimension | Convergence | Leading Variant |
|-----------|-------------|-----------------|
| 1. Accuracy | 65% | Hybrid (C) |
| 2. Safety | 60% | Hybrid (C) / Manual (B) |
| 3. User Control | 70% | Hybrid (C) |
| 4. Workflow Friction | 75% | Auto (A) / Hybrid (C) |
| 5. Maintainability | 70% | Manual (B) |
| **Overall** | **68%** | **Hybrid (C)** |

## Key Unresolved Points

1. Whether tier classification accuracy is sufficient to serve as the foundation for execution_mode detection (A claims yes, B claims compounding risk)
2. Whether the `--dry-run` review step is actually used by real users (C depends on this)
3. Whether the execution_mode feature is important enough to justify any heuristic complexity (all variants assume it is)
