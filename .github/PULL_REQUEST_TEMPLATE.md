# Pull Request

## 概要

<!-- このPRの目的を簡潔に説明 -->

## 変更内容

<!-- 主な変更点をリストアップ -->
-

## 関連Issue

<!-- 関連するIssue番号があれば記載 -->
Closes #

## チェックリスト

### Git Workflow
- [ ] 外部貢献の場合: Fork → topic branch → upstream PR の流れに従った
- [ ] コラボレーターの場合: topic branch使用（main直コミットしていない）
- [ ] `git rebase upstream/main` 済み（コンフリクトなし）
- [ ] コミットメッセージは Conventional Commits に準拠（`feat:`, `fix:`, `docs:` など）

### Code Quality
- [ ] 変更は1目的に限定（巨大PRでない、目安: ~200行差分以内）
- [ ] 既存のコード規約・パターンに従っている
- [ ] 新機能/修正には適切なテストを追加
- [ ] Lint/Format/Typecheck すべてパス
- [ ] CI/CD パイプライン成功（グリーン状態）

### Security
- [ ] シークレット・認証情報をコミットしていない
- [ ] `.gitignore` で必要なファイルを除外済み
- [ ] 破壊的変更なし／ある場合は `!` 付きコミット + MIGRATION.md 記載

### Documentation
- [ ] 必要に応じてドキュメントを更新（README, CLAUDE.md, docs/など）
- [ ] 複雑なロジックにコメント追加
- [ ] APIの変更がある場合は適切に文書化

## テスト方法

<!-- このPRの動作確認方法 -->

## スクリーンショット（該当する場合）

<!-- UIの変更がある場合はスクリーンショットを添付 -->

## 備考

<!-- レビュワーに伝えたいこと、技術的な判断の背景など -->
