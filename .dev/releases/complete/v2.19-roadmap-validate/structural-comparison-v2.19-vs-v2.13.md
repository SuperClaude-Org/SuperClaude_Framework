# Structural Comparison: v2.19 vs v2.13 Roadmaps

## Scope

This comparison is intentionally focused on **structure rather than content**. The goal is to identify differences in:

- document shape,
- formatting patterns,
- metadata richness,
- level of normalization,
- validation and dependency modeling,
- provenance visibility,
- and other artifacts that likely reflect **pipeline differences** more than topic differences.

Compared files:

- `/.dev/releases/complete/v2.19-roadmap-validate/roadmap.md`
- `/.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md`

---

## Executive Summary

The two roadmap artifacts reflect two materially different structural philosophies.

**v2.19** looks like a roadmap produced by a **more deliberative, adversarial, synthesis-oriented pipeline**. Its structure emphasizes:

- architectural framing,
- merge provenance,
- phased execution,
- open-question resolution,
- distributed validation,
- and runtime/pipeline semantics.

**v2.13** looks like a roadmap produced by a **more deterministic, milestone-driven, execution-planning pipeline**. Its structure emphasizes:

- rich machine-readable frontmatter,
- normalized milestone indexing,
- deliverable accounting,
- dependency clarity,
- and tabular execution tracking.

In short:

- **v2.19 = architected narrative + validation-oriented synthesis**
- **v2.13 = structured execution plan + indexed milestone ledger**

---

## Side-by-Side Structural Rubric

Scoring scale:

- **1** = minimal presence
- **3** = moderate presence
- **5** = strong / explicit structural emphasis

| Dimension | v2.19 | v2.13 | Structural observation | Likely pipeline signal |
|---|---:|---:|---|---|
| Frontmatter richness | 2 | 5 | v2.19 frontmatter is sparse and purpose-specific; v2.13 frontmatter is dense and schema-like | v2.13 pipeline likely encodes planning metadata more aggressively |
| Machine-readability of metadata | 2 | 5 | v2.13 includes milestone index, counts, personas, validation score/status; v2.19 does not | v2.13 pipeline appears more automation/indexing oriented |
| Body carries semantic load | 5 | 3 | v2.19 stores most planning semantics in markdown sections; v2.13 distributes more into YAML + tables | v2.19 pipeline favors document-centric synthesis |
| Template rigidity / normalization | 3 | 5 | v2.13 repeats a stable milestone template; v2.19 is more adaptive in sectioning | v2.13 pipeline likely more templated/deterministic |
| Narrative architectural framing | 5 | 3 | v2.19 has a strong executive summary and key architectural decisions section; v2.13 is lighter here | v2.19 pipeline likely more architecture-aware |
| Phase-oriented planning | 5 | 1 | v2.19 is explicitly phase-based | v2.19 pipeline likely plans in staged execution waves |
| Milestone-oriented planning | 2 | 5 | v2.13 is explicitly milestone-based with summary table and detailed sections | v2.13 pipeline likely plans as delivery packages |
| Deliverable indexing discipline | 4 | 5 | both are strong, but v2.13 is more normalized and ledger-like | both pipelines value deliverables; v2.13 more rigidly |
| Dependency modeling clarity | 4 | 5 | both have dependency graphs; v2.13 is cleaner and more classical, v2.19 includes alignment semantics | v2.13 optimized for execution clarity; v2.19 for orchestration nuance |
| Parallelism modeling | 5 | 2 | v2.19 explicitly models concurrent work and alignment checkpointing; v2.13 is mostly linear/critical-path oriented | v2.19 pipeline likely designed for multi-stream orchestration |
| Validation embedded throughout plan | 5 | 3 | v2.19 includes per-phase validation and success-mapping; v2.13 centralizes validation more in acceptance structures | v2.19 pipeline more governance/verification centric |
| Acceptance criteria normalization | 4 | 5 | v2.13’s milestone tables consistently include acceptance criteria in a stable pattern | v2.13 pipeline likely optimized for tracking and signoff |
| Provenance visibility | 5 | 2 | v2.19 explicitly records merge provenance, variant selection, debate convergence; v2.13 references upstream decision context more lightly | v2.19 pipeline exposes internal synthesis history |
| Ambiguity / open-question handling | 5 | 2 | v2.19 has a dedicated open-questions-resolved section; v2.13 has a decision summary but less ambiguity trace | v2.19 pipeline likely preserves uncertainty resolution explicitly |
| Operational / runtime semantics | 5 | 3 | v2.19 spends more structure on pipeline behavior, failure modes, resume semantics, degraded outputs | v2.19 pipeline treats workflow behavior as first-class planning material |
| Quantitative inventorying | 3 | 5 | v2.13 is more metrically dense in frontmatter and summary sections | v2.13 pipeline likely more scoring/indexing oriented |
| Readability for humans | 4 | 4 | both are readable, but in different ways: v2.19 via narrative, v2.13 via normalization | different optimization targets rather than quality gap |
| Traceability for downstream tooling | 3 | 5 | v2.13 is better pre-structured for tooling; v2.19 would require more parsing of prose sections | v2.13 likely built with stronger machine-consumption intent |
| Architectural decision traceability | 5 | 4 | both are good, but v2.19 foregrounds decisions more explicitly in the roadmap itself | v2.19 pipeline favors reasoning visibility |
| Pipeline fingerprint strength | 5 | 4 | both show pipeline fingerprints; v2.19 does so more explicitly through provenance and synthesis sections | v2.19 reveals its generation method more clearly |

