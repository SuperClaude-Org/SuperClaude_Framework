# Extraction: Adversarial Debate Feature — Complete Command + Skill + Agent Example

## Source Files
- `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md` (v1.1.0, 2026-02-20)
- `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/roadmap.md` (v1.7.0, 2026-02-21)

## Extraction Purpose
This document captures all information relevant to developing custom commands, skills, and agents for the SuperClaude framework, using the v1.7 adversarial debate feature as a complete worked example.

---

## 1. Component Architecture: Command + Skill + Agent Triad

The adversarial feature demonstrates SuperClaude's three-layer component model. Each layer has a distinct role and a defined file location.

### 1.1 File Structure (The Blueprint)

From the spec, Section 12:

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

From the roadmap, File Manifest section, the scaffolding also includes:

```
src/superclaude/skills/sc-adversarial/__init__.py   # Package marker
```

And framework integration edits:

```
COMMANDS.md      # Add sc:adversarial entry
FLAGS.md         # Add --adversarial flags if needed
ORCHESTRATOR.md  # Add routing rules for adversarial pattern
```

**Total new files**: 9
**Total edited files**: 3 (framework registration files)

### 1.2 Component Roles

| Component | Location | Size | Role |
|-----------|----------|------|------|
| **Command** | `src/superclaude/commands/adversarial.md` | ~80-100 lines | Entry point: usage, flags, examples, boundaries |
| **Skill** | `src/superclaude/skills/sc-adversarial/SKILL.md` | ~400-500 lines | Behavioral brain: 5-step protocol, convergence, error handling |
| **Skill refs** | `src/superclaude/skills/sc-adversarial/refs/` | 4 files | Detailed reference docs the skill draws on |
| **Agent: debate-orchestrator** | `src/superclaude/agents/debate-orchestrator.md` | ~60-80 lines | Process coordinator, does NOT participate in debates |
| **Agent: merge-executor** | `src/superclaude/agents/merge-executor.md` | ~40-60 lines | Executes refactoring plans, specialist in document integration |
| **Dynamic advocates** | Created at runtime per `--agents` spec | N/A | Instantiated from model:persona:"instruction" specifications |

### 1.3 How Components Trigger Each Other

The invocation chain works as follows:

1. **User invokes command**: `/sc:adversarial --compare file1.md,file2.md --depth standard`
2. **Command definition** (`adversarial.md`) defines the interface — flags, modes, examples
3. **Skill** (`SKILL.md`) contains the behavioral instructions — the 5-step protocol that Claude follows
4. **Skill refs** provide detailed algorithms (scoring protocol, debate protocol) that the skill references
5. **Agents** are delegated to by the skill's protocol:
   - `debate-orchestrator` coordinates the overall pipeline (Steps 1-4)
   - `merge-executor` handles Step 5 (merge execution)
   - Advocate agents are instantiated dynamically per `--agents` spec

The spec also describes how **other commands invoke sc:adversarial** (Section 7.1):

> "sc:roadmap invokes sc:adversarial in two scenarios:
> **Multi-spec mode**: `sc:roadmap → sc:adversarial --compare spec1.md,spec2.md → unified-spec.md → roadmap generation`
> **Multi-roadmap mode**: `sc:roadmap → sc:adversarial --source spec.md --generate roadmap --agents opus,sonnet → unified-roadmap.md`"

---

## 2. Command Design Pattern

### 2.1 Dual Input Modes

The command supports two distinct invocation patterns (FR-001):

**Mode A: Compare existing files**
```bash
/sc:adversarial --compare file1.md,file2.md[,file3.md,...,file10.md]
```

**Mode B: Generate + compare from source**
```bash
/sc:adversarial --source source.md --generate <type> --agents <agent-spec>[,<agent-spec>,...]
```

### 2.2 Flag Design

From spec Section 6.2:

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

### 2.3 Agent Specification Format

The `--agents` flag uses a hybrid format:

```
<model>                              # e.g., opus
<model>:<persona>                    # e.g., opus:architect
<model>:<persona>:"<instruction>"    # e.g., opus:architect:"focus on scalability"
```

