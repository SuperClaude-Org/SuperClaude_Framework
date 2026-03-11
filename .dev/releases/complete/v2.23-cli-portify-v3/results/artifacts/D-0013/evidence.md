# D-0013: Code Generation Instructions Removed

## Verification

### Phase 3/4 Sections (lines 154-251)
- `grep -n 'generate_code\|code_output\|integration_test' SKILL.md` in Phase 3/4: **0 matches**
- `grep -n 'code-templates' SKILL.md`: **0 matches**
- Phase 3 rewritten to spec synthesis (template instantiation + brainstorm)
- Phase 4 rewritten to spec panel review (convergent loop)

### Removed Content
- Old Phase 3: "Load `refs/code-templates.md`... Generate files in dependency order..."
- Old Phase 4: "Patch `main.py`... Generate structural test..."
- `--skip-integration` CLI flag removed from argument table and frontmatter
- "Code Generation Principles" header renamed to "Pipeline Design Principles"
- Boundaries updated: "Generate complete CLI subcommand module" replaced with spec synthesis language
