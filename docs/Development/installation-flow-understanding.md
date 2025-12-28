# SuperClaude Installation Flow - Complete Understanding

> **学習内容**: インストーラーがどうやって `~/.claude/` にファイルを配置するかの完全理解

---

## 🔄 インストールフロー全体像

### ユーザー操作
```bash
# Step 1: パッケージインストール
pipx install SuperClaude
# または
npm install -g @bifrost_inc/superclaude

# Step 2: セットアップ実行
SuperClaude install
```

### 内部処理の流れ

```yaml
1. Entry Point:
   File: superclaude/__main__.py → main()

2. CLI Parser:
   File: superclaude/__main__.py → create_parser()
   Command: "install" サブコマンド登録

3. Component Manager:
   File: setup/cli/install.py
   Role: インストールコンポーネントの調整

4. Commands Component:
   File: setup/components/commands.py → CommandsComponent
   Role: スラッシュコマンドのインストール

5. Source Files:
   Location: superclaude/commands/*.md
   Content: pm.md, implement.md, test.md, etc.

6. Destination:
   Location: ~/.claude/commands/sc/*.md
   Result: ユーザー環境に配置
```

---

## 📁 CommandsComponent の詳細

### クラス構造
```python
class CommandsComponent(Component):
    """
    Role: スラッシュコマンドのインストール・管理
    Parent: setup/core/base.py → Component
    Install Path: ~/.claude/commands/sc/
    """
```

### 主要メソッド

#### 1. `__init__()`
```python
def __init__(self, install_dir: Optional[Path] = None):
    super().__init__(install_dir, Path("commands/sc"))
```
**理解**:
- `install_dir`: `~/.claude/` （ユーザー環境）
- `Path("commands/sc")`: サブディレクトリ指定
- 結果: `~/.claude/commands/sc/` にインストール

#### 2. `_get_source_dir()`
```python
def _get_source_dir(self) -> Path:
    # setup/components/commands.py の位置から計算
    project_root = Path(__file__).parent.parent.parent
    # → ~/github/SuperClaude_Framework/

    return project_root / "superclaude" / "commands"
    # → ~/github/SuperClaude_Framework/superclaude/commands/
```

**理解**:
```
Source: ~/github/SuperClaude_Framework/superclaude/commands/*.md
Target: ~/.claude/commands/sc/*.md

つまり:
superclaude/commands/pm.md
  ↓ コピー
~/.claude/commands/sc/pm.md
```

#### 3. `_install()` - インストール実行
```python
def _install(self, config: Dict[str, Any]) -> bool:
    self.logger.info("Installing SuperClaude command definitions...")

    # 既存コマンドのマイグレーション
    self._migrate_existing_commands()

    # 親クラスのインストール実行
    return super()._install(config)
```

**理解**:
1. ログ出力
2. 旧バージョンからの移行処理
3. 実際のファイルコピー（親クラスで実行）

#### 4. `_migrate_existing_commands()` - マイグレーション
```python
def _migrate_existing_commands(self) -> None:
    """
    旧Location: ~/.claude/commands/*.md
    新Location: ~/.claude/commands/sc/*.md

    V3 → V4 移行時の処理
    """
    old_commands_dir = self.install_dir / "commands"
    new_commands_dir = self.install_dir / "commands" / "sc"

    # 旧場所からファイル検出
    # 新場所へコピー
    # 旧場所から削除
```

**理解**:
- V3: `/analyze` → V4: `/sc:analyze`
- 名前空間衝突を防ぐため `/sc:` プレフィックス

#### 5. `_post_install()` - メタデータ更新
```python
def _post_install(self) -> bool:
    # メタデータ更新
    metadata_mods = self.get_metadata_modifications()
    self.settings_manager.update_metadata(metadata_mods)

    # コンポーネント登録
    self.settings_manager.add_component_registration(
        "commands",
        {
            "version": __version__,
            "category": "commands",
            "files_count": len(self.component_files),
        },
    )
```

**理解**:
- `~/.claude/.superclaude.json` 更新
- インストール済みコンポーネント記録
- バージョン管理

---

## 📋 実際のファイルマッピング

### Source（このプロジェクト）
```
~/github/SuperClaude_Framework/superclaude/commands/
├── pm.md                  # PM Agent定義
├── implement.md           # Implement コマンド
├── test.md                # Test コマンド
├── analyze.md             # Analyze コマンド
├── research.md            # Research コマンド
├── ...（全26コマンド）
```

