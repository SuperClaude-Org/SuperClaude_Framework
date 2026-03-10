# Test Strategy: v1.2-analyze-auggie - /sc:analyze Auggie MCP Integration

## Metadata
- **Source Specification**: `.dev/releases/current/v1.2-analyze-auggie/sc-analyze-auggie-feature-spec.md`
- **Generated**: 2026-01-26
- **Generator**: SuperClaude Roadmap Generator v1.0
- **Test Framework**: pytest with superclaude plugin

---

## Test Environment

### Directory Structure
```
tests/
├── analyze/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures and configuration
│   ├── test_acceptance.py       # AT-1 to AT-8 Gherkin scenarios
│   ├── test_mcp_integration.py  # MCP server integration
│   ├── test_validation.py       # Hybrid validation pipeline
│   ├── test_budgeting.py        # Adaptive token budgeting
│   ├── test_memory.py           # Cross-session memory
│   ├── test_degradation.py      # Fallback and circuit breaker
│   └── test_ab_framework.py     # A/B testing infrastructure
└── fixtures/
    └── analyze/
        ├── sample_codebase_small/   # <10K LOC
        ├── sample_codebase_medium/  # 10-100K LOC
        ├── sample_codebase_large/   # 100K-1M LOC
        └── known_issues/            # Pre-seeded vulnerabilities
```

### Test Configuration
```python
# conftest.py
import pytest

@pytest.fixture
def mock_auggie_mcp():
    """Mock Auggie MCP for isolated testing"""
    ...

@pytest.fixture
def mock_serena_memory():
    """Mock Serena memory for cross-session tests"""
    ...

@pytest.fixture
def sample_codebase(request):
    """Parametrized fixture for different codebase sizes"""
    size = request.param  # small, medium, large
    ...
```

---

## Test Categories

### 1. Unit Tests
**Purpose**: Individual function validation
**Coverage Target**: ≥80%
**Location**: `tests/analyze/test_unit_*.py`

| Component | Test Count | Coverage |
|-----------|------------|----------|
| Query template generation | 12 | Functions for each language |
| Token budget calculation | 8 | All size × aggressiveness combinations |
| Confidence scoring | 6 | All validation stage combinations |
| Degradation message generation | 4 | All MCP failure modes |

### 2. Integration Tests
**Purpose**: Multi-component workflows
**Coverage Target**: ≥70%
**Location**: `tests/analyze/test_integration_*.py`

| Workflow | Test Count | Components |
|----------|------------|------------|
| Full analysis pipeline | 5 | Auggie → Serena → Grep → Output |
| MCP server coordination | 4 | Circuit breaker, fallback chain |
| Memory persistence | 3 | write_memory → read_memory → delta |
| Progressive disclosure | 3 | Summary → Details → Evidence |

### 3. Compliance Tests
**Purpose**: Tier classification accuracy and SuperClaude patterns
**Coverage Target**: 100% of tier combinations
**Location**: `tests/analyze/test_compliance.py`

| Compliance Tier | Test Scenarios |
|-----------------|----------------|
| STRICT | Security paths, auth modules, database changes |
| STANDARD | Feature files, service modules, API endpoints |
| LIGHT | Config changes, minor updates, formatting |
| EXEMPT | Documentation, git operations, exploration |

### 4. End-to-End Tests
**Purpose**: Full skill invocation
**Coverage Target**: All 8 acceptance tests
**Location**: `tests/analyze/test_acceptance.py`

---

## Test Matrix

