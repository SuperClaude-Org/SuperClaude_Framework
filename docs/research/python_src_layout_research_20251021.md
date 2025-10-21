# Python Src Layout Research - Repository vs Package Naming

**Date**: 2025-10-21
**Question**: Should `superclaude` repository use `src/superclaude/` (nested) or simpler structure?
**Confidence**: High (90%) - Based on official PyPA docs + real-world examples

---

## 🎯 Executive Summary

**結論**: `src/superclaude/` の二重ネストは**正しい**が、**必須ではない**

**あなたの感覚は正しい**：
- リポジトリ名 = パッケージ名が一般的
- `src/` layout自体は推奨されているが、パッケージ名の重複は避けられる
- しかし、PyPA公式例は `src/package_name/` を使用

**選択肢**：
1. **標準的** (PyPA推奨): `src/superclaude/` ← 今の構造
2. **シンプル** (可能): `src/` のみでモジュール直下に配置
3. **フラット** (古い): リポジトリ直下に `superclaude/`

---

## 📚 調査結果

### 1. PyPA公式ガイドライン

**ソース**: https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/

**公式例**:
```
project_root/
├── src/
│   └── awesome_package/    # ← パッケージ名で二重ネスト
│       ├── __init__.py
│       └── module.py
├── pyproject.toml
└── README.md
```

**PyPAの推奨**:
- `src/` layoutは**強く推奨** ("strongly suggested")
- 理由：
  1. ✅ インストール前に誤ったインポートを防ぐ
  2. ✅ パッケージングエラーを早期発見
  3. ✅ ユーザーがインストールする形式でテスト

**重要**: PyPAは `src/package_name/` の構造を**公式例として使用**

---

### 2. 実世界のプロジェクト調査

| プロジェクト | リポジトリ名 | 構造 | パッケージ名 | 備考 |
|------------|------------|------|------------|------|
| **Click** | `click` | ✅ `src/click/` | `click` | PyPA推奨通り |
| **FastAPI** | `fastapi` | ❌ フラット `fastapi/` | `fastapi` | ルート直下 |
| **setuptools** | `setuptools` | ❌ フラット `setuptools/` | `setuptools` | ルート直下 |

**パターン**:
- すべて **リポジトリ名 = パッケージ名**
- Clickのみ `src/` layout採用
- FastAPI/setuptoolsはフラット構造（古いプロジェクト）

---

### 3. なぜ二重ネストが標準なのか

**PyPA公式の構造例**:
```python
# プロジェクト: awesome_package
awesome_package/           # リポジトリ（GitHub名）
├── src/
│   └── awesome_package/   # Pythonパッケージ
│       ├── __init__.py
│       └── module.py
└── pyproject.toml
```

**理由**:
1. **明確な分離**: `src/` = インストール対象、その他 = 開発用
2. **命名規則**: パッケージ名は `import` 時に使うので、リポジトリ名と一致させる
3. **ツール対応**: hatchling/setuptoolsの `packages = ["src/package_name"]` 設定

---

### 4. あなたの感覚との比較

**あなたの疑問**:
> リポジトリ名が `superclaude` なのに、なぜ `src/superclaude/` と重複？

**答え**:
1. **リポジトリ名** (`superclaude`): GitHub上の名前、プロジェクト全体
2. **パッケージ名** (`src/superclaude/`): Pythonで `import superclaude` する際の名前
3. **重複は正常**: 同じ名前を使うのが**標準的なパターン**

**モノレポとの違い**:
- モノレポ: 複数パッケージを含む (`src/package1/`, `src/package2/`)
- SuperClaude: 単一パッケージなので、リポジトリ名 = パッケージ名

---

## 🔀 代替案の検討

### オプション 1: 現在の構造（PyPA推奨）

```
superclaude/                 # リポジトリ
├── src/
│   └── superclaude/         # パッケージ ← 二重ネスト
│       ├── __init__.py
│       ├── pm_agent/
│       └── cli/
├── tests/
└── pyproject.toml
```

