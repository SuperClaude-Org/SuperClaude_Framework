# Solution 02: Specification-Execution Gap (RC2, Rank 3)

## Problem Summary

Wave 2 step 3 compresses 5 sub-operations into a single sentence using the verb "Invoke," which has no defined mapping to any Claude Code tool call. The `refs/adversarial-integration.md` document uses pseudo-CLI syntax (`sc:adversarial --compare ...`) that resembles user-facing commands rather than programmatic tool calls. Claude cannot resolve "Invoke sc:adversarial" to a concrete action because:

1. The verb "Invoke" is not in the framework's verb-to-tool vocabulary (contrast with "Dispatch" in Wave 4, which maps to Task tool)
2. Five sub-operations are compressed into one step: parse agent specs, expand model-only agents, add orchestrator conditionally, invoke adversarial, handle return contract
3. Critical execution details are deferred to cross-references (`refs/adversarial-integration.md`) rather than inlined at the point of action
4. The pseudo-CLI syntax in the cross-reference document (`sc:adversarial --source <spec> --generate roadmap --agents ...`) looks like a terminal command, not a tool call instruction

**Combined Score**: 0.77 (likelihood 0.75, impact 0.80)

## Comparative Analysis: Why Wave 4 Works

Wave 4 is unambiguous because it follows three structural principles that Wave 2 step 3 violates:

### Principle 1: Atomic Steps (one verb, one tool, one output)

**Wave 4 step 1**: "Dispatch quality-engineer agent using the prompt from `refs/validation.md`"
- Verb: Dispatch (maps to Task tool)
- Agent: quality-engineer
- Input: prompt template from a specific reference section
- Output: validation report JSON

**Wave 2 step 3**: "parse agent specs ... Expand model-only agents ... If agent count >=5, orchestrator is added ... Invoke sc:adversarial ... Handle return contract ..."
- Verbs: parse, expand, add, invoke, handle (5 verbs, 0 tool mappings)
- Agent: unclear (sc:adversarial is a skill, not an agent name)
- Input: scattered across multiple cross-references
- Output: implicit ("The adversarial output replaces template-based generation")

### Principle 2: Explicit Tool Binding

Wave 4 uses "Dispatch" consistently. The framework's ORCHESTRATOR.md defines "Dispatch" as mapping to Task agents. Claude can resolve this.

Wave 2 uses "Invoke" which appears nowhere in the tool-mapping vocabulary. The only "invoke" reference in the framework is the Skill tool description ("Use this tool to invoke it"), but `Skill` is absent from `allowed-tools`.

### Principle 3: Inline Prompts vs. Cross-References

Wave 4's `refs/validation.md` contains complete, self-contained agent prompts with `{variable}` placeholders. Claude reads the ref and has everything needed to construct a Task tool call.

Wave 2's `refs/adversarial-integration.md` contains invocation "formats" (`sc:adversarial --compare <spec-files> --depth <roadmap-depth>`) that look like CLI commands. There is no prompt template, no Task tool instruction, no agent behavioral specification. Claude must infer the entire execution mechanism.

## Options Analysis

### Option A: Explicit Skill Tool-Call Syntax

**Instruction**: "Use the Skill tool with `skill='sc:adversarial'` and `args='--source <spec> --generate roadmap --agents <expanded-agents>'`"

| Criterion | Assessment |
|-----------|------------|
| Clarity | High -- unambiguous tool call |
| Robustness | Low -- fails entirely if Skill tool unavailable |
| Consistency | Low -- no other wave uses Skill tool syntax |
| Complexity | Low -- simple one-line change |
| Addresses root cause | Partial -- fixes verb ambiguity but not the 5-operation compression |

**Verdict**: Insufficient. Solves the verb problem but introduces a single point of failure and does not decompose the compressed step.

### Option B: Expanded Sub-Steps with Tool Mapping

**Instruction**: Decompose step 3 into numbered sub-steps (3a-3f), each with one verb, one tool, one output, mirroring Wave 4's pattern.

