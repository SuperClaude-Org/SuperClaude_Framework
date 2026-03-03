---
spec_sources:
  - .dev/releases/current/v2.05-sprint-cli-specification/sprint-cli-specification.md
  - .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/roadmap.md
generated: 2026-03-03T00:00:00Z
generator: sc:roadmap
functional_requirements: 46
nonfunctional_requirements: 12
total_requirements: 58
domains_detected: [backend, infrastructure, performance, documentation, frontend, security]
complexity_score: 0.845
complexity_class: HIGH
risks_identified: 16
dependencies_identified: 16
success_criteria_count: 25
extraction_mode: chunked (multi-spec consolidated)
---

# Extraction Report: Sprint CLI + Cleanup Audit v2

## Overview

This extraction consolidates two complementary specifications into a unified requirements set:

1. **Sprint CLI Specification** (v1.0, 2053 lines): Design specification for `superclaude sprint` — a multi-phase orchestration CLI that executes Claude Code sessions sequentially with Rich TUI dashboard, tmux integration, sidecar monitoring, and structured logging.

2. **Cleanup Audit v2 Roadmap** (397 lines): Existing roadmap for sc:cleanup-audit v2 improvements — scanner hardening, structural analysis, cross-reference synthesis, budget controls, and validation infrastructure.

**Consolidation Assessment**: Zero functional overlap — Spec 1 defines a new CLI tool, Spec 2 defines improvements to an existing audit command. Convergence score 0.85 (high confidence, complementary feature sets).

---

## Functional Requirements

### Sprint CLI Domain (Spec 1)

| ID | Description | Priority | Source Lines |
|---|---|---|---|
| FR-001 | Provide `sprint` subcommand group integrated into existing `superclaude` Click CLI via `main.add_command()` | P0 | L270-281 |
| FR-002 | `sprint run` accepts INDEX_PATH positional arg + flags: `--start`, `--end`, `--max-turns`, `--model`, `--dry-run`, `--no-tmux`, `--permission-flag` | P0 | L310-343 |
| FR-003 | `sprint attach` reconnects to running `sc-sprint-*` tmux session | P1 | L369-376 |
| FR-004 | `sprint status` reads JSONL execution log to display phase completion without tmux attachment | P1 | L379-387 |
| FR-005 | `sprint logs` tails human-readable execution log with `--lines N` and `--follow` flags | P1 | L389-401 |
| FR-006 | `sprint kill` sends SIGTERM with 10s grace period, then SIGKILL; `--force` skips grace period | P1 | L403-414 |
| FR-007 | Rich-based TUI dashboard with phase table, overall progress bar, and active phase detail panel | P0 | L429-534 |
| FR-008 | TUI renders phase status with color-coded styles: green (PASS), red (HALT/ERROR), yellow (RUNNING), dim (pending) | P1 | L470-504 |
| FR-009 | Stall detection with visual warning when output stops growing for >60s (bold red blink) | P1 | L496-504 |
| FR-010 | Sprint complete state shows final summary with all-phases status and log path | P1 | L506-534 |
| FR-011 | Sprint halted state shows halt reason, resume command, and result file path | P1 | L536-548 |
| FR-012 | Tmux session naming: `sc-sprint-{SHA1(release_dir)[:8]}` for concurrent sprint support | P0 | L745-747 |
| FR-013 | Tmux pane layout: 75% TUI dashboard (top), 25% raw output tail (bottom) | P1 | L750-765 |
| FR-014 | Auto-detect tmux availability; fall back to foreground if tmux unavailable or `--no-tmux` set | P0 | L778-786 |
| FR-015 | Tmux tail pane updates automatically when executor starts a new phase | P1 | L871-886 |
| FR-016 | Sidecar monitor thread polls output file every 500ms extracting: task IDs, tool names, file changes, line counts | P0 | L927-1059 |
| FR-017 | Monitor tracks output growth rate (exponential moving average) and stall duration | P1 | L1020-1027 |
| FR-018 | Monitor reads only new bytes since last poll (incremental read via file seek) | P1 | L1028-1037 |
| FR-019 | Process management via subprocess.Popen with process groups (`os.setpgrp`) for clean tree kill | P0 | L1096-1250 |
| FR-020 | Timeout computed as `max_turns * 120s + 300s` buffer; exit code 124 on timeout (matches bash) | P0 | L1127-1130 |
| FR-021 | Graceful shutdown: SIGTERM → 10s wait → SIGKILL to process group | P0 | L1216-1243 |
| FR-022 | Signal handler for SIGINT/SIGTERM that sets shutdown flag checked by executor loop | P0 | L1252-1283 |
| FR-023 | Executor core loop: for each phase → launch subprocess → monitor → parse result → CONTINUE/HALT decision | P0 | L1287-1461 |
| FR-024 | Phase status determination priority: timeout(124) → non-zero exit → HALT signal → CONTINUE signal → no-report fallback | P0 | L1423-1460 |
| FR-025 | Build `/sc:task-unified` prompt per phase with compliance strict, systematic strategy, tier-based execution rules | P0 | L1131-1162 |
| FR-026 | Phase completion protocol: YAML frontmatter result file with status, task counts, files modified, EXIT_RECOMMENDATION | P0 | L1149-1162 |
| FR-027 | Dual logging: JSONL (machine-readable) + Markdown (human-readable) with phase-by-phase rows | P0 | L1464-1592 |
| FR-028 | Log levels: DEBUG (JSONL only), INFO (all), WARN (highlighted), ERROR (highlighted + terminal bell) | P1 | L1482-1487 |
| FR-029 | Phase discovery via regex: matches `phase-N-tasklist.md`, `pN-tasklist.md`, `Phase_N_tasklist.md`, `tasklist-PN.md` | P0 | L1596-1651 |
| FR-030 | Two-strategy phase discovery: grep index file first, fall back to directory scan | P0 | L1619-1650 |
| FR-031 | Validation: check phase files exist, detect sequence gaps, enrich with heading names | P1 | L1667-1692 |
| FR-032 | Desktop notifications: cross-platform (notify-send on Linux, osascript on macOS), best-effort | P2 | L1751-1816 |
| FR-033 | Dry-run mode: show discovered phases without executing | P1 | L358-360 |
| FR-034 | Migration Phase 1: ship Python implementation in v4.3.0 | P0 | L2005-2011 |
| FR-035 | Migration Phase 2: replace execute-sprint.sh with thin shim forwarding to Python | P1 | L2013-2028 |
| FR-036 | Migration Phase 3: remove bash shim and update docs in v4.4.0 | P2 | L2030-2035 |

