# セッション管理ガイド

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#session-management-guide)

SuperClaude は、Serena MCP サーバーを通じて永続的なセッション管理を提供し、Claude Code の会話全体にわたる真のコンテキスト保存と長期的なプロジェクト継続性を実現します。

## 永続メモリを使用したコアセッションコマンド

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#core-session-commands-with-persistent-memory)

### `/sc:load`- 永続メモリによるコンテキストの読み込み

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#scload---context-loading-with-persistent-memory)

**目的**: 以前のセッションからのプロジェクトコンテキストと永続メモリを使用してセッションを初期化します。MCP  
**統合**: Serena MCP をトリガーして、保存されたプロジェクトメモリを読み取ります。  
**構文**:`/sc:load [project_path]`

**何が起こるのですか**：

- Serena MCPは以前のセッションから永続メモリファイルを読み取ります
- プロジェクトのコンテキストは保存されたメモリから復元されます
- 過去の決定、パターン、進捗状況が読み込まれます
- セッション状態は履歴コンテキストで初期化されます

**ユースケース**:

```shell
# Load existing project context from persistent memory
/sc:load src/

# Resume specific project work with full history
/sc:load "authentication-system"

# Initialize with codebase analysis and previous insights
/sc:load . --analyze
```

### `/sc:save`- メモリへのセッションの永続性

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#scsave---session-persistence-to-memory)

**目的**: 現在のセッション状態と決定を永続メモリ  
**MCP に保存します。統合**: Serena MCP をトリガーしてメモリ ファイルに書き込みます。  
**構文**:`/sc:save "session_description"`

**何が起こるのですか**：

- 現在の状況と決定はセレナのメモリに書き込まれます
- プロジェクトの状態と進捗は会話を通じて維持されます
- 重要な洞察とパターンは将来のセッションのために保存されます
- セッション概要はタイムスタンプ付きで作成され、検索に利用できます

**ユースケース**:

```shell
# Save completed feature work for future reference
/sc:save "user authentication implemented with JWT"

# Checkpoint during complex work
/sc:save "API design phase complete, ready for implementation"

# Store architectural decisions permanently
/sc:save "microservices architecture decided, service boundaries defined"
```

### `/sc:reflect`- メモリコンテキストによる進捗状況の評価

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#screflect---progress-assessment-with-memory-context)

**目的**: 保存されたメモリに対して現在の進行状況を分析し、セッションの完全性を検証する  
**MCP 統合**: Serena MCP を使用して、保存されたメモリと現在の状態を比較する  
**構文**:`/sc:reflect [--scope project|session]`

**何が起こるのですか**：

- セレナMCPは過去の記憶と現在の文脈を読み取ります
- 進捗は保存された目標とマイルストーンに対して評価されます
- 歴史的背景に基づいてギャップと次のステップが特定される
- セッションの完全性はプロジェクトメモリに対して検証されます

**ユースケース**:

```shell
# Assess project progress against stored milestones
/sc:reflect --scope project

# Validate current session completeness
/sc:reflect

# Check if ready to move to next phase based on memory
/sc:reflect --scope session
```

## 永続メモリアーキテクチャ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#persistent-memory-architecture)

### Serena MCP が真の永続性を実現する方法

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#how-serena-mcp-enables-true-persistence)

**メモリストレージ**:

- 構造化メモリファイルとして保存されるセッションコンテキスト
- プロジェクトの決定とアーキテクチャパターンは永久に保存されます
- コード分​​析の結果と洞察は会話を通じて保持されます
- 進捗状況の追跡とマイルストーンのデータは長期にわたって維持されます

**セッション間の継続性**:

- 以前のセッションのコンテキストが新しい会話で自動的に利用可能
- 決定と根拠は会話を通じて保存され、アクセス可能
- 過去のパターンと解決策からの学習を維持
- 一貫したプロジェクト理解が永久に維持される

**メモリタイプ**:

- **プロジェクトの思い出**：長期プロジェクトの文脈とアーキテクチャ
- **セッションの記憶**：具体的な会話の結果と決定
- **パターンメモリ**：再利用可能なソリューションとアーキテクチャパターン
- **進捗の思い出**：マイルストーンの追跡と完了ステータス

## 永続性を備えたセッションライフサイクルパターン

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#session-lifecycle-patterns-with-persistence)

### 新しいプロジェクトの初期化

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#new-project-initialization)

