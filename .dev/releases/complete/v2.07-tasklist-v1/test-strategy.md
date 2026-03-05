---
spec_source: ".dev/releases/current/v2.07-tasklist-v1/sc-tasklist-command-spec-v1.0.md"
generated: "2026-03-05T01:40:00Z"
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 2
work_milestones: 5
interleave_ratio: "1:2"
major_issue_policy: stop-and-fix
complexity_class: MEDIUM
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is **1:2** (one validation milestone per 2 work milestones), derived from complexity class MEDIUM (0.571)

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M2 (Command Layer) + M3 (Skill Layer) | Command/skill pairing, lint-architecture, frontmatter validity, bidirectional references | Any lint check failure; missing `## Activation` section; SKILL.md frontmatter invalid; `name:` not ending in `-protocol` |
| V2 | M5 (Output Validation & Sprint Compatibility) | Full acceptance criteria (SC-001–SC-013); output parity; Sprint CLI compatibility; quality gates | Any SC-### failure; output diff against v3.0 produces functional delta; `sprint run` cannot discover phase files |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. V1 validates M2+M3 (the command/skill core). V2 validates M4+M5 (tooling integration and output quality).

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Algorithm drift producing non-identical output (RISK-001); lint-architecture rule failure with no workaround (RISK-003); Sprint CLI cannot discover phase files (RISK-004) |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Command file exceeds 500-line hard fail (RISK-007/FR-074); pre-write quality gate undefined (RISK-008); `__init__.py` triggers unintended package imports (RISK-009) |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Command file exceeds 200-line warning (FR-073); MCP server unavailable at runtime (RISK-006); task description lacks concrete verb |
| Info | Log only, no action required | N/A | Template discovery fallback to inline; persona auto-selection confidence below 0.5; minor formatting differences between v3.0 and SKILL.md |

## Acceptance Gates

Per-milestone acceptance criteria derived from spec requirements and mapped to deliverables.

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | Directory structure exists; `__init__.py` is empty; placeholder files have valid frontmatter | All 4 deliverables (D1.1–D1.4) verified; `pyproject.toml` excludes skill dir from package scanning |
| M2 | All 8 sections present; frontmatter matches §5.1; validation logic documented; line count <500 | All 6 deliverables (D2.1–D2.6) verified; no Critical/Major issues |
| M3 | SKILL.md body matches v3.0 verbatim; all 4 extracted files exist; stage validation criteria defined | All 7 deliverables (D3.1–D3.7) verified; diff shows zero functional delta from v3.0 |
| V1 | Lint checks #1, #2, #6, #8, #9 all pass | `make lint-architecture` reports zero errors for the new pair |
| M4 | sync-dev, verify-sync, lint-architecture, install all work; skill NOT in `~/.claude/skills/` | All 5 deliverables (D4.1–D4.5) verified |
| M5 | Bundle output valid; Sprint CLI discovers phases; v3.0 parity confirmed; lean format; standalone descriptions | All 5 deliverables (D5.1–D5.5) verified |
| V2 | SC-001 through SC-013 all pass | 100% success criteria met; zero Critical/Major issues remaining |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 (discoverability) | SC-001 | M4 | Run `superclaude install`; verify command appears in palette |
| FR-003 (lint passes) | SC-005 | V1, M4 | `make lint-architecture` |
| FR-005 (v3.0 parity) | SC-009 | M5 | Diff v3.0 output vs. `/sc:tasklist` output on same roadmap |
| FR-018–FR-022 (input validation) | D2.4 | M2 | Test with empty file, missing file, bad --output path |
| FR-034–FR-035 (SKILL.md content) | D3.2 | M3 | Character-level diff of v3.0 source vs. SKILL.md body |
| FR-044–FR-045 (file emission) | D5.1, SC-002 | M5 | Generate bundle; verify index + phase files exist |
| FR-048 (stage order) | SC-008 | M3 | Verify TodoWrite calls in stage 1–6 order |
| FR-050 (no output on validation fail) | SC-012 | V2 | Test with deliberately malformed roadmap; verify no files written |
| FR-061–FR-066 (output format) | SC-002–SC-007 | M5 | Manual review + Sprint CLI test |
| FR-067–FR-068 (install behavior) | D4.4, D4.5 | M4 | `superclaude install`; verify file locations |
| NFR-002 (zero behavioral drift) | SC-009 | M5 | Side-by-side output comparison |
| NFR-005 (atomic output) | SC-012 | V2 | Inject Stage 3 failure; verify zero files emitted |
| NFR-007 (no lint rule changes) | D4.3 | M4 | Verify lint rules unchanged; pair passes existing rules |
| RISK-001 (algorithm drift) | D3.2, D5.3 | M3, M5 | Diff-based verification at both reformatting and output stages |
| RISK-004 (naming convention) | D5.2 | M5 | `superclaude sprint run` on generated index |
| RISK-008 (quality gate gap) | D3.3, DV2.3 | M3, V2 | Verify criteria defined in SKILL.md and enforced at runtime |
