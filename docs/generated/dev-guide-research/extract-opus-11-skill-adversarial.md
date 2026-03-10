# Extraction: sc-adversarial Skill Pattern for SuperClaude Framework

## Source Files

| # | File | Purpose |
|---|------|---------|
| 1 | `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-adversarial/SKILL.md` | Main skill definition (1747 lines) |
| 2 | `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-adversarial/refs/agent-specs.md` | Agent specification reference |
| 3 | `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-adversarial/refs/scoring-protocol.md` | Hybrid scoring algorithm reference |
| 4 | `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-adversarial/refs/debate-protocol.md` | 5-step debate protocol reference |
| 5 | `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-adversarial/refs/artifact-templates.md` | Output format templates |
| 6 | `/config/workspace/SuperClaude_Framework/src/superclaude/commands/adversarial.md` | Slash command entry point |
| 7 | `/config/workspace/SuperClaude_Framework/src/superclaude/agents/debate-orchestrator.md` | Orchestrator agent definition |
| 8 | `/config/workspace/SuperClaude_Framework/src/superclaude/agents/merge-executor.md` | Merge specialist agent definition |
| 9 | `/config/workspace/SuperClaude_Framework/src/superclaude/cli/install_skill.py` | Skill installation logic |
| 10 | `/config/workspace/SuperClaude_Framework/src/superclaude/cli/install_skills.py` | Batch skill installation |

---

## 1. Complete Directory Layout as a Reusable Pattern

### Actual sc-adversarial Layout

```
src/superclaude/
├── skills/
│   └── sc-adversarial/               # Skill package directory
│       ├── __init__.py                # Empty file (Python package marker)
│       ├── SKILL.md                   # PRIMARY: Full skill definition
│       └── refs/                      # REFERENCE DOCS: Protocol details
│           ├── agent-specs.md         # Agent specification patterns
│           ├── artifact-templates.md  # Output format templates
│           ├── debate-protocol.md     # Core protocol steps
│           └── scoring-protocol.md    # Scoring algorithm details
├── commands/
│   └── adversarial.md                 # Slash command entry point
└── agents/
    ├── debate-orchestrator.md         # Coordinating agent
    └── merge-executor.md              # Specialist agent
```

### Generalized Skill Directory Pattern

```
src/superclaude/
├── skills/
│   └── sc-<skill-name>/              # Convention: sc- prefix for slash-command skills
│       ├── __init__.py                # Empty Python package marker
│       ├── SKILL.md                   # REQUIRED: Main skill definition
│       └── refs/                      # OPTIONAL: Supporting reference documents
│           ├── <protocol>.md          # Protocol/process definitions
│           ├── <templates>.md         # Output format templates
│           ├── <specs>.md             # Input/configuration specifications
│           └── <algorithm>.md         # Algorithm/scoring details
├── commands/
│   └── <skill-name>.md               # Corresponding slash command (without sc- prefix)
└── agents/
    └── <agent-name>.md               # Any agents the skill delegates to
```

### Installation Behavior

Skills whose directory name starts with `sc-` and have a corresponding command file (`commands/<name>.md`) are served via `/sc:<name>` commands and are NOT installed as separate skills to `~/.claude/skills/`. From `install_skills.py`:

```python
def _has_corresponding_command(skill_name: str) -> bool:
    """Check if an sc-* skill has a matching slash command."""
    if not skill_name.startswith("sc-"):
        return False
    cmd_name = skill_name[3:]  # strip "sc-" prefix
    package_root = Path(__file__).resolve().parent.parent
    return (package_root / "commands" / f"{cmd_name}.md").exists()
```

Skills without the `sc-` prefix (e.g., `confidence-check`) are installed as standalone skills to `~/.claude/skills/`.

### Skill Validation

A directory is recognized as a valid skill if it contains `SKILL.md`, `skill.md`, or `implementation.md`. From `install_skill.py`:

