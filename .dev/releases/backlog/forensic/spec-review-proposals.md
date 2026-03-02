# /sc:forensic Spec Review Proposals (Critique Mode)

## PROPOSAL-001: Move panel additions into normative sections

**Category**: consistency
**Severity**: critical
**Affected sections**: [3.1, 3.2, 5.3, 7, 9, 12, 14, 17, Appendix A]
**Current state**: FR-047..FR-055, NFR-009..NFR-010, and Schema 9.9 are listed as “added” in Section 17, but are not actually present in the normative requirements table/schemas/phase logic.
**Proposed change**: Integrate all “panel-incorporated” additions into their canonical sections (requirements, schemas, phase behavior, flags), and keep Section 17 as rationale-only commentary.
**Rationale**: Implementers will follow normative sections, not retrospective commentary. Current structure creates conflicting interpretations of what is actually required.
**Impact**: Updates requirement counts, schema inventory, acceptance tests, and CLI contract.

## PROPOSAL-002: Resolve `--depth` semantic conflict

**Category**: requirements
**Severity**: major
**Affected sections**: [3.1 FR-013, FR-022, FR-038, 5.3, 7.2, 7.4, 14.2]
**Current state**: Command-level `--depth` is defined as mapping to adversarial depth, but Phase 2 and 3b hardcode `deep` and `standard` respectively; circuit breaker may force `quick`.
**Proposed change**: Define precedence order: `circuit-breaker override > explicit --depth > phase default`. Document per-phase defaults only when `--depth` is omitted.
**Rationale**: Without precedence rules, two valid implementations can behave differently for the same command input.
**Impact**: CLI parsing logic, adversarial invocation generation, test matrix.

## PROPOSAL-003: Normalize dry-run behavior and final report semantics

**Category**: requirements
**Severity**: major
**Affected sections**: [3.1 FR-044, 7.7, 12, 13, 17]
**Current state**: FR-044 says dry-run skips Phases 4-5; panel text says Phase 6 should still produce final report for 0-3b. This is not codified in phase rules.
**Proposed change**: Add explicit dry-run phase plan: execute 0→3b→6; mark Phase 4/5 status as `skipped_by_mode` in `progress.json`; require “would-implement” section in report.
**Rationale**: Dry-run must be deterministic and auditable, otherwise users cannot compare runs reliably.
**Impact**: Checkpoint schema, report template, resume logic.

## PROPOSAL-004: Fix artifact path inconsistencies for adversarial outputs

**Category**: consistency
**Severity**: major
**Affected sections**: [3.1 FR-015, FR-016, FR-033, 7.2, 12.1, 13]
**Current state**: Some sections reference `adversarial/base-selection.md` at root; directory structure places it under `phase-2/adversarial/`.
**Proposed change**: Standardize all references to `phase-2/adversarial/base-selection.md` and `phase-2/adversarial/debate-transcript.md` (or choose root-only consistently).
**Rationale**: Artifact lookup errors will break resume and report generation.
**Impact**: Phase handoff contracts, implementation paths, automated validation checks.

## PROPOSAL-005: Correct Phase 3b output location contract

**Category**: phase-interaction
**Severity**: major
**Affected sections**: [3.1 FR-023, FR-024, 7.4, 12.1, 7.7]
**Current state**: `fix-selection.md` is referenced as Phase 3b output, but directory structure places it in `phase-3/` and later phases read it from ambiguous location.
**Proposed change**: Define canonical path (`phase-3b/fix-selection.md`) and update all references; add migration fallback for legacy path if present during resume.
**Rationale**: Clear phase ownership prevents incorrect replay and stale artifact consumption.
**Impact**: Resume logic, output templates, orchestration code.

## PROPOSAL-006: Add missing schema for `new-tests-manifest.json`

**Category**: schema
**Severity**: major
**Affected sections**: [3.1 FR-028, 7.5, 9]
**Current state**: `new-tests-manifest.json` is mandatory output and Phase 5 input, but no formal schema is defined.
**Proposed change**: Add schema with required fields: file path, test type, related hypothesis ID(s), status (new/modified), and optional scenario tags.
**Rationale**: Without schema, Phase 5 test selection and correlation logic is under-specified and non-interoperable.
**Impact**: Test agent prompt, validation logic, report generation.

## PROPOSAL-007: Align Risk Surface schema with prompts and requirements

**Category**: schema
**Severity**: major
**Affected sections**: [3.1 FR-004, 7.0 Agent 0c, 9.3, 17]
**Current state**: Schema requires `overall_risk_score`, but Agent 0c prompt/FR language does not require emitting it; panel mentions `secrets_exposure` addition but schema is unchanged.
**Proposed change**: Update FR/prompt/schema together to require `overall_risk_score` calculation method and include `secrets_exposure` category with constraints.
**Rationale**: Risk scoring drives model-tier and prioritization; missing fields create non-deterministic domain generation.
**Impact**: Phase 0 synthesis, model selection, security reporting.

