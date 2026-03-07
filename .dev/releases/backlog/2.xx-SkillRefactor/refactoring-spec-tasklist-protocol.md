# Refactoring Spec: sc:tasklist-protocol

**Date**: 2026-03-06
**Scope**: Dual-lens architectural analysis -- cli-portify pattern adoption + CLI runner pipeline optimization
**Target**: `src/superclaude/skills/sc-tasklist-protocol/SKILL.md` (v3.0)
**Reference**: `src/superclaude/skills/sc-cli-portify/SKILL.md` + `src/superclaude/cli/pipeline/`

---

## Current Architecture Assessment

### Current Step Count and Flow

The skill executes as a single Claude inference session across 6 sequential stages:

| Stage | Name | Mode | Primary Work |
|-------|------|------|-------------|
| 1 | Input Ingest | Read file, parse text | Read roadmap, identify sections |
| 2 | Parse + Phase Bucketing | Regex splitting, heading detection | Split into R-### items, assign to phase buckets |
| 3 | Task Conversion | Rule application + content generation | Convert items to T-format tasks with steps, criteria |
| 4 | Enrichment | Deterministic scoring + inference | Effort/Risk/Tier/Confidence computation, MCP tools, deliverable IDs |
| 5 | File Emission | Template filling + Write calls | mkdir + Write tasklist-index.md + phase-N-tasklist.md files |
| 6 | Self-Check | 17-point validation | Sprint compatibility, semantic, structural quality gates |

**Total stages**: 6, strictly sequential, all executed within one Claude session.

### Current Validation Mechanisms

**17-point self-check** (all executed as LLM self-referential validation):

- **Sprint Compatibility (checks 1-8)**: Index file exists, phase files referenced, contiguous phase numbers, valid T-format IDs, correct phase headings, end-of-phase checkpoints, no cross-phase metadata leakage, literal filenames in index.
- **Semantic Quality Gate (checks 9-12)**: Non-empty enrichment fields, globally unique D-#### IDs, no placeholder descriptions, roadmap item traceability.
- **Structural Quality Gate (checks 13-17)**: Task count bounds per phase, clarification task adjacency, circular dependency detection, XL splitting enforcement, confidence bar format consistency.

**Gate behavior**: Structural gates are designated "blocking" and semantic gates "advisory," but both are enforced only through inference -- there is no programmatic enforcement mechanism.

### Current Integration Points

- **Tool usage**: Read (stage 1), Grep (stage 2), Write (stage 5), Bash/mkdir (stage 5), Glob (stage 6), TodoWrite (stages 1-6)
- **MCP**: Sequential (optional, tier classification ambiguity), Context7 (optional, framework pattern validation)
- **Downstream consumer**: `superclaude sprint run` -- reads the generated phase-N-tasklist.md files via regex phase discovery

### Architectural Strengths to Preserve

1. **Deterministic algorithm specification**: The SKILL.md is exceptionally precise about its generation rules. Effort scoring, risk scoring, tier classification, and phase numbering are fully specified as deterministic algorithms with no discretionary choices. This precision is the skill's core value.
2. **Atomic write constraint**: The bundle is validated in-memory before any Write call. This is a sound design principle.
3. **Traceability chain**: R-### to T-format to D-#### with cross-referencing in registries and matrix is well-designed for auditability.
4. **Sprint CLI compatibility**: Output format is tightly coupled to sprint CLI regex expectations. Any refactoring must preserve this contract exactly.
5. **Clarification task pattern**: The mechanism for handling missing information (inserting clarification tasks rather than guessing) is a disciplined approach worth preserving.

---

## Pattern Adoption Matrix