```python
def _is_valid_skill_dir(path: Path) -> bool:
    manifest_files = {"SKILL.md", "skill.md", "implementation.md"}
    if any((path / manifest).exists() for manifest in manifest_files):
        return True
    # Otherwise check for any content files (ts/py/etc.)
    for item in path.iterdir():
        if item.is_file() and item.suffix in {".ts", ".js", ".py", ".json"}:
            return True
    return False
```

---

## 2. SKILL.md Structure and Format

The SKILL.md file is the primary skill definition. It uses YAML frontmatter followed by structured markdown. The sc-adversarial SKILL.md is 1747 lines and serves as both specification and implementation guide.

### 2.1 YAML Frontmatter (Required)

```yaml
---
name: sc:adversarial
description: Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

The three required frontmatter fields are:
- **`name`**: The skill/command name (uses `sc:` prefix with colon for namespaced commands)
- **`description`**: One-line description of what the skill does
- **`allowed-tools`**: Comma-separated list of Claude Code tools the skill is permitted to use

### 2.2 Extended Metadata (HTML Comment, Optional)

```html
<!-- Extended metadata (for documentation, not parsed):
category: analysis
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [architect, analyzer, scribe]
-->
```

This provides additional metadata that is not parsed by the runtime but documents category, complexity level, MCP server dependencies, and persona integrations.

### 2.3 Section Structure

The SKILL.md follows this ordered section structure:

1. **Purpose** -- What the skill does and its core objective
2. **Required Input** -- Mandatory flags/arguments (with `MANDATORY` callout)
3. **Triggers** -- How the skill is activated (explicit, keywords, integration)
4. **Dual Input Modes** -- Multiple operational modes (Mode A, Mode B)
5. **N-Step Protocol** -- The core pipeline with numbered steps
6. **Configurable Parameters** -- Flag table with defaults and ranges
7. **Interactive Mode** -- User interaction checkpoints
8. **Artifact Output Structure** -- Directory layout of outputs
9. **Error Handling Matrix** -- YAML-based error scenarios and behaviors
10. **Return Contract** -- Structured output for programmatic integration
11. **Agent Delegation** -- Agent roles, models, tools, responsibilities
12. **MCP Integration** -- MCP server usage by step
13. **Compliance Tier Classification** -- Default compliance level
14. **Boundaries** -- Will Do / Will Not Do lists
15. **Implementation Details** -- Deep per-step specifications (bulk of file)

### 2.4 Key Structural Patterns in SKILL.md

#### Purpose Section Pattern

```markdown
## Purpose

Generic, reusable command implementing a structured adversarial debate, comparison,
and merge pipeline. [...]

**Core Objective**: Verify and validate accuracy of statements in generated artifacts,
weeding out hallucinations and sycophantic agreement through structured adversarial
pressure using steelman debate strategy.

**Key Differentiator**: Uses multi-model adversarial reasoning (10-15% accuracy gains,
30%+ factual error reduction) as a generic framework tool invocable by any SuperClaude command.
```

#### Protocol Step Pattern

Each step in the pipeline follows this template:

```markdown
### Step N: <Step Name>

**Input**: <what this step receives>
**Delegation**: <which agent/tool handles it>
**Process**:

\```yaml
<step_name>:
  <sub_operation>:
    action: "<what to do>"
    output: "<what it produces>"
\```

**Output**: `adversarial/<artifact-name>.md` -- <description>
**Template**: See `refs/artifact-templates.md` Section N
```

#### Error Handling Matrix Pattern

```yaml
error_handling:
  <scenario_name>:
    behavior: "<what to do>"
    constraint: "<limits>"
    fallback: "<if behavior fails>"

  <scenario_name>:
    threshold: "<detection criterion>"
    behavior: "<response>"
    log: "<what to record>"
```

#### Return Contract Pattern

