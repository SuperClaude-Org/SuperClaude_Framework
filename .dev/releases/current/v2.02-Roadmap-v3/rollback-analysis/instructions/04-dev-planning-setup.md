# Instruction 04: Dev Planning File Setup After Rollback

**Purpose:** Step-by-step guide for copying all dev planning files back into place after a git rollback to `9060a65` (or master).
**Prerequisite:** You have a backup of the `feature/v2.01-Roadmap-V3` branch (or a tarball/copy of the files listed below).
**Nature:** These are all non-runtime files. Zero production code depends on them. They are planning documents, execution records, and architecture policy.

---

## 1. Complete File Inventory

### 1.1 Tasklist Files

All paths relative to repo root. TASKLIST_ROOT = `.dev/releases/current/v2.01-Roadmap-v3/tasklist/`

| # | File | Role | Priority |
|---|------|------|----------|
| 1 | `TASKLIST_ROOT/tasklist-P1.md` | Phase 1 focused execution view | P2 (derived from P6) |
| 2 | `TASKLIST_ROOT/tasklist-P2.md` | Phase 2 focused execution view | P2 (derived from P6) |
| 3 | `TASKLIST_ROOT/tasklist-P3.md` | Phase 3 focused execution view | P2 (derived from P6) |
| 4 | `TASKLIST_ROOT/tasklist-P4.md` | Phase 4 focused execution view | P2 (derived from P6) |
| 5 | `TASKLIST_ROOT/tasklist-P5.md` | Phase 5 focused execution view | P2 (derived from P6) |
| 6 | `TASKLIST_ROOT/tasklist-P6.md` | **Canonical complete tasklist** (all 6 phases, 18 tasks, 22 deliverables) | **P0 -- Critical** |

NOTE: The synthesis files only mention P5 and P6, but the branch actually contains P1 through P6. All six per-phase files exist and should be preserved.

### 1.2 Checkpoint Reports

| # | File | Role | Priority |
|---|------|------|----------|
| 7 | `TASKLIST_ROOT/checkpoints/CP-P01-END.md` | Phase 1 completion record (probe result, prerequisites, tier policy) | **P0 -- Critical** |
| 8 | `TASKLIST_ROOT/checkpoints/CP-P02-END.md` | Phase 2 completion record (fallback wiring, 8-point audit) | P1 -- Important |

### 1.3 Architecture Policy (DUPLICATION ISSUE)

| # | File | Role | Priority |
|---|------|------|----------|
| 9 | `docs/architecture/command-skill-policy.md` | Architecture policy v1.0.0 (337 lines) -- **canonical location** | **P0 -- Critical** |
| 10 | `src/superclaude/ARCHITECTURE.md` | **Byte-identical copy** of #9 | P3 -- See deduplication recommendation below |

### 1.4 Evidence and Artifact Directories

These directories contain the empirical evidence backing the checkpoint reports. Copy the entire directory trees:

| # | Directory | Contents |
|---|-----------|----------|
| 11 | `TASKLIST_ROOT/artifacts/` | D-0001 through D-0008 subdirs, T01.03 subdir, approach docs (3), adversarial pipeline (8 files) |
| 12 | `TASKLIST_ROOT/evidence/` | T01.01/ through T02.03/ subdirs, each containing result.md |

---

## 2. Copy Instructions

Execute these steps in order. All paths are relative to the repository root.

### Step 1: Create Directory Structure

```bash
# From repo root
mkdir -p .dev/releases/current/v2.01-Roadmap-v3/tasklist/checkpoints
mkdir -p .dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts
mkdir -p .dev/releases/current/v2.01-Roadmap-v3/tasklist/evidence
mkdir -p docs/architecture
```

### Step 2: Copy Tasklist Files

```bash
# Copy all 6 per-phase tasklist files
cp BACKUP/tasklist-P1.md .dev/releases/current/v2.01-Roadmap-v3/tasklist/
cp BACKUP/tasklist-P2.md .dev/releases/current/v2.01-Roadmap-v3/tasklist/
cp BACKUP/tasklist-P3.md .dev/releases/current/v2.01-Roadmap-v3/tasklist/
cp BACKUP/tasklist-P4.md .dev/releases/current/v2.01-Roadmap-v3/tasklist/
cp BACKUP/tasklist-P5.md .dev/releases/current/v2.01-Roadmap-v3/tasklist/
cp BACKUP/tasklist-P6.md .dev/releases/current/v2.01-Roadmap-v3/tasklist/
```

DO NOT copy `tasklist-P copy 2.md`. That file was intentionally deleted (macOS Finder duplicate with problematic filename).

