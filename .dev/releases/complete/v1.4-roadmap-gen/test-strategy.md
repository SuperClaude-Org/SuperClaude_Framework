# Test Strategy: /sc:roadmap Command

## Metadata
- **Target**: `/sc:roadmap` SuperClaude Skill
- **Generated**: 2026-01-26
- **Generator**: SuperClaude Roadmap Generator v1.0
- **Specification**: SC-ROADMAP-FEATURE-SPEC.md v1.1.0

---

## Test Environment

### Directory Structure
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
├── integration/
│   ├── test_wave1_pipeline.py
│   ├── test_wave2_pipeline.py
│   ├── test_wave3_pipeline.py
│   ├── test_wave4_validation.py
│   ├── test_wave5_completion.py
│   └── test_full_pipeline.py
├── compliance/
│   ├── test_todowrite_states.py
│   ├── test_task_tool_pattern.py
│   ├── test_path_conventions.py
│   ├── test_mcp_circuit_breakers.py
│   └── test_critical_corrections.py
└── fixtures/
    ├── sample_spec.md          # Complete valid specification
    ├── minimal_spec.md         # Minimum viable specification
    ├── invalid_spec.md         # Missing requirements
    ├── empty_spec.md           # Empty file
    ├── security_spec.md        # Security-focused spec
    └── multi_domain_spec.md    # Multi-domain spec
