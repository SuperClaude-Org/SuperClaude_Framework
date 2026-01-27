# OpenCode Custom Commands Research

**Research Date**: 2026-01-17
**Source Codebase**: `<opencode-root>/.opencode/`
**Purpose**: Understanding custom command architecture for potential adaptation

---

## Executive Summary

OpenCode implements a sophisticated custom command system using markdown files with YAML frontmatter. Commands can orchestrate multi-agent workflows, specify model preferences, control tool access, and coordinate complex multi-phase pipelines. The `/rf:crossLLM` command demonstrates an advanced 7-phase workflow with 12+ specialized agents working in parallel and sequence.

---

## 1. Directory Structure

```
.opencode/
    command/           # Command definitions (entry points)
        rf:crossLLM.md
    agent/             # Agent definitions (sub-agents)
        rf-crossLLM-orchestrator.md
        rf-crossLLM-proposer-1.md
        rf-crossLLM-proposer-2.md
        rf-crossLLM-proposer-3.md
        rf-crossLLM-debate.md
        rf-crossLLM-judge.md
        rf-crossLLM-evaluator-qag.md
        rf-crossLLM-domain-detector.md
        rf-crossLLM-claim-extractor.md
        rf-crossLLM-importance-classifier.md
        rf-crossLLM-gpt.md
        rf-crossLLM-claude.md
        rf-crossLLM-gemini.md
    resources/         # Configuration and rubrics
        model-capabilities.yaml
        scoring-config.md
        rubric-qag/
            generic.md
            overlays/
                code.md
                documentation.md
                proposal.md
                script.md
```

---

## 2. File Format Specification

### 2.1 Command Files (`command/`)

Commands are markdown files with:
- **YAML Frontmatter**: Metadata (description only for simple commands)
- **Markdown Body**: Routing logic, usage documentation, modes

**Example: Command Entry Point**
```markdown
---
description: Response/content upgrade (v1 or v2)
---

You are executing `/rf:crossLLM`.

Args: `$ARGUMENTS`

## Modes

### v1 (conversation-only)
- `/rf:crossLLM gpt`
- `/rf:crossLLM claude`

Routing:
- If `$1` is `gpt`: invoke `@rf-crossLLM-gpt`.
- If `$1` is `claude`: invoke `@rf-crossLLM-claude`.

### v2 (content sources + model chains + debate)
- `/rf:crossLLM v2 convo <chain>`
- `/rf:crossLLM v2 file <chain> <path>`

Routing:
- If `$1` is `v2`: invoke `@rf-crossLLM-orchestrator`.
```

### 2.2 Agent Files (`agent/`)

Agents have richer YAML frontmatter:

| Property | Type | Description |
|----------|------|-------------|
| `description` | string | Brief purpose statement |
| `mode` | string | Execution mode (`subagent`) |
| `model` | string | LLM model identifier (e.g., `litellm-cli-proxy/gpt-5.2`) |
| `temperature` | float | Model temperature setting (0.0-1.0) |
| `tools` | object | Tool access controls |

**Example: Agent Definition**
```yaml
---
description: Orchestrates rf-crossLLM v2 (sources, chains, debate, multi-model evaluation).
mode: subagent
model: litellm-cli-proxy/gpt-5.2
temperature: 0.1
tools:
  bash: true
  read: true
  write: true
  edit: true
  list: true
  glob: true
  grep: true
  task: true
  webfetch: true
---

You are the rf-crossLLM v2 orchestrator.
[... detailed instructions ...]
```

### 2.3 Tool Access Control

Each agent can be granted or denied specific tools:

| Tool | Purpose |
|------|---------|
| `bash` | Shell command execution |
| `read` | File reading |
| `write` | File writing |
| `edit` | File editing |
| `list` | Directory listing |
| `glob` | Pattern matching |
| `grep` | Content search |
| `task` | Sub-agent spawning |
| `webfetch` | Web content retrieval |

**Read-only agents** (evaluators, judges) typically have all tools disabled:
```yaml
tools:
  write: false
  edit: false
  bash: false
```

