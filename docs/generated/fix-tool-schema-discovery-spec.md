---
title: "Fix: Tool Schema Discovery Failure in Sprint Subprocess"
version: "1.0.0"
status: draft
feature_id: FIX-001
parent_feature: null
spec_type: refactoring
complexity_score: 0.2
complexity_class: simple
target_release: 4.2.1
authors: [user, claude]
created: 2026-03-15
quality_scores:
  clarity: 9.0
  completeness: 8.5
  testability: 9.5
  consistency: 9.0
  overall: 9.0
---

## 1. Problem Statement

`superclaude sprint run` fails consistently at Phase 2 because `claude`
subprocesses spawned in `--print --output-format stream-json` mode do not have
tool schemas available at session start. The model attempts to call `TodoWrite`
and `Bash` using guessed parameter shapes, which differ from the actual schemas,
causing `InputValidationError` on every invocation.

### 1.1 Evidence

| Evidence | Source | Impact |
|----------|--------|--------|
| `TodoWrite failed: parameter 'todos' expected array, got string; schema not in discovered-tool set` | `results/phase-2-output.txt` | Phase 2 exits code 1; sprint halts |
| `Bash failed: required parameter 'command' missing; unexpected parameter 'cmd' provided; schema not in discovered-tool set` | `results/phase-2-output.txt` | Same phase exit |
| `--tools default` flag confirmed to inject full tool list (Bash, TodoWrite, Glob, Read, Edit, Write, …) in `init` event | Manual validation run | Fix verified before spec written |

### 1.2 Scope Boundary

**In scope**: Adding `--tools default` to `build_command()` in
`src/superclaude/cli/pipeline/process.py` and updating the associated test
assertions.

**Out of scope**: Sprint orchestration logic, prompt construction, the
`extra_args` passthrough mechanism, any other process subclass, schema
validation improvements.

---

## 2. Solution Overview

Insert `"--tools", "default"` into the command list built by
`ClaudeProcess.build_command()`. This flag tells the `claude` CLI to inject all
built-in tool schemas at session start, bypassing the message-history discovery
mechanism that fails in non-interactive subprocess mode.

The change is a two-line addition to one method. All subclasses
(`SprintProcess`, etc.) inherit `build_command()` and pick up the fix
automatically.

### 2.1 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Where to add the flag | `pipeline/process.py:build_command()` (base class) | Each subclass independently; `extra_args` at call site | Single authoritative location; all consumers inherit; no call-site changes needed |
| Flag value | `--tools default` | `--tools all`, per-tool enumeration | `default` matches the built-in set actually needed; `all` may include experimental tools |
| Placement in cmd list | After `--no-session-persistence`, before `--max-turns` | End of list, before `-p` | Keeps session-control flags grouped; does not affect flag parsing order |

### 2.2 Command Before / After

```
BEFORE:
  claude --print --verbose --dangerously-skip-permissions
         --no-session-persistence
         --max-turns <n>
         --output-format stream-json
         -p <prompt>
         [--model <m>] [extra_args...]

AFTER:
  claude --print --verbose --dangerously-skip-permissions
         --no-session-persistence
         --tools default              <-- inserted here
         --max-turns <n>
         --output-format stream-json
         -p <prompt>
         [--model <m>] [extra_args...]
```

---

## 3. Functional Requirements

### FR-001.1: build_command() includes --tools default

**Description**: `ClaudeProcess.build_command()` must include the flags
`--tools` and `default` (as adjacent list elements) in the returned command
list.

**Acceptance Criteria**:
- [ ] `"--tools" in cmd` is `True`
- [ ] `cmd[cmd.index("--tools") + 1] == "default"`
- [ ] Flag appears between `--no-session-persistence` and `--max-turns`

**Dependencies**: None

### FR-001.2: Existing command structure unchanged

**Description**: All flags present before this fix must remain in the returned
command list. The `extra_args` passthrough must continue to work.

**Acceptance Criteria**:
- [ ] `--print`, `--verbose`, `--no-session-persistence`, `--max-turns`,
  `--output-format`, `-p` all still present
