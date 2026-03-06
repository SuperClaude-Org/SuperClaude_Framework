# D-0027: Error Policies Specification

## Overview

Pipeline error handling: halt-on-failure (default) marks dependents as skipped; `--pipeline-on-error continue` leaves parallel branches running. Minimum variant constraint (>=2) for compare phases.

## Policies

### halt-on-failure (default)
- Mark failed phase as failed
- Mark all dependent phases as skipped
- Cancel sibling phases in same level
- Halt pipeline

### continue-on-failure (--pipeline-on-error continue)
- Mark failed phase as failed
- Mark dependent phases as skipped
- Allow independent branches to continue
- Report partial completion

## Minimum Variant Constraint

Compare phases require >=2 variant inputs. Checked before execution. Failure triggers active error policy.

## Implementation Location

`src/superclaude/skills/sc-adversarial-protocol/SKILL.md` — Meta-Orchestrator section, Error Policies subsection.

## Deliverable Status

- **Task**: T03.11
- **Roadmap Item**: R-027
- **Status**: COMPLETE
- **Tier**: STANDARD