---

## Detailed Structural Analysis

## 1. Frontmatter sophistication and intent

### v2.19 frontmatter is minimal and purpose-specific
At `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:1-5`, the frontmatter has only:

- `spec_source`
- `complexity_score`
- `adversarial`

This suggests a pipeline that treats the body as the primary carrier of structure, with only a few top-level pipeline facts encoded in metadata.

### v2.13 frontmatter is much richer and machine-oriented
At `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:1-47`, the frontmatter includes:

- generation metadata,
- generator identity,
- complexity class,
- domain distribution,
- personas,
- milestone counts/index,
- totals,
- validation score/status.

This reflects a different structural philosophy: the pipeline encodes a **summary model of the roadmap itself** in YAML before the body begins.

### Structural implication
- **v2.13 pipeline** appears more **schema-heavy** and optimized for:
  - downstream automation,
  - indexing,
  - validation,
  - aggregation.
- **v2.19 pipeline** appears more **document-centric**, with the semantic richness living in markdown sections rather than machine-readable metadata.

---

## 2. Document shape: phases vs milestones

### v2.19 uses a phased implementation plan
Starting at `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:23`, the document is organized as:

- Phase 1
- Phase 2
- Phase 3
- Phase 4
- Phase 5

Each phase has:

- milestone statement,
- deliverables,
- validation,
- estimated effort,
- dependencies where relevant.

This is a **program-plan / staged execution** structure.

### v2.13 uses milestone-based decomposition
Starting at `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:59`, it introduces a milestone summary table, then detailed milestone sections:

- M1
- M2
- M3
- M4

Each milestone includes:

- objective,
- deliverables,
- dependencies,
- risk assessment.

This is a **work-package / delivery-tracking** structure.

### Structural implication
This is one of the clearest pipeline differences:

- **v2.19 pipeline thinks in sequential implementation phases**
- **v2.13 pipeline thinks in milestone containers with indexed deliverables**

That is not just stylistic; it changes how the roadmap is likely generated:

- phase-first pipelines often derive from architecture/planning prompts,
- milestone-first pipelines often derive from templated planning schemas or CLI-oriented planning runners.

---

## 3. Narrative density vs tabular normalization

### v2.19 has more narrative explanation
Examples:

- Executive Summary with architectural framing: `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:9-21`
- Key Architectural Decisions: `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:15-20`
- Merge Provenance: `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:21`
- Open Questions — Resolved Recommendations: `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:230-245`