---

## 3. Command Invocation Patterns

### 3.1 Prefix Convention

Commands use namespace prefixes:
- `/rf:crossLLM` - The `rf:` prefix (likely "refine" or project-specific namespace)
- Pattern: `/<namespace>:<command-name>`

### 3.2 Argument Handling

Commands receive arguments via `$ARGUMENTS` variable:
- `$1`, `$2`, `$3+` - Positional arguments
- Named flags: `--ground`, `--ground-max-claims N`

**Example Argument Parsing**:
```
/rf:crossLLM v2 file claude>gpt .dev/fixtures/input.md --ground
          ^   ^         ^              ^                  ^
         $1  $2        $3             $4               flag
```

### 3.3 Agent Invocation Syntax

Agents are invoked with `@` prefix:
- `@rf-crossLLM-orchestrator` - Invoke the orchestrator agent
- `@rf-crossLLM-proposer-1` - Invoke proposer variant 1

---

## 4. Multi-Agent Workflow Architecture

### 4.1 The rf:crossLLM Pipeline (7 Phases)

```
Phase A: Intake
    |
    v
Phase B: Parallel Proposals  -----> [proposer-1] [proposer-2] [proposer-3]
    |                                    |            |            |
    v                                    v            v            v
Phase C: Debate  <------------------ [3 proposals merged]
    |
    v
Phase D: Judge  -----------------> [judgement.md] + [upgrade candidate]
    |
    v
Phase E: Multi-Model QAG Evaluation
    |
    +---> E1: Domain Detection  --> [domain-detector]
    |
    +---> E2: Parallel Evaluation --> [evaluator-qag x3 models]
    |                                     claude-sonnet-4-5
    |                                     gpt-5.2
    |                                     gemini-2.5-pro
    |
    +---> E3: Swap Augmentation --> Position bias check
    |
    +---> E4: Score Reconciliation --> Variance analysis
    |
    +---> E5: Cross-Validation --> Debate vs Evaluator alignment
    |
    +---> E6: Generate Scorecard --> [scorecard.md]
    |
    v
Phase F: Multi-hop Chains (if N>=2 models in chain)
    |
    v
Phase G: Grounding (if --ground enabled)
    |
    +---> G1: Extract Claims --> [claim-extractor]
    +---> G2: Classify Importance --> [importance-classifier]
    +---> G3: Apply Overrides --> Routing-impact rules
    +---> G4: Ground HIGH Claims --> webfetch + verify
    +---> G5: Enforce Removal --> Remove CONTRADICTED claims
    +---> G6: Write Artifacts --> [grounding-report.md]
    +---> G7: Re-evaluate --> Repeat Phase E if removals
    +---> G8: Update Scorecard --> Grounding summary
```

### 4.2 Agent Specialization Patterns

**Proposer Variants** (3 parallel agents with different strategies):
| Agent | Strategy | Temperature | Focus |
|-------|----------|-------------|-------|
| proposer-1 | minimal-delta | 0.2 | Value preservation, light fixes |
| proposer-2 | structure-first | 0.3 | Reorganization, clarity |
| proposer-3 | comprehensive | 0.3 | Full rewrite allowed |

**Model-Specific Agents**:
| Agent | Model | Purpose |
|-------|-------|---------|
| rf-crossLLM-claude | claude-sonnet-4-5-20250929 | Claude-specific upgrade pass |
| rf-crossLLM-gpt | gpt-5.2 | GPT-specific upgrade pass |
| rf-crossLLM-gemini | gemini-2.5-pro | Gemini-specific evaluation |

### 4.3 Parallel Execution

The orchestrator explicitly runs multiple agents in parallel:
```markdown
### Phase B - Parallel Proposals

Spawn three proposer subagents in parallel and capture their outputs:
- `@rf-crossLLM-proposer-1`
- `@rf-crossLLM-proposer-2`
- `@rf-crossLLM-proposer-3`
```