| Criterion | Assessment |
|-----------|------------|
| Clarity | High -- mirrors the proven Wave 4 pattern |
| Robustness | Medium -- still needs a mechanism for sc:adversarial execution |
| Consistency | High -- matches existing wave instruction style |
| Complexity | Medium -- adds ~15 lines to SKILL.md |
| Addresses root cause | Full -- fixes verb ambiguity AND operation compression |

**Verdict**: Strong candidate. Directly applies the pattern that works in Wave 4.

### Option C: Decision Tree with Fallback Paths

**Instruction**: If Skill tool available, use it. If not, execute the 5-step adversarial protocol inline using Task agents with debate-orchestrator behavioral instructions.

| Criterion | Assessment |
|-----------|------------|
| Clarity | Medium -- branching adds cognitive load |
| Robustness | High -- handles both Skill-available and Skill-unavailable scenarios |
| Consistency | Low -- no other wave has branching execution paths |
| Complexity | High -- effectively doubles the instruction set for this step |
| Addresses root cause | Full -- covers all failure modes |

**Verdict**: Over-engineered for the current problem. The fallback path adds complexity that itself could become a source of ambiguity.

### Option D: Separate Wave 2A (Non-Adversarial) and Wave 2B (Adversarial)

**Instruction**: Split Wave 2 into two waves with independent entry/exit criteria.

| Criterion | Assessment |
|-----------|------------|
| Clarity | High -- clean separation of concerns |
| Robustness | High -- Wave 2B can be skipped or debugged independently |
| Consistency | Medium -- adds a wave (current architecture is 0, 1A, 1B, 2, 3, 4) |
| Complexity | High -- duplicates entry/exit criteria, ref loading, save points |
| Addresses root cause | Full -- but at significant architectural cost |

**Verdict**: Architecturally sound but disproportionate. The problem is instructional ambiguity, not structural organization. Wave 1A already demonstrates that conditional adversarial logic can coexist within an existing wave when instructions are clear.

## Recommended Solution

**Option B (Expanded Sub-Steps)** with a targeted fallback note from Option C.

Rationale: Option B directly replicates the structural pattern that makes Wave 4 work -- atomic steps with explicit tool bindings. The fallback note from Option C addresses the Skill tool availability concern without introducing full branching complexity. This is the minimal change that eliminates the specification-execution gap.

## Implementation Details

### Change 1: Define Verb-to-Tool Glossary (SKILL.md Section 4, before Wave 0)

Add a vocabulary section to SKILL.md that defines the mapping between instruction verbs and Claude Code tools. This prevents future ambiguity for any verb used in any wave.

**Location**: `src/superclaude/skills/sc-roadmap/SKILL.md`, new subsection in Section 4 before Wave 0.

```markdown
### Instruction Vocabulary

| Verb | Tool | Example |
|------|------|---------|
| Dispatch | Task | "Dispatch quality-engineer agent" = create Task with agent prompt |
| Read | Read | "Read refs/validation.md" = Read tool on file path |
| Write | Write | "Write extraction.md" = Write tool to output path |
| Validate | Bash/Read | "Validate file exists" = Read tool or Bash `test -f` |
| Score | (inline) | "Score template compatibility" = compute in current context |
| Parse | (inline) | "Parse agent specs" = process in current context |
| Invoke skill | Skill | "Invoke sc:adversarial" = Skill tool with skill name and args |
```

### Change 2: Decompose Wave 2 Step 3 into Atomic Sub-Steps

Replace the current Wave 2 step 3 (single compressed sentence) with numbered sub-steps that follow Wave 4's pattern.

**Location**: `src/superclaude/skills/sc-roadmap/SKILL.md`, Wave 2 Behavioral Instructions, step 3.

