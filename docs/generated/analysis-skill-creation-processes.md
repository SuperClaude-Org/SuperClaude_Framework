# Analysis: Skill Creation Processes — SuperClaude Pipeline vs Anthropic Skill Creator

**Generated**: 2026-03-04
**Request**: Compare the current SuperClaude skill creation pipeline with Anthropic's skill-creator skill

---

## 1. SuperClaude Pipeline: Current Process

The SuperClaude skill creation process is a **4-stage sequential pipeline** where each stage produces a discrete artifact that feeds the next. The process is developer-driven and architecture-heavy, optimized for creating complex, multi-file skills with subagents, rules engines, and framework integration.

### Stage 1: `sc:brainstorm` — Requirements Discovery

**Purpose**: Collaborative Socratic dialogue to flesh out initial ideas into concrete requirements.

**Observed in reference artifacts**:
- The v2.01 Architecture Refactor began with problem identification and root cause analysis
  - Sprint spec §2 "The Core Problem" documents the discovery phase
    ([sprint-spec.md:36–43](../.dev/releases/complete/v2.01-Architecture-Refactor/sprint-spec.md#L36-L43))
  - Root causes ranked by severity in §3
    ([sprint-spec.md:L48+](../.dev/releases/complete/v2.01-Architecture-Refactor/sprint-spec.md))

**Process characteristics**:
- Non-presumptive questioning to elicit hidden requirements
- Edge case identification through guided exploration
- Output: informal requirement brief with problem statement, scope, and constraints

### Stage 2: `sc:spec-panel` — Multi-Expert Specification Review

**Purpose**: Transform brainstorm output into a formal specification/PRD, validated by a panel of domain experts (Wiegers, Fowler, Adzic, Nygard, Crispin).

**Observed in reference artifacts**:
- The v2.01 spec-panel produced a 5-expert review with per-expert scoring
  ([spec-panel-report.md:1–19](../.dev/releases/complete/v2.01-Architecture-Refactor/spec-panel-report.md#L1-L19))
- Panel scored the spec 3.9/10, identifying 8 cross-expert consensus findings (CC-1 through CC-8)
  ([spec-panel-report.md:20–100](../.dev/releases/complete/v2.01-Architecture-Refactor/spec-panel-report.md#L20-L100))
- Each finding includes severity, affected experts, and **required action** — not just observations

**For the cleanup-audit skill**:
- The spec-v2 was derived from merged research (Agent 1: 40 structural rules, Agent 2: 22 ranked capabilities)
  ([sc-cleanup-audit-spec-v2.md:7–8](../.dev/releases/complete/v.1.06-CleanupAudit/sc-cleanup-audit-spec-v2.md#L7-L8))
- Spec defines full architecture: SKILL.md frontmatter, 5-step behavioral flow, 3-pass audit model, 5 custom subagents, 16 reusable principles
  ([sc-cleanup-audit-spec-v2.md:11–48](../.dev/releases/complete/v.1.06-CleanupAudit/sc-cleanup-audit-spec-v2.md#L11-L48))

**Process characteristics**:
- 5 independent parallel expert reviews with deduplication
- Scoring with explicit pass/fail thresholds
- Cross-expert consensus findings have highest confidence
- Output: scored review report + actionable remediation items

### Stage 3: `sc:roadmap` — Milestone-Based Implementation Plan

**Purpose**: Transform the reviewed spec into a sequenced roadmap with milestones, deliverables, tasks, acceptance criteria, and dependency DAGs.

**Observed in reference artifacts**:
- The v2.01 roadmap produced 10 milestones with YAML frontmatter metadata
  ([roadmap.md:1–80](../.dev/releases/complete/v2.01-Architecture-Refactor/roadmap.md#L1-L80))
- Complexity scoring (0.727 = HIGH), domain distribution, persona assignment
  ([roadmap.md:6–14](../.dev/releases/complete/v2.01-Architecture-Refactor/roadmap.md#L6-L14))

**For the cleanup-audit skill**:
- Roadmap produced 6 milestones, 22 deliverables, 82 tasks, 36 detailed task specifications
  ([sc-cleanup-audit-roadmap.md:9](../.dev/releases/complete/v.1.06-CleanupAudit/sc-cleanup-audit-roadmap.md#L9))
- Dependency graph with parallelization opportunities identified: M2 ∥ M3 saves ~40%
  ([sc-cleanup-audit-roadmap.md:936–984](../.dev/releases/complete/v.1.06-CleanupAudit/sc-cleanup-audit-roadmap.md#L936-L984))
- Each task has: Type, Priority (P0-P3), Files affected, Steps, Acceptance criteria, Verification commands
  ([sc-cleanup-audit-roadmap.md:63–110](../.dev/releases/complete/v.1.06-CleanupAudit/sc-cleanup-audit-roadmap.md#L63-L110))
- Risk register with 8 identified risks, probability/impact/mitigation
  ([sc-cleanup-audit-roadmap.md:987–999](../.dev/releases/complete/v.1.06-CleanupAudit/sc-cleanup-audit-roadmap.md#L987-L999))

**Process characteristics**:
- Milestone-based with explicit dependency ordering
- Per-task acceptance criteria with verification commands
- Parallelization analysis baked into the plan
- Output: roadmap document with full task breakdown

### Stage 4: `sc:workflow` — Executable Task List

**Purpose**: Transform the roadmap into an ordered, executable task list with phase gates and scope maps.

**Observed in reference artifacts**:
- The v2.01 workflow produced a 7-phase execution plan with DAG dependencies
  ([workflow_sc-roadmap-refactor.md:1–77](../.dev/releases/complete/v2.01-Architecture-Refactor/workflow_sc-roadmap-refactor.md#L1-L77))
- Scope map ties each file to its originating bug/task reference
  ([workflow_sc-roadmap-refactor.md:22–35](../.dev/releases/complete/v2.01-Architecture-Refactor/workflow_sc-roadmap-refactor.md#L22-L35))
- Cross-references workflow phases to sprint-spec phases for traceability
  ([workflow_sc-roadmap-refactor.md:36–50](../.dev/releases/complete/v2.01-Architecture-Refactor/workflow_sc-roadmap-refactor.md#L36-L50))

**Process characteristics**:
- Phase-gated execution with explicit "not in scope" boundaries
- File-level scope maps for every change
- Traceability back to spec requirements
- Output: ordered task list ready for execution via TodoWrite

### Pipeline Summary

```
sc:brainstorm → sc:spec-panel → sc:roadmap → sc:workflow → Execute
   (ideas)       (validated      (milestones    (task list)    (code)
                   spec/PRD)       + DAG)
```

**Strengths**:
- Deep architectural rigor — specs are expert-reviewed before coding starts
- Full traceability from requirement → spec → milestone → task → file
- Parallelization opportunities identified at planning time
- Risk management baked into the roadmap
- Produces reusable framework artifacts (rules, templates, subagents)

**Weaknesses**:
- Heavy upfront investment — 4 stages before any code is written
- No automated eval/benchmark loop — quality is assessed by expert panel, not by running the skill
- No iterative test→improve cycle built into the pipeline
- Output-focused (produces artifacts) rather than outcome-focused (does the skill work?)

---

## 2. Anthropic Skill Creator: Process

The Anthropic skill-creator is a **single-skill iterative loop** focused on draft→test→evaluate→improve cycles with quantitative benchmarking and human review.

### Phase 1: Capture Intent
([SKILL.md:47–54](../.claude/skills/skill-creator/SKILL.md#L47-L54))

- Understand what the skill should do, when it should trigger, expected output format
- If conversation already contains a workflow, extract answers from history
- 4 key questions: purpose, triggers, output format, test case suitability

### Phase 2: Interview and Research
([SKILL.md:57–60](../.claude/skills/skill-creator/SKILL.md#L57-L60))

- Proactively ask about edge cases, I/O formats, success criteria, dependencies
- Check available MCPs for research (docs, similar skills, best practices)
- Research in parallel via subagents if available

### Phase 3: Write the SKILL.md
([SKILL.md:64–109](../.claude/skills/skill-creator/SKILL.md#L64-L109))

**Skill writing guide includes**:
- Anatomy: `SKILL.md` + optional `scripts/`, `references/`, `assets/`
  ([SKILL.md:75–84](../.claude/skills/skill-creator/SKILL.md#L75-L84))
- Progressive disclosure: metadata (~100 words always loaded) → body (<500 lines on trigger) → bundled resources (on demand)
  ([SKILL.md:88–92](../.claude/skills/skill-creator/SKILL.md#L88-L92))
- Writing style: explain *why* over heavy-handed MUSTs, use theory of mind
  ([SKILL.md:137–139](../.claude/skills/skill-creator/SKILL.md#L137-L139))
- Description should be "pushy" to combat undertriggering
  ([SKILL.md:67](../.claude/skills/skill-creator/SKILL.md#L67))

### Phase 4: Test Cases
([SKILL.md:143–161](../.claude/skills/skill-creator/SKILL.md#L143-L161))

- Create 2-3 realistic test prompts
- Share with user for validation before running
- Save to `evals/evals.json` — prompts only, no assertions yet

### Phase 5: Run and Evaluate (The Core Loop)
([SKILL.md:163–289](../.claude/skills/skill-creator/SKILL.md#L163-L289))

This is a **5-step continuous sequence**:

1. **Spawn all runs** — with-skill AND baseline in the same turn (parallel subagents)
   ([SKILL.md:169–197](../.claude/skills/skill-creator/SKILL.md#L169-L197))
2. **Draft assertions while runs execute** — use wait time productively
   ([SKILL.md:199–205](../.claude/skills/skill-creator/SKILL.md#L199-L205))
3. **Capture timing data** from task notifications (`total_tokens`, `duration_ms`)
   ([SKILL.md:209–219](../.claude/skills/skill-creator/SKILL.md#L209-L219))
4. **Grade, aggregate, launch viewer** — grader agent → benchmark aggregation → HTML viewer with qualitative outputs + quantitative benchmark
   ([SKILL.md:223–265](../.claude/skills/skill-creator/SKILL.md#L223-L265))
5. **Read feedback** from `feedback.json` — empty = fine, focus on specific complaints
   ([SKILL.md:267–289](../.claude/skills/skill-creator/SKILL.md#L267-L289))

### Phase 6: Improve the Skill (Iteration Loop)
([SKILL.md:294–322](../.claude/skills/skill-creator/SKILL.md#L294-L322))

**4 improvement principles**:
1. **Generalize from feedback** — don't overfit to test cases
   ([SKILL.md:298](../.claude/skills/skill-creator/SKILL.md#L298))
2. **Keep the prompt lean** — remove things not pulling their weight, read transcripts not just outputs
   ([SKILL.md:300](../.claude/skills/skill-creator/SKILL.md#L300))
3. **Explain the why** — avoid heavy-handed MUSTs, use theory of mind
   ([SKILL.md:302](../.claude/skills/skill-creator/SKILL.md#L302))
4. **Look for repeated work** — if all test runs write the same helper script, bundle it
   ([SKILL.md:304](../.claude/skills/skill-creator/SKILL.md#L304))

**Loop continues until**: user is happy, feedback is all empty, or no meaningful progress
([SKILL.md:318–322](../.claude/skills/skill-creator/SKILL.md#L318-L322))

### Phase 7: Description Optimization
([SKILL.md:333–404](../.claude/skills/skill-creator/SKILL.md#L333-L404))

- Generate 20 trigger eval queries (10 should-trigger, 10 should-not-trigger)
- Realistic prompts with edge cases, not simple keyword matches
  ([SKILL.md:348–358](../.claude/skills/skill-creator/SKILL.md#L348-L358))
- Run automated optimization loop: 60/40 train/test split, 3x per query, up to 5 iterations
  ([SKILL.md:375–394](../.claude/skills/skill-creator/SKILL.md#L375-L394))

### Pipeline Summary

```
Capture Intent → Interview → Draft SKILL.md → Test Cases → Run + Eval → Improve → Repeat
                                                               ↑_______________|
                                                          (iterate until satisfied)
                                                                    ↓
                                                          Description Optimization
```

**Strengths**:
- Tight feedback loop — draft→test→improve cycles catch issues early
- Quantitative benchmarking with statistical rigor (mean ± stddev, variance analysis)
- Baseline comparison (with-skill vs without-skill or old vs new)
- Human-in-the-loop review with structured feedback capture
- Description optimization with automated trigger accuracy testing
- Lean philosophy — "explain the why" over heavy MUSTs

**Weaknesses**:
- No multi-expert review of the spec before implementation
- No architecture-level planning for complex multi-file skills
- No dependency DAG, milestone planning, or risk register
- No framework integration guidance (COMMANDS.md, ORCHESTRATOR.md, PERSONAS.md)
- No subagent definition pattern — treats skills as single SKILL.md units
- No traceability from requirements to implementation

---

## 3. Comparison Matrix

| Dimension | SuperClaude Pipeline | Anthropic Skill Creator |
|-----------|---------------------|------------------------|
| **Stages** | 4 sequential + execute | 3 linear + iterative loop |
| **Planning depth** | Deep (expert panel, milestones, DAG) | Light (interview, draft) |
| **Testing approach** | Post-implementation validation | Test-driven iteration |
| **Feedback mechanism** | Expert panel scores | Human review + quantitative benchmark |
| **Iteration** | Not built in (re-run pipeline) | Core design (draft→test→improve loop) |
| **Baseline comparison** | None | With-skill vs without-skill |
| **Quantitative metrics** | None | Pass rate, tokens, timing, variance |
| **Description optimization** | Manual | Automated 5-iteration optimization |
| **Multi-file skills** | Native (rules, templates, subagents) | Mentioned but not emphasized |
| **Framework integration** | Built in (COMMANDS.md, ORCHESTRATOR.md) | Not addressed |
| **Risk management** | Risk register + mitigation | Not addressed |
| **Traceability** | Full (requirement→spec→milestone→task) | Not addressed |
| **Time to first test** | Long (4 stages before code) | Short (draft + 2-3 test cases) |
| **Output** | Architecture artifacts + code | Working skill + benchmarks |

---

## 4. Recommendations

The two processes are **complementary, not competing**. The SuperClaude pipeline excels at architectural planning for complex skills; the Anthropic skill-creator excels at iterative quality refinement.

**Potential hybrid workflow**:
1. `sc:brainstorm` → requirements discovery (keep)
2. `sc:spec-panel` → expert validation (keep for complex skills, skip for simple)
3. **skill-creator** → draft SKILL.md + test + iterate (replace sc:roadmap→sc:workflow for the skill itself)
4. `sc:roadmap` + `sc:workflow` → only for framework integration planning (COMMANDS.md, agents, build system)
5. **skill-creator description optimization** → add as final step (new)
