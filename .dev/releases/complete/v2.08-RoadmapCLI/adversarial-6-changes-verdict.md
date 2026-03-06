<!-- Provenance: Adversarial debate output -->
<!-- Advocate: Opus (system-architect) — Score: see per-change -->
<!-- Critic: Haiku (system-architect) — Score: see per-change -->
<!-- Adjudication date: 2026-03-05 -->

# Adversarial Debate: 6 Recommended v2.08 Spec Changes

## Debate Summary

**Topic**: Whether to adopt 6 editorial changes to the v2.08-RoadmapCLI spec identified by cross-release impact analysis (v2.03, v2.05, v2.07).

**Advocate** (Opus): Argued for full adoption of all 6 changes. Position: all are low-effort text edits with effectively zero risk.

**Critic** (Haiku): Argued for 2 rejections, 3 reductions, 1 reluctant acceptance. Position: spec is 960+ lines; every addition must earn its place by addressing risks not naturally discoverable during implementation.

**Debate depth**: standard (2 rounds implicit via position + counter-position)

---

## Per-Change Adjudication

### CHANGE-4: Add missing modules to Section 3.1 module listing

| Dimension | Advocate | Critic |
|-----------|----------|--------|
| Position | ADOPT (9/10) | REDUCE (6/10) |
| Core argument | Omission creates extraction ambiguity; prevents over-extraction of sprint-specific modules | Section 3.1 is an extraction diagram, not a file inventory; implementers will discover these files via imports |
| Risk framing | NFR-007 violation if debug_logger.py mistakenly extracted | Precedent problem — listing unchanged files bloats the diagram |

**Verdict: ADOPT (REDUCED FORM)**

The Critic's point about Section 3.1 being an extraction diagram is valid — it should not become a full directory listing. However, the Advocate's NFR-007 concern is real: `debug_logger.py` looks generic and could be mistakenly extracted. The compromise: a single-line comment acknowledging their existence, as the Critic proposed.

**Convergence**: 80%

**Final wording**: Add after the sprint/ module listing in Section 3.1:
```
    # Also in sprint/ (NOT extracted): debug_logger.py, diagnostics.py
```

---

### CHANGE-5: Add computed property chain verification to M2 acceptance criteria

| Dimension | Advocate | Critic |
|-----------|----------|--------|
| Position | ADOPT (8/10) | REJECT (8/10) |
| Core argument | 7 computed properties chain through release_dir alias; current D2.1 only tests the alias itself | D2.4 catches breakage via existing tests; naming 7 properties is implementation detail in acceptance criteria |
| Risk framing | Silent path resolution bugs in production | Maintenance burden; sets precedent for property-level enumeration in specs |

**Verdict: REJECT (with risk note)**

The Critic wins this one. The Advocate's concern about silent path resolution is valid in theory, but the Critic correctly identifies that D2.4 (`uv run pytest tests/sprint/`) already catches this class of failure — sprint tests use `config.results_dir`, `config.output_file()`, etc. in production code paths. If the property chain breaks, existing tests fail. Adding 7 property names to acceptance criteria hardcodes implementation details.

However, the Advocate's underlying concern is worth acknowledging. Add a risk note instead:

**Final wording**: Add to M2 Risk Assessment (not acceptance criteria):
```
| release_dir alias chain resolution | Low | Medium | Property alias must resolve transitively for all SprintConfig computed properties that depend on release_dir; existing sprint tests exercise these paths |
```

**Convergence**: 65%

---

### CHANGE-6: Update executor line count and sprint_run_step complexity in Section 13.5

| Dimension | Advocate | Critic |
|-----------|----------|--------|
| Position | ADOPT (9/10) | REDUCE (7/10) |
| Core argument | "~100 lines" is factually wrong (~180); omits 4 critical behaviors | Line counts are fragile; the (a)-(d) checklist belongs in tasklists, not specs |
| Risk framing | Implementer underestimates M2 migration complexity | Section becomes an implementation checklist rather than design rationale |

**Verdict: ADOPT (REDUCED FORM)**

Both sides agree the line count is wrong. The Critic's objection to the (a)-(d) checklist has merit — Section 13.5 is about the composition pattern, not implementation checklists. But the Advocate is right that ~100 is misleading by 80%. The compromise: fix the number and add a brief behavioral note without the full checklist.

**Convergence**: 75%

**Final wording**: Replace Section 13.5's sprint_run_step comment with:
```python
    def sprint_run_step(step, pipeline_config, cancel_check):
        # Sprint's existing poll loop: ~180 lines including debug logging,
        # stall watchdog, TUI error resilience, and diagnostic collection.
        # See executor.py for the full orchestration surface.
        ...
        return StepResult(...)
```

---

### CHANGE-7: Add debug_log() removal note to migration strategy

