---
feature: /sc:forensic + sc:forensic-protocol
spec_source: .dev/releases/backlog/forensic/forensic-spec.md
test_strategy_version: 2.0.0
date: 2026-02-28
complexity_class: HIGH
interleave_ratio: "1:1"
validation_philosophy: continuous_parallel
stop_and_fix_threshold: critical
collision_suffix: "-2"
---

# /sc:forensic — Validation and Test Strategy

## Philosophy

**Complexity class HIGH → interleave ratio 1:1**: For every authoring task, a corresponding
test or validation task is authored. Tests are not deferred to a final "testing milestone" —
they are authored in M6 but designed in parallel with M3-M5 phase authoring. This means
test fixtures are defined while phase behavior is being written, preventing schema drift
between implementation and tests.

**Continuous parallel validation**: Tests run at the boundary of each milestone, not at the
end of the roadmap. A failing test at M3 is detected and fixed before M4 authoring begins.
The cost of deferring test failure discovery is proportional to how many milestones have
accumulated since the defect was introduced.

**Behavioral contract testing, not implementation testing**: Tests validate that the
behavioral contracts documented in the spec and SKILL.md are honored — specifically that
each phase produces the correct artifact schema when given the correct input artifacts.
We do not test internal implementation choices (model tier selection heuristics, exact
prompt wording).

---

## Test Classification

| Type | Purpose | Milestone Gate |
|------|---------|---------------|
| Smoke tests (per-phase) | Verify each phase produces schema-valid artifacts on minimal input | M6 |
| Integration tests | Verify cross-phase artifact handoff and checkpoint/resume | M6 |
| Edge case tests | Verify boundary conditions (zero hypotheses, tiny target, dry-run) | M6 |
| Schema conformance tests | Verify all 9 schemas validate correctly with sample data | M6 |
| Security tests | Verify `--redact` applies to all artifact types with pattern coverage | M6 |
| Manual reviews | Verify SKILL.md completeness (no stubs), command file accuracy | M6 |

---

## Per-Milestone Validation Gates

### M0: Spec Amendments Tier 1

**Validation method**: Peer review (manual)

| Check | Method |
|-------|--------|
| All 55 FRs have normative markers (MUST/SHOULD/MAY) | grep count on spec |
| Section 12.0 path table present with all canonical paths | manual cross-reference |
| `fix-selection.md` schema referenced by Phase 4 input contract | manual cross-reference |
| `--depth` flag precedence rule present | manual spec review |
| Model-tier fallback documented with `progress.json` logging | manual spec review |

**Stop-and-fix threshold**: Any missing normative marker or missing path table entry halts M1.

### M1: Spec Amendments Tiers 2-3

**Validation method**: Peer review + schema syntax check

| Check | Method |
|-------|--------|
| All 9 schemas parse as valid YAML | YAML linter |
| Slug pattern (`^[a-z][a-z0-9-]+$`) applied to domain IDs | grep on schema |
| Three-level token budget present in each of 7 phase sections | count check |
| All 12 new/amended FRs from proposal-verdicts.md are represented | count check |
| No cross-references broken by P-009 slug migration | manual audit |

**Stop-and-fix threshold**: Any broken cross-reference or missing schema field halts M2.

### M2: Foundation (Command + Skill Shell + Schemas)

**Validation method**: Automated sync check + manual review

| Check | Method |
|-------|--------|
| `forensic.md` exists at both canonical paths | file existence |
| All 10 flags present with correct types and defaults | diff vs spec §5.3 |
| Activation block present and correct | grep on command file |
| All 9 schemas in `refs/schemas.md` include proposal amendments | schema count + spot check |
| `make verify-sync` exits 0 | CI command |
| SKILL.md phase stubs all present (no empty phase sections) | grep on SKILL.md |

**Stop-and-fix threshold**: Any flag missing or sync failure halts M3.

### M3: Phase 0 Behavior

**Validation method**: Content review + smoke test design (test written in advance)

