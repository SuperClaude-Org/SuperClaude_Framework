# Tasklist: M5 - P3 Polish & Hardening

## Metadata
- **Milestone**: M5
- **Dependencies**: M4 (P2 Validation & Budgeting)
- **Estimated Complexity**: Medium
- **Risk Level**: LOW (R7: evidence overhead)
- **Duration**: Week 5
- **ROI Range**: 5.42 - 5.53

---

## Tasks

### T5.1: Auggie Result Quality Scoring
**Type**: IMPROVEMENT
**Priority**: P3-Low
**ROI Score**: 5.53
**Files Affected**:
- `src/superclaude/commands/analyze.md`

#### Steps
1. Define quality score metrics (relevance, completeness, confidence)
2. Implement relevance scoring based on query match
3. Implement completeness scoring based on coverage
4. Implement confidence scoring based on consistency
5. Calculate composite quality score
6. Log scores in verbose output
7. Trigger refinement when score < threshold

#### Acceptance Criteria
- [ ] relevance_score calculated for each Auggie result
- [ ] completeness_score calculated for each Auggie result
- [ ] confidence_score calculated for each Auggie result
- [ ] Composite score combines all metrics
- [ ] Scores logged when --verbose active
- [ ] Refinement triggers when composite < 0.7

#### Quality Score Metrics
```yaml
quality_metrics:
  relevance_score:
    description: "How well results match the query intent"
    calculation: "Semantic similarity between query and results"
    range: 0.0 - 1.0
    threshold: 0.6

  completeness_score:
    description: "How thoroughly the codebase was searched"
    calculation: "Files analyzed / total relevant files"
    range: 0.0 - 1.0
    threshold: 0.7

  confidence_score:
    description: "How consistent results are with each other"
    calculation: "Agreement between multiple query approaches"
    range: 0.0 - 1.0
    threshold: 0.7

  composite_score:
    description: "Overall quality indicator"
    calculation: "(relevance * 0.4) + (completeness * 0.3) + (confidence * 0.3)"
    range: 0.0 - 1.0
    action_threshold: 0.7
```

#### Quality Score Calculation
```python
def calculate_quality_scores(auggie_results, query, codebase_info):
    # Relevance: semantic match to query
    relevance = calculate_semantic_similarity(
        query,
        [r.content for r in auggie_results]
    )

    # Completeness: coverage of relevant files
    files_analyzed = len(set(r.file_path for r in auggie_results))
    expected_files = estimate_relevant_files(query, codebase_info)
    completeness = min(1.0, files_analyzed / expected_files)

    # Confidence: consistency of results
    confidence = calculate_result_consistency(auggie_results)

    # Composite
    composite = (relevance * 0.4) + (completeness * 0.3) + (confidence * 0.3)

    return {
        "relevance_score": relevance,
        "completeness_score": completeness,
        "confidence_score": confidence,
        "composite_score": composite
    }
```

#### Verbose Output Format
```
Quality Scores:
  📊 Relevance:    0.85 ████████░░
  📊 Completeness: 0.72 ███████░░░
  📊 Confidence:   0.91 █████████░
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 Composite:    0.82 ████████░░ ✓ Above threshold
```

#### Verification
```bash
# Test quality scoring
uv run pytest tests/analyze/test_quality_scoring.py -v
```

---

### T5.2: Real-Time Degradation Feedback
**Type**: IMPROVEMENT
**Priority**: P3-Low
**ROI Score**: 5.42
**Files Affected**:
- `src/superclaude/commands/analyze.md`

#### Steps
1. Define degradation states and triggers
2. Implement real-time degradation detection
3. Create degradation banner/message templates
4. Implement impact explanation generation
5. Add capability status indicator
6. Track degradation for output quality marking
7. Implement recovery notification

#### Acceptance Criteria
- [ ] Degradation detected in real-time during analysis
- [ ] Banner shown immediately when degradation occurs
- [ ] Impact explanation includes affected capabilities
- [ ] Capability status shows what's available
- [ ] Output marked with quality impact
- [ ] Recovery notification when service restored

