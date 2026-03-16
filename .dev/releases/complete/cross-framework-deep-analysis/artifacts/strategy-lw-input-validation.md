# Strategy: LW Component — Input Validation

**Component**: Input Validation
**Source**: `.gfdoc/scripts/input_validation.sh`
**Path Verified**: true
**Strategy Analyzable**: true
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

Input validation implements a three-layer defense-in-depth model specifically designed to prevent path traversal attacks, command injection, and workspace boundary violations on task names.

**Core rigor mechanisms:**

- **Layer 1 — Regex-based validation** (`validate_task_name()`): Length 3-100 characters; allowed characters `[A-Za-z0-9._/-]` only; forbidden patterns `../`, `..\`, `..`, null bytes, `//`; forbidden prefixes `/` and `.`; forbidden suffix `.`. `input_validation.sh:61-111`
- **Layer 2 — Realpath boundary check** (`is_path_safe()`): Constructs full path, resolves symlinks and `..` sequences via `realpath`, checks resolved path starts within workspace boundaries (`.gfdoc/tasks/` OR `.dev/tasks/`). Accepts either location for dual-structure support. `input_validation.sh:133-220`
- **Layer 3 — Sanitization fallback** (`sanitize_task_name()`): For near-valid input, attempts recovery: spaces→hyphens, remove invalid chars, collapse double slashes, strip leading/trailing dots and slashes, truncate to 100 chars. Fails if result is empty or <3 chars. `input_validation.sh:244-286`
- **Null byte detection**: Uses length comparison (`${#task_name}` vs `printf` byte count) to detect null bytes that bash string operations would otherwise miss. `input_validation.sh:96-102`
- **Workspace root detection**: Uses `git rev-parse --show-toplevel` with fallback to `pwd`. Prevents false boundary determinations in non-git directories. `input_validation.sh:154-161`
- **Dual path support**: Accepts both `.gfdoc/tasks` (legacy) and `.dev/tasks` (new), in priority order. Explicit migration support. `input_validation.sh:163-215`

**Rigor verdict**: The three-layer defense is textbook security design. The realpath boundary check in Layer 2 is the most critical — regex alone cannot prevent all path traversal attacks (symlinks, encoded sequences). Using `realpath` ensures the resolved path is checked, not just the input string.

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- The dual-path support (`.gfdoc/tasks` + `.dev/tasks`) doubles the boundary check logic in Layer 2. This is appropriate for the migration period but adds ongoing maintenance overhead.
- Layer 3 sanitization is a "near-valid input recovery" path. Providing a recovery path for invalid input creates ambiguity: callers must decide whether to use sanitization or enforce strict validation.
- The `realpath -m` flag (no-dereference mode used in some versions) vs `realpath` with symlink resolution creates subtle platform differences on macOS vs Linux.

**Operational drag:**
- `realpath` subprocess invocations (two per validation in the dual-path check) add external process overhead per task validation.
- The null byte detection via `printf` comparison is clever but adds a subprocess call to every validation.

**Maintenance burden:**
- The `validate_task_name()` and `is_path_safe()` functions serve different callers (CLI scripts, interactive scripts). Keeping both functions synchronized requires care.
- The `input_validation.sh` filename differs from the documented path in the milestone spec (`lib/input_validation.sh` vs root scripts directory). Actual deployed path is in `.gfdoc/scripts/`. Minor but creates documentation drift.
- No automated test suite for the validation functions — the milestone doc (`MILESTONE-v5.3-M3.5`) documents the tests as specification, but there is no test runner.

---

## 3. Execution Model

Input validation operates as a **library of reusable security functions** sourced by shell scripts before processing user input:

1. Script sources `input_validation.sh` at startup
2. For every task name input: call `validate_task_name()` (Layer 1)
3. If valid: call `is_path_safe()` (Layer 2) to verify workspace boundary
4. If input is near-valid: optionally call `sanitize_task_name()` (Layer 3) before re-validation
5. If any layer fails: exit with error message; log rejected input for audit

**Quality enforcement**: Fail-fast at each layer with explicit error messages. Layer 1 rejects early (no subprocess), Layer 2 applies boundary enforcement (subprocess), Layer 3 is recovery (not enforcement).

**Extension points**:
- Additional forbidden patterns can be added to Layer 1 regex
- Workspace boundary can be reconfigured by setting `WORKSPACE_ROOT`
- Layer 3 sanitization rules are individually modifiable

---

## 4. Pattern Categorization

**Directly Adoptable:**
- The three-layer defense structure (format validation → boundary check → sanitization fallback) is directly adoptable for SuperClaude's sprint CLI task name inputs and any user-provided file path arguments.
- The null byte detection technique (length comparison via printf) is directly adoptable.
- The realpath-based workspace boundary enforcement is directly adoptable for any CLI tool that accepts file path arguments.

**Conditionally Adoptable:**
- The dual-path support pattern is conditionally adoptable for migration scenarios where path structure is changing.
- The sanitization layer is conditionally adoptable — useful when user-facing UX should accept common inputs (names with spaces) rather than rejecting them.

**Reject:**
- Adopting the bash-specific implementation. The patterns should be ported to the sprint CLI's native language (Python/TypeScript).
- The `realpath` subprocess dependency — Python's `pathlib.Path.resolve()` or Node's `path.resolve()` are native alternatives without subprocess overhead.