| Check | Method |
|-------|--------|
| Phase 0 prompts reference `secrets_exposure` category (P-007) | content review |
| Domain generation prompt produces slug IDs | prompt review |
| Tiny target bypass rule (<5 files) is present | content review |
| Three-level token budget for Phase 0: soft/ceiling/overflow | count check |
| MCP availability pre-check block present | content review |
| `target_root` field in domain generation output | schema cross-ref |

**Stop-and-fix threshold**: Missing `secrets_exposure` or missing slug format halts M4.

### M4: Phases 1 and 3 Behavior

**Validation method**: Content review + prompt schema validation

| Check | Method |
|-------|--------|
| Investigation agent prompt produces slug-based hypothesis IDs | prompt review |
| Fix proposal prompt enforces exactly 3 tiers | prompt review |
| Zero-hypothesis handling block present | content review |
| Three-level token budgets for Phases 1 and 3 | count check |
| `test_requirements` structure matches schema | schema cross-ref |

**Stop-and-fix threshold**: Missing fix tier enforcement or zero-hypothesis handler halts M5.

### M5: Full Pipeline (Phases 2, 3b, 4, 5, 6)

**Validation method**: Content review + fixture design

| Check | Method |
|-------|--------|
| Phase 2 and 3b adversarial invocation patterns match spec §7.2 and §7.4 | cross-ref |
| Baseline test artifact capture in Agent 5b (P-017) | content review |
| Exit criteria section defines all 3 statuses | count check |
| `--clean` gate on `success` only | content review |
| `refs/redaction.md` contains at least 4 secret regex patterns | content review |
| `refs/checkpoint-resume.md` references all P-008 new required fields | content review |
| `--dry-run` bypass of Phases 4-5 | logic review |

**Stop-and-fix threshold**: Missing exit criteria or missing baseline test capture halts M6.

### M6: Testing + Sync + Verification

**Validation method**: Automated test suite execution

**Stop-and-fix rule**: ALL tests must pass before release. Any failing test, even in an
"optional" category, is fixed before marking M6 complete. Zero exceptions.

---

## Test Specifications

### Smoke Tests: Per-Phase

Each smoke test uses a minimal fixture (3-5 files) per P-015 requirement.

**Fixture design**: A synthetic 5-file Python project:
```
fixture/
  main.py         # Entry point with subprocess call
  auth.py         # Authentication with bare except
  utils.py        # Shared utilities with no tests
  tests/
    test_main.py  # Partial coverage
```

This fixture is designed to produce observable output from Phase 0 (detects subprocess usage,
bare except, untested `utils.py`) and at least 2 domains.

#### test_phase0_smoke.py

**Inputs**: Fixture directory path
**Expected outputs**: `structural-inventory.json`, `dependency-graph.json`,
`risk-surface.json`, `investigation-domains.json`

| Assertion | What it checks |
|-----------|---------------|
| All 4 output files exist | Basic phase completion |
| `structural-inventory.json` conforms to schema | Schema conformance |
| `risk-surface.json` contains `overall_risk_score` field (P-007) | Proposal integration |
| `risk-surface.json` contains `secrets_exposure` category (P-007) | Proposal integration |
| `investigation-domains.json` domain names are kebab-case slugs (P-009) | Proposal integration |
| Each domain has `target_root` field (P-021) | Proposal integration |
| Domain count is 1-10 | Constraint |
| `progress.json` has `phase_status_map` with Phase 0 status | P-008 |

#### test_phase1_smoke.py

**Inputs**: Phase 0 fixture output (deterministic, canned)
**Expected outputs**: `findings-domain-*.md` files per domain

| Assertion | What it checks |
|-----------|---------------|
| One findings file per domain | Agent count |
| Hypothesis IDs match `H-{slug}-{seq}` pattern (P-009) | Proposal integration |
| All hypotheses have `evidence` with at least 1 entry | Evidence requirement |
| All hypotheses have `falsification` field | Schema conformance |
| Confidence scores are 0.0-1.0 | Range validation |
| `progress.json` updated with Phase 1 status | Checkpoint |

#### test_phase3_smoke.py

**Inputs**: Canned Phase 2 output (base-selection.md with 2 surviving hypotheses)
**Expected outputs**: `fix-proposal-H-*.md` files

