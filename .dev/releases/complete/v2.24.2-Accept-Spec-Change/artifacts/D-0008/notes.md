# D-0008: Resolved Open Questions

Phase 2 decision artifact for accept-spec-change open questions.

---

## Q1: Severity field source

**Question:** Where does the `severity` field come from in deviation records?

**Decision:** The `severity` field is NOT present in existing deviation file frontmatter. It is not referenced in `spec_patch.py` and is not part of the `DeviationRecord` dataclass. The field is omitted from the accept-spec-change workflow entirely.

**Rationale:** Grep across `.dev/releases/` shows `severity` is used in audit-gating contexts (profiles, risk assessment) but never in deviation record frontmatter. The `DeviationRecord` dataclass uses `disposition`, `spec_update_required`, `affects_spec_sections`, and `acceptance_rationale` -- no severity field. If severity is needed in future, it can be added as an optional field without breaking existing records.

---

## Q2: `started_at` fallback behavior

**Question:** What happens when `started_at` is absent from a step in `.roadmap-state.json`?

**Decision:** Fail-closed. When `started_at` is absent, the condition is treated as NOT met. This means any retry logic that depends on `started_at` (e.g., time-based retry eligibility) will not proceed.

**Rationale:** Fail-closed is the safest default. If `started_at` is missing, it means the step either never started or the state file was corrupted. In both cases, the operator should run the step from scratch rather than assuming any time-based condition is satisfied. This prevents silent data corruption from propagating through the pipeline.

---

## Q3: Post-acceptance file lifecycle

**Question:** What happens to `dev-*-accepted-deviation.md` files after `accept-spec-change` updates the hash?

**Decision:** Deviation files remain in place as an immutable audit trail. They are NOT deleted, moved, or modified by the `accept-spec-change` command.

**Rationale:** Deviation files serve as evidence that a spec change was reviewed and accepted. Deleting them would destroy the audit trail. The `spec_hash` update in `.roadmap-state.json` is the only mutation. Future runs can still scan these files -- if the hash is current, the command exits 0 with "nothing to do" (idempotent). This is confirmed by the idempotency tests in `test_accept_spec_change.py`.

---

## Q4: Multiple deviation batches

**Question:** How are multiple qualifying deviation records handled in a single prompt?

**Decision:** All qualifying records are displayed in a single prompt. The operator sees every `DEV-*` record with `disposition: ACCEPTED` and `spec_update_required: true`, then confirms or aborts for the entire batch.

**Rationale:** `scan_accepted_deviation_records()` returns all qualifying records as a list. The prompt displays each record's ID, affected sections, and rationale. A single `y/N` confirmation covers all records. This avoids the complexity of per-record acceptance and matches the workflow: the spec has already been edited to incorporate all accepted deviations, so the hash update covers all of them atomically.

---

## Consistency Check

All four decisions are consistent with the Phase 1 implementation in `spec_patch.py`:
- No `severity` field in `DeviationRecord` (Q1)
- No `started_at` fallback logic in `prompt_accept_spec_change` -- it only checks `spec_hash` (Q2 is about the broader pipeline, documented here for Phase 3)
- No file deletion or modification of deviation files (Q3)
- `scan_accepted_deviation_records()` returns full list, prompt shows all (Q4)
