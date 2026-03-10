# Execution Instructions: v3.0-roadmap-gen - Roadmap Generator Command

## Context Loading (READ THESE FIRST)

1. **Source Specification**: `<project-root>/.dev/plans/v3.0_Roadmaps/v3.0_Roadmap-Generator-Specification.md`
2. **This Roadmap**: `<project-root>/.dev/plans/v3.0_Roadmaps/v3.0-roadmap-gen/roadmap.md`
3. **Test Strategy**: `<project-root>/.dev/plans/v3.0_Roadmaps/v3.0-roadmap-gen/test-strategy.md`
4. **Extraction**: `<project-root>/.dev/plans/v3.0_Roadmaps/v3.0-roadmap-gen/extraction.md`
5. **crossLLM Integration Protocol**: `<project-root>/docs/generated/crossLLM-Integration-Protocol.md`

### Codebase Overview
| Directory | Purpose |
|-----------|---------|
| `.opencode/command/` | Command definition files |
| `.opencode/agent/` | Agent prompt files |
| `.opencode/resources/templates/roadmaps/` | Roadmap templates (new) |
| `.dev/tests/` | Test files and fixtures |
| `docs/generated/` | Generated documentation |

---

## Execution Rules

1. **Work through milestones IN ORDER**: M1 → M2 → M3 → M4 → M5 → M6
2. **Within milestones, respect dependency order**: See dependency graph in roadmap.md
3. **Complete ALL deliverables before the milestone checkpoint**
4. **Run verification checkpoint before proceeding to the next milestone**
5. **If verification fails → STOP and create an issue report**

---

## Task Execution Pattern (for each deliverable)

### 1. READ
- Read acceptance criteria from roadmap.md
- Read related sections in specification
- Examine affected files (if they exist)

### 2. PLAN
- List specific file changes needed
- Identify dependencies on other deliverables
- Note any risks or concerns

### 3. IMPLEMENT
- Create/modify files as specified
- Follow existing patterns in codebase
- Avoid unrelated refactors (scope discipline)

### 4. TEST
- Write tests per test-strategy.md
- Run unit tests for the deliverable
- Verify tests pass

### 5. VERIFY
- Check acceptance criteria explicitly
- Compare output to expected schema
- Run any integration tests for milestone

### 6. DOCUMENT
- Update comments if needed
- Note any deviations from plan
- Update roadmap.md deliverable status

### 7. COMMIT (if applicable)
- Logical commit referencing the deliverable ID
- Format: `feat(roadmap-gen): <ID> <description>`

---

## Milestone Execution Details

### Milestone 1: Foundation
**Order**: REQ-001 → REQ-002 → REQ-003 → REQ-004 → REQ-005 → IMP-005

| Step | Deliverable | Action |
|------|-------------|--------|
| 1.1 | REQ-001 | Create `.opencode/command/rf:roadmap-gen.md` with full syntax |
| 1.2 | REQ-002 | Create `.opencode/agent/rf-roadmap-gen-orchestrator.md` skeleton |
| 1.3 | REQ-003 | Implement Phase 0 preflight validation in orchestrator |
| 1.4 | REQ-004 | Implement Phase 1 input extraction in orchestrator |
| 1.5 | REQ-005 | Implement Phase 2 persona selection in orchestrator |
| 1.6 | IMP-005 | Add --output flag handling to command and orchestrator |

**Checkpoint M1**:
- [ ] Command parses all options correctly
- [ ] Orchestrator logs phase entry/exit
- [ ] Phase 0 rejects invalid inputs
- [ ] Phase 1 produces valid extraction.md
- [ ] Phase 2 calculates domain distribution correctly

### Milestone 2: Template System
**Order**: DOC-001, DOC-002, DOC-003 (parallel) → REQ-007 → REQ-006

| Step | Deliverable | Action |
|------|-------------|--------|
| 2.1 | DOC-001 | Create `.opencode/resources/templates/roadmaps/feature-release.md` |
| 2.2 | DOC-002 | Create `.opencode/resources/templates/roadmaps/quality-release.md` |
| 2.3 | DOC-003 | Create `.opencode/resources/templates/roadmaps/documentation-release.md` |
| 2.4 | REQ-007 | Create `.opencode/agent/rf-roadmap-gen-template-scorer.md` |
| 2.5 | REQ-006 | Implement Phase 2.5 template evaluation in orchestrator |

**Checkpoint M2**:
- [ ] All 3 templates exist with correct structure
- [ ] Template scorer produces consistent scores
- [ ] Phase 2.5 selects correct template for domain
- [ ] template-selection.md generated with rationale

### Milestone 3: Core Generation Pipeline
**Order**: REQ-008 → REQ-009 → REQ-010 → REQ-011

| Step | Deliverable | Action |
|------|-------------|--------|
| 3.1 | REQ-008 | Implement Phase 3 roadmap construction |
| 3.2 | REQ-009 | Implement Phase 4 test strategy generation |
| 3.3 | REQ-010 | Implement Phase 5 execution prompt generation |
| 3.4 | REQ-011 | Implement Phase 6 self-validation |

**Checkpoint M3**:
- [ ] roadmap.md follows required schema
- [ ] All extraction items appear in exactly one milestone
- [ ] test-strategy.md covers all deliverables
- [ ] execution-prompt.md has valid paths
- [ ] Phase 6 detects intentionally introduced discrepancies