```

### Test Configuration
- **Test Runner**: pytest with superclaude plugin
- **Coverage Tool**: pytest-cov
- **Minimum Coverage**: 80% for unit, 70% for integration
- **Timeout**: 60s per test (120s for E2E)

---

## Test Categories

### 1. Unit Tests
**Purpose**: Individual function validation
**Coverage Target**: >80%

| Test File | Focus Area | Deliverable Coverage |
|-----------|------------|---------------------|
| test_spec_validation.py | File checks, content validation | D2.1 |
| test_extraction.py | FR/NFR parsing, scope extraction | D2.2 |
| test_domain_analysis.py | Keyword classification, percentages | D2.3 |
| test_complexity_scoring.py | 5-factor formula, normalization | D2.4 |
| test_persona_activation.py | Thresholds, selection logic | D2.5 |
| test_template_discovery.py | Search hierarchy, fallback | D3.1, D3.2 |
| test_milestone_generation.py | Count formula, domain mapping | D3.3 |
| test_artifact_generation.py | All 5 generators | D4.1-D4.5 |

### 2. Integration Tests
**Purpose**: Multi-component workflow validation
**Coverage Target**: >70%

| Test File | Focus Area | Wave Coverage |
|-----------|------------|---------------|
| test_wave1_pipeline.py | Spec → Extraction → Domain → Score | Wave 1 |
| test_wave2_pipeline.py | Template → Selection → TodoWrite | Wave 2 |
| test_wave3_pipeline.py | All artifact generation | Wave 3 |
| test_wave4_validation.py | Multi-agent validation | Wave 4 |
| test_wave5_completion.py | Check → Memory persistence | Wave 5 |
| test_full_pipeline.py | Complete E2E workflow | All Waves |

### 3. Compliance Tests
**Purpose**: SuperClaude convention verification
**Coverage Target**: 100% of critical corrections

| Test File | Focus Area | Critical Correction |
|-----------|------------|---------------------|
| test_todowrite_states.py | 3 states only, no "blocked" | #4 |
| test_task_tool_pattern.py | No subagent_type parameter | #1 |
| test_path_conventions.py | SuperClaude path standards | #2 |
| test_mcp_circuit_breakers.py | Fallback behavior | Per MCP.md |
| test_critical_corrections.py | All 6 corrections | #1-#6 |

### 4. E2E Tests
**Purpose**: Full skill invocation validation
**Coverage Target**: >60%

| Test | Description | Success Criteria |
|------|-------------|------------------|
| test_basic_invocation | `/sc:roadmap sample_spec.md` | All 5 artifacts generated |
| test_with_template | `--template security` | Security template applied |
| test_with_depth | `--depth deep` | Extended analysis |
| test_dry_run | `--dry-run` | No files created |
| test_custom_output | `--output custom/` | Artifacts in custom dir |

---

## Test Matrix

### Deliverable → Test Type Mapping

| ID | Deliverable | Unit | Integration | Compliance | E2E |
|----|-------------|------|-------------|------------|-----|
| D1.1 | SKILL.md creation | - | - | ✅ Path | ✅ |
| D1.2 | Skill directory | - | - | ✅ Path | ✅ |
| D1.3 | Template directory | - | - | ✅ Path | - |
| D1.4 | Template files | - | - | ✅ Path | - |
| D2.1 | Spec validation | ✅ | ✅ Wave1 | - | ✅ |
| D2.2 | Extraction engine | ✅ | ✅ Wave1 | - | ✅ |
| D2.3 | Domain classifier | ✅ | ✅ Wave1 | - | ✅ |
| D2.4 | Complexity scoring | ✅ | ✅ Wave1 | - | ✅ |
| D2.5 | Persona activation | ✅ | ✅ Wave1 | - | ✅ |
| D3.1 | Template discovery | ✅ | ✅ Wave2 | - | ✅ |
| D3.2 | Template scoring | ✅ | ✅ Wave2 | - | - |
| D3.3 | Inline generation | ✅ | ✅ Wave2 | - | ✅ |
| D3.4 | TodoWrite init | ✅ | ✅ Wave2 | ✅ States | ✅ |
| D4.1 | roadmap.md gen | ✅ | ✅ Wave3 | - | ✅ |
| D4.2 | extraction.md gen | ✅ | ✅ Wave3 | - | ✅ |
| D4.3 | tasklists gen | ✅ | ✅ Wave3 | - | ✅ |
| D4.4 | test-strategy gen | ✅ | ✅ Wave3 | - | ✅ |
| D4.5 | execution-prompt gen | ✅ | ✅ Wave3 | - | ✅ |
| D5.1 | Quality validation | - | ✅ Wave4 | ✅ Task | ✅ |
| D5.2 | Self-review | - | ✅ Wave4 | - | ✅ |
| D5.3 | Score aggregation | - | ✅ Wave4 | - | ✅ |
| D5.4 | Completion check | - | ✅ Wave5 | - | ✅ |
| D5.5 | Memory persistence | - | ✅ Wave5 | - | ✅ |

---

## SuperClaude-Specific Validation

### Critical Corrections Verification

| # | Correction | Test Method | Assertion |
|---|------------|-------------|-----------|
| 1 | No subagent_type param | Parse Task calls | `'subagent_type' not in params` |
| 2 | CREATE template dir | Check before generation | `mkdir` command present |
| 3 | Compliance in ORCHESTRATOR.md | Reference check | Correct import path |
| 4 | TodoWrite 3 states | State validation | `states ⊆ {pending, in_progress, completed}` |
| 5 | 7 wave-enabled commands | Count verification | `len(wave_commands) == 7` |
| 6 | /sc:git no tag/diff/log | Subcommand check | Subcommands not referenced |

### TodoWrite State Compliance

```python
def test_todowrite_state_compliance():
    """Verify TodoWrite uses only valid states"""
    VALID_STATES = {'pending', 'in_progress', 'completed'}

    # Parse all TodoWrite calls in skill
    for call in parse_todowrite_calls(skill_content):
        for todo in call.todos:
            assert todo.status in VALID_STATES, \
                f"Invalid state: {todo.status}"
            assert 'blocked' not in todo.status.lower(), \
                "Found 'blocked' state (forbidden)"

def test_blocked_workaround_pattern():
    """Verify blocked items use [BLOCKED: reason] prefix"""
    # For items that are blocked, verify pattern:
    # content: "[BLOCKED: reason] Task description"
    # status: pending (NOT blocked)
    for call in parse_todowrite_calls(skill_content):
        for todo in call.todos:
            if 'BLOCKED' in todo.content:
                assert todo.status == 'pending', \
                    "Blocked items must have 'pending' status"
                assert todo.content.startswith('[BLOCKED:'), \
                    "Invalid blocked pattern"