| Deliverable ID | Unit | Integration | Compliance | E2E |
|----------------|------|-------------|------------|-----|
| M1-D1 (MCP tool name) | ✓ | ✓ | - | ✓ |
| M1-D2 (directory_path) | ✓ | ✓ | - | ✓ |
| M1-D3 (Circuit breaker) | ✓ | ✓ | - | ✓ |
| M2-D1 (Progressive disclosure) | ✓ | ✓ | - | ✓ |
| M2-D2 (Tier classification) | ✓ | - | ✓ | ✓ |
| M2-D3 (Cross-session memory) | ✓ | ✓ | - | ✓ |
| M2-D4 (Degradation feedback) | ✓ | ✓ | - | ✓ |
| M3-D1 (Language templates) | ✓ | ✓ | - | - |
| M3-D2 (Iterative refinement) | ✓ | ✓ | - | ✓ |
| M3-D3 (Aggressiveness flag) | ✓ | ✓ | - | ✓ |
| M4-D1 (Hybrid validation) | ✓ | ✓ | - | ✓ |
| M4-D2 (Adaptive budgeting) | ✓ | ✓ | - | ✓ |
| M5-D1 (Quality scoring) | ✓ | ✓ | - | - |
| M5-D2 (Degradation feedback) | ✓ | ✓ | - | ✓ |

---

## Acceptance Test Specifications

### AT-1: Basic Semantic Discovery
```gherkin
Feature: Basic Semantic Discovery
  Scenario: Analyze authentication module for security issues
    Given a codebase with authentication module at "@auth"
    And Auggie MCP is available
    When /sc:analyze @auth --focus security --depth quick
    Then findings include all auth-related security patterns
    And execution completes within 30 seconds
    And token usage is under 8K
    And Auggie queries include directory_path parameter
```

### AT-2: Graceful Degradation with Feedback
```gherkin
Feature: Graceful Degradation
  Scenario: Continue analysis when MCP unavailable
    Given Auggie MCP is unavailable (circuit breaker open)
    When /sc:analyze @src --focus quality --depth deep
    Then analysis completes using native tools (Glob + Grep)
    And user receives degradation notification "⚠️ Semantic search unavailable"
    And results include degradation impact note
    And quality is marked as "reduced precision"
```

### AT-3: Evidence Chain with Progressive Disclosure
```gherkin
Feature: Progressive Disclosure
  Scenario: Show evidence tiers progressively
    Given security analysis finds SQL injection
    When default output is shown
    Then finding shows summary tier only (location, severity, action required)

    When user requests --verbose
    Then finding shows details tier (context, impact, fix suggestion)

    When user requests --evidence
    Then finding shows evidence tier (code snippet, validation chain, cross-references)
    And confidence score is provided
```

### AT-4: Large Codebase Handling
```gherkin
Feature: Large Codebase Support
  Scenario: Analyze codebase with 500K+ LOC
    Given a codebase with 500K+ LOC
    When /sc:analyze --focus architecture --depth comprehensive
    Then analysis detects "large" size tier
    And token budget is multiplied by 2.0x
    And analysis uses hierarchical narrowing
    And completes within 5 minutes
```

### AT-5: Aggressiveness Control
```gherkin
Feature: Aggressiveness Control
  Scenario: Use aggressive analysis mode
    Given a standard codebase
    When /sc:analyze @src --focus security --depth deep --aggressiveness aggressive
    Then Auggie queries are 1.5x the balanced baseline
    And token budget is 1.3x the balanced baseline
    And hybrid validation is mandatory
```

### AT-6: Tier Classification Integration
```gherkin
Feature: Tier Classification
  Scenario: Auto-detect STRICT tier for security paths
    Given a file path containing "auth" in security-sensitive location
    When /sc:analyze @src/auth --tier auto
    Then tier classification detects STRICT
    And auto-aggressiveness is set to aggressive
    And auto-depth is set to deep minimum
    And hybrid validation is mandatory
```

### AT-7: Iterative Query Refinement
```gherkin
Feature: Iterative Refinement
  Scenario: Refine query when initial results low quality
    Given an initial broad query with quality_score 0.45
    When /sc:analyze --depth comprehensive
    Then refinement strategy is triggered
    And query is narrowed based on initial results
    And second query achieves quality_score >= 0.7
    And refinement trace is logged
```

### AT-8: Cross-Session Memory
```gherkin
Feature: Cross-Session Memory
  Scenario: Show delta from previous analysis
    Given a previous analysis exists in Serena memory
    When /sc:analyze @src is run again
    Then previous findings are loaded from memory
    And delta is calculated (new/resolved/recurring)
    And output shows "🆕 5 new | ✅ 3 resolved | 🔁 7 recurring"
    And trend indicator shows health score change
```

