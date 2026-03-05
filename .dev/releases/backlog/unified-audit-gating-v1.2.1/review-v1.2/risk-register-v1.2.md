# Unified Audit Gating System v1.2 — Risk Register

| ID | Risk | Cause | Impact | Likelihood | Mitigation | Owner | Trigger | Rollback |
|---|---|---|---|---|---|---|---|---|
| R1 | Invalid completion from failed audit branch | Ambiguous terminal transition expression | Incorrect task/milestone/release closure | Medium | Replace shorthand with explicit transition table + guard checks | State-machine owner | Any completion attempt after `audit_*_failed` | Disable hard-enforcement, revert to shadow-only decisions |
| R2 | Stuck `audit_*_running` states | Timeout/retry semantics incomplete | Pipeline deadlock, operator stalls | High | Define heartbeat, stale timeout, bounded retries, deterministic terminal state | Reliability owner | Running state exceeds timeout budget | Auto-transition to failed(timeout), allow controlled re-queue |
| R3 | Non-reproducible gate outcomes | Threshold/profile semantics unresolved | Audit disputes, inconsistent pass/fail | High | Lock profile thresholds and severity policy before rollout | Policy owner | Same inputs produce divergent outcomes | Freeze to strict deterministic baseline profile |
| R4 | Throughput degradation on minor work | Tier-1 mandatory for LIGHT/EXEMPT without latency SLO enforcement | Developer friction, delayed delivery | High | Enforce Tier-1 P95 runtime SLO and fast-fail remediation output | DX owner | Tier-1 P95 latency breach | Temporary soft-enforcement for LIGHT/EXEMPT |
| R5 | Override governance drift | Governance metadata exists but approval workflow is under-specified | Policy erosion, inconsistent override usage | Medium | Add approver model, reason taxonomy, review cadence | PM/Process owner | Override volume spike or low-quality reasons | Restrict overrides to stricter approval temporarily |
| R6 | Migration failure during rollout | Legacy mapping/compatibility not fully parameterized | Blocked phase/release closure | Medium | Add legacy mapping test matrix + compatibility checks | Migration owner | Soft/full phase failure-rate exceeds threshold | Revert to prior phase, keep shadow artifacts |
| R7 | Runtime cost spikes | No explicit token/tool call budget per tier | Operational inefficiency | Medium | Add cost budgets and hard caps by tier | Performance owner | Cost/KPI threshold breach | Disable expensive optional checks, deterministic core only |
| R8 | Incomplete audit traceability | Evidence schema exists, but event contract not explicit | Low confidence in forensic reconstruction | Medium | Add transition/event schema with correlation IDs | Observability owner | Missing evidence in failed checks | Block completion and force re-run with trace enabled |
| R9 | Incorrect profile interpretation | `strictness` flags and profile terms inconsistent | Misconfiguration and inconsistent behavior | Medium | Unify nomenclature and precedence rules | API owner | Config parse ambiguity or policy mismatch | Default to strict baseline + explicit warning |
| R10 | Unowned open decisions | Handoff lists open items but no owner/deadline | Decision drift, schedule slips | High | Assign owner/date to each open item before implementation | Program manager | Unresolved item at phase gate | Hold phase advancement; return to design sign-off |

## Evidence anchors
- `01-requirements-spec.md` → **Locked Decisions**, **Non-Functional Requirements**, **Acceptance Criteria**
- `02-design-spec-v1.md` → **State Machine**, **Flags**, **Migration / Rollout**, **Failure / Override Policy**
- `03-adversarial-review.md` → **Risk Register**, **Strongest Arguments Against**
- `04-design-v1.1-delta-handoff.md` → **v1.1 Delta Summary**, **Open Items for Next Reviewer**, **Transition invariants**
- `05-review-checklist.md` → **3) State Machine**, **8) Migration**, **9) Risk & Reliability**, **10) Readiness**
