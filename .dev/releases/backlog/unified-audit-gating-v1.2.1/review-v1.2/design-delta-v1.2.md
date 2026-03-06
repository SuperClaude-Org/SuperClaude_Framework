# Unified Audit Gating System v1.2 — Design Delta from v1.1

## Scope
Delta from:
- `/config/workspace/SuperClaude_Framework/.dev/releases/backlog/audit-gate/04-design-v1.1-delta-handoff.md`

Validated against:
- `01-requirements-spec.md`, `02-design-spec-v1.md`, `03-adversarial-review.md`, `05-review-checklist.md`

---

## Add

1. **Normative transition table (task/milestone/release) with guards**
- Add explicit legal transitions and guard predicates.
- Add required illegal transition list.
- Rationale: removes ambiguity in `passed|failed -> terminal` shorthand.
  - Evidence: `02-design-spec-v1.md` → **State Machine**; `05-review-checklist.md` → **3) State Machine & Transition Invariants**.

2. **Failure-class taxonomy and deterministic mapping**
- Add `failure_class: policy|transient|system|timeout|unknown` in GateResult decision layer.
- Map each class to next state and retry behavior.
- Rationale: required for reproducibility and partial-failure reliability.
  - Evidence: `01-requirements-spec.md` → **Non-Functional Requirements**; `04-design-v1.1-delta-handoff.md` → **Canonical GateResult Schema (v1.1)**.

3. **Profile semantics contract**
- Add precedence rules and numeric thresholds for `strict`, `standard`, `legacy_migration`.
- Add task-tier major severity behavior for each profile.
- Rationale: currently open and determinism-blocking.
  - Evidence: `04-design-v1.1-delta-handoff.md` → **Open Items (1,2)**.

4. **Retry/backoff/watchdog policy**
- Add max attempts, backoff function, stale-running cutoff, and terminal fallback.
- Rationale: deadlock resistance and bounded runtime.
  - Evidence: `04-design-v1.1-delta-handoff.md` → **Open Items (3)**; `03-adversarial-review.md` → **Risk Register**.

5. **Rollback/safe-disable contract**
- Add explicit policy for phase rollback (`full -> soft -> shadow`) and emergency disable behavior.
- Rationale: required by checklist, currently unspecified.
  - Evidence: `05-review-checklist.md` → **8) Migration & Backward Compatibility**.

6. **Observability event schema**
- Add `GateTransitionEvent` and `GateCheckEvent` contracts with correlation IDs.
- Rationale: auditability and deterministic replay support.
  - Evidence: `01-requirements-spec.md` → **Non-Functional Requirements**.

7. **KPI/SLO gate thresholds and enforcement points**
- Add measurable phase-gate criteria for runtime, determinism, false-block rate, and retry amplification.
- Rationale: converts conditional GO into testable GO.
  - Evidence: `03-adversarial-review.md` → **Go / No-Go**; `05-review-checklist.md` → **10) Implementation Readiness Decision**.

---

## Remove

1. **Ambiguous terminal shorthand transitions**
- Remove representation that can imply completion from failed branches.
- Replace with explicit branch-specific transitions.

2. **Implicit profile semantics**
- Remove undocumented interpretation of `strictness`/profiles.
- Replace with one canonical profile model.

---

## Change

1. **API policy flags**
- Change from strictness-only mental model to explicit canonical `--profile` contract.
- Retain `--strictness` as a deprecated alias mapped 1:1 to `--profile` through Soft enforcement only; remove alias at Full enforcement.
- Rationale: resolves v1/v1.1 inconsistency.
  - Evidence: `02-design-spec-v1.md` → **Flags**; `04-design-v1.1-delta-handoff.md` → **v1.1 Delta Summary (B)**.

2. **Override governance data model**
- Add `approver`, `approval_state`, `review_due_at` fields in governance workflow layer.
- Keep release override forbidden invariant unchanged.
- Rationale: reduce governance ambiguity and abuse risk.
  - Evidence: `05-review-checklist.md` → **6) Override Policy & Governance**.

3. **Tier-1 check set optimization**
- Change Tier-1 to fixed deterministic minimal set with explicit cost cap and predictable evidence output format.
- Rationale: preserve mandatory Tier-1 while reducing friction.
  - Evidence: `01-requirements-spec.md` → **Locked Decisions**; `03-adversarial-review.md` → **Strongest Arguments Against (2)**.

---

## Rationale summary
v1.2 should preserve v1.1’s deterministic-first direction while closing correctness and operational reliability gaps that remain open in thresholds, retry semantics, rollback, and explicit transition legality.
