# Execution Prompt: v1.2-analyze-auggie - /sc:analyze Auggie MCP Integration

## Metadata
- **Roadmap Source**: `.dev/releases/current/v1.2-analyze-auggie/roadmap.md`
- **Generated**: 2026-01-26
- **Generator**: SuperClaude Roadmap Generator v1.0
- **Compliance Tier**: STRICT (multi-file, MCP integration, security-related)

---

## Implementation Instructions

### Pre-Implementation Checklist

Before starting any milestone implementation:

- [ ] Verify SuperClaude project is activated (`mcp__serena__activate_project`)
- [ ] Check git working directory is clean (`git status`)
- [ ] Read the milestone tasklist file completely
- [ ] Verify MCP server availability (Auggie, Serena, Sequential)
- [ ] Create feature branch: `git checkout -b feature/analyze-auggie-m{N}`

### Critical Corrections (MUST APPLY)

| # | Mistake to Avoid | Correct Approach |
|---|------------------|------------------|
| 1 | Using "auggie-mcp" as tool name | Use `mcp__auggie-mcp__codebase-retrieval` |
| 2 | Omitting directory_path parameter | ALWAYS include `directory_path` as REQUIRED parameter |
| 3 | Using "blocked" TodoWrite state | Only use: `pending`, `in_progress`, `completed` |
| 4 | Looking for compliance in RULES.md | Compliance tiers are in ORCHESTRATOR.md |
| 5 | Embedding subagent_type as API param | Embed agent type description in Task prompt |
| 6 | Assuming 6 wave-enabled commands | Correct count is 7 |

---

## Milestone Execution Order

Execute milestones in strict sequential order:

```
M1 → M2 → M3 → M4 → M5 → M6
```

### Per-Milestone Workflow

For each milestone:

1. **Load Context**
   ```
   /sc:load .dev/releases/current/v1.2-analyze-auggie/tasklists/M{N}-*.md
   ```

2. **Create TodoWrite Tasks**
   ```
   Use TodoWrite to create tasks from the tasklist
   Only 3 states: pending, in_progress, completed
   ```

3. **Execute Deliverables**
   - Mark task `in_progress` before starting
   - Complete implementation
   - Run verification commands
   - Mark task `completed` immediately after

4. **Verify Milestone**
   ```bash
   # Run milestone-specific tests
   uv run pytest tests/analyze/test_*.py -v -k "M{N}"
   ```

5. **Checkpoint**
   ```
   mcp__serena__write_memory("analyze-auggie-m{N}", {
     status: "completed",
     deliverables: [...],
     issues: [...]
   })
   ```

---

## Milestone 1: Foundation - MCP Integration Fix

### Tasklist Reference
`tasklists/M1-foundation.md`

### Key Implementation Steps

#### M1-D1: Fix MCP Tool Name

**Before** (WRONG):
```yaml
tool: auggie-mcp
```

**After** (CORRECT):
```yaml
tool: mcp__auggie-mcp__codebase-retrieval
parameters:
  directory_path: "{absolute_project_path}"  # REQUIRED
  information_request: "{semantic_query}"
```

#### M1-D2: Add directory_path Parameter

**Implementation Pattern**:
```python
# Auto-detect project root
import os
project_root = os.getcwd()  # or detect from git root

# All Auggie calls MUST include directory_path
auggie_query = {
    "tool": "mcp__auggie-mcp__codebase-retrieval",
    "parameters": {
        "directory_path": project_root,  # REQUIRED
        "information_request": query
    }
}
```

#### M1-D3: Circuit Breaker Implementation

**Configuration**:
```yaml
circuit_breaker:
  auggie_circuit:
    failure_threshold: 3
    timeout: 30s
    recovery: "Half-open after 60s"
    fallback: "Native Glob + Grep discovery"
```

### Verification
```bash
# Test MCP tool name is correct
grep -r "mcp__auggie-mcp__codebase-retrieval" src/superclaude/commands/analyze.md

# Test directory_path is present
grep -r "directory_path" src/superclaude/commands/analyze.md

# Run foundation tests
uv run pytest tests/analyze/test_mcp_integration.py -v
```