### Step 3: Copy Checkpoint Reports

```bash
cp BACKUP/CP-P01-END.md .dev/releases/current/v2.01-Roadmap-v3/tasklist/checkpoints/
cp BACKUP/CP-P02-END.md .dev/releases/current/v2.01-Roadmap-v3/tasklist/checkpoints/
```

### Step 4: Copy Architecture Policy (Canonical Location Only)

```bash
cp BACKUP/command-skill-policy.md docs/architecture/command-skill-policy.md
```

See Section 5 (Deduplication) for handling the `src/superclaude/ARCHITECTURE.md` copy.

### Step 5: Copy Evidence and Artifact Trees

```bash
# Copy entire directory trees recursively
cp -r BACKUP/artifacts/ .dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/
cp -r BACKUP/evidence/  .dev/releases/current/v2.01-Roadmap-v3/tasklist/evidence/
```

Expected artifact structure after copy:
```
artifacts/
  D-0001/evidence.md
  D-0002/notes.md
  D-0003/evidence.md
  D-0004/evidence.md
  D-0005/evidence.md
  D-0006/spec.md
  D-0007/spec.md
  D-0008/spec.md
  T01.03/notes.md
  approach-1-empirical-probe-first.md
  approach-2-claude-p-proposal.md
  approach-3-hybrid-dual-path.md
  adversarial/
    debate-transcript.md
    scoring-rubric.md
    base-selection.md
    refactoring-plan.md
    merged-approach.md
    specification-draft-v1.md
    spec-panel-review.md
    specification-draft-v2.md

evidence/
  T01.01/result.md
  T01.02/result.md
  T01.03/result.md
  T02.01/result.md
  T02.02/result.md
  T02.03/result.md
```

---

## 3. Path Updates Needed (Old Skill Paths to `-protocol`)

After copying, the following files contain stale path references using old directory names (e.g. `sc-adversarial/` instead of `sc-adversarial-protocol/`). These references should be updated IF the skill directory renames are being preserved in the recreation.

### 3.1 Files Requiring Path Updates

**Tasklist files (all 6):**
- `tasklist-P1.md` -- references `sc-adversarial/SKILL.md`, `sc-roadmap/SKILL.md`, `sc-roadmap/refs/adversarial-integration.md`
- `tasklist-P2.md` -- references `sc-roadmap/SKILL.md` (multiple occurrences)
- `tasklist-P3.md` -- references `sc-roadmap/SKILL.md`, `sc-adversarial/SKILL.md`
- `tasklist-P4.md` -- references `sc-adversarial/SKILL.md`, `sc-roadmap/refs/adversarial-integration.md`, `sc-roadmap/SKILL.md`
- `tasklist-P5.md` -- references `sc-roadmap/SKILL.md`, `sc-roadmap/refs/adversarial-integration.md`, `sc-adversarial/SKILL.md`
- `tasklist-P6.md` -- references `sc-roadmap/refs/adversarial-integration.md`, `sc-adversarial/SKILL.md`, `sc-roadmap/SKILL.md`

**Checkpoint file:**
- `checkpoints/CP-P01-END.md` -- line 20 references `sc-adversarial/SKILL.md`, `sc-roadmap/SKILL.md`

**Architecture policy:**
- `docs/architecture/command-skill-policy.md` -- contains old paths in the migration table (showing before/after). These references are INTENTIONAL (they document the migration from old to new) and should NOT be updated.

### 3.2 Replacement Commands

Run these from the tasklist directory (`.dev/releases/current/v2.01-Roadmap-v3/tasklist/`):

```bash
# Update all tasklist and checkpoint files
# NOTE: Do NOT run this on command-skill-policy.md (its old paths are intentional documentation)

FILES=(
  tasklist-P1.md tasklist-P2.md tasklist-P3.md
  tasklist-P4.md tasklist-P5.md tasklist-P6.md
  checkpoints/CP-P01-END.md
)

for f in "${FILES[@]}"; do
  sed -i \
    -e 's|skills/sc-adversarial/|skills/sc-adversarial-protocol/|g' \
    -e 's|skills/sc-roadmap/|skills/sc-roadmap-protocol/|g' \
    -e 's|skills/sc-cleanup-audit/|skills/sc-cleanup-audit-protocol/|g' \
    -e 's|skills/sc-task-unified/|skills/sc-task-unified-protocol/|g' \
    -e 's|skills/sc-validate-tests/|skills/sc-validate-tests-protocol/|g' \
    "$f"
done
```

### 3.3 Dev Artifact Path References (Optional)

24 of 25 dev artifact files also use old paths. Only `specification-draft-v2.md` uses the corrected `-protocol` suffix. These are historical documents recording the state at creation time. Two options:

- **Option A (Recommended):** Accept as historical. Add a note at the top of the artifacts directory README (if one exists) that pre-Phase-3 artifacts use legacy path names.
- **Option B:** Batch-update all artifact files with the same `sed` commands above. This rewrites history but keeps paths resolvable.

---

## 4. Architecture Policy Duplication Issue

### Problem

Two byte-identical 337-line files exist with no canonical marker:
- `docs/architecture/command-skill-policy.md`
- `src/superclaude/ARCHITECTURE.md`

Neither file references the other. No `make sync` target covers this pair. Future edits to one will silently diverge from the other.

### Recommendation: Keep `docs/architecture/`, Remove the `src/` Duplicate

**Rationale:**
- `docs/architecture/` is the natural home for architecture policy documents
- `src/superclaude/` is for distributable Python package source, not policy docs
- The filename mismatch (`command-skill-policy.md` vs `ARCHITECTURE.md`) adds confusion
- The `make sync-dev` target already handles `src/ -> .claude/` sync for skills/agents; adding a policy doc sync to a different directory pattern would be awkward

**Steps:**

```bash
# Option 1: Remove the duplicate (cleanest)
rm src/superclaude/ARCHITECTURE.md

# Option 2: Replace with a pointer file (preserves discoverability)
cat > src/superclaude/ARCHITECTURE.md << 'EOF'
# Architecture Policy

The canonical architecture policy document lives at:
`docs/architecture/command-skill-policy.md`

This file is a pointer. Do not duplicate content here.
EOF

# Option 3: Symlink (works on Linux/Mac, may cause issues on Windows or in packaging)
rm src/superclaude/ARCHITECTURE.md
ln -s ../../docs/architecture/command-skill-policy.md src/superclaude/ARCHITECTURE.md
```

Option 1 is recommended. Option 2 is acceptable if developer discoverability in `src/` is valued.

---

## 5. Verification Checklist

After all copies are in place, run these checks to confirm completeness and consistency.

### 5.1 File Existence

```bash
REPO_ROOT="."  # adjust as needed
TROOT="$REPO_ROOT/.dev/releases/current/v2.01-Roadmap-v3/tasklist"

echo "=== Tasklist files ==="
for i in 1 2 3 4 5 6; do
  [ -f "$TROOT/tasklist-P${i}.md" ] && echo "PASS: tasklist-P${i}.md" || echo "FAIL: tasklist-P${i}.md MISSING"
done

echo "=== Checkpoints ==="
for cp in CP-P01-END.md CP-P02-END.md; do
  [ -f "$TROOT/checkpoints/$cp" ] && echo "PASS: $cp" || echo "FAIL: $cp MISSING"
done

echo "=== Architecture Policy ==="
[ -f "$REPO_ROOT/docs/architecture/command-skill-policy.md" ] && echo "PASS: command-skill-policy.md" || echo "FAIL: command-skill-policy.md MISSING"

echo "=== Evidence records ==="
for t in T01.01 T01.02 T01.03 T02.01 T02.02 T02.03; do
  [ -f "$TROOT/evidence/$t/result.md" ] && echo "PASS: evidence/$t" || echo "FAIL: evidence/$t MISSING"
done

echo "=== Decision artifacts ==="
for d in D-0001 D-0002 D-0003 D-0004 D-0005 D-0006 D-0007 D-0008; do
  ls "$TROOT/artifacts/$d/"*.md >/dev/null 2>&1 && echo "PASS: artifacts/$d" || echo "FAIL: artifacts/$d MISSING"
done
[ -f "$TROOT/artifacts/T01.03/notes.md" ] && echo "PASS: artifacts/T01.03" || echo "FAIL: artifacts/T01.03 MISSING"

echo "=== Approach documents ==="
for a in approach-1-empirical-probe-first.md approach-2-claude-p-proposal.md approach-3-hybrid-dual-path.md; do
  [ -f "$TROOT/artifacts/$a" ] && echo "PASS: $a" || echo "FAIL: $a MISSING"
done

echo "=== Adversarial pipeline ==="
for f in debate-transcript.md scoring-rubric.md base-selection.md refactoring-plan.md merged-approach.md specification-draft-v1.md spec-panel-review.md specification-draft-v2.md; do
  [ -f "$TROOT/artifacts/adversarial/$f" ] && echo "PASS: adversarial/$f" || echo "FAIL: adversarial/$f MISSING"
done
```

### 5.2 Path Consistency (Post-Update)

