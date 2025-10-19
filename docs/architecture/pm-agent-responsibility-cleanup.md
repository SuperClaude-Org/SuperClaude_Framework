# PM Agent Responsibility Cleanup & MCP Integration

## 問題整理

### 1. 既存MODEとの重複

**MODE_Task_Management.md と pm-agent.md が完全重複**:

```yaml
MODE_Task_Management.md:
  - write_memory() / read_memory() 使用
  - Serena MCP依存
  - セッション開始時のlist_memories()
  - TodoWrite + memory並行管理

pm-agent.md:
  - docs/memory/ ファイル管理
  - ローカルファイルベース
  - セッション開始時のRead並行実行
  - TodoWrite + docs/memory/並行管理

結論: 完全に機能が重複、統合必須
```

### 2. Memory管理の責務が不明確

**現状の問題**:
```yaml
docs/memory/:
  - いつクリアするか決まってない
  - ファイルベース vs MCP memoryの使い分け不明
  - ライフサイクル管理なし

write_memory() (Serena MCP):
  - いつ使うべきか不明確
  - docs/memory/との使い分けなし
  - 削除タイミング不明
```

### 3. MCPの役割分担が曖昧

**ユーザーの指摘**:
- Serena = コード理解に使う
- Memory = Mindbaseに任せるべき
- 現状は役割が混在

## 解決策: 責務の明確化

### Memory Management Strategy

```yaml
Level 1 - Session Memory (Mindbase MCP):
  Purpose: 会話履歴の長期保存（Claude Code標準機能）
  Technology: Mindbase MCP (自動管理)
  Scope: 全プロジェクト横断
  Lifecycle: 永続（自動管理）
  Use Cases:
    - 過去の会話検索
    - 長期的なパターン学習
    - プロジェクト間の知識共有

Level 2 - Project Documentation (File-based):
  Purpose: プロジェクト固有の知識ベース
  Technology: Markdown files in docs/
  Scope: プロジェクトごと
  Lifecycle: Git管理（明示的削除まで永続）
  Locations:
    docs/patterns/: 成功パターン（永続）
    docs/mistakes/: 失敗記録（永続）
    CLAUDE.md: グローバルルール（永続）

Level 3 - Task State (Serena MCP - Code Understanding):
  Purpose: コードベース理解のためのシンボル管理
  Technology: Serena MCP
  Scope: セッション内
  Lifecycle: セッション終了で自動削除
  Use Cases:
    - コード構造の理解
    - シンボル間の関係追跡
    - リファクタリング支援

Level 4 - TodoWrite (Claude Code Built-in):
  Purpose: 現在のタスク進捗管理
  Technology: Claude Code標準機能
  Scope: セッション内
  Lifecycle: タスク完了で削除
  Use Cases:
    - 現在進行中のタスク追跡
    - サブタスクの管理
    - 進捗の可視化
```

### Memory Lifecycle Rules

```yaml
Session Start:
  1. Mindbaseから過去の関連会話を自動ロード（Claude Code標準）
  2. docs/patterns/ と docs/mistakes/ を読む（必要に応じて）
  3. CLAUDE.md を常に読む
  4. Serena: 使わない（コード理解時のみ）
  5. TodoWrite: 新規作成（必要なら）

During Work:
  1. Mindbase: 自動保存（Claude Code標準）
  2. docs/: 新しいパターン/ミスを文書化
  3. Serena: コード理解時のみ使用
  4. TodoWrite: 進捗更新

Session End:
  1. Mindbase: 自動保存（Claude Code標準）
  2. docs/: 学習内容を永続化
  3. Serena: 自動削除（何もしない）
  4. TodoWrite: 完了タスクはクリア

Monthly Maintenance:
  1. docs/patterns/: 古い（>6ヶ月）で未参照なら削除
  2. docs/mistakes/: 重複をマージ
  3. CLAUDE.md: ベストプラクティス抽出
```

### MCP Role Clarification

```yaml
Mindbase MCP (会話履歴):
  Auto-Managed: Claude Codeが自動管理
  PM Agent Role: なし（自動で動く）
  User Action: なし（透明）

Serena MCP (コード理解):
  Trigger: コードベース理解が必要な時のみ
  PM Agent Role: コード理解時に自動活用
  Examples:
    - リファクタリング計画
    - シンボル追跡
    - コード構造分析
  NOT for: タスク管理、会話記憶

Sequential MCP (複雑な推論):
  Trigger: 複雑な分析・設計が必要な時
  PM Agent Role: Commander modeで活用
  Examples:
    - アーキテクチャ設計
    - 複雑なデバッグ
    - システム分析

Context7 MCP (ドキュメント参照):
  Trigger: 公式ドキュメント参照が必要な時
  PM Agent Role: Pre-Implementation Confidence Check
  Examples:
    - ライブラリの使い方確認
    - ベストプラクティス参照
    - API仕様確認
```

## 統合後のPM Agent Architecture

### 削除すべきもの

```yaml
DELETE:
  1. docs/memory/ ディレクトリ全体
     理由: Mindbaseと重複、ライフサイクル不明確

  2. MODE_Task_Management.md の memory操作部分
     理由: pm-agent.mdと重複

  3. pm-agent.md の docs/memory/ 参照
     理由: Mindbaseに統合

  4. write_memory() / read_memory() 使用
     理由: Serenaはコード理解専用
```

### 統合後の責務

```yaml
PM Agent Core Responsibilities:

1. Session Lifecycle Management:
   Start:
     - Git status確認
     - CLAUDE.md読み込み
     - docs/patterns/ 最近5件読み込み
     - Mindbase自動ロード（Claude Code標準）

   End:
     - docs/patterns/ or docs/mistakes/ 更新
     - CLAUDE.md更新（必要なら）
     - Mindbase自動保存（Claude Code標準）

2. Documentation Guardian:
   - 実装前にdocs/patterns/とdocs/mistakes/を確認
   - 関連ドキュメントを自動読み込み
   - Pre-Implementation Confidence Check

3. Commander (Complex Tasks):
   - TodoWrite でタスク管理
   - Sequentialで複雑な分析
   - 並列実行の調整

4. Post-Implementation Documentation:
   - 成功パターン → docs/patterns/
   - 失敗記録 → docs/mistakes/
   - グローバルルール → CLAUDE.md

5. Mistake Handler (Reflexion):
   - docs/mistakes/ 検索（過去の失敗確認）
   - 新しいミス → docs/mistakes/ 文書化
   - 防止策の適用
```

### 簡潔な実装

**不要な複雑性の削除**:
```yaml
削除:
  - docs/memory/ 全体（Mindbaseで代替）
  - write_memory() 使用（Serenaはコード理解専用）
  - 複雑なメモリ管理ロジック

残す:
  - docs/patterns/（成功パターン）
  - docs/mistakes/（失敗記録）
  - CLAUDE.md（グローバルルール）
  - TodoWrite（進捗管理）
```

**シンプルな自動起動**:
```yaml
Session Start:
  1. git status && git branch
  2. Read CLAUDE.md
  3. Read docs/patterns/*.md (最近5件)
  4. Mindbase自動ロード（透明）
  5. 準備完了 → ユーザーリクエスト待機

実装前:
  1. 関連docs/patterns/とdocs/mistakes/読む
  2. Confidence Check
  3. Context7で公式ドキュメント確認（必要なら）

実装中:
  1. TodoWrite更新
  2. コード理解が必要 → Serena使用
  3. 複雑な分析 → Sequential使用

実装後:
  1. パターン抽出 → docs/patterns/
  2. ミス記録 → docs/mistakes/
  3. グローバルルール → CLAUDE.md
  4. Mindbase自動保存
```

## 移行手順

```yaml
Phase 1 - Cleanup:
  - [ ] docs/memory/ ディレクトリ削除
  - [ ] MODE_Task_Management.md からmemory操作削除
  - [ ] pm-agent.md からdocs/memory/参照削除

Phase 2 - MCP Role Clarification:
  - [ ] pm-agent.md にMCP使用ガイドライン追加
  - [ ] Serena = コード理解専用 明記
  - [ ] Mindbase = 自動管理 明記
  - [ ] Sequential = 複雑な分析 明記
  - [ ] Context7 = 公式ドキュメント参照 明記

Phase 3 - Documentation:
  - [ ] docs/patterns/README.md 作成（成功パターン記録ガイド）
  - [ ] docs/mistakes/README.md 作成（失敗記録ガイド）
  - [ ] Memory管理ポリシー文書化

Phase 4 - Testing:
  - [ ] セッション開始の自動ロードテスト
  - [ ] 実装前のドキュメント確認テスト
  - [ ] 実装後の文書化テスト
  - [ ] MCPの適切な使用テスト
```

## 利点

**シンプルさ**:
- ✅ Memory管理層が明確（Mindbase / File-based / TodoWrite）
- ✅ MCPの役割が明確（Serena=コード、Sequential=分析、Context7=ドキュメント）
- ✅ 不要な複雑性削除（docs/memory/削除、write_memory()削除）

**保守性**:
- ✅ ライフサイクルが明確（永続 vs セッション内）
- ✅ 責務分離（会話=Mindbase、知識=docs/、進捗=TodoWrite）
- ✅ 削除ルールが明確（月次メンテナンス）

**効率性**:
- ✅ 自動管理（Mindbase、Serena自動削除）
- ✅ 必要最小限のファイル読み込み
- ✅ 適切なMCP使用（コード理解時のみSerena）

## 結論

**削除**: docs/memory/全体、write_memory()使用、MODE_Task_Management.mdのmemory部分

**統合**: Mindbase（会話履歴）+ docs/（知識ベース）+ TodoWrite（進捗）+ Serena（コード理解）

**簡潔化**: 責務を明確にして、不要な複雑性を削除

これでPM Agentはシンプルかつ強力になります。
