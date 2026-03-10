# SC-ADVERSARIAL-SPEC: Generic Adversarial Debate & Merge Pipeline

## Metadata
- **Version**: 1.0.0
- **Status**: Draft
- **Author**: Brainstorm session (sc:roadmap v2 requirements discovery)
- **Date**: 2026-02-20
- **Dependencies**: None (foundational command)
- **Dependents**: sc:roadmap v2 (multi-spec, multi-roadmap modes)
- **Priority**: P1

---

## 1. Executive Summary

`/sc:adversarial` is a generic, reusable command that implements a structured adversarial debate, comparison, and merge pipeline. It accepts multiple artifacts (files or generated variants), identifies differences and contradictions, orchestrates a structured debate between agents to evaluate strengths and weaknesses, selects the strongest base, produces a refactoring plan to incorporate the best of all versions, and executes that plan to produce a unified output.

**Core Objective**: To verify and validate the accuracy and validity of any statement in generated artifacts, weeding out hallucinations and sycophantic agreement through structured adversarial pressure. The pipeline employs a steelman debate strategy — advocates must first construct the strongest possible version of opposing positions before critiquing them — not to simply determine a winner, but to incorporate the genuine strengths from all sides into a unified version where the weaknesses of each have been addressed and mitigated and the strengths leveraged. The result is an output that is demonstrably more accurate, complete, and robust than any individual input.

**Key Differentiator**: Unlike simple diffing or merging tools, sc:adversarial uses multi-model adversarial reasoning grounded in empirical research showing 10-15% accuracy gains on reasoning tasks and 30%+ reduction in factual errors. It is designed as a generic framework tool that any SuperClaude command can invoke.

---

## 2. Scope

### 2.1 In Scope

- Comparing 2-10 artifacts (files) across any domain (specs, roadmaps, code, documentation)
- Generating variant artifacts from a source using different agent/model configurations
- Structured adversarial debate with configurable depth (1-3 rounds)
- Automated conflict detection and resolution with optional interactive mode
- Base selection with documented rationale
- Refactoring plan generation and execution via dedicated merge agent
- Full process artifact generation for transparency and auditability
- Convergence detection at configurable threshold (default 80%)

### 2.2 Out of Scope

