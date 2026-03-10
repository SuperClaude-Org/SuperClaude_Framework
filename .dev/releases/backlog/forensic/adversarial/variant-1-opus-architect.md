# Proposal Assessment: Architect Perspective

**Agent**: opus:architect
**Focus**: Architectural soundness, implementation feasibility within Claude Code's actual capabilities, avoiding over-specification
**Skeptical lens**: Proposals that add complexity without clear implementation benefit

---

## PROPOSAL-001: Move panel additions into normative sections
- **Verdict**: ACCEPT
- **Confidence**: 0.95
- **Rationale**: This is a fundamental document integrity issue. Having requirements listed in commentary (Section 17) but absent from normative tables creates ambiguity that directly causes divergent implementations. Implementers will follow normative sections; if requirements exist only in commentary, they are effectively optional. This is the single highest-impact structural fix.

## PROPOSAL-002: Resolve `--depth` semantic conflict
- **Verdict**: ACCEPT
- **Confidence**: 0.92
- **Rationale**: Precedence ambiguity between command-level flags, phase defaults, and circuit-breaker overrides is a classic source of non-deterministic behavior. The proposed precedence order (circuit-breaker > explicit flag > phase default) follows standard override semantics and is straightforward to implement. Without this, two correct implementations could behave differently.

## PROPOSAL-003: Normalize dry-run behavior and final report semantics
- **Verdict**: ACCEPT
- **Confidence**: 0.88
- **Rationale**: Dry-run is a critical user workflow for validating forensic analysis without side effects. The proposal to execute 0-3b-6 with explicit `skipped_by_mode` status is clean and implementable. The "would-implement" report section adds value for users evaluating findings before committing to fixes.

## PROPOSAL-004: Fix artifact path inconsistencies for adversarial outputs
- **Verdict**: ACCEPT
- **Confidence**: 0.93
- **Rationale**: Path inconsistencies between spec sections are implementation-blocking. Any resume or cross-phase reference that reads from the wrong path will silently fail or produce corrupt state. Standardizing to `phase-2/adversarial/` follows the phase-scoped directory convention already established.

## PROPOSAL-005: Correct Phase 3b output location contract
- **Verdict**: ACCEPT
- **Confidence**: 0.90
- **Rationale**: Same class of issue as P-004. Ambiguous output locations for `fix-selection.md` will break downstream consumers. The proposal to use `phase-3b/fix-selection.md` is consistent with naming the phase "3b." The migration fallback for legacy paths during resume is a prudent addition but should be kept simple (check both paths, prefer canonical).

## PROPOSAL-006: Add missing schema for `new-tests-manifest.json`
- **Verdict**: ACCEPT
- **Confidence**: 0.87
- **Rationale**: A mandatory Phase 5 input without a schema is an interoperability gap. The proposed fields (file path, test type, hypothesis IDs, status) are the minimum needed for correlation. This is a straightforward schema addition with no architectural risk.

## PROPOSAL-007: Align Risk Surface schema with prompts and requirements
- **Verdict**: MODIFY
- **Confidence**: 0.80
- **Rationale**: The misalignment between schema, prompts, and FRs for risk surface is real. However, `overall_risk_score` calculation methods can become over-specified -- the spec should define the output contract (field exists, range 0.0-1.0) without mandating a specific calculation algorithm, leaving that to the agent's judgment.
- **Modification**: Accept schema alignment and `secrets_exposure` category addition, but specify `overall_risk_score` as a required output field with range constraint only, not a mandated calculation formula.

## PROPOSAL-008: Strengthen `progress.json` for reproducibility and resume safety
- **Verdict**: MODIFY
- **Confidence**: 0.82
- **Rationale**: The core additions (run_id, spec_version, phase_status_map) are essential for safe resume. However, `git_head_or_snapshot` creates a hard dependency on git that the spec deliberately avoids for non-git targets. `target_paths` is good but `flags` as mandatory could block minimal resume scenarios.
- **Modification**: Make `run_id`, `spec_version`, `phase_status_map`, and `target_paths` required. Make `git_head` and `flags` recommended-but-optional with a warning when absent during resume validation.

## PROPOSAL-009: Make domain IDs stable across retries/resume
- **Verdict**: MODIFY
- **Confidence**: 0.78
- **Rationale**: Index drift is a real problem for cross-phase references. However, UUIDs are overkill for a session-scoped artifact and harm readability. A deterministic hash is better but adds implementation complexity.
- **Modification**: Use a deterministic slug derived from domain name (e.g., `dom-subprocess-lifecycle`) rather than UUID or hash. Retain numeric display index separately. This is human-readable, stable across reruns with same domains, and trivial to implement.

## PROPOSAL-010: Enforce exactly three fix tiers with uniqueness constraints
- **Verdict**: ACCEPT
- **Confidence**: 0.91
- **Rationale**: The `--fix-tier` flag assumes all three tiers exist. Allowing 1-3 with potential duplicates creates a runtime failure when the user selects a tier that does not exist. Schema enforcement is the correct layer for this constraint. Simple, no architectural risk.

