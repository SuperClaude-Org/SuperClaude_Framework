# Execution Instructions: v1.3-task-unified-accountability - Accountability Framework

## Context Loading (READ THESE FIRST)
1. **Source specification**: `/config/workspace/SuperClaude/.roadmaps/v1.3-task-unified-accountability/SPEC-REVISED.md`
2. **This roadmap**: `/config/workspace/SuperClaude/.roadmaps/v1.3-task-unified-accountability/roadmap.md`
3. **Test strategy**: `/config/workspace/SuperClaude/.roadmaps/v1.3-task-unified-accountability/test-strategy.md`
4. **Codebase overview**:
   - `src/superclaude/` - Python package source
   - `skills/sc-task-unified/` - Skill definition files
   - `tests/` - Test suite
   - `config/` - Configuration files
   - `docs/` - Documentation

## Execution Rules
1. Work through milestones IN ORDER (M1 → M2 → M3 → M4 → M5 → M6)
2. Within milestones, respect dependency order (see dependency graph in roadmap.md)
3. Complete ALL deliverables before the milestone checkpoint
4. Run verification checkpoint before proceeding to the next milestone
5. If verification fails → STOP and create an issue report in `.roadmaps/v1.3-task-unified-accountability/issues/`

## Task Execution Pattern (for each deliverable)

### 1. READ
- Review acceptance criteria in roadmap.md
- Review related test specifications in test-strategy.md
- Review affected files (if they exist)
- Check SPEC-REVISED.md for detailed requirements

### 2. PLAN
- List specific file changes needed
- Identify dependencies on other deliverables
- Estimate token budget for implementation
- Note any clarifications needed

### 3. IMPLEMENT
- Make changes clearly (avoid unrelated refactors)
- Follow existing code patterns in `src/superclaude/`
- Use Python type hints consistently
- Keep functions focused and testable

### 4. TEST
- Write tests per test-strategy.md before or alongside implementation
- Run tests: `uv run pytest tests/accountability/ -v`
- Verify coverage: `uv run pytest tests/accountability/ --cov=superclaude.accountability`
- All tests must pass before proceeding

### 5. VERIFY
- Check acceptance criteria explicitly against implementation
- Use the GIVEN/WHEN/THEN format from SPEC-REVISED.md
- Document verification results

### 6. DOCUMENT
- Update docs if behavior/API changed
- Add docstrings to new functions/classes
- Update SKILL.md if user-facing behavior changes

### 7. COMMIT (if applicable)
- Create logical commit referencing the deliverable ID
- Format: `feat(accountability): REQ-001 worklog initialization`
- Include test files in same commit as implementation

---

## Milestone Execution Guide

### Milestone 1: Foundation Infrastructure
**Execute in order:**
1. REQ-010 (Session ID) - No dependencies
2. REQ-008 (Tier Policy) - No dependencies
3. REQ-009 (Config Schema) - No dependencies
4. REQ-011 (Memory Naming) - Depends on REQ-010
5. REQ-015 (Serena Fallback) - No dependencies

**Files to create:**
```
src/superclaude/accountability/
├── __init__.py
├── session.py      # REQ-010
├── config.py       # REQ-008, REQ-009
├── memory.py       # REQ-011
└── fallback.py     # REQ-015

config/
└── accountability.yaml  # REQ-008, REQ-009

tests/accountability/
├── __init__.py
├── test_session.py
├── test_config.py
├── test_memory.py
└── test_fallback.py
```

**Checkpoint M1:**
- [ ] `uv run pytest tests/accountability/test_session.py -v` passes
- [ ] `uv run pytest tests/accountability/test_config.py -v` passes
- [ ] `uv run pytest tests/accountability/test_memory.py -v` passes
- [ ] `uv run pytest tests/accountability/test_fallback.py -v` passes
- [ ] Session ID uniqueness verified
- [ ] Config loads and validates
- [ ] Fallback mode triggers on mock timeout

---

