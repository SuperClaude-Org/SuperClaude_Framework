#!/usr/bin/env python3
"""
OpenRouter翻译引擎
集成OpenRouter API使用Google Gemini 2.5 Flash模型进行翻译
"""

import os
import asyncio
import json
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from openai import OpenAI

from .translator import TranslationContext, TranslationResult


@dataclass
class OpenRouterConfig:
    """OpenRouter配置"""
    api_key: str
    model: str = "google/gemini-2.5-flash"
    base_url: str = "https://openrouter.ai/api/v1"
    max_tokens: int = 4000
    temperature: float = 0.3


class OpenRouterTranslator:
    """OpenRouter翻译引擎 - 基于Gemini 2.5 Flash的专业翻译"""
    
    def __init__(self, config: Optional[OpenRouterConfig] = None):
        """
        初始化OpenRouter翻译引擎
        
        Args:
            config: OpenRouter配置，如果为None则从环境变量读取
        """
        if config is None:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("请设置环境变量 OPENROUTER_API_KEY")
            config = OpenRouterConfig(api_key=api_key)
        
        self.config = config
        self.client = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
        )
        
        # 成本配置 (OpenRouter Gemini 2.0 Flash定价)
        self.cost_config = {
            "input": 0.000075,   # $0.075 per 1M tokens
            "output": 0.0003     # $0.30 per 1M tokens
        }
        
        # SuperClaude 专用术语词典
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
        
        # 预定义翻译上下文
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
        
        # 构建Gemini优化的翻译提示
        system_prompt = self._build_gemini_prompt(context, target_lang)
        
        # 添加术语干预
        terms_context = ""
        if self._has_superclaude_terms(text, target_lang):
            terms = self._get_terms_for_text(text, target_lang)
            if terms:
                terms_list = [f"- {t['source']} → {t['target']}" for t in terms]
                terms_context = f"\n\n专业术语对照:\n" + "\n".join(terms_list)
        
        user_prompt = f"""{system_prompt}

请将以下文本翻译为{self._get_language_name(target_lang)}：

"{text}"

{terms_context}

请只返回翻译结果，不要包含任何其他内容。"""
        
        messages = [
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            completion = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                extra_headers={
                    "HTTP-Referer": "https://github.com/SuperClaude/SuperClaude",
                    "X-Title": "SuperClaude i18n Translation System"
                }
            )
            
            translated_text = completion.choices[0].message.content.strip()
            
            # 估算成本
            input_tokens = completion.usage.prompt_tokens if completion.usage else self._estimate_tokens(text)
            output_tokens = completion.usage.completion_tokens if completion.usage else self._estimate_tokens(translated_text)
            cost = self._calculate_cost(input_tokens, output_tokens)
            
            return TranslationResult(
                source=text,
                target=translated_text,
                lang=target_lang,
                context=context.content_type,
                confidence=0.95,  # Gemini翻译质量较高
                cost_estimate=cost
            )
            
        except Exception as e:
            print(f"OpenRouter translation error: {e}")
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
        """优化的批量翻译，利用Gemini的长上下文能力"""
        
        # Gemini 2.5 Flash: 1M context window
        MAX_BATCH_SIZE = 20  # 每次最多20条文本
        REQUESTS_PER_MINUTE = 30  # OpenRouter限制
        MIN_DELAY = 60.0 / REQUESTS_PER_MINUTE  # 最小间隔2秒
        
        results = []
        
        # 将文本分批处理
        for i in range(0, len(texts), MAX_BATCH_SIZE):
            batch_texts = texts[i:i + MAX_BATCH_SIZE]
            
            if len(batch_texts) > 1:
                # 批量翻译，利用Gemini的长上下文
                batch_results = await self._translate_batch_optimized(
                    batch_texts, target_lang, context
                )
            else:
                # 单条文本直接翻译
                result = await self.translate_with_context(batch_texts[0], target_lang, context)
                batch_results = [result]
            
            results.extend(batch_results)
            
            # 添加频率控制延迟
            if i + MAX_BATCH_SIZE < len(texts):
                print(f"  处理进度: {min(i + MAX_BATCH_SIZE, len(texts))}/{len(texts)}")
                await asyncio.sleep(MIN_DELAY)
        
        return results
    
    async def _translate_batch_optimized(self, 
                                       texts: List[str], 
                                       target_lang: str,
                                       context: TranslationContext) -> List[TranslationResult]:
        """利用Gemini长上下文的批量翻译"""
        
        # 构建批量翻译提示
        system_prompt = self._build_gemini_prompt(context, target_lang)
        
        # 创建JSON格式的批量输入
        batch_input = {}
        for i, text in enumerate(texts, 1):
            batch_input[str(i)] = text
        
        # 术语上下文
        terms_context = ""
        all_terms = set()
        for text in texts:
            if self._has_superclaude_terms(text, target_lang):
                terms = self._get_terms_for_text(text, target_lang)
                for term in terms:
                    all_terms.add(f"- {term['source']} → {term['target']}")
        
        if all_terms:
            terms_context = f"\n\n专业术语对照:\n" + "\n".join(sorted(all_terms))
        
        user_prompt = f"""请将以下JSON中的所有文本翻译为{self._get_language_name(target_lang)}，保持相同的JSON结构和键名：

输入JSON:
{json.dumps(batch_input, ensure_ascii=False, indent=2)}

翻译要求：
{system_prompt}{terms_context}

请只返回翻译后的JSON，保持相同格式，不要包含其他解释。"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        try:
            completion = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                extra_headers={
                    "HTTP-Referer": "https://github.com/SuperClaude/SuperClaude",
                    "X-Title": "SuperClaude i18n Translation System"
                }
            )
            
            response_text = completion.choices[0].message.content.strip()
            
            # 解析JSON响应
            try:
                # 清理可能的markdown代码块
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                translated_data = json.loads(response_text)
                
                results = []
                for i, text in enumerate(texts, 1):
                    key = str(i)
                    if key in translated_data:
                        translated_text = translated_data[key]
                    else:
                        translated_text = f"[Translation failed: missing key {key}]"
                    
                    # 估算成本
                    input_tokens = completion.usage.prompt_tokens if completion.usage else self._estimate_tokens(user_prompt)
                    output_tokens = completion.usage.completion_tokens if completion.usage else self._estimate_tokens(response_text)
                    cost_per_item = self._calculate_cost(input_tokens, output_tokens) / len(texts)
                    
                    results.append(TranslationResult(
                        source=text,
                        target=translated_text,
                        lang=target_lang,
                        context=context.content_type,
                        confidence=0.92,  # 批量翻译稍微降低置信度
                        cost_estimate=cost_per_item
                    ))
                
                return results
                
            except json.JSONDecodeError as e:
                print(f"Batch translation JSON parsing error: {e}")
                print(f"Raw response: {response_text[:200]}...")
                # 降级到单个翻译
                return await self._fallback_individual_translation(texts, target_lang, context)
            
        except Exception as e:
            print(f"Batch translation error: {e}")
            # 降级到单个翻译
            return await self._fallback_individual_translation(texts, target_lang, context)
    
    async def _fallback_individual_translation(self, 
                                             texts: List[str], 
                                             target_lang: str,
                                             context: TranslationContext) -> List[TranslationResult]:
        """降级到单个翻译"""
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
        
        print(f"Total estimated cost: ${total_cost:.4f}")
        return translated_content
    
    def _build_gemini_prompt(self, context: TranslationContext, target_lang: str) -> str:
        """构建Gemini优化的翻译提示"""
        
        base_prompts = {
            "command": "这是SuperClaude命令的描述。请提供技术准确、简洁专业的翻译，保持术语一致性。",
            "persona": "这是SuperClaude专家角色的描述。请体现专业性和角色特点，保持描述准确性。",
            "ui": "这是SuperClaude界面文本。请提供简洁明了、用户友好的翻译。",
            "error_message": "这是SuperClaude错误信息。请清晰直接地翻译，帮助用户理解问题。",
            "help": "这是SuperClaude帮助文档。请详细清晰地翻译，保持指导性。"
        }
        
        base_prompt = base_prompts.get(context.content_type, base_prompts["ui"])
        
        lang_names = {
            "zh_CN": "简体中文",
            "zh_TW": "繁體中文", 
            "ja_JP": "日本語",
            "ko_KR": "한국어",
            "es_ES": "español",
            "fr_FR": "français",
            "de_DE": "Deutsch",
            "ru_RU": "русский язык",
            "ar_SA": "العربية"
        }
        
        lang_name = lang_names.get(target_lang, "目标语言")
        
        return f"""SuperClaude是AI增强的开发框架，为Claude Code提供专业开发工具。