```yaml
return_contract:
  merged_output_path: "<path to merged file>"
  convergence_score: "<final convergence percentage>"
  artifacts_dir: "<path to adversarial/ directory>"
  status: "success | partial | failed"
  unresolved_conflicts: ["<list of unresolved items>"]
```

#### Parameter Table Pattern

```markdown
| Parameter | Flag | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| Depth | `--depth` | `standard` | quick/standard/deep | Controls debate rounds |
| Convergence | `--convergence` | `0.80` | 0.50-0.99 | Alignment threshold |
```

### 2.5 Implementation Details Section Pattern

The Implementation Details section is the largest part of the SKILL.md (approximately 1000+ lines). It provides step-by-step, sub-task-level YAML specifications. Each sub-task is tagged with a task ID (e.g., T03.01, T04.02):

```markdown
## Implementation Details -- Step 2: Adversarial Debate Protocol

### Advocate Agent Instantiation (T03.01)

\```yaml
advocate_instantiation:
  per_agent_spec:
    parse:
      - "Extract model (required): first segment before ':'"
      - "Extract persona (optional): second segment"
    validate:
      model: "Must be recognized"
  prompt_generation:
    template: |
      You are an advocate agent in a structured adversarial debate.
      ...
\```
```

---

## 3. How the refs/ Subdirectory Is Used

The `refs/` directory contains reference documents that decompose the SKILL.md's complexity into focused, reusable protocol documents. Each ref is cross-referenced from the SKILL.md using explicit path references.

### 3.1 Cross-Reference Pattern in SKILL.md

```markdown
**Reference**: See `refs/scoring-protocol.md` for complete algorithm
**Template**: See `refs/artifact-templates.md` Section 4
```

### 3.2 Reference Document Roles

| File | Role | Content Type |
|------|------|-------------|
| `refs/agent-specs.md` | Agent specification format and behavior rules | Input/config specification |
| `refs/scoring-protocol.md` | Complete hybrid scoring algorithm | Algorithm definition |
| `refs/debate-protocol.md` | 5-step protocol overview and flow | Process protocol |
| `refs/artifact-templates.md` | Output format specifications for all artifacts | Template definitions |

### 3.3 Reference Document Structure Pattern

Each reference document follows this structure:

```markdown
# <Title> Reference

<One-line description of what this reference covers.>

---

## Section N: <Topic>

### <Subsection>

\```yaml
<specification_in_yaml>
\```

---

*Reference document for sc:adversarial skill*
*Source: SC-ADVERSARIAL-SPEC.md <Section reference>*
```

The footer line citing the source specification document is a consistent pattern across all refs.

### 3.4 Factoring Strategy

The refs/ directory factors out content by concern:
- **Protocol** (`debate-protocol.md`): The high-level process flow -- what happens in what order
- **Specifications** (`agent-specs.md`): How inputs are configured and validated -- the grammar of agent specs
- **Algorithms** (`scoring-protocol.md`): Deterministic computation logic -- scoring formulas and rubrics
- **Templates** (`artifact-templates.md`): Exact output format -- what the generated artifacts look like

This allows the SKILL.md to be the authoritative combined definition while the refs serve as focused lookup documents for specific concerns during execution.

---

## 4. Agent Specification Patterns Within Skills

### 4.1 Agent Spec Format

The adversarial skill defines a custom agent specification format:

```
<model>                              # Model only
<model>:<persona>                    # Model + persona
<model>:<persona>:"<instruction>"    # Model + persona + custom instruction
```

From `refs/agent-specs.md`:

```yaml
agent_spec_parsing:
  separator: ":"
  instruction_delimiter: '"' (double quotes)
  validation:
    - "Model must be a recognized model name or alias"
    - "Persona must match a valid SuperClaude persona (if provided)"
    - "Instruction must be enclosed in double quotes (if provided)"
  error_handling:
    invalid_model: "STOP with error: 'Unknown model: <model>'"
    invalid_persona: "WARN: Unknown persona '<persona>', using model defaults"
    missing_quotes: "STOP with error: 'Instruction must be quoted: <spec>'"
```

