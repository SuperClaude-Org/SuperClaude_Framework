/sc:workflow Orchestrate deterministic roadmap-to-sprint packaging for {RELEASE}

## Objective
Transform roadmap input into sprint-executable artifacts using a **two-stage deterministic pipeline**:
1) Generate canonical `tasklist.md` only
2) Compile `tasklist.md` into `tasklist-index.md` + canonical phase files

## Inputs
- Generator prompt (source of generation rules):
  `/config/workspace/SuperClaude_Framework/.dev/releases/backlog/v.1.5-Tasklists/Tasklist-Generator-Prompt-v2.1-unified.md`
- Roadmap input:
  `{RELEASEROADMAP}`
- Supplementary spec/context:
  `{RELEASESPEC}`

## Output root
- `{RELEASETASKLISTDESTINATION}`

All generated artifacts must be rooted at `{RELEASETASKLISTDESTINATION}`.

## Stage A — Generate canonical tasklist
Execute generator prompt against the roadmap + supplementary context and produce exactly:
- `{RELEASETASKLISTDESTINATION}/tasklist.md`

### Stage A constraints
- Follow generator non-leakage/truthfulness rules exactly.
- Preserve roadmap deliverables and priority waves.
- Include clarification tasks where required.
- Include tier classification + confidence per task.
- Do not emit phase files or index in this stage.

## Stage B — Deterministic compile to sprint artifacts
Compile `tasklist.md` into sprint runtime artifacts:
- `{RELEASETASKLISTDESTINATION}/tasklist-index.md`
- `{RELEASETASKLISTDESTINATION}/phase-1-tasklist.md`
- `{RELEASETASKLISTDESTINATION}/phase-2-tasklist.md`
- ... sequentially with no gaps

Canonical naming must match sprint discovery rules.

### Stage B compile rules
- Deterministic: same `tasklist.md` => same compiled artifacts.
- Preserve task IDs, phase ordering, dependencies, and traceability links.
- Fail fast on contract violations (missing required fields/sections).

## Stage C — Preflight gate (mandatory)
Run dry-run validation before execution:
```bash
superclaude sprint run {RELEASETASKLISTDESTINATION}/tasklist-index.md --dry-run
```

Gate policy:
- **Errors**: block execution
- **Warnings**: non-blocking by default (log and continue)
- **Strict mode** (if requested): block on warnings too

## Stage D — Execution handoff
If preflight passes policy, execute sprint:
```bash
superclaude sprint run {RELEASETASKLISTDESTINATION}/tasklist-index.md
```

Execution runtime will invoke per-phase task execution via `/sc:task-unified` using strict/systematic execution prompt contracts.

## Command ownership contract
- `/sc:workflow`: orchestration, generation, compilation, gating
- `/sc:task-unified`: task compliance/execution semantics during phase runs

## Deliverables checklist
- [ ] `tasklist.md` generated (canonical)
- [ ] `tasklist-index.md` compiled
- [ ] canonical phase files compiled with sequential numbering
- [ ] dry-run executed and gate result recorded
- [ ] ready-to-run sprint command produced
