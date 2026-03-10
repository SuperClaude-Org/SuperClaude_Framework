# File Status Analysis: v.1.4-roadmap-gen Directory

**Analysis Date**: 2026-01-26
**Purpose**: Classify files as OUTDATED (IBOpenCode-specific) vs CURRENT (SuperClaude-applicable)

---

## Executive Summary

| Category | Count | Action |
|----------|-------|--------|
| 🔴 OUTDATED (Archive) | 11 | Move to `archive/ibopencode-source/` |
| 🟢 CURRENT (Keep) | 5 | These are SuperClaude-applicable |
| 📁 TOTAL | 16 files + 1 directory | |

---

## File Classification

### 🔴 OUTDATED FILES (IBOpenCode-Specific) — Archive These

These files are 100% IBOpenCode-specific and will cause confusion if kept alongside SuperClaude work.

| File | Evidence | Recommendation |
|------|----------|----------------|
| `v3.0_Roadmap-Generator-Specification.md` | References `/rf:roadmap-gen`, `.opencode/command/`, `gpt-5.2`, crossLLM | **ARCHIVE** |
| `Roadmap-Generator-Prompt.md` | 9-phase pipeline, `.roadmaps/[version]/` IBOpenCode structure | **ARCHIVE** |
| `roadmap.md` | References `/rf:roadmap-gen`, `.opencode/agent/`, IBOpenCode paths | **ARCHIVE** |
| `test-strategy.md` | References `.dev/tests/`, `.dev/fixtures/`, crossLLM mocks | **ARCHIVE** |
| `execution-prompt.md` | References `<project-root>/`, `.opencode/` paths | **ARCHIVE** |
| `extraction.md` | REQ IDs tied to IBOpenCode `/rf:roadmap-gen` command | **ARCHIVE** |
| `Roadmap-Generator-analysis.md` | Analysis of `rf:crossLLM` command (IBOpenCode-specific) | **ARCHIVE** |
| `tasklists/M1-foundation.md` | IBOpenCode paths, `.opencode/command/`, agent specs | **ARCHIVE** |
| `tasklists/M2-template-system.md` | `.opencode/resources/templates/` paths | **ARCHIVE** |
| `tasklists/M3-core-generation.md` | IBOpenCode orchestrator references | **ARCHIVE** |
| `tasklists/M4-crossllm-integration.md` | `/rf:crossLLM` command integration | **ARCHIVE** |
| `tasklists/M5-enhancements.md` | IBOpenCode enhancement flags | **ARCHIVE** |
| `tasklists/M6-documentation.md` | IBOpenCode documentation paths | **ARCHIVE** |

**Total Outdated**: 13 files (including 6 tasklist files)

---

### 🟢 CURRENT FILES (SuperClaude-Applicable) — Keep These

These files were created during the translation work and apply directly to SuperClaude/Claude Code.

| File | Purpose | Status |
|------|---------|--------|
| `analysis-opencode-specific.md` | Documents OpenCode CLI features needing translation | ✅ KEEP - Reference |
| `analysis-ibopencode-framework-specific.md` | Documents IBOpenCode Framework features needing translation | ✅ KEEP - Reference |
| `claude-code-proposals-opencode.md` | 10 translation proposals for OpenCode features | ✅ KEEP - Blueprint |
| `claude-code-proposals-framework.md` | 11 translation proposals for Framework features | ✅ KEEP - Blueprint |
| `workflow-superclaude-refactoring.md` | Comprehensive refactoring workflow plan | ✅ KEEP - Execution Guide |

**Total Current**: 5 files

---

## Recommended Directory Structure After Cleanup

```
.roadmaps/v.1.4-roadmap-gen/
├── archive/                                    # NEW - Archive outdated files
│   └── ibopencode-source/                     # Original IBOpenCode files
│       ├── v3.0_Roadmap-Generator-Specification.md
│       ├── Roadmap-Generator-Prompt.md
│       ├── roadmap.md
│       ├── test-strategy.md
│       ├── execution-prompt.md
│       ├── extraction.md
│       ├── Roadmap-Generator-analysis.md
│       └── tasklists/
│           ├── M1-foundation.md
│           ├── M2-template-system.md
│           ├── M3-core-generation.md
│           ├── M4-crossllm-integration.md
│           ├── M5-enhancements.md
│           └── M6-documentation.md
│
├── analysis-opencode-specific.md              # KEEP - Analysis reference
├── analysis-ibopencode-framework-specific.md  # KEEP - Analysis reference
├── claude-code-proposals-opencode.md          # KEEP - Translation proposals
├── claude-code-proposals-framework.md         # KEEP - Translation proposals
├── workflow-superclaude-refactoring.md        # KEEP - Execution guide
└── FILE-STATUS-ANALYSIS.md                    # THIS FILE - Status tracking
```

---

## Action Items

### Option A: Archive (Recommended)
Preserves original source material for reference while clearly separating it from active SuperClaude work.

```bash
# Execute from .roadmaps/v.1.4-roadmap-gen/
mkdir -p archive/ibopencode-source/tasklists

# Move outdated files
mv v3.0_Roadmap-Generator-Specification.md archive/ibopencode-source/
mv Roadmap-Generator-Prompt.md archive/ibopencode-source/
mv roadmap.md archive/ibopencode-source/
mv test-strategy.md archive/ibopencode-source/
mv execution-prompt.md archive/ibopencode-source/
mv extraction.md archive/ibopencode-source/
mv Roadmap-Generator-analysis.md archive/ibopencode-source/

# Move tasklists
mv tasklists/* archive/ibopencode-source/tasklists/
rmdir tasklists
```

### Option B: Delete
If original IBOpenCode files are not needed for reference:

```bash
# Execute from .roadmaps/v.1.4-roadmap-gen/
rm v3.0_Roadmap-Generator-Specification.md
rm Roadmap-Generator-Prompt.md
rm roadmap.md
rm test-strategy.md
rm execution-prompt.md
rm extraction.md
rm Roadmap-Generator-analysis.md
rm -rf tasklists/
```

---

## Classification Criteria Used

### IBOpenCode Indicators (→ OUTDATED)
- References to `/rf:` command prefix
- Paths containing `.opencode/`
- References to `crossLLM` command
- Model specifications (`gpt-5.2`, `claude-sonnet-4-5`)
- Temperature values (`temperature: 0.1`)
- `.dev/` directory structure
- Agent naming pattern `@rf-*`

### SuperClaude Indicators (→ CURRENT)
- References to `/sc:` command prefix
- Paths containing `.claude/skills/`
- References to `plugins/superclaude/`
- Wave orchestration terminology
- Compliance tier system references
- PERSONAS.md confidence thresholds
- Task tool delegation patterns

---

## Verification Checklist

After cleanup, verify:
- [ ] All 5 SuperClaude-applicable files remain in main directory
- [ ] All 13 IBOpenCode files are archived/deleted
- [ ] No broken references in kept files
- [ ] `workflow-superclaude-refactoring.md` can stand alone as execution guide

---

*Generated by /sc:analyze on 2026-01-26*
