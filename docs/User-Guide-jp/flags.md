# SuperClaude フラグガイド 🏁

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#superclaude-flags-guide-)

**ほとんどのフラグは自動的にアクティブになります**。Claude Code は、リクエスト内のキーワードとパターンに基づいて適切なコンテキストを実行するための動作指示を読み取ります。

## 必須の自動アクティベーションフラグ（ユースケースの90%）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#essential-auto-activation-flags-90-of-use-cases)

### コア分析フラグ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#core-analysis-flags)

|フラグ|起動時|何をするのか|
|---|---|---|
|`--think`|5つ以上のファイルまたは複雑な分析|標準的な構造化分析（約4Kトークン）|
|`--think-hard`|アーキテクチャ分析、システム依存関係|強化されたツールによる詳細な分析（約1万トークン）|
|`--ultrathink`|重要なシステムの再設計、レガシーシステムの近代化|すべてのツールで最大深度分析（約32Kトークン）|

### MCP サーバーフラグ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#mcp-server-flags)

|フラグ|サーバ|目的|自動トリガー|
|---|---|---|---|
|`--c7`/`--context7`|コンテキスト7|公式ドキュメント、フレームワークパターン|ライブラリのインポート、フレームワークに関する質問|
|`--seq`/`--sequential`|一連|多段階推論、デバッグ|複雑なデバッグ、システム設計|
|`--magic`|魔法|UIコンポーネント生成|`/ui`コマンド、フロントエンドキーワード|
|`--play`/`--playwright`|劇作家|ブラウザテスト、E2E検証|テスト要求、視覚的検証|
|`--morph`/`--morphllm`|モルフィム|一括変換、パターン編集|一括操作、スタイルの強制|
|`--serena`|セレナ|プロジェクトメモリ、シンボル操作|シンボル操作、大規模なコードベース|

### 動作モードフラグ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#behavioral-mode-flags)

|フラグ|起動時|何をするのか|
|---|---|---|
|`--brainstorm`|漠然とした要望、探索キーワード|共同発見のマインドセット|
|`--introspect`|自己分析、エラー回復|推論プロセスを透明性を持って公開する|
|`--task-manage`|>3ステップ、複雑なスコープ|委任を通じて調整する|
|`--orchestrate`|マルチツール操作、パフォーマンスニーズ|ツールの選択と並列実行の最適化|
|`--token-efficient`/`--uc`|コンテキスト >75%、効率性のニーズ|シンボル強化通信、30～50%削減|

### 実行制御フラグ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#execution-control-flags)

|フラグ|起動時|何をするのか|
|---|---|---|
|`--loop`|「改善する」「磨く」「洗練する」というキーワード|反復的な強化サイクル|
|`--safe-mode`|生産、リソース使用率85%以上|最大限の検証、慎重な実行|
|`--validate`|リスク >0.7、本番環境|実行前のリスク評価|
|`--delegate`|>7 ディレクトリまたは >50 ファイル|サブエージェント並列処理|

## コマンド固有のフラグ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#command-specific-flags)

### 分析コマンドフラグ（`/sc:analyze`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#analysis-command-flags-scanalyze)

|フラグ|目的|価値観|
|---|---|---|
|`--focus`|特定のドメインをターゲットとする|`security`、、、、`performance`​`quality`​`architecture`|
|`--depth`|分析の徹底性|`quick`、`deep`|
|`--format`|出力形式|`text`、、`json`​`report`|

### ビルドコマンドフラグ（`/sc:build`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#build-command-flags-scbuild)

|フラグ|目的|価値観|
|---|---|---|
|`--type`|ビルド構成|`dev`、、`prod`​`test`|
|`--clean`|ビルド前にクリーンアップ|ブール値|
|`--optimize`|最適化を有効にする|ブール値|
|`--verbose`|詳細な出力|ブール値|

### 設計コマンドフラグ（`/sc:design`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#design-command-flags-scdesign)

|フラグ|目的|価値観|
|---|---|---|
|`--type`|設計目標|`architecture`、、、、`api`​`component`​`database`|
|`--format`|出力形式|`diagram`、、`spec`​`code`|

### コマンドフラグの説明（`/sc:explain`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#explain-command-flags-scexplain)

|フラグ|目的|価値観|
|---|---|---|
|`--level`|複雑さのレベル|`basic`、、`intermediate`​`advanced`|
|`--format`|説明スタイル|`text`、、`examples`​`interactive`|
|`--context`|ドメインコンテキスト|任意のドメイン（例：`react`、`security`）|

### コマンドフラグの改善（`/sc:improve`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#improve-command-flags-scimprove)

