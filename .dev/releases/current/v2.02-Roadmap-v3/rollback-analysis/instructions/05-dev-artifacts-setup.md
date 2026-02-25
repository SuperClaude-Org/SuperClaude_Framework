# 05 - Dev Artifacts Setup (Post-Rollback Copy Guide)

**Date**: 2026-02-24
**Purpose**: Step-by-step instructions for restoring all dev artifact files after a git rollback
**Method**: COPY from backup -- these artifacts are NOT recreated, they are restored
**Source**: Synthesis documents A, B, and adversarial-to-framework context analysis

---

## 1. Complete File Inventory (28 files)

All paths are relative to:
```
.dev/releases/current/v2.01-Roadmap-v3/tasklist/
```

### 1.1 Approach Documents (3 files)

| # | File | Lines | HARD-TO-RECREATE |
|---|------|-------|------------------|
| 1 | `artifacts/approach-1-empirical-probe-first.md` | 879 | **YES** |
| 2 | `artifacts/approach-2-claude-p-proposal.md` | 718 | **YES** |
| 3 | `artifacts/approach-3-hybrid-dual-path.md` | 1121 | **YES** |

### 1.2 Decision Artifacts D-0001 through D-0008 (8 files)

| # | File | Type | Task |
|---|------|------|------|
| 4 | `artifacts/D-0001/evidence.md` | Probe result | T01.01 |
| 5 | `artifacts/D-0002/notes.md` | Sprint variant decision | T01.01 |
| 6 | `artifacts/D-0003/evidence.md` | Prerequisite validation | T01.02 |
| 7 | `artifacts/D-0004/evidence.md` | allowed-tools (roadmap.md) | T02.01 |
| 8 | `artifacts/D-0005/evidence.md` | allowed-tools (SKILL.md) | T02.02 |
| 9 | `artifacts/D-0006/spec.md` | Wave 2 step 3 sub-steps | T02.03 |
| 10 | `artifacts/D-0007/spec.md` | Fallback protocol | T02.03 |
| 11 | `artifacts/D-0008/spec.md` | Return contract routing | T02.03 |

### 1.3 Policy Artifact (1 file)

| # | File | Task |
|---|------|------|
| 12 | `artifacts/T01.03/notes.md` | Tier classification policy |

### 1.4 Adversarial Pipeline Artifacts (8 files)

| # | File | ID | Lines | HARD-TO-RECREATE |
|---|------|----|-------|------------------|
| 13 | `artifacts/adversarial/base-selection.md` | ADV-3 | ~100 | **YES** |
| 14 | `artifacts/adversarial/scoring-rubric.md` | ADV-2 | ~300 | **YES** |
| 15 | `artifacts/adversarial/debate-transcript.md` | ADV-1 | ~400 | **YES** |
| 16 | `artifacts/adversarial/merged-approach.md` | ADV-5 | 546 | |
| 17 | `artifacts/adversarial/refactoring-plan.md` | ADV-4 | 80 | |
| 18 | `artifacts/adversarial/specification-draft-v1.md` | ADV-6 | 653 | |
| 19 | `artifacts/adversarial/specification-draft-v2.md` | ADV-8 | 872 | |
| 20 | `artifacts/adversarial/spec-panel-review.md` | ADV-7 | 281 | **YES** |

### 1.5 Evidence Records (6 files)

| # | File | Task | Result |
|---|------|------|--------|
| 21 | `evidence/T01.01/result.md` | T01.01 | TOOL_NOT_AVAILABLE |
| 22 | `evidence/T01.02/result.md` | T01.02 | PASS (6/6) |
| 23 | `evidence/T01.03/result.md` | T01.03 | Policy decision |
| 24 | `evidence/T02.01/result.md` | T02.01 | PASS |
| 25 | `evidence/T02.02/result.md` | T02.02 | PASS |
| 26 | `evidence/T02.03/result.md` | T02.03 | PASS (8/8 audit) |

### 1.6 Checkpoint Files (2 files)

