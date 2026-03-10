# D-0012: Contract Validation and Resume Protocol Specification

**Task**: T02.03
**Roadmap Items**: R-022, R-023, R-024, R-025
**Date**: 2026-03-08
**Depends On**: D-0010 (versioning policy), D-0011 (per-phase schemas)

---

## 1. Contract Validation Logic

### Interface

```
validate_contract(contract_path: str, expected_phase: int) -> ValidatedContract | ContractError
```

### Validation Steps

On reading an incoming contract, the validator performs these checks in order:

#### Step 1: File Existence and Parse
- Verify file exists at `contract_path`
- Parse YAML content
- On parse failure: return `ContractError("YAML_PARSE_FAILED", path, details)`

#### Step 2: Common Header Validation
- Verify `schema_version` field exists and is a string matching `"MAJOR.MINOR"` pattern
- Verify `phase` field exists and equals `expected_phase - 1` (the producing phase)
- Verify `status` field exists and is one of: `"passed"`, `"failed"`, `"skipped"`
- Verify `timestamp` field exists and is a valid ISO 8601 string
- Verify `resume_checkpoint` field exists and is a non-empty string
- Verify `validation_status` object exists with `blocking_passed`, `blocking_failed`, `advisory` sub-fields

#### Step 3: Schema Version Compatibility
- Parse `schema_version` into MAJOR and MINOR integers
- Compare against expected version (currently "1.0"):
  - Same MAJOR, any MINOR: **compatible** (proceed)
  - Different MAJOR: **incompatible** (abort)
- On incompatible version:
  ```
  ContractError(
    code="CONTRACT_VERSION_MISMATCH",
    message="Expected schema_version 1.x, got {actual}. "
            "Phase {expected_phase - 1} contract at {path} was produced by an incompatible schema version. "
            "Action: Re-run Phase {expected_phase - 1} to regenerate the contract with schema version 1.x."
  )
  ```

#### Step 4: Required Field Presence (Phase-Specific)
- Load the expected field set for the contract's phase from the schema registry (D-0011)
- For each required field:
  - Verify field key exists in parsed YAML
  - `null` values are allowed (per null-field policy from D-0010)
  - Missing keys are NOT allowed
- On missing required fields:
  ```
  ContractError(
    code="MISSING_REQUIRED_FIELDS",
    message="Contract at {path} is missing required fields: {missing_fields}. "
            "Action: Re-run Phase {phase} to regenerate the contract."
  )
  ```

#### Step 5: Status Enum Validation
- Verify `status` is one of the allowed values: `"passed"`, `"failed"`, `"skipped"`
- Verify `phase` is in range 0-4 (or -1 for return contract)

#### Step 6: Blocking Failure Check
- If `status == "failed"` AND `validation_status.blocking_failed > 0`:
  - Return validated contract with `can_proceed = False`
  - Include failure details for downstream decision-making

### Output

```
ValidatedContract:
  data: dict              # Parsed and validated contract data
  schema_version: str     # Parsed version
  phase: int              # Producing phase
  status: str             # "passed" | "failed" | "skipped"
  can_proceed: bool       # True if consuming phase should proceed
  warnings: list[str]     # Advisory warnings (e.g., higher minor version)
```

---

## 2. Return Contract Assembly

### Interface

```
assemble_return_contract(phase_contracts: dict[int, ValidatedContract], pipeline_state: PipelineState) -> dict
```

### Assembly Logic

1. **Determine overall status**:
   - If all phases passed: `status = "passed"`
   - If any phase failed: `status = "failed"`
   - If pipeline was halted before completion: `status = "failed"`

2. **Identify failure information**:
   - `failure_phase`: Phase number where first failure occurred, `null` if passed
   - `failure_type`: Classification of failure, `null` if passed
     - `"validation_failed"`: Self-validation check failed
     - `"gate_failed"`: Gate validation failed
     - `"unsupported_pattern"`: Phase 0 detected unsupported pattern
     - `"collision"`: Output directory collision detected
     - `"generation_error"`: Code generation failed
     - `"integration_error"`: main.py patching or smoke test failed

3. **Aggregate generated files**:
   - Collect all file paths from Phase 3 `generated_files` and Phase 4 outputs
   - Include `portify-analysis.md`, `portify-spec.md`, `portify-summary.md` if they exist

