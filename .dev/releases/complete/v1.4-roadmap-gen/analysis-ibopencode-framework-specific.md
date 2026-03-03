# IBOpenCode Framework-Specific Analysis

**Analysis Date**: 2026-01-26
**Scope**: All files in `/config/workspace/SuperClaude/.roadmaps/v.1.4-roadmap-gen/`
**Purpose**: Identify all IBOpenCode Framework-specific specs for SuperClaude translation

---

## Executive Summary

**CRITICAL FINDING**: 100% of files (13/13) are exclusively designed for the IBOpenCode Framework. This is a complete roadmap for building the `/rf:roadmap-gen` command as a custom command in the IBOpenCode framework ecosystem.

---

## IBOpenCode Framework-Specific Elements

### 1. Framework Architecture

**File**: `v3.0_Roadmap-Generator-Specification.md` (Lines 7, 339-410)

| Component | Description | SuperClaude Equivalent Needed |
|-----------|-------------|------------------------------|
| Command System | `.opencode/command/` directory | `.claude/commands/` or Skills |
| Agent System | `.opencode/agent/` with model specs | Task agents / subagents |
| Resource System | `.opencode/resources/templates/` | SuperClaude templates |
| Pipeline Architecture | 9-phase agent pipeline | Wave orchestration system |

### 2. IBOpenCode Agent System

**Complete Agent Specifications** (Lines 607-695):

| Agent | Model | Temperature | Purpose |
|-------|-------|-------------|---------|
| `@rf-roadmap-gen-orchestrator` | gpt-5.2 | 0.1 | Main pipeline coordinator |
| `@rf-roadmap-gen-template-scorer` | claude-sonnet-4-5 | 0.1 | Template evaluation |

**Agent Definition Format**:
```yaml
# IBOpenCode Agent Definition
Location: .opencode/agent/{agent-name}.md
Naming: @rf-{command}-{role}
Model: Specified in agent file
Tools: bash, read, write, edit, list, glob, grep, task
```

### 3. IBOpenCode Command Definition System

**Command Registry** (Lines 609-644):

```markdown
# IBOpenCode Command Format
Location: .opencode/command/{command-name}.md
Prefix: /rf: (release framework namespace)
Structure:
  - Syntax definition
  - Options parsing
  - Routing directive to orchestrator
```

**Current Commands**:
- `/rf:roadmap-gen` - Roadmap generation (being built)
- `/rf:crossLLM` - Cross-model validation/upgrade

### 4. crossLLM Integration Protocol

**Section 5** (Lines 513-603) - Framework-level protocol:

| Aspect | Specification |
|--------|--------------|
| Command | `/rf:crossLLM v2 file <chain> <artifact_path>` |
| Applicability | All IBOpenCode commands generating `.md` artifacts |
| Input Contract | Any `.md` file in `.roadmaps/<version>/` |
| Output Contract | `.dev/runs/rf-crossLLM/<runId>/` |
| Reusability | Designed as framework pattern |

**Integration Pseudo-code** (Lines 522-579):
```
For each artifact:
  1. Invoke /rf:crossLLM v2 file <chain> <artifact_path>
  2. Wait for completion
  3. Read .dev/runs/rf-crossLLM/<runId>/scorecard.md
  4. If score >= threshold:
     - Copy upgrade.md to replace original
  5. Else:
     - Keep original, log warning
```

### 5. IBOpenCode Resource Structure

**Template Hierarchy** (Lines 434-477):

```
.opencode/resources/templates/roadmaps/
├── feature-release.md          # New features
├── quality-release.md          # Quality improvements
├── documentation-release.md    # Docs-focused releases
└── variants/                   # Specialized variants
    ├── security-release.md
    ├── performance-release.md
    └── migration-release.md
```

### 6. IBOpenCode File Naming Conventions

| Convention | Pattern | Example |
|------------|---------|---------|
| Command Prefix | `/rf:` | `/rf:roadmap-gen` |
| Agent Naming | `@rf-{name}` | `@rf-roadmap-gen-orchestrator` |
| File Paths | `.opencode/` root | `.opencode/command/rf:roadmap-gen.md` |
| Agent Files | Markdown | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |

### 7. IBOpenCode Persona System

