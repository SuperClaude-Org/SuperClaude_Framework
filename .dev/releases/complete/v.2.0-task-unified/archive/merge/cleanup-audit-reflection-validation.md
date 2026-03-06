# sc:cleanup-audit Proposals — Reflection & Validation Report

**Date**: 2026-02-20
**Method**: Sequential thinking analysis across 5 validation dimensions
**Input**: cleanup-audit-improvement-proposals.md (12 proposals from 4-agent debate)

---

## Overall Verdict

The proposals are **individually sound but collectively have structural issues** that must be addressed before implementation. Three critical findings emerged from validation:

1. **The spec-implementation gap is the #1 issue not addressed** — the current `sc:cleanup-audit` spec already promises 5 categories, coverage tracking, checkpointing, and evidence-gated classification that weren't implemented
2. **Token cost estimates are systematically low by 2-3x** — particularly P4 (Evidence-Mandatory KEEP) which alone could double total audit cost
3. **Dependency ordering is wrong** — Proposal 1 (Cross-Reference) is ranked #1 but depends on infrastructure from Proposals 6 and 11 which are ranked #6 and #11

---

## Dimension 1: Internal Consistency

### Issues Found

**CRITICAL: Hidden Dependency Chain**
```
P11 (Scan Profile) → P6 (Batch Decomposition) → P1 (Cross-Reference) → P10 (Deduplication)
```
Proposal 1 requires structured scanner output with `external_dependencies` and `export_targets` fields. These fields don't exist in current scanner output. P1 cannot work until P6 or P11 creates domain-aware scanners that produce this schema. Yet P1 is ranked #1 and P6/P11 are ranked #6/#11.

**HIGH: Coverage/Evidence Tier Mismatch**
P3 (Coverage) defines tiers by file criticality: critical/high/standard/low.
P4 (Evidence KEEP) defines tiers by evidence depth: A/B/C/D.
These are **different classification schemes** that need to be unified — a file classified as "critical" for coverage should also be "Tier A" for evidence, but the proposals don't establish this mapping.

**MEDIUM: INVESTIGATE Category Orphan**
P1 introduces INVESTIGATE as a cross-boundary classification, but P8 (Categories) doesn't include it in the report structure. The two-tier system (DELETE/KEEP/MODIFY + qualifier) has no place for INVESTIGATE.

**MEDIUM: Config Bootstrapping Gap**
P5 requires `audit.config.yaml` with project-specific values but says "fail explicitly if absent." This makes the improved tool LESS usable than the current version on cold-start. No proposal addresses config generation.

---

## Dimension 2: Feasibility Against Subagent Architecture

### Key Discovery: Spec Already Defines Missing Features

The **current** `sc:cleanup-audit` spec (`/config/.claude/commands/sc/cleanup-audit.md`) already includes:
- 5 classification categories: `DELETE/CONSOLIDATE/MOVE/FLAG/KEEP`
- Coverage tracking: "transparently report what was and was not audited"
- Incremental checkpointing: "resume-from-checkpoint on session interruption"
- Evidence-gated classification: "requiring grep proof for every recommendation"
- Spot-check validation: "10%"

Several proposals reinvent features the spec already promises. The PRD should distinguish **"enforce existing spec"** from **"add new capabilities."**

### Feasibility Per Proposal

| Proposal | Feasibility | Notes |
|----------|-------------|-------|
| P1 (Cross-Reference) | Feasible | Requires structured scanner output first |
| P2 (Credential Scan) | Feasible, Low Cost | Can be orchestrator Bash, no subagent needed |
| P3 (Coverage Manifest) | Feasible, Moderate | Manifest must be disk-persisted, not in-context |
| P4 (Evidence KEEP) | Feasible, **Expensive** | 585-1,171 files at Tier A = major token cost |
| P5 (File-Type Rules) | Feasible | Needs default config generation, not hard fail |
| P6 (Batch Decomposition) | Feasible, Moderate | Replaces scanner spawning logic |
| P7 (Calibration Files) | **Risky** | No known-good/bad files on cold-start |
| P8 (Categories) | Already in spec! | Spec has 5 categories; proposal refines to two-tier |
| P9 (Doc Audit) | Feasible | New pass, bounded by token cap |
| P10 (Deduplication) | Feasible, Trivial | Consolidator prompt enhancement |
| P11 (Scan Profile) | Feasible, Low Cost | Haiku pre-pass |
| P12 (Signal-Triggered Depth) | Feasible, Low Cost | Prompt engineering |

---

## Dimension 3: Runtime/Token Impact Realism

### Token Cost Estimates are Systematically Low

**P4 (Evidence-Mandatory KEEP)** is the most significant underestimate:
- Tier A = 10-20% of 5,857 files = 585-1,171 files
- Each requires ~3 grep operations + content read = ~300-500 tokens/file
- Total: **175K-585K additional tokens** (current audit likely uses ~100-150K total)
- P4 alone could **double or triple** the total audit cost

**P6 (Batch Decomposition)** underestimates prompt overhead:
- Going from 6 scanners to 20+ batches adds ~2-3K tokens per spawn for system prompt
- Additional overhead: **40-60K tokens** in prompt duplication

**P12 (Signal-Triggered Depth)** assumes low trigger rate:
- In messy codebases (the target audience), trigger rate could be 40-50%, not 15-20%
- Actual overhead may be +40-50% rather than +15-20%

### Revised Estimates

