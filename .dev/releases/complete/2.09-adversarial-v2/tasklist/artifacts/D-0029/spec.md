# D-0029: Round 2.5 Dispatch Logic — Depth-Conditioned Execution

## Overview

Round 2.5 (Invariant Probe) dispatch is controlled by the `--depth` flag, consistent with the existing depth-based dispatch pattern used by Rounds 2 and 3.

## Dispatch Rules

| Depth Level | Round 2.5 Behavior | Log Message |
|-------------|-------------------|-------------|
| `--depth quick` | **SKIP** | `Round 2.5 (invariant probe) skipped: --depth quick` |
| `--depth standard` | **EXECUTE** | (no skip message) |
| `--depth deep` | **EXECUTE** | (no skip message) |

## Implementation Location

`src/superclaude/skills/sc-adversarial-protocol/SKILL.md` — `round_2_5_invariant_probe` section:

```yaml
condition: "--depth standard OR --depth deep"
skip_condition: "--depth quick → skip (log: 'Round 2.5 (invariant probe) skipped: --depth quick')"
```

## Skip Log Message Format

The skip log message includes all required elements:
- **Round name**: "Round 2.5 (invariant probe)"
- **Reason for skip**: "skipped"
- **Depth value**: "--depth quick"

Full message: `Round 2.5 (invariant probe) skipped: --depth quick`

## Consistency with Existing Dispatch

This follows the same pattern as:
- Round 2: `skip_condition: "--depth quick → skip Round 2 entirely (log: 'Round 2 skipped: depth=quick')"`
- Round 3: `skip_conditions: not_deep: "--depth quick OR --depth standard → skip (log: 'Round 3 skipped: depth={depth}')"`

## Acceptance Criteria

- AC-AD1-4: Round 2.5 skipped at `--depth quick` with descriptive log message — **PASS**
- Executes at `--depth standard` and `--depth deep` — **PASS**
- Skip log message includes round name, reason, depth value — **PASS**
