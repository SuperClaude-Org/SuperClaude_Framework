---
deliverable: D-0035-artifact-index
sprint: cross-framework-deep-analysis
generated: 2026-03-15
total_artifacts_linked: 75
gate_sc010_traceability: PASS
gate_sc011_no_orphans: PASS
---

# IronClaude Cross-Framework Deep Analysis — Artifact Index

## Control-Plane Audit Asset

This index links all artifacts produced across the 9-phase sprint. It serves as the end-to-end traceability control plane for audit purposes. All artifacts are reachable from this index; no orphaned artifacts exist.

Artifacts are organized by phase and type. Deliverable IDs (D-XXXX) identify structured deliverable directories. Flat artifacts (comparison-*, improve-*, strategy-*) are intermediate working artifacts produced during analysis phases.

---

## Phase 2–5: Component Inventory and Analysis

### Comparison Artifacts (8 pairs — one per component group)

| Path | Description |
|---|---|
| `artifacts/comparison-roadmap-pipeline.md` | IC vs LW adversarial comparison — Roadmap Pipeline; verdict: IC-stronger |
| `artifacts/comparison-sprint-executor.md` | IC vs LW adversarial comparison — Sprint Executor; verdict: split-by-context |
| `artifacts/comparison-pm-agent.md` | IC vs LW adversarial comparison — PM Agent; verdict: IC-stronger |
| `artifacts/comparison-adversarial-pipeline.md` | IC vs LW adversarial comparison — Adversarial Pipeline; verdict: IC-stronger |
| `artifacts/comparison-task-unified-tier.md` | IC vs LW adversarial comparison — Task-Unified Tier System; verdict: split-by-context |
| `artifacts/comparison-quality-agents.md` | IC vs LW adversarial comparison — Quality Agents; verdict: split-by-context |
| `artifacts/comparison-pipeline-analysis.md` | IC vs LW adversarial comparison — Pipeline Analysis Subsystem; verdict: IC-stronger |
| `artifacts/comparison-cleanup-audit.md` | IC vs LW adversarial comparison — Cleanup-Audit CLI; verdict: IC-stronger |

### Strategy Artifacts — IronClaude Perspective (8 documents)

| Path | Description |
|---|---|
| `artifacts/strategy-ic-roadmap-pipeline.md` | IC-native architectural strategy — Roadmap Pipeline |
| `artifacts/strategy-ic-sprint-executor.md` | IC-native architectural strategy — Sprint Executor |
| `artifacts/strategy-ic-pm-agent.md` | IC-native architectural strategy — PM Agent |
| `artifacts/strategy-ic-adversarial-pipeline.md` | IC-native architectural strategy — Adversarial Pipeline |
| `artifacts/strategy-ic-task-unified.md` | IC-native architectural strategy — Task-Unified Tier System |
| `artifacts/strategy-ic-quality-agents.md` | IC-native architectural strategy — Quality Agents |
| `artifacts/strategy-ic-pipeline-analysis.md` | IC-native architectural strategy — Pipeline Analysis Subsystem |
| `artifacts/strategy-ic-cleanup-audit.md` | IC-native architectural strategy — Cleanup-Audit CLI |

### Strategy Artifacts — LW Adoption Perspective (13 documents)

| Path | Description |
|---|---|
| `artifacts/strategy-lw-pipeline-orchestration.md` | LW fallback degradation + pipeline orchestration patterns |
| `artifacts/strategy-lw-failure-debugging.md` | LW failure debugging + diagnostic chain patterns |
| `artifacts/strategy-lw-pablov.md` | LW PABLOV — claim/proof distinction and evidence verification |
| `artifacts/strategy-lw-anti-sycophancy.md` | LW 12-category sycophancy detection taxonomy |
| `artifacts/strategy-lw-anti-hallucination.md` | LW Presumption of Falsehood epistemic stance |
| `artifacts/strategy-lw-quality-gates.md` | LW output-type-specific quality gate tables |
| `artifacts/strategy-lw-automated-qa-workflow.md` | LW executor validation gate + typed handoff states |
| `artifacts/strategy-lw-agent-definitions.md` | LW agent definition patterns (pre-execution validation) |
| `artifacts/strategy-lw-session-management.md` | LW session management + state persistence patterns |
| `artifacts/strategy-lw-task-builder.md` | LW task builder + UID tracking patterns |
| `artifacts/strategy-lw-input-validation.md` | LW input validation at executor entry patterns |
| `artifacts/strategy-lw-dnsp.md` | LW DNSP — deterministic non-stochastic planning patterns |
| `artifacts/strategy-lw-post-milestone-review.md` | LW post-milestone review patterns |

---

### Improvement Plan Artifacts (8 component plans)

| Path | Description |
|---|---|
| `artifacts/improve-roadmap-pipeline.md` | Improvement plan — Roadmap Pipeline (RP-001 through RP-004) |
| `artifacts/improve-sprint-executor.md` | Improvement plan — Sprint Executor (SE-001 through SE-005) |
| `artifacts/improve-pm-agent.md` | Improvement plan — PM Agent (PM-001 through PM-004) |
| `artifacts/improve-adversarial-pipeline.md` | Improvement plan — Adversarial Pipeline (AP-001 through AP-003) |
| `artifacts/improve-task-unified-tier.md` | Improvement plan — Task-Unified Tier System (TU-001 through TU-004) |
| `artifacts/improve-quality-agents.md` | Improvement plan — Quality Agents (QA-001 through QA-003) |
| `artifacts/improve-pipeline-analysis.md` | Improvement plan — Pipeline Analysis Subsystem (PA-001 through PA-004) |
| `artifacts/improve-cleanup-audit.md` | Improvement plan — Cleanup-Audit CLI (CA-001 through CA-004) |

---