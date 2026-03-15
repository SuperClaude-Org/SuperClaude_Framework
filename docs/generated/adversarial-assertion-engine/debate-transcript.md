# Debate Transcript: Assertion Engine for Python Pre-Sprint Executor

## Debate Configuration
- **Variants**: 3 (A: Inline DSL, B: Structured Block, C: Hardcoded Python)
- **Dimensions**: Benefit, Risk, Complexity
- **Rounds**: 3 (Opening, Cross-Examination, Convergence)
- **Convergence threshold**: 85%
- **Final convergence**: 87.7%

---

## Round 1: Opening Arguments

### Advocate A (Inline DSL)

**Benefit**: Everything visible in one line within the existing metadata table. The `/sc:tasklist` generator can append a single `| Assert |` row. Human readers see the complete assertion logic inline with the task definition. No need to scroll to a separate block.

**Risk**: Single-line DSL parsing is fragile. Arrow notation and semicolons create a micro-language that needs its own parser, error messages, and escaping rules. If someone puts a semicolon or arrow in a match string, it breaks. No established escaping convention.

**Complexity**: Requires building a custom tokenizer/parser for the DSL (~150 LOC). Testing surface includes malformed DSL strings, escaping edge cases, operator precedence. Moderate implementation effort.

### Advocate B (Structured Block)

**Benefit**: Multi-line format is more readable for complex assertions. The `required` keyword distinguishes hard failures (executor-level) from classification labels (semantic). Separate `stdout`/`stderr` targeting is explicit rather than overloaded. Fits naturally alongside existing `**Steps:**` and `**Acceptance Criteria:**` blocks in the tasklist format.

**Risk**: More lines to parse, but each line is simpler and independently valid. Still a custom micro-language but with less ambiguity per line. The `required` vs `label=` semantic distinction needs clear documentation to avoid misuse. Generator must produce multi-line blocks (slightly more complex template).

**Complexity**: Similar total parsing effort to A (~120 LOC) but with simpler per-line grammar. Each line is independently parseable, reducing coupling. Testing is slightly easier because assertions are isolated -- a malformed line 2 does not affect line 1.

### Advocate C (Hardcoded Python)

**Benefit**: Unlimited expressiveness -- any Python logic including regex, numeric ranges, multi-field correlations. Zero parsing fragility. Classification logic is testable with standard pytest. Full IDE support (autocomplete, type checking, refactoring tools). Aligns with existing codebase patterns: `FailureClassifier`, `TrailingGatePolicy`, and `GateCriteria` all live in Python.

**Risk**: Requires code changes + registration to add new classifiers. The tasklist becomes a pointer (`| Classifier | name |`) rather than self-describing. If someone reads the tasklist without access to the Python source, they cannot understand the classification logic.

**Complexity**: Near-zero parser implementation (~30 LOC: dict lookup + function call). Testing surface is standard Python unit tests -- no custom grammar to exercise. Maintenance burden is the lowest of all three options. Cognitive load for contributors is minimal -- it is just Python.

---

## Round 2: Cross-Examination

### A attacks B
The multi-line `**Assertions:**` block doubles the visual footprint of tasks that need classification. The tasklist already has `**Steps:**`, `**Acceptance Criteria:**`, `**Deliverables:**`, `**Validation:**`, `**Dependencies:**`, and `**Notes:**` blocks. Adding another block contributes to tasklist bloat. The benefit of inline is density -- a single table row adds zero visual noise.

### B rebuts A
Density is not a virtue when it sacrifices readability. A single 120+ character `| Assert |` line containing semicolons, arrows, quoted strings, and operator tokens is harder to parse visually than 3 clear, labeled lines. The tasklist already has 6+ blocks per task; adding a 7th with 2-4 lines is negligible. Furthermore, multi-line format enables syntax highlighting and per-line error reporting, which inline format cannot support.

### A attacks C
The tasklist becomes opaque. A human reading the tasklist cannot understand the classification without consulting Python source code. This violates the principle that the tasklist should be the single source of truth for what a task does and how it is validated. The classifier name `empirical_gate_v1` tells the reader nothing about what constitutes WORKING vs BROKEN.