This roadmap reads like a **synthesized planning artifact** intended to explain why the shape is what it is.

### v2.13 has more normalized tabular structure
Examples:

- milestone summary table: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:61-66`
- deliverables tables under each milestone: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:90-95`, `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:118-126`, `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:150-154`, `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:177-184`
- risk register: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:200-206`
- decision summary: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:210-216`
- success criteria: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:220-226`

This roadmap reads like a **structured execution specification** intended to be easy to inspect and track.

### Structural implication
- **v2.19** optimizes for **planning rationale and synthesis clarity**
- **v2.13** optimizes for **consistency, scanning, and measurability**

---

## 4. Adversarial/debate provenance visibility

### v2.19 makes pipeline provenance explicit in the body
At `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:21`, it includes:

- base variant,
- alternative variant,
- scores,
- adversarial debate rounds,
- convergence.

That strongly suggests the artifact was produced by a system that:

1. generated multiple variants,
2. compared them,
3. merged them,
4. preserved provenance explicitly.

### v2.13 references adversarial context, but less structurally central
At `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:53`, it says the roadmap implements an option from an adversarial-debated architecture decision, but the roadmap itself is not structurally organized around merge provenance.

### Structural implication
- **v2.19 pipeline** exposes internal synthesis mechanics directly in the roadmap.
- **v2.13 pipeline** may use debate upstream, but the final artifact is shaped more like a finalized plan than a merged decision record.

This is a strong indicator of pipeline evolution.

---

## 5. Resolution of uncertainty

### v2.19 includes a dedicated “Open Questions — Resolved Recommendations” section
See `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:230-245`.

That is structurally important: the roadmap itself contains unresolved-or-just-resolved design decisions and records the chosen direction.

### v2.13 includes “Decision Summary,” but not open-question resolution
See `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:208-216`.

The difference:

- **Decision Summary** = finalized outcomes
- **Open Questions — Resolved Recommendations** = explicit trace of ambiguity resolution

### Structural implication
The v2.19 pipeline appears more aware of planning ambiguity and intentionally records resolution steps. That suggests a pipeline designed to reduce late instability and surface design forks explicitly.

---

## 6. Validation structure

### v2.19 embeds validation into every phase and into success criteria
Examples:

- per-phase “Validation” subsections: `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:36`, `56`, `78`, `100`
- success criteria table tied to validation method and phase: `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:191-203`

This creates a strong **plan → verification** coupling throughout the document.

### v2.13 centralizes validation more toward milestone acceptance and final acceptance
Examples:

- acceptance criteria embedded in deliverable tables throughout,
- dedicated “Validation and Acceptance” milestone: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:169-195`
- success criteria in a separate section: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:218-226`

This is still rigorous, but structurally different:

- v2.19 distributes validation across the plan,
- v2.13 consolidates validation into milestone acceptance patterns and a final validation milestone.

### Structural implication
- **v2.19** feels like a **pipeline correctness / governance roadmap**
- **v2.13** feels like an **implementation program with acceptance gates**

---

## 7. Dependency modeling style

### v2.19 shows phase dependency graph with explicit parallelism checkpoint
See:

- parallel execution note: `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:44`
- dependency graph: `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:217-223`

This includes an **alignment checkpoint** between parallel streams, which is structurally more sophisticated.

### v2.13 shows milestone dependency graph and critical path
See:

- dependency graph: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:68-78`

This is cleaner and more classic project-planning structure:

- milestone dependencies,
- critical path,
- less emphasis on synchronization semantics.

### Structural implication
- **v2.19 pipeline** appears more tuned for **multi-stream orchestration**
- **v2.13 pipeline** appears more tuned for **execution ordering clarity**

---

## 8. Attention to operational/pipeline semantics

### v2.19 is more operationally self-aware
Examples:

- isolated subprocess rationale: `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:15-19`
- degraded validation report semantics: `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:19`, `74-75`, `236-239`
- `--resume` behavior and validation state persistence: `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:94-96`, `149-150`, `244-245`

Structurally, the roadmap spends significant space on runtime and workflow behavior.

