

---
spec_source: "release-spec-accept-spec-change.md"
generated: "2026-03-13T00:00:00Z"
generator: "claude-opus-4-6-requirements-extractor"
functional_requirements: 13
nonfunctional_requirements: 8
total_requirements: 21
complexity_score: 0.65
complexity_class: moderate
domains_detected: 4
risks_identified: 5
dependencies_identified: 4
success_criteria_count: 15
extraction_mode: full
---

## Functional Requirements

**FR-001** (FR-2.24.2.1): **Locate state file** — Read `.roadmap-state.json` from `output_dir`. Exit 1 with message "No .roadmap-state.json found in <output_dir>. Run `roadmap run` first." if absent or unreadable.

**FR-002** (FR-2.24.2.2): **Recompute current spec hash** — Load `spec_file` path from state file, compute `sha256(spec_file.read_bytes())`. Exit 1 with "Spec file not found: <path>" if missing.

**FR-003** (FR-2.24.2.3): **Check for hash mismatch** — If current hash equals `state["spec_hash"]`, print "Spec hash is already current. Nothing to do." and exit 0. Treat absent/null/empty `spec_hash` as mismatch. Byte-exact string equality on hex digest, no normalization. Must be idempotent (AC-3).

**FR-004** (FR-2.24.2.4): **Scan for accepted deviation evidence** — Glob `output_dir` for `dev-*-accepted-deviation.md` files. Parse YAML frontmatter. Collect records where `disposition: ACCEPTED` (case-insensitive) and `spec_update_required: true` (YAML boolean, not string `"true"`). Skip unparseable files with stderr warning. Exit 1 with descriptive message if zero qualifying records found.

**FR-005** (FR-2.24.2.5): **Display evidence summary and prompt** — Print summary of matching deviation records with IDs, severity, affected sections, and rationale. Prompt `[y/N]`. Only `y`/`Y` single character confirms; all other input (including `yes`, empty string) treated as N. Non-interactive detection via `not sys.stdin.isatty()`: when non-interactive and `auto_accept=False`, exit 0 with "Aborted." without touching state file.

**FR-006** (FR-2.24.2.6): **Update spec_hash atomically** — On confirmation, write updated state using atomic pattern: write to `.roadmap-state.json.tmp` then `os.replace()`. Overwrite existing `.tmp` file. Modify only `spec_hash`; preserve all other keys verbatim (`steps`, `fidelity_status`, `validation`, `remediate`, `certify`, `agents`, `depth`, `last_run`).

**FR-007** (FR-2.24.2.7): **Confirmation output** — Print old/new hashes (truncated to 12 chars), list accepted deviation IDs, and instruct user to run `roadmap run --resume`. Exit 0.

**FR-008** (FR-2.24.2.8): **auto_accept parameter** — Add `auto_accept: bool = False` to `execute_roadmap()` signature. When `True`, skip interactive prompt and proceed automatically if evidence found. Thread through call chain: `execute_roadmap() → _apply_resume_after_spec_patch() → prompt_accept_spec_change()`. When `False` and non-interactive, fall through to normal failure handling without prompting.

**FR-009** (FR-2.24.2.9): **Post-spec-fidelity-FAIL detection** — After spec-fidelity FAIL, check three conditions (all required): (1) `_spec_patch_cycle_count` has not fired (count < 1); (2) qualifying deviation files exist with mtime strictly `>` spec-fidelity `started_at` timestamp (with proper ISO→timestamp conversion); (3) spec file hash differs from `initial_spec_hash` (local var captured at `execute_roadmap()` entry, NOT `state["spec_hash"]`).

**FR-010** (FR-2.24.2.10): **Disk-reread at resume boundary** — Six-step sequence: (1) re-read state from disk; (2) recompute spec hash; (3) atomic write of new hash to state file (abort cycle on write failure with stderr error); (4) re-read state from disk again (this is the object passed to `_apply_resume()`); (5) rebuild steps via `_build_steps(config)`; (6) call `_apply_resume(post_write_state, steps)`.

**FR-011** (FR-2.24.2.11): **Recursion guard** — `_spec_patch_cycle_count` must be a local variable inside `execute_roadmap()`, initialized to 0. Increment before entering cycle. Skip if count >= 1. Per-invocation scope, not per-process or module-level. Maximum one spec-patch resume cycle per `execute_roadmap()` invocation.

**FR-012** (FR-2.24.2.12): **Cycle outcome logging** — Log entry message with deviation count and "cycle 1/1", completion message on cycle end, and suppression message when recursion guard fires. All messages prefixed with `[roadmap]`.

