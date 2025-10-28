---
name: sc:index-repo
description: Repository Indexing - 94% token reduction (58K → 3K)
---

# Repository Index Creator

📊 **Index Creator activated**

## Problem Statement

**Before**: Reading all files → 58,000 tokens every session
**After**: Read PROJECT_INDEX.md → 3,000 tokens (94% reduction)

## Index Creation Flow

### Phase 1: Analyze Repository Structure

**Parallel analysis** (5 concurrent Glob searches):

1. **Code Structure**
   ```
   src/**/*.{ts,py,js,tsx,jsx}
   lib/**/*.{ts,py,js}
   superclaude/**/*.py
   ```

2. **Documentation**
   ```
   docs/**/*.md
   *.md (root level)
   README*.md
   ```

3. **Configuration**
   ```
   *.toml
   *.yaml, *.yml
   *.json (exclude package-lock, node_modules)
   ```

4. **Tests**
   ```
   tests/**/*.{py,ts,js}
   **/*.test.{ts,py,js}
   **/*.spec.{ts,py,js}
   ```

5. **Scripts & Tools**
   ```
   scripts/**/*
   bin/**/*
   tools/**/*
   ```

### Phase 2: Extract Metadata

For each file category, extract:
- Entry points (main.py, index.ts, cli.py)
- Key modules and exports
- API surface (public functions/classes)
- Dependencies (imports, requires)

### Phase 3: Generate Index

Create `PROJECT_INDEX.md` with structure:

```markdown
# Project Index: {project_name}

Generated: {timestamp}

## 📁 Project Structure

{tree view of main directories}

## 🚀 Entry Points

- CLI: {path} - {description}
- API: {path} - {description}
- Tests: {path} - {description}

## 📦 Core Modules

### Module: {name}
- Path: {path}
- Exports: {list}
- Purpose: {1-line description}

## 🔧 Configuration

- {config_file}: {purpose}

## 📚 Documentation

- {doc_file}: {topic}

## 🧪 Test Coverage

- Unit tests: {count} files
- Integration tests: {count} files
- Coverage: {percentage}%

## 🔗 Key Dependencies

- {dependency}: {version} - {purpose}

## 📝 Quick Start

1. {setup step}
2. {run step}
3. {test step}
```

### Phase 4: Validation

Quality checks:
- [ ] All entry points identified?
- [ ] Core modules documented?
- [ ] Index size < 5KB?
- [ ] Human-readable format?

---

## Usage

**Create index**:
```
/index-repo
```

**Update existing index**:
```
/index-repo mode=update
```

**Quick index (skip tests)**:
```
/index-repo mode=quick
```

---

## Token Efficiency

**ROI Calculation**:
- Index creation: 2,000 tokens (one-time)
- Index reading: 3,000 tokens (every session)
- Full codebase read: 58,000 tokens (every session)

**Break-even**: 1 session
**10 sessions savings**: 550,000 tokens
**100 sessions savings**: 5,500,000 tokens

---

## Output Format

Creates two files:
1. `PROJECT_INDEX.md` (3KB, human-readable)
2. `PROJECT_INDEX.json` (10KB, machine-readable)

---

**Index Creator is now active.** Run to analyze current repository.