- Executing the merged output (that's the calling command's or user's responsibility)
- Domain-specific validation of merged content (calling command handles this)
- Real-time collaborative editing
- Version control integration (git operations)
- Cost optimization or token budgeting (no constraints per user requirement)

---

## 3. Functional Requirements

### FR-001: Dual Input Modes

The command supports two primary input modes:

**Mode A: Compare existing files**
```bash
/sc:adversarial --compare file1.md,file2.md[,file3.md,...,file10.md]
```
Accepts 2-10 existing files for comparison, debate, and merge.

**Mode B: Generate + compare from source**
```bash
/sc:adversarial --source source.md --generate <type> --agents <agent-spec>[,<agent-spec>,...]
```
Generates variant artifacts from a source file using specified agents, then runs the comparison/debate/merge pipeline on the generated variants.

**Agent specification format** (hybrid model + optional persona + optional instruction):
```
<model>                              # e.g., opus
<model>:<persona>                    # e.g., opus:architect
<model>:<persona>:"<instruction>"    # e.g., opus:architect:"focus on scalability"
```

**Supported models**: Any model available in the environment (opus, sonnet, haiku, or configured aliases).

**Agent count**: 2-10 agents. Minimum 2 required for adversarial comparison.

### FR-002: 5-Step Adversarial Protocol

The core pipeline executes 5 sequential steps. Each step produces a documented artifact.

#### Step 1: Diff Analysis
- **Input**: All variant artifacts
- **Process**: Systematic comparison identifying:
  - Structural differences (organization, section ordering, hierarchy depth)
  - Content differences (requirements coverage, detail level, approach)
  - Contradictions (conflicting recommendations, incompatible approaches)
  - Unique contributions (ideas present in only one variant)
- **Output**: `diff-analysis.md` - organized by category with severity ratings
- **Delegation**: `/sc:analyze` or equivalent analytical agent

#### Step 2: Adversarial Debate
- **Input**: All variants + diff-analysis.md
- **Process**: Structured debate where agents argue for their variant's approach
  - Each variant gets an advocate agent
  - Advocates present strengths of their approach and critique weaknesses of others
  - Rebuttals address criticisms with evidence
  - Debate rounds controlled by `--depth` flag:
    - `quick`: 1 round (advocate statements only)
    - `standard`: 2 rounds (advocate + rebuttal)
    - `deep`: Up to 3 rounds, continuing until 80% alignment or max rounds reached
- **Convergence**: Measured as percentage of diff points where agents agree on the superior approach. Default threshold: 80%.
- **Output**: `debate-transcript.md` - full debate with per-point scoring
- **Delegation**: debate-orchestrator agent coordinates, domain agents participate

#### Step 3: Base Selection (Hybrid Quantitative-Qualitative Scoring)
- **Input**: All variants + debate-transcript.md
- **Process**: Select the strongest overall variant using a two-layer scoring protocol that combines deterministic quantitative metrics (50% weight) with evidence-anchored qualitative assessment (50% weight). See **Appendix A: Scoring Protocol** for the complete algorithm.
  - **Quantitative Layer** (deterministic, fully repeatable):
    - `requirement_coverage`: % of source requirements referenced in the variant (grep-matched against source)
    - `internal_consistency`: 1 - (contradictions found / total claims), detected via structured scan
    - `specificity_ratio`: ratio of concrete statements (numbers, dates, named entities, specific thresholds) to vague statements ("appropriate", "as needed", "properly")
    - `dependency_completeness`: % of referenced items (sections, milestones, components) that are defined elsewhere in the document
    - `section_coverage`: number of top-level sections normalized against the maximum across all variants
    - Formula: `quant_score = (requirement_coverage × 0.30) + (internal_consistency × 0.25) + (specificity_ratio × 0.15) + (dependency_completeness × 0.15) + (section_coverage × 0.15)`
  - **Qualitative Layer** (LLM-assessed via additive binary rubric):
    - Each of 5 dimensions (completeness, correctness, structure, clarity, risk coverage) evaluated against 5 binary criteria (met/not met)
    - Each criterion: 1 point if met, 0 if not. No partial credit.
    - Evidence citation required for every criterion assessment (Claim-Evidence-Verdict)
    - Formula: `qual_score = total_criteria_met / total_criteria_possible`
  - **Final score**: `variant_score = (0.50 × quant_score) + (0.50 × qual_score)`
  - **Tiebreaker**: If two variants score within 5% of each other, debate performance (points won in Step 2) breaks the tie
  - **Position-bias mitigation**: Qualitative evaluation runs twice per variant with different presentation orderings; inconsistent assessments are discarded and re-evaluated
  - Select highest-scoring variant as base
  - Document full scoring breakdown with evidence in output artifact
- **Output**: `base-selection.md` - quantitative metrics, qualitative rubric results, combined scoring matrix, tiebreaker application (if any), and selection rationale with evidence citations
- **Delegation**: debate-orchestrator agent

#### Step 4: Refactoring Plan
- **Input**: Selected base + all other variants + debate-transcript.md
- **Process**: Generate a plan to incorporate strengths from non-base variants into the base
  - For each unique strength in non-base variants (as determined by debate):
    - Describe the improvement
    - Identify where it integrates into the base
    - Assess risk of integration
    - Specify the merge approach
  - For each weakness identified in the base during debate:
    - Describe the issue
    - Reference which non-base variant addresses it better
    - Specify the fix approach
  - Plan is reviewed before execution (auto-approved by default, user-approved with `--interactive`)
- **Output**: `refactor-plan.md` - actionable merge plan with integration points
- **Delegation**: debate-orchestrator agent drafts, reviewed by analytical agent

#### Step 5: Merge Execution
- **Input**: Base variant + refactor-plan.md
- **Process**: Execute the refactoring plan to produce a unified output
  - Apply each planned change to the base document
  - Maintain provenance annotations (which source contributed each section)
  - Validate structural integrity after merge
  - Run consistency check on the final output
- **Output**: Unified merged artifact (filename matches the artifact type, e.g., `roadmap.md`, `spec.md`)
- **Delegation**: merge-executor agent (NEW - dedicated to this task)

### FR-003: Configurable Debate Parameters

| Parameter | Flag | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| Depth | `--depth` | `standard` | quick/standard/deep | Controls debate rounds (1/2/3) |
| Convergence | `--convergence` | `0.80` | 0.50-0.99 | Alignment threshold for deep mode |
| Interactive | `--interactive` | `false` | true/false | User approval at key decision points |
| Output dir | `--output` | Auto-derived | Any path | Where artifacts are written |
| Focus areas | `--focus` | All | Comma-separated | Debate focus (structure,completeness,risk,etc.) |

### FR-004: Interactive Mode

When `--interactive` is specified, the pipeline pauses for user input at:
1. **After diff analysis**: User can highlight priority areas for debate
2. **After debate**: User can override convergence assessment
3. **After base selection**: User can override the selected base
4. **After refactoring plan**: User can modify the plan before execution

Default (non-interactive): All decisions auto-resolved. Rationale documented in artifacts.

### FR-005: Artifact Output Structure

All process artifacts written to a subdirectory of the output location:

```
<output-dir>/
├── <merged-output>.md          # Final unified artifact
└── adversarial/
    ├── variant-1-<agent>.md    # Agent 1's generated variant (Mode B) or input file copy (Mode A)
    ├── variant-2-<agent>.md    # Agent 2's generated variant
    ├── ...                     # Up to 10 variants
    ├── diff-analysis.md        # Step 1 output
    ├── debate-transcript.md    # Step 2 output
    ├── base-selection.md       # Step 3 output
    ├── refactor-plan.md        # Step 4 output
    └── merge-log.md            # Step 5 execution log
```

**Naming conventions for variants**:
- Mode A (compare): `variant-1-original.md`, `variant-2-original.md` (copies of input files)
- Mode B (generate): `variant-1-<model>-<persona>.md`, e.g., `variant-1-opus-architect.md`

### FR-006: Error Handling

| Scenario | Behavior |
|----------|----------|
| Agent fails to generate variant | Retry once, then proceed with N-1 variants (minimum 2 required) |
| Variants too similar (<10% diff) | Skip debate, select either as base, log "variants substantially identical" |
| Variants too divergent (no convergence after max rounds) | Force-select by score, document non-convergence, flag for user review |
| Merge execution produces invalid output | Preserve all artifacts, flag failure, provide refactor-plan.md for manual execution |
| Single variant remains after failures | Abort adversarial process, return the surviving variant as-is with warning |

### FR-007: Return Contract

When invoked by another command (e.g., sc:roadmap), sc:adversarial returns:
- Path to the merged output file
- Final convergence score
- Path to the adversarial/ artifacts directory
- Success/partial/failed status
- List of unresolved conflicts (if any)

---

## 4. Non-Functional Requirements

### NFR-001: Performance
- Parallel variant generation (Mode B): All agents run concurrently
- Debate rounds: Advocate statements generated in parallel, rebuttals sequential
- No token or cost constraints on agent operations
- Target: Complete standard-depth pipeline in <5 minutes for typical artifacts

### NFR-002: Transparency
- Every decision documented with rationale in artifacts
- Provenance tracking: merged output annotates which source contributed each section
- Full debate transcript preserved regardless of outcome
- No "black box" decisions - all scoring visible

### NFR-003: Determinism
- Same inputs + same agents + same depth → same process (debate content may vary due to model non-determinism, but the protocol is deterministic)
- Scoring algorithms use explicit formulas, not subjective assessment
- Tie-breaking rules documented and consistent

### NFR-004: Extensibility
- Generic protocol works with any artifact type
- New agent types can participate without protocol changes
- Focus areas are extensible (callers can define custom focus dimensions)
- Debate protocol can be extended with custom scoring rubrics via `--rubric` flag (future)

---

## 5. Agent Definitions

### 5.1 debate-orchestrator (NEW)

**Purpose**: Coordinates the entire adversarial pipeline. Does NOT participate in debates - it manages the process.

**Responsibilities**:
- Parse input mode and validate parameters
- Dispatch variant generation (Mode B) in parallel
- Coordinate the 5-step protocol
- Track convergence scoring across debate rounds
- Make base selection using scoring algorithm
- Hand off to merge-executor for step 5
- Compile final return contract

**Model preference**: Highest-capability model available (opus preferred) - the orchestrator needs strong reasoning for scoring and coordination.

**Tools**: Task (for delegation), Read, Write, Glob, Grep, Bash (for file operations)

**Does NOT**:
- Generate variants (delegates to specified agents)
- Participate in debates (delegates to advocate agents)
- Execute merges (delegates to merge-executor)

### 5.2 merge-executor (NEW)

**Purpose**: Executes refactoring plans to produce unified merged artifacts. Specialist in document integration.

**Responsibilities**:
- Read the base variant and refactoring plan
- Apply each planned change methodically
- Maintain structural integrity during merge
- Add provenance annotations
- Validate the merged output for consistency
- Produce merge-log.md documenting each applied change

**Model preference**: High-capability model (opus or sonnet) - needs strong writing and structural reasoning.

**Tools**: Read, Write, Edit, Grep (for content verification)

**Does NOT**:
- Make strategic decisions about what to merge (follows the plan)
- Override the refactoring plan without escalation
- Participate in debates or scoring

### 5.3 Advocate Agents (Dynamic)

These are NOT pre-defined agents. They are instantiated dynamically from the `--agents` specification. Each advocate:
- Receives their variant + all other variants + diff-analysis.md
- Argues for their variant's strengths in the specified focus areas
- Critiques weaknesses in other variants with evidence
- Responds to rebuttals in subsequent rounds

The advocate's behavior is shaped by:
- The model specified (opus, sonnet, haiku)
- The persona specified (architect, security, analyzer, etc.)
- The custom instruction (if provided)

---

## 6. Command Interface

### 6.1 Usage

```bash
# Mode A: Compare existing files
/sc:adversarial --compare file1.md,file2.md[,...,fileN.md] [options]

# Mode B: Generate + compare
/sc:adversarial --source <file> --generate <type> --agents <spec>[,...] [options]
```

### 6.2 Flags

| Flag | Short | Required | Default | Description |
|------|-------|----------|---------|-------------|
| `--compare` | `-c` | Mode A | - | Comma-separated file paths (2-10) |
| `--source` | `-s` | Mode B | - | Source file for variant generation |
| `--generate` | `-g` | Mode B | - | Type of artifact to generate (roadmap, spec, etc.) |
| `--agents` | `-a` | Mode B | - | Agent specs: model[:persona[:"instruction"]] |
| `--depth` | `-d` | No | `standard` | Debate depth: quick, standard, deep |
| `--convergence` | | No | `0.80` | Alignment threshold (0.50-0.99) |
| `--interactive` | `-i` | No | `false` | Pause for user input at decision points |
| `--output` | `-o` | No | Auto | Output directory |
| `--focus` | `-f` | No | All | Debate focus areas (comma-separated) |

### 6.3 Examples

```bash
# Compare two roadmap drafts
/sc:adversarial --compare draft-a.md,draft-b.md --depth standard

# Generate 3 roadmap variants from a spec using different models/personas
/sc:adversarial --source auth-spec.md --generate roadmap \
  --agents opus:architect,sonnet:security,opus:analyzer \
  --depth deep --convergence 0.85

# Compare 5 specs with interactive mode
/sc:adversarial --compare spec1.md,spec2.md,spec3.md,spec4.md,spec5.md \
  --interactive --depth deep

# Quick comparison with focused debate
/sc:adversarial --compare plan-a.md,plan-b.md \
  --depth quick --focus structure,completeness

# Full pipeline with custom output
/sc:adversarial --source migration-plan.md --generate roadmap \
  --agents opus:architect:"prioritize backward compatibility",sonnet:security:"zero-trust" \
  --depth deep --output .dev/releases/current/migration-v2/
```

---

## 7. Integration Points

### 7.1 sc:roadmap v2 Integration

sc:roadmap invokes sc:adversarial in two scenarios:

**Multi-spec mode** (`/sc:roadmap --specs spec1.md,spec2.md`):
```
sc:roadmap → sc:adversarial --compare spec1.md,spec2.md → unified-spec.md → roadmap generation
```

**Multi-roadmap mode** (`/sc:roadmap --multi-roadmap --agents opus,sonnet`):
```
sc:roadmap → sc:adversarial --source spec.md --generate roadmap --agents opus,sonnet → unified-roadmap.md
```

**Combined mode** (both flags):
```
sc:roadmap → sc:adversarial --compare specs → unified-spec.md
           → sc:adversarial --source unified-spec.md --generate roadmap --agents → unified-roadmap.md
```

### 7.2 Future Integration Candidates

| Command | Use Case |
|---------|----------|
| `/sc:design` | Compare multiple architectural designs |
| `/sc:implement` | Compare implementation approaches before committing |
| `/sc:spec-panel` | Augment expert panel with adversarial cross-review |
| `/sc:test` | Compare test strategies or coverage approaches |
| `/sc:improve` | Generate competing improvement plans, merge best of each |

### 7.3 Delegation Pattern

When sc:adversarial delegates to existing commands:

| Step | Delegates To | Purpose |
|------|-------------|---------|
| Diff analysis | `/sc:analyze` or analytical agent | Structured comparison |
| Advocate generation | Domain agents (per --agents spec) | Generate debate arguments |
| Refactoring plan | Analytical agent | Draft the merge plan |
| Merge execution | merge-executor agent | Execute the plan |

---

## 8. Artifact Specifications

### 8.1 diff-analysis.md

```markdown
# Diff Analysis: <artifact-type> Comparison

## Metadata
- Generated: <timestamp>
- Variants compared: <count>
- Total differences found: <count>
- Categories: structural (<N>), content (<N>), contradictions (<N>), unique (<N>)

## Structural Differences

| # | Area | Variant A | Variant B | Severity |
|---|------|-----------|-----------|----------|
| S-001 | Section ordering | Auth before API | API before Auth | Low |
| S-002 | Hierarchy depth | 3-level milestones | 2-level milestones | Medium |

## Content Differences

| # | Topic | Variant A Approach | Variant B Approach | Severity |
|---|-------|-------------------|-------------------|----------|
| C-001 | Auth strategy | JWT with refresh tokens | OAuth2 with PKCE | High |

## Contradictions

| # | Point of Conflict | Variant A Position | Variant B Position | Impact |
|---|-------------------|-------------------|-------------------|--------|
| X-001 | Database choice | PostgreSQL required | MongoDB preferred | High |

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|-------------|-----------------|
| U-001 | A | Rollback strategy for each milestone | High |
| U-002 | B | Performance budget per component | Medium |
```

### 8.2 debate-transcript.md

```markdown
# Adversarial Debate Transcript

## Metadata
- Depth: <quick|standard|deep>
- Rounds completed: <N>
- Convergence achieved: <percentage>%
- Focus areas: <list>

## Round 1: Advocate Statements

### Variant A Advocate (opus:architect)
**Position**: [Summary of argument for Variant A]
**Key strengths claimed**:
1. [Strength with evidence]
2. [Strength with evidence]
**Weaknesses identified in Variant B**:
1. [Critique with evidence]

### Variant B Advocate (sonnet:security)
**Position**: [Summary of argument for Variant B]
**Key strengths claimed**:
1. [Strength with evidence]
**Weaknesses identified in Variant A**:
1. [Critique with evidence]

## Round 2: Rebuttals (if --depth standard or deep)

### Variant A Rebuttal
[Response to Variant B's critiques with counter-evidence]

### Variant B Rebuttal
[Response to Variant A's critiques with counter-evidence]

## Round 3: Final Arguments (if --depth deep and convergence < threshold)

[Final positions after considering rebuttals]

## Scoring Matrix

| Diff Point | Winner | Confidence | Evidence Summary |
|------------|--------|------------|-----------------|
| S-001 | A | 85% | Better dependency flow |
| C-001 | B | 72% | Stronger security model |
| X-001 | A | 60% | More practical for team |

## Convergence Assessment
- Points resolved: <N> of <total>
- Alignment: <percentage>%
- Threshold: <configured>%
- Status: <CONVERGED|NOT_CONVERGED>
```

### 8.3 base-selection.md

```markdown
# Base Selection Report

## Quantitative Scoring (50% weight)

| Metric | Weight | Variant A (opus:architect) | Variant B (sonnet:security) |
|--------|--------|---------------------------|----------------------------|
| requirement_coverage | 0.30 | 0.88 (22/25 requirements) | 0.80 (20/25 requirements) |
| internal_consistency | 0.25 | 0.95 (1 contradiction/20 claims) | 0.90 (2 contradictions/20 claims) |
| specificity_ratio | 0.15 | 0.72 (concrete/total statements) | 0.68 |
| dependency_completeness | 0.15 | 0.85 (17/20 refs defined) | 0.90 (18/20 refs defined) |
| section_coverage | 0.15 | 1.00 (12/12 normalized) | 0.83 (10/12 normalized) |
| **quant_score** | | **0.884** | **0.832** |

## Qualitative Scoring (50% weight) — Additive Binary Rubric

### Completeness (5 criteria)
| Criterion | Variant A | Evidence | Variant B | Evidence |
|-----------|-----------|----------|-----------|----------|
| Covers all explicit requirements | ✅ | Sections 2-7 map to spec R-001 through R-025 | ✅ | Sections 2-6 cover R-001 through R-020 |
| Addresses edge cases/failures | ✅ | Section 5.3: "rollback procedure per milestone" | ❌ | No failure handling section found |
| Includes dependencies/prerequisites | ✅ | Section 1.2: dependency graph | ✅ | Section 1.3: prerequisites list |
| Defines success/completion criteria | ❌ | No explicit success criteria section | ✅ | Section 8: acceptance criteria |
| Specifies out-of-scope items | ✅ | Section 1.4: "Explicitly excludes..." | ❌ | No scoping section |
| **Subtotal** | **4/5** | | **3/5** | |

[... similar tables for correctness, structure, clarity, risk_coverage ...]

### Qualitative Summary
| Dimension | Variant A | Variant B |
|-----------|-----------|-----------|
| Completeness | 4/5 | 3/5 |
| Correctness | 4/5 | 5/5 |
| Structure | 5/5 | 3/5 |
| Clarity | 4/5 | 4/5 |
| Risk Coverage | 3/5 | 4/5 |
| **qual_score** | **20/25 = 0.800** | **19/25 = 0.760** |

## Combined Scoring

| Variant | Quant (×0.50) | Qual (×0.50) | **Final Score** | Debate Tiebreaker |
|---------|---------------|--------------|-----------------|-------------------|
| A (opus:architect) | 0.442 | 0.400 | **0.842** | 65% wins (not needed) |
| B (sonnet:security) | 0.416 | 0.380 | **0.796** | 35% wins |

**Margin**: 5.8% (>5% threshold, no tiebreaker needed)

## Selected Base: Variant A (opus:architect)

### Selection Rationale
Variant A scores higher on both quantitative (0.884 vs 0.832) and qualitative (0.800 vs 0.760) layers. The quantitative advantage is driven by higher requirement coverage (88% vs 80%) and full section coverage. The qualitative advantage comes from stronger structure and completeness despite weaker risk coverage.

### Strengths to Preserve from Base
1. Comprehensive requirement traceability (22/25 requirements mapped)
2. Complete section structure with dependency graph

### Strengths to Incorporate from Non-Base Variants
1. Variant B's superior correctness (5/5 vs 4/5) — zero factual errors
2. Variant B's risk coverage (4/5 vs 3/5) — explicit threat modeling section
3. Variant B's acceptance criteria section (missing from base)
```

### 8.4 refactor-plan.md

```markdown
# Refactoring Plan: Merge into Base (Variant A)

## Overview
- Base: Variant A (opus:architect)
- Incorporating strengths from: Variant B (sonnet:security)
- Planned changes: <N>
- Risk level: <Low|Medium|High>

## Planned Changes

### Change 1: Incorporate Zero-Trust Auth Model (from Variant B)
- **Source**: Variant B, Section 3.2
- **Target**: Base, Section 3.2 (replace JWT approach)
- **Rationale**: Debate Round 2 established B's auth model as superior (72% confidence)
- **Integration point**: Replace Section 3.2 entirely, update references in Sections 4.1 and 5.3
- **Risk**: Medium - requires adjusting 3 dependent sections

### Change 2: Add Performance Budgets (from Variant B)
- **Source**: Variant B, Section 6 (unique contribution U-002)
- **Target**: Base, new Section 6.5
- **Rationale**: Unique contribution with medium value, no conflict with base
- **Integration point**: Insert as new subsection after existing Section 6.4
- **Risk**: Low - additive change, no conflicts

## Changes NOT Being Made (with rationale)
- [Difference that was debated but base approach was determined superior]

## Review Status
- [ ] Auto-approved (default) / [ ] User-approved (--interactive)
```

---

## 9. Boundaries

### Will Do
- Compare 2-10 artifacts through structured adversarial debate
- Generate variant artifacts using different model/persona configurations
- Produce transparent, documented merge decisions
- Execute refactoring plans to produce unified outputs
- Support configurable depth, convergence thresholds, and focus areas
- Work as a generic tool invocable by any SuperClaude command

### Will Not Do
- Validate domain-specific correctness of merged output (calling command's responsibility)
- Execute the merged output (planning tool, not execution tool)
- Manage git operations or version control
- Make decisions without documented rationale
- Operate with fewer than 2 variants (minimum for adversarial comparison)
- Override user decisions in interactive mode

---

## 10. MCP Integration

| Server | Usage | Phase |
|--------|-------|-------|
| Sequential | Debate scoring, convergence analysis, refactoring plan logic | Steps 2-4 |
| Serena | Memory persistence of adversarial outcomes for cross-session learning | Step 5 |
| Context7 | Domain pattern validation during merge | Step 5 |

**Circuit breaker**: If Sequential is unavailable, fall back to native Claude reasoning with depth reduction (deep → standard, standard → quick).

---

## 11. Success Criteria

### Functional
- [ ] Mode A (compare) produces valid merged output from 2-10 input files
- [ ] Mode B (generate) produces variants using specified agent configurations
- [ ] All 5 protocol steps execute and produce documented artifacts
- [ ] Debate depth respects --depth flag (1/2/3 rounds)
- [ ] Convergence detection works at configurable threshold
- [ ] Interactive mode pauses at correct decision points
- [ ] Return contract provides all required fields to calling command

### Quality
- [ ] Every decision traceable to evidence in artifacts
- [ ] Merged output incorporates documented strengths from all variants
- [ ] No silent conflict resolution - all contradictions addressed in artifacts
- [ ] Provenance annotations in merged output

### Performance
- [ ] Variant generation runs in parallel (Mode B)
- [ ] Standard depth completes in <5 minutes for typical artifacts
- [ ] 5-10 agents supported without degradation

---

## 12. File Structure

```
src/superclaude/commands/
└── adversarial.md              Command definition (~80-100 lines)

src/superclaude/skills/sc-adversarial/
├── SKILL.md                    Behavioral instructions (~400-500 lines)
└── refs/
    ├── debate-protocol.md      5-step protocol details, convergence detection
    ├── scoring-protocol.md     Hybrid quant-qual scoring algorithm (from Appendix A)
    ├── agent-specs.md          Agent specification format, advocate behavior
    └── artifact-templates.md   Output format specifications

src/superclaude/agents/
├── debate-orchestrator.md      Process coordinator agent
└── merge-executor.md           Refactoring plan executor agent
```

---

## 13. Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Agents produce nearly identical outputs | Medium | Low | Detect <10% diff, skip debate, return either |
| Debate fails to converge | Low | Medium | Force-select by score after max rounds, document non-convergence |
| Merge execution corrupts base document | Low | High | Preserve all original variants, merge-log enables manual recovery |
| Token consumption for 10-agent deep debate | Medium | Low | No cost constraints per requirement, but document actual usage |
| Advocate agents argue in bad faith (model limitations) | Low | Medium | Debate-orchestrator validates evidence claims against source material |

---

## 14. Appendix A: Scoring Protocol (Full Specification)

### A.1 Quantitative Layer (50% of final score)

All quantitative metrics are computed deterministically from artifact text. No LLM judgment is involved in this layer.

#### Metrics

| Metric | Symbol | Computation | Weight |
|--------|--------|------------|--------|
| Requirement Coverage | `RC` | Count of source requirements referenced in variant (grep-matched by requirement ID or keyword) ÷ total source requirements | 0.30 |
| Internal Consistency | `IC` | 1 - (contradictions detected ÷ total scorable claims). Contradictions: statements within the same variant that assert incompatible positions. | 0.25 |
| Specificity Ratio | `SR` | Count of concrete statements (containing numbers, dates, named entities, specific thresholds, measurable criteria) ÷ total substantive statements. Excludes headings, boilerplate, and metadata. | 0.15 |
| Dependency Completeness | `DC` | Count of internal references (to sections, milestones, components, terms) that resolve to a definition within the document ÷ total internal references. | 0.15 |
| Section Coverage | `SC` | Variant's top-level section count ÷ max(top-level section count across all variants). | 0.15 |

#### Formula

```
quant_score = (RC × 0.30) + (IC × 0.25) + (SR × 0.15) + (DC × 0.15) + (SC × 0.15)
```

All metrics are normalized to [0.0, 1.0]. `quant_score` ∈ [0.0, 1.0].

#### Contradiction Detection Protocol

A contradiction is identified when:
1. Two statements within the same variant make opposing claims about the same subject
2. A stated requirement conflicts with a stated constraint
3. A timeline or dependency creates an impossible sequence

The orchestrator performs a structured scan: for each claim in the variant, check whether any other claim in the same variant asserts the opposite or an incompatible position. Claims must be specific enough to be falsifiable — vague statements cannot contradict.

### A.2 Qualitative Layer (50% of final score)

Uses an additive binary rubric with mandatory evidence citation (Claim-Evidence-Verdict protocol).

#### Dimensions and Criteria

**Completeness** (5 criteria):
1. Covers all explicit requirements from source input
2. Addresses edge cases and failure scenarios
3. Includes dependencies and prerequisites
4. Defines success/completion criteria
5. Specifies what is explicitly out of scope

**Correctness** (5 criteria):
1. No factual errors or hallucinated claims
2. Technical approaches are feasible with stated constraints
3. Terminology used consistently and accurately throughout
4. No internal contradictions (cross-validated with quantitative IC metric)
5. Claims supported by evidence or rationale within the document

**Structure** (5 criteria):
1. Logical section ordering (prerequisites before dependents)
2. Consistent hierarchy depth (no orphaned subsections)
3. Clear separation of concerns between sections
4. Navigation aids present (table of contents, cross-references, or index)
5. Follows conventions of the artifact type (e.g., roadmap conventions for roadmaps)

**Clarity** (5 criteria):
1. Unambiguous language (no "should consider", "might", "as appropriate")
2. Concrete rather than abstract (specific actions, not general principles)
3. Each section has a clear purpose statement or can be summarized in one sentence
4. Acronyms and domain terms defined on first use
5. Actionable next steps or decision points clearly identified

**Risk Coverage** (5 criteria):
1. Identifies at least 3 risks with probability and impact assessment
2. Provides mitigation strategy for each identified risk
3. Addresses failure modes and recovery procedures
4. Considers external dependencies and their failure scenarios
5. Includes monitoring or validation mechanism for risk detection

#### Evidence Citation Protocol (CEV)

Every criterion assessment MUST follow this structure:
```
CLAIM:    "[Criterion description] is met/not met in Variant X"
EVIDENCE: "[Direct quote or section reference from the variant]"
          OR "No evidence found — searched sections [list]"
VERDICT:  MET (1 point) | NOT MET (0 points)
```

If the evaluator cannot cite specific evidence for a MET verdict, the criterion defaults to NOT MET. This prevents hallucinated quality assessments.

#### Formula

```
qual_score = total_criteria_met / 25
```

`qual_score` ∈ [0.0, 1.0]. Maximum: 25/25 = 1.0.

### A.3 Combined Scoring

```
variant_score = (0.50 × quant_score) + (0.50 × qual_score)
```

`variant_score` ∈ [0.0, 1.0].

### A.4 Tiebreaker Protocol

If the top two variants score within 5% of each other (`|score_A - score_B| < 0.05`):
1. Debate performance breaks the tie: the variant that won more diff points in Step 2 is selected
2. If debate performance is also tied (within 5%): the variant with higher `correctness` criteria count wins (correctness is the most valuable dimension for the pipeline's hallucination-detection objective)
3. If still tied: the variant presented first in the input order is selected (arbitrary but deterministic)

### A.5 Position-Bias Mitigation

The qualitative evaluation runs twice per variant:
- **Pass 1**: Variants evaluated in input order (A, B, C, ...)
- **Pass 2**: Variants evaluated in reverse order (C, B, A, ...)

Per criterion, per variant:
- If both passes agree → use the agreed verdict
- If passes disagree → criterion is re-evaluated with explicit comparison prompt citing both passes' evidence, and the re-evaluation verdict is final

This eliminates systematic position bias documented in LLM-as-judge research.

---

## 15. Version History

- **1.0.0** (2026-02-20): Initial draft from sc:roadmap v2 brainstorm session
- **1.1.0** (2026-02-20): Incorporated spec-panel feedback — added Hybrid Quantitative-Qualitative scoring protocol (Appendix A), steelman goal statement, removed --dry-run

---

*Specification generated from /sc:brainstorm requirements discovery session*
*Reviewed via /sc:spec-panel — feedback incorporated*