### Cleanup Audit v2 Domain (Spec 2)

| ID | Description | Priority | Source |
|---|---|---|---|
| FR-037 | Enforce v1-promised behaviors: two-tier classification, coverage tracking, batch checkpointing, evidence-gated rules, 10% validation | P0 | M1 |
| FR-038 | Correctness fixes: real credential scanning, gitignore detection, scanner schema hardening, batch retry policy | P0 | M2 |
| FR-039 | Phase-0 profiling: domain/risk-tier profiling, monorepo batch decomposition, auto-config generation, dry-run estimates | P1 | M3 |
| FR-040 | Structural audit depth: 8-field profiles, file-type verification, signal-triggered escalation, tiered KEEP evidence | P1 | M4 |
| FR-041 | Cross-reference synthesis: 3-tier dependency graph, dead code candidates, duplication matrix, docs audit, dynamic-import safety | P1 | M5 |
| FR-042 | Consolidation engine: cross-phase dedup, stratified 10% spot-check, coverage + validation artifacts, directory assessments | P1 | M6 |
| FR-043 | Budget controls: budget accounting, degradation sequence, degrade-priority override, budget realism reporting | P1 | M7 |
| FR-044 | Reporting and resume: report depth modes, resume from checkpoints, anti-lazy guards, report completeness checks | P2 | M8 |
| FR-045 | Optional full docs audit: `--pass-docs` with 5-section output, known-issues registry with TTL/LRU lifecycle | P3 | M9 |
| FR-046 | Final acceptance: AC1-AC20 automated validation suite, benchmark runs, concurrent-run isolation, limitations reporting | P1 | M10 |

---

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source |
|---|---|---|---|---|
| NFR-001 | TUI refresh rate must maintain smooth display during active monitoring | performance | 2 FPS (500ms polling cycle) | Spec1 L601 |
| NFR-002 | Monitor thread must not block main thread or TUI updates | reliability | Daemon thread, atomic field writes, no locks | Spec1 L1092 |
| NFR-003 | Process shutdown must complete within bounded time | reliability | SIGTERM + 10s + SIGKILL + 5s = max 15s | Spec1 L1216-1243 |
| NFR-004 | No new external dependencies beyond existing click and rich | maintainability | stdlib only for new modules | Spec1 L2038-2042 |
| NFR-005 | Sprint must survive SSH disconnects when running in tmux | reliability | Tmux detach/reattach preserves state | Spec1 L916-923 |
| NFR-006 | Multiple concurrent sprints on different release directories | scalability | Hash-based tmux session naming | Spec1 L746-747 |
| NFR-007 | Total implementation ~2,160 lines across 11 files | maintainability | Estimated scope constraint | Spec1 L47 |
| NFR-008 | Desktop notifications must fail silently | reliability | Best-effort, 5s timeout, no exceptions propagated | Spec1 L1763-1784 |
| NFR-009 | Monitor reads only incremental output (no re-reading entire file) | performance | Seek-based incremental read | Spec1 L1028-1037 |
| NFR-010 | Cleanup audit budget accounting must enforce predictable degradation | performance | Defined degradation sequence | Spec2 M7 |
| NFR-011 | Token budget estimation must support dry-run preview mode | performance | Pre-execution cost estimate | Spec2 M3 |
| NFR-012 | Credential scanning must never expose secret values in output | security | Non-disclosure policy + output scrub checks | Spec2 M2 |

