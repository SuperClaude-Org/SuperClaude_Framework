# /sc:forensic Spec Review -- Proposal Verdicts

**Pipeline**: /sc:adversarial (Mode B, 3 agents, depth: deep)
**Convergence**: 100% (22/22 proposals resolved in 2 rounds)
**Agents**: opus:architect, opus:quality-engineer, opus:analyzer
**Date**: 2026-02-28
**Source**: spec-review-proposals.md (22 proposals)
**Artifacts**: adversarial/ directory (diff-analysis.md, debate-transcript.md, variant-1/2/3)

---

## 1. Per-Proposal Verdict Table

| ID | Verdict | Confidence | Dissenting Opinions |
|----|---------|------------|---------------------|
| P-001 | **ACCEPT** | 0.96 | None (unanimous) |
| P-002 | **ACCEPT** | 0.92 | None (unanimous) |
| P-003 | **ACCEPT** | 0.88 | None (unanimous) |
| P-004 | **ACCEPT** | 0.94 | None (unanimous) |
| P-005 | **ACCEPT** | 0.90 | None (unanimous) |
| P-006 | **ACCEPT** | 0.89 | None (unanimous). QE suggests adding `schema_version` field (minor enhancement). |
| P-007 | **MODIFY** | 0.85 | QE initially wanted mandated calculation formula; converged to recommended default. |
| P-008 | **MODIFY** | 0.84 | QE initially wanted all fields mandatory; converged to conditional git requirement. |
| P-009 | **MODIFY** | 0.82 | Analyzer initially proposed minimal fix (read-from-artifacts only); converged to slug-based IDs. |
| P-010 | **ACCEPT** | 0.91 | None (unanimous) |
| P-011 | **ACCEPT** | 0.84 | None (unanimous) |
| P-012 | **MODIFY** | 0.83 | Architect/Analyzer initially accepted as-is; converged to QE's three-level model. |
| P-013 | **ACCEPT** | 0.93 | None (unanimous) |
| P-014 | **ACCEPT** | 0.90 | None (unanimous) |
| P-015 | **ACCEPT** | 0.87 | QE initially wanted minimum domain warning; withdrew in Round 2. |
| P-016 | **ACCEPT** | 0.88 | None (unanimous) |
| P-017 | **ACCEPT** | 0.85 | Analyzer initially wanted SHOULD; converged to MUST with timeout implementation note. |
| P-018 | **ACCEPT** | 0.91 | None (unanimous) |
| P-019 | **MODIFY** | 0.78 | QE initially wanted archive sub-option; converged to terminal-success-only. |
| P-020 | **MODIFY** | 0.77 | QE initially wanted full configurable policy; converged to simple flag + prompt guidance. |
| P-021 | **MODIFY** | 0.80 | QE initially wanted record-level root; converged to domain-level for v1. |
| P-022 | **REJECT** | 0.76 | QE initially wanted behavioral contract; revised to reject with minor FR addendum suggestion. |

### Summary
- **ACCEPT**: 14 proposals (P-001 through P-006, P-010, P-011, P-013 through P-018)
- **MODIFY**: 7 proposals (P-007, P-008, P-009, P-012, P-019, P-020, P-021)
- **REJECT**: 1 proposal (P-022)

---

## 2. Modification Details

### P-007: Align Risk Surface schema (MODIFY)
**Original**: Update FR/prompt/schema to require `overall_risk_score` calculation method and `secrets_exposure` category.
**Modification**: Accept schema alignment and `secrets_exposure` category addition. Require `overall_risk_score` as a mandatory output field with range [0.0, 1.0]. Provide "recommended default: max of category scores" as guidance, not a mandated formula. Require the agent to document its scoring rationale in the artifact.
**Rationale**: Mandating a specific formula constrains agent intelligence while adding spec rigidity. A recommended default provides determinism for implementations that want it while allowing improvement.

### P-008: Strengthen progress.json (MODIFY)
**Original**: Add `spec_version`, `run_id`, `target_paths`, `git_head_or_snapshot`, `phase_status_map`; require `flags` as mandatory.
**Modification**: Make `run_id`, `spec_version`, `phase_status_map`, and `target_paths` REQUIRED. Make `git_head` REQUIRED when target is a git repository (auto-detected), OPTIONAL otherwise. Make `flags` RECOMMENDED with a warning when absent during resume validation.
**Rationale**: Core fields enable safe resume. Conditional git_head preserves resume safety for git targets without breaking non-git universality. Mandatory flags adds burden for minimal practical benefit since flags are already encoded in the command invocation.

