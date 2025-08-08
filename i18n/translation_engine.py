#!/usr/bin/env python3
"""
翻译引擎选择器 / Translation Engine Selector
统一管理多个翻译引擎的接口和选择逻辑 / Unified management of multiple translation engine interfaces and selection logic
"""

import os
from typing import Dict, List, Optional, Union
from enum import Enum

from .translator import QwenTranslator, TranslationContext, TranslationResult
from .openrouter_translator import OpenRouterTranslator


class EngineType(Enum):
    """翻译引擎类型 / Translation engine type"""
    QWEN = "qwen"
    OPENROUTER = "openrouter"


class TranslationEngineManager:
    """翻译引擎管理器 / Translation engine manager"""
    
    def __init__(self, default_engine: EngineType = EngineType.QWEN):
        """
        初始化引擎管理器 / Initialize engine manager
        
        Args:
            default_engine: 默认使用的翻译引擎 / Default translation engine to use
        """
        self.default_engine = default_engine
        self._engines = {}
        self._initialize_engines()
    
    def _initialize_engines(self):
        """初始化可用的翻译引擎"""
        # 检查千问引擎
        if os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY"):
            try:
                self._engines[EngineType.QWEN] = QwenTranslator()
                print("✅ 千问翻译引擎初始化成功 / Qwen translation engine initialized successfully")
            except Exception as e:
                print(f"⚠️ 千问翻译引擎初始化失败 / Qwen translation engine initialization failed: {e}")
        
        # 检查OpenRouter引擎
        if os.getenv("OPENROUTER_API_KEY"):
            try:
                self._engines[EngineType.OPENROUTER] = OpenRouterTranslator()
                print("✅ OpenRouter翻译引擎初始化成功 / OpenRouter translation engine initialized successfully")
            except Exception as e:
                print(f"⚠️ OpenRouter翻译引擎初始化失败 / OpenRouter translation engine initialization failed: {e}")
        
        if not self._engines:
            raise RuntimeError("没有可用的翻译引擎。请设置相关API密钥。")
    
    def get_available_engines(self) -> List[EngineType]:
        """获取可用的翻译引擎列表"""
        return list(self._engines.keys())
    
    def get_engine(self, engine_type: Optional[EngineType] = None):
        """
        获取指定的翻译引擎
        
        Args:
            engine_type: 引擎类型，如果为None则使用默认引擎
            
        Returns:
            翻译引擎实例
        """
        if engine_type is None:
            engine_type = self.default_engine
        
        if engine_type not in self._engines:
            available = ", ".join([e.value for e in self._engines.keys()])
            raise ValueError(f"引擎 '{engine_type.value}' 不可用。可用引擎: {available}")
        
        return self._engines[engine_type]
    
    def set_default_engine(self, engine_type: EngineType):
        """设置默认翻译引擎"""
        if engine_type not in self._engines:
            available = ", ".join([e.value for e in self._engines.keys()])
            raise ValueError(f"引擎 '{engine_type.value}' 不可用。可用引擎: {available}")
        
        self.default_engine = engine_type
        print(f"默认翻译引擎设置为 / Default translation engine set to: {engine_type.value}")
    
    async def translate_with_context(self, 
                                   text: str, 
                                   target_lang: str,
                                   context: TranslationContext,
                                   engine_type: Optional[EngineType] = None) -> TranslationResult:
        """使用指定引擎进行翻译"""
        engine = self.get_engine(engine_type)
        return await engine.translate_with_context(text, target_lang, context)
    
    async def translate_batch(self, 
                            texts: List[str], 
                            target_lang: str,
                            context: TranslationContext,
                            engine_type: Optional[EngineType] = None) -> List[TranslationResult]:
        """使用指定引擎进行批量翻译"""
        engine = self.get_engine(engine_type)
        return await engine.translate_batch(texts, target_lang, context)
    
    async def translate_superclaude_content(self, 
                                         content_dict: Dict[str, Dict[str, str]], 
                                         target_lang: str,
                                         engine_type: Optional[EngineType] = None) -> Dict[str, Dict[str, str]]:
        """使用指定引擎翻译SuperClaude内容"""
        engine = self.get_engine(engine_type)
        return await engine.translate_superclaude_content(content_dict, target_lang)
    
    def get_cost_estimate(self, 
                         content_dict: Dict[str, Dict[str, str]], 
                         engine_type: Optional[EngineType] = None) -> Dict[str, Union[int, float]]:
        """获取翻译成本估算"""
        engine = self.get_engine(engine_type)
        return engine.get_cost_estimate(content_dict)
    
    def get_supported_languages(self, 
                              engine_type: Optional[EngineType] = None) -> List[Dict[str, str]]:
        """获取支持的语言列表"""
        engine = self.get_engine(engine_type)
        return engine.get_supported_languages()
    
    def compare_engines(self, content_dict: Dict[str, Dict[str, str]]) -> Dict[str, Dict]:
        """比较不同引擎的成本和特性"""
        comparison = {}
        
        for engine_type in self._engines:
            try:
                cost_info = self.get_cost_estimate(content_dict, engine_type)
                engine = self.get_engine(engine_type)
                
                # 获取引擎特性
                features = {
                    "batch_size": getattr(engine, "MAX_BATCH_SIZE", 10) if hasattr(engine, "translate_batch") else 1,
                    "context_window": "8K" if engine_type == EngineType.QWEN else "1M",
                    "model": getattr(engine, "model", None) or getattr(engine.config, "model", "unknown")
                }
                
                comparison[engine_type.value] = {
                    "cost": cost_info,
                    "features": features,
                    "currency": "RMB" if engine_type == EngineType.QWEN else "USD"
                }
                
            except Exception as e:
                comparison[engine_type.value] = {
                    "error": str(e)
                }
        
        return comparison
    
    def recommend_engine(self, 
                        content_dict: Dict[str, Dict[str, str]], 
                        priority: str = "cost") -> EngineType:
        """
        推荐最适合的翻译引擎
        
        Args:
            content_dict: 要翻译的内容
            priority: 优先级 ("cost" | "quality" | "speed")
            
        Returns:
            推荐的引擎类型
        """
        if priority == "cost":
            # 千问通常成本更低
            if EngineType.QWEN in self._engines:
                return EngineType.QWEN
            else:
                return list(self._engines.keys())[0]
        
        elif priority == "quality":
            # Gemini质量更高
            if EngineType.OPENROUTER in self._engines:
                return EngineType.OPENROUTER
            else:
                return list(self._engines.keys())[0]
        
        elif priority == "speed":
            # 根据批量处理能力推荐
            total_items = sum(len(items) for items in content_dict.values())
            if total_items > 50 and EngineType.OPENROUTER in self._engines:
                # 大量内容，使用长上下文的Gemini
                return EngineType.OPENROUTER
            else:
                # 少量内容，使用千问
                return EngineType.QWEN if EngineType.QWEN in self._engines else list(self._engines.keys())[0]
        
        else:
            return self.default_engine
    
    def get_engine_info(self) -> Dict[str, Dict]:
        """获取所有引擎的详细信息"""
        info = {}
        
        for engine_type, engine in self._engines.items():
            try:
                if engine_type == EngineType.QWEN:
                    info[engine_type.value] = {
                        "name": "千问翻译引擎",
                        "model": engine.model,
                        "provider": "阿里云",
                        "context_window": "8K tokens",
                        "batch_size": "10 items",
                        "currency": "RMB",
                        "strengths": ["成本低", "中文优化", "术语准确"]
                    }
                elif engine_type == EngineType.OPENROUTER:
                    info[engine_type.value] = {
                        "name": "OpenRouter引擎",
                        "model": engine.config.model,
                        "provider": "Google Gemini",
                        "context_window": "1M tokens",
                        "batch_size": "20 items",
                        "currency": "USD",
                        "strengths": ["质量高", "长上下文", "多语言优秀"]
                    }
            except Exception as e:
                info[engine_type.value] = {"error": str(e)}
        
        return info


