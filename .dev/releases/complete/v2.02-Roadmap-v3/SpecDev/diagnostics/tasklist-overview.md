# Tasklist Overview — sc:roadmap Adversarial Failure Diagnostic

**Release**: v2.1-CleanupAudit-v2
**Workflow**: 4-Phase Diagnostic & Remediation
**Task Count**: 17 tasks across 4 phases
**Compliance**: STRICT (sub-agent verification, Sequential MCP required)
**Created**: 2026-02-22

---

## Problem Statement

When `sc:roadmap` was invoked with `--multi-roadmap --agents opus,haiku`, Wave 2 failed to invoke `sc:adversarial` as prescribed by `refs/adversarial-integration.md`. Instead, two `system-architect` Task agents were spawned directly, produced competing text, and the main agent manually synthesized them — bypassing the structured adversarial debate pipeline entirely.

**Expected behavior**: Wave 2 step 3 invokes `sc:adversarial --source <spec> --generate roadmap --agents opus:<persona>,haiku:<persona> --depth standard --output <dir>`, which spawns a `debate-orchestrator` agent that coordinates the 5-step adversarial pipeline.

**Actual behavior**: Two `system-architect` Task agents spawned in parallel, each generating a roadmap variant. The main agent then manually merged the outputs without debate, scoring, or base selection.

---

## Phase Summary

| Phase | Name | Tasks | Parallelism | Key Skill | Output Dir |
|-------|------|-------|-------------|-----------|------------|
| P1 | Root Cause Investigation | T01.01–T01.06 | 5 parallel + 1 sequential | /sc:troubleshoot, /sc:adversarial | diagnostics/ |
| P2 | Solution Proposals | T02.01–T02.05 | 5 parallel | /sc:reflect, /sc:design | solutions/ |
| P3 | Solution Debate | T03.01–T03.05 | 5 parallel | /sc:adversarial | debates/ |
| P4 | Ranking & Sprint Design | T04.01 | 1 sequential | /sc:spec-panel | ./ |

---

## Dependency Graph

```
T01.01 ──┐
T01.02 ──┤
T01.03 ──┼─→ T01.06 ─→ T02.01 ──┐
T01.04 ──┤              T02.02 ──┤
T01.05 ──┘              T02.03 ──┼─→ T03.01 ──┐
                         T02.04 ──┤   T03.02 ──┤
                         T02.05 ──┘   T03.03 ──┼─→ T04.01
                                      T03.04 ──┤
                                      T03.05 ──┘
```

---

## Critical Source Files (Read-Only)

| File | Relevance |
|------|-----------|
| `src/superclaude/skills/sc-roadmap/SKILL.md` | Wave 2 behavioral instructions (lines 130-143) |
| `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | Invocation patterns, return contract, agent parsing |
| `src/superclaude/skills/sc-adversarial/SKILL.md` | Mode B stub (lines 505-513), full adversarial protocol |
| `src/superclaude/agents/debate-orchestrator.md` | Agent that should have been spawned |
| `.claude/commands/sc/roadmap.md` | Command entry point |

---

## Task Registry

| ID | Phase | Title | Depends On | Agent Type | Skill |
|----|-------|-------|------------|------------|-------|
| T01.01 | P1 | Invocation Wiring Gap | — | root-cause-analyst | /sc:troubleshoot |
| T01.02 | P1 | Spec-Execution Gap | — | root-cause-analyst | /sc:troubleshoot |
| T01.03 | P1 | Agent Dispatch Mechanism | — | root-cause-analyst | /sc:troubleshoot |
| T01.04 | P1 | Return Contract Data Flow | — | root-cause-analyst | /sc:troubleshoot |
| T01.05 | P1 | Claude Behavioral Interpretation | — | root-cause-analyst | /sc:troubleshoot |
| T01.06 | P1 | Adversarial Root Cause Ranking | T01.01–T01.05 | debate-orchestrator | /sc:adversarial |
| T02.01 | P2 | Solution: Invocation Wiring | T01.06 | self-review | /sc:reflect |
| T02.02 | P2 | Solution: Spec-Execution | T01.06 | self-review | /sc:reflect |
| T02.03 | P2 | Solution: Agent Dispatch | T01.06 | system-architect | /sc:design |
| T02.04 | P2 | Solution: Return Contract | T01.06 | system-architect | /sc:design |
| T02.05 | P2 | Solution: Claude Behavior | T01.06 | general-purpose | (raw analysis) |
| T03.01 | P3 | Debate: Invocation Wiring Fix | T02.01–T02.05 | debate-orchestrator | /sc:adversarial |
| T03.02 | P3 | Debate: Spec-Execution Fix | T02.01–T02.05 | debate-orchestrator | /sc:adversarial |
| T03.03 | P3 | Debate: Agent Dispatch Fix | T02.01–T02.05 | debate-orchestrator | /sc:adversarial |
| T03.04 | P3 | Debate: Return Contract Fix | T02.01–T02.05 | debate-orchestrator | /sc:adversarial |
| T03.05 | P3 | Debate: Claude Behavior Fix | T02.01–T02.05 | debate-orchestrator | /sc:adversarial |
| T04.01 | P4 | Ranking & Sprint Design | T03.01–T03.05 | system-architect | /sc:spec-panel |

---

## Scoring Dimensions

### Root Cause Ranking (Phase 1, T01.06)
- **Likelihood**: How probable is this root cause? (0.0–1.0)
- **Impact**: How much does this explain the observed failure? (0.0–1.0)
- **Combined**: `(likelihood * 0.6) + (impact * 0.4)`

### Solution Debate Scoring (Phase 3)
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Root cause coverage | 0.25 | Does the fix address the root cause completely? |
| Completeness | 0.20 | Does the fix handle edge cases and error paths? |
| Feasibility | 0.25 | Can the fix be implemented without major refactoring? |
| Blast radius | 0.15 | How many other skills/commands are affected? |
| Confidence | 0.15 | How confident are we this fix works? |

### Final Ranking (Phase 4, T04.01)
- **Problem rank**: `(likelihood * 0.6) + (impact * 0.4)` (from P1)
- **Solution rank**: `(fix_likelihood * 0.5) + (feasibility * 0.3) + (low_blast_radius * 0.2)` (from P3)

---

## Checkpoint Registry

| Checkpoint | After | Verification |
|------------|-------|-------------|
| CP-P1-END | T01.06 | 5 root cause files + ranked-root-causes.md + adversarial/ dir in diagnostics/ |
| CP-P2-END | T02.05 | 5 solution files in solutions/, each referencing assigned root cause |
| CP-P3-END | T03.05 | 5 debate results in debates/, each with fix likelihood scores |
| CP-P4-END | T04.01 | sprint-spec.md with ranked lists, top 3 pairs, actionable sprint |
