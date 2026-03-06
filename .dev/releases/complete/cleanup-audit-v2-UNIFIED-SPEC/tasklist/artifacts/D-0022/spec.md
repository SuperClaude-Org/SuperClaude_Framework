# D-0022: 3-Tier Dependency Graph Builder Specification

## Evidence Tiers

| Tier | Source Method | Confidence | Example |
|------|-------------|------------|---------|
| A | AST-parsed import statement | 0.90 | `from module import Class` parsed by AST |
| B | Grep-based reference match | 0.65 | String `"module"` found in file via pattern search |
| C | Inferred relationship | 0.35 | Naming convention or directory co-location suggests dependency |

## Tier-C Safety Policy

Tier-C evidence **never promotes a file to DELETE**. Inferred relationships carry insufficient confidence for destructive actions. Tier-C edges are included in the graph for visibility but excluded from deletion decision logic.

## Graph Structure

| Component | Schema |
|-----------|--------|
| Nodes | `{file_path, file_type, profile_ref}` |
| Edges | `{source, target, tier, confidence, evidence_type}` |

Edges are directional: `source` imports/references `target`.

## Implementation

- Module: `src/superclaude/cli/audit/dependency_graph.py`
- `build_graph()`: constructs full dependency graph from Phase 2 profiles
- `query_importers()`: returns all files that import a given target, grouped by tier
- `query_exports()`: returns all files that a given source depends on
- Graph is stored as adjacency lists for efficient traversal