> "Supported models: Any model available in the environment (opus, sonnet, haiku, or configured aliases)."
> "Agent count: 2-10 agents. Minimum 2 required for adversarial comparison."

### 2.4 Return Contract (FR-007)

When invoked by another command, sc:adversarial returns a structured contract:

> "sc:adversarial returns:
> - Path to the merged output file
> - Final convergence score
> - Path to the adversarial/ artifacts directory
> - Success/partial/failed status
> - List of unresolved conflicts (if any)"

This is critical for composability — other commands depend on this contract.

### 2.5 Complete Usage Examples

From spec Section 6.3:

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

## 3. Skill Design Pattern

### 3.1 SKILL.md Structure

The skill file is the behavioral core at ~400-500 lines. It encodes:

- The 5-step adversarial protocol (the full pipeline logic)
- Convergence detection algorithms
- Error handling behavior
- Artifact output format requirements

### 3.2 Skill Reference Files (refs/)

The `refs/` subdirectory contains detailed reference documents that the SKILL.md draws upon:

| File | Content | Purpose |
|------|---------|---------|
| `debate-protocol.md` | 5-step protocol details, convergence detection | Core algorithmic reference |
| `scoring-protocol.md` | Hybrid quant-qual scoring algorithm | Appendix A of the spec, extracted |
| `agent-specs.md` | Agent specification format, advocate behavior | How dynamic agents are instantiated |
| `artifact-templates.md` | Output format specifications | Templates for all 5 output artifacts |

### 3.3 The 5-Step Protocol (Core Skill Logic)

From spec Section FR-002, the skill orchestrates these steps:

**Step 1: Diff Analysis**
- Input: All variant artifacts
- Output: `diff-analysis.md`
- Identifies: structural differences, content differences, contradictions, unique contributions
- Delegation: analytical agent

**Step 2: Adversarial Debate**
- Input: All variants + diff-analysis.md
- Output: `debate-transcript.md`
- Process: advocate agents argue for their variant, with configurable rounds
- Depth control: quick (1 round), standard (2 rounds), deep (up to 3 rounds)
- Convergence: measured as % of diff points where agents agree; default threshold 80%
- Delegation: debate-orchestrator coordinates, domain agents participate

**Step 3: Base Selection**
- Input: All variants + debate-transcript.md
- Output: `base-selection.md`
- Uses hybrid quantitative-qualitative scoring (50/50 weight)
- Delegation: debate-orchestrator agent

**Step 4: Refactoring Plan**
- Input: Selected base + all other variants + debate-transcript.md
- Output: `refactor-plan.md`
- Generates actionable merge plan with integration points
- Delegation: debate-orchestrator drafts, analytical agent reviews

**Step 5: Merge Execution**
- Input: Base variant + refactor-plan.md
- Output: Unified merged artifact + `merge-log.md`
- Maintains provenance annotations
- Delegation: merge-executor agent

### 3.4 Artifact Output Structure

From FR-005:

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

Naming conventions:
- Mode A: `variant-1-original.md`, `variant-2-original.md` (copies of input files)
- Mode B: `variant-1-<model>-<persona>.md`, e.g., `variant-1-opus-architect.md`

---

## 4. Agent Design Patterns

### 4.1 debate-orchestrator Agent

From spec Section 5.1:

> "**Purpose**: Coordinates the entire adversarial pipeline. Does NOT participate in debates - it manages the process."

Responsibilities:
- Parse input mode and validate parameters
- Dispatch variant generation (Mode B) in parallel
- Coordinate the 5-step protocol
- Track convergence scoring across debate rounds
- Make base selection using scoring algorithm
- Hand off to merge-executor for step 5
- Compile final return contract

Key constraints:
> "**Does NOT**: Generate variants (delegates to specified agents), Participate in debates (delegates to advocate agents), Execute merges (delegates to merge-executor)"

> "**Model preference**: Highest-capability model available (opus preferred) - the orchestrator needs strong reasoning for scoring and coordination."

> "**Tools**: Task (for delegation), Read, Write, Glob, Grep, Bash (for file operations)"

Size: ~60-80 lines

### 4.2 merge-executor Agent

From spec Section 5.2:

> "**Purpose**: Executes refactoring plans to produce unified merged artifacts. Specialist in document integration."

