# Patch Checklist

Generated: 2026-03-13
Total edits: 11 across 5 files

## File-by-file edit checklist

- phase-1-tasklist.md
  - [ ] H1: Fix T01.01 AC — change "imports only stdlib modules" to "imports only stdlib and PyYAML"
  - [ ] M1: Fix T01.01 validation filter — add `or unreadable or missing` to `-k` expression
  - [ ] H2: Fix T01.02 validation filter — add `or string_true` to `-k` expression
  - [ ] M2: Add T01.02 AC bullet for absent-field default behavior
  - [ ] L1: Add T01.03 AC return-code specification for abort path
  - [ ] M3: Add T01.04 AC bullet requiring "1" in coercion parametrize set

- phase-3-tasklist.md
  - [ ] H3: Fix T03.05 AC — remove "stderr (not stdout)" constraint; replace with stdout capture language
  - [ ] M4: Fix T03.05 deliverable message strings — change from verbatim strings to content requirements

- phase-4-tasklist.md
  - [ ] M5: Fix T04.04 validation filter — change to broader keyword set matching likely test names
  - [ ] L2: Add T04.03 AC target file path for operator docs

- phase-5-tasklist.md
  - [ ] H4: Add T05.02 subprocess check AC and validation step

## Cross-file consistency sweep
- [ ] Confirm all validation filters across phase files use keywords that will plausibly match test function names
- [ ] Confirm PyYAML is referenced consistently (allowed in spec_patch.py, declared in pyproject.toml)

---

## Precise diff plan

### 1) phase-1-tasklist.md — Highest impact (4 edits)

#### T01.01 — AC fix for PyYAML

**A. Fix stdlib-only import criterion**
Current issue: AC says "imports only stdlib modules" — would reject valid `import yaml`
Change: Replace AC bullet with PyYAML-inclusive wording
Diff intent:
- Before: "`spec_patch.py` imports only stdlib modules (no imports from `executor.py` or `commands.py`)"
- After: "`spec_patch.py` imports only stdlib and PyYAML (`import yaml`) — no imports from `executor.py`, `commands.py`, or any other superclaude internal module"

**B. Broaden validation filter (M1)**
Current issue: Filter `-k "hash or state_file or idempotent"` misses unreadable-state tests
Change: Add `or unreadable or missing` to filter
Diff intent:
- Before: `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "hash or state_file or idempotent"`
- After: `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "hash or state_file or idempotent or unreadable or missing"`

#### T01.02 — Filter and AC fix

**C. Broaden validation filter (H2)**
Current issue: Filter misses string_true rejection test
Change: Add `or string_true` to filter
Diff intent:
- Before: `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "deviation or yaml or coercion"`
- After: `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "deviation or yaml or coercion or string_true"`

**D. Add absent-field default AC bullet (M2)**
Current issue: No AC covers absent `disposition` or `spec_update_required` fields
Change: Add 5th AC bullet
Diff intent: Append after the 4th AC bullet:
- "If `disposition` or `spec_update_required` fields are absent from frontmatter, the record is excluded (not an error); processing continues with remaining files"

#### T01.03 — Return code AC (L1)

**E. Add return code to abort AC**
Current issue: AC silent on return code for non-interactive abort
Change: Append to 2nd AC bullet
Diff intent:
- Before: "Non-interactive terminal (`not sys.stdin.isatty()`) with `auto_accept=False` exits with `Aborted.` message and zero file modification (mtime unchanged)"
- After: "Non-interactive terminal (`not sys.stdin.isatty()`) with `auto_accept=False` exits with `Aborted.` message, return code 0, and zero file modification (mtime unchanged) — exit code 1 is reserved for missing file and no-qualifying-deviations conditions"

#### T01.04 — Coercion AC (M3)

**F. Add "1" to coercion AC**
Current issue: AC doesn't explicitly require `"1"` in parametrize set
Change: Add 5th AC bullet
Diff intent: Append after the 4th AC bullet:
- "Coercion test parametrize set includes `'1'` (YAML 1.1 integer-as-boolean) as a passing case alongside `'yes'`, `'on'`, `'True'`, and `'TRUE'`"

---

### 2) phase-3-tasklist.md (2 edits)

#### T03.05 — Logging fixes

**G. Fix stderr/stdout (H3)**
Current issue: AC requires stderr; roadmap doesn't specify stream; Python print() uses stdout
Change: Replace stderr AC bullet
Diff intent:
- Before: "Log messages written to stderr (not stdout)"
- After: "Log messages are printed to stdout with `[roadmap]` prefix and are capturable by test frameworks via stdout capture (e.g., `capsys.readouterr().out`)"

**H. Fix verbatim strings to content requirements (M4)**
Current issue: Deliverables list exact verbatim message strings not specified by roadmap
Change: Replace specific strings with content requirements
Diff intent:
- Before: "`[roadmap] spec-patch cycle 1/1: N qualifying deviation(s) detected`" (etc.)
- After: "Entry message (content: `[roadmap]` prefix + qualifying deviation count + 'cycle 1/1' identifier)"
  "Completion message (content: `[roadmap]` prefix + cycle success indication)"
  "Suppression message (content: `[roadmap]` prefix + indication that guard blocked retry)"

---

### 3) phase-4-tasklist.md (2 edits)

#### T04.04 — Validation filter (M5)

**I. Broaden validation filter**
Current issue: Filter keywords `state_integrity`, `key_preservation`, `mtime_unchanged` won't match typical test names
Change: Replace with plausible keyword alternatives
Diff intent:
- Before: `-k "state_integrity or key_preservation or mtime_unchanged"`
- After: `-k "spec_hash or mtime or disk_reread or only_spec_hash or key_preserved"`

#### T04.03 — Operator docs target (L2)

**J. Add operator docs target path**
Current issue: No file path for operator docs deliverable
Change: Append path guidance to AC bullet
Diff intent:
- Before: "Operator docs mention exclusive access requirement for `.roadmap-state.json`"
- After: "Operator-facing documentation (in `docs/generated/` or inline CLI help text for `accept-spec-change`) explicitly mentions that `.roadmap-state.json` requires exclusive write access during execution"

---

### 4) phase-5-tasklist.md (1 edit)

#### T05.02 — Subprocess check (H4)

**K. Add subprocess verification**
Current issue: Roadmap §5.2 requires subprocess check; T05.02 has none
Change: Add AC bullet and validation bullet
Diff intent for AC: Append after last existing AC bullet:
- "`grep -rn 'subprocess\\|Popen\\|os.system' src/superclaude/cli/roadmap/spec_patch.py` returns no matches (NFR: no subprocess pipeline execution in patch module)"

Diff intent for Validation: Change second validation bullet from generic to:
- "`grep -rn 'subprocess' src/superclaude/cli/roadmap/spec_patch.py`"

---

## Suggested execution order (highest-impact files first)

1. phase-1-tasklist.md (4 High/Medium fixes, most implementer-facing)
2. phase-5-tasklist.md (1 High fix, blocks release gate)
3. phase-3-tasklist.md (1 High + 1 Medium)
4. phase-4-tasklist.md (1 Medium + 1 Low)