### P-009: Make domain IDs stable (MODIFY)
**Original**: Introduce stable `domain_id` (UUID or deterministic hash) and hypothesis IDs based on `domain_id` + sequence.
**Modification**: Use deterministic slug derived from domain name (e.g., `dom-subprocess-lifecycle`) as the stable `domain_id`. Hypothesis IDs use the slug: `H-{domain_slug}-{seq}`. Retain numeric display index separately for human readability in tables and reports.
**Rationale**: Slugs are human-readable, stable across reruns with the same domains, and trivially implementable (slugify the domain name). UUIDs/hashes sacrifice readability for no additional benefit in this context.

### P-012: Convert hard token ceilings (MODIFY)
**Original**: Define budget policy: soft target + hard stop + fallback action.
**Modification**: Define three explicit levels per phase: (1) **Soft target** -- the design goal for normal operation, (2) **Hard ceiling** -- a testable maximum set at approximately 2x the soft target, and (3) **Overflow action** -- what happens when hard ceiling is reached (summarize, sample, or defer, with explicit warning artifact). Retain hard ceilings as testable constraints rather than removing them entirely.
**Rationale**: The QE correctly identified that removing hard ceilings eliminates testability. The three-level model preserves testable bounds while acknowledging that soft targets will be exceeded in practice for large codebases.

### P-019: Clarify resume behavior with --clean (MODIFY)
**Original**: Restrict `--clean` to terminal successful runs, or implement `--clean=archive|delete` with guardrails.
**Modification**: Restrict `--clean` to execute only after terminal `success` status. For `success_with_risks` or `failed` runs, artifacts are always retained. No archive/delete sub-options for v1 -- simplify to a binary behavior: clean on success, retain otherwise.
**Rationale**: The archive sub-option adds CLI complexity for a niche use case. Terminal-success-only covers 90%+ of the use case. Users with `success_with_risks` outcomes need their artifacts for review by definition.

### P-020: Redact sensitive data (MODIFY)
**Original**: Add configurable redaction policy for all persisted artifacts with optional secure raw retention flag.
**Modification**: (1) Add requirement in all agent prompts for secret pattern awareness (regex for API keys, tokens, passwords, private keys). (2) Add `--redact` flag (default: `true`) that applies basic pattern matching to all persisted artifacts (findings, fix proposals, transcripts, manifests). (3) Defer configurable per-environment redaction policy and secure raw retention to v2.
**Rationale**: A simple flag with sensible defaults addresses the security concern without the complexity of a configurable policy framework. Enterprise customization can be layered on in v2.

### P-021: Add multi-root path provenance (MODIFY)
**Original**: Add `root_id`/`target_root` fields to path-bearing records and normalize path conventions.
**Modification**: Add `target_root` at the **domain level** (each domain has a single root from the set of target paths). Individual file paths within a domain are relative to the domain's `target_root`. Note a v1 limitation: if a single domain spans files from multiple target roots, the domain should be split. Add this as a domain generation constraint.
**Rationale**: Domain-level root provenance covers the vast majority of multi-root cases (each domain typically maps to one target). Record-level root on every path-bearing entry adds O(n) schema complexity for a rare edge case. The domain-split constraint ensures the model remains correct.

---

## 3. Rejection Rationale

### P-022: Specify scheduler behavior for MCP concurrency caps -- REJECTED

**Rationale**: Three converging arguments led to rejection:

1. **Framework delegation** (Architect, Analyzer): MCP scheduling (semaphores, backoff, queue ordering) is a framework-level concern already handled by SuperClaude's circuit-breaker patterns in MCP.md. Duplicating this specification in the forensic spec creates maintenance conflicts and potential divergence with the framework implementation.

2. **Existing mitigation** (Analyzer): The `--concurrency` flag already limits parallel agents, which is the primary lever for controlling MCP load. Additional scheduling specification adds no practical value beyond what `--concurrency` already provides.

3. **Over-specification** (Architect): Prescribing internal scheduling mechanisms (deterministic queue ordering, per-server semaphores) constrains implementation choices at a level of detail inappropriate for a requirements specification.

**Minor addendum accepted**: The QE's suggestion to add a brief note to an existing FR (e.g., FR-039 on `--concurrency`) stating "implementations SHOULD respect per-server MCP concurrency limits as defined in MCP.md" is adopted as a minor clarification, not a new requirement. This does not warrant a full proposal acceptance.

---

## 4. Prioritized Implementation Order

Proposals ordered by: (1) blocking severity, (2) dependency relationships, (3) implementation effort.

