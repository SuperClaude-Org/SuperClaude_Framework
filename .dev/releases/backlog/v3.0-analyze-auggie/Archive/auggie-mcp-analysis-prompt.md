# Auggie MCP Framework-Wide Integration Analysis
## Multi-Phase Parallel Agent Orchestration Prompt

> **Generated**: 2026-02-20
> **Context**: Full framework audit for `mcp__auggie-mcp__codebase-retrieval` integration
> **Scope**: All commands, agents, and skills in SuperClaude Framework v4.2.0

---

## Pre-Execution Context

### What Auggie MCP Is
The `mcp__auggie-mcp__codebase-retrieval` tool (Augment's context engine) provides:
- Natural language semantic code search across entire codebases
- Real-time indexed results reflecting current disk state
- Cross-language retrieval with proprietary embedding models
- Two required parameters: `information_request` (string) and `directory_path` (absolute path)

### Current State (Verified by Research Agents)
- **Components with Auggie references**: 3 of ~65 total (task-unified.md, task-mcp.md, sc-task-unified SKILL.md) — all generic mentions of "codebase-retrieval", not proper MCP invocations
- **Components with `auggie-mcp` in mcp-servers frontmatter**: 0 of 30 commands
- **Existing v1.2 backlog** (`.dev/.releases/backlog/v1.2-analyze-auggie/`): Comprehensive planning package targeting ONLY `/sc:analyze`. Contains feature spec, debate transcript, 6 milestone tasklists. **NONE implemented in code.**

### Component Inventory

**Commands** (30 in `src/superclaude/commands/`):
analyze, brainstorm, build, cleanup, cleanup-audit, design, document, estimate, explain, git, help, implement, improve, index, load, pm, recommend, reflect, research, review-translation, roadmap, save, sc, select-tool, spawn, spec-panel, task, task-mcp, task-unified, test, troubleshoot, workflow

**Agents** (27 in `src/superclaude/agents/`):
audit-analyzer, audit-comparator, audit-consolidator, audit-scanner, audit-validator, backend-architect, business-panel-experts, deep-research, deep-research-agent, devops-architect, frontend-architect, learning-guide, performance-engineer, pm-agent, python-expert, quality-engineer, refactoring-expert, repo-index, requirements-analyst, root-cause-analyst, security-engineer, self-review, socratic-mentor, system-architect, technical-writer

**Skills** (5 in `src/superclaude/skills/`):
sc-cleanup-audit, sc-roadmap, sc-task-unified, sc-validate-tests, confidence-check

---

## PHASE 0: Backlog Alignment Assessment

### Objective
Determine overlap between existing v1.2-analyze-auggie backlog and the broader Phase 1-4 analysis below.

### Execution
Spin up **4 parallel agents** to evaluate the backlog against each subsequent phase:

```
Agent P0-A: "Evaluate .dev/.releases/backlog/v1.2-analyze-auggie/ alignment with Phase 1 (existing Auggie uses)"
Agent P0-B: "Evaluate .dev/.releases/backlog/v1.2-analyze-auggie/ alignment with Phase 2 (new Auggie candidates)"
Agent P0-C: "Evaluate .dev/.releases/backlog/v1.2-analyze-auggie/ alignment with Phase 3 (implementation proposals)"
Agent P0-D: "Evaluate .dev/.releases/backlog/v1.2-analyze-auggie/ alignment with Phase 4 (PRD/spec creation)"
```

Each agent should:
1. Read ALL files in the backlog directory (7 top-level + 6 tasklists)
2. Map each backlog item to the corresponding Phase below
3. Flag items that are: (a) directly reusable, (b) partially applicable, (c) out of scope
4. Identify gaps in the backlog that the broader analysis will cover
5. Produce a **Delta Report** showing: what the backlog covers vs what's new

### Expected Output
A consolidated alignment matrix showing overlap percentages and a clear "net new work" list for Phases 1-4.

---

## PHASE 1: Existing Auggie MCP Usage Analysis

### Step 1.1: Inventory Current Uses
Spin up **3 parallel agents** to analyze the 3 components with existing `codebase-retrieval` references:

```
Agent P1.1-A: "Analyze Auggie MCP usage in src/superclaude/commands/task-unified.md — read the full file, identify every codebase-retrieval reference, map how it's used in the workflow, and assess whether it's invoked correctly with directory_path parameter"

Agent P1.1-B: "Analyze Auggie MCP usage in src/superclaude/commands/task-mcp.md — read the full file, identify every codebase-retrieval reference, map how it's used in the workflow, and assess whether it's invoked correctly with directory_path parameter"

Agent P1.1-C: "Analyze Auggie MCP usage in src/superclaude/skills/sc-task-unified/SKILL.md — read the full file, identify every codebase-retrieval reference, map how it's used in the workflow, and assess whether it's invoked correctly with directory_path parameter"
```

### Step 1.2: Chain-of-Thought Ideal Use Deduction
For each component identified in 1.1, spin up a **parallel agent per component**:

```
Agent P1.2-X (per component): "Using chain-of-thought reasoning, analyze [COMPONENT_NAME] and deduce the ideal use of Auggie MCP (mcp__auggie-mcp__codebase-retrieval) for this specific use case. Consider:
  1. What is this component's primary purpose and workflow?
  2. Where in the workflow would semantic code search provide the highest value?
  3. What specific information_request queries would be most effective?
  4. What is the ideal placement (before analysis? during discovery? for validation?)?
  5. Should it be mandatory, preferred, or optional at each integration point?
  6. What fallback behavior should exist when Auggie is unavailable?
Present your reasoning step-by-step with confidence scores for each deduction."
```

### Step 1.3: Adversarial Debate — Current vs Ideal
For each component, spin up **2 parallel agents** in adversarial debate:

```
Agent P1.3-X-PRO: "Argue FOR the current implementation of Auggie MCP in [COMPONENT_NAME]. Defend why the current usage pattern is sufficient. Consider: simplicity, reliability, fallback safety, token efficiency, and maintainability."

Agent P1.3-X-CON: "Argue AGAINST the current implementation of Auggie MCP in [COMPONENT_NAME]. Identify specific shortcomings: missed semantic opportunities, incorrect invocation patterns, missing directory_path, suboptimal query formulation, lack of circuit breaker, missing fallback behavior."
```

Each pair produces a **Debate Summary** with: consensus points, unresolved tensions, and clear winner with justification.

### Step 1.4: Improvement Proposals (for sub-optimal uses)
For each component found to have sub-optimal usage, spin up **1 agent**:

```
Agent P1.4-X: "Propose exactly 6 improvements to the Auggie MCP usage in [COMPONENT_NAME]. For each proposal:
  1. Description of the improvement
  2. Expected impact (token savings, precision improvement, latency change)
  3. Implementation complexity (low/medium/high)
  4. Risk assessment
  5. Dependencies on other components
  6. Measurable success criteria

Then engage in internal adversarial reasoning:
- For each proposal, argue its strongest case (steelman)
- For each proposal, argue its weakest case (strawman)
- Score each on: impact (1-10), feasibility (1-10), risk (1-10 inverted)
- Select TOP 3 proposals with justification"
```

### Step 1.5: Implementation Strategy (Top 3 per component)
Spin up **3 parallel agents per component** (one per selected improvement):

```
Agent P1.5-X-N: "Propose the complete implementation strategy for improvement #N in [COMPONENT_NAME]:
  1. Exact file changes required (with line-level specificity)
  2. New MCP invocation patterns (show exact tool call syntax)
  3. Fallback/degradation behavior
  4. Testing approach (unit + integration + acceptance)
  5. Rollback plan if improvement causes regression
  6. Migration path from current to improved state
  7. Token budget impact analysis"
```

---

## PHASE 2: New Auggie MCP Candidate Evaluation

### Step 2.1: Candidate Identification
Spin up **3 parallel agent groups** by component type:

```
Agent Group P2.1-CMD (commands): "Evaluate ALL 27 commands that do NOT currently reference Auggie MCP. For each command, read its mcp-servers frontmatter and full workflow. Categorize as:
  - HIGH BENEFIT: Semantic code search would fundamentally improve this command's effectiveness
  - MEDIUM BENEFIT: Would add value but isn't transformative
  - LOW BENEFIT: Marginal improvement, not worth the integration complexity
  - NO BENEFIT: Auggie MCP is irrelevant to this command's purpose

Commands to evaluate: analyze, brainstorm, build, cleanup, cleanup-audit, design, document, estimate, explain, git, help, implement, improve, index, load, pm, recommend, reflect, research, review-translation, roadmap, save, sc, select-tool, spawn, spec-panel, test, troubleshoot, workflow

For each HIGH/MEDIUM candidate, specify: WHERE in the workflow Auggie should be invoked, WHAT queries would be made, and WHY this improves outcomes."

Agent Group P2.1-AGT (agents): "Evaluate ALL 25 agent definitions that do NOT reference Auggie MCP. For each agent, read its definition and assess the benefit of incorporating codebase-retrieval as a default tool. Categorize using the same HIGH/MEDIUM/LOW/NO scale.

Agents to evaluate: audit-analyzer, audit-comparator, audit-consolidator, audit-scanner, audit-validator, backend-architect, business-panel-experts, deep-research, deep-research-agent, devops-architect, frontend-architect, learning-guide, performance-engineer, pm-agent, python-expert, quality-engineer, refactoring-expert, repo-index, requirements-analyst, root-cause-analyst, security-engineer, self-review, socratic-mentor, system-architect, technical-writer"

Agent Group P2.1-SKL (skills): "Evaluate ALL 5 skills for Auggie MCP integration benefit. Read each SKILL.md and supporting files. Categorize using the same scale.

Skills: sc-cleanup-audit, sc-roadmap, sc-task-unified, sc-validate-tests, confidence-check"
```

### Step 2.2: Adversarial Benefit Validation
For each HIGH/MEDIUM candidate from Step 2.1, spin up **parallel adversarial agents**:

```
Agent P2.2-X-ADVOCATE: "Argue FOR incorporating Auggie MCP into [COMPONENT_NAME]. Present concrete scenarios where semantic code search would catch what Glob/Grep/Read misses. Quantify expected improvements in: precision, token efficiency, developer experience, and analysis depth."

Agent P2.2-X-SKEPTIC: "Argue AGAINST incorporating Auggie MCP into [COMPONENT_NAME]. Challenge the proposed benefits: Is the overhead worth it? Does the component really need semantic search? Would simpler tools suffice? What's the maintenance burden? What happens when Auggie is down?"
```

### Step 2.3: Validated Benefits Summary
Each adversarial pair produces a **Validation Verdict**:
- VALIDATED: Benefits withstand adversarial scrutiny → proceed to Phase 3
- CONDITIONAL: Benefits valid only under specific conditions → document conditions
- REJECTED: Benefits don't survive scrutiny → remove from candidates

Output: A ranked list of validated components with validated benefit scores.

---

## PHASE 3: Implementation Proposals

### Step 3.1: Implementation Design
For each VALIDATED component from Phase 2, spin up a **parallel agent**:

```
Agent P3.1-X: "Design the necessary changes to [COMPONENT_NAME] to implement Auggie MCP integration. Provide:
  1. Exact changes to mcp-servers frontmatter
  2. New workflow steps incorporating codebase-retrieval
  3. Specific information_request query templates for this component's domain
  4. directory_path resolution strategy
  5. Circuit breaker / fallback behavior
  6. Progressive enhancement (works without Auggie, better with it)
  7. Token budget impact (additional tokens for MCP calls vs savings from better results)
  8. Testing plan specific to this component
  9. Documentation updates needed"
```

### Step 3.2: Self-Review via /sc:reflect
Each implementation agent should apply reflective validation:

```
Agent P3.2-X: "Review and validate the implementation proposal for [COMPONENT_NAME] using structured self-reflection:
  1. CORRECTNESS: Does the proposal use the correct MCP tool name and required parameters?
  2. COMPLETENESS: Are all integration points covered? Any missed opportunities?
  3. CONSISTENCY: Does this align with how other components integrate MCP servers?
  4. SAFETY: Is the fallback behavior robust? What happens under failure?
  5. EFFICIENCY: Is the token budget reasonable? Could queries be more targeted?
  6. TESTABILITY: Can the proposal be verified? Are acceptance criteria measurable?
  7. RISK: What could go wrong? Rate each risk 1-5 severity and probability.

  Produce a CONFIDENCE SCORE (0-100) and list any concerns that should be addressed."
```

### Step 3.3: Adversarial Evaluation of Proposals
For each proposal, spin up **2 adversarial agents**:

```
Agent P3.3-X-STRENGTH: "Identify and argue the TOP 3 STRENGTHS of this implementation proposal for [COMPONENT_NAME]. What makes it well-designed? What problems does it solve elegantly?"

Agent P3.3-X-WEAKNESS: "Identify and argue the TOP 3 WEAKNESSES and RISKS of this implementation proposal for [COMPONENT_NAME]. What could fail? What's over-engineered? What's missing? What maintenance burden does it create?"
```

### Step 3.4: Proposal Finalization
Consolidate adversarial feedback into final proposals. Each proposal should include:
- Final implementation spec (incorporating adversarial feedback)
- Risk mitigation plan for each identified weakness
- Go/No-Go recommendation with confidence score

---

## PHASE 4: PRD/Spec Generation via /sc:spec-panel

### Step 4.1: Gather All Final Proposals
Consolidate outputs from Phases 0-3 into a structured input for spec generation.

### Step 4.2: Execute /sc:spec-panel
Use the spec-panel command to generate a formal PRD/Feature Spec with:

```
/sc:spec-panel "Auggie MCP Framework-Wide Integration" --think-hard

Input to spec-panel:
  - Phase 0 alignment report (what's reusable from v1.2 backlog)
  - Phase 1 improvement implementations (existing component upgrades)
  - Phase 2 validated new integrations (new component additions)
  - Phase 3 finalized proposals (implementation specs)

Structure the PRD as:
  1. Executive Summary
  2. Problem Statement (current state: 3/65 components use Auggie)
  3. Solution Overview (framework-wide semantic search integration)
  4. Milestones — one per component upgrade:
     - Milestone N: [Component Name] Auggie MCP Integration
       - Deliverables
       - Acceptance Criteria
       - Testing Plan
       - Dependencies
       - Risk Assessment
  5. Cross-Cutting Concerns:
     - Circuit breaker standardization
     - Fallback behavior consistency
     - Token budget framework
     - mcp-servers frontmatter conventions
  6. Success Metrics
  7. Risk Register
  8. Timeline and Resource Estimates
```

### Step 4.3: Review Cycle
Run /sc:reflect on the generated PRD to validate:
- Internal consistency across milestones
- No duplicate work with v1.2 backlog
- Realistic scope and complexity estimates
- Complete acceptance criteria for every milestone

---

## Execution Notes

### Parallelism Strategy
- **Phase 0**: 4 agents in parallel
- **Phase 1**: 3 + 3 + 6 + 3 + 9 = ~24 agents across 5 steps (many parallelizable)
- **Phase 2**: 3 + N*2 + consolidation = ~15-25 agents
- **Phase 3**: N + N + N*2 + consolidation = ~20-30 agents
- **Phase 4**: Sequential (spec-panel + reflect)
- **Total estimated agent invocations**: 65-85

### Token Management
- Use `--uc` (ultracompressed) for all intermediate agent outputs
- Phase 0 agents: ~5K tokens each
- Phase 1-2 agents: ~3-8K tokens each
- Phase 3 agents: ~5-10K tokens each
- Phase 4: ~15-20K tokens

### Quality Gates Between Phases
- Phase 0 → Phase 1: Alignment report approved, no duplicate work identified
- Phase 1 → Phase 2: All existing uses analyzed, improvements proposed
- Phase 2 → Phase 3: Validated candidates list finalized
- Phase 3 → Phase 4: All proposals pass self-review with confidence ≥ 70%

### Key Constraints
- All Auggie MCP invocations MUST use exact tool name: `mcp__auggie-mcp__codebase-retrieval`
- All invocations MUST include `directory_path` parameter with absolute path
- All integrations MUST include fallback behavior when Auggie is unavailable
- No component should REQUIRE Auggie for basic functionality (progressive enhancement)
