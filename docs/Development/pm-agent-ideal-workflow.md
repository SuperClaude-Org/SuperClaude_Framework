# PM Agent - Ideal Autonomous Workflow

> **目的**: 何百回も同じ指示を繰り返さないための自律的オーケストレーションシステム

## 🎯 解決すべき問題

### 現状の課題
- **繰り返し指示**: 同じことを何百回も説明している
- **同じミスの反復**: 一度間違えたことを再度間違える
- **知識の喪失**: セッションが途切れると学習内容が失われる
- **コンテキスト制限**: 限られたコンテキストで効率的に動作できていない

### あるべき姿
**自律的で賢いPM Agent** - ドキュメントから学び、計画し、実行し、検証し、学習を記録するループ

---

## 📋 完璧なワークフロー（理想形）

### Phase 1: 📖 状況把握（Context Restoration）

```yaml
1. ドキュメント読み込み:
   優先順位:
     1. タスク管理ドキュメント → 進捗確認
        - docs/development/tasks/current-tasks.md
        - 前回どこまでやったか
        - 次に何をすべきか

     2. アーキテクチャドキュメント → 仕組み理解
        - docs/development/architecture-*.md
        - このプロジェクトの構造
        - インストールフロー
        - コンポーネント連携

     3. 禁止事項・ルール → 制約確認
        - CLAUDE.md（グローバル）
        - PROJECT/CLAUDE.md（プロジェクト固有）
        - docs/development/constraints.md

     4. 過去の学び → 同じミスを防ぐ
        - docs/mistakes/ （失敗記録）
        - docs/patterns/ （成功パターン）

2. ユーザーリクエスト理解:
   - 何をしたいのか
   - どこまで進んでいるのか
   - 何が課題なのか
```

### Phase 2: 🔍 調査・分析（Research & Analysis）

```yaml
1. 既存実装の理解:
   # ソースコード側（Git管理）
   - setup/components/*.py → インストールロジック
   - superclaude/ → ランタイムロジック
   - tests/ → テストパターン

   # インストール後（ユーザー環境・Git管理外）
   - ~/.claude/commands/sc/ → 実際の配置確認
   - ~/.claude/*.md → 現在の仕様確認

   理解内容:
   「なるほど、ここでこう処理されて、
    こういうファイルが ~/.claude/ に作られるのね」

2. ベストプラクティス調査:
   # Deep Research活用
   - 公式リファレンス確認
   - 他プロジェクトの実装調査
   - 最新のベストプラクティス

   気づき:
   - 「ここ無駄だな」
   - 「ここ古いな」
   - 「これはいい実装だな」
   - 「この共通化できるな」

3. 重複・改善ポイント発見:
   - ライブラリの共通化可能性
   - 重複実装の検出
   - コード品質向上余地
```

### Phase 3: 📝 計画立案（Planning）

```yaml
1. 改善仮説作成:
   # このプロジェクト内で（Git管理）
   File: docs/development/hypothesis-YYYY-MM-DD.md

   内容:
   - 現状の問題点
   - 改善案
   - 期待される効果（トークン削減、パフォーマンス向上等）
   - 実装方針
   - 必要なテスト

2. ユーザーレビュー:
   「こういうプランでこんなことをやろうと思っています」

   提示内容:
   - 調査結果のサマリー
   - 改善提案（理由付き）
   - 実装ステップ
   - 期待される成果

   ユーザー承認待ち → OK出たら実装へ
```

### Phase 4: 🛠️ 実装（Implementation）

```yaml
1. ソースコード修正:
   # Git管理されているこのプロジェクトで作業
   cd ~/github/SuperClaude_Framework

   修正対象:
   - setup/components/*.py → インストールロジック
   - superclaude/ → ランタイム機能
   - setup/data/*.json → 設定データ

   # サブエージェント活用
   - backend-architect: アーキテクチャ実装
   - refactoring-expert: コード改善
   - quality-engineer: テスト設計

2. 実装記録:
   File: docs/development/experiment-YYYY-MM-DD.md

   内容:
   - 試行錯誤の記録
   - 遭遇したエラー
   - 解決方法
   - 気づき
```

### Phase 5: ✅ 検証（Validation）

```yaml
1. テスト作成・実行:
   # テストを書く
   Write tests/test_new_feature.py

   # テスト実行
   pytest tests/test_new_feature.py -v

   # ユーザー要求を満たしているか確認
   - 期待通りの動作か？
   - エッジケースは？
   - パフォーマンスは？

2. エラー時の対応:
   エラー発生
   ↓
   公式リファレンス確認
   「このエラー何でだろう？」
   「ここの定義違ってたんだ」
   ↓
   修正
   ↓
   再テスト
   ↓
   合格まで繰り返し

3. 動作確認:
   # インストールして実際の環境でテスト
   SuperClaude install --dev

   # 動作確認
   claude  # 起動して実際に試す
```

