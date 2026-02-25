# v2.01 Architecture Refactor: Extraction from Master Traceability Matrix

**Source:** `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/context/master-traceability.md`
**Extracted:** 2026-02-24
**Purpose:** Isolate systemic architectural patterns, cross-cutting bugs, and root-cause indicators relevant to the v2.01 architectural refactor. Exclude v2.02-specific roadmap sprint artifacts.

---

## 1. Consolidated Bug List -- v2.01 Relevance Classification

### v2.01-RELEVANT (Systemic / Architectural)

| Bug ID | Severity | Summary | Why v2.01 |
|--------|----------|---------|-----------|
| **BUG-001** | HIGH | `allowed-tools` gap: 4 of 5 commands missing `Skill` in frontmatter after adding `## Activation` sections | **ROOT CAUSE INDICATOR.** The architecture migration added Activation sections to all 5 commands but only wired `Skill` into `allowed-tools` for 1 of 5. This is a systemic enforcement gap -- the policy defined the requirement, the migration executed the visible part (Activation section), but the invisible prerequisite (frontmatter update) was missed in 4/5 cases. This pattern -- "visible instruction followed, invisible prerequisite skipped" -- is a core v2.01 problem. |
| **BUG-004** | MEDIUM | Architecture policy document duplication (`docs/architecture/command-skill-policy.md` vs `src/superclaude/ARCHITECTURE.md`) with no canonical authority, no symlink, no sync target | **Systemic.** Canonical source ambiguity is an architectural concern. Any framework that has two identical copies of a governing document with no synchronization mechanism will drift. This is a DRY violation at the governance level. |
| **BUG-005** | MEDIUM | Roadmap SKILL.md Wave 0 step 5 references stale path (`sc-adversarial/` instead of `sc-adversarial-protocol/`) | **Systemic.** Stale internal cross-references within executable specs cause silent failures. The rename migration updated directory names and frontmatter but missed in-body path references. This reveals that path references embedded in prose/instructions are invisible to structural migration tools. |
| **BUG-006** | LOW | `make lint-architecture` implements only 6 of 10 policy-specified CI checks | **Systemic enforcement gap.** Policy defines enforcement; build system partially implements. The gap between spec and enforcement is itself a v2.01 concern -- how do we ensure that policy specifications are fully implemented? |
| **BUG-009** | LOW | Wave 2 Step 3e inlines return contract routing instead of delegating to ref section, diverging from Wave 1A pattern | **Architectural consistency.** Pattern inconsistency within the same skill file (some steps delegate to refs, some inline) creates cognitive load and maintenance burden. v2.01 should establish a consistent delegation pattern. |

### v2.02-SPECIFIC (Sprint / Roadmap Task Artifacts)

| Bug ID | Severity | Summary | Why v2.02 |
|--------|----------|---------|-----------|
| **BUG-002** | MEDIUM | Tasklist files reference old directory names (`sc-adversarial/` vs `sc-adversarial-protocol/`) | Specific to the v2.02 sprint tasklist files. The stale references are in `.dev/releases/` planning documents, not framework source. |
| **BUG-003** | MEDIUM | 24 of 25 dev artifacts use pre-rename paths | Historical sprint artifacts. These are records of state-at-time-of-creation. Not a systemic framework issue. |
| **BUG-007** | LOW | Checkpoint artifact existence unverified | Sprint hygiene issue. Specific to the v2.02 evidence/artifact directory structure. |
| **BUG-008** | LOW | Return contract field count mismatch (resolved in spec-v2) | Already resolved in v2.02 spec iteration. Historical inconsistency in sprint artifacts. |
| **BUG-010** | LOW | Sprint variant decision (TOOL_NOT_AVAILABLE) may be environment-dependent | Sprint execution concern. The decision methodology is relevant (see Section 6 below), but the specific decision is v2.02-scoped. |

---

## 2. Cross-Category Dependency Model (Reusable Pattern)

The traceability matrix reveals a 4-layer dependency chain that is generalizable to v2.01:

```
LAYER 1: ARCHITECTURE POLICY (Governance)
    Defines rules, naming conventions, size limits, CI enforcement specs
    |
    v
LAYER 2: DESIGN ARTIFACTS (Design Decisions)
    Approaches, debates, scoring, specifications
    |
    v
LAYER 3: EXECUTION PLANNING (Sprint/Task Structure)
    Tasks, phases, gates, checkpoints, evidence collection
    |
    v
LAYER 4: FRAMEWORK CHANGES (Actual Source Code)
    File renames, content edits, build system updates, sync operations
```

### Key Architectural Insight

