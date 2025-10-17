# Files Moved

The files in `superclaude/core/` have been reorganized into domain-specific directories:

## New Structure

### Framework (思想・行動規範・グローバルフラグ)
- `PRINCIPLES.md` → `superclaude/framework/principles.md`
- `RULES.md` → `superclaude/framework/rules.md`
- `FLAGS.md` → `superclaude/framework/flags.md`

### Business (ビジネス領域の共通リソース)
- `BUSINESS_SYMBOLS.md` → `superclaude/business/symbols.md`
- `BUSINESS_PANEL_EXAMPLES.md` → `superclaude/business/examples.md`

### Research (調査・評価・設定)
- `RESEARCH_CONFIG.md` → `superclaude/research/config.md`

## Rationale

The `core/` directory was too abstract and made it difficult to find specific documentation. The new structure provides:

- **Clear domain boundaries**: Easier to navigate and maintain
- **Scalability**: Easy to add new directories (e.g., `benchmarks/`, `policies/`)
- **Lowercase naming**: Consistent with modern documentation practices

## Migration

All internal references have been updated. External references should update to the new paths.

This directory will be removed in the next major release.
