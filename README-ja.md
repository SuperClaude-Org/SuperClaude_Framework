<div align="center">

# 🚀 SuperClaudeフレームワーク

### **Claude Codeを構造化開発プラットフォームに変換**

<p align="center">
  <img src="https://img.shields.io/badge/version-4.1.5-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

<p align="center">
  <a href="https://superclaude.netlify.app/">
    <img src="https://img.shields.io/badge/🌐_ウェブサイトを訪問-blue" alt="Website">
  </a>
  <a href="https://pypi.org/project/superclaude/">
    <img src="https://img.shields.io/pypi/v/SuperClaude.svg?" alt="PyPI">
  </a>
  <a href="https://www.npmjs.com/package/@bifrost_inc/superclaude">
    <img src="https://img.shields.io/npm/v/@bifrost_inc/superclaude.svg" alt="npm">
  </a>
</p>

<!-- Language Selector -->
<p align="center">
  <a href="README.md">
    <img src="https://img.shields.io/badge/🇺🇸_English-blue" alt="English">
  </a>
  <a href="README-zh.md">
    <img src="https://img.shields.io/badge/🇨🇳_中文-red" alt="中文">
  </a>
  <a href="README-ja.md">
    <img src="https://img.shields.io/badge/🇯🇵_日本語-green" alt="日本語">
  </a>
</p>

<p align="center">
  <a href="#-クイックインストール">クイックスタート</a> •
  <a href="#-プロジェクトを支援">支援</a> •
  <a href="#-v4の新機能">新機能</a> •
  <a href="#-ドキュメント">ドキュメント</a> •
  <a href="#-貢献">貢献</a>
</p>

</div>

---

<div align="center">

## 📊 **フレームワーク統計**

| **コマンド数** | **エージェント** | **モード** | **MCPサーバー** |
|:------------:|:----------:|:---------:|:---------------:|
| **21** | **14** | **5** | **6** |
| スラッシュコマンド | 専門AI | 動作モード | 統合サービス |

</div>

---

<div align="center">

## 🎯 **概要**

SuperClaudeは**メタプログラミング設定フレームワーク**で、動作指示の注入とコンポーネント統制を通じて、Claude Codeを構造化開発プラットフォームに変換します。強力なツールとインテリジェントエージェントを備えたシステム化されたワークフロー自動化を提供します。

## ⚡ **クイックインストール**

### **インストール方法を選択**

| 方法 | コマンド | 最適な用途 |
|:------:|---------|----------|
| **🐍 pipx** | `pipx install SuperClaude && pipx upgrade SuperClaude && SuperClaude install` | **✅ 推奨** - Linux/macOS |
| **📦 pip** | `pip install SuperClaude && pip upgrade SuperClaude && SuperClaude install` | 従来のPython環境 |
| **🌐 npm** | `npm install -g @bifrost_inc/superclaude && superclaude install` | クロスプラットフォーム、Node.jsユーザー |

</div>

<details>
<summary><b>⚠️ 重要：SuperClaude V3からのアップグレード</b></summary>

**SuperClaude V3がインストールされている場合は、V4をインストールする前にアンインストールする必要があります：**

```bash
# V3を最初にアンインストール
関連するファイルとディレクトリをすべて削除：
*.md *.json および commands/

# その後V4をインストール
pipx install SuperClaude && pipx upgrade SuperClaude && SuperClaude install
```

**✅ アップグレード時に保持される内容：**
- ✓ カスタムスラッシュコマンド（`commands/sc/`外のもの）
- ✓ `CLAUDE.md`内のカスタム内容
- ✓ Claude Codeの`.claude.json`、`.credentials.json`、`settings.json`、`settings.local.json`
- ✓ 追加したカスタムエージェントとファイル

**⚠️ 注意：** V3の他のSuperClaude関連`.json`ファイルは競合を引き起こす可能性があるため削除してください。

</details>

<details>
<summary><b>💡 PEP 668エラーのトラブルシューティング</b></summary>

```bash
# オプション1：pipxを使用（推奨）
pipx install SuperClaude

# オプション2：ユーザーインストール
pip install --user SuperClaude

# オプション3：強制インストール（注意して使用）
pip install --break-system-packages SuperClaude
```
</details>

---

<div align="center">

## 💖 **プロジェクトを支援**

