# D-0002: Dependency Trace

## Downstream Consumers of the Return Contract

### Consumer 1: `sc:roadmap`

**Skill location**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

**How it consumes the output**: `sc:roadmap` takes a `<spec-file-path>` as its primary argument. The reviewed spec produced by `sc:cli-portify` (`portify-release-spec.md`) is the input artifact. sc:roadmap does NOT parse the return contract YAML directly -- it reads the spec file referenced by `spec_file` in the return contract.

**Contract fields consumed**:
- `spec_file` (path): Used to locate the reviewed release spec to generate a roadmap from
- `downstream_ready` (bool): Advisory signal -- if false, human should review before feeding to sc:roadmap
- `quality_scores.overall` (float): Advisory quality indicator

**Evidence**: `sc-roadmap-protocol/SKILL.md:24` -- "User runs `/sc:roadmap <spec-file>` in Claude Code"; `sc-roadmap-protocol/SKILL.md:37` -- "The roadmap is a planning artifact. sc:roadmap does not trigger downstream commands."

### Consumer 2: `sc:tasklist`

**Skill location**: `src/superclaude/skills/sc-tasklist-protocol/SKILL.md`

**How it consumes the output**: `sc:tasklist` consumes roadmap output (not the return contract directly). The dependency chain is: `sc:cli-portify` -> reviewed spec -> `sc:roadmap` -> roadmap -> `sc:tasklist` -> tasklist.

**Indirect contract fields consumed** (via the reviewed spec):
- Section 10 "Downstream Inputs" subsection "For sc:roadmap" provides themes/milestones
- Section 10 "Downstream Inputs" subsection "For sc:tasklist" provides task breakdown guidance

**Evidence**: No direct references to `cli-portify` or `release-spec` found in `sc-tasklist-protocol/`. The relationship is mediated through `sc:roadmap`.

### Downstream Consumer of the Reviewed Spec Artifact

The reviewed spec artifact (`portify-release-spec.md`) is consumed by:
1. **Human reviewer**: At the Phase 4 user review gate
2. **`sc:roadmap`**: As the spec-file input for roadmap generation
3. **`sc:tasklist`**: Indirectly via the roadmap generated from the spec

## Summary

| Consumer | Artifact Consumed | Contract Fields Used | Relationship |
|----------|-------------------|----------------------|-------------|
| Human reviewer | `portify-release-spec.md` | `spec_file`, `quality_scores`, `downstream_ready` | Direct |
| `sc:roadmap` | `portify-release-spec.md` | `spec_file`, `downstream_ready` | Direct |
| `sc:tasklist` | Roadmap (from sc:roadmap) | None directly | Indirect (2 hops) |