Responsibilities:
- Read the base variant and refactoring plan
- Apply each planned change methodically
- Maintain structural integrity during merge
- Add provenance annotations
- Validate the merged output for consistency
- Produce merge-log.md documenting each applied change

Key constraints:
> "**Does NOT**: Make strategic decisions about what to merge (follows the plan), Override the refactoring plan without escalation, Participate in debates or scoring"

> "**Model preference**: High-capability model (opus or sonnet) - needs strong writing and structural reasoning."

> "**Tools**: Read, Write, Edit, Grep (for content verification)"

Size: ~40-60 lines

### 4.3 Dynamic Advocate Agents

From spec Section 5.3:

> "These are NOT pre-defined agents. They are instantiated dynamically from the `--agents` specification."

Each advocate:
- Receives their variant + all other variants + diff-analysis.md
- Argues for their variant's strengths in the specified focus areas
- Critiques weaknesses in other variants with evidence
- Responds to rebuttals in subsequent rounds

> "The advocate's behavior is shaped by:
> - The model specified (opus, sonnet, haiku)
> - The persona specified (architect, security, analyzer, etc.)
> - The custom instruction (if provided)"

---

## 5. Scoring and Algorithm Design

### 5.1 Hybrid Quantitative-Qualitative Scoring

From Appendix A — this is the most detailed algorithm in the spec and demonstrates how to design deterministic evaluation within an LLM-driven system.

**Quantitative Layer (50% weight)** — fully deterministic, no LLM judgment:

| Metric | Symbol | Weight | Computation |
|--------|--------|--------|-------------|
| Requirement Coverage | RC | 0.30 | grep-matched requirements / total source requirements |
| Internal Consistency | IC | 0.25 | 1 - (contradictions / total claims) |
| Specificity Ratio | SR | 0.15 | concrete statements / total statements |
| Dependency Completeness | DC | 0.15 | resolved internal refs / total internal refs |
| Section Coverage | SC | 0.15 | section count / max section count across variants |

Formula:
```
quant_score = (RC * 0.30) + (IC * 0.25) + (SR * 0.15) + (DC * 0.15) + (SC * 0.15)
```

**Qualitative Layer (50% weight)** — LLM-assessed with strict evidence requirements:

Five dimensions, each with 5 binary criteria (25 total):
- Completeness, Correctness, Structure, Clarity, Risk Coverage
- Each criterion: 1 point if met, 0 if not. No partial credit.
- Evidence citation required via Claim-Evidence-Verdict (CEV) protocol

Formula:
```
qual_score = total_criteria_met / 25
```

**Combined**:
```
variant_score = (0.50 * quant_score) + (0.50 * qual_score)
```

### 5.2 Position-Bias Mitigation

> "The qualitative evaluation runs twice per variant:
> - **Pass 1**: Variants evaluated in input order (A, B, C, ...)
> - **Pass 2**: Variants evaluated in reverse order (C, B, A, ...)
>
> Per criterion, per variant:
> - If both passes agree -> use the agreed verdict
> - If passes disagree -> criterion is re-evaluated with explicit comparison prompt citing both passes' evidence, and the re-evaluation verdict is final
>
> This eliminates systematic position bias documented in LLM-as-judge research."

### 5.3 Tiebreaker Protocol

> "If the top two variants score within 5% of each other:
> 1. Debate performance breaks the tie: the variant that won more diff points in Step 2 is selected
> 2. If debate performance is also tied: the variant with higher correctness criteria count wins
> 3. If still tied: the variant presented first in the input order is selected (arbitrary but deterministic)"

### 5.4 Convergence Detection

> "Measured as percentage of diff points where agents agree on the superior approach. Default threshold: 80%."

Depth controls how many rounds are allowed:
- `quick`: 1 round (advocate statements only)
- `standard`: 2 rounds (advocate + rebuttal)
- `deep`: Up to 3 rounds, continuing until convergence threshold or max rounds

---

## 6. Error Handling Design

From FR-006:

| Scenario | Behavior |
|----------|----------|
| Agent fails to generate variant | Retry once, then proceed with N-1 variants (minimum 2 required) |
| Variants too similar (<10% diff) | Skip debate, select either as base, log "variants substantially identical" |
| Variants too divergent (no convergence after max rounds) | Force-select by score, document non-convergence, flag for user review |
| Merge execution produces invalid output | Preserve all artifacts, flag failure, provide refactor-plan.md for manual execution |
| Single variant remains after failures | Abort adversarial process, return the surviving variant as-is with warning |

---

## 7. MCP Integration Pattern

From spec Section 10:

| Server | Usage | Phase |
|--------|-------|-------|
| Sequential | Debate scoring, convergence analysis, refactoring plan logic | Steps 2-4 |
| Serena | Memory persistence of adversarial outcomes for cross-session learning | Step 5 |
| Context7 | Domain pattern validation during merge | Step 5 |

Circuit breaker fallback:
> "If Sequential is unavailable, fall back to native Claude reasoning with depth reduction (deep -> standard, standard -> quick)."

---

## 8. Testing and Validation Strategy

### 8.1 Bottom-Up with Artifact Validation

From the roadmap, Implementation Strategy section:

> "Each milestone produces testable artifacts. Validate each step's output quality before proceeding:
> 1. **M0**: Scaffold -> `make sync-dev` -> verify all files exist
> 2. **M1**: Test with 2 real markdown files -> inspect diff-analysis.md quality
> 3. **M2**: Test with diff-analysis.md from M1 -> inspect debate-transcript.md for genuine disagreement (not sycophantic)
> 4. **M3**: Test with debate transcript -> verify scoring determinism (run twice, same quant scores)
> 5. **M4**: Test merge -> verify provenance annotations, structural integrity
> 6. **M5**: Full pipeline E2E -> both modes -> error handling edge cases"

### 8.2 Acceptance Criteria per Milestone

**M0 (Foundation)**:
> "All files created, `make sync-dev` copies to `.claude/`, `make verify-sync` passes."

**M1 (Diff Analysis)**:
> "Given 2+ input files, produces a well-structured diff-analysis.md with structural, content, contradiction, and unique contribution sections."

**M2 (Debate)**:
> "Given diff-analysis.md and 2+ advocate agents, produces debate with correct round count, convergence tracking, and per-point scoring."

**M3 (Scoring)**:
> "Given variants + debate transcript, produces deterministic quantitative scores, evidence-backed qualitative scores, combined ranking, and documented base selection."

**M4 (Merge)**:
> "Given base + other variants + debate transcript, produces a merge plan, executes it to produce a unified document with provenance, and returns the contract."

**M5 (Integration)**:
> "Full pipeline runs successfully in both Mode A and Mode B. All error handling paths tested. Framework files updated. `make sync-dev && make verify-sync` passes."

### 8.3 Success Criteria (from Spec Section 11)

**Functional**:
- Mode A (compare) produces valid merged output from 2-10 input files
- Mode B (generate) produces variants using specified agent configurations
- All 5 protocol steps execute and produce documented artifacts
- Debate depth respects --depth flag (1/2/3 rounds)
- Convergence detection works at configurable threshold
- Interactive mode pauses at correct decision points
- Return contract provides all required fields to calling command

**Quality**:
- Every decision traceable to evidence in artifacts
- Merged output incorporates documented strengths from all variants
- No silent conflict resolution — all contradictions addressed in artifacts
- Provenance annotations in merged output

**Performance**:
- Variant generation runs in parallel (Mode B)
- Standard depth completes in <5 minutes for typical artifacts
- 5-10 agents supported without degradation

---

## 9. Integration with the SuperClaude Framework

### 9.1 Framework Registration (M5)

From the roadmap, T5.4:

> "Framework registration: update COMMANDS.md, FLAGS.md, ORCHESTRATOR.md, PERSONAS.md routing tables for sc:adversarial."

This means new commands must be registered in four framework files to be fully integrated.

### 9.2 ORCHESTRATOR.md Routing Entry

The existing ORCHESTRATOR.md already contains routing entries for adversarial (added during development):

```
| "adversarial debate" | complex | analysis | architect + analyzer personas, --ultrathink, Sequential + Serena | 95% |
| "compare variants" | complex | analysis | analyzer persona, --think-hard, Sequential | 90% |
| "merge best of" | complex | analysis | architect persona, --think, Sequential | 85% |
```

