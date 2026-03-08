---
validation_milestones: 8
interleave_ratio: '1:1'
---

# Test Strategy: Roadmap Pipeline Reliability (v2.17)

## 1. Validation Milestones Mapped to Roadmap Phases

### M1: P1 Scoping Complete (Pre-implementation gate)
**Validates:** Caller inventory, canonical field list, fixture capture
- Confirm `_check_frontmatter` caller count via grep evidence
- Document all 13 frontmatter fields from `templates.md`
- Capture 2+ fixture files (1 passing, 1 failing) from real pipeline output
- **Acceptance:** Scoping artifacts exist in test fixtures directory; no code changes yet

### M2: P1 Gate Fix — Unit Tests Green
**Validates:** FR-001 through FR-006, FR-020, NFR-001, NFR-002
- All 8 new `_check_frontmatter` regex test cases pass
- All pre-existing `tests/pipeline/test_gates.py` tests pass unchanged
- All pre-existing `tests/roadmap/test_gates_data.py` tests pass unchanged
- **Acceptance:** `uv run pytest tests/pipeline/test_gates.py tests/roadmap/test_gates_data.py -v` — all green, zero regressions

### M3: P2 Sanitizer — Unit Tests Green
**Validates:** FR-007 through FR-012, NFR-003, NFR-004
- All 7 `_sanitize_output` test cases pass (clean, preamble, no-frontmatter, atomic failure, UTF-8, idempotence, 10MB boundary)
- Integration with `roadmap_run_step` call ordering verified
- **Acceptance:** `uv run pytest tests/roadmap/test_executor.py -v` — all green

### M4: P3 Prompt Hardening — Validation Checks Pass
**Validates:** FR-013 through FR-015, NFR-005
- All 7 `build_*_prompt()` functions contain `<output_format>` block
- Block placement is after main body (position assertion)
- Token overhead < 200 tokens per function
- **Acceptance:** `uv run pytest tests/roadmap/test_prompts.py -v` — all green

### M5: P4 Protocol Parity — Unit Tests Green
**Validates:** FR-016 through FR-019, NFR-006
- `EXTRACT_GATE` requires all 13+ fields
- `build_extract_prompt()` references all required fields
- Executor-populated fields (`pipeline_diagnostics`) absent from LLM prompt
- `build_generate_prompt()` consumes expanded extraction without error
- **Acceptance:** `uv run pytest tests/roadmap/test_gates_data.py tests/roadmap/test_prompts.py -v` — all green

### M6: Cross-Pipeline Regression Gate
**Validates:** NFR-001, NFR-002, Risk #5
- Full pipeline test suite passes: `uv run pytest tests/pipeline/ -v`
- Full roadmap test suite passes: `uv run pytest tests/roadmap/ -v`
- No test modifications required outside new additions
- **Acceptance:** Zero test failures across both directories

### M7: Integration — Mock Pipeline End-to-End
**Validates:** Success Criteria #1, #4, #5
- Mock-subprocess pipeline run completes 8/8 steps
- Gate validation passes on sanitized mock output
- State save/reload roundtrip succeeds
- **Acceptance:** `TestIntegrationMockSubprocess` tests all pass with expanded gates

### M8: E2E — Real Pipeline Run (Manual)
**Validates:** Success Criteria #1, #2, #3
- `superclaude roadmap run <spec> --depth deep --agents opus:architect,haiku:analyzer` completes 8/8 steps
- `grep -L '^---' .dev/releases/*/pipeline-output/*.md` returns empty
- Extraction frontmatter contains all 13+ fields
- **Acceptance:** Human-verified evidence for all 3 checks

---

## 2. Test Categories

### Unit Tests (22+ cases)

| Component | File | New Cases | Existing Cases | Total |
|-----------|------|-----------|----------------|-------|
| `_check_frontmatter` regex | `tests/pipeline/test_gates.py` | 0 (8 already exist) | 8 | 8 |
| `gate_passed` tiers | `tests/pipeline/test_gates.py` | 0 | 12 | 12 |
| `_sanitize_output` | `tests/roadmap/test_executor.py` | 2 (10MB, atomic failure) | 5 | 7 |
| `build_*_prompt` output_format | `tests/roadmap/test_prompts.py` | 7 (one per builder) | 5 | 12 |
| `build_extract_prompt` fields | `tests/roadmap/test_prompts.py` | 2 (field list, section list) | 0 | 2 |
| `EXTRACT_GATE` fields | `tests/roadmap/test_gates_data.py` | 0 (already covers 13 fields) | 4 | 4 |
| Semantic check helpers | `tests/roadmap/test_gates_data.py` | 0 | 12 | 12 |
| Executor-populated field exclusion | `tests/roadmap/test_prompts.py` | 1 | 0 | 1 |