### Milestone 4: crossLLM Integration
**Order**: REQ-014 → REQ-012 → REQ-013 → REQ-015 → REQ-016 → REQ-020 → REQ-017 → REQ-018

| Step | Deliverable | Action |
|------|-------------|--------|
| 4.1 | REQ-014 | Implement draft preservation logic |
| 4.2 | REQ-012 | Implement Phase 7 crossLLM integration |
| 4.3 | REQ-013 | Enable parallel upgrade execution |
| 4.4 | REQ-015 | Implement circuit breaker logic |
| 4.5 | REQ-016 | Implement upgrade log generation |
| 4.6 | REQ-020 | Implement version folder management |
| 4.7 | REQ-017 | Implement Phase 7.5 consistency validation |
| 4.8 | REQ-018 | Implement consistency report generation |

**Checkpoint M4**:
- [ ] crossLLM invoked with correct chain
- [ ] Parallel execution confirmed
- [ ] .draft.md files created before upgrade
- [ ] Circuit breaker triggers at ≥50% failures
- [ ] upgrade-log.md follows schema
- [ ] v1/, v2/ folders created correctly
- [ ] consistency-report.md generated

### Milestone 5: Enhancements & Polish
**Order**: REQ-019 → IMP-001 → IMP-002 → IMP-003 → IMP-004

| Step | Deliverable | Action |
|------|-------------|--------|
| 5.1 | REQ-019 | Implement multi-iteration upgrade support |
| 5.2 | IMP-001 | Add --chain flag handling |
| 5.3 | IMP-002 | Add --upgrade-threshold flag handling |
| 5.4 | IMP-003 | Add --upgrade-only flag handling |
| 5.5 | IMP-004 | Add --sequential-upgrades flag handling |

**Checkpoint M5**:
- [ ] --version 3 creates v1/v2/v3 with chain cycling
- [ ] --chain overrides iteration 1 only
- [ ] --upgrade-threshold applies to result filtering
- [ ] --upgrade-only limits upgraded artifacts
- [ ] --sequential-upgrades forces sequential execution

### Milestone 6: Documentation & Testing
**Order**: DOC-004, DOC-005 (parallel) → REF-001

| Step | Deliverable | Action |
|------|-------------|--------|
| 6.1 | DOC-004 | Create `docs/generated/Commands/roadmap-gen_UserDoc.md` |
| 6.2 | DOC-005 | Create `docs/generated/Commands/roadmap-gen_TD.md` |
| 6.3 | REF-001 | Verify/update `docs/generated/crossLLM-Integration-Protocol.md` |

**Checkpoint M6**:
- [ ] User docs cover all syntax, options, examples
- [ ] Technical docs cover architecture, agents, protocol
- [ ] Integration Protocol is standalone and reusable
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All acceptance criteria verified

---

## Verification Checkpoints

After each milestone:
- [ ] All deliverables complete (check IDs against extraction.md)
- [ ] All unit tests passing
- [ ] All integration tests for milestone passing
- [ ] No linting/type errors (if applicable)
- [ ] Documentation current

---

## Stop Conditions

**HALT execution and report if:**
1. Any test fails after a reasonable fix attempt (3 tries max)
2. Unexpected dependency discovered (not in extraction.md)
3. Security concern identified (credentials, unsafe operations)
4. Scope creep detected (work not in roadmap)
5. crossLLM integration fundamentally broken (API change)

---

## Rollback Procedure

If critical issue encountered:
1. **Document issue** in `.dev/plans/v3.0_Roadmaps/v3.0-roadmap-gen/issues/`
2. **Identify last known-good state** (git commit if available)
3. **Report to human** with:
   - Issue description
   - Steps to reproduce
   - Impact assessment
   - Recommended resolution

---

## Progress Tracking

Use TodoWrite to track progress:
```
{"content": "M1: REQ-001 Command definition", "status": "pending"}
{"content": "M1: REQ-002 Orchestrator skeleton", "status": "pending"}
...
```

Update status to `in_progress` when starting, `completed` when verified.

---

## File Creation Sequence

| Order | File | Purpose |
|-------|------|---------|
| 1 | `.opencode/command/rf:roadmap-gen.md` | Command definition |
| 2 | `.opencode/agent/rf-roadmap-gen-orchestrator.md` | Main orchestrator |
| 3 | `.opencode/resources/templates/roadmaps/feature-release.md` | Template |
| 4 | `.opencode/resources/templates/roadmaps/quality-release.md` | Template |
| 5 | `.opencode/resources/templates/roadmaps/documentation-release.md` | Template |
| 6 | `.opencode/agent/rf-roadmap-gen-template-scorer.md` | Template scorer |
| 7 | `docs/generated/Commands/roadmap-gen_UserDoc.md` | User docs |
| 8 | `docs/generated/Commands/roadmap-gen_TD.md` | Tech docs |

---

## Success Validation

At completion, verify:
1. `/rf:roadmap-gen ./test-spec.md` produces all 4 artifacts
2. `/rf:roadmap-gen ./test-spec.md --version 1` skips upgrade
3. `/rf:roadmap-gen ./test-spec.md --version 3` creates v1/v2/v3
4. All acceptance criteria in specification met
5. All tests in test-strategy.md passing

---

*Generated by Roadmap-Generator v2.0*
