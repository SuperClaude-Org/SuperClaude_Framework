# Backward Compatibility Regression Report

**Baseline**: D-0002 (8 canonical invocations)
**Target**: `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-adversarial-protocol/SKILL.md`
**Date**: 2026-03-05
**Verdict**: **PASS** -- All 8 invariants verified, zero regressions detected.

---

## Per-Invocation Status Table

| # | Invocation | Mode | Expected Behavior | Status | Evidence |
|---|-----------|------|-------------------|--------|----------|
| 1 | `--compare f1.md,f2.md` | A | Route via step_1 Mode A, 2 files validated, 5-step protocol executes | **PASS** | step_1 mode_a_signal at L517; step_2_mode_a_parsing at L522; count_check "2 <= file_count <= 10" at L525 |
| 2 | `--compare f1.md,f2.md,f3.md` | A | Route via step_1 Mode A, 3 files validated | **PASS** | Same routing as #1; count validation accepts 2-10 at L525 |
| 3 | `--compare f1..f10` (10 files) | A | Route via step_1 Mode A, 10 files accepted (max boundary) | **PASS** | count_check "2 <= file_count <= 10" at L525; too_many STOP at >10 at L530 |
| 4 | `--source s.md --generate roadmap --agents opus,sonnet` | B | Route via step_1 Mode B, 2 agents parsed, variants generated | **PASS** | step_1 mode_b_signal at L518; step_3_mode_b_parsing at L534; agent count_check "2 <= agent_count <= 10" at L549 |
| 5 | `--source s.md --generate roadmap --agents opus:arch,sonnet:sec,haiku:qa` | B | Route via step_1 Mode B, 3 agents with personas | **PASS** | agent_spec_parsing format at L542-L548; Mode B generation at L1856-L1890 |
| 6 | `--source s.md --generate spec --agents a,b --depth deep` | B | Route via Mode B with deep (3 rounds) | **PASS** | depth values at L560; round_3 condition "--depth deep" at L1072 |
| 7 | `--compare f1.md --source s.md --generate t --agents a,b` (conflict) | ERROR | STOP: conflicting Mode A + Mode B flags | **PASS** | step_1 conflict at L519: "Cannot use --compare with --source/--generate/--agents" |
| 8 | (no mode flags) | ERROR | STOP: missing required flags | **PASS** | step_1 neither at L520: "Must provide --compare (Mode A), --source + --generate + --agents (Mode B), or --pipeline (Pipeline Mode)" |

---

## Invariant Verification Detail

### 1. step_0_pipeline_guard (L499)

**Status**: PASS

The guard is intact at line 499. When `--pipeline` is ABSENT, it sets `pipeline_mode = false` (L508) and proceeds to `step_1_detect_mode` (L509). When `--pipeline` is PRESENT, it sets `pipeline_mode = true` (L504), skips steps 1-4, and routes to the Meta-Orchestrator section (L506). The conflict check at L511-L512 correctly STOPs when `--pipeline` co-occurs with `--compare` or `--source/--generate/--agents`.

### 2. step_1_detect_mode (L515-L520)

**Status**: PASS

Gated by `condition: "pipeline_mode == false"` at L516. Mode A triggers on `--compare` (L517). Mode B triggers on `--source AND --generate AND --agents` (L518). Conflict detection at L519 produces STOP. Missing-flags detection at L520 produces STOP. All four routing paths are intact.

### 3. Invocations #1-#6 (valid routing)

**Status**: PASS

- Mode A parsing (step_2, L522-L532): Split on commas, count validated 2-10, existence checks, type checks.
- Mode B parsing (step_3, L534-L556): Source/generate/agents extracted, missing_flag_error at L539, agent spec format `<model>[:persona[:instruction]]` at L542-L548, count validated 2-10.
- Depth flag correctly wired: `quick` = 1 round, `standard` = 2 rounds, `deep` = 3 rounds (L317, L560, L1046-L1075).

### 4. Invocations #7-#8 (error conditions)

**Status**: PASS

- Invocation #7 (conflict): L519 -- `"If both Mode A and Mode B flags present -> STOP with error"`
- Invocation #8 (missing): L520 -- `"If neither mode detected -> STOP with error"`
- Additional pipeline conflict: L511-L512 -- `"STOP with error: 'Cannot use --pipeline with --compare or --source/--generate/--agents'"`

### 5. Return Contract Fields (9 mandatory)

**Status**: PASS

All 9 fields verified present in the return contract at L404-L413 and the detailed field definitions table at L420-L430:

