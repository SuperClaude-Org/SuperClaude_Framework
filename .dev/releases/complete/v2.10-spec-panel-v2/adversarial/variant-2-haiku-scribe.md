---
document_id: ROADMAP-SPEC-PANEL-2026-Q1
title: "/sc:spec-panel Correctness & Adversarial Review Enhancements"
version: "1.0"
date: "2026-03-04"
source_spec: "SPEC-PANEL-2026-Q1 v1.0"
owner_persona: "scribe"
complexity: "medium"
milestone_count: 6
interleave_ratio: "1 validation per 2 work milestones"
status: "proposed"
---

# Roadmap: /sc:spec-panel Correctness & Adversarial Review Enhancements

## 1) Scope and outcomes

Deliver the four approved capabilities in phased order with explicit validation gates:

- **SP-2** (Phase 1): James Whittaker adversarial expert persona
- **SP-3** (Phase 2): Mandatory Guard Condition Boundary Table artifact
- **SP-1** (Phase 3): `--focus correctness` review pass
- **SP-4** (Phase 3): Pipeline Dimensional Analysis heuristic

**Deferred:** SP-5 remains out of scope.

---

## 2) Milestone plan (6 total, balanced work/validation)

| ID | Type | Milestone title | Phase | Duration (target) | Depends on | Primary deliverable |
|---|---|---|---|---:|---|---|
| M1 | Work | Add adversarial expert persona (SP-2) | Phase 1 | 1–2 days | None | Whittaker persona integrated into expert sequence/output |
| M2 | Work | Enforce boundary-table artifact contract (SP-3 foundations) | Phase 2 | 2–3 days | M1 | Mandatory Output Artifacts + table template/triggers |
| M3 | Validation | Validate Phase 1–2 correctness baseline | Gate A | 1 day | M1, M2 | Pass/fail evidence on v0.04 + overhead + artifact completeness |
| M4 | Work | Implement `--focus correctness` mode behavior (SP-1) | Phase 3 | 2–3 days | M3 | Correctness focus panel, behaviors FR-14.1..14.6, auto-suggest FR-16 |
| M5 | Work | Add pipeline dimensional analysis + integrations (SP-4) | Phase 3 | 2–3 days | M4 | Pipeline detection/annotation/tracing/consistency checks + integration mappings |
| M6 | Validation | Validate Phase 3 and release readiness | Gate B | 1 day | M4, M5 | End-to-end validation, metrics check, go/no-go decision |

---

## 3) Milestone details and acceptance criteria

### M1 — Add adversarial expert persona (SP-2)

**Summary:** Introduce Whittaker adversarial mindset as a first-class reviewer with required attack format.

**Key work items**
- Define Whittaker persona in `spec-panel.md`.
- Insert reviewer sequence position **after Fowler and Nygard**.
- Add **Adversarial Analysis** section to output examples.
- Update boundaries count to **11 experts**.
- Align with existing YAML structure and severity scale.

**Acceptance criteria (testable)**
- [ ] Persona appears in spec and review sequence in the required slot.
- [ ] Output format includes exact pattern:
      `I can break this by [attack]. Invariant at [location] fails when [condition]. Concrete: [state trace]`
- [ ] All 5 attack methodologies are documented:
  - Zero/Empty Attack
  - Divergence Attack
  - Sentinel Collision Attack
  - Sequence Attack
  - Accumulation Attack
- [ ] Uses existing severities only: `CRITICAL | MAJOR | MINOR`.
- [ ] Incremental token overhead attributable to SP-2 is **≤10%** on v0.04 test spec.

---

### M2 — Enforce boundary-table artifact contract (SP-3 foundations)

**Summary:** Add structural forcing function so guard reasoning cannot be skipped.

**Key work items**
- Add **Mandatory Output Artifacts** section.
- Define **7-column Guard Condition Boundary Table** template.
- Require **6 input-condition rows per guard**.
- Add trigger detection logic for table generation.
- Mark incomplete entries as blocking conditions for synthesis.
- Define downstream propagation format for AD-1 and RM-1.
- Integrate SP-2 as validator of boundary entries (adversarial challenge).

**Acceptance criteria (testable)**
- [ ] Table schema is machine-parseable markdown and fixed at 7 columns.
- [ ] Each guard has at least 6 condition rows.
- [ ] Any `GAP` cell auto-maps to severity **MAJOR or higher**.
- [ ] Blank "Specified behavior" auto-maps to severity **MAJOR or higher**.
- [ ] Synthesis is blocked when table completeness checks fail.
- [ ] AD-1 and RM-1 receive parseable downstream artifact payloads.
- [ ] Additional SP-3 overhead is **≤10%**; cumulative Phase 1+2 remains **≤25%** target.

---

### M3 — Validate Phase 1–2 correctness baseline (Gate A)

**Summary:** Freeze Phase 1/2 quality before Phase 3 expansion.

**Validation suite**
- Run `/sc:spec-panel` against v0.04 reference specification.
- Confirm Whittaker output presence and attack methodology coverage.
- Confirm boundary table completeness/blocking behavior.
- Confirm AD-1/RM-1 propagation format validity.
- Measure cumulative overhead.

**Acceptance criteria (pass/fail)**
- [ ] Whittaker adversarial section appears in every qualifying review.
- [ ] Boundary table generated for all detected guards; no silent omissions.
- [ ] Incomplete table cases correctly block synthesis.
- [ ] Cumulative overhead (Phase 1 + Phase 2) is **<25%**.
- [ ] Gate A report includes defects, fixes, and explicit sign-off for Phase 3 entry.

---

### M4 — Implement `--focus correctness` mode behavior (SP-1)