# 创建全局引擎管理器实例
def create_translation_manager(engine_preference: Optional[str] = None) -> TranslationEngineManager:
    """
    创建翻译引擎管理器
    
    Args:
        engine_preference: 首选引擎 ("qwen" | "openrouter")
        
    Returns:
        翻译引擎管理器实例
    """
    default_engine = EngineType.QWEN
    
    if engine_preference:
        try:
            default_engine = EngineType(engine_preference.lower())
        except ValueError:
            print(f"⚠️ 无效的引擎偏好 '{engine_preference}'，使用默认引擎 / Invalid engine preference '{engine_preference}', using default engine")
    
    return TranslationEngineManager(default_engine)


if __name__ == "__main__":
    # 测试翻译引擎管理器
    async def test_engine_manager():
        try:
            manager = create_translation_manager()
            
            print("可用引擎 / Available engines:", [e.value for e in manager.get_available_engines()])
            print("引擎信息 / Engine information:")
            import json
            engine_info = manager.get_engine_info()
            print(json.dumps(engine_info, ensure_ascii=False, indent=2))
            
            # 测试翻译
            if manager.get_available_engines():
                context = manager.get_engine().contexts["commands"]
                result = await manager.translate_with_context(
                    "Multi-dimensional code analysis",
                    "zh_CN",
                    context
                )
                print(f"\n翻译测试 / Translation test:")
                print(f"原文 / Original: {result.source}")
                print(f"译文 / Translation: {result.target}")
                print(f"引擎 / Engine: {manager.default_engine.value}")
                
        except Exception as e:
            print(f"测试失败 / Test failed: {e}")
    
    import asyncio
    # asyncio.run(test_engine_manager())