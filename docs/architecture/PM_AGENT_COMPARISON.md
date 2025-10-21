# PM Agent: Upstream vs Clean Architecture Comparison

**Date**: 2025-10-21
**Purpose**: 本家（Upstream）と今回のクリーンアーキテクチャでのPM Agent実装の違い

---

## 🎯 概要

### Upstream (本家) - Skills型PM Agent

**場所**: `~/.claude/skills/pm/` にインストール
**形式**: Markdown skill + Python init hooks
**読み込み**: Claude Codeが起動時に全Skills読み込み

### This PR - Core型PM Agent

**場所**: `src/superclaude/pm_agent/` Pythonパッケージ
**形式**: Pure Python modules
**読み込み**: pytest実行時のみ、import必要分だけ

---

## 📂 ディレクトリ構造比較

### Upstream (本家)

```
~/.claude/
└── skills/
    └── pm/                              # PM Agent Skill
        ├── implementation.md            # ~25KB - 全ワークフロー
        ├── modules/
        │   ├── git-status.md            # ~5KB - Git状態フォーマット
        │   ├── token-counter.md         # ~8KB - トークンカウント
        │   └── pm-formatter.md          # ~10KB - ステータス出力
        └── workflows/
            └── task-management.md       # ~15KB - タスク管理

superclaude/
├── agents/
│   └── pm-agent.md                      # ~50KB - Agent定義
├── commands/
│   └── pm.md                            # ~5KB - /sc:pm command
└── core/
    └── pm_init/                         # Python init hooks
        ├── __init__.py
        ├── context_contract.py          # ~10KB - Context管理
        ├── init_hook.py                 # ~10KB - Session start
        └── reflexion_memory.py          # ~12KB - Reflexion

Total: ~150KB ≈ 35K-40K tokens
```

**特徴**:
- ✅ Skills系: Markdown中心、人間可読
- ✅ Auto-activation: セッション開始時に自動実行
- ✅ PDCA Cycle: docs/pdca/ にドキュメント蓄積
- ❌ Token heavy: 全Markdown読み込み
- ❌ Claude Code依存: Skillsシステム前提

---

### This PR (Clean Architecture)

```
src/superclaude/
└── pm_agent/                            # Python package
    ├── __init__.py                      # Package exports
    ├── confidence.py                    # ~8KB - Pre-execution
    ├── self_check.py                    # ~15KB - Post-validation
    ├── reflexion.py                     # ~12KB - Error learning
    └── token_budget.py                  # ~10KB - Budget management

tests/pm_agent/
├── test_confidence_check.py             # 18 tests
├── test_self_check_protocol.py          # 16 tests
├── test_reflexion_pattern.py            # 16 tests
└── test_token_budget.py                 # 29 tests

Total: ~45KB ≈ 10K-12K tokens (import時のみ)
```

**特徴**:
- ✅ Python-first: コードとして実装
- ✅ Lazy loading: 使う機能のみimport
- ✅ Test coverage: 79 tests完備
- ✅ Pytest integration: Fixtureで簡単利用
- ❌ Auto-activation: なし（手動or pytest）
- ❌ PDCA docs: 自動生成なし

---

## 🔄 機能比較

### 1. Session Start Protocol

#### Upstream (本家)
```yaml
Trigger: EVERY session start (自動)
Method: pm_init/init_hook.py

Actions:
  1. PARALLEL Read:
     - docs/memory/pm_context.md
     - docs/memory/last_session.md
     - docs/memory/next_actions.md
     - docs/memory/current_plan.json
  2. Confidence Check (200 tokens)
  3. Output: 🟢 [branch] | [n]M [n]D | [token]%

Token Cost: ~8K (memory files) + 200 (confidence)
```

#### This PR
```python
# 自動実行なし - 手動で呼び出し
from superclaude.pm_agent.confidence import ConfidenceChecker

checker = ConfidenceChecker()
confidence = checker.assess(context)

Token Cost: ~2K (confidence moduleのみ)
```

**差分**:
- ❌ 自動実行なし
- ✅ トークン消費 8.2K → 2K (75%削減)
- ✅ オンデマンド実行

---

### 2. Pre-Execution Confidence Check

#### Upstream (本家)
```markdown
# superclaude/agents/pm-agent.md より

Confidence Check (200 tokens):
  ❓ "全ファイル読めた？"
  ❓ "コンテキストに矛盾ない？"
  ❓ "次のアクション実行に十分な情報？"

Output: Markdown形式
Location: Agent definition内
```

