# Agent 4: Retrospective ↔ Merged Spec Diagnostic Analysis

**Sources analyzed**:
- `v2.07-sprint-retrospective-consolidated.md` — Post-sprint retrospective for v2.07-tasklist-v1
- `merged-spec.md` — v2.08 Roadmap CLI merged specification (v1.1)

**Scope**: Diagnostic only. No fix proposals.

---

## 1. Top 3 Theories for Why Bugs Survive the Workflow Despite Planning Rigor

### Theory 1: Validation Theater — Structural Checks Substitute for Behavioral Verification

The retrospective explicitly identified the most significant gap: **"No End-to-End Invocation Test"** (§4.1). The sprint passed 38/39 tasks at a 97.4% rate, yet no one ever typed the actual user command (`/sc:tasklist @roadmap.md`) to see if it worked end-to-end. The merged spec then replicates this exact pattern — it defines 7 acceptance criteria (AC-01 through AC-07), but AC-02 (the full pipeline test) is explicitly noted as "validated manually" and excluded from the automated test architecture (§13.6: "Not in v1 scope — AC-02 validated manually"). The most important test — does the thing actually work? — is deferred in both releases.

The pipeline's gate system (`gate_passed()`) checks file existence, line counts, and YAML frontmatter fields. These are necessary but insufficient. A file can have perfect frontmatter and correct line counts while containing completely fabricated content. The spec acknowledges this obliquely with the "no circular self-validation" principle (§1), but then has no mechanism for actually validating *content quality* — it merely validates *content structure*. The semantic checks added (§4, STRICT tier) check for heading gaps and cross-reference resolution, but these are formatting checks, not correctness checks.

**Evidence**:
- Retrospective §4.1: "Phase 4 validated artifacts structurally but never demonstrated a user typing `/sc:tasklist @roadmap.md` and observing the full command-to-skill-to-output pipeline."
- Retrospective §2.2: 6 of 11 Acceptance Criteria marked "PARTIALLY MET" — all sharing the gap of "validated at the design/structure level but lack an observed end-to-end invocation trace."
- Merged spec §13.6 Test Architecture: "Full pipeline E2E | Integration (optional) | … Not in v1 scope — AC-02 validated manually."

### Theory 2: The "Noted-But-Not-Prevented" Pattern — Retrospective Findings Become Spec Prose Instead of Structural Constraints

The retrospective identified 7 sprint runner defects (§5), 3 immediate action items (§8), and 5 process improvements (§8 Backlog). The merged spec was written *the day before* the retrospective was finalized, so by timeline it could not have incorporated these findings. But the deeper issue is structural: the workflow has no mechanism to transform retrospective findings into enforceable constraints in subsequent specs.

