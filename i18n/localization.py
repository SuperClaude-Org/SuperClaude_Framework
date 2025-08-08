#!/usr/bin/env python3
"""
SuperClaude本地化管理器 / SuperClaude Localization Manager
运行时本地化功能，提供多语言文本获取和语言切换 / Runtime localization functionality, provides multilingual text retrieval and language switching
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class LocaleInfo:
    """语言信息 / Language information"""
    code: str
    name: str
    native_name: str
    is_rtl: bool = False


class LocalizationManager:
    """SuperClaude本地化管理器 - 运行时多语言支持 / SuperClaude localization manager - Runtime multilingual support"""
    
    def __init__(self, locale_dir: str = None, default_locale: str = "en_US"):
        """
        初始化本地化管理器
        
        Args:
            locale_dir: 本地化文件目录
            default_locale: 默认语言
        """
        if locale_dir is None:
            # 默认使用项目的i18n/locales目录
            locale_dir = Path(__file__).parent / "locales"
        
        self.locale_dir = Path(locale_dir)
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.fallback_locale = "en_US"
        
        # 创建本地化目录
        self.locale_dir.mkdir(parents=True, exist_ok=True)
        
        # 语言信息配置
        self.supported_locales = {
            "en_US": LocaleInfo("en_US", "English", "English"),
            "zh_CN": LocaleInfo("zh_CN", "Simplified Chinese", "简体中文"),
            "zh_TW": LocaleInfo("zh_TW", "Traditional Chinese", "繁體中文"),
            "ja_JP": LocaleInfo("ja_JP", "Japanese", "日本語"),
            "ko_KR": LocaleInfo("ko_KR", "Korean", "한국어"),
            "es_ES": LocaleInfo("es_ES", "Spanish", "Español"),
            "fr_FR": LocaleInfo("fr_FR", "French", "Français"),
            "de_DE": LocaleInfo("de_DE", "German", "Deutsch"),
            "ru_RU": LocaleInfo("ru_RU", "Russian", "Русский"),
            "ar_SA": LocaleInfo("ar_SA", "Arabic", "العربية", is_rtl=True)
        }
        
        # 缓存已加载的语言文件
        self._locale_cache = {}
        
        # 从环境变量读取用户首选语言
        self._detect_user_locale()
    
    def _detect_user_locale(self):
        """检测用户首选语言"""
        # 优先级: 环境变量 > 系统语言 > 默认语言
        preferred = os.getenv("SUPERCLAUDE_LANGUAGE") or os.getenv("LANG", "").split('.')[0].replace('_', '_')
        
        if preferred in self.supported_locales:
            self.current_locale = preferred
        elif preferred.startswith("zh"):
            self.current_locale = "zh_CN"  # 中文默认简体
        elif preferred.startswith("en"):
            self.current_locale = "en_US"
        # 否则保持默认语言
    
    def _load_locale_file(self, locale: str) -> Dict[str, Any]:
        """加载语言文件"""
        if locale in self._locale_cache:
            return self._locale_cache[locale]
        
        locale_file = self.locale_dir / f"{locale}.json"
        
        if not locale_file.exists():
            print(f"Warning: Locale file not found: {locale_file}")
            return {}
        
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._locale_cache[locale] = data
                return data
        except Exception as e:
            print(f"Error loading locale file {locale_file}: {e}")
            return {}
    
    def get_text(self, key: str, locale: str = None, **kwargs) -> str:
        """
        获取本地化文本
        
        Args:
            key: 文本键，支持点号分隔的嵌套键 (如 "ui.install_success")
            locale: 语言代码，None则使用当前语言
            **kwargs: 格式化参数
        
        Returns:
            本地化文本
        """
        if locale is None:
            locale = self.current_locale
        
        # 尝试从指定语言获取
        text = self._get_text_from_locale(key, locale)
        
        # 如果找不到，尝试fallback语言
        if text is None and locale != self.fallback_locale:
            text = self._get_text_from_locale(key, self.fallback_locale)
        
        # 最后返回键名本身
        if text is None:
            text = key
        
        # 格式化文本
        if kwargs and text:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError) as e:
                print(f"Warning: Failed to format text '{key}': {e}")
        
        return text
    
    def _get_text_from_locale(self, key: str, locale: str) -> Optional[str]:
        """从指定语言文件获取文本"""
        data = self._load_locale_file(locale)
        
        if not data:
            return None
        
        # 处理嵌套键 (如 "ui.install_success")
        keys = key.split('.')
        current = data
        
        try:
            for k in keys:
                current = current[k]
            return current if isinstance(current, str) else None
        except (KeyError, TypeError):
            return None
    
    def set_locale(self, locale: str) -> bool:
        """
        设置当前语言
        
        Args:
            locale: 语言代码
            
        Returns:
            是否设置成功
        """
        if locale not in self.supported_locales:
            print(f"Warning: Unsupported locale: {locale}")
            return False
        
        # 检查语言文件是否存在
        locale_file = self.locale_dir / f"{locale}.json"
        if not locale_file.exists():
            print(f"Warning: Locale file not found: {locale_file}")
            return False
        
        self.current_locale = locale
        return True
    
    def get_current_locale(self) -> str:
        """获取当前语言代码"""
        return self.current_locale
    
    def get_locale_info(self, locale: str = None) -> Optional[LocaleInfo]:
        """获取语言信息"""
        if locale is None:
            locale = self.current_locale
        return self.supported_locales.get(locale)
    
    def get_supported_locales(self) -> List[LocaleInfo]:
        """获取支持的语言列表"""
        return list(self.supported_locales.values())
    
    def get_available_locales(self) -> List[LocaleInfo]:
        """获取可用的语言列表（已有语言文件）"""
        available = []
        for locale, info in self.supported_locales.items():
            locale_file = self.locale_dir / f"{locale}.json"
            if locale_file.exists():
                available.append(info)
        return available
    
    def is_rtl(self, locale: str = None) -> bool:
        """判断是否为从右到左的语言"""
        if locale is None:
            locale = self.current_locale
        locale_info = self.supported_locales.get(locale)
        return locale_info.is_rtl if locale_info else False
    
    def reload_locale(self, locale: str = None):
        """重新加载语言文件"""
        if locale is None:
            locale = self.current_locale
        
        if locale in self._locale_cache:
            del self._locale_cache[locale]
        
        self._load_locale_file(locale)
    
    def get_translation_coverage(self, locale: str) -> Dict[str, Any]:
        """获取翻译覆盖率统计"""
        locale_data = self._load_locale_file(locale)
        fallback_data = self._load_locale_file(self.fallback_locale) if locale != self.fallback_locale else {}
        
        def count_keys(data: Dict, prefix: str = "") -> int:
            """递归计算键的数量"""
            count = 0
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    count += count_keys(value, full_key)
                elif isinstance(value, str):
                    count += 1
            return count
        
        locale_keys = count_keys(locale_data)
        fallback_keys = count_keys(fallback_data)
        
        coverage_rate = locale_keys / fallback_keys if fallback_keys > 0 else 0.0
        
        return {
            "locale": locale,
            "translated_keys": locale_keys,
            "total_keys": fallback_keys,
            "coverage_rate": round(coverage_rate, 3),
            "missing_keys": max(0, fallback_keys - locale_keys)
        }
    
    # 便捷方法
    def _(self, key: str, **kwargs) -> str:
        """简化的翻译方法"""
        return self.get_text(key, **kwargs)
    
    def translate(self, key: str, **kwargs) -> str:
        """翻译方法别名"""
        return self.get_text(key, **kwargs)
    
    def get_command_description(self, command: str) -> str:
        """获取命令描述"""
        return self.get_text(f"commands.{command}")
    
    def get_persona_description(self, persona: str) -> str:
        """获取Persona描述"""
        return self.get_text(f"personas.{persona}")
    
    def get_ui_text(self, key: str, **kwargs) -> str:
        """获取UI文本"""
        return self.get_text(f"ui.{key}", **kwargs)
    
    def get_error_message(self, key: str, **kwargs) -> str:
        """获取错误消息"""
        return self.get_text(f"errors.{key}", **kwargs)
    
    def get_help_text(self, key: str) -> str:
        """获取帮助文本"""
        return self.get_text(f"help.{key}")


# 全局本地化管理器实例
_global_localizer = None


def get_localizer() -> LocalizationManager:
    """获取全局本地化管理器实例"""
    global _global_localizer
    if _global_localizer is None:
        _global_localizer = LocalizationManager()
    return _global_localizer


def init_localization(locale_dir: str = None, default_locale: str = "en_US") -> LocalizationManager:
    """初始化本地化系统"""
    global _global_localizer
    _global_localizer = LocalizationManager(locale_dir, default_locale)
    return _global_localizer


# 便捷的全局函数
def _(key: str, **kwargs) -> str:
    """全局翻译函数"""
    return get_localizer().get_text(key, **kwargs)


def set_language(locale: str) -> bool:
    """设置全局语言"""
    return get_localizer().set_locale(locale)


def get_language() -> str:
    """获取当前语言"""
    return get_localizer().get_current_locale()


if __name__ == "__main__":
    # 测试本地化管理器
    localizer = LocalizationManager()
    
    print(f"Current locale: {localizer.get_current_locale()}")
    print(f"Supported locales: {[info.code for info in localizer.get_supported_locales()]}")
    
    # 测试文本获取（这些键在实际的语言文件中应该存在）
    print(f"Test text: {localizer.get_text('ui.welcome', name='SuperClaude')}")
    
    # 测试语言切换
    if localizer.set_locale("zh_CN"):
        print(f"Language changed to: {localizer.get_current_locale()}")
        print(f"Test Chinese text: {localizer.get_text('ui.welcome', name='SuperClaude')}")
    
    # 测试覆盖率统计
    coverage = localizer.get_translation_coverage("zh_CN")
    print(f"Translation coverage: {coverage}")