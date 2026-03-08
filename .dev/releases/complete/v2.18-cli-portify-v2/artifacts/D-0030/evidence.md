# D-0030: main.py Patch and Integration Smoke Test Evidence

**Task**: T04.05
**Roadmap Items**: R-075, R-076, R-077
**Date**: 2026-03-08

---

## main.py Patch

### Import Added
```python
from superclaude.cli.cleanup_audit import cleanup_audit_group
```

### Command Registration Added
```python
main.add_command(cleanup_audit_group, name="cleanup-audit")
```

### Patch Location
After the existing `roadmap` command registration at line 360, before `if __name__ == "__main__":`.

## Smoke Test Results

| Test | Result | Details |
|------|--------|---------|
| Module imports | PASS | `cleanup_audit_group` imported from `superclaude.cli.cleanup_audit` |
| Click command group | PASS | `cleanup_audit_group` is a `click.Group` instance |
| Command registration | PASS | `cleanup-audit` found in `main.commands`: install, mcp, update, install-skill, doctor, version, sprint, roadmap, cleanup-audit |
| No naming collision | PASS | `cleanup-audit` registered exactly once |

## Registered Commands After Patch

```
install, mcp, update, install-skill, doctor, version, sprint, roadmap, cleanup-audit
```

## Validation Command

```bash
uv run python -c "from superclaude.cli.main import main; assert 'cleanup-audit' in [c for c in main.commands.keys()]"
```

Result: **Exits 0**

## Risk Mitigation

- **RISK-008** (name collision): No collision with existing commands ✓
- Rollback: `git checkout -- src/superclaude/cli/main.py` ✓
