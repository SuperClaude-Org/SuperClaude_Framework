# D-0024: Pipeline Resume Specification

## Overview

`--pipeline-resume` reads the manifest, validates artifact checksums (SHA-256), and re-executes from the first incomplete phase.

## Algorithm

1. Read pipeline-manifest.yaml
2. For each completed phase: validate SHA-256 checksums
3. First invalidated or incomplete phase = resume point
4. Re-execute from resume point onward
5. Also re-execute all downstream phases of invalidated phases

## Error Handling

- Missing manifest: STOP with descriptive error
- Corrupt manifest: STOP with parse error
- Missing checksum file: treat as invalidated

## Implementation Location

`src/superclaude/skills/sc-adversarial-protocol/SKILL.md` — Meta-Orchestrator section, Pipeline Resume subsection.

## Deliverable Status

- **Task**: T03.08
- **Roadmap Item**: R-024
- **Status**: COMPLETE
- **Tier**: STRICT