## PROPOSAL-011: Remove orchestrator-source-read fallback contradiction
- **Verdict**: ACCEPT
- **Confidence**: 0.86
- **Rationale**: The architectural invariant that the orchestrator never reads source code is load-bearing -- it enables the token budget model. The fallback that violates this invariant undermines the entire architecture. Delegating to a lightweight scoring agent preserves both the invariant and degraded operation capability.

## PROPOSAL-012: Convert hard token ceilings to enforceable policy with overflow behavior
- **Verdict**: ACCEPT
- **Confidence**: 0.85
- **Rationale**: Hard token ceilings without overflow policy are aspirational, not enforceable. Claude Code does not expose precise token counting APIs to spec implementers. The soft-target + hard-stop + fallback model is realistic and gives implementers actionable guidance. This is a feasibility-critical change.

## PROPOSAL-013: Add capability fallback for model-tier assignment
- **Verdict**: ACCEPT
- **Confidence**: 0.93
- **Rationale**: This is the most feasibility-critical proposal. Claude Code's Task tool does not guarantee model selection -- the runtime may substitute models based on availability. Logging "requested vs actual" tier is essential for debugging and quality assessment. Without this, the entire model-tiering system is aspirational.

## PROPOSAL-014: Reconcile MCP tool assumptions with executable tool contract
- **Verdict**: ACCEPT
- **Confidence**: 0.89
- **Rationale**: The spec assumes MCP tools are available without acknowledging the deferred-tool loading protocol. This is a real runtime blocker -- calling Serena or Context7 without first loading them via ToolSearch will fail. The tool contract must be explicit about activation preconditions.

## PROPOSAL-015: Resolve minimum-domain rule for tiny targets
- **Verdict**: ACCEPT
- **Confidence**: 0.90
- **Rationale**: Forcing 3 domains on a 1-3 file target produces synthetic domains that dilute analysis quality. An adaptive minimum of 1 domain is the correct architectural choice. The spec should define merge/split heuristics: merge when domains share >60% file overlap, split when a domain exceeds a file count threshold.

## PROPOSAL-016: Define deterministic handling when zero hypotheses survive
- **Verdict**: ACCEPT
- **Confidence**: 0.87
- **Rationale**: Silently lowering the confidence threshold mutates user intent and makes runs non-reproducible. The proposal to keep thresholds immutable by default with an explicit `--auto-relax-threshold` opt-in is the correct design. The no-findings terminal path needs a dedicated report section confirming "no issues found at threshold X."

## PROPOSAL-017: Add baseline test artifact to normative phase contracts
- **Verdict**: ACCEPT
- **Confidence**: 0.84
- **Rationale**: Without a baseline test run, you cannot distinguish regressions introduced by fixes from pre-existing failures. This is essential for the validation phase to be meaningful. The artifact (`phase-4/baseline-test-results.md`) and the `introduced_failures` vs `preexisting_failures` distinction are well-scoped.

## PROPOSAL-018: Define pass/fail exit criteria for pipeline completion
- **Verdict**: ACCEPT
- **Confidence**: 0.88
- **Rationale**: A pipeline without defined exit states is not CI-integrable. The three-state model (`success`, `success_with_risks`, `failed`) with signal mapping is standard practice. This is a necessary addition for any consumer of the pipeline output.

## PROPOSAL-019: Clarify resume behavior with `--clean` and artifact lifecycle
- **Verdict**: MODIFY
- **Confidence**: 0.75
- **Rationale**: The proposal identifies a real issue (cleaning artifacts needed for resume) but the `--clean=archive|delete` sub-option adds CLI complexity for a minor feature. The simpler fix is to restrict `--clean` to terminal successful runs only, which covers 90% of the use case.
- **Modification**: Restrict `--clean` to only execute after terminal `success` status. For `success_with_risks` or `failed`, artifacts are always retained. Drop the archive sub-option.

## PROPOSAL-020: Redact sensitive data across all exported artifacts
- **Verdict**: MODIFY
- **Confidence**: 0.76
- **Rationale**: The security concern is valid -- intermediate artifacts can contain secrets. However, implementing a configurable redaction policy across all artifact types adds significant complexity. A simpler approach is more feasible for v1.
- **Modification**: Require agents to apply the existing redaction pattern (regex-based secret detection) to all persisted artifacts, rather than defining a new configurable policy system. Add a single `--redact-artifacts` flag (default: true) rather than a full policy framework.

## PROPOSAL-021: Add multi-root path provenance to schemas
- **Verdict**: ACCEPT
- **Confidence**: 0.83
- **Rationale**: Multi-root path ambiguity is a real issue when the command accepts multiple target paths. Adding `target_root` to path-bearing records is a minimal schema change that prevents incorrect cross-referencing. The normalization convention (relative to which root) must be explicit.

## PROPOSAL-022: Specify scheduler behavior for MCP concurrency caps
- **Verdict**: REJECT
- **Confidence**: 0.72
- **Rationale**: This proposal asks the spec to define an MCP-aware scheduler with semaphores, exponential backoff, and deterministic queue ordering. This is over-specification for a v1 spec -- it prescribes implementation internals that belong in an implementation guide, not a requirements specification. The existing circuit-breaker patterns in the SuperClaude framework already handle MCP degradation. The spec should state the *requirement* (respect MCP concurrency limits) without mandating the scheduling algorithm.