The dependency flows ONE WAY (top-down), but **bugs propagate BOTTOM-UP**:
- A Layer 4 bug (BUG-001: missing `Skill` in `allowed-tools`) reveals a Layer 1 gap (policy specified Activation sections but did not explicitly require `allowed-tools` update as a co-requisite).
- A Layer 4 bug (BUG-005: stale path in SKILL.md body) reveals a Layer 3 gap (migration checklist did not include in-body path references).

**v2.01 Implication:** The architecture refactor must ensure that Layer 1 policies include explicit co-requisite checklists, and Layer 3 migration procedures include "invisible prerequisite" scanning.

### Linkage Pattern (Template)

| Governance Decision | Required Co-Requisite | Framework Change | Verification Method |
|--------------------|-----------------------|------------------|---------------------|
| `-protocol` naming convention | Frontmatter `name` field update | Directory rename + SKILL.md edit | `grep` on frontmatter |
| `## Activation` section in commands | `Skill` in `allowed-tools` frontmatter | Command file edit (2 locations: src + .claude) | `grep` on frontmatter |
| 150-line command cap | Protocol content extracted to skill | Command rewrite + skill expansion | `wc -l` check |
| CI enforcement spec | Make target implementation | Makefile additions | `make lint-architecture` execution |

---

## 3. Unresolved Items -- Architectural (v2.01-Relevant)

Filtered from Section 5 to exclude sprint-specific task completions.

| Item | Priority | Architectural Relevance |
|------|----------|------------------------|
| `make lint-architecture` incomplete (6/10 checks) | HIGH | Enforcement gap. Policy without enforcement is suggestion. v2.01 must define the enforcement completeness standard. |
| `claude -p` Tier 2 ref loader | HIGH | Fundamental to the 3-tier loading model. Without this, Tier 2 (ref files) cannot be loaded on-demand. The entire architectural model is incomplete without it. |
| Cross-skill invocation patterns | HIGH | How skills invoke other skills is THE core architectural question. The v2.02 sprint discovered that the Skill tool returns TOOL_NOT_AVAILABLE -- meaning the designed invocation path does not work. v2.01 must resolve this. |
| 6 oversized command splits | MEDIUM | Commands exceeding the 150-line cap remain. The policy is defined but not fully enforced. |
| Architecture policy deduplication | LOW | Two identical copies with no sync mechanism. Governance hygiene. |
| Missing `refs/headless-invocation.md` | MEDIUM | Referenced in 4 design documents but never created. Infrastructure file gap. |
| Missing probe fixtures and schema files | LOW | Test infrastructure gap. Referenced in specifications but never materialized. |

---

## 4. Change Narrative Structure (Template for v2.01)

The traceability document's Section 7 provides a reusable narrative structure:

```
### Prologue: The Problem (Pre-Work)
- State the architectural problem being solved
- Identify root causes (not symptoms)
- Quantify the impact (e.g., "567-line command file consuming tokens on every invocation")

### Act 1: Policy/Specification (Day 1)
- Document the architectural decisions
- Enumerate specific rules with enforcement mechanisms
- Identify migration phases

### Act 2: Design Work (Concurrent)
- Alternative approaches with trade-off analysis
- Adversarial review / debate process
- Specification iteration with panel review

### Act 3: Probe / Validation (Phase 1)
- Test fundamental assumptions BEFORE building
- Record consequential decisions with full rationale
- Gate clearance for subsequent phases

### Act N: Implementation (Phase N)
- Specific changes with verification
- Bug discovery during execution
- Divergence documentation

### Epilogue: Current State
- Completed items with metrics
- In-progress items with blocking factors
- Unresolved bugs ranked by severity
- Key metrics (files affected, lines changed, artifacts produced)
```

---

## 5. Task-to-File Matrix Pattern (Reusable for v2.01)

The matrix structure maps each task to its framework file changes. For v2.01, this pattern should be adopted:

| Task | Description | Compliance Tier | Files Changed | Verification Method | Status |
|------|-------------|-----------------|---------------|---------------------|--------|
| (task ID) | (what) | EXEMPT/LIGHT/STANDARD/STRICT | (specific file paths) | (how verified) | (state) |

### Key Design Decisions from the Source Pattern

1. **Compliance tier per task**: Each task has an explicit tier (EXEMPT, LIGHT, STANDARD, STRICT) that determines verification rigor.
2. **"None" is a valid change**: Some tasks produce evidence/decisions but change zero framework files (T01.01, T01.02, T01.03). This is legitimate and should be tracked.
3. **Parallel (non-tasklist) changes**: Architecture migrations that happen concurrently with sprint tasks but are NOT tracked in the tasklist need their own section. The source document's "Parallel Architecture Changes" table captures this.
4. **Mirror files**: Every command change affects 2 files (`src/superclaude/commands/` + `.claude/commands/sc/`). The matrix must track both.

