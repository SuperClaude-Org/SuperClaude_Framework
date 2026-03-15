# Strategy: LW Component — Quality Gates

**Component**: Quality Gates
**Source**: `.gfdoc/rules/core/quality_gates.md`
**Path Verified**: true
**Strategy Analyzable**: true
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

The quality gates system defines a structured, multi-dimensional verification framework with universal principles that apply across all output types, plus output-type-specific gate tables.

**Core rigor mechanisms:**

- **Universal six principles**: Verifiability (traceable to requirements), Completeness (all requirements satisfied), Correctness (technically accurate), Consistency (uniform conventions), Clarity (well-structured), Anti-Sycophancy v5.2 (factually accurate over agreeable). `quality_gates.md:57-64`
- **Output-type-specific gate tables**: Different gate categories apply to code outputs, analysis/report outputs, and opinion outputs. This prevents both over-checking (applying code gates to docs) and under-checking (skipping evidence gates for analysis). `quality_gates.md:86-131`
- **Three-tier severity system**: Sev 1 (critical/blocks — immediate fix), Sev 2 (important — fix in cycle), Sev 3 (minor — fix when able). `quality_gates.md:157-165`
- **Evidence verification requirements**: Every technical claim requires a structured evidence table with explicit "Verified" or "Unverified" status. `quality_gates.md:134-148`
- **Anti-sycophancy as a first-class gate**: Factual accuracy over agreeableness is a universal gate principle, not an optional add-on. `quality_gates.md:64`
- **Task completion checklist**: Six mandatory conditions before any task is complete, including "no placeholder content remains." `quality_gates.md:149-156`

**Rigor verdict**: The explicit severity tiers and the mandatory task completion checklist are well-designed. The distinction between gate categories by output type prevents false positives (requiring code linting for documentation).

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- The gate tables are comprehensive but assume a human or agent will manually apply each check row by row. There is no automation described in the gate specification itself — it defers to "linting tools," "schema validators," etc. as future work. `quality_gates.md:167-185`
- The opinion analysis gate category (applying only to `/rf:opinion` outputs) creates a special case that adds cognitive load to gate application.

**Operational drag:**
- The evidence table requirement for all technical claims adds significant per-claim overhead. Every claim must be entered in a structured table with status and source. For high-volume analysis tasks, this becomes a bottleneck.
- The "no placeholder or temporary content remains" check is unenforced (no automated detection) — relying on agent compliance.

**Maintenance burden:**
- Version `1.1.0` with `last_updated: 2025-10-14` suggests the document evolves. Updates to gate definitions require propagating changes to all agents that reference it.
- The reference to `anti_sycophancy.md` as "Anti-Sycophancy v5.2" links this document's validity to the versioning of another document.

---

## 3. Execution Model

Quality gates operate as a **checklist-based post-execution gate**: after work is produced, gates are applied as a structured review.

The enforcement mechanism is **agent-behavioral** (the QA agent reads and applies the gates) rather than **programmatic** (no automated gate executor). Gates are effective only insofar as the QA agent prompt references and applies them correctly.

The `/rf:opinion` command activates a separate three-layer analysis path (Constitutional AI, Chain-of-Verification, multi-perspective). `quality_gates.md:119-132`

**Quality enforcement**: Applied during QA phase by the QA agent. Gate failures produce specific severity ratings that route to different correction urgencies.

**Extension points**:
- "Projects should extend these quality gates" — explicit extension mechanism via project-specific rules. `quality_gates.md:178-185`
- Custom validation scripts can be added per project.

---

## 4. Pattern Categorization

**Directly Adoptable:**
- The six universal quality gate principles are directly adoptable as SuperClaude's NFR (Non-Functional Requirement) baseline for all task outputs.
- The three-tier severity system (Sev 1/2/3) maps cleanly to SuperClaude's STRICT/STANDARD/LIGHT compliance tiers.
- Anti-sycophancy as a universal gate principle (not optional) is directly adoptable.

**Conditionally Adoptable:**
- The output-type-specific gate tables are conditionally adoptable. The principle (different checks for code vs. analysis vs. opinion) is sound; the specific table format may need adaptation to SuperClaude's output types.
- The evidence table format is conditionally adoptable — valuable for STRICT tier, excessive for LIGHT tier.

**Reject:**
- Manual application of gates without automation enforcement for high-volume scenarios. SuperClaude should aim for programmatic gate enforcement where possible.
- The opinion analysis gate category as a separate special case — it can be absorbed into a unified evidence gate.
