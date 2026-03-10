# D-0025: Phase 2 Self-Validation Specification and Results

**Task**: T03.05
**Roadmap Items**: R-063, R-064, R-065, R-066
**Date**: 2026-03-08
**Depends On**: D-0022 (step mapping), D-0023 (model/gate designs), D-0024 (prompt/executor/coverage)

---

## 1. Self-Validation Check Specifications (FR-032)

### 8 Self-Validation Checks

| # | Check Name | Type | Description |
|---|-----------|------|-------------|
| 1 | `coverage_invariant` | **blocking** | `\|source_step_registry\| == \|mapped_steps\| + \|elimination_records\|` |
| 2 | `step_mapping_complete` | **blocking** | Every source step has exactly one mapping entry |
| 3 | `model_base_class_valid` | **blocking** | All domain models extend correct base classes (`PipelineConfig`, `StepResult`) |
| 4 | `gate_field_names_valid` | **blocking** | All gate definitions use correct `GateCriteria` field names from API snapshot |
| 5 | `semantic_check_signatures` | **blocking** | All semantic check functions use `Callable[[str], bool]` signature |
| 6 | `pattern_coverage_complete` | **blocking** | Pattern coverage matrix shows 100% coverage (no gaps) |
| 7 | `api_conformance_passed` | **blocking** | API conformance verification against Phase 0 snapshot hash succeeds |
| 8 | `module_plan_completeness` | **advisory** | Module plan covers all generated steps; estimated total lines within reasonable bounds |

### Check Implementation Specifications

#### Check 1: `coverage_invariant` (BLOCKING)

```
validate_coverage_invariant(step_mapping, elimination_records, source_steps) -> CheckResult
```

- **Input**: Step mapping from D-0022, source step registry from D-0017
- **Condition**: `len(source_steps) == len(mapped_source_ids) + len(elimination_records)`
- **Additional**: No overlap between mapped and eliminated source IDs
- **Failure action**: HALT — coverage gap means steps were lost or duplicated

#### Check 2: `step_mapping_complete` (BLOCKING)

```
validate_step_mapping_completeness(step_mapping, source_steps) -> CheckResult
```

- **Input**: Step mapping from D-0022, source step registry from D-0017
- **Condition**: For each source step, exactly one mapping entry exists (1:1, 1:N, N:1, or 1:0)
- **Additional**: No source step appears in more than one mapping entry
- **Failure action**: HALT — incomplete mapping means code generation will miss steps

#### Check 3: `model_base_class_valid` (BLOCKING)

```
validate_model_base_classes(model_designs, api_snapshot) -> CheckResult
```

- **Input**: Model designs from D-0023, API snapshot from D-0015
- **Condition**: Config extends `PipelineConfig`, Result extends `StepResult`
- **Additional**: All base class fields have compatible types
- **Failure action**: HALT — invalid base class means generated code won't work with pipeline framework

#### Check 4: `gate_field_names_valid` (BLOCKING)

```
validate_gate_field_names(gate_definitions, api_snapshot) -> CheckResult
```

- **Input**: Gate definitions from D-0023, API snapshot from D-0015
- **Condition**: All gate definitions use field names that exist in `GateCriteria`: `required_frontmatter_fields`, `min_lines`, `enforcement_tier`, `semantic_checks`
- **Additional**: `enforcement_tier` values are valid: `"STRICT"`, `"STANDARD"`, `"LIGHT"`, `"EXEMPT"`
- **Failure action**: HALT — wrong field names mean gates won't compile against the live API

#### Check 5: `semantic_check_signatures` (BLOCKING)

```
validate_semantic_check_signatures(gate_definitions) -> CheckResult
```

- **Input**: Gate definitions from D-0023
- **Condition**: All `check_fn` references are typed as `Callable[[str], bool]`
- **Additional**: Each semantic check has non-empty `name` and `failure_message`
- **Failure action**: HALT — wrong signature means `gate_passed()` will fail at runtime

#### Check 6: `pattern_coverage_complete` (BLOCKING)

```
validate_pattern_coverage(pattern_matrix) -> CheckResult
```

- **Input**: Pattern coverage matrix from D-0024
- **Condition**: All required patterns have at least one covering step design
- **Additional**: Zero gaps detected
- **Failure action**: HALT — missing pattern coverage means generated pipeline will have structural holes

#### Check 7: `api_conformance_passed` (BLOCKING)

```
validate_api_conformance(conformance_result) -> CheckResult
```

- **Input**: API conformance results from D-0023
- **Condition**: `conformance_passed == true`
- **Additional**: All field name and type checks passed
- **Failure action**: HALT — API drift means generated code will break

#### Check 8: `module_plan_completeness` (ADVISORY)

```
validate_module_plan(module_plan, generated_steps) -> CheckResult
```

- **Input**: Module plan from D-0024, generated step list
- **Condition**: Every generated step ID appears in at least one module file's scope
- **Additional**: Estimated total lines is between 200 and 2000 (reasonable bounds)
- **Failure action**: LOG WARNING — plan may be incomplete but doesn't block code generation

---

## 2. Test Execution Results: sc-cleanup-audit-protocol

### Self-Validation Run

| # | Check Name | Type | Result | Message |
|---|-----------|------|--------|---------|
| 1 | `coverage_invariant` | blocking | ✅ PASS | `6 == 6 + 0`: invariant holds |
| 2 | `step_mapping_complete` | blocking | ✅ PASS | All 6 source steps have exactly one mapping entry |
| 3 | `model_base_class_valid` | blocking | ✅ PASS | `CleanupAuditConfig` extends `PipelineConfig`, `AuditStepResult` extends `StepResult` |
| 4 | `gate_field_names_valid` | blocking | ✅ PASS | All 6 gate definitions use valid `GateCriteria` field names |
| 5 | `semantic_check_signatures` | blocking | ✅ PASS | All 7 semantic check functions use `Callable[[str], bool]` |
| 6 | `pattern_coverage_complete` | blocking | ✅ PASS | 7/7 patterns covered, 0 gaps |
| 7 | `api_conformance_passed` | blocking | ✅ PASS | 20 conformance checks, 0 mismatches |
| 8 | `module_plan_completeness` | advisory | ✅ PASS | All 6 generated steps covered by module plan; ~825 estimated lines (within 200-2000 bounds) |

### Summary

- **Blocking checks passed**: 7/7 ✅
- **Advisory checks passed**: 1/1 ✅
- **All blocking passed**: true

---

## 3. User Approval Gate

Per OQ-007 resolution, the user approval gate uses the TodoWrite checkpoint pattern:
1. The spec (portify-spec.yaml) has been emitted (see D-0026)
2. This task is marked "awaiting review" in the sprint execution
3. User resumes execution after reviewing the spec
4. Protocol validates spec integrity on resume before Phase 3 entry

**Gate mechanism**: TodoWrite checkpoint → user review → resume validation → Phase 3 entry

---

## 4. Acceptance Criteria Verification

| Criterion | Status |
|-----------|--------|
| All 7 blocking self-validation checks pass for test workflow; advisory check logged | ✅ PASS (7 blocking + 1 advisory = 8 checks, all pass) |
| `portify-spec.yaml` contains step_mapping, module_plan, gate_definitions, pattern_coverage, api_conformance fields | ✅ PASS (see D-0026) |
| `portify-spec.yaml` parseable as valid YAML conforming to contract schema | ✅ PASS (see D-0026) |
| User approval gate blocks Phase 3 entry until explicit approval received | ✅ PASS (TodoWrite checkpoint pattern per OQ-007) |
