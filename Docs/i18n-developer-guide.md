# SuperClaude i18n Developer Guide / SuperClaude i18n 开发者指南

## Overview / 概述

This guide is for SuperClaude framework developers who need to manage translations, add new languages, or maintain the i18n system.

本指南适用于需要管理翻译、添加新语言或维护i18n系统的SuperClaude框架开发者。

## 🚀 本地化部署概述 / Localization Deployment Overview

SuperClaude i18n system now provides **fully localized language switching** with no remote dependencies:

SuperClaude i18n系统现在提供**完全本地化的语言切换**，无需任何远程依赖：

### ✅ 本地化特性 / Localization Features
- **包内翻译** / **Package Translations**: 所有翻译文件随SuperClaude安装包一起分发 / All translation files distributed with SuperClaude installation package
- **即时切换** / **Instant Switching**: 语言切换无需网络连接或下载 / Language switching requires no network connection or downloads
- **包资源访问** / **Package Resource Access**: 使用Python `importlib.resources` 访问翻译文件 / Uses Python `importlib.resources` to access translation files
- **离线工作** / **Offline Operation**: 完全离线环境下可正常工作 / Works completely in offline environments

### 🔧 开发者与用户分离 / Developer-User Separation
- **开发者**: 管理API翻译、构建翻译文件、打包到安装包 / **Developers**: Manage API translations, build translation files, package into installation
- **用户**: 简单的语言切换命令，无需了解翻译过程 / **Users**: Simple language switching commands, no need to understand translation process

## API Translation Workflow / API 翻译工作流

### 1. Prerequisites / 前置条件

#### API Keys Setup / API密钥设置
```bash
# Qwen3 (推荐用于中文) / Qwen3 (Recommended for Chinese)
export QWEN_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
# 或者 / Or
export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"

# OpenRouter (支持多种模型) / OpenRouter (Multi-model support)
export OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx"
```

#### Environment Verification / 环境验证
```bash
# 检查环境配置 / Check environment configuration
python tools/i18n_build_tool.py --check

# 输出示例 / Example output:
# ✅ Qwen API: Available
# ✅ OpenRouter API: Available
# ✅ Cache directory: /Users/ray/workspace/SuperClaude/.superclaude/cache
# ✅ Content snapshot: /Users/ray/workspace/SuperClaude/.superclaude/incremental/content_snapshot.json
```

### 2. Full Translation Build / 完整翻译构建

#### Step 1: Extract Content / 步骤1：提取内容
```bash
# 创建英文基础文件 / Create English base file
python tools/i18n_build_tool.py --create-base

# 输出 / Output:
# Extracted 156 commands, 11 personas, 243 UI strings
# Created: i18n/locales/en_US.json
```

#### Step 2: Build Translations / 步骤2：构建翻译
```bash
# 构建所有语言 / Build all languages
python tools/i18n_build_tool.py --build-all --engine qwen

# 构建特定语言 / Build specific languages
python tools/i18n_build_tool.py --build zh_CN ja_JP --engine qwen

# 使用OpenRouter / Use OpenRouter
python tools/i18n_build_tool.py --build-all --engine openrouter --model claude-3-5-haiku-20241022
```

#### Step 3: Verify Quality / 步骤3：验证质量
```bash
# 查看构建报告 / View build report
python tools/quality_monitor.py report

# 输出示例 / Example output:
# Language: zh_CN
#   Quality Score: 0.963
#   Translation Cost: $0.0541
#   Cache Hit Rate: 85%
#   Build Time: 12.3s
```

### 3. Incremental Translation / 增量翻译

#### Automatic Detection / 自动检测
```bash
# 检测变更并更新 / Detect changes and update
python tools/i18n_build_tool.py --update

# 输出 / Output:
# Detected 3 changed items in 2 files
# Updating translations for: zh_CN, ja_JP, ko_KR...
# Cost saved by caching: $0.42 (87%)
```

#### Manual Incremental Update / 手动增量更新
```python
# test_incremental_system.py
import asyncio
from i18n.incremental import IncrementalTranslationManager

async def update_translations():
    manager = IncrementalTranslationManager()
    
    # 检测变更 / Detect changes
    changes = manager.detect_content_changes()
    print(f"Found {len(changes)} changes")
    
    # 仅翻译变更内容 / Translate only changes
    if changes:
        result = await manager.translate_changes(
            changes, 
            languages=["zh_CN", "ja_JP", "ko_KR"]
        )
        print(f"Translation cost: ${result['total_cost']:.4f}")
        print(f"Saved by incremental: ${result['saved_cost']:.4f}")

asyncio.run(update_translations())
```

### 4. Git Integration / Git 集成

#### Install Git Hooks / 安装Git钩子
```bash
# 安装翻译钩子 / Install translation hooks
python tools/install_hooks.py

# 钩子将自动在以下事件触发 / Hooks will trigger on:
# - pre-commit: 检测内容变更 / Detect content changes
# - post-commit: 触发增量翻译 / Trigger incremental translation
# - pre-push: 验证翻译质量 / Validate translation quality
```

