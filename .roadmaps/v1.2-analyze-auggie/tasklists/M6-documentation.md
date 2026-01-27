# Tasklist: M6 - Documentation & Testing

## Metadata
- **Milestone**: M6
- **Dependencies**: M5 (P3 Polish & Hardening)
- **Estimated Complexity**: Medium
- **Risk Level**: LOW (R5: user learning curve)
- **Duration**: Week 6

---

## Tasks

### T6.1: Updated analyze.md Command Definition
**Type**: DOC
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/commands/analyze.md`

#### Steps
1. Review all new flags and options added in M1-M5
2. Update YAML header with new MCP servers
3. Document all new flags (--aggressiveness, --tier, --verbose, --evidence)
4. Update examples section with new usage patterns
5. Document tier classification behavior
6. Document progressive disclosure output
7. Document cross-session memory behavior
8. Review and update fallback behavior documentation

#### Acceptance Criteria
- [ ] All new flags documented with valid values
- [ ] All new options documented with defaults
- [ ] Examples cover common use cases
- [ ] Tier classification behavior explained
- [ ] Progressive disclosure explained
- [ ] Cross-session memory explained
- [ ] Fallback behavior documented

#### Command Definition Structure
```yaml
---
name: analyze
description: "Semantic code analysis across quality, security, performance, and architecture domains with Auggie MCP integration"
category: utility
complexity: standard
mcp-servers: [mcp__auggie-mcp__codebase-retrieval, mcp__sequential-thinking__sequentialthinking]
mcp-optional: [serena]
personas: [analyzer, security, performance, architect]
fallback-enabled: true
tier-classification: auto
progressive-disclosure: true
---

## Usage

/sc:analyze [target] [flags]

## Flags

### Depth Control
--depth [quick|deep|comprehensive]    # Analysis depth tier (default: deep)

### Aggressiveness Control (NEW)
--aggressiveness [minimal|balanced|aggressive|maximum]    # Query intensity (default: balanced)

### Tier Classification (NEW)
--tier [auto|strict|standard|light|exempt]    # Compliance tier (default: auto)

### Output Control (NEW)
--verbose    # Show Details tier (context, impact, fix suggestions)
--evidence   # Show Evidence tier (code snippets, validation chain, confidence)

### Focus Control
--focus [quality|security|performance|architecture]    # Analysis domains (comma-separated)

## Examples

### Quick security scan
/sc:analyze @src --focus security --depth quick

### Comprehensive audit with maximum thoroughness
/sc:analyze @src --focus security,quality --depth comprehensive --aggressiveness maximum

### Show full evidence chain
/sc:analyze @auth --focus security --evidence

### Force STRICT tier for sensitive code
/sc:analyze @database --tier strict
```

#### Verification
```bash
# Verify all flags documented
grep -E "(--aggressiveness|--tier|--verbose|--evidence)" src/superclaude/commands/analyze.md
```

---

### T6.2: MCP Integration Examples
**Type**: DOC
**Priority**: P1-High
**Files Affected**:
- `docs/user-guide/analyze-mcp.md`

#### Steps
1. Create documentation file
2. Document Auggie MCP integration pattern
3. Document Serena MCP integration pattern
4. Document Sequential MCP integration pattern
5. Provide code examples for each integration
6. Document circuit breaker behavior
7. Document fallback scenarios

#### Acceptance Criteria
- [ ] Auggie integration fully documented with examples
- [ ] Serena integration documented for memory and validation
- [ ] Sequential integration documented for reasoning
- [ ] Circuit breaker behavior explained
- [ ] Fallback scenarios covered
- [ ] Code examples are copy-pasteable

#### Documentation Structure
```markdown
# MCP Integration in /sc:analyze

## Overview
The analyze command integrates with three MCP servers...

## Auggie MCP Integration

### Purpose
Semantic code discovery using natural language queries.

### Required Parameter
All Auggie calls MUST include `directory_path`:
```yaml
tool: mcp__auggie-mcp__codebase-retrieval
parameters:
  directory_path: "/absolute/path/to/project"  # REQUIRED
  information_request: "Find authentication vulnerabilities"
```

### Example Usage
[Code examples]

## Serena MCP Integration

### Purpose
Symbol analysis and cross-session memory.

### Memory Operations
[Examples of write_memory and read_memory]

### Symbol Validation
[Examples of find_symbol and find_referencing_symbols]

## Sequential MCP Integration

### Purpose
Multi-step reasoning for complex analysis.

### Usage in Analysis
[Examples of sequential thinking for synthesis]