### 9.3 COMMANDS.md Entry

The existing COMMANDS.md contains:

```
**`/sc:adversarial [--compare files|--source file --generate type --agents specs]
  [--depth quick|standard|deep] [--convergence N] [--interactive] [--focus areas]`**
  — Structured adversarial debate, comparison, and merge pipeline (wave-enabled, complex profile)
- **Auto-Persona**: Architect, Analyzer, Scribe
- **MCP**: Sequential (debate scoring/convergence), Serena (memory persistence), Context7 (domain validation)
- **Tools**: [Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task]
- **Agents**: debate-orchestrator (coordinator), merge-executor (specialist), advocate agents (dynamic)
```

### 9.4 Composability with Other Commands

From spec Section 7.2, future integration candidates:

| Command | Use Case |
|---------|----------|
| `/sc:design` | Compare multiple architectural designs |
| `/sc:implement` | Compare implementation approaches before committing |
| `/sc:spec-panel` | Augment expert panel with adversarial cross-review |
| `/sc:test` | Compare test strategies or coverage approaches |
| `/sc:improve` | Generate competing improvement plans, merge best of each |

### 9.5 Delegation Pattern

From spec Section 7.3:

| Step | Delegates To | Purpose |
|------|-------------|---------|
| Diff analysis | `/sc:analyze` or analytical agent | Structured comparison |
| Advocate generation | Domain agents (per --agents spec) | Generate debate arguments |
| Refactoring plan | Analytical agent | Draft the merge plan |
| Merge execution | merge-executor agent | Execute the plan |

---

## 10. Spec-to-Implementation Pipeline

This feature demonstrates the full SuperClaude development lifecycle:

### 10.1 Discovery Phase

> "Specification generated from /sc:brainstorm requirements discovery session"
> "Reviewed via /sc:spec-panel — feedback incorporated"

The spec was created through brainstorming, then reviewed by a spec panel that added the hybrid scoring protocol.

### 10.2 Spec Phase

The spec (SC-ADVERSARIAL-SPEC.md) contains 15 sections covering:
1. Executive Summary
2. Scope (in/out)
3. Functional Requirements (FR-001 through FR-007)
4. Non-Functional Requirements (NFR-001 through NFR-004)
5. Agent Definitions
6. Command Interface
7. Integration Points
8. Artifact Specifications (with full templates)
9. Boundaries (will do / will not do)
10. MCP Integration
11. Success Criteria
12. File Structure
13. Risks
14. Appendix A: Scoring Protocol
15. Version History

### 10.3 Roadmap Phase

The roadmap breaks the spec into 6 milestones (M0-M5):

```
M0: Foundation & Scaffolding                    [2-3h]
M1: Diff Analysis Engine (Step 1)               [3-4h]
M2: Adversarial Debate Protocol (Step 2)        [6-8h]  <- Core complexity
M3: Hybrid Scoring & Base Selection (Step 3)    [4-6h]
M4: Refactoring Plan & Merge Execution (4-5)    [4-6h]
M5: Integration, Polish & Validation            [4-6h]
```

Total: 23-33 hours (~4-5 days), strictly sequential critical path.

### 10.4 Implementation Strategy

> "Recommended Approach: Bottom-Up with Artifact Validation"

Each milestone produces testable artifacts, validated before proceeding. The roadmap explicitly identifies:
- Parallel execution opportunities (T2.2, T5.2, T3.3)
- Model selection per agent role
- Risk mitigations per milestone

### 10.5 The sync-dev Workflow

From roadmap M0 acceptance criteria:

> "All files created, `make sync-dev` copies to `.claude/`, `make verify-sync` passes."

This is the standard workflow for all SuperClaude component development:
1. Edit files in `src/superclaude/` (source of truth)
2. Run `make sync-dev` to copy to `.claude/` (where Claude Code reads them)
3. Run `make verify-sync` to confirm sync

---

## 11. Architecture Decisions for Multi-Agent Features

### 11.1 Separation of Concerns

The orchestrator pattern is central: the debate-orchestrator coordinates but does not participate. This prevents the coordinator from biasing outcomes.