| Assertion | What it checks |
|-----------|---------------|
| One fix proposal file per hypothesis | Agent count |
| Each file has exactly 3 entries in `fix_options` (P-010) | Proposal integration |
| Each tier is one of: minimal, moderate, robust | Enum constraint |
| `test_requirements` has at least 1 entry with `type` field | Schema |
| `progress.json` updated with Phase 3 status | Checkpoint |

#### test_phase5_smoke.py

**Inputs**: Canned Phase 4 output (`changes-manifest.json`, `new-tests-manifest.json`)
**Expected outputs**: `lint-results.txt`, `test-results.md`, `self-review.md`

| Assertion | What it checks |
|-----------|---------------|
| All 3 output files exist | Basic phase completion |
| `test-results.md` contains baseline test section (P-017) | Proposal integration |
| `self-review.md` contains all 4 mandatory questions | Protocol |
| `progress.json` updated with Phase 5 status | Checkpoint |

### Integration Tests

#### test_checkpoint_resume.py

**Scenario**: Pipeline runs Phases 0-2, writes progress.json, session is interrupted.
New session invokes `--resume`.

| Assertion | What it checks |
|-----------|---------------|
| Resume reads `progress.json` and starts from Phase 3 | Resume logic |
| `run_id` is stable across resume (same UUID) (P-008) | Stability |
| `phase_status_map` shows Phases 0-2 as `complete` | P-008 |
| Flags from original invocation are restored from `progress.json.flags` | Consistency |
| Artifact integrity check: missing Phase 1 artifact → demotes to Phase 1 restart | Spec §12.3 |

### Edge Case Tests

#### test_zero_hypotheses.py

**Scenario**: Phase 2 produces 0 hypotheses meeting confidence threshold.

| Assertion | What it checks |
|-----------|---------------|
| Empty-result artifact is produced | P-016 |
| No Phase 3 artifacts are produced (no agent spawn) | P-016 |
| `progress.json` status is `failed` or `success_with_risks` | P-018 |
| User-visible message is emitted | P-016 |

#### test_tiny_target.py

**Scenario**: Target path has 3 files.

| Assertion | What it checks |
|-----------|---------------|
| `investigation-domains.json` contains exactly 1 domain | P-015 |
| Domain name is derived from target path, not auto-discovered | P-015 |
| Pipeline continues normally after Phase 0 | Correctness |

#### test_dry_run.py

**Scenario**: `--dry-run` flag is set.

| Assertion | What it checks |
|-----------|---------------|
| Phase plan output is produced before any agents spawn | P-003 |
| Phase plan contains domain count estimate and model tier estimates | P-003 |
| No Phase 4-5 artifacts are produced | FR-044 |
| `progress.json` status reflects dry-run halt | Observability |

### Security Tests

#### test_redaction.py

**Scenario**: Phase 1 findings artifact contains synthetic secrets.

**Fixture secret patterns**:
```python
SYNTHETIC_SECRETS = [
    "sk-proj-abc123def456",           # OpenAI API key prefix
    "ghp_xxxxxxxxxxxxxxxxxxxxxxxx",   # GitHub personal access token
    "password=super_secret_123",      # Password assignment
    "-----BEGIN PRIVATE KEY-----",    # PEM private key header
]
```

| Assertion | What it checks |
|-----------|---------------|
| None of the 4 synthetic secret patterns appear in output artifacts | P-020 |
| Redaction log artifact is produced | P-020 |
| Non-secret code content is preserved in output | False-positive check |
| `--redact false` disables redaction | Flag behavior |

### Schema Conformance Tests

#### test_schemas.py

Tests all 9 schemas against positive (valid) and negative (invalid) sample data.