```shell
# 1. Start fresh project
/sc:brainstorm "e-commerce platform requirements"

# 2. Save initial decisions to persistent memory
/sc:save "project scope and requirements defined"

# 3. Begin implementation planning
/sc:workflow "user authentication system"

# 4. Save architectural decisions permanently
/sc:save "auth architecture: JWT + refresh tokens + rate limiting"
```

### 既存の作業の再開（クロス会話）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#resuming-existing-work-cross-conversation)

```shell
# 1. Load previous context from persistent memory
/sc:load "e-commerce-project"

# 2. Assess current state against stored progress
/sc:reflect --scope project  

# 3. Continue with next phase using stored context
/sc:implement "payment processing integration"

# 4. Save progress checkpoint to memory
/sc:save "payment system integrated with Stripe API"
```

### 長期プロジェクト管理

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#long-term-project-management)

```shell
# Weekly checkpoint pattern with persistence
/sc:load project-name
/sc:reflect --scope project
# ... work on features ...
/sc:save "week N progress: features X, Y, Z completed"

# Phase completion pattern with memory
/sc:reflect --scope project
/sc:save "Phase 1 complete: core authentication and user management"
/sc:workflow "Phase 2: payment and order processing"
```

## クロス会話の継続性

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#cross-conversation-continuity)

### 粘り強く新しい会話を始める

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#starting-new-conversations-with-persistence)

新しい Claude Code 会話を開始すると、永続メモリ システムによって次のことが可能になります。

1. **自動コンテキスト復元**
    
    ```shell
    /sc:load project-name
    # Automatically restores all previous context, decisions, and progress
    ```
    
2. **進歩の継続**
    
    - 以前のセッションの決定はすぐに利用可能
    - アーキテクチャパターンとコードの洞察は保存されます
    - プロジェクトの履歴と根拠が維持される
3. **インテリジェントなコンテキスト構築**
    
    - Serena MCPは、現在の作業に基づいて関連するメモリを提供します
    - 過去のソリューションとパターンが新しい実装に影響を与える
    - プロジェクトの進捗状況が追跡され、理解される

### メモリ最適化

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#memory-optimization)

**有効なメモリ使用量**:

- 説明的かつ検索可能なメモリ名を使用する
- プロジェクトのフェーズとタイムスタンプのコンテキストを含める
- 特定の機能やアーキテクチャ上の決定を参照する
- 将来の検索を直感的にする

**記憶内容戦略**：

- 結果だけでなく、意思決定と根拠も保存する
- 検討した代替アプローチを含める
- 統合パターンと依存関係を文書化する
- 学習内容と洞察を将来の参考のために保存する

**メモリライフサイクル管理**:

- 古くなったメモリの定期的なクリーンアップ
- 関連するセッション記憶の統合
- 完了したプロジェクトフェーズのアーカイブ
- 時代遅れのアーキテクチャ上の決定の削減

## 永続セッションのベストプラクティス

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#best-practices-for-persistent-sessions)

### セッション開始プロトコル

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#session-start-protocol)

1. `/sc:load`既存のプロジェクトの場合は常に
2. `/sc:reflect`記憶から現在の状態を理解するために使用する
3. 永続的なコンテキストと保存されたパターンに基づいて作業を計画する
4. 過去の決定とアーキテクチャの選択に基づいて構築する

### セッション終了プロトコル

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#session-end-protocol)

1. `/sc:reflect`保存された目標に対する完全性を評価するために使用します
2. 重要な決定を`/sc:save`将来のセッションのために保存する
3. 次のステップと未解決の質問を記憶に記録する
4. 将来のシームレスな継続のためにコンテキストを保存する

### 記憶品質の維持

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#memory-quality-maintenance)

- 簡単に思い出せるように、分かりやすく説明的なメモリ名を使用する
- 決定事項と代替アプローチに関する背景情報を含める
- 特定のコードの場所とパターンを参照する
- セッション間でメモリ構造の一貫性を維持する

## 他のSuperClaude機能との統合

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#integration-with-other-superclaude-features)

### MCP サーバー調整

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#mcp-server-coordination)

- **Serena MCP** : 永続メモリインフラストラクチャを提供します
- **シーケンシャルMCP** : 保存されたメモリを使用して複雑な分析を強化します
- **Context7 MCP** : 保存されたパターンとドキュメント化のアプローチを参照します
- **Morphllm MCP** : 保存されたリファクタリングパターンを一貫して適用します

