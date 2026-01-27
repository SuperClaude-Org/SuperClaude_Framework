---
name: sc:roadmap
description: Generate comprehensive project roadmaps from specification documents
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---

# /sc:roadmap - Roadmap Generator

<!-- Extended metadata (for documentation, not parsed):
category: planning
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [architect, scribe, analyzer]
-->

## Purpose

Generate deterministic release roadmap packages from specification documents with integrated multi-agent validation. Transforms project requirements, feature descriptions, or PRD files into actionable milestone-based roadmaps.

**Key Differentiator**: Unlike general planning tools, `/sc:roadmap` **requires** a specification file as mandatory input, ensuring roadmaps are grounded in documented requirements rather than ad-hoc descriptions.

## Required Input

**MANDATORY**: A specification file path must be provided. The command will not execute without it.

```
/sc:roadmap <spec-file-path>
```

**Supported Input Formats**:
- Markdown (`.md`) - Primary format
- Text (`.txt`) - Plain text specifications
- YAML (`.yaml`, `.yml`) - Structured requirements
- JSON (`.json`) - API/schema specifications

## Triggers

- Explicit: `/sc:roadmap path/to/spec.md`
- Keywords: "generate roadmap", "create roadmap from spec", "roadmap for"

## Usage

```bash
# Basic usage - specification file required
/sc:roadmap path/to/feature-spec.md

# With specific template
/sc:roadmap specs/auth-system.md --template security

# Custom output location
/sc:roadmap requirements/v2.0-prd.md --output .roadmaps/v2.0-release/

# Deep analysis with strict validation
/sc:roadmap specs/migration-plan.md --depth deep --compliance strict

# Quick preview without file generation
/sc:roadmap specs/quick-fix.md --dry-run

# Override persona selection
/sc:roadmap specs/api-design.md --persona backend
```

## Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--template <type>` | `-t` | Template type: `feature`, `quality`, `docs`, `security`, `performance`, `migration` | Auto-detect |
| `--output <dir>` | `-o` | Output directory for roadmap artifacts | `.roadmaps/<spec-name>/` |
| `--depth <level>` | `-d` | Analysis depth: `quick`, `standard`, `deep` | `standard` |
| `--validate` | `-v` | Enable multi-agent validation (STRICT tier) | `true` |
| `--no-validate` | | Skip validation phase | `false` |
| `--compliance <tier>` | `-c` | Force compliance tier: `strict`, `standard`, `light` | Auto-detect |
| `--persona <name>` | `-p` | Override primary persona | Auto-select |
| `--dry-run` | | Preview without generating files | `false` |

## Behavioral Flow

5-wave orchestration architecture:

### Wave 1: Detection & Analysis
- Parse specification file
- Extract requirements, scope, dependencies
- Score complexity (0.0-1.0)
- Activate personas based on domain distribution

### Wave 2: Planning & Template Selection
- Template discovery: local → user → plugin → inline
- Score template compatibility
- Create task breakdown via TodoWrite
- Establish milestone structure

### Wave 3: Generation
- Generate roadmap.md with milestone hierarchy
- Generate tasklist files per milestone
- Generate test-strategy.md
- Generate execution-prompt.md

### Wave 4: Validation (Multi-Agent)
- Task with quality-engineer prompt: Completeness, consistency
- Task with self-review prompt: 4-question validation protocol
- Score aggregation
- Decision: PASS (≥85%) | REVISE (70-84%) | REJECT (<70%)

### Wave 5: Completion
- think_about_whether_you_are_done()
- Memory persistence via Serena
- Git operations (if requested)
- Final output summary

## MCP Integration

- **Sequential**: Wave analysis and validation reasoning
- **Context7**: Template patterns and best practices
- **Serena**: Session persistence and memory

## Outputs (5 Required Artifacts)

| Artifact | Location | Description |
|----------|----------|-------------|
| `roadmap.md` | `<output>/roadmap.md` | Master roadmap document |
| `extraction.md` | `<output>/extraction.md` | Extracted requirements summary |
| `tasklists/M{N}-*.md` | `<output>/tasklists/` | Per-milestone task files |
| `test-strategy.md` | `<output>/test-strategy.md` | Testing and validation approach |
| `execution-prompt.md` | `<output>/execution-prompt.md` | Implementation instructions |

## Boundaries

### Will Do
- Generate structured roadmaps from specification files
- Apply multi-agent validation for quality assurance
- Create milestone-based task breakdowns
- Integrate with SuperClaude persona and MCP systems
- Persist session state via Serena memory
- Support multiple template types

### Will Not Do
- Execute implementation tasks (use `/sc:task` or `/sc:implement`)
- Make business prioritization decisions
- Generate roadmaps without specification input
- Override compliance tier verification without justification
- Skip validation for STRICT tier operations
- Write outside designated output directories

## Compliance Tier Classification

Default tier: **STANDARD** with automatic escalation to **STRICT** when:
- Complexity score > 0.8
- Security-related requirements detected
- Multi-domain scope (>3 domains)
- User specifies `--compliance strict`

## Related Commands

| Command | Integration | Usage |
|---------|-------------|-------|
| `/sc:task` | Execute roadmap tasks | `/sc:task "Implement M1 tasks"` |
| `/sc:implement` | Build roadmap features | `/sc:implement @roadmap.md M1.1` |
| `/sc:analyze` | Review roadmap quality | `/sc:analyze @roadmap.md --focus quality` |
| `/sc:improve` | Enhance roadmap | `/sc:improve @roadmap.md` |

---

*Skill definition for SuperClaude Framework v4.2.0+*
*Based on SC-ROADMAP-FEATURE-SPEC.md v1.1.0*