| Phase | Proposed | Realistic | Key Driver |
|-------|----------|-----------|------------|
| After Tier 1 | ~55 min, +25% tokens | **~80 min, +60-100% tokens** | P4 evidence gathering |
| After Tier 1+2 | ~65 min, +50% tokens | **~100 min, +100-150% tokens** | P6 batch overhead |
| After All | ~75 min, +80% tokens | **~120-150 min, +150-200% tokens** | Cumulative |

### Mitigation
Add a `--budget` flag with hard token ceiling. Orchestrator allocates proportionally across phases and cuts low-priority work when approaching limit.

---

## Dimension 4: Missing Risks and Failure Modes

### Risk 1: Config File Bootstrapping (P5) — HIGH
First-run users without `audit.config.yaml` get an error. Fix: Generate sensible defaults on first run with project-structure heuristics (detect port from docker-compose, detect framework from package.json).

### Risk 2: Calibration File Cold Start (P7) — HIGH
No known-good/bad files exist for unfamiliar codebases. P7 is the weakest proposal — high complexity for uncertain benefit. Fix: Use synthetic calibration (inject temporary test file) OR defer calibration to second audit run using prior results.

### Risk 3: Manifest Size Scaling (P3) — MEDIUM
For monorepos with 50,000+ files, per-file manifests become unwieldy. Fix: Track per-directory coverage above N files threshold.

### Risk 4: Dynamic Import False Positives (P1, P4) — HIGH
Next.js codebase uses `next/dynamic` and `React.lazy()` extensively. Files used only via dynamic import show zero static references. Fix: Add dynamic import pattern detection scanning for `import(`, `require(`, `React.lazy`, `next/dynamic`.

### Risk 5: LLM Output Schema Compliance (P1, P7, P8) — MEDIUM
Multiple proposals require valid JSON from LLM subagents. Malformed output breaks synthesis. Fix: Add schema validation post-processing with common malformation repair.

### Risk 6: Report Overwhelming — MEDIUM
From ~300-line report to potentially thousands of lines. Fix: Add `--report-depth summary|standard|detailed` flag. Default to summary with links to sections.

### Risk 7: Spec-Implementation Gap — CRITICAL
Adding features to a spec that already has unimplemented features creates a larger gap. The PRD must address baseline spec compliance before new features.

---

## Dimension 5: Priority Ranking Assessment

### Current Ranking Problems

1. **P1 (Cross-Reference) at #1 is WRONG** — it depends on P6/P11 infrastructure. Without structured scanner output, the synthesis phase has nothing to operate on.

2. **P2 (Credential Scan) at #2 is CORRECT** — low cost, correctness fix, no dependencies.

3. **P3/P4 (Coverage + Evidence KEEP) at #3/#4** — must be co-designed as they share the file classification scheme.

4. **P7 (Calibration) viability is questionable** — cold-start problem makes it unreliable for first-run audits.

### Recommended Revised Ordering

**Phase 0: Enforce Existing Spec**
- Make the current spec's 5 categories actually work (DELETE/CONSOLIDATE/MOVE/FLAG/KEEP)
- Implement the existing coverage tracking promise
- Implement the existing checkpointing promise
- Implement evidence-gated classification as specified

**Phase 1: Correctness Fixes** (P2, P15)
- Credential file scanning fix (P2)
- Gitignore consistency check (P15)
- These fix WRONG ANSWERS, not missing depth

**Phase 2: Infrastructure** (P6, P11, P3)
- Scan profile detection (P11) — lightweight, enables everything else
- Dynamic batch decomposition (P6) — produces structured output
- Coverage manifest (P3) — tracks what's examined
- Co-design P3/P4 tier classification scheme

**Phase 3: Depth Improvements** (P4, P1, P5)
- Evidence-mandatory KEEP at Tier A (P4) — with hard budget ceiling
- Cross-reference resolution (P1) — now has structured output to consume
- File-type-specific rules (P5) — with auto-generated default config

**Phase 4: Quality & Polish** (P8, P10, P12)
- Two-tier recommendation categories (P8)
- Post-hoc deduplication (P10)
- Signal-triggered depth (P12)

**Phase 5: Extensions** (P9, P7, P13, P14)
- Documentation audit pass (P9) — opt-in
- Anti-lazy enforcement via calibration (P7) — after baseline data exists
- Pass-level checkpointing (P13)
- Broken reference collection (P14)

---

## Validation Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Internal Consistency | 6/10 | Dependency chain issues, tier classification mismatch, orphaned category |
| Architecture Feasibility | 8/10 | All proposals feasible; P7 risky; spec already covers several features |
| Runtime Estimates | 4/10 | Systematically underestimated by 2-3x; P4 cost is dominant factor |
| Risk Coverage | 5/10 | 8 missing risks identified; cold-start problems unaddressed |
| Priority Ranking | 5/10 | Dependency ordering wrong; spec gap unrecognized; phases needed |

**Overall: 5.6/10 — Proposals are directionally correct but need restructuring before they can become a PRD.**

### Critical Changes for PRD

1. **Add Phase 0**: Enforce existing spec before adding features
2. **Fix dependency ordering**: Infrastructure (P6, P11) before features that consume it (P1)
3. **Co-design P3/P4**: Unify coverage tiers and evidence tiers
4. **Add budget controls**: `--budget` flag with proportional allocation
5. **Address cold-start**: Default config generation for P5; defer calibration for P7
6. **Revise token estimates**: 2-3x higher than proposed
7. **Add report depth control**: `--report-depth` flag to manage output volume
8. **Add INVESTIGATE to category system**: Bridge P1 and P8

---

*Reflection validation complete | 2026-02-20*