| # | File | Purpose |
|---|------|---------|
| 27 | `checkpoints/CP-P01-END.md` | Phase 1 completion checkpoint |
| 28 | `checkpoints/CP-P02-END.md` | Phase 2 completion checkpoint |

**Total: 28 files across 6 categories.**

---

## 2. Directory Structure Creation

Run these commands from the repo root to create the full directory tree. If the rollback removed these directories, they must be recreated before copying files.

```bash
# Base path variable for convenience
BASE=".dev/releases/current/v2.01-Roadmap-v3/tasklist"

# Create all artifact directories
mkdir -p "$BASE/artifacts/D-0001"
mkdir -p "$BASE/artifacts/D-0002"
mkdir -p "$BASE/artifacts/D-0003"
mkdir -p "$BASE/artifacts/D-0004"
mkdir -p "$BASE/artifacts/D-0005"
mkdir -p "$BASE/artifacts/D-0006"
mkdir -p "$BASE/artifacts/D-0007"
mkdir -p "$BASE/artifacts/D-0008"
mkdir -p "$BASE/artifacts/T01.03"
mkdir -p "$BASE/artifacts/adversarial"

# Create evidence directories
mkdir -p "$BASE/evidence/T01.01"
mkdir -p "$BASE/evidence/T01.02"
mkdir -p "$BASE/evidence/T01.03"
mkdir -p "$BASE/evidence/T02.01"
mkdir -p "$BASE/evidence/T02.02"
mkdir -p "$BASE/evidence/T02.03"

# Create checkpoint directory
mkdir -p "$BASE/checkpoints"
```

Full tree after creation:
```
.dev/releases/current/v2.01-Roadmap-v3/tasklist/
├── artifacts/
│   ├── approach-1-empirical-probe-first.md
│   ├── approach-2-claude-p-proposal.md
│   ├── approach-3-hybrid-dual-path.md
│   ├── D-0001/
│   │   └── evidence.md
│   ├── D-0002/
│   │   └── notes.md
│   ├── D-0003/
│   │   └── evidence.md
│   ├── D-0004/
│   │   └── evidence.md
│   ├── D-0005/
│   │   └── evidence.md
│   ├── D-0006/
│   │   └── spec.md
│   ├── D-0007/
│   │   └── spec.md
│   ├── D-0008/
│   │   └── spec.md
│   ├── T01.03/
│   │   └── notes.md
│   └── adversarial/
│       ├── base-selection.md
│       ├── scoring-rubric.md
│       ├── debate-transcript.md
│       ├── merged-approach.md
│       ├── refactoring-plan.md
│       ├── specification-draft-v1.md
│       ├── specification-draft-v2.md
│       └── spec-panel-review.md
├── evidence/
│   ├── T01.01/
│   │   └── result.md
│   ├── T01.02/
│   │   └── result.md
│   ├── T01.03/
│   │   └── result.md
│   ├── T02.01/
│   │   └── result.md
│   ├── T02.02/
│   │   └── result.md
│   └── T02.03/
│       └── result.md
└── checkpoints/
    ├── CP-P01-END.md
    └── CP-P02-END.md
```

---

## 3. Copy Instructions

### 3.1 Backup Source

Before performing the rollback, the current artifact files should have been backed up. The backup location is assumed to be:

```
$BACKUP_DIR/   # Set this to wherever the pre-rollback backup was stored
```

### 3.2 Copy Commands

After the rollback and after running the `mkdir` commands from Section 2:

```bash
BASE=".dev/releases/current/v2.01-Roadmap-v3/tasklist"

# --- Approach Documents (3 files) ---
cp "$BACKUP_DIR/artifacts/approach-1-empirical-probe-first.md"  "$BASE/artifacts/"
cp "$BACKUP_DIR/artifacts/approach-2-claude-p-proposal.md"      "$BASE/artifacts/"
cp "$BACKUP_DIR/artifacts/approach-3-hybrid-dual-path.md"       "$BASE/artifacts/"

# --- Decision Artifacts D-0001 through D-0008 (8 files) ---
cp "$BACKUP_DIR/artifacts/D-0001/evidence.md"   "$BASE/artifacts/D-0001/"
cp "$BACKUP_DIR/artifacts/D-0002/notes.md"      "$BASE/artifacts/D-0002/"
cp "$BACKUP_DIR/artifacts/D-0003/evidence.md"   "$BASE/artifacts/D-0003/"
cp "$BACKUP_DIR/artifacts/D-0004/evidence.md"   "$BASE/artifacts/D-0004/"
cp "$BACKUP_DIR/artifacts/D-0005/evidence.md"   "$BASE/artifacts/D-0005/"
cp "$BACKUP_DIR/artifacts/D-0006/spec.md"       "$BASE/artifacts/D-0006/"
cp "$BACKUP_DIR/artifacts/D-0007/spec.md"       "$BASE/artifacts/D-0007/"
cp "$BACKUP_DIR/artifacts/D-0008/spec.md"       "$BASE/artifacts/D-0008/"

# --- Policy Artifact (1 file) ---
cp "$BACKUP_DIR/artifacts/T01.03/notes.md"      "$BASE/artifacts/T01.03/"

# --- Adversarial Pipeline (8 files) ---
cp "$BACKUP_DIR/artifacts/adversarial/base-selection.md"            "$BASE/artifacts/adversarial/"
cp "$BACKUP_DIR/artifacts/adversarial/scoring-rubric.md"            "$BASE/artifacts/adversarial/"
cp "$BACKUP_DIR/artifacts/adversarial/debate-transcript.md"         "$BASE/artifacts/adversarial/"
cp "$BACKUP_DIR/artifacts/adversarial/merged-approach.md"           "$BASE/artifacts/adversarial/"
cp "$BACKUP_DIR/artifacts/adversarial/refactoring-plan.md"          "$BASE/artifacts/adversarial/"
cp "$BACKUP_DIR/artifacts/adversarial/specification-draft-v1.md"    "$BASE/artifacts/adversarial/"
cp "$BACKUP_DIR/artifacts/adversarial/specification-draft-v2.md"    "$BASE/artifacts/adversarial/"
cp "$BACKUP_DIR/artifacts/adversarial/spec-panel-review.md"         "$BASE/artifacts/adversarial/"

# --- Evidence Records (6 files) ---
cp "$BACKUP_DIR/evidence/T01.01/result.md"      "$BASE/evidence/T01.01/"
cp "$BACKUP_DIR/evidence/T01.02/result.md"      "$BASE/evidence/T01.02/"
cp "$BACKUP_DIR/evidence/T01.03/result.md"      "$BASE/evidence/T01.03/"
cp "$BACKUP_DIR/evidence/T02.01/result.md"      "$BASE/evidence/T02.01/"
cp "$BACKUP_DIR/evidence/T02.02/result.md"      "$BASE/evidence/T02.02/"
cp "$BACKUP_DIR/evidence/T02.03/result.md"      "$BASE/evidence/T02.03/"

# --- Checkpoint Files (2 files) ---
cp "$BACKUP_DIR/checkpoints/CP-P01-END.md"      "$BASE/checkpoints/"
cp "$BACKUP_DIR/checkpoints/CP-P02-END.md"      "$BASE/checkpoints/"
```

### 3.3 Alternative: Bulk Copy

If the backup preserves the full directory structure:

```bash
BASE=".dev/releases/current/v2.01-Roadmap-v3/tasklist"

cp -r "$BACKUP_DIR/artifacts/"   "$BASE/"
cp -r "$BACKUP_DIR/evidence/"    "$BASE/"
cp -r "$BACKUP_DIR/checkpoints/" "$BASE/"
```

---

## 4. HARD-TO-RECREATE Artifacts (6 files -- MUST PRESERVE)

These 6 artifacts are rated **HARD** recreation difficulty. They contain original creative/stochastic outputs that cannot be mechanically regenerated. If the backup is lost, budget 4-8 hours of design work plus adversarial debate execution to reproduce them.