| Dimension | Advocate | Critic |
|-----------|----------|--------|
| Position | ADOPT WITH MODS (6/10) | ACCEPT RELUCTANTLY (4/10) |
| Core argument | process.py has 6 debug_log() calls; NFR-07 makes this a hard constraint | Self-correcting failure (ImportError); one line in migration strategy is worth the cost |
| Risk framing | 15-30 minutes of wasted implementation time | Minor spec bloat |

**Verdict: ADOPT**

Both sides converge on acceptance. The Critic agrees this is the one change addressing a compile-time blocker. The Advocate's modified wording (less prescriptive, mentioning stdlib logging as an option) addresses the Critic's concern about over-constraining the solution.

**Convergence**: 90%

**Final wording**: Add to Section 12, after step 2:
```
Note: sprint/process.py contains debug_log() calls tied to sprint's debug logger.
When extracting ClaudeProcess to pipeline/process.py, replace with stdlib logging
or remove (NFR-007 prohibits pipeline/ from importing sprint modules).
```

---

### CHANGE-8: Add monitor coupling annotation

| Dimension | Advocate | Critic |
|-----------|----------|--------|
| Position | ADOPT (7/10) | REJECT (8/10) |
| Core argument | 199 lines of NDJSON-specific parsing; annotation prevents extraction mistakes | YAGNI — nobody proposes extracting monitor.py; coupling info already in the module docstring |
| Risk framing | Future scope creep if someone tries to generalize the monitor | Precedent for annotating every unchanged module |

**Verdict: REJECT**

The Critic wins decisively. The monitor.py docstring already documents the stream-json coupling. The spec says monitor.py is "unchanged." Nobody is proposing to extract it. Annotating why an unchanged file is unchanged is defensive documentation that the Critic correctly identifies as YAGNI. If a future implementer considers extracting monitor.py, they will read the file and discover the coupling in 6 lines.

**Convergence**: 60%

**Final wording**: No change.

---

### CHANGE-9: Add stall watchdog regression test to M2 acceptance criteria

| Dimension | Advocate | Critic |
|-----------|----------|--------|
| Position | ADOPT (8/10) | REDUCE (7/10) |
| Core argument | Watchdog is 37 lines with warn/kill modes; could silently regress; D2.4 only ensures existing tests pass | D2.4 already covers; mandating new tests expands M2 scope |
| Risk framing | Silent watchdog regression in production | M2 scope creep from "zero-regression" to "improve test coverage" |

**Verdict: ADOPT (REDUCED FORM)**

The Critic's scope concern is valid — M2 should not become a "write new sprint tests" milestone. But the Advocate raises a real point: if existing tests lack watchdog coverage, D2.4 provides no protection. The compromise: conditional wording that verifies existing coverage without mandating new tests.

**Convergence**: 75%

**Final wording**: Add to D2.4 acceptance criteria:
```
Stall watchdog behavior (--stall-timeout, --stall-action) exercised by existing
sprint tests continues to pass post-migration.
```

---

## Final Verdict Summary

| Change | Advocate | Critic | Verdict | Action |
|--------|----------|--------|---------|--------|
| **4** (missing modules) | ADOPT 9/10 | REDUCE 6/10 | **ADOPT REDUCED** | Add 1-line comment to Section 3.1 |
| **5** (property chain) | ADOPT 8/10 | REJECT 8/10 | **REJECT** | Add risk note to M2 instead |
| **6** (executor lines) | ADOPT 9/10 | REDUCE 7/10 | **ADOPT REDUCED** | Fix line count + brief behavioral note |
| **7** (debug_log note) | ADOPT 6/10 | ACCEPT 4/10 | **ADOPT** | Add 2-line note to Section 12 |
| **8** (monitor coupling) | ADOPT 7/10 | REJECT 8/10 | **REJECT** | No change |
| **9** (watchdog test) | ADOPT 8/10 | REDUCE 7/10 | **ADOPT REDUCED** | Conditional wording in D2.4 |

### Changes to Apply: 4 (of 6)

| Priority | Change | Effort | Location |
|----------|--------|--------|----------|
| 1 | CHANGE-6: Fix line count ~100→~180 + behavioral note | 1 edit | merged-spec.md Section 13.5 |
| 2 | CHANGE-7: debug_log() removal note | 1 edit | merged-spec.md Section 12 |
| 3 | CHANGE-4: Comment listing sprint-only modules | 1 edit | merged-spec.md Section 3.1 |
| 4 | CHANGE-9: Conditional watchdog test wording | 1 edit | roadmap.md D2.4 |

### Rejected: 2

| Change | Reason |
|--------|--------|
| CHANGE-5 | D2.4 already catches property chain breakage; risk note added instead |
| CHANGE-8 | YAGNI; monitor.py docstring already documents coupling |

### Additional Action (from CHANGE-5 rejection)

Add 1 risk row to M2 risk assessment table (not acceptance criteria).
