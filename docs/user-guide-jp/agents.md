# SuperClaude エージェントガイド 🤖

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#superclaude-agents-guide-)

SuperClaude は、Claude Code が専門知識を得るために呼び出すことができる 14 のドメイン スペシャリスト エージェントを提供します。

## 🧪 エージェントのアクティベーションのテスト

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#-testing-agent-activation)

このガイドを使用する前に、エージェントの選択が機能することを確認してください。

```shell
# Test manual agent invocation
@agent-python-expert "explain decorators"
# Example behavior: Python expert responds with detailed explanation

# Test security agent auto-activation
/sc:implement "JWT authentication"
# Example behavior: Security engineer should activate automatically

# Test frontend agent auto-activation
/sc:implement "responsive navigation component"  
# Example behavior: Frontend architect + Magic MCP should activate

# Test systematic analysis
/sc:troubleshoot "slow API performance"
# Example behavior: Root-cause analyst + performance engineer activation

# Test combining manual and auto
/sc:analyze src/
@agent-refactoring-expert "suggest improvements"
# Example behavior: Analysis followed by refactoring suggestions
```

**テストが失敗した場合**: エージェントファイルが存在する`~/.claude/agents/`か、Claude Codeセッションを再起動してください。

## コアコンセプト

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#core-concepts)

### SuperClaude エージェントとは何ですか?

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#what-are-superclaude-agents)

**エージェントは**、Claude Codeの行動を変更するコンテキスト指示として実装された、専門分野のAIドメインエキスパートです。各エージェントは、ドメイン固有の専門知識、行動パターン、問題解決アプローチを含む、ディレクトリ`.md`内に綿密に作成されたファイルです`superclaude/Agents/`。

**重要**: エージェントは別個の AI モデルやソフトウェアではなく、Claude Code が読み取って特殊な動作を採用するコンテキスト構成です。

### エージェントの2つの使用方法

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#two-ways-to-use-agents)

#### 1. @agent- プレフィックスを使用した手動呼び出し

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#1-manual-invocation-with-agent--prefix)

```shell
# Directly invoke a specific agent
@agent-security "review authentication implementation"
@agent-frontend "design responsive navigation"
@agent-architect "plan microservices migration"
```

#### 2. 自動アクティベーション（行動ルーティング）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#2-auto-activation-behavioral-routing)

「自動アクティベーション」とは、Claude Codeがリクエスト内のキーワードとパターンに基づいて適切なコンテキストで動作指示を読み取り、エンゲージすることを意味します。SuperClaudeは、Claudeが最適なスペシャリストにルーティングするための動作ガイドラインを提供します。

> **📝 エージェントの「自動アクティベーション」の仕組み**：エージェントのアクティベーションは自動システムロジックではなく、コンテキストファイル内の動作指示です。ドキュメントでエージェントが「自動アクティベート」と記載されている場合、それはClaude Codeが指示を読み取り、リクエスト内のキーワードとパターンに基づいて特定のドメインの専門知識を活用することを意味します。これにより、基盤となるメカニズムを透明化しながら、インテリジェントなルーティング体験を実現します。

```shell
# These commands auto-activate relevant agents
/sc:implement "JWT authentication"  # → security-engineer auto-activates
/sc:design "React dashboard"        # → frontend-architect auto-activates
/sc:troubleshoot "memory leak"      # → performance-engineer auto-activates
```

**MCP サーバーは**、Context7 (ドキュメント作成)、Sequential (分析)、Magic (UI)、Playwright (テスト)、Morphllm (コード変換) などの専用ツールを通じて拡張機能を提供します。

**ドメイン スペシャリストは、**狭い専門分野に焦点を絞り、ジェネラリストのアプローチよりも深く正確なソリューションを提供します。

### エージェント選択ルール

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#agent-selection-rules)

**優先順位の階層:**

1. **手動オーバーライド**- @agent-[name] は自動アクティベーションよりも優先されます
2. **キーワード**- 直接的なドメイン用語は主要なエージェントをトリガーします
3. **ファイルタイプ**- 拡張子は言語/フレームワークの専門家を活性化します
4. **複雑性**- 複数ステップのタスクには調整エージェントが関与する
5. **コンテキスト**- 関連概念は補完的なエージェントをトリガーします

**紛争解決:**

- 手動呼び出し → 指定したエージェントが優先されます
- 複数のマッチング → マルチエージェントコーディネーション
- 不明瞭なコンテキスト → 要件アナリストの活性化
- 複雑性が高い → システムアーキテクトの監視
- 品質に関する懸念 → 自動QAエージェントの組み込み

**選択決定ツリー:**

```
Task Analysis →
├─ Manual @agent-? → Use specified agent
├─ Single Domain? → Activate primary agent
├─ Multi-Domain? → Coordinate specialist agents  
├─ Complex System? → Add system-architect oversight
├─ Quality Critical? → Include security + performance + quality agents
└─ Learning Focus? → Add learning-guide + technical-writer
```

## クイックスタートの例

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#quick-start-examples)

### 手動エージェント呼び出し

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#manual-agent-invocation)

```shell
# Explicitly call specific agents with @agent- prefix
@agent-python-expert "optimize this data processing pipeline"
@agent-quality-engineer "create comprehensive test suite"
@agent-technical-writer "document this API with examples"
@agent-socratic-mentor "explain this design pattern"
```

### 自動エージェント調整

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#automatic-agent-coordination)

```shell
# Commands that trigger auto-activation
/sc:implement "JWT authentication with rate limiting"
# → Triggers: security-engineer + backend-architect + quality-engineer

/sc:design "accessible React dashboard with documentation"
# → Triggers: frontend-architect + learning-guide + technical-writer  

/sc:troubleshoot "slow deployment pipeline with intermittent failures"
# → Triggers: devops-architect + performance-engineer + root-cause-analyst

/sc:audit "payment processing security vulnerabilities"
# → Triggers: security-engineer + quality-engineer + refactoring-expert
```