## Circuit Breaker Behavior

### Configuration
[Circuit breaker settings]

### Fallback Chain
[What happens when each server is unavailable]

## Common Patterns

### Pattern 1: Security Analysis
[Full example]

### Pattern 2: Cross-Session Analysis
[Full example with memory]
```

#### Verification
```bash
# Verify documentation exists
test -f docs/user-guide/analyze-mcp.md && echo "File exists"
```

---

### T6.3: Progressive Disclosure Output Examples
**Type**: DOC
**Priority**: P1-High
**Files Affected**:
- `docs/user-guide/analyze-output.md`

#### Steps
1. Create documentation file
2. Document Tier 1 (Summary) output format
3. Document Tier 2 (Details) output format
4. Document Tier 3 (Evidence) output format
5. Show side-by-side comparisons
6. Explain when to use each tier
7. Document delta output for cross-session

#### Acceptance Criteria
- [ ] All 3 tiers clearly documented
- [ ] Visual examples for each tier
- [ ] Use case guidance provided
- [ ] Delta output format shown
- [ ] Copy-pasteable examples

#### Documentation Structure
```markdown
# Understanding /sc:analyze Output

## Output Tiers

### Tier 1: Summary (Default)
Shown by default. Quick overview of findings.

```
Analysis Results: @src/auth
━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Findings: 5 issues (2 critical, 2 high, 1 medium)
🔴 Top Issues:
   1. [SEC-001] SQL Injection - api/users.py:45 (Critical)
   2. [SEC-003] Missing Auth - api/admin.py:12 (Critical)
   3. [SEC-007] Weak Hash - utils/crypto.py:23 (High)

🏥 Health Score: 0.65 (Fair)
📈 Trend: ↑ Improved from 0.58 last analysis
```

### Tier 2: Details (--verbose)
Add `--verbose` for context and fix suggestions.

```
[SEC-001] SQL Injection (Critical)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Location: api/users.py:45
Status: 🆕 New

Context:
  Direct string concatenation in SQL query within
  user input handler. Query constructed from
  untrusted request parameters without sanitization.

Impact:
  Allows arbitrary SQL execution, enabling data
  exfiltration, modification, or destruction.
  OWASP Top 10 #1 vulnerability.

Fix Suggestion:
  Use parameterized queries with SQLAlchemy ORM:
  `db.session.query(User).filter_by(id=user_id)`
```

### Tier 3: Evidence (--evidence)
Add `--evidence` for full audit trail.

```
[SEC-001] SQL Injection (Critical)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Details from Tier 2...]

Evidence:
  Code Snippet:
  │ 44 │ def get_user(user_id):
  │ 45 │     query = f"SELECT * FROM users WHERE id = {user_id}"
  │ 46 │     return db.execute(query)

  Validation Chain:
    ✅ Auggie Relevance:    0.92
    ✅ Serena Verified:     true (symbol found, 3 references)
    ✅ Grep Confirmed:      true (pattern matched)

  Cross-References:
    → validation.py:12 (missing sanitization)
    → db_config.py:8 (connection without prepared statements)

  Confidence: 0.94 (HIGH)
  Methodology: semantic pattern match + hybrid validation

  Cross-Session:
    First Detected: 2026-01-20
    Status: recurring (3 previous analyses)
```

## Delta Output

When previous analysis exists:

```
Delta from Last Analysis (2026-01-25)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆕 New Issues: 2
   [SEC-015] New auth bypass in admin panel
   [PERF-003] N+1 query in user list

✅ Resolved: 3
   [SEC-002] Hardcoded credentials (fixed)
   [SEC-005] Insecure session (fixed)
   [QUAL-001] Dead code removed

🔁 Recurring: 5
   [SEC-001] SQL Injection (3rd occurrence)
   [SEC-003] Missing auth
   ...

📈 Health Score: 0.65 → 0.72 (+10.8%)
```
```

#### Verification
```bash
# Verify documentation exists
test -f docs/user-guide/analyze-output.md && echo "File exists"
```

---

### T6.4: AT-1 to AT-8 Acceptance Tests
**Type**: TEST
**Priority**: P1-High
**Files Affected**:
- `tests/analyze/test_acceptance.py`

#### Steps
1. Implement AT-1: Basic Semantic Discovery
2. Implement AT-2: Graceful Degradation with Feedback
3. Implement AT-3: Evidence Chain with Progressive Disclosure
4. Implement AT-4: Large Codebase Handling
5. Implement AT-5: Aggressiveness Control
6. Implement AT-6: Tier Classification Integration
7. Implement AT-7: Iterative Query Refinement
8. Implement AT-8: Cross-Session Memory

#### Acceptance Criteria
- [ ] All 8 acceptance tests implemented
- [ ] Tests follow Gherkin Given/When/Then structure
- [ ] Tests use appropriate fixtures
- [ ] All tests pass
- [ ] Coverage includes success and failure paths

#### Test Implementation
```python
# tests/analyze/test_acceptance.py
import pytest