|フラグ|目的|価値観|
|---|---|---|
|`--type`|改善の焦点|`quality`、、、、、`performance`​`maintainability`​`style`​`security`|
|`--safe`|保守的なアプローチ|ブール値|
|`--interactive`|ユーザーガイダンス|ブール値|
|`--preview`|実行せずに表示する|ブール値|

### タスクコマンドフラグ（`/sc:task`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#task-command-flags-sctask)

|フラグ|目的|価値観|
|---|---|---|
|`--strategy`|タスクアプローチ|`systematic`、、`agile`​`enterprise`|
|`--parallel`|並列実行|ブール値|
|`--delegate`|サブエージェントの調整|ブール値|

### ワークフローコマンドフラグ（`/sc:workflow`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#workflow-command-flags-scworkflow)

|フラグ|目的|価値観|
|---|---|---|
|`--strategy`|ワークフローアプローチ|`systematic`、、`agile`​`enterprise`|
|`--depth`|分析の深さ|`shallow`、、`normal`​`deep`|
|`--parallel`|並列調整|ブール値|

### コマンドフラグのトラブルシューティング ( `/sc:troubleshoot`)

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#troubleshoot-command-flags-sctroubleshoot)

|フラグ|目的|価値観|
|---|---|---|
|`--type`|問題カテゴリ|`bug`、、、、`build`​`performance`​`deployment`|
|`--trace`|トレース分析を含める|ブール値|
|`--fix`|修正を適用する|ブール値|

### クリーンアップコマンドフラグ（`/sc:cleanup`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#cleanup-command-flags-sccleanup)

|フラグ|目的|価値観|
|---|---|---|
|`--type`|クリーンアップ対象|`code`、、、、`imports`​`files`​`all`|
|`--safe`/`--aggressive`|清掃強度|ブール値|
|`--interactive`|ユーザーガイダンス|ブール値|
|`--preview`|実行せずに表示する|ブール値|

### コマンドフラグの推定（`/sc:estimate`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#estimate-command-flags-scestimate)

|フラグ|目的|価値観|
|---|---|---|
|`--type`|焦点を推定する|`time`、、`effort`​`complexity`|
|`--unit`|時間単位|`hours`、、`days`​`weeks`|
|`--breakdown`|詳細な内訳|ブール値|

### インデックスコマンドフラグ（`/sc:index`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#index-command-flags-scindex)

|フラグ|目的|価値観|
|---|---|---|
|`--type`|インデックスターゲット|`docs`、、、、`api`​`structure`​`readme`|
|`--format`|出力形式|`md`、、`json`​`yaml`|

### コマンドフラグを反映する ( `/sc:reflect`)

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#reflect-command-flags-screflect)

|フラグ|目的|価値観|
|---|---|---|
|`--type`|反射スコープ|`task`、、`session`​`completion`|
|`--analyze`|分析を含める|ブール値|
|`--validate`|完全性を検証する|ブール値|

### スポーンコマンドフラグ（`/sc:spawn`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#spawn-command-flags-scspawn)

|フラグ|目的|価値観|
|---|---|---|
|`--strategy`|調整アプローチ|`sequential`、、`parallel`​`adaptive`|
|`--depth`|分析の深さ|`normal`、`deep`|

### Gitコマンドフラグ（`/sc:git`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#git-command-flags-scgit)

|フラグ|目的|価値観|
|---|---|---|
|`--smart-commit`|コミットメッセージを生成する|ブール値|
|`--interactive`|ガイド付き操作|ブール値|

### 選択ツールコマンドフラグ ( `/sc:select-tool`)

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#select-tool-command-flags-scselect-tool)

|フラグ|目的|価値観|
|---|---|---|
|`--analyze`|ツール分析|ブール値|
|`--explain`|選択の説明|ブール値|

### テストコマンドフラグ（`/sc:test`）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#test-command-flags-sctest)

|フラグ|目的|価値観|
|---|---|---|
|`--coverage`|カバー範囲を含める|ブール値|
|`--type`|テストの種類|`unit`、、`integration`​`e2e`|
|`--watch`|ウォッチモード|ブール値|

## 高度な制御フラグ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#advanced-control-flags)

### 範囲と焦点

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#scope-and-focus)

|フラグ|目的|価値観|
|---|---|---|
|`--scope`|分析境界|`file`、、、、`module`​`project`​`system`|
|`--focus`|ドメインターゲティング|`performance`、、、、、、`security`​`quality`​`architecture`​`accessibility`​`testing`|

### 実行制御

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#execution-control)

|フラグ|目的|価値観|
|---|---|---|
|`--concurrency [n]`|並列オペレーションを制御する|1-15|
|`--iterations [n]`|改善サイクル|1-10|
|`--all-mcp`|すべてのMCPサーバーを有効にする|ブール値|
|`--no-mcp`|ネイティブツールのみ|ブール値|

