# D-0005: Phase 5 Gate Decision

## Task: T01.05 -- Gate decision on Phase 5 activation

**Date**: 2026-03-15

## Decision: PHASE 5 ACTIVATES

### Gate Input

- **Phase 0 Result**: BROKEN (see D-0004)
- **Roadmap Mapping**: BROKEN → Phase 5 activates after Phases 2-4

### Gate Logic

Per roadmap Task 0.5:
- WORKING → skip Phase 5, proceed to Phases 2, 3, 4, 6, 7
- BROKEN → Phase 5 activates and becomes release-blocking

**Result**: BROKEN → **Phase 5 activates**

### Phase Execution Order

1. Phase 2 (next) — proceed as planned
2. Phase 3 — proceed as planned
3. Phase 4 — proceed as planned
4. **Phase 5 — ACTIVATED** (conditional `--file` fallback remediation, release-blocking)
5. Phase 6 — proceed as planned
6. Phase 7 — proceed as planned

### Phase 5 Context

Phase 5 remediation should account for the specific failure mode discovered:

1. `--file` is a cloud file download mechanism, NOT a local file path injector
2. Alternative content delivery methods should be investigated:
   - Stdin piping: `cat file.md | claude --print -p "question"`
   - Prompt concatenation: include file content directly in the `-p` argument
   - System prompt injection: `--system-prompt "$(cat file.md)"`
3. The roadmap's ~80% probability of BROKEN was correct
4. The failure is architectural (design intent of `--file`), not a bug

### Downstream Impact

All phases that depend on file content delivery to the CLI must use alternative mechanisms. Phase 5 must define and validate these alternatives before Phase 6-7 can finalize.

## Acceptance Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Gate decision is binary | PASS | Phase 5 activated |
| Decision maps BROKEN→activate | PASS | Per roadmap Task 0.5 |
| Downstream dependencies updated | PASS | Execution order documented above |
| Decision recorded | PASS | This file |