### Milestone 2: Core Worklog System
**Execute in order:**
1. REF-001 (Interfaces) - Define interfaces first
2. REQ-001 (Worklog Init) - Depends on M1
3. REQ-012 (Entry Details) - Parallel with REQ-002
4. REQ-002 (Operation Logging) - Depends on REQ-001
5. REQ-003 (Batched Writes) - Depends on REQ-001
6. REQ-007 (Finalization) - Depends on REQ-001, REQ-002, REQ-003

**Files to create/modify:**
```
src/superclaude/accountability/
├── interfaces.py   # REF-001
├── schema.py       # REQ-012
├── worklog.py      # REQ-001, REQ-002, REQ-007
└── buffer.py       # REQ-003

tests/accountability/
├── test_interfaces.py
├── test_schema.py
├── test_worklog.py
└── test_buffer.py
```

**Checkpoint M2:**
- [ ] `uv run pytest tests/accountability/ -v` all pass
- [ ] Integration test: STANDARD task creates complete worklog
- [ ] Batch buffer test: 30 operations = 3 MCP calls
- [ ] Coverage ≥95% for new code

---

### Milestone 3: Verification System
**Execute in order:**
1. REQ-004 (Verification Loop) - Depends on M2
2. REQ-013 (State Machine) - Extends REQ-004
3. REQ-005 (Circuit Breaker) - Depends on REQ-004
4. REQ-014 (User Escalation) - Depends on REQ-005
5. IMP-002 (Latency Budget) - Parallel

**Files to create/modify:**
```
src/superclaude/accountability/
├── verification.py      # REQ-004, REQ-013
├── circuit_breaker.py   # REQ-005
├── escalation.py        # REQ-014
└── timeout.py           # IMP-002

tests/accountability/
├── test_verification.py     # 100% coverage required
├── test_circuit_breaker.py  # 100% coverage required
├── test_escalation.py
└── test_timeout.py
```

**Checkpoint M3:**
- [ ] `uv run pytest tests/accountability/test_verification.py -v --cov --cov-fail-under=100` passes
- [ ] `uv run pytest tests/accountability/test_circuit_breaker.py -v --cov --cov-fail-under=100` passes
- [ ] Integration test: Verification pass on first attempt
- [ ] Integration test: Circuit breaker trips after 3 failures
- [ ] User escalation options functional

---

### Milestone 4: Checkpoint & Optimization
**Execute in order:**
1. REQ-006 (Checkpoints) - Depends on M2
2. IMP-001 (Token Efficiency) - Depends on M2
3. IMP-003 (Memory Retention) - Depends on REQ-007
4. IMP-004 (Adaptive Timeout) - Depends on IMP-002

**Files to create/modify:**
```
src/superclaude/accountability/
├── checkpoints.py   # REQ-006
├── metrics.py       # IMP-001
├── retention.py     # IMP-003
└── timeout.py       # IMP-004 (extend)

tests/accountability/
├── test_checkpoints.py
├── test_metrics.py
├── test_retention.py
└── test_performance.py
```

**Checkpoint M4:**
- [ ] STRICT task generates exactly 3 checkpoints
- [ ] STANDARD task generates exactly 1 checkpoint
- [ ] Token overhead ≤750 for STRICT with batching
- [ ] Memory cleanup runs correctly
- [ ] Adaptive timeout skips optional operations

---

### Milestone 5: Testing & Quality
**Execute in order:**
1. BUG-001 (Schema tests) - 100% coverage
2. BUG-002 (Verification tests) - 100% coverage
3. BUG-003 (Circuit breaker tests) - 100% coverage
4. BUG-004 (E2E integration tests)
5. BUG-005 (Performance tests)

**Files to create:**
```
tests/accountability/
├── test_worklog_schema.py   # BUG-001
├── test_e2e.py              # BUG-004
└── test_performance.py      # BUG-005 (extend)

tests/fixtures/accountability/
├── sample_worklog.json
├── sample_config.yaml
├── mock_todo_states.py
└── mock_serena_responses.py
```

