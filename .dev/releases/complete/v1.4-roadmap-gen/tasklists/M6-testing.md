# Tasklist: M6 - Testing & Documentation

## Metadata
- **Milestone**: M6
- **Dependencies**: M5
- **Estimated Complexity**: Low-Medium
- **Primary Persona**: QA, Scribe
- **Deliverables**: 4

---

## Tasks

### T6.1: Implement Unit Tests
**Type**: TEST
**Priority**: P1-High
**Files Affected**:
- `tests/sc-roadmap/unit/` (create directory and tests)

#### Steps
1. Create test directory structure:
   ```
   tests/sc-roadmap/
   ├── unit/
   │   ├── test_spec_validation.py
   │   ├── test_extraction.py
   │   ├── test_domain_analysis.py
   │   ├── test_complexity_scoring.py
   │   ├── test_persona_activation.py
   │   ├── test_template_discovery.py
   │   ├── test_milestone_generation.py
   │   └── test_artifact_generation.py
   └── fixtures/
       ├── sample_spec.md
       ├── minimal_spec.md
       └── invalid_spec.md
   ```
2. Write unit tests for each Wave 1 function:
   - Spec validation (file exists, not empty, has requirements)
   - Requirements extraction (FR, NFR, scope parsing)
   - Domain analysis (keyword classification)
   - Complexity scoring (formula, weights, normalization)
   - Persona activation (thresholds, selection)
3. Write unit tests for Wave 2 functions:
   - Template discovery (search order, fallback)
   - Template scoring (factors, threshold)
   - Inline generation (milestone count formula)
4. Write unit tests for Wave 3 generators:
   - Each artifact generator produces valid output
   - ID schema followed
   - Required sections present
5. Target coverage: >80% per wave

#### Acceptance Criteria
- [ ] Test directory structure created
- [ ] Fixtures available for testing
- [ ] Wave 1 functions tested
- [ ] Wave 2 functions tested
- [ ] Wave 3 generators tested
- [ ] Coverage >80%

#### Verification
```bash
# Run unit tests
pytest tests/sc-roadmap/unit/ -v --cov=.claude/skills/sc-roadmap --cov-report=term-missing
# Coverage should be >80%
```

---

### T6.2: Implement Integration Tests
**Type**: TEST
**Priority**: P1-High
**Files Affected**:
- `tests/sc-roadmap/integration/` (create directory and tests)

#### Steps
1. Create integration test directory:
   ```
   tests/sc-roadmap/integration/
   ├── test_wave1_pipeline.py
   ├── test_wave2_pipeline.py
   ├── test_wave3_pipeline.py
   ├── test_wave4_validation.py
   ├── test_wave5_completion.py
   └── test_full_pipeline.py
   ```
2. Write wave-level integration tests:
   - Wave 1: Spec → Extraction → Domain → Complexity → Persona
   - Wave 2: Template discovery → Selection → Task init
   - Wave 3: All 5 artifacts generated correctly
   - Wave 4: Quality validation → Self-review → Aggregation
   - Wave 5: Completion check → Memory persistence
3. Write full pipeline test:
   - Input: Sample specification
   - Output: All 5 artifacts validated
   - Validation score >= 85%

#### Acceptance Criteria
- [ ] Wave pipelines tested
- [ ] Full pipeline E2E test passing
- [ ] Artifacts validated after generation
- [ ] Score >= 85% for valid specs

#### Verification
```bash
# Run integration tests
pytest tests/sc-roadmap/integration/ -v
# All tests should pass
```

---

### T6.3: Implement Compliance Tests
**Type**: TEST
**Priority**: P1-High
**Files Affected**:
- `tests/sc-roadmap/compliance/` (create directory and tests)

#### Steps
1. Create compliance test directory:
   ```
   tests/sc-roadmap/compliance/
   ├── test_todowrite_states.py
   ├── test_task_tool_pattern.py
   ├── test_path_conventions.py
   ├── test_mcp_circuit_breakers.py
   └── test_critical_corrections.py
   ```
