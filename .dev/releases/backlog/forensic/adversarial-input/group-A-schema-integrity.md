# Group A: Schema & Data Integrity (6 proposals)

These proposals address data schema completeness, field alignment, and cross-schema consistency.

## PROPOSAL-006: Add missing schema for `new-tests-manifest.json`

**Category**: schema | **Severity**: major
**Affected sections**: [3.1 FR-028, 7.5, 9]
**Current state**: `new-tests-manifest.json` is mandatory output and Phase 5 input, but no formal schema is defined.
**Proposed change**: Add schema with required fields: file path, test type, related hypothesis ID(s), status (new/modified), and optional scenario tags.
**Rationale**: Without schema, Phase 5 test selection and correlation logic is under-specified and non-interoperable.
**Impact**: Test agent prompt, validation logic, report generation.

## PROPOSAL-007: Align Risk Surface schema with prompts and requirements

**Category**: schema | **Severity**: major
**Affected sections**: [3.1 FR-004, 7.0 Agent 0c, 9.3, 17]
**Current state**: Schema requires `overall_risk_score`, but Agent 0c prompt/FR language does not require emitting it; panel mentions `secrets_exposure` addition but schema is unchanged.
**Proposed change**: Update FR/prompt/schema together to require `overall_risk_score` calculation method and include `secrets_exposure` category with constraints.
**Rationale**: Risk scoring drives model-tier and prioritization; missing fields create non-deterministic domain generation.
**Impact**: Phase 0 synthesis, model selection, security reporting.

## PROPOSAL-008: Strengthen `progress.json` for reproducibility and resume safety

**Category**: schema | **Severity**: major
**Affected sections**: [9.8, 12.2, 12.3, 14.1, 17]
**Current state**: Resume logic depends on flags and codebase identity checks, but schema does not require immutable run metadata (target paths, repo HEAD, run ID, schema version).
**Proposed change**: Add required fields: `spec_version`, `run_id`, `target_paths`, `git_head_or_snapshot`, `phase_status_map`; require `flags` as mandatory for resumable runs.
**Rationale**: Prevents stale or tampered resumes and supports deterministic transitions.
**Impact**: Resume validator, pre-flight checks, reporting provenance.

## PROPOSAL-009: Make domain IDs stable across retries/resume

**Category**: architecture | **Severity**: major
**Affected sections**: [7.0, 7.1, 9.4, 9.5, 12.4]
**Current state**: Hypothesis IDs are index-based (`H-{domain_index}-{sequence}`), but domain order can change after reruns or partial resume.
**Proposed change**: Introduce stable `domain_id` (UUID or deterministic hash) and hypothesis IDs based on `domain_id` + sequence; retain display index separately.
**Rationale**: Index drift breaks cross-phase references and invalidates fix mappings.
**Impact**: Findings schema, fix proposal schema, manifests, report tables.

## PROPOSAL-010: Enforce exactly three fix tiers with uniqueness constraints

**Category**: schema | **Severity**: major
**Affected sections**: [3.1 FR-018, 7.3, 9.6]
**Current state**: FR-018 requires three tiers, but schema permits 1..3 options and does not prevent duplicate tiers.
**Proposed change**: Require exactly 3 `fix_options` and uniqueness of `tier` values (`minimal`, `moderate`, `robust`).
**Rationale**: Orchestrator `--fix-tier` selection assumes all tiers exist and are uniquely addressable.
**Impact**: Fix proposal validation, phase 3b comparison, greenlight logic.

## PROPOSAL-021: Add multi-root path provenance to schemas

**Category**: schema | **Severity**: major
**Affected sections**: [3.1 FR-036, 9.1, 9.4, 9.7, 13]
**Current state**: Paths are described as relative to "target root," but command accepts multiple target paths; provenance is ambiguous.
**Proposed change**: Add `root_id`/`target_root` fields to path-bearing records and normalize path conventions for multi-root runs.
**Rationale**: Ambiguous file identity causes incorrect correlation between hypotheses, fixes, and validation artifacts.
**Impact**: All manifests, report path rendering, diff tooling.
