# D-0016: Manifest Completeness Gate Specification

## Module
`src/superclaude/cli/audit/manifest_gate.py`

## Gate Rules
- Default threshold: 95% of eligible files must be profiled
- Eligible = all files minus excluded (binary, vendor, cache)
- Gate blocks analysis start if coverage < threshold
- Missing files logged for diagnosis

## Excluded Patterns
Directories: `.git/`, `node_modules/`, `vendor/`, `__pycache__/`, `.venv/`, `dist/`, `build/`
Extensions: `.pyc`, `.so`, `.png`, `.jpg`, `.zip`, `.pdf`, etc.

## Result Schema
```json
{
  "passed": true,
  "coverage": 0.97,
  "threshold": 0.95,
  "total_eligible": 100,
  "total_profiled": 97,
  "missing_count": 3,
  "missing_files": ["a.py", "b.py", "c.py"]
}
```
