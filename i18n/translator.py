#!/usr/bin/env python3
"""
千问3翻译引擎 / Qwen3 Translation Engine
集成阿里云千问3翻译模型，提供上下文感知的专业翻译服务 / Integrates Alibaba Cloud Qwen3 translation model, providing context-aware professional translation services
"""

import os
import asyncio
import json
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class TranslationContext:
    """翻译上下文配置 / Translation context configuration"""
    content_type: str  # ui, documentation, error_message, command, persona
    domain: str        # technical, user_interface, help_text
    style: str         # formal, concise, descriptive
    
    
@dataclass
class TranslationResult:
    """翻译结果 / Translation result"""
    source: str
    target: str
    lang: str
    context: str
    confidence: float
    cost_estimate: float = 0.0
    

class QwenTranslator:
    """千问3翻译引擎 - 专业的上下文感知翻译 / Qwen3 Translation Engine - Professional context-aware translation"""
    
    def __init__(self, model_type: str = "plus"):
        """
        初始化千问3翻译引擎 / Initialize Qwen3 translation engine
        
        Args:
            model_type: 模型类型 ("turbo" 速度优先, "plus" 质量优先，默认使用plus) / Model type ("turbo" for speed priority, "plus" for quality priority, defaults to plus)
        """
        api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("请设置环境变量 QWEN_API_KEY 或 DASHSCOPE_API_KEY / Please set environment variable QWEN_API_KEY or DASHSCOPE_API_KEY")
            
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        # 选择模型版本 / Select model version
        self.model = "qwen-mt-plus" if model_type == "plus" else "qwen-mt-turbo"
        
        # 成本配置 (每1K tokens的价格，人民币) / Cost configuration (price per 1K tokens, RMB)
        self.cost_config = {
            "qwen-mt-turbo": {"input": 0.0007, "output": 0.00195},
            "qwen-mt-plus": {"input": 0.0018, "output": 0.0054}
        }
        
        # SuperClaude 专用术语词典 / SuperClaude specialized terminology dictionary
        self.superclaude_terms = {
            "analyze": {"zh_CN": "分析", "ja_JP": "分析", "ko_KR": "분석"},
            "implement": {"zh_CN": "实现", "ja_JP": "実装", "ko_KR": "구현"},
            "build": {"zh_CN": "构建", "ja_JP": "ビルド", "ko_KR": "빌드"},
            "improve": {"zh_CN": "改进", "ja_JP": "改善", "ko_KR": "개선"},
            "design": {"zh_CN": "设计", "ja_JP": "設計", "ko_KR": "설계"},
            "component": {"zh_CN": "组件", "ja_JP": "コンポーネント", "ko_KR": "컴포넌트"},
            "persona": {"zh_CN": "专家角色", "ja_JP": "ペルソナ", "ko_KR": "페르소나"},
            "framework": {"zh_CN": "框架", "ja_JP": "フレームワーク", "ko_KR": "프레임워크"},
            "architecture": {"zh_CN": "架构", "ja_JP": "アーキテクチャ", "ko_KR": "아키텍처"},
            "performance": {"zh_CN": "性能", "ja_JP": "パフォーマンス", "ko_KR": "성능"},
            "security": {"zh_CN": "安全", "ja_JP": "セキュリティ", "ko_KR": "보안"},
            "workflow": {"zh_CN": "工作流", "ja_JP": "ワークフロー", "ko_KR": "워크플로"},
            "orchestration": {"zh_CN": "编排", "ja_JP": "オーケストレーション", "ko_KR": "오케스트레이션"},
            "troubleshoot": {"zh_CN": "故障排除", "ja_JP": "トラブルシューティング", "ko_KR": "문제 해결"},
            "refactor": {"zh_CN": "重构", "ja_JP": "リファクタリング", "ko_KR": "리팩토링"}
        }
        
        # 预定义翻译上下文 / Predefined translation contexts
        self.contexts = {
            "commands": TranslationContext(
                content_type="command",
                domain="technical", 
                style="concise"
            ),
            "personas": TranslationContext(
                content_type="persona",
                domain="technical", 
                style="professional"
            ),
            "ui": TranslationContext(
                content_type="ui",
                domain="user_interface",
                style="friendly"
            ),
            "errors": TranslationContext(
                content_type="error_message",
                domain="technical",
                style="clear"
            ),
            "help": TranslationContext(
                content_type="help",
                domain="documentation",
                style="instructional"
            )
        }
    
    async def translate_with_context(self, 
                                   text: str, 
                                   target_lang: str,
                                   context: TranslationContext) -> TranslationResult:
        """上下文感知的单文本翻译"""
        
        # 构建上下文提示
        system_prompt = self._build_context_prompt(context, target_lang)
        
        # 千问API不支持system角色，将指令嵌入到user消息中
        user_prompt = f"{system_prompt}\n\n需要翻译的内容：{text}"
        messages = [
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # 千问翻译API需要translation_options参数
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                extra_body={
                    "translation_options": {
                        "source_lang": "auto",
                        "target_lang": self._get_target_lang_code(target_lang)
                    }
                }
            )
            
            translated_text = completion.choices[0].message.content.strip()
            
            # 估算成本
            input_tokens = self._estimate_tokens(text)
            output_tokens = self._estimate_tokens(translated_text)
            cost = self._calculate_cost(input_tokens, output_tokens)
            
            return TranslationResult(
                source=text,
                target=translated_text,
                lang=target_lang,
                context=context.content_type,
                confidence=0.95,  # 千问3翻译质量较高
                cost_estimate=cost
            )
            
        except Exception as e:
            print(f"Translation error: {e}")
            return TranslationResult(
                source=text,
                target=f"[Translation failed: {str(e)}]",
                lang=target_lang,
                context=context.content_type,
                confidence=0.0,
                cost_estimate=0.0
            )
    
    async def translate_batch(self, 
                            texts: List[str], 
                            target_lang: str,
                            context: TranslationContext) -> List[TranslationResult]:
        """优化的批量翻译，利用模型上下文窗口和频率控制"""
        
        # 千问翻译模型限制: 8K上下文，每分钟120次请求
        MAX_BATCH_SIZE = 10  # 每次最多10条文本
        REQUESTS_PER_MINUTE = 60  # 保守估计，避免频率限制
        MIN_DELAY = 60.0 / REQUESTS_PER_MINUTE  # 最小间隔1秒
        
        results = []
        
        # 将文本分批处理
        for i in range(0, len(texts), MAX_BATCH_SIZE):
            batch_texts = texts[i:i + MAX_BATCH_SIZE]
            batch_results = []
            
            # 为这一批创建合并的翻译请求
            if len(batch_texts) > 1:
                batch_results = await self._translate_batch_optimized(
                    batch_texts, target_lang, context
                )
            else:
                # 单条文本直接翻译
                result = await self.translate_with_context(batch_texts[0], target_lang, context)
                batch_results = [result]
            
            results.extend(batch_results)
            
            # 添加频率控制延迟
            if i + MAX_BATCH_SIZE < len(texts):  # 不是最后一批
                print(f"  处理进度: {min(i + MAX_BATCH_SIZE, len(texts))}/{len(texts)}")
                await asyncio.sleep(MIN_DELAY)
        
        return results
    
    async def _translate_batch_optimized(self, 
                                       texts: List[str], 
                                       target_lang: str,
                                       context: TranslationContext) -> List[TranslationResult]:
        """优化的批量翻译实现，利用模型的上下文处理能力"""
        
        # 构建批量翻译提示
        system_prompt = self._build_context_prompt(context, target_lang)
        
        # 创建编号的文本列表
        numbered_texts = []
        for i, text in enumerate(texts, 1):
            numbered_texts.append(f"{i}. {text}")
        
        batch_content = "\n".join(numbered_texts)
        user_prompt = f"""{system_prompt}

请翻译以下编号的文本，保持编号格式，每行一个翻译结果：

{batch_content}"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                extra_body={
                    "translation_options": {
                        "source_lang": "auto",
                        "target_lang": self._get_target_lang_code(target_lang)
                    }
                }
            )
            
            # 解析批量翻译结果
            response_text = completion.choices[0].message.content.strip()
            translated_lines = response_text.split('\n')
            
            results = []
            for i, text in enumerate(texts):
                # 尝试从对应行提取翻译结果
                if i < len(translated_lines):
                    line = translated_lines[i].strip()
                    # 移除编号前缀 "1. ", "2. " 等
                    if line and len(line) > 3 and line[1:3] == '. ':
                        translated_text = line[3:].strip()
                    else:
                        translated_text = line
                else:
                    translated_text = f"[Translation failed: batch parsing error]"
                
                # 估算成本
                input_tokens = self._estimate_tokens(user_prompt) // len(texts)
                output_tokens = self._estimate_tokens(translated_text)
                cost = self._calculate_cost(input_tokens, output_tokens)
                
                results.append(TranslationResult(
                    source=text,
                    target=translated_text,
                    lang=target_lang,
                    context=context.content_type,
                    confidence=0.90,  # 批量翻译稍微降低置信度
                    cost_estimate=cost
                ))
            
            return results
            
        except Exception as e:
            print(f"Batch translation error: {e}")
            # 降级到单个翻译
            results = []
            for text in texts:
                result = await self.translate_with_context(text, target_lang, context)
                results.append(result)
                await asyncio.sleep(0.1)  # 短暂延迟
            return results
    
    async def translate_superclaude_content(self, 
                                         content_dict: Dict[str, Dict[str, str]], 
                                         target_lang: str) -> Dict[str, Dict[str, str]]:
        """翻译SuperClaude结构化内容"""
        
        translated_content = {}
        total_cost = 0.0
        
        for category, items in content_dict.items():
            if category not in self.contexts:
                print(f"Warning: Unknown content category '{category}', using default context")
                context = self.contexts["ui"]
            else:
                context = self.contexts[category]
            
            print(f"Translating {category} ({len(items)} items)...")
            
            # 批量翻译该类别的内容
            texts = list(items.values())
            keys = list(items.keys())
            
            results = await self.translate_batch(texts, target_lang, context)
            
            # 重新构建字典
            translated_items = {}
            for key, result in zip(keys, results):
                translated_items[key] = result.target
                total_cost += result.cost_estimate
                
            translated_content[category] = translated_items
            
            print(f"  Completed {category}: {len(translated_items)} translations")
        
        print(f"Total estimated cost: ¥{total_cost:.4f}")
        return translated_content
    
    def _build_context_prompt(self, context: TranslationContext, target_lang: str) -> str:
        """构建上下文感知的翻译提示"""
        
        # 基础提示模板
        base_prompts = {
            "command": "你是SuperClaude命令翻译专家。翻译要求：技术准确，保持专业术语一致性，体现命令功能特点。",
            "persona": "你是SuperClaude专家角色翻译专家。翻译要求：体现专业性和角色特点，保持描述的准确性。",
            "ui": "你是SuperClaude界面翻译专家。翻译要求：简洁明了，符合软件界面习惯，用户友好。",
            "error_message": "你是SuperClaude错误信息翻译专家。翻译要求：清晰直接，帮助用户理解和解决问题。",
            "help": "你是SuperClaude帮助文档翻译专家。翻译要求：详细清晰，保持指导性，易于理解。"
        }
        
        base_prompt = base_prompts.get(context.content_type, base_prompts["ui"])
        
        # 语言特定配置
        lang_names = {
            "zh_CN": "简体中文",
            "zh_TW": "繁體中文", 
            "ja_JP": "日本語",
            "ko_KR": "한국어",
            "es_ES": "Español",
            "fr_FR": "Français",
            "de_DE": "Deutsch",
            "ru_RU": "Русский",
            "ar_SA": "العربية"
        }
        
        lang_name = lang_names.get(target_lang, "目标语言")
        
        return f"""{base_prompt}