> "Does NOT: Generate variants (delegates to specified agents), Participate in debates (delegates to advocate agents), Execute merges (delegates to merge-executor)"

### 11.2 Parallel vs Sequential Execution

From the roadmap:

> "**Parallel Execution Opportunities**:
> - M2 T2.2: Advocate statements generated in parallel (all agents simultaneously)
> - M5 T5.2: Mode B variant generation in parallel (all agents simultaneously)
> - M3 T3.3: Position-bias dual-pass can run in parallel (forward + reverse simultaneously)"

But rebuttals are sequential (T2.3) because each agent needs to see prior round output.

### 11.3 Steelman Strategy (Anti-Sycophancy)

From the executive summary:

> "The pipeline employs a steelman debate strategy — advocates must first construct the strongest possible version of opposing positions before critiquing them — not to simply determine a winner, but to incorporate the genuine strengths from all sides into a unified version."

Risk mitigation for sycophantic convergence (R1 in roadmap):

> "Steelman protocol, explicit 'maintain distinct positions' prompting, longer advocate prompts"

### 11.4 Transparency and Auditability

NFR-002:
> "Every decision documented with rationale in artifacts. Provenance tracking: merged output annotates which source contributed each section. Full debate transcript preserved regardless of outcome. No 'black box' decisions - all scoring visible."

### 11.5 Extensibility

NFR-004:
> "Generic protocol works with any artifact type. New agent types can participate without protocol changes. Focus areas are extensible (callers can define custom focus dimensions). Debate protocol can be extended with custom scoring rubrics via `--rubric` flag (future)."

---

## 12. Risk Management Approach

From the roadmap Risk Assessment:

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|------------|
| R1 | Sycophantic convergence | Medium | High | Steelman protocol, distinct-position prompting |
| R2 | Inconsistent quantitative metrics across artifact types | Medium | Medium | Calibrate against 3+ types, per-type weight overrides |
| R3 | Merge corrupts base document | Low | High | Post-merge validation, originals preserved |
| R4 | Parallel dispatch rate limits | Medium | Low | Sequential fallback, retry logic |
| R5 | Position-bias mitigation disagrees on many criteria | Low | Medium | Cap at 1 re-eval per criterion |
| R6 | Nearly identical Mode B outputs | Medium | Low | Detect <10% diff, skip debate |
| R7 | Very long transcripts from 10-agent deep debate | Medium | Low | Document actual usage |
| R8 | Contract mismatches with sc:roadmap v2 | Low | Medium | Define contract early, validate in M5 |

---

## 13. Key Takeaways for Building SuperClaude Features

1. **Three-layer architecture**: Command (interface) + Skill (behavior) + Agent(s) (delegation). The command is thin (~80-100 lines), the skill is substantial (~400-500 lines), and agents are focused specialists (~40-80 lines each).

2. **Skills use refs/ subdirectories**: Complex skills break their reference material into separate files under `refs/` to keep the main SKILL.md focused on behavioral instructions.

3. **Agents have strict boundaries**: Each agent definition explicitly states what it does AND does not do. The orchestrator pattern (coordinate but don't participate) prevents bias.

4. **Dynamic agent instantiation**: Not all agents are pre-defined. The adversarial feature creates advocate agents at runtime from user-provided specifications.

5. **Return contracts enable composability**: When one command invokes another, the return contract (paths, scores, status, conflicts) allows the caller to make decisions based on structured output.

6. **Framework registration is required**: New commands must update COMMANDS.md, FLAGS.md, ORCHESTRATOR.md, and PERSONAS.md to be fully integrated into the routing system.

7. **The sync-dev workflow**: All source lives in `src/superclaude/`, gets synced to `.claude/` via `make sync-dev`, and verified via `make verify-sync`.

8. **Bottom-up validation**: Each milestone produces inspectable artifacts. Test each step independently before integrating.

9. **Spec-first development**: The pipeline is: brainstorm -> spec (with panel review) -> roadmap (with milestones and risks) -> implementation (milestone by milestone).

10. **MCP integration with circuit breakers**: Each MCP server has a fallback strategy. The feature degrades gracefully rather than failing hard.