> 正直に言うと、SuperClaudeの維持には時間とリソースが必要です。
> 
> *Claude Maxサブスクリプションだけでもテスト用に月100ドルかかり、それに加えてドキュメント、バグ修正、機能開発に費やす時間があります。*
> *日常の作業でSuperClaudeの価値を感じていただけるなら、プロジェクトの支援をご検討ください。*
> *数ドルでも基本コストをカバーし、開発を継続することができます。*
> 
> コード、フィードバック、または支援を通じて、すべての貢献者が重要です。このコミュニティの一員でいてくれてありがとう！🙏

<table>
<tr>
<td align="center" width="33%">
  
### ☕ **Ko-fi**
[![Ko-fi](https://img.shields.io/badge/Support_on-Ko--fi-ff5e5b?logo=ko-fi)](https://ko-fi.com/superclaude)

*一回限りの貢献*

</td>
<td align="center" width="33%">

### 🎯 **Patreon**
[![Patreon](https://img.shields.io/badge/Become_a-Patron-f96854?logo=patreon)](https://patreon.com/superclaude)

*月額支援*

</td>
<td align="center" width="33%">

### 💜 **GitHub**
[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsor-30363D?logo=github-sponsors)](https://github.com/sponsors/SuperClaude-Org)

*柔軟な階層*

</td>
</tr>
</table>

### **あなたの支援により可能になること：**

| 項目 | コスト/影響 |
|------|-------------|
| 🔬 **Claude Maxテスト** | 検証とテスト用に月100ドル |
| ⚡ **機能開発** | 新機能と改善 |
| 📚 **ドキュメンテーション** | 包括的なガイドと例 |
| 🤝 **コミュニティサポート** | 迅速な問題対応とヘルプ |
| 🔧 **MCP統合** | 新しいサーバー接続のテスト |
| 🌐 **インフラストラクチャ** | ホスティングとデプロイメントのコスト |

> **注意：** ただし、プレッシャーはありません。フレームワークはいずれにしてもオープンソースのままです。人々がそれを使用し、評価していることを知るだけでもモチベーションになります。コード、ドキュメント、または情報の拡散による貢献も助けになります！🙏

</div>

---

<div align="center">

## 🎉 **V4の新機能**

> *バージョン4は、コミュニティフィードバックと実際の使用パターンに基づいて重要な改善をもたらします。*

<table>
<tr>
<td width="50%">

### 🤖 **よりスマートなエージェントシステム**
**14の専門エージェント**がドメイン専門知識を持ちます：
- セキュリティエンジニアが実際の脆弱性をキャッチ
- フロントエンドアーキテクトがUIパターンを理解
- コンテキストに基づく自動調整
- オンデマンドでドメイン固有の専門知識

</td>
<td width="50%">

### 📝 **改良された名前空間**
すべてのコマンドに**`/sc:`プレフィックス**：
- カスタムコマンドとの競合なし
- 完全なライフサイクルをカバーする21のコマンド
- ブレインストーミングからデプロイメントまで
- 整理されたコマンド構造

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **MCPサーバー統合**
**6つの強力なサーバー**が連携：
- **Context7** → 最新ドキュメント
- **Sequential** → 複雑な分析
- **Magic** → UIコンポーネント生成
- **Playwright** → ブラウザテスト
- **Morphllm** → 一括変換
- **Serena** → セッション持続

</td>
<td width="50%">

### 🎯 **動作モード**
異なるコンテキストのための**5つの適応モード**：
- **ブレインストーミング** → 適切な質問をする
- **オーケストレーション** → 効率的なツール調整
- **トークン効率** → 30-50%のコンテキスト節約
- **タスク管理** → システム化された組織
- **内省** → メタ認知分析

</td>
</tr>
<tr>
<td width="50%">

### ⚡ **最適化されたパフォーマンス**
**より小さなフレームワーク、より大きなプロジェクト：**
- フレームワークフットプリントの削減
- コードのためのより多くのコンテキスト
- より長い会話が可能
- 複雑な操作の有効化

</td>
<td width="50%">

### 📚 **ドキュメントの全面見直し**
**開発者のための完全な書き直し：**
- 実際の例とユースケース
- 一般的な落とし穴の文書化
- 実用的なワークフローを含む
- より良いナビゲーション構造

</td>
</tr>
</table>

</div>

---

<div align="center">

## 📚 **ドキュメント**

### **🇯🇵 SuperClaude完全日本語ガイド**

<table>
<tr>
<th align="center">🚀 はじめに</th>
<th align="center">📖 ユーザーガイド</th>
<th align="center">🛠️ 開発者リソース</th>
<th align="center">📋 リファレンス</th>
</tr>
<tr>
<td valign="top">

- 📝 [**クイックスタートガイド**](docs/getting-started/quick-start.md)  
  *すぐに開始*

- 💾 [**インストールガイド**](docs/getting-started/installation.md)  
  *詳細なセットアップ手順*

</td>
<td valign="top">

- 🎯 [**コマンドリファレンス**](docs/user-guide-jp/commands.md)  
  *全21のスラッシュコマンド*

- 🤖 [**エージェントガイド**](docs/user-guide-jp/agents.md)  
  *14の専門エージェント*

- 🎨 [**動作モード**](docs/user-guide-jp/modes.md)  
  *5つの適応モード*

- 🚩 [**フラグガイド**](docs/user-guide-jp/flags.md)  
  *動作制御パラメータ*

- 🔧 [**MCPサーバー**](docs/user-guide-jp/mcp-servers.md)  
  *6つのサーバー統合*

- 💼 [**セッション管理**](docs/user-guide-jp/session-management.md)  
  *状態の保存と復元*

</td>
<td valign="top">

- 🏗️ [**技術アーキテクチャ**](docs/developer-guide/technical-architecture.md)  
  *システム設計の詳細*

- 💻 [**コード貢献**](docs/developer-guide/contributing-code.md)  
  *開発ワークフロー*

- 🧪 [**テスト＆デバッグ**](docs/developer-guide/testing-debugging.md)  
  *品質保証*

</td>
<td valign="top">

- ✨ [**ベストプラクティス**](docs/reference/quick-start-practices.md)  
  *プロのコツとパターン*

- 📓 [**サンプル集**](docs/reference/examples-cookbook.md)  
  *実際の使用例*

- 🔍 [**トラブルシューティング**](docs/reference/troubleshooting.md)  
  *一般的な問題と修正*

</td>
</tr>
</table>

</div>

---

<div align="center">

## 🤝 **貢献**

### **SuperClaudeコミュニティに参加**

あらゆる種類の貢献を歓迎します！お手伝いできる方法は以下のとおりです：

| 優先度 | 領域 | 説明 |
|:--------:|------|-------------|
| 📝 **高** | ドキュメント | ガイドの改善、例の追加、タイプミス修正 |
| 🔧 **高** | MCP統合 | サーバー設定の追加、統合テスト |
| 🎯 **中** | ワークフロー | コマンドパターンとレシピの作成 |
| 🧪 **中** | テスト | テストの追加、機能の検証 |
| 🌐 **低** | 国際化 | ドキュメントの他言語への翻訳 |

<p align="center">
  <a href="CONTRIBUTING.md">
    <img src="https://img.shields.io/badge/📖_読む-貢献ガイド-blue" alt="Contributing Guide">
  </a>
  <a href="https://github.com/SuperClaude-Org/SuperClaude_Framework/graphs/contributors">
    <img src="https://img.shields.io/badge/👥_表示-すべての貢献者-green" alt="Contributors">
  </a>
</p>

</div>

---

<div align="center">

## ⚖️ **ライセンス**

このプロジェクトは**MITライセンス**の下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?" alt="MIT License">
</p>

</div>

---

<div align="center">

## ⭐ **Star履歴**

<a href="https://www.star-history.com/#SuperClaude-Org/SuperClaude_Framework&Timeline">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=SuperClaude-Org/SuperClaude_Framework&type=Timeline&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=SuperClaude-Org/SuperClaude_Framework&type=Timeline" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=SuperClaude-Org/SuperClaude_Framework&type=Timeline" />
 </picture>
</a>

</div>

---

<div align="center">

### **🚀 SuperClaudeコミュニティによって情熱をもって構築**

<p align="center">
  <sub>境界を押し広げる開発者のために❤️で作られました</sub>
</p>

<p align="center">
  <a href="#-superclaudeフレームワーク">トップに戻る ↑</a>
</p>

</div>