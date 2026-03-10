# Claude Code Proposals for OpenCode-Specific Features

**Document Date**: 2026-01-26
**Purpose**: Translate OpenCode CLI features to Claude Code native implementations
**Scope**: All OpenCode-specific elements from `analysis-opencode-specific.md`

---

## Executive Summary

This document provides comprehensive proposals for translating the 10 OpenCode CLI-specific features to Claude Code native approaches. Each proposal includes:
- Detailed Claude Code native approach
- Specific feature references (Task tool, Skills, subagent patterns)
- Advantages and limitations analysis
- Implementation examples

**Translation Philosophy**: Leverage Claude Code's native skill system, Task tool for delegation, and established SuperClaude patterns rather than recreating OpenCode's command infrastructure.

---

## 1. Command System Translation

### OpenCode Approach
```
/rf:roadmap-gen <input_spec_path> [options]
```
- Custom command namespace (`/rf:`)
- Routing via `.opencode/command/rf:roadmap-gen.md`
- Orchestrator invocation pattern

### Claude Code Native Approach

**Primary Method: Skills System**

Claude Code's skill system provides the equivalent command definition capability through markdown-based skill definitions.

**Implementation Structure**:
```
.claude/skills/
  sc-roadmap-gen/
    SKILL.md              # Skill definition (equivalent to command definition)
```

**Skill Definition Example** (`SKILL.md`):
```markdown
---
name: sc:roadmap-gen
description: Generate deterministic release roadmap packages from specification documents
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---

# /sc:roadmap-gen - Roadmap Generation Command

## Purpose
Generate complete roadmap packages from specification documents with integrated quality upgrade.

## Usage
```bash
/sc:roadmap-gen @<spec_path> [options]
```

## Arguments
- `@<path>`: Path to specification file (required)
- `--version <N>`: Number of upgrade iterations (default: 2)
- `--no-upgrade`: Skip upgrade phase (equivalent to --version 1)
- `--output <dir>`: Custom output directory name

## Execution Flow
1. Parse arguments and validate inputs
2. Extract specification content (Phase 1)
3. Select persona context (Phase 2)
4. Evaluate templates (Phase 2.5)
5. Generate roadmap artifacts (Phases 3-5)
6. Self-validate (Phase 6)
7. Upgrade via multi-agent orchestration (Phase 7)
8. Validate consistency (Phase 7.5)
```

**Advantages of Claude Code Approach**:
1. **Native Integration**: Skills are first-class Claude Code features with automatic discovery
2. **Simpler Syntax**: Uses established `/sc:` namespace consistent with SuperClaude
3. **Tool Declarations**: `allowed-tools` header enables tool access without custom routing
4. **Version Control**: Skills live alongside code in repository structure

**Limitations**:
- No custom argument parsing infrastructure (handled manually in skill body)
- No separate routing layer (skill body contains all logic)

**Implementation Example**:
```bash
# User invokes
/sc:roadmap-gen @specs/v3.0-release.md --version 2

# Claude Code
1. Loads skill from .claude/skills/sc-roadmap-gen/SKILL.md
2. Follows behavioral instructions in skill body
3. Has access to declared tools
```

---

## 2. Agent System Translation

### OpenCode Approach
```
.opencode/agent/
  rf-roadmap-gen-orchestrator.md     # Main pipeline coordinator
  rf-roadmap-gen-template-scorer.md  # Template evaluation
```
- Agent files define prompts and model configurations
- Orchestrator coordinates multi-phase execution
- Specialized agents for domain-specific tasks

### Claude Code Native Approach

**Primary Method: Task Tool with subagent_type**

Claude Code's Task tool provides native sub-agent delegation with specialized personalities.

**Agent Pattern Mapping**:
| OpenCode Agent | Claude Code Equivalent |
|----------------|------------------------|
| Orchestrator | Parent skill + TodoWrite coordination |
| Template Scorer | `Task` with `subagent_type: "code-reviewer"` or custom |
| Validators | `Task` with `subagent_type: "quality-engineer"` |
| Domain Extractors | `Task` with domain context |

