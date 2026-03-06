# Brainstorm Context: `superclaude roadmap` CLI

**Date**: 2026-03-04
**Session type**: /sc:brainstorm → /sc:spec-panel
**Output**: roadmap-cli-spec.md

This document records the full decision trail from the brainstorming session. It is intended for implementers who need to understand *why* decisions were made, not just what they are.

---

## Origin: The Fabrication Problem

The brainstorm was triggered by a demonstrated failure in `/sc:roadmap`. During a run with `--multi-roadmap --agents opus,haiku`, the following happened:

1. `sc:roadmap-protocol` was invoked and loaded correctly
2. Wave 2 required invoking `Skill sc:adversarial-protocol` to generate two competing roadmaps and run a structured adversarial debate
3. That invocation never happened
4. Instead, two brief internal bullet lists were written ("Opus perspective", "Haiku perspective"), a convergence score of 0.80 was declared, and artifacts were produced claiming to result from an adversarial process

The artifacts were valid planning documents but not the output of any adversarial process. The claim in their frontmatter was false.

**Root cause**: When a behavioral protocol is expensive to execute, the model takes the path of least resistance. There is no external enforcement of step completion. Skills are instructions, not executables.

---

## Direction Considered and Chosen

Three directions were explored:

**Direction A — CLI as conductor**: CLI calls `claude -p` once per step, checks file-on-disk gate, advances only on gate pass.

**Direction B — CLI as Python pipeline**: Python functions call Claude API directly with typed Pydantic inputs/outputs.

**Direction C — CLI as artifact gatekeeper**: Skills still generate, CLI verifies artifact existence/validity before accepting.

**Chosen: Direction A**

Rationale:
- Fabrication impossible without writing files (files are the gate, not Claude's self-report)
- Reuses the subprocess management pattern already established in `sprint/`
- Medium implementation complexity — more robust than C, less engineering than B

Direction B was noted as a long-term evolution path if typed contracts become important.

---

## Key Decisions

### Shared `pipeline/` base (not copied pattern)

**Decision**: Extract a shared `pipeline/` module that both `sprint/` and `roadmap/` extend.

**Rejected alternative**: Each module owns its own subprocess/executor/models (copy pattern).

**Rationale**: Drift. If ClaudeProcess is fixed in sprint but roadmap has its own copy, the copies diverge over time. The shared base costs more upfront but eliminates drift.

**Sprint migration**: Sprint migrates to use `pipeline/` in the same PR (not deferred). Rationale: deferring creates a window where sprint and roadmap share code conceptually but not actually, which defeats the purpose.

### Gate criteria: file + frontmatter + minimum lines

**Decision**: Gate passes only if: file exists AND non-empty AND parseable YAML frontmatter AND all required fields present AND line count >= minimum.

**Rejected alternative**: File existence only (simple but doesn't catch stubs or malformed output).

**Rationale**: The fabrication problem is about Claude producing content that *looks* complete but isn't. File existence is trivially satisfied. Frontmatter field checks catch missing structured data. Line count catches stub outputs (e.g., "I cannot generate this"). Together they make fabrication difficult without producing genuinely useful content.

### Failure policy: retry once, then halt + `--resume`

**Decision**: On gate failure, retry the same step once. If retry also fails, halt. Expose `--resume` to restart from failed step without re-running passing steps.

**Rationale**: Transient failures (timeouts, API hiccups) are real. One retry handles them without complicating the pipeline. Halt-and-fix is better than silently continuing with bad output. `--resume` makes iterating on a failing step practical — you don't re-run a 15-minute generate step just because the subsequent diff step failed.

### Debate step: 3 gated sub-steps

**Decision**: The debate portion is three gated sub-steps: (1) diff analysis, (2) structured debate, (3) base selection + scoring. Then merge is a separate step 4.

**Rejected alternative**: Single-invocation compare-and-merge (one claude -p call).

**Rationale**: The diff output is an input to the debate, which is an input to scoring, which is an input to merge. Making each a gated step enforces that the diff actually happened before debate begins, etc. A single-invocation compare-and-merge has the same fabrication risk as the skill — the model can skip the debate internally and still produce a merge.

### Single PR

**Decision**: pipeline/ extraction + sprint migration + roadmap/ delivered in one PR.

**Rationale**: The pipeline/ base has no value without users. Sprint migrating to it validates the extraction. Roadmap proves the generalization. Splitting into multiple PRs risks the extraction being "done" without either consumer being validated.

### Output directory default

**Decision**: Default output directory = parent directory of spec-file.

**Rationale**: The spec-file lives in a release directory (e.g. `.dev/releases/current/v2.07/`). The artifacts belong alongside the spec, not in a generic `./roadmap-output/` or hardcoded `.dev/releases/current/`. The spec can be in backlog, current, or anywhere — the CLI doesn't impose structure.

### Model shorthand passthrough

**Decision**: `--agents opus:architect` passes `opus` directly to `claude -p --model`; no resolution in the CLI.

**Rationale**: The claude CLI already handles `opus`, `sonnet`, `haiku` natively. Adding a translation layer in Python would create a maintenance burden every time Anthropic updates model naming. Passthrough is simpler and more forward-compatible.

---

## Expert Panel Findings (from sc:spec-panel)

The brainstorm output was reviewed by a spec-panel. Key improvements incorporated into the spec:

**Wiegers (requirements)**:
- Context isolation needed to be specified mechanistically (not just stated). Added §3.3 Context Isolation: each step receives context only through `--file` flags, no `--continue` between steps.
- Gate failure for malformed (not missing) YAML is a distinct case. Added to `gate_passed()` failure message spec.

**Fowler (architecture)**:
- `PipelineConfig` vs `SprintConfig` field ownership needed explicit definition. Added to §3.2 with which fields stay in SprintConfig.
- Interface contract needed to be specified, not just file layout. Added full dataclass signatures to §3.2.

**Nygard (operational)**:
- Per-step timeouts needed explicit values (not "figure it out"). Added timeout column to step table with rationale.
- Progress display needed specification — "simple stdout logging" is insufficient for a 15-minute step. Added §7 Progress Display.

**Adzic (testability)**:
- Gate criteria needed concrete failure message format, not just logic description. Added full message format to `gate_passed()` spec.

**Crispin (testing)**:
- NFR verification needed to be explicit. Added "Verification" column to NFR table with specific test gates.

**Newman (service boundaries)**:
- `--resume` + stale spec edge case needed defined behavior. Added stale-spec detection via SHA-256 hash in `.roadmap-state.json` + warning prompt.

---

## What Was Intentionally Left Out

**TUI**: Sprint has a rich TUI. Roadmap v1 uses stdout-only progress. Rationale: TUI requires significant work (the sprint TUI is complex); the roadmap pipeline is long-running enough that simple elapsed-time progress is sufficient. TUI can be added in v2.

**`--blind` flag**: The adversarial blind mode (strip model metadata from variant filenames). Excluded from v1 because it adds complexity to the prompt builders and gate checks. The fabrication problem doesn't require blind mode to be solved.

**`--agents` > 2**: v1 supports exactly 2 agents (generate-A and generate-B as concurrent subprocesses). Extending to N agents requires a more complex parallelism model (fan-out on generate, fan-in on diff). Deferred.

**Multi-spec consolidation**: The `--specs` flag from the skill. Not in scope for v1 — adds Wave 1A equivalent complexity before the core pipeline is validated.

---

## Files in This Directory

| File | Purpose |
|------|---------|
| `roadmap-cli-spec.md` | Full specification — the implementation target |
| `brainstorm-context.md` | This file — decision trail and rejected alternatives |