### 手動と自動のアプローチを組み合わせる

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#combining-manual-and-auto-approaches)

```shell
# Start with command (auto-activation)
/sc:implement "user profile system"

# Then explicitly add specialist review
@agent-security "review the profile system for OWASP compliance"
@agent-performance-engineer "optimize database queries"
```

---

## SuperClaude エージェントチーム 👥

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#the-superclaude-agent-team-)

### アーキテクチャとシステム設計エージェント 🏗️

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#architecture--system-design-agents-%EF%B8%8F)

### システムアーキテクト 🏢

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#system-architect-)

**専門分野**：スケーラビリティとサービスアーキテクチャに重点を置いた大規模分散システム設計

**自動アクティベーション**:

- キーワード: 「アーキテクチャ」、「マイクロサービス」、「スケーラビリティ」、「システム設計」、「分散」
- コンテキスト: マルチサービスシステム、アーキテクチャ上の決定、テクノロジーの選択
- 複雑さ: 5 つ以上のコンポーネントまたはドメイン間統合要件

**機能**:

- サービス境界の定義とマイクロサービスの分解
- テクノロジースタックの選択と統合戦略
- スケーラビリティ計画とパフォーマンスアーキテクチャ
- イベント駆動型アーキテクチャとメッセージングパターン
- データフロー設計とシステム統合

**例**:

1. **Eコマースプラットフォーム**：イベントソーシングを使用して、ユーザー、製品、支払い、通知サービスのマイクロサービスを設計します。
2. **リアルタイム分析**：ストリーム処理と時系列ストレージによる高スループットデータ取り込みのためのアーキテクチャ
3. **マルチテナント SaaS** : テナント分離、共有インフラストラクチャ、水平スケーリング戦略を備えたシステム設計

### 成功基準

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#success-criteria)

- [ ] 応答に表れたシステムレベルの思考
- [ ] サービスの境界と統合パターンについて言及する
- [ ] スケーラビリティと信頼性の考慮を含む
- [ ] テクノロジースタックの推奨事項を提供する

**検証:** `/sc:design "microservices platform"`システム アーキテクトをアクティブ化する必要があります。  
**テスト:**出力には、サービスの分解と統合パターンが含まれている必要があります。  
**チェック:**インフラストラクチャに関する懸念事項については、DevOps アーキテクトと調整する必要があります。

**最適な組み合わせ**: devops-architect (インフラストラクチャ)、performance-engineer (最適化)、security-engineer (コンプライアンス)

---

### バックエンドアーキテクト ⚙️

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#backend-architect-%EF%B8%8F)

**専門分野**: APIの信頼性とデータの整合性を重視した堅牢なサーバーサイドシステム設計

**自動アクティベーション**:

- キーワード: 「API」、「バックエンド」、「サーバー」、「データベース」、「REST」、「GraphQL」、「エンドポイント」
- ファイルタイプ: API仕様、サーバー構成、データベーススキーマ
- コンテキスト: サーバーサイドロジック、データの永続性、API開発

**機能**:

- RESTful および GraphQL API のアーキテクチャと設計パターン
- データベーススキーマ設計とクエリ最適化戦略
- 認証、承認、セキュリティの実装
- エラー処理、ログ記録、監視の統合
- キャッシュ戦略とパフォーマンスの最適化

**例**:

1. **ユーザー管理 API** : ロールベースのアクセス制御とレート制限を備えた JWT 認証
2. **支払い処理**: べき等性と監査証跡を備えた PCI 準拠のトランザクション処理
3. **コンテンツ管理**: キャッシュ、ページネーション、リアルタイム通知を備えた RESTful API

**最適な組み合わせ**: security-engineer (認証/セキュリティ)、performance-engineer (最適化)、quality-engineer (テスト)

---

### フロントエンドアーキテクト 🎨

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#frontend-architect-)

**専門分野**: アクセシビリティとユーザーエクスペリエンスを重視した最新の Web アプリケーション アーキテクチャ

**自動アクティベーション**:

- キーワード: 「UI」、「フロントエンド」、「React」、「Vue」、「Angular」、「コンポーネント」、「アクセシビリティ」、「レスポンシブ」
- ファイルタイプ: .jsx、.vue、.ts (フロントエンド)、.css、.scss
- コンテキスト: ユーザーインターフェース開発、コンポーネント設計、クライアント側アーキテクチャ

**機能**:

- コンポーネントアーキテクチャと設計システムの実装
- 状態管理パターン (Redux、Zustand、Pinia)
- アクセシビリティ準拠（WCAG 2.1）とインクルーシブデザイン
- パフォーマンスの最適化とバンドル分析
- プログレッシブウェブアプリとモバイルファースト開発

**例**:

1. **ダッシュボードインターフェース**: リアルタイム更新とレスポンシブなグリッドレイアウトによるアクセスしやすいデータ視覚化
2. **フォーム システム**: 検証、エラー処理、アクセシビリティ機能を備えた複雑なマルチステップ フォーム
3. **デザインシステム**: 一貫したスタイルとインタラクションパターンを備えた再利用可能なコンポーネントライブラリ

**最適な組み合わせ**: 学習ガイド (ユーザー ガイダンス)、パフォーマンス エンジニア (最適化)、品質エンジニア (テスト)

---

### DevOps アーキテクト 🚀

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#devops-architect-)

**専門分野**: 信頼性の高いソフトウェア配信のためのインフラストラクチャ自動化と展開パイプライン設計

**自動アクティベーション**:

- キーワード: 「デプロイ」、「CI/CD」、「Docker」、「Kubernetes」、「インフラストラクチャ」、「監視」、「パイプライン」
- ファイルタイプ: Dockerfile、docker-compose.yml、k8s マニフェスト、CI 構成
- コンテキスト: 導入プロセス、インフラストラクチャ管理、自動化

**機能**:

- 自動テストとデプロイメントを備えた CI/CD パイプライン設計
- コンテナオーケストレーションとKubernetesクラスタ管理
- Terraform とクラウド プラットフォームを使用した Infrastructure as Code
- 監視、ログ記録、および可観測性スタックの実装
- セキュリティスキャンとコンプライアンスの自動化

**例**:

1. **マイクロサービスのデプロイメント**: サービスメッシュ、自動スケーリング、ブルーグリーンリリースを備えた Kubernetes のデプロイメント
2. **マルチ環境パイプライン**: 自動テスト、セキュリティスキャン、段階的なデプロイメントを備えた GitOps ワークフロー
3. **モニタリングスタック**: メトリック、ログ、トレース、アラートシステムによる包括的な監視

**最適な職種**: システム アーキテクト (インフラストラクチャ計画)、セキュリティ エンジニア (コンプライアンス)、パフォーマンス エンジニア (監視)

### 品質・分析エージェント 🔍

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#quality--analysis-agents-)

### セキュリティエンジニア 🔒

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#security-engineer-)

**専門分野**: 脅威モデリングと脆弱性防止に重点を置いたアプリケーション セキュリティ アーキテクチャ

**自動アクティベーション**:

- キーワード: 「セキュリティ」、「認証」、「脆弱性」、「暗号化」、「コンプライアンス」、「OWASP」
- コンテキスト: セキュリティレビュー、認証フロー、データ保護要件
- リスク指標: 支払い処理、ユーザーデータ、API アクセス、規制遵守の必要性

**機能**:

- 脅威モデルと攻撃対象領域分析
- 安全な認証と認可の設計 (OAuth、JWT、SAML)
- データ暗号化戦略と鍵管理
- 脆弱性評価と侵入テストのガイダンス
- セキュリティコンプライアンス（GDPR、HIPAA、PCI-DSS）の実装

**例**:

1. **OAuth 実装**: トークンの更新とロールベースのアクセスによる安全なマルチテナント認証
2. **API セキュリティ**: レート制限、入力検証、SQL インジェクション防止、セキュリティ ヘッダー
3. **データ保護**: 保存時/転送時の暗号化、キーローテーション、プライバシーバイデザインアーキテクチャ

**最適な人材**: バックエンド アーキテクト (API セキュリティ)、品質エンジニア (セキュリティ テスト)、根本原因アナリスト (インシデント対応)

---

### パフォーマンスエンジニア ⚡

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#performance-engineer-)

**専門分野**：スケーラビリティとリソース効率を重視したシステムパフォーマンスの最適化

**自動アクティベーション**:

- キーワード: 「パフォーマンス」、「遅い」、「最適化」、「ボトルネック」、「レイテンシ」、「メモリ」、「CPU」
- コンテキスト: パフォーマンスの問題、スケーラビリティの懸念、リソースの制約
- メトリクス: 応答時間 >500 ミリ秒、メモリ使用量が多い、スループットが低い

**機能**:

- パフォーマンスプロファイリングとボトルネックの特定
- データベースクエリの最適化とインデックス戦略
- キャッシュ実装（Redis、CDN、アプリケーションレベル）
- 負荷テストと容量計画
- メモリ管理とリソースの最適化

**例**:

1. **API最適化**: キャッシュとクエリの最適化により、応答時間を2秒から200ミリ秒に短縮
2. **データベースのスケーリング**: リードレプリカ、接続プール、クエリ結果のキャッシュを実装する
3. **フロントエンドのパフォーマンス**: バンドルの最適化、遅延読み込み、および CDN 実装により、読み込み時間が 3 秒未満に短縮されます。

**最適な組み合わせ**: システム アーキテクト (スケーラビリティ)、DevOps アーキテクト (インフラストラクチャ)、ルート原因アナリスト (デバッグ)

---

### 根本原因分析者 🔍

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#root-cause-analyst-)

**専門分野**：証拠に基づく分析と仮説検定を用いた体系的な問題調査

**自動アクティベーション**:

- キーワード: 「バグ」、「問題」、「問題」、「デバッグ」、「調査」、「トラブルシューティング」、「エラー」
- コンテキスト: システム障害、予期しない動作、複雑な複数コンポーネントの問題
- 複雑性: 体系的な調査を必要とするシステム間問題

**機能**:

- 体系的なデバッグ方法論と根本原因分析
- システム間のエラー相関と依存関係のマッピング
- 障害調査のためのログ分析とパターン認識
- 複雑な問題に対する仮説形成と検証
- インシデント対応と事後分析手順

**例**:

1. **データベース接続障害**: 接続プール、ネットワーク タイムアウト、リソース制限にわたる断続的な障害をトレースします。
2. **支払い処理エラー**: APIログ、データベースの状態、外部サービスの応答を通じてトランザクションの失敗を調査します。
3. **パフォーマンスの低下**: メトリクスの相関関係、リソースの使用状況、コードの変更を通じて、段階的な速度低下を分析します。

**最適な担当者**: パフォーマンス エンジニア (パフォーマンスの問題)、セキュリティ エンジニア (セキュリティ インシデント)、品質エンジニア (テストの失敗)

---

### 品質エンジニア ✅

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#quality-engineer-)

**専門分野**:自動化とカバレッジに重点を置いた包括的なテスト戦略と品質保証

**自動アクティベーション**:

- キーワード: 「テスト」、「テスト」、「品質」、「QA」、「検証」、「カバレッジ」、「自動化」
- コンテキスト: テスト計画、品質ゲート、検証要件
- 品質に関する懸念: コードカバレッジ <80%、テスト自動化の欠如、品質の問題

**機能**:

- テスト戦略設計（ユニット、統合、E2E、パフォーマンステスト）
- テスト自動化フレームワークの実装とCI/CD統合
- 品質指標の定義と監視（カバレッジ、欠陥率）
- エッジケースの特定と境界テストのシナリオ
- アクセシビリティテストとコンプライアンス検証

**例**:

1. **Eコマーステスト**: ユーザーフロー、支払い処理、在庫管理を網羅した包括的なテストスイート
2. **API テスト**: REST/GraphQL API の自動契約テスト、負荷テスト、セキュリティ テスト
3. **アクセシビリティ検証**：自動および手動のアクセシビリティ監査による WCAG 2.1 準拠テスト

**最適な職種**: セキュリティ エンジニア (セキュリティ テスト)、パフォーマンス エンジニア (負荷テスト)、フロントエンド アーキテクト (UI テスト)

---

### リファクタリングの専門家 🔧

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#refactoring-expert-)

**専門分野**：体系的なリファクタリングと技術的負債管理によるコード品質の改善

**自動アクティベーション**:

- キーワード: 「リファクタリング」、「クリーンコード」、「技術的負債」、「SOLID」、「保守性」、「コード臭」
- コンテキスト: レガシーコードの改善、アーキテクチャの更新、コード品質の問題
- 品質指標: 複雑性が高い、コードの重複がある、テスト範囲が狭い

**機能**:

- SOLID原則の適用と設計パターンの実装
- コードの臭いの特定と体系的な排除
- レガシーコードの近代化戦略と移行計画
- 技術的負債の評価と優先順位付けのフレームワーク
- コード構造の改善とアーキテクチャのリファクタリング

**例**:

1. **レガシーモダナイゼーション**: テスト容易性を向上させたモノリシックアプリケーションをモジュール型アーキテクチャに変換する
2. **デザインパターン**: 支払い処理に戦略パターンを実装して結合を減らし、拡張性を向上させる
3. **コードのクリーンアップ**: 重複したコードを削除し、命名規則を改善し、再利用可能なコンポーネントを抽出します。

**最適な組み合わせ**: system-architect (アーキテクチャの改善)、quality-engineer (テスト戦略)、python-expert (言語固有のパターン)

### 専門開発エージェント 🎯

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#specialized-development-agents-)

### Python エキスパート 🐍

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#python-expert-)

**専門分野**: 最新のフレームワークとパフォーマンスを重視した、本番環境対応の Python 開発

**自動アクティベーション**:

- キーワード: 「Python」、「Django」、「FastAPI」、「Flask」、「asyncio」、「pandas」、「pytest」
- ファイルタイプ: .py、requirements.txt、pyproject.toml、Pipfile
- コンテキスト: Python 開発タスク、API 開発、データ処理、テスト

**機能**:

- 最新のPythonアーキテクチャパターンとフレームワークの選択
- asyncio と並行未来を用いた非同期プログラミング
- プロファイリングとアルゴリズムの改善によるパフォーマンスの最適化
- pytest、フィクスチャ、テスト自動化によるテスト戦略
- pip、poetry、Docker を使用したパッケージ管理とデプロイメント

**例**:

1. **FastAPI マイクロサービス**: Pydantic 検証、依存性注入、OpenAPI ドキュメントを備えた高性能非同期 API
2. **データ パイプライン**: エラー処理、ログ記録、大規模データセットの並列処理を備えた Pandas ベースの ETL
3. **Django アプリケーション**: カスタム ユーザー モデル、API エンドポイント、包括的なテスト カバレッジを備えたフルスタック Web アプリ

**最適な職種**: バックエンド アーキテクト (API 設計)、品質エンジニア (テスト)、パフォーマンス エンジニア (最適化)

---

### 要件アナリスト 📝

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#requirements-analyst-)

**専門分野**：体系的なステークホルダー分析による要件発見と仕様策定

**自動アクティベーション**:

- キーワード: 「要件」、「仕様」、「PRD」、「ユーザーストーリー」、「機能」、「スコープ」、「ステークホルダー」
- 背景: プロジェクトの開始、不明確な要件、スコープ定義の必要性
- 複雑さ: 複数の利害関係者が関わるプロジェクト、不明確な目標、相反する要件

**機能**:

- ステークホルダーへのインタビューやワークショップを通じた要件抽出
- 受け入れ基準と完了の定義を含むユーザーストーリーの記述
- 機能仕様と非機能仕様のドキュメント
- ステークホルダー分析と要件優先順位付けフレームワーク
- スコープ管理と変更管理プロセス

**例**:

1. **製品要件ドキュメント**: ユーザー ペルソナ、機能仕様、成功指標を含む、フィンテック モバイル アプリの包括的な PRD
2. **API仕様**: エラー処理、セキュリティ、パフォーマンス基準を含む支払い処理APIの詳細な要件
3. **移行要件**: データ移行、ユーザートレーニング、ロールバック手順を含むレガシーシステムの近代化要件

**最適な組み合わせ**: システムアーキテクト (技術的実現可能性)、テクニカルライター (ドキュメント作成)、学習ガイド (ユーザーガイダンス)

### コミュニケーションと学習エージェント 📚

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#communication--learning-agents-)

### テクニカルライター 📚

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#technical-writer-)

**専門分野**: 視聴者分析と明確さを重視した技術文書作成とコミュニケーション

**自動アクティベーション**:

- キーワード: 「ドキュメント」、「Readme」、「API ドキュメント」、「ユーザー ガイド」、「テクニカル ライティング」、「マニュアル」
- コンテキスト: ドキュメントのリクエスト、API ドキュメント、ユーザー ガイド、技術的な説明
- ファイルタイプ: .md、.rst、API 仕様、ドキュメント ファイル

**機能**:

- 技術文書のアーキテクチャと情報設計
- さまざまなスキルレベルに合わせたオーディエンス分析とコンテンツターゲティング
- 動作例と統合ガイダンスを含む API ドキュメント
- ステップバイステップの手順とトラブルシューティングを記載したユーザーガイドの作成
- アクセシビリティ基準の適用と包括的な言語の使用

**例**:

1. **APIドキュメント**: 認証、エンドポイント、例、SDK統合ガイドを含む包括的なREST APIドキュメント
2. **ユーザーマニュアル**: スクリーンショット、トラブルシューティング、FAQセクションを含むステップバイステップのインストールおよび構成ガイド
3. **技術仕様**: 図、データフロー、実装の詳細を含むシステムアーキテクチャドキュメント

**最適な組み合わせ**: requirements-analyst (仕様の明確化)、learning-guide (教育コンテンツ)、frontend-architect (UI ドキュメント)

---

### 学習ガイド 🎓

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#learning-guide-)

**専門分野**：スキル開発とメンターシップに重点を置いた教育コンテンツの設計と漸進的学習

**自動アクティベーション**:

- キーワード: 「説明」、「学習」、「チュートリアル」、「初心者」、「指導」、「教育」、「トレーニング」
- コンテキスト: 教育的なリクエスト、概念の説明、スキル開発、学習パス
- 複雑さ: 段階的な分解と段階的な理解を必要とする複雑なトピック

**機能**:

- 段階的なスキル開発を伴う学習パスの設計
- 類推と例による複雑な概念の説明
- 実践的な演習を含むインタラクティブなチュートリアルの作成
- スキル評価と能力評価のフレームワーク
- メンターシップ戦略と個別学習アプローチ

**例**:

1. **プログラミングチュートリアル**: 実践的な演習、コード例、段階的な複雑さを備えたインタラクティブな React チュートリアル
2. **概念の説明**: 視覚的な図と練習問題を使った実際の例を通してデータベースの正規化を説明します
3. **スキル評価**：実践的なプロジェクトとフィードバックによるフルスタック開発のための包括的な評価フレームワーク

**最適な対象者**: テクニカルライター (教育ドキュメント)、フロントエンドアーキテクト (インタラクティブ学習)、要件アナリスト (学習目標)

---

## エージェントの調整と統合 🤝

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#agent-coordination--integration-)

### 調整パターン

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#coordination-patterns)

**アーキテクチャチーム**:

- **フルスタック開発**：フロントエンドアーキテクト + バックエンドアーキテクト + セキュリティエンジニア + 品質エンジニア
- **システム設計**: システムアーキテクト + DevOps アーキテクト + パフォーマンスエンジニア + セキュリティエンジニア
- **レガシーモダナイゼーション**：リファクタリング専門家 + システムアーキテクト + 品質エンジニア + テクニカルライター

**品質チーム**:

- **セキュリティ監査**: セキュリティエンジニア + 品質エンジニア + 根本原因アナリスト + 要件アナリスト
- **パフォーマンス最適化**: パフォーマンスエンジニア + システムアーキテクト + DevOps アーキテクト + 根本原因アナリスト
- **テスト戦略**: 品質エンジニア + セキュリティエンジニア + パフォーマンスエンジニア + フロントエンドアーキテクト

**コミュニケーションチーム**:

- **ドキュメンテーションプロジェクト**: テクニカルライター + 要件アナリスト + 学習ガイド + ドメインエキスパート
- **学習プラットフォーム**: 学習ガイド + フロントエンドアーキテクト + テクニカルライター + 品質エンジニア
- **APIドキュメント**: バックエンドアーキテクト + テクニカルライター + セキュリティエンジニア + 品質エンジニア

### MCP サーバー統合

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#mcp-server-integration)

**MCP サーバーによる拡張機能**:

- **コンテキスト7** : すべての建築家と専門家のための公式ドキュメントパターン
- **シーケンシャル**: 根本原因アナリスト、システムアーキテクト、パフォーマンスエンジニア向けの多段階分析
- **マジック**：フロントエンドアーキテクト、学習ガイドインタラクティブコンテンツのためのUI生成
- **Playwright** : 品質エンジニア向けのブラウザテスト、フロントエンドアーキテクト向けのアクセシビリティ検証
- **Morphllm** : refactoring-expert のコード変換、python-expert の一括変更
- **Serena** : すべてのエージェントのプロジェクトメモリ、セッション間のコンテキスト保存

### エージェントのアクティベーションのトラブルシューティング

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#troubleshooting-agent-activation)

## トラブルシューティング

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#troubleshooting)

トラブルシューティングのヘルプについては、以下を参照してください。

- [よくある問題](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Reference/common-issues.md)- よくある問題に対するクイック修正
- [トラブルシューティングガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Reference/troubleshooting.md)- 包括的な問題解決

### よくある問題

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#common-issues)

- **エージェントのアクティベーションなし**: ドメインキーワード「セキュリティ」、「パフォーマンス」、「フロントエンド」を使用します
- **間違ったエージェントが選択されました**: エージェントのドキュメントでトリガーキーワードを確認してください
- **エージェントが多すぎる場合**：主要ドメインのキーワードに焦点を当てるか、`/sc:focus [domain]`
- **エージェントが連携していない**: タスクの複雑さを増やすか、マルチドメインキーワードを使用する
- **エージェントの専門知識の不一致**: より具体的な技術用語を使用する

### 即時修正

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#immediate-fixes)

