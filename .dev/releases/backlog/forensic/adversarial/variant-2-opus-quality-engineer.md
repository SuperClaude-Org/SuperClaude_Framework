# Proposal Assessment: Quality Engineer Perspective

**Agent**: opus:quality-engineer
**Focus**: Testability, determinism, edge case completeness, schema rigor
**Skeptical lens**: Proposals that weaken quality gates

---

## PROPOSAL-001: Move panel additions into normative sections
- **Verdict**: ACCEPT
- **Confidence**: 0.97
- **Rationale**: Non-normative requirements are untestable requirements. If FR-047 through FR-055 are not in the normative table, acceptance tests cannot reference them. This is a test matrix integrity issue -- every requirement must be in one canonical location for traceability. Highest priority fix.

## PROPOSAL-002: Resolve `--depth` semantic conflict
- **Verdict**: ACCEPT
- **Confidence**: 0.94
- **Rationale**: Without defined precedence, the same input produces different outputs depending on implementation interpretation. This makes the spec non-deterministic and untestable -- you cannot write a test for `--depth standard` behavior if a phase default silently overrides it. The proposed precedence chain is testable: each level can be independently verified.

## PROPOSAL-003: Normalize dry-run behavior and final report semantics
- **Verdict**: ACCEPT
- **Confidence**: 0.91
- **Rationale**: Dry-run without codified phase rules is an untestable feature. The explicit phase plan (0-3b-6) with `skipped_by_mode` status is deterministic and verifiable. The "would-implement" section enables comparison testing between dry-run and full-run outputs.

## PROPOSAL-004: Fix artifact path inconsistencies for adversarial outputs
- **Verdict**: ACCEPT
- **Confidence**: 0.95
- **Rationale**: Path inconsistencies cause test flakiness -- a test checking for `adversarial/base-selection.md` passes or fails depending on which spec section the implementer followed. This must be deterministic. Every artifact path must appear in exactly one canonical form throughout the spec.

## PROPOSAL-005: Correct Phase 3b output location contract
- **Verdict**: ACCEPT
- **Confidence**: 0.92
- **Rationale**: Same category as P-004. A test that reads `fix-selection.md` from the wrong location will produce false negatives. The migration fallback for resume is a testable edge case that should be covered.

## PROPOSAL-006: Add missing schema for `new-tests-manifest.json`
- **Verdict**: ACCEPT
- **Confidence**: 0.93
- **Rationale**: A mandatory artifact without a schema cannot be validated. This is a quality gate gap -- Phase 5 consumes this artifact but has no way to verify its structure. The proposed fields are the minimum for schema validation. I would additionally require a `schema_version` field for forward compatibility.

## PROPOSAL-007: Align Risk Surface schema with prompts and requirements
- **Verdict**: ACCEPT
- **Confidence**: 0.88
- **Rationale**: Schema-prompt-FR misalignment means the agent may produce output that passes schema validation but violates FR intent, or vice versa. All three must be synchronized. The `overall_risk_score` must have a defined calculation method (even if simple: max of category scores) to ensure deterministic model-tier assignment.

## PROPOSAL-008: Strengthen `progress.json` for reproducibility and resume safety
- **Verdict**: ACCEPT
- **Confidence**: 0.90
- **Rationale**: Resume without immutable run metadata is non-deterministic. A resumed run on a different git HEAD could produce silently wrong results. All proposed fields (`spec_version`, `run_id`, `target_paths`, `git_head_or_snapshot`, `phase_status_map`, `flags`) are necessary for reproducibility testing. Making any of them optional weakens the resume safety guarantee.

## PROPOSAL-009: Make domain IDs stable across retries/resume
- **Verdict**: ACCEPT
- **Confidence**: 0.86
- **Rationale**: Index-based IDs that change across retries break cross-phase reference integrity. Any test that checks hypothesis-to-fix correlation will be flaky if domain indices shift. Stable IDs (whether UUID, hash, or slug) are necessary for deterministic cross-reference validation.

## PROPOSAL-010: Enforce exactly three fix tiers with uniqueness constraints
- **Verdict**: ACCEPT
- **Confidence**: 0.95
- **Rationale**: Schema permitting 1-3 tiers without uniqueness means a validator cannot catch a fix proposal with two `minimal` tiers and no `robust`. This is a schema correctness issue that directly impacts `--fix-tier` selection. Exactly 3 with uniqueness is the correct constraint.

## PROPOSAL-011: Remove orchestrator-source-read fallback contradiction
- **Verdict**: ACCEPT
- **Confidence**: 0.84
- **Rationale**: Architectural invariant violations in fallback paths are the hardest bugs to test -- they only manifest under failure conditions. The proposed delegated scoring agent maintains testability of the fallback path without violating the token budget model.

