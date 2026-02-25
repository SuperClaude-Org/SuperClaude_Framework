# v2.01 Extraction: Planning & Artifacts Patterns

**Source**: `v2.02-Roadmap-v3/rollback-analysis/instructions/04-dev-planning-setup.md` and `05-dev-artifacts-setup.md`
**Extraction date**: 2026-02-24
**Filter**: v2.01-relevant architectural patterns only. v2.02-specific task IDs, file paths, and copy commands excluded.

---

## 1. Sprint Artifact Directory Structure Pattern

A reusable three-tier directory structure for organizing sprint execution artifacts:

```
<release-root>/tasklist/
├── tasklist-P{N}.md          # Per-phase focused execution views (derived)
├── tasklist-P{MAX}.md        # Canonical complete tasklist (all phases) -- P0 CRITICAL
├── artifacts/
│   ├── D-{NNNN}/             # Numbered decision artifacts (evidence.md, notes.md, spec.md)
│   ├── T{NN.NN}/             # Task-linked policy/notes artifacts
│   ├── approach-{N}-*.md     # Alternative approach documents (pre-decision)
│   └── adversarial/          # Adversarial pipeline outputs (debate, scoring, specs)
├── evidence/
│   └── T{NN.NN}/result.md    # Per-task verification results
└── checkpoints/
    └── CP-P{NN}-END.md       # Phase completion checkpoint reports
```

**Key design principles**:
- Artifacts are organized by type (decisions, evidence, checkpoints), not by phase or date.
- Decision artifacts use a sequential numbering scheme (`D-0001`, `D-0002`, ...) for stable referencing.
- Evidence records map 1:1 to task IDs (`T01.01/result.md` backs task T01.01).
- The canonical tasklist (`P{MAX}`) is the single source of truth; per-phase files are derived views.
- Checkpoint reports summarize phase-level outcomes and are the primary cross-reference documents.

**Applicability to v2.01**: This structure should be adopted for the v2.01 Architecture Refactor sprint organization. The three-tier split (artifacts / evidence / checkpoints) enforces separation of design work, verification data, and summary reporting.

---

## 2. Evidence Chain Structure

A general QA pattern for traceable decision-making:

```
evidence/T{NN.NN}/result.md   -- raw verification result (PASS/FAIL + data)
        |
        v
artifacts/D-{NNNN}/           -- decision artifact citing the evidence
        |
        v
checkpoints/CP-P{NN}-END.md   -- phase summary referencing decisions + evidence
```

**Chain properties**:
- **Bottom-up construction**: Evidence is gathered first, then decisions reference evidence, then checkpoints reference decisions.
- **Independent verifiability**: Each evidence record can be audited without reading the checkpoint.
- **Traceability**: Any claim in a checkpoint can be traced back to a specific evidence record via a decision artifact.

**Anti-pattern observed**: Checkpoints that make claims without linking to evidence records. The v2.02 sprint explicitly structured evidence records to prevent this.

**v2.01 adoption**: Every architectural decision in the refactor should have a backing evidence record. Phase checkpoints should cite specific `D-{NNNN}` artifacts rather than making unsupported assertions.

---

## 3. Deduplication Recommendation

**Observed problem**: Two byte-identical copies of an architecture policy document existed in different locations (`docs/architecture/` and `src/superclaude/`) with no canonical marker and no sync mechanism. Future edits to one would silently diverge from the other.

**General principle**: Architecture and policy documents should live in ONE canonical location. The recommended canonical home is `docs/architecture/` (not `src/`), because:
- `src/` is for distributable package source, not policy documents.
- Filename mismatches between copies (e.g., `command-skill-policy.md` vs `ARCHITECTURE.md`) add confusion.
- Existing sync mechanisms (`make sync-dev`) cover specific component types; adding ad-hoc policy sync would be inconsistent.

**Resolution options** (in order of preference):
1. Remove the duplicate entirely (cleanest).
2. Replace the duplicate with a pointer file referencing the canonical location.
3. Symlink (works on Linux/Mac, may cause packaging issues).

**v2.01 rule**: Any architecture document produced during the refactor must have exactly one canonical location. If discoverability from multiple paths is needed, use pointer files, not copies.

---

## 4. HARD-to-Recreate Classification

A framework for classifying work products by recreation difficulty, determining preservation vs. regeneration strategy:

### Classification Criteria

| Classification | Characteristics | Preservation Priority | Example |
|---|---|---|---|
| **HARD** | Original creative/stochastic output. Contains emergent reasoning, adversarial debate outcomes, or empirical observations that cannot be deterministically reproduced. | MUST preserve. Budget 4-8 hours to reproduce if lost. | Debate transcripts, scoring rubrics, approach designs, empirical probe results |
| **MEDIUM-HARD** | Reproducible given specific inputs, but exact outputs (finding numbers, cross-references, line numbers) would differ on re-run. | Should preserve. ~2 hours to reproduce. | Panel reviews with line-number references to source documents |
| **EASY / Derived** | Mechanically derivable from other artifacts. Can be regenerated from canonical sources. | Low priority. Minutes to reproduce. | Per-phase tasklist views derived from canonical tasklist, path-updated copies |

### What Makes Something HARD-to-Recreate

