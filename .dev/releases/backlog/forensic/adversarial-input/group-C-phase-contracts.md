# Group C: Phase Contracts & Consistency (5 proposals)

These proposals address phase handoff contracts, artifact paths, normative consistency, and inter-phase semantics.

## PROPOSAL-001: Move panel additions into normative sections

**Category**: consistency | **Severity**: critical
**Affected sections**: [3.1, 3.2, 5.3, 7, 9, 12, 14, 17, Appendix A]
**Current state**: FR-047..FR-055, NFR-009..NFR-010, and Schema 9.9 are listed as "added" in Section 17, but are not actually present in the normative requirements table/schemas/phase logic.
**Proposed change**: Integrate all "panel-incorporated" additions into their canonical sections (requirements, schemas, phase behavior, flags), and keep Section 17 as rationale-only commentary.
**Rationale**: Implementers will follow normative sections, not retrospective commentary. Current structure creates conflicting interpretations of what is actually required.
**Impact**: Updates requirement counts, schema inventory, acceptance tests, and CLI contract.

## PROPOSAL-002: Resolve `--depth` semantic conflict

**Category**: requirements | **Severity**: major
**Affected sections**: [3.1 FR-013, FR-022, FR-038, 5.3, 7.2, 7.4, 14.2]
**Current state**: Command-level `--depth` is defined as mapping to adversarial depth, but Phase 2 and 3b hardcode `deep` and `standard` respectively; circuit breaker may force `quick`.
**Proposed change**: Define precedence order: `circuit-breaker override > explicit --depth > phase default`. Document per-phase defaults only when `--depth` is omitted.
**Rationale**: Without precedence rules, two valid implementations can behave differently for the same command input.
**Impact**: CLI parsing logic, adversarial invocation generation, test matrix.

## PROPOSAL-004: Fix artifact path inconsistencies for adversarial outputs

**Category**: consistency | **Severity**: major
**Affected sections**: [3.1 FR-015, FR-016, FR-033, 7.2, 12.1, 13]
**Current state**: Some sections reference `adversarial/base-selection.md` at root; directory structure places it under `phase-2/adversarial/`.
**Proposed change**: Standardize all references to `phase-2/adversarial/base-selection.md` and `phase-2/adversarial/debate-transcript.md` (or choose root-only consistently).
**Rationale**: Artifact lookup errors will break resume and report generation.
**Impact**: Phase handoff contracts, implementation paths, automated validation checks.

## PROPOSAL-005: Correct Phase 3b output location contract

**Category**: phase-interaction | **Severity**: major
**Affected sections**: [3.1 FR-023, FR-024, 7.4, 12.1, 7.7]
**Current state**: `fix-selection.md` is referenced as Phase 3b output, but directory structure places it in `phase-3/` and later phases read it from ambiguous location.
**Proposed change**: Define canonical path (`phase-3b/fix-selection.md`) and update all references; add migration fallback for legacy path if present during resume.
**Rationale**: Clear phase ownership prevents incorrect replay and stale artifact consumption.
**Impact**: Resume logic, output templates, orchestration code.

## PROPOSAL-003: Normalize dry-run behavior and final report semantics

**Category**: requirements | **Severity**: major
**Affected sections**: [3.1 FR-044, 7.7, 12, 13, 17]
**Current state**: FR-044 says dry-run skips Phases 4-5; panel text says Phase 6 should still produce final report for 0-3b. This is not codified in phase rules.
**Proposed change**: Add explicit dry-run phase plan: execute 0→3b→6; mark Phase 4/5 status as `skipped_by_mode` in `progress.json`; require "would-implement" section in report.
**Rationale**: Dry-run must be deterministic and auditable, otherwise users cannot compare runs reliably.
**Impact**: Checkpoint schema, report template, resume logic.
