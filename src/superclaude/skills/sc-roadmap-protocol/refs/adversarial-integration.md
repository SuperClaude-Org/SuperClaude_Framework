# Adversarial Integration Reference

Reference document for sc:adversarial integration within sc:roadmap. Contains mode detection, invocation patterns, return contract consumption, error handling, agent specification parsing, frontmatter population, and divergent-specs heuristic.

**Loaded in**: Wave 1A (when `--specs` present) and Wave 2 (when `--multi-roadmap` present).

---

## Mode Detection

sc:roadmap supports three adversarial modes. Mode is determined by flag presence:

| Mode | Trigger Flags | Active Wave | Purpose |
|------|--------------|-------------|---------|
| Multi-spec consolidation | `--specs` | Wave 1A | Merge multiple specs into unified spec |
| Multi-roadmap generation | `--multi-roadmap --agents` | Wave 2 | Generate competing roadmap variants, merge best elements |
| Combined | `--specs` AND `--multi-roadmap --agents` | Wave 1A then Wave 2 | Both pipelines sequentially |

**Detection logic**:
1. If `--specs` flag present AND `--multi-roadmap` flag present → Combined mode
2. If `--specs` flag present (without `--multi-roadmap`) → Multi-spec consolidation
3. If `--multi-roadmap` flag present (without `--specs`) → Multi-roadmap generation
4. If neither flag present → No adversarial mode (standard single-spec pipeline)

**Prerequisite check** (Wave 0): When either `--specs` or `--multi-roadmap` is present, verify `src/superclaude/skills/sc-adversarial/SKILL.md` exists. If not found, abort: `"sc:adversarial skill not installed. Required for --specs/--multi-roadmap flags. Install via: superclaude install"`

---

## Agent Specification Parsing

The `--agents` flag accepts a comma-separated list of agent specifications. Each agent spec follows the format `model[:persona[:"instruction"]]`.

### Parsing Algorithm

1. **Split agent list**: Split the `--agents` value on `,` to produce individual agent specs
2. **Per-agent parsing**: For each agent spec, split on `:` (max 3 segments):
   - **Segment 1** (required): Model identifier (e.g., `opus`, `sonnet`, `haiku`, `gpt52`, `gemini`)
   - **Segment 2** (optional): If unquoted → persona name. If quoted → instruction (no persona)
   - **Segment 3** (optional): Instruction string (must be quoted)
3. **Quoted-second-segment detection**: If the second segment starts with `"` (quote character), treat it as an instruction, not a persona. The agent has no explicit persona and will inherit the primary persona from Wave 1B.

### Format Examples

| Input | Model | Persona | Instruction |
|-------|-------|---------|-------------|
| `opus` | opus | (inherited from Wave 1B) | none |
| `opus:architect` | opus | architect | none |
| `opus:architect:"focus on scalability"` | opus | architect | "focus on scalability" |
| `opus:"focus on scalability"` | opus | (inherited from Wave 1B) | "focus on scalability" |

### Mixed Format Example

`--agents opus:architect,sonnet,gpt52:security` parses to:
- Agent 1: model=opus, persona=architect
- Agent 2: model=sonnet, persona=(inherited)
- Agent 3: model=gpt52, persona=security

### Validation Rules

- **Agent count**: Must be 2-10 agents. If <2 or >10, abort: `"Agent count must be 2-10. Provided: N"`
- **Model validation**: All model identifiers must be recognized. Unknown models trigger abort: `"Unknown model '<model>' in --agents. Available models: opus, sonnet, haiku, gpt52, gemini, ..."`
- **Agent expansion**: Model-only agents (no explicit persona) inherit the primary persona auto-detected from Wave 1B domain analysis. Example: if Wave 1B detects primary persona "security", then `opus` expands to `opus:security`.

### Orchestrator Addition