| # | File | Why HARD |
|---|------|----------|
| 1 | `artifacts/approach-1-empirical-probe-first.md` (879 lines) | Original design work: 13 test cases, 3 strategies, 3 decision gates, 7 risks. Creative architectural reasoning that cannot be deterministically reproduced. |
| 2 | `artifacts/approach-2-claude-p-proposal.md` (718 lines) | Original design work: full `claude -p` implementation spec, command templates, 14 sprint-spec changes. Selected as the winning base approach (score 0.900). |
| 3 | `artifacts/approach-3-hybrid-dual-path.md` (1121 lines) | Original design work: dual-path architecture, mid-pipeline fallover, 6 verification specs. Source of key absorbed features (5-step fallback, convergence tracking). |
| 4 | `artifacts/adversarial/debate-transcript.md` (~400 lines) | Stochastic adversarial debate output: 2 rounds + final, 12 convergence decisions (C-001 to C-010, U-001, U-002). The emergent reasoning and specific advocate arguments cannot be deterministically reproduced. |
| 5 | `artifacts/adversarial/scoring-rubric.md` (~300 lines) | Adversarial scoring with position-bias mitigation: 50/50 quant/qual, 5 metrics + 25 binary criteria. Scores may vary on re-run. |
| 6 | `artifacts/adversarial/base-selection.md` (~100 lines) | Selection decision with absorption plan: Ap2 at 0.900 selected, specific absorptions from Ap1 and Ap3 listed. Depends on exact debate and scoring outputs. |

**Additional note**: `spec-panel-review.md` (ADV-7) is rated MEDIUM-HARD. Its 27 findings with line-number references to spec-v1 would change if the source spec changes. It is not rated HARD only because it is reproducible given spec-v1 and the SKILL.md files, but the exact finding numbers and cross-references would differ.

**Preservation priority order** (most critical first):
1. `specification-draft-v2.md` -- most mature design document; addresses all review findings
2. Three approach documents -- source material enabling full re-derivation
3. `D-0001/evidence.md` + `D-0002/notes.md` -- foundational probe result determining sprint trajectory
4. `spec-panel-review.md` -- 27 actionable findings that drove spec evolution
5. `debate-transcript.md` -- convergence decisions shaping the merged architecture
6. Everything else (reconstructable from above)

---

## 5. Path Updates Required

### 5.1 The Rename

During the sprint, skill directories were renamed to add a `-protocol` suffix:

| Old Path (pre-rename) | New Path (post-rename) |
|------------------------|------------------------|
| `src/superclaude/skills/sc-adversarial/` | `src/superclaude/skills/sc-adversarial-protocol/` |
| `src/superclaude/skills/sc-roadmap/` | `src/superclaude/skills/sc-roadmap-protocol/` |
| `src/superclaude/skills/sc-cleanup-audit/` | `src/superclaude/skills/sc-cleanup-audit-protocol/` |
| `src/superclaude/skills/sc-task-unified/` | `src/superclaude/skills/sc-task-unified-protocol/` |
| `src/superclaude/skills/sc-validate-tests/` | `src/superclaude/skills/sc-validate-tests-protocol/` |

### 5.2 Which Artifacts Need Path Updates

**24 of 25 analyzed artifacts use pre-rename paths.** Only `specification-draft-v2.md` uses the corrected `-protocol` suffix.

If the rollback **preserves** the `-protocol` directory rename (directories remain renamed), the following artifacts contain stale path references:

| Artifact | Contains References To |
|----------|------------------------|
| `approach-1-empirical-probe-first.md` | `sc-adversarial/`, `sc-roadmap/` |
| `approach-2-claude-p-proposal.md` | `sc-adversarial/`, `sc-roadmap/` |
| `approach-3-hybrid-dual-path.md` | `sc-adversarial/`, `sc-roadmap/` (with SKILL.md line numbers) |
| `D-0001/evidence.md` | `sc-adversarial/`, `sc-roadmap/` |
| `D-0002/notes.md` | `sc-adversarial/`, `sc-roadmap/` |
| `D-0003/evidence.md` | `sc-adversarial/`, `sc-roadmap/` (pre-rename directory state) |
| `D-0004/evidence.md` | `sc-roadmap/` (grep target) |
| `D-0005/evidence.md` | `sc-roadmap/` (grep target) |
| `D-0006/spec.md` | `sc-adversarial/`, `sc-roadmap/` |
| `D-0007/spec.md` | `sc-adversarial/`, `sc-roadmap/` |
| `D-0008/spec.md` | `sc-adversarial/`, `sc-roadmap/` |
| `T01.03/notes.md` | Lists affected files with old paths |
| `adversarial/debate-transcript.md` | References approach documents (implied old paths) |
| `adversarial/scoring-rubric.md` | References approach documents (implied old paths) |
| `adversarial/base-selection.md` | References approach documents (implied old paths) |
| `adversarial/refactoring-plan.md` | References `sc:adversarial SKILL.md` generically |
| `adversarial/merged-approach.md` | `sc-adversarial/`, `sc-roadmap/` (explicitly noted pre-rename) |
| `adversarial/specification-draft-v1.md` | `sc-adversarial/`, `sc-roadmap/` (noted as retained issue) |
| `adversarial/spec-panel-review.md` | Line-number references to old file locations |
| All `evidence/T*/result.md` | Grep validations ran against old paths |

**Does NOT need path updates**:
| Artifact | Notes |
|----------|-------|
| `adversarial/specification-draft-v2.md` | Already uses `sc-adversarial-protocol/` |

### 5.3 Decision: Update or Leave As-Is

Two valid approaches:

**Option A: Leave artifacts as-is (RECOMMENDED)**. These are historical records. The pre-rename paths document the state at time of creation. Add a note at the top of any artifact that references old paths:

```markdown
> **Path Note**: This artifact was created before the `-protocol` rename. References to
> `sc-adversarial/` and `sc-roadmap/` should be read as `sc-adversarial-protocol/` and
> `sc-roadmap-protocol/` respectively.
```

**Option B: Search-and-replace all paths**. Only do this if artifact accuracy for automated tooling is required:

```bash
BASE=".dev/releases/current/v2.01-Roadmap-v3/tasklist"

# Find all .md files with old paths and replace
find "$BASE" -name "*.md" -exec sed -i \
  -e 's|sc-adversarial/|sc-adversarial-protocol/|g' \
  -e 's|sc-roadmap/|sc-roadmap-protocol/|g' \
  -e 's|sc-cleanup-audit/|sc-cleanup-audit-protocol/|g' \
  -e 's|sc-task-unified/|sc-task-unified-protocol/|g' \
  -e 's|sc-validate-tests/|sc-validate-tests-protocol/|g' \
  {} +
```

**Warning for Option B**: This will also affect inline code blocks, quoted text, and historical narrative where the old path is contextually correct. Use with caution.

---

## 6. Verification

### 6.1 File Count Verification

After copying, verify all 28 files are present:

```bash
BASE=".dev/releases/current/v2.01-Roadmap-v3/tasklist"

echo "=== File Count ==="
ACTUAL=$(find "$BASE/artifacts" "$BASE/evidence" "$BASE/checkpoints" -type f -name "*.md" | wc -l)
echo "Expected: 28"
echo "Actual:   $ACTUAL"
[ "$ACTUAL" -eq 28 ] && echo "PASS" || echo "FAIL - missing files"
```

### 6.2 Individual File Existence Check