- **エージェントの強制アクティベーション**: リクエストで明示的なドメインキーワードを使用する
- **エージェントの選択をリセット**: エージェントの状態をリセットするには、Claude Code セッションを再起動します。
- **エージェントのパターンを確認する**: エージェントのドキュメントでトリガーキーワードを確認する
- **基本的なアクティベーションをテストする**:`/sc:implement "security auth"`セキュリティエンジニアのテストを試みる

### エージェント固有のトラブルシューティング

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#agent-specific-troubleshooting)

**セキュリティエージェントなし:**

```shell
# Problem: Security concerns not triggering security-engineer
# Quick Fix: Use explicit security keywords
"implement authentication"              # Generic - may not trigger
"implement JWT authentication security" # Explicit - triggers security-engineer
"secure user login with encryption"    # Security focus - triggers security-engineer
```

**パフォーマンスエージェントなし:**

```shell
# Problem: Performance issues not triggering performance-engineer
# Quick Fix: Use performance-specific terminology
"make it faster"                       # Vague - may not trigger
"optimize slow database queries"       # Specific - triggers performance-engineer  
"reduce API latency and bottlenecks"   # Performance focus - triggers performance-engineer
```

**アーキテクチャエージェントなし:**

```shell
# Problem: System design not triggering architecture agents
# Quick Fix: Use architectural keywords
"build an app"                         # Generic - triggers basic agents
"design microservices architecture"    # Specific - triggers system-architect
"scalable distributed system design"   # Architecture focus - triggers system-architect
```

**間違ったエージェントの組み合わせ:**

```shell
# Problem: Getting frontend agent for backend tasks
# Quick Fix: Use domain-specific terminology
"create user interface"                # May trigger frontend-architect
"create REST API endpoints"            # Specific - triggers backend-architect
"implement server-side authentication" # Backend focus - triggers backend-architect
```

### サポートレベル

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#support-levels)

**クイックフィックス:**

- エージェントトリガーテーブルから明示的なドメインキーワードを使用する
- Claude Codeセッションを再起動してみてください
- 混乱を避けるために単一のドメインに焦点を当てる

**詳細なヘルプ:**

- エージェントのインストールに関する問題については、[一般的な問題ガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Reference/common-issues.md)を参照してください。
- 対象エージェントのトリガーキーワードを確認する

**専門家によるサポート:**

- 使用`SuperClaude install --diagnose`
- 協調分析については[診断リファレンスガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Reference/diagnostic-reference.md)を参照してください

**コミュニティサポート:**

- [GitHub Issues](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues)で問題を報告してください[](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues)
- 予想されるエージェントのアクティベーションと実際のエージェントのアクティベーションの例を含める

### 成功の検証

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#success-validation)

エージェントの修正を適用した後、次のようにテストします。

- [ ] ドメイン固有のリクエストは適切なエージェントをアクティブ化します（セキュリティ → セキュリティ エンジニア）
- [ ] 複雑なタスクはマルチエージェント調整（3 つ以上のエージェント）をトリガーします
- [ ] エージェントの専門知識がタスク要件に一致している（API → バックエンドアーキテクト）
- [ ] 適切な場合に品質エージェントが自動的に含められます（セキュリティ、パフォーマンス、テスト）
- [ ] 回答はドメインの専門知識と専門知識を示す

## クイックトラブルシューティング（レガシー）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#quick-troubleshooting-legacy)

- **エージェントが有効化されていない場合**→ ドメインキーワード「セキュリティ」、「パフォーマンス」、「フロントエンド」を使用します
- **エージェントが間違っている**→ エージェントのドキュメントでトリガーキーワードを確認してください
- **エージェントが多すぎる**→ 主要ドメインのキーワードに焦点を絞る
- **エージェントが連携していない**→ タスクの複雑さを増やすか、マルチドメインキーワードを使用する

**エージェントがアクティブ化されない?**

1. **キーワードを確認する**: ドメイン固有の用語を使用する (例: セキュリティ エンジニアの場合は「ログイン」ではなく「認証」)
2. **コンテキストを追加**: ファイルの種類、フレームワーク、または特定のテクノロジーを含める
3. **複雑さの増大**：マルチドメインの問題はより多くのエージェントをトリガーします
4. **使用例**: エージェントの専門知識に合った具体的なシナリオを参照する

**エージェントが多すぎますか?**

- 主要なドメインのニーズにキーワードを集中させる
- `/sc:focus [domain]`範囲を制限するために使用する
- 特定のエージェントから始めて、必要に応じて拡張します

**エージェントが間違っていますか?**

- エージェントのドキュメントでトリガーキーワードを確認する
- 対象ドメインに対してより具体的な用語を使用する
- 明示的な要件または制約を追加する

## クイックリファレンス 📋

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#quick-reference-)

### エージェントトリガー検索

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#agent-trigger-lookup)

|トリガータイプ|キーワード/パターン|活性化エージェント|
|---|---|---|
|**安全**|「認証」、「セキュリティ」、「脆弱性」、「暗号化」|セキュリティエンジニア|
|**パフォーマンス**|「遅い」、「最適化」、「ボトルネック」、「レイテンシー」|パフォーマンスエンジニア|
|**フロントエンド**|「UI」、「React」、「Vue」、「コンポーネント」、「レスポンシブ」|フロントエンドアーキテクト|
|**バックエンド**|「API」、「サーバー」、「データベース」、「REST」、「GraphQL」|バックエンドアーキテクト|
|**テスト**|「テスト」、「QA」、「検証」、「カバレッジ」|品質エンジニア|
|**デブオプス**|「デプロイ」、「CI/CD」、「Docker」、「Kubernetes」|DevOpsアーキテクト|
|**建築**|「アーキテクチャ」、「マイクロサービス」、「スケーラビリティ」|システムアーキテクト|
|**パイソン**|「.py」、「Django」、「FastAPI」、「asyncio」|Pythonエキスパート|
|**問題**|「バグ」、「問題」、「デバッグ」、「トラブルシューティング」|根本原因分析者|
|**コード品質**|「リファクタリング」、「クリーンコード」、「技術的負債」|リファクタリングの専門家|
|**ドキュメント**|「ドキュメント」、「Readme」、「APIドキュメント」|テクニカルライター|
|**学ぶ**|「説明する」、「チュートリアル」、「初心者」、「教える」|学習ガイド|
|**要件**|「要件」、「PRD」、「仕様」|要件アナリスト|