**Checkpoint M5:**
- [ ] `uv run pytest tests/accountability/ --cov --cov-fail-under=95` passes
- [ ] All E2E scenarios pass (STRICT, STANDARD, failure, flags)
- [ ] Performance tests validate token overhead ≤300 weighted average
- [ ] No regressions in existing tests

---

### Milestone 6: Documentation & Release
**Execute in order:**
1. DOC-001 (SKILL.md Section 6)
2. DOC-002 (Flag Reference)
3. DOC-003 (Migration Guide)
4. DOC-004 (Config Documentation)

**Files to modify/create:**
```
skills/sc-task-unified/
└── SKILL.md              # DOC-001, DOC-002

docs/
├── migration/
│   └── v1.3-accountability.md    # DOC-003
└── reference/
    └── accountability-config.md  # DOC-004
```

**Checkpoint M6:**
- [ ] SKILL.md Section 6 exists and is complete
- [ ] All 5 new flags documented with examples
- [ ] Migration guide reviewed and accurate
- [ ] Config documentation complete
- [ ] CHANGELOG.md updated

---

## Verification Checkpoints (Summary)

After each milestone:
- [ ] All deliverables code-complete (check IDs against roadmap.md)
- [ ] All tests passing (`uv run pytest tests/accountability/ -v`)
- [ ] Coverage targets met (`uv run pytest --cov=superclaude.accountability`)
- [ ] No linting errors (`uv run ruff check src/superclaude/accountability/`)
- [ ] No type errors (`uv run mypy src/superclaude/accountability/`)
- [ ] Documentation updated if APIs changed

## Stop Conditions

HALT execution and report if:
- Any test fails after a reasonable fix attempt (2 tries)
- Unexpected dependency discovered not in roadmap
- Security concern identified (e.g., unvalidated input to memory writes)
- Scope creep detected (work not in roadmap.md)
- Token overhead exceeds bounds significantly (>50% over budget)
- Performance regression detected (latency >2x baseline)

## Rollback Procedure

If critical issue:
1. Document issue in `.roadmaps/v1.3-task-unified-accountability/issues/ISSUE-NNN.md`
2. Identify last known-good state: `git log --oneline -10`
3. Report to human with:
   - Issue description
   - Affected deliverables
   - Proposed resolution
   - Estimated impact

## Issue Report Template

```markdown
# Issue Report: ISSUE-NNN

## Summary
[Brief description]

## Affected Deliverables
- REQ-XXX: [status]

## Root Cause
[Analysis]

## Proposed Resolution
[Options]

## Impact Assessment
- Scope: [M1-M6]
- Severity: [Low|Medium|High|Critical]
- Blocking: [Yes|No]

## Evidence
[Logs, screenshots, test output]
```

---

## Quick Reference

### Commands
```bash
# Run all accountability tests
uv run pytest tests/accountability/ -v

# Run with coverage
uv run pytest tests/accountability/ --cov=superclaude.accountability --cov-report=html

# Run specific milestone tests
uv run pytest tests/accountability/ -m "m1" -v

# Run performance tests
uv run pytest tests/accountability/ -m "performance" --benchmark-json=benchmark.json

# Lint
uv run ruff check src/superclaude/accountability/

# Type check
uv run mypy src/superclaude/accountability/
```

### Key Files
| Purpose | Location |
|---------|----------|
| Specification | `.roadmaps/v1.3-task-unified-accountability/SPEC-REVISED.md` |
| Roadmap | `.roadmaps/v1.3-task-unified-accountability/roadmap.md` |
| Test Strategy | `.roadmaps/v1.3-task-unified-accountability/test-strategy.md` |
| Source Code | `src/superclaude/accountability/` |
| Tests | `tests/accountability/` |
| Skill Definition | `skills/sc-task-unified/SKILL.md` |
| Config | `config/accountability.yaml` |

### Success Metrics
| Metric | Target |
|--------|--------|
| Worklog capture rate | ≥95% |
| Verification success rate | ≥98% |
| Course corrections from checkpoints | ≥10% |
| Token overhead (weighted avg) | ≤300 tokens |
| Test coverage | ≥95% (100% for critical) |
