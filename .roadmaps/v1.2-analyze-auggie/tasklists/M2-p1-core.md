# Tasklist: M2 - P1 Core Features

## Metadata
- **Milestone**: M2
- **Dependencies**: M1 (Foundation - MCP Integration Fix)
- **Estimated Complexity**: High
- **Risk Level**: MEDIUM (R10: memory corruption)
- **Duration**: Week 1-2
- **ROI Range**: 6.71 - 7.01

---

## Tasks

### T2.1: Progressive Disclosure Output (3-tier)
**Type**: FEATURE
**Priority**: P1-High
**ROI Score**: 7.01 (Highest priority improvement)
**Files Affected**:
- `src/superclaude/commands/analyze.md`

#### Steps
1. Define the 3-tier output structure schema
2. Implement Tier 1 (Summary) - always shown by default
3. Implement Tier 2 (Details) - shown with `--verbose` flag
4. Implement Tier 3 (Evidence) - shown with `--evidence` flag
5. Add flag parsing for --verbose and --evidence
6. Ensure backward compatibility with existing output

#### Acceptance Criteria
- [ ] Default output shows only Summary tier (location, severity, action_required)
- [ ] `--verbose` adds Details tier (context, impact, fix_suggestion)
- [ ] `--evidence` adds Evidence tier (code_snippet, validation_chain, confidence)
- [ ] Tiers are additive (--evidence includes --verbose content)
- [ ] No performance penalty for Summary-only output

#### Output Schema
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
  impact: "Allows arbitrary SQL execution, data breach risk"
  fix_suggestion: "Use parameterized queries with SQLAlchemy"

# Tier 3: Evidence (--evidence)
evidence:
  code_snippet: "query = f\"SELECT * FROM users WHERE id = {user_id}\""
  validation_chain:
    auggie_relevance: 0.92
    serena_verified: true
    grep_confirmed: true
  cross_references:
    - "validation.py:12 (missing sanitization)"
  confidence: 0.94
  methodology: "semantic pattern match + hybrid validation"
```

#### Verification
```bash
# Test default output (summary only)
uv run pytest tests/analyze/test_acceptance.py::test_at3_progressive_disclosure -v
```

---

### T2.2: Tier Classification Integration
**Type**: FEATURE
**Priority**: P1-High
**ROI Score**: 6.83
**Files Affected**:
- `src/superclaude/commands/analyze.md`
- `.claude/skills/sc-task-unified/SKILL.md` (reference)

#### Steps
1. Import tier classification logic from sc:task-unified
2. Implement auto-detection of tier based on analysis target
3. Map tiers to analysis parameters (aggressiveness, depth, validation)
4. Add `--tier auto|strict|standard|light|exempt` flag
5. Display classification confidence and rationale

#### Acceptance Criteria
- [ ] Auto-detection identifies STRICT for security paths (auth/, security/, crypto/)
- [ ] Auto-detection identifies EXEMPT for documentation paths (*.md, docs/)
- [ ] Tier mapping correctly adjusts aggressiveness and depth
- [ ] User can override auto-detection with --tier flag
- [ ] Classification confidence shown when <70%

#### Tier Mapping Table
```yaml
tier_mapping:
  STRICT:
    auto_aggressiveness: aggressive
    auto_depth: deep  # minimum
    validation: mandatory_hybrid
    evidence_tier: Full
    triggers: ["auth/", "security/", "crypto/", "database/", "migration/"]

  STANDARD:
    auto_aggressiveness: balanced
    auto_depth: deep
    validation: spot_check
    evidence_tier: Summary + Details
    triggers: ["src/", "lib/", "services/"]

  LIGHT:
    auto_aggressiveness: minimal
    auto_depth: quick
    validation: none
    evidence_tier: Summary only
    triggers: ["config/", "*.json", "*.yaml"]

  EXEMPT:
    auto_aggressiveness: minimal
    auto_depth: quick
    validation: none
    evidence_tier: Summary only
    triggers: ["*.md", "docs/", "README", "CHANGELOG"]
```

#### Verification
```bash
# Test tier classification
uv run pytest tests/analyze/test_acceptance.py::test_at6_tier_classification -v
```

---

### T2.3: Cross-Session Memory via Serena
**Type**: FEATURE
**Priority**: P1-High
**ROI Score**: 6.71
**Files Affected**:
- `src/superclaude/commands/analyze.md`

#### Steps
1. Define memory schema (latest, history, patterns)
2. Implement project hash generation for memory keys
3. Implement write_memory on analysis completion
4. Implement read_memory on analysis start
5. Calculate delta (new, resolved, recurring findings)
6. Display delta summary in output
7. Implement pattern learning (hot spots, common issues)

#### Acceptance Criteria
- [ ] Analysis results stored via mcp__serena__write_memory
- [ ] Previous results loaded via mcp__serena__read_memory
- [ ] Delta calculated correctly (new/resolved/recurring)
- [ ] Output shows delta: "🆕 X new | ✅ Y resolved | 🔁 Z recurring"
- [ ] Trend indicator shows health score change

#### Memory Schema
```yaml
memory_keys:
  analysis_{project_hash}_latest:
    findings: [...]
    timestamp: "2026-01-26"
    health_score: 0.75

  analysis_{project_hash}_history:
    - timestamp: "2026-01-25"
      health_score: 0.72
      finding_count: 15
    - timestamp: "2026-01-20"
      health_score: 0.68
      finding_count: 18

  patterns_{project_hash}:
    hot_spots: ["api/users.py", "auth/middleware.py"]
    common_issues: ["sql_injection", "missing_validation"]
    improvement_trend: [0.68, 0.72, 0.75]