1. **Original design work**: Architectural reasoning, strategy formulation, risk identification, decision gate design. These involve creative synthesis that varies across sessions.
2. **Stochastic adversarial outputs**: Debate transcripts, convergence decisions, scoring outcomes. The emergent reasoning and specific advocate arguments differ on every run.
3. **Empirical observations**: Runtime probe results that depend on environment state at a specific point in time. A future re-run may produce different results.
4. **Absorption/integration decisions**: Which features from losing approaches get absorbed into the winner. These depend on the exact debate and scoring context.

### Preservation Priority Order

When backup space or attention is limited, preserve in this order:
1. Most mature synthesis document (addresses all review findings).
2. Source approach documents (enable full re-derivation).
3. Foundational empirical evidence (determines trajectory).
4. Review findings (drove evolution).
5. Debate transcripts (shaped architecture).
6. Everything else (reconstructable from above).

**v2.01 application**: Before starting any design phase, classify expected outputs by recreation difficulty. HARD outputs should be committed to version control immediately upon creation, not batched with other changes.

---

## 5. Compliance Tier Classification for Executable .md Files

**Policy decision observed**: Executable `.md` files (skill definitions, command specifications) are NOT exempt from compliance enforcement, even though they are markdown files.

**Rationale**: The compliance tier system classifies tasks by risk. While documentation-only `.md` files (READMEs, guides) qualify for EXEMPT tier, `.md` files that define executable behavior (SKILL.md files, command definitions, protocol specifications) carry the same risk as code changes. They should be classified at STANDARD or STRICT tier depending on scope.

**Classification rule**:
- `.md` files in `docs/`, `README*`, `CHANGELOG*` -> EXEMPT tier
- `.md` files that define executable behavior (skills, commands, agents, protocols) -> STANDARD minimum, STRICT if multi-file or security-adjacent

**Impact**: This classification affected 9 downstream tasks in the observed sprint. Any v2.01 task that modifies skill definitions, command specifications, or protocol documents must go through at minimum STANDARD compliance, not EXEMPT.

**v2.01 relevance**: The architecture refactor will likely modify multiple SKILL.md and command definition files. These must not be treated as "just documentation" for compliance purposes.

---

## 6. Scope Creep Warning: Referenced-but-Never-Created Artifacts

**Observed pattern**: 7 artifacts were referenced in approach documents and specifications but were never actually created during sprint execution. Categories:

| Type | Count | Why Never Created |
|---|---|---|
| Probe test fixtures (minimal SKILL.md, variant files) | 3 | Probe never executed beyond initial availability check; the runtime environment answered the question before fixtures were needed. |
| Infrastructure reference files | 1 | Not needed for the fallback-only variant that was selected. |
| Schema/contract files | 1 | Schema was defined inline in specifications instead of as a separate file. |
| Future-phase artifacts (D-0009, D-0010) | 2 | Referenced in a deliverable registry but phases 3+ were never executed. |

**General lessons**:
1. **Approach documents will reference artifacts that may never exist.** This is normal -- approaches describe potential paths, not guaranteed outputs. Do not treat referenced artifacts as commitments.
2. **Deliverable registries should distinguish "planned" from "created."** A registry entry without an existence check creates false expectations.
3. **Early empirical probes can eliminate entire branches of planned work.** The sprint's initial probe eliminated the need for 3 test fixtures and 1 infrastructure file. This is a feature, not a failure -- it represents scope reduction through evidence.
4. **Inline definitions vs. separate files**: When a schema or contract is small enough, defining it inline in the spec is preferable to creating a separate file that adds coordination overhead.

**v2.01 application**: During sprint planning, mark deliverables as CONDITIONAL when they depend on outcomes of earlier tasks. Do not count conditional deliverables toward sprint velocity until the condition is resolved.

---

## 7. General Sprint Planning Structure Lessons

### Canonical Source of Truth

- Maintain exactly one canonical tasklist that contains all phases. Per-phase views should be derived (generated or filtered), not independently authored.
- If per-phase files exist alongside a canonical file, the canonical file wins on any conflict.

### Phase Checkpoint Pattern

- Each phase ends with a checkpoint report (`CP-P{NN}-END.md`).
- Checkpoints must reference specific evidence records and decision artifacts.
- Checkpoints record irreproducible empirical data (probe results, environment observations) that cannot be reconstructed from source code alone.

### Historical Path References in Artifacts

- When directory renames occur mid-sprint, pre-rename artifacts become historically inaccurate but contextually correct.
- **Recommended approach**: Accept artifacts as historical records. Add a path-note header rather than batch-updating old paths. This preserves the historical record while maintaining navigability.
- Exception: Active planning documents (tasklists, checkpoints) SHOULD be updated to reflect current paths, since they are used for ongoing navigation.

### File Naming Hygiene

- Avoid filenames with spaces or OS-generated suffixes (e.g., macOS Finder "copy 2" duplicates). These cause problems in bash scripts and version control.
- Decision artifacts should use stable, sequential identifiers (`D-0001`, not descriptive names that might need renaming).

### Verification as a First-Class Artifact

- Verification scripts (file existence checks, content spot-checks, size sanity checks) should be written alongside the artifacts they verify, not as an afterthought.
- A verification checklist serves double duty: it confirms completeness during setup AND documents the expected structure for future maintainers.
