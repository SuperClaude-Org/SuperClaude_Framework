# v3.1 — A/B Testing Methodology for Command/Skill Regression & Value Testing

**Status**: Backlog
**Created**: 2026-02-21
**Updated**: 2026-02-21 (spec-panel review incorporated)
**Origin**: Troubleshooting investigation — duplicate slash commands from global + local installs

---

## Problem Statement

SuperClaude is installed both globally (`~/.claude/`) and locally (project `.claude/`), causing duplicate command listings. Rather than treating this as a pure bug, we leverage it as a **built-in A/B testing mechanism**: global = baseline (old), local = candidate (new).

Additionally, commands and skills should be tested against **vanilla prompts** — plain natural language that accomplishes the same goal without any SuperClaude instrumentation. This measures whether a command is **earning its keep** beyond what raw Claude Code can do alone.

## Key Insights

1. **Global/Local Split**: Claude Code merges global `~/.claude/` (first in list) and project `.claude/` (second in list). By toggling these, we isolate old vs new versions.
2. **Vanilla Baseline**: By disabling ALL `.claude/` infrastructure (global + local + framework files), we measure raw Claude Code capability — the true baseline against which every command must justify its existence.

---

## Three-Tier Testing Model

| Tier | Variants Compared | Runs Per Variant | Total Sessions | When to Use |
|------|-------------------|------------------|----------------|-------------|
| **Regression** | Baseline vs Candidate | 5 each | 10 + scoring | Every command modification |
| **Value Validation** | Vanilla vs Baseline vs Candidate | 5 each | 15 + scoring | New commands, major rewrites, >50% behavioral change |
| **Deprecation Audit** | Vanilla vs Current | 5 each | 10 + scoring | Quarterly health check across all commands |

### What Each Variant Measures

| Variant | Isolation State | What It Measures |
|---------|----------------|------------------|
| **Vanilla** | ALL `.claude/` disabled (global + local + framework) | Raw Claude Code capability — the floor |
| **Baseline** | Global `~/.claude/` only (local disabled) | Current published release quality |
| **Candidate** | Global + Local `.claude/` active (local has modifications) | Modified version quality |

### Comparison Matrix

| Comparison | Question Answered | Decision |
|------------|-------------------|----------|
| Candidate vs Baseline | Did the change improve or regress? | Merge or reject the modification |
| Baseline vs Vanilla | Does the current command add value? | Keep or rework the command |
| Candidate vs Vanilla | Does the new version add value? | Validate the modification's net effect |

### Acceptance Criteria

- **Regression tier**: Candidate must not score significantly lower than Baseline on any dimension (p < 0.05)
- **Value validation tier**: Command must outperform vanilla by statistically significant margin on ≥3 of 5 scoring dimensions
- **Deprecation audit**: Commands failing to beat vanilla on ≥2 dimensions are flagged for rework

---

## Deliverables

### 1. Shell Script: `scripts/ab_test_commands.sh`

**Purpose**: Orchestrates isolation, parallel agent execution, scoring, and comparison.

**Three Isolation Modes**:

```bash
# Mode: vanilla — disable ALL .claude/ infrastructure
#   Renames: ~/.claude/ → ~/.claude-ab-backup/
#   Renames: .claude/ → .claude-ab-backup-local/
#   Result: Raw Claude Code, no SuperClaude

# Mode: baseline — global only
#   Renames: .claude/ → .claude-ab-candidate/
#   Result: Current published release

# Mode: candidate — all active
#   Restores: .claude/ (with modifications)
#   Result: Modified local version
```

**Execution Phases**:
- **Phase 1 (Vanilla)**: Disable all `.claude/`, run 5 parallel sessions with vanilla-equivalent prompt. Capture to `docs/generated/ab-tests/<timestamp>/vanilla/run-{1..5}.md`
- **Phase 2 (Baseline)**: Restore global only, run 5 parallel sessions with command invocation. Capture to `baseline/run-{1..5}.md`
- **Phase 3 (Candidate)**: Restore local, run 5 parallel sessions with command invocation. Capture to `candidate/run-{1..5}.md`
- **Phase 4 (Score)**: Evaluator agent scores all outputs against rubric. Results to `metrics.jsonl`
- **Phase 5 (Compare)**: Feed metrics into `scripts/ab_test_workflows.py` for statistical comparison
- **Safety**: Uses `trap` to guarantee restoration of ALL `.claude/` directories on exit/error/SIGINT