```

#### Delta Calculation Logic
```python
def calculate_delta(current_findings, previous_findings):
    current_ids = {f.id for f in current_findings}
    previous_ids = {f.id for f in previous_findings}

    return {
        "new": current_ids - previous_ids,      # 🆕
        "resolved": previous_ids - current_ids,  # ✅
        "recurring": current_ids & previous_ids  # 🔁
    }
```

#### Verification
```bash
# Test cross-session memory
uv run pytest tests/analyze/test_memory.py -v
uv run pytest tests/analyze/test_acceptance.py::test_at8_cross_session_memory -v
```

---

### T2.4: Basic Degradation Feedback
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/commands/analyze.md`

#### Steps
1. Detect when MCP servers are unavailable
2. Generate appropriate degradation message
3. Display message at start of analysis
4. Include capability impact explanation
5. Track degradation state for output quality marking

#### Acceptance Criteria
- [ ] User sees "⚠️ Semantic search unavailable" when Auggie down
- [ ] Message includes impact explanation
- [ ] Output marked as "reduced precision" when degraded
- [ ] Multiple degradation states handled (partial, full)

#### Degradation Messages
```yaml
degradation_messages:
  auggie_unavailable:
    banner: "⚠️ Semantic search unavailable - using pattern matching"
    impact: "Reduced precision, may miss semantic relationships"
    quality_note: "Analysis quality: REDUCED"

  serena_unavailable:
    banner: "⚠️ Symbol analysis unavailable - using file-based analysis"
    impact: "No cross-reference validation"
    quality_note: "Validation: PARTIAL"

  full_degradation:
    banner: "⚠️ Running in full fallback mode"
    impact: "Using native tools only, limited analysis capability"
    quality_note: "Analysis quality: BASIC"
```

#### Verification
```bash
# Test degradation feedback
uv run pytest tests/analyze/test_acceptance.py::test_at2_graceful_degradation -v
```

---

### T2.5: Memory Persistence Tests
**Type**: TEST
**Priority**: P1-High
**Files Affected**:
- `tests/analyze/test_memory.py`

#### Steps
1. Create test fixtures for memory operations
2. Write test for write_memory on completion
3. Write test for read_memory on start
4. Write test for delta calculation
5. Write test for corrupted memory handling
6. Write cross-session integration test

#### Acceptance Criteria
- [ ] Memory write completes without error
- [ ] Memory read returns correct structure
- [ ] Delta calculation is accurate
- [ ] Corrupted memory triggers graceful recovery
- [ ] Cross-session test passes

#### Test Structure
```python
# tests/analyze/test_memory.py
import pytest

class TestAnalyzeMemory:

    def test_write_memory_on_completion(self, mock_serena):
        """Findings stored via write_memory on analysis completion"""
        pass

    def test_read_memory_on_start(self, mock_serena):
        """Previous findings loaded via read_memory on analysis start"""
        pass

    def test_delta_calculation(self):
        """Delta correctly identifies new/resolved/recurring"""
        pass

    def test_corrupted_memory_recovery(self, mock_serena_corrupted):
        """Graceful recovery when memory corrupted"""
        pass

    @pytest.mark.integration
    def test_cross_session_persistence(self, real_serena):
        """Full cross-session test with real Serena"""
        pass
```

#### Verification
```bash
# Run memory tests
uv run pytest tests/analyze/test_memory.py -v
```

---

## Milestone Completion Checklist

- [ ] T2.1: Progressive Disclosure Output - completed
- [ ] T2.2: Tier Classification Integration - completed
- [ ] T2.3: Cross-Session Memory via Serena - completed
- [ ] T2.4: Basic Degradation Feedback - completed
- [ ] T2.5: Memory Persistence Tests - completed
- [ ] All verification commands pass
- [ ] AD-4 (Progressive Disclosure) implemented
- [ ] Memory checkpoint saved

## Checkpoint Command
```
mcp__serena__write_memory("analyze-auggie-m2", {
  status: "completed",
  deliverables: ["M2-D1", "M2-D2", "M2-D3", "M2-D4", "M2-D5"],
  roi_delivered: [7.01, 6.83, 6.71],
  issues: [],
  verified: true
})
```

---

*Tasklist M2 - Generated by SuperClaude Roadmap Generator v1.0*
