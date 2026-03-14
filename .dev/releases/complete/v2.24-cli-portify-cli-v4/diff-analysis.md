

---
total_diff_points: 14
shared_assumptions_count: 12
---

# Diff Analysis: Opus-Architect vs Haiku-Architect Roadmaps

## 1. Shared Assumptions and Agreements

1. **7-step, 4-phase pipeline** — Both agree on the consolidated step count and phase structure
2. **Synchronous-only execution** — No async/await, explicit prohibition enforced via static checks
3. **Zero modifications to `pipeline/` and `sprint/`** — Strict base-module immutability
4. **18-module structure under `src/superclaude/cli/cli_portify/`** — Both reference DEV-001 as authoritative
5. **Steps 1–2 pure programmatic, Steps 3–7 Claude-assisted** — Same deterministic/model boundary
6. **`PortifyConfig` extends `PipelineConfig`, `PortifyStepResult` extends `StepResult`** — Same type hierarchy
7. **Gate tiers: EXEMPT, STANDARD, STRICT** — Same enforcement model with `tuple[bool, str]` return
8. **Convergence loop with CONVERGED/ESCALATED terminal states** — Same convergence model
9. **TurnLedger budget guards** — Both require pre-launch budget checks
10. **Skill fallback pattern** — Pre-flight check for `/sc:brainstorm` and `/sc:spec-panel`, inline fallback if unavailable
11. **`--dry-run` halts after Step 4** — Same halt point with `skipped` downstream phases
12. **Contract emission on all exit paths** — success, partial, failed, dry_run

## 2. Divergence Points

### D-1: Phase 0 — Architecture Confirmation Phase
- **Opus**: Jumps directly into Phase 1 (Foundation). Open questions listed in Section 7 but not given a dedicated phase.
- **Haiku**: Adds explicit **Phase 0** for resolving spec ambiguities, freezing module layout, and defining artifact contracts before any code.
- **Impact**: Haiku's approach reduces rework risk by front-loading decisions. Opus risks discovering ambiguities mid-implementation. Haiku adds 0.5–1 day upfront but likely saves more downstream.

### D-2: Phase Numbering and Granularity
- **Opus**: 5 phases (Foundation → Analysis & Design → Spec Synthesis → Review & Convergence → Infrastructure)
- **Haiku**: 8 phases (Phase 0–7), splitting infrastructure, UX/resume, and validation into separate phases
- **Impact**: Haiku's finer granularity provides clearer milestone boundaries and exit criteria. Opus bundles infrastructure as a cross-cutting concern, which is more realistic but harder to track.

### D-3: Infrastructure Parallelization Strategy
- **Opus**: Explicitly calls out Phase 5 (Infrastructure) as parallelizable from Phase 2 onward, with a critical path diagram showing the fork.
- **Haiku**: Sequences infrastructure (Phase 3) before content generation (Phase 4), treating subprocess orchestration as a prerequisite rather than parallel track.
- **Impact**: Opus enables faster delivery through parallelism. Haiku's sequencing is safer — subprocess infrastructure must be stable before content steps depend on it. Haiku's ordering is more defensible architecturally.

### D-4: Subprocess Orchestration as Distinct Phase
- **Opus**: Subprocess management (`PortifyProcess`) is introduced within Phase 2 milestones alongside the first Claude-assisted steps.
- **Haiku**: Dedicates an entire **Phase 3** to subprocess orchestration core (process wrapper, monitoring, diagnostics, gate bindings) before any Claude-assisted content steps.
- **Impact**: Haiku's separation produces a testable subprocess platform before depending on it. Opus intermingles infrastructure with first usage, increasing coupling risk.

### D-5: Monitor Signal Vocabulary Resolution
- **Opus**: Lists GAP-008 (NDJSON signal vocabulary) as a blocking open question for Phase 5.
- **Haiku**: Incorporates signal extraction and NDJSON logging within Phase 3 (subprocess core) without calling out the vocabulary as a separate blocking concern.
- **Impact**: Opus is more explicit about the unresolved nature. Haiku assumes resolution during implementation, which could lead to ad-hoc signal design.

### D-6: Resume Semantics Depth
- **Opus**: Lists resume as a Phase 5 milestone with general guidance; lists GAP-005 and F-006 as open questions.
- **Haiku**: Dedicates Phase 6 to resume semantics with explicit work items: resumability matrix, partial file handling, context preservation for review steps.
- **Impact**: Haiku provides more concrete resume design. Opus defers detail, risking late-stage rework.

### D-7: User Review Gate Implementation Detail
- **Opus**: Mentions stderr prompt with `y`/`n` and `USER_REJECTED` status. Includes `--skip-review` flag.
- **Haiku**: Adds TUI pause behavior, explicit UX interaction design, and testability of review gates as Phase 6 work items.
- **Impact**: Haiku treats user interaction as a first-class UX concern. Opus treats it as a simple prompt.

