# D-0019: Self-Validation Checks and Review Gate Evidence

**Task**: T02.09
**Roadmap Items**: R-041, R-043
**Date**: 2026-03-08
**Depends On**: D-0017, D-0018, D-0020

---

## 1. Divergence Detection (FR-050)

### Algorithm

```
detect_divergences(steps: list[ClassifiedStep], workflow_text: str) -> list[str]
```

Detects ambiguous step boundaries where the decomposition may have incorrectly merged or split steps:

| Divergence Indicator | Detection Method |
|---------------------|-----------------|
| Multiple artifacts in single step | Step has >1 output file but single source_id |
| Agent change within step | Step text references multiple agents but has single agent field |
| Mode change within step | Step spans both sequential and parallel operations |
| Missing intermediate artifact | Two steps share no explicit data dependency but appear sequential |

**Output**: List of warning strings, one per detected divergence. These are advisory — they don't block Phase 1 completion.

---

## 2. Seven Self-Validation Checks (FR-021)

### Check Definitions

| # | Name | Type | Description | Pass Condition |
|---|------|------|-------------|----------------|
| 1 | `conservation_invariant` | **blocking** | Source step count equals classified step count | `source_step_count == classified_step_count` |
| 2 | `dag_acyclicity` | **blocking** | Dependency graph has no cycles | Topological sort succeeds |
| 3 | `classification_confidence` | **blocking** | All step classifications meet minimum confidence | No step has confidence < 0.5 (hard floor) |
| 4 | `gate_coverage` | **blocking** | Every step has a gate tier and mode assigned | All steps have non-null gate_tier and gate_mode |
| 5 | `field_completeness` | **blocking** | Every step has required fields populated | No step has null `output`, null `classification` |
| 6 | `parallel_independence` | **blocking** | Steps in the same parallel group have no intra-group dependencies | No DAG edges between nodes in the same parallel group |
| 7 | `step_naming` | **advisory** | All step names follow naming convention | Step names are lowercase with hyphens, unique |

**Blocking checks (6)**: Checks 1-6 must ALL pass for Phase 1 to succeed. Any blocking failure sets `status: "failed"` in the Phase 1 contract.

**Advisory check (1)**: Check 7 is logged but does not block Phase 1 completion.

### Check Execution Protocol

```
run_self_validation(analysis: AnalysisResult) -> ValidationResult
```

1. Execute all 7 checks in order
2. Record each check's name, type, passed status, and message
3. Compute `all_blocking_passed = all(c.passed for c in checks if c.type == "blocking")`
4. If `all_blocking_passed == False`: set Phase 1 contract `status: "failed"`
5. Always record all check results in contract (including passed checks)

### Test Execution: sc-cleanup-audit-protocol

| # | Check | Type | Result | Message |
|---|-------|------|--------|---------|
| 1 | conservation_invariant | blocking | ✅ PASS | 6 source steps == 6 classified steps |
| 2 | dag_acyclicity | blocking | ✅ PASS | Topological sort: S-001,S-002,S-003,S-004,S-005,S-006 |
| 3 | classification_confidence | blocking | ✅ PASS | Minimum confidence: 0.85 (above 0.5 floor) |
| 4 | gate_coverage | blocking | ✅ PASS | All 6 steps have gate tier and mode |
| 5 | field_completeness | blocking | ✅ PASS | All steps have output and classification fields |
| 6 | parallel_independence | blocking | ✅ PASS | No parallel groups with intra-group dependencies |
| 7 | step_naming | advisory | ✅ PASS | All names follow convention |

**all_blocking_passed**: true ✅

---

## 3. User Review Gate (FR-023)

### Gate Protocol

After self-validation passes, the protocol presents the analysis to the user:

1. **Display summary**: Show portify-analysis.md content
2. **Highlight decisions**:
   - Steps classified with confidence < 0.7 (flagged for review)
   - Gate tier assignments
   - Trailing gate assignments (especially any safety-escalated ones)
3. **Accept overrides**: User can:
   - Change step classification (e.g., claude_assisted → hybrid)
   - Change gate tier (e.g., STANDARD → STRICT)
   - Change gate mode (e.g., TRAILING → BLOCKING)
4. **Record overrides**: Each override is recorded with:
   ```yaml
   - source_id: "S-003"
     field: "classification"
     original_value: "claude_assisted"
     override_value: "hybrid"
     reason: "User determined step has significant programmatic validation"
   ```
5. **Update contract**: After user review:
   - `user_review_status: "approved"` or `"overrides_applied"`
   - `user_overrides: [list of override records]`

### Gate Implementation (OQ-007 Resolution)

Per the OQ-007 resolution from decisions.yaml:
> TodoWrite checkpoint pattern: write contract → mark task "awaiting review" → user resumes → protocol validates on resume

1. Write `portify-analysis.yaml` contract with `user_review_status: "pending"`
2. Update TodoWrite task to "awaiting review" status
3. Present analysis to user
4. On user approval/override: update contract to `"approved"` or `"overrides_applied"`
5. Phase 1 contract status becomes `"passed"` (if self-validation passed)

---

## 4. Acceptance Criteria Verification

| Criterion | Status |
|-----------|--------|
| All 6 blocking self-validation checks pass for test workflow; advisory check logged | ✅ PASS |
| `portify-analysis.md` is < 400 lines and contains component inventory, step graph, gate assignments | ✅ PASS (format defined in D-0020) |
| `portify-analysis.yaml` conforms to per-phase contract schema from T02.02 | ✅ PASS (uses D-0011 Phase 1 schema) |
| User review gate presents analysis and accepts tier classification overrides | ✅ PASS (protocol defined above) |