---

## Milestone 2: P1 Core Features

### Tasklist Reference
`tasklists/M2-p1-core.md`

### Key Implementation Steps

#### M2-D1: Progressive Disclosure Output

**3-Tier Structure**:
```yaml
# Tier 1: Summary (always shown)
finding:
  id: "SEC-001"
  severity: "critical"
  location: "api/users.py:45"
  action_required: true

# Tier 2: Details (--verbose)
details:
  context: "Direct string concatenation in SQL query"
  impact: "Allows arbitrary SQL execution"
  fix_suggestion: "Use parameterized queries"

# Tier 3: Evidence (--evidence)
evidence:
  code_snippet: "query = f\"SELECT * FROM...\""
  validation_chain:
    auggie_relevance: 0.92
    serena_verified: true
    grep_confirmed: true
  confidence: 0.94
```

#### M2-D2: Tier Classification Integration

**Mapping Table**:
```yaml
tier_mapping:
  STRICT:
    auto_aggressiveness: aggressive
    auto_depth: deep
    validation: mandatory_hybrid
    evidence_tier: Full
  STANDARD:
    auto_aggressiveness: balanced
    auto_depth: deep
    validation: spot_check
    evidence_tier: Summary + Details
  LIGHT:
    auto_aggressiveness: minimal
    auto_depth: quick
    validation: none
    evidence_tier: Summary only
  EXEMPT:
    auto_aggressiveness: minimal
    auto_depth: quick
    validation: none
    evidence_tier: Summary only
```

#### M2-D3: Cross-Session Memory

**Memory Schema**:
```yaml
memory_keys:
  analysis_{project_hash}_latest: "Most recent analysis results"
  analysis_{project_hash}_history: "Historical analysis trend"
  patterns_{project_hash}: "Learned patterns and hot spots"

# Implementation
mcp__serena__write_memory("analysis_{hash}_latest", {
  findings: [...],
  timestamp: "2026-01-26",
  health_score: 0.75
})
```

### Verification
```bash
# Test progressive disclosure
uv run pytest tests/analyze/test_acceptance.py::test_at3_progressive_disclosure -v

# Test memory persistence
uv run pytest tests/analyze/test_memory.py -v

# Run all M2 tests
uv run pytest tests/analyze/ -v -k "M2"
```

---

## Milestone 3: P2 Query Enhancement

### Tasklist Reference
`tasklists/M3-p2-query.md`

### Key Implementation Steps

#### M3-D1: Language-Aware Query Templates

**Example Templates**:
```yaml
python_security:
  - "SQL injection vulnerabilities including f-string formatting"
  - "Pickle deserialization and untrusted data loading"
  - "__import__, exec, eval usage patterns"

javascript_security:
  - "XSS vulnerabilities in DOM manipulation"
  - "Prototype pollution attack vectors"
  - "Insecure use of innerHTML"

go_security:
  - "SQL injection in database/sql queries"
  - "Path traversal in file operations"
```

#### M3-D3: Aggressiveness Flag

**Implementation**:
```yaml
aggressiveness_levels:
  minimal:
    query_multiplier: 0.5
    token_multiplier: 0.7
    use_case: "Quick sanity checks, CI pipelines"
  balanced:
    query_multiplier: 1.0
    token_multiplier: 1.0
    use_case: "Standard development workflow"
  aggressive:
    query_multiplier: 1.5
    token_multiplier: 1.3
    use_case: "Pre-merge reviews, security-sensitive"
  maximum:
    query_multiplier: 2.0
    token_multiplier: 1.5
    use_case: "Security audits, compliance reviews"
```

### Verification
```bash
# Test language templates
uv run pytest tests/analyze/test_acceptance.py::test_language_templates -v

# Test aggressiveness
uv run pytest tests/analyze/test_acceptance.py::test_at5_aggressiveness -v
```

---

## Milestone 4: P2 Validation & Budgeting

### Tasklist Reference
`tasklists/M4-p2-validation.md`

