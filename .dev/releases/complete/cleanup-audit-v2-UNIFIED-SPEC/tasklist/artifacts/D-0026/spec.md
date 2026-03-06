# D-0026: Dynamic Import Safety Detector Specification

## Detected Patterns

| Pattern | Language | Example |
|---------|----------|---------|
| `import(variable)` | JavaScript/TypeScript | `import(moduleName)` with non-literal argument |
| `require(variable)` | JavaScript/Node.js | `require(path.join(dir, name))` with computed path |
| `__import__()` | Python | `__import__("module_" + suffix)` |
| `importlib.import_module()` | Python | `importlib.import_module(f"plugins.{name}")` |

Only **variable/computed** arguments trigger detection. Static string literals (e.g., `import("./fixed.js")`) are handled by the standard AST import pipeline and excluded here.

## Classification Policy

Files containing dynamic imports receive:
- Action: `KEEP:monitor` (never DELETE)
- Qualifiers: `["monitor", "dynamic_import"]`

Rationale: dynamic imports create runtime dependencies invisible to static analysis. Deleting such files risks breaking lazy-loaded modules, plugin systems, or conditional feature gates.

## Implementation

- Module: `src/superclaude/cli/audit/dynamic_imports.py`
- `scan_dynamic_imports()`: detects patterns via regex over file content
- `classify_dynamic()`: applies KEEP:monitor policy and attaches qualifiers
- Each detection includes: `{file_path, line_number, pattern_type, matched_text}`