class TestAnalyzeAcceptance:
    """Acceptance tests AT-1 through AT-8"""

    @pytest.mark.acceptance
    def test_at1_basic_semantic_discovery(self, sample_codebase, mock_auggie):
        """
        AT-1: Basic Semantic Discovery

        Given a codebase with authentication module at "@auth"
        And Auggie MCP is available
        When /sc:analyze @auth --focus security --depth quick
        Then findings include all auth-related security patterns
        And execution completes within 30 seconds
        And token usage is under 8K
        And Auggie queries include directory_path parameter
        """
        pass

    @pytest.mark.acceptance
    def test_at2_graceful_degradation(self, sample_codebase, mock_auggie_unavailable):
        """
        AT-2: Graceful Degradation with Feedback

        Given Auggie MCP is unavailable (circuit breaker open)
        When /sc:analyze @src --focus quality --depth deep
        Then analysis completes using native tools (Glob + Grep)
        And user receives degradation notification
        And results include degradation impact note
        And quality is marked as "reduced precision"
        """
        pass

    @pytest.mark.acceptance
    def test_at3_progressive_disclosure(self, sample_codebase, sql_injection_finding):
        """
        AT-3: Evidence Chain with Progressive Disclosure

        Given security analysis finds SQL injection
        When default output is shown
        Then finding shows summary tier only

        When user requests --verbose
        Then finding shows details tier

        When user requests --evidence
        Then finding shows evidence tier
        And confidence score is provided
        """
        pass

    @pytest.mark.acceptance
    def test_at4_large_codebase(self, large_codebase):
        """
        AT-4: Large Codebase Handling with Adaptive Budgeting

        Given a codebase with 500K+ LOC
        When /sc:analyze --focus architecture --depth comprehensive
        Then analysis detects "large" size tier
        And token budget is multiplied by 2.0x
        And analysis uses hierarchical narrowing
        And completes within 5 minutes
        """
        pass

    @pytest.mark.acceptance
    def test_at5_aggressiveness(self, sample_codebase, mock_auggie):
        """
        AT-5: Aggressiveness Control

        Given a standard codebase
        When /sc:analyze @src --focus security --depth deep --aggressiveness aggressive
        Then Auggie queries are 1.5x the balanced baseline
        And token budget is 1.3x the balanced baseline
        And hybrid validation is mandatory
        """
        pass

    @pytest.mark.acceptance
    def test_at6_tier_classification(self, auth_codebase):
        """
        AT-6: Tier Classification Integration

        Given a file path containing "auth" in security-sensitive location
        When /sc:analyze @src/auth --tier auto
        Then tier classification detects STRICT
        And auto-aggressiveness is set to aggressive
        And auto-depth is set to deep minimum
        And hybrid validation is mandatory
        """
        pass

    @pytest.mark.acceptance
    def test_at7_iterative_refinement(self, sample_codebase, low_quality_initial_results):
        """
        AT-7: Iterative Query Refinement

        Given an initial broad query with quality_score 0.45
        When /sc:analyze --depth comprehensive
        Then refinement strategy is triggered
        And query is narrowed based on initial results
        And second query achieves quality_score >= 0.7
        And refinement trace is logged
        """
        pass

    @pytest.mark.acceptance
    def test_at8_cross_session_memory(self, sample_codebase, mock_serena_with_history):
        """
        AT-8: Cross-Session Memory

        Given a previous analysis exists in Serena memory
        When /sc:analyze @src is run again
        Then previous findings are loaded from memory
        And delta is calculated (new/resolved/recurring)
        And output shows delta summary
        And trend indicator shows health score change
        """
        pass
```

#### Verification
```bash
# Run all acceptance tests
uv run pytest tests/analyze/test_acceptance.py -v -m acceptance