- [ ] `extra_args` list still appended after `--model`
- [ ] `--model` flag still conditional on `self.model` being non-empty

**Dependencies**: FR-001.1

### FR-001.3: Test coverage for the new flag

**Description**: A regression test must assert `--tools default` is present so
future edits to `build_command()` cannot silently drop it.

**Acceptance Criteria**:
- [ ] New test `test_tools_default_in_command` exists in
  `tests/pipeline/test_process.py`
- [ ] `test_required_flags` updated to assert `--tools` and `default` present
- [ ] `test_stream_json_matches_sprint_flags` updated similarly
- [ ] All three tests pass under `uv run pytest tests/pipeline/test_process.py -v`

**Dependencies**: FR-001.1

---

## 4. Architecture

### 4.1 New Files

None.

### 4.2 Modified Files

| File | Change | Rationale |
|------|--------|-----------|
| `src/superclaude/cli/pipeline/process.py` | Add `"--tools", "default"` to `build_command()` cmd list (2 lines) | Root fix |
| `tests/pipeline/test_process.py` | Add `test_tools_default_in_command`; update two existing tests | Regression coverage |

### 4.4 Module Dependency Graph

```
ClaudeProcess (pipeline/process.py)
  └── build_command()   <-- only method touched
        inherited by SprintProcess, RoadmapProcess, etc.
              (no changes to subclasses)
```

### 4.6 Implementation Order

```
1. Read pipeline/process.py lines 69-87    -- understand current state, no changes
2. Read tests/pipeline/test_process.py     -- identify assertions to update
   Read tests/sprint/test_process.py       -- [parallel with step 2] check for breaking assertions
   Read tests/roadmap/test_executor.py     -- [parallel with step 2] same check
3. Edit pipeline/process.py                -- insert --tools default
4. Edit tests/pipeline/test_process.py     -- add new test, update two existing
5. uv run pytest tests/pipeline/ -v        -- confirm green
6. uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v  -- no regressions
7. superclaude sprint run ... --dry-run    -- CLI layer smoke test
```

---

## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-001.1 | No performance regression | subprocess start time unchanged | `--tools default` adds <1ms to flag parsing |
| NFR-001.2 | Backwards compatible | All existing callers unaffected | Full test suite green |

---

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `--tools default` enables a tool that was previously hidden, causing unintended model behaviour | Low | Medium | The set of default tools is stable and already used in interactive mode; subprocess mode was the anomaly |
| Subclass overrides `build_command()` and does not call `super()` | Low | Low | Read subclass files in T01/T02 to confirm inheritance chain; none currently override |
| Index-based test assertions in sprint/roadmap suites break | Low | Low | Covered by T06 — update any positional assertions to membership checks |

---

## 8. Test Plan

### 8.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| `test_tools_default_in_command` (new) | `tests/pipeline/test_process.py` | `--tools default` present and adjacent in cmd list |
| `test_required_flags` (updated) | `tests/pipeline/test_process.py` | All required flags including `--tools`/`default` present |
| `test_stream_json_matches_sprint_flags` (updated) | `tests/pipeline/test_process.py` | Stream-json invocation also carries `--tools default` |

### 8.2 Integration Tests

| Test | Validates |
|------|-----------|
| `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` | No regressions across all command-building assertions |
| `superclaude sprint run ... --dry-run` | CLI parses and config loads with new flag present |

---

## 10. Downstream Inputs

### For sc:roadmap
Single bug fix; no milestone impact. Closes a blocker on the
cross-framework-deep-analysis sprint.

### For sc:tasklist
Tasks are already fully specified in the source tasklist
(`docs/generated/fix-tool-schema-discovery-tasklist.md`). No additional
decomposition needed.

---

## 11. Open Items

None. Root cause identified, fix validated, implementation path clear.

---

## Appendix B: Reference Documents

| Document | Relevance |
|----------|-----------|
| `docs/generated/fix-tool-schema-discovery-tasklist.md` | Step-by-step implementation tasks with exact code snippets |
| `src/superclaude/cli/pipeline/process.py` | File under edit |
| `tests/pipeline/test_process.py` | Test file under edit |
