# コードスタイルと規約

## Python コーディング規約

### フォーマット（Black設定）
- **行長**: 88文字
- **ターゲットバージョン**: Python 3.8-3.12
- **除外ディレクトリ**: .eggs, .git, .venv, build, dist

### 型ヒント（mypy設定）
- **必須**: すべての関数定義に型ヒントを付ける
- `disallow_untyped_defs = true`: 型なし関数定義を禁止
- `disallow_incomplete_defs = true`: 不完全な型定義を禁止
- `check_untyped_defs = true`: 型なし関数定義をチェック
- `no_implicit_optional = true`: 暗黙的なOptionalを禁止

### ドキュメント規約
- **パブリックAPI**: すべてドキュメント化必須
- **例示**: 使用例を含める
- **段階的複雑さ**: 初心者→上級者の順で説明

### 命名規則
- **変数/関数**: snake_case（例: `display_header`, `setup_logging`）
- **クラス**: PascalCase（例: `Colors`, `LogLevel`）
- **定数**: UPPER_SNAKE_CASE
- **プライベート**: 先頭にアンダースコア（例: `_internal_method`）

### ファイル構造
```
superclaude/          # メインパッケージ
├── core/            # コア機能
├── modes/           # 行動モード
├── agents/          # 専門エージェント
├── mcp/             # MCPサーバー統合
├── commands/        # スラッシュコマンド
└── examples/        # 使用例

setup/               # セットアップコンポーネント
├── core/           # インストーラーコア
├── utils/          # ユーティリティ
├── cli/            # CLIインターフェース
├── components/     # インストール可能コンポーネント
├── data/           # 設定データ
└── services/       # サービスロジック
```

### エラーハンドリング
- 包括的なエラーハンドリングとログ記録
- ユーザーフレンドリーなエラーメッセージ
- アクション可能なエラーガイダンス