#### Degradation States
```yaml
degradation_states:
  FULL_CAPABILITY:
    icon: "✅"
    message: null  # No message needed
    impact: null

  SEMANTIC_DEGRADED:
    trigger: "Auggie MCP unavailable"
    icon: "⚠️"
    banner: "Semantic search unavailable - using pattern matching"
    impact: "Reduced precision, may miss semantic relationships"
    affected: ["semantic discovery", "relevance scoring"]
    quality_note: "Analysis quality: REDUCED"

  VALIDATION_DEGRADED:
    trigger: "Serena MCP unavailable"
    icon: "⚠️"
    banner: "Symbol analysis unavailable - using file-based analysis"
    impact: "No cross-reference validation, reduced confidence scoring"
    affected: ["hybrid validation stage 2", "symbol tracking"]
    quality_note: "Validation: PARTIAL"

  REASONING_DEGRADED:
    trigger: "Sequential MCP unavailable"
    icon: "⚠️"
    banner: "Advanced reasoning unavailable - using direct synthesis"
    impact: "Simpler analysis patterns, may miss complex issues"
    affected: ["multi-step reasoning", "pattern synthesis"]
    quality_note: "Analysis depth: BASIC"

  FULL_DEGRADATION:
    trigger: "All MCP servers unavailable"
    icon: "🔴"
    banner: "Running in full fallback mode"
    impact: "Using native tools only, limited analysis capability"
    affected: ["all MCP features"]
    quality_note: "Analysis quality: BASIC"
```

#### Banner Implementation
```python
def display_degradation_banner(degradation_state):
    """Display real-time degradation notification"""
    if degradation_state.banner:
        print(f"\n{degradation_state.icon} {degradation_state.banner}")
        print(f"   Impact: {degradation_state.impact}")
        if degradation_state.affected:
            print(f"   Affected: {', '.join(degradation_state.affected)}")
        print()

def display_recovery_notification(recovered_service):
    """Display notification when service recovered"""
    print(f"\n✅ {recovered_service} recovered - resuming full capability")
```

#### Output Quality Marking
```yaml
output_quality_marking:
  # Add to analysis output header
  header_format: |
    Analysis Report
    ━━━━━━━━━━━━━━━
    Target: {target}
    Depth: {depth}
    Quality: {quality_note}  # <-- Added when degraded

  # Add to findings
  finding_format: |
    [SEC-001] SQL Injection (Critical)
    Location: api/users.py:45
    Confidence: 0.72 [REDUCED*]  # <-- Asterisk when degraded

    * Confidence may be reduced due to semantic search unavailability
```

#### Verification
```bash
# Test degradation feedback
uv run pytest tests/analyze/test_degradation.py -v
```

---

### T5.3: Performance Monitoring Integration
**Type**: IMPROVEMENT
**Priority**: P3-Low
**Files Affected**:
- `src/superclaude/commands/analyze.md`

#### Steps
1. Define performance metrics to track
2. Implement latency tracking per phase
3. Implement token usage tracking
4. Implement MCP call counting
5. Add metrics to verbose output
6. Implement threshold alerting
7. Create performance summary

#### Acceptance Criteria
- [ ] Latency tracked per analysis phase
- [ ] Token usage tracked accurately
- [ ] MCP call count tracked
- [ ] Metrics shown in --verbose output
- [ ] Alerts triggered when thresholds exceeded
- [ ] Performance summary at analysis end

#### Performance Metrics
```yaml
performance_metrics:
  latency:
    phases:
      - classify_configure
      - discovery
      - analysis
      - synthesis
      - report
    total: "sum of all phases"
    threshold_warning: "p95 exceeded"

  tokens:
    phases:
      - classify_configure
      - discovery
      - analysis
      - synthesis
      - report
    total: "sum of all phases"
    threshold_warning: "budget exceeded"

  mcp_calls:
    servers:
      - auggie
      - serena
      - sequential
    total: "sum of all servers"
    efficiency: "results per call"
```