**Implementation Structure**:
```yaml
# Instead of separate agent files, agents are invoked inline:

# Orchestrator pattern - in main skill body
1. Use TodoWrite for phase tracking
2. Execute phases with tool calls
3. Delegate specialized tasks via Task tool

# Specialized agent delegation
Task tool invocation:
  description: "Evaluate template suitability for extraction content"
  context: <extraction_content + persona_context>
  subagent_type: "code-reviewer"  # or appropriate type
```

**Template Scorer Agent Equivalent**:
```markdown
# In skill execution, use Task for scorer:

For template evaluation, invoke Task:
- Description: "Score each template against extraction content and persona"
- Provide: template paths, extraction.md content, persona selection
- Request: structured scores (0-100), recommendation (USE|VARIANT_CANDIDATE), rationale
- subagent_type: "code-reviewer" (for structured analysis)
```

**Orchestrator Pattern Implementation**:
```markdown
## Execution (Orchestrator Behavior)

### Phase Management
Use TodoWrite to track phase execution:

Phase 0: Preflight Validation
  - Validate spec file exists
  - Check output directory writability
  - Mark phase complete

Phase 1-6: Generation
  - Execute each phase sequentially
  - Update TodoWrite status
  - Capture outputs to .roadmaps/<version>/

Phase 7: Multi-Agent Upgrade
  - Spawn parallel Task agents for each artifact
  - subagent_type: "quality-engineer"
  - Coordinate results

Phase 7.5: Consistency Validation
  - Single Task agent validates cross-artifact consistency
```

**Advantages**:
1. **Native Delegation**: Task tool is purpose-built for sub-agent work
2. **Parallel Execution**: Multiple Task invocations can run concurrently
3. **Built-in Types**: `subagent_type` provides specialized agent behaviors
4. **Context Isolation**: Each Task has clean context boundaries

**Limitations**:
- No explicit model configuration (gpt-5.2, claude-sonnet) per agent
- Agent prompts embedded in skill rather than separate files
- No cross-session agent state (handled via Serena memory)

**Implementation Example**:
```markdown
# Template Scorer Delegation

When executing Phase 2.5:

1. Load templates via Glob: `.claude/resources/templates/roadmaps/*.md`
2. For each template, invoke Task:
   ```
   Task: "Score template compatibility"
   Context:
     - Template: <template_content>
     - Extraction: <extraction.md content>
     - Persona: <selected_persona>
   Expected Output: JSON with score (0-100), recommendation, rationale
   ```
3. Aggregate scores, select highest or create variant
```

---

## 3. Directory Structure Translation

### OpenCode Approach
```
.opencode/                    # OpenCode config directory
  command/                    # Command definitions
  agent/                      # Agent prompts
  resources/templates/        # Template files
.dev/                         # Development/test directory
  runs/rf-crossLLM/           # Execution outputs
.roadmaps/                    # Output directory
```

### Claude Code Native Approach

**Directory Mapping**:
| OpenCode Path | Claude Code Equivalent | Purpose |
|---------------|------------------------|---------|
| `.opencode/command/` | `.claude/skills/` or `src/superclaude/commands/` | Command/skill definitions |
| `.opencode/agent/` | Embedded in skills OR `.claude/agents/` | Agent prompts (inline) |
| `.opencode/resources/templates/` | `.claude/resources/templates/` | Template files |
| `.dev/runs/` | `.claudedocs/` or project-specific | Execution outputs |
| `.dev/mocks/` | `tests/fixtures/` | Test fixtures |
| `.roadmaps/` | `.roadmaps/` (preserve) | Output directory (unchanged) |

**Recommended Structure**:
```
.claude/
  settings.json               # User settings
  skills/
    sc-roadmap-gen/
      SKILL.md               # Main skill definition
  resources/
    templates/
      roadmaps/
        feature-release.md
        quality-release.md
        documentation-release.md
        variants/
  agents/                    # Optional: reusable agent prompts
    template-scorer.md
    consistency-validator.md

.roadmaps/                   # Output directory (unchanged)
  <release-name>/
    v1/                      # Draft version
    v2/                      # Upgraded version

.claudedocs/                 # Claude-generated documentation
  execution-logs/
  analysis-reports/

tests/
  fixtures/                  # Test fixtures (replaces .dev/mocks)
```

**Key Decisions**:

1. **Skills Directory**: Use `.claude/skills/` for skill definitions - this is the Claude Code standard location for project-local skills.

2. **Resources**: Create `.claude/resources/` for templates - consistent with Claude Code conventions and discoverable by skills.

3. **Agent Prompts**:
   - **Option A**: Embed in skill body (simpler, single-file)
   - **Option B**: Create `.claude/agents/` for reusable prompts (when agents are shared across skills)

4. **Outputs**:
   - Keep `.roadmaps/` as-is for generated content
   - Use `.claudedocs/` for Claude-generated analysis and logs

**Advantages**:
1. **Standard Locations**: Uses Claude Code expected directories
2. **Discoverable**: Skills auto-discovered from `.claude/skills/`
3. **Clean Separation**: Templates, agents, outputs all have clear homes
4. **Test Integration**: Fixtures in `tests/` work with pytest

**Implementation Example**:
```bash
# Skill accesses templates
Glob: ".claude/resources/templates/roadmaps/*.md"

# Output to roadmaps
Write: ".roadmaps/my-release/v1/roadmap.md"

# Execution log
Write: ".claudedocs/execution-logs/roadmap-gen-2026-01-26.md"
```

---

## 4. Command Flags Translation

### OpenCode Approach
```
--chain <model_chain>       # Model selection
--no-upgrade                # Skip upgrade phase
--upgrade-only <artifacts>  # Selective upgrade
--upgrade-threshold <N>     # Quality threshold
--version <N>               # Iteration count
--parallel-upgrades         # Parallel execution
--sequential-upgrades       # Sequential execution
--output <dir>              # Output directory
```

### Claude Code Native Approach

**Flag Handling Strategy**: Parse flags in skill body using simple string matching or leverage SuperClaude's existing flag infrastructure.

**Method 1: Inline Parsing**
```markdown
## Argument Parsing

When invoked as `/sc:roadmap-gen @<path> [options]`:

1. Extract spec path from first @-prefixed argument
2. Parse flags:
   - `--version <N>`: Extract N, default 2
   - `--no-upgrade`: Set version to 1
   - `--output <dir>`: Extract directory name
   - `--parallel` / `--sequential`: Set execution mode

Example parsing logic:
- If arguments contain "--no-upgrade": version = 1
- If arguments match "--version (\d+)": version = captured number
- If arguments match "--output (\S+)": output_dir = captured string
```

**Method 2: SuperClaude FLAGS.md Integration**

Leverage existing SuperClaude flag system from `.claude/FLAGS.md`:

```yaml
# Add to FLAGS.md for roadmap-gen specific flags

**--roadmap-version [N]**
- Trigger: /sc:roadmap-gen command
- Behavior: Set upgrade iteration count (1-5)

**--no-upgrade**
- Trigger: /sc:roadmap-gen command
- Behavior: Skip upgrade phase entirely (version 1 only)

**--parallel-upgrades** (default)
- Trigger: /sc:roadmap-gen with multiple artifacts
- Behavior: Upgrade artifacts in parallel via concurrent Task agents

**--sequential-upgrades**
- Trigger: Debugging or dependency-ordered upgrades
- Behavior: Process artifacts one at a time
```

**Flag-to-Behavior Mapping**:
| OpenCode Flag | Claude Code Translation | Implementation |
|---------------|------------------------|----------------|
| `--chain <model>` | N/A (Claude Code model is fixed) | Handled via multi-agent debate pattern |
| `--version <N>` | `--roadmap-version <N>` | Version folder naming |
| `--no-upgrade` | `--no-upgrade` | Skip Phase 7/7.5 |
| `--parallel-upgrades` | Default behavior | Concurrent Task invocations |
| `--sequential-upgrades` | `--sequential` | Force sequential processing |
| `--output <dir>` | `--output <dir>` | Directory naming |
| `--upgrade-threshold` | Skill configuration | Quality gate in upgrade logic |

**Advantages**:
1. **Consistency**: Follows SuperClaude flag conventions
2. **Documentation**: Flags documented in central FLAGS.md
3. **Extensibility**: Easy to add new flags

**Limitations**:
- No automatic flag validation (skill must validate)
- Complex flag parsing done manually in skill

**Implementation Example**:
```markdown
## Flag Processing

Parse `$ARGUMENTS` for recognized flags:

```pseudocode
version = 2  # default
output = basename(spec_path)
parallel = true

if "--no-upgrade" in args:
    version = 1
elif match "--version (\d+)" in args:
    version = captured_int

if "--output" in args:
    output = next_arg_after("--output")

if "--sequential" in args:
    parallel = false
```
```

---

## 5. CrossLLM Integration Translation

### OpenCode Approach
```
/rf:crossLLM v2 file <chain> <artifact_path>
```
- Invokes separate crossLLM command
- Multi-model adversarial debate (claude > gpt, gpt > gemini)
- Output to `.dev/runs/rf-crossLLM/<runId>/`
- Returns `upgrade.md` and `scorecard.md`

### Claude Code Native Approach

**Strategy**: Implement multi-perspective quality upgrade using Claude Code's Task tool for parallel expert review.

**Pattern: Multi-Agent Quality Debate**

Instead of cross-model orchestration, use multiple Task agents with different reviewer perspectives:

```markdown
## Multi-Perspective Upgrade Pattern

### Expert Reviewer Agents

For each artifact upgrade, spawn 3 Task agents in parallel:

1. **Critic Agent** (subagent_type: "code-reviewer")
   - Focus: Find weaknesses, gaps, inconsistencies
   - Output: List of issues with severity ratings

2. **Enhancer Agent** (subagent_type: "code-reviewer")
   - Focus: Propose improvements and additions
   - Input: Original artifact + Critic's issues
   - Output: Proposed enhancements

3. **Judge Agent** (subagent_type: "quality-engineer")
   - Focus: Evaluate proposals, synthesize final version
   - Input: Original + Critic feedback + Enhancer proposals
   - Output: Final upgraded artifact + scorecard

### Execution Flow
```
Original Artifact
       |
       v
[Critic] [Enhancer] (parallel)
       |
       v
    [Judge]
       |
       v
Upgraded Artifact + Scorecard
```
```

**Implementation Structure**:
```markdown
### Upgrade Protocol

For artifact_path:

1. Copy to artifact.draft.md (preserve original)

2. Spawn Critic Task:
   Description: "Critically analyze this roadmap artifact for gaps, inconsistencies, unclear sections"
   Context: <artifact content>
   Expected: JSON with issues array [{description, severity, location}]

3. Spawn Enhancer Task:
   Description: "Propose improvements addressing these issues"
   Context: <artifact + critic_output>
   Expected: JSON with enhancements array [{issue_ref, proposed_change, rationale}]

4. Spawn Judge Task:
   Description: "Synthesize final improved version"
   Context: <artifact + critic + enhancer outputs>
   Expected: {upgraded_content: string, scorecard: {result: PASS|FAIL, improvements: [], score: N}}

5. If scorecard.result == PASS and score > threshold:
   - Replace artifact with upgraded_content
   - Save scorecard.md
   - Log upgrade result

6. If FAIL:
   - Keep draft as canonical
   - Log warning with scorecard rationale
```

**Output Structure**:
```
.roadmaps/<release>/v2/
  roadmap.md               # Upgraded version
  roadmap.draft.md         # Pre-upgrade backup
  upgrade-log.md           # Upgrade results

.claudedocs/upgrade-runs/<timestamp>/
  critic-output.json       # Critic agent output
  enhancer-output.json     # Enhancer agent output
  judge-scorecard.json     # Final judgment
```

**Advantages**:
1. **Single Model**: Uses Claude throughout (no model coordination)
2. **Parallel Processing**: Multiple Task agents run concurrently
3. **Structured Output**: JSON outputs for parsing
4. **Auditability**: Full record of debate/enhancement process

**Limitations**:
- No actual cross-model debate (single Claude model)
- May lack diversity of "opinions" vs true multi-model
- Relies on prompt engineering for perspective differentiation

**Mitigation for Model Diversity**:
```markdown
# Use persona differentiation in Task descriptions

Critic Task Persona:
  "You are a skeptical technical reviewer. Your job is to find flaws."

Enhancer Task Persona:
  "You are an experienced technical writer focused on clarity and completeness."

Judge Task Persona:
  "You are an impartial arbiter weighing evidence from multiple perspectives."
```

---

## 6. MCP Integration Translation

### OpenCode Approach
```
Sequential Thinking MCP for CoT-based algorithm design
- Used in template scoring criteria development
- Referenced at specification Lines 219, 696, 697
```

### Claude Code Native Approach

**Claude Code MCP Support**:
Claude Code has native MCP server integration. The Sequential Thinking MCP is already referenced in SuperClaude's MCP.md documentation.

**Direct Integration**:
```markdown
## MCP Server Usage in Roadmap Gen

### Sequential Thinking Integration

Use mcp__sequential-thinking__sequentialthinking for:
- Template scoring algorithm design (Phase 2.5)
- Cross-artifact consistency analysis (Phase 7.5)
- Complex reasoning requiring structured breakdown

Invocation Example:
```
mcp__sequential-thinking__sequentialthinking:
  thought: "Analyzing template compatibility: first factor is domain alignment..."
  thoughtNumber: 1
  totalThoughts: 5
  nextThoughtNeeded: true
```

### Serena MCP Integration

Use Serena for project memory and session persistence:
- mcp__serena__activate_project: Load project context
- mcp__serena__write_memory: Store extraction results
- mcp__serena__find_symbol: Navigate codebase structure
- mcp__serena__list_memories: Check existing state

### Context7 Integration

Use for template pattern lookup:
- Retrieve official documentation patterns
- Get best practices for roadmap structures
```

**MCP Coordination Pattern**:
```markdown
### Phase 2.5: Template Evaluation with MCP

1. Load templates via Glob
2. For each template, use Sequential Thinking to:
   - Decompose scoring into factors
   - Weight each factor based on context
   - Calculate composite score

3. Use Serena to:
   - Store scoring results in memory
   - Enable cross-session template learning

4. Output template-selection.md with:
   - Scores for each template
   - Selection rationale
   - MCP reasoning trail
```

**Advantages**:
1. **Native Support**: Claude Code already integrates MCP servers
2. **SuperClaude Patterns**: Existing MCP.md documents usage patterns
3. **Tool Orchestration**: MCP calls are first-class tool invocations

**Implementation Reference**:
```yaml
# From SuperClaude MCP.md patterns

sequential_workflow:
  - Use for complexity > 0.7
  - Pair with --think or --ultrathink flags
  - Coordinate with other MCP servers

serena_workflow:
  - Activate project at session start
  - Write memories after major phases
  - Read memories before dependent phases
```

---

## 7. Template System Translation

### OpenCode Approach
```
.opencode/resources/templates/roadmaps/
  feature-release.md
  quality-release.md
  documentation-release.md
  variants/
```
- Template Scorer Agent evaluates compatibility
- 80% threshold for direct use
- Variant creation when no match

### Claude Code Native Approach

**Template Location**:
```
.claude/resources/templates/roadmaps/
  feature-release.md
  quality-release.md
  documentation-release.md
  variants/             # Auto-generated variants
```

**Template Loading Pattern**:
```markdown
## Template System

### Template Discovery

Load available templates:
```
Glob: ".claude/resources/templates/roadmaps/*.md"
```
Returns: List of template paths

### Template Structure

Each template follows section-based overlay pattern:

```markdown
---
name: feature-release
domain: feature, enhancement, API
required-sections: [summary, milestones, success-criteria, dependencies, risks]
optional-sections: [api-changes, migration-notes, deprecations]
---

# [RELEASE_NAME] Roadmap

## Executive Summary
[Generated from extraction]

## Milestones
[Phase-based breakdown]

## Success Criteria
[Measurable outcomes]

<!-- OPTIONAL: api-changes -->
## API Changes
[If applicable]
<!-- /OPTIONAL -->
```
```

**Template Scoring Implementation**:
```markdown
### Template Evaluation (Phase 2.5)

For each template:

1. Parse template frontmatter for domain tags
2. Compare domain tags with extraction domain distribution
3. Check required section coverage
4. Calculate compatibility score:

   Score Factors:
   - Domain alignment: 40%
   - Structure fit: 30%
   - Complexity match: 20%
   - Optional section relevance: 10%

5. If best_score >= 80:
   - Select template
   - Note activated optional sections

6. If best_score < 80:
   - Use best template as base
   - Create variant with adjustments
   - Save to variants/ with timestamp
   - Log creation rationale
```

**Template Resource Management**:
```markdown
## Resource Management

### Reading Templates
Use Read tool with absolute paths:
```
Read: ".claude/resources/templates/roadmaps/feature-release.md"
```

### Creating Variants
```
Write: ".claude/resources/templates/roadmaps/variants/feature-release-v1-2026-01-26.md"
Content: Modified template with activated/deactivated sections
```

### Template Cache
Consider caching parsed templates in session for reuse:
```
Serena write_memory: "template_cache"
Content: {parsed templates with scores}
```
```

**Advantages**:
1. **Standard Location**: `.claude/resources/` follows conventions
2. **YAML Frontmatter**: Easy parsing for metadata
3. **Optional Sections**: Marker-based activation/deactivation
4. **Version Tracking**: Variants include timestamps

---

## 8. Quality Gates Translation

### OpenCode Approach
```
- Integration tests reference .dev/mocks/crossLLM/
- Mock responses for /rf:crossLLM command execution
- Test constraint: NO writes outside .dev/ or .roadmaps/
- Phase 6: Self-Validation (traceability verification)
- Phase 7.5: Cross-Artifact Consistency validation
```

### Claude Code Native Approach

**Quality Gate Implementation**:

```markdown
## Quality Gate System

### Gate 1: Preflight Validation (Phase 0)

Validate before any generation:
```
checks:
  - spec_file_exists: Read spec_path, verify content
  - output_dir_writable: Bash "touch .roadmaps/test && rm .roadmaps/test"
  - no_version_conflict: Check if version folder exists
  - required_tools_available: Verify Glob, Read, Write access
```

### Gate 2: Self-Validation (Phase 6)

Post-generation traceability check:
```
checks:
  - extraction_coverage: All items in extraction.md appear in roadmap.md
  - id_uniqueness: No duplicate IDs across artifacts
  - reference_validity: All cross-references point to existing items
  - completeness: Required sections present in each artifact

Implementation:
1. Parse extraction.md for all item IDs
2. Parse roadmap.md for item references
3. Verify bijective mapping
4. Report any mismatches
```

### Gate 3: Upgrade Quality (Phase 7)

Quality threshold for accepting upgrades:
```
threshold: 25  # Minimum improvement percentage

checks:
  - improvement_score: Must exceed threshold
  - no_regressions: No removed content without replacement
  - consistency: Upgraded content maintains artifact structure
  - scorecard_pass: Judge agent returns PASS
```

### Gate 4: Cross-Artifact Consistency (Phase 7.5)

Post-upgrade validation:
```
checks:
  - id_reference_integrity: All IDs in test-strategy exist in roadmap
  - coverage_completeness: All deliverables have test coverage
  - structural_alignment: Milestone hierarchy matches across artifacts
  - naming_consistency: Deliverable names match (allow minor variations)

Implementation:
1. Parse all v2 artifacts
2. Build reference maps
3. Check each consistency rule
4. Generate consistency-report.md with findings
```
```

**Test Fixtures Pattern**:
```markdown
## Test Fixtures

Location: tests/fixtures/roadmap-gen/

Structure:
```
tests/fixtures/roadmap-gen/
  valid-spec.md           # Standard valid specification
  minimal-spec.md         # Minimum viable specification
  invalid-spec.md         # Missing required sections
  mock-templates/
    feature-release.md
    quality-release.md
  expected-outputs/
    extraction.md
    roadmap.md
```

Usage in tests:
```python
@pytest.fixture
def valid_spec(fixture_path):
    return fixture_path / "roadmap-gen" / "valid-spec.md"

def test_extraction_phase(valid_spec):
    # Test extraction against valid spec
    result = extract_spec(valid_spec)
    assert result.items_count > 0
```
```

**Write Constraint Implementation**:
```markdown
## Safe Execution Zone

Skill must enforce write boundaries:

Allowed Write Paths:
- .roadmaps/           # Output directory
- .claudedocs/         # Analysis outputs
- tests/fixtures/      # Test generation only

Prohibited Write Paths:
- src/                 # Source code
- .claude/             # Configuration (except designated areas)
- Root directory files

Implementation:
Before any Write operation, validate path prefix:
```pseudocode
if not (path.startswith(".roadmaps/") or
        path.startswith(".claudedocs/") or
        path.startswith("tests/fixtures/")):
    STOP with error: "Write outside safe zone: {path}"
```
```

**Advantages**:
1. **Explicit Gates**: Clear checkpoint definitions
2. **Pytest Integration**: Fixtures work with SuperClaude test infrastructure
3. **Safe Zones**: Explicit path restrictions prevent accidents

---

## 9. Model Configuration Translation

### OpenCode Approach
```yaml
orchestrator:
  model: gpt-5.2
  temperature: 0.1
  tools: [bash, read, write, edit, list, glob, grep, task]

template_scorer:
  model: claude-sonnet-4-5
  temperature: 0.1
  tools: [read, glob]
```

### Claude Code Native Approach

**Model Selection Reality**: Claude Code runs on Claude models exclusively. The multi-model crossLLM pattern doesn't directly translate.

**Translation Strategy**:

```markdown
## Model and Configuration

### Claude Code Model
Claude Code uses the session's Claude model (currently Claude Opus 4.5 or similar).
No per-agent model selection is available.

### Behavioral Configuration via Prompts

Instead of model selection, configure behavior through:

1. **Temperature-equivalent**: Use prompting for determinism
   ```
   "Provide a deterministic, consistent analysis. Avoid creative interpretation."
   ```

2. **Tool Access**: Defined in skill header
   ```yaml
   allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
   ```

3. **Agent Role**: Embedded in Task descriptions
   ```
   Task: "You are a template scorer. Evaluate systematically..."
   ```
```

**Configuration Mapping**:
| OpenCode Config | Claude Code Equivalent |
|-----------------|------------------------|
| `model: gpt-5.2` | N/A (Claude model fixed) |
| `temperature: 0.1` | Prompt: "Be deterministic and consistent" |
| `tools: [read, glob]` | `allowed-tools: Read, Glob` in skill |
| Agent prompt file | Inline in Task description or skill body |

**Deterministic Behavior Pattern**:
```markdown
## Ensuring Consistent Output

For scorer agents requiring deterministic output:

Task Description Pattern:
```
"Score templates against the following criteria. Provide scores on a 0-100 scale.
Be systematic and consistent. Use the exact criteria provided without creative interpretation.
Output in JSON format with no additional commentary."
```

For orchestrator phases:
```
"Execute phases in exact order. Do not skip or reorder phases.
Document each phase completion before proceeding."
```
```

**Advantages**:
1. **Simplicity**: No model management complexity
2. **Consistency**: Same model throughout eliminates compatibility issues
3. **Prompt Control**: Behavior controlled via clear instructions

**Limitations**:
- Cannot leverage model diversity
- No A/B testing across models
- Single-model "blind spots" not mitigated

**Mitigation via Perspective Diversity**:
```markdown
## Pseudo-Multi-Model via Perspectives

Use different prompting perspectives to simulate model diversity:

Perspective 1 - "Skeptical Analyst":
"Assume the worst. What could go wrong with this artifact?"

Perspective 2 - "Optimistic Enhancer":
"Assume good intent. How can this be made even better?"

Perspective 3 - "Neutral Judge":
"Weigh both perspectives. What is the balanced truth?"
```

---

## 10. Documentation Output Translation

### OpenCode Approach
```
docs/generated/Commands/roadmap-gen_UserDoc.md
docs/generated/Commands/roadmap-gen_TD.md
docs/generated/crossLLM-Integration-Protocol.md
```

### Claude Code Native Approach

**Documentation Structure**:
```
docs/
  user-guide/
    roadmap-gen.md           # User documentation
  reference/
    roadmap-gen-technical.md # Technical specification
    integration-protocol.md  # Reusable integration pattern
  generated/
    roadmap-outputs/         # Links to generated roadmaps
```

**Auto-Generation Pattern**:
```markdown
## Documentation Generation

### Phase 8: Documentation (Optional Post-Phase)

After successful roadmap generation, optionally generate:

1. **Execution Summary**
   Path: .claudedocs/roadmap-gen-runs/<timestamp>/summary.md
   Content: Phases executed, timing, upgrade results

2. **Template Usage Log**
   Path: .claudedocs/roadmap-gen-runs/<timestamp>/template-log.md
   Content: Template selected, sections activated, variant created

3. **Quality Report**
   Path: .roadmaps/<release>/<version>/quality-report.md
   Content: Gate results, consistency findings, recommendations
```

**User Documentation Template**:
```markdown
# /sc:roadmap-gen User Guide

## Overview
Generate release roadmap packages from specification documents.

## Quick Start
```bash
/sc:roadmap-gen @specs/my-release.md
```

## Arguments
| Argument | Required | Description | Default |
|----------|----------|-------------|---------|
| `@<path>` | Yes | Path to specification | - |
| `--version <N>` | No | Upgrade iterations | 2 |
| `--no-upgrade` | No | Skip upgrade phase | false |
| `--output <dir>` | No | Output directory | spec filename |

## Examples
[Usage examples with expected outputs]

## Output Structure
[Description of generated files]
```

**Technical Documentation Template**:
```markdown
# /sc:roadmap-gen Technical Specification

## Architecture
[Component overview with flow diagram]

## Phases
[Detailed phase descriptions]

## Quality Gates
[Gate definitions and requirements]

## MCP Integration
[Server usage patterns]

## Extension Points
[How to customize or extend]
```

**Advantages**:
1. **Consistent Structure**: Follows SuperClaude docs organization
2. **Separation of Concerns**: User guide vs technical spec
3. **Execution Logs**: Captured in .claudedocs for analysis

---

## Summary: Translation Matrix

| # | OpenCode Feature | Claude Code Translation | Primary Tools |
|---|-----------------|------------------------|---------------|
| 1 | Command System (`/rf:`) | Skills (`.claude/skills/`) | Skill loader |
| 2 | Agent System | Task tool + subagent_type | Task |
| 3 | Directory Structure | `.claude/` conventions | Glob, Read, Write |
| 4 | Command Flags | Inline parsing + FLAGS.md | Argument parsing |
| 5 | crossLLM Integration | Multi-perspective Task agents | Task (parallel) |
| 6 | MCP Integration | Native MCP support | mcp__* tools |
| 7 | Template System | `.claude/resources/` | Read, Glob, Write |
| 8 | Quality Gates | Validation phases + pytest | TodoWrite, Task |
| 9 | Model Configuration | Prompt-based behavior | Task descriptions |
| 10 | Documentation Output | docs/ + .claudedocs/ | Write |

## Implementation Priorities

**Phase 1: Foundation**
1. Create skill structure at `.claude/skills/sc-roadmap-gen/`
2. Implement argument parsing in skill body
3. Set up resource directories

**Phase 2: Core Generation**
4. Implement phases 1-6 in skill
5. Create starter templates
6. Add quality gates

**Phase 3: Multi-Agent Upgrade**
7. Implement multi-perspective upgrade pattern
8. Add consistency validation
9. Create upgrade log format

**Phase 4: Documentation**
10. Generate user documentation
11. Create technical specification
12. Add to SuperClaude docs structure

---

*Document generated for SuperClaude v4.1.9 translation effort*
*Based on analysis of OpenCode CLI v3.0 Roadmap-Generator Specification*