**Summary:** Add dedicated correctness-focused expert panel and mandatory correctness artifacts.

**Key work items**
- Extend Focus Areas to include `--focus correctness`.
- Implement correctness panel composition:
  - Nygard (lead), Fowler, Adzic, Crispin, Whittaker
- Define/implement FR-14.1 through FR-14.6 behavior deltas.
- Add required output templates:
  - State Variable Registry
  - Guard Condition Boundary Table
  - Pipeline Flow Diagram
- Implement FR-16 auto-suggestion heuristic triggers:
  - 3+ mutable state variables
  - Numeric threshold guards
  - Pipeline/filter operations
- Update usage line to expose correctness focus option.

**Acceptance criteria (testable)**
- [ ] CLI/help usage includes `--focus correctness`.
- [ ] Correctness mode uses exactly the required 5-expert panel.
- [ ] All 3 mandatory outputs are always present in correctness mode.
- [ ] Auto-suggestion fires on each required trigger condition.
- [ ] False positive rate for auto-suggestion is **<30%** on validation set.
- [ ] Correctness-focus overhead is **≤25%** vs standard focus.

---

### M5 — Add pipeline dimensional analysis + integrations (SP-4)

**Summary:** Detect quantity-consistency defects in multi-stage data flows.

**Key work items**
- Add pipeline detection trigger:
  - 2+ stage data flow where output count may differ from input count
- Implement 4-step heuristic:
  1. Pipeline Detection
  2. Quantity Annotation
  3. Downstream Tracing
  4. Consistency Check
- Assign leadership/roles:
  - Fowler leads dimensional analysis
  - Whittaker adversarially attacks each stage
- Emit `CRITICAL` severity on dimensional mismatch.
- Wire integration mappings:
  - SP-4 → `sc:roadmap` RM-3
  - SP-2 → `sc:roadmap` RM-2
  - SP-1 → `sc:adversarial` AD-5
  - SP-2 → `sc:adversarial` AD-2

**Acceptance criteria (testable)**
- [ ] Pipeline heuristic triggers only when 2+ qualifying stages are detected.
- [ ] Quantity annotations are present at each stage boundary.
- [ ] Dimensional mismatch findings are always `CRITICAL`.
- [ ] No-pipeline overhead is **<5%**.
- [ ] Pipeline-present overhead is **≤10%**.
- [ ] Integration payloads conform to mapped AD/RM consumers.

---

### M6 — Validate Phase 3 and release readiness (Gate B)

**Summary:** Final quality gate with measurable success metrics and go/no-go.

**Validation suite**
- End-to-end runs on v0.04 and adversarial regression set.
- Focused runs with and without `--focus correctness`.
- Overhead profile checks by mode.
- Artifact quality scoring for formulaic vs concrete entries.
- Risk review for R-1 through R-6.

**Acceptance criteria (release gate)**
- [ ] Boundary bug catch rate is **>80%** on defined benchmark set.
- [ ] Reviews produce **>0 GAP cells** where applicable (no false "perfect" artifacts).
- [ ] Average adversarial findings per review is **≥2**.
- [ ] Overhead: **<25%** (Phase 1+2 baseline), **<40%** in Phase 3 full mode.
- [ ] Formulaic entries are **<50%** of artifact rows.
- [ ] Gate B report includes go/no-go decision and rollback plan.

---

## 4) Dependency map (blocking relationships)

| Blocked milestone | Blocker(s) | Why blocked |
|---|---|---|
| M2 | M1 | SP-3 uses SP-2 adversarial validator role |
| M3 | M1, M2 | Gate A validates both completed phases |
| M4 | M3 | Correctness mode begins only after Phase 1–2 quality freeze |
| M5 | M4 | Pipeline dimensional analysis is part of Phase 3 depth package |
| M6 | M4, M5 | Gate B requires full Phase 3 implementation |

---

## 5) Validation-first checkpoints

| Gate | Trigger | Required evidence | Exit condition |
|---|---|---|---|
| Gate A (M3) | End of M2 | v0.04 run logs, overhead report, artifact completeness report | Phase 3 authorized |
| Gate B (M6) | End of M5 | end-to-end metrics dashboard, risk review, integration verification | Release go/no-go |

---

## 6) Risk controls mapped to roadmap

| Risk ID | Risk | Mitigation milestone(s) | Control metric |
|---|---|---|---|
| R-1 | Correctness theater | M2, M3, M6 | `% formulaic entries <50%`, mandatory artifact completeness |
| R-2 | Overhead exceeds tolerance | M1, M2, M4, M6 | phase/mode overhead thresholds all pass |
| R-3 | Context window competition | M3, M6 | stable output completeness across long specs |
| R-4 | False positives | M4, M6 | auto-suggest FP rate <30% |
| R-5 | Pipeline under-triggering | M5, M6 | detected/expected pipeline trigger recall in benchmark |
| R-6 | Expert persona bloat | M1, M3 | no uncontrolled expert growth; boundaries remain explicit |

---

## 7) Deliverable inventory by phase

| Phase | Deliverables |
|---|---|
| Phase 1 | Whittaker persona, sequence update, adversarial output section, boundaries=11 |
| Phase 2 | Mandatory artifacts section, guard boundary table contract, trigger/blocking logic, AD-1/RM-1 propagation |
| Phase 3 | `--focus correctness`, FR-14.1..14.6 behavior set, state registry template, pipeline flow diagram spec, FR-16 auto-suggest, SP-4 heuristic |
| Validation | Gate A and Gate B evidence packs, overhead and quality metrics, release decision |

---

## 8) Out of scope (explicit)

- **SP-5 cross-expert challenge protocol** is deferred (B-tier, 57.5/100) and excluded from this roadmap.