**FR-013** (FR-2.24.2.13): **Normal failure on cycle exhaustion** — If spec-fidelity still fails after patched resume, fall through to `_format_halt_output` + `sys.exit(1)`. Use post-resume (second run) results for halt output, not first-run results. No second cycle.

## Non-Functional Requirements

**NFR-001**: **Atomic write safety** — No partial state corruption on power loss mid-write. `os.replace()` provides POSIX atomicity on same filesystem. Windows support is best-effort.

**NFR-002**: **Read-only on abort** — State file must never be touched if user answers N or operation is aborted. Measurable via unchanged mtime after abort.

**NFR-003**: **Idempotency** — Running `accept-spec-change` twice with the same spec change is safe. Second run exits 0 cleanly with "nothing to do" message.

**NFR-004**: **No pipeline execution** — `spec_patch.py` must never invoke pipeline subprocesses. Zero `ClaudeProcess` usage in the module.

**NFR-005**: **Exclusive access** — No concurrent write protection implemented. Documented constraint: operator must prevent concurrent access to `.roadmap-state.json`.

**NFR-006**: **Module isolation** — `spec_patch.py` imports only stdlib + PyYAML. No imports from `executor.py` or `commands.py`. Prevents circular dependency risk.

**NFR-007**: **Backward compatibility** — `execute_roadmap()` signature change must be backward-compatible. `auto_accept` defaults to `False`. All existing callers work without modification.

**NFR-008**: **Minimal public API surface** — All new functions in `executor.py` use leading underscore convention. Only `execute_roadmap()` is public. No new public symbols introduced.

## Complexity Assessment

**complexity_score**: 0.65
**complexity_class**: moderate

**Scoring rationale**:
- **Scope** (+0.15): Three files modified, three new files created. Changes are additive — no modification of existing `_apply_resume()` logic.
- **State management** (+0.20): Atomic file writes, disk-reread patterns, hash comparison across multiple sources (local var vs state file vs current file). Multi-step state trace in FR-10.
- **Control flow** (+0.15): Three-condition detection gate (FR-9), recursion guard, auto_accept threading through call chain, non-interactive detection.
- **Edge cases** (+0.10): YAML boolean vs string distinction, mtime resolution limitations, frontmatter parse errors, `.tmp` file pre-existence, absent/null/empty hash handling.
- **Integration surface** (+0.05): Single new CLI command, one signature change with default parameter. No breaking changes.

The spec is well-defined with explicit state traces and edge case handling, which reduces implementation ambiguity despite moderate inherent complexity.

## Architectural Constraints

1. **Module dependency direction**: `spec_patch.py` is a leaf module — it must NOT import from `executor.py` or `commands.py`. Dependency flows: `commands.py → spec_patch.py` and `executor.py → spec_patch.py`.

2. **Atomic write pattern**: All state file mutations must use write-to-tmp + `os.replace()` pattern. No direct writes to `.roadmap-state.json`.

3. **No modification of `_apply_resume()`**: Changes are additive only. The existing resume logic is untouched.

4. **Same-process architecture**: Auto-resume cycle runs in-process (no subprocess call to `accept-spec-change`). Disk-reread provides safety boundary.

5. **Private API convention**: All new `executor.py` functions use leading underscore (`_apply_resume_after_spec_patch`, `_find_qualifying_deviation_files`). Public API surface is `execute_roadmap()` only.

6. **POSIX primary target**: `os.replace()` atomicity guaranteed on POSIX with same-filesystem constraint. Windows is best-effort.

7. **No file locking**: Concurrent modification of `.roadmap-state.json` is not protected. Single-writer assumption documented as constraint.

8. **Click framework**: CLI command uses `click.Path(exists=True)` for `output_dir` argument. Zero optional flags by design.

## Risk Inventory

**RISK-001** (Medium severity): **TOCTOU window on state file** — State file could be modified between read and atomic write. *Mitigation*: NFR-5 documents exclusive access constraint; no concurrent `roadmap run` supported.

**RISK-002** (Low severity): **Filesystem mtime resolution** — On filesystems with 1-second mtime resolution (HFS+, some NFS), files written in the same second as `started_at` won't satisfy FR-9 Condition 2. *Mitigation*: Documented limitation; implementations may use `>=` with rationale.

**RISK-003** (Low severity): **PyYAML boolean coercion** — `yes`/`on`/`1` accepted as boolean `true` per YAML 1.1. *Mitigation*: Intentional broader acceptance documented in spec.