| Field | Location | Present |
|-------|----------|---------|
| `merged_output_path` | L405, L422 | Yes |
| `convergence_score` | L406, L423 | Yes |
| `artifacts_dir` | L407, L424 | Yes |
| `status` | L408, L425 | Yes |
| `base_variant` | L409, L426 | Yes |
| `unresolved_conflicts` | L410, L427 | Yes |
| `fallback_mode` | L411, L428 | Yes |
| `failure_stage` | L412, L429 | Yes |
| `invocation_method` | L413, L430 | Yes |

The write-on-failure guarantee (L416) is also intact.

### 6. Phase 2 Additions Are Gated

**Status**: PASS

- **Meta-Orchestrator section** (L1961+): Explicitly stated at L1967 as the routing target "When `--pipeline` is detected by `step_0_pipeline_guard`". Only reachable when `pipeline_mode = true`. Inline shorthand parser, YAML loader, DAG builder, cycle detection, reference integrity, and dry-run render are all contained within this section.
- **Shared assumption extraction** (L100-L108, L792-L890): Added as a new sub-step within Step 1 Diff Analysis, after `unique_contribution_extraction`. This is an **addition**, not a replacement. The original four sub-steps (structural_diff, content_diff, contradiction_detection, unique_contribution_extraction) remain intact at L80-L98.
- **A-NNN promotion** (L825-L834): Adds synthetic diff points; does not remove or alter existing S-NNN, C-NNN, X-NNN, U-NNN processing.
- **Advocate prompt ACCEPT/REJECT/QUALIFY** (L946-L967): Added to advocate prompt template as item 6; original items 1-5 unchanged at L939-L945.
- **Three-level taxonomy L1/L2/L3** (L122-L165): Added as `debate_topic_taxonomy` within Step 2 definition; the original debate structure (advocate_instantiation, round_1, round_2, round_3, convergence_detection, scoring_matrix) remains intact at L167-L193.
- **Taxonomy coverage gate** (L1117-L1138): Post-round check; does not replace any existing convergence logic.
- **Convergence formula update** (L1097-L1101): Updated to include A-NNN in denominator, with explicit backward compatibility note: "Debates without shared assumptions produce identical convergence scores (backward compatible)."

No existing protocol steps were removed or replaced.

### 7. Depth Controls

**Status**: PASS

- `quick` = 1 round: L317 ("Controls debate rounds (1/2/3)"), L1047 ("--depth quick -> skip Round 2 entirely"), L1074 ("--depth quick OR --depth standard -> skip [Round 3]")
- `standard` = 2 rounds: L317, L1046 ("--depth standard OR --depth deep" enables Round 2), L1074 (skips Round 3)
- `deep` = 3 rounds: L317, L1072 ("--depth deep AND convergence < configured_threshold after Round 2" enables Round 3)
- Depth values enum: L560 `["quick", "standard", "deep"]` with default "standard"
- Circuit breaker depth reduction: L1903 ("deep -> standard, standard -> quick")

### 8. Min/Max Variants

**Status**: PASS

- Minimum 2: L65 ("minimum 2 required for adversarial comparison"), L375 ("Minimum 2 variants required"), L529 ("Adversarial comparison requires at least 2 files"), L554 ("at least 2 agents"), L1004 (minimum: 2), L1006 ("at least 2 variants"), L1034 ("fewer than 2 advocates remain -> ABORT"), L1819 ("Minimum 2 variants required at all times")
- Maximum 10: L530 ("Maximum 10 files supported"), L555 ("Maximum 10 agents supported"), L1005 (maximum: 10), L1007 ("Maximum 10 variants supported")

---

## Regressions Found

**None.**

All 8 canonical invocations route correctly. All Phase 2 additions (M2: Meta-Orchestrator/pipeline mode, M3: shared assumptions, taxonomy, advocate prompts, convergence formula) are either gated behind `pipeline_mode = true` or are additive extensions to existing protocol steps with no removals or behavioral changes to the non-pipeline path.

---

## Overall Verdict

| Category | Result |
|----------|--------|
| Pipeline guard routing | PASS |
| Mode A/B detection | PASS |
| Valid invocations (1-6) | PASS |
| Error invocations (7-8) | PASS |
| Return contract (9 fields) | PASS |
| Phase 2 gating | PASS |
| Depth controls (1/2/3 rounds) | PASS |
| Min/max variants (2-10) | PASS |
| **OVERALL** | **PASS** |
