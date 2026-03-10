# Tasklist Refactor: v2.08 Spec-to-Tasklist Alignment

**Date**: 2026-03-05
**Purpose**: Apply 27 REQUIRED changes to v2.08 tasklist files to align with spec/roadmap updates
**Strategy**: Batch by file, largest first

---

## Phase 1: phase-2-tasklist.md (10 changes)

### T-R01: Update phase-2 header paragraph
- **Line ~3**: Replace `All 14 existing sprint test files must pass without modification (NFR-002).` with `All sprint test files must be passing at extraction start; no sprint test modifications during pipeline/ migration (NFR-002). Note: v2.07 modified 9 of the original 14 test files; the baseline is the post-v2.07 state.`
- **Source**: Change-1 Finding 3

### T-R02: Update T02.04 title
- **Line ~156**: Replace `Run full sprint regression: all 14 test files pass with zero modifications` with `Run full sprint regression: all sprint test files pass with zero modifications during pipeline migration`
- **Source**: Change-1 Finding 4

### T-R03: Update T02.04 Why field
- **Line ~161**: Replace `NFR-002 requires all 14 existing sprint test files pass without modification after pipeline migration, validating zero regression.` with `NFR-002 requires all sprint test files passing at extraction start remain passing with no sprint test modifications during pipeline/ migration, validating zero regression. Baseline is the post-v2.07 state.`
- **Source**: Change-1 Finding 5

### T-R04: Update T02.04 deliverables bullet
- **Line ~180**: Replace `all 14 test files passing and zero test file modifications` with `all sprint test files passing and zero test file modifications during pipeline/ migration`
- **Source**: Change-1 Finding 6

### T-R05: Update T02.04 step 1
- **Line ~183**: Replace `Enumerate all 14 sprint test files to establish baseline` with `Enumerate all sprint test files to establish baseline (post-v2.07 state)`
- **Source**: Change-1 Finding 7

### T-R06: Update T02.04 step 5
- **Line ~187**: Replace `all 14 files collected` with `all sprint test files collected`
- **Source**: Change-1 Finding 8

### T-R07: Update T02.04 AC bullet 1
- **Line ~191**: Replace `all 14 test files discovered and passing` with `all sprint test files discovered and passing`
- **Source**: Change-1 Finding 9

### T-R08: Update T02.04 AC — add watchdog traceability
- **After existing AC bullets**: Add `- Stall watchdog behavior (--stall-timeout, --stall-action) exercised by existing sprint tests continues to pass post-migration`
- **Source**: Change-9 Finding 1

### T-R09: Update T02.01 AC — add transitive property chain
- **After existing AC bullets for T02.01**: Add `- All SprintConfig computed properties that depend on release_dir (debug_log_path, results_dir, execution_log_jsonl, execution_log_md, output_file, error_file, result_file) resolve correctly through the release_dir->work_dir alias chain`
- **Source**: Change-9 Finding 3

### T-R10: Update Phase 2 checkpoint
- **Line ~210**: Replace `all 14 test files passing` with `all sprint test files passing`
- **Source**: Change-1 Finding 10

---

## Phase 2: phase-1-tasklist.md (10 changes)

### T-R11: Update T01.04 title
- Replace `Move \`ClaudeProcess\` from \`sprint/process.py\` to \`pipeline/process.py\`` with `Extract \`ClaudeProcess\` to \`pipeline/process.py\` with \`output_format\` parameterization`
- **Source**: Change-2 Finding 1a

### T-R12: Update T01.04 deliverables
- **Line ~180**: Replace `identical \`ClaudeProcess\` class moved from sprint` with `\`ClaudeProcess\` extracted from sprint with \`output_format\` parameter (default: \`stream-json\` for sprint backward-compat; \`text\` for roadmap gate-compatible output)`
- **Source**: Change-2 Finding 1b

### T-R13: Update T01.04 step 3
- Replace `Copy \`ClaudeProcess\` class to \`src/superclaude/cli/pipeline/process.py\` with identical implementation` with `Copy \`ClaudeProcess\` class to \`src/superclaude/cli/pipeline/process.py\`; add \`output_format: str = "stream-json"\` parameter; replace all \`debug_log()\` calls with stdlib \`logging\` (NFR-007 prohibits pipeline/ from importing sprint modules)`
- **Source**: Change-2 Finding 1c + Change-7

