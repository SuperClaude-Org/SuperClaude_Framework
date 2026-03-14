# Agent 1 Artifact Research — v2.24-cli-portify-cli-v4 Roadmap Pipeline

**Investigation date**: 2026-03-13
**Agent role**: Root Cause Analyst — evidence collection and pipeline state documentation
**Scope**: Roadmap generation pipeline stages, state persistence, resume behavior, spec-fidelity failure

---

## 1. Roadmap Pipeline Summary — What It Does

The `superclaude roadmap run` CLI orchestrates an 11-step pipeline that generates a validated release roadmap from a spec file. Each step runs as a fresh Claude subprocess with no shared session state. File-on-disk artifacts act as gates between steps.

**Source**: `src/superclaude/cli/roadmap/executor.py`, `src/superclaude/cli/roadmap/commands.py`

### Pipeline Stages (in order)

| # | Step ID | Output File | Gate Tier | Parallel? |
|---|---------|-------------|-----------|-----------|
| 1 | `extract` | `extraction.md` | STRICT | No |
| 2a | `generate-{agent_a.id}` | `roadmap-{agent_a.id}.md` | STRICT | Yes (parallel with 2b) |
| 2b | `generate-{agent_b.id}` | `roadmap-{agent_b.id}.md` | STRICT | Yes (parallel with 2a) |
| 3 | `diff` | `diff-analysis.md` | STANDARD | No |
| 4 | `debate` | `debate-transcript.md` | STANDARD | No |
| 5 | `score` | `base-selection.md` | STANDARD | No |
| 6 | `merge` | `roadmap.md` | STRICT | No |
| 7 | `test-strategy` | `test-strategy.md` | STANDARD | No |
| 8 | `spec-fidelity` | `spec-fidelity.md` | STRICT | No |
| 9 | `remediate` | `remediation-tasklist.md` | STRICT | No (post-pipeline) |
| 10 | `certify` | `certification-report.md` | STRICT | No (post-pipeline) |

Steps 1-8 are built by `_build_steps()` and run via `execute_pipeline()`. Steps 9 (`remediate`) and 10 (`certify`) are part of the full step ID list tracked in `_get_all_step_ids()` but are separate post-pipeline phases invoked by the remediate and certify subsystems.

After steps 1-8 complete successfully, auto-validation runs via `_auto_invoke_validate()` unless `--no-validate` is passed.

### Gate Enforcement Tiers

Gates are evaluated by `gate_passed()` in `src/superclaude/cli/pipeline/gates.py`:

- **EXEMPT**: Always passes (no file check).
- **LIGHT**: File must exist and be non-empty.
- **STANDARD**: File exists + non-empty + minimum line count + required YAML frontmatter fields.
- **STRICT**: All STANDARD checks + semantic check functions (custom logic).

The `spec-fidelity` step uses `SPEC_FIDELITY_GATE` which is STRICT and requires:
- Required frontmatter fields: `high_severity_count`, `medium_severity_count`, `low_severity_count`, `total_deviations`, `validation_complete`, `tasklist_ready`
- Semantic check `high_severity_count_zero`: `high_severity_count` must equal 0
- Semantic check `tasklist_ready_consistent`: `tasklist_ready: true` must be consistent with zero high-severity count and `validation_complete: true`

---

## 2. State Persistence Mechanism

State is persisted to `.roadmap-state.json` in the output directory via `_save_state()` and read via `read_state()`, both in `executor.py`.

**Write path**: atomic — content is written to a `.tmp` file, then `os.replace()` is called to atomically replace the state file. This prevents partial-write corruption.

**State schema** (`schema_version: 1`):

```
{
  "schema_version": 1,
  "spec_file": "<absolute path to spec>",
  "spec_hash": "<sha256 of spec file bytes>",
  "agents": [{"model": "...", "persona": "..."}],
  "depth": "quick|standard|deep",
  "last_run": "<ISO 8601 UTC timestamp>",
  "steps": {
    "<step_id>": {
      "status": "PASS|FAIL|TIMEOUT|CANCELLED|SKIPPED",
      "attempt": <int>,
      "output_file": "<absolute path>",
      "started_at": "<ISO 8601>",
      "completed_at": "<ISO 8601>"
    }
  },
  "fidelity_status": "pass|fail|skipped|degraded",
  "validation": {"status": "pass|fail|skipped", "timestamp": "..."},
  "remediate": {...},  // present only after remediate phase
  "certify": {...}     // present only after certify phase
}
```

