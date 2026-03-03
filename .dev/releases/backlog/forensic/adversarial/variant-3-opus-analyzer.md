# Proposal Assessment: Analyzer Perspective

**Agent**: opus:analyzer
**Focus**: Practical impact -- which proposals fix real implementation blockers vs. theoretical concerns
**Skeptical lens**: Proposals that address unlikely scenarios at the cost of spec complexity

---

## PROPOSAL-001: Move panel additions into normative sections
- **Verdict**: ACCEPT
- **Confidence**: 0.96
- **Rationale**: This is a real implementation blocker. An implementer reading Section 3 will miss requirements listed only in Section 17. This is not a theoretical concern -- it will cause incomplete implementations on every first read of the spec. Highest practical impact.

## PROPOSAL-002: Resolve `--depth` semantic conflict
- **Verdict**: ACCEPT
- **Confidence**: 0.90
- **Rationale**: The conflict between command-level `--depth`, phase defaults, and circuit-breaker overrides will surface immediately during implementation. The first developer to implement Phase 2 will hit the question: "do I use the user's `--depth standard` or the hardcoded `deep`?" This is a day-1 implementation blocker.

## PROPOSAL-003: Normalize dry-run behavior and final report semantics
- **Verdict**: ACCEPT
- **Confidence**: 0.85
- **Rationale**: Dry-run is a common first use of any pipeline -- users want to see what the tool would do before committing. If dry-run behavior is ambiguous, users lose trust. The explicit phase plan is implementable and addresses a real user workflow. Not as urgent as path fixes but important for adoption.

## PROPOSAL-004: Fix artifact path inconsistencies for adversarial outputs
- **Verdict**: ACCEPT
- **Confidence**: 0.94
- **Rationale**: Path inconsistencies are the #1 source of "it works for me but not for you" bugs. This will cause real failures during resume, report generation, and cross-phase artifact reads. Every hour spent debugging a wrong path is wasted. Fix this before any implementation begins.

## PROPOSAL-005: Correct Phase 3b output location contract
- **Verdict**: ACCEPT
- **Confidence**: 0.89
- **Rationale**: Same practical impact as P-004. Path ambiguity will cause real bugs. The migration fallback for resume is a nice-to-have but adds complexity -- for v1, picking one canonical path and being consistent is sufficient.

## PROPOSAL-006: Add missing schema for `new-tests-manifest.json`
- **Verdict**: ACCEPT
- **Confidence**: 0.86
- **Rationale**: Phase 5 consuming a schema-less artifact will produce the "it parsed differently" class of bugs. The schema is small and well-defined. Practical fix with low complexity cost.

## PROPOSAL-007: Align Risk Surface schema with prompts and requirements
- **Verdict**: MODIFY
- **Confidence**: 0.77
- **Rationale**: The misalignment is real but the practical impact depends on how risk scores are used downstream. If `overall_risk_score` drives model-tier selection (which it does), then the field must exist. However, mandating a specific calculation method adds spec complexity for minimal practical benefit -- the agent will produce a reasonable score regardless.
- **Modification**: Require the `overall_risk_score` field and the `secrets_exposure` category. Do not mandate calculation method -- instead require that the agent documents its scoring rationale in the artifact. This is more practically useful than a formula.

## PROPOSAL-008: Strengthen `progress.json` for reproducibility and resume safety
- **Verdict**: MODIFY
- **Confidence**: 0.79
- **Rationale**: `run_id` and `phase_status_map` are essential for any resume implementation -- you cannot resume without knowing what completed. `spec_version` prevents version mismatch. But `git_head_or_snapshot` and mandatory `flags` are over-engineering for v1 -- most users will not be resuming across git states, and the flags are already encoded in the command that produced the checkpoint.
- **Modification**: Require `run_id`, `spec_version`, `phase_status_map`, `target_paths`. Make `git_head`, `flags`, and `codebase_hash` optional with a "resume safety" warning when absent.

## PROPOSAL-009: Make domain IDs stable across retries/resume
- **Verdict**: MODIFY
- **Confidence**: 0.73
- **Rationale**: Index drift is theoretically problematic but practically rare -- most runs complete without retry. The real scenario is resume after Phase 0, where domains are already generated. For resume, the fix is simple: read domain IDs from the existing `investigation-domains.json` rather than regenerating. A full stable-ID system (UUIDs, hashes) adds complexity for a corner case.
- **Modification**: Require that resume reads domain IDs from the existing Phase 0 output rather than regenerating. For fresh runs, index-based IDs are fine. Add a `domain_name` field as a human-readable stable identifier for debugging, not as the primary key.

## PROPOSAL-010: Enforce exactly three fix tiers with uniqueness constraints
- **Verdict**: ACCEPT
- **Confidence**: 0.88
- **Rationale**: The `--fix-tier` flag will crash or produce undefined behavior if the selected tier does not exist. This is a real bug that will surface in the first non-trivial test. Simple schema fix with high practical value.

## PROPOSAL-011: Remove orchestrator-source-read fallback contradiction
- **Verdict**: ACCEPT
- **Confidence**: 0.82
- **Rationale**: The architectural invariant is important, but the practical risk is: what happens when adversarial debate fails? If the fallback requires the orchestrator to read source code, you blow the token budget. The delegated scoring agent is a practical solution that keeps the pipeline running under failure conditions.