### Phase 6: 📚 学習記録（Learning Documentation）

```yaml
1. 成功パターン記録:
   File: docs/patterns/[pattern-name].md

   内容:
   - どんな問題を解決したか
   - どう実装したか
   - なぜこのアプローチか
   - 再利用可能なパターン

2. 失敗・ミス記録:
   File: docs/mistakes/mistake-YYYY-MM-DD.md

   内容:
   - どんなミスをしたか
   - なぜ起きたか
   - 防止策
   - チェックリスト

3. タスク更新:
   File: docs/development/tasks/current-tasks.md

   内容:
   - 完了したタスク
   - 次のタスク
   - 進捗状況
   - ブロッカー

4. グローバルパターン更新:
   必要に応じて:
   - CLAUDE.md更新（グローバルルール）
   - PROJECT/CLAUDE.md更新（プロジェクト固有）
```

### Phase 7: 🔄 セッション保存（Session Persistence）

```yaml
1. Serenaメモリー保存:
   write_memory("session_summary", 完了内容)
   write_memory("next_actions", 次のアクション)
   write_memory("learnings", 学んだこと)

2. ドキュメント整理:
   - docs/temp/ → docs/patterns/ or docs/mistakes/
   - 一時ファイル削除
   - 正式ドキュメント更新
```

---

## 🔧 活用可能なツール・リソース

### MCPサーバー（フル活用）
- **Sequential**: 複雑な分析・推論
- **Context7**: 公式ドキュメント参照
- **Tavily**: Deep Research（ベストプラクティス調査）
- **Serena**: セッション永続化、メモリー管理
- **Playwright**: E2Eテスト、動作確認
- **Morphllm**: 一括コード変換
- **Magic**: UI生成（必要時）
- **Chrome DevTools**: パフォーマンス測定

### サブエージェント（適材適所）
- **requirements-analyst**: 要件整理
- **system-architect**: アーキテクチャ設計
- **backend-architect**: バックエンド実装
- **refactoring-expert**: コード改善
- **security-engineer**: セキュリティ検証
- **quality-engineer**: テスト設計・実行
- **performance-engineer**: パフォーマンス最適化
- **technical-writer**: ドキュメント執筆

### 他プロジェクト統合
- **makefile-global**: Makefile標準化パターン
- **airis-mcp-gateway**: MCPゲートウェイ統合
- その他有用なパターンは積極的に取り込む

---

## 🎯 重要な原則

### Git管理の区別
```yaml
✅ Git管理されている（変更追跡可能）:
  - ~/github/SuperClaude_Framework/
  - ここで全ての変更を行う
  - コミット履歴で追跡
  - PR提出可能

❌ Git管理外（変更追跡不可）:
  - ~/.claude/
  - 読むだけ、理解のみ
  - テスト時のみ一時変更（必ず戻す！）
```

### テスト時の注意
```bash
# テスト前: 必ずバックアップ
cp ~/.claude/commands/sc/pm.md ~/.claude/commands/sc/pm.md.backup

# テスト実行
# ... 検証 ...

# テスト後: 必ず復元！！
mv ~/.claude/commands/sc/pm.md.backup ~/.claude/commands/sc/pm.md
```

### ドキュメント構造
```
docs/
├── Development/          # 開発用ドキュメント
│   ├── tasks/           # タスク管理
│   ├── architecture-*.md # アーキテクチャ
│   ├── constraints.md   # 制約・禁止事項
│   ├── hypothesis-*.md  # 改善仮説
│   └── experiment-*.md  # 実験記録
├── patterns/            # 成功パターン（清書後）
├── mistakes/            # 失敗記録と防止策
└── (既存のuser-guide等)
```

---

## 🚀 実装優先度

### Phase 1（必須）
1. ドキュメント構造整備
2. タスク管理システム
3. セッション復元ワークフロー

### Phase 2（重要）
4. 自己評価・検証ループ
5. 学習記録自動化
6. エラー時再学習フロー

### Phase 3（強化）
7. PMO機能（重複検出、共通化提案）
8. パフォーマンス測定・改善
9. 他プロジェクト統合

---

## 📊 成功指標

### 定量的指標
- **繰り返し指示の削減**: 同じ指示 → 50%削減目標
- **ミス再発率**: 同じミス → 80%削減目標
- **セッション復元時間**: <30秒で前回の続きから開始

### 定性的指標
- ユーザーが「前回の続きから」と言うだけで再開できる
- 過去のミスを自動的に避けられる
- 公式ドキュメント参照が自動化されている
- 実装→テスト→検証が自律的に回る

---

## 💡 次のアクション

このドキュメント作成後:
1. 既存のインストールロジック理解（setup/components/）
2. タスク管理ドキュメント作成（docs/development/tasks/）
3. PM Agent実装修正（このワークフローを実際に実装）

このドキュメント自体が**PM Agentの憲法**となる。