### v2.13 is more implementation-task-focused
Its structure is centered on:

- tests,
- code changes,
- acceptance criteria,
- quantified cleanup,
- milestone outputs.

Less document space is devoted to operational semantics of the planning pipeline itself.

### Structural implication
This strongly suggests:

- **v2.19 pipeline** was built for a workflow where pipeline behavior itself is a first-class concern.
- **v2.13 pipeline** was built for producing a clear implementation plan for code changes.

---

## 9. Quantification style

### v2.13 is more heavily quantified in metadata and body
Examples:

- complexity class + validation score: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:5`, `45-46`
- domain percentages: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:7-11`
- milestone counts and deliverable counts: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:12-44`
- explicit totals and measurable success criteria: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/roadmap.md:42-46`, `220-226`

### v2.19 quantifies where needed, but less comprehensively
It includes:

- complexity score: `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md:3`
- phase estimates: `38`, `58`, `80`, `102`, `140`
- total timeline: `205-215`
- success criteria table: `193-203`

But it is less metrically dense overall.

### Structural implication
- **v2.13** looks more like a product of a pipeline with **strong schema/template normalization**
- **v2.19** looks more like a product of a pipeline with **strong synthesis and judgment layers**

---

## 10. Consistency and polish patterns

### v2.13 feels more templated and uniform
The repeated pattern is very stable:

- Objective
- Deliverables
- Dependencies
- Risk Assessment

This repeats per milestone with high consistency. That usually indicates a **strong template-driven generator**.

### v2.19 feels more custom-shaped around the problem
It has:

- Executive Summary
- Phased Implementation Plan
- Risk Assessment
- Resource Requirements
- Success Criteria & Validation Approach
- Timeline Estimates
- Open Questions — Resolved Recommendations

This is coherent, but less rigidly repetitive. It feels more like a **merged/curated planning artifact** than a strict template expansion.

### Structural implication
- **v2.13** likely came from a pipeline with stronger deterministic formatting.
- **v2.19** likely came from a pipeline allowing more adaptive document shaping based on planning context.

---

## Most Likely Pipeline-Driven Differences

The strongest signals that these differences are due to the pipelines rather than the topics themselves are:

1. **Frontmatter richness**
   - v2.13 has much more machine-readable planning metadata.
   - v2.19 keeps metadata sparse.

2. **Phase-first vs milestone-first organization**
   - v2.19 = phases
   - v2.13 = milestones with indexed deliverables

3. **Adversarial merge provenance surfaced in final artifact**
   - v2.19 explicitly preserves merge/debate provenance.
   - v2.13 does not foreground it structurally.

4. **Open-question resolution section**
   - v2.19 explicitly records ambiguity resolution.
   - v2.13 records decisions more statically.

5. **Operational semantics emphasis**
   - v2.19 devotes more structure to runtime/workflow behavior.
   - v2.13 devotes more structure to implementation execution.

6. **Template rigidity**
   - v2.13 is more normalized and repetitive.
   - v2.19 is more synthesized and tailored.

---

## Bottom-Line Comparison

### v2.19 structural profile
- Sparse metadata
- Rich executive summary
- Phase-oriented plan
- Explicit merge provenance
- Explicit open-question resolution
- Strong operational semantics
- Distributed validation structure
- More synthesized, less templated

### v2.13 structural profile
- Dense metadata
- Milestone-oriented execution plan
- Strong indexing and tabulation
- Stable repeated section template
- More measurable inventory of work items
- Cleaner dependency and acceptance structure
- More schema-driven, more deterministic

---

## Inference About Pipeline Evolution

If these were produced by different pipelines, the strongest structural inference is:

- **v2.13’s pipeline** prioritized **deterministic structure, metadata completeness, and execution traceability**.
- **v2.19’s pipeline** prioritized **multi-artifact synthesis, reasoning visibility, architectural framing, and decision-resolution transparency**.

That means v2.19 is not simply “better formatted.” It is optimized for a different goal: **explaining and governing a plan**, not just **tracking and executing it**.