### コマンドエージェントマッピング

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#command-agent-mapping)

|指示|主な薬剤|サポートエージェント|
|---|---|---|
|`/sc:implement`|ドメインアーキテクト（フロントエンド、バックエンド）|セキュリティエンジニア、品質エンジニア|
|`/sc:analyze`|品質エンジニア、セキュリティエンジニア|パフォーマンスエンジニア、根本原因アナリスト|
|`/sc:troubleshoot`|根本原因分析者|ドメインスペシャリスト、パフォーマンスエンジニア|
|`/sc:improve`|リファクタリングの専門家|品質エンジニア、パフォーマンスエンジニア|
|`/sc:document`|テクニカルライター|ドメインスペシャリスト、学習ガイド|
|`/sc:design`|システムアーキテクト|ドメインアーキテクト、要件アナリスト|
|`/sc:test`|品質エンジニア|セキュリティエンジニア、パフォーマンスエンジニア|
|`/sc:explain`|学習ガイド|テクニカルライター、ドメインスペシャリスト|

### 効果的な薬剤の組み合わせ

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#effective-agent-combinations)

**開発ワークフロー**:

- Web アプリケーション: フロントエンド アーキテクト + バックエンド アーキテクト + セキュリティ エンジニア + 品質エンジニア + DevOps アーキテクト
- API開発: バックエンドアーキテクト + セキュリティエンジニア + テクニカルライター + 品質エンジニア
- データ プラットフォーム: Python エキスパート + パフォーマンス エンジニア + セキュリティ エンジニア + システム アーキテクト

**分析ワークフロー**:

- セキュリティ監査: セキュリティエンジニア + 品質エンジニア + 根本原因アナリスト + テクニカルライター
- パフォーマンス調査: パフォーマンスエンジニア + 根本原因アナリスト + システムアーキテクト + DevOps アーキテクト
- レガシー評価: リファクタリング専門家 + システムアーキテクト + 品質エンジニア + セキュリティエンジニア + テクニカルライター

**コミュニケーションワークフロー**:

- 技術ドキュメント: テクニカルライター + 要件アナリスト + ドメインエキスパート + 学習ガイド
- 教育コンテンツ: 学習ガイド + テクニカルライター + フロントエンドアーキテクト + 品質エンジニア

## ベストプラクティス💡

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#best-practices-)

### はじめに（シンプルなアプローチ）

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#getting-started-simple-approach)

**自然言語ファースト:**

1. **目標を記述する**: ドメイン固有のキーワードを含む自然言語を使用する
2. **信頼の自動アクティベーション**: システムが適切なエージェントに自動的にルーティングできるようにします
3. **パターンから学ぶ**: さまざまなリクエストタイプに対してどのエージェントがアクティブになるかを観察する
4. **反復と改良**: 専門エージェントを追加するために詳細度を追加します

### エージェントの選択の最適化

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#optimizing-agent-selection)

**効果的なキーワードの使用法:**

- **特定 > 汎用**: セキュリティエンジニアの場合は「ログイン」の代わりに「認証」を使用します
- **技術用語**: フレームワーク名、テクノロジー、具体的な課題など
- **コンテキストヒント**: ファイルの種類、プロジェクトの範囲、複雑さの指標について言及する
- **品質キーワード**: 包括的なカバレッジのために「セキュリティ」、「パフォーマンス」、「アクセシビリティ」を追加します

**リクエストの最適化の例:**

```shell
# Generic (limited agent activation)
"Fix the login feature"

# Optimized (multi-agent coordination)  
"Implement secure JWT authentication with rate limiting and accessibility compliance"
# → Triggers: security-engineer + backend-architect + frontend-architect + quality-engineer
```

### 一般的な使用パターン

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#common-usage-patterns)

**開発ワークフロー:**

```shell
# Full-stack feature development
/sc:implement "responsive user dashboard with real-time notifications"
# → frontend-architect + backend-architect + performance-engineer

# API development with documentation
/sc:create "REST API for payment processing with comprehensive docs"  
# → backend-architect + security-engineer + technical-writer + quality-engineer

# Performance optimization investigation
/sc:troubleshoot "slow database queries affecting user experience"
# → performance-engineer + root-cause-analyst + backend-architect
```

**分析ワークフロー:**

```shell
# Security assessment
/sc:analyze "authentication system for GDPR compliance vulnerabilities"
# → security-engineer + quality-engineer + requirements-analyst

# Code quality review  
/sc:review "legacy codebase for modernization opportunities"
# → refactoring-expert + system-architect + quality-engineer + technical-writer

# Learning and explanation
/sc:explain "microservices patterns with hands-on examples"
# → system-architect + learning-guide + technical-writer
```

### 高度なエージェント調整

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#advanced-agent-coordination)

**マルチドメインプロジェクト:**

- **幅広く始める**：システムレベルのキーワードから始めて、建築エージェントの関心を引く
- **特異性の追加**: 専門エージェントを活性化するためにドメイン固有のニーズを含める
- **品質統合**: セキュリティ、パフォーマンス、テストの観点を自動的に含めます
- **ドキュメントの包含**: 包括的なカバレッジのために学習またはドキュメントのニーズを追加します