#### This PR
```python
# src/superclaude/pm_agent/confidence.py

class ConfidenceChecker:
    def assess(self, context: Dict[str, Any]) -> float:
        """
        Assess confidence (0.0-1.0)

        Checks:
        1. Documentation verified? (40%)
        2. Patterns identified? (30%)
        3. Implementation clear? (30%)

        Budget: 100-200 tokens
        """
        # Python実装
        return confidence_score
```

**差分**:
- ✅ Python関数として実装
- ✅ テスト可能（18 tests）
- ✅ Pytest fixture利用可能
- ✅ 型安全
- ❌ Markdown定義なし

---

### 3. Post-Implementation Self-Check

#### Upstream (本家)
```yaml
# agents/pm-agent.md より

Self-Evaluation Checklist:
  - [ ] Did I follow architecture patterns?
  - [ ] Did I read documentation first?
  - [ ] Did I check existing implementations?
  - [ ] Are all tasks complete?
  - [ ] What mistakes did I make?
  - [ ] What did I learn?

Token Budget:
  Simple: 200 tokens
  Medium: 1,000 tokens
  Complex: 2,500 tokens

Output: docs/pdca/[feature]/check.md
```

#### This PR
```python
# src/superclaude/pm_agent/self_check.py

class SelfCheckProtocol:
    def validate(self, implementation: Dict[str, Any])
        -> Tuple[bool, List[str]]:
        """
        Four Questions Protocol:
        1. All tests pass?
        2. Requirements met?
        3. Assumptions verified?
        4. Evidence exists?

        7 Hallucination Red Flags detection

        Returns: (passed, issues)
        """
        # Python実装
```

**差分**:
- ✅ プログラマティックに実行可能
- ✅ 16 tests完備
- ✅ Hallucination detection実装
- ❌ PDCA docs自動生成なし

---

### 4. Reflexion (Error Learning)

#### Upstream (本家)
```python
# superclaude/core/pm_init/reflexion_memory.py

class ReflexionMemory:
    """
    Error learning with dual storage:
    1. Local JSONL: docs/memory/solutions_learned.jsonl
    2. Mindbase: Semantic search (if available)

    Lookup: mindbase → grep fallback
    """
```

#### This PR
```python
# src/superclaude/pm_agent/reflexion.py

class ReflexionPattern:
    """
    Same dual storage strategy:
    1. Local JSONL: docs/memory/solutions_learned.jsonl
    2. Mindbase: Semantic search (optional)

    Methods:
    - get_solution(error_info) → past solution lookup
    - record_error(error_info) → save to memory
    - get_statistics() → recurrence rate
    """
```

**差分**:
- ✅ 同じアルゴリズム
- ✅ 16 tests追加
- ✅ Mindbase optional化
- ✅ Statistics追加

---

### 5. Token Budget Management

#### Upstream (本家)
```yaml
# agents/pm-agent.md より

Token Budget (Complexity-Based):
  Simple Task (typo): 200 tokens
  Medium Task (bug): 1,000 tokens
  Complex Task (feature): 2,500 tokens

Implementation: Markdown定義のみ
Enforcement: 手動
```

#### This PR
```python
# src/superclaude/pm_agent/token_budget.py

class TokenBudgetManager:
    BUDGETS = {
        "simple": 200,
        "medium": 1000,
        "complex": 2500,
    }

    def use(self, tokens: int) -> bool:
        """Track usage"""

    @property
    def remaining(self) -> int:
        """Get remaining budget"""

    def get_recommendation(self) -> str:
        """Suggest optimization"""
```

**差分**:
- ✅ プログラム的に強制可能
- ✅ 使用量トラッキング
- ✅ 29 tests完備
- ✅ pytest fixture化

---

## 📊 トークン消費比較

### シナリオ: PM Agent利用時

| フェーズ | Upstream | This PR | 削減 |
|---------|----------|---------|------|
| **Session Start** | 8.2K tokens (auto) | 0K (manual) | -8.2K |
| **Confidence Check** | 0.2K (included) | 2K (on-demand) | +1.8K |
| **Self-Check** | 1-2.5K (depends) | 1-2.5K (same) | 0K |
| **Reflexion** | 3K (full MD) | 3K (Python) | 0K |
| **Token Budget** | 0K (manual) | 0.5K (tracking) | +0.5K |
| **Total (typical)** | **12.4K tokens** | **6K tokens** | **-6.4K (52%)** |

**Key Point**: Session start自動実行がない分、大幅削減

---

## ✅ 維持される機能