Similarly for evaluation:
```markdown
### E2: Multi-Model QAG Evaluation (Parallel)

Spawn 3 evaluator instances in parallel, each using `@rf-crossLLM-evaluator-qag`:

| Instance | Model Override | Inputs |
|----------|----------------|--------|
| eval-claude | claude-sonnet-4-5 | draft, upgrade, generic rubric, domain overlay, domain |
| eval-gpt | gpt-5.2 | draft, upgrade, generic rubric, domain overlay, domain |
| eval-gemini | gemini-2.5-pro | draft, upgrade, generic rubric, domain overlay, domain |
```

---

## 5. Resource System

### 5.1 External Resources

Commands reference external resources for:
- **Capability Contracts**: `model-capabilities.yaml` - Feature flags per model
- **Scoring Configuration**: `scoring-config.md` - Thresholds and evaluation parameters
- **Rubrics**: `rubric-qag/generic.md` + domain overlays

### 5.2 Capability Contract Example

```yaml
version: "1.1"
capabilities:
  supports_network_grounding: true
  supports_schema_enforcement: false
  supports_multimodal_inputs: false
  supports_long_context_tokens: 200000
```

Orchestrators validate capabilities before executing:
```markdown
If `--ground` is passed but `supports_network_grounding=false`:
- Print error: "Error: --ground requested but grounding is not supported"
- STOP immediately and write NO run artifacts
```

### 5.3 Rubric System

**Generic Rubric** (`generic.md`):
- 6 dimensions: Correctness, Completeness, Clarity/Structure, Actionability, Assumption Hygiene, Value Preservation
- 3 questions per dimension (0-3 points)
- Hard checks (structural validation) reported separately

**Domain Overlays** (e.g., `code.md`):
- 2 additional questions per dimension (0-2 points)
- Combined: 0-5 points per dimension
- Activated based on domain detection

---

## 6. Error Handling & Recovery

### 6.1 Retry Budget System

```yaml
retry_budget:
  per_component_retries: 1
  pipeline_retry_budget: 5
  circuit_breaker: 3 consecutive failures
```

### 6.2 Graceful Degradation

| Failure Mode | Degradation Strategy |
|--------------|---------------------|
| 1 evaluator fails | Use median of 2 remaining models |
| 2 evaluators fail | Use single model, mark as UNVERIFIED |
| All evaluators fail | Fail pipeline, preserve artifacts |
| Domain detector fails | Default to GENERIC domain |
| Debate fails | Skip debate, proceed with proposals |

### 6.3 Human Review Workflow

When variance remains HIGH after automated tiebreakers:
1. Write `human-review-request.md` with specific decisions needed
2. Write `run-state.json` with `AWAITING_HUMAN_REVIEW` status
3. User provides verdicts in review file
4. Resume with `/rf:crossLLM v2 resume <run-id>`

---

## 7. Output Artifacts

Commands generate structured artifacts in `.dev/runs/rf-crossLLM/<run-id>/`:

| Artifact | Purpose |
|----------|---------|
| `input.md` | Exact input content |
| `proposals/proposal-1.md` | First proposer output |
| `proposals/proposal-2.md` | Second proposer output |
| `proposals/proposal-3.md` | Third proposer output |
| `debate.md` | Comparison with quality signals |
| `judgement.md` | Judge's selection rationale |
| `upgrade.md` | Final upgraded content |
| `scorecard.md` | Multi-model QAG evaluation |
| `grounding/` | Grounding artifacts (if enabled) |
| `run-state.json` | Pipeline state for resume |

---

## 8. Comparison with Claude Code Slash Commands

### 8.1 Similarities

| Feature | OpenCode | Claude Code (SuperClaude) |
|---------|----------|--------------------------|
| File format | Markdown + YAML frontmatter | Markdown + YAML frontmatter |
| Namespace | `/<prefix>:<name>` | `/sc:<name>` |
| Agent invocation | `@agent-name` | `@agent-name` or Skill tool |
| Tool control | Per-agent tool access | Global tool access |
| Resources | External markdown/yaml | Embedded in skill files |