### 4.2 Three Agent Types Defined

The skill defines three distinct agent roles:

#### Static Agents (Pre-defined in `src/superclaude/agents/`)

**debate-orchestrator**: Coordinating agent that manages the pipeline.

```yaml
# From agents/debate-orchestrator.md frontmatter:
---
name: debate-orchestrator
description: Coordinate adversarial debate pipeline without participating in debates
category: analysis
---
```

Key behavioral constraints:
- "Never participate in debates or advocate for any variant"
- "Focus on process integrity, fair scoring, and comprehensive documentation"
- Does NOT generate variants, participate in debates, or execute merges

**merge-executor**: Specialist agent that applies refactoring plans.

```yaml
# From agents/merge-executor.md frontmatter:
---
name: merge-executor
description: Execute refactoring plans to produce unified merged artifacts with provenance annotations
category: quality
---
```

Key behavioral constraints:
- "Follow the refactoring plan precisely and methodically"
- Does NOT make strategic decisions or override the plan
- Reports issues back to orchestrator rather than improvising

#### Dynamic Agents (Instantiated per-session)

**Advocate Agents**: Created dynamically from `--agents` specification. Not pre-defined as files. Instantiated via Task tool with generated prompts.

From SKILL.md:

```yaml
advocate_instantiation:
  prompt_generation:
    template: |
      You are an advocate agent in a structured adversarial debate.
      Your variant: {variant_name}
      Model: {model}
      Persona: {persona or 'default'}
      Custom instruction: {instruction or 'none'}

      RULES:
      1. Argue for your variant's strengths with EVIDENCE (cite sections, quotes)
      2. STEELMAN opposing variants BEFORE critiquing them
      3. Cite specific sections, quotes, or content as evidence for every claim
      4. Acknowledge genuine weaknesses in your variant honestly
      5. Focus on these areas: {focus_areas or 'All'}
```

### 4.3 Agent Definition File Pattern (for Pre-defined Agents)

```yaml
---
name: <agent-name>
description: <one-line description>
category: <analysis|quality|development|etc.>
---

# <Agent Title>

## Triggers
- <when this agent is invoked>

## Behavioral Mindset
<1-2 sentences defining the agent's core approach>

## Model Preference
<which model tier and why>

## Tools
- **<Tool>**: <how this agent uses it>

## Responsibilities
1. **<Responsibility>**: <description>

## Focus Areas
- **<Area>**: <what to focus on>

## Outputs
- **<artifact>**: <description>

## Does NOT
- **<anti-pattern>**: <what the agent must avoid>

## Boundaries
**Will:** / **Will Not:**
```

---

## 5. Protocol Definitions

### 5.1 The 5-Step Protocol

From `refs/debate-protocol.md`:

```
Step 1: Diff Analysis      -> diff-analysis.md
Step 2: Adversarial Debate -> debate-transcript.md
Step 3: Base Selection     -> base-selection.md
Step 4: Refactoring Plan   -> refactor-plan.md
Step 5: Merge Execution    -> merge-log.md + merged output
```

"Steps must execute in order -- each step's output feeds into the next."

### 5.2 Steelman Debate Protocol

From `refs/agent-specs.md`:

```yaml
steelman_protocol:
  before_critiquing:
    action: "Construct the strongest possible version of opposing positions"
    purpose: "Demonstrate understanding before disagreement"
    format: |
      ## Steelman: Variant [X]
      The strongest argument for Variant X's approach is: [steelman]
      This addresses: [what it gets right]
      However, I believe Variant [mine] improves upon this because: [critique]
```

### 5.3 Convergence Detection Protocol

From SKILL.md:

```yaml
convergence_detection:
  metric: "Percentage of diff points where advocates agree on superior approach"
  formula: "convergence = agreed_points / total_diff_points"
  threshold:
    default: 0.80
    configurable: "--convergence flag (range 0.50-0.99)"

  agreement_determination:
    unanimous: "All advocates agree on same winner -> agreed=true"
    majority: ">=2/3 of advocates agree -> agreed=true (winner = majority choice)"
    split: "No majority -> agreed=false (point remains unresolved)"

  early_termination_conditions:
    unanimous_agreement: "All points unanimous -> terminate immediately"
    stable_majority: ">=threshold for 2 consecutive rounds -> terminate"
    max_rounds: "Maximum rounds reached -> terminate"
    oscillation_detection: "Same points flip between rounds -> terminate with flag"
```

### 5.4 Claim-Evidence-Verdict (CEV) Protocol

From `refs/scoring-protocol.md`:

```
CLAIM:    "[Criterion description] is met/not met in Variant X"
EVIDENCE: "[Direct quote or section reference from the variant]"
          OR "No evidence found -- searched sections [list]"
VERDICT:  MET (1 point) | NOT MET (0 points)
```

Rules:
- "No partial credit: Each criterion is 1 point (met) or 0 points (not met)"
- "If the evaluator cannot cite specific evidence for a MET verdict, the criterion defaults to NOT MET"
- "This prevents hallucinated quality assessments"

### 5.5 Position-Bias Mitigation Protocol

From `refs/scoring-protocol.md`:

```
Pass 1: Variants evaluated in input order (A, B, C, ...)
Pass 2: Variants evaluated in reverse order (C, B, A, ...)

Per criterion, per variant:
- Both passes agree -> Use the agreed verdict
- Passes disagree -> Re-evaluate with explicit comparison prompt citing both passes
```

### 5.6 Hybrid Scoring Algorithm

From `refs/scoring-protocol.md`:

```
quant_score = (RC x 0.30) + (IC x 0.25) + (SR x 0.15) + (DC x 0.15) + (SC x 0.15)
qual_score = total_criteria_met / 25
variant_score = (0.50 x quant_score) + (0.50 x qual_score)
```

Quantitative metrics (deterministic, no LLM judgment):
- Requirement Coverage (RC): 0.30 weight
- Internal Consistency (IC): 0.25 weight
- Specificity Ratio (SR): 0.15 weight
- Dependency Completeness (DC): 0.15 weight
- Section Coverage (SC): 0.15 weight

Qualitative rubric (25 binary criteria across 5 dimensions):
- Completeness (5 criteria)
- Correctness (5 criteria)
- Structure (5 criteria)
- Clarity (5 criteria)
- Risk Coverage (5 criteria)

---

## 6. Template Patterns

### 6.1 Artifact Template Structure

From `refs/artifact-templates.md`, the file defines 6 output format templates organized as numbered sections:

- Section 1: `diff-analysis.md` template
- Section 2: `debate-transcript.md` template
- Section 3: `base-selection.md` template
- Section 4: `refactor-plan.md` template
- Section 5: `merge-log.md` template
- Section 6: Merged output provenance format

### 6.2 Template Conventions

Each template specifies:
1. **Document title and metadata header** (ISO-8601 timestamps, counts, configuration)
2. **Structured sections** with specific table formats
3. **ID schemes** for cross-referencing (S-NNN, C-NNN, X-NNN, U-NNN)
4. **Scaling rules** for >2 variants (horizontal table expansion)
5. **Validation rules** (what must be present and consistent)

### 6.3 Example: Diff Analysis Template

From `refs/artifact-templates.md` Section 1:

```markdown
# Diff Analysis: <artifact-type> Comparison

## Metadata
- Generated: <ISO-8601 timestamp>
- Variants compared: <count>
- Total differences found: <count>
- Categories: structural (<N>), content (<N>), contradictions (<N>), unique (<N>)

## Structural Differences

| # | Area | Variant A | Variant B | ... | Severity |
|---|------|-----------|-----------|-----|----------|
| S-001 | <area> | <description> | <description> | ... | Low/Medium/High |
```

