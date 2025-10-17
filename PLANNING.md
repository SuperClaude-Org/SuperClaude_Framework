# SuperClaude Framework - Planning & Architecture

## 📋 プロジェクト概要

### 目的
Claude Codeを構造化された開発プラットフォームに変換するメタプログラミング設定フレームワーク。行動命令注入とコンポーネントオーケストレーションにより、体系的なワークフロー自動化を実現。

### 背景
- LLMベースの開発支援ツールは強力だが、一貫性のある振る舞いの実現が困難
- プロジェクトごとに開発ルールを再説明するコストが高い
- エージェント、モード、MCPサーバーを統合した統一フレームワークの必要性

### 成果物
- 26 スラッシュコマンド
- 16 専門エージェント
- 7 動作モード
- 8 MCP サーバー統合

---

## 🏗️ アーキテクチャ

### コアコンポーネント

```
SuperClaude Framework
├── Modes（動作モード）         - 文脈に応じた振る舞い変更
├── Agents（専門エージェント）   - ドメイン特化型タスク実行
├── Commands（スラッシュコマンド） - ユーザーインターフェース
└── MCP Servers（外部統合）     - 外部ツール連携
```

### レイヤー構造

| レイヤー | 責務 | 実装場所 |
|---------|------|---------|
| **Entry Point** | Claude Code統合ポイント | `.claude/CLAUDE.md` |
| **Framework Core** | 原則・ルール・フラグ | `superclaude/framework/` |
| **Behavioral Modes** | 動作モード定義 | `superclaude/modes/` |
| **Specialized Agents** | エージェント実装 | `superclaude/agents/` |
| **Commands** | コマンド定義 | `superclaude/commands/` |
| **MCP Integration** | 外部ツール連携 | 設定ファイル |
| **Installation** | セットアップロジック | `setup/` |

### PM Agent（メタレイヤー）
- **役割**: 実行ではなく調整・学習・ドキュメント化
- **起動タイミング**: セッション開始、タスク完了、エラー検出
- **責務**:
  - セッション開始プロトコル（状態確認、トークン計算、信頼性チェック）
  - 実行後の知見抽出とドキュメント化
  - 失敗パターンの分析と予防策作成
  - 定期的なドキュメントメンテナンス

---

## 📁 ディレクトリ構成

### ルートレベル（重要ドキュメント）

```
/
├── README.md           # プロジェクト概要、インストール、使い方
├── PLANNING.md         # このファイル：アーキテクチャ、設計思想、開発ルール
├── TASK.md             # タスクリスト（継続更新）
├── KNOWLEDGE.md        # 蓄積された知見（学習内容）
├── CONTRIBUTING.md     # コントリビューションガイド
└── LICENSE             # MITライセンス
```

### ソースコード構成

```
superclaude/
├── framework/          # フレームワークコア
│   ├── principles.md   # 設計原則（SOLID, DRY, KISS等）
│   ├── rules.md        # 行動ルール（優先度付き）
│   └── flags.md        # 動作フラグ定義
├── modes/              # 動作モード
│   ├── MODE_Brainstorming.md
│   ├── MODE_DeepResearch.md
│   ├── MODE_Orchestration.md
│   ├── MODE_Token_Efficiency.md
│   └── ...
├── agents/             # 専門エージェント
│   ├── pm-agent/       # PM Agent（メタレイヤー）
│   ├── deep-research-agent/
│   ├── security-engineer/
│   └── ...
├── commands/           # スラッシュコマンド
│   └── sc/             # /sc: プレフィックス付きコマンド
├── business/           # ビジネス領域リソース
├── research/           # リサーチ設定
└── modules/            # 再利用可能モジュール
```

### 開発・テスト

```
setup/                  # インストールスクリプト
├── cli/                # CLIコマンド
├── components/         # セットアップコンポーネント
├── core/               # コアロジック
└── services/           # サービス層

tests/                  # テストスイート
├── performance/        # パフォーマンステスト
└── pm_agent/           # PM Agentテスト

docs/                   # ドキュメント
├── getting-started/    # 入門ガイド
├── user-guide/         # ユーザーガイド
├── developer-guide/    # 開発者ガイド
├── reference/          # リファレンス
└── memory/             # セッションメモリ（一時ファイル）
```

---

## 💻 技術スタック

### 開発言語
- **Python**: 3.12+ （UV必須、Mac汚染禁止）
- **Node.js**: 24 （Mac Brewインストール済み、それ以外コンテナ）
- **Shell**: Bash（セットアップスクリプト）

### パッケージ管理
- **Python**: UV（仮想環境管理）
- **Node.js**: pnpm（npm/yarn禁止）

### 配布
- **PyPI**: `pipx install SuperClaude`（推奨）
- **npm**: `npm install -g @bifrost_inc/superclaude`

