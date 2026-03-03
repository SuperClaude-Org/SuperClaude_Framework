# Spec Panel Review: SC-ROADMAP-V2-SPEC + Roadmap

**Reviewed**: `SC-ROADMAP-V2-SPEC.md` (v1.2.0, 1029 lines) + `roadmap.md` (313 lines)
**Reference**: `SuperClaude-Developer-Guide-Commands-Skills-Agents.md` (2064 lines)
**Date**: 2026-02-21
**Panel Mode**: Critique
**Focus**: Requirements, Architecture, Testing

---

## Overall Quality Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Requirements Clarity | 8.2/10 | Strong FRs with explicit acceptance criteria; 3 flags lack behavioral FRs |
| Architecture Consistency | 8.5/10 | refs/ pattern well-aligned with framework; Wave 1A/1B deviation needs justification |
| Testability | 8.0/10 | FR-015 is comprehensive; per-artifact validation scoring underspecified |
| Completeness | 7.8/10 | 3 missing FRs for declared flags; template scoring undefined |
| Composability | 9.0/10 | Return contracts, frontmatter schema, and pipeline position are excellent |

---

## CRITICAL FINDINGS (Must Fix Before Implementation)

### C1: Frontmatter Schema Naming Inconsistency

**Expert**: Karl Wiegers (Requirements) + Martin Fowler (Architecture)
**Severity**: CRITICAL
**Impact**: Will cause breaking change or implementation confusion

The existing `roadmap.md` (the one generated from this spec) uses:
```yaml
generated_by: sc:roadmap
generated_at: "2026-02-21"
```

But the spec (FR-002) defines:
```yaml
generator: sc:roadmap
generated: <ISO-8601 timestamp>
```

**NFR-003 states**: "Fields may be added but not removed or renamed after initial release." This means the spec is already in conflict with its own NFR since the generated roadmap predates the spec's finalization.