### システムフラグ（SuperClaude インストール）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#system-flags-superclaude-installation)

|フラグ|目的|価値観|
|---|---|---|
|`--verbose`/`-v`|詳細ログ|ブール値|
|`--quiet`/`-q`|出力を抑制する|ブール値|
|`--dry-run`|操作をシミュレーションする|ブール値|
|`--force`|チェックをスキップする|ブール値|
|`--yes`/`-y`|自動確認|ブール値|
|`--install-dir`|ターゲットディレクトリ|パス|
|`--legacy`|レガシースクリプトを使用する|ブール値|
|`--version`|バージョンを表示|ブール値|
|`--help`|ヘルプを表示|ブール値|

## 一般的な使用パターン

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#common-usage-patterns)

### フロントエンド開発

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#frontend-development)

```shell
/sc:implement "responsive dashboard" --magic --c7
/sc:design component-library --type component --format code
/sc:test ui-components/ --magic --play
/sc:improve legacy-ui/ --magic --morph --validate
```

### バックエンド開発

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#backend-development)

```shell
/sc:analyze api/ --focus performance --seq --think
/sc:design payment-api --type api --format spec
/sc:troubleshoot "API timeout" --type performance --trace
/sc:improve auth-service --type security --validate
```

### 大規模プロジェクト

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#large-projects)

```shell
/sc:analyze . --ultrathink --all-mcp --safe-mode
/sc:workflow enterprise-system --strategy enterprise --depth deep
/sc:cleanup . --type all --safe --interactive
/sc:estimate "migrate to microservices" --type complexity --breakdown
```

### 品質とメンテナンス

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#quality--maintenance)

```shell
/sc:improve src/ --type quality --safe --interactive
/sc:cleanup imports --type imports --preview
/sc:reflect --type completion --validate
/sc:git commit --smart-commit
```

## フラグインタラクション

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#flag-interactions)

### 互換性のある組み合わせ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#compatible-combinations)

- `--think`+ `--c7`: ドキュメント付き分析
- `--magic`+ `--play`: テスト付きのUI生成
- `--serena`+ `--morph`: 変換によるプロジェクトメモリ
- `--safe-mode`+ `--validate`: 最大限の安全性
- `--loop`+ `--validate`: 検証を伴う反復的な改善

### 競合するフラグ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#conflicting-flags)

- `--all-mcp`個別のMCPフラグと比較（どちらか一方を使用）
- `--no-mcp`任意のMCPフラグと比較（--no-mcpが優先）
- `--safe`vs `--aggressive`（クリーンアップ強度）
- `--quiet`vs `--verbose`（出力レベル）

### 関係の自動有効化

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#auto-enabling-relationships)

- `--safe-mode`自動的`--uc`に有効になり、`--validate`
- `--ultrathink`すべてのMCPサーバーを自動的に有効にする
- `--think-hard`自動的に有効になります`--seq`+`--c7`
- `--magic`UIに重点を置いたエージェントを起動する

## トラブルシューティングフラグ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#troubleshooting-flags)

### よくある問題

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#common-issues)

- **ツールが多すぎる**:`--no-mcp`ネイティブツールのみでテストする
- **操作が遅すぎます**:`--uc`出力を圧縮するために追加します
- **検証ブロッキング**:開発で`--validate`は代わりに使用してください`--safe-mode`
- **コンテキスト圧力**:`--token-efficient`使用率が75%を超えると自動的にアクティブ化されます

### デバッグフラグ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#debug-flags)

```shell
/sc:analyze . --verbose                      # Shows decision logic and flag activation
/sc:select-tool "operation" --explain        # Explains tool selection process
/sc:reflect --type session --analyze         # Reviews current session decisions
```

### クイックフィックス

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#quick-fixes)

```shell
/sc:analyze . --help                         # Shows available flags for command
/sc:analyze . --no-mcp                       # Native execution only
/sc:cleanup . --preview                      # Shows what would be cleaned
```

## フラグの優先ルール

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#flag-priority-rules)

1. **安全第一**: `--safe-mode`> `--validate`> 最適化フラグ
2. **明示的なオーバーライド**: ユーザーフラグ > 自動検出
3. **深度階層**：`--ultrathink`> `--think-hard`>`--think`
4. **MCP制御**:`--no-mcp`すべてのMCPフラグを上書きします
5. **スコープの優先順位**: システム > プロジェクト > モジュール > ファイル

## 関連リソース

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/flags.md#related-resources)

- [コマンドガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/commands.md)- これらのフラグを使用するコマンド
- [MCP サーバーガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md)- MCP フラグのアクティブ化について
- [セッション管理](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md)- 永続セッションでのフラグの使用