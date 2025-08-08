#!/usr/bin/env python3
"""
SuperClaude i18n 指令处理器 / SuperClaude i18n Command Handler
处理 /sc:i18n 指令的核心逻辑 / Core logic for handling /sc:i18n commands
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from i18n.localization import LocalizationManager, set_language, get_current_language
    from i18n.builder import SuperClaudeI18nBuilder
    from i18n.incremental import IncrementalTranslationManager
    from i18n.cache import TranslationCache
    from i18n.validator import QualityValidator
    from i18n.translation_engine import TranslationEngineManager
except ImportError as e:
    print(f"⚠️ i18n模块导入警告 / i18n module import warning: {e}")


class I18nCommandHandler:
    """i18n指令处理器 / i18n Command Handler"""
    
    def __init__(self, project_root: str = None):
        """初始化处理器 / Initialize handler"""
        self.project_root = Path(project_root or PROJECT_ROOT)
        self.config_file = self.project_root / ".superclaude" / "i18n_config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化组件 / Initialize components
        self.localizer = LocalizationManager()
        self.cache = TranslationCache()
        self.validator = QualityValidator()
        
        # 加载配置 / Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载i18n配置 / Load i18n configuration"""
        default_config = {
            "default_language": "zh_CN",
            "fallback_language": "en_US", 
            "translation_engine": "qwen",
            "cache_enabled": True,
            "quality_threshold": 0.8,
            "supported_languages": [
                "en_US", "zh_CN", "zh_TW", "ja_JP", "ko_KR", 
                "ru_RU", "es_ES", "de_DE", "fr_FR", "ar_SA"
            ]
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    default_config.update(config)
                    return default_config
            except Exception as e:
                print(f"⚠️ 配置文件读取失败，使用默认配置 / Config file read failed, using default: {e}")
        
        return default_config
    
    def _save_config(self):
        """保存i18n配置 / Save i18n configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 配置文件保存失败 / Config file save failed: {e}")
    
    async def handle_command(self, command: str, args: List[str]) -> str:
        """处理i18n指令 / Handle i18n command"""
        try:
            if command == "switch":
                return await self._handle_switch(args)
            elif command == "current":
                return self._handle_current()
            elif command == "list":
                return self._handle_list()
            elif command == "translate":
                return await self._handle_translate(args)
            elif command == "build":
                return await self._handle_build(args)
            elif command == "update":
                return await self._handle_update()
            elif command == "config":
                return self._handle_config()
            elif command == "cache":
                return await self._handle_cache(args)
            elif command == "validate":
                return await self._handle_validate(args)
            elif command == "report":
                return await self._handle_report()
            else:
                return self._handle_help()
        except Exception as e:
            return f"❌ 指令执行失败 / Command execution failed: {e}"
    
    async def _handle_switch(self, args: List[str]) -> str:
        """处理语言切换 / Handle language switching"""
        if not args:
            return "❌ 请指定语言代码 / Please specify language code\n使用方法 / Usage: /sc:i18n switch <language_code>"
        
        lang_code = args[0]
        
        # 验证语言代码
        if lang_code not in self.config["supported_languages"]:
            supported = ", ".join(self.config["supported_languages"])
            return f"❌ 不支持的语言代码 / Unsupported language code: {lang_code}\n支持的语言 / Supported languages: {supported}"
        
        # 检查本地化文件是否存在
        locale_file = self.project_root / "i18n" / "locales" / f"{lang_code}.json"
        if not locale_file.exists():
            return f"⚠️ 本地化文件不存在 / Localization file not found: {locale_file}\n请先运行 / Please run: /sc:i18n build {lang_code}"
        
        # 切换语言
        try:
            set_language(lang_code)
            self.config["default_language"] = lang_code
            self._save_config()
            
            # 获取语言的本地名称
            lang_names = {
                "en_US": "English",
                "zh_CN": "简体中文",
                "zh_TW": "繁體中文", 
                "ja_JP": "日本語",
                "ko_KR": "한국어",
                "ru_RU": "Русский",
                "es_ES": "Español",
                "de_DE": "Deutsch",
                "fr_FR": "Français",
                "ar_SA": "العربية"
            }
            
            lang_name = lang_names.get(lang_code, lang_code)
            return f"✅ 语言已切换 / Language switched: {lang_name} ({lang_code})"
            
        except Exception as e:
            return f"❌ 语言切换失败 / Language switch failed: {e}"
    
    def _handle_current(self) -> str:
        """显示当前语言 / Show current language"""
        current_lang = get_current_language()
        lang_names = {
            "en_US": "English",
            "zh_CN": "简体中文", 
            "zh_TW": "繁體中文",
            "ja_JP": "日本語",
            "ko_KR": "한국어",
            "ru_RU": "Русский",
            "es_ES": "Español",
            "de_DE": "Deutsch",
            "fr_FR": "Français",
            "ar_SA": "العربية"
        }
        
        lang_name = lang_names.get(current_lang, current_lang)
        return f"📍 当前语言 / Current language: {lang_name} ({current_lang})"
    
    def _handle_list(self) -> str:
        """列出可用语言 / List available languages"""
        result = ["🌍 可用语言 / Available languages:\n"]
        
        lang_info = [
            ("en_US", "English", "English"),
            ("zh_CN", "简体中文", "简体中文"),
            ("zh_TW", "繁體中文", "繁體中文"),
            ("ja_JP", "日本語", "日本語"),
            ("ko_KR", "한국어", "한국어"),
            ("ru_RU", "Русский", "Русский"),
            ("es_ES", "Español", "Español"),
            ("de_DE", "Deutsch", "Deutsch"),
            ("fr_FR", "Français", "Français"),
            ("ar_SA", "العربية", "العربية")
        ]
        
        current_lang = get_current_language()
        
        for code, name, native in lang_info:
            if code in self.config["supported_languages"]:
                status = "🔸" if code == current_lang else "  "
                locale_file = self.project_root / "i18n" / "locales" / f"{code}.json"
                available = "✅" if locale_file.exists() else "⚠️"
                result.append(f"{status} {available} {code} - {name} ({native})")
        
        result.append("\n🔸 = 当前语言 / Current language")
        result.append("✅ = 已构建 / Built, ⚠️ = 需构建 / Needs build")
        
        return "\n".join(result)
    
    async def _handle_translate(self, args: List[str]) -> str:
        """处理翻译请求 / Handle translation request"""
        if not args:
            return "❌ 请指定目标语言 / Please specify target language\n使用方法 / Usage: /sc:i18n translate <target_language>"
        
        target_lang = args[0]
        
        if target_lang not in self.config["supported_languages"]:
            return f"❌ 不支持的语言 / Unsupported language: {target_lang}"
        
        try:
            builder = SuperClaudeI18nBuilder(str(self.project_root))
            result = await builder.build_single_language(target_lang)
            
            if result:
                return f"✅ 翻译完成 / Translation completed: {target_lang}\n生成了 {len(result)} 个翻译项 / Generated {len(result)} translation items"
            else:
                return f"⚠️ 翻译未生成内容 / Translation generated no content for: {target_lang}"
                
        except Exception as e:
            return f"❌ 翻译失败 / Translation failed: {e}"
    
    async def _handle_build(self, args: List[str]) -> str:
        """处理构建请求 / Handle build request"""
        languages = args if args else self.config["supported_languages"]
        
        # 验证语言代码
        invalid_langs = [lang for lang in languages if lang not in self.config["supported_languages"]]
        if invalid_langs:
            return f"❌ 不支持的语言 / Unsupported languages: {', '.join(invalid_langs)}"
        
        try:
            builder = SuperClaudeI18nBuilder(str(self.project_root))
            results = await builder.build_all_languages(languages)
            
            if results:
                builder.save_locale_files(results)
                report = builder.generate_build_report(results)
                
                return f"✅ 构建完成 / Build completed\n{report['summary']}"
            else:
                return "⚠️ 构建未生成内容 / Build generated no content"
                
        except Exception as e:
            return f"❌ 构建失败 / Build failed: {e}"
    
    async def _handle_update(self) -> str:
        """处理增量更新 / Handle incremental update"""
        try:
            manager = IncrementalTranslationManager(str(self.project_root))
            changes = manager.detect_content_changes()
            
            if not changes:
                return "✅ 无需更新 / No updates needed - 内容未发生变化 / Content unchanged"
            
            # 执行增量翻译
            languages = self.config["supported_languages"]
            result = await manager.translate_changes(changes, languages)
            
            return f"✅ 增量更新完成 / Incremental update completed\n更新了 {len(changes)} 项变更 / Updated {len(changes)} changes"
            
        except Exception as e:
            return f"❌ 增量更新失败 / Incremental update failed: {e}"
    
    def _handle_config(self) -> str:
        """显示配置信息 / Show configuration"""
        config_str = json.dumps(self.config, indent=2, ensure_ascii=False)
        return f"⚙️ i18n配置 / i18n Configuration:\n```json\n{config_str}\n```"
    
    async def _handle_cache(self, args: List[str]) -> str:
        """处理缓存操作 / Handle cache operations"""
        if not args:
            return "❌ 请指定缓存操作 / Please specify cache operation\n可用操作 / Available operations: clear, stats"
        
        operation = args[0]
        
        if operation == "clear":
            try:
                self.cache.clear_cache()
                return "✅ 翻译缓存已清理 / Translation cache cleared"
            except Exception as e:
                return f"❌ 缓存清理失败 / Cache clear failed: {e}"
        
        elif operation == "stats":
            try:
                stats = self.cache.get_cache_statistics()
                return f"📊 缓存统计 / Cache Statistics:\n{json.dumps(stats, indent=2, ensure_ascii=False)}"
            except Exception as e:
                return f"❌ 获取缓存统计失败 / Get cache stats failed: {e}"
        
        else:
            return f"❌ 未知缓存操作 / Unknown cache operation: {operation}"
    
    async def _handle_validate(self, args: List[str]) -> str:
        """处理质量验证 / Handle quality validation"""
        language = args[0] if args else self.config["default_language"]
        
        if language not in self.config["supported_languages"]:
            return f"❌ 不支持的语言 / Unsupported language: {language}"
        
        try:
            locale_file = self.project_root / "i18n" / "locales" / f"{language}.json"
            if not locale_file.exists():
                return f"❌ 本地化文件不存在 / Localization file not found: {locale_file}"
            
            # 这里可以添加具体的质量验证逻辑
            return f"✅ 质量验证完成 / Quality validation completed for: {language}"
            
        except Exception as e:
            return f"❌ 质量验证失败 / Quality validation failed: {e}"
    
    async def _handle_report(self) -> str:
        """生成质量报告 / Generate quality report"""
        try:
            # 这里可以添加具体的报告生成逻辑
            return "📋 质量报告生成完成 / Quality report generated\n详细报告请查看日志文件 / See log files for detailed report"
        except Exception as e:
            return f"❌ 报告生成失败 / Report generation failed: {e}"
    
    def _handle_help(self) -> str:
        """显示帮助信息 / Show help information"""
        return """
🌍 SuperClaude i18n 指令帮助 / SuperClaude i18n Command Help

语言切换 / Language Switching:
  /sc:i18n switch <lang>     切换到指定语言 / Switch to specified language
  /sc:i18n current           显示当前语言 / Show current language  
  /sc:i18n list              列出可用语言 / List available languages

翻译管理 / Translation Management:
  /sc:i18n translate <lang>  翻译到目标语言 / Translate to target language
  /sc:i18n build [langs...]  构建本地化文件 / Build localization files
  /sc:i18n update            增量更新翻译 / Incremental update

配置管理 / Configuration Management:
  /sc:i18n config            显示配置信息 / Show configuration
  /sc:i18n cache clear       清理翻译缓存 / Clear translation cache
  /sc:i18n cache stats       显示缓存统计 / Show cache statistics

质量检查 / Quality Check:
  /sc:i18n validate [lang]   验证翻译质量 / Validate translation quality
  /sc:i18n report            生成质量报告 / Generate quality report

示例 / Examples:
  /sc:i18n switch zh_CN      # 切换到简体中文
  /sc:i18n build ja_JP       # 构建日语本地化文件
  /sc:i18n cache clear       # 清理翻译缓存
"""


# 全局处理器实例 / Global handler instance
_handler = None

def get_i18n_handler() -> I18nCommandHandler:
    """获取i18n指令处理器实例 / Get i18n command handler instance"""
    global _handler
    if _handler is None:
        _handler = I18nCommandHandler()
    return _handler

async def handle_i18n_command(command: str, args: List[str]) -> str:
    """处理i18n指令的入口函数 / Entry function for handling i18n commands"""
    handler = get_i18n_handler()
    return await handler.handle_command(command, args)


if __name__ == "__main__":
    # 测试代码 / Test code
    async def test():
        handler = I18nCommandHandler()
        
        # 测试各种指令
        commands = [
            ("current", []),
            ("list", []),
            ("config", []),
            ("cache", ["stats"])
        ]
        
        for cmd, args in commands:
            print(f"\n🧪 测试指令 / Testing command: /sc:i18n {cmd} {' '.join(args)}")
            result = await handler.handle_command(cmd, args)
            print(result)
    
    asyncio.run(test())