2. Test TodoWrite state management:
   - Only 3 states used (pending, in_progress, completed)
   - No "blocked" state appears anywhere
   - Blocked items use [BLOCKED: reason] prefix
3. Test Task tool pattern:
   - No `subagent_type` parameter used
   - Agent type embedded in prompt
4. Test path conventions:
   - Skills at `.claude/skills/{name}/SKILL.md`
   - Templates at `plugins/superclaude/templates/roadmaps/`
5. Test MCP integration:
   - Circuit breaker thresholds configured
   - Fallback behavior works
6. Test all 6 critical corrections:
   - No subagent_type parameter
   - Template directory created (not assumed)
   - Compliance tiers from ORCHESTRATOR.md
   - TodoWrite 3 states only
   - 7 wave-enabled commands
   - /sc:git subcommands don't exist

#### Acceptance Criteria
- [ ] TodoWrite compliance verified
- [ ] Task tool pattern correct
- [ ] Path conventions followed
- [ ] MCP fallbacks working
- [ ] All 6 critical corrections verified

#### Verification
```bash
# Run compliance tests
pytest tests/sc-roadmap/compliance/ -v
# All tests should pass

# Manual verification
grep -r "blocked" .claude/skills/sc-roadmap/ | grep -v "BLOCKED:"
# Should return empty (no "blocked" state)

grep "subagent_type" .claude/skills/sc-roadmap/
# Should return empty
```

---

### T6.4: Update COMMANDS.md Documentation
**Type**: DOC
**Priority**: P2-Medium
**Files Affected**:
- `COMMANDS.md` (or equivalent commands documentation)

#### Steps
1. Locate COMMANDS.md in repository
2. Add `/sc:roadmap` entry under appropriate section (Planning Commands)
3. Include:
   - Command name and syntax
   - Required input (spec file path)
   - Available flags
   - Brief description
   - Example usage
   - Related commands
4. Verify entry follows existing format

#### Acceptance Criteria
- [ ] /sc:roadmap entry added to COMMANDS.md
- [ ] Format matches existing entries
- [ ] All flags documented
- [ ] Examples provided
- [ ] Cross-references to related commands

#### Verification
```bash
# Check COMMANDS.md for entry
grep "sc:roadmap" COMMANDS.md
# Should find the command entry
```

---

## Milestone Completion Checklist

- [ ] T6.1: Unit tests implemented (>80% coverage)
- [ ] T6.2: Integration tests passing
- [ ] T6.3: Compliance tests verified
- [ ] T6.4: COMMANDS.md updated

## Dependencies

```
M5 Complete ──► T6.1 (unit tests)
            ├──► T6.2 (integration tests)
            ├──► T6.3 (compliance tests)
            └──► T6.4 (documentation)

T6.1, T6.2, T6.3, T6.4 can execute in parallel
```

## Test Coverage Targets

| Test Type | Coverage Target | Focus Areas |
|-----------|----------------|-------------|
| Unit | >80% | Individual functions, edge cases |
| Integration | >70% | Wave pipelines, data flow |
| Compliance | 100% | Critical corrections, conventions |
| E2E | >60% | Full workflow validation |

## SuperClaude-Specific Test Assertions

```python
# TodoWrite state test
def test_todowrite_no_blocked_state():
    """Verify TodoWrite never uses 'blocked' state"""
    valid_states = {'pending', 'in_progress', 'completed'}
    # Assert all states in valid_states

# Task tool test
def test_task_no_subagent_type():
    """Verify Task calls don't use subagent_type parameter"""
    # Parse Task calls
    # Assert 'subagent_type' not in parameters

# Path convention test
def test_skill_path_convention():
    """Verify skill at correct SuperClaude path"""
    expected = '.claude/skills/sc-roadmap/SKILL.md'
    # Assert path exists and follows convention
```

---

*Tasklist generated by SuperClaude Roadmap Generator v1.0*