| Pattern | Applicable | Adoption Design | Effort | Risk if Skipped |
|---------|-----------|-----------------|--------|-----------------|
| **(a) Programmatic enforcement over self-referential LLM validation** | **High**. 14 of 17 self-checks are structurally verifiable (regex, counting, format matching). The LLM checking its own work is unreliable -- it may "pass" checks it actually violated. | Implement 14 Python functions in a `gates.py` module. Each reads the written markdown files and returns `tuple[bool, str]`. Run after stage 5 (File Emission). Checks 9 (non-empty fields), 10 (unique D-IDs), 13 (task count bounds), and 15 (circular deps) require cross-file analysis. Checks 11 (no placeholders), 12 (orphan tasks), 14 (clarification adjacency) are single-file regex. Checks 1-8 are file-existence and format checks. Only checks related to "content quality" (parts of check 11: is the description actually meaningful?) and "task specificity" (the generation-time sub-checks: named artifact, imperative verb) genuinely require inference. | **Medium** (2-3 days). Each check is a straightforward Python function operating on markdown text. Most are 10-30 lines. | **High**. Without programmatic enforcement, the self-check is theater -- the LLM will report "all 17 checks passed" even when violations exist. This is the single highest-value pattern to adopt. Observed failure modes include: duplicate D-IDs across phases, non-contiguous phase numbers after gap correction, missing end-of-phase checkpoints, and malformed T-format IDs. |
| **(b) Pure-function gate criteria: `(str) -> tuple[bool, str]`** | **High**. Direct mapping from the 17 checks to typed functions. | Define in `src/superclaude/cli/tasklist/gates.py`. Examples: `_phase_numbers_contiguous(content: str) -> tuple[bool, str]`, `_task_ids_valid_format(content: str) -> tuple[bool, str]`, `_deliverable_ids_unique(index_content: str, phase_contents: list[str]) -> tuple[bool, str]`, `_end_of_phase_checkpoint_present(content: str) -> tuple[bool, str]`, `_no_cross_phase_metadata(content: str) -> tuple[bool, str]`, `_task_count_bounds(content: str, min_tasks: int, max_tasks: int) -> tuple[bool, str]`, `_confidence_bar_format(content: str) -> tuple[bool, str]`. Wire into `SemanticCheck` dataclass from pipeline models. | **Low** (1-2 days). Functions are trivial regex/parsing operations. | **Medium**. Without typed gate functions, any future pipeline integration lacks the validation hooks it needs. The function signatures also serve as executable documentation of the self-check contract. |
| **(c) Classification rubric: programmatic vs inference** | **High**. The skill mixes heavily deterministic work (scoring, ID assignment, template filling) with genuinely inference-dependent work (understanding roadmap prose, generating task descriptions, creating acceptance criteria). | See Pipeline Optimization Plan below for per-stage classification. Summary: Stages 1, 2, 4 (scoring only), 5, 6 are largely or fully programmatic. Stage 3 (task content generation) and stage 4 (acceptance criteria, step generation) require inference. | **Low** (analysis only, no code). Classification informs which stages benefit from portification. | **Low** immediate risk, but skipping this analysis means future portification efforts will misclassify stages, either over-automating (losing inference quality) or under-automating (keeping unreliable self-checks). |
| **(d) Step graph with dependency resolution** | **Medium**. The 6 stages are strictly sequential with no parallelism opportunities in the current design. However, modeling them as a step graph enables the executor to manage retry, resume, and gate evaluation. Stage 4 (Enrichment) is internally decomposable: tier classification is a pure function that could run as a programmatic step separate from the inference-based enrichment. | Model as 7-8 steps in a `Step` graph: `ingest -> parse -> bucket -> convert_tasks (Claude) -> enrich_scores (programmatic) -> enrich_content (Claude) -> emit_files (programmatic) -> validate (programmatic)`. Dependencies are linear. No parallel groups needed for the current design, though batch parallelism over phase files during emission could be added later. | **Medium** (1-2 days for step definitions). | **Low**. The current sequential flow works. Step graph becomes valuable only when combined with resume/retry (pattern e) or subprocess isolation (pattern h). |
| **(e) Resume/retry with exact CLI resume commands** | **Medium**. If file emission (stage 5) fails partway through writing N+1 files, the current skill has no mechanism to resume. It must regenerate everything from scratch. For large roadmaps (10+ phases, 50+ tasks), this wastes significant inference budget. | Implement checkpoint serialization: after each stage, serialize intermediate state (parsed items, phase buckets, task stubs, enriched tasks) to a JSON file in a `.tasklist-work/` directory. On resume, detect the last successful checkpoint and resume from there. Resume command: `superclaude tasklist --resume .tasklist-work/checkpoint.json`. | **Medium-High** (2-3 days). Requires defining serializable intermediate representations for each stage boundary. | **Low-Medium**. The skill typically runs in 1-3 minutes for moderate roadmaps. Resume matters most for very large roadmaps or when Claude subprocess budget is constrained. |
| **(f) Budget economics via TurnLedger** | **Low** (current design). The skill runs as a single Claude session, so there is no multi-subprocess budget to track. | Becomes relevant only if the skill is portified with subprocess stages. In that case, integrate `TurnLedger` with debit/credit for each Claude-assisted step (task conversion, content enrichment). Pre-launch guards would prevent starting a new phase's task conversion if budget is exhausted. | **Low** (piggybacks on portification if done). | **Negligible** in current architecture. The single-session model has implicit budget management via Claude's own turn limits. |
| **(g) Diagnostic chain** | **Medium**. Currently if the self-check fails, the LLM tries to fix it inline -- an unreliable approach. A proper diagnostic chain would: (1) classify failures as structural (fixable programmatically), semantic (needs LLM re-generation of specific section), or content (roadmap ambiguity requiring clarification), then (2) route to appropriate remediation. | Implement `DiagnosticCollector` that captures all gate failures. `FailureClassifier` maps each failure to a remediation strategy: structural failures get programmatic fixes (renumber phases, regenerate IDs), semantic failures trigger targeted re-prompting of the specific task/section, content failures produce clarification task insertions. `ReportGenerator` produces a diagnostic summary if remediation fails. | **Medium** (2-3 days). Requires defining failure taxonomy and remediation strategies. | **Medium**. Without diagnostics, failures during self-check result in the LLM either silently ignoring the failure or attempting ad-hoc fixes that may introduce new violations. |
| **(h) 4-layer subprocess isolation** | **Low**. Only relevant if stages are decomposed into child Claude sessions. The current single-session design does not need isolation. | If portified: stages 3 (task conversion) and 4 (content enrichment) would run as isolated `ClaudeProcess` instances with scoped work directories, git ceiling, isolated plugin/settings dirs. Each subprocess receives only the context it needs (parsed items for stage 3, task stubs for stage 4). | **Medium** (1-2 days, but only if portifying). | **Negligible** in current architecture. Relevant only for full portification. |
| **(i) Context injection for inter-step data flow** | **High**. The stages have implicit data flow: parsed items (stage 1-2) feed task conversion (stage 3), which feeds enrichment (stage 4), which feeds emission (stage 5). Currently this data exists only in the LLM's context window. If the context window fills or the LLM loses track, data is silently lost. | Define typed intermediate data structures: `ParsedRoadmapItem(id: str, text: str, phase_bucket: int)`, `TaskStub(id: str, title: str, roadmap_items: list[str], phase: int)`, `EnrichedTask(...)` with all scoring fields. Serialize to JSON at stage boundaries. Inject into subsequent prompts or programmatic steps. | **Medium** (2 days). Requires defining dataclasses for each stage boundary. | **Medium**. Without explicit data flow, the LLM may silently drop roadmap items during conversion, lose deliverable IDs during enrichment, or produce inconsistent cross-references. Typed intermediates make data loss detectable. |