**CLI Interface**:
```bash
# Full 3-variant value validation
./scripts/ab_test_commands.sh \
  --command "sc:roadmap" \
  --args "spec-document.md" \
  --tier value-validation \
  --runs 5 \
  --output docs/generated/ab-tests/

# Quick 2-variant regression test
./scripts/ab_test_commands.sh \
  --command "sc:analyze" \
  --args "src/ --focus security" \
  --tier regression \
  --runs 5

# Deprecation audit (vanilla vs current)
./scripts/ab_test_commands.sh \
  --command "sc:explain" \
  --args "src/superclaude/pm_agent/confidence.py" \
  --tier deprecation \
  --runs 5

# Dry run (verify isolation without spawning agents)
./scripts/ab_test_commands.sh \
  --command "sc:roadmap" \
  --args "spec.md" \
  --dry-run
```

### 2. Equivalent Prompt Library: `tests/ab/vanilla-prompts.yml`

**Purpose**: Each command has a documented vanilla-equivalent prompt — a fair plain-language representation of the same goal.

```yaml
# Vanilla-equivalent prompts for A/B testing
# These should describe the GOAL, not the METHOD
# Review periodically to ensure fairness

sc:roadmap:
  vanilla_prompt: |
    Read {input_file} and generate a comprehensive project roadmap.
    Include: milestones, dependencies between milestones, timeline
    estimates, risk factors, and a phased delivery plan.
  scoring_focus: [structure, completeness, actionability]

sc:analyze:
  vanilla_prompt: |
    Analyze {target} for code quality issues.
    Cover: complexity, maintainability, security vulnerabilities,
    performance bottlenecks, and test coverage gaps.
    Provide severity ratings and specific remediation steps.
  scoring_focus: [accuracy, depth, actionability]

sc:cleanup-audit:
  vanilla_prompt: |
    Audit this repository for dead code, unused dependencies,
    redundant files, and cleanup opportunities.
    Provide evidence-backed recommendations organized by priority.
  scoring_focus: [accuracy, completeness, evidence_quality]

sc:explain:
  vanilla_prompt: |
    Explain how {target} works. Cover its purpose, key components,
    data flow, and important design decisions. Make it accessible
    to a developer unfamiliar with the codebase.
  scoring_focus: [clarity, accuracy, completeness]

sc:implement:
  vanilla_prompt: |
    Implement {description}. Follow existing project conventions,
    write tests, and ensure the implementation integrates properly
    with the existing codebase.
  scoring_focus: [correctness, completeness, code_quality]

# ... additional commands added as needed
```

**Prompt Equivalence Review**: Each vanilla prompt MUST be reviewed to ensure it's a fair representation of what a knowledgeable user would type — not deliberately sandbagged (too vague) or artificially enhanced (containing the command's internal instructions).

### 3. Scoring Rubric: `tests/ab/scoring-rubric.yml`

**Five Scoring Dimensions** (each 1-10 with anchored definitions):

```yaml
dimensions:
  structure:
    description: "Consistency and utility of output format"
    anchors:
      1: "Wall of text, no headings or organization"
      5: "Some headings but inconsistent hierarchy, basic formatting"
      10: "Consistent heading hierarchy, tables, code blocks, actionable sections"

  completeness:
    description: "Coverage of all aspects of the task"
    anchors:
      1: "Addresses only one aspect, major gaps"
      5: "Covers main points but misses edge cases or secondary concerns"
      10: "Comprehensive coverage including edge cases, alternatives, and caveats"

  accuracy:
    description: "Correctness of information and recommendations"
    anchors:
      1: "Multiple factual errors or hallucinations"
      5: "Mostly correct with minor inaccuracies"
      10: "Fully accurate, verifiable claims, no hallucinations"

  actionability:
    description: "Can the user immediately act on the output?"
    anchors:
      1: "Vague suggestions, no concrete next steps"
      5: "Some actionable items but requires interpretation"
      10: "Specific, ordered action items with clear ownership and criteria"

  efficiency:
    description: "Quality per token spent"
    anchors:
      1: "Excessive verbosity, low signal-to-noise ratio"
      5: "Reasonable length with some padding"
      10: "Concise, every paragraph earns its place"

scoring_method:
  primary: "rubric_anchored"    # Default: score against anchored rubric
  alternative: "pairwise"        # Optional: "Which output better accomplishes the goal?"
  automated_supplements:          # Supplement (don't replace) human-like scoring
    - heading_count_and_depth
    - structural_element_detection  # tables, code blocks, lists
    - token_efficiency_ratio        # quality_score / tokens_used
```

### 4. KNOWLEDGE.md Addition

New section under **Advanced Techniques** (after Technique 3, ~line 489):

**"Technique 4: A/B Regression & Value Testing for Commands and Skills"**

Documents:
- The three-tier testing model (regression / value-validation / deprecation)
- The global/local/vanilla isolation mechanism
- The 5-run averaged scoring methodology
- The equivalent prompt library concept
- How to interpret results and when to use which tier
- Link to the script and developer guide

