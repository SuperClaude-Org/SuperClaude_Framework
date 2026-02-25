# Root Cause #4: Return Contract Data Flow

## Summary

The return contract between sc:adversarial and sc:roadmap specifies structured data fields (status, convergence_score, merged_output_path, etc.) but there is no implemented transport mechanism to deliver them. Claude Code skills are markdown instruction files that shape LLM behavior -- they are not callable functions that return typed structs. The only working inter-agent data flow precedent in the codebase (sc:cleanup-audit) uses explicit file-based fan-out/fan-in, which sc:adversarial's return contract does not fully adopt. This architectural gap makes inline execution (spawning agents directly within sc:roadmap's conversation context) the rational shortcut.

## Evidence

### Expected Return Contract (from adversarial-integration.md)

Lines 145-153 of `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` define the expected fields:

```
| Field                  | Type                    | Usage in sc:roadmap                                          |
|------------------------|-------------------------|--------------------------------------------------------------|
| status                 | success | partial | failed | Routes to handling branch                                  |
| merged_output_path     | string (file path)      | Used as input for subsequent waves                           |
| convergence_score      | float (0.0-1.0)         | Recorded in roadmap.md frontmatter; used for threshold routing |
| artifacts_dir          | string (directory path)  | Recorded in roadmap.md frontmatter for traceability          |
| unresolved_conflicts   | integer                 | If >0, logged as warning in extraction.md                    |
| base_variant           | string (model:persona)  | Recorded in roadmap.md frontmatter (multi-roadmap mode only) |
```

These fields feed into three distinct routing branches (lines 156-186):
- `status == "success"` -- proceed normally, record scores in frontmatter
- `status == "partial"` -- check convergence_score against 60% threshold, conditionally proceed or abort
- `status == "failed"` -- abort roadmap generation

The convergence_score threshold routing (lines 163-176) is particularly demanding: it requires a float comparison against 60%, with branching into interactive prompts vs. hard abort depending on the `--interactive` flag.

### sc:adversarial Output Mechanism

The return contract is defined twice in `src/superclaude/skills/sc-adversarial/SKILL.md`:

**High-level definition** (lines 339-350, FR-007):
```yaml
return_contract:
  merged_output_path: "<path to merged file>"
  convergence_score: "<final convergence percentage>"
  artifacts_dir: "<path to adversarial/ directory>"
  status: "success | partial | failed"
  unresolved_conflicts: ["<list of unresolved items>"]
```

**Detailed definition** (lines 1525-1588, T05.07):
```yaml
return_contract:
  purpose: "Enable programmatic integration with other commands (sc:roadmap, sc:design)"
  ...
  integration_pattern:
    generic_integration: |
      Any command can invoke sc:adversarial and consume the return contract:
      1. Call sc:adversarial with appropriate flags
      2. Read return contract fields: merged_output_path, convergence_score, status
      3. If status == 'success': use merged_output_path as the final artifact
      ...
```

The `generic_integration` pattern says "Call sc:adversarial" and "Read return contract fields" but never specifies the mechanism. It reads like a function call API, but skills are not functions.

The debate-orchestrator agent (line 36 of `src/superclaude/agents/debate-orchestrator.md`) is responsible for compiling the return contract:
> "Compile final return contract: Assemble merged output path, convergence score, artifacts directory, status, and unresolved conflicts for the calling command"

But "compile" and "assemble" are verbs without a defined output format or delivery channel. The debate-orchestrator is itself a Task agent -- its only output is the text response returned to the Task tool caller.

### Inter-Skill Data Flow Precedents

**Only one precedent exists**: sc:cleanup-audit (lines 56, 76 of `src/superclaude/skills/sc-cleanup-audit/SKILL.md`):

```
Fan-out/fan-in orchestration: Orchestrator divides work -> spawns N parallel agents ->
agents write to disk -> orchestrator reads and merges
```

```
Fan-Out/Fan-In Orchestration: File inventory -> parallel agent waves (7-8) ->
disk-based results -> consolidated report
```

sc:cleanup-audit solves the data flow problem by having agents write files to a well-known directory (`.claude-audit/`) and having the orchestrator read those files. This is the only inter-agent data flow pattern implemented in the codebase.

**No skill-to-skill data flow precedent exists.** Searching for "inter-skill", "skill-to-skill", "cross-skill", "invoke skill", and "skill communication" returned zero matches across the entire `src/superclaude/` tree.

### Task Agent Return Values

The Task tool in Claude Code returns a single text string -- the agent's final conversational response. Key characteristics:

1. **Unstructured text**: The return value is natural language, not a typed data structure
2. **No named fields**: There is no mechanism to return `{status: "success", convergence_score: 0.85}` as a programmatically accessible object
3. **Parsing burden**: To extract structured data from a Task agent response, the caller must parse the agent's text output for patterns -- but neither sc:roadmap nor sc:adversarial specifies a parse protocol
4. **No guaranteed format**: Task agents produce free-form text; there is no enforcement mechanism to guarantee the agent outputs YAML/JSON in a specific schema

The Skill tool (used for skill invocation) is even less suitable -- it loads a SKILL.md into the conversation context and shapes behavior. It does not "call" the skill and "receive" a return value. It transforms the current agent's behavior.

## Analysis

### File-Based vs In-Memory

The return contract specification is **ambiguous** about the transport mechanism, but implicitly assumes **in-memory/function-call semantics**:

- The language "sc:adversarial returns a structured result" (adversarial-integration.md line 141) implies function-call return
- The `generic_integration` pattern says "Read return contract fields" as if accessing struct members
- There is no instruction to write a `return-contract.json` or `return-contract.yaml` file
- There is no instruction for sc:roadmap to read such a file

The artifacts themselves (merged output, adversarial/ directory) are file-based and deterministic. But the metadata fields (status, convergence_score, unresolved_conflicts, base_variant) are **ephemeral** -- they exist in the debate-orchestrator's reasoning context but are never persisted to a standalone file.

### Deterministic Path Discovery

**Partially solvable**: sc:roadmap passes `--output <roadmap-output-dir>` to sc:adversarial, so it knows where to look for files:
- `<output-dir>/adversarial/` -- exists, deterministic
- `<output-dir>/<merged-output>.md` -- exists, but filename is not fully deterministic (depends on artifact type)
- convergence_score -- **not written to any file** (exists only in debate-transcript.md as narrative text, not as a parseable field)
- status -- **not written to any file** (must be inferred from which artifacts exist and their content)
- unresolved_conflicts -- partially recoverable from debate-transcript.md's "Unresolved points" list
- base_variant -- partially recoverable from base-selection.md's "Selected Base" section

The caller could reconstruct some fields by reading and parsing the adversarial artifacts, but this reverse-engineering is never specified and would be fragile.

### Shortcut Motivation

The absence of a return mechanism strongly motivates inline execution:

1. **Context retention**: By doing adversarial work inline (spawning agents directly within sc:roadmap's conversation), Claude retains all data in its context window. Convergence scores, status, and unresolved conflicts are immediately available without cross-skill transport.

2. **Routing simplification**: The status-routing logic (success/partial/failed with convergence thresholds) requires structured data access. Inline execution makes this trivial -- the data never leaves the conversation context.

3. **Risk avoidance**: Invoking sc:adversarial as a separate skill creates a "hope and pray" situation: sc:roadmap would invoke the skill, then need to figure out what happened by reading files and parsing text. Any deviation from expected output format would break the pipeline.

4. **Precedent gap**: With zero precedents for skill-to-skill return contracts in the codebase, Claude has no pattern to follow. The cleanup-audit fan-out/fan-in pattern works for same-skill sub-agents but has never been attempted cross-skill.

5. **Specification vs implementation gap**: The return contract is thoroughly specified (6 fields, routing logic, threshold handling, frontmatter population) but has zero implementation guidance. This is a spec that describes WHAT data should flow but not HOW it flows -- the classic interface-without-implementation problem.

## Likelihood Score: 0.85/1.0

This is a high-likelihood root cause. The return contract's lack of transport mechanism creates a concrete, structural obstacle that Claude would encounter during execution. Unlike ambiguity in instructions (which Claude might resolve through interpretation), the absence of a data pipeline is a hard technical limitation. Claude cannot invent a skill-to-skill return protocol that does not exist in the framework. The rational response is to keep everything in-context by doing the work inline.

The 0.15 gap accounts for the possibility that Claude could have worked around this by: (a) having sc:adversarial write a `return-contract.yaml` file as a convention, or (b) parsing the debate-transcript.md for convergence data. These workarounds are plausible but not specified, making them unlikely to be attempted autonomously.

## Impact Score: 0.80/1.0

This root cause significantly explains the observed failure. Without a return mechanism:
- sc:roadmap cannot route on status (success/partial/failed)
- sc:roadmap cannot threshold on convergence_score
- sc:roadmap cannot populate frontmatter from return contract fields
- The entire adversarial integration pattern collapses from a composable pipeline to an opaque side-effect

However, this alone does not explain the full failure. Even if Claude decided to skip sc:adversarial invocation, it could have followed the adversarial protocol manually within the sc:roadmap conversation. The fact that it did not follow the full protocol (debate rounds, scoring, etc.) suggests additional root causes beyond just the return contract gap.

## Recommendation

### Immediate Fix: Define a File-Based Return Protocol

Add a return contract file convention to sc:adversarial's SKILL.md:

```yaml
return_contract_file:
  path: "<output-dir>/adversarial/return-contract.yaml"
  written_by: "debate-orchestrator as final step"
  format: |
    status: success|partial|failed
    merged_output_path: <path>
    convergence_score: <float>
    artifacts_dir: <path>
    unresolved_conflicts: <integer>
    base_variant: <model:persona>
  consumed_by: "Calling command reads this file after sc:adversarial completes"
```

Add corresponding read instructions to adversarial-integration.md:

```
After sc:adversarial completes, read <output-dir>/adversarial/return-contract.yaml
to obtain structured return data. Parse YAML and route based on status field.
```

### Structural Fix: Adopt the Fan-Out/Fan-In Pattern

Follow the sc:cleanup-audit precedent explicitly. Instead of treating sc:adversarial as a "function call," treat it as a "file-producing process":

1. sc:roadmap invokes sc:adversarial (via Skill tool or inline instructions)
2. sc:adversarial writes all artifacts PLUS return-contract.yaml to the output directory
3. sc:roadmap reads return-contract.yaml from the known output path
4. sc:roadmap routes based on parsed fields

This aligns with the only working inter-agent data flow pattern in the framework.

### Long-Term: Framework-Level Skill Return Protocol

Consider adding a framework-wide convention for skill-to-skill communication:
- Standard return contract file location: `<skill-output-dir>/.return-contract.yaml`
- Standard schema with required fields (status, output_path) and optional fields
- Standard read/parse instructions in ORCHESTRATOR.md
- This would enable composable skill pipelines beyond just roadmap+adversarial