#### Manual Hook Execution / 手动执行钩子
```bash
# 手动触发翻译钩子 / Manually trigger translation hook
python tools/hooks/translation_hook.py

# 跳过自动翻译 / Skip auto-translation
git commit --no-verify -m "Skip translation for this commit"
```

### 5. Cache Management / 缓存管理

#### View Cache Statistics / 查看缓存统计
```bash
python tools/i18n_build_tool.py --cache-stats

# 输出 / Output:
# Cache Statistics:
#   Total entries: 1,847
#   Cache size: 2.3 MB
#   Hit rate: 82.5%
#   Avg save per hit: $0.0023
#   Total saved: $4.25
```

#### Clear Cache / 清理缓存
```bash
# 清理过期缓存 / Clear expired cache
python tools/i18n_build_tool.py --clear-cache

# 清理所有缓存 / Clear all cache
python tools/i18n_build_tool.py --clear-cache --force
```

### 6. Adding New Languages / 添加新语言

#### Step 1: Update Configuration / 步骤1：更新配置
```python
# i18n/builder.py
SUPPORTED_LANGUAGES = [
    "en_US", "zh_CN", "zh_TW", "ja_JP", "ko_KR",
    "ru_RU", "es_ES", "de_DE", "fr_FR", "ar_SA",
    "pt_BR"  # 新增葡萄牙语 / Add Portuguese
]
```

#### Step 2: Build New Language / 步骤2：构建新语言
```bash
# 构建新语言 / Build new language
python tools/i18n_build_tool.py --build pt_BR --engine qwen

# 验证质量 / Verify quality
python tools/quality_monitor.py validate pt_BR
```

#### Step 3: Update User Config / 步骤3：更新用户配置
```python
# ~/.claude/i18n/config.json
{
  "supported_languages": [
    "en_US", "zh_CN", "zh_TW", "ja_JP", "ko_KR",
    "ru_RU", "es_ES", "de_DE", "fr_FR", "ar_SA",
    "pt_BR"  // 新增 / Add new
  ]
}
```

## API Cost Optimization / API 成本优化

### Cost Comparison / 成本对比

| Method / 方法 | Cost per Build / 每次构建成本 | Time / 时间 | Quality / 质量 |
|--------------|-------------------------------|------------|---------------|
| Full Translation / 完整翻译 | $0.50-$1.00 | 60-120s | 100% |
| Incremental / 增量翻译 | $0.05-$0.15 | 10-30s | 100% |
| With Cache / 带缓存 | $0.10-$0.30 | 15-45s | 100% |
| Incremental + Cache / 增量+缓存 | $0.02-$0.08 | 5-15s | 100% |

### Optimization Strategies / 优化策略

```python
# 1. 批量处理 / Batch Processing
from i18n.builder import SuperClaudeI18nBuilder

async def batch_translate():
    builder = SuperClaudeI18nBuilder(
        batch_size=100,  # 增加批量大小 / Increase batch size
        parallel_workers=5  # 并行处理 / Parallel processing
    )
    await builder.build_all_languages()

# 2. 智能缓存 / Smart Caching
from i18n.cache import TranslationCache

cache = TranslationCache(
    similarity_threshold=0.85,  # 相似度阈值 / Similarity threshold
    max_age_days=60  # 延长缓存有效期 / Extend cache validity
)

# 3. 选择性翻译 / Selective Translation
from i18n.incremental import IncrementalTranslationManager

manager = IncrementalTranslationManager(
    change_threshold=0.1,  # 仅翻译>10%变化的内容 / Only translate >10% changes
    priority_languages=["zh_CN", "ja_JP"]  # 优先语言 / Priority languages
)
```

## Quality Assurance / 质量保证

### Quality Metrics / 质量指标

```python
from i18n.validator import QualityValidator

validator = QualityValidator()

# 验证单个翻译 / Validate single translation
score = validator.validate_translation(
    original="Execute comprehensive code analysis",
    translated="执行全面的代码分析",
    target_lang="zh_CN",
    content_type="command"
)

print(f"Overall Score: {score.overall_score}")  # 0.0-1.0
print(f"Completeness: {score.completeness}")    # 信息完整性 / Information completeness
print(f"Fluency: {score.fluency}")              # 语言流畅度 / Language fluency
print(f"Terminology: {score.terminology}")       # 术语准确性 / Terminology accuracy
```

### Quality Thresholds / 质量阈值

| Score / 分数 | Quality Level / 质量等级 | Action / 操作 |
|-------------|-------------------------|--------------|
| ≥ 0.95 | Excellent / 优秀 | Auto-approve / 自动批准 |
| 0.85-0.95 | Good / 良好 | Manual review optional / 可选人工审核 |
| 0.70-0.85 | Acceptable / 可接受 | Manual review required / 需要人工审核 |
| < 0.70 | Poor / 差 | Retranslate / 重新翻译 |