```

### Task Tool Pattern Compliance

```python
def test_task_no_subagent_type():
    """Verify Task calls embed agent type in prompt"""
    for call in parse_task_calls(skill_content):
        # Verify no subagent_type parameter
        assert 'subagent_type' not in call.parameters, \
            "subagent_type parameter should not be used"

        # Verify agent type in prompt
        prompt = call.parameters.get('prompt', '')
        agent_patterns = [
            'You are a quality-engineer',
            'quality-engineer agent',
            'performing.*validation'
        ]
        assert any(re.search(p, prompt) for p in agent_patterns), \
            "Agent type must be embedded in prompt"
```

### Path Convention Compliance

```python
def test_skill_path_convention():
    """Verify skill at correct SuperClaude path"""
    expected_path = '.claude/skills/sc-roadmap/SKILL.md'
    assert Path(expected_path).exists(), \
        f"Skill must be at {expected_path}"

def test_template_path_convention():
    """Verify templates at correct path"""
    expected_path = 'plugins/superclaude/templates/roadmaps/'
    # Templates may not exist initially
    # Verify skill checks/creates this directory
```

---

## Performance Test Criteria

| Test | Metric | Target | Measurement |
|------|--------|--------|-------------|
| Wave 1 execution | Time | < 30s | pytest-benchmark |
| Full generation (standard) | Time | < 2 min | pytest-benchmark |
| Full generation (deep) | Time | < 5 min | pytest-benchmark |
| Validation phase | Time | < 60s | pytest-benchmark |
| Memory usage | Peak | < 500MB | memory_profiler |

---

## Fixture Specifications

### sample_spec.md (Complete Valid Specification)
```markdown
# Sample Feature Specification

## Overview
A complete sample specification for testing.

## Requirements
### Functional Requirements
- FR-001: User authentication via OAuth2
- FR-002: Session management
- FR-003: Role-based access control

### Non-Functional Requirements
- NFR-001: 99.9% uptime
- NFR-002: <200ms response time

## Scope
### In Scope
- Authentication flow
- Session handling

### Out of Scope
- User management UI

## Dependencies
- OAuth2 provider
- Redis session store

## Success Criteria
- All requirements implemented
- Tests passing
- Documentation complete
```

### minimal_spec.md (Minimum Viable)
```markdown
# Minimal Spec

## Overview
Bare minimum specification.

## Requirements
- FR-001: Basic functionality

## Scope
In scope: Basic feature
```

### invalid_spec.md (Missing Requirements)
```markdown
# Invalid Spec

## Overview
This spec is missing requirements section.

## Notes
Some notes here but no requirements.
```

---

## Test Execution Commands

```bash
# Run all tests
pytest tests/sc-roadmap/ -v

# Run unit tests only
pytest tests/sc-roadmap/unit/ -v

# Run integration tests
pytest tests/sc-roadmap/integration/ -v

# Run compliance tests
pytest tests/sc-roadmap/compliance/ -v

# Run with coverage
pytest tests/sc-roadmap/ -v --cov=.claude/skills/sc-roadmap --cov-report=html

# Run specific test file
pytest tests/sc-roadmap/compliance/test_critical_corrections.py -v

# Run E2E tests
pytest tests/sc-roadmap/integration/test_full_pipeline.py -v
```

---

## Acceptance Criteria Summary

| Category | Criteria | Status |
|----------|----------|--------|
| Unit Coverage | >80% | [ ] |
| Integration Coverage | >70% | [ ] |
| Compliance Tests | 100% passing | [ ] |
| E2E Tests | 100% passing | [ ] |
| Critical Corrections | All 6 verified | [ ] |
| Performance Targets | All met | [ ] |
| TodoWrite Compliance | 3 states only | [ ] |
| Task Tool Compliance | No subagent_type | [ ] |

---

*Test Strategy generated by SuperClaude Roadmap Generator v1.0*
*Specification: SC-ROADMAP-FEATURE-SPEC.md v1.1.0*