State is written once after the main pipeline finishes (`_save_state(config, results)`). The `validation`, `remediate`, and `certify` keys are preserved across state rewrites — `_save_state()` reads the existing state and carries those keys forward if not being explicitly updated.

`fidelity_status` is derived from the spec-fidelity step result:
- `PASS` + `validation_complete: false` in output → `"degraded"`
- `PASS` (normal) → `"pass"`
- `SKIPPED` → `"skipped"`
- `FAIL` or `TIMEOUT` → `"fail"`

---

## 3. Current State of `.roadmap-state.json` (Full Contents)

```json
{
  "schema_version": 1,
  "spec_file": "/config/workspace/IronClaude/.dev/releases/current/v2.24-cli-portify-cli-v4/portify-release-spec.md",
  "spec_hash": "3d1a6d1581bd8352ace0f80faf845b1131b8df36b3fe7e458e299a7647dfbaa9",
  "agents": [
    {"model": "opus", "persona": "architect"},
    {"model": "haiku", "persona": "architect"}
  ],
  "depth": "standard",
  "last_run": "2026-03-13T04:16:42.439743+00:00",
  "steps": {
    "extract":                  {"status": "PASS", "attempt": 1, "output_file": ".../extraction.md",           "started_at": "03:48:10", "completed_at": "03:50:12"},
    "generate-opus-architect":  {"status": "PASS", "attempt": 1, "output_file": ".../roadmap-opus-architect.md","started_at": "03:50:12", "completed_at": "03:51:53"},
    "generate-haiku-architect": {"status": "PASS", "attempt": 1, "output_file": ".../roadmap-haiku-architect.md","started_at": "03:50:12", "completed_at": "03:52:10"},
    "diff":                     {"status": "PASS", "attempt": 1, "output_file": ".../diff-analysis.md",        "started_at": "03:52:10", "completed_at": "03:53:21"},
    "debate":                   {"status": "PASS", "attempt": 1, "output_file": ".../debate-transcript.md",    "started_at": "03:53:21", "completed_at": "03:56:56"},
    "score":                    {"status": "PASS", "attempt": 1, "output_file": ".../base-selection.md",       "started_at": "03:56:56", "completed_at": "04:03:08"},
    "merge":                    {"status": "PASS", "attempt": 1, "output_file": ".../roadmap.md",              "started_at": "04:03:08", "completed_at": "04:09:49"},
    "test-strategy":            {"status": "PASS", "attempt": 1, "output_file": ".../test-strategy.md",        "started_at": "04:09:49", "completed_at": "04:12:41"},
    "spec-fidelity":            {"status": "FAIL", "attempt": 2, "output_file": ".../spec-fidelity.md",        "started_at": "04:14:36", "completed_at": "04:16:42"}
  },
  "fidelity_status": "fail"
}
```

**Notable observations**:
- Steps 1-8 (`extract` through `test-strategy`) all PASS on attempt 1.
- The `spec-fidelity` step ran on attempt 2 (meaning it failed on attempt 1 and was automatically retried per `retry_limit=1`), and still FAIL.
- No `validation`, `remediate`, or `certify` keys present — the pipeline halted before reaching those phases.
- Total pipeline runtime: approximately 28 minutes and 32 seconds (03:48:10 to 04:16:42).

---

## 4. Stages Completed vs Failed

| Step | Status | Attempts | Notes |
|------|--------|----------|-------|
| extract | PASS | 1 | |
| generate-opus-architect | PASS | 1 | Parallel |
| generate-haiku-architect | PASS | 1 | Parallel |
| diff | PASS | 1 | |
| debate | PASS | 1 | |
| score | PASS | 1 | |
| merge | PASS | 1 | |
| test-strategy | PASS | 1 | |
| spec-fidelity | **FAIL** | **2** | Gate failure: `high_severity_count` must be 0 |
| remediate | NOT RUN | — | Skipped due to upstream failure |
| certify | NOT RUN | — | Skipped due to upstream failure |

The pipeline halted at `spec-fidelity`. No `.err` content was present in `spec-fidelity.err` (1 line, empty).

---

## 5. Why spec-fidelity Failed — Root Cause

The `spec-fidelity` step ran successfully in the sense that the Claude subprocess produced a valid output file (`spec-fidelity.md`). The step FAIL status is from the gate check, not from a subprocess error.