### エージェントとメモリの連携

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#agent-collaboration-with-memory)

- エージェントは強化されたコンテキストのために永続的なメモリにアクセスします
- 以前の専門家の決定は保存され、参照されます
- 共有メモリを介したセッション間エージェント調整
- プロジェクトの履歴に基づいた一貫した専門家の推奨

### 永続性を備えたコマンド統合

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#command-integration-with-persistence)

- すべての`/sc:`コマンドは永続的なコンテキストを参照し、そのコンテキストに基づいて構築できます。
- 以前のコマンド出力と決定はセッション間で利用可能
- ワークフローパターンは保存され、再利用できる
- 実装履歴は将来の指揮決定を導く

## 永続セッションのトラブルシューティング

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#troubleshooting-persistent-sessions)

### よくある問題

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#common-issues)

**メモリが読み込まれません**:

- Serena MCP が正しく構成され、実行されていることを確認します。
- メモリファイルの権限とアクセス可能性を確認する
- プロジェクトの命名規則の一貫性を確保する
- メモリファイルの整合性とフォーマットを検証する

**セッション間のコンテキスト損失**:

- `/sc:save`セッションを終了する前に必ず使用してください
- 簡単に検索できるように、わかりやすいメモリ名を使用する
- メモリの完全性を定期的`/sc:reflect`に検証する
- 重要なメモリファイルを定期的にバックアップする

**メモリの競合**:

- バージョン管理にはタイムスタンプ付きのメモリ名を使用する
- 古くなった記憶の定期的なクリーンアップ
- プロジェクトとセッションのメモリを明確に分離
- セッション間で一貫したメモリ命名規則

### クイックフィックス

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#quick-fixes)

**セッション状態をリセット**:

```shell
/sc:load --fresh  # Start without previous context
/sc:reflect       # Assess current state
```

**メモリクリーンアップ**:

```shell
/sc:reflect --cleanup  # Remove obsolete memories
/sc:save --consolidate # Merge related memories
```

**コンテキスト回復**:

```shell
/sc:load --recent     # Load most recent memories
/sc:reflect --repair  # Identify and fix context gaps
```

## 高度な永続セッションパターン

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#advanced-persistent-session-patterns)

### 複数フェーズのプロジェクト

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#multi-phase-projects)

- 整理のためにフェーズ固有のメモリ命名を使用する
- フェーズ全体でアーキテクチャ上の決定の継続性を維持する
- 永続メモリによるクロスフェーズ依存関係の追跡
- 歴史的背景を考慮した漸進的な複雑性管理

### チームコラボレーション

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#team-collaboration)

- 共有メモリの規則と命名規則
- チームのコンテキストにおける意思決定根拠の保存
- すべてのチームメンバーがアクセスできる統合パターンのドキュメント
- メモリを介した一貫したコードスタイルとアーキテクチャの適用

### 長期メンテナンス

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#long-term-maintenance)

- 完了したプロジェクトのメモリアーカイブ戦略
- 蓄積された記憶によるパターンライブラリの開発
- 時間をかけて構築された再利用可能なソリューションドキュメント
- 永続的なメモリ蓄積による知識ベースの構築

## 永続セッション管理の主な利点

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#key-benefits-of-persistent-session-management)

### プロジェクトの継続性

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#project-continuity)

- 複数の会話にわたるシームレスな作業継続
- Claude Codeセッション間でコンテキストが失われることはありません
- 保存されたアーキテクチャ上の決定と技術的根拠
- 長期的なプロジェクトの進捗追跡

### 生産性の向上

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#enhanced-productivity)

- プロジェクトのコンテキストを再度説明する必要性が減少
- 起動時間が速く、作業を継続できる
- 過去の洞察とパターンに基づいて
- 累積的なプロジェクト知識の成長

### 品質の一貫性

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md#quality-consistency)

- セッション間で一貫したアーキテクチャパターン
- コード品質の決定と標準の保持
- 再利用可能なソリューションとベストプラクティス
- 技術的負債の認識を維持

---

**重要なポイント**: Serena MCP によるセッション管理により、SuperClaude は単一の会話の支援から永続的なプロジェクト パートナーシップへと変わり、すべての開発フェーズと Claude Code の会話にわたってコンテキスト、決定、学習が維持されます。