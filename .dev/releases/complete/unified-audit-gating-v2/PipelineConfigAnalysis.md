 Sprint Pipeline Configuration Analysis                                 
                                                                         
  1. max_turns Default: 50 → 100                                         
                                                                  
  Source of Truth Chain

  There are 4 source-of-truth defaults that independently set max_turns =
   50:

  ┌───────┬────────────────────────────┬─────┬──────────────────────┐
  │ Prior │            File            │ Lin │         Role         │
  │  ity  │                            │  e  │                      │
  ├───────┼────────────────────────────┼─────┼──────────────────────┤
  │       │ src/superclaude/cli/pipeli │     │ PipelineConfig.max_t │
  │ S1    │ ne/models.py               │ 175 │ urns: int = 50 —     │
  │       │                            │     │ base class default   │
  ├───────┼────────────────────────────┼─────┼──────────────────────┤
  │       │                            │     │ SprintConfig.max_tur │
  │ S2    │ src/superclaude/cli/sprint │ 285 │ ns: int = 50 —       │
  │       │ /models.py                 │     │ overrides S1         │
  │       │                            │     │ (re-declares)        │
  ├───────┼────────────────────────────┼─────┼──────────────────────┤
  │       │ src/superclaude/cli/sprint │     │ Click --max-turns    │
  │ S3    │ /commands.py               │ 54  │ default=50 — CLI     │
  │       │                            │     │ entry point          │
  ├───────┼────────────────────────────┼─────┼──────────────────────┤
  │       │                            │     │ load_sprint_config(m │
  │ S4    │ src/superclaude/cli/sprint │ 108 │ ax_turns: int = 50)  │
  │       │ /config.py                 │     │ — function signature │
  │       │                            │     │  default             │
  └───────┴────────────────────────────┴─────┴──────────────────────┘

  Additionally, one derived default in the pipeline layer:

  ┌───────┬────────────────────────────┬─────┬────────────────────────┐
  │ Prior │            File            │ Lin │          Role          │
  │  ity  │                            │  e  │                        │
  ├───────┼────────────────────────────┼─────┼────────────────────────┤
  │       │ src/superclaude/cli/pipeli │     │ ClaudeProcess.__init__ │
  │ D1    │ ne/process.py              │ 43  │ (max_turns: int = 50)  │
  │       │                            │     │ — constructor default  │
  └───────┴────────────────────────────┴─────┴────────────────────────┘

  Derived Values (NOT separate defaults — computed from config.max_turns)

  - executor.py:77 — timeout_seconds=self._config.max_turns * 60
  (SprintGatePolicy)
  - process.py:108 — timeout_seconds=config.max_turns * 120 + 300 (sprint
   ClaudeProcess)
  - executor.py:478 — timeout_seconds=config.max_turns * 120 + 300
  (_run_task_subprocess)

  These are correctly derived from config.max_turns and need no edits.

  initial_budget and max_turns Relationship

  They are INDEPENDENT. TurnLedger.initial_budget is a required
  positional argument with no default — callers explicitly set it. There
  is no formula like initial_budget = max_turns * N. Changing max_turns
  does not require changing initial_budget.

  However, there is a practical concern: with max_turns=100 and a 9-phase
   sprint, a single phase could consume up to 100 turns. If
  initial_budget remains small (e.g., 200), budget exhaustion happens
  faster. This is a tuning question, not a bug.

  Test Files Asserting max_turns == 50

  ┌───────────────────────────────────┬──────┬───────────────────────┐
  │               File                │ Line │         Type          │
  ├───────────────────────────────────┼──────┼───────────────────────┤
  │ tests/sprint/test_models.py       │ 188  │ assert cfg.max_turns  │
  │                                   │      │ == 50                 │
  ├───────────────────────────────────┼──────┼───────────────────────┤
  │                                   │      │ assert                │
  │ tests/sprint/test_config.py       │ 215  │ config.max_turns ==   │
  │                                   │      │ 50                    │
  ├───────────────────────────────────┼──────┼───────────────────────┤
  │ tests/pipeline/test_models.py     │ 54   │ assert cfg.max_turns  │
  │                                   │      │ == 50                 │
  ├───────────────────────────────────┼──────┼───────────────────────┤
  │ tests/sprint/test_e2e_trailing.py │ 88   │ max_turns=50          │
  │                                   │      │ (fixture, explicit)   │
  ├───────────────────────────────────┼──────┼───────────────────────┤
  │ tests/sprint/test_process.py      │ 31,  │ max_turns=50          │
  │                                   │ 92   │ (fixture, explicit)   │
  ├───────────────────────────────────┼──────┼───────────────────────┤
  │ tests/pipeline/test_process.py    │ 116  │ max_turns=50          │
  │                                   │      │ (fixture, explicit)   │
  └───────────────────────────────────┴──────┴───────────────────────┘

  The first 3 are default-assertion tests that must be updated. The last
  3 are explicit values in fixtures — these are intentional test
  parameters, not default-dependent, and do not need updating (they test
  specific scenarios, not defaults).

  ---
  2. reimbursement_rate Default: 0.5 → 0.8

  Source of Truth

  ┌───────┬────────────────────────────┬─────┬───────────────┬──────┐
  │ Prior │            File            │ Lin │    Current    │ Targ │
  │  ity  │                            │  e  │               │  et  │
  ├───────┼────────────────────────────┼─────┼───────────────┼──────┤
  │       │ src/superclaude/cli/sprint │     │ reimbursement │      │
  │ S1    │ /models.py                 │ 476 │ _rate: float  │ 0.8  │
  │       │                            │     │ = 0.5         │      │
  └───────┴────────────────────────────┴─────┴───────────────┴──────┘

  This is the sole source of truth. All callers either inherit this
  default or explicitly override it.

  Spec vs Implementation Discrepancy

  The spec (unified-spec-v1.0.md:178) says reimbursement_rate: float =
  0.90 (90%), but the implementation uses 0.5. Your target of 0.8 is a
  middle ground. The spec's mathematical proof in section 3.4 (lines
  225-235) is written for 90%:

  net_cost_per_task = (actual_turns × 0.10) + overhead_turns
                    = (8 × 0.10) + 2 = 2.8 turns per passing task
  For 46 tasks: ~129 turns drain. 200-turn budget sustains with ~71
  margin.

  Mathematical Invariant Analysis at 0.8

  Does budget still monotonically decay? Yes. rate < 1.0 guarantees
  net_cost > 0.

  At 0.8:
  net_cost_per_task = (actual_turns × 0.20) + overhead_turns
                    = (8 × 0.20) + 2 = 3.6 turns per passing task
  For 46 tasks: ~166 turns drain. 200-turn budget sustains with ~34
  margin.

  At 0.5 (current):
  net_cost_per_task = (8 × 0.50) + 2 = 6 turns per passing task
  For 46 tasks: ~276 turns drain. 200-turn budget DOES NOT sustain —
  exhaustion at ~33 tasks.

  Key insight: 0.5 is actually too aggressive — it causes budget
  exhaustion before completing a 46-task sprint with a 200-turn budget.
  Moving to 0.8 is a correctness improvement that better aligns with the
  spec's intent.

  Minimum allocation / remediation guards: Unaffected.
  minimum_allocation=5 and minimum_remediation_budget=3 are absolute
  thresholds checked against available(), not against the rate. They work
   correctly at any rate.

  Runaway sprint prevention: At 0.8, each task still costs net turns *
  0.2 + overhead. The series sum(0.8^n) converges to 5 * initial_cost, so
   even with maximum theoretical reimbursement chaining, the total cost
  is bounded. No infinite run is possible.

  Test Files Asserting reimbursement_rate == 0.5

  ┌──────────────────────────┬─────┬────────────────────────┬───────┐
  │           File           │ Lin │          Type          │ Impac │
  │                          │  e  │                        │   t   │
  ├──────────────────────────┼─────┼────────────────────────┼───────┤
  │ tests/sprint/test_models │     │ assert ledger.reimburs │ Must  │
  │ .py                      │ 527 │ ement_rate == 0.5      │ updat │
  │                          │     │                        │ e     │
  └──────────────────────────┴─────┴────────────────────────┴───────┘

  Test Files Using reimbursement_rate Implicitly (via default)

  File: tests/pipeline/test_full_flow.py
  Lines: 97, 309
  What it does: int(10 * ledger.reimbursement_rate) — uses the default;
    assertions check reimbursed == reimbursement which is derived from
    rate, so these auto-adjust correctly

  The test_full_flow.py tests are well-written: they compute expected
  values from ledger.reimbursement_rate rather than hardcoding 5. They
  will pass at any rate.

  ---
  3. Ranked Edit List

  Tier 1: Source-of-Truth Defaults (MUST change)

  #: 1
  File: src/superclaude/cli/pipeline/models.py
  Line: 175
  Current: max_turns: int = 50
  New: max_turns: int = 100
  Risk: Low — base class default
  ────────────────────────────────────────
  #: 2
  File: src/superclaude/cli/sprint/models.py
  Line: 285
  Current: max_turns: int = 50
  New: max_turns: int = 100
  Risk: Low — overrides base
  ────────────────────────────────────────
  #: 3
  File: src/superclaude/cli/sprint/commands.py
  Line: 54
  Current: default=50
  New: default=100
  Risk: Low — CLI entry point
  ────────────────────────────────────────
  #: 4
  File: src/superclaude/cli/sprint/commands.py
  Line: 55
  Current: help="Max agent turns per phase (default: 50)"
  New: help="Max agent turns per phase (default: 100)"
  Risk: Low — help text
  ────────────────────────────────────────
  #: 5
  File: src/superclaude/cli/sprint/config.py
  Line: 108
  Current: max_turns: int = 50
  New: max_turns: int = 100
  Risk: Low — function default
  ────────────────────────────────────────
  #: 6
  File: src/superclaude/cli/pipeline/process.py
  Line: 43
  Current: max_turns: int = 50
  New: max_turns: int = 100
  Risk: Low — constructor default
  ────────────────────────────────────────
  #: 7
  File: src/superclaude/cli/sprint/models.py
  Line: 476
  Current: reimbursement_rate: float = 0.5
  New: reimbursement_rate: float = 0.8
  Risk: See note below

  Tier 2: Test Default Assertions (MUST update to match)

  #: 8
  File: tests/pipeline/test_models.py
  Line: 54
  Current: assert cfg.max_turns == 50
  New: assert cfg.max_turns == 100
  Risk: None
  ────────────────────────────────────────
  #: 9
  File: tests/sprint/test_models.py
  Line: 188
  Current: assert cfg.max_turns == 50
  New: assert cfg.max_turns == 100
  Risk: None
  ────────────────────────────────────────
  #: 10
  File: tests/sprint/test_config.py
  Line: 215
  Current: assert config.max_turns == 50
  New: assert config.max_turns == 100
  Risk: None
  ────────────────────────────────────────
  #: 11
  File: tests/sprint/test_models.py
  Line: 527
  Current: assert ledger.reimbursement_rate == 0.5
  New: assert ledger.reimbursement_rate == 0.8
  Risk: None

  Tier 3: No Changes Needed

  These files use explicit values in fixtures (not default-dependent) or
  dynamically compute from ledger.reimbursement_rate:

  - tests/sprint/test_e2e_trailing.py:88 — explicit max_turns=50 in
  fixture (intentional test parameter)
  - tests/sprint/test_process.py:31,92 — explicit max_turns=50 in fixture
  - tests/pipeline/test_process.py:116 — explicit max_turns=50 in fixture
  - tests/pipeline/test_full_flow.py:97,309 — computes from
  ledger.reimbursement_rate, auto-adjusts
  - All TurnLedger(initial_budget=N) constructions — initial_budget is
  independent of both changes

  ---
  4. Flags / Warnings

  Item: Spec proof (NFR-008)
  Severity: Info
  Details: The mathematical proof in unified-spec-v1.0.md:225-235 uses
  90%
    rate. At 0.8, the proof is stronger (faster decay), so it remains
    valid. No update needed for correctness, but the numbers in the prose

    (2.8 turns, ~129 turns) become inaccurate. Consider updating spec
  docs
     if accuracy matters.
  ────────────────────────────────────────
  Item: Timeout scaling
  Severity: Info
  Details: timeout_seconds = max_turns * 120 + 300 — at max_turns=100
  this
    becomes 12,300s (~3.4 hours) per phase. This is derived and correct,
    but verify this is acceptable for your use case.
  ────────────────────────────────────────
  Item: Budget adequacy
  Severity: Warning
  Details: At reimbursement_rate=0.8 with max_turns=100, a single task
    could consume up to 100 turns with only 80 reimbursed (net cost: 20).

    Sprints with many tasks need initial_budget scaled accordingly. The
    current code requires callers to set initial_budget explicitly, so
    this is a tuning concern, not a code change.

  Total edits: 11 (7 source, 4 tests). All are simple value replacements.
   No structural changes, no new files, no logic changes.