## Troubleshooting / 故障排除

### Common Issues / 常见问题

#### 1. API Connection Failed / API连接失败
```bash
# 检查API密钥 / Check API keys
echo $QWEN_API_KEY
echo $OPENROUTER_API_KEY

# 测试连接 / Test connection
python -c "from i18n.translator import QwenTranslator; t = QwenTranslator(); print(t.test_connection())"
```

#### 2. Translation Quality Issues / 翻译质量问题
```bash
# 强制重新翻译 / Force retranslation
python tools/i18n_build_tool.py --build zh_CN --force --no-cache

# 使用不同模型 / Use different model
python tools/i18n_build_tool.py --build zh_CN --engine openrouter --model claude-3-5-sonnet-20241022
```

#### 3. Cache Corruption / 缓存损坏
```bash
# 清理并重建缓存 / Clear and rebuild cache
rm -rf .superclaude/cache/*
python tools/i18n_build_tool.py --rebuild-cache
```

#### 4. Incremental Detection Issues / 增量检测问题
```bash
# 重置内容快照 / Reset content snapshot
rm .superclaude/incremental/content_snapshot.json
python tools/i18n_build_tool.py --create-snapshot

# 验证检测 / Verify detection
python test_incremental_system.py
```

## Performance Metrics / 性能指标

### Build Performance / 构建性能

| Languages / 语言数 | Full Build / 完整构建 | Incremental / 增量 | With Cache / 带缓存 |
|-------------------|---------------------|-------------------|-------------------|
| 1 | 15s | 3s | 5s |
| 5 | 75s | 15s | 25s |
| 9 | 135s | 27s | 45s |

### Cost Savings / 成本节省

```
Initial build (9 languages): $0.50
Subsequent builds with cache: $0.05-$0.15 (70-90% savings)
Incremental updates: $0.02-$0.08 (84-96% savings)
```

## CI/CD Integration / CI/CD 集成

### GitHub Actions Example / GitHub Actions 示例

```yaml
# .github/workflows/translation.yml
name: Translation Update

on:
  push:
    paths:
      - '**/*.py'
      - '**/*.md'
      - 'i18n/**'

jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run incremental translation
        env:
          QWEN_API_KEY: ${{ secrets.QWEN_API_KEY }}
        run: python tools/i18n_build_tool.py --update
      
      - name: Validate quality
        run: python tools/quality_monitor.py validate --threshold 0.85
      
      - name: Commit translations
        uses: EndBug/add-and-commit@v7
        with:
          message: 'Update translations [skip ci]'
          add: 'i18n/locales/*.json'
```

## API Reference / API 参考

### Translation Builder / 翻译构建器

```python
from i18n.builder import SuperClaudeI18nBuilder

# 初始化 / Initialize
builder = SuperClaudeI18nBuilder(
    engine="qwen",           # 翻译引擎 / Translation engine
    cache_enabled=True,      # 启用缓存 / Enable cache
    batch_size=50,          # 批量大小 / Batch size
    max_retries=3,          # 最大重试 / Max retries
    quality_threshold=0.85  # 质量阈值 / Quality threshold
)

# 构建单个语言 / Build single language
locale = await builder.build_single_language("zh_CN")

# 构建所有语言 / Build all languages
locales = await builder.build_all_languages()

# 保存文件 / Save files
builder.save_locale_files(locales)
```

### Incremental Manager / 增量管理器

```python
from i18n.incremental import IncrementalTranslationManager

# 初始化 / Initialize
manager = IncrementalTranslationManager(
    snapshot_path=".superclaude/incremental/content_snapshot.json",
    change_threshold=0.05  # 5%变化阈值 / 5% change threshold
)

# 检测变更 / Detect changes
changes = manager.detect_content_changes()

# 翻译变更 / Translate changes
result = await manager.translate_changes(
    changes,
    languages=["zh_CN", "ja_JP"],
    engine="qwen"
)

# 更新快照 / Update snapshot
manager.update_snapshot()
```

## Contributing / 贡献指南

### Adding Translation Features / 添加翻译功能

1. Create feature branch / 创建功能分支
2. Update translation engine / 更新翻译引擎
3. Add tests / 添加测试
4. Update documentation / 更新文档
5. Submit PR / 提交PR

### Code Standards / 代码标准

- Use type hints / 使用类型提示
- Add docstrings / 添加文档字符串
- Follow PEP 8 / 遵循PEP 8
- Test coverage ≥80% / 测试覆盖率≥80%

## Support / 支持

For issues or questions / 如有问题或疑问:
- GitHub Issues: [SuperClaude/issues](https://github.com/username/SuperClaude/issues)
- Documentation: [i18n-guide.md](./i18n-guide.md)
- API Docs: [API Reference](#api-reference--api-参考)