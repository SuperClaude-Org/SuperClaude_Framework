# Roadmap Extract Failure Context

## Scope

Investigate why `superclaude roadmap run` fails at the `extract` step for:

```bash
superclaude roadmap run \
  .dev/releases/current/v2.17-cli-portify-v2/refactoring-spec-cli-portify.md \
  --depth deep \
  --agents opus:architect,haiku:analyzer
```

## Failure Symptom

Pipeline halts after two attempts at `extract` with:

```text
YAML frontmatter missing or unparseable in .../extraction.md: no opening ---
```

## Key Files

### CLI entry and orchestration
- `src/superclaude/cli/roadmap/commands.py`
- `src/superclaude/cli/roadmap/executor.py`
- `src/superclaude/cli/roadmap/prompts.py`

### Shared pipeline runtime
- `src/superclaude/cli/pipeline/process.py`
- `src/superclaude/cli/pipeline/gates.py`
- `src/superclaude/cli/pipeline/executor.py`
- `src/superclaude/cli/pipeline/models.py`

### Source command / skill references being ported
- `src/superclaude/commands/roadmap.md`
- `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`
- `src/superclaude/skills/sc-roadmap-protocol/refs/extraction-pipeline.md`
- `src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`

### Runtime artifacts
- `.dev/releases/current/v2.17-cli-portify-v2/refactoring-spec-cli-portify.md`
- `.dev/releases/current/v2.17-cli-portify-v2/extraction.md`
- `.dev/releases/current/v2.17-cli-portify-v2/extraction.err`

## Execution Flow

1. `roadmap run` parses args and builds `RoadmapConfig` in `src/superclaude/cli/roadmap/commands.py`.
2. `execute_roadmap()` builds step list in `src/superclaude/cli/roadmap/executor.py`.
3. Step 1 uses:
   - prompt from `build_extract_prompt()`
   - output file `extraction.md`
   - gate `EXTRACT_GATE`
4. `roadmap_run_step()` launches a Claude subprocess through `ClaudeProcess`.
5. `ClaudeProcess.start()` writes subprocess stdout directly to `extraction.md` and stderr to `extraction.err`.
6. After subprocess exit, `gate_passed()` validates the output file.

## Extract Step Contract

### Prompt contract
`src/superclaude/cli/roadmap/prompts.py`
- Requires output to begin with YAML frontmatter.
- Requests only 3 frontmatter fields:
  - `functional_requirements`
  - `complexity_score`
  - `complexity_class`

### Gate contract
`src/superclaude/cli/roadmap/gates.py`
- `EXTRACT_GATE` requires:
  - frontmatter fields `functional_requirements`, `complexity_score`, `complexity_class`
  - minimum 50 lines
  - enforcement tier `STANDARD`

### Shared parser behavior
`src/superclaude/cli/pipeline/gates.py`
- `_check_frontmatter()` strips only leading whitespace.
- It then requires the stripped content to start with `---`.
- If not, it returns:
  - `YAML frontmatter missing or unparseable ...: no opening ---`

## Concrete Artifact Evidence

`extraction.md` begins with a prose preamble before frontmatter:

```md
Now I have the full spec. Let me produce the extraction document.

---
functional_requirements: 87
complexity_score: 0.92
complexity_class: enterprise
---
```

So the file contains the required fields, but not at the beginning of the stripped document.

## Important Mismatch Discovered

The programmatic CLI prompt/gate pair is much thinner than the source `sc-roadmap` protocol.

### Source protocol expects richer extraction output
`src/superclaude/skills/sc-roadmap-protocol/SKILL.md` + `refs/templates.md`
- Wave 1B writes extraction early.
- Wave 3 later updates extraction frontmatter.
- Template expects many more fields, including:
  - `spec_source` / `spec_sources`
  - `generated`
  - `generator`
  - `nonfunctional_requirements`
  - `total_requirements`
  - `domains_detected`
  - `risks_identified`
  - `dependencies_identified`
  - `success_criteria_count`
  - `extraction_mode`
  - `pipeline_diagnostics`

### Current CLI extract prompt does not model that contract
This means the CLI implementation is not yet faithfully porting the source roadmap protocol’s extraction artifact structure.

## Command Invocation Details

`src/superclaude/cli/pipeline/process.py`
- Command includes:
  - `claude`
  - `--print`
  - `--verbose`
  - `--no-session-persistence`
  - `--output-format text`
  - `-p <prompt>`
- Extra inputs are either embedded into the prompt or passed by `--file`.

## Likely Root-Cause Families

1. **Artifact framing failure**
   - Raw Claude stdout is written directly to the artifact file.
   - No normalization step removes preamble text before gate validation.

2. **Prompt contract weakness / schema drift**
   - Extract prompt is weaker and narrower than the source protocol/templates.
   - The model may not be anchored to a machine-first artifact shape.

3. **CLI mode incompatibility**
   - The subprocess runs with `--verbose` + text output while the gate expects a clean artifact starting at byte 0.

## Constraints for Follow-up Investigation

Any fix should be evaluated against:
- exact source protocol parity
- resumability behavior
- gate strictness expectations across later roadmap steps
- whether the failure is best fixed in prompt design, subprocess invocation mode, artifact normalization, or a combination

## Initial Conclusion

The immediate failure is not that frontmatter is absent. The immediate failure is that the pipeline validates `extraction.md` as if the file starts with frontmatter, but the produced artifact starts with non-whitespace prose.