{base_prompt}

翻译要求：
1. 保持SuperClaude专业术语的准确性和一致性
2. 适应{lang_name}的表达习惯
3. 保持原文格式和结构
4. 不要翻译技术标识符（如/sc:analyze、--focus等）
5. 根据内容类型({context.content_type})调整翻译风格"""
    
    def _get_language_name(self, lang_code: str) -> str:
        """获取语言名称"""
        lang_names = {
            "zh_CN": "简体中文",
            "zh_TW": "繁體中文", 
            "ja_JP": "日本語",
            "ko_KR": "한국어",
            "es_ES": "español",
            "fr_FR": "français",
            "de_DE": "Deutsch",
            "ru_RU": "русский язык",
            "ar_SA": "العربية"
        }
        return lang_names.get(lang_code, "目标语言")
    
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
        # Gemini简单估算：英文约4个字符=1token，中文约1.5个字符=1token
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            # 包含中文
            return int(len(text) / 1.5)
        else:
            # 英文文本
            return int(len(text) / 4)
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """计算翻译成本（美元）"""
        input_cost = (input_tokens / 1000000) * self.cost_config["input"]
        output_cost = (output_tokens / 1000000) * self.cost_config["output"]
        return input_cost + output_cost
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """获取支持的语言列表"""
        return [
            {"code": "zh_CN", "name": "简体中文", "native": "简体中文"},
            {"code": "zh_TW", "name": "繁體中文", "native": "繁體中文"},
            {"code": "ja_JP", "name": "Japanese", "native": "日本語"},
            {"code": "ko_KR", "name": "Korean", "native": "한국어"},
            {"code": "es_ES", "name": "Spanish", "native": "español"},
            {"code": "fr_FR", "name": "French", "native": "français"},
            {"code": "de_DE", "name": "German", "native": "Deutsch"},
            {"code": "ru_RU", "name": "Russian", "native": "русский язык"},
            {"code": "ar_SA", "name": "Arabic", "native": "العربية"}
        ]
    
    def get_cost_estimate(self, content_dict: Dict[str, Dict[str, str]]) -> Dict[str, Union[int, float]]:
        """估算翻译成本"""
        total_chars = 0
        for category, items in content_dict.items():
            for text in items.values():
                total_chars += len(text)
        
        # 估算token数
        estimated_tokens = self._estimate_tokens(" ".join(
            text for category in content_dict.values() 
            for text in category.values()
        ))
        
        # 假设输入和输出token数接近
        input_tokens = estimated_tokens
        output_tokens = estimated_tokens
        
        cost = self._calculate_cost(input_tokens, output_tokens)
        
        return {
            "total_characters": total_chars,
            "estimated_input_tokens": input_tokens,
            "estimated_output_tokens": output_tokens,
            "estimated_cost_usd": round(cost, 6),
            "model": self.config.model
        }


if __name__ == "__main__":
    # 测试OpenRouter翻译引擎
    async def test_openrouter_translator():
        try:
            translator = OpenRouterTranslator()
            
            # 测试单个翻译
            context = translator.contexts["commands"]
            result = await translator.translate_with_context(
                "Multi-dimensional code and system analysis",
                "zh_CN",
                context
            )
            
            print(f"Original: {result.source}")
            print(f"Translated: {result.target}")
            print(f"Cost: ${result.cost_estimate:.6f}")
            
        except Exception as e:
            print(f"Test failed: {e}")
            print("Make sure to set OPENROUTER_API_KEY environment variable")
    
    # 运行测试
    # asyncio.run(test_openrouter_translator())