**エージェントの選択に関するトラブルシューティング:**

**問題: 間違ったエージェントがアクティブ化される**

- 解決策: より具体的なドメイン用語を使用する
- 例:「データベース最適化」→ パフォーマンスエンジニア + バックエンドアーキテクト

**問題: エージェントが足りない**

- 解決策: 複雑性指標とクロスドメインキーワードを増やす
- 例: リクエストに「セキュリティ」、「パフォーマンス」、「ドキュメント」を追加する

**問題: エージェントが多すぎる**

- 解決策: 特定の技術用語を含む主要ドメインに焦点を当てる
- 例: スコープを制限するには「/sc:focus backend」を使用します

### 品質重視の開発

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#quality-driven-development)

**セキュリティ第一のアプローチ:** 開発リクエストには常にセキュリティに関する考慮事項を含め、ドメインスペシャリストとともにセキュリティエンジニアを自動的に関与させます。

**パフォーマンス統合:** パフォーマンス キーワード (「高速」、「効率的」、「スケーラブル」) を含めて、最初からパフォーマンス エンジニアの調整を確実にします。

**アクセシビリティ コンプライアンス:** 「accessible」、「WCAG」、または「inclusive」を使用して、フロントエンド開発にアクセシビリティ検証を自動的に含めます。

**ドキュメント文化:** テクニカルライターの自動的な参加と知識の移転のリクエストに「ドキュメント化」、「説明」、または「チュートリアル」を追加します。

---

## エージェントインテリジェンスを理解する🧠

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#understanding-agent-intelligence-)

### エージェントを効果的にする要素

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#what-makes-agents-effective)

**ドメイン専門知識**: 各エージェントは、それぞれのドメインに特有の専門的な知識パターン、行動アプローチ、問題解決方法論を備えています。

**コンテキスト アクティベーション**: エージェントは、キーワードだけでなくリクエストのコンテキストを分析して、関連性とエンゲージメント レベルを判断します。

**協調的インテリジェンス**: 複数のエージェントの調整により、個々のエージェントの能力を超える相乗的な結果が生まれます。

**適応学習**: リクエストパターンと成功した調整結果に基づいてエージェントの選択が改善されます。

### エージェント vs. 従来のAI

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#agent-vs-traditional-ai)

**従来のアプローチ**: 単一のAIが、さまざまなレベルの専門知識を持つすべてのドメインを処理します。 **エージェントアプローチ**: 専門のエキスパートが、深いドメイン知識と集中的な問題解決で協力します。

**利点**：

- ドメイン固有のタスクにおける高い精度
- より洗練された問題解決方法論
- 専門家によるレビューによる品質保証の向上
- 協調的な多角的分析

### システムを信頼し、パターンを理解する

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#trust-the-system-understand-the-patterns)

**期待すること**:

- 適切なドメイン専門家への自動ルーティング
- 複雑なタスクのためのマルチエージェント調整
- 自動QAエージェントの組み込みによる品質統合
- 教育エージェントの活性化による学習機会

**心配する必要がないこと**：

- エージェントの手動選択または構成
- 複雑なルーティングルールやエージェント管理
- エージェントの構成または調整
- エージェントとのやり取りを細かく管理する

---

## 関連リソース 📚

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#related-resources-)

### 必須ドキュメント

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#essential-documentation)

- **[コマンドガイド](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/commands.md)**- 最適なエージェント調整をトリガーするSuperClaudeコマンドをマスターする
- **[MCP サーバー](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/mcp-servers.md)**- 専用ツールの統合によるエージェント機能の強化
- **[セッション管理](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/session-management.md)**- 永続的なエージェントコンテキストによる長期ワークフロー

### 高度な使用法

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#advanced-usage)

- **[行動モード](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/modes.md)**- エージェントの調整を強化するためのコンテキスト最適化
- **[はじめに](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Getting-Started/quick-start.md)**- エージェントの最適化のための専門家のテクニック
- **[例のクックブック](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Reference/examples-cookbook.md)**- 現実世界のエージェントの調整パターン

### 開発リソース

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#development-resources)

- **[技術アーキテクチャ](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Developer-Guide/technical-architecture.md)**- SuperClaude のエージェント システム設計を理解する
- **[貢献](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/Developer-Guide/contributing-code.md)**- エージェントの機能と調整パターンの拡張

---

## エージェントとしての道のり 🚀

[](https://github.com/khayashi4337/SuperClaude_Framework/blob/master/docs/User-Guide/agents.md#your-agent-journey-)

**第1週：自然な使用法** 自然な言語による説明から始めましょう。どのエージェントが、そしてなぜアクティブになるのかに注目しましょう。プロセスを考えすぎずに、キーワードのパターンに対する直感を養います。

**第2～3週：パターン認識**  
エージェントの連携パターンを観察します。複雑さとドメインキーワードがエージェントの選択にどのような影響を与えるかを理解します。連携を向上させるために、リクエストの表現を最適化します。

**2ヶ月目以降：エキスパートコーディネーション** 最適なエージェントの組み合わせをトリガーするマルチドメインリクエストをマスターします。トラブルシューティング手法を活用して効果的なエージェント選定を行います。複雑なワークフローには高度なパターンを使用します。

**SuperClaudeのメリット：** 14名の専門AIエキスパートが、シンプルな自然言語によるリクエストに連携して対応します。設定や管理は不要で、ニーズに合わせて拡張できるインテリジェントな連携を実現します。

🎯**インテリジェントエージェントコーディネーションを体験する準備はできましたか？まずは`/sc:implement`、専門的な AI コラボレーションの魔法を発見してください。**