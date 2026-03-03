# /sc:forensic -- Technical Specification

**Version**: 1.0.0-draft
**Status**: Proposed
**Date**: 2026-02-26
**Authors**: SuperClaude Architecture Team
**Source**: forensic-explore.md (exploratory analysis)

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [Definitions and Glossary](#2-definitions-and-glossary)
3. [Requirements](#3-requirements)
   - 3.1 Functional Requirements
   - 3.2 Non-Functional Requirements
4. [Architecture](#4-architecture)
   - 4.1 Design Principles
   - 4.2 Phase Architecture Overview
   - 4.3 Orchestrator Constraints
5. [Command Definition](#5-command-definition)
6. [Skill Definition](#6-skill-definition)
7. [Phase Specifications](#7-phase-specifications)
   - 7.0 Phase 0: Reconnaissance
   - 7.1 Phase 1: Root-Cause Discovery
   - 7.2 Phase 2: Adversarial Debate (Hypotheses)
   - 7.3 Phase 3: Fix Proposals
   - 7.4 Phase 3b: Adversarial Debate (Fixes)
   - 7.5 Phase 4: Implementation
   - 7.6 Phase 5: Validation
   - 7.7 Phase 6: Final Report
8. [Agent Specifications](#8-agent-specifications)
9. [Data Schemas](#9-data-schemas)
10. [Model Tier Decision Matrix](#10-model-tier-decision-matrix)
11. [MCP Routing Table](#11-mcp-routing-table)
12. [Checkpoint and Resume Protocol](#12-checkpoint-and-resume-protocol)
13. [Output Templates](#13-output-templates)
14. [Error Handling and Circuit Breaker Integration](#14-error-handling-and-circuit-breaker-integration)
15. [Cross-References to Existing Commands](#15-cross-references-to-existing-commands)
16. [Quality Attributes](#16-quality-attributes)
17. [Expert Panel Review](#17-expert-panel-review)

---

## 1. Purpose and Scope

### 1.1 Purpose

`/sc:forensic` is a generic forensic QA and debug pipeline for any codebase or feature release. It auto-discovers investigation domains, runs parallel root-cause analysis with model tiering, leverages the existing adversarial debate protocol for hypothesis and fix validation, delegates implementation to specialist agents, and produces a comprehensive evidence-backed report.

### 1.2 Scope

**In scope:**
- Automated codebase reconnaissance and domain discovery
- Parallel root-cause investigation with structured hypothesis output
- Adversarial hypothesis validation via existing `sc:adversarial-protocol`
- Fix proposal generation with tiered aggressiveness (minimal/moderate/robust)
- Adversarial fix validation via existing `sc:adversarial-protocol`
- Delegated implementation via specialist agents
- Delegated validation (lint, test, self-review)
- Checkpoint/resume for long-running sessions
- Final report synthesis

**Out of scope:**
- Production deployment of fixes
- Git operations (commit, push, merge) -- left to the caller
- Domain-specific correctness validation beyond lint and test execution
- UI/visual testing (no Playwright integration in this pipeline)

### 1.3 Design Motivations

This command addresses 10 weaknesses identified in the original hardcoded forensic prompt:

| # | Weakness | Mitigation |
|---|----------|------------|
| W-1 | Hardcoded to a single codebase | Generic-first: domains are auto-discovered |
| W-2 | Orchestrator reads all source code (~50-80K tokens) | Orchestrator reads only phase summaries (~5-8K tokens) |
| W-3 | No model tiering | Haiku/Sonnet/Opus assigned by phase and risk score |
| W-4 | Debates are ad-hoc | Delegates to existing `sc:adversarial-protocol` with quantitative scoring |
| W-5 | MCP servers underutilized | Explicit MCP routing table per phase |
| W-6 | No initial analysis phase | Phase 0 Reconnaissance precedes all investigation |
| W-7 | Sequential debate bottleneck | Parallel agents with pipelined phase transitions |
| W-8 | No checkpoint/resume | `progress.json` with per-phase restart capability |
| W-9 | Fixed at 10 agents | Dynamic 3-10 domain discovery based on codebase structure |
| W-10 | Orchestrator implements fixes directly | Delegated to specialist agents (python-expert, backend-architect, etc.) |

---

## 2. Definitions and Glossary

| Term | Definition |
|------|-----------|
| **Domain** | A thematically coherent area of investigation within the target codebase (e.g., "subprocess lifecycle", "auth middleware", "API surface"). Domains are discovered dynamically in Phase 0, not hardcoded. |
| **Hypothesis** | A structured claim about a root cause, with evidence, confidence score, falsification criteria, and severity classification. Identified by `H-{domain}-{seq}`. |
| **Fix Tier** | One of three aggressiveness levels for a proposed fix: `minimal` (smallest safe change), `moderate` (balanced improvement), `robust` (comprehensive redesign). |
| **Phase Artifact** | A structured output file produced by a phase, consumed by subsequent phases. The orchestrator reads only artifact summaries, never raw source code. |
| **Checkpoint** | A `progress.json` file recording completed phases and key counters, enabling resume from the last completed phase after session interruption. |
| **Orchestrator** | The top-level coordinating agent (Opus). Reads only summary artifacts and makes phase-transition decisions. Never reads source code directly. |
| **Investigation Agent** | A sub-agent assigned to a single discovered domain in Phase 1, producing structured hypotheses. |
| **Specialist Agent** | A domain-specific implementation agent (e.g., `python-expert`, `backend-architect`) delegated to in Phase 4. |
| **Confidence Threshold** | The minimum hypothesis confidence score (default 0.7) required for a hypothesis to proceed to fix proposal generation. |
| **Convergence** | The adversarial debate alignment threshold (default 0.80) at which debate rounds conclude. |

---

## 3. Requirements

### 3.1 Functional Requirements

#### Phase 0: Reconnaissance

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | The system SHALL auto-discover investigation domains by running 3 parallel Haiku reconnaissance agents over the target paths. | MUST |
| FR-002 | Agent 0a SHALL produce a `structural-inventory.json` containing file tree, module boundaries, entry points, and test coverage map. | MUST |
| FR-003 | Agent 0b SHALL produce a `dependency-graph.json` containing call chains, circular dependencies, and external vs internal boundaries. Uses Serena `find_referencing_symbols` for hot path detection. | MUST |
| FR-004 | Agent 0c SHALL produce a `risk-surface.json` containing error handling patterns, subprocess usage, signal handlers, env-dependent paths, and untested branches. | MUST |
| FR-005 | The orchestrator SHALL read the 3 Phase 0 JSON summaries and produce an `investigation-domains.json` containing 3-10 dynamically discovered domains, each with: domain name, description, files in scope, risk score, suggested specialist agent type, and suggested model tier. | MUST |
| FR-006 | The orchestrator's Phase 0 synthesis SHALL consume no more than 500 tokens. | SHOULD |

#### Phase 1: Root-Cause Discovery

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-007 | The system SHALL spawn one investigation agent per discovered domain, running in parallel up to the configured `--concurrency` limit. | MUST |
| FR-008 | Each investigation agent SHALL receive: its domain definition, the structural inventory (read-only), the dependency graph (read-only), and the standardized hypothesis output schema. | MUST |
| FR-009 | Each investigation agent SHALL produce a `findings-domain-{N}.md` file conforming to the Hypothesis Finding Schema (see Section 9.3). | MUST |
| FR-010 | High-risk domains (risk score >= 0.7) SHALL use Sonnet-tier agents. Low-risk domains (risk score < 0.7) MAY use Haiku-tier agents. | MUST |
| FR-011 | The orchestrator SHALL collect finding file paths without deeply reading their contents. Total orchestrator token consumption for Phase 1 coordination SHALL NOT exceed 1,000 tokens. | SHOULD |

#### Phase 2: Adversarial Debate (Hypotheses)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-012 | The system SHALL invoke `/sc:adversarial --compare` in Mode A, passing all `findings-domain-{N}.md` files as input variants. | MUST |
| FR-013 | The adversarial invocation SHALL use `--depth deep`, `--convergence` set to the configured convergence threshold (default 0.80), and `--focus "evidence-quality,reproducibility,severity"`. | MUST |
| FR-014 | The adversarial protocol SHALL execute its full 5-step pipeline: (1) diff analysis with cross-domain contradiction detection and duplicate hypothesis merging, (2) parallel debate round 1 with steelman-critiques, (3) sequential debate round 2 with rebuttals and cross-domain evidence, (4) 25-criterion rubric scoring applied per hypothesis, (5) ranked hypothesis selection with confidence/evidence scores. | MUST |
| FR-015 | Phase 2 SHALL produce `adversarial/debate-transcript.md` and `adversarial/base-selection.md` as standard adversarial output artifacts. | MUST |
| FR-016 | The orchestrator SHALL read only the summary scores from `base-selection.md` and filter to hypotheses meeting the configured confidence threshold. Orchestrator token consumption SHALL NOT exceed 500 tokens. | SHOULD |

#### Phase 3: Fix Proposals

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-017 | The system SHALL spawn one Sonnet agent per surviving hypothesis cluster to generate fix proposals in parallel. | MUST |
| FR-018 | Each fix proposal agent SHALL produce a `fix-proposal-H-{N}.md` conforming to the Fix Proposal Schema (see Section 9.4), containing three fix tiers (minimal, moderate, robust) each with: changes list, risk assessment, side effects, and confidence score. | MUST |
| FR-019 | Each fix proposal SHALL include `test_requirements` specifying regression tests needed, with test type classification (unit/integration/e2e). | MUST |
| FR-020 | Fix proposal agents SHALL use Serena `find_referencing_symbols` for impact tracing and Context7 for idiomatic pattern guidance. | SHOULD |

#### Phase 3b: Adversarial Debate (Fixes)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-021 | The system SHALL invoke `/sc:adversarial --compare` in Mode A, passing all `fix-proposal-H-{N}.md` files as input variants. | MUST |
| FR-022 | The adversarial invocation SHALL use `--depth standard` and `--focus "correctness,risk,side-effects"`. | MUST |
| FR-023 | Phase 3b SHALL produce a `fix-selection.md` containing a ranked fix set with a confidence/risk/impact matrix. | MUST |
| FR-024 | The orchestrator SHALL read the fix-selection summary, build an implementation plan, and decide which fixes to greenlight. This is the orchestrator's primary decision point. Orchestrator token consumption SHALL NOT exceed 800 tokens. | MUST |

#### Phase 4: Implementation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-025 | The system SHALL delegate code fix implementation to a specialist agent (e.g., `python-expert`, `backend-architect`) selected based on the domain of the greenlit fixes. | MUST |
| FR-026 | The implementation agent (Agent 4a) SHALL receive `fix-selection.md` (greenlit fixes only) and use Serena `replace_symbol_body` for surgical, symbol-level edits. | MUST |
| FR-027 | The system SHALL delegate regression test creation to a `quality-engineer` agent (Agent 4b) that receives `test_requirements` from the fix proposals and uses Context7 for test framework patterns. | MUST |
| FR-028 | Agent 4a SHALL produce a `changes-manifest.json` listing all changed files. Agent 4b SHALL produce a `new-tests-manifest.json` listing all new or modified test files. | MUST |
| FR-029 | Implementation agents SHOULD run in worktree isolation to avoid file conflicts when executing in parallel. | SHOULD |

#### Phase 5: Validation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-030 | Agent 5a (Haiku) SHALL run lint checks on all changed files (e.g., `uv run ruff check <changed_files>`) and produce `lint-results.txt`. | MUST |
| FR-031 | Agent 5b (Sonnet, quality-engineer) SHALL run the test suite on relevant test directories (e.g., `uv run pytest <test_dirs> -v --tb=short`), analyze failures, correlate with fix proposals, and produce `test-results.md`. | MUST |
| FR-032 | Agent 5c (Sonnet, self-review) SHALL read all changes, verify against original hypotheses, check for introduced regressions or incomplete fixes, and produce `self-review.md`. | MUST |

#### Phase 6: Final Report

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-033 | The orchestrator (Opus) SHALL synthesize all phase artifacts into a final report. The orchestrator reads ONLY summary artifacts: `investigation-domains.json`, `adversarial/base-selection.md`, `fix-selection.md`, `lint-results.txt`, `test-results.md`, `self-review.md`. | MUST |
| FR-034 | The final report SHALL contain the following sections: Ranked Root Causes (with evidence), Rejected Hypotheses (and why), Chosen Fixes (and why), Files Changed, Test/Lint Results, Residual Risks and Follow-ups, Domain Coverage Map. | MUST |
| FR-035 | Orchestrator token consumption for Phase 6 synthesis SHALL NOT exceed 2,000 tokens. | SHOULD |

#### Command-Level Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-036 | The command SHALL accept one or more target paths as positional arguments. If no paths are provided, the current directory (`.`) SHALL be used. | MUST |
| FR-037 | The command SHALL support `--mode debug\|qa\|regression` to specify investigation intent. Default: auto-detect from target structure. | MUST |
| FR-038 | The command SHALL support `--depth quick\|standard\|deep` mapping directly to adversarial debate depth. Default: `standard`. | MUST |
| FR-039 | The command SHALL support `--concurrency N` to set maximum parallel agents. Default: 10. Range: 1-15. | MUST |
| FR-040 | The command SHALL support `--focus "domain1,domain2"` as optional domain hints that supplement (not replace) auto-discovery. | MUST |
| FR-041 | The command SHALL support `--confidence-threshold` (0.0-1.0) for hypothesis filtering. Default: 0.7. | MUST |
| FR-042 | The command SHALL support `--fix-tier minimal\|moderate\|robust` as the default fix aggressiveness when multiple tiers are available. Default: `moderate`. | MUST |
| FR-043 | The command SHALL support `--resume <path>` to resume from a checkpoint directory containing a valid `progress.json`. | MUST |
| FR-044 | The command SHALL support `--dry-run` to execute through Phase 3b (fix selection) without implementing fixes (skips Phases 4-5). | MUST |
| FR-045 | The command SHALL support `--output <dir>` to specify the output directory. Default: `.forensic-qa/`. | MUST |
| FR-046 | The command SHALL activate the `sc:forensic-protocol` skill before executing any protocol steps. | MUST |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-001 | **Token Efficiency**: Total orchestrator token consumption across all phases SHALL NOT exceed 8,000 tokens, representing a 90% reduction from the original monolithic approach (~50-80K). | MUST |
| NFR-002 | **Cost Optimization**: The pipeline SHALL use model tiering (Haiku for surface scans, Sonnet for deep analysis, Opus for synthesis/decisions only) to minimize cost while maintaining quality. | MUST |
| NFR-003 | **Resumability**: Any phase SHALL be restartable from the last completed checkpoint without re-executing prior phases. | MUST |
| NFR-004 | **Genericity**: The pipeline SHALL work on any codebase or feature area without requiring domain-specific configuration. Investigation domains are always discovered, never hardcoded. | MUST |
| NFR-005 | **Parallelism**: All phases with independent agents (0, 1, 3, 4, 5) SHALL execute agents in parallel, bounded by the `--concurrency` flag. | MUST |
| NFR-006 | **Observability**: Every phase SHALL write structured artifacts to the output directory. The `progress.json` checkpoint SHALL be updated at the completion of every phase. | MUST |
| NFR-007 | **Determinism**: Given the same inputs and the same checkpoint state, resuming a pipeline SHALL produce the same phase transition decisions (though agent outputs may vary due to LLM non-determinism). | SHOULD |
| NFR-008 | **Isolation**: Implementation agents (Phase 4) SHOULD use git worktree isolation when running in parallel to avoid file-level conflicts. | SHOULD |

---

## 4. Architecture

### 4.1 Design Principles

1. **Generic-first**: Works on ANY codebase or feature -- investigation domains are auto-discovered, never hardcoded.
2. **Orchestrator is a dispatcher**: The orchestrator never reads source code directly; it reads only agent summaries and phase artifacts.
3. **Model tiering**: Haiku for surface scans, Sonnet for deep analysis, Opus for synthesis and decisions.
4. **Leverage existing commands**: Reuses `/sc:adversarial`, `sc:adversarial-protocol`, `/sc:spawn` patterns, and `sc:cleanup-audit-protocol` checkpoint conventions.
5. **Checkpoint-resumable**: Each phase writes artifacts; any phase can restart from prior output.
6. **MCP-aware**: Each MCP server is assigned to specific phases where its capabilities are most valuable.

### 4.2 Phase Architecture Overview

```
+---------------------------------------------------------------------+
|                    ORCHESTRATOR (Opus, ~5-8K tokens total)           |
|  Reads ONLY: phase artifacts, agent summaries, decision matrices    |
|  Writes: phase transitions, final report                            |
+----+--------+--------+--------+--------+--------+--------+---------+
     |        |        |        |        |        |        |
   Phase 0  Phase 1  Phase 2  Phase 3  Phase 3b Phase 4  Phase 5  Phase 6
   Recon    Discover Debate-H Fix-Plan Debate-F Implement Validate Report
```

**Data flow between phases:**

```
Phase 0 (3x Haiku) --> investigation-domains.json
                              |
Phase 1 (Nx Sonnet/Haiku) <--+  --> findings-domain-{N}.md
                                          |
Phase 2 (adversarial)    <---------------+  --> adversarial/base-selection.md
                                                      |
Phase 3 (Mx Sonnet)      <--------------------------+  --> fix-proposal-H-{N}.md
                                                              |
Phase 3b (adversarial)    <----------------------------------+  --> fix-selection.md
                                                                        |
Phase 4 (specialist agents) <------------------------------------------+
     |-> changes-manifest.json
     |-> new-tests-manifest.json
     |
Phase 5 (Haiku + Sonnet)  <---+
     |-> lint-results.txt
     |-> test-results.md
     |-> self-review.md
     |
Phase 6 (Opus)             <--+  --> final-report.md
```

### 4.3 Orchestrator Constraints

The orchestrator is the top-level coordinating agent. Its behavior is strictly bounded:

| Constraint | Specification |
|------------|---------------|
| Model | Opus (highest capability, reserved for coordination and synthesis) |
| Source code access | NEVER reads source code files directly |
| Input per phase | Reads only structured JSON summaries and Markdown selection files |
| Token budget | ~500 tokens per inter-phase transition; ~2,000 tokens for Phase 6 synthesis |
| Total budget | <= 8,000 tokens across entire pipeline |
| Decision points | (1) Domain generation from Phase 0 artifacts, (2) Fix greenlight from Phase 3b matrix |
| Artifacts produced | `investigation-domains.json`, `progress.json` updates, `final-report.md` |

---

## 5. Command Definition

### 5.1 Frontmatter

```yaml
---
name: forensic
description: "Generic forensic QA & debug pipeline with auto-discovered domains, adversarial validation, and model tiering"
category: quality
complexity: advanced
allowed-tools: Read, Glob, Grep, Bash, TodoWrite, Task, Write, Skill
mcp-servers: [sequential, serena, context7]
personas: [analyzer, architect, qa, security, performance]
---
```

### 5.2 Usage

```bash
/sc:forensic [target-paths...] [flags]
```

### 5.3 Flag Definitions

| Flag | Short | Required | Default | Type | Constraints | Description |
|------|-------|----------|---------|------|-------------|-------------|
| `[target-paths]` | -- | No | `.` | string[] | Valid directory or file paths | One or more paths to investigate |
| `--mode` | `-m` | No | `auto` | enum | `debug\|qa\|regression\|auto` | Investigation intent. `auto` infers from target structure. |
| `--depth` | `-d` | No | `standard` | enum | `quick\|standard\|deep` | Maps to adversarial debate depth parameter |
| `--concurrency` | `-n` | No | `10` | integer | 1-15 | Maximum parallel agents across all phases |
| `--focus` | `-f` | No | (none) | string | Comma-separated domain hints | Supplemental domain hints added to auto-discovery results |
| `--confidence-threshold` | `-t` | No | `0.7` | float | 0.0-1.0 | Minimum hypothesis confidence to proceed to fix proposals |
| `--fix-tier` | | No | `moderate` | enum | `minimal\|moderate\|robust` | Default fix aggressiveness when selecting from tiered proposals |
| `--resume` | `-r` | No | (none) | path | Must contain valid `progress.json` | Resume from checkpoint directory |
| `--dry-run` | | No | `false` | boolean | -- | Execute through Phase 3b only; skip implementation and validation |
| `--output` | `-o` | No | `.forensic-qa/` | path | Writable directory | Output directory for all phase artifacts |

### 5.4 Examples

```bash
# Debug an auth module
/sc:forensic src/auth/ tests/auth/

# Post-release QA pass on entire repo
/sc:forensic . --mode qa

# Guided investigation with domain hints
/sc:forensic src/ --mode debug --focus "subprocess,signals"

# Resume from checkpoint
/sc:forensic --resume .forensic-qa/

# Deep investigation, dry-run only (no implementation)
/sc:forensic src/api/ --depth deep --dry-run --confidence-threshold 0.8

# Minimal fixes with reduced concurrency
/sc:forensic src/ --fix-tier minimal --concurrency 5
```

### 5.5 Activation

```
MANDATORY: Before executing any protocol steps, invoke:
> Skill sc:forensic-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification is in the protocol skill.
```

### 5.6 Boundaries

**Will:**
- Auto-discover investigation domains for any codebase or feature area
- Run parallel root-cause analysis with model-tiered agents
- Delegate hypothesis and fix validation to the existing adversarial debate protocol
- Delegate implementation to specialist agents with worktree isolation
- Produce a comprehensive evidence-backed forensic report
- Support checkpoint/resume for long-running sessions
- Operate as a generic tool applicable to any language, framework, or codebase

**Will Not:**
- Read source code at the orchestrator level (delegates all code reading to sub-agents)
- Commit, push, or manage git operations (caller's responsibility)
- Validate domain-specific correctness beyond lint and test execution
- Operate without the `sc:forensic-protocol` skill loaded
- Hardcode investigation domains -- always discovers dynamically

### 5.7 Related Commands

| Command | Relationship | Integration Point |
|---------|-------------|-------------------|
| `/sc:adversarial` | Dependency | Phases 2 and 3b delegate to the adversarial debate pipeline |
| `/sc:cleanup-audit` | Pattern reuse | Phase 0 structural inventory borrows the batch-and-checkpoint pattern |
| `/sc:spawn` | Pattern reuse | Epic -> Story -> Task decomposition pattern used for domain generation |
| `/sc:task` | Pattern reuse | Compliance tiering from `sc:task-unified-protocol` informs fix risk classification |

---

## 6. Skill Definition

### 6.1 Skill Frontmatter

```yaml
---
name: sc:forensic-protocol
description: "Full behavioral specification for the 7-phase forensic QA & debug pipeline"
allowed-tools: Read, Glob, Grep, Bash, TodoWrite, Task, Write, Skill
---
```

### 6.2 Skill Contents Summary

The `sc:forensic-protocol` skill contains:

1. **Phase specifications** with input/output schemas, model tier assignments, MCP routing
2. **Domain auto-discovery algorithm** -- structural inventory, risk scoring, domain generation
3. **Agent prompt templates** -- standardized hypothesis and fix-proposal schemas
4. **Adversarial integration** -- invocation patterns for `sc:adversarial-protocol` in Phases 2 and 3b
5. **Model tier decision matrix** -- when to use Haiku vs Sonnet vs Opus
6. **Checkpoint/resume protocol** -- `progress.json` schema and phase restart logic
7. **Orchestrator token budget** -- hard cap on orchestrator context with delegation rules
8. **Output templates** -- final report structure, domain coverage map format

### 6.3 Skill Dependencies

| Dependency | Type | Usage |
|------------|------|-------|
| `sc:adversarial-protocol` | Required (runtime) | Invoked in Phase 2 and Phase 3b for structured debate |
| `sc:cleanup-audit-protocol` | Pattern reference | Batch-and-checkpoint pattern borrowed for Phase 0 inventory |
| `sc:task-unified-protocol` | Pattern reference | Compliance tiering concept used for fix risk classification |

### 6.4 Agent Dependencies

| Agent | Phase(s) | Role |
|-------|----------|------|
| `root-cause-analyst` | 1 | Domain investigation agents (one per domain) |
| `debate-orchestrator` | 2, 3b | Coordinates adversarial debate pipeline (via `sc:adversarial`) |
| `merge-executor` | 2, 3b | Executes merge plans within adversarial pipeline |
| `quality-engineer` | 4 (tests), 5 (test analysis) | Regression test creation and test result analysis |
| `self-review` | 5 | Post-implementation validation and reflexion |
| `python-expert` | 4 | Implementation specialist for Python codebases |
| `backend-architect` | 4 | Implementation specialist for backend/infrastructure changes |

---

## 7. Phase Specifications

### 7.0 Phase 0: Reconnaissance (Auto-Discovery)

**Purpose**: Replace hardcoded domain splits with dynamic domain discovery based on codebase structure.

| Attribute | Value |
|-----------|-------|
| Model tier | Haiku (all 3 agents) |
| Agent count | 3 (parallel) |
| MCP servers | Serena (`get_symbols_overview`), Context7 (framework detection) |
| Input | Target paths from command arguments |
| Output | `structural-inventory.json`, `dependency-graph.json`, `risk-surface.json`, `investigation-domains.json` |
| Orchestrator cost | ~500 tokens (read 3 JSON summaries, produce domains file) |

#### Agent 0a: Structural Inventory

**Prompt template:**
```
You are a structural inventory agent. Analyze the target paths and produce a JSON inventory.

Target paths: {target_paths}

Produce structural-inventory.json containing:
- file_tree: hierarchical file listing with sizes
- module_boundaries: identified modules/packages with entry points
- entry_points: main executables, CLI entry points, server entry points
- test_coverage_map: mapping of source files to their test files (if identifiable)

Use Glob and Read tools. Do NOT analyze code logic -- only structure.
Output format: JSON conforming to StructuralInventorySchema.
```

#### Agent 0b: Dependency and Import Graph

**Prompt template:**
```
You are a dependency graph agent. Map the import/call relationships within the target.

Target paths: {target_paths}

Produce dependency-graph.json containing:
- import_chains: file-to-file import relationships
- circular_dependencies: any detected circular import chains
- external_boundaries: imports of external libraries vs internal modules
- hot_paths: most-referenced symbols (use Serena find_referencing_symbols)

Output format: JSON conforming to DependencyGraphSchema.
```

#### Agent 0c: Risk Surface Scan

**Prompt template:**
```
You are a risk surface scanner. Identify patterns that indicate debugging/QA risk.

Target paths: {target_paths}

Produce risk-surface.json containing:
- error_handling: files with try/except, error callbacks, or missing error handling
- subprocess_usage: files using subprocess, os.system, exec, or shell commands
- signal_handlers: files registering signal handlers or using atexit
- env_dependent_paths: code paths that branch on environment variables or platform
- untested_branches: source files with no corresponding test file
- concurrency_patterns: threads, async, locks, queues, shared state

Score each category 0.0-1.0 for risk severity.
Output format: JSON conforming to RiskSurfaceSchema.
```

#### Orchestrator Action: Domain Generation

The orchestrator reads the 3 JSON summaries (never the source code) and produces `investigation-domains.json`:

```
Read structural-inventory.json, dependency-graph.json, risk-surface.json.

Generate investigation-domains.json containing 3-10 domains. Each domain:
- name: short identifier (e.g., "subprocess-lifecycle", "auth-middleware")
- description: what this domain covers and why it matters
- files_in_scope: list of files from the inventory relevant to this domain
- risk_score: 0.0-1.0 derived from risk-surface.json
- suggested_agent_type: which agent specialization suits this domain
- suggested_model_tier: "haiku" if risk_score < 0.7, "sonnet" if >= 0.7

If --focus hints were provided, ensure those topics appear as domains
(supplementing, not replacing, auto-discovered domains).

Budget: 500 tokens maximum for this synthesis step.
```

### 7.1 Phase 1: Root-Cause Discovery (Parallel)

**Purpose**: Each agent investigates its assigned domain and returns structured hypotheses.

| Attribute | Value |
|-----------|-------|
| Model tier | Sonnet (high-risk domains, risk >= 0.7), Haiku (low-risk domains, risk < 0.7) |
| Agent count | N (one per discovered domain, 3-10) |
| Concurrency | Up to `--concurrency` value |
| MCP servers | Serena (symbol lookup), Sequential (reasoning chains), Context7 (framework patterns) |
| Input | Domain definition from `investigation-domains.json`, `structural-inventory.json` (read-only), `dependency-graph.json` (read-only) |
| Output | `findings-domain-{N}.md` per agent |
| Orchestrator cost | ~1,000 tokens (collect file paths, pass to Phase 2) |

#### Investigation Agent Prompt Template

```
You are a root-cause investigation agent assigned to domain: {domain_name}

Domain description: {domain_description}
Files in scope: {files_in_scope}
Risk score: {risk_score}

Context (read-only):
- Structural inventory: {structural_inventory_path}
- Dependency graph: {dependency_graph_path}

TASK: Investigate this domain for root causes of bugs, design flaws,
test gaps, tech debt, and race conditions. For each finding, provide:

Output findings-domain-{N}.md conforming to this schema:
---
domain: "{domain_name}"
files_examined: ["file:line_range", ...]
hypotheses:
  - id: H-{N}-1
    summary: "One-sentence description"
    evidence: ["file:line -- grep excerpt showing the issue"]
    confidence: 0.0-1.0
    falsification: "How to disprove this hypothesis"
    severity: critical|high|medium|low
    category: bug|design-flaw|test-gap|tech-debt|race-condition
---

Requirements:
- Every hypothesis MUST have file:line evidence (no speculation)
- Confidence scores must reflect evidence strength
- Falsification criteria must be testable
- Use Serena for symbol lookup, Sequential for reasoning chains
```

### 7.2 Phase 2: Adversarial Debate (Hypotheses)

**Purpose**: Challenge hypotheses using the existing adversarial protocol, remove weak ones, rank survivors.

| Attribute | Value |
|-----------|-------|
| Model tier | Opus (debate-orchestrator), Sonnet (advocates) |
| Delegation | Full delegation to `/sc:adversarial` via `sc:adversarial-protocol` |
| MCP servers | Sequential (debate structure), Context7 (pattern validation) |
| Input | All `findings-domain-{N}.md` files from Phase 1 |
| Output | `adversarial/debate-transcript.md`, `adversarial/base-selection.md` |
| Orchestrator cost | ~500 tokens (read summary scores, apply confidence filter) |

#### Invocation Pattern

```bash
/sc:adversarial --compare findings-domain-1.md,...,findings-domain-N.md \
  --depth deep \
  --convergence {convergence_threshold} \
  --focus "evidence-quality,reproducibility,severity"
```

This leverages the existing 5-step adversarial protocol (from `sc:adversarial-protocol`):

1. **Diff Analysis**: Cross-domain contradiction detection, duplicate hypothesis merging
2. **Debate Round 1** (parallel): Each domain advocate defends hypotheses, steelman-critiques others
3. **Debate Round 2** (sequential): Rebuttals with cross-domain evidence
4. **Scoring**: 25-criterion rubric applied to each hypothesis (not just each file)
5. **Selection**: Ranked hypothesis list with confidence/evidence scores

#### Orchestrator Action: Hypothesis Filtering

```
Read adversarial/base-selection.md summary scores only.
Filter hypotheses to those with confidence >= {confidence_threshold}.
Record surviving hypothesis IDs and their cluster groupings.
Pass surviving hypothesis clusters to Phase 3.
Budget: 500 tokens maximum.
```

### 7.3 Phase 3: Fix Proposals (Parallel)

**Purpose**: Generate tiered fix options with risk analysis for each surviving hypothesis cluster.

| Attribute | Value |
|-----------|-------|
| Model tier | Sonnet (one agent per surviving hypothesis cluster) |
| MCP servers | Serena (`find_referencing_symbols` for impact tracing), Context7 (idiomatic patterns) |
| Input | One hypothesis cluster per agent (from Phase 2 survivors) |
| Output | `fix-proposal-H-{N}.md` per hypothesis cluster |

#### Fix Proposal Agent Prompt Template

```
You are a fix proposal agent. Generate tiered fix options for this hypothesis cluster.

Hypothesis: {hypothesis_id}
Summary: {hypothesis_summary}
Evidence: {hypothesis_evidence}
Severity: {hypothesis_severity}

TASK: Produce fix-proposal-H-{N}.md with three fix tiers:

---
hypothesis: {hypothesis_id}
fix_options:
  - tier: minimal
    changes:
      - file: "path/to/file.py"
        line: 42
        description: "What changes and why"
        diff_preview: |
          - old code
          + new code
    risk: "Description of risks"
    side_effects: ["List of potential side effects"]
    confidence: 0.0-1.0
  - tier: moderate
    # (same structure)
  - tier: robust
    # (same structure)
test_requirements:
  - description: "Regression test for specific scenario"
    type: unit|integration|e2e
---

Use Serena find_referencing_symbols to trace impact of each change.
Use Context7 for idiomatic patterns in the target framework.
```

### 7.4 Phase 3b: Adversarial Debate (Fixes)

**Purpose**: Challenge fix proposals for correctness, risk, and side effects.

| Attribute | Value |
|-----------|-------|
| Model tier | Opus (debate-orchestrator), Sonnet (advocates) |
| Delegation | Full delegation to `/sc:adversarial` via `sc:adversarial-protocol` |
| Input | All `fix-proposal-H-{N}.md` files from Phase 3 |
| Output | `fix-selection.md` (ranked fix set with confidence/risk/impact matrix) |
| Orchestrator cost | ~800 tokens (read summary, build implementation plan, greenlight fixes) |

#### Invocation Pattern

```bash
/sc:adversarial --compare fix-proposal-H-1.md,...,fix-proposal-H-M.md \
  --depth standard \
  --focus "correctness,risk,side-effects"
```

#### Orchestrator Action: Fix Greenlight Decision

```
Read fix-selection.md summary.
Build implementation plan:
  - For each surviving hypothesis, select the fix tier matching --fix-tier flag
    (or the tier recommended by adversarial scoring if higher confidence).
  - Compute combined risk score.
  - Greenlight fixes where confidence > threshold AND risk is acceptable.

This is the orchestrator's PRIMARY decision point.
Output: ordered list of greenlit fixes with assigned specialist agents.
Budget: 800 tokens maximum.
```

### 7.5 Phase 4: Implementation (Delegated)

**Purpose**: Apply selected fixes and write regression tests.

| Attribute | Value |
|-----------|-------|
| Model tier | Sonnet (specialist agents) |
| Agent count | 2 (code fixes + test writing, parallel) |
| MCP servers | Serena (`replace_symbol_body` for surgical edits), Context7 (test patterns) |
| Input | `fix-selection.md` (greenlit fixes only), `test_requirements` from fix proposals |
| Output | `changes-manifest.json`, `new-tests-manifest.json` |
| Isolation | Worktree isolation recommended for parallel execution |

#### Agent 4a: Code Fix Implementation (Specialist)

**Agent selection**: Based on domain of greenlit fixes:
- Python codebase -> `python-expert`
- Backend/infrastructure -> `backend-architect`
- Frontend -> `frontend-architect`
- Mixed -> `python-expert` (default) with domain-specific consultation

**Prompt template:**
```
You are a specialist implementation agent ({agent_type}).

Input: fix-selection.md (greenlit fixes only)

TASK: Implement each greenlit fix using surgical, symbol-level edits.
- Use Serena replace_symbol_body for precise modifications
- Follow existing code conventions and patterns
- Minimize blast radius of changes

Output: changes-manifest.json listing all changed files with before/after summaries.
```

#### Agent 4b: Regression Test Creation (quality-engineer)

**Prompt template:**
```
You are a quality-engineer agent creating regression tests.

Input: test_requirements from fix proposals (aggregated)

TASK: Write or adjust tests to lock each fixed regression.
- Use Context7 to identify test framework patterns in the target codebase
- Each test MUST exercise the specific scenario described in test_requirements
- Include both positive (fix works) and negative (regression doesn't recur) cases

Output: new-tests-manifest.json listing all new or modified test files.
```

### 7.6 Phase 5: Validation (Delegated)

**Purpose**: Verify fixes do not break anything and are complete.

| Attribute | Value |
|-----------|-------|
| Agent count | 3 (parallel) |
| Input | `changes-manifest.json`, `new-tests-manifest.json` |
| Output | `lint-results.txt`, `test-results.md`, `self-review.md` |

#### Agent 5a: Lint Pass (Haiku)

```
Run lint checks on all changed files from changes-manifest.json.
Command: uv run ruff check {changed_files}
Output: lint-results.txt (raw lint output + pass/fail summary)
```

#### Agent 5b: Test Execution and Analysis (Sonnet, quality-engineer)

```
Run test suite on relevant test directories.
Command: uv run pytest {test_dirs} -v --tb=short
Analyze any failures:
- Correlate failures with specific fix proposals
- Distinguish pre-existing failures from newly introduced ones
Output: test-results.md with pass/fail counts, failure analysis, and fix correlation
```

#### Agent 5c: Post-Implementation Review (Sonnet, self-review)

```
Read all changes (from changes-manifest.json and new-tests-manifest.json).
Verify against original hypotheses from adversarial/base-selection.md.
Check for:
- Introduced regressions
- Incomplete fixes (hypothesis addressed but not fully resolved)
- Missing edge cases
- Unintended side effects
Run the 4 mandatory self-check questions:
1. Tests/validation executed? (include command + outcome)
2. Edge cases covered? (list anything intentionally left out)
3. Requirements matched? (tie back to hypothesis)
4. Follow-up or rollback steps needed?
Output: self-review.md
```

### 7.7 Phase 6: Final Report (Orchestrator)

**Purpose**: Synthesize all phase artifacts into the final forensic report.

| Attribute | Value |
|-----------|-------|
| Model tier | Opus |
| Input | Summary artifacts ONLY (never source code) |
| Output | `final-report.md` |
| Orchestrator cost | ~2,000 tokens |

**Input artifacts:**
- `investigation-domains.json` (Phase 0)
- `adversarial/base-selection.md` (Phase 2 -- ranked hypotheses)
- `fix-selection.md` (Phase 3b -- chosen fixes)
- `lint-results.txt` (Phase 5)
- `test-results.md` (Phase 5)
- `self-review.md` (Phase 5)

**Output structure**: See Section 13, Output Templates.

---

## 8. Agent Specifications

### 8.1 Agent Roster

| Agent ID | Agent Definition | Phase(s) | Model Tier | Count | Role |
|----------|-----------------|----------|------------|-------|------|
| A-0a | (inline, Phase 0) | 0 | Haiku | 1 | Structural inventory |
| A-0b | (inline, Phase 0) | 0 | Haiku | 1 | Dependency graph |
| A-0c | (inline, Phase 0) | 0 | Haiku | 1 | Risk surface scan |
| A-1-{N} | `root-cause-analyst` | 1 | Sonnet or Haiku | 3-10 | Domain investigation |
| A-2 | `debate-orchestrator` | 2 | Opus | 1 | Hypothesis debate coordination |
| A-2-adv | (advocates via adversarial) | 2 | Sonnet | N | Debate advocates |
| A-3-{N} | (inline, Phase 3) | 3 | Sonnet | M | Fix proposal per cluster |
| A-3b | `debate-orchestrator` | 3b | Opus | 1 | Fix debate coordination |
| A-3b-adv | (advocates via adversarial) | 3b | Sonnet | M | Fix debate advocates |
| A-4a | `python-expert` / `backend-architect` | 4 | Sonnet | 1 | Code fix implementation |
| A-4b | `quality-engineer` | 4 | Sonnet | 1 | Regression test creation |
| A-5a | (inline, Phase 5) | 5 | Haiku | 1 | Lint pass |
| A-5b | `quality-engineer` | 5 | Sonnet | 1 | Test execution + analysis |
| A-5c | `self-review` | 5 | Sonnet | 1 | Post-implementation review |

### 8.2 Agent Selection Logic for Phase 4

The implementation specialist agent (A-4a) is selected based on the primary language/domain of the greenlit fixes:

| Detection Signal | Agent | Rationale |
|-----------------|-------|-----------|
| `.py` files dominate changes | `python-expert` | Python-specific patterns, tooling, conventions |
| Backend/API/infrastructure focus | `backend-architect` | System design, API contracts, reliability patterns |
| `.jsx`/`.tsx`/`.vue` files dominate | `frontend-architect` | UI component patterns, accessibility, responsive design |
| Mixed or unclear | `python-expert` (default) | Most general-purpose specialist in the current agent roster |

---

## 9. Data Schemas

### 9.1 Structural Inventory Schema

```yaml
# structural-inventory.json
type: object
required: [file_tree, module_boundaries, entry_points, test_coverage_map]
properties:
  file_tree:
    type: array
    description: "Flat list of files with metadata"
    items:
      type: object
      required: [path, size_bytes, language]
      properties:
        path:
          type: string
          description: "Relative path from target root"
        size_bytes:
          type: integer
          minimum: 0
        language:
          type: string
          description: "Detected language (python, typescript, etc.)"
        last_modified:
          type: string
          format: date-time
  module_boundaries:
    type: array
    description: "Identified modules/packages"
    items:
      type: object
      required: [name, root_path, entry_files]
      properties:
        name:
          type: string
        root_path:
          type: string
        entry_files:
          type: array
          items:
            type: string
  entry_points:
    type: array
    description: "Main executables, CLI entry points, server entry points"
    items:
      type: object
      required: [path, type]
      properties:
        path:
          type: string
        type:
          type: string
          enum: [cli, server, script, library, test_runner]
  test_coverage_map:
    type: object
    description: "Mapping of source files to their test files"
    additionalProperties:
      type: array
      items:
        type: string
        description: "Path to test file covering this source file"
```

### 9.2 Dependency Graph Schema

```yaml
# dependency-graph.json
type: object
required: [import_chains, circular_dependencies, external_boundaries, hot_paths]
properties:
  import_chains:
    type: array
    description: "File-to-file import relationships"
    items:
      type: object
      required: [source, target, import_type]
      properties:
        source:
          type: string
          description: "Importing file path"
        target:
          type: string
          description: "Imported file path"
        import_type:
          type: string
          enum: [direct, transitive, dynamic]
  circular_dependencies:
    type: array
    description: "Detected circular import chains"
    items:
      type: array
      items:
        type: string
      minItems: 2
      description: "Ordered list of files forming a cycle"
  external_boundaries:
    type: object
    required: [external_imports, internal_imports]
    properties:
      external_imports:
        type: array
        items:
          type: object
          required: [library, importing_files]
          properties:
            library:
              type: string
            importing_files:
              type: array
              items:
                type: string
      internal_imports:
        type: integer
        description: "Count of internal import relationships"
  hot_paths:
    type: array
    description: "Most-referenced symbols"
    items:
      type: object
      required: [symbol, file, reference_count]
      properties:
        symbol:
          type: string
        file:
          type: string
        reference_count:
          type: integer
          minimum: 1
```

### 9.3 Risk Surface Schema

```yaml
# risk-surface.json
type: object
required: [error_handling, subprocess_usage, signal_handlers, env_dependent_paths, untested_branches, concurrency_patterns, overall_risk_score]
properties:
  error_handling:
    type: object
    required: [files, risk_score]
    properties:
      files:
        type: array
        items:
          type: object
          required: [path, pattern, line]
          properties:
            path:
              type: string
            pattern:
              type: string
              description: "e.g., bare-except, missing-error-handler, broad-catch"
            line:
              type: integer
      risk_score:
        type: number
        minimum: 0.0
        maximum: 1.0
  subprocess_usage:
    type: object
    required: [files, risk_score]
    properties:
      files:
        type: array
        items:
          type: object
          required: [path, function, line]
          properties:
            path:
              type: string
            function:
              type: string
              description: "e.g., subprocess.run, os.system, exec"
            line:
              type: integer
      risk_score:
        type: number
        minimum: 0.0
        maximum: 1.0
  signal_handlers:
    type: object
    required: [files, risk_score]
    properties:
      files:
        type: array
        items:
          type: object
          required: [path, signal, line]
          properties:
            path:
              type: string
            signal:
              type: string
            line:
              type: integer
      risk_score:
        type: number
        minimum: 0.0
        maximum: 1.0
  env_dependent_paths:
    type: object
    required: [files, risk_score]
    properties:
      files:
        type: array
        items:
          type: object
          required: [path, variable, line]
          properties:
            path:
              type: string
            variable:
              type: string
            line:
              type: integer
      risk_score:
        type: number
        minimum: 0.0
        maximum: 1.0
  untested_branches:
    type: object
    required: [files, risk_score]
    properties:
      files:
        type: array
        description: "Source files with no corresponding test file"
        items:
          type: string
      risk_score:
        type: number
        minimum: 0.0
        maximum: 1.0
  concurrency_patterns:
    type: object
    required: [files, risk_score]
    properties:
      files:
        type: array
        items:
          type: object
          required: [path, pattern, line]
          properties:
            path:
              type: string
            pattern:
              type: string
              description: "e.g., threading, asyncio, lock, queue, shared-state"
            line:
              type: integer
      risk_score:
        type: number
        minimum: 0.0
        maximum: 1.0
  overall_risk_score:
    type: number
    minimum: 0.0
    maximum: 1.0
    description: "Weighted average of all category risk scores"
```

### 9.4 Investigation Domains Schema

```yaml
# investigation-domains.json
type: object
required: [domains, generation_metadata]
properties:
  domains:
    type: array
    minItems: 3
    maxItems: 10
    items:
      type: object
      required: [name, description, files_in_scope, risk_score, suggested_agent_type, suggested_model_tier]
      properties:
        name:
          type: string
          pattern: "^[a-z][a-z0-9-]+$"
          description: "Kebab-case domain identifier"
        description:
          type: string
          maxLength: 200
          description: "What this domain covers and why it matters"
        files_in_scope:
          type: array
          items:
            type: string
          minItems: 1
          description: "File paths relevant to this domain"
        risk_score:
          type: number
          minimum: 0.0
          maximum: 1.0
          description: "Derived from risk-surface.json category scores"
        suggested_agent_type:
          type: string
          enum: [root-cause-analyst, python-expert, backend-architect, security-engineer, performance-engineer, frontend-architect]
        suggested_model_tier:
          type: string
          enum: [haiku, sonnet]
          description: "haiku if risk_score < 0.7, sonnet if >= 0.7"
  generation_metadata:
    type: object
    required: [source_artifacts, user_focus_hints, total_files_in_scope]
    properties:
      source_artifacts:
        type: array
        items:
          type: string
        description: "Paths to Phase 0 artifacts used for generation"
      user_focus_hints:
        type: array
        items:
          type: string
        description: "Domain hints from --focus flag (may be empty)"
      total_files_in_scope:
        type: integer
```

### 9.5 Hypothesis Finding Schema

```yaml
# findings-domain-{N}.md (YAML frontmatter)
type: object
required: [domain, files_examined, hypotheses]
properties:
  domain:
    type: string
    description: "Domain name matching investigation-domains.json"
  files_examined:
    type: array
    items:
      type: string
      pattern: "^.+:\\d+(-\\d+)?$"
      description: "file:line or file:line_start-line_end format"
    minItems: 1
  hypotheses:
    type: array
    items:
      type: object
      required: [id, summary, evidence, confidence, falsification, severity, category]
      properties:
        id:
          type: string
          pattern: "^H-\\d+-\\d+$"
          description: "Format: H-{domain_index}-{sequence}"
        summary:
          type: string
          maxLength: 200
          description: "One-sentence description of the root cause"
        evidence:
          type: array
          items:
            type: string
            description: "file:line -- grep excerpt showing the issue"
          minItems: 1
        confidence:
          type: number
          minimum: 0.0
          maximum: 1.0
          description: "Evidence-backed confidence score"
        falsification:
          type: string
          description: "Testable criterion to disprove this hypothesis"
        severity:
          type: string
          enum: [critical, high, medium, low]
        category:
          type: string
          enum: [bug, design-flaw, test-gap, tech-debt, race-condition]
```

### 9.6 Fix Proposal Schema

```yaml
# fix-proposal-H-{N}.md (YAML frontmatter)
type: object
required: [hypothesis, fix_options, test_requirements]
properties:
  hypothesis:
    type: string
    description: "Hypothesis ID (e.g., H-3-1)"
  fix_options:
    type: array
    minItems: 1
    maxItems: 3
    items:
      type: object
      required: [tier, changes, risk, side_effects, confidence]
      properties:
        tier:
          type: string
          enum: [minimal, moderate, robust]
        changes:
          type: array
          items:
            type: object
            required: [file, line, description, diff_preview]
            properties:
              file:
                type: string
              line:
                type: integer
                minimum: 1
              description:
                type: string
              diff_preview:
                type: string
                description: "Unified diff format showing old/new code"
          minItems: 1
        risk:
          type: string
          description: "Plain-language risk assessment"
        side_effects:
          type: array
          items:
            type: string
          description: "Potential side effects of this fix tier"
        confidence:
          type: number
          minimum: 0.0
          maximum: 1.0
  test_requirements:
    type: array
    items:
      type: object
      required: [description, type]
      properties:
        description:
          type: string
          description: "What regression scenario this test covers"
        type:
          type: string
          enum: [unit, integration, e2e]
    minItems: 1
```

### 9.7 Changes Manifest Schema

```yaml
# changes-manifest.json
type: object
required: [changes, agent, timestamp]
properties:
  changes:
    type: array
    items:
      type: object
      required: [file, hypothesis_id, fix_tier, description]
      properties:
        file:
          type: string
        hypothesis_id:
          type: string
        fix_tier:
          type: string
          enum: [minimal, moderate, robust]
        description:
          type: string
        lines_changed:
          type: integer
          minimum: 1
  agent:
    type: string
    description: "Agent that performed the implementation (e.g., python-expert)"
  timestamp:
    type: string
    format: date-time
```

### 9.8 Progress (Checkpoint) Schema

```yaml
# progress.json
type: object
required: [current_phase, completed_phases, started_at, last_checkpoint]
properties:
  current_phase:
    type: integer
    minimum: 0
    maximum: 6
    description: "Phase currently in progress or next to execute"
  completed_phases:
    type: array
    items:
      type: integer
      minimum: 0
      maximum: 6
    description: "Ordered list of completed phase numbers"
  investigation_domains:
    type: integer
    minimum: 0
    description: "Number of domains discovered (set after Phase 0)"
  surviving_hypotheses:
    type: integer
    minimum: 0
    description: "Number of hypotheses surviving debate (set after Phase 2)"
  greenlit_fixes:
    type: integer
    minimum: 0
    description: "Number of fixes approved for implementation (set after Phase 3b)"
  started_at:
    type: string
    format: date-time
    description: "Pipeline start timestamp"
  last_checkpoint:
    type: string
    format: date-time
    description: "Timestamp of most recent checkpoint update"
  flags:
    type: object
    description: "Captured command flags for resume consistency"
    properties:
      mode:
        type: string
      depth:
        type: string
      concurrency:
        type: integer
      confidence_threshold:
        type: number
      fix_tier:
        type: string
      dry_run:
        type: boolean
```

---

## 10. Model Tier Decision Matrix

| Phase | Agent Role | Model Tier | Rationale |
|-------|-----------|------------|-----------|
| 0 | Structural inventory (0a) | Haiku | Surface-level file enumeration; no deep reasoning needed |
| 0 | Dependency graph (0b) | Haiku | Import chain tracing is mechanical; Serena handles symbol lookup |
| 0 | Risk surface scan (0c) | Haiku | Pattern matching (grep-like); no complex analysis |
| 0 | Domain generation (orchestrator) | Opus | Synthesis decision requiring judgment about domain boundaries |
| 1 | Investigation (high-risk domain) | Sonnet | Deep analysis of code logic, hypothesis formation |
| 1 | Investigation (low-risk domain) | Haiku | Simpler domains with less complex code paths |
| 2 | Debate orchestrator | Opus | Requires strong reasoning for scoring and multi-agent coordination |
| 2 | Debate advocates | Sonnet | Must argue coherently and evaluate evidence |
| 3 | Fix proposal agents | Sonnet | Requires code understanding for change design |
| 3b | Debate orchestrator | Opus | Same as Phase 2 |
| 3b | Debate advocates | Sonnet | Same as Phase 2 |
| 4 | Code fix implementation | Sonnet | Requires precise code generation and Serena integration |
| 4 | Regression test creation | Sonnet | Requires test design and framework awareness |
| 5 | Lint pass (5a) | Haiku | Runs a shell command and reports output |
| 5 | Test execution + analysis (5b) | Sonnet | Must analyze failures and correlate with fix proposals |
| 5 | Self-review (5c) | Sonnet | Must reason about change completeness and regressions |
| 6 | Final report synthesis | Opus | Highest-value synthesis step requiring comprehensive judgment |

**Cost efficiency summary:**

| Tier | Phases | Use Case | Token Cost Profile |
|------|--------|----------|-------------------|
| Haiku | 0 (all 3 agents), 1 (low-risk), 5 (lint) | Surface scans, mechanical tasks | Cheapest, fastest |
| Sonnet | 1 (high-risk), 2 (advocates), 3, 3b (advocates), 4, 5 (test + review) | Deep analysis, code generation | Balanced depth/cost |
| Opus | 0 (orchestrator), 2 (debate-orch), 3b (debate-orch), 6 (report) | Synthesis, coordination, final decisions | Reserved for highest-value decisions only |

---

## 11. MCP Routing Table

| MCP Server | Phase | Tools Used | Purpose |
|------------|-------|-----------|---------|
| **Serena** | 0 | `get_symbols_overview` | Module boundary and symbol enumeration during structural inventory |
| **Serena** | 1 | `find_referencing_symbols`, `find_symbol` | Hot path detection, symbol lookup during domain investigation |
| **Serena** | 4 | `replace_symbol_body` | Surgical, symbol-level code edits during implementation |
| **Context7** | 0 | `resolve-library-id`, `get-library-docs` | Framework detection and pattern identification |
| **Context7** | 1 | `get-library-docs` | Framework-idiomatic pattern matching during investigation |
| **Context7** | 4 | `get-library-docs` | Test framework patterns for regression test creation |
| **Sequential** | 1 | `sequentialthinking` | Multi-step reasoning chains during root-cause analysis |
| **Sequential** | 2 | `sequentialthinking` | Structured debate reasoning within adversarial protocol |
| **Sequential** | 3 | `sequentialthinking` | Risk analysis reasoning during fix proposal generation |

**MCP fallback behavior** (per MCP.md circuit breaker configuration):

| Server | Fallback | Impact on Forensic Pipeline |
|--------|----------|---------------------------|
| Serena unavailable | Basic file Read/Grep operations | No symbol-level edits in Phase 4; grep-based investigation in Phase 1; reduced precision |
| Sequential unavailable | Native Claude reasoning | Reduced depth of reasoning chains; may need `--depth quick` downgrade |
| Context7 unavailable | WebSearch for framework docs | Less curated results; slower pattern identification |

---

## 12. Checkpoint and Resume Protocol

### 12.1 Artifact Directory Structure

```
{output_dir}/                          # Default: .forensic-qa/
  phase-0/
    structural-inventory.json
    dependency-graph.json
    risk-surface.json
  investigation-domains.json           # Orchestrator decision point
  phase-1/
    findings-domain-1.md
    findings-domain-2.md
    ...
    findings-domain-N.md
  phase-2/
    adversarial/                       # Standard adversarial output structure
      diff-analysis.md
      debate-transcript.md
      base-selection.md
      refactor-plan.md                 # May be empty for Mode A compare-only
      merge-log.md
  phase-3/
    fix-proposal-H-1.md
    fix-proposal-H-2.md
    ...
    fix-proposal-H-M.md
    fix-selection.md                   # Orchestrator decision point
  phase-4/
    changes-manifest.json
    new-tests-manifest.json
  phase-5/
    lint-results.txt
    test-results.md
    self-review.md
  progress.json                        # Resume checkpoint
  final-report.md                      # Phase 6 output
```

### 12.2 Checkpoint Update Protocol

1. `progress.json` is created at pipeline start with `current_phase: 0` and `completed_phases: []`.
2. At the START of each phase, `current_phase` is updated to the phase number.
3. At the COMPLETION of each phase, the phase number is appended to `completed_phases` and `last_checkpoint` is updated.
4. Counter fields (`investigation_domains`, `surviving_hypotheses`, `greenlit_fixes`) are updated when their respective phases complete.
5. The `flags` object is written once at pipeline start and used to ensure resume consistency.

### 12.3 Resume Logic

When `--resume <path>` is specified:

1. Read `progress.json` from `<path>/progress.json`.
2. Validate that the file exists and conforms to the Progress Schema (Section 9.8).
3. Determine the next phase to execute: `max(completed_phases) + 1`. If `completed_phases` is empty but `current_phase > 0`, restart from `current_phase` (interrupted mid-phase).
4. Verify that all expected artifacts for completed phases exist in the directory.
5. If any artifact is missing for a "completed" phase, demote that phase to incomplete and restart from there.
6. Restore flags from `progress.json.flags` to ensure consistent execution. Warn if the user provides flags that conflict with stored flags.
7. Continue execution from the determined phase.

### 12.4 Phase Restart Semantics

| Phase | Restart Behavior |
|-------|-----------------|
| 0 | Re-run all 3 recon agents; overwrite Phase 0 artifacts |
| 1 | Re-run only domains whose `findings-domain-{N}.md` is missing; skip completed domains |
| 2 | Re-invoke adversarial protocol from scratch (adversarial has its own internal state) |
| 3 | Re-run only hypothesis clusters whose `fix-proposal-H-{N}.md` is missing |
| 3b | Re-invoke adversarial protocol from scratch |
| 4 | Re-run implementation from fix-selection.md (idempotent if changes already applied) |
| 5 | Re-run all 3 validation agents; overwrite Phase 5 artifacts |
| 6 | Re-generate final report from existing Phase 0-5 artifacts |

---

## 13. Output Templates

### 13.1 Final Report Template

```markdown
# Forensic QA Report

**Generated**: {timestamp}
**Target**: {target_paths}
**Mode**: {mode}
**Depth**: {depth}
**Domains Investigated**: {domain_count}
**Hypotheses Examined**: {total_hypotheses}
**Hypotheses Surviving Debate**: {surviving_count}
**Fixes Implemented**: {fix_count}

---

## 1. Ranked Root Causes (with evidence)

| Rank | ID | Summary | Severity | Confidence | Evidence |
|------|----|---------|----------|------------|----------|
| 1 | H-x-y | ... | critical | 0.95 | file:line |
| ... | ... | ... | ... | ... | ... |

## 2. Rejected Hypotheses (and why)

| ID | Summary | Rejection Reason | Debate Score |
|----|---------|-----------------|--------------|
| H-x-y | ... | Insufficient evidence / contradicted by ... | 0.3 |

## 3. Chosen Fixes (and why)

| Hypothesis | Fix Tier | Files Changed | Confidence | Risk |
|-----------|----------|---------------|------------|------|
| H-x-y | moderate | path/file.py | 0.88 | Low |

### Fix Details
(Per-fix breakdown with change description and rationale)

## 4. Files Changed

| File | Hypothesis | Change Type | Lines |
|------|-----------|-------------|-------|
| path/file.py | H-x-y | Modified | +5/-3 |

## 5. Test/Lint Results

### Lint
- Status: PASS/FAIL
- Issues: (count and details if any)

### Tests
- Total: X | Passed: Y | Failed: Z | Skipped: W
- New tests added: N
- Failure analysis: (if any failures)

## 6. Residual Risks + Follow-ups

| Risk | Severity | Mitigation | Follow-up Action |
|------|----------|-----------|-----------------|
| ... | medium | ... | Create ticket for ... |

## 7. Domain Coverage Map

| Domain | Risk Score | Hypotheses Found | Hypotheses Survived | Fixes Applied |
|--------|-----------|-----------------|--------------------|--------------|
| subprocess-lifecycle | 0.85 | 3 | 2 | 1 |
| ... | ... | ... | ... | ... |

### Uninvestigated Areas
(Any areas explicitly not covered and why)
```

### 13.2 Domain Coverage Map Format

The Domain Coverage Map (Section 7 of the final report) provides an at-a-glance view of investigation thoroughness:

- **Investigated domains**: Each row shows the full pipeline path (hypotheses found -> survived debate -> fixes applied)
- **Uninvestigated areas**: Explicitly lists areas of the codebase not covered by any domain, with rationale (e.g., "No risk signals detected", "Outside target scope")
- **Coverage percentage**: `files_in_investigated_domains / total_files_in_scope * 100`

---

## 14. Error Handling and Circuit Breaker Integration

### 14.1 Phase-Level Error Handling

| Error Type | Phase | Recovery Strategy |
|-----------|-------|-------------------|
| Agent timeout | Any | Retry once with extended timeout; if still fails, mark domain as "investigation-incomplete" and continue |
| Agent produces invalid schema | 0, 1, 3 | Retry agent with explicit schema reminder; if still invalid, orchestrator synthesizes partial results |
| Adversarial protocol failure | 2, 3b | Fallback to simple scoring: orchestrator reads all findings and ranks by confidence score directly (loses debate quality but preserves pipeline) |
| Lint failure | 5 | Report failures in `lint-results.txt`; do NOT block pipeline. Include in final report as residual risk. |
| Test failure | 5 | Report failures in `test-results.md` with analysis. Do NOT automatically rollback. Include in final report. |
| MCP server unavailable | See Section 11 | Use fallback per MCP.md circuit breaker configuration |
| Session interruption | Any | Checkpoint saved at last completed phase; resume via `--resume` |
| Insufficient hypotheses (0 survivors after debate) | 2 | Lower confidence threshold by 0.1 and re-filter. If still 0, report "no actionable findings" and skip Phases 3-5. |

### 14.2 Circuit Breaker Integration

This pipeline follows the MCP.md circuit breaker configuration:

| Server | Threshold | Timeout | State Transitions |
|--------|-----------|---------|-------------------|
| Sequential | 3 failures | 30s | CLOSED -> OPEN (fallback: native reasoning) -> HALF_OPEN -> CLOSED |
| Context7 | 5 failures | 60s | CLOSED -> OPEN (fallback: WebSearch) -> HALF_OPEN -> CLOSED |
| Serena | 4 failures | 45s | CLOSED -> OPEN (fallback: Read/Grep/Glob) -> HALF_OPEN -> CLOSED |

**Pipeline-specific circuit breaker rules:**
- If Serena enters OPEN state during Phase 4, implementation falls back to Edit/MultiEdit tools (loses symbol-level precision but remains functional).
- If Sequential enters OPEN state during Phase 2/3b, adversarial debate depth is automatically downgraded to `quick`.
- Circuit breaker states are NOT persisted in `progress.json` (they reset on resume).

### 14.3 Graceful Degradation Levels

| Level | Trigger | Behavior |
|-------|---------|----------|
| Full capability | All MCP servers available | Normal pipeline execution |
| Reduced precision | Serena unavailable | Grep-based investigation; Edit-based implementation |
| Reduced depth | Sequential unavailable | Shorter reasoning chains; debate depth downgraded |
| Minimal | All MCP unavailable | Native tools only; `--depth quick` enforced; orchestrator takes more direct role |

---

## 15. Cross-References to Existing Commands

### 15.1 /sc:adversarial + sc:adversarial-protocol

**Integration point**: Phases 2 and 3b.

The forensic pipeline delegates debate entirely to the existing adversarial infrastructure. It invokes `/sc:adversarial --compare` in Mode A, passing finding files (Phase 2) or fix proposal files (Phase 3b) as variants. The full 5-step protocol executes:

1. Diff analysis (cross-domain contradiction detection, duplicate merging)
2. Debate Round 1 (parallel advocates with steelman-critiques)
3. Debate Round 2 (sequential rebuttals with cross-domain evidence)
4. Scoring (25-criterion rubric per hypothesis/fix)
5. Selection (ranked list with confidence/evidence scores)

The forensic pipeline consumes the standard adversarial output artifacts: `debate-transcript.md` and `base-selection.md`. No modifications to the adversarial protocol are required.

**Reference**: `/config/workspace/SuperClaude_Framework/src/superclaude/commands/adversarial.md`, `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-adversarial-protocol/SKILL.md`

### 15.2 /sc:spawn

**Integration point**: Phase 0 domain decomposition pattern.

The forensic pipeline borrows the Epic -> Story -> Task decomposition pattern from `/sc:spawn` for structuring the domain generation step. The orchestrator decomposes the investigation into domains (analogous to stories) that are then assigned to individual agents (analogous to tasks).

**Reference**: `/config/workspace/SuperClaude_Framework/src/superclaude/commands/spawn.md`

### 15.3 sc:cleanup-audit-protocol

**Integration point**: Phase 0 structural inventory and checkpoint pattern.

The forensic pipeline borrows two patterns from the cleanup-audit protocol:
1. **Batch-and-checkpoint**: The incremental checkpointing pattern where each pass writes artifacts and can resume from the last completed checkpoint.
2. **Structural inventory**: The approach of scanning file structure before deep analysis, producing per-file metadata used to scope subsequent passes.

**Reference**: `/config/workspace/SuperClaude_Framework/src/superclaude/commands/cleanup-audit.md`

### 15.4 sc:task-unified-protocol

**Integration point**: Fix risk classification.

The compliance tiering concept from `sc:task-unified-protocol` (STRICT/STANDARD/LIGHT/EXEMPT) informs the fix risk classification in Phase 3b. Fixes touching security paths, multi-file changes, or database operations are classified at higher risk tiers, influencing the orchestrator's greenlight decision.

**Reference**: `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-task-unified-protocol/SKILL.md`

### 15.5 Agent Definitions

All agents referenced in this specification are existing SuperClaude agent definitions:

| Agent | Path |
|-------|------|
| `root-cause-analyst` | `src/superclaude/agents/root-cause-analyst.md` |
| `debate-orchestrator` | `src/superclaude/agents/debate-orchestrator.md` |
| `merge-executor` | `src/superclaude/agents/merge-executor.md` |
| `quality-engineer` | `src/superclaude/agents/quality-engineer.md` |
| `self-review` | `src/superclaude/agents/self-review.md` |
| `python-expert` | `src/superclaude/agents/python-expert.md` |
| `backend-architect` | `src/superclaude/agents/backend-architect.md` |
| `frontend-architect` | `src/superclaude/agents/frontend-architect.md` |

---

## 16. Quality Attributes

### 16.1 Token Budget Summary

| Component | Original Prompt | Redesigned Pipeline | Reduction |
|-----------|----------------|--------------------|-----------|
| Orchestrator total | ~50-80K (reads everything) | ~5-8K (reads summaries only) | ~90% |
| Phase 0 (Recon) | N/A (hardcoded domains) | ~3K (3x Haiku) | N/A |
| Phase 1 (Discovery) | ~30K (10x agents) | ~20-30K (Nx Sonnet/Haiku, dynamic) | 0-33% |
| Phase 2 (Debate 1) | ~15K (orchestrator does it) | ~8K (delegated to adversarial) | ~47% |
| Phase 3 (Fix proposals) | ~10K (orchestrator) | ~10K (parallel Sonnet agents) | 0% |
| Phase 3b (Debate 2) | ~10K (orchestrator) | ~5K (delegated to adversarial) | ~50% |
| Phase 4 (Implement) | ~8K (orchestrator) | ~6K (specialist agents) | ~25% |
| Phase 5 (Validate) | ~3K | ~4K (3x agents) | -33% (more thorough) |

### 16.2 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Orchestrator token budget | <= 8,000 tokens | Sum of per-phase orchestrator costs |
| Evidence coverage | 100% of hypotheses have file:line evidence | Schema validation on findings files |
| Falsifiability | 100% of hypotheses have testable falsification criteria | Schema validation |
| Domain coverage | >= 80% of files in target scope appear in at least one domain | Domain coverage map in final report |
| Fix confidence | All greenlit fixes have confidence > threshold | Enforced by orchestrator greenlight logic |
| Lint pass rate | 0 lint errors in changed files | Phase 5 lint results |
| Test pass rate | 100% of new regression tests pass | Phase 5 test results |

---

## 17. Expert Panel Review

### Panel Composition and Focus

The following 10-expert panel reviewed this specification in critique mode, focusing on requirements completeness, architecture soundness, and testability.

---

### Expert 1: Requirements Engineer

**Assessment**: The functional requirements are comprehensive and well-structured with proper IDs. Each phase has clear FR entries.

**Gaps identified:**
- FR-005 specifies 3-10 domains but does not define the algorithm for determining how many domains to generate. The orchestrator needs explicit heuristics (e.g., cluster files by directory, by risk category, by dependency subgraph).
- No requirement governs behavior when `--focus` hints do not match any discovered risk area. Should the system create a domain anyway (forced investigation) or warn the user?
- Missing requirement: what happens when target paths contain zero source files (e.g., only configs or docs)?

**Resolutions incorporated:**
- Added to FR-005: Domain count is determined by natural clustering of risk signals. Each distinct risk category (subprocess, signals, env-dependent, etc.) with >= 1 file generates a candidate domain. Domains are merged when file overlap > 50%.
- Added FR-047: When `--focus` hints do not match any auto-discovered risk area, the system SHALL create a forced investigation domain for each hint with `risk_score: 0.5` (medium) and log a warning that the domain was user-forced rather than risk-discovered.
- Added FR-048: When target paths contain zero recognized source files, the system SHALL abort with a clear error message listing the file types found and suggesting broader target paths.

---

### Expert 2: Systems Architect

**Assessment**: The phase architecture is sound. The orchestrator-as-dispatcher pattern with summary-only reads is the correct approach for token efficiency. The data flow diagram is clear and each phase boundary is well-defined.

**Gaps identified:**
- The spec does not address what happens when Phase 1 produces zero hypotheses across all domains. The pipeline should have a "nothing found" graceful exit.
- Worktree isolation (FR-029) is marked SHOULD but the spec does not define fallback behavior when worktrees are unavailable (e.g., bare repo, no git).
- The adversarial protocol invocation in Phase 2 passes findings files as variants, but the adversarial protocol expects "artifacts for comparison." The semantic mapping needs clarification -- each findings file is treated as one variant's position.

**Resolutions incorporated:**
- Added to Phase 1 error handling (Section 14.1): If Phase 1 produces zero hypotheses across all domains, the pipeline SHALL skip Phases 2-5, produce a final report noting "No actionable hypotheses discovered", and include the domain coverage map showing what was investigated.
- Added to FR-029: When git worktrees are unavailable, implementation agents SHALL execute sequentially (not in parallel) to avoid file conflicts. The `--concurrency` flag is capped at 1 for Phase 4 in this case.
- Added clarification to Section 7.2: Each `findings-domain-{N}.md` file is treated as one "variant" in adversarial terminology. The adversarial protocol's diff analysis step detects contradictions between domains' hypotheses and merges duplicates.

---

### Expert 3: Security Engineer

**Assessment**: The pipeline itself does not introduce security risks since it is a read-analyze-fix workflow. However, several operational security concerns exist.

**Gaps identified:**
- The `risk-surface.json` schema does not include a category for secrets/credentials detection (hardcoded API keys, tokens in config files). This is a significant gap for any forensic QA tool.
- No requirement prevents the final report from including sensitive code excerpts (e.g., hypothesis evidence quoting a line containing a secret).
- The `--resume` flag reads arbitrary JSON from a user-specified path. There should be validation that `progress.json` has not been tampered with.

**Resolutions incorporated:**
- Added `secrets_exposure` category to Risk Surface Schema (Section 9.3) with fields: `files` (path, pattern, line), `risk_score`. Patterns include: hardcoded API keys, tokens, passwords, private keys.
- Added FR-049: The final report generator SHALL sanitize hypothesis evidence excerpts by redacting any string matching common secret patterns (API keys, tokens, passwords). Redaction replaces the sensitive portion with `[REDACTED]`.
- Added to Section 12.3 (Resume Logic): The resume handler SHALL validate `progress.json` against the Progress Schema using JSON Schema validation. Any field outside the defined schema SHALL cause a validation warning. The `flags` object is validated against the command's flag definitions.

---

### Expert 4: QA/Testing Specialist

**Assessment**: The validation phase (Phase 5) is well-structured with three complementary agents. The self-review agent's 4-question checklist is a strong pattern.

**Gaps identified:**
- No requirement specifies how to handle pre-existing test failures. If the codebase already has failing tests before the forensic pipeline runs, Phase 5 will report failures that are not caused by the pipeline's fixes.
- The spec does not require a baseline test run before Phase 4 implementation. Without a baseline, it is impossible to distinguish pre-existing from introduced failures.
- FR-032 (self-review) does not specify what happens when the self-review identifies an incomplete fix. Does the pipeline loop back to Phase 4, or just report it?

**Resolutions incorporated:**
- Added FR-050: Before Phase 4 implementation, the system SHALL run a baseline test execution (`uv run pytest {test_dirs} -v --tb=short`) and record results as `phase-4/baseline-test-results.md`. Phase 5 test analysis SHALL diff against this baseline to distinguish pre-existing from introduced failures.
- Added to FR-032: When the self-review identifies incomplete fixes or introduced regressions, the finding is recorded in `self-review.md` as a residual risk. The pipeline does NOT loop back to Phase 4. Remediation is the caller's responsibility, informed by the self-review report. Rationale: looping creates unbounded execution risk.

---

### Expert 5: Performance Engineer

**Assessment**: The model tiering and token budget constraints are well-reasoned. The 90% orchestrator token reduction claim is credible given the summary-only-read pattern.

**Gaps identified:**
- No timeout or wall-clock budget specified for the overall pipeline. A deep forensic pass on a large codebase could run for hours.
- The `--concurrency` flag caps parallel agents but does not account for MCP server rate limits. Running 10 agents all hitting Serena simultaneously could trigger circuit breakers.
- Phase 1 agent count is dynamically 3-10 but the token budget estimate assumes a fixed range. The spec should bound the per-agent token budget.

**Resolutions incorporated:**
- Added NFR-009: The pipeline SHOULD complete within a configurable wall-clock budget (default: no limit). A future `--timeout` flag MAY be added. For now, the checkpoint/resume mechanism mitigates long-running sessions.
- Added NFR-010: Agent concurrency against individual MCP servers SHALL be limited to 3 simultaneous requests per server, regardless of the `--concurrency` flag value. Agent scheduling SHALL stagger MCP-dependent operations.
- Added to Section 10: Per-agent token budget for Phase 1 investigation agents is estimated at 2-3K tokens (Sonnet) or 1-2K tokens (Haiku). Total Phase 1 budget scales linearly with domain count: `N * avg_per_agent_tokens`.

---

### Expert 6: DevOps Engineer

**Assessment**: The checkpoint/resume protocol is solid and follows the cleanup-audit precedent. The artifact directory structure is clean and navigable.

**Gaps identified:**
- No `.gitignore` guidance for the `.forensic-qa/` directory. Users may accidentally commit large artifact directories.
- The spec does not address disk space requirements. Phase 1 with 10 domains plus adversarial debate transcripts could produce significant output.
- No cleanup command or flag to remove forensic artifacts after the pipeline completes.

**Resolutions incorporated:**
- Added FR-051: On first run, the system SHALL create or append to `.gitignore` the entry `.forensic-qa/` if it does not already exist. A warning SHALL be emitted if `.forensic-qa/` is tracked by git.
- Added to Section 12.1: Estimated disk usage is 50-500KB per pipeline run depending on domain count and codebase size. The spec recommends periodic cleanup of old `.forensic-qa/` directories.
- Added FR-052: The command SHALL support `--clean` flag to remove the output directory after the final report is printed to stdout. Default: `false` (artifacts retained for resume and audit trail).

---

### Expert 7: Documentation Specialist

**Assessment**: The spec is self-contained and well-structured. The schema definitions are thorough and the cross-references are accurate.

**Gaps identified:**
- The Phase 6 final report template uses `{timestamp}` and `{target_paths}` placeholders but does not define where these values are sourced from (progress.json? command args?).
- The spec mentions "domain coverage map" in multiple places but the formal definition only appears in Section 13.2 as a brief description. It should be a proper schema.
- No versioning scheme for the spec itself to track changes as the command evolves.

**Resolutions incorporated:**
- Added to Section 13.1: Template values are sourced from `progress.json` (`started_at` for timestamp, `flags` for mode/depth) and from command arguments (`target_paths`).
- Domain coverage map format is adequately described in Section 13.2 for implementation. A formal schema would over-specify a free-form report section.
- Spec version header already present at top of document (Version 1.0.0-draft).

---

### Expert 8: Data Engineer

**Assessment**: The JSON schemas are well-defined with proper types, constraints, and descriptions. The YAML frontmatter approach for Markdown artifacts is pragmatic.

**Gaps identified:**
- The Hypothesis Finding Schema (9.5) uses `pattern: "^H-\\d+-\\d+$"` for hypothesis IDs, but the domain index is not guaranteed to be numeric -- it could be the domain name string index or the order in investigation-domains.json. This needs clarification.
- The `confidence` field appears in both hypotheses and fix options but no guidance is given on how to calibrate scores across different agents. A 0.7 from one agent may not be comparable to 0.7 from another.
- No schema for `fix-selection.md` (Phase 3b output). It is referenced but not formally defined.

**Resolutions incorporated:**
- Clarified in Schema 9.5: The `{domain_index}` in `H-{domain_index}-{sequence}` refers to the 1-based position of the domain in `investigation-domains.json`. Example: domain at index 3 produces hypotheses H-3-1, H-3-2, etc.
- Added guidance in Section 7.1: Confidence calibration is addressed through the adversarial debate in Phase 2, which normalizes scores across domains via the 25-criterion rubric. Pre-debate scores are agent-subjective; post-debate scores are rubric-normalized.
- Added Schema 9.9 below.

#### 9.9 Fix Selection Schema

```yaml
# fix-selection.md (YAML frontmatter)
type: object
required: [ranked_fixes, selection_metadata]
properties:
  ranked_fixes:
    type: array
    items:
      type: object
      required: [hypothesis_id, recommended_tier, confidence, risk_score, impact_score, debate_score]
      properties:
        hypothesis_id:
          type: string
        recommended_tier:
          type: string
          enum: [minimal, moderate, robust]
        confidence:
          type: number
          minimum: 0.0
          maximum: 1.0
        risk_score:
          type: number
          minimum: 0.0
          maximum: 1.0
          description: "Higher = more risky"
        impact_score:
          type: number
          minimum: 0.0
          maximum: 1.0
          description: "Higher = more impactful fix"
        debate_score:
          type: number
          minimum: 0.0
          maximum: 1.0
          description: "Score from adversarial debate rubric"
        side_effects:
          type: array
          items:
            type: string
  selection_metadata:
    type: object
    required: [total_proposals, debate_depth, convergence_achieved]
    properties:
      total_proposals:
        type: integer
      debate_depth:
        type: string
        enum: [quick, standard, deep]
      convergence_achieved:
        type: number
        minimum: 0.0
        maximum: 1.0
```

---

### Expert 9: Reliability Engineer

**Assessment**: The error handling matrix (Section 14) covers the major failure modes. The circuit breaker integration is appropriate.

**Gaps identified:**
- No idempotency guarantee for Phase 4 implementation. If the pipeline is interrupted during Phase 4 and resumed, `replace_symbol_body` may apply changes on top of partially-applied changes, producing corruption.
- The Phase 1 partial restart (re-run only missing domains) assumes that completed domain findings are still valid. If the codebase changed between sessions (e.g., another developer committed), the findings may be stale.
- No health check or pre-flight validation before pipeline start (e.g., can we reach MCP servers, is the output directory writable, are tools available).

**Resolutions incorporated:**
- Added to Phase 4 restart semantics (Section 12.4): On resume, Phase 4 SHALL check `changes-manifest.json` for partially-applied changes. If the manifest exists but is incomplete, implementation restarts from scratch on a clean worktree (stashing or reverting partial changes). The implementation agent SHALL validate pre-conditions before applying each change.
- Added FR-053: On resume, the system SHALL compare the current `git rev-parse HEAD` (or file modification timestamps if not a git repo) against the value recorded at pipeline start. If the codebase has changed, a warning SHALL be emitted. The user may proceed (accepting stale findings) or abort.
- Added FR-054: Before Phase 0, the system SHALL perform a pre-flight check: (1) output directory is writable, (2) target paths exist and contain files, (3) required tools (Read, Grep, Glob, Bash, Write, Task) are available. MCP server availability is checked lazily at first use, not pre-flight (to avoid unnecessary startup costs).

---

### Expert 10: Product/UX Specialist

**Assessment**: The command interface is clean and the flag set is well-scoped. The examples in Section 5.4 cover common use cases.

**Gaps identified:**
- No progress reporting mechanism during execution. The pipeline may run for 30+ minutes with no user feedback. Users need to know which phase is active and approximate progress.
- The `--dry-run` flag stops at Phase 3b but the user gets no indication of what WOULD have been implemented. The dry-run output should include the implementation plan.
- No `--verbose` or `--quiet` flag for controlling output verbosity during execution.

**Resolutions incorporated:**
- Added FR-055: The system SHALL emit phase transition messages to stdout at the start and completion of each phase, including: phase number, phase name, agent count, and elapsed time. Format: `[forensic] Phase {N}: {name} -- {status} ({elapsed})`.
- Added to FR-044: When `--dry-run` is specified, the Phase 3b output (`fix-selection.md`) SHALL include the full implementation plan (which fixes would be applied, which agents would be assigned, which files would change) as a "dry-run implementation plan" section. The final report SHALL be generated (Phase 6) covering Phases 0-3b only.
- Verbosity control deferred to a future enhancement. The checkpoint artifacts provide detailed information for users who need to inspect intermediate state.

---

### 17.1 Summary of Panel-Driven Additions

| ID | Addition | Source Expert |
|----|----------|--------------|
| FR-047 | Forced domain creation for unmatched `--focus` hints | Requirements Engineer |
| FR-048 | Abort on zero source files with clear error | Requirements Engineer |
| FR-049 | Secret redaction in final report evidence excerpts | Security Engineer |
| FR-050 | Baseline test run before Phase 4 implementation | QA/Testing Specialist |
| FR-051 | Auto-add `.forensic-qa/` to `.gitignore` | DevOps Engineer |
| FR-052 | `--clean` flag for artifact cleanup | DevOps Engineer |
| FR-053 | Stale codebase detection on resume | Reliability Engineer |
| FR-054 | Pre-flight validation checks | Reliability Engineer |
| FR-055 | Phase transition progress reporting | Product/UX Specialist |
| NFR-009 | Wall-clock budget consideration | Performance Engineer |
| NFR-010 | Per-server MCP concurrency limit (3 per server) | Performance Engineer |
| Schema 9.9 | Fix Selection Schema | Data Engineer |

---

## Appendix A: Complete Flag Reference (Including Panel Additions)

| Flag | Short | Default | Type | Description |
|------|-------|---------|------|-------------|
| `[target-paths]` | -- | `.` | string[] | Paths to investigate |
| `--mode` | `-m` | `auto` | enum | `debug\|qa\|regression\|auto` |
| `--depth` | `-d` | `standard` | enum | `quick\|standard\|deep` |
| `--concurrency` | `-n` | `10` | integer (1-15) | Max parallel agents |
| `--focus` | `-f` | (none) | string | Comma-separated domain hints |
| `--confidence-threshold` | `-t` | `0.7` | float (0.0-1.0) | Minimum hypothesis confidence |
| `--fix-tier` | -- | `moderate` | enum | `minimal\|moderate\|robust` |
| `--resume` | `-r` | (none) | path | Resume from checkpoint |
| `--dry-run` | -- | `false` | boolean | Stop after Phase 3b |
| `--output` | `-o` | `.forensic-qa/` | path | Output directory |
| `--clean` | -- | `false` | boolean | Remove artifacts after final report |

---

## Appendix B: Token Budget by Phase (Orchestrator Only)

| Phase | Orchestrator Action | Budget |
|-------|-------------------|--------|
| 0 | Read 3 JSON summaries, generate domains | 500 tokens |
| 1 | Collect finding file paths | 1,000 tokens |
| 2 | Read base-selection summary, filter hypotheses | 500 tokens |
| 3 | (no orchestrator action -- agents run independently) | 0 tokens |
| 3b | Read fix-selection, build implementation plan, greenlight | 800 tokens |
| 4 | (no orchestrator action -- specialists execute) | 0 tokens |
| 5 | (no orchestrator action -- validators execute) | 0 tokens |
| 6 | Synthesize final report from summary artifacts | 2,000 tokens |
| **Total** | | **~4,800 tokens** (well within 8K budget) |

---

*End of specification.*
