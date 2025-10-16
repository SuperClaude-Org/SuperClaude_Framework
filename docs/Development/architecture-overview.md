# アーキテクチャ概要

## プロジェクト構造

### メインパッケージ（superclaude/）
```
superclaude/
├── __init__.py           # パッケージ初期化
├── __main__.py           # CLIエントリーポイント
├── core/                 # コア機能
├── modes/                # 行動モード（7種類）
│   ├── Brainstorming     # 要件探索
│   ├── Business_Panel    # ビジネス分析
│   ├── DeepResearch      # 深層研究
│   ├── Introspection     # 内省分析
│   ├── Orchestration     # ツール調整
│   ├── Task_Management   # タスク管理
│   └── Token_Efficiency  # トークン効率化
├── agents/               # 専門エージェント（16種類）
├── mcp/                  # MCPサーバー統合（8種類）
├── commands/             # スラッシュコマンド（26種類）
└── examples/             # 使用例
```

### セットアップパッケージ（setup/）
```
setup/
├── __init__.py
├── core/                 # インストーラーコア
├── utils/                # ユーティリティ関数
├── cli/                  # CLIインターフェース
├── components/           # インストール可能コンポーネント
│   ├── agents.py        # エージェント設定
│   ├── mcp.py           # MCPサーバー設定
│   └── ...
├── data/                 # 設定データ（JSON/YAML）
└── services/             # サービスロジック
```

## 主要コンポーネント

### CLIエントリーポイント（__main__.py）
- `main()`: メインエントリーポイント
- `create_parser()`: 引数パーサー作成
- `register_operation_parsers()`: サブコマンド登録
- `setup_global_environment()`: グローバル環境設定
- `display_*()`: ユーザーインターフェース関数

### インストールシステム
- **コンポーネントベース**: モジュラー設計
- **フォールバック機能**: レガシーサポート
- **設定管理**: `~/.claude/` ディレクトリ
- **MCPサーバー**: Node.js統合

## デザインパターン

### 責任の分離
- **setup/**: インストールとコンポーネント管理
- **superclaude/**: ランタイム機能と動作
- **tests/**: テストとバリデーション
- **docs/**: ドキュメントとガイド

### プラグインアーキテクチャ
- モジュラーコンポーネントシステム
- 動的ロードと登録
- 拡張可能な設計

### 設定ファイル階層
1. `~/.claude/CLAUDE.md` - グローバルユーザー設定
2. プロジェクト固有 `CLAUDE.md` - プロジェクト設定
3. `~/.claude/.claude.json` - Claude Code設定
4. MCPサーバー設定ファイル

## 統合ポイント

### Claude Code統合
- スラッシュコマンド注入
- 行動指示インジェクション
- セッション永続化

### MCPサーバー
1. **Context7**: ライブラリドキュメント
2. **Sequential**: 複雑な分析
3. **Magic**: UIコンポーネント生成
4. **Playwright**: ブラウザテスト
5. **Morphllm**: 一括変換
6. **Serena**: セッション永続化
7. **Tavily**: Web検索
8. **Chrome DevTools**: パフォーマンス分析

## 拡張ポイント

### 新規コンポーネント追加
1. `setup/components/` に実装
2. `setup/data/` に設定追加
3. テストを `tests/` に追加
4. ドキュメントを `docs/` に追加

### 新規エージェント追加
1. トリガーキーワード定義
2. 機能説明作成
3. 統合テスト追加
4. ユーザーガイド更新
