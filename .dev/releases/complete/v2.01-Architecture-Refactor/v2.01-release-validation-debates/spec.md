# v2.01 Release Validation — Test Harness Specification

## Overview

**Purpose**: Empirically validate that the v2.01 Architecture Refactor achieves its objectives through repeated, scored, automated test runs using `claude -p` non-interactive mode.

**Architecture**: Orchestrator → 5 parallel teams → each team runs 3 model variants × 8 behavioral tests + 5 structural tests in parallel.

**Data points**: 5 runs × (5 structural + 3 models × 8 behavioral) = 5 × 29 = **145 data points**

## Test Matrix

### Tier 1: Structural Regression (Model-Independent)

| ID | SC | Test Name | Command | Scoring |
|----|-----|-----------|---------|---------|
| S1 | SC-004 | Architecture lint | `make lint-architecture` | exit 0 → 1.0, else 0.0 |
| S2 | SC-005 | Sync parity | `make verify-sync` | exit 0 → 1.0, else 0.0 |
| S3 | SC-009 | Stale references | `grep` for 5 old skill names | 0 matches → 1.0, else 0.0 |
| S4 | SC-010 | task-unified size | `wc -l ≤ 106` | ≤106 → 1.0, else 0.0 |
| S5 | SC-003 | Frontmatter completeness | `grep allowed-tools.*Skill` in 5 commands | 5/5 → 1.0, 4/5 → 0.8, etc. |

### Tier 2: Behavioral — Tier Classification (3 Models × 4 Tests)

Each test sends a task description to `claude -p` with the task-unified command loaded and checks whether the CLASSIFICATION header output matches the expected tier.

| ID | Prompt | Expected Tier | Scoring Rubric |
|----|--------|---------------|----------------|
| B1 | `"fix security vulnerability in auth module"` | STRICT | See rubric below |
| B2 | `"explain how the routing middleware works"` | EXEMPT | See rubric below |
| B3 | `"fix typo in error message"` | LIGHT | See rubric below |
| B4 | `"add pagination to user list endpoint"` | STANDARD | See rubric below |

**Classification Scoring Rubric** (per test):

| Criterion | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| Header present | 0.25 | `SC:TASK-UNIFIED:CLASSIFICATION` found | Partial header | No header |
| Tier correct | 0.40 | Exact match | Adjacent tier* | Wrong tier |
| Confidence ≥ 0.70 | 0.20 | ≥ 0.70 | 0.50–0.69 | < 0.50 or missing |
| Keywords present | 0.15 | Relevant keywords listed | Some keywords | No keywords |

*Adjacent tier: STRICT↔STANDARD, STANDARD↔LIGHT, LIGHT↔EXEMPT

**Test score** = sum(criterion_score × weight)

### Tier 3: Behavioral — Skill Invocation Wiring (3 Models × 4 Tests)

Each test invokes a slash command via `claude -p` and checks whether the full protocol skill was loaded and its behavioral flow initiated.

| ID | Command Invoked | Expected Protocol | Detection Signals |
|----|----------------|-------------------|-------------------|
| W1 | `/sc:task "implement JWT auth"` | sc:task-unified-protocol | Classification header + tier checklist |
| W2 | `/sc:adversarial --compare a.md,b.md` | sc:adversarial-protocol | Step 1 diff analysis initiated or "Mode A" acknowledged |
| W3 | `/sc:validate-tests --all` | sc:validate-tests-protocol | Test loading or classification algorithm referenced |
| W4 | `/sc:roadmap @sprint-spec.md` | sc:roadmap-protocol | Wave 0 or spec loading initiated |

**Wiring Scoring Rubric** (per test):

| Criterion | Weight | 1.0 | 0.5 | 0.0 |
|-----------|--------|-----|-----|-----|
| Skill invoked | 0.35 | Protocol skill name appears in output | Partial reference | No evidence |
| Protocol flow started | 0.35 | First protocol step initiated | Acknowledged but not started | No protocol flow |
| No raw command dump | 0.15 | Command file not echoed verbatim | Partial echo | Full command file dumped |
| Appropriate tool use | 0.15 | Tools attempted (Read, Grep, etc.) | Mentioned but not used | No tool engagement |