---

## 6. Verification Methodology Patterns (Reusable)

### Evidence Structure (Two-Tier)

- **Tier 1 (result.md)**: 5-6 lines. Binary result, validation method, artifact pointer.
- **Tier 2 (artifact)**: Full detailed evidence with specifications, checklists, or policy rationale.

### Verification Methods Used

| Method | When Used | Confidence |
|--------|-----------|------------|
| `grep` on specific file | Frontmatter field verification (allowed-tools, name) | HIGH -- deterministic |
| Structural audit (N-point checklist) | Complex implementation verification (T02.03: 8-point) | HIGH -- comprehensive |
| Adversarial review | Design quality (panel review: 27 findings) | MEDIUM-HIGH -- depends on reviewer quality |
| Manual runtime probe | Tool availability (T01.01: Skill tool) | DEFINITIVE for the tested environment |
| File existence check | Prerequisite validation (T01.02: 6 checks) | HIGH -- deterministic |
| Policy reasoning record | Decision documentation (T01.03) | N/A -- captures rationale, not correctness |

### Decision Artifact Pattern (D-series)

Each decision gets a numbered artifact (D-0001 through D-NNNN) with:
- Source task
- Decision content
- Framework changes driven
- Implementation status (RECORDED / APPLIED / VERIFIED / NOT STARTED)

---

## 7. Systemic Quality Gaps

### Missing Tests / Enforcement

| Gap | Description | v2.01 Relevance |
|-----|-------------|-----------------|
| No automated `allowed-tools` consistency check | BUG-001 was found by manual agent review, not CI. There is no `make` target that verifies all commands with `## Activation` sections also have `Skill` in `allowed-tools`. | HIGH -- v2.01 should add this to `lint-architecture` |
| No in-body path reference scanner | BUG-005 was found manually. When directories are renamed, the migration updates directory names and frontmatter but does NOT scan for path references embedded in markdown prose. | HIGH -- v2.01 should add a post-rename path reference check |
| No canonical source enforcement | BUG-004 exists because there is no mechanism to prevent or detect document duplication. | MEDIUM -- v2.01 should establish canonical source policy |
| 4 of 10 CI checks unimplemented | BUG-006. Policy without enforcement degrades to suggestion. | HIGH -- v2.01 should complete or document deferrals |
| No cross-file consistency validation | The Activation section in a command references a skill by name, but nothing validates that the referenced skill directory actually exists. | HIGH -- add to lint-architecture |
| No return contract schema validation | BUG-008 showed field count mismatch between design docs and implementation. No schema enforcement exists. | MEDIUM -- if return contracts are used in v2.01 |

### Pattern: "Visible Instruction Followed, Invisible Prerequisite Skipped"

This is the most important systemic pattern extracted from the traceability matrix:

1. **BUG-001**: The `## Activation` section (visible) was added to all 5 commands. The `allowed-tools` frontmatter update (invisible prerequisite) was done for only 1 of 5.
2. **BUG-005**: Directory renames (visible) were completed. In-body path references (invisible) were not updated.
3. **BUG-006**: CI check policy (visible) was written. Implementation (invisible) was only 60% complete.

**Root Cause Hypothesis:** When instructions say "add X," agents execute the explicit instruction but do not identify implicit co-requisites. The instruction "add an Activation section" does not say "and also update allowed-tools" -- so the agent adds the section and considers the task complete.

---

## 8. Root Cause Indicators: Why Agents Don't Follow Instructions

This is the central v2.01 problem. The traceability matrix provides several data points:

### 8.1 The Explicit vs. Implicit Gap

**Evidence:** BUG-001 (4/5 commands missing `Skill` in allowed-tools)

The architecture policy document (`command-skill-policy.md`) defined the Activation section pattern. It did NOT explicitly state: "When adding an Activation section that uses `Skill`, you must also add `Skill` to the `allowed-tools` frontmatter." The co-requisite was implicit.

**Lesson for v2.01:** Every instruction must make ALL co-requisites explicit. Never assume agents will infer prerequisites.

### 8.2 The "One Example Generalizes" Failure

**Evidence:** T02.01 added `Skill` to `roadmap.md`'s allowed-tools. T02.02 added `Skill` to `sc-roadmap-protocol/SKILL.md`'s allowed-tools. But the migration of the OTHER 4 commands did NOT receive analogous tasks.

The sprint explicitly tasked the `roadmap` command's wiring. It did NOT create parallel tasks for the other 4 commands' `allowed-tools` updates. The migration assumed that renaming directories and adding Activation sections was sufficient.