### 5. PLANNING.md Addition

New subsection under **Absolute Rules**:

**"Command/Skill Quality Testing"**

- All modifications to existing commands/skills MUST pass regression testing (Tier 1) before merging
- New commands MUST pass value validation testing (Tier 2) before release
- All commands undergo deprecation audit (Tier 3) quarterly
- Minimum 5 runs per variant, statistical significance required (p < 0.05)

### 6. Developer Guide: `docs/developer-guide/ab-testing-commands.md`

Comprehensive guide covering:
- **Why**: Prevent regression AND validate command value-add
- **Three-tier model**: When to use regression vs value-validation vs deprecation
- **How isolation works**: Global/local/vanilla mechanism explained with diagrams
- **Prerequisites**: Global SuperClaude installed, local dev copy via `make sync-dev`
- **Step-by-step workflows**: For each tier
- **Writing vanilla prompts**: Guidelines for fair prompt equivalence
- **Scoring rubric**: Dimensions, anchors, and interpretation
- **Interpreting results**: What p-values and effect sizes mean
- **Cost considerations**: When to use lightweight vs heavyweight testing
- **Integration with existing tools**: `ab_test_workflows.py` and `analyze_workflow_metrics.py`
- **Future**: Potential `/sc:test --type ab` integration

---

## Files to Create/Modify

| File | Action | Estimated Size |
|------|--------|----------------|
| `scripts/ab_test_commands.sh` | **Create** | ~200 lines |
| `tests/ab/vanilla-prompts.yml` | **Create** | ~100 lines (grows with commands) |
| `tests/ab/scoring-rubric.yml` | **Create** | ~60 lines |
| `docs/developer-guide/ab-testing-commands.md` | **Create** | ~150 lines |
| `KNOWLEDGE.md` | **Edit** | Insert ~40 lines after line 489 |
| `PLANNING.md` | **Edit** | Insert ~15 lines in Absolute Rules section |

## Verification Plan

1. `shellcheck scripts/ab_test_commands.sh` — validate script syntax
2. `--dry-run` flag test — verify ALL `.claude/` directories are moved and restored correctly (including global)
3. Validate `vanilla-prompts.yml` parses correctly
4. `make verify-sync` — confirm no drift
5. Markdown rendering check for KNOWLEDGE.md and PLANNING.md
6. Run one full value-validation test on a simple command (e.g., `sc:explain`) to calibrate scoring

## Dependencies

- Existing `scripts/ab_test_workflows.py` (statistical comparison engine)
- Existing `scripts/analyze_workflow_metrics.py` (metrics aggregation)
- `docs/memory/workflow_metrics.jsonl` schema (JSONL format)
- Global SuperClaude installation (`~/.claude/`)
- `claude` CLI available for headless session execution

## Cost Model

| Tier | Sessions | Evaluator Calls | Estimated Tokens | When Justified |
|------|----------|-----------------|------------------|----------------|
| Regression | 10 | 10 | ~30-80K | Every command modification |
| Value Validation | 15 | 15 | ~50-150K | New commands, major rewrites, >50% change |
| Deprecation Audit | 10 | 10 | ~30-80K | Quarterly per-command health check |

## Open Questions / Future Work

- **`/sc:test --type ab` integration**: Should this become a first-class subcommand of `/sc:test`?
- **CI integration**: Auto-trigger regression tests on PRs modifying `.claude/commands/` or `.claude/skills/`
- **Docker isolation for vanilla**: Safer than renaming `~/.claude/` — use a clean container with no SuperClaude installed
- **Pairwise preference scoring**: Potentially more reliable than rubric scoring for subtle differences
- **Prompt equivalence review process**: Who reviews vanilla prompts for fairness? (suggest: PR review requirement)
- **Sample size calibration**: 5 runs is starting point; may need 10-20 for statistical power on subtle changes
- **Cross-command scoring normalization**: Different commands have different quality ceilings; how to compare across command families

## Spec Panel Review Notes (2026-02-21)

**Experts consulted**: Wiegers (requirements), Adzic (examples), Fowler (architecture), Crispin (testing), Nygard (operations)

**Key findings incorporated**:
1. Added vanilla baseline testing — measures command VALUE, not just regression
2. Added 3-tier testing model with cost-appropriate usage guidelines
3. Added equivalent prompt library as a formal deliverable
4. Added anchored scoring rubric with explicit level definitions
5. Defined 3 isolation modes (vanilla/baseline/candidate) with safety concerns noted
6. Added cost model and usage thresholds
7. Flagged Docker isolation as safer alternative for vanilla testing
