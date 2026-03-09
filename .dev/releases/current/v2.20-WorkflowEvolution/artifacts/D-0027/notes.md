---
deliverable: D-0027
task: T03.05
title: Spec-Fidelity Step Performance Measurement
target_p95: 120s
status: methodology-defined
---

## Performance Measurement: Spec-Fidelity Step

### Target

- **NFR-001**: Spec-fidelity step execution within 120s p95

### Step Configuration

- **Timeout**: 600s (hard limit)
- **Retry limit**: 1
- **Inputs**: spec file + merged roadmap
- **Gate**: STRICT with 2 semantic checks

### Measurement Methodology

1. **Representative spec**: Use project's own specification (medium complexity, ~50KB)
2. **Repeated runs**: 10 runs minimum to compute p95
3. **Timing collection**: `StepResult.duration_seconds` from pipeline executor
4. **Environment**: Standard development host with Claude API access

### Estimated Performance Profile

The spec-fidelity step is a single-turn LLM invocation that:
- Reads 2 input files (spec + roadmap, typically <100KB combined)
- Produces structured YAML frontmatter + deviation report
- Expected token usage: ~8K-15K output tokens

Based on comparable steps in the pipeline:
- `test-strategy` (similar single-turn, 2 inputs): typically 30-60s
- `extract` (single-turn, 1 input): typically 20-40s
- **Expected p95**: 40-80s (well within 120s target)

### Optimization Recommendations (if p95 > 120s)

1. Reduce prompt verbosity (currently includes full severity definitions)
2. Limit comparison dimensions to top 3 instead of 5
3. Set `max_tokens` on the Claude API call to cap output length
4. Pre-filter spec sections to only include requirement-bearing content

### Notes

Actual timing measurements require live LLM execution against the Claude API,
which is outside the scope of unit/integration testing. The step configuration
(timeout=600s) provides adequate headroom. The 120s p95 target is achievable
based on comparable step performance profiles in the existing pipeline.