## PROPOSAL-012: Convert hard token ceilings to enforceable policy with overflow behavior
- **Verdict**: ACCEPT
- **Confidence**: 0.83
- **Rationale**: Hard token ceilings will be violated in practice -- a complex codebase with 10 domains will produce findings that exceed any fixed budget. The current spec gives no guidance on what to do when this happens, which means implementations will handle it ad-hoc (truncation, crash, silent data loss). Defining overflow behavior prevents a class of real production failures.

## PROPOSAL-013: Add capability fallback for model-tier assignment
- **Verdict**: ACCEPT
- **Confidence**: 0.95
- **Rationale**: This is the most practically impactful feasibility proposal. In real Claude Code usage, model selection via Task tool is not guaranteed. If the spec assumes Opus is always available for Phase 6 and the runtime substitutes Sonnet, the user gets a different quality report with no indication of why. This will cause real user confusion and bug reports.

## PROPOSAL-014: Reconcile MCP tool assumptions with executable tool contract
- **Verdict**: ACCEPT
- **Confidence**: 0.91
- **Rationale**: This is a real runtime blocker. The first implementation attempt will fail when trying to call Serena without loading it via ToolSearch first. The spec must declare tool activation as a prerequisite, or every implementation will independently discover and work around this issue.

## PROPOSAL-015: Resolve minimum-domain rule for tiny targets
- **Verdict**: ACCEPT
- **Confidence**: 0.88
- **Rationale**: Users will run `/sc:forensic` on a single file or small module. Forcing 3 domains on 2 files produces absurd results like "Domain 1: file1.py lines 1-50, Domain 2: file1.py lines 51-100, Domain 3: file2.py." This will happen in practice and undermine user trust. Adaptive minimum is essential.

## PROPOSAL-016: Define deterministic handling when zero hypotheses survive
- **Verdict**: ACCEPT
- **Confidence**: 0.85
- **Rationale**: Zero surviving hypotheses is not unlikely -- a well-maintained codebase analyzed with a high threshold will produce this result. The current behavior (silently lower threshold) will confuse users who explicitly chose 0.8 and find hypotheses rated 0.7 in their report. The immutable threshold with explicit opt-in is the right UX choice.

## PROPOSAL-017: Add baseline test artifact to normative phase contracts
- **Verdict**: MODIFY
- **Confidence**: 0.78
- **Rationale**: The baseline test concept is sound, but adding a mandatory artifact and diff computation to Phase 4/5 increases pipeline runtime significantly for large test suites. For v1, this should be recommended but not mandatory.
- **Modification**: Make baseline test run a SHOULD (not MUST) requirement. Add the artifact path and diff computation to the spec, but allow implementations to skip it when the test suite exceeds a configurable timeout threshold (e.g., `--baseline-timeout 300s`). Default behavior: attempt baseline, gracefully degrade if timeout exceeded.

## PROPOSAL-018: Define pass/fail exit criteria for pipeline completion
- **Verdict**: ACCEPT
- **Confidence**: 0.90
- **Rationale**: Without exit criteria, the pipeline is a report generator, not a quality gate. The three-state model directly enables CI integration, which is a high-value practical capability. Every consumer of the pipeline output needs to know: did it pass?

## PROPOSAL-019: Clarify resume behavior with `--clean` and artifact lifecycle
- **Verdict**: MODIFY
- **Confidence**: 0.70
- **Rationale**: The `--clean` edge case is real but low-frequency. Most users either want artifacts (for review) or don't (for CI). The archive sub-option adds CLI complexity for a niche use case.
- **Modification**: Simply document that `--clean` removes artifacts after successful completion only. Failed or partial runs always retain artifacts. No sub-options needed for v1.

## PROPOSAL-020: Redact sensitive data across all exported artifacts
- **Verdict**: MODIFY
- **Confidence**: 0.72
- **Rationale**: The security concern is real but the practical frequency is low -- most forensic analysis targets application logic, not secret-handling code. A full configurable redaction policy is over-engineering for v1.
- **Modification**: Add a note in agent prompts requiring secret pattern awareness (regex for API keys, tokens, passwords). Add `--redact` flag (default: true) that applies basic pattern matching to all persisted artifacts. Defer configurable policy to v2.

## PROPOSAL-021: Add multi-root path provenance to schemas
- **Verdict**: MODIFY
- **Confidence**: 0.75
- **Rationale**: Multi-root is a real feature (the command accepts multiple paths), but in practice most invocations will target a single root. Adding `root_id`/`target_root` to every path-bearing record adds schema complexity that affects the common case to handle an uncommon case.
- **Modification**: Add `target_root` at the domain level (each domain has a root), not at every individual path record. Individual paths within a domain are relative to the domain's root. This is simpler and covers the practical case.

## PROPOSAL-022: Specify scheduler behavior for MCP concurrency caps
- **Verdict**: REJECT
- **Confidence**: 0.78
- **Rationale**: MCP scheduling is a framework-level concern handled by SuperClaude's existing circuit-breaker and MCP.md configuration. The forensic spec should not re-specify framework internals. The practical risk of MCP congestion is already mitigated by the `--concurrency` flag limiting parallel agents. Adding a scheduler specification to this spec creates maintenance burden and potential conflicts with the framework-level implementation. This is a solution looking for a problem that the framework already solves.