**Recommendation**: Choose ONE naming convention and apply it everywhere:
- Option A: Use `generator`/`generated` (spec's convention) — cleaner
- Option B: Use `generated_by`/`generated_at` (existing convention) — backward compatible

Additionally, the existing roadmap has `depth: standard` and `template: inline` in frontmatter but the spec doesn't define these fields. Either add them to the spec or acknowledge them as deprecated.

**Priority**: P0 — Fix before any implementation begins

---

### C2: Three Declared Flags Have No Functional Requirements

**Expert**: Karl Wiegers (Requirements) + Lisa Crispin (Testing)
**Severity**: CRITICAL
**Impact**: Implementers cannot build testable behavior without behavioral contracts

| Flag | In Flags Table (6.2) | Has FR | In Roadmap Deliverables |
|------|----------------------|--------|------------------------|
| `--dry-run` | **NO** (missing from table) | **NO** | Yes (M7 D7.3) |
| `--compliance` | Yes | **NO** | Not explicitly |
| `--template` | Yes | Partial (mentioned in Wave 2) | Yes (M3 D3.1) |

**`--dry-run`**: Neither in the formal flags table (6.2) nor in any FR. Only appears in M7 D7.3 of the roadmap. What does "preview roadmap structure" mean concretely? Console output of milestone tree? YAML skeleton? Frontmatter only?

**`--compliance`**: Listed with "Force compliance tier: strict, standard, light" but no FR defines what compliance tiers mean for roadmap generation. Does STRICT = deeper extraction? More validation rounds? The sc:task-unified compliance tiers don't map directly to a generation command.

**`--template`**: Partially covered in Wave 2 description but the 4-tier discovery algorithm is only in refs/templates.md specification, not as a testable FR.

**Recommendation**:
1. Add **FR-018**: `--dry-run` flag behavior (output format, what gets computed vs skipped)
2. Add **FR-019**: `--compliance` flag behavior for sc:roadmap, OR remove the flag if compliance tiers don't meaningfully apply
3. Elevate the template discovery to an explicit FR or subsection of FR-006 Wave 2

**Priority**: P0 — FRs are the implementation contract

---

### C3: Template Compatibility Scoring Is Referenced But Never Defined

**Expert**: Gojko Adzic (Specification by Example)
**Severity**: HIGH
**Impact**: refs/scoring.md must contain this algorithm but the spec never defines its inputs, outputs, or purpose

Section 9.2 says refs/scoring.md contains "Template compatibility scoring algorithm" but:
- No FR references template compatibility scoring
- The Wave 2 description says "Template discovery (4-tier search with scoring)" but doesn't define what "scoring" means
- No worked example shows how template scoring works

**Recommendation**: Either:
- Add a subsection to FR-006 Wave 2 defining template compatibility scoring (inputs: spec domains + complexity; output: ranked template list with scores)
- OR explicitly note that template scoring is deferred to implementation and documented only in refs/scoring.md

**Priority**: P1 — Ambiguous but implementer can infer from context

---

## MAJOR FINDINGS (Should Fix)

### M1: Wave 1A/1B Deviates from Standard 5-Wave Pattern Without Justification

**Expert**: Martin Fowler (Architecture)
**Severity**: MAJOR
**Impact**: Developers familiar with the standard Wave 0-4 pattern will be confused by subwave numbering

The developer guide defines the standard wave pattern as `Wave 0 → 1 → 2 → 3 → 4`. The spec introduces `Wave 1A` and `Wave 1B` as subwaves. While functional, this creates a 6-step pipeline (0, 1A, 1B, 2, 3, 4) that doesn't match the framework's documented pattern.

**Options**:
- **Option A**: Keep 1A/1B but document the rationale ("conditional subwaves for adversarial mode" — Wave 1A is skipped in single-spec mode)
- **Option B**: Promote to Wave 0 (prereqs), Wave 1 (adversarial consolidation, conditional), Wave 2 (extraction), Wave 3 (planning/template), Wave 4 (generation), Wave 5 (validation). This is cleaner but adds a wave.
- **Option C (Recommended)**: Keep the 5-wave structure. Make Wave 1 handle BOTH consolidation (if --specs) AND extraction sequentially. The "A/B" subwave notation adds complexity without necessity — Wave 1 simply has two phases.

**Recommendation**: Option C. Simplify Wave 1 description to show sequential phases within a single wave.

**Priority**: P2 — Cosmetic but affects developer comprehension

---

### M2: Section Numbering Error (3.3 → 3.5 → 3.4)

**Expert**: Karl Wiegers (Requirements)
**Severity**: MINOR
**Impact**: Undermines spec credibility, confuses cross-references

Section 3.3 (Ref Loading Protocol) is followed by 3.5 (Command File vs SKILL.md Relationship), then 3.4 (SKILL.md Content Outline). The numbering is out of sequence.

**Recommendation**: Reorder to 3.3 → 3.4 → 3.5 in logical sequence.

**Priority**: P3 — Quick fix

---

### M3: Command File Update Missing from M1 Deliverables

**Expert**: Michael Nygard (Production) + Martin Fowler (Architecture)
**Severity**: MAJOR
**Impact**: The command file (`commands/roadmap.md`) is the entry point that users invoke. Without it, the skill cannot be tested.

M1 creates SKILL.md and 5 refs/ files but does NOT include updating `src/superclaude/commands/roadmap.md`. The developer guide explicitly states the workflow: Command file → triggers SKILL.md → loads refs/.

M6 handles "Updated roadmap.md command file" but M6 depends only on M1, meaning it could be done early. However, there's no deliverable for a **minimal** command file in M1 that enables testing.

**Recommendation**: Add D1.6 to M1: "Minimal roadmap.md command file with basic triggers, usage, and SKILL.md activation" (~40 lines). M6 then updates this minimal file with all flags and examples.

**Priority**: P1 — Blocks integration testing of M1

---

### M4: Per-Artifact Validation Scoring Underspecified

**Expert**: Lisa Crispin (Testing)
**Severity**: MAJOR
**Impact**: Wave 4 validates both roadmap.md and test-strategy.md but doesn't define what happens when one passes and the other fails

FR-006 Wave 4 describes validation scoring as PASS/REVISE/REJECT with thresholds. But:
- What if roadmap.md scores 90% (PASS) but test-strategy.md scores 75% (REVISE)?
- Does the REVISE loop regenerate both artifacts or only the failing one?
- Is the validation_score in frontmatter a combined score or per-artifact?

**Recommendation**: Add clarification:
- Define validation_score as the **minimum** of per-artifact scores (conservative)
- REVISE loop regenerates only the failing artifact(s)
- Add `test_strategy_score` and `roadmap_score` sub-fields to frontmatter for transparency

**Priority**: P1 — Prevents ambiguous implementation of the REVISE loop

---

### M5: Divergent Convergence Thresholds Could Confuse

**Expert**: Karl Wiegers (Requirements)
**Severity**: MINOR
**Impact**: Two different convergence thresholds with different consequences

| Threshold | Consequence | Location |
|-----------|------------|----------|
| convergence < 50% | Warning about divergent specs | FR-003 |
| convergence < 60% | Abort or prompt user | FR-011 |
| convergence >= 60% | Proceed with warning | FR-011 |

These are logically consistent (50% warning, <60% abort, >=60% proceed) but scattered across two FRs.

**Recommendation**: Consolidate into a single convergence threshold table in FR-011, with all thresholds and their consequences in one place:

```
| Convergence | Action |
|------------|--------|
| >= 60% | Proceed, log warning in extraction.md |
| 50-59% | Abort (or prompt if --interactive) |
| < 50% | Abort with "specs too divergent" warning |
```

**Priority**: P2 — Clarity improvement

---

### M6: `--output` Default Ambiguous for Multi-Spec Mode

**Expert**: Gojko Adzic (Specification by Example)
**Severity**: MINOR
**Impact**: When `--specs spec1.md,spec2.md` is used, which spec name determines the default output directory?

The default output is `.dev/releases/current/<spec-name>/`. With multiple specs, `<spec-name>` is undefined.

**Recommendation**: Define the rule:
- Multi-spec mode: Use `unified-<first-spec-name>/` as default
- OR require `--output` when using `--specs`

**Priority**: P2

---

## ROADMAP-SPECIFIC FINDINGS

### R1: M1 Scope May Be Too Ambitious

**Expert**: Michael Nygard (Production)
**Severity**: WARNING

M1 requires creating 6 files (SKILL.md + 5 refs/). Each ref file requires detailed algorithmic content. This is essentially writing the entire skill's knowledge base in a single milestone.

**Recommendation**: Consider splitting M1 into:
- M1a: SKILL.md + refs/extraction-pipeline.md + refs/scoring.md (enables M2)
- M1b: refs/templates.md + refs/validation.md + refs/adversarial-integration.md (enables M3-M5)

This gives faster feedback and enables parallel work on M2 sooner.

---

### R2: M4 and M5 Parallel Development Not Reflected in Deliverable Design

**Expert**: Martin Fowler (Architecture)
**Severity**: INFO

The roadmap notes "M4 and M5 can be developed in parallel after M3" but their deliverables don't account for integration. When both merge into M7, there may be conflicts in:
- refs/validation.md (both M4 and M5 touch validation)
- Frontmatter schema additions from both milestones

**Recommendation**: Add an integration note to M7 deliverables acknowledging this merge point.

---

## POSITIVE OBSERVATIONS (Expert Consensus)

The panel unanimously recognizes these strengths:

1. **Return Contract Design** (Fowler, Adzic): The inter-skill composition via typed return contracts is exemplary. `status/merged_output_path/convergence_score/artifacts_dir/unresolved_conflicts` covers all necessary integration points.

2. **Chunked Extraction Protocol** (Wiegers, Nygard): FR-016 is remarkably thorough with 7-step algorithm, 4-pass verification, and explicit failure handling. This is production-grade specification.

3. **YAML Frontmatter as Versioned Contract** (Fowler): NFR-003's additions-only policy with major version bumps for required fields is the correct approach for downstream consumers.

4. **Session Persistence Design** (Nygard): Wave-boundary save points with spec-hash mismatch detection is operationally sound. The resume protocol handles the common failure modes.

5. **Test Strategy Philosophy** (Crispin): The continuous parallel validation approach (FR-007) with computed interleave ratios is innovative and well-reasoned.

6. **refs/ Lazy Loading** (Fowler): Maximum 2-3 refs loaded at any point, with explicit wave-to-ref mapping, aligns perfectly with the framework's token management best practices.

---

## IMPROVEMENT PRIORITY MATRIX

| # | Finding | Impact | Effort | Priority | Recommendation |
|---|---------|--------|--------|----------|---------------|
| C1 | Frontmatter naming inconsistency | HIGH | LOW | P0 | Reconcile `generator`/`generated` naming |
| C2 | 3 flags without FRs | HIGH | MEDIUM | P0 | Add FR-018 (dry-run), FR-019 (compliance), elevate template discovery |
| C3 | Template scoring undefined | MEDIUM | LOW | P1 | Add subsection to FR-006 Wave 2 |
| M3 | Command file missing from M1 | HIGH | LOW | P1 | Add D1.6 minimal command file |
| M4 | Per-artifact validation scoring | HIGH | LOW | P1 | Define min-score rule and per-artifact tracking |
| M1 | Wave 1A/1B naming | LOW | LOW | P2 | Simplify to phases within Wave 1 |
| M5 | Convergence threshold scatter | LOW | LOW | P2 | Consolidate into single table |
| M6 | --output default for multi-spec | LOW | LOW | P2 | Define multi-spec naming convention |
| M2 | Section numbering | LOW | TRIVIAL | P3 | Fix 3.3→3.5→3.4 ordering |
| R1 | M1 scope ambitious | MEDIUM | MEDIUM | P2 | Consider splitting M1 |

---

## EXPERT SIGNATURES

- **Karl Wiegers** (Requirements): "Spec is strong at v1.2.0. The 3 missing FRs for declared flags are the primary gap — every flag needs a testable behavioral contract."
- **Martin Fowler** (Architecture): "The refs/ split pattern is well-executed. Frontmatter naming inconsistency is the most urgent fix — it's a contract issue."
- **Gojko Adzic** (Specification by Example): "FR-014's worked example is good but covers only the simplest case (single-spec, no adversarial). Add a worked example for multi-spec or multi-roadmap mode."
- **Michael Nygard** (Production): "Session persistence design is solid. M1 scope is the main roadmap risk — consider phased delivery."
- **Lisa Crispin** (Testing): "FR-015 test cases are comprehensive. Per-artifact validation scoring needs clarification before Wave 4 implementation."

---

*Generated by /sc:spec-panel in critique mode*
*Reference: SuperClaude-Developer-Guide-Commands-Skills-Agents.md*
