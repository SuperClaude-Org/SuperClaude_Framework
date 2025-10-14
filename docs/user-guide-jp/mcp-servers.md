# SuperClaude MCP サーバーガイド 🔌

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#superclaude-mcp-servers-guide-)

## 概要

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#overview)

MCP（モデルコンテキストプロトコル）サーバーは、専用ツールを通じてClaude Codeの機能を拡張します。SuperClaudeは6つのMCPサーバーを統合し、タスクに応じてサーバーをいつ起動するかをClaudeに指示します。

### 🔍 現実チェック

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#-reality-check)

- **MCPサーバーとは**: 追加ツールを提供する外部Node.jsプロセス
- **含まれていないもの**：SuperClaude 機能が組み込まれている
- **アクティベーションの仕組み**: クロードは状況に応じて適切なサーバーを使用するための指示を読み上げます
- **提供されるもの**：Claude Codeのネイティブ機能を拡張する実際のツール

**コアサーバー:**

- **context7** : 公式ライブラリドキュメントとパターン
- **段階的思考**：多段階の推論と分析
- **マジック**：モダンなUIコンポーネント生成
- **プレイライト**：ブラウザ自動化とE2Eテスト
- **morphllm-fast-apply** : パターンベースのコード変換
- **serena** : セマンティックコード理解とプロジェクトメモリ

## クイックスタート

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#quick-start)

**セットアップの確認**：MCPサーバーは自動的に起動します。インストールとトラブルシューティングについては、[「インストールガイド」](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Getting-Started/installation.md)と[「トラブルシューティング」](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Reference/troubleshooting.md)を参照してください。

**自動アクティベーションロジック:**

|リクエストに含まれるもの|アクティブ化されたサーバー|
|---|---|
|ライブラリのインポート、API名|**コンテキスト7**|
|`--think`、デバッグ|**連続思考**|
|`component`、`UI`、 フロントエンド|**魔法**|
|`test`、、`e2e`​`browser`|**劇作家**|
|複数ファイルの編集、リファクタリング|**morphllm-高速適用**|
|大規模プロジェクト、セッション|**セレナ**|

## サーバーの詳細

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#server-details)

### コンテキスト7 📚

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#context7-)

**目的**: 公式ライブラリドキュメントへのアクセス **トリガー**: インポートステートメント、フレームワークキーワード、ドキュメントリクエスト **要件**: Node.js 16+、APIキーなし

```shell
# Automatic activation
/sc:implement "React authentication system"
# → Provides official React patterns

# Manual activation  
/sc:analyze auth-system/ --c7
```

### 連続思考 🧠

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#sequential-thinking-)

**目的**: 構造化された多段階の推論と体系的な分析 **トリガー**: 複雑なデバッグ、`--think`フラグ、アーキテクチャ分析 **要件**: Node.js 16+、APIキーなし

```shell
# Automatic activation
/sc:troubleshoot "API performance issues"
# → Enables systematic root cause analysis

# Manual activation
/sc:analyze --think-hard architecture/
```

### 魔法✨

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#magic-)

**目的**: 21st.dev パターンからのモダン UI コンポーネント生成 **トリガー**: UI リクエスト、`/ui`コマンド、コンポーネント開発 **要件**: Node.js 16+、TWENTYFIRST_API_KEY()

```shell
# Automatic activation
/sc:implement "responsive dashboard component"
# → Generates accessible UI with modern patterns

# API key setup
export TWENTYFIRST_API_KEY="your_key_here"
```

### 劇作家🎭

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#playwright-)

**目的**: 実際のブラウザ自動化とE2Eテスト **トリガー**: ブラウザテスト、E2Eシナリオ、視覚的検証 **要件**: Node.js 16以上、APIキーなし

```shell
# Automatic activation
/sc:test --type e2e "user login flow"
# → Enables browser automation testing

# Manual activation
/sc:validate "accessibility compliance" --play
```

### morphllm-fast-apply 🔄

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#morphllm-fast-apply-)

**目的**: 効率的なパターンベースのコード変換 **トリガー**: 複数ファイルの編集、リファクタリング、フレームワークの移行 **要件**: Node.js 16+、MORPH_API_KEY

```shell
# Automatic activation
/sc:improve legacy-codebase/ --focus maintainability
# → Applies consistent patterns across files

# API key setup
export MORPH_API_KEY="your_key_here"
```

### セレナ🧭

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#serena-)

**目的**: プロジェクトメモリを使用したセマンティックコード理解 **トリガー**: シンボル操作、大規模コードベース、セッション管理 **要件**: Python 3.9+、UV パッケージマネージャー、API キーなし

```shell
# Automatic activation  
/sc:load existing-project/
# → Builds project understanding and memory

# Manual activation
/sc:refactor "extract UserService" --serena
```

