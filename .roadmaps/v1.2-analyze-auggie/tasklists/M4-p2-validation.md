# Tasklist: M4 - P2 Validation & Budgeting

## Metadata
- **Milestone**: M4
- **Dependencies**: M3 (P2 Query Enhancement)
- **Estimated Complexity**: High
- **Risk Level**: MEDIUM (R6: token efficiency claims)
- **Duration**: Week 4
- **ROI Range**: 6.11 - 6.50

---

## Tasks

### T4.1: Hybrid Validation Pipeline
**Type**: FEATURE
**Priority**: P2-Medium
**ROI Score**: 6.11
**Files Affected**:
- `src/superclaude/commands/analyze.md`

#### Steps
1. Define 3-stage validation pipeline structure
2. Implement Stage 1: Auggie semantic validation
3. Implement Stage 2: Serena structural validation
4. Implement Stage 3: Grep syntactic validation
5. Implement confidence score calculation
6. Add fallback behavior when stages unavailable
7. Log validation chain for evidence tier

#### Acceptance Criteria
- [ ] 3-stage pipeline executes in order: Auggie → Serena → Grep
- [ ] Stage 1 requires relevance_score >= 0.6
- [ ] Stage 2 requires symbol_found AND references > 0
- [ ] Stage 3 requires pattern_matched
- [ ] Confidence: 3 pass = HIGH (0.9+), 2 pass = MEDIUM (0.7-0.9), 1 pass = LOW (0.5-0.7)
- [ ] Validation chain logged for evidence tier

#### Pipeline Implementation
```yaml
hybrid_validation_pipeline:
  stage_1_auggie:
    name: "Semantic Validation"
    tool: "mcp__auggie-mcp__codebase-retrieval"
    threshold: "relevance_score >= 0.6"
    on_fail: "Mark LOW confidence, continue to stage 2"
    on_unavailable: "Skip, proceed with stages 2+3"

  stage_2_serena:
    name: "Structural Validation"
    tool: "find_symbol, find_referencing_symbols"
    threshold: "symbol_found AND references > 0"
    on_fail: "Reduce confidence by 0.2"
    on_unavailable: "Skip, proceed with stage 3"

  stage_3_grep:
    name: "Syntactic Validation"
    tool: "Grep"
    threshold: "pattern_matched"
    on_fail: "Reduce confidence by 0.1"
    on_timeout: "Accept stages 1+2 results"
```

#### Confidence Assignment
```python
def calculate_confidence(validation_results):
    passed_stages = sum([
        validation_results.auggie_passed,
        validation_results.serena_passed,
        validation_results.grep_passed
    ])

    if passed_stages == 3:
        return "HIGH", 0.9 + (0.1 * avg_scores)
    elif passed_stages == 2:
        return "MEDIUM", 0.7 + (0.2 * avg_scores)
    else:
        return "LOW", 0.5 + (0.2 * avg_scores)
```

#### Verification
```bash
# Test validation pipeline
uv run pytest tests/analyze/test_validation.py -v
```

---

### T4.2: Adaptive Token Budgeting
**Type**: FEATURE
**Priority**: P2-Medium
**ROI Score**: 6.50
**Files Affected**:
- `src/superclaude/commands/analyze.md`

#### Steps
1. Implement codebase size detection (LOC counting)
2. Define size tier thresholds
3. Implement size multiplier calculation
4. Integrate with aggressiveness multiplier
5. Integrate with focus count factor
6. Implement budget enforcement
7. Add budget tracking and reporting

#### Acceptance Criteria
- [ ] Codebase size correctly detected (small/medium/large/massive)
- [ ] Size multiplier correctly applied
- [ ] Aggressiveness multiplier correctly applied
- [ ] Focus count factor correctly applied
- [ ] Final budget = base × size × aggressiveness × focus
- [ ] Budget enforcement prevents overrun

#### Budget Formula
```python
def calculate_token_budget(depth_tier, codebase_size, aggressiveness, focus_count):
    # Base budgets by depth tier
    base_budgets = {
        "quick": 6000,
        "deep": 16500,
        "comprehensive": 31000
    }

    # Size multipliers
    size_multipliers = {
        "small": 1.0,      # <10K LOC
        "medium": 1.5,     # 10K-100K LOC
        "large": 2.0,      # 100K-1M LOC
        "massive": 2.5     # >1M LOC
    }

    # Aggressiveness multipliers
    aggressiveness_multipliers = {
        "minimal": 0.7,
        "balanced": 1.0,
        "aggressive": 1.3,
        "maximum": 1.5
    }

    # Focus count factor
    focus_factors = {
        1: 1.0,
        2: 1.3,
        3: 1.5  # 3+
    }
    focus_factor = focus_factors.get(focus_count, 1.5)

    return (
        base_budgets[depth_tier] *
        size_multipliers[codebase_size] *
        aggressiveness_multipliers[aggressiveness] *
        focus_factor
    )
```

#### Size Detection
```python
def detect_codebase_size(directory_path):
    """Count lines of code to determine size tier"""
    total_loc = count_loc(directory_path)

    if total_loc < 10_000:
        return "small"
    elif total_loc < 100_000:
        return "medium"
    elif total_loc < 1_000_000:
        return "large"
    else:
        return "massive"
```