**Gate failure reason**: `SPEC_FIDELITY_GATE` semantic check `high_severity_count_zero` failed.

The output file `spec-fidelity.md` contains:
```yaml
high_severity_count: 3
medium_severity_count: 8
low_severity_count: 5
total_deviations: 16
validation_complete: true
tasklist_ready: false
```

Three HIGH severity deviations were found in the roadmap:

| ID | Finding |
|----|---------|
| DEV-001 | Roadmap's Section 4.6 Implementation Order references pre-DEV-001 flat file layout (`tui.py`, `logging_.py`, `diagnostics.py`, `config.py`, `inventory.py`, `commands.py`) instead of the accepted 18-module structure with `monitor.py` and `steps/` subdirectory |
| DEV-002 | F-007 structural validation requirement for `has_section_12` gate is absent from the roadmap — spec requires the gate check for findings table or zero-gap summary text, not just heading presence |
| DEV-003 | SC validation matrix (Phase 7) is missing explicit test criteria for two spec-mandated behaviors: F-007 structural content validation and F-004 per-iteration independent timeout behavior |

The gate blocks progression because `high_severity_count: 3` fails the `_high_severity_count_zero` semantic check, and `tasklist_ready: false` is consistent with that (gate logic in `_tasklist_ready_consistent` allows false when high_severity_count > 0).

**Important nuance on DEV-001**: The accepted deviation record (`dev-001-accepted-deviation.md`) establishes that DEV-001 is a formally accepted architectural deviation — the spec should be updated to match the roadmap, not the other way around. However, the spec has not been updated yet, so the spec-fidelity gate still sees the mismatch and reports it as HIGH. The DEV-001 gate failure is a documentation lag artifact, not an architectural error.

**DEV-002 and DEV-003** are genuine roadmap gaps requiring patches to `roadmap.md`. The remediation plan (`roadmap-remediation.md`) and tasklist (`remediation-tasklist.md`) have already been produced.

---

## 6. How --resume Works and Why It May Regenerate Steps

The `_apply_resume()` function in `executor.py` (lines 1055-1131) implements resume logic. It does NOT read `.roadmap-state.json` to determine which steps to skip. It re-evaluates gate criteria directly against each step's output file on disk.

**Resume algorithm**:

```
For each step (in pipeline order):
  If a prior step already failed → include all remaining steps (run from failure point forward)
  Else if step is a parallel group:
    If ALL steps in the group pass their gates → skip the group
    Else → mark found_failure = True, include group
  Else (single step):
    If spec hash changed since last run AND this is the extract step → force re-run
    If step has a gate AND gate_passed(output_file, gate) → skip
    Else → mark found_failure = True, include step
```

**Key implication**: Resume skips steps from the beginning up to (but not including) the first step whose gate fails. All steps at and after the first failure are re-run.

**This means**:

1. If `spec-fidelity` fails its gate, a `--resume` call will:
   - Skip steps 1-8 (extract through test-strategy) because their output files still exist and pass their gates.
   - Re-run `spec-fidelity` from scratch (not from a checkpoint within the step).

2. The pipeline does NOT regenerate already-passing roadmaps (`roadmap.md`, `roadmap-opus-architect.md`, etc.) when resuming with a failing `spec-fidelity` — those steps will be skipped because their gates pass.

3. However, if `roadmap.md` is modified (to apply patches DEV-002 and DEV-003), the `merge` gate will still pass (gate checks structure/frontmatter, not content equality) so `merge` will also be skipped. The modified `roadmap.md` content will be used as input to the re-run `spec-fidelity` step.

4. If the spec file itself changes, `_apply_resume()` detects the SHA-256 hash mismatch, prints a warning, and forces re-run of the `extract` step — which cascades to all downstream steps (the `found_failure` flag is set on extract, so every subsequent step is also included).

**Stale spec detection** (lines 1067-1079):
```python
saved_hash = state.get("spec_hash", "")
current_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()
if saved_hash and saved_hash != current_hash:
    force_extract = True
```

This is the mechanism that would cause a full pipeline re-run if the spec file is edited between runs.

---

## 7. Key Source Code Snippets

### 7.1 Gate evaluation used by --resume

`src/superclaude/cli/pipeline/gates.py`, lines 20-69:

```python
def gate_passed(output_file: Path, criteria: GateCriteria) -> tuple[bool, str | None]:
    tier = criteria.enforcement_tier
    if tier == "EXEMPT":
        return True, None
    if not output_file.exists():
        return False, f"File not found: {output_file}"
    content = output_file.read_text(encoding="utf-8")
    if len(content.strip()) == 0:
        return False, f"File empty (0 bytes): {output_file}"
    if tier == "LIGHT":
        return True, None
    lines = content.splitlines()
    if len(lines) < criteria.min_lines:
        return False, (...)
    if criteria.required_frontmatter_fields:
        ok, reason = _check_frontmatter(content, criteria.required_frontmatter_fields, output_file)
        if not ok:
            return False, reason
    if tier == "STANDARD":
        return True, None
    # STRICT: semantic checks
    if criteria.semantic_checks:
        for check in criteria.semantic_checks:
            if not check.check_fn(content):
                return False, f"Semantic check '{check.name}' failed: {check.failure_message}"
    return True, None
```

### 7.2 spec-fidelity gate STRICT semantic checks

`src/superclaude/cli/roadmap/gates.py`, SPEC_FIDELITY_GATE definition:

```python
SPEC_FIDELITY_GATE = GateCriteria(
    required_frontmatter_fields=[
        "high_severity_count", "medium_severity_count", "low_severity_count",
        "total_deviations", "validation_complete", "tasklist_ready",
    ],
    min_lines=20,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="high_severity_count_zero",
            check_fn=_high_severity_count_zero,
            failure_message="high_severity_count must be 0 for spec-fidelity gate to pass",
        ),
        SemanticCheck(
            name="tasklist_ready_consistent",
            check_fn=_tasklist_ready_consistent,
            failure_message="tasklist_ready is inconsistent with severity counts or validation_complete",
        ),
    ],
)
```

### 7.3 _apply_resume — the critical resume skip logic

`src/superclaude/cli/roadmap/executor.py`, lines 1082-1130 (condensed):

```python
found_failure = False
result: list[Step | list[Step]] = []

for entry in steps:
    if found_failure:
        result.append(entry)  # after first failure, include all remaining
        continue
    if isinstance(entry, list):  # parallel group
        all_pass = all(gate_fn(s.output_file, s.gate)[0] for s in entry if s.gate)
        if all_pass:
            skipped += len(entry)  # skip the whole parallel group
        else:
            found_failure = True
            result.append(entry)
    else:  # single step
        if force_extract and entry.id == "extract":
            found_failure = True
            result.append(entry)
            continue
        if entry.gate:
            passed, _ = gate_fn(entry.output_file, entry.gate)
            if passed:
                skipped += 1
                continue  # skip this step
        found_failure = True
        result.append(entry)
```

### 7.4 Spec hash check for stale-spec detection

`src/superclaude/cli/roadmap/executor.py`, lines 1067-1079:

```python
saved_hash = state.get("spec_hash", "")
current_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()
if saved_hash and saved_hash != current_hash:
    print("WARNING: spec-file has changed since last run.\n  Forcing re-run of extract step.",
          file=sys.stderr)
    force_extract = True
```

---

## 8. Artifact Inventory in Release Directory

All files found under `.dev/releases/current/v2.24-cli-portify-cli-v4/`:

| File | Status | Notes |
|------|--------|-------|
| `portify-release-spec.md` | Input | Source spec for the pipeline run |
| `extraction.md` | PASS | Step 1 output |
| `roadmap-opus-architect.md` | PASS | Step 2a output (Variant A) |
| `roadmap-haiku-architect.md` | PASS | Step 2b output (Variant B) |
| `diff-analysis.md` | PASS | Step 3 output |
| `debate-transcript.md` | PASS | Step 4 output |
| `base-selection.md` | PASS | Step 5 output |
| `roadmap.md` | PASS | Step 6 output (merged roadmap) |
| `test-strategy.md` | PASS | Step 7 output |
| `spec-fidelity.md` | **FAIL** | Step 8 output — 3 HIGH deviations found |
| `spec-fidelity.err` | Empty | No subprocess stderr captured |
| `*.err` files | Various | Stderr captures for each step subprocess |
| `.roadmap-state.json` | State | Pipeline state, `fidelity_status: "fail"` |
| `dev-001-accepted-deviation.md` | Remediation | Formal acceptance record for DEV-001 |
| `roadmap-remediation.md` | Remediation | Patch plan for DEV-002, DEV-003, DEV-008 |
| `remediation-tasklist.md` | Remediation | Ordered task list for applying patches |