### 8.2 Key Differences

| Aspect | OpenCode | Claude Code |
|--------|----------|-------------|
| **Model specification** | Per-agent `model:` field | Implicit (uses current model) |
| **Temperature control** | Per-agent `temperature:` field | Not directly controllable |
| **Parallel execution** | Explicit parallel spawning | Agent-based (Task tool) |
| **Tool granularity** | Per-agent enable/disable | Session-wide access |
| **Run persistence** | `.dev/runs/` artifacts | Session memory (Serena) |
| **Human-in-the-loop** | Explicit resume workflow | Manual intervention |
| **Multi-model evaluation** | Built-in cross-model consensus | Single model |

### 8.3 OpenCode Advantages

1. **Model Diversity**: Can route to different LLMs (GPT, Claude, Gemini) within a single workflow
2. **Fine-grained Tool Control**: Read-only agents can be locked down completely
3. **Built-in Persistence**: Artifacts automatically saved for audit/resume
4. **Ensemble Evaluation**: Multi-model scoring with variance analysis
5. **Grounding Pipeline**: Automated fact-checking with claim extraction

### 8.4 Claude Code Advantages

1. **Deep Integration**: Native tool access without explicit enabling
2. **Persona System**: Rich behavioral personas beyond just agents
3. **MCP Server Integration**: Sequential, Context7, Magic, Playwright
4. **Wave Orchestration**: Multi-stage command execution
5. **Session Lifecycle**: Serena-based project memory

---

## 9. Architectural Insights for Adaptation

### 9.1 Patterns Worth Adopting

1. **Proposer Diversity**: Multiple agents with different strategies competing, then synthesized
2. **Evaluation Pipeline**: Domain detection -> rubric selection -> multi-evaluator consensus
3. **Variance Analysis**: Detect when models disagree significantly, trigger tiebreakers
4. **Grounding Phase**: Extract claims, classify importance, verify against external sources
5. **Artifact Trail**: Every intermediate result saved for debugging and audit

### 9.2 Implementation Considerations

For Claude Code/SuperClaude adoption:
- Use Task tool for parallel agent spawning (equivalent to OpenCode parallel phases)
- Use Serena MCP for artifact persistence (alternative to `.dev/runs/`)
- Leverage WebSearch/WebFetch for grounding (already available)
- Sequential MCP for complex reasoning (already integrated)

### 9.3 Potential Enhancements

Based on OpenCode patterns:
- Multi-strategy proposal generation (minimal-delta vs structure-first)
- Cross-validation between different analysis phases
- Automated human review workflows with state persistence
- Ensemble evaluation with variance detection

---

## 10. Key Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| `<opencode-root>/.opencode/command/rf:crossLLM.md` | 61 | Command entry point |
| `<opencode-root>/.opencode/agent/rf-crossLLM-orchestrator.md` | 676 | Main orchestrator |
| `<opencode-root>/.opencode/agent/rf-crossLLM-evaluator-qag.md` | 167 | QAG evaluation |
| `<opencode-root>/.opencode/agent/rf-crossLLM-debate.md` | 181 | Proposal comparison |
| `<opencode-root>/.opencode/resources/scoring-config.md` | 175 | Scoring thresholds |
| `<opencode-root>/.opencode/resources/rubric-qag/generic.md` | 151 | Base evaluation rubric |

---

## Appendix: Agent Template

```markdown
---
description: Brief purpose statement
mode: subagent
model: litellm-cli-proxy/<model-id>
temperature: <0.0-1.0>
tools:
  bash: <true|false>
  read: <true|false>
  write: <true|false>
  edit: <true|false>
  list: <true|false>
  glob: <true|false>
  grep: <true|false>
  task: <true|false>
  webfetch: <true|false>
---

# Agent Instructions

## Inputs
[What this agent receives]

## Process
[Step-by-step instructions]

## Output Format
[Expected output structure]

## Rules
[Constraints and requirements]
```

---

*Research conducted from IBOpenCode codebase version as of 2026-01-17*
