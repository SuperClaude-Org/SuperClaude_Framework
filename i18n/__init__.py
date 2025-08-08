#!/usr/bin/env python3
"""
SuperClaude i18n模块 / SuperClaude i18n Module
提供多语言支持和本地化功能 / Provides multilingual support and localization functionality

主要组件 / Main Components:
- LocalizationManager: 运行时本地化管理器 / Runtime localization manager
- ContentExtractor: SuperClaude内容提取器 / SuperClaude content extractor
- QwenTranslator: 千问3翻译引擎 / Qwen3 translation engine
"""

from .localization import LocalizationManager
from .extractor import SuperClaudeContentExtractor
from .translator import QwenTranslator
from .cache import TranslationCache
from .validator import QualityValidator

__version__ = "1.0.0"
__all__ = [
    "LocalizationManager",
    "SuperClaudeContentExtractor", 
    "QwenTranslator",
    "TranslationCache",
    "QualityValidator"
]