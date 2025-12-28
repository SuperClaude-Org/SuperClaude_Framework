# OSS Fork Workflow Best Practices 2025

**Research Date**: 2025-10-16
**Context**: 2-tier fork structure (OSS upstream → personal fork)
**Goal**: Clean PR workflow maintaining sync with zero garbage commits

---

## 🎯 Executive Summary

2025年のOSS貢献における標準フォークワークフローは、**個人フォークのmainブランチを絶対に汚さない**ことが大原則。upstream同期にはmergeではなく**rebase**を使用し、PR前には**rebase -i**でコミット履歴を整理することで、クリーンな差分のみを提出する。

**推奨ブランチ戦略**:
```
master (or main): upstream mirror（同期専用、直接コミット禁止）
feature/*: 機能開発ブランチ（upstream/masterから派生）
```

**"dev"ブランチは不要** - 役割が曖昧で混乱の原因となる。

---

## 📚 Current Structure

```
upstream: SuperClaude-Org/SuperClaude_Framework ← OSS本家
  ↓ (fork)
origin: kazukinakai/SuperClaude_Framework ← 個人フォーク
```

**Current Branches**:
- `master`: upstream追跡用
- `dev`: 作業ブランチ（❌ 役割不明確）
- `feature/*`: 機能ブランチ

---

## ✅ Recommended Workflow (2025 Standard)

### Phase 1: Initial Setup (一度だけ)

```bash
# 1. Fork on GitHub UI
# SuperClaude-Org/SuperClaude_Framework → kazukinakai/SuperClaude_Framework

# 2. Clone personal fork
git clone https://github.com/kazukinakai/SuperClaude_Framework.git
cd SuperClaude_Framework

# 3. Add upstream remote
git remote add upstream https://github.com/SuperClaude-Org/SuperClaude_Framework.git

# 4. Verify remotes
git remote -v
# origin    https://github.com/kazukinakai/SuperClaude_Framework.git (fetch/push)
# upstream  https://github.com/SuperClaude-Org/SuperClaude_Framework.git (fetch/push)
```

### Phase 2: Daily Workflow

#### Step 1: Sync with Upstream

```bash
# Fetch latest from upstream
git fetch upstream

# Update local master (fast-forward only, no merge commits)
git checkout master
git merge upstream/master --ff-only

# Push to personal fork (keep origin/master in sync)
git push origin master
```

**重要**: `--ff-only`を使うことで、意図しないマージコミットを防ぐ。

#### Step 2: Create Feature Branch

```bash
# Create feature branch from latest upstream/master
git checkout -b feature/pm-agent-redesign master

# Alternative: checkout from upstream/master directly
git checkout -b feature/clean-docs upstream/master
```

**命名規則**:
- `feature/xxx`: 新機能
- `fix/xxx`: バグ修正
- `docs/xxx`: ドキュメント
- `refactor/xxx`: リファクタリング

#### Step 3: Development

```bash
# Make changes
# ... edit files ...

# Commit (atomic commits: 1 commit = 1 logical change)
git add .
git commit -m "feat: add PM Agent session persistence"

# Continue development with multiple commits
git commit -m "refactor: extract memory logic to separate module"
git commit -m "test: add unit tests for memory operations"
git commit -m "docs: update PM Agent documentation"
```

**Atomic Commits**:
- 1コミット = 1つの論理的変更
- コミットメッセージは具体的に（"fix typo"ではなく"fix: correct variable name in auth.js:45"）

#### Step 4: Clean Up Before PR

```bash
# Interactive rebase to clean commit history
git rebase -i master

# Rebase editor opens:
# pick abc1234 feat: add PM Agent session persistence
# squash def5678 refactor: extract memory logic to separate module
# squash ghi9012 test: add unit tests for memory operations
# pick jkl3456 docs: update PM Agent documentation

# Result: 2 clean commits instead of 4
```

**Rebase Operations**:
- `pick`: コミットを残す
- `squash`: 前のコミットに統合
- `reword`: コミットメッセージを変更
- `drop`: コミットを削除

#### Step 5: Verify Clean Diff

```bash
# Check what will be in the PR
git diff master...feature/pm-agent-redesign --name-status

# Review actual changes
git diff master...feature/pm-agent-redesign

# Ensure ONLY your intended changes are included
# No garbage commits, no disabled code, no temporary files
```

#### Step 6: Push and Create PR

```bash
# Push to personal fork
git push origin feature/pm-agent-redesign

# Create PR using GitHub CLI
gh pr create --repo SuperClaude-Org/SuperClaude_Framework \
  --title "feat: PM Agent session persistence with local memory" \
  --body "$(cat <<'EOF'
## Summary
- Implements session persistence for PM Agent
- Uses local file-based memory (no external MCP dependencies)
- Includes comprehensive test coverage

## Test Plan
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual verification complete

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### Phase 3: Handle PR Feedback

```bash
# Make requested changes
# ... edit files ...

# Commit changes
git add .
git commit -m "fix: address review comments - improve error handling"

# Clean up again if needed
git rebase -i master

# Force push (safe because it's your feature branch)
git push origin feature/pm-agent-redesign --force-with-lease
```

**Important**: `--force-with-lease`は`--force`より安全（リモートに他人のコミットがある場合は失敗する）

---

## 🚫 Anti-Patterns to Avoid

### ❌ Never Commit to master/main

```bash
# WRONG
git checkout master
git commit -m "quick fix"  # ← これをやると同期が壊れる

# CORRECT
git checkout -b fix/typo master
git commit -m "fix: correct typo in README"
```

### ❌ Never Merge When You Should Rebase

```bash
# WRONG (creates unnecessary merge commits)
git checkout feature/xxx
git merge master  # ← マージコミットが生成される

# CORRECT (keeps history linear)
git checkout feature/xxx
git rebase master  # ← 履歴が一直線になる
```

### ❌ Never Rebase Public Branches

```bash
# WRONG (if others are using this branch)
git checkout shared-feature
git rebase master  # ← 他人の作業を壊す

# CORRECT
git checkout shared-feature
git merge master  # ← 安全にマージ
```

### ❌ Never Include Unrelated Changes in PR

```bash
# Check before creating PR
git diff master...feature/xxx

# If you see unrelated changes:
# - Stash or commit them separately
# - Create a new branch from clean master
# - Cherry-pick only relevant commits
git checkout -b feature/xxx-clean master
git cherry-pick <commit-hash>
```

---

## 🔧 "dev" Branch Problem & Solution

### 問題: "dev"ブランチの役割が曖昧

```
❌ Current (Confusing):
master ← upstream同期
dev ← 作業場？統合？staging？（不明確）
feature/* ← 機能開発

問題:
1. devから派生すべきか、masterから派生すべきか不明
2. devをいつupstream/masterに同期すべきか不明
3. PRのbaseはmaster？dev？（混乱）
```

### 解決策 Option 1: "dev"を廃止（推奨）

```bash
# Delete dev branch
git branch -d dev
git push origin --delete dev

# Use clean workflow:
master ← upstream同期専用（直接コミット禁止）
feature/* ← upstream/masterから派生

# Example:
git fetch upstream
git checkout master
git merge upstream/master --ff-only
git checkout -b feature/new-feature master
```

**利点**:
- シンプルで迷わない
- upstream同期が明確
- PRのbaseが常にmaster（一貫性）

### 解決策 Option 2: "dev" → "integration"にリネーム

```bash
# Rename for clarity
git branch -m dev integration
git push origin -u integration
git push origin --delete dev

# Use as integration testing branch:
master ← upstream同期専用
integration ← 複数featureの統合テスト
feature/* ← upstream/masterから派生

# Workflow:
git checkout -b feature/xxx master  # masterから派生
# ... develop ...
git checkout integration
git merge feature/xxx  # 統合テスト用にマージ
# テスト完了後、masterからPR作成
```

**利点**:
- 統合テスト用ブランチとして明確な役割
- 複数機能の組み合わせテストが可能

**欠点**:
- 個人開発では通常不要（OSSでは使わない）

### 推奨: Option 1（"dev"廃止）

理由:
- OSSコントリビューションでは"dev"は標準ではない
- シンプルな方が混乱しない
- upstream/master → feature/* → PR が最も一般的

---

## 📊 Branch Strategy Comparison

| Strategy | master/main | dev/integration | feature/* | Use Case |
|----------|-------------|-----------------|-----------|----------|
| **Simple (推奨)** | upstream mirror | なし | from master | OSS contribution |
| **Integration** | upstream mirror | 統合テスト | from master | 複数機能の組み合わせテスト |
| **Confused (❌)** | upstream mirror | 役割不明 | from dev? | 混乱の元 |

---

## 🎯 Recommended Actions for Your Repo

### Immediate Actions

```bash
# 1. Check current state
git branch -vv
git remote -v
git status

# 2. Sync master with upstream
git fetch upstream
git checkout master
git merge upstream/master --ff-only
git push origin master

# 3. Option A: Delete "dev" (推奨)
git branch -d dev  # ローカル削除
git push origin --delete dev  # リモート削除

# 3. Option B: Rename "dev" → "integration"
git branch -m dev integration
git push origin -u integration
git push origin --delete dev

# 4. Create feature branch from clean master
git checkout -b feature/your-feature master
```

### Long-term Workflow

```bash
# Daily routine:
git fetch upstream && git checkout master && git merge upstream/master --ff-only && git push origin master

# Start new feature:
git checkout -b feature/xxx master

# Before PR:
git rebase -i master
git diff master...feature/xxx  # verify clean diff
git push origin feature/xxx
gh pr create --repo SuperClaude-Org/SuperClaude_Framework
```

---

## 📖 References

### Official Documentation
- [GitHub: Syncing a Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork)
- [Atlassian: Merging vs. Rebasing](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
- [Atlassian: Forking Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow)

### 2025 Best Practices
- [DataCamp: Git Merge vs Rebase (June 2025)](https://www.datacamp.com/blog/git-merge-vs-git-rebase)
- [Mergify: Rebase vs Merge Tips (April 2025)](https://articles.mergify.com/rebase-git-vs-merge/)
- [Zapier: Git Rebase vs Merge (May 2025)](https://zapier.com/blog/git-rebase-vs-merge/)

### Community Resources
- [GitHub Gist: Standard Fork & Pull Request Workflow](https://gist.github.com/Chaser324/ce0505fbed06b947d962)
- [Medium: Git Fork Development Workflow](https://medium.com/@abhijit838/git-fork-development-workflow-and-best-practices-fb5b3573ab74)
- [Stack Overflow: Keeping Fork in Sync](https://stackoverflow.com/questions/55501551/what-is-the-standard-way-of-keeping-a-fork-in-sync-with-upstream-on-collaborativ)

---

## 💡 Key Takeaways

1. **Never commit to master/main** - upstream同期専用として扱う
2. **Rebase, not merge** - upstream同期とPR前クリーンアップにrebase使用
3. **Atomic commits** - 1コミット1機能を心がける
4. **Clean before PR** - `git rebase -i`で履歴整理
5. **Verify diff** - `git diff master...feature/xxx`で差分確認
6. **"dev" is confusing** - 役割不明確なブランチは廃止または明確化

**Golden Rule**: upstream/master → feature/* → rebase -i → PR
これが2025年のOSS貢献における標準ワークフロー。