#### Performance Summary Format
```
Performance Summary
━━━━━━━━━━━━━━━━━━━
Phase           Latency    Tokens    MCP Calls
──────────────────────────────────────────────
Classify        1.2s       1,200     1 (Auggie)
Discovery       8.5s       4,800     5 (Auggie)
Analysis        15.3s      8,200     8 (Serena)
Synthesis       3.1s       1,500     2 (Sequential)
Report          0.8s       800       0
──────────────────────────────────────────────
Total           28.9s      16,500    16

Budget Usage: 16,500 / 20,000 (82.5%) ✓
Latency: 28.9s / 90s target (32.1%) ✓
```

#### Verification
```bash
# Test performance monitoring
uv run pytest tests/analyze/test_performance.py -v
```

---

### T5.4: Degradation Simulation Tests
**Type**: TEST
**Priority**: P3-Low
**Files Affected**:
- `tests/analyze/test_degradation.py`

#### Steps
1. Create fixtures for MCP unavailability simulation
2. Write tests for Auggie unavailability
3. Write tests for Serena unavailability
4. Write tests for Sequential unavailability
5. Write tests for full degradation
6. Write tests for recovery scenarios
7. Write tests for partial degradation

#### Acceptance Criteria
- [ ] Each MCP server unavailability tested
- [ ] Full degradation scenario tested
- [ ] Recovery notification tested
- [ ] Partial degradation combinations tested
- [ ] Output quality marking verified

#### Test Structure
```python
# tests/analyze/test_degradation.py
import pytest

class TestDegradationFeedback:

    def test_auggie_unavailable(self, mock_auggie_unavailable):
        """User sees semantic degradation message when Auggie down"""
        # Given Auggie MCP is unavailable
        # When analysis runs
        # Then user sees "⚠️ Semantic search unavailable"
        # And output marked as "REDUCED"
        pass

    def test_serena_unavailable(self, mock_serena_unavailable):
        """User sees validation degradation when Serena down"""
        pass

    def test_sequential_unavailable(self, mock_sequential_unavailable):
        """User sees reasoning degradation when Sequential down"""
        pass

    def test_full_degradation(self, mock_all_mcp_unavailable):
        """User sees full fallback message when all MCP down"""
        # Given all MCP servers unavailable
        # When analysis runs
        # Then user sees "🔴 Running in full fallback mode"
        # And output marked as "BASIC"
        pass

    def test_recovery_notification(self, mock_auggie_recovery):
        """User sees recovery notification when service restored"""
        pass

    @pytest.mark.parametrize("unavailable_servers", [
        ["auggie"],
        ["serena"],
        ["auggie", "serena"],
        ["serena", "sequential"],
    ])
    def test_partial_degradation_combinations(self, unavailable_servers):
        """Various partial degradation scenarios handled correctly"""
        pass
```

#### Verification
```bash
# Run degradation tests
uv run pytest tests/analyze/test_degradation.py -v
```

---

## Milestone Completion Checklist

- [ ] T5.1: Auggie Result Quality Scoring - completed
- [ ] T5.2: Real-Time Degradation Feedback - completed
- [ ] T5.3: Performance Monitoring Integration - completed
- [ ] T5.4: Degradation Simulation Tests - completed
- [ ] All verification commands pass
- [ ] Integration with M4 features verified
- [ ] Performance metrics baseline established
- [ ] Memory checkpoint saved

## Checkpoint Command
```
mcp__serena__write_memory("analyze-auggie-m5", {
  status: "completed",
  deliverables: ["M5-D1", "M5-D2", "M5-D3", "M5-D4"],
  roi_delivered: [5.53, 5.42],
  quality_scoring: "implemented",
  degradation_feedback: "real-time",
  performance_monitoring: "active",
  issues: [],
  verified: true
})
```

---

*Tasklist M5 - Generated by SuperClaude Roadmap Generator v1.0*
