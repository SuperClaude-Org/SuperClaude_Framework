# SuperClaude Plugin Installation Guide

## 公式インストール方法（推奨）

### 前提条件

1. **ripgrep のインストール**
   ```bash
   brew install ripgrep
   ```

2. **環境変数の設定**（~/.zshrc または ~/.bashrc に追加）
   ```bash
   export USE_BUILTIN_RIPGREP=0
   ```

3. **シェルの再起動**
   ```bash
   exec $SHELL
   ```

### インストール手順

#### 方法A: ローカルマーケットプレイス経由（推奨）

1. Claude Code でマーケットプレイスを追加:
   ```
   /plugin marketplace add /Users/kazuki/github/superclaude
   ```

2. プラグインをインストール:
   ```
   /plugin install pm-agent@superclaude-local
   ```

3. Claude Code を再起動

4. 動作確認:
   ```
   /pm
   /research
   /index-repo
   ```

#### 方法B: 開発者モード（直接コピー）

**注意**: この方法は開発中のテスト用です。公式方法（方法A）の使用を推奨します。

```bash
# プロジェクトルートで実行
make reinstall-plugin-dev
```

Claude Code を再起動後、コマンドが利用可能になります。

## インストールされるコマンド

### /pm
PM Agent モードを起動。以下の機能を提供：
- 90%信頼度チェック（実装前）
- 並列実行最適化
- トークン予算管理
- エビデンスベース開発

### /research
Deep Research モード。以下の機能を提供：
- 並列Web検索（Tavily MCP）
- 公式ドキュメント優先
- ソース検証
- 信頼度付き結果

### /index-repo
リポジトリインデックス作成。以下の機能を提供：
- プロジェクト構造解析
- 94%トークン削減（58K → 3K）
- エントリポイント特定
- モジュールマップ生成

## フックの自動実行

SessionStart フックにより、新しいセッション開始時に `/pm` コマンドが自動実行されます。

無効化したい場合は、`~/.claude/plugins/pm-agent/hooks/hooks.json` を編集してください。

## トラブルシューティング

### コマンドが認識されない場合

1. **ripgrep の確認**:
   ```bash
   which rg
   rg --version
   ```

   インストールされていない場合：
   ```bash
   brew install ripgrep
   ```

2. **環境変数の確認**:
   ```bash
   echo $USE_BUILTIN_RIPGREP
   ```

   設定されていない場合：
   ```bash
   echo 'export USE_BUILTIN_RIPGREP=0' >> ~/.zshrc
   exec $SHELL
   ```

3. **プラグインの確認**:
   ```bash
   ls -la ~/.claude/plugins/pm-agent/
   ```

   存在しない場合は再インストール：
   ```bash
   make reinstall-plugin-dev
   ```

4. **Claude Code を再起動**

### それでも動かない場合

Claude Code のバージョンを確認してください。2.0.x には既知のバグがあります：
- GitHub Issue #8831: Custom slash commands not discovered

回避策：
- NPM版に切り替える（Homebrew版にバグの可能性）
- ripgrep をシステムにインストール（上記手順）

## プラグイン構造（参考）

```
~/.claude/plugins/pm-agent/
├── plugin.json          # プラグインメタデータ
├── marketplace.json     # マーケットプレイス情報
├── commands/            # Markdown コマンド
│   ├── pm.md
│   ├── research.md
│   └── index-repo.md
└── hooks/
    └── hooks.json       # SessionStart フック設定
```

## 開発者向け情報

プラグインのソースコードは `/Users/kazuki/github/superclaude/` にあります。

変更を反映するには：
```bash
make reinstall-plugin-dev
# Claude Code を再起動
```

## サポート

問題が発生した場合は、以下を確認してください：
- 公式ドキュメント: https://docs.claude.com/ja/docs/claude-code/plugins
- GitHub Issues: https://github.com/anthropics/claude-code/issues
- プロジェクトドキュメント: CLAUDE.md, PLANNING.md
