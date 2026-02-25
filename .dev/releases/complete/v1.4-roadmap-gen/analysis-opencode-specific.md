# OpenCode CLI-Specific Analysis

**Analysis Date**: 2026-01-26
**Scope**: All files in `/config/workspace/SuperClaude/.roadmaps/v.1.4-roadmap-gen/`
**Purpose**: Identify all OpenCode CLI-specific specs for Claude Code translation

---

## Executive Summary

**CRITICAL FINDING**: This entire roadmap directory is 100% specific to OpenCode/IBOpenCode. The specification, roadmap, tasklists, and supporting documents describe the `/rf:roadmap-gen` command for IBOpenCode's custom command system, not SuperClaude.

---

## OpenCode-Specific Elements Identified

### 1. Command System Architecture

| Reference | File Location | Description | Criticality |
|-----------|---------------|-------------|-------------|
| `/rf:roadmap-gen` | `roadmap.md` Line 48 | Primary command being built | **CRITICAL** |
| `/rf:crossLLM` | Specification Lines 513-603 | Integration command | **CRITICAL** |
| Command Router | Specification Lines 342-348 | Validates syntax, parses options, routes to orchestrator | **HIGH** |

**OpenCode Command Syntax**:
```
/rf:roadmap-gen <input_spec_path> [options]
```

### 2. Agent System & Prompts

| Agent | File Path | Purpose |
|-------|-----------|---------|
| Orchestrator | `.opencode/agent/rf-roadmap-gen-orchestrator.md` | Main pipeline coordinator |
| Template Scorer | `.opencode/agent/rf-roadmap-gen-template-scorer.md` | Template evaluation |
| Validators | Various `.opencode/agent/` files | Quality validation |

**OpenCode-Specific**: The `.opencode/agent/` directory structure is unique to OpenCode.

### 3. Command Flags & Options

All flags are OpenCode command API-specific:

| Flag | Purpose | Line Reference |
|------|---------|----------------|
| `--chain <model_chain>` | Model selection | Line 76 |
| `--no-upgrade` | Skip upgrade phase | Line 77 |
| `--upgrade-only <artifacts>` | Selective upgrade | Line 78 |
| `--upgrade-threshold <N>` | Quality threshold | Line 79 |
| `--version <N>` | Version specification | Line 80 |
| `--parallel-upgrades` | Parallel execution | Line 81 |
| `--sequential-upgrades` | Sequential execution | Line 82 |
| `--output <dir>` | Output directory | Line 83 |

### 4. Directory Structure

OpenCode-specific file hierarchy:

```
.opencode/                    ← OpenCode config directory (CRITICAL)
├── command/                  ← Command definitions
│   └── rf:roadmap-gen.md
├── agent/                    ← Agent prompts
│   ├── rf-roadmap-gen-orchestrator.md
│   └── rf-roadmap-gen-template-scorer.md
└── resources/                ← Resource templates
    └── templates/
        └── roadmaps/
            ├── feature-release.md
            ├── quality-release.md
            ├── documentation-release.md
            └── variants/

.dev/                         ← Development directory
├── plans/
├── tests/
├── fixtures/
├── mocks/
│   └── crossLLM/            ← Mock responses for testing
└── runs/
    └── rf-crossLLM/         ← crossLLM output

.roadmaps/                    ← Output directory (adaptable)
```

### 5. Model & Configuration Specifications

| Setting | Value | Location |
|---------|-------|----------|
| Orchestrator Model | `gpt-5.2` | Specification Line 658 |
| Template Scorer Model | `claude-sonnet-4-5` | Line 668 |
| Temperature | `0.1` (deterministic) | Line 659 |
| Available Tools | bash, read, write, edit, list, glob, grep, task | Various |

### 6. crossLLM Integration Protocol

**Critical Integration Points**:

- **Invocation**: `/rf:crossLLM v2 file <chain> <artifact_path>`
- **Input**: Any `.md` file in `.roadmaps/<version>/`
- **Output Location**: `.dev/runs/rf-crossLLM/<runId>/`
- **Success File**: `upgrade.md`
- **Result File**: `scorecard.md`

**Interface Contract** (Lines 412-430):
```
Input:   .roadmaps/<version>/*.md
Output:  .dev/runs/rf-crossLLM/<runId>/upgrade.md
         .dev/runs/rf-crossLLM/<runId>/scorecard.md
```

### 7. Phase 7.5 Consistency Validation

**Specification**: Lines 264-293
**Purpose**: Uses `/rf:crossLLM` for content upgrade validation
**OpenCode-Specific**: Command invocation pattern tied to OpenCode infrastructure

### 8. Documentation Output Paths

| Document | Path |
|----------|------|
| User Docs | `docs/generated/Commands/roadmap-gen_UserDoc.md` |
| Technical Docs | `docs/generated/Commands/roadmap-gen_TD.md` |
| Integration Protocol | `docs/generated/crossLLM-Integration-Protocol.md` |

### 9. MCP Server Integration

- **Sequential Thinking MCP** (Line 696, 697): Used for CoT-based algorithm design
- **Usage Context**: Within IBOpenCode's MCP orchestration system
- **Reference**: Line 219 "Use Sequential Thinking MCP to design and refine scoring criteria"

### 10. Quality Assurance Gates

- Integration tests reference `.dev/mocks/crossLLM/`
- Mock responses for `/rf:crossLLM` command execution
- Test environment constraint: "NO writes outside `.dev/` or `.roadmaps/`"

---

## Summary Table: OpenCode-Specific References by Category

| Category | Count | Key References | Criticality |
|----------|-------|----------------|-------------|
| Command Definitions | 2 | `/rf:roadmap-gen`, `/rf:crossLLM` | **CRITICAL** |
| Agent Specifications | 3 | orchestrator, scorer, validators | **CRITICAL** |
| Directory Structure | 6 | `.opencode/*`, `.dev/*` | **CRITICAL** |
| File Paths | 20+ | Template paths, artifact outputs | **HIGH** |
| Interface Contracts | 4 | Command routing, MCP calls | **HIGH** |
| Flags & Options | 8 | All command parameters | **HIGH** |
| Integration Points | 2 | crossLLM integration, protocol | **CRITICAL** |
| Model/Tool Config | 5 | gpt-5.2, claude-sonnet, tools | **MEDIUM** |

---

## Items Requiring Claude Code Translation

1. **Command System** → Claude Code slash commands / skills
2. **Agent System** → Claude Code Task agents / subagents
3. **Directory Structure** → `.claude/` equivalent paths
4. **Command Flags** → Claude Code flag/argument system
5. **crossLLM Integration** → Claude Code multi-agent orchestration
6. **MCP Integration** → Claude Code native MCP support
7. **Template System** → Claude Code resource management
8. **Quality Gates** → Claude Code validation patterns