**New test cases: ~12 | Existing preserved: ~41+**

### Integration Tests (4 cases)

| Scenario | File | Description |
|----------|------|-------------|
| Pipeline pass-through | `tests/roadmap/test_executor.py` | Mock runner writes gate-passing output with expanded fields; 8/8 steps pass |
| Pipeline halt on gate | `tests/roadmap/test_executor.py` | Runner writes output missing required field; pipeline halts correctly |
| State roundtrip | `tests/roadmap/test_executor.py` | `_save_state` → `read_state` with new gate fields |
| Generate consumes extraction | `tests/roadmap/test_prompts.py` | `build_generate_prompt()` accepts extraction with all 13+ fields |

### E2E Tests (1 case, manual)

| Scenario | Method | Criteria |
|----------|--------|----------|
| Full pipeline run | `superclaude roadmap run <spec>` | 8/8 steps complete, clean artifacts, protocol-complete extraction |

### Acceptance Tests (per milestone — see Section 5)

---

## 3. Test-Implementation Interleaving Strategy

**Ratio: 1:1** — Each implementation unit is immediately followed by its test verification before proceeding.

```
P1 Scoping
  └─ Grep callers, capture fixtures, document fields
  └─ EXIT GATE: Fixture files exist (M1)

P1 Implementation
  ├─ Write _FRONTMATTER_PATTERN regex          → Run 8 regex unit tests
  ├─ Update _check_frontmatter() body          → Run full test_gates.py
  └─ EXIT GATE: All pipeline + roadmap tests green (M2)

P2 Implementation  ║  P3 Implementation (parallel)
  ├─ Write _sanitize_output()                  ║  ├─ Add _OUTPUT_FORMAT_BLOCK
  │  → Run 7 sanitizer tests                   ║  │  → Run 7 prompt presence tests
  ├─ Wire into roadmap_run_step()              ║  ├─ Verify position + token budget
  │  → Run integration tests                   ║  │  → Run 3 validation checks
  └─ EXIT GATE: test_executor.py green (M3)    ║  └─ EXIT GATE: test_prompts.py green (M4)

P4 Implementation
  ├─ Update build_extract_prompt() fields      → Run field list test
  ├─ Update EXTRACT_GATE required_fields       → Run test_gates_data.py
  ├─ Verify executor-only field exclusion      → Run exclusion test
  ├─ Verify generate prompt consumption        → Run consumption test
  └─ EXIT GATE: All unit tests green (M5)

Cross-pipeline regression
  └─ Run full suite: uv run pytest tests/pipeline/ tests/roadmap/ -v (M6)

Integration verification
  └─ Run mock pipeline integration tests (M7)

E2E validation (manual)
  └─ Run real pipeline, inspect artifacts (M8)
```

**Key principle:** No phase advances until its exit gate passes. P2 and P3 are parallelizable because they touch different files with no shared state.

---

## 4. Risk-Based Test Prioritization

Tests are ordered by risk severity and probability, highest priority first:

| Priority | Risk | Tests | Rationale |
|----------|------|-------|-----------|
| **P0** | Shared gate regression (Risk #5) | Existing `test_gates.py` full suite, cross-pipeline regression run | Highest blast radius — all 8 pipeline steps affected |
| **P0** | Regex false positive on `---` rules (Risk #1) | `test_horizontal_rule_rejected`, `test_multiple_frontmatter_blocks` | Incorrect match would silently accept invalid artifacts |
| **P1** | Protocol parity breaks generate (Risk #4) | Generate consumption test, mock pipeline integration | Medium severity + medium probability |
| **P1** | Field ownership ambiguity (Risk #6) | Executor-populated field exclusion test | Cross-file coordination hazard |
| **P2** | Sanitizer strips valid content (Risk #2) | Clean file no-op, no-frontmatter no-op, atomic write recovery | High severity but low probability |
| **P2** | Backward compatibility (NFR-001, NFR-002) | All existing tests pass unchanged | Regression safety net |
| **P3** | Prompt hardening insufficient (Risk #3) | Output format presence + position tests | Low severity — P1 and P2 are deterministic backups |
| **P3** | 10MB boundary (NFR-003) | Large file test | Edge case, unlikely in practice |

---

## 5. Acceptance Criteria Per Milestone

### M1 — P1 Scoping Complete
- [ ] `grep -r "_check_frontmatter" src/` output captured and caller count documented
- [ ] Canonical 13-field list extracted from `templates.md` and recorded
- [ ] At least 1 failing + 1 passing fixture file captured as test data
- [ ] No code changes made yet

### M2 — P1 Gate Fix
- [ ] `_FRONTMATTER_PATTERN` is a compiled module-level constant using `re.MULTILINE`
- [ ] Regex requires `key: value` between `---` delimiters
- [ ] 8 regex test cases pass: byte-0, preamble, horizontal rule, missing fields, multiple blocks, empty doc, extra whitespace, regression fixture
- [ ] All pre-existing `test_gates.py` tests pass without modification
- [ ] All pre-existing `test_gates_data.py` tests pass without modification

### M3 — P2 Sanitizer
- [ ] `_sanitize_output()` exists in `executor.py` with signature `(path: Path) -> int`
- [ ] Atomic write via `.tmp` + `os.replace()` confirmed by test
- [ ] 7 test cases pass: clean, preamble, no-frontmatter, atomic failure, UTF-8, idempotence, 10MB
- [ ] `_log.info()` called with byte count when stripping
- [ ] Wired into `roadmap_run_step()` after subprocess, before gate

### M4 — P3 Prompt Hardening
- [ ] All 7 `build_*_prompt()` functions contain `<output_format>` XML block
- [ ] Block placed at end of each prompt (after main body)
- [ ] Token overhead per function < 200 tokens
- [ ] Positive instruction ("MUST begin with"), negative instruction ("Do NOT"), and template present

### M5 — P4 Protocol Parity
- [ ] `EXTRACT_GATE.required_frontmatter_fields` contains all 13 fields
- [ ] `build_extract_prompt()` references all 13 fields by name
- [ ] `pipeline_diagnostics` does NOT appear in extract prompt text
- [ ] `build_generate_prompt()` can consume extraction output with all 13+ fields
- [ ] Extract prompt requests FR-NNN/NFR-NNN structured sections

### M6 — Cross-Pipeline Regression
- [ ] `uv run pytest tests/pipeline/ -v` — zero failures
- [ ] `uv run pytest tests/roadmap/ -v` — zero failures
- [ ] No existing test files modified (new tests only)

### M7 — Integration Verification
- [ ] Mock pipeline completes 8/8 steps with expanded gate fields
- [ ] State persistence roundtrips correctly with new fields
- [ ] Gate failure halts pipeline at correct step

### M8 — E2E Validation
- [ ] `superclaude roadmap run` completes 8/8 steps
- [ ] All `.md` artifacts start with `---` (no preamble)
- [ ] Extraction frontmatter contains all 13+ fields with non-empty values
- [ ] Generate step produces valid roadmap consuming expanded extraction
- [ ] Evidence recorded for each criterion

---

## 6. Quality Gates Between Phases

```
┌─────────┐     QG1      ┌─────────┐     QG2      ┌──────────┐     QG3      ┌─────────┐
│ P1 Gate │────────────▶ │ P2 San. │────────────▶ │ P4 Proto │────────────▶ │  E2E    │
│  Fix    │              │ + P3    │              │  Parity  │              │  Valid  │
└─────────┘              └─────────┘              └──────────┘              └─────────┘
```

### QG1: P1 → P2/P3 (Gate Correctness)
- **Required:** M2 acceptance criteria all pass
- **Command:** `uv run pytest tests/pipeline/test_gates.py tests/roadmap/test_gates_data.py -v`
- **Rationale:** P2 sanitizer is tested against P1 gate logic. P3 prompts target the same frontmatter format. Both depend on correct gate behavior.
- **Blocking:** Any `_check_frontmatter` regression blocks all subsequent phases.

### QG2: P2+P3 → P4 (Defense Layers Verified)
- **Required:** M3 + M4 acceptance criteria all pass
- **Command:** `uv run pytest tests/roadmap/test_executor.py tests/roadmap/test_prompts.py -v`
- **Rationale:** P4 expands field requirements across gate + prompt. Both sanitizer and prompt hardening must be stable before expanding the contract.
- **Blocking:** Sanitizer atomic write failure or prompt format regression blocks P4.

### QG3: P4 → E2E (All Units + Integration Green)
- **Required:** M5 + M6 + M7 acceptance criteria all pass
- **Command:** `uv run pytest tests/pipeline/ tests/roadmap/ -v`
- **Rationale:** E2E runs are expensive (real LLM calls). All deterministic tests must pass first to avoid wasting resources on known failures.
- **Blocking:** Any unit or integration failure blocks E2E execution.

### Post-Release Quality Gate
- **Monitor:** Sanitizer invocation frequency via `_log.info` output
- **Threshold:** If >50% of pipeline runs require sanitization after 10 runs, prompt hardening (P3) is insufficient — file follow-up issue
- **Action:** No release gate, but documented observability criterion (Success Criterion #6 from roadmap)