### MCP サーバー統合
| サーバー | 用途 | 優先度 |
|---------|------|-------|
| **Context7** | 最新ドキュメント参照 | 高 |
| **Sequential** | 複雑な分析・推論 | 高 |
| **Tavily** | Web検索（Deep Research） | 高 |
| **Magic** | UI コンポーネント生成 | 中 |
| **Playwright** | ブラウザテスト | 中 |
| **Serena** | セッション永続化 | 中 |
| **Morphllm** | 一括コード変換 | 低 |
| **Chrome DevTools** | パフォーマンス分析 | 低 |

---

## 🚨 絶対守る開発ルール

### 1. Evidence-Based Principle（最優先）
```yaml
Rule: 嘘・推測・仮定は絶対禁止
Action:
  - 知識不足の場合: Context7/Tavily で調査
  - インフラ変更: 公式ドキュメント確認必須
  - エラー発生: エラーメッセージで検索
Evidence: 推測によるTraefikポート設定ミスの前例あり
```

### 2. Parallel Execution Default
```yaml
Rule: 並列実行をデフォルト、Sequential は依存関係のみ
Trigger: 独立した3つ以上の操作
Action:
  - ファイル読み込み: 並列Read
  - 検索操作: 並列Grep/Glob
  - 分析タスク: 並列Agent起動
Exception: 明示的な依存関係がある場合のみSequential
Evidence: PM Agent並列実行仕様違反の前例あり
```

### 3. Infrastructure Safety
```yaml
Rule: インフラ設定変更時は必ず公式ドキュメント確認
Trigger: Traefik, nginx, Docker, Kubernetes等の設定変更
Action:
  - WebFetch で公式ドキュメント取得
  - MODE_DeepResearch 起動
  - 推測ベースの変更をブロック
Rationale: 設定ミスは本番障害に直結
```

### 4. Mac Environment Protection
```yaml
Rule: Macホスト環境を汚染しない
Allowed on Mac:
  - Brew CLIツール（docker, gh, uv等）
  - XDG準拠の設定ファイル（~/.config/）
  - キャッシュ（~/.cache/、削除可能）
Forbidden on Mac:
  - pnpm/npm/yarn install（必ずDocker内）
  - Python pip install（UV仮想環境必須）
  - 依存関係のグローバルインストール
Method: 全てDocker/Containerに閉じ込める
```

### 5. Latest Information Validation
```yaml
Rule: 知識は1年以上古い前提で、常に最新情報を確認
Action:
  - ライブラリ/フレームワーク: Context7で最新版確認
  - ベストプラクティス: Tavily/WebSearchで2025年の情報
  - エラー解決: 最新のStack Overflow/GitHub Issues
Frequency: タスク開始時、実装前、エラー発生時
```

### 6. Implementation Completeness
```yaml
Rule: 開始したら完成させる、半完成は禁止
Forbidden:
  - TODO コメント（コア機能）
  - throw new Error("Not implemented")
  - モックオブジェクト・スタブ実装
  - プレースホルダー
Required: 動作するコードのみ
Exception: 明示的に「MVP」「Prototype」と宣言された場合のみ
```

### 7. Scope Discipline
```yaml
Rule: 要求された機能のみ実装、余計な機能追加禁止
Approach: MVP First → フィードバック → 反復改善
Forbidden:
  - 認証システム（要求されていない）
  - デプロイ設定（要求されていない）
  - モニタリング（要求されていない）
  - エンタープライズ機能（要求されていない）
Principle: YAGNI（You Aren't Gonna Need It）
```

### 8. Professional Honesty
```yaml
Rule: マーケティング言語禁止、事実のみ記述
Forbidden:
  - "blazingly fast", "100% secure"
  - "magnificent", "excellent"
  - 根拠のない数値（"95% faster"等）
Required:
  - "untested", "MVP", "needs validation"
  - トレードオフの明示
  - 問題点の指摘
Tone: 技術的・客観的・批判的
```

### 9. Git Workflow Safety
```yaml
Rule: 常にFeature Branchで作業、main/master直接編集禁止
Protocol:
  1. git status && git branch（セッション開始時必須）
  2. git checkout -b feature/xxx（新機能）
  3. 頻繁にコミット（意味のあるメッセージ）
  4. git diff（コミット前に必ず確認）
  5. リスク操作前にコミット（Restore Point作成）
Safety: 常にロールバック可能な状態を維持
```

### 10. File Organization
```yaml
Rule: ファイルは目的ごとに適切な場所へ配置
Placement:
  - Tests: tests/, __tests__/, test/
  - Scripts: scripts/, tools/, bin/
  - Claude用ドキュメント: docs/research/
  - 一時ファイル: 作業後に削除
Forbidden:
  - test_*.py を src/ に配置
  - debug.sh をルートに配置
  - *.test.js を src/ に配置
Principle: 関心の分離（Separation of Concerns）
```

