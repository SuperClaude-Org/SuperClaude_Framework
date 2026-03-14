# D-0024: Release Notes — v2.24.2

## v2.24.2: Accept-Spec-Change

### New Features

- **`superclaude roadmap accept-spec-change` command**: Updates the stored `spec_hash` in `.roadmap-state.json` after accepted deviations, allowing `--resume` to proceed without a full cascade. Requires at least one `dev-*-accepted-deviation.md` file with `disposition: ACCEPTED` and `spec_update_required: true` as evidence.

- **Auto-resume after spec-fidelity failure**: When `execute_roadmap()` is called with `auto_accept=True` and spec-fidelity fails, the executor automatically detects qualifying deviation files and spec changes, performs a single retry cycle with disk-reread state, and resumes the pipeline. At most one retry per invocation.

### Implementation Details

- New leaf module `spec_patch.py` with strict import isolation (stdlib + PyYAML only)
- Atomic state writes via `.tmp` + `os.replace()`
- All new executor functions are private (`_` prefixed)
- `execute_roadmap()` extended with `auto_accept=False` default (backward compatible)
- 65 automated tests covering 14 acceptance criteria and 8 non-functional requirements

### Known Limitations

- Single-writer assumption: no file locking for `.roadmap-state.json`
- mtime resolution on HFS+/NFS may affect auto-resume detection timing
- YAML 1.1 boolean coercion is intentionally accepted (documented contract)