## PROPOSAL-012: Convert hard token ceilings to enforceable policy with overflow behavior
- **Verdict**: MODIFY
- **Confidence**: 0.80
- **Rationale**: Removing hard ceilings entirely weakens a quality gate. Token budgets serve as testable constraints -- you can verify an implementation stays within budget. The proposal should retain the hard ceiling as a testable maximum while adding the soft target and overflow policy.
- **Modification**: Define three levels: soft target (design goal), hard ceiling (testable maximum, e.g., 2x soft target), and overflow action (what happens at hard ceiling). This preserves testability while acknowledging real-world variability.

## PROPOSAL-013: Add capability fallback for model-tier assignment
- **Verdict**: ACCEPT
- **Confidence**: 0.91
- **Rationale**: Silent model substitution without logging makes quality metrics unreliable. If a phase that should use Opus silently falls back to Haiku, test results are not comparable across runs. "Requested vs actual" logging enables quality regression detection and is a necessary observability feature.

## PROPOSAL-014: Reconcile MCP tool assumptions with executable tool contract
- **Verdict**: ACCEPT
- **Confidence**: 0.90
- **Rationale**: Undeclared tool dependencies are a category of runtime failure that cannot be caught by static analysis of the spec. Explicit tool activation preconditions enable pre-flight checks: before running Phase 1, verify that required MCP tools are loadable. This makes failures deterministic rather than mid-pipeline.

## PROPOSAL-015: Resolve minimum-domain rule for tiny targets
- **Verdict**: MODIFY
- **Confidence**: 0.83
- **Rationale**: Adaptive domain count is correct, but removing the minimum entirely risks degenerate cases. A single domain with a single file produces a trivial analysis that may not justify the pipeline overhead.
- **Modification**: Set minimum to 1 domain (not 3) but require a minimum of 1 file per domain and add a warning when total file count is below a threshold (e.g., 3 files) suggesting the user consider a simpler analysis tool.

## PROPOSAL-016: Define deterministic handling when zero hypotheses survive
- **Verdict**: ACCEPT
- **Confidence**: 0.92
- **Rationale**: Silent threshold mutation is a testability anti-pattern -- a test expecting threshold 0.7 behavior cannot predict when the system will autonomously lower to 0.6. Immutable thresholds with explicit opt-in relaxation produce deterministic, testable behavior. The no-findings terminal path must produce a structured report (not just skip phases) for completeness.

## PROPOSAL-017: Add baseline test artifact to normative phase contracts
- **Verdict**: ACCEPT
- **Confidence**: 0.93
- **Rationale**: Without baseline test results, the validation phase cannot compute `introduced_failures` -- the most critical quality metric. This is not optional for a forensic QA pipeline. The baseline run also provides a regression testing anchor for the entire pipeline.

## PROPOSAL-018: Define pass/fail exit criteria for pipeline completion
- **Verdict**: ACCEPT
- **Confidence**: 0.94
- **Rationale**: A pipeline without exit criteria cannot be used in CI/CD. The three-state model is testable: each state has clear signal conditions that can be verified. This is a quality gate for the pipeline itself, not just the code under investigation.

## PROPOSAL-019: Clarify resume behavior with `--clean` and artifact lifecycle
- **Verdict**: ACCEPT
- **Confidence**: 0.79
- **Rationale**: The `--clean` and resume interaction is an edge case that needs explicit handling. The `--clean=archive|delete` option provides testable behavior for both paths. Restricting to terminal success only leaves the `success_with_risks` case ambiguous -- users may want to clean after reviewing risks.

## PROPOSAL-020: Redact sensitive data across all exported artifacts
- **Verdict**: ACCEPT
- **Confidence**: 0.85
- **Rationale**: Intermediate artifacts containing secrets are a security quality gate failure. Redaction must apply to all persisted artifacts to be meaningful. The configurable policy is necessary because different environments have different sensitivity requirements. A simple flag is insufficient for enterprise use cases where redaction patterns vary.

## PROPOSAL-021: Add multi-root path provenance to schemas
- **Verdict**: ACCEPT
- **Confidence**: 0.87
- **Rationale**: Multi-root path ambiguity produces non-deterministic cross-reference behavior. A hypothesis referencing `src/auth.py` without root context could match files in multiple targets. The `target_root` field makes path resolution deterministic and testable.

## PROPOSAL-022: Specify scheduler behavior for MCP concurrency caps
- **Verdict**: MODIFY
- **Confidence**: 0.74
- **Rationale**: The full scheduler specification (semaphores, backoff, queue ordering) is implementation detail. However, the spec must define testable concurrency behavior: what happens when the concurrency cap is reached? Without this, implementations may silently drop requests, queue indefinitely, or fail fast -- all with different test implications.
- **Modification**: Define the observable behavior contract (max concurrent requests per server, behavior when cap is reached: queue with timeout), not the implementation mechanism. Drop the deterministic queue ordering requirement, which is unrealistic for a v1 spec.