---

## Pipeline Optimization Plan

| Skill Phase | Current Mode | Recommended Mode | Gate Design | Rationale |
|-------------|-------------|------------------|-------------|-----------|
| **Stage 1: Input Ingest** | Inference (Read + parse) | **Pure programmatic** | `LIGHT`: file exists, non-empty, contains at least one heading or bullet | Reading a file and detecting sections/headings/bullets is `pathlib.Path.read_text()` + regex. No inference needed. Python reads the roadmap, splits by headings/bullets, produces `list[ParsedRoadmapItem]`. |
| **Stage 2: Parse + Phase Bucketing** | Inference (Grep + categorize) | **Pure programmatic** | `STANDARD`: every item assigned to exactly one phase, phase count >= 1, no unassigned items | Phase detection (scan for "Phase N", "vN.N", "Milestone") is regex. Bucket assignment follows the deterministic rules in Section 4.2 exactly. Phase renumbering (Section 4.3) is arithmetic. All of this is implementable as a Python function with zero ambiguity. |
| **Stage 3: Task Conversion** | Inference (content generation) | **Hybrid**: programmatic ID assignment + Claude-assisted content | `STRICT`: valid T-format IDs (programmatic), non-empty titles, 3-8 steps per task, exactly 4 acceptance criteria, exactly 2 validation bullets | Splitting rules (Section 4.4) are deterministic -- Python can detect when an item should split. Task ID assignment (Section 4.5) is arithmetic. But generating meaningful task descriptions, steps, acceptance criteria, and validation bullets requires inference -- the LLM reads the roadmap prose and produces implementation-oriented content. Gate checks the structural envelope; content quality is advisory. |
| **Stage 4: Enrichment** | Inference (scoring + content) | **Split into two sub-stages**: (4a) **Pure programmatic** scoring + (4b) **Claude-assisted** content enrichment | (4a) `STANDARD`: all tasks have Effort/Risk/Tier/Confidence computed, scores match algorithm. (4b) `STANDARD`: deliverable descriptions non-empty, artifact paths follow pattern. | Effort scoring (Section 5.2.1), Risk scoring (Section 5.2.2), Tier classification (Section 5.3), and Confidence scoring (Section 5.4) are 100% deterministic algorithms with explicit formulas. These are the strongest candidates for programmatic extraction in the entire skill. The keyword matching, score computation, compound phrase detection, and context booster application are all string operations + arithmetic. Deliverable ID assignment (D-####) is also deterministic. Content enrichment (MCP tool requirements, sub-agent delegation decisions) follows lookup tables. Only deliverable descriptions and intended artifact path inference benefit from LLM assistance. |
| **Stage 5: File Emission** | Inference (template filling + Write) | **Pure programmatic** | `STRICT`: all N+1 files written, file sizes > 0, phase file count matches index, literal filenames in index table | Template filling with structured data is string formatting, not inference. Given the enriched task data as a typed data structure, a Python function can render `tasklist-index.md` and each `phase-N-tasklist.md` using f-strings or Jinja2 templates. The templates are fully specified in SKILL.md Sections 6A and 6B. This eliminates a major source of format drift (LLM forgetting em-dash separators, wrong heading levels, missing sections). |
| **Stage 6: Self-Check** | Inference (17-point validation) | **Pure programmatic** | `STRICT`: all 14 structural checks pass as `tuple[bool, str]` gate functions. 3 semantic checks (content quality, task specificity, acceptance criteria meaningfulness) remain advisory. | This is the pattern (a) adoption. 14 of 17 checks are trivially implementable as Python functions inspecting markdown files. The 3 remaining checks that genuinely require judgment (is the description "meaningful"? does the acceptance criterion name a "specific" artifact?) could optionally be implemented as a lightweight Claude subprocess with a focused prompt, but are more practically left as advisory warnings. |

### What Stays as Inference vs Becomes Programmatic

**Stays as inference (requires LLM)**:
- Understanding vague roadmap prose ("improve performance", "harden security")
- Generating task descriptions with implementation-oriented steps
- Creating acceptance criteria that are specific to the roadmap's domain
- Writing phase goals derived from roadmap context
- Producing "Why" fields that explain task motivation
- Near-field completion criterion generation (needs domain understanding)
- Deliverable descriptions (short human-readable summaries)

**Becomes programmatic (deterministic algorithms)**:
- Roadmap item parsing (regex splitting on headings/bullets/numbered lists)
- Phase bucket assignment (heading detection + default bucketing rules)
- Phase renumbering (sequential assignment, no gaps)
- Task splitting decision (keyword detection for split triggers)
- Task ID assignment (T<PP>.<TT> zero-padded arithmetic)
- Roadmap Item ID assignment (R-### sequential)
- Deliverable ID assignment (D-#### sequential)
- Effort scoring (EFFORT_SCORE algorithm: character count + split flag + keyword match + dependency words)
- Risk scoring (RISK_SCORE algorithm: keyword category matching)
- Tier classification (compound phrase overrides + keyword matching + context boosters + priority resolution)
- Confidence scoring (max tier score, ambiguity penalty, compound boost, vague input penalty)
- Verification method routing (tier-to-method lookup table)
- MCP tool requirements (tier-to-tools lookup table)
- Sub-agent delegation requirements (tier + risk lookup)
- Checkpoint insertion (every 5 tasks + end-of-phase, deterministic naming)
- File emission (template rendering with structured data)
- All 14 structural self-checks

### Output Format Changes for Pipeline Compatibility

If portified, the intermediate data flow would use JSON-serialized dataclasses rather than in-context LLM state:

1. **Stage 1-2 output**: `TasklistParseResult` JSON with `list[ParsedRoadmapItem]` and `list[PhaseBucket]`
2. **Stage 3 output**: `TaskConversionResult` JSON with `list[TaskStub]` (ID, title, phase, roadmap items, raw content from Claude)
3. **Stage 4a output**: `EnrichmentScores` JSON with effort/risk/tier/confidence per task
4. **Stage 4b output**: `EnrichedTaskBundle` JSON with full task data including Claude-generated content
5. **Stage 5 output**: The markdown files themselves (tasklist-index.md + phase-N-tasklist.md)
6. **Stage 6 output**: `ValidationReport` JSON with per-check pass/fail/reason

The final markdown output format remains unchanged -- Sprint CLI compatibility is preserved exactly.

### Gates Per Step (Portified Design)

| Step | Gate Tier | Gate Mode | Checks |
|------|-----------|-----------|--------|
| Ingest | LIGHT | BLOCKING | File read succeeded, non-empty content |
| Parse | STANDARD | BLOCKING | Item count > 0, all items have IDs, no duplicate R-### |
| Bucket | STANDARD | BLOCKING | Phase count >= 1, all items assigned, contiguous numbering |
| Task Convert (Claude) | STRICT | BLOCKING | Valid T-format IDs, non-empty titles, step count 3-8, AC count = 4, validation count = 2 |
| Enrich Scores (programmatic) | STANDARD | BLOCKING | All tasks have Effort/Risk/Tier/Confidence, scores within valid ranges |
| Enrich Content (Claude) | STANDARD | TRAILING | Deliverable descriptions non-empty, artifact paths match pattern |
| Emit Files | STRICT | BLOCKING | N+1 files exist, sizes > 0, index contains Phase Files table with literal filenames |
| Validate | STRICT | BLOCKING | 14 structural checks pass, 3 semantic checks advisory |

---

## Portification Candidacy

**Recommendation: Selective adoption**

### Justification

Full portification (decomposing all 6 stages into subprocess-managed steps with `ClaudeProcess`, `TurnLedger`, TUI, and NDJSON monitoring) is disproportionate to the skill's complexity. The tasklist-protocol is a single-pass generator that typically completes in 1-3 minutes. The overhead of subprocess management, isolation layers, and budget tracking would exceed the cost of the work being managed.

However, **selective adoption of patterns (a), (b), (c), and (i) delivers the majority of the reliability improvement** without the architectural overhead of full portification:

1. **Pattern (a) + (b): Programmatic post-write validation** -- This is the highest-value change. Implementing 14 gate functions that run after file emission and before the skill reports completion transforms self-check from unreliable inference to deterministic verification. This can be done as a Python module (`src/superclaude/cli/tasklist/gates.py`) that the skill invokes via `Bash` tool call after writing files, or that integrates into a lightweight pipeline wrapper.

2. **Pattern (c): Extraction of deterministic algorithms** -- Moving effort/risk/tier/confidence scoring into Python functions eliminates a major source of inconsistency. The LLM sometimes miscounts keywords, forgets to apply compound phrase overrides, or miscalculates confidence penalties. A Python implementation of these algorithms guarantees correct scores every time. This module (`src/superclaude/cli/tasklist/scoring.py`) can be invoked by the skill via `Bash` to compute scores for each task, or can be used to validate LLM-computed scores post-hoc.

3. **Pattern (i): Typed intermediate representations** -- Defining `ParsedRoadmapItem`, `PhaseBucket`, `TaskStub`, and `EnrichedTask` as Python dataclasses with JSON serialization creates a contract between stages. Even if the skill continues to run as a single Claude session, these types serve as validation schemas for the intermediate data.

4. **Pattern (g): Lightweight diagnostic chain** -- A `FailureClassifier` that categorizes gate failures and suggests targeted fixes (rather than asking the LLM to "fix all issues") improves remediation reliability.

**What NOT to adopt now**:
- Full subprocess isolation (pattern h) -- single-session execution is sufficient
- TurnLedger budget tracking (pattern f) -- single session does not need it
- Step graph with executor (pattern d) -- adds complexity without proportional benefit for a 6-stage linear pipeline
- Resume/retry (pattern e) -- low ROI for a 1-3 minute operation; revisit if roadmap size grows significantly

### Selective Adoption Architecture

```
src/superclaude/cli/tasklist/
  __init__.py
  scoring.py       # Effort, Risk, Tier, Confidence algorithms (pure functions)
  gates.py         # 14 structural gate functions + 3 advisory semantic checks
  models.py        # ParsedRoadmapItem, PhaseBucket, TaskStub, EnrichedTask
  diagnostics.py   # FailureClassifier + remediation routing
  parser.py        # Roadmap parsing + phase bucketing (pure programmatic)
  emitter.py       # Template rendering for index + phase files (pure programmatic)
```

The skill SKILL.md would be updated to call these modules via `Bash`:
- After stage 2: `uv run python -m superclaude.cli.tasklist.parser <roadmap-path> --output .tasklist-work/parse-result.json`
- After stage 4: `uv run python -m superclaude.cli.tasklist.scoring .tasklist-work/task-stubs.json --output .tasklist-work/scores.json`
- After stage 5: `uv run python -m superclaude.cli.tasklist.gates <tasklist-root> --format json`
- On gate failure: `uv run python -m superclaude.cli.tasklist.diagnostics <gate-results.json>`

---

## Testing Plan

### Phase 1: Unit Tests for Programmatic Functions

**Target**: `tests/tasklist/`

| Test Module | Coverage Target | Key Properties |
|-------------|----------------|----------------|
| `test_scoring.py` | Effort scoring algorithm | Score computation matches Section 5.2.1 exactly for all keyword combinations; score-to-label mapping is correct; Clarification Tasks always score 0 |
| `test_scoring.py` | Risk scoring algorithm | Score computation matches Section 5.2.2 exactly; risk driver extraction is correct; cross-cutting keywords detected |
| `test_scoring.py` | Tier classification | Compound phrase overrides take precedence; keyword matching accumulates correctly; context boosters apply; priority resolution (STRICT > EXEMPT > LIGHT > STANDARD) resolves ties correctly |
| `test_scoring.py` | Confidence scoring | Base score capped at 0.95; ambiguity penalty of 15% applied when top two within 0.1; compound boost of 15%; vague input penalty of 30% |
| `test_gates.py` | All 14 structural gates | Each gate function returns `(True, None)` for valid input and `(False, reason)` for invalid input with a descriptive reason string |
| `test_parser.py` | Roadmap parsing | Headings, bullets, numbered lists detected as item boundaries; R-### IDs assigned sequentially; multi-sentence splitting only when independently actionable |
| `test_parser.py` | Phase bucketing | Explicit phase labels detected; default 3-bucket fallback; phase renumbering eliminates gaps |
| `test_emitter.py` | Template rendering | Index file contains all required sections; phase files contain only phase-scoped content; literal filenames in Phase Files table; em-dash separators; heading levels correct |

### Phase 2: Integration Tests for Pipeline Compatibility

| Test | Description |
|------|-------------|
| `test_sprint_compat.py` | Generated output is discoverable by sprint CLI phase regex |
| `test_round_trip.py` | Parse roadmap -> generate tasklist -> validate gates -> all pass |
| `test_scoring_consistency.py` | Python scoring matches LLM scoring on 10 reference roadmaps |

### Phase 3: Regression Tests

| Test | Description |
|------|-------------|
| `test_golden_files.py` | Compare generated output against golden reference files for 3-5 canonical roadmaps |
| `test_format_stability.py` | Output format matches sprint CLI expectations across version changes |

### Phase 4: Property-Based Tests for Determinism

| Property | Test Strategy |
|----------|---------------|
| Determinism | Same roadmap input produces identical output (byte-for-byte) on repeated runs |
| Contiguity | Phase numbers are always 1..N with no gaps, for any N |
| ID uniqueness | No duplicate R-###, T<PP>.<TT>, or D-#### across any generated bundle |
| Traceability coverage | Every R-### appears in the traceability matrix; every task references at least one R-### |
| Effort monotonicity | Adding a keyword from the effort keyword list never decreases the effort score |
| Tier priority | STRICT always wins over any lower-priority tier when keywords conflict |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Programmatic scoring diverges from SKILL.md spec** | Medium | High -- incorrect tier classification changes verification routing, which affects sprint execution safety | Pin scoring algorithms to SKILL.md version; add version assertion in scoring.py header; test against reference vectors derived from SKILL.md examples |
| **Template rendering produces format that breaks sprint CLI** | Medium | High -- sprint CLI cannot discover phases, entire tasklist unusable | Integration test against actual sprint CLI phase discovery regex; golden file tests lock output format |
| **LLM stops calling Bash validation after file emission** | Medium | Medium -- reverts to unreliable self-check | Make the Bash validation call mandatory in the skill protocol (add to "File Emission Rules" as a hard requirement); consider enforcing via a thin pipeline wrapper that runs gates automatically |
| **Intermediate data model changes break stage boundaries** | Low | Medium -- if ParsedRoadmapItem schema changes, downstream stages fail | Version the JSON schema; add schema validation at deserialization boundaries |
| **Over-extraction of inference work into programmatic code** | Low | High -- if task description generation is made programmatic, output quality degrades severely | Maintain strict classification rubric; never extract stages that require understanding natural language or making domain judgments |
| **Selective adoption becomes a maintenance burden** | Medium | Medium -- two systems to maintain (SKILL.md protocol + Python modules) with potential drift | Single source of truth: Python modules are authoritative for scoring/gates/parsing; SKILL.md references them rather than duplicating algorithms |
| **Roadmap formats not covered by parser** | Medium | Low -- parser falls back to default 3-bucket strategy | Extensive parser tests with diverse roadmap formats; fallback behavior is well-defined in Section 4.2 |
| **Performance regression from Bash subprocess calls** | Low | Low -- adding 4-5 subprocess calls adds ~2-5 seconds to a 1-3 minute operation | Negligible overhead; monitor if roadmap size grows to 100+ phases |

---

## Summary of Recommendations (Priority-Ordered)

1. **Implement programmatic gate validation** (patterns a+b) -- Highest ROI. 14 Python functions replace unreliable self-referential LLM validation. Estimated effort: 2-3 days.

2. **Extract deterministic scoring algorithms** (pattern c) -- Eliminates the most common source of output inconsistency (miscounted keywords, missed compound phrases, wrong confidence penalties). Estimated effort: 1-2 days.

3. **Define typed intermediate data structures** (pattern i) -- Creates stage boundary contracts that make data loss detectable. Estimated effort: 1-2 days.

4. **Extract template rendering** (pattern c, stage 5) -- Eliminates format drift in file emission. The LLM forgets heading levels, em-dash separators, or section ordering with surprising frequency. Estimated effort: 1-2 days.

5. **Add lightweight diagnostics** (pattern g) -- Improves failure remediation when gates detect issues. Estimated effort: 1 day.

**Total estimated effort for selective adoption**: 6-10 days.
**Expected reliability improvement**: Elimination of the most common failure modes (format violations, scoring errors, missing sections, duplicate IDs) which currently occur in an estimated 15-25% of generations for complex roadmaps.