---

## Dependencies

| ID | Description | Type | Affected FRs |
|---|---|---|---|
| DEP-001 | Sprint CLI depends on existing `superclaude` Click group in main.py | internal | FR-001 |
| DEP-002 | TUI depends on Rich library (already a project dependency) | external | FR-007, FR-008 |
| DEP-003 | Tmux integration depends on tmux binary availability on host | external | FR-012, FR-013, FR-014 |
| DEP-004 | Process management depends on POSIX signal support (Linux/macOS) | external | FR-019, FR-021, FR-022 |
| DEP-005 | Phase discovery depends on tasklist-index.md naming convention | internal | FR-029, FR-030 |
| DEP-006 | Executor depends on `claude` CLI binary being in PATH | external | FR-023, FR-025 |
| DEP-007 | Phase prompt depends on `/sc:task-unified` command availability | internal | FR-025 |
| DEP-008 | Monitor signal extraction depends on Claude output format patterns | internal | FR-016 |
| DEP-009 | Desktop notifications depend on platform-specific tools (notify-send, osascript) | external | FR-032 |
| DEP-010 | Migration shim depends on Python sprint being fully functional | internal | FR-034 → FR-035 |
| DEP-011 | Cleanup audit M2 depends on M1 (v1 promise enforcement) | internal | FR-037 → FR-038 |
| DEP-012 | Cleanup audit M3-M5 form sequential dependency chain | internal | FR-039 → FR-040 → FR-041 |
| DEP-013 | Cleanup audit M7 depends on M3, M4, M5 (budget needs profiling + depth + synthesis) | internal | FR-043 |
| DEP-014 | Cleanup audit M10 depends on all prior milestones M1-M8 | internal | FR-046 |
| DEP-015 | Sprint test suite depends on pytest and tmp_path fixture | external | FR-034 |
| DEP-016 | Cleanup audit cross-reference synthesis depends on static tools (grep, AST) | external | FR-041 |

---

## Success Criteria

| ID | Criterion | Derived From | Measurable |
|---|---|---|---|
| SC-001 | `superclaude sprint run` discovers and executes all phases from a tasklist-index | FR-001, FR-002, FR-023 | Yes |
| SC-002 | TUI displays real-time phase progress with status colors and active panel | FR-007, FR-008 | Yes |
| SC-003 | Sprint survives SSH disconnect and is resumable via `sprint attach` | FR-003, FR-014, NFR-005 | Yes |
| SC-004 | Stall detection triggers visual warning after 60s no output growth | FR-009, FR-017 | Yes |
| SC-005 | HALT on STRICT-tier failure stops execution and shows resume command | FR-011, FR-024 | Yes |
| SC-006 | Multiple concurrent sprints run isolated via unique tmux sessions | FR-012, NFR-006 | Yes |
| SC-007 | Phase discovery handles all 4 naming conventions | FR-029, FR-030 | Yes |
| SC-008 | Dual JSONL + Markdown logs capture all phase events | FR-027, FR-028 | Yes |
| SC-009 | Process cleanup terminates entire child tree on shutdown | FR-019, FR-021, NFR-003 | Yes |
| SC-010 | Dry-run mode shows phases without execution | FR-033 | Yes |
| SC-011 | Desktop notifications fire on phase completion and sprint completion | FR-032 | Yes |
| SC-012 | No new external dependencies introduced | NFR-004 | Yes |
| SC-013 | All 9 test files pass with >80% coverage | FR-034 | Yes |
| SC-014 | Migration shim correctly forwards to Python implementation | FR-035 | Yes |
| SC-015 | Cleanup audit report includes core action sections | FR-037 | Yes |
| SC-016 | Coverage artifact includes per-tier metrics | FR-037, FR-042 | Yes |
| SC-017 | DELETE entries carry zero-reference evidence | FR-037, FR-041 | Yes |
| SC-018 | Budget-limited runs complete gracefully with degradation | FR-043, NFR-010 | Yes |
| SC-019 | Credential scanning distinguishes real vs template | FR-038, NFR-012 | Yes |
| SC-020 | Dependency graph emitted with valid nodes and confidence labels | FR-041 | Yes |
| SC-021 | Cold-start audit succeeds without pre-existing config | FR-039 | Yes |
| SC-022 | Validation sample meets >=10% threshold | FR-042 | Yes |
| SC-023 | Dry-run audit returns estimates only | FR-039 | Yes |
| SC-024 | Concurrent audit runs remain isolated | FR-046 | Yes |
| SC-025 | AC1-AC20 automated validation suite passes | FR-046 | Yes |

