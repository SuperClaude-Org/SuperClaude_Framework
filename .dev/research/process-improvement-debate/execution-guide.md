# Process Improvement Debate — Execution Guide

**Generated**: 2026-03-04 15:51
**Output directory**: `/config/workspace/IronHands-CLI/.dev/Research/process-improvement-debate`

## Phase 1: Parallel Brainstorm (3 agents)

Launch these 3 agents IN PARALLEL. Each reads its prompt file and writes its
output to the specified .md file in `/config/workspace/IronHands-CLI/.dev/Research/process-improvement-debate/`.

| Agent | Prompt | Output | Model |
|-------|--------|--------|-------|
| brainstorm-spec-panel | `prompts/01-brainstorm-spec-panel.md` | `brainstorm-spec-panel.md` | opus |
| brainstorm-adversarial | `prompts/02-brainstorm-adversarial.md` | `brainstorm-adversarial.md` | opus |
| brainstorm-roadmap | `prompts/03-brainstorm-roadmap.md` | `brainstorm-roadmap.md` | opus |

### Claude Code Agent Invocation (copy-paste ready)

For each agent, the orchestrating agent should:
1. Read the prompt file
2. Invoke `/sc:brainstorm` with the prompt content
3. Write the brainstorm output to the specified output file

## Phase 2: Adversarial Debate (1 agent, after Phase 1 completes)

| Agent | Prompt | Outputs | Model |
|-------|--------|---------|-------|
| adversarial-debate | `prompts/04-adversarial-debate.md` | `debate-transcript.md`, `scoring-results.md`, `final-recommendations.md`, `cross-cutting-analysis.md` | opus |

### Dependency

Phase 2 MUST wait for all 3 Phase 1 agents to complete and write their output files.

## Expected Final Artifacts

After both phases complete, `/config/workspace/IronHands-CLI/.dev/Research/process-improvement-debate/` should contain:

```
process-improvement-debate/
├── prompts/
│   ├── 01-brainstorm-spec-panel.md      # Input prompt
│   ├── 02-brainstorm-adversarial.md     # Input prompt
│   ├── 03-brainstorm-roadmap.md         # Input prompt
│   └── 04-adversarial-debate.md         # Input prompt
├── manifest.json                         # Machine-readable execution manifest
├── execution-guide.md                    # This file
├── scoring-framework.md                  # Scoring dimensions and formula
├── brainstorm-spec-panel.md             # Phase 1 output
├── brainstorm-adversarial.md            # Phase 1 output
├── brainstorm-roadmap.md                # Phase 1 output
├── debate-transcript.md                 # Phase 2 output
├── scoring-results.md                   # Phase 2 output
├── final-recommendations.md             # Phase 2 output
└── cross-cutting-analysis.md            # Phase 2 output
```

## Scoring Framework Reference

See `scoring-framework.md` for the 4-dimension scoring system:
- Implementation Complexity (20% weight, inverted)
- Cost/Time Overhead (15% weight, inverted)
- Likelihood of Impact (40% weight, direct)
- Generalizability (25% weight, direct)

Composite formula normalizes to 0-100 with S/A/B/C/D tier classification.