**Current** (lines 137):
```markdown
3. If `--multi-roadmap`: parse agent specs using the parsing algorithm from
   `refs/adversarial-integration.md` "Agent Specification Parsing" section.
   Expand model-only agents with the primary persona from Wave 1B. If agent
   count >=5, orchestrator is added automatically. Invoke sc:adversarial for
   multi-roadmap generation per `refs/adversarial-integration.md`
   "Multi-Roadmap Generation" invocation pattern. Handle return contract per
   `refs/adversarial-integration.md` "Return Contract Consumption" section.
   The adversarial output replaces template-based generation.
```

**Proposed**:
```markdown
3. If `--multi-roadmap`, execute sub-steps 3a-3f:

   3a. **Parse agent specs** (inline): Split `--agents` value on `,`. For
       each agent, split on `:` (max 3 segments: model, persona, instruction).
       See `refs/adversarial-integration.md` "Agent Specification Parsing"
       for quoted-segment detection and format examples.

   3b. **Expand model-only agents** (inline): For any agent without an
       explicit persona, set persona to the primary persona auto-detected
       in Wave 1B. Example: if Wave 1B detected "security", then `opus`
       becomes `opus:security`.

   3c. **Add orchestrator** (inline, conditional): If expanded agent count
       >= 5, append an orchestrator agent to the list. The orchestrator
       coordinates debate rounds and is not counted toward the 2-10 limit.

   3d. **Invoke sc:adversarial** (Skill tool): Use the Skill tool:
       - `skill`: `"sc:adversarial"`
       - `args`: `"--source <spec-or-unified-spec> --generate roadmap
         --agents <expanded-agent-specs> --depth <depth-flag-value>
         --output <output-dir>"` (append `--interactive` if flag is set)

       If the Skill tool is unavailable (not in allowed-tools or returns
       an error indicating the skill cannot be found): read
       `src/superclaude/skills/sc-adversarial/SKILL.md`, then dispatch a
       Task agent with the adversarial skill's behavioral instructions
       embedded in the Task prompt. Include the agent specs, source file
       path, and depth parameter in the Task prompt.

   3e. **Consume return contract** (inline): Read the return contract from
       sc:adversarial output. Route on `status` field:
       - `status: success` --> use `merged_output_path` as roadmap input,
         record `convergence_score` and `artifacts_dir` in frontmatter
       - `status: partial` + convergence >= 60% --> proceed with warning
         logged in extraction.md
       - `status: partial` + convergence < 60% --> if `--interactive`,
         prompt user; otherwise abort
       - `status: failed` --> abort with error message including
         `artifacts_dir` for debugging

   3f. **Replace template generation** (inline): The adversarial merged
       output replaces steps 4-6 of this wave. Skip to step 7 (record
       decision in Decision Summary). Record adversarial mode, agents,
       convergence_score, and base_variant in the Decision Summary.
```

### Change 3: Apply Same Decomposition to Wave 1A Step 2

Wave 1A step 2 has the same "Invoke" verb problem but was not the observed failure point because `--specs` was not used in the failing test case. Fix it proactively to prevent the same failure mode.

**Location**: `src/superclaude/skills/sc-roadmap/SKILL.md`, Wave 1A Behavioral Instructions, step 2.

**Current** (line 100):
```markdown
2. Invoke sc:adversarial with `--compare` mode per
   `refs/adversarial-integration.md` "Multi-Spec Consolidation" invocation
   pattern. Propagate `--interactive` flag if set (see
   `refs/adversarial-integration.md` "--interactive Flag Propagation" section).
```

**Proposed**:
```markdown
2. **Invoke sc:adversarial for spec consolidation** (Skill tool): Use the
   Skill tool:
   - `skill`: `"sc:adversarial"`
   - `args`: `"--compare <spec-files> --depth <depth-flag-value>
     --output <output-dir>"` (append `--interactive` if flag is set)

   If the Skill tool is unavailable: read
   `src/superclaude/skills/sc-adversarial/SKILL.md`, then dispatch a Task
   agent with the adversarial skill's behavioral instructions embedded in
   the Task prompt. Include the spec file paths, depth, and output directory
   in the Task prompt.