### Tier 1: Critical Blockers (implement before any coding begins)
These fix structural issues that would cause all implementations to diverge.

| Priority | Proposal | Category | Rationale |
|----------|----------|----------|-----------|
| 1 | **P-001** | consistency | Normative section integrity -- all other proposals reference normative requirements |
| 2 | **P-004** | consistency | Path standardization -- all cross-phase references depend on correct paths |
| 3 | **P-005** | phase-interaction | Phase 3b output contract -- downstream phases depend on this |
| 4 | **P-002** | requirements | --depth precedence -- affects Phase 2 and 3b adversarial invocations |
| 5 | **P-013** | feasibility | Model-tier fallback -- affects all agent invocations across all phases |

### Tier 2: Schema and Contract Fixes (implement during schema finalization)
These complete the data contracts that agents and phases depend on.

| Priority | Proposal | Category | Rationale |
|----------|----------|----------|-----------|
| 6 | **P-006** | schema | new-tests-manifest schema -- Phase 5 input contract |
| 7 | **P-007** | schema | Risk surface alignment -- Phase 0 output drives model selection |
| 8 | **P-010** | schema | Fix tier enforcement -- Phase 3 output constraint |
| 9 | **P-008** | schema | progress.json strengthening -- resume safety foundation |
| 10 | **P-009** | architecture | Stable domain IDs -- cross-phase reference integrity |
| 11 | **P-021** | schema | Multi-root provenance -- path resolution correctness |

### Tier 3: Behavioral Specifications (implement during phase logic)
These define how the pipeline behaves in specific scenarios.

| Priority | Proposal | Category | Rationale |
|----------|----------|----------|-----------|
| 12 | **P-014** | feasibility | MCP tool contract -- runtime prerequisite for all MCP-using phases |
| 13 | **P-015** | edge-case | Tiny target handling -- domain generation algorithm |
| 14 | **P-012** | feasibility | Token budget policy -- orchestrator implementation guidance |
| 15 | **P-011** | architecture | Orchestrator fallback -- error handling pipeline |
| 16 | **P-003** | requirements | Dry-run phase plan -- command-level behavior |
| 17 | **P-016** | edge-case | Zero-hypothesis handling -- filtering logic |

### Tier 4: Quality and Reporting (implement during validation/report phases)
These affect the output quality and pipeline integration.

| Priority | Proposal | Category | Rationale |
|----------|----------|----------|-----------|
| 18 | **P-018** | requirements | Exit criteria -- pipeline completion semantics |
| 19 | **P-017** | testing | Baseline test artifact -- validation phase completeness |
| 20 | **P-020** | security | Artifact redaction -- security posture for all outputs |
| 21 | **P-019** | consistency | --clean behavior -- post-run cleanup semantics |

---

## 5. Adversarial Process Summary

**Pipeline execution**: 3 agents produced independent assessments of 22 proposals. Round 1 parallel debate identified 8 contested proposals (P-007, P-008, P-009, P-012, P-017, P-019, P-020, P-021) and 1 rejected proposal (P-022). Round 2 sequential rebuttals resolved all 8 contested proposals through convergence. Round 3 was skipped (convergence 100% >= 85% threshold).

**Key debate dynamics**:
- The Quality-Engineer consistently pushed for comprehensive coverage and mandatory fields. This was moderated by the Architect's feasibility concerns and the Analyzer's practical frequency assessment.
- The Architect's slug-based domain ID proposal (P-009) was adopted by all three agents as a superior alternative to the original UUID/hash suggestion.
- The Quality-Engineer's three-level token budget model (P-012) was adopted by all three agents as superior to the original two-level proposal.
- The Analyzer shifted position on P-017 (baseline tests) from SHOULD to MUST after the Quality-Engineer's argument about distinguishing introduced vs preexisting failures.
- P-022 was the only rejection, with strong agreement that MCP scheduling belongs at the framework level.

**Confidence distribution**:
- High confidence (>= 0.90): 8 proposals (P-001, P-002, P-004, P-005, P-010, P-013, P-014, P-018)
- Medium confidence (0.80-0.89): 10 proposals (P-003, P-006, P-007, P-008, P-009, P-011, P-012, P-015, P-016, P-017)
- Lower confidence (< 0.80): 4 proposals (P-019, P-020, P-021, P-022)

**Return contract**:
- Status: success
- Convergence score: 1.00
- Artifacts directory: `.dev/releases/backlog/forensic/adversarial/`
- Unresolved conflicts: none