## PROPOSAL-008: Strengthen `progress.json` for reproducibility and resume safety

**Category**: schema
**Severity**: major
**Affected sections**: [9.8, 12.2, 12.3, 14.1, 17]
**Current state**: Resume logic depends on flags and codebase identity checks, but schema does not require immutable run metadata (target paths, repo HEAD, run ID, schema version).
**Proposed change**: Add required fields: `spec_version`, `run_id`, `target_paths`, `git_head_or_snapshot`, `phase_status_map`; require `flags` as mandatory for resumable runs.
**Rationale**: Prevents stale or tampered resumes and supports deterministic transitions.
**Impact**: Resume validator, pre-flight checks, reporting provenance.

## PROPOSAL-009: Make domain IDs stable across retries/resume

**Category**: architecture
**Severity**: major
**Affected sections**: [7.0, 7.1, 9.4, 9.5, 12.4]
**Current state**: Hypothesis IDs are index-based (`H-{domain_index}-{sequence}`), but domain order can change after reruns or partial resume.
**Proposed change**: Introduce stable `domain_id` (UUID or deterministic hash) and hypothesis IDs based on `domain_id` + sequence; retain display index separately.
**Rationale**: Index drift breaks cross-phase references and invalidates fix mappings.
**Impact**: Findings schema, fix proposal schema, manifests, report tables.

## PROPOSAL-010: Enforce exactly three fix tiers with uniqueness constraints

**Category**: schema
**Severity**: major
**Affected sections**: [3.1 FR-018, 7.3, 9.6]
**Current state**: FR-018 requires three tiers, but schema permits 1..3 options and does not prevent duplicate tiers.
**Proposed change**: Require exactly 3 `fix_options` and uniqueness of `tier` values (`minimal`, `moderate`, `robust`).
**Rationale**: Orchestrator `--fix-tier` selection assumes all tiers exist and are uniquely addressable.
**Impact**: Fix proposal validation, phase 3b comparison, greenlight logic.

## PROPOSAL-011: Remove orchestrator-source-read fallback contradiction

**Category**: architecture
**Severity**: major
**Affected sections**: [4.1 principle 2, 4.3, 14.1]
**Current state**: Architecture says orchestrator never reads source code; error fallback for adversarial failure asks orchestrator to directly rank findings content, potentially exceeding bounded role and token budget.
**Proposed change**: Replace fallback with delegated lightweight scoring agent(s); orchestrator should only read generated summaries.
**Rationale**: Preserves architectural invariant and token model while maintaining degraded operation.
**Impact**: Error handling pipeline, token budget assumptions, implementation complexity.

## PROPOSAL-012: Convert hard token ceilings to enforceable policy with overflow behavior

**Category**: feasibility
**Severity**: major
**Affected sections**: [3.1 FR-006/011/016/024/035, 4.3, 16.1, Appendix B]
**Current state**: Strict per-phase token caps are specified but no policy defines what to do when context inputs exceed those budgets.
**Proposed change**: Define budget policy: soft target + hard stop + fallback action (summarize, sample, or defer) with explicit warning artifact.
**Rationale**: Fixed caps are not realistically guaranteed for variable-size artifacts without deterministic truncation rules.
**Impact**: Orchestrator implementation, observability, quality metric interpretation.

## PROPOSAL-013: Add capability fallback for model-tier assignment

**Category**: feasibility
**Severity**: critical
**Affected sections**: [3.1 FR-010, 4.3, 7, 8, 10]
**Current state**: Spec assumes direct control over Haiku/Sonnet/Opus assignment per agent, which may not always be enforceable in runtime/delegation contexts.
**Proposed change**: Define “requested tier” vs “actual tier” fields in phase metadata and require logging of tier substitution when hard assignment is unavailable.
**Rationale**: Prevents silent divergence between spec intent and runtime behavior.
**Impact**: Agent invocation contracts, quality metrics, cost reporting.

## PROPOSAL-014: Reconcile MCP tool assumptions with executable tool contract

**Category**: feasibility
**Severity**: major
**Affected sections**: [5.1, 6.1, 11, 14.2]
**Current state**: Command frontmatter allows only basic tools plus Skill/Task, yet fallback rules rely on Edit/MultiEdit; MCP calls are assumed available without explicit deferred-tool loading protocol.
**Proposed change**: Update allowed tool contract and add explicit MCP availability/activation preconditions (including fallback to native tool set).
**Rationale**: Current spec can fail at runtime due to undeclared tool dependencies.
**Impact**: Command/skill metadata, implementation guardrails, error handling.

## PROPOSAL-015: Resolve minimum-domain rule for tiny targets

