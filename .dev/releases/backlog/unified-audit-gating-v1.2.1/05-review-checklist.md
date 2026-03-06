# Unified Audit Gating System — Review Checklist (Pass/Fail)

Use this checklist to review design quality and implementation readiness consistently.

## Review Outcome
- [ ] PASS
- [ ] FAIL
- Reviewer:
- Date:
- Notes:

---

## 1) Context Completeness
- [ ] Locked user decisions are captured exactly (configurable strictness, Tier-1 required for LIGHT/EXEMPT, override scope limits, single command, explicit audit_* states)
- [ ] Requirements, design, adversarial review, and v1.1 delta are internally consistent
- [ ] No unresolved contradiction across package files

PASS criteria: all checked.

---

## 2) Command/API Surface
- [ ] Single primary command is clearly defined: `/sc:audit-gate`
- [ ] Scope argument supports task/milestone/release
- [ ] Strictness/config profile controls are specified
- [ ] Override behavior and restrictions are explicit in API
- [ ] Return format includes machine-readable contract

PASS criteria: all checked.

---

## 3) State Machine & Transition Invariants
- [ ] Task flow includes explicit audit states and completion gate
- [ ] Milestone flow includes explicit audit states and completion gate
- [ ] Release flow includes explicit audit states and release gate
- [ ] Forbidden transitions are defined (esp. release override)
- [ ] Timeout/retry/recovery semantics for `audit_*_running` are defined

PASS criteria: all checked.

---

## 4) Data Contracts (Determinism & Auditability)
- [ ] Canonical `GateResult` schema exists and is versioned
- [ ] Canonical `OverrideRecord` schema exists and is versioned
- [ ] Every failed check requires evidence reference (path or file:line)
- [ ] Drift summary distinguishes edited vs non-edited
- [ ] Deterministic decision basis is explicit (LLM advisory vs deterministic core)

PASS criteria: all checked.

---

## 5) Tier Model Soundness
- [ ] Tier-1 scope is lightweight and high-frequency safe
- [ ] Tier-2 scope validates aggregate milestone integrity
- [ ] Tier-3 scope enforces full release closure
- [ ] Severity model (critical/major/minor) is defined and used in blocking policy
- [ ] Profile behavior (strict/standard/legacy_migration) is defined or flagged as open item

PASS criteria: all checked OR open items explicitly tracked with owners.

---

## 6) Override Policy & Governance
- [ ] Overrides allowed only for task/milestone
- [ ] Release override explicitly forbidden
- [ ] Override requires structured reason metadata (code + text + actor + timestamp)
- [ ] Override records are surfaced in higher-tier reports
- [ ] Abuse controls are defined (review cadence, reason taxonomy, optional expiry)

PASS criteria: all checked.

---

## 7) Sprint CLI Integration
- [ ] Task completion transition invokes task gate
- [ ] Milestone/phase completion transition invokes milestone gate
- [ ] Release completion transition invokes release gate
- [ ] Gate reports are persisted as checkpoint/evidence artifacts
- [ ] Integration does not require test results as sole validation source

PASS criteria: all checked.

---

## 8) Migration & Backward Compatibility
- [ ] Legacy state mapping strategy exists
- [ ] Shadow-mode rollout is specified
- [ ] Soft enforcement phase is specified
- [ ] Full enforcement phase is specified
- [ ] Rollback/safe-disable mechanism is specified

PASS criteria: all checked OR missing items called out as blockers.

---

## 9) Risk & Reliability Controls
- [ ] Risk register exists and covers latency, deadlocks, false positives/negatives, migration breakage
- [ ] Mitigations are specific and actionable
- [ ] Tier-1 runtime budget expectation is stated
- [ ] Stuck-state recovery path is explicit
- [ ] Decision transparency standard is defined (why failed, what evidence)

PASS criteria: all checked.

---

## 10) Implementation Readiness Decision
- [ ] Open issues list exists with owners and decision deadlines
- [ ] No critical blocker remains unresolved
- [ ] Next-step artifact map is sufficient for `/sc:workflow` or `/sc:implement`

Decision:
- [ ] GO to workflow/implementation
- [ ] NO-GO (list blockers below)

Blockers:
1.
2.
3.

---

## Minimum Acceptance Threshold
A review is considered **PASS** only if:
- Sections 2, 3, 4, 6, and 7 all pass fully, and
- Any remaining gaps are non-critical and explicitly tracked with owners.
