# テスト手順とCI/CD

## テスト構成

### pytest設定
- **テストディレクトリ**: `tests/`
- **テストファイルパターン**: `test_*.py`, `*_test.py`
- **テストクラス**: `Test*`
- **テスト関数**: `test_*`
- **オプション**: `-v --tb=short --strict-markers`

### カバレッジ設定
- **対象**: `superclaude/`, `setup/`
- **除外**: `*/tests/*`, `*/test_*`, `*/__pycache__/*`
- **目標**: 90%以上のカバレッジ
- **レポート**: `show_missing = true` で未カバー行を表示

### テストマーカー
- `@pytest.mark.slow`: 遅いテスト（`-m "not slow"`で除外可能）
- `@pytest.mark.integration`: 統合テスト

## 既存テストファイル
```
tests/
├── test_get_components.py      # コンポーネント取得テスト
├── test_install_command.py     # インストールコマンドテスト
├── test_installer.py           # インストーラーテスト
├── test_mcp_component.py       # MCPコンポーネントテスト
├── test_mcp_docs_component.py  # MCPドキュメントコンポーネントテスト
└── test_ui.py                  # UIテスト
```

## タスク完了時の必須チェックリスト

### 1. コード品質チェック
```bash
# フォーマット
black .

# 型チェック
mypy superclaude setup

# リンター
flake8 superclaude setup
```

### 2. テスト実行
```bash
# すべてのテスト
pytest -v

# カバレッジチェック（90%以上必須）
pytest --cov=superclaude --cov=setup --cov-report=term-missing
```

### 3. ドキュメント更新
- 機能追加 → 該当ドキュメントを更新
- API変更 → docstringを更新
- 使用例を追加

### 4. Git操作
```bash
# 変更確認
git status
git diff

# コミット前に必ず確認
git diff --staged

# Conventional Commitsに従う
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in X"
git commit -m "docs: update installation guide"
```

## CI/CD ワークフロー

### GitHub Actions
- **publish-pypi.yml**: PyPI自動公開
- **readme-quality-check.yml**: ドキュメント品質チェック

### ワークフロートリガー
- プッシュ時: リンター、テスト実行
- プルリクエスト: 品質チェック、カバレッジ確認
- タグ作成: PyPI自動公開

## 品質基準

### コード品質
- すべてのテスト合格必須
- 新機能は90%以上のテストカバレッジ
- 型ヒント完備
- エラーハンドリング実装

### ドキュメント品質
- パブリックAPIはドキュメント化必須
- 使用例を含める
- 段階的複雑さ（初心者→上級者）

### パフォーマンス
- 大規模プロジェクトでのパフォーマンス最適化
- クロスプラットフォーム互換性
- リソース効率の良い実装