| 機能 | Upstream | This PR | Status |
|------|----------|---------|--------|
| Pre-execution confidence | ✅ | ✅ | **維持** |
| Post-implementation validation | ✅ | ✅ | **維持** |
| Error learning (Reflexion) | ✅ | ✅ | **維持** |
| Token budget allocation | ✅ | ✅ | **維持** |
| Dual storage (JSONL + Mindbase) | ✅ | ✅ | **維持** |
| Hallucination detection | ✅ | ✅ | **維持** |
| Test coverage | Partial | 79 tests | **改善** |

---

## ⚠️ 削除される機能

### 1. Auto-Activation (Session Start)

**Upstream**:
```yaml
EVERY session start:
  - Auto-read memory files
  - Auto-restore context
  - Auto-output status
```

**This PR**:
```python
# Manual activation required
from superclaude.pm_agent.confidence import ConfidenceChecker
checker = ConfidenceChecker()
```

**影響**: ユーザーが明示的に呼び出す必要あり
**代替案**: Skillsシステムで実装可能

---

### 2. PDCA Cycle Documentation

**Upstream**:
```yaml
Auto-generate:
  - docs/pdca/[feature]/plan.md
  - docs/pdca/[feature]/do.md
  - docs/pdca/[feature]/check.md
  - docs/pdca/[feature]/act.md
```

**This PR**:
```python
# なし - ユーザーが手動で記録
```

**影響**: 自動ドキュメント生成なし
**代替案**: Skillsとして実装可能

---

### 3. Task Management Workflow

**Upstream**:
```yaml
# workflows/task-management.md
- TodoWrite auto-tracking
- Progress checkpoints
- Session continuity
```

**This PR**:
```python
# TodoWriteはClaude Codeネイティブツールとして利用可能
# PM Agent特有のワークフローなし
```

**影響**: PM Agent統合ワークフローなし
**代替案**: pytest + TodoWriteで実現可能

---

## 🎯 移行パス

### ユーザーが本家PM Agentの機能を使いたい場合

**Option 1: Skillsとして併用**
```bash
# Core PM Agent (This PR) - always installed
pip install -e .

# Skills PM Agent (Upstream) - optional
superclaude install-skill pm-agent
```

**Result**:
- Pytest fixtures: `src/superclaude/pm_agent/`
- Auto-activation: `~/.claude/skills/pm/`
- **両方利用可能**

---

**Option 2: Skills完全移行**
```bash
# 本家Skills版のみ使用
superclaude install-skill pm-agent

# Pytest fixturesは使わない
```

**Result**:
- Upstream互換100%
- トークン消費は本家と同じ

---

**Option 3: Coreのみ（推奨）**
```bash
# This PRのみ
pip install -e .

# Skillsなし
```

**Result**:
- 最小トークン消費
- Pytest integration最適化
- Auto-activation なし

---

## 💡 推奨アプローチ

### プロジェクト用途別

**1. ライブラリ開発者 (pytest重視)**
→ **Option 3: Core のみ**
- Pytest fixtures活用
- テスト駆動開発
- トークン最小化

**2. Claude Code パワーユーザー (自動化重視)**
→ **Option 1: 併用**
- Auto-activation活用
- PDCA docs自動生成
- Pytest fixturesも利用

**3. 本家互換性重視**
→ **Option 2: Skills のみ**
- 100% Upstream互換
- 既存ワークフロー維持

---

## 📋 まとめ

### 主な違い

| 項目 | Upstream | This PR |
|------|----------|---------|
| **実装** | Markdown + Python hooks | Pure Python |
| **配置** | ~/.claude/skills/ | site-packages/ |
| **読み込み** | Auto (session start) | On-demand (import) |
| **トークン** | 12.4K | 6K (-52%) |
| **テスト** | Partial | 79 tests |
| **Auto-activation** | ✅ | ❌ |
| **PDCA docs** | ✅ Auto | ❌ Manual |
| **Pytest fixtures** | ❌ | ✅ |

### 互換性

**機能レベル**: 95%互換
- Core機能すべて維持
- Auto-activationとPDCA docsのみ削除

**移行難易度**: Low
- Skills併用で100%互換可能
- コード変更不要（import pathのみ）

### 推奨

**このPRを採用すべき理由**:
1. ✅ 52%トークン削減
2. ✅ 標準Python packaging
3. ✅ テストカバレッジ完備
4. ✅ 必要ならSkills併用可能

**本家Upstream維持すべき理由**:
1. ✅ Auto-activation便利
2. ✅ PDCA docs自動生成
3. ✅ Claude Code統合最適化

**ベストプラクティス**: **併用** (Option 1)
- Core (This PR): Pytest開発用
- Skills (Upstream): 日常使用のAuto-activation
- 両方のメリット享受

---

**作成日**: 2025-10-21
**ステータス**: Phase 2完了時点の比較