For example, the retrospective found that "PARTIAL status [is] silently promoted to PASS" (§5, Finding #1, rated P0). The merged spec then designs a `StepStatus` enum with PASS, FAIL, TIMEOUT, SKIPPED, CANCELLED, and PENDING — but no PARTIAL status. The exact defect was documented, rated highest priority, and then the next spec reproduced the same status-fidelity gap by omitting a PARTIAL state from its own pipeline model.

Similarly, the retrospective found that `files_changed` was always 0 due to stream-json incompatibility (§5, Finding #2, P1). The merged spec's `StepResult` dataclass has no `files_changed` field at all — the telemetry gap was identified and then repeated by omission.

**Evidence**:
- Retrospective §5, Finding #1: "PARTIAL status silently promoted to PASS" (P0)
- Merged spec §3.2: `StepStatus` enum has PASS|FAIL|TIMEOUT|SKIPPED|CANCELLED|PENDING — no PARTIAL
- Retrospective §5, Finding #2: "`files_changed` always 0 (stream-json incompatible)" (P1)
- Merged spec §3.2 `StepResult`: no `files_changed` or artifact-tracking field

### Theory 3: Specification Completeness Masks Implementation Risk — The More Detailed the Spec, the More Confident the Agent, Regardless of Actual Feasibility

The merged spec is extraordinarily detailed: 13 sections, full dataclass definitions, thread concurrency models, test architecture, prompt builder signatures, state file JSON schemas, and a complete field allocation table. This level of detail creates a false sense of completeness. The spec describes *what should exist* in exhaustive detail but provides no mechanism to verify that the described components can actually be integrated without regression.

The retrospective hints at this: the sprint achieved "100% quality scores, zero algorithm drift" on structural checks, but the single failure (T03.08) was a pre-existing systemic bug in `install_skills.py` that none of the extensive planning had detected. The risk register predicted 10 risks and missed 2 "surprise risks" — pre-existing lint failures and stale pipx cache. Both were environmental/integration issues invisible to spec-level analysis.

The merged spec's migration strategy (§12) has step 7: "Run `uv run pytest tests/sprint/` — all tests must pass before proceeding to roadmap/ work." But it provides no fallback if they don't pass, no pre-migration characterization test strategy, and no guidance on what constitutes a "passing" migration versus one that merely doesn't crash. The confidence expressed in the test architecture (§13.6: "All sprint test files passing at extraction start are not modified during pipeline/ migration") assumes a clean baseline that the retrospective showed doesn't exist.

**Evidence**:
- Retrospective §2.4: 2 "surprise risks (not in register)" — pre-existing lint failures, stale pipx cache
- Retrospective §4.4: "Two pre-existing issues cause `make lint-architecture` and `make verify-sync` to exit non-zero"
- Merged spec §12 step 7: "Run `uv run pytest tests/sprint/` — all tests must pass before proceeding" (no contingency)
- Merged spec §13.6: "Sprint test stability guarantee: All sprint test files passing at extraction start are not modified" (assumes clean state the retro showed is absent)

---

## 2. Blind Spots Identified

### 2.1 No Environmental Pre-Flight in the Workflow

Neither the retrospective's action items nor the merged spec include an environmental pre-flight step. The retrospective found "pre-existing lint failures" and "stale pipx cache" as surprise risks (§2.4), and Action Item #9 in the backlog proposes a "Pre-flight baseline scan for known failures." The merged spec does not include any pre-flight validation step. The pipeline launches directly into the `extract` step with no verification that the environment (installed packages, clean lint, passing existing tests) is ready.

### 2.2 No Integration Smoke Test Between Migration and New Feature

The merged spec §12 describes an 8-step implementation sequence: steps 1-6 are pipeline extraction and sprint migration, step 7 is "run sprint tests," and step 8 is "Build roadmap/ on top of the now-stable pipeline/ base." There is no step between 7 and 8 to verify that the extracted `pipeline/` module works *independently* — only that sprint still works *through* it. If `pipeline/executor.py`'s `execute_pipeline()` has a bug that sprint's `sprint_run_step` accidentally works around, roadmap will discover it only when roadmap-specific execution starts.

### 2.3 The Workflow Has No Mechanism to Detect "Acknowledged But Not Addressed"

The retrospective produces findings. The spec is written. But nothing in the workflow verifies that retrospective findings appear as constraints, tests, or explicit deferrals in the spec. There is no traceability from retrospective → spec requirement. The retrospective's action items (§8) assign owners ("Backend," "QA," "Maintenance") but these are role labels, not tracked commitments. No issue tracker, no PR linking, no blocking dependency.

### 2.4 Content Quality is Systematically Unverifiable

The merged spec's §1 correctly identifies that "Claude controls its own workflow" is the root cause of fabrication risk. The solution — external conductor with file-on-disk gates — addresses *sequencing fabrication* (skipping steps) but not *content fabrication* (producing plausible but incorrect output within a step). The gate system cannot detect if a roadmap variant is high-quality or garbage, only that it has the right metadata structure. The spec's §11 Deferred Features table lists "Content quality heuristics for input" as "Rejected per tasklist debate outcomes" — meaning the workflow has consciously decided it cannot verify content quality, but hasn't compensated with any alternative.

---

## 3. Confidence vs Reality Gaps

### 3.1 Scorecard Confidence vs Actual Validation Depth

The retrospective reports impressive numbers: 97.4% pass rate, 273/273 quality checks, 100% traceability. But these numbers measure *process execution fidelity*, not *output correctness*. The 6 "PARTIALLY MET" acceptance criteria (§2.2) are described with a neutral framing ("share a common gap"), but this gap — no end-to-end invocation — is fundamental. A 97.4% number is misleading when the 2.6% gap (one failure) was a pre-existing bug and the actual functional validation gap (no e2e test) isn't counted as a failure at all.

**Evidence**:
- Retrospective §2.1: "38 Passed (97.4%)" — but §2.2 shows 6/11 AC and 5/13 SC only PARTIALLY MET
- Retrospective §9 overall grade: "B+" — generous given that the most critical validation (e2e invocation) was never performed

### 3.2 Risk Register Accuracy vs Predictive Value

The retrospective reports the risk register predicted 8 of 10 risks correctly "did not materialize." This is framed as evidence of good risk assessment. But predicting that risks *won't* happen doesn't validate the register — it means those items were either non-risks or lucky. The 2 surprise risks (pre-existing failures, stale cache) — the ones that actually caused problems — were not predicted. The register's predictive value for *actual* issues was 0/2.

**Evidence**:
- Retrospective §2.4: "Predicted correctly (did not materialize): 8" — framed as success
- Retrospective §2.4: "Surprise risks (not in register): 2" — both caused real impact

### 3.3 "Sprint Runner Works" vs Telemetry Reality

The retrospective §3.1 declares "Sprint Runner Works" as the first "What Went Well" item. Yet §4.3 immediately documents 3 telemetry inaccuracies including a P0 (phase status misreported) and a P1 (files_changed always 0). The sprint runner "works" in the sense that it doesn't crash, but it misreports its own state — the exact failure mode the merged spec's conductor is designed to prevent. The confidence in "it works" is at odds with "it lies about its own results."

**Evidence**:
- Retrospective §3.1: "The core orchestration loop executed 39 tasks across 4 phases without crashes, timeouts, or stuck processes."
- Retrospective §4.3: "Phase 3 status: `'pass'` (should be `'partial'`)" — P0 severity

### 3.4 Spec Completeness vs Implementation Coverage

The merged spec provides 15 functional requirements, 7 non-functional requirements, and 7 acceptance criteria. The test architecture (§13.6) maps each to specific test files. But the test category table reveals that the highest-value tests — E2E pipeline tests — are explicitly "Not in v1 scope." The spec is 100% specified and approximately 80% tested, with the untested 20% being the integration layer where bugs actually live. The gap between "fully specified" and "fully verified" is invisible from within the spec itself.

**Evidence**:
- Merged spec §10: 7 Acceptance Criteria defined
- Merged spec §13.6: "Full pipeline E2E | Integration (optional) | … Not in v1 scope"
- Merged spec §13.6 Sprint regression: "All existing mocks/fixtures unchanged" — testing migration by not changing tests

---

## 4. Evidence Citations

### From Retrospective

| Citation | Section | Supports |
|----------|---------|----------|
| "Phase 4 validated artifacts structurally but never demonstrated a user typing `/sc:tasklist @roadmap.md` and observing the full command-to-skill-to-output pipeline." | §4.1 | Theory 1 (validation theater) |
| "PARTIAL status silently promoted to PASS" | §5, Finding #1 | Theory 2 (noted-not-prevented); the exact defect class recurs in the next spec |
| "`files_changed` always 0 (stream-json incompatible)" | §5, Finding #2 | Theory 2; telemetry gap not addressed in merged spec |
| "Predicted correctly (did not materialize): 8 … Surprise risks (not in register): 2" | §2.4 | Gap 3.2 (risk register accuracy illusion) |
| "The core orchestration loop executed 39 tasks across 4 phases without crashes, timeouts, or stuck processes." | §3.1 | Gap 3.3 ("works" vs "lies about results") |
| "Two pre-existing issues cause `make lint-architecture` and `make verify-sync` to exit non-zero" | §4.4 | Blind spot 2.1 (no pre-flight); Theory 3 (environmental risk) |
| "~85-90% of adversarial conclusions were incorporated. Notable omissions: Strategy 2's 6-field structured error format was simplified to 2-field" | §4.5 | Theory 2 pattern; adversarial findings partially incorporated |
| "No criterion was NOT MET. The PARTIALLY MET items share a common gap" | §2.2 | Gap 3.1 (scorecard confidence); reframing partial as not-failed |

### From Merged Spec

| Citation | Section | Supports |
|----------|---------|----------|
| "Not in v1 scope — AC-02 validated manually." | §13.6 | Theory 1; E2E test deferred again |
| `StepStatus`: "PASS \| FAIL \| TIMEOUT \| SKIPPED" (later adds CANCELLED, PENDING) — no PARTIAL | §3.2 | Theory 2; retro's P0 finding not structurally prevented |
| "Gate validation is tier-proportional … STRICT: all STANDARD checks + semantic checks" | §3.3 | Theory 1; even STRICT tier only checks structure, not content |
| "Content quality heuristics for input … rejected per tasklist debate outcomes" | §11 | Blind spot 2.4; content quality consciously abandoned |
| "Run `uv run pytest tests/sprint/` — all tests must pass before proceeding to roadmap/ work" | §12, step 7 | Theory 3; assumes clean baseline retro showed doesn't exist |
| "All sprint test files passing at extraction start are not modified during pipeline/ migration" | §13.6 | Theory 3; stability guarantee based on assumption, not verification |
| "The conductor never invokes Claude to judge Claude's output" | §1 | Correct principle, but creates a verification vacuum for content quality (Blind spot 2.4) |
| "Claude cannot advance to step N+1 because the CLI hasn't issued that prompt yet. Fabrication becomes impossible without writing the required output files." | §1 | Addresses *sequencing* fabrication only; content fabrication remains possible |

---

## 5. Cross-Cutting Observation: The Retrospective-to-Spec Gap Is Structural

The v2.07 retrospective was dated 2026-03-05. The merged spec is dated 2026-03-04. The spec *predates* the retrospective — meaning the retrospective findings could not have been incorporated by timeline. This is not a criticism of either document in isolation, but it reveals a structural workflow gap: there is no feedback loop where retrospective findings become blocking requirements for the next spec. The retrospective produces action items (§8), the next spec is already written, and the action items become backlog entries that may or may not be addressed in a future release.

This means every release re-discovers some version of the same issues because the discovery happens *after* the next release is already specified. The workflow plans forward but learns backward, and nothing connects the two.
