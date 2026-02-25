# Tasklist: M4 - Wave 3 Implementation (Artifact Generation)

## Metadata
- **Milestone**: M4
- **Dependencies**: M3
- **Estimated Complexity**: High
- **Primary Persona**: Backend
- **Deliverables**: 6

---

## Tasks

### T4.1: Implement roadmap.md Generator
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Generate Metadata section:
   - Source Specification path
   - Generated timestamp
   - Generator version
   - Item counts (requirements, milestones, tasks)
2. Generate Persona Assignment section
3. Generate Executive Summary (2-3 sentences)
4. Generate Milestones Overview table
5. Generate per-milestone sections:
   - Objective
   - Dependencies
   - Risk Level
   - Deliverables table (ID, Type, Description, Criteria, Files)
6. Generate Dependency Graph (ASCII or mermaid)
7. Generate Risk Register table
8. Generate Success Criteria checklist
9. Use ID schema per spec Appendix E:
   - Milestones: `M{1digit}` (M1, M2)
   - Deliverables: `D{milestone}.{seq}` (D1.1, D2.3)

#### Acceptance Criteria
- [ ] All required sections present per spec Section 3.4
- [ ] Milestone structure matches Wave 2 planning
- [ ] IDs are unique and follow schema
- [ ] Dependencies accurately reflected
- [ ] Risk register populated

#### Verification
```bash
# Validate roadmap structure
grep -E "^## |^### " roadmap.md
# Should show all major sections
```

---

### T4.2: Implement extraction.md Generator
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Generate Metadata section (source, timestamp, generator)
2. Generate Executive Summary
3. Generate Extracted Requirements table:
   - ID, Type, Domain, Description, Priority, Dependencies
4. Generate Domain Distribution Analysis table
5. Generate Complexity Analysis section:
   - Factor scoring breakdown
   - Total complexity score
6. Generate Persona Assignment section
7. Generate Dependencies Identified section
8. Generate Risks Identified table
9. Generate Summary Statistics

#### Acceptance Criteria
- [ ] All requirements from spec captured
- [ ] Domain distribution percentages correct
- [ ] Complexity calculation documented
- [ ] Persona assignment explained
- [ ] Statistics accurate

#### Verification
```bash
# Check requirement coverage
grep "FR-" extraction.md | wc -l
# Should match spec requirement count
```

---

### T4.3: Implement Tasklist Generator
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Create tasklists/ directory if not exists
2. For each milestone M{N}:
   - Generate file: `M{N}-{name}.md`
   - Include Metadata (milestone, dependencies, complexity)
   - Generate Tasks section per deliverable
3. For each task:
   - Generate header: `### T{M}.{N}: Task Name`
   - Include: Type, Priority, Files Affected
   - Generate Steps (numbered, specific actions)
   - Generate Acceptance Criteria (checkboxes)
   - Generate Verification (bash commands)
4. Include Milestone Completion Checklist
5. Include Dependencies section
6. Include Notes section

#### Acceptance Criteria
- [ ] One file per milestone
- [ ] Naming convention: `M{N}-{name}.md`
- [ ] All deliverables have tasks
- [ ] Steps are actionable
- [ ] Verification commands work

#### Verification
```bash
# Count tasklist files
ls tasklists/M*.md | wc -l
# Should equal milestone count
```

---

### T4.4: Implement test-strategy.md Generator
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Generate Test Environment section:
   - Test location path
   - Fixtures path
   - Test runner configuration
2. Generate Test Categories:
   - Unit Tests: Individual function validation
   - Integration Tests: Multi-component workflows
   - Compliance Tests: Tier classification accuracy
   - E2E Tests: Full skill invocation
3. Generate Test Matrix:
   - Map each deliverable to test types
4. Generate SuperClaude-Specific Validation checklist:
   - TodoWrite state transitions (3 states only)
   - Task tool prompt embedding (no subagent_type)
   - Wave orchestration triggers
   - Compliance tier classification
   - MCP circuit breakers

#### Acceptance Criteria
- [ ] All test categories defined
- [ ] Test matrix covers all deliverables
- [ ] SuperClaude-specific checks included
- [ ] Test paths follow conventions

#### Verification
```bash
# Check test matrix completeness
grep -c "D[0-9]" test-strategy.md
# Should match deliverable count
```

---

### T4.5: Implement execution-prompt.md Generator
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Generate Overview section
2. Generate Prerequisites checklist
3. Generate Execution Order:
   - List milestones in dependency order
   - Note parallel opportunities
4. Generate Per-Milestone Instructions:
   - Key tasks to complete
   - Critical notes/warnings
   - Verification steps
5. Generate Post-Execution Checklist
6. Generate Troubleshooting section:
   - Common issues and solutions
7. Generate Success Verification section

#### Acceptance Criteria
- [ ] Clear execution order documented
- [ ] Dependencies explained
- [ ] Critical warnings highlighted
- [ ] Troubleshooting guidance included
- [ ] Success verification defined

#### Verification
```bash
# Check execution order
grep -E "^M[0-9]|Milestone" execution-prompt.md
# Should show ordered milestone list
```

---

### T4.6: Implement Wave 3 Parallelization
**Type**: IMPROVEMENT
**Priority**: P2-Medium
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Implement dependency tracking:
   ```
   roadmap.md → tasklists/ → [test-strategy.md, execution-prompt.md]
   ```
2. After tasklists complete, generate test-strategy and execution-prompt concurrently
3. Use parallel Write operations where supported
4. Track completion status for all artifacts

#### Acceptance Criteria
- [ ] Sequential operations respect dependencies
- [ ] Concurrent operations execute together
- [ ] Performance improvement: 30-45% per spec Section 3.7
- [ ] No race conditions in file writes

#### Verification
```bash
# Check timestamps of generated files
ls -la test-strategy.md execution-prompt.md
# Timestamps should be nearly identical (concurrent)
```

---

## Milestone Completion Checklist

- [ ] T4.1: roadmap.md generated
- [ ] T4.2: extraction.md generated
- [ ] T4.3: tasklists/ files generated
- [ ] T4.4: test-strategy.md generated
- [ ] T4.5: execution-prompt.md generated
- [ ] T4.6: Parallelization working

## Dependencies

```
T4.1 (roadmap) ──► T4.3 (tasklists) ──► T4.4 (test-strategy)
                                    └──► T4.5 (execution-prompt)
                                         [concurrent eligible]

T4.2 (extraction) ◄── Wave 1 output (can generate early)
```

## Output Directory Structure

```
.roadmaps/<spec-name>/
├── roadmap.md           (T4.1)
├── extraction.md        (T4.2)
├── test-strategy.md     (T4.4)
├── execution-prompt.md  (T4.5)
└── tasklists/           (T4.3)
    ├── M1-foundation.md
    ├── M2-wave1.md
    ├── M3-wave2.md
    ├── M4-wave3.md
    ├── M5-wave4-5.md
    └── M6-testing.md
```

---

*Tasklist generated by SuperClaude Roadmap Generator v1.0*