### 6.4 Provenance Annotation Template

From `refs/artifact-templates.md` Section 6:

```markdown
<!-- Provenance: This document was produced by /sc:adversarial -->
<!-- Base: Variant A (opus:architect) -->
<!-- Merge date: ISO-8601 timestamp -->

# Document Title

<!-- Source: Base (original) -->
[Original base content preserved here]

<!-- Source: Variant B (sonnet:security), Section 3.2 -- merged per Change #1 -->
[Content incorporated from Variant B]
```

Rules:
- "Every section or significant block includes a `<!-- Source: ... -->` tag"
- "Annotations are HTML comments -- invisible in rendered markdown"

---

## 7. How This Skill Integrates with Commands and Agents

### 7.1 Command-Skill Relationship

The skill has a corresponding command file at `src/superclaude/commands/adversarial.md`. The command file is a lightweight entry point; the SKILL.md contains the full implementation logic.

**Command file frontmatter** (from `adversarial.md`):

```yaml
---
name: adversarial
description: "Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts"
category: analysis
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [architect, analyzer, scribe]
---
```

The command file provides:
- Usage examples with `bash` code blocks
- A brief behavioral summary
- An options table (flags with descriptions)
- Boundaries (Will/Will Not)
- Related commands table

The SKILL.md provides:
- Full protocol specification
- Complete implementation details per step
- Error handling matrix
- Return contract
- MCP integration layer details
- Framework registration instructions

### 7.2 Agent-Skill Integration

The skill delegates to two pre-defined agents stored in `src/superclaude/agents/`:

1. `debate-orchestrator.md` -- Coordinates the entire 5-step pipeline
2. `merge-executor.md` -- Executes Step 5 (merge)

And dynamically instantiates advocate agents via Task tool based on `--agents` flag.

The delegation chain is:
```
/sc:adversarial command
  -> debate-orchestrator agent (coordinates Steps 1-5)
    -> advocate agents (dynamic, participate in Step 2 debate)
    -> merge-executor agent (executes Step 5 merge)
```

### 7.3 Inter-Command Integration

From SKILL.md:

```yaml
integration_pattern:
  sc_roadmap_v2:
    multi_spec: |
      Multiple spec documents -> generate one roadmap per spec -> adversarial merge.
      Invocation: /sc:adversarial --compare roadmap-from-spec1.md,roadmap-from-spec2.md
    multi_roadmap: |
      One spec -> generate multiple roadmap variants -> adversarial merge.
      Invocation: /sc:adversarial --source spec.md --generate roadmap --agents opus:architect,sonnet:security
  generic_integration: |
    Any command can invoke sc:adversarial and consume the return contract:
    1. Call sc:adversarial with appropriate flags
    2. Read return contract fields: merged_output_path, convergence_score, status
    3. If status == 'success': use merged_output_path as the final artifact
    4. If status == 'partial': use merged_output_path but flag unresolved_conflicts
    5. If status == 'failed': fall back to manual selection
```

### 7.4 Framework Registration

The skill specifies how it should be registered in framework configuration files:

```yaml
framework_registration:
  commands_md:
    entry: |
      **`/sc:adversarial [options]`** -- Structured adversarial debate, comparison, and merge pipeline
      - **Auto-Persona**: Architect, Analyzer, Scribe
      - **MCP**: Sequential (debate scoring), Serena (persistence), Context7 (validation)
      - **Tools**: [Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task]

  orchestrator_md:
    routing_entry:
      pattern: "adversarial debate"
      complexity: "complex"
      domain: "analysis"
      auto_activates: "architect + analyzer personas, --ultrathink, Sequential + Serena"
      confidence: "95%"
```

### 7.5 MCP Server Integration