| Schema | Positive Test | Negative Test |
|--------|--------------|---------------|
| structural-inventory | Valid inventory with all required fields | Missing `test_coverage_map` |
| dependency-graph | Valid graph with circular dep | Missing `hot_paths` |
| risk-surface | Valid surface with `overall_risk_score` (P-007) | `overall_risk_score` out of range |
| investigation-domains | Valid domains with slug IDs and `target_root` (P-009, P-021) | Non-slug domain name |
| hypothesis-finding | Valid finding with slug hypothesis ID | Missing `falsification` |
| fix-proposal | Exactly 3 tiers (P-010) | 2 tiers (should fail) |
| changes-manifest | Valid manifest | Missing `timestamp` |
| new-tests-manifest | Valid manifest with `schema_version` (P-006) | Missing `schema_version` |
| progress | Valid with `run_id`, `phase_status_map`, `target_paths` (P-008) | Missing `run_id` |

---

## Test File Organization

All test files are placed in `tests/sprint/forensic/`. This follows the existing `tests/sprint/`
convention established by the sprint CLI module.

```
tests/sprint/forensic/
  __init__.py
  conftest.py                    # Shared fixtures (5-file synthetic codebase, canned artifacts)
  test_phase0_smoke.py
  test_phase1_smoke.py
  test_phase3_smoke.py
  test_phase5_smoke.py
  test_checkpoint_resume.py
  test_zero_hypotheses.py
  test_tiny_target.py
  test_dry_run.py
  test_redaction.py
  test_schemas.py
  fixtures/
    synthetic_codebase/          # 5-file Python project for smoke tests
      main.py
      auth.py
      utils.py
      tests/
        test_main.py
    canned_artifacts/            # Pre-generated artifacts for phase isolation
      phase0_output/             # For Phase 1 tests
      phase2_output/             # For Phase 3 tests (2 surviving hypotheses)
      phase4_output/             # For Phase 5 tests
```

---

## Stop-and-Fix Severity Levels

| Severity | Definition | Action |
|----------|-----------|--------|
| CRITICAL | Schema validation fails; checkpoint/resume breaks; Phase boundary contract violated | Stop immediately. Fix before any further authoring. |
| HIGH | Missing proposal integration (P-006 through P-021); wrong flag default; security pattern miss | Fix within current milestone before marking complete. |
| MEDIUM | Minor schema field missing; off-by-one in token budget; non-blocking edge case | Fix within current milestone. Document if deferring. |
| LOW | Documentation clarity issue; example not matching usage | Fix opportunistically; do not delay milestone for LOW. |

**Default stop-and-fix threshold**: CRITICAL and HIGH issues always halt the milestone.

---

## Continuous Validation Schedule

| Milestone Complete | Tests to Run | Expected Outcome |
|-------------------|-------------|-----------------|
| M0 | Manual spec review checklist (SC-001 to SC-005) | All 5 criteria pass |
| M1 | Manual spec review checklist (SC-006 to SC-017) + YAML lint | All 12 criteria pass; 9 schemas parse |
| M2 | `make verify-sync` + manual file existence checks (SC-018 to SC-024) | Sync exits 0; all files present |
| M3 | Content review (SC-025 to SC-031) | All 7 criteria pass |
| M4 | Content review (SC-032 to SC-038) | All 7 criteria pass |
| M5 | Content review (SC-039 to SC-048) | All 10 criteria pass |
| M6 | `uv run pytest tests/sprint/forensic/ -v` + `make verify-sync` | All tests pass; sync exits 0 |

**Total success criteria**: 58 (SC-001 through SC-058)

---

## Integration with Existing Test Infrastructure

The forensic test suite integrates with the existing SuperClaude pytest infrastructure:

```bash
# Run only forensic tests
uv run pytest tests/sprint/forensic/ -v

# Run with coverage
uv run pytest tests/sprint/forensic/ --cov=superclaude -v

# Run smoke tests only (fast subset)
uv run pytest tests/sprint/forensic/ -v -k "smoke"

# Run all tests from project root
make test
```

Tests use the existing `pytest` setup from `pyproject.toml` entry points and respect the
existing test marker system (`@pytest.mark.unit`, `@pytest.mark.integration`).

Smoke tests should be marked `@pytest.mark.integration` (they cross phase boundaries in
fixture terms, even though they use canned inputs).

Schema tests should be marked `@pytest.mark.unit` (pure data validation, no I/O).