---

## 📐 コーディング規約

### 命名規則
```yaml
Principle: 責務が明確にわかる具体的な名前
Forbidden:
  - core/, common/, utils/（抽象的）
  - *-service, *-manager, *-handler（曖昧）
  - data, temp, misc（意味不明）
Required:
  - user-authentication/, order-processing/
  - calculateTax(), validateEmail()
  - UserRepository, OrderService（明確な責務）
Convention:
  - JavaScript/TypeScript: camelCase
  - Python: snake_case
  - Directories: kebab-case
```

### ファイルサイズ
```yaml
Target: 500行以下/ファイル
Approach:
  - Single Responsibility Principle
  - 500行超えたらモジュール分割
  - 関数は50行以下を目標
Rationale: テスト可能性、保守性向上
```

### コメント
```yaml
Required:
  - 複雑なロジックの意図説明
  - 非自明な設計判断の理由
  - APIドキュメント（公開関数）
Forbidden:
  - コードの直訳（"ユーザーを取得"等）
  - TODOコメント（Issue化すべき）
  - コメントアウトされたコード（削除）
```

---

## 🧪 テスト戦略

### 完了の定義
```yaml
Definition: 「テスト済み + 動作確認済み」
Required:
  - ユニットテスト（ロジック部分）
  - 統合テスト（コンポーネント連携）
  - 動作確認手順の文書化
Forbidden: 口頭報告のみで完了宣言
```

### テストタイプ
| タイプ | 対象 | ツール | 頻度 |
|-------|------|-------|------|
| **Unit** | 個別関数/クラス | pytest, jest | コミット毎 |
| **Integration** | コンポーネント連携 | pytest, jest | PR前 |
| **E2E** | ユーザーシナリオ | Playwright | リリース前 |
| **Performance** | トークン使用量、速度 | カスタム | メジャーリリース |

---

## 🚀 デプロイメント

### 配布チャネル
- **PyPI**: `pipx install SuperClaude`（推奨）
- **npm**: `npm install -g @bifrost_inc/superclaude`

### バージョニング
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Current**: v4.2.0

### リリースプロセス
1. 機能完成 → tests/ でテスト
2. CHANGELOG.md 更新
3. バージョンバンプ
4. PyPI/npm 公開
5. GitHub Release作成
6. ドキュメントサイト更新

---

## 📚 Self-Improvement Loop

### セッション開始プロトコル
```yaml
1. Read PLANNING.md:
   - アーキテクチャ理解
   - 絶対守るルール確認

2. Read TASK.md:
   - 現在のタスク確認
   - 優先度把握

3. Read KNOWLEDGE.md:
   - 過去の知見参照
   - 失敗パターン回避

4. Git Status:
   - ブランチ確認
   - 変更状況把握

5. Token Budget:
   - リソース確認
   - 効率化判断

6. Confidence Check:
   - 理解度検証（>70%）
   - 不明点の質問
```

### 実行中の学習
```yaml
Discovery:
  - 新しいベストプラクティス → KNOWLEDGE.md に追記
  - 設計パターン発見 → KNOWLEDGE.md に記録

Failure:
  - エラー検出 → 根本原因分析
  - 失敗パターン → PLANNING.md ルール追加

Completion:
  - タスク完了 → TASK.md 更新
  - 知見抽出 → KNOWLEDGE.md に追加
```

### 定期振り返り
```yaml
Frequency:
  - セッション終了時
  - 週次レビュー
  - 月次メンテナンス

Process:
  1. Self-Reflection: 何を間違えた？
  2. Pattern Extraction: 繰り返しパターン？
  3. Document Update: ルール/知見更新
  4. Metrics Tracking: 改善率測定
```

---

## 🔄 ワークフロー例

### 新機能開発
```bash
# 1. セッション開始
Read PLANNING.md, TASK.md, KNOWLEDGE.md
git status && git branch

# 2. ブランチ作成
git checkout -b feature/new-command

# 3. 調査（Evidence-Based）
Context7/Tavily で最新情報確認

# 4. 実装（並列実行）
Parallel: Read files, Analyze code, Generate tests

# 5. テスト
pytest tests/

# 6. コミット
git add . && git commit -m "feat: add new command"

# 7. 学習
KNOWLEDGE.md に発見を追記
```

---

## 📞 質問・不明点

```yaml
Principle: わからないことを質問するのは良いこと
Forbidden: 理解していないまま実装着手（害悪）
Action:
  - 曖昧な要求 → 具体的な質問で引き出す
  - 技術的不明点 → Context7/Tavily で調査
  - それでも不明 → ユーザーに質問
```

---

**このドキュメントは生きている設計書です。**
**新しい知見、失敗パターン、改善案があれば継続的に更新してください。**
**迷ったらこのファイルに戻ってきてください。**