# Run with coverage
uv run pytest tests/analyze/test_acceptance.py --cov=superclaude --cov-report=term-missing
```

---

### T6.5: A/B Testing Framework
**Type**: TEST
**Priority**: P2-Medium
**Files Affected**:
- `tests/analyze/test_ab_framework.py`

#### Steps
1. Design A/B testing infrastructure
2. Implement baseline measurement (native tools)
3. Implement treatment measurement (MCP-enhanced)
4. Implement comparison metrics
5. Create test harness for precision measurement
6. Document A/B testing methodology

#### Acceptance Criteria
- [ ] A/B framework measures token usage
- [ ] A/B framework measures latency
- [ ] A/B framework measures precision
- [ ] Comparison report generated
- [ ] Statistical significance calculated

#### A/B Framework Structure
```python
# tests/analyze/test_ab_framework.py
import pytest
from dataclasses import dataclass

@dataclass
class ABTestResult:
    variant: str  # "baseline" or "treatment"
    tokens_used: int
    latency_seconds: float
    precision: float
    recall: float
    findings_count: int

class AnalyzeABTestFramework:
    """Framework for A/B testing analyze command improvements"""

    def run_baseline(self, target, focus, depth):
        """Run analysis with native tools only (no MCP)"""
        pass

    def run_treatment(self, target, focus, depth):
        """Run analysis with full MCP integration"""
        pass

    def compare_results(self, baseline: ABTestResult, treatment: ABTestResult):
        """Generate comparison report"""
        return {
            "token_reduction": (baseline.tokens_used - treatment.tokens_used) / baseline.tokens_used,
            "latency_improvement": (baseline.latency_seconds - treatment.latency_seconds) / baseline.latency_seconds,
            "precision_improvement": treatment.precision - baseline.precision,
            "recall_improvement": treatment.recall - baseline.recall,
        }

class TestABFramework:

    @pytest.mark.ab_test
    def test_token_efficiency_claim(self, ab_framework, test_codebase):
        """Verify 40-70% token reduction claim"""
        baseline = ab_framework.run_baseline(test_codebase, "security", "deep")
        treatment = ab_framework.run_treatment(test_codebase, "security", "deep")
        comparison = ab_framework.compare_results(baseline, treatment)

        assert comparison["token_reduction"] >= 0.40, "Must achieve 40% token reduction"
        assert comparison["token_reduction"] <= 0.70, "Should not exceed 70% reduction"

    @pytest.mark.ab_test
    def test_precision_improvement_claim(self, ab_framework, test_codebase_with_known_issues):
        """Verify ≥85% precision target"""
        treatment = ab_framework.run_treatment(test_codebase_with_known_issues, "security", "deep")

        assert treatment.precision >= 0.85, "Must achieve 85% precision"
```

#### Verification
```bash
# Run A/B tests (may be slow)
uv run pytest tests/analyze/test_ab_framework.py -v -m ab_test
```

---

## Milestone Completion Checklist

- [ ] T6.1: Updated analyze.md Command Definition - completed
- [ ] T6.2: MCP Integration Examples - completed
- [ ] T6.3: Progressive Disclosure Output Examples - completed
- [ ] T6.4: AT-1 to AT-8 Acceptance Tests - completed
- [ ] T6.5: A/B Testing Framework - completed
- [ ] All 8 acceptance tests passing
- [ ] Documentation review complete
- [ ] Memory checkpoint saved

## Checkpoint Command
```
mcp__serena__write_memory("analyze-auggie-m6", {
  status: "completed",
  deliverables: ["M6-D1", "M6-D2", "M6-D3", "M6-D4", "M6-D5"],
  acceptance_tests_passed: 8,
  documentation_complete: true,
  issues: [],
  verified: true
})
```

---

## Final Implementation Completion

After M6 completion, run final verification:

```bash
# Run full test suite
uv run pytest tests/analyze/ -v --cov=superclaude --cov-report=html

# Verify all acceptance tests
uv run pytest tests/analyze/test_acceptance.py -v -m acceptance

# Generate coverage report
uv run pytest tests/analyze/ --cov-report=term-missing
```

### Final Memory Persistence
```
mcp__serena__write_memory("analyze-auggie-complete", {
  version: "1.2",
  milestones_completed: ["M1", "M2", "M3", "M4", "M5", "M6"],
  test_coverage: 85,
  acceptance_tests_passed: 8,
  features_implemented: [
    "MCP Integration Fix",
    "Progressive Disclosure",
    "Tier Classification",
    "Cross-Session Memory",
    "Language-Aware Templates",
    "Iterative Refinement",
    "Aggressiveness Control",
    "Hybrid Validation",
    "Adaptive Budgeting",
    "Quality Scoring",
    "Degradation Feedback",
    "Performance Monitoring"
  ],
  completion_date: "2026-01-26"
})
```

---

*Tasklist M6 - Generated by SuperClaude Roadmap Generator v1.0*
