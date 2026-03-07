# D-0023: Pipeline Manifest Specification

## Overview

Pipeline manifest (`pipeline-manifest.yaml`) created at pipeline start, updated after each phase with return contract, status, and artifact checksums.

## Schema Summary

- pipeline_id: UUID
- created_at: ISO 8601
- global_config: depth, convergence, parallel, blind, plateau, error_policy
- phases[]: id, type, agents, level, status, started_at, finished_at, return_contract, artifact_checksums

## Phase Status Values

pending | running | completed | failed | skipped

## Lifecycle

1. Creation: generate UUID, list all phases as pending
2. Per-phase update: set status, record return contract, compute SHA-256 checksums
3. Finalization: record overall pipeline status

## Implementation Location

`src/superclaude/skills/sc-adversarial-protocol/SKILL.md` — Meta-Orchestrator section, Pipeline Manifest subsection.

## Deliverable Status

- **Task**: T03.07
- **Roadmap Item**: R-023
- **Status**: COMPLETE
- **Tier**: STRICT