## 構成

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#configuration)

**MCP 構成ファイル ( `~/.claude.json`):**

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "sequential-thinking": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "magic": {
      "command": "npx",
      "args": ["@21st-dev/magic"],
      "env": {"TWENTYFIRST_API_KEY": "${TWENTYFIRST_API_KEY}"}
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "morphllm-fast-apply": {
      "command": "npx",
      "args": ["@morph-llm/morph-fast-apply"],
      "env": {"MORPH_API_KEY": "${MORPH_API_KEY}"}
    },
    "serena": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--context", "ide-assistant"]
    }
  }
}
```

## 使用パターン

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#usage-patterns)

**サーバー制御:**

```shell
# Enable specific servers
/sc:analyze codebase/ --c7 --seq

# Disable all MCP servers
/sc:implement "simple function" --no-mcp

# Enable all servers
/sc:design "complex architecture" --all-mcp
```

**マルチサーバー調整:**

```shell
# Full-stack development
/sc:implement "e-commerce checkout"
# → Sequential: workflow analysis
# → Context7: payment patterns  
# → Magic: UI components
# → Serena: code organization
# → Playwright: E2E testing
```

## トラブルシューティング

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#troubleshooting)

**よくある問題:**

- **サーバーが接続されていません**: Node.js を確認してください: `node --version`(v16 以上が必要)
- **Context7 が失敗しました**: キャッシュをクリアしてください:`npm cache clean --force`
- **Magic/Morphllm エラー**: API キーがない場合に発生する可能性があります (有料サービス)
- **サーバーのタイムアウト**: Claude Codeセッションを再起動します

**クイックフィックス:**

```shell
# Reset connections
# Restart Claude Code session

# Check dependencies  
node --version  # Should show v16+

# Test without MCP
/sc:command --no-mcp

# Check configuration
ls ~/.claude.json
```

**API キーの設定:**

```shell
# For Magic server (required for UI generation)
export TWENTYFIRST_API_KEY="your_key_here"

# For Morphllm server (required for bulk transformations)
export MORPH_API_KEY="your_key_here"

# Add to shell profile for persistence
echo 'export TWENTYFIRST_API_KEY="your_key"' >> ~/.bashrc
echo 'export MORPH_API_KEY="your_key"' >> ~/.bashrc
```

**環境変数の使用法:**

- ✅ `TWENTYFIRST_API_KEY`- Magic MCP サーバー機能に必要
- ✅ `MORPH_API_KEY`- Morphllm MCP サーバー機能に必要
- ❌ ドキュメント内のその他の環境変数 - 例のみ、フレームワークでは使用されません
- 📝 どちらも有料のサービスAPIキーですが、フレームワークはそれらなしでも動作します

## サーバーの組み合わせ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#server-combinations)

**APIキーなし（無料）** :

- コンテキスト7 + シーケンシャルシンキング + 劇作家 + セレナ

**1 APIキー**:

- プロフェッショナルなUI開発に魔法を加える

**2つのAPIキー**:

- 大規模リファクタリングのために morphllm-fast-apply を追加

**一般的なワークフロー:**

- **学習**：コンテキスト7 + シーケンシャルシンキング
- **Web開発**：マジック + context7 + プレイライト
- **エンタープライズリファクタリング**：serena + morphllm + sequential-thinking
- **複雑な分析**：シーケンシャルシンキング + コンテキスト7 + セレナ

## 統合

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#integration)

**SuperClaude コマンドを使用する場合:**

- 分析コマンドは自動的にSequential + Serenaを使用します
- 実装コマンドはMagic + Context7を使用する
- テストコマンドにはPlaywright + Sequentialを使用する

**動作モードの場合:**

- ブレインストーミングモード：発見のためのシーケンシャル
- タスク管理：永続性のための Serena
- オーケストレーションモード: 最適なサーバーの選択

**パフォーマンスコントロール:**

- システム負荷に基づく自動リソース管理
- 同時実行制御: `--concurrency N`(1-15)
- 制約下での優先度ベースのサーバー選択

## 関連リソース

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md#related-resources)

**必読:**

- [コマンドガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/commands.md)- MCPサーバーをアクティブ化するコマンド
- [クイックスタートガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Getting-Started/quick-start.md)- MCP セットアップガイド

**高度な使用法:**

- [行動モード](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/modes.md)- モード-MCP調整
- [エージェントガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md)- エージェントとMCPの統合
- [セッション管理](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md)- Serena ワークフロー

**技術リファレンス:**

- [例のクックブック](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Reference/examples-cookbook.md)- MCP ワークフローパターン
- [技術アーキテクチャ](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Developer-Guide/technical-architecture.md)- 統合の詳細