**Lesson for v2.01:** When a pattern applies to N items, create N explicit tasks (or one explicit "apply to all N" task with a checklist). Never assume one example will be generalized.

### 8.3 The Structural vs. Semantic Migration Gap

**Evidence:** BUG-005 (stale path in SKILL.md body text)

Structural migrations (directory renames, frontmatter updates) are deterministic and greppable. Semantic references (path mentioned in a sentence of prose) are invisible to structural tooling.

**Lesson for v2.01:** Post-migration validation must include semantic scanning -- grep for ALL old names/paths across ALL files, not just the structurally affected ones.

### 8.4 The Policy-Enforcement Completeness Gap

**Evidence:** BUG-006 (6/10 CI checks implemented)

A policy document specifying 10 checks was authored. The implementation covered 6. No record exists of which 4 were deferred or why.

**Lesson for v2.01:** Policy specifications must include an implementation tracker. Each item in a policy should have a corresponding "implemented: yes/no/deferred (reason)" field.

### 8.5 The Context Window Problem

**Evidence:** From the Change Narrative (Section 7, Prologue)

> "every command invocation auto-loaded the entire protocol into Claude's context window, consuming tokens even when the protocol was not needed"

> "when command summaries diverged from skill specifications, Claude would hallucinate protocol steps rather than failing explicitly"

This reveals TWO root causes for instruction non-compliance:
1. **Token competition:** When too much context is loaded, important instructions get diluted.
2. **Divergence-induced hallucination:** When two sources (command summary and skill spec) contain different versions of the same protocol, the agent may synthesize a third version that matches neither.

**Lesson for v2.01:** The 3-tier loading model (command as door, skill as room, ref as drawer) is the architectural response to this problem. v2.01 must ensure this model is fully implemented and enforced, not just specified.

### 8.6 The Skill Tool Re-Entry Block

**Evidence:** From the Change Narrative (Prologue + Act 3)

> "if a skill with the same name as the command was already running, invoking it again would fail"

> "T01.01's probe returned TOOL_NOT_AVAILABLE"

The designed invocation mechanism (Skill tool) does not work as expected. The entire `-protocol` naming convention exists to work around a re-entry block, and even then the tool may not be available.

**Lesson for v2.01:** Architecture must be designed around VERIFIED capabilities, not assumed ones. The probe-first methodology (T01.01) is the right approach -- but the probe should happen BEFORE the architecture policy is written, not after.

### 8.7 Summary: The Five Root Causes

| # | Root Cause | Manifestation | v2.01 Mitigation |
|---|-----------|---------------|------------------|
| 1 | Implicit co-requisites | BUG-001: Activation added, allowed-tools not | Make ALL co-requisites explicit in every instruction |
| 2 | One-example-generalizes assumption | BUG-001: roadmap wired, 4 others not | Create N tasks for N items, or explicit "apply to all" with checklist |
| 3 | Structural-only migration | BUG-005: directory renamed, prose path not | Post-migration semantic grep for all old names |
| 4 | Spec without enforcement tracking | BUG-006: 10 checks specified, 6 built | Implementation tracker per policy item |
| 5 | Context dilution / source divergence | Narrative: hallucinated protocol steps | 3-tier loading model with strict separation |

---

## 9. Reusable Patterns for v2.01 Planning

### 9.1 Pre-Implementation Probe Protocol

Before designing around a capability, PROBE it:
1. Define the capability assumption
2. Execute a minimal test
3. Record the result as a decision artifact
4. Branch the design based on the result (variant selection)

### 9.2 Compliance Tier System

Tasks are classified by risk:
- **EXEMPT**: Read-only, no framework changes
- **LIGHT**: Single-field changes, low risk
- **STANDARD**: Standard implementation
- **STRICT**: Multi-file, security-adjacent, or cross-cutting changes requiring structural audit

The key insight from the source: executable `.md` files should NOT be auto-classified as EXEMPT just because they are markdown. Files that Claude interprets as instructions are functionally code.

### 9.3 Checkpoint Pattern

After each phase:
- Enumerate completed tasks with pass/fail
- List blocking factors for next phase
- Record cumulative decision artifact inventory
- Gate: all tasks must PASS before next phase begins

### 9.4 Adversarial Review Pattern

For significant design decisions:
1. Generate N competing approaches
2. Structured debate with convergence tracking
3. Quantitative + qualitative scoring
4. Base selection with targeted absorptions from runners-up
5. Panel review with findings → specification iteration

### 9.5 Evidence-Based Decision Tracking

Every decision that affects framework changes gets:
- A numbered artifact (D-NNNN)
- Clear provenance (which task produced it)
- Forward traceability (which framework changes it drives)
- Implementation status tracking