4. **Compute counts**:
   - `total_steps`: From Phase 1 `step_graph` length
   - `programmatic_steps`: Count where `classification == "pure_programmatic"`
   - `claude_assisted_steps`: Count where `classification == "claude_assisted"`
   - `hybrid_steps`: Count where `classification == "hybrid"`
   - `files_generated`: From Phase 3 `generated_files` length
   - `gates_passed` / `gates_failed`: From Phase 3 validation results

5. **Populate remaining fields**:
   - `api_snapshot_hash`: From Phase 0 `api_snapshot.content_hash`
   - `resume_command`: Generated from failure point if failed, `null` if passed
   - `warnings`: Aggregated from all `validation_status.advisory` lists
   - `phase_contracts`: Embed each phase contract (or `null` if phase not reached)

6. **Apply null-field policy**: Any field not computable (because a phase wasn't reached) is set to `null`

### Return Contract Emission

The return contract is ALWAYS emitted, even on failure. This ensures:
- Callers always get structured output
- Resume information is always available
- Partial results are preserved

---

## 3. Resume Protocol

### Interface

```
resume_pipeline(resume_checkpoint: str, contract_dir: str) -> ResumeResult
```

### Resume Flow

#### Step 1: Read Latest Contract State
- Scan `contract_dir` for all `portify-*.yaml` files
- Parse each contract and build phase completion map:
  ```
  phase_state = {
    0: ValidatedContract | None,
    1: ValidatedContract | None,
    2: ValidatedContract | None,
    3: ValidatedContract | None,
    4: ValidatedContract | None,
  }
  ```

#### Step 2: Parse Resume Checkpoint
- Parse `resume_checkpoint` format: `"phase-{N}:{step}"`
- Extract target phase number and step within that phase
- Validate: target phase must be >= 0 and <= 4

#### Step 3: Validate Completed Phase Contracts
- For each phase BEFORE the target phase (phase < target):
  - If contract exists: re-validate using `validate_contract()`
  - If contract is missing: error — cannot resume without prior phase output
  - If contract fails re-validation: error — prior phase output is corrupt
  - **Contracts are NOT blindly trusted on resume** — they are re-validated

#### Step 4: Determine Resume Entry Point
- Skip all phases with `status == "passed"` AND valid contracts
- Resume at `target_phase` from the specified step
- If the target phase's contract exists with `status == "failed"`:
  - Re-execute from the beginning of that phase (not the failed step within it)
  - Rationale: partial phase state may be inconsistent

#### Step 5: Verify Filesystem Consistency
- If Phase 0 contract exists, verify `api_snapshot.content_hash` still matches the live snapshot
- If hash mismatch: warn that API may have changed since original run
  - Advisory warning, not blocking (user may have intentionally updated API)

### Output

```
ResumeResult:
  resume_from_phase: int           # Phase to resume from
  validated_prior_contracts: dict   # Re-validated prior phase contracts
  warnings: list[str]             # Advisory warnings (e.g., API hash mismatch)
  can_resume: bool                # True if resume is possible
  error: str | None               # Error message if resume is not possible
```

### Resume Error Cases

| Error | Cause | Action |
|-------|-------|--------|
| `NO_CONTRACTS_FOUND` | No portify-*.yaml in contract_dir | Start from Phase 0 |
| `PRIOR_CONTRACT_MISSING` | Phase N-1 contract missing | Re-run from Phase N-1 |
| `PRIOR_CONTRACT_CORRUPT` | Phase N-1 contract fails re-validation | Re-run from Phase N-1 |
| `INVALID_CHECKPOINT` | resume_checkpoint format invalid | Report error |
| `PHASE_OUT_OF_RANGE` | Target phase > 4 or < 0 | Report error |

---

## 4. Contract Error Codes

| Code | Meaning | Severity |
|------|---------|----------|
| `YAML_PARSE_FAILED` | Contract file is not valid YAML | Blocking |
| `CONTRACT_VERSION_MISMATCH` | Major version incompatible | Blocking |
| `MISSING_REQUIRED_FIELDS` | Required fields absent from contract | Blocking |
| `INVALID_STATUS_ENUM` | Status field has invalid value | Blocking |
| `INVALID_PHASE_NUMBER` | Phase number out of range | Blocking |
| `PRIOR_CONTRACT_MISSING` | Resume needs prior contract that doesn't exist | Blocking |
| `PRIOR_CONTRACT_CORRUPT` | Prior contract fails re-validation | Blocking |
| `API_HASH_MISMATCH` | API snapshot hash changed since original run | Advisory |
| `HIGHER_MINOR_VERSION` | Contract has higher minor version than expected | Advisory |