**RISK-004** (Medium severity): **Invalid YAML in deviation files** — Files matching glob pattern but containing malformed YAML frontmatter. *Mitigation*: FR-004 requires warn-and-skip behavior with stderr warning per file.

**RISK-005** (Low probability, High impact): **Accidental `auto_accept=True`** — A caller passes `auto_accept=True` unintentionally, bypassing human review. *Mitigation*: Parameter is internal (not CLI-exposed); only sprint runner uses it.

## Dependency Inventory

| # | Dependency | Type | Version | Usage |
|---|-----------|------|---------|-------|
| 1 | **PyYAML** | Python library | `>=6.0` | YAML frontmatter parsing in `spec_patch.py` (new dependency in `pyproject.toml`) |
| 2 | **Click** | Python library | `>=8.0.0` (existing) | CLI command definition for `accept-spec-change` |
| 3 | **hashlib** (stdlib) | Python stdlib | N/A | SHA-256 hash computation |
| 4 | **executor.py internals** | Internal module | Current | `execute_roadmap()`, `_apply_resume()`, `_build_steps()`, `_format_halt_output()`, `_save_state()`, `read_state()` — existing functions consumed but not modified |

## Success Criteria

| ID | Criterion | Threshold |
|----|-----------|-----------|
| AC-1 | `accept-spec-change` exits 1 with clear message when no accepted deviation records found | Exit code 1 + descriptive stderr message |
| AC-2 | `accept-spec-change` updates only `spec_hash` — all other state keys preserved verbatim | Byte-level JSON comparison of non-`spec_hash` keys |
| AC-3 | `accept-spec-change` is idempotent — running twice does not corrupt state | Second run exits 0 with "nothing to do" |
| AC-4 | `accept-spec-change` never touches state file if user answers N | State file mtime unchanged after N response |
| AC-5a | Updated `spec_hash` matches value `_apply_resume()` compares against | Hash equality verification |
| AC-5b | After `accept-spec-change`, `roadmap run --resume` skips upstream steps (extract, generate, diff, debate, score, merge, test-strategy) | Only spec-fidelity re-runs |
| AC-6 | Auto-resume cycle fires at most once per `execute_roadmap()` invocation | Recursion guard prevents second cycle |
| AC-7 | Auto-resume cycle re-reads state from disk, not in-memory results | Post-write disk state passed to `_apply_resume()` |
| AC-8 | If spec-fidelity still fails after patched resume, pipeline exits 1 normally | No infinite loop; `sys.exit(1)` after single retry |
| AC-9 | `auto_accept=True` skips prompt; `False` prompts user | Behavioral verification in both modes |
| AC-10 | `execute_roadmap()` callable without `auto_accept` argument | Backward-compatible default `False` |
| AC-11 | Non-interactive + `auto_accept=False` exits 0 with "Aborted." without modifying state | CI/pipe environment safety |
| AC-12 | Cycle entry/completion/suppression messages logged correctly | `[roadmap]` prefixed messages at each lifecycle point |
| AC-13 | Atomic write failure in FR-10 Step 3 aborts cycle and falls through | stderr error + normal failure path |
| AC-14 | YAML parse errors in deviation files produce warnings, not crashes | Warn + skip + continue processing |

## Open Questions

All items from Section 11 of the spec are marked **Resolved**. The following residual questions remain:

1. **Severity field in deviation records**: FR-005 shows `HIGH` severity in the prompt output example, but the `DeviationRecord` dataclass (§4.5) has no `severity` field. Where does the severity value come from? Is it extracted from the frontmatter (undocumented field) or inferred?

2. **PyYAML already in dependency tree?**: The spec adds `pyyaml>=6.0` to `pyproject.toml`. If PyYAML is already an indirect dependency, this is low-risk. If not, it's a new transitive dependency for all `superclaude` users — worth confirming acceptable.

3. **Deviation record cleanup**: After `accept-spec-change` succeeds, should the deviation `.md` files be archived, moved, or left in place? The spec is silent on post-acceptance file lifecycle.

4. **Multiple spec edits between runs**: If the spec is edited multiple times (with multiple deviation records from different subprocess runs), does the command handle this correctly? The scan collects all matching records, but the prompt shows them as a single batch — stakeholder confirmation that this is the intended UX.

5. **`started_at` field absence**: FR-009 Condition 2 depends on `state["steps"]["spec-fidelity"]["started_at"]`. What happens if this key is absent (e.g., spec-fidelity never ran)? The spec doesn't define fallback behavior for missing timestamp.
