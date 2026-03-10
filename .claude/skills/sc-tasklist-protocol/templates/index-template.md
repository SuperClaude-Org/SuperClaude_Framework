# Index File Template (`tasklist-index.md`)

Read-only reference extracted from SKILL.md Section 6A. This file exists for human review; the skill uses its own inline copy.

---

The index file contains all cross-phase metadata, registries, traceability, and templates.

## Structure

### Title
`# TASKLIST INDEX -- <Roadmap Name or Short Description>`

If the roadmap has no name, use: `# TASKLIST INDEX -- Roadmap Execution Plan`

### Metadata & Artifact Paths
`## Metadata & Artifact Paths`

| Field | Value |
|---|---|
| Sprint Name | `<Roadmap Name or Short Description>` |
| Generator Version | `Roadmap->Tasklist Generator v4.0` |
| Generated | `<ISO-8601 date>` |
| TASKLIST_ROOT | `<computed per Section 3.1>` |
| Total Phases | `<N>` |
| Total Tasks | `<count>` |
| Total Deliverables | `<count>` |
| Complexity Class | `LOW|MEDIUM|HIGH` |
| Primary Persona | `<derived from roadmap domain>` |
| Consulting Personas | `<comma-separated>` |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | `TASKLIST_ROOT/tasklist-index.md` |
| Phase 1 Tasklist | `TASKLIST_ROOT/phase-1-tasklist.md` |
| Phase 2 Tasklist | `TASKLIST_ROOT/phase-2-tasklist.md` |
| ... | ... |
| Execution Log | `TASKLIST_ROOT/execution-log.md` |
| Checkpoint Reports | `TASKLIST_ROOT/checkpoints/` |
| Evidence Directory | `TASKLIST_ROOT/evidence/` |
| Artifacts Directory | `TASKLIST_ROOT/artifacts/` |
| Validation Reports | `TASKLIST_ROOT/validation/` |
| Feedback Log | `TASKLIST_ROOT/feedback-log.md` |

### Phase Files Table
`## Phase Files`

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Foundation | T01.01-T01.04 | STRICT: 1, STANDARD: 2, EXEMPT: 1 |
| 2 | phase-2-tasklist.md | Backend Core | T02.01-T02.05 | STRICT: 2, STANDARD: 3 |
| ... | ... | ... | ... | ... |

Rules:
- The **File** column must contain **literal filenames** -- NOT path-prefixed.
- "Phase Name" is derived from the roadmap bucket heading; if none, use defaults.
- "Task IDs" is a compact range like `T01.01-T01.07` (only if continuous), otherwise comma-separated.
- "Tier Distribution" shows count per tier.

### Source Snapshot
`## Source Snapshot`
- 3-6 bullets, strictly derived from roadmap text.

### Deterministic Rules Applied
`## Deterministic Rules Applied`
- 8-12 bullets summarizing rules applied.

### Roadmap Item Registry
`## Roadmap Item Registry`

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|

### Deliverable Registry
`## Deliverable Registry`

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|

### Traceability Matrix
`## Traceability Matrix`

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|

### Execution Log Template
`## Execution Log Template`

**Intended Path:** `TASKLIST_ROOT/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run | Result | Evidence Path |
|---|---:|---|---:|---|---|---|---|

### Checkpoint Report Template
`## Checkpoint Report Template`

- `# Checkpoint Report -- <Checkpoint Title>`
- `**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/<deterministic-name>.md`
- `**Scope:** <tasks covered>`
- `## Status` -- `Overall: Pass | Fail | TBD`
- `## Verification Results` (exactly 3 bullets)
- `## Exit Criteria Assessment` (exactly 3 bullets)
- `## Issues & Follow-ups`
- `## Evidence`

### Feedback Collection Template
`## Feedback Collection Template`

**Intended Path:** `TASKLIST_ROOT/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|

### Glossary
`## Glossary`
- Include only if the roadmap explicitly defines terms. Otherwise omit.

### Generation Notes (Optional)
`## Generation Notes`
- Lists any fallback behaviors activated during generation.
