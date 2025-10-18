# README Translation Guide

## 概要

SuperClaude は **Neural CLI** を使用してローカルで高速翻訳を実現しています。

## 🎯 特徴

- **✅ 完全ローカル実行** - API キー不要
- **🚀 高速翻訳** - Ollama + qwen2.5:3b
- **💰 無料** - クラウド API 不要
- **🔒 プライバシー** - データは外部送信されない

## 🔧 セットアップ

### 1. Ollama インストール

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# モデルダウンロード
ollama pull qwen2.5:3b
```

### 2. Neural CLI ビルド (初回のみ)

```bash
cd ~/github/neural/src-tauri
cargo build --bin neural-cli --release
```

**ビルド済みバイナリ**: `~/github/neural/src-tauri/target/release/neural-cli`

## 📝 使用方法

### 自動翻訳 (推奨)

```bash
cd ~/github/SuperClaude_Framework
make translate
```

**実行内容**:
1. neural-cli を自動インストール (~/.local/bin/)
2. README.md → README-zh.md (簡体字中国語)
3. README.md → README-ja.md (日本語)

### 手動翻訳

```bash
neural-cli translate README.md \
  --from English \
  --to "Simplified Chinese" \
  --output README-zh.md

neural-cli translate README.md \
  --from English \
  --to Japanese \
  --output README-ja.md
```

### Ollama 接続確認

```bash
neural-cli health
```

**出力例**:
```
✅ Ollama is running at http://localhost:11434

📦 Available models:
  - qwen2.5:3b
  - llama3:latest
  - ...
```

## ⚙️ 高度な設定

### カスタム Ollama URL

```bash
neural-cli translate README.md \
  --from English \
  --to Japanese \
  --output README-ja.md \
  --ollama-url http://custom-host:11434
```

### 別モデル使用

```bash
neural-cli translate README.md \
  --from English \
  --to Japanese \
  --output README-ja.md \
  --model llama3:latest
```

## 🚫 トラブルシューティング

### エラー: "Failed to connect to Ollama"

**原因**: Ollama が起動していない

**解決策**:
```bash
# Ollama を起動
ollama serve

# 別ターミナルで確認
neural-cli health
```

### エラー: "Model not found: qwen2.5:3b"

**原因**: モデルがダウンロードされていない

**解決策**:
```bash
ollama pull qwen2.5:3b
```

### 翻訳品質が低い

**改善策**:
1. **より大きなモデルを使用**:
   ```bash
   ollama pull qwen2.5:7b
   neural-cli translate README.md --model qwen2.5:7b ...
   ```

2. **プロンプトを調整**: `neural/src-tauri/src/bin/cli.rs` の `translate_text` 関数を編集

3. **温度パラメータを調整**:
   ```rust
   "temperature": 0.1,  // より保守的な翻訳
   "temperature": 0.5,  // より自由な翻訳
   ```

## 📊 パフォーマンス

| ファイルサイズ | 翻訳時間 (qwen2.5:3b) | メモリ使用量 |
|:-------------:|:---------------------:|:------------:|
| 5KB README    | ~30秒                 | ~2GB         |
| 10KB README   | ~1分                  | ~2GB         |
| 20KB README   | ~2分                  | ~2GB         |

**システム要件**:
- RAM: 最低4GB (推奨8GB)
- ストレージ: ~2GB (モデル用)
- CPU: Apple Silicon or x86_64

## 🔗 関連リンク

- [Ollama Documentation](https://ollama.com/docs)
- [Qwen2.5 Model](https://ollama.com/library/qwen2.5)
- [Neural CLI Source](~/github/neural)

## 🎯 ワークフロー例

### README 更新フロー

```bash
# 1. README.md を編集
vim README.md

# 2. 翻訳実行
make translate

# 3. 翻訳結果を確認
git diff README-zh.md README-ja.md

# 4. 必要に応じて手動調整
vim README-ja.md

# 5. コミット
git add README.md README-zh.md README-ja.md
git commit -m "docs: update README and translations"
```

### 大規模翻訳バッチ

```bash
# 複数ファイルを一括翻訳
for file in docs/*.md; do
  neural-cli translate "$file" \
    --from English \
    --to Japanese \
    --output "${file%.md}-ja.md"
done
```

## 💡 Tips

1. **Ollama をバックグラウンドで常時起動**:
   ```bash
   # macOS (LaunchAgent)
   brew services start ollama
   ```

2. **翻訳前にチェック**:
   ```bash
   neural-cli health  # Ollama 接続確認
   ```

3. **翻訳後の品質チェック**:
   - マークダウン構造が保持されているか
   - コードブロックが正しいか
   - リンクが機能するか

4. **Git diff で確認**:
   ```bash
   git diff README-ja.md | grep -E "^\+|^\-" | less
   ```