There are also supplementary files (`portify-analysis.md`, `portify-spec.md`, `panel-report.md`, `release-spec-remediation.md`) that appear to be pre-pipeline working documents from earlier in the v2.24 release process.

---

## 9. Observations: Why --resume Would Regenerate Roadmaps

Based on the evidence, here are the specific conditions under which `--resume` would regenerate steps unexpectedly:

### Condition A: Spec file modified (most likely cause)

If `portify-release-spec.md` is edited between runs — even whitespace changes — the SHA-256 hash changes, `force_extract = True` is set, and the entire pipeline re-runs from `extract` onward (all 8 steps). This produces entirely new `roadmap-opus-architect.md`, `roadmap-haiku-architect.md`, `roadmap.md`, etc.

**Evidence**: The `spec_hash` in state is `3d1a6d158...`. Any change to the spec file would trigger full pipeline regeneration.

### Condition B: Output files deleted or truncated

If any step's output file is deleted, moved, or emptied, its gate will fail (file-not-found or empty-file check in `gate_passed()`). The resume algorithm will include that step and all downstream steps. Because steps are connected (each uses the previous step's output as input), regenerating `roadmap.md` (merge step) also regenerates `spec-fidelity.md` content.

### Condition C: Gate criteria tightened

If a new version of the code tightens a gate (e.g., adds a new required frontmatter field), a previously-passing output file may fail the gate on the next `--resume`, causing that step and all downstream steps to re-run.

### Condition D: Parallel group partial failure

For the `generate` parallel group (steps 2a and 2b), the resume logic only skips the group if ALL steps in the group pass their gates. If one of the two roadmap files fails its gate, both are re-run. This is by design (the diff step needs both roadmaps from the same generation run).

### Why --resume Does NOT regenerate in the current state

Given the current state (spec-fidelity FAIL, all earlier steps PASS):

- A `--resume` call will check gates for `extract`, the parallel generate group, `diff`, `debate`, `score`, `merge`, `test-strategy` in order.
- All of these output files exist and contain valid content that passes their respective gates.
- The first failing gate is `spec-fidelity` (because `spec-fidelity.md` has `high_severity_count: 3`).
- Resume will skip steps 1-8 and only re-run `spec-fidelity`.
- The regenerated roadmaps scenario would only occur if the spec file changed or an earlier output file was invalidated.

**The correct next step** per `remediation-tasklist.md` is:
1. Apply TASK-R1.1 and TASK-R1.2 patches to `roadmap.md` (add missing domain model details and gate contract section).
2. Verify the patches (TASK-R2.1).
3. Run `superclaude roadmap run .../portify-release-spec.md --resume` (TASK-R2.2).
4. `--resume` will skip steps 1-8 and re-run only `spec-fidelity` against the patched `roadmap.md`.

---

## 10. Pipeline Architecture Files (Source Locations)

| Component | File |
|-----------|------|
| CLI commands and flags | `/config/workspace/IronClaude/src/superclaude/cli/roadmap/commands.py` |
| Pipeline executor and state management | `/config/workspace/IronClaude/src/superclaude/cli/roadmap/executor.py` |
| Gate criteria definitions | `/config/workspace/IronClaude/src/superclaude/cli/roadmap/gates.py` |
| Gate evaluation logic | `/config/workspace/IronClaude/src/superclaude/cli/pipeline/gates.py` |
| Pipeline models (Step, StepResult, etc.) | `/config/workspace/IronClaude/src/superclaude/cli/pipeline/models.py` |
| Roadmap-specific models (RoadmapConfig, AgentSpec) | `/config/workspace/IronClaude/src/superclaude/cli/roadmap/models.py` |
| State file (release artifact) | `/config/workspace/IronClaude/.dev/releases/current/v2.24-cli-portify-cli-v4/.roadmap-state.json` |
| Spec-fidelity output (failing gate) | `/config/workspace/IronClaude/.dev/releases/current/v2.24-cli-portify-cli-v4/spec-fidelity.md` |
| DEV-001 acceptance record | `/config/workspace/IronClaude/.dev/releases/current/v2.24-cli-portify-cli-v4/dev-001-accepted-deviation.md` |
| Remediation patch plan | `/config/workspace/IronClaude/.dev/releases/current/v2.24-cli-portify-cli-v4/roadmap-remediation.md` |
| Remediation tasklist | `/config/workspace/IronClaude/.dev/releases/current/v2.24-cli-portify-cli-v4/remediation-tasklist.md` |
