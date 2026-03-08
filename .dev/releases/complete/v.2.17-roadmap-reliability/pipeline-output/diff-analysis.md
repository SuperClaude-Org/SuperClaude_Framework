

---
total_diff_points: 12
shared_assumptions_count: 14
---

# Shared Assumptions and Agreements

Both variants agree on the following:

1. **Root cause diagnosis**: Three interacting failures — byte-0 gate check, no preamble sanitization, insufficient prompt constraints
2. **Defense-in-depth architecture**: Fix must span gate, sanitizer, prompts, and protocol parity — no single layer is sufficient
3. **Complexity score**: 0.72 (moderate)
4. **File scope**: Same 4 files across 2 package subdirectories
5. **Gate fix approach**: Replace byte-0 check with `re.search()` using compiled `_FRONTMATTER_PATTERN` with `re.MULTILINE`, requiring `key: value` between delimiters
6. **Return semantics**: `(True, None)` / `(False, reason)` preserved
7. **Sanitizer design**: Atomic write via `os.replace()`, UTF-8 preservation, log stripped byte count, no-op when already clean
8. **Sanitizer placement**: After subprocess completion, before gate validation in `roadmap_run_step()`
9. **Prompt hardening**: `<output_format>` XML block at end of all 7 `build_*_prompt()` functions, positive + negative instructions, ≤200 token overhead
10. **Extraction field set**: Same 13+ canonical fields from protocol template
11. **Dependencies**: All stdlib (`re`, `os`, `pathlib`, `logging`) — no new packages
12. **Implementation order**: P1 (gate) first, P2 and P3 parallelizable, P4 last
13. **Highest risk**: Shared `_check_frontmatter()` regression across other pipeline consumers
14. **Success criteria**: 8-step pipeline completion, clean artifacts, 13+ field extraction, green test suite, no shared regressions

# Divergence Points

## 1. Phase 0 — Baseline Analysis

- **Architect**: Omits a formal Phase 0; jumps directly to implementation with implicit scoping
- **Analyzer**: Adds an explicit Phase 0 (0.5 day) for inventory of callers, canonical field confirmation, fixture capture, and impact mapping
- **Impact**: Analyzer's Phase 0 reduces implementation risk by establishing verified scope before code changes. Architect assumes sufficient understanding exists, which is faster but riskier if assumptions are wrong.

## 2. Phase 5 — End-to-End Validation

- **Architect**: Folds E2E validation into success criteria without a dedicated phase
- **Analyzer**: Adds an explicit Phase 5 (0.5 day) with structured E2E run, artifact inspection, regression evidence, and release decision gate
- **Impact**: Analyzer's approach produces a formal release readiness artifact. Architect's approach relies on validation being implicit in each phase's gate, which may miss cross-phase interaction failures.

## 3. Total Phase Count

- **Architect**: 4 phases (P1–P4)
- **Analyzer**: 6 phases (P0–P5)
- **Impact**: Analyzer's structure is more granular with explicit bookends. Architect's is leaner but conflates scoping and validation into implementation phases.

## 4. Effort Estimates

- **Architect**: 7–11 hours across 4 phases
- **Analyzer**: 3.5–4.5 engineering days (≈28–36 hours) across 6 phases
- **Impact**: Significant divergence. Architect scopes this as a focused sprint; Analyzer scopes it as nearly a full work-week. The delta likely reflects Analyzer's inclusion of Phase 0/5 overhead, fixture design time, and more conservative buffer assumptions. Architect's estimate is more realistic for a single experienced developer; Analyzer's accounts for coordination overhead and thoroughness.

## 5. Test Case Counts

- **Architect**: Specifies exact counts — 8 (P1), 5 (P2), 3 (P3), 4 (P4) = 20 cases
- **Analyzer**: Lists test categories and scenarios without fixed counts
- **Impact**: Architect provides a concrete, reviewable test plan. Analyzer provides a flexible test strategy that adapts to discovered edge cases. Architect's is better for estimation; Analyzer's is better for coverage completeness.

## 6. Staffing Model

- **Architect**: Implicitly single-developer execution
- **Analyzer**: Explicitly identifies 3 roles (implementer, QA engineer, documentation/protocol reviewer)
- **Impact**: Analyzer's model is more realistic for team execution but heavier. Architect's model fits a solo developer or pair better.