## `claude -p` Invocation Patterns

### Tier Classification Tests (B1–B4)

```bash
claude -p \
  --dangerously-skip-permissions \
  --model "${MODEL}" \
  --max-turns 3 \
  --output-format text \
  "/sc:task \"${PROMPT}\"" \
  2>&1
```

**Rationale**:
- `--dangerously-skip-permissions`: Required for automated non-interactive runs
- `--max-turns 3`: Sufficient for classification (header output is turn 1); prevents runaway
- `--output-format text`: Easier to parse classification header from raw text
- Model varies: haiku, sonnet, opus

### Wiring Tests (W1–W4)

```bash
claude -p \
  --dangerously-skip-permissions \
  --model "${MODEL}" \
  --max-turns 5 \
  --output-format text \
  "${COMMAND}" \
  2>&1
```

**Rationale**:
- `--max-turns 5`: Wiring tests need more turns — skill load (1) + protocol init (2-3) + first step (4-5)
- Higher turn count allows protocol flow to begin, proving the wiring works

### W2 (Adversarial) Special Case

W2 needs dummy files to compare. Create them in a temp directory before the test:

```bash
TMPDIR=$(mktemp -d)
echo "# Draft A\nApproach: microservices" > "$TMPDIR/a.md"
echo "# Draft B\nApproach: monolith" > "$TMPDIR/b.md"

claude -p \
  --dangerously-skip-permissions \
  --model "${MODEL}" \
  --max-turns 5 \
  --add-dir "$TMPDIR" \
  --output-format text \
  "/sc:adversarial --compare $TMPDIR/a.md,$TMPDIR/b.md --depth quick" \
  2>&1

rm -rf "$TMPDIR"
```

### W4 (Roadmap) Special Case

W4 needs a spec file:

```bash
claude -p \
  --dangerously-skip-permissions \
  --model "${MODEL}" \
  --max-turns 5 \
  --output-format text \
  "/sc:roadmap @.dev/releases/current/v2.01-Architecture-Refactor/sprint-spec.md" \
  2>&1
```

## Parallelization Architecture

```
orchestrator.py (asyncio)
│
├─ team_1/ ─────────────────────────────────────────────────
│  ├─ [parallel] S1, S2, S3, S4, S5          (5 bash jobs)
│  ├─ [parallel] B1-haiku, B2-haiku, B3-haiku, B4-haiku
│  ├─ [parallel] B1-sonnet, B2-sonnet, B3-sonnet, B4-sonnet
│  ├─ [parallel] B1-opus, B2-opus, B3-opus, B4-opus
│  ├─ [parallel] W1-haiku, W2-haiku, W3-haiku, W4-haiku
│  ├─ [parallel] W1-sonnet, W2-sonnet, W3-sonnet, W4-sonnet
│  └─ [parallel] W1-opus, W2-opus, W3-opus, W4-opus
│
├─ team_2/ ── (same structure) ──────────────────────────────
├─ team_3/ ── (same structure) ──────────────────────────────
├─ team_4/ ── (same structure) ──────────────────────────────
└─ team_5/ ── (same structure) ──────────────────────────────

Concurrency: 5 teams × 29 agents = 145 max parallel
Semaphore: limit to 30 concurrent claude -p processes (API rate limits)
```

### Concurrency Control

```python
# Global semaphore limits concurrent claude -p calls
CLAUDE_SEMAPHORE = asyncio.Semaphore(30)

# Structural tests run with no limit (bash, fast)
STRUCTURAL_SEMAPHORE = asyncio.Semaphore(25)
```

## Output Format

### Per-Test Result (JSON)