### T-R14: Update T01.04 AC bullet 1
- Replace `identical behavior to original sprint version` with `\`output_format\` parameter present; default \`"stream-json"\` preserves identical behavior to original sprint version; \`"text"\` produces gate-compatible plain-text output`
- **Source**: Change-2 Finding 1e

### T-R15: Add T01.04 AC — backward compat
- Add new AC bullet: `- \`ClaudeProcess(output_format="stream-json")\` produces byte-identical subprocess arguments to the original sprint \`ClaudeProcess\``
- **Source**: Change-2 Finding 1f

### T-R16: Add T01.04 AC — NFR-007 compliance
- Add new AC bullet: `- \`pipeline/process.py\` contains zero imports from \`superclaude.cli.sprint\` (NFR-007); all \`debug_log()\` calls replaced with stdlib logging or removed`
- **Source**: Change-7

### T-R17: Add T01.04 validation command
- Add to validation section: `- \`grep -r "from superclaude.cli.sprint" src/superclaude/cli/pipeline/process.py\` returns empty`
- **Source**: Change-7

### T-R18: Update T01.07 step 6
- Replace `ClaudeProcess from pipeline matches sprint behavior` with `ClaudeProcess default \`output_format="stream-json"\` matches sprint behavior; \`output_format="text"\` produces gate-compatible output`
- **Source**: Change-2 Finding 3a

### T-R19: Reserved (merged into T-R13)
- Combined debug_log step update into T-R13 for atomicity

### T-R20: Reserved
- Placeholder for any phase-1 additions discovered during execution

---

## Phase 3: phase-5-tasklist.md (6 changes)

### T-R21: Update T05.03 title
- Replace `all 14 test files pass with zero modifications post-migration` with `all sprint test files pass with zero modifications during pipeline/ migration`
- **Source**: Change-1 Finding 11

### T-R22: Update T05.03 deliverables
- Replace `all 14 test files passing and zero test modifications` with `all sprint test files passing and zero test modifications during pipeline/ migration`
- **Source**: Change-1 Finding 12

### T-R23: Update T05.03 step 5
- Replace `all 14 files collected and passing` with `all sprint test files collected and passing`
- **Source**: Change-1 Finding 13

### T-R24: Update T05.03 AC bullet 1
- Replace `all 14 test files discovered and passing` with `all sprint test files discovered and passing`
- **Source**: Change-1 Finding 14

### T-R25: Update T05.03 AC bullet 4
- Replace `No sprint test file was modified at any point during the project` with `No sprint test file was modified at any point during pipeline/ migration (v2.08 scope)`
- **Source**: Change-1 Finding 15

### T-R26: Update Phase 5 checkpoint
- Replace `14 test files pass with zero modifications` with `all sprint test files pass with zero modifications during pipeline/ migration`
- **Source**: Change-1 Finding 16

---

## Phase 4: tasklist-index.md (2 changes)

### T-R27: Update D-0011 deliverable text
- Replace `Sprint regression validation (all 14 test files pass)` with `Sprint regression validation (all sprint test files pass; no modifications during migration)`
- **Source**: Change-1 Finding 1

### T-R28: Update D-0031 deliverable text
- Replace `Sprint regression (14 test files pass unmodified)` with `Sprint regression (all sprint test files pass unmodified during pipeline/ migration)`
- **Source**: Change-1 Finding 2

---

## Execution Summary

| Phase | File | Changes | Effort |
|-------|------|---------|--------|
| 1 | phase-2-tasklist.md | 10 | ~15 min |
| 2 | phase-1-tasklist.md | 8 active (2 reserved) | ~15 min |
| 3 | phase-5-tasklist.md | 6 | ~10 min |
| 4 | tasklist-index.md | 2 | ~5 min |
| **Total** | **4 files** | **26 active + 1 merged** | **~45 min** |

## Validation Gate

After all changes applied, verify:
```bash
grep -rn "14 test files\|14 existing\|all 14" .dev/releases/current/v2.08-RoadmapCLI/tasklist/
# Expected: 0 matches

grep -rn "identical.*ClaudeProcess\|identical implementation" .dev/releases/current/v2.08-RoadmapCLI/tasklist/
# Expected: 0 matches

grep -rn "debug_log\|NFR-007" .dev/releases/current/v2.08-RoadmapCLI/tasklist/phase-1-tasklist.md
# Expected: at least 2 matches (AC bullets)
```
