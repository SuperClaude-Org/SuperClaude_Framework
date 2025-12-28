# 推奨コマンド集

## インストール・セットアップ
```bash
# 推奨インストール方法
pipx install SuperClaude
pipx upgrade SuperClaude
SuperClaude install

# または pip
pip install SuperClaude
pip install --upgrade SuperClaude
SuperClaude install

# コンポーネント一覧
SuperClaude install --list-components

# 特定コンポーネントのインストール
SuperClaude install --components core
SuperClaude install --components mcp --force
```

## 開発環境セットアップ
```bash
# 仮想環境作成（推奨）
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# または
.venv\Scripts\activate     # Windows

# 開発用依存関係インストール
pip install -e ".[dev]"

# テスト用依存関係のみ
pip install -e ".[test]"
```

## テスト実行
```bash
# すべてのテスト実行
pytest

# 詳細モード
pytest -v

# カバレッジ付き
pytest --cov=superclaude --cov=setup --cov-report=html

# 特定のテストファイル
pytest tests/test_installer.py

# 特定のテスト関数
pytest tests/test_installer.py::test_function_name

# 遅いテストを除外
pytest -m "not slow"

# 統合テストのみ
pytest -m integration
```

## コード品質チェック
```bash
# フォーマット確認（実行しない）
black --check .

# フォーマット適用
black .

# 型チェック
mypy superclaude setup

# リンター実行
flake8 superclaude setup

# すべての品質チェックを実行
black . && mypy superclaude setup && flake8 superclaude setup && pytest
```

## パッケージビルド
```bash
# ビルド環境クリーンアップ
rm -rf dist/ build/ *.egg-info

# パッケージビルド
python -m build

# ローカルインストールでテスト
pip install -e .

# PyPI公開（メンテナーのみ）
python -m twine upload dist/*
```

## Git操作
```bash
# ステータス確認（必須）
git status
git branch

# フィーチャーブランチ作成
git checkout -b feature/your-feature-name

# 変更をコミット
git add .
git diff --staged  # コミット前に確認
git commit -m "feat: add new feature"

# プッシュ
git push origin feature/your-feature-name
```

## macOS（Darwin）固有コマンド
```bash
# ファイル検索
find . -name "*.py" -type f

# コンテンツ検索
grep -r "pattern" ./

# ディレクトリリスト
ls -la

# シンボリックリンク確認
ls -lh ~/.claude

# Python3がデフォルト
python3 --version
pip3 --version
```

## SuperClaude使用例
```bash
# コマンド一覧表示
/sc:help

# セッション管理
/sc:load    # セッション復元
/sc:save    # セッション保存

# 開発コマンド
/sc:implement "feature description"
/sc:test
/sc:analyze @file.py
/sc:research "topic"

# エージェント活用
@agent-backend "create API endpoint"
@agent-security "review authentication"
```
