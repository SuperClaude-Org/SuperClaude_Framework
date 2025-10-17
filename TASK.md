# SuperClaude Framework - Task List

最終更新: 2025-10-17

---

## 🔴 Critical（最優先）

### インポートパス修正
- [ ] **CLAUDE.md のインポートパス修正**
  - 問題: `@superclaude/MODE_*.md` → `modes/` プレフィックス欠落
  - 原因: コミット `4599b90` でディレクトリ再構成時に発生
  - 実際の場所: `superclaude/modes/MODE_*.md`
  - 影響: MODE定義が正しくロードされない
  - 対応: `.claude/CLAUDE.md` の全 `@superclaude/MODE_*` を `@superclaude/modes/MODE_*` に修正

### 並列実行機能の復元
- [ ] **PARALLEL ツール呼び出しの徹底**
  - 問題: Sequential実行されるべきでない操作がSequentialになっている
  - 要求: pm-agent.md および parallel-with-reflection.md の仕様通り
  - パターン: Wave → Checkpoint → Wave（並列→検証→並列）
  - 修正箇所: エージェント実装、モード定義

---

## 🟡 High Priority（重要）

### PM Agent自動起動
- [ ] **セッション開始時の自動起動実装**
  - 現状: 手動 `/sc:pm` 実行が必要
  - 目標: セッション開始時に自動実行
  - プロトコル:
    1. Read PLANNING.md, TASK.md, KNOWLEDGE.md
    2. Git status確認
    3. Token budget計算
    4. Confidence check
    5. Ready表示

### Business Panel遅延ロード
- [ ] **常時ロード削除によるトークン削減**
  - 現状: 4,169トークン常時消費
  - 目標: 必要時のみロード（`/sc:business-panel` コマンド実行時）
  - 効果: 起動トークン3,000+削減

### ドキュメント構造改善
- [x] **PLANNING.md 作成** (2025-10-17)
  - アーキテクチャ、ディレクトリ構成、絶対守るルール
- [ ] **TASK.md 作成** (進行中)
- [ ] **KNOWLEDGE.md 作成**
  - 蓄積された知見、調査結果、失敗パターン
- [ ] **README.md 更新**
  - 新ドキュメント構造への参照追加

---

## 🟢 Medium Priority（中優先度）

### スタートアッププロトコル再設計
- [ ] **ディレクトリ構造探索優先**
  - 現状: MODE定義を先にロード
  - 目標: プロジェクト構造を理解してからMODE適用
  - 順序:
    1. Git status、ディレクトリ構造把握
    2. PLANNING.md, TASK.md読み込み
    3. MODE定義ロード

### パフォーマンス検証
- [ ] **Before/After トークン使用量測定**
  - 測定項目:
    - セッション開始時のトークン使用量
    - Business Panel削除の効果
    - 並列実行の効率化
  - 目標: >3,000トークン削減を証明

---

## ⚪ Low Priority（低優先度）

### ドキュメント整理
- [ ] **重複ドキュメントの削除**
  - 対象: docs/ 内の古い・重複ファイル
  - 基準: PLANNING.md, TASK.md, KNOWLEDGE.mdと重複する内容
  - 保持: ユーザーガイド、開発者ガイド等の公式ドキュメント

### テストカバレッジ向上
- [ ] **PM Agent ユニットテスト**
  - 対象: tests/pm_agent/
  - カバレッジ目標: >80%

---

## ✅ Completed（完了）

### 2025-10-17
- [x] **ドキュメント再構成** (コミット `4599b90`, `edae4ac`)
  - `framework/business/research` ディレクトリへ移動
  - コンポーネント参照更新
- [x] **PM Agent動的トークン計算実装** (コミット `eb90e17`)
  - モジュラーアーキテクチャ
- [x] **Root cause調査完了** (checkpoint.json)
  - ディレクトリリファクタでCLAUDE.mdのインポートパス破損を特定
- [x] **PLANNING.md 作成**
  - アーキテクチャ、ディレクトリ構成、開発ルール完全版

---

## 📋 Future Backlog（将来の課題）

### 新機能
- [ ] Self-Improvement Loop完全実装
  - セッション開始プロトコル
  - 実行中の学習フロー
  - 定期振り返りメカニズム
- [ ] Context7 統合強化
  - 最新ドキュメント自動参照
- [ ] Deep Research エージェント改善
  - Multi-hop推論の精度向上

### インフラ
- [ ] CI/CD パイプライン整備
- [ ] 自動テスト実行環境

---

## 📝 Task Management Rules

### 新しいタスクの追加
```yaml
Format:
  - [ ] **タスク名**
    - 説明: 何をするか
    - 理由: なぜ必要か
    - 成功基準: 完了の定義

Priority:
  🔴 Critical: 即座に対応（バグ、ブロッカー）
  🟡 High: 近日中に対応（重要機能）
  🟢 Medium: 計画的に対応（改善）
  ⚪ Low: 余裕があれば対応（最適化）
```

### タスク完了時
```yaml
Action:
  1. チェックボックスにチェック [x]
  2. 完了日付を追記
  3. Completedセクションに移動
  4. 学んだことを KNOWLEDGE.md に追記
```

### タスクの優先度変更
```yaml
Trigger:
  - ブロッカー発生 → Critical昇格
  - 依存関係変化 → 優先度調整
  - ユーザー要求 → 優先度変更
```

---

**このファイルは生きているタスクリストです。**
**常に最新の状態に保ち、完了したタスクは速やかにCompletedセクションへ移動してください。**