**メリット**:
- ✅ PyPA公式推奨に完全準拠
- ✅ Clickなど最新プロジェクトと同じ構造
- ✅ パッケージングツールが期待する標準形式

**デメリット**:
- ❌ パス が長い: `src/superclaude/pm_agent/confidence.py`
- ❌ 一見冗長に見える

---

### オプション 2: フラット src/ 構造（非標準）

```
superclaude/                 # リポジトリ
├── src/
│   ├── __init__.py          # ← superclaude パッケージ
│   ├── pm_agent/
│   └── cli/
├── tests/
└── pyproject.toml
```

**pyproject.toml変更**:
```toml
[tool.hatch.build.targets.wheel]
packages = ["src"]  # ← src自体をパッケージとして扱う
```

**メリット**:
- ✅ パスが短い
- ✅ 重複感がない

**デメリット**:
- ❌ **非標準**: PyPA例と異なる
- ❌ **混乱**: `src/` がパッケージ名になる（`import src`?）
- ❌ ツール設定が複雑

---

### オプション 3: フラット layout（非推奨）

```
superclaude/                 # リポジトリ
├── superclaude/             # パッケージ ← ルート直下
│   ├── __init__.py
│   ├── pm_agent/
│   └── cli/
├── tests/
└── pyproject.toml
```

**メリット**:
- ✅ シンプル
- ✅ FastAPI/setuptoolsと同じ

**デメリット**:
- ❌ **PyPA非推奨**: 開発時にインストール版と競合リスク
- ❌ 古いパターン（新規プロジェクトは避けるべき）

---

## 💡 推奨事項

### 結論: **現在の構造を維持**

**理由**:
1. ✅ PyPA公式推奨に準拠
2. ✅ 最新ベストプラクティス（Click参照）
3. ✅ パッケージングツールとの相性が良い
4. ✅ 将来的にモノレポ化も可能

**あなたの疑問への回答**:
- 二重ネストは**意図的な設計**
- リポジトリ名（プロジェクト） ≠ パッケージ名（Python importable）
- 同じ名前を使うのが**慣例**だが、別々の概念

---

## 📊 エビデンス要約

| 項目 | 証拠 | 信頼性 |
|------|------|--------|
| PyPA推奨 | [公式ドキュメント](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) | ⭐⭐⭐⭐⭐ |
| 実例（Click） | [GitHub: pallets/click](https://github.com/pallets/click) | ⭐⭐⭐⭐⭐ |
| 実例（FastAPI） | [GitHub: fastapi/fastapi](https://github.com/fastapi/fastapi) | ⭐⭐⭐⭐ (古い構造) |
| 構造例 | [PyPA src-layout.rst](https://github.com/pypa/packaging.python.org/blob/main/source/discussions/src-layout-vs-flat-layout.rst) | ⭐⭐⭐⭐⭐ |

---

## 🎓 学んだこと

1. **src/ layoutの目的**: インストール前のテストを強制し、パッケージングエラーを早期発見
2. **二重ネストの理由**: `src/` = 配布対象の分離、`package_name/` = import時の名前
3. **業界標準**: 新しいプロジェクトは `src/package_name/` を採用すべき
4. **例外**: FastAPI/setuptoolsはフラット（歴史的理由）

---

## 🚀 アクションアイテム

**推奨**: 現在の構造を維持

**もし変更するなら**:
- [ ] `pyproject.toml` の `packages` 設定変更
- [ ] 全テストのインポートパス修正
- [ ] ドキュメント更新

**変更しない理由**:
- ✅ 現在の構造は正しい
- ✅ PyPA推奨に準拠
- ✅ 変更のメリットが不明確

---

**研究完了**: 2025-10-21
**信頼度**: High (90%)
**推奨**: **変更不要** - 現在の `src/superclaude/` 構造は最新ベストプラクティス
