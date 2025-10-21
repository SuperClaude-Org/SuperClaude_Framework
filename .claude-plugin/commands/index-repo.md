---
name: index-repo
description: "Create repository structure index for fast context loading (94% token reduction)"
category: optimization
complexity: simple
mcp-servers: []
personas: []
---

# Repository Indexing for Token Efficiency

**Problem**: Loading全ファイルで毎回50,000トークン消費
**Solution**: 最初だけインデックス作成、以降3,000トークンで済む (94%削減)

## Auto-Execution

**PM Mode Session Start**:
```python
index_path = Path("PROJECT_INDEX.md")
if not index_path.exists() or is_stale(index_path, days=7):
    print("🔄 Creating repository index...")
    # Execute indexing automatically
    uv run python superclaude/indexing/parallel_repository_indexer.py
```

**Manual Trigger**:
```bash
/sc:index-repo           # Full index
/sc:index-repo --quick   # Fast scan
/sc:index-repo --update  # Incremental
```

## What It Does

### Parallel Analysis (5 concurrent tasks)
1. **Code structure** (src/, lib/, superclaude/)
2. **Documentation** (docs/, *.md)
3. **Configuration** (.toml, .yaml, .json)
4. **Tests** (tests/, **tests**)
5. **Scripts** (scripts/, bin/, tools/)

### Output Files
- `PROJECT_INDEX.md` - Human-readable (3KB)
- `PROJECT_INDEX.json` - Machine-readable (10KB)
- `.superclaude/knowledge/agent_performance.json` - Learning data

## Token Efficiency

**Before** (毎セッション):
```
Read all .md files: 41,000 tokens
Read all .py files: 15,000 tokens
Glob searches: 2,000 tokens
Total: 58,000 tokens
```

**After** (インデックス使用):
```
Read PROJECT_INDEX.md: 3,000 tokens
Direct file access: 1,000 tokens
Total: 4,000 tokens

Savings: 93% (54,000 tokens)
```

## Usage in Sessions

```python
# Session start
index = read_file("PROJECT_INDEX.md")  # 3,000 tokens

# Navigation
"Where is the validator code?"
→ Index says: superclaude/validators/
→ Direct read, no glob needed

# Understanding
"What's the project structure?"
→ Index has full overview
→ No need to scan all files

# Implementation
"Add new validator"
→ Index shows: tests/validators/ exists
→ Index shows: 5 existing validators
→ Follow established pattern
```

## Execution

```bash
$ /sc:index-repo

================================================================================
🚀 Parallel Repository Indexing
================================================================================
Repository: /Users/kazuki/github/SuperClaude_Framework
Max workers: 5
================================================================================

📊 Executing parallel tasks...

  ✅ code_structure: 847ms (system-architect)
  ✅ documentation: 623ms (technical-writer)
  ✅ configuration: 234ms (devops-architect)
  ✅ tests: 512ms (quality-engineer)
  ✅ scripts: 189ms (backend-architect)

================================================================================
✅ Indexing complete in 2.41s
================================================================================

💾 Index saved to: PROJECT_INDEX.md
💾 JSON saved to: PROJECT_INDEX.json

Files: 247 | Quality: 72/100
```

## Integration with Setup

```python
# setup/components/knowledge_base.py

def install_knowledge_base():
    """Install framework knowledge"""
    # ... existing installation ...

    # Auto-create repository index
    print("\n📊 Creating repository index...")
    run_indexing()
    print("✅ Index created - 93% token savings enabled")
```

## When to Re-Index

**Auto-triggers**:
- セットアップ時 (初回のみ)
- INDEX.mdが7日以上古い
- PM Modeセッション開始時にチェック

**Manual re-index**:
- 大規模リファクタリング後 (>20 files)
- 新機能追加後 (new directories)
- 週1回 (active development)

**Skip**:
- 小規模編集 (<5 files)
- ドキュメントのみ変更
- INDEX.mdが24時間以内

## Performance

**Speed**:
- Large repo (500+ files): 3-5 min
- Medium repo (100-500 files): 1-2 min
- Small repo (<100 files): 10-30 sec

**Self-Learning**:
- Tracks agent performance
- Optimizes future runs
- Stored in `.superclaude/knowledge/`

---

**Implementation**: `superclaude/indexing/parallel_repository_indexer.py`
**Related**: `/sc:pm` (uses index), `/sc:save`, `/sc:load`