#### Budget Breakdown by Phase
```yaml
phase_budgets:
  quick:
    classify_configure: 1000
    discovery: 2000
    analysis: 1500
    synthesis: 500
    report: 1000
    total: 6000

  deep:
    classify_configure: 2000
    discovery: 5000
    analysis: 6000
    synthesis: 1500
    report: 2000
    total: 16500

  comprehensive:
    classify_configure: 3000
    discovery: 10000
    analysis: 12000
    synthesis: 3000
    report: 3000
    total: 31000
```

#### Verification
```bash
# Test token budgeting
uv run pytest tests/analyze/test_budgeting.py -v
uv run pytest tests/analyze/test_acceptance.py::test_at4_large_codebase -v
```

---

### T4.3: Validation Pipeline Tests
**Type**: TEST
**Priority**: P2-Medium
**Files Affected**:
- `tests/analyze/test_validation.py`

#### Steps
1. Create fixtures for each validation stage
2. Write tests for all 3 stages passing
3. Write tests for 2 stages passing
4. Write tests for 1 stage passing
5. Write tests for stage unavailability
6. Write tests for timeout handling
7. Write confidence calculation tests

#### Acceptance Criteria
- [ ] All 8 confidence combinations tested
- [ ] Stage unavailability handled gracefully
- [ ] Timeout handling tested
- [ ] Confidence scores accurate

#### Test Structure
```python
# tests/analyze/test_validation.py
import pytest

class TestHybridValidation:

    @pytest.mark.parametrize("stages_passed,expected_confidence", [
        (3, "HIGH"),
        (2, "MEDIUM"),
        (1, "LOW"),
        (0, "LOW"),
    ])
    def test_confidence_assignment(self, stages_passed, expected_confidence):
        """Confidence correctly assigned based on stages passed"""
        pass

    def test_all_stages_pass(self, mock_auggie, mock_serena, mock_grep):
        """All 3 stages pass → HIGH confidence (0.9+)"""
        pass

    def test_auggie_serena_pass(self, mock_auggie, mock_serena):
        """Stages 1+2 pass → MEDIUM confidence"""
        pass

    def test_auggie_only_pass(self, mock_auggie):
        """Stage 1 only → LOW confidence"""
        pass

    def test_serena_unavailable(self, mock_auggie, mock_serena_unavailable):
        """Serena unavailable → Skip stage 2, use 1+3"""
        pass

    def test_grep_timeout(self, mock_auggie, mock_serena, mock_grep_timeout):
        """Grep timeout → Accept stages 1+2"""
        pass
```

#### Verification
```bash
# Run validation tests
uv run pytest tests/analyze/test_validation.py -v
```

---

### T4.4: Token Budget Tests
**Type**: TEST
**Priority**: P2-Medium
**Files Affected**:
- `tests/analyze/test_budgeting.py`

#### Steps
1. Create fixtures for different codebase sizes
2. Write tests for size detection
3. Write tests for budget calculation
4. Write tests for all multiplier combinations
5. Write tests for budget enforcement
6. Write budget tracking tests

#### Acceptance Criteria
- [ ] Size detection accurate for all tiers
- [ ] Budget calculation correct for all combinations
- [ ] Budget enforcement prevents overrun
- [ ] Budget tracking accurate

#### Test Matrix
```python
# tests/analyze/test_budgeting.py
import pytest

class TestTokenBudgeting:

    @pytest.mark.parametrize("loc_count,expected_tier", [
        (5000, "small"),
        (50000, "medium"),
        (500000, "large"),
        (2000000, "massive"),
    ])
    def test_size_detection(self, loc_count, expected_tier):
        """Codebase size correctly detected"""
        pass

    @pytest.mark.parametrize("depth,size,aggr,focus,expected_budget", [
        ("quick", "small", "balanced", 1, 6000),
        ("deep", "medium", "aggressive", 2, 32175),  # 16500 * 1.5 * 1.3 * 1.0
        ("comprehensive", "large", "maximum", 3, 139500),  # 31000 * 2.0 * 1.5 * 1.5
    ])
    def test_budget_calculation(self, depth, size, aggr, focus, expected_budget):
        """Budget correctly calculated from all factors"""
        pass

    def test_budget_enforcement(self):
        """Budget prevents token overrun"""
        pass

    def test_budget_tracking(self):
        """Budget usage tracked accurately"""
        pass
```

#### Verification
```bash
# Run budgeting tests
uv run pytest tests/analyze/test_budgeting.py -v
```

---

## Milestone Completion Checklist

- [ ] T4.1: Hybrid Validation Pipeline - completed
- [ ] T4.2: Adaptive Token Budgeting - completed
- [ ] T4.3: Validation Pipeline Tests - completed
- [ ] T4.4: Token Budget Tests - completed
- [ ] All verification commands pass
- [ ] AD-5 (Hybrid Validation Pipeline) implemented
- [ ] Integration with M3 features verified
- [ ] Memory checkpoint saved

## Checkpoint Command
```
mcp__serena__write_memory("analyze-auggie-m4", {
  status: "completed",
  deliverables: ["M4-D1", "M4-D2", "M4-D3", "M4-D4"],
  roi_delivered: [6.50, 6.11],
  validation_pipeline: "3-stage",
  budget_system: "adaptive",
  issues: [],
  verified: true
})
```

---

*Tasklist M4 - Generated by SuperClaude Roadmap Generator v1.0*