---

## SuperClaude-Specific Validation

### Critical Correction Tests
- [ ] MCP tool name is exactly `mcp__auggie-mcp__codebase-retrieval`
- [ ] All Auggie calls include `directory_path` parameter
- [ ] TodoWrite uses only 3 states: `pending`, `in_progress`, `completed`
- [ ] No "blocked" state in any TodoWrite operation
- [ ] Compliance tier classification from ORCHESTRATOR.md patterns

### MCP Integration Tests
- [ ] Circuit breaker triggers after 3 failures within 30s
- [ ] Fallback to Glob/Grep works when Auggie unavailable
- [ ] Serena memory write_memory/read_memory functions correctly
- [ ] Sequential thinking used for multi-step reasoning

### Wave Orchestration Tests (if applicable)
- [ ] 7 wave-enabled commands recognized
- [ ] Wave triggers correctly at complexity ≥0.7

---

## Quality Gates

```yaml
analysis_quality_gates:
  relevance:
    check: "Findings relate to specified --focus"
    threshold: 95%

  actionability:
    check: "Specific file:line references provided"
    threshold: 100%

  context:
    check: "Semantic context included in findings"
    threshold: 80%

  severity:
    check: "Impact-based severity ratings"
    threshold: "All critical and high findings"

  validation_chain:
    check: "Hybrid validation completed for MEDIUM+ confidence findings"
    threshold: 100%

  progressive_disclosure:
    check: "All 3 tiers properly populated"
    threshold: 100%

  quality_scoring:
    check: "Auggie results scored before processing"
    threshold: 100%
```

---

## Performance Benchmarks

### Latency Targets

| Tier | Target (p95) | Measurement Method |
|------|--------------|-------------------|
| quick | <30 seconds | Wall clock time |
| deep | <90 seconds | Wall clock time |
| comprehensive | <5 minutes | Wall clock time |

### Token Budget Targets

| Tier | Base Budget | Measurement Method |
|------|-------------|-------------------|
| quick | 5-8K | Token counting middleware |
| deep | 15-25K | Token counting middleware |
| comprehensive | 30-50K | Token counting middleware |

### Precision/Recall Targets

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Precision | ~40% | ≥85% | Human review of 100 random findings |
| Recall | ~60% | ≥90% | Comparison against known issue sets |
| False positive rate | ~50% | <10% | User dismissal tracking |

---

## Fault Injection Tests

### MCP Unavailability Scenarios

| Scenario | Injection Method | Expected Behavior |
|----------|------------------|-------------------|
| Auggie timeout | Mock 30s+ response time | Circuit breaker opens, fallback active |
| Auggie error | Mock 500 response | Retry 3x, then fallback |
| Serena unavailable | Mock connection refused | Skip memory operations, warn user |
| Sequential unavailable | Mock timeout | Use native reasoning, note limitation |

### Recovery Tests

| Scenario | Test Method | Success Criteria |
|----------|-------------|------------------|
| Circuit recovery | Wait 60s after open | Half-open state, test request sent |
| Memory recovery | Clear and repopulate | Delta shows all as "new" |
| Graceful restart | Kill mid-analysis | Next run resumes or restarts cleanly |

---

## Test Execution

### Commands

```bash
# Run all analyze tests
uv run pytest tests/analyze/ -v

# Run specific test file
uv run pytest tests/analyze/test_acceptance.py -v

# Run with coverage
uv run pytest tests/analyze/ --cov=superclaude.analyze --cov-report=html

# Run only compliance tests
uv run pytest tests/analyze/test_compliance.py -v

# Run with markers
uv run pytest tests/analyze/ -m "acceptance" -v
uv run pytest tests/analyze/ -m "integration" -v
```

### CI/CD Integration

```yaml
# .github/workflows/test-analyze.yml
name: Analyze Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -e ".[dev]"
      - name: Run tests
        run: uv run pytest tests/analyze/ -v --cov
```

---

*Test Strategy Generated by SuperClaude Roadmap Generator v1.0*