---

## Risks

| ID | Risk | Probability | Impact | Affected FRs | Source |
|---|---|---|---|---|---|
| RISK-001 | Claude output format changes break monitor signal extraction patterns | Medium | High | FR-016 | Inferred |
| RISK-002 | Tmux version incompatibilities across Linux/macOS distributions | Low | Medium | FR-012, FR-013 | Inferred |
| RISK-003 | Process group kill may leave orphaned grandchild processes | Low | High | FR-019, FR-021 | Inferred |
| RISK-004 | Rich Live display flickers or corrupts on narrow terminals | Low | Medium | FR-007, FR-008 | Inferred |
| RISK-005 | Phase file naming convention too rigid, missing valid patterns | Medium | Medium | FR-029, FR-030 | Explicit (Spec1 L2046-2053) |
| RISK-006 | Timeout calculation (`max_turns * 120 + 300`) may be too aggressive or too loose | Medium | Medium | FR-020 | Inferred |
| RISK-007 | GIL-reliance for thread safety in monitor-TUI communication may break on future Python | Low | Medium | FR-016, NFR-002 | Explicit (Spec1 L1092) |
| RISK-008 | Token budget underestimation for cleanup audit phases | High | High | FR-043 | Explicit (Spec2 R-001) |
| RISK-009 | Spec-implementation gap recurrence in cleanup audit | High | High | FR-037 | Explicit (Spec2 R-002) |
| RISK-010 | Schema malformation from Haiku outputs in scanner | Medium | Medium | FR-038 | Explicit (Spec2 R-003) |
| RISK-011 | Dynamic import false positives in cross-reference synthesis | Medium | High | FR-041 | Explicit (Spec2 R-004) |
| RISK-012 | Large-repo scaling limits in cleanup audit | High | High | FR-039, FR-043 | Explicit (Spec2 R-005) |
| RISK-013 | Context-window pressure during synthesis/consolidation phases | High | High | FR-041, FR-042 | Explicit (Spec2 R-006) |
| RISK-014 | Credential value exposure in audit output | Low | High | FR-038 | Explicit (Spec2 R-007) |
| RISK-015 | Validation results interpreted as accuracy (misleading) | Medium | Medium | FR-042, FR-046 | Explicit (Spec2 R-008) |
| RISK-016 | Migration breaks existing execute-sprint.sh users | Medium | Medium | FR-034, FR-035 | Inferred |

---

## Complexity Analysis

### Factor Breakdown

| Factor | Raw | Normalized | Weight | Weighted |
|---|---|---|---|---|
| requirement_count | 58 (46 FR + 12 NFR) | 1.00 | 0.25 | 0.250 |
| dependency_depth | 6 (longest chain: M1→M2→M3→M4→M5→M6) | 0.75 | 0.25 | 0.188 |
| domain_spread | 4 domains ≥10% | 0.80 | 0.20 | 0.160 |
| risk_severity | 2.28 weighted avg | 0.64 | 0.15 | 0.096 |
| scope_size | 2450 lines | 1.00 | 0.15 | 0.150 |

**Total Complexity Score: 0.845**

**Classification: HIGH** → 8-12 milestones, 1:1 test interleave ratio

### Domain Distribution Chart

```
backend        ████████████████████████████████████████░░  42%
infrastructure ██████████████████████░░░░░░░░░░░░░░░░░░░░  22%
performance    ██████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  14%
documentation  ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  10%
frontend       ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   8%
security       ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   4%
```

### Persona Assignment

| Role | Persona | Confidence | Rationale |
|---|---|---|---|
| Primary | backend | 0.59 | Dominant domain at 42% — CLI, process management, executor |
| Consulting | architect | 0.35 | Cross-cutting system design, dependency orchestration |
| Consulting | devops | 0.31 | Infrastructure domain at 22% — tmux, subprocess, signals |
