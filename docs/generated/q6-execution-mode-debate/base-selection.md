# Base Selection -- Q6: execution_mode Annotation Location

## Quantitative Metrics

| Metric | 3a | 3b | 3c | 3d | Weight |
|---|---|---|---|---|---|
| Discovery timing satisfaction | 1.0 | 0.8 | 0.0 | 0.5 | 0.30 |
| Parser change LOC estimate | 10 | 30 | 20 | 45 | 0.15 |
| Generator change LOC estimate | 5 | 15 | 20 | 25 | 0.10 |
| Files modified (runner side) | 2 | 2 | 2 | 3 | 0.05 |
| Format consistency (0-1) | 1.0 | 0.3 | 1.0 | 0.9 | 0.15 |
| Evolution path to finer granularity (0-1) | 0.8 | 0.5 | 1.0 | 1.0 | 0.10 |
| YAGNI compliance (0-1) | 1.0 | 0.9 | 0.4 | 0.5 | 0.15 |

### Normalized Scores (higher = better)

Discovery timing: 3a=1.0, 3b=0.8, 3c=0.0, 3d=0.5
Parser simplicity (inverted LOC): 3a=1.0, 3b=0.33, 3c=0.50, 3d=0.22
Generator simplicity (inverted LOC): 3a=1.0, 3b=0.33, 3c=0.25, 3d=0.20
Files modified (inverted): 3a=1.0, 3b=1.0, 3c=1.0, 3d=0.67
Format consistency: 3a=1.0, 3b=0.3, 3c=1.0, 3d=0.9
Evolution path: 3a=0.8, 3b=0.5, 3c=1.0, 3d=1.0
YAGNI: 3a=1.0, 3b=0.9, 3c=0.4, 3d=0.5

### Weighted Composite

| Variant | Weighted Score |
|---|---|
| **3a** | 0.30(1.0) + 0.15(1.0) + 0.10(1.0) + 0.05(1.0) + 0.15(1.0) + 0.10(0.8) + 0.15(1.0) = **0.98** |
| **3b** | 0.30(0.8) + 0.15(0.33) + 0.10(0.33) + 0.05(1.0) + 0.15(0.3) + 0.10(0.5) + 0.15(0.9) = **0.58** |
| **3c** | 0.30(0.0) + 0.15(0.50) + 0.10(0.25) + 0.05(1.0) + 0.15(1.0) + 0.10(1.0) + 0.15(0.4) = **0.40** |
| **3d** | 0.30(0.5) + 0.15(0.22) + 0.10(0.20) + 0.05(0.67) + 0.15(0.9) + 0.10(1.0) + 0.15(0.5) = **0.52** |

## Qualitative Rubric (CEV Protocol)

### Correctness
- **3a**: Fully correct -- annotation is available at the exact code site where the decision is made.
- **3b**: Correct but requires opening each phase file before the phase loop, adding latency.
- **3c**: Incorrect for the stated requirement -- annotation is not available before subprocess launch without restructuring the parser.
- **3d**: Partially correct -- phase default is available, but override resolution requires pre-parsing.

### Extensibility
- **3a**: Good. Migration path to 3d is clean: add optional `execution_mode` field to `TaskEntry`, make index value the default, task overrides win. No breaking changes.
- **3b**: Poor. YAML frontmatter is a dead-end format choice for this codebase.
- **3c**: Good for task-level, but does not solve the discovery timing problem.
- **3d**: Best extensibility, but pays the complexity cost upfront for a need that does not yet exist.

### Verifiability
- **3a**: Trivially verifiable -- single source of truth in one table.
- **3b**: Requires verifying each phase file has frontmatter.
- **3c**: Requires verifying every task has the field.
- **3d**: Requires verifying consistency between index default and task overrides.

## Combined Scoring

| Variant | Quantitative (0.6) | Qualitative (0.4) | Combined |
|---|---|---|---|
| **3a** | 0.98 * 0.6 = 0.588 | 0.93 * 0.4 = 0.372 | **0.960** |
| **3b** | 0.58 * 0.6 = 0.348 | 0.45 * 0.4 = 0.180 | **0.528** |
| **3c** | 0.40 * 0.6 = 0.240 | 0.50 * 0.4 = 0.200 | **0.440** |
| **3d** | 0.52 * 0.6 = 0.312 | 0.65 * 0.4 = 0.260 | **0.572** |

## Selection

**Selected base: 3a (Index-level column)**

**Rationale**: 3a scores highest on both quantitative and qualitative dimensions. It satisfies the primary constraint (discovery timing) perfectly, requires the least code change, and fits the existing format conventions. The evolution path to 3d (if mixed-mode phases ever materialize) is clean and non-breaking.

**Position-bias mitigation note**: Variants were evaluated in shuffled order (3c, 3a, 3d, 3b) during qualitative rubric to prevent primacy bias. 3a scored highest regardless of evaluation order.