## 7. Risk Table Depth

- **Architect**: 5 risks with compact severity/probability/mitigation
- **Analyzer**: 6 risks with expanded "why it matters" rationale and explicit validation evidence per risk
- **Impact**: Analyzer adds Risk 6 (runtime diagnostics field ownership ambiguity) which Architect doesn't address. Analyzer's per-risk validation evidence is stronger for audit trails.

## 8. Open Questions Treatment

- **Architect**: Dedicates a section with 6 numbered open questions and explicit architect recommendations for each (defer, investigate, not a real issue)
- **Analyzer**: Embeds recommendations inline as numbered list at the end, without framing them as open questions
- **Impact**: Architect's approach is more actionable for a team — each question has a clear disposition. Analyzer's recommendations are stronger on principle but less structured for decision-making.

## 9. `--verbose` Flag and ClaudeProcess Behavior

- **Architect**: Explicitly calls out `--verbose` stdout interaction as Open Question #1, recommends investigating during P2 but not blocking
- **Analyzer**: References "Claude subprocess integration" as a dependency but doesn't isolate the `--verbose` concern
- **Impact**: Architect surfaces a specific operational risk that could affect sanitizer behavior. Analyzer treats it as general subprocess stability.

## 10. Large File / 10MB Threshold

- **Architect**: Addresses in Open Question #6 — acceptable for now, add 5MB warning log, defer streaming I/O
- **Analyzer**: Lists "large artifact sample near 10MB" as a test resource requirement and includes it in sanitizer test cases
- **Impact**: Analyzer tests the boundary; Architect defers it. Analyzer's approach is more thorough for NFR validation.

## 11. Sanitizer Invocation Frequency Tracking

- **Architect**: Does not mention post-rollout monitoring of sanitizer usage
- **Analyzer**: Recommendation #4 explicitly calls for tracking sanitizer invocation frequency as a signal of upstream prompt/subprocess issues
- **Impact**: Analyzer's recommendation provides a feedback loop for long-term reliability assessment that Architect omits.

## 12. Observability Section

- **Architect**: Logging mentioned in P2 implementation but no dedicated observability strategy
- **Analyzer**: Includes an explicit "Observability checks" subsection in validation (review logs, confirm sanitation-only-when-needed, distinguish LLM vs executor/gate issues)
- **Impact**: Analyzer's approach supports operational debugging after release. Architect focuses on correctness at release time.

# Areas Where One Variant Is Clearly Stronger

**Architect is stronger in:**
- **Conciseness and actionability** — 4 phases, specific test counts, concrete hour estimates make this immediately executable
- **Open questions disposition** — Each ambiguity has an explicit recommendation (defer/investigate/not-an-issue)
- **Parallelization callout** — Explicitly states `P2 ∥ P3` with a visual recommended execution order
- **Architectural risk note** — The P1 cross-pipeline regression commentary is well-placed and specific

**Analyzer is stronger in:**
- **Scope verification** — Phase 0 prevents implementing against wrong assumptions
- **Release readiness** — Phase 5 provides formal E2E validation with release decision gate
- **Risk depth** — Additional risk (field ownership) and validation evidence per risk
- **Post-release operability** — Sanitizer frequency tracking and observability checks
- **Test strategy flexibility** — Category-based testing adapts to discovered edge cases
- **Defense-in-depth articulation** — More explicit about why each layer exists independently

# Areas Requiring Debate to Resolve

1. **Effort estimates (7–11h vs 3.5–4.5 days)**: The 3–4x gap needs reconciliation. Is this a solo sprint or a team effort? The answer determines which estimate is appropriate.

2. **Phase 0 necessity**: Is a formal baseline analysis phase warranted given the spec already identifies the 4 files and root causes? Or does jumping straight to P1 carry acceptable risk?

3. **Phase 5 as separate phase vs integrated validation**: Should E2E validation be a distinct milestone with its own time allocation, or is it sufficiently covered by per-phase validation gates?

4. **Test specification style**: Fixed counts (Architect: 20 cases) vs flexible categories (Analyzer: adapt to discovery). Which approach better serves a reliability-focused release?

5. **Post-release monitoring scope**: Should sanitizer invocation tracking and observability be in-scope for this release or deferred to operational runbooks?