```json
{
  "test_id": "B1",
  "run": 1,
  "model": "sonnet",
  "timestamp": "2026-02-24T15:30:00Z",
  "duration_ms": 4230,
  "prompt": "fix security vulnerability in auth module",
  "expected": {
    "tier": "STRICT",
    "header_present": true,
    "protocol_invoked": true
  },
  "actual": {
    "tier": "STRICT",
    "confidence": 0.92,
    "keywords": ["security", "vulnerability", "auth"],
    "header_present": true,
    "override": false,
    "rationale": "Security-critical change in auth module"
  },
  "scores": {
    "header_present": 1.0,
    "tier_correct": 1.0,
    "confidence_adequate": 1.0,
    "keywords_relevant": 1.0,
    "weighted_total": 1.0
  },
  "raw_output_path": "results/run_1/B1_sonnet_output.txt"
}
```

### Aggregate Report Format

```
╔═══════════════════════════════════════════════════════════════╗
║           v2.01 Release Validation Report                     ║
║           5 runs × 3 models × 13 tests = 145 data points     ║
╚═══════════════════════════════════════════════════════════════╝

STRUCTURAL TESTS (25 data points — model-independent)
─────────────────────────────────────────────────────
  S1 lint-architecture     5/5  ████████████████████  100%
  S2 verify-sync           5/5  ████████████████████  100%
  S3 stale-references      5/5  ████████████████████  100%
  S4 task-unified-size     5/5  ████████████████████  100%
  S5 frontmatter           5/5  ████████████████████  100%

TIER CLASSIFICATION — By Model (60 data points)
─────────────────────────────────────────────────────
          Haiku       Sonnet      Opus        Mean
  B1      0.95±0.05   1.00±0.00   1.00±0.00   0.98
  B2      0.85±0.10   0.95±0.05   1.00±0.00   0.93
  B3      0.90±0.07   0.95±0.05   1.00±0.00   0.95
  B4      0.80±0.12   0.90±0.07   0.95±0.05   0.88

SKILL WIRING — By Model (60 data points)
─────────────────────────────────────────────────────
          Haiku       Sonnet      Opus        Mean
  W1      0.90±0.08   1.00±0.00   1.00±0.00   0.97
  W2      0.75±0.15   0.85±0.10   0.95±0.05   0.85
  W3      0.85±0.10   0.95±0.05   1.00±0.00   0.93
  W4      0.80±0.12   0.90±0.08   0.95±0.05   0.88

MODEL COMPARISON
─────────────────────────────────────────────────────
  Haiku:    Mean 86.2%  Std 9.1%   Min 75%  Max 100%
  Sonnet:   Mean 93.8%  Std 4.2%   Min 85%  Max 100%
  Opus:     Mean 98.1%  Std 2.0%   Min 95%  Max 100%

AGGREGATE VERDICT
─────────────────────────────────────────────────────
  Overall mean:     92.7%
  Structural:       100.0% (deterministic)
  Behavioral mean:  90.4%
  Cross-model std:  4.4%
  VERDICT:          RELEASE APPROVED ✅  (threshold: ≥85%)
```

## Scoring Methodology

### Per-Test Score
Weighted sum of criterion scores (see rubrics above). Range: 0.0–1.0.

### Per-Run Score
```
run_score = (sum(structural_scores) + sum(behavioral_scores)) / total_tests
```

### Model Score
```
model_score = mean(all test scores for that model across 5 runs)
model_std   = std(all test scores for that model across 5 runs)
```

### Aggregate Score
```
aggregate = mean(all 145 data points)
structural_aggregate = mean(25 structural data points)
behavioral_aggregate = mean(120 behavioral data points)
```

### Release Approval Thresholds

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Structural aggregate | = 100% | Deterministic; anything less is a bug |
| Behavioral aggregate (any model) | ≥ 80% | Model may miss nuances |
| Behavioral aggregate (best model) | ≥ 90% | At least one model must be strong |
| Cross-model std | ≤ 15% | Models shouldn't wildly disagree |
| Per-test minimum (any model) | ≥ 50% | No test should consistently fail |

**RELEASE APPROVED** if ALL thresholds met.

## File Structure

```
tests/v2.01-release-validation/
├── spec.md                          # This document
├── orchestrator.py                  # Main orchestrator (asyncio)
├── runner.py                        # Single-test runner
├── scorer.py                        # Score calculation and parsing
├── reporter.py                      # Aggregate report generation
├── tests/
│   ├── structural/
│   │   ├── s1_lint.sh
│   │   ├── s2_sync.sh
│   │   ├── s3_stale.sh
│   │   ├── s4_size.sh
│   │   └── s5_frontmatter.sh
│   └── behavioral/
│       ├── b1_strict.yaml           # Test definition: prompt, expected, rubric
│       ├── b2_exempt.yaml
│       ├── b3_light.yaml
│       ├── b4_standard.yaml
│       ├── w1_task_wiring.yaml
│       ├── w2_adversarial_wiring.yaml
│       ├── w3_validate_wiring.yaml
│       └── w4_roadmap_wiring.yaml
├── results/                         # Created at runtime
│   ├── run_1/
│   │   ├── S1_result.json
│   │   ├── B1_haiku_result.json
│   │   ├── B1_haiku_output.txt
│   │   ├── B1_sonnet_result.json
│   │   ├── ...
│   ├── run_2/ ...
│   ├── run_3/ ...
│   ├── run_4/ ...
│   ├── run_5/ ...
│   └── aggregate_report.md
└── README.md
```

## Implementation Notes

### Output Parsing

The scorer parses `claude -p` text output using regex:

```python
import re

def parse_classification_header(output: str) -> dict | None:
    """Extract tier classification from SC:TASK-UNIFIED:CLASSIFICATION block."""
    pattern = r'<!--\s*SC:TASK-UNIFIED:CLASSIFICATION\s*-->\s*\n'
    pattern += r'TIER:\s*(\w+)\s*\n'
    pattern += r'CONFIDENCE:\s*([\d.]+)\s*\n'
    pattern += r'KEYWORDS:\s*(.+)\s*\n'
    pattern += r'OVERRIDE:\s*(\w+)\s*\n'
    pattern += r'RATIONALE:\s*(.+)\s*\n'
    pattern += r'<!--\s*/SC:TASK-UNIFIED:CLASSIFICATION\s*-->'

    match = re.search(pattern, output)
    if not match:
        return None

    return {
        "tier": match.group(1),
        "confidence": float(match.group(2)),
        "keywords": [k.strip() for k in match.group(3).split(",")],
        "override": match.group(4).lower() == "true",
        "rationale": match.group(5).strip()
    }

def parse_wiring_signals(output: str, test_id: str) -> dict:
    """Detect protocol invocation signals in output."""
    signals = {
        "W1": {
            "skill_pattern": r"sc:task-unified-protocol",
            "flow_patterns": [r"TIER:", r"CLASSIFICATION", r"Classified as"],
        },
        "W2": {
            "skill_pattern": r"sc:adversarial-protocol",
            "flow_patterns": [r"Step 1", r"diff analysis", r"Mode [AB]"],
        },
        "W3": {
            "skill_pattern": r"sc:validate-tests-protocol",
            "flow_patterns": [r"Load Test", r"classification", r"test spec"],
        },
        "W4": {
            "skill_pattern": r"sc:roadmap-protocol",
            "flow_patterns": [r"Wave 0", r"spec.*load", r"roadmap gen"],
        },
    }
    # ... scoring logic
```

### Error Handling

```python
async def run_claude_p(model: str, prompt: str, max_turns: int = 3) -> tuple[str, int, float]:
    """Run claude -p and return (output, exit_code, duration_ms)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "claude", "-p",
            "--dangerously-skip-permissions",
            "--model", model,
            "--max-turns", str(max_turns),
            "--output-format", "text",
            prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        return stdout.decode(), proc.returncode, duration
    except asyncio.TimeoutError:
        proc.kill()
        return "TIMEOUT", -1, 120000
    except Exception as e:
        return f"ERROR: {e}", -2, 0
```

### Idempotency

All tests are **read-only**:
- Structural tests: `make lint-architecture`, `make verify-sync`, `grep`, `wc -l`
- Behavioral tests: `claude -p` with no write permissions needed (classification only)
- Wiring tests: `claude -p` with `--max-turns 5` limits any side effects

No git worktrees needed. Safe to run 5 teams in parallel on the same checkout.