上下文：SuperClaude是一个AI增强的开发框架，为Claude Code提供专业的开发工具和多种专家persona支持。

翻译规则：
1. 保持SuperClaude专业术语的准确性和一致性
2. 适应{lang_name}的表达习惯和语言特点
3. 保持原文格式和结构
4. 不要翻译技术标识符（如/sc:analyze、--focus等）
5. 根据内容类型({context.content_type})调整翻译风格
6. 保持专业性和可读性的平衡

请直接输出翻译结果，不要添加额外说明。"""
    
    def _get_target_lang_code(self, lang: str) -> str:
        """转换语言代码为千问API支持的格式"""
        lang_mapping = {
            "zh_CN": "Chinese",
            "zh_TW": "Traditional Chinese", 
            "ja_JP": "Japanese",
            "ko_KR": "Korean",
            "es_ES": "Spanish",
            "fr_FR": "French",
            "de_DE": "German",
            "ru_RU": "Russian",
            "ar_SA": "Arabic"
        }
        return lang_mapping.get(lang, "Chinese")
    
    def _has_superclaude_terms(self, text: str, target_lang: str) -> bool:
        """检查文本是否包含SuperClaude专业术语"""
        text_lower = text.lower()
        for term in self.superclaude_terms:
            if term in text_lower and target_lang in self.superclaude_terms[term]:
                return True
        return False
    
    def _get_terms_for_text(self, text: str, target_lang: str) -> List[Dict[str, str]]:
        """获取文本中的术语干预列表"""
        terms = []
        text_lower = text.lower()
        
        for english_term, translations in self.superclaude_terms.items():
            if english_term in text_lower and target_lang in translations:
                terms.append({
                    "source": english_term,
                    "target": translations[target_lang]
                })
        
        return terms
    
    def _estimate_tokens(self, text: str) -> int:
        """估算文本的token数量"""
        # 简单估算：英文约1.3个字符=1token，中文约1个字符=1token
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            # 包含中文
            return len(text)
        else:
            # 英文文本
            return int(len(text) / 1.3)
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """计算翻译成本（人民币）"""
        config = self.cost_config[self.model]
        input_cost = (input_tokens / 1000) * config["input"]
        output_cost = (output_tokens / 1000) * config["output"]
        return input_cost + output_cost
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """获取支持的语言列表"""
        return [
            {"code": "zh_CN", "name": "简体中文", "native": "简体中文"},
            {"code": "zh_TW", "name": "繁體中文", "native": "繁體中文"},
            {"code": "ja_JP", "name": "Japanese", "native": "日本語"},
            {"code": "ko_KR", "name": "Korean", "native": "한국어"},
            {"code": "es_ES", "name": "Spanish", "native": "Español"},
            {"code": "fr_FR", "name": "French", "native": "Français"},
            {"code": "de_DE", "name": "German", "native": "Deutsch"},
            {"code": "ru_RU", "name": "Russian", "native": "Русский"},
            {"code": "ar_SA", "name": "Arabic", "native": "العربية"}
        ]
    
    def get_cost_estimate(self, content_dict: Dict[str, Dict[str, str]]) -> Dict[str, Union[int, float]]:
        """估算翻译成本"""
        total_chars = 0
        for category, items in content_dict.items():
            for text in items.values():
                total_chars += len(text)
        
        # 估算token数
        estimated_tokens = int(total_chars / 1.2)  # 平均字符到token的转换率
        
        # 假设输入和输出token数接近
        input_tokens = estimated_tokens
        output_tokens = estimated_tokens
        
        cost = self._calculate_cost(input_tokens, output_tokens)
        
        return {
            "total_characters": total_chars,
            "estimated_input_tokens": input_tokens,
            "estimated_output_tokens": output_tokens,
            "estimated_cost_rmb": round(cost, 4),
            "model": self.model
        }


# 兼容性别名，保持与演示工具的一致性
SuperClaudeQwenTranslator = QwenTranslator


if __name__ == "__main__":
    # 测试翻译引擎
    async def test_translator():
        try:
            translator = QwenTranslator()
            
            # 测试单个翻译
            context = translator.contexts["commands"]
            result = await translator.translate_with_context(
                "Multi-dimensional code and system analysis",
                "zh_CN",
                context
            )
            
            print(f"Original: {result.source}")
            print(f"Translated: {result.target}")
            print(f"Cost: ¥{result.cost_estimate:.4f}")
            
        except Exception as e:
            print(f"Test failed: {e}")
            print("Make sure to set DASHSCOPE_API_KEY environment variable")
    
    # 运行测试
    # asyncio.run(test_translator())