### Destination（ユーザー環境）
```
~/.claude/commands/sc/
├── pm.md                  # → /sc:pm で実行可能
├── implement.md           # → /sc:implement で実行可能
├── test.md                # → /sc:test で実行可能
├── analyze.md             # → /sc:analyze で実行可能
├── research.md            # → /sc:research で実行可能
├── ...（全26コマンド）
```

### Claude Code動作
```
User: /sc:pm "Build authentication"

Claude Code:
  1. ~/.claude/commands/sc/pm.md 読み込み
  2. YAML frontmatter 解析
  3. Markdown本文を展開
  4. PM Agent として実行
```

---

## 🔧 他のコンポーネント

### Modes Component
```python
File: setup/components/modes.py
Source: superclaude/modes/*.md
Target: ~/.claude/*.md

Example:
  superclaude/modes/MODE_Brainstorming.md
    ↓
  ~/.claude/MODE_Brainstorming.md
```

### Agents Component
```python
File: setup/components/agents.py
Source: superclaude/agents/*.md
Target: ~/.claude/agents/*.md（または統合先）
```

### Core Component
```python
File: setup/components/core.py
Source: superclaude/core/CLAUDE.md
Target: ~/.claude/CLAUDE.md

これがグローバル設定！
```

---

## 💡 開発時の注意点

### ✅ 正しい変更方法
```bash
# 1. ソースファイルを変更（Git管理）
cd ~/github/SuperClaude_Framework
vim superclaude/commands/pm.md

# 2. テスト追加
Write tests/test_pm_command.py

# 3. テスト実行
pytest tests/test_pm_command.py -v

# 4. コミット
git add superclaude/commands/pm.md tests/
git commit -m "feat: enhance PM command"

# 5. 開発版インストール
pip install -e .
# または
SuperClaude install --dev

# 6. 動作確認
claude
/sc:pm "test"
```

### ❌ 間違った変更方法
```bash
# ダメ！Git管理外を直接変更
vim ~/.claude/commands/sc/pm.md

# 変更は次回インストール時に上書きされる
SuperClaude install  # ← 変更が消える！
```

---

## 🎯 PM Mode改善の正しいフロー

### Phase 1: 理解（今ここ！）
```bash
✅ setup/components/commands.py 理解完了
✅ superclaude/commands/*.md の存在確認完了
✅ インストールフロー理解完了
```

### Phase 2: 現在の仕様確認
```bash
# ソース確認（Git管理）
Read superclaude/commands/pm.md

# インストール後確認（参考用）
Read ~/.claude/commands/sc/pm.md

# 「なるほど、こういう仕様になってるのか」
```

### Phase 3: 改善案作成
```bash
# このプロジェクト内で（Git管理）
Write docs/Development/hypothesis-pm-enhancement-2025-10-14.md

内容:
- 現状の問題（ドキュメント寄りすぎ、PMO機能不足）
- 改善案（自律的PDCA、自己評価）
- 実装方針
- 期待される効果
```

### Phase 4: 実装
```bash
# ソースファイル修正
Edit superclaude/commands/pm.md

変更例:
- PDCA自動実行の強化
- docs/ ディレクトリ活用の明示
- 自己評価ステップの追加
- エラー時再学習フローの追加
```

### Phase 5: テスト・検証
```bash
# テスト追加
Write tests/test_pm_enhanced.py

# テスト実行
pytest tests/test_pm_enhanced.py -v

# 開発版インストール
SuperClaude install --dev

# 実際に使ってみる
claude
/sc:pm "test enhanced workflow"
```

### Phase 6: 学習記録
```bash
# 成功パターン記録
Write docs/patterns/pm-autonomous-workflow.md

# 失敗があれば記録
Write docs/mistakes/mistake-2025-10-14.md
```

---

## 📊 Component間の依存関係

```yaml
Commands Component:
  depends_on: ["core"]

Core Component:
  provides:
    - ~/.claude/CLAUDE.md（グローバル設定）
    - 基本ディレクトリ構造

Modes Component:
  depends_on: ["core"]
  provides:
    - ~/.claude/MODE_*.md

Agents Component:
  depends_on: ["core"]
  provides:
    - エージェント定義

MCP Component:
  depends_on: ["core"]
  provides:
    - MCPサーバー設定
```

---

## 🚀 次のアクション

理解完了！次は：

1. ✅ `superclaude/commands/pm.md` の現在の仕様確認
2. ✅ 改善提案ドキュメント作成
3. ✅ 実装修正（PDCA強化、PMO機能追加）
4. ✅ テスト追加・実行
5. ✅ 動作確認
6. ✅ 学習記録

このドキュメント自体が**インストールフローの完全理解記録**として機能する。
次回のセッションで読めば、同じ説明を繰り返さなくて済む。