**Category**: edge-case
**Severity**: critical
**Affected sections**: [3.1 FR-005, 7.0, 9.4]
**Current state**: Domain count is fixed to 3-10 and schema enforces minItems=3, which is impossible for tiny scopes (e.g., 1-3 files).
**Proposed change**: Make domain count adaptive (`1..10`) with merge/split heuristics and explicit minimum of 1 when source files exist.
**Rationale**: Prevents forced synthetic domains that dilute analysis quality and distort risk.
**Impact**: Domain generation algorithm, schema validation, downstream agent count.

## PROPOSAL-016: Define deterministic handling when zero hypotheses survive

**Category**: edge-case
**Severity**: major
**Affected sections**: [14.1, 7.2, 7.3, 7.7, 13]
**Current state**: Error table says lower threshold by 0.1 and retry; if still zero, skip phases. This mutates user intent and can create inconsistent outcomes.
**Proposed change**: Keep user threshold immutable unless `--auto-relax-threshold` is explicitly enabled; define a strict no-findings terminal path with dedicated report section.
**Rationale**: Predictable behavior is required for reproducibility and trust in quality gates.
**Impact**: Filtering logic, CLI flags, final report template.

## PROPOSAL-017: Add baseline test artifact to normative phase contracts

**Category**: testing
**Severity**: major
**Affected sections**: [3.1 FR-031/032, 7.5, 12.1, 17]
**Current state**: Panel text introduces baseline test run, but Phase 4/5 contracts and artifact tree do not include it.
**Proposed change**: Add `phase-4/baseline-test-results.md` as required artifact; require Phase 5b to compute `introduced_failures` vs `preexisting_failures`.
**Rationale**: Without baseline diffing, “regression introduced by fix” is not testable.
**Impact**: Validation logic, reporting metrics, acceptance criteria.

## PROPOSAL-018: Define pass/fail exit criteria for pipeline completion

**Category**: requirements
**Severity**: major
**Affected sections**: [14.1, 16.2, 7.6, 7.7]
**Current state**: Lint/test failures do not block pipeline, but quality metrics target 0 lint errors and 100% test pass for new tests; no final exit status model is defined.
**Proposed change**: Introduce explicit run outcome states (`success`, `success_with_risks`, `failed`) and map lint/test/self-review signals to each state.
**Rationale**: Consumers need machine-readable success semantics, not only narrative report text.
**Impact**: Final report frontmatter, CI integration, user expectations.

## PROPOSAL-019: Clarify resume behavior with `--clean` and artifact lifecycle

**Category**: consistency
**Severity**: minor
**Affected sections**: [5.3, Appendix A, 12, 17]
**Current state**: `--clean` removes output directory after final report, but resumability depends on retained artifacts; behavior is undefined for partial failures or interrupted cleanup.
**Proposed change**: Restrict `--clean` to terminal successful runs, or implement archive-before-clean (`--clean=archive|delete`) with guardrails.
**Rationale**: Prevents accidental loss of forensic evidence and resume checkpoints.
**Impact**: CLI UX, post-run operations, recovery options.

## PROPOSAL-020: Redact sensitive data across all exported artifacts, not just final report

**Category**: security
**Severity**: major
**Affected sections**: [7.1, 9.5, 13, 14, 17]
**Current state**: Secret redaction is proposed only for final report excerpts; raw findings/fix artifacts may still contain sensitive strings.
**Proposed change**: Add configurable redaction policy for all persisted artifacts (`findings`, `fix proposals`, transcripts), with optional secure raw retention flag.
**Rationale**: Most leakage risk comes from intermediate artifacts, not just report output.
**Impact**: Agent prompt requirements, schema notes, security posture.

## PROPOSAL-021: Add multi-root path provenance to schemas

**Category**: schema
**Severity**: major
**Affected sections**: [3.1 FR-036, 9.1, 9.4, 9.7, 13]
**Current state**: Paths are described as relative to “target root,” but command accepts multiple target paths; provenance is ambiguous.
**Proposed change**: Add `root_id`/`target_root` fields to path-bearing records and normalize path conventions for multi-root runs.
**Rationale**: Ambiguous file identity causes incorrect correlation between hypotheses, fixes, and validation artifacts.
**Impact**: All manifests, report path rendering, diff tooling.

## PROPOSAL-022: Specify scheduler behavior for MCP concurrency caps

**Category**: architecture
**Severity**: major
**Affected sections**: [3.2 NFR-010 (panel), 7.1, 11, 14.3, 17]
**Current state**: Per-server concurrency cap is mentioned in commentary but no scheduling contract exists (queueing, fairness, backoff, priority).
**Proposed change**: Define MCP-aware scheduler: per-server semaphores, exponential backoff policy, and deterministic queue ordering for resumability.
**Rationale**: Without scheduling rules, high parallelism can trigger avoidable circuit-breaker degradation and non-deterministic outcomes.
**Impact**: Runtime orchestration, performance characteristics, reproducibility.