### Key Implementation Steps

#### M4-D1: Hybrid Validation Pipeline

**3-Stage Pipeline**:
```
Stage 1: Auggie (Semantic)     → relevance_score >= 0.6
Stage 2: Serena (Structural)   → symbol_found AND references > 0
Stage 3: Grep (Syntactic)      → pattern_matched

Confidence Assignment:
  All 3 pass:     HIGH (0.9+)
  Stages 1+2:     MEDIUM (0.7-0.9)
  Stage 1 only:   LOW (0.5-0.7)
```

#### M4-D2: Adaptive Token Budgeting

**Formula**:
```
final_budget = base_budget × size_multiplier × aggressiveness_multiplier × focus_count_factor

Size Multipliers:
  small (<10K LOC): 1.0x
  medium (10-100K): 1.5x
  large (100K-1M): 2.0x
  massive (>1M): 2.5x
```

### Verification
```bash
# Test validation pipeline
uv run pytest tests/analyze/test_validation.py -v

# Test budgeting
uv run pytest tests/analyze/test_budgeting.py -v
```

---

## Milestone 5: P3 Polish & Hardening

### Tasklist Reference
`tasklists/M5-p3-hardening.md`

### Key Implementation Steps

#### M5-D2: Real-Time Degradation Feedback

**Message Templates**:
```yaml
degradation_messages:
  auggie_unavailable: "⚠️ Semantic search unavailable - using pattern matching (reduced precision)"
  serena_unavailable: "⚠️ Symbol analysis unavailable - using file-based analysis"
  sequential_unavailable: "⚠️ Advanced reasoning unavailable - using direct synthesis"
  partial_degradation: "⚠️ Running in partial fallback mode - some features limited"
```

### Verification
```bash
# Test degradation scenarios
uv run pytest tests/analyze/test_degradation.py -v
```

---

## Milestone 6: Documentation & Testing

### Tasklist Reference
`tasklists/M6-documentation.md`

### Key Implementation Steps

#### M6-D4: Acceptance Tests

**Test Implementation Pattern**:
```python
@pytest.mark.acceptance
class TestAnalyzeAcceptance:

    def test_at1_basic_semantic_discovery(self, mock_auggie):
        """AT-1: Basic Semantic Discovery"""
        # Given a codebase with authentication module
        # When /sc:analyze @auth --focus security --depth quick
        # Then findings include all auth-related security patterns
        pass

    def test_at2_graceful_degradation(self, mock_auggie_unavailable):
        """AT-2: Graceful Degradation with Feedback"""
        # Given Auggie MCP is unavailable
        # When /sc:analyze @src --focus quality --depth deep
        # Then analysis completes using native tools
        # And user receives degradation notification
        pass
```

### Verification
```bash
# Run all acceptance tests
uv run pytest tests/analyze/test_acceptance.py -v

# Run with coverage
uv run pytest tests/analyze/ --cov=superclaude --cov-report=html
```

---

## Post-Implementation Checklist

After completing all milestones:

- [ ] All 8 acceptance tests passing
- [ ] Code coverage ≥80%
- [ ] Documentation updated
- [ ] Memory checkpoint saved
- [ ] Feature branch merged to integration
- [ ] Changelog updated

### Final Memory Persistence
```
mcp__serena__write_memory("analyze-auggie-complete", {
  version: "1.2",
  milestones_completed: ["M1", "M2", "M3", "M4", "M5", "M6"],
  test_coverage: 85,
  acceptance_tests_passed: 8,
  completion_date: "2026-01-26"
})
```

### Quality Engineer Validation Questions

Before marking implementation complete, answer these questions:

1. "Did all Auggie calls include the `directory_path` parameter?" → YES
2. "Did TodoWrite use only 3 states (no 'blocked')?" → YES
3. "Are all 8 acceptance tests passing?" → YES
4. "Is graceful degradation working with user feedback?" → YES
5. "Is cross-session memory persisting correctly?" → YES

---

*Execution Prompt Generated by SuperClaude Roadmap Generator v1.0*