```

### Change 4: Add `Skill` to allowed-tools

**Location**: `src/superclaude/skills/sc-roadmap/SKILL.md`, line 4 (frontmatter).

**Current**:
```yaml
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
```

**Proposed**:
```yaml
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

Note: This change is shared with Solution 01 (RC1). It is listed here for completeness but should be implemented once.

### Change 5: Rewrite adversarial-integration.md Invocation Patterns

The pseudo-CLI syntax in `refs/adversarial-integration.md` should be rewritten as Skill tool call specifications, not CLI commands. This ensures that when Claude follows the cross-reference, it finds tool-call syntax rather than terminal-command syntax.

**Location**: `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`, "Invocation Patterns" section (lines 73-136).

**Current** (example):
```markdown
**Invocation format**:
sc:adversarial --compare <spec-files> --depth <roadmap-depth> --output <roadmap-output-dir> [--interactive]
```

**Proposed** (example):
```markdown
**Skill tool call**:
- `skill`: `"sc:adversarial"`
- `args`: `"--compare <spec-files> --depth <roadmap-depth> --output <roadmap-output-dir>"` (append `--interactive` if sc:roadmap's `--interactive` flag is set)

**Fallback** (if Skill tool unavailable):
- Read `src/superclaude/skills/sc-adversarial/SKILL.md`
- Dispatch Task agent with adversarial behavioral instructions embedded in prompt
- Include parameters: spec-files, depth, output directory
```

Apply this rewrite to both the "Multi-Spec Consolidation" and "Multi-Roadmap Generation" invocation pattern subsections.

## Files Modified

| File | Change | Lines Affected |
|------|--------|----------------|
| `src/superclaude/skills/sc-roadmap/SKILL.md` | Add verb-to-tool glossary | New subsection before Wave 0 |
| `src/superclaude/skills/sc-roadmap/SKILL.md` | Decompose Wave 2 step 3 | Replace line 137 with ~30 lines |
| `src/superclaude/skills/sc-roadmap/SKILL.md` | Decompose Wave 1A step 2 | Replace line 100 with ~10 lines |
| `src/superclaude/skills/sc-roadmap/SKILL.md` | Add Skill to allowed-tools | Line 4 (shared with Solution 01) |
| `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | Rewrite invocation patterns | Lines 73-136 |

## Overlap with Other Solutions

- **Solution 01 (RC1)**: Change 4 (add Skill to allowed-tools) is shared. Implement once.
- **Solution 04 (RC4)**: The return contract consumption in step 3e assumes a transport mechanism. Solution 04 defines the file-based `return-contract.yaml` convention. Step 3e should reference that convention once Solution 04 is implemented.

## Confidence Score

**Overall**: 0.85

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Correctness | 0.90 | Directly mirrors the Wave 4 pattern that demonstrably works |
| Completeness | 0.85 | Covers Wave 2 step 3 and Wave 1A step 2; does not address every cross-reference in adversarial-integration.md |
| Risk of regression | 0.15 | Low -- changes are additive (more detail), not structural (no wave reordering) |
| Dependency on other solutions | 0.30 | Step 3d's Skill tool call requires Solution 01 (allowed-tools). Step 3e's return contract requires Solution 04 (transport mechanism). Without these, the fallback path in 3d handles the Skill tool case, but 3e remains partially unresolved. |

## Verification Criteria

1. **Verb resolution test**: Every verb in the rewritten steps maps to a tool in the glossary or is marked `(inline)` for current-context operations.
2. **Atomic step test**: No sub-step contains more than one tool call or more than one conditional branch.
3. **Wave 4 parity test**: The rewritten Wave 2 step 3 follows the same structural pattern as Wave 4 steps 1-4 (verb + agent/target + reference + output).
4. **Cross-reference test**: Every cross-reference to `refs/adversarial-integration.md` from SKILL.md points to a section that uses tool-call syntax, not pseudo-CLI syntax.

---

*Solution designed 2026-02-22. Analyst: claude-opus-4-6 (self-review agent).*
*Root cause reference: ranked-root-causes.md, RC2 (Rank 3, score 0.77).*
