<div align="center">

# 🚀 SuperClaudeフレームワーク

### **Claude Codeを構造化開発プラットフォームに変換**

<p align="center">
  <img src="https://img.shields.io/badge/version-4.2.0-blue" alt="Version">
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

| **コマンド** | **エージェント** | **モード** | **MCPサーバー** |
|:------------:|:----------:|:---------:|:---------------:|
| **30** | **16** | **7** | **8** |
| スラッシュコマンド | 専門AI | 動作モード | 統合サービス |

ブレインストーミングからデプロイまでの完全な開発ライフサイクルをカバーする30のスラッシュコマンド。

</div>

---

<div align="center">

## 🎯 **概要**

SuperClaudeは**メタプログラミング設定フレームワーク**で、動作指示の注入とコンポーネント統制を通じて、Claude Codeを構造化開発プラットフォームに変換します。強力なツールとインテリジェントエージェントを備えたシステム化されたワークフロー自動化を提供します。


## 免責事項

このプロジェクトはAnthropicと関連または承認されていません。
Claude Codeは[Anthropic](https://www.anthropic.com/)によって構築および維持されている製品です。

## 📖 **開発者および貢献者向け**

**SuperClaudeフレームワークを使用するための重要なドキュメント：**

| ドキュメント | 目的 | いつ読むか |
|----------|---------|--------------|
| **[PLANNING.md](PLANNING.md)** | アーキテクチャ、設計原則、絶対的なルール | セッション開始時、実装前 |
| **[TASK.md](TASK.md)** | 現在のタスク、優先順位、バックログ | 毎日、作業開始前 |
| **[KNOWLEDGE.md](KNOWLEDGE.md)** | 蓄積された知見、ベストプラクティス、トラブルシューティング | 問題に遭遇したとき、パターンを学習するとき |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | 貢献ガイドライン、ワークフロー | PRを提出する前 |

> **💡 プロのヒント**：Claude Codeはセッション開始時にこれらのファイルを読み取り、プロジェクト標準に沿った一貫性のある高品質な開発を保証します。

## ⚡ **クイックインストール**

> **重要**：古いドキュメントで説明されているTypeScriptプラグインシステムは
> まだ利用できません（v5.0で予定）。v4.xの現在のインストール
> 手順については、以下の手順に従ってください。

### **現在の安定バージョン (v4.2.0)**

SuperClaudeは現在スラッシュコマンドを使用しています。

**オプション1：pipx（推奨）**
```bash
# PyPIからインストール
pipx install superclaude

# コマンドをインストール（/research、/index-repo、/agent、/recommendをインストール）
superclaude install

# インストールを確認
superclaude install --list
superclaude doctor
```

インストール後、Claude Codeを再起動してコマンドを使用します：
- `/sc:research` - 並列検索による深いウェブ研究
- `/sc:index-repo` - コンテキスト最適化のためのリポジトリインデックス作成
- `/sc:agent` - 専門AIエージェント
- `/sc:recommend` - コマンド推奨
- `/sc` - 利用可能なすべてのSuperClaudeコマンドを表示

**オプション2：Gitから直接インストール**
```bash
# リポジトリをクローン
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework

# インストールスクリプトを実行
./install.sh
```

### **v5.0で提供予定（開発中）**

新しいTypeScriptプラグインシステムを積極的に開発中です（詳細は[#419](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues/419)を参照）。リリース後、インストールは次のように簡略化されます：

```bash
# この機能はまだ利用できません
/plugin marketplace add SuperClaude-Org/superclaude-plugin-marketplace
/plugin install superclaude
```

**ステータス**：開発中。ETAは未定です。

### **パフォーマンス向上（オプションのMCP）**

**2〜3倍**高速な実行と**30〜50%**少ないトークンのために、オプションでMCPサーバーをインストールできます：

```bash
# パフォーマンス向上のためのオプションのMCPサーバー（airis-mcp-gateway経由）：
# - Serena: コード理解（2〜3倍高速）
# - Sequential: トークン効率的な推論（30〜50%少ないトークン）
# - Tavily: 深い研究のためのウェブ検索
# - Context7: 公式ドキュメント検索
# - Mindbase: すべての会話にわたるセマンティック検索（オプションの拡張）

# 注：エラー学習は組み込みのReflexionMemoryを介して利用可能（インストール不要）
# Mindbaseはセマンティック検索の拡張を提供（「recommended」プロファイルが必要）
# MCPサーバーのインストール：https://github.com/agiletec-inc/airis-mcp-gateway
# 詳細はdocs/mcp/mcp-integration-policy.mdを参照
```

**パフォーマンス比較：**
- **MCPなし**：完全に機能、標準パフォーマンス ✅
- **MCPあり**：2〜3倍高速、30〜50%少ないトークン ⚡

</div>

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

## 🎉 **V4.1の新機能**

> *バージョン4.1は、スラッシュコマンドアーキテクチャの安定化、エージェント機能の強化、ドキュメントの改善に焦点を当てています。*

<table>
<tr>
<td width="50%">

### 🤖 **よりスマートなエージェントシステム**
ドメイン専門知識を持つ**16の専門エージェント**：
- PM Agentは体系的なドキュメントを通じて継続的な学習を保証
- 自律的なウェブ研究のための深い研究エージェント
- セキュリティエンジニアが実際の脆弱性をキャッチ
- フロントエンドアーキテクトがUIパターンを理解
- コンテキストに基づく自動調整
- オンデマンドでドメイン固有の専門知識

</td>
<td width="50%">

### ⚡ **最適化されたパフォーマンス**
**より小さなフレームワーク、より大きなプロジェクト：**
- フレームワークフットプリントの削減
- コードのためのより多くのコンテキスト
- より長い会話が可能
- 複雑な操作の有効化

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **MCPサーバー統合**
**8つの強力なサーバー**（airis-mcp-gateway経由）：
- **Tavily** → プライマリウェブ検索（深い研究）
- **Serena** → セッション持続性とメモリ
- **Mindbase** → セッション横断学習（ゼロフットプリント）
- **Sequential** → トークン効率的な推論
- **Context7** → 公式ドキュメント検索
- **Playwright** → JavaScript重量コンテンツ抽出
- **Magic** → UIコンポーネント生成
- **Chrome DevTools** → パフォーマンス分析

</td>
<td width="50%">

### 🎯 **動作モード**
異なるコンテキストのための**7つの適応モード**：
- **ブレインストーミング** → 適切な質問をする
- **ビジネスパネル** → 多専門家戦略分析
- **深い研究** → 自律的なウェブ研究
- **オーケストレーション** → 効率的なツール調整
- **トークン効率** → 30-50%のコンテキスト節約
- **タスク管理** → システム化された組織
- **内省** → メタ認知分析

</td>
</tr>
<tr>
<td width="50%">

### 📚 **ドキュメントの全面見直し**
**開発者のための完全な書き直し：**
- 実際の例とユースケース
- 一般的な落とし穴の文書化
- 実用的なワークフローを含む
- より良いナビゲーション構造

</td>
<td width="50%">

### 🧪 **安定性の強化**
**信頼性に焦点：**
- コアコマンドのバグ修正
- テストカバレッジの改善
- より堅牢なエラー処理
- CI/CDパイプラインの改善

</td>
</tr>
</table>

</div>

---

<div align="center">

## 🔬 **深い研究機能**

### **DRエージェントアーキテクチャに準拠した自律的ウェブ研究**

SuperClaude v4.2は、自律的、適応的、インテリジェントなウェブ研究を可能にする包括的な深い研究機能を導入します。

<table>
<tr>
<td width="50%">

### 🎯 **適応的計画**
**3つのインテリジェント戦略：**
- **計画のみ**：明確なクエリに対する直接実行
- **意図計画**：曖昧なリクエストの明確化
- **統一**：協調的な計画の洗練（デフォルト）

</td>
<td width="50%">

### 🔄 **マルチホップ推論**
**最大5回の反復検索：**
- エンティティ拡張（論文 → 著者 → 作品）
- 概念深化（トピック → 詳細 → 例）
- 時間的進行（現在 → 歴史）
- 因果連鎖（効果 → 原因 → 予防）

</td>
</tr>
<tr>
<td width="50%">

### 📊 **品質スコアリング**
**信頼度ベースの検証：**
- ソースの信頼性評価（0.0-1.0）
- カバレッジの完全性追跡
- 統合の一貫性評価
- 最小しきい値：0.6、目標：0.8

</td>
<td width="50%">

### 🧠 **ケースベース学習**
**セッション横断インテリジェンス：**
- パターン認識と再利用
- 時間経過による戦略最適化
- 成功したクエリ式の保存
- パフォーマンス改善追跡

</td>
</tr>
</table>

### **研究コマンドの使用**

```bash
# 自動深度での基本研究
/research "2024年の最新AI開発"

# 制御された研究深度（TypeScriptのオプション経由）
/research "量子コンピューティングのブレークスルー"  # depth: exhaustive

# 特定の戦略選択
/research "市場分析"  # strategy: planning-only

# ドメインフィルタリング研究（Tavily MCP統合）
/research "Reactパターン"  # domains: reactjs.org,github.com
```

### **研究深度レベル**

| 深度 | ソース | ホップ | 時間 | 最適な用途 |
|:-----:|:-------:|:----:|:----:|----------|
| **クイック** | 5-10 | 1 | ~2分 | 簡単な事実、単純なクエリ |
| **標準** | 10-20 | 3 | ~5分 | 一般的な研究（デフォルト） |
| **深い** | 20-40 | 4 | ~8分 | 包括的な分析 |
| **徹底的** | 40+ | 5 | ~10分 | 学術レベルの研究 |

### **統合ツールオーケストレーション**

深い研究システムは複数のツールをインテリジェントに調整します：
- **Tavily MCP**：プライマリウェブ検索と発見
- **Playwright MCP**：複雑なコンテンツ抽出
- **Sequential MCP**：マルチステップ推論と統合
- **Serena MCP**：メモリと学習の持続性
- **Context7 MCP**：技術ドキュメント検索

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

- 🎯 [**スラッシュコマンド**](docs/user-guide/commands.md)
  *完全な `/sc` コマンドリスト*

- 🤖 [**エージェントガイド**](docs/user-guide/agents.md)
  *16の専門エージェント*

- 🎨 [**動作モード**](docs/user-guide/modes.md)
  *7つの適応モード*

- 🚩 [**フラグガイド**](docs/user-guide/flags.md)
  *動作制御パラメータ*

- 🔧 [**MCPサーバー**](docs/user-guide/mcp-servers.md)
  *8つのサーバー統合*

- 💼 [**セッション管理**](docs/user-guide/session-management.md)
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
---

## 📋 **全30コマンド**

<details>
<summary><b>完全なコマンドリストを展開</b></summary>

### 🧠 計画と設計 (4)
- `/brainstorm` - 構造化ブレインストーミング
- `/design` - システムアーキテクチャ
- `/estimate` - 時間/工数見積もり
- `/spec-panel` - 仕様分析

### 💻 開発 (5)
- `/implement` - コード実装
- `/build` - ビルドワークフロー
- `/improve` - コード改善
- `/cleanup` - リファクタリング
- `/explain` - コード説明

### 🧪 テストと品質 (4)
- `/test` - テスト生成
- `/analyze` - コード分析
- `/troubleshoot` - デバッグ
- `/reflect` - 振り返り

### 📚 ドキュメント (2)
- `/document` - ドキュメント生成
- `/help` - コマンドヘルプ

### 🔧 バージョン管理 (1)
- `/git` - Git操作

### 📊 プロジェクト管理 (3)
- `/pm` - プロジェクト管理
- `/task` - タスク追跡
- `/workflow` - ワークフロー自動化

### 🔍 研究と分析 (2)
- `/research` - 深いウェブ研究
- `/business-panel` - ビジネス分析

### 🎯 ユーティリティ (9)
- `/agent` - AIエージェント
- `/index-repo` - リポジトリインデックス
- `/index` - インデックスエイリアス
- `/recommend` - コマンド推奨
- `/select-tool` - ツール選択
- `/spawn` - 並列タスク
- `/load` - セッション読み込み
- `/save` - セッション保存
- `/sc` - 全コマンド表示

[**📖 詳細なコマンドリファレンスを表示 →**](docs/reference/commands-list.md)

</details>
