# Phase File Template (`phase-N-tasklist.md`)

Read-only reference extracted from SKILL.md Section 6B. This file exists for human review; the skill uses its own inline copy.

---

Each phase file is a **self-contained execution unit**. It contains only the tasks for that phase plus inline checkpoints. It does NOT contain registries, traceability matrices, templates, or completion protocol instructions.

## Phase Heading and Goal

```
# Phase N -- <Phase Name>
```

- Level-1 heading (`#`) with em-dash separator
- Phase name portion must not exceed 50 characters
- Required for Sprint CLI TUI display name extraction
- Include a one-paragraph phase goal (2-3 sentences max, derived from roadmap)

## Task Format

```
### T<PP>.<TT> -- <Task Title>
```

| Field | Value |
|---|---|
| Roadmap Item IDs | `R-###` (comma-separated; must include at least 1) |
| Why | <1-2 sentences derived from roadmap> |
| Effort | `<XS|S|M|L|XL>` |
| Risk | `<Low|Medium|High>` |
| Risk Drivers | `<matched categories/keywords only>` |
| Tier | `<STRICT|STANDARD|LIGHT|EXEMPT>` |
| Confidence | `[████████--] XX%` |
| Requires Confirmation | `Yes | No` (Yes if confidence < 0.70) |
| Critical Path Override | `Yes | No` |
| Verification Method | `<method per tier>` |
| MCP Requirements | `<Required: X, Y | Preferred: Z | None>` |
| Fallback Allowed | `Yes | No` |
| Sub-Agent Delegation | `Required | Recommended | None` |
| Deliverable IDs | `D-####` (comma-separated; must include at least 1) |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-####/spec.md`
- `TASKLIST_ROOT/artifacts/D-####/notes.md`
- `TASKLIST_ROOT/artifacts/D-####/evidence.md`

**Deliverables:**
- 1-5 concrete outputs

**Steps:**
1. **[PLANNING]** Load context and identify scope
2. **[PLANNING]** Check dependencies and blockers
3. **[EXECUTION]** ...
4. **[EXECUTION]** ...
5. **[VERIFICATION]** Validation step aligned to tier
6. **[COMPLETION]** Documentation and evidence

**Acceptance Criteria:** (exactly 4 bullets)
- Functional completion (MUST name specific, verifiable output)
- Quality/safety criterion
- Determinism/repeatability criterion
- Documentation/traceability criterion

**Validation:** (exactly 2 bullets)
- Manual check: ...
- Evidence: linkable artifact produced

**Dependencies:** `<Task IDs or "None">`
**Rollback:** `TBD` or as stated in roadmap
**Notes:** <optional; max 2 lines>

### Near-Field Completion Criterion

The first Acceptance Criteria bullet MUST name a specific, objectively verifiable output.

**Accepted forms:**
- A named file or artifact at a specific path
- A test command outcome with specific test suite
- An observable state with measurable criteria

**Rejected forms (fail self-check):**
- "Implementation is complete."
- "The feature works correctly."
- "Tests pass." (without specifying which tests)
- "Documented." (without specifying what document)

### Acceptance Criteria Specificity Rules
- STRICT tasks: ALL criteria must be artifact-referencing
- STANDARD tasks: >=1 criterion must be artifact-referencing
- LIGHT and EXEMPT tasks: no minimum

## Inline Checkpoints

```
### Checkpoint: Phase <P> / Tasks <start>-<end>
```

**Purpose:** ...
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/<deterministic-name>.md`
**Verification:** (exactly 3 bullets)
**Exit Criteria:** (exactly 3 bullets)

Deterministic name format:
- Range checkpoints: `CP-P<PP>-T<start>-T<end>.md`
- End-of-phase: `CP-P<PP>-END.md`

## End-of-Phase Checkpoint (Mandatory)

Every phase file MUST end with:

```
### Checkpoint: End of Phase <N>
```

This checkpoint serves as the gate for the next phase and must include all standard checkpoint fields.