```yaml
mcp_integration:
  sequential:
    usage: "Debate scoring, convergence analysis, refactoring plan logic"
    steps: "Steps 2-4"
    circuit_breaker:
      failure_threshold: 3
      timeout: "30s"
      fallback: "Native Claude reasoning with depth reduction"
      depth_reduction: "deep -> standard, standard -> quick"

  serena:
    usage: "Memory persistence of adversarial outcomes"
    steps: "Step 5 (post-merge)"
    circuit_breaker:
      failure_threshold: 4
      timeout: "45s"
      fallback: "Skip persistence, log warning"

  context7:
    usage: "Domain pattern validation during merge"
    steps: "Step 5 (merge validation)"
    circuit_breaker:
      failure_threshold: 5
      timeout: "60s"
      fallback: "Skip domain validation, rely on structural checks only"
```

---

## 8. Summary: Reusable Skill Development Pattern

### Minimum Required Files

```
src/superclaude/skills/<skill-name>/
├── __init__.py    # Empty file
└── SKILL.md       # Required: frontmatter + full definition
```

### Full Pattern (Complex Skill)

```
src/superclaude/skills/sc-<name>/
├── __init__.py
├── SKILL.md                     # Primary definition
└── refs/                        # Decomposed reference docs
    ├── <protocol>.md            # Process/protocol definitions
    ├── <algorithm>.md           # Scoring/computation logic
    ├── <specs>.md               # Input format specifications
    └── <templates>.md           # Output format templates

src/superclaude/commands/<name>.md       # Slash command entry point
src/superclaude/agents/<agent-1>.md      # Pre-defined agents
src/superclaude/agents/<agent-2>.md      # (one per static role)
```

### SKILL.md Frontmatter Fields

```yaml
---
name: sc:<name>                  # Required: skill name
description: <one-line>          # Required: what it does
allowed-tools: <tool-list>       # Required: permitted tools
---
```

### SKILL.md Recommended Section Order

1. Purpose (with Core Objective and Key Differentiator)
2. Required Input (with MANDATORY callout)
3. Triggers (explicit, keyword, integration)
4. Input Modes
5. Core Protocol (numbered steps, each with Input/Delegation/Process/Output/Template)
6. Configurable Parameters (table)
7. Interactive Mode (checkpoints)
8. Artifact Output Structure (directory tree)
9. Error Handling Matrix (YAML)
10. Return Contract (YAML, for programmatic integration)
11. Agent Delegation (roles, models, tools, responsibilities, anti-patterns)
12. MCP Integration (server, usage, steps, circuit breaker)
13. Compliance Tier Classification
14. Boundaries (Will Do / Will Not Do)
15. Implementation Details (deep per-step YAML specifications with task IDs)

### Agent Definition Pattern

```yaml
---
name: <agent-name>
description: <one-line>
category: <category>
---
```

Followed by: Triggers, Behavioral Mindset, Model Preference, Tools, Responsibilities, Focus Areas, Outputs, Does NOT, Boundaries.

### Key Design Principles Demonstrated

1. **Separation of concerns**: SKILL.md is authoritative; refs/ decompose by concern (protocol, algorithm, specs, templates)
2. **YAML as specification language**: All protocols, algorithms, and behaviors defined in YAML blocks within markdown
3. **Explicit delegation**: Clear agent roles with documented boundaries (Does NOT sections)
4. **Error handling as first class**: Complete error matrix with detection, behavior, constraint, fallback
5. **Return contracts**: Structured output enabling inter-command composition
6. **Circuit breakers**: Per-MCP-server failure handling with graceful degradation
7. **Dynamic agent instantiation**: Not all agents are pre-defined; some are created at runtime from specs
8. **Evidence-based decisions**: CEV protocol, position-bias mitigation, and confidence calibration prevent hallucinated assessments
9. **Provenance tracking**: Source attribution throughout merged outputs
10. **Interactive mode as overlay**: Non-interactive is default; interactive adds checkpoints without changing the protocol

---

*Extracted 2026-02-21 from SuperClaude Framework v4.2.0, branch feature/1.7-adversarialdebate*