### C rebuts A
The tasklist is already not self-contained. Steps reference shell commands whose behavior depends on runtime environment. Acceptance criteria reference external systems and file paths. A classifier name like `empirical_gate_v1` is arguably MORE descriptive than `output contains "PINEAPPLE" -> WORKING; exit_code != 0 -> CLI FAILURE; default -> BROKEN` -- the former communicates intent (empirical gate), while the latter communicates mechanics (string matching). And crucially: the known use cases are 3 tasks in one phase. The total classification logic is ~15 lines of Python. This is not a system that needs a DSL.

### B attacks C
Hardcoded classifiers cannot be generated by `/sc:tasklist`. The generator produces markdown. If it needs to specify classification behavior, it must either: (a) generate Python code and register it, which is a fundamentally different workflow, or (b) reference pre-existing classifiers by name, limiting the generator to only classifications that already exist in the codebase.

### C rebuts B
The generator already does not produce Python code -- it produces markdown. Classifier functions are part of the executor codebase, written once during development of the executor feature and reused across tasklists. The generator references them by name, which is trivially achievable: `| Classifier | empirical_gate_v1 |`. If a new classification need arises that no existing classifier handles, the developer writes a new Python function (5-10 lines) and registers it. This is the same workflow as adding a new gate criteria -- it does not require a DSL.

### C attacks A and B
Both DSL options introduce a custom language into the project. Custom languages have compounding maintenance costs: documentation, error messages, edge cases, escaping rules, version evolution, backward compatibility. The project already has `FailureClassifier` and `GateCriteria` in Python. Adding a DSL when the existing pattern is Python classifiers creates architectural inconsistency -- two competing paradigms for the same concept (output classification). This violates DRY at the architectural level.

### A and B rebut C
If future tasklists need novel classification logic that does not match any existing classifier, Option C requires a developer to write Python code and redeploy. Options A and B allow the tasklist author (or the `/sc:tasklist` generator) to specify new assertions without touching the executor codebase. This is especially relevant for the `/sc:tasklist` generator, which should be able to produce complete, self-contained tasklists.

### C counter-rebuts
The "tasklist author" is an LLM agent running `/sc:tasklist`. That agent can equally well reference existing classifier names. And if truly novel classification is needed, writing a Python function is more reliable than extending a DSL -- the DSL will eventually need regex support, numeric comparisons, multi-field assertions, and other features that collectively amount to reinventing a (bad) programming language. The natural end-state of DSL evolution is: "we should have just used Python."

---

## Round 3: Convergence Assessment

### Per-Point Scoring Matrix

| Debate Point | A | B | C | Convergence |
|---|---|---|---|---|
| Handles known classification needs | Yes | Yes | Yes | 100% |
| Extends to unknown future needs | Limited | Limited | Unlimited | 90% |
| Human readability of tasklist | High (inline) | High (multi-line) | Medium (pointer) | 70% |
| Generator integration | Natural (text) | Natural (text) | Natural (name ref) | 85% |
| Parsing fragility risk | High | Medium | None | 95% |
| Security risk (injection/eval) | Low (no eval) | Low (no eval) | None (no parsing) | 100% |
| Semantic ambiguity | Medium | Low | None | 90% |
| Migration cost if wrong choice | Medium | Medium | Low | 85% |
| Implementation effort | ~150 LOC | ~120 LOC | ~30 LOC | 95% |
| Testing surface area | High | Medium | Low | 90% |
| Ongoing maintenance burden | High | Medium | Low | 85% |
| Cognitive load for new contributors | High | Medium | Low | 90% |
| Architectural consistency with codebase | Low | Low | High | 95% |

### Convergence Summary
- **Points with >90% agreement**: 9 of 13
- **Points with >80% agreement**: 12 of 13
- **Single disagreement point**: Readability (70%) -- Advocates A/B argue self-describing tasklists are important; Advocate C argues intent-describing names suffice
- **Overall convergence**: 87.7% (above 85% threshold)

### Key Consensus Points
1. All three options handle the known 3 classification tasks adequately
2. Option C has the lowest implementation, testing, and maintenance costs by a wide margin
3. Option C aligns with existing codebase patterns; A and B introduce new paradigms
4. The readability trade-off is real but bounded (classifier names can be descriptive)
5. DSL evolution pressure is a genuine long-term risk for A and B