**Phase 2: Persona Selection** (Prompt Lines 102-126):

| Persona Type | Threshold | Selection Logic |
|--------------|-----------|-----------------|
| Primary | >40% relevance | Dominant domain expertise |
| Consulting | >15% relevance | Supporting expertise |

**Algorithm**:
```
For each domain in specification:
  score = domain_weight * relevance_factor
  if score > 40%: assign as Primary
  else if score > 15%: assign as Consulting
```

### 8. Framework Directory Structure

**Complete IBOpenCode Layout**:

```
.opencode/                          # Framework root (CRITICAL)
├── command/                        # Custom commands
│   └── rf:roadmap-gen.md
├── agent/                          # Agent definitions
│   ├── rf-roadmap-gen-orchestrator.md
│   └── rf-roadmap-gen-template-scorer.md
└── resources/                      # Shared resources
    └── templates/
        └── roadmaps/

.dev/                              # Development artifacts
├── plans/                         # Planning documents
├── tests/                         # Test suites
├── fixtures/                      # Test fixtures
├── mocks/                         # Mock data
│   └── crossLLM/                 # crossLLM mocks
└── runs/                          # Execution outputs
    └── rf-crossLLM/              # crossLLM runs

.roadmaps/                         # Generated roadmaps
└── <version>/                     # Version folders
    ├── roadmap.md
    ├── tasklists/
    └── artifacts/

docs/generated/                    # Generated documentation
└── Commands/
    ├── roadmap-gen_UserDoc.md
    └── roadmap-gen_TD.md
```

### 9. IBOpenCode Quality Standards

**Safety Rules** (Prompt Lines 27-47):

| Rule | Description |
|------|-------------|
| Fabrication Prevention | Never invent data without evidence |
| Schema Stability | Maintain output format consistency |
| Boundary Enforcement | NO writes outside `.dev/` or `.roadmaps/` |
| Validation Gates | Multi-phase quality checks |

### 10. IBOpenCode Tasklist Generator

**Metadata Format** (All tasklist files):

```yaml
Generator: Tasklist-Generator v2.1
Generation Mode: Deterministic
Root Path: .dev/plans/v3.0_Roadmaps/v3.0-roadmap-gen/tasklists/
```

**Task ID Convention**: `T{milestone}.{sequence}` (e.g., T01.01, T02.03)

### 11. Version Management

**IBOpenCode Version Convention** (Lines 479-510):

| Version | Meaning |
|---------|---------|
| v1 | Initial draft (pre-upgrade) |
| v2+ | Post-crossLLM upgrade |
| vN | Progressive refinement |

---

## Framework Component Mapping for SuperClaude Translation

| IBOpenCode Component | SuperClaude Equivalent |
|---------------------|------------------------|
| `.opencode/` directory | `.claude/` or `plugins/superclaude/` |
| `/rf:` commands | `/sc:` skills or slash commands |
| `@rf-` agents | Task subagents (Explore, Plan, etc.) |
| `.opencode/resources/` | `src/superclaude/` templates |
| crossLLM integration | Multi-agent Task orchestration |
| Persona system | PERSONAS.md persona auto-activation |
| 9-phase pipeline | Wave orchestration system |
| Tasklist Generator | TodoWrite + Task management mode |
| Quality gates | SuperClaude validation framework |

---

## Critical Dependencies Requiring Translation

1. **Command Registry** → SuperClaude Skills system
2. **Agent Orchestration** → Task tool with subagent_type
3. **crossLLM Protocol** → Multi-agent validation workflow
4. **Template System** → SuperClaude resource management
5. **Persona Selection** → PERSONAS.md auto-activation triggers
6. **Quality Gates** → SuperClaude validation modes
7. **Version Management** → Git-based versioning
8. **Documentation Generation** → Scribe persona + Context7

---

## Scope Analysis Summary

| Metric | Value |
|--------|-------|
| Total Files Analyzed | 13 |
| IBOpenCode-Specific | 13/13 (100%) |
| Technology-Neutral | 0 |
| Directly Reusable | 0 |
| Requires Translation | 13/13 (100%) |

**Conclusion**: Every file requires complete translation to SuperClaude/Claude Code architecture. The Integration Protocol (Section 5) offers the most reusable conceptual pattern.