```bash
BASE=".dev/releases/current/v2.01-Roadmap-v3/tasklist"

EXPECTED_FILES=(
  # Approach docs (3)
  "artifacts/approach-1-empirical-probe-first.md"
  "artifacts/approach-2-claude-p-proposal.md"
  "artifacts/approach-3-hybrid-dual-path.md"
  # Decision artifacts (8)
  "artifacts/D-0001/evidence.md"
  "artifacts/D-0002/notes.md"
  "artifacts/D-0003/evidence.md"
  "artifacts/D-0004/evidence.md"
  "artifacts/D-0005/evidence.md"
  "artifacts/D-0006/spec.md"
  "artifacts/D-0007/spec.md"
  "artifacts/D-0008/spec.md"
  # Policy artifact (1)
  "artifacts/T01.03/notes.md"
  # Adversarial pipeline (8)
  "artifacts/adversarial/base-selection.md"
  "artifacts/adversarial/scoring-rubric.md"
  "artifacts/adversarial/debate-transcript.md"
  "artifacts/adversarial/merged-approach.md"
  "artifacts/adversarial/refactoring-plan.md"
  "artifacts/adversarial/specification-draft-v1.md"
  "artifacts/adversarial/specification-draft-v2.md"
  "artifacts/adversarial/spec-panel-review.md"
  # Evidence records (6)
  "evidence/T01.01/result.md"
  "evidence/T01.02/result.md"
  "evidence/T01.03/result.md"
  "evidence/T02.01/result.md"
  "evidence/T02.02/result.md"
  "evidence/T02.03/result.md"
  # Checkpoints (2)
  "checkpoints/CP-P01-END.md"
  "checkpoints/CP-P02-END.md"
)

PASS=0
FAIL=0
for f in "${EXPECTED_FILES[@]}"; do
  if [ -f "$BASE/$f" ]; then
    PASS=$((PASS + 1))
  else
    echo "MISSING: $BASE/$f"
    FAIL=$((FAIL + 1))
  fi
done

echo ""
echo "Results: $PASS passed, $FAIL missing out of ${#EXPECTED_FILES[@]} expected"
```

### 6.3 Content Spot-Checks

Verify key content markers that confirm files are not empty or corrupted:

```bash
BASE=".dev/releases/current/v2.01-Roadmap-v3/tasklist"

echo "=== Content Spot-Checks ==="

# D-0001 must contain TOOL_NOT_AVAILABLE
grep -q "TOOL_NOT_AVAILABLE" "$BASE/artifacts/D-0001/evidence.md" && \
  echo "PASS: D-0001 contains TOOL_NOT_AVAILABLE" || \
  echo "FAIL: D-0001 missing expected content"

# D-0002 must contain FALLBACK-ONLY
grep -q "FALLBACK.ONLY" "$BASE/artifacts/D-0002/notes.md" && \
  echo "PASS: D-0002 contains FALLBACK-ONLY" || \
  echo "FAIL: D-0002 missing expected content"

# Debate transcript must contain convergence decisions
grep -q "C-001" "$BASE/artifacts/adversarial/debate-transcript.md" && \
  echo "PASS: debate-transcript contains C-001" || \
  echo "FAIL: debate-transcript missing convergence decisions"

# Scoring rubric must contain approach scores
grep -q "0.900" "$BASE/artifacts/adversarial/scoring-rubric.md" && \
  echo "PASS: scoring-rubric contains Ap2 score 0.900" || \
  echo "FAIL: scoring-rubric missing expected scores"

# Spec-v2 must use -protocol paths
grep -q "sc-adversarial-protocol" "$BASE/artifacts/adversarial/specification-draft-v2.md" && \
  echo "PASS: spec-v2 uses -protocol paths" || \
  echo "FAIL: spec-v2 missing -protocol paths"

# Panel review must contain 27 findings reference
grep -q "27" "$BASE/artifacts/adversarial/spec-panel-review.md" && \
  echo "PASS: panel review references findings" || \
  echo "FAIL: panel review missing expected content"

# T01.03 policy must reference EXEMPT
grep -q "EXEMPT" "$BASE/artifacts/T01.03/notes.md" && \
  echo "PASS: T01.03 contains EXEMPT ruling" || \
  echo "FAIL: T01.03 missing expected content"

# D-0007 must contain convergence 0.5 sentinel
grep -q "0.5" "$BASE/artifacts/D-0007/spec.md" && \
  echo "PASS: D-0007 contains 0.5 sentinel" || \
  echo "FAIL: D-0007 missing convergence sentinel"

# D-0008 must contain 0.6 threshold
grep -q "0.6" "$BASE/artifacts/D-0008/spec.md" && \
  echo "PASS: D-0008 contains 0.6 threshold" || \
  echo "FAIL: D-0008 missing convergence threshold"
```

