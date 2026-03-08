# Workflow Analysis Protocol

Loaded during Phase 1 of portification. Guides the systematic decomposition of an inference-based workflow into a pipeline specification.

## Discovery Checklist

When analyzing a target workflow, locate and read these components in order:

### 1. Find the Command

Look in `src/superclaude/commands/` for the matching command file. Extract:
- Frontmatter: category, complexity, mcp-servers, personas
- Behavioral Flow section: the high-level step sequence
- Arguments and options
- Boundaries (Will Do / Will Not Do)

### 2. Find the Skill

Look in `src/superclaude/skills/` for the matching skill directory. Read:
- `SKILL.md`: The full protocol with step-by-step behavioral flow
- `refs/`: All reference files (algorithms, templates, scoring protocols)
- `rules/`: Validation rules and classification taxonomies
- `templates/`: Output format templates (these become gate validation targets)
- `scripts/`: Shell scripts for preprocessing (these become pure-programmatic steps)
- Note which refs are loaded at which phase/wave

### 3. Find the Agents

Search for agents referenced in the skill:
- Look in `src/superclaude/agents/` for `.md` files
- Note each agent's: triggers, tools, responsibilities, boundaries
- Identify delegation patterns: parallel vs sequential, orchestrator vs worker

### 4. Map the Data Flow

Trace how data moves through the workflow:
- What inputs does each step consume?
- What artifacts does each step produce?
- Which artifacts feed into downstream steps?
- What is the final output?

## Step Decomposition Algorithm

For each discrete operation in the workflow:

### Identify Step Boundaries

A new Step starts when:
- A new artifact is produced
- A different agent takes over
- The execution mode changes (sequential → parallel)
- A quality gate must be evaluated
- The operation type changes (analysis → generation → validation)

### Classify Each Step

Rate each step on the **programmatic spectrum**:

| Classification | Characteristics | Implementation |
|---------------|-----------------|----------------|
| **Pure Programmatic** | Deterministic, formula-based, structural | Python function, no Claude |
| **Programmatic + Validation** | Structural check with semantic judgment | Python primary, Claude for edge cases |
| **Claude-Assisted** | Content generation within structured format | Claude subprocess with gate validation |
| **Pure Inference** | Creative, subjective, context-dependent | Claude subprocess with light gate |

### Map to Pipeline Primitives

| Workflow Concept | Pipeline Primitive |
|-----------------|-------------------|
| Sequential step | `Step` in step list |
| Parallel operations | `list[Step]` parallel group |
| Quality gate | `GateCriteria` on the Step |
| Agent delegation | Prompt in `prompts.py` |
| Scoring formula | Python function in `gates.py` or separate module |
| Status decision | `_determine_status()` in `executor.py` |
| Input validation | `config.py` validation logic |
| Output format | Frontmatter requirements in gate + prompt |
| Retry on failure | `retry_limit` on Step |
| Skip on success | Resume logic in executor |

## Analysis Output Format

Phase 1 produces `portify-analysis.md` with this structure:

```markdown
---
source_skill: <skill-name>
source_command: <command-name>
step_count: <N>
parallel_groups: <N>
gate_count: <N>
agent_count: <N>
complexity: simple|moderate|high
---

# Portification Analysis: {workflow-name}

## Source Components

| Component | Path | Lines | Purpose |
|-----------|------|-------|---------|
| Command | ... | ... | ... |
| Skill | ... | ... | ... |
| Agent: ... | ... | ... | ... |
| Ref: ... | ... | ... | ... |

## Step Graph

### Step 1: {name}
- **Type**: pure-programmatic | claude-assisted | hybrid
- **Inputs**: [list of input artifacts]
- **Output**: artifact-name.md
- **Gate**: exempt | light | standard | strict
- **Agent**: none | agent-name
- **Parallel**: yes (with step N) | no
- **Timeout**: Ns
- **Retry**: N attempts
- **Notes**: any special considerations

### Step 2: {name}
...

## Parallel Groups

| Group | Steps | Rationale |
|-------|-------|-----------|
| 1 | step-2, step-3 | Independent variant generation |

## Gates Summary

| Step | Tier | Frontmatter | Min Lines | Semantic Checks |
|------|------|-------------|-----------|-----------------|
| ... | ... | ... | ... | ... |

## Agent Delegation Map

| Agent | Used In Steps | Parallel | Contract |
|-------|--------------|----------|----------|
| ... | ... | ... | ... |

## Data Flow Diagram

```
[input] → step-1 → [artifact-1]
                         ↓
                    ┌─step-2─┐
                    │         │ (parallel)
                    └─step-3─┘
                         ↓
               [artifact-2, artifact-3]
                         ↓
                    step-4 → [final-output]
```

## Classification Summary

| Category | Count | Steps |
|----------|-------|-------|
| Pure Programmatic | N | ... |
| Claude-Assisted | N | ... |
| Hybrid | N | ... |
| Pure Inference | N | ... |

## Recommendations

- Things that should definitely be programmatic but are currently inference
- Steps that could be split for better gate coverage
- Opportunities for parallelization
- Potential failure modes and how to handle them
```

## Common Workflow Patterns

### Pattern: Multi-Agent Debate
Found in: adversarial, spec-panel

Steps:
1. Parse inputs and validate (programmatic)
2. Generate variants in parallel (Claude, parallel group)
3. Diff analysis (Claude, single step with strict gate)
4. Debate rounds (Claude, sequential with convergence gate)
5. Score and select (hybrid — formulas are programmatic, rubrics are Claude)
6. Generate plan (Claude, standard gate)
7. Execute merge (Claude, strict gate with post-validation)

### Pattern: Multi-Pass Audit
Found in: cleanup-audit

Steps:
1. Discover files (programmatic)
2. Surface scan with batching (Claude, batched parallel)
3. Deep analysis per file (Claude, batched parallel)
4. Cross-cutting comparison (Claude, single with strict gate)
5. Consolidate findings (Claude, standard gate)
6. Validate claims (Claude, sampling with standard gate)

### Pattern: Extract-Transform-Validate
Found in: roadmap, tasklist

Steps:
1. Extract requirements (Claude, strict gate on frontmatter)
2. Generate artifacts (Claude, parallel for multiple agents)
3. Compare/analyze (Claude, standard gate)
4. Synthesize final (Claude, strict gate)
5. Validate structure (programmatic)

### Pattern: Iterative Refinement
Found in: implement, improve

Steps:
1. Analyze current state (Claude, standard gate)
2. Generate plan (Claude, standard gate)
3. Execute changes (Claude, strict gate)
4. Validate changes (programmatic + Claude)
5. Iterate if quality threshold not met (retry loop)
