---
name: adversarial
description: "Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts"
category: analysis
complexity: advanced
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
mcp-servers: [sequential, context7, serena]
personas: [architect, analyzer, scribe]
---

# /sc:adversarial - Adversarial Debate & Merge Pipeline

## Required Input
- Mode A: `--compare file1,file2[,...,fileN]` (2-10 existing files)
- Mode B: `--source <file> --generate <type> --agents <spec>[,...]` (generate + compare)
- Pipeline: `--pipeline "<shorthand>"` or `--pipeline @pipeline.yaml` (multi-phase DAG)

## Usage

```bash
# Mode A: Compare existing files
/sc:adversarial --compare file1.md,file2.md[,...,fileN.md] [options]

# Mode B: Generate variants from source + compare
/sc:adversarial --source source.md --generate <type> --agents <agent-spec>[,...] [options]

# Pipeline Mode: Multi-phase DAG execution (inline shorthand)
/sc:adversarial --pipeline "generate:opus:architect,haiku:architect -> compare" [options]

# Pipeline Mode: Multi-phase DAG execution (YAML file)
/sc:adversarial --pipeline @pipeline.yaml [options]
```

### Arguments

**Mode A (Compare)**:
- `--compare`: Comma-separated file paths (2-10 existing files)

**Mode B (Generate + Compare)**:
- `--source`: Source file for variant generation
- `--generate`: Type of artifact to generate (roadmap, spec, design, etc.)
- `--agents`: Agent specifications in `model[:persona[:"instruction"]]` format

**Pipeline Mode (Multi-Phase DAG)**:
- `--pipeline`: Inline shorthand or `@path.yaml` file defining a multi-phase pipeline
  - Shorthand syntax: `generate:agents -> compare` with `|` for parallel, `->` for sequential
  - YAML syntax: Array of phase definitions with `type`, `agents`, `depends_on`, `config`
  - Mutually exclusive with `--compare` and `--source`/`--generate`/`--agents`

## Options

| Flag | Short | Required | Default | Description |
|------|-------|----------|---------|-------------|
| `--compare` | `-c` | Mode A | - | Comma-separated file paths (2-10) |
| `--source` | `-s` | Mode B | - | Source file for variant generation |
| `--generate` | `-g` | Mode B | - | Type of artifact to generate |
| `--agents` | `-a` | Mode B | - | Agent specs: `model[:persona[:"instruction"]]` |
| `--pipeline` | | Pipeline | - | Inline shorthand or `@path.yaml` -- mutually exclusive with --compare/--source |
| `--pipeline-parallel` | | No | `3` | Max concurrent phases per DAG level (1-10) |
| `--pipeline-resume` | | No | `false` | Resume from manifest checkpoint, skip completed phases |
| `--pipeline-on-error` | | No | `halt` | Error policy: halt (stop all) or continue (independent branches proceed) |
| `--depth` | `-d` | No | `standard` | Debate depth: quick, standard, deep |
| `--convergence` | | No | `0.80` | Alignment threshold (0.50-0.99) |
| `--interactive` | `-i` | No | `false` | Pause for user input at decision points |
| `--output` | `-o` | No | Auto | Output directory for artifacts |
| `--focus` | `-f` | No | All | Debate focus areas (comma-separated) |
| `--blind` | | No | `false` | Strip model names from artifacts before comparison |
| `--auto-stop-plateau` | | No | `false` | Halt on convergence plateau (<5% delta, 2 consecutive compare phases) |

## Behavioral Summary

5-step adversarial protocol: Step 1 (diff analysis across variants), Step 2 (structured adversarial debate with configurable depth), Step 3 (hybrid quantitative-qualitative scoring and base selection), Step 4 (refactoring plan generation), Step 5 (merge execution with provenance annotations). Produces 6 artifacts: diff-analysis.md, debate-transcript.md, base-selection.md, refactor-plan.md, merge-log.md, and the merged output. Pipeline Mode orchestrates multiple generate/compare phases as a DAG with parallel scheduling, artifact routing between phases, manifest-based resume, and convergence plateau detection.

## Examples

### Compare Two Roadmap Drafts
```bash
/sc:adversarial --compare draft-a.md,draft-b.md --depth standard
```

### Generate 3 Variants with Different Personas
```bash
/sc:adversarial --source auth-spec.md --generate roadmap \
  --agents opus:architect,sonnet:security,opus:analyzer \
  --depth deep --convergence 0.85
```

### Compare 5 Specs with Interactive Mode
```bash
/sc:adversarial --compare spec1.md,spec2.md,spec3.md,spec4.md,spec5.md \
  --interactive --depth deep
```

### Quick Comparison with Focused Debate
```bash
/sc:adversarial --compare plan-a.md,plan-b.md \
  --depth quick --focus structure,completeness
```

### Full Mode B with Custom Output
```bash
/sc:adversarial --source migration-plan.md --generate roadmap \
  --agents opus:architect:"prioritize backward compatibility",sonnet:security:"zero-trust" \
  --depth deep --output .dev/releases/current/migration-v2/
```

### Blind Multi-Model Comparison
```bash
/sc:adversarial --source spec.md --generate roadmap \
  --agents opus:architect,haiku:analyzer --blind --depth deep
```

### Pipeline: Parallel Generate + Compare (Inline Shorthand)
```bash
/sc:adversarial --pipeline "generate:opus:architect,haiku:architect | generate:opus:security,haiku:security -> compare" \
  --source spec.md --depth deep --blind
```

### Pipeline: Multi-Phase from YAML
```bash
/sc:adversarial --pipeline @pipeline-definition.yaml \
  --pipeline-parallel 2 --pipeline-on-error continue --interactive
```

### Pipeline: Resume After Failure
```bash
/sc:adversarial --pipeline @pipeline-definition.yaml --pipeline-resume
```

## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:adversarial-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification is in the protocol skill.

## Boundaries

**Will:**
- Compare 2-10 artifacts through structured adversarial debate
- Generate variant artifacts using different model/persona configurations
- Produce transparent, documented merge decisions with full scoring breakdown
- Execute refactoring plans to produce unified outputs with provenance annotations
- Support configurable depth, convergence thresholds, and focus areas
- Orchestrate multi-phase pipelines with DAG-based dependency resolution
- Resume interrupted pipelines from the last completed phase
- Run blind evaluations stripping model identity from comparisons
- Work as a generic tool invocable by any SuperClaude command

**Will Not:**
- Validate domain-specific correctness of merged output (calling command's responsibility)
- Execute the merged output (planning/merge tool, not execution tool)
- Manage git operations or version control
- Make decisions without documented rationale
- Operate with fewer than 2 variants (minimum for adversarial comparison)
- Override user decisions in interactive mode

## Related Commands

| Command | Integration | Usage |
|---------|-------------|-------|
| `/sc:roadmap` | Multi-spec/multi-roadmap modes | `/sc:roadmap --specs spec1.md,spec2.md` |
| `/sc:design` | Compare architectural designs | `/sc:adversarial --compare design-a.md,design-b.md` |
| `/sc:spec-panel` | Augment panel with adversarial review | Invoke adversarial post-panel |
| `/sc:improve` | Compare improvement approaches | Generate competing plans, merge best |
| `/sc:tasklist` | Pipeline output as sprint input | Generate tasklist from pipeline merged output |