```bash
# Should return 0 matches if path updates were applied correctly
echo "=== Stale path check (tasklist + checkpoints) ==="
grep -rl 'skills/sc-adversarial/' "$TROOT"/tasklist-P*.md "$TROOT"/checkpoints/*.md 2>/dev/null
grep -rl 'skills/sc-roadmap/' "$TROOT"/tasklist-P*.md "$TROOT"/checkpoints/*.md 2>/dev/null
grep -rl 'skills/sc-cleanup-audit/' "$TROOT"/tasklist-P*.md "$TROOT"/checkpoints/*.md 2>/dev/null
echo "(No output above = PASS)"
```

### 5.3 Content Integrity

```bash
# Canonical tasklist should have all 6 phases
echo "=== Phase coverage in P6 ==="
grep -c "^### Phase" "$TROOT/tasklist-P6.md"
# Expected: 6

# Architecture policy should be 337 lines
echo "=== Policy line count ==="
wc -l < "$REPO_ROOT/docs/architecture/command-skill-policy.md"
# Expected: 337

# CP-P01-END should contain the TOOL_NOT_AVAILABLE finding
echo "=== Critical probe result ==="
grep -c "TOOL_NOT_AVAILABLE" "$TROOT/checkpoints/CP-P01-END.md"
# Expected: >= 1
```

### 5.4 Deduplication Check

```bash
# Verify src/superclaude/ARCHITECTURE.md is either removed or is a pointer/symlink
if [ -f "$REPO_ROOT/src/superclaude/ARCHITECTURE.md" ]; then
  if [ -L "$REPO_ROOT/src/superclaude/ARCHITECTURE.md" ]; then
    echo "OK: ARCHITECTURE.md is a symlink"
  elif diff -q "$REPO_ROOT/docs/architecture/command-skill-policy.md" "$REPO_ROOT/src/superclaude/ARCHITECTURE.md" >/dev/null 2>&1; then
    echo "WARNING: ARCHITECTURE.md is still a full duplicate -- resolve per Section 4"
  else
    echo "OK: ARCHITECTURE.md has been replaced with a pointer"
  fi
else
  echo "OK: ARCHITECTURE.md removed (cleanest option)"
fi
```

---

## 6. Critical Preservation Notes

### CP-P01-END.md Contains Irreproducible Empirical Data

**This is the single most important file to preserve correctly.**

`CP-P01-END.md` records the T01.01 probe result: the Claude Code `Skill` tool returned `TOOL_NOT_AVAILABLE`. This is an empirical observation about the runtime environment at the time of testing (2026-02-23). Key properties:

- The probe result **cannot be reconstructed from source code** -- it required running the Skill tool in a live Claude Code session and observing the error.
- The result **determined the entire sprint variant** (FALLBACK-ONLY). Every downstream task in Phases 2-6 was shaped by this single finding.
- The **pre-execution confidence was 40%** -- this was a genuine probe with uncertain outcome, not a foregone conclusion.
- If the Skill tool becomes available in a future Claude Code version, the probe result would differ, but the **historical record** of what was found on 2026-02-23 remains valid and should be preserved as-is.

Additionally, CP-P01-END.md contains the T01.03 tier classification policy decision: executable `.md` files are NOT exempt from compliance. This affects 9 downstream tasks. While this decision could be re-reasoned, the specific reasoning chain and confidence assessment are captured only in this file.

### Evidence Records Back the Checkpoints

The `evidence/` directory contains the raw verification data that supports the checkpoint claims. Without `evidence/T01.01/result.md`, the probe result in CP-P01-END.md has no backing evidence. Without `evidence/T02.03/result.md`, the 8-point structural audit in CP-P02-END.md cannot be independently verified.

### Decision Artifacts Encode the Design Process

The `artifacts/adversarial/` directory contains the full adversarial debate pipeline output (debate transcript, scoring rubric, merged approach, two specification drafts, panel review). This represents substantial design work that cannot be mechanically regenerated -- the debate decisions, scoring, and expert panel findings are products of specific analytical sessions.

---

## 7. Summary: Execution Order

1. Create directory structure (Step 1)
2. Copy tasklist-P6.md first (canonical source of truth)
3. Copy tasklist-P1 through P5 (focused views)
4. Copy CP-P01-END.md and CP-P02-END.md (checkpoint records)
5. Copy `command-skill-policy.md` to `docs/architecture/`
6. Copy entire `artifacts/` and `evidence/` directory trees
7. Resolve the ARCHITECTURE.md duplication (Section 4)
8. Run path updates if skill renames are in effect (Section 3)
9. Run verification checklist (Section 5)
10. Confirm CP-P01-END.md contains `TOOL_NOT_AVAILABLE` (Section 6)
