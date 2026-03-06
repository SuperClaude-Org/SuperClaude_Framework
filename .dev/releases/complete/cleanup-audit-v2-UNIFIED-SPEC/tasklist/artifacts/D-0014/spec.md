# D-0014: Auto-Config Generation Specification

## Module
`src/superclaude/cli/audit/auto_config.py`

## Cold-Start Detection
Checks for absence of `.cleanup-audit.json` in the config directory.

## Config Derivation Rules
| Field | Rule |
|-------|------|
| batch_size | <=50 files: 25, <=200: 50, >200: 100 |
| depth | >30% high-risk: "deep", >10%: "standard", else: "surface" |
| report_mode | Always "full" |
| budget | file_count * 200 * risk_multiplier, clamped to [10K, 500K] |

## Config File
Written to `.cleanup-audit.json` as formatted JSON. Generation event is logged.