When agent count ≥ 5, sc:roadmap automatically adds an orchestrator agent to coordinate adversarial debate rounds and prevent combinatorial explosion. The orchestrator:
- Groups similar variants
- Runs elimination rounds before final merge
- Is not counted toward the 2-10 agent limit (it's infrastructure, not a competing agent)

---

## Invocation Patterns

### Multi-Spec Consolidation (Wave 1A)

**Invocation format**:
```
sc:adversarial --compare <spec-files> --depth <roadmap-depth> --output <roadmap-output-dir> [--interactive]
```

**Parameter mapping**:
- `<spec-files>`: Value of sc:roadmap's `--specs` flag (comma-separated paths)
- `<roadmap-depth>`: Value of sc:roadmap's `--depth` flag (maps directly: quick→quick, standard→standard, deep→deep)
- `<roadmap-output-dir>`: sc:roadmap's resolved output directory
- `--interactive`: Present only when sc:roadmap's `--interactive` flag is set

**Depth mapping** (controls debate rounds):
| sc:roadmap --depth | sc:adversarial --depth | Debate Rounds |
|--------------------|------------------------|---------------|
| quick | quick | 1 |
| standard | standard | 2 |
| deep | deep | 3 |

**Example invocations**:
```
# Standard depth, 3 specs
sc:adversarial --compare spec1.md,spec2.md,spec3.md --depth standard --output .dev/releases/current/auth-system/

# Deep depth with interactive approval
sc:adversarial --compare spec1.md,spec2.md --depth deep --output .dev/releases/current/auth-system/ --interactive
```

### Multi-Roadmap Generation (Wave 2)

**Invocation format**:
```
sc:adversarial --source <spec-or-unified-spec> --generate roadmap --agents <expanded-agent-specs> --depth <roadmap-depth> --output <roadmap-output-dir> [--interactive]
```

**Parameter mapping**:
- `<spec-or-unified-spec>`: Single spec file path, or unified spec from Wave 1A (if combined mode)
- `--generate roadmap`: Fixed value — tells sc:adversarial what artifact type to generate
- `<expanded-agent-specs>`: Agent specs after expansion (model-only agents filled with primary persona)
- `<roadmap-depth>`: Value of sc:roadmap's `--depth` flag
- `<roadmap-output-dir>`: sc:roadmap's resolved output directory
- `--interactive`: Present only when sc:roadmap's `--interactive` flag is set

**Example invocations**:
```
# 3 agents, standard depth (after persona expansion to "security")
sc:adversarial --source spec.md --generate roadmap --agents opus:security,sonnet:security,gpt52:security --depth standard --output .dev/releases/current/auth-system/

# 5+ agents triggers orchestrator (orchestrator added automatically by sc:adversarial)
sc:adversarial --source spec.md --generate roadmap --agents opus:architect,sonnet:security,gpt52:backend,haiku:frontend,gemini:performance --depth deep --output .dev/releases/current/platform/ --interactive
```

### Combined Mode

When both `--specs` and `--multi-roadmap --agents` are present:
1. Wave 1A: Invoke multi-spec consolidation → produces unified spec
2. Wave 1B: Extract from unified spec (standard pipeline)
3. Wave 2: Invoke multi-roadmap generation with unified spec as `--source`

The unified spec from Wave 1A becomes the `--source` input for Wave 2's multi-roadmap invocation.

---

## Return Contract Consumption

sc:adversarial returns a structured result. sc:roadmap consumes the following fields. Note: the return contract schema itself is defined in SC-ADVERSARIAL-SPEC.md; this section documents only how sc:roadmap uses each field.

### Return Fields

| Field | Type | Usage in sc:roadmap |
|-------|------|---------------------|
| `status` | `success` \| `partial` \| `failed` | Routes to handling branch (see below) |
| `merged_output_path` | string (file path) | Used as input for subsequent waves |
| `convergence_score` | float (0.0-1.0) | Recorded in roadmap.md frontmatter; used for threshold routing |
| `artifacts_dir` | string (directory path) | Recorded in roadmap.md frontmatter for traceability |
| `unresolved_conflicts` | integer | If >0, logged as warning in extraction.md |
| `base_variant` | string (model:persona) | Recorded in roadmap.md frontmatter (multi-roadmap mode only) |

### Status Routing

```
status == "success"
  → Use merged_output_path as input for subsequent waves
  → Record convergence_score and artifacts_dir in frontmatter
  → Proceed normally

status == "partial"
  → Check convergence_score:
    ≥ 60%:
      → Proceed with warning logged in extraction.md:
        "Adversarial consolidation partial (convergence: XX%). Some conflicts unresolved."
      → Record convergence_score and artifacts_dir in frontmatter
      → Use merged_output_path as input
    < 60%:
      → If --interactive flag set:
        → Prompt user: "Adversarial convergence is XX% (below 60% threshold).
           Proceed anyway? [Y/n]"
        → If user approves: proceed as ≥60% path
        → If user declines: abort
      → If --interactive not set:
        → Abort with message: "Adversarial convergence XX% is below 60% threshold.
           Use --interactive to approve low-convergence results, or revise specifications."

status == "failed"
  → Abort roadmap generation
  → Error message includes:
    - "sc:adversarial failed. Roadmap generation aborted."
    - unresolved_conflicts count (if present)
    - artifacts_dir (if present, for debugging)
    - Recommendation: "Review adversarial artifacts at <artifacts_dir> for details."
```

### Unresolved Conflicts Handling

When `unresolved_conflicts > 0` (regardless of status), log warning in extraction.md:
```
> **Warning**: Adversarial consolidation produced N unresolved conflicts.
> Review artifacts at <artifacts_dir> for conflict details.
```

---

## Divergent-Specs Heuristic

**Trigger**: convergence_score < 50% (regardless of status)

**Action**: Emit warning message:
```
"Specifications may be too divergent for meaningful consolidation.
Consider running separate roadmaps or using --interactive for manual conflict resolution."
```

This warning is in addition to any status-based handling. It fires even if convergence is 50-59% and --interactive is used to proceed — the warning alerts the user that the consolidated result may be low quality.

**Recording**: The warning is logged in extraction.md under a "Consolidation Warnings" section.

---

## Frontmatter Population

When adversarial mode is used, the `adversarial` block in roadmap.md frontmatter is populated from the return contract fields:

```yaml
adversarial:
  mode: <multi-spec|multi-roadmap|combined>    # From mode detection
  agents: [<agent-spec-1>, <agent-spec-2>]     # From --agents flag (expanded form)
  convergence_score: <0.0-1.0>                 # From return contract
  base_variant: <model:persona>                # From return contract (multi-roadmap only)
  artifacts_dir: <path>                        # From return contract
```

**Population rules**:
- `mode`: Set based on mode detection logic (see above)
- `agents`: List of expanded agent specs (after model-only expansion). For multi-spec mode, this is the implicit agents used by sc:adversarial (typically 2 advocate agents)
- `convergence_score`: Direct copy from return contract
- `base_variant`: Present only in multi-roadmap and combined modes. Set from return contract's `base_variant` field (the variant that won the adversarial debate)
- `artifacts_dir`: Direct copy from return contract. Path to directory containing adversarial debate artifacts

**When adversarial mode is NOT used**: The `adversarial` block is completely absent from frontmatter (not present with null values — entirely omitted).

---

## Error Handling

### Adversarial Skill Not Installed

**Condition**: `--specs` or `--multi-roadmap` flag present, but `src/superclaude/skills/sc-adversarial/SKILL.md` not found.

**Action**: Abort in Wave 0 with:
```
"sc:adversarial skill not installed. Required for --specs/--multi-roadmap flags.
Install via: superclaude install"
```

### Unknown Model Identifier

**Condition**: `--multi-roadmap` flag present, and a model identifier in `--agents` is not recognized.

**Action**: Abort in Wave 0 with:
```
"Unknown model '<model>' in --agents. Available models: opus, sonnet, haiku, gpt52, gemini, ..."
```

### Agent Count Out of Range

**Condition**: Agent list has fewer than 2 or more than 10 entries.

**Action**: Abort in Wave 0 with:
```
"Agent count must be 2-10. Provided: N"
```

### sc:adversarial Invocation Failure

**Condition**: sc:adversarial invocation fails (not a status response, but a skill-level failure).

**Action**: Abort with:
```
"sc:adversarial invocation failed. Check that the skill is properly installed and configured."
```

---

## --interactive Flag Propagation

The `--interactive` flag on sc:roadmap propagates to sc:adversarial invocations in both adversarial paths:

| sc:roadmap invocation | Propagation |
|----------------------|-------------|
| `--specs` (Wave 1A) | `--interactive` appended to `sc:adversarial --compare` invocation |
| `--multi-roadmap` (Wave 2) | `--interactive` appended to `sc:adversarial --source --generate` invocation |
| Combined mode | `--interactive` appended to both invocations |

**Behavioral impact**:
- When `--interactive` is set: sc:adversarial prompts for user approval at decision points; sc:roadmap prompts at convergence <60% threshold
- When `--interactive` is NOT set: sc:adversarial uses auto-resolution; sc:roadmap aborts at convergence <60% threshold

**Flag presence rule**: Only append `--interactive` to sc:adversarial invocation when `--interactive` is explicitly set on sc:roadmap. Default (no flag) means no propagation.

---

*Reference document for sc:roadmap v2.0.0 — loaded on-demand during Wave 1A and/or Wave 2*