### 6.4 Size Sanity Check

Approach documents should be the largest files. If any approach doc is under 10KB, something is wrong:

```bash
BASE=".dev/releases/current/v2.01-Roadmap-v3/tasklist"

echo "=== Size Sanity Check ==="
for f in \
  "artifacts/approach-1-empirical-probe-first.md" \
  "artifacts/approach-2-claude-p-proposal.md" \
  "artifacts/approach-3-hybrid-dual-path.md" \
  "artifacts/adversarial/specification-draft-v2.md" \
  "artifacts/adversarial/specification-draft-v1.md" \
  "artifacts/adversarial/merged-approach.md"; do
  SIZE=$(stat -c%s "$BASE/$f" 2>/dev/null || echo 0)
  if [ "$SIZE" -lt 10000 ]; then
    echo "WARNING: $f is only ${SIZE} bytes (expected >10KB)"
  else
    echo "OK: $f is ${SIZE} bytes"
  fi
done
```

---

## 7. Missing Artifacts (Referenced but Never Created)

The following 7 artifacts are referenced in approach documents and specifications but were never created during the sprint. They do NOT need to be restored because they never existed. Document their absence for future sprint planning.

| # | Referenced Artifact | Referenced By | Purpose | Notes |
|---|---------------------|---------------|---------|-------|
| 1 | `refs/headless-invocation.md` | Approach 2, merged-approach, spec-v1, spec-v2 | Infrastructure reference file for `claude -p` invocation patterns | Not needed for fallback-only variant |
| 2 | `spec-minimal.md` (probe fixture) | Approach 1, spec-v2 | Minimal SKILL.md fixture for probe testing | Probe never executed beyond initial availability check |
| 3 | `variant-a.md` (probe fixture) | Approach 1, spec-v2 | Variant A fixture for probe testing | Probe never executed beyond initial availability check |
| 4 | `variant-b.md` (probe fixture) | Approach 1, spec-v2 | Variant B fixture for probe testing | Probe never executed beyond initial availability check |
| 5 | `expected-schema.yaml` / `return-contract.yaml` | Approach 1 (Appendix B) | Schema validation file for return contract | Schema defined inline in specs instead |
| 6 | D-0009 artifact | spec-v2 deliverable registry | Unknown (referenced in registry, not described) | Phase 3+ was not executed |
| 7 | D-0010 artifact | spec-v2 deliverable registry | Unknown (referenced in registry, not described) | Phase 3+ was not executed |

**Additional structural gaps** (not individual files but categories):
- No evidence records for Phases 3-5 (T03.01, T03.02, T04.01-T04.03, T05.01-T05.03) -- these phases were not executed
- No `command-skill-policy.md` analysis was performed (referenced by D-0004)
- `sprint-spec.md` is referenced by Approach 1 but not present in the artifact set

---

## 8. Quick Reference: Copy Checklist

Use this checklist to track completion during the restore process:

```
[ ] 1. Directory structure created (Section 2)
[ ] 2. Approach documents copied (3 files)
[ ] 3. Decision artifacts D-0001 to D-0008 copied (8 files)
[ ] 4. Policy artifact T01.03 copied (1 file)
[ ] 5. Adversarial pipeline artifacts copied (8 files)
[ ] 6. Evidence records copied (6 files)
[ ] 7. Checkpoint files copied (2 files)
[ ] 8. File count verification passed (28 files)
[ ] 9. Content spot-checks passed (Section 6.3)
[ ] 10. Size sanity check passed (Section 6.4)
[ ] 11. Path update decision made (Section 5.3: Option A or B)
[ ] 12. HARD-TO-RECREATE artifacts confirmed present (Section 4: 6 files)
```