### D-8: Test Strategy Organization
- **Opus**: Provides an **automated validation matrix** (SC-001 through SC-014) mapping criteria to test types with specific validation methods.
- **Haiku**: Organizes testing by layer (unit → integration → compliance → architectural validation) with an evidence package concept.
- **Impact**: Opus's matrix is more traceable — each criterion has a clear test. Haiku's layered approach is more holistic but less precise about what validates what.

### D-9: Timeline Estimates
- **Opus**: Qualitative estimates per phase (Small/Medium/Large) without day counts.
- **Haiku**: Quantitative estimates (0.5–3 days per phase, 10.5–18 days total) with week-by-week cadence.
- **Impact**: Haiku provides actionable scheduling. Opus avoids commitment but offers less planning utility.

### D-10: Team/Role Requirements
- **Opus**: No explicit team roles defined.
- **Haiku**: Defines 4 roles: Architect/lead, Backend/Python implementer, QA engineer, optional UX/TUI contributor.
- **Impact**: Haiku is more realistic for project planning. Opus implicitly assumes a single implementer.

### D-11: Architectural Recommendations Framing
- **Opus**: 6 specific, actionable recommendations (e.g., "build a test harness for Claude subprocess mocking early", "design convergence loop as standalone component").
- **Haiku**: 5 broader principle-level recommendations (e.g., "bias toward explicit state machines", "treat contracts as the real system boundary").
- **Impact**: Opus's recommendations are more implementation-ready. Haiku's are more philosophically grounded. Both valuable, complementary.

### D-12: Failure Classification Taxonomy
- **Opus**: Lists failure types implicitly across risk mitigations.
- **Haiku**: Explicitly enumerates failure classifications in Phase 3: timeout, missing artifact, malformed frontmatter, gate failure, user rejection, budget exhaustion.
- **Impact**: Haiku's explicit taxonomy enables consistent diagnostics. Opus leaves classification emergent.

### D-13: Section Hashing Placement
- **Opus**: Mentions section hashing in Phase 4 (panel-review milestone) as an NFR-008 enforcement.
- **Haiku**: Splits it: utility implementation in Phase 1, enforcement in Phase 5.
- **Impact**: Haiku's approach is better — build the hashing utility early, use it later. Opus co-locates implementation with usage, which works but misses reuse potential.

### D-14: Template Validation Timing
- **Opus**: Recommends gating `release-spec-template.md` at startup (Recommendation #5) but places the actual check in Phase 3 (Step 5).
- **Haiku**: Validates template presence during Phase 1 (startup) or before synthesis, with explicit failure contract.
- **Impact**: Haiku aligns behavior with the principle. Opus states the principle but doesn't embed it in the phase structure.

## 3. Areas Where One Variant is Clearly Stronger

### Opus is stronger in:
- **Validation traceability** — SC-001 through SC-014 matrix is directly testable and auditable
- **Subprocess mocking recommendation** — Explicitly calls for a test harness early, which is critical for development velocity
- **Convergence loop isolation** — Recommendation to extract as standalone testable component is architecturally sound
- **Risk ID specificity** — R-1 through R-9 with clear owner assignments
- **Critical path visualization** — ASCII diagram showing parallelizable Phase 5

### Haiku is stronger in:
- **Phase 0 architecture confirmation** — Prevents ambiguity-driven rework
- **Subprocess platform isolation** — Dedicated phase before first usage reduces coupling
- **Failure classification taxonomy** — Explicit enumeration enables consistent diagnostics
- **Timeline concreteness** — Day estimates and week-by-week cadence enable real planning
- **Resume semantics depth** — Dedicated phase with explicit work items
- **Role definition** — Practical for multi-person execution
- **Section hashing lifecycle** — Build utility early, enforce later
- **State machine framing** — Convergence, review, resume as explicit state machines

## 4. Areas Requiring Debate to Resolve

1. **Infrastructure parallelization vs sequencing** (D-3/D-4): Should subprocess infrastructure be built in parallel with Phase 1 (Opus) or as a prerequisite gate before content steps (Haiku)? Trade-off is speed vs safety. **Recommendation**: Haiku's sequencing is safer for a first implementation; parallelization can be attempted in subsequent releases.

2. **Phase 0 necessity** (D-1): Is a dedicated architecture confirmation phase worth the calendar time? **Recommendation**: Yes — the spec has at least 3 blocking ambiguities (timeout semantics, resume behavior, scoring precision) that will cause rework if discovered during implementation.

3. **Validation approach** (D-8): Matrix-based (Opus) vs layer-based (Haiku) test organization? **Recommendation**: Merge both — use Opus's SC matrix as the traceability index, organized into Haiku's test layers.

4. **Timeline format** (D-9): Qualitative vs quantitative? **Recommendation**: Use Haiku's quantitative estimates with Opus's qualitative sizing as cross-checks. Avoid false precision but provide planning utility.

5. **Signal vocabulary resolution** (D-5): Should NDJSON signal vocabulary be resolved upfront (Opus) or defined during implementation (Haiku)? **Recommendation**: Define a minimal vocabulary upfront (Phase 0), extend during implementation. Blocking on full vocabulary definition is unnecessary, but having no plan risks inconsistency.
