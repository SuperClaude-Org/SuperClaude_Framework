#!/usr/bin/env python3
"""
SuperClaude翻译构建器 / SuperClaude Translation Builder
基于千问3的开发时翻译工具，生成完整的本地化文件 / Development-time translation tool based on Qwen3, generates complete localization files
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from .extractor import SuperClaudeContentExtractor
from .translator import QwenTranslator, TranslationContext
from .validator import QualityValidator
from .cache import TranslationCache


@dataclass
class BuildMetadata:
    """构建元数据 / Build metadata"""
    language: str
    name: str
    version: str
    build_time: str
    total_items: int
    build_cost: float
    quality_score: float
    

@dataclass
class LocaleFileData:
    """本地化文件数据结构 / Localization file data structure"""
    metadata: Dict[str, Any]
    commands: Dict[str, str]
    personas: Dict[str, str]
    ui: Dict[str, str]
    errors: Dict[str, str]
    help: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 / Convert to dictionary"""
        return {
            "metadata": self.metadata,
            "commands": self.commands,
            "personas": self.personas,
            "ui": self.ui,
            "errors": self.errors,
            "help": self.help
        }


class SuperClaudeI18nBuilder:
    """SuperClaude i18n构建器 - 开发时翻译工具 / SuperClaude i18n Builder - Development-time translation tool"""
    
    def __init__(self, project_root: str = ".", enable_cache: bool = True, translation_manager=None):
        """
        初始化构建器 / Initialize builder
        
        Args:
            project_root: 项目根目录 / Project root directory
            enable_cache: 是否启用翻译缓存 / Whether to enable translation cache
            translation_manager: 翻译引擎管理器，如果为None则使用默认QwenTranslator / Translation engine manager, uses default QwenTranslator if None
        """
        self.project_root = Path(project_root)
        self.output_dir = self.project_root / "i18n" / "locales"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化组件 / Initialize components
        self.extractor = SuperClaudeContentExtractor(project_root)
        
        # 使用翻译引擎管理器或默认翻译器 / Use translation engine manager or default translator
        if translation_manager is not None:
            self.translation_manager = translation_manager
            self.translator = None  # 使用管理器时不直接使用translator / Don't use translator directly when using manager
        else:
            self.translator = QwenTranslator()
            self.translation_manager = None
            
        self.validator = QualityValidator()
        self.cache = TranslationCache() if enable_cache else None
        
        self.language_config = {
            "zh_CN": {"name": "简体中文", "priority": 1},
            "zh_TW": {"name": "繁體中文", "priority": 2},
            "ja_JP": {"name": "日本語", "priority": 3},
            "ko_KR": {"name": "한국어", "priority": 4},
            "ru_RU": {"name": "Русский", "priority": 5},
            "es_ES": {"name": "Español", "priority": 6},
            "de_DE": {"name": "Deutsch", "priority": 7},
            "fr_FR": {"name": "Français", "priority": 8},
            "ar_SA": {"name": "العربية", "priority": 9}
        }
        
        print(f"🏗️  SuperClaude i18n Builder initialized")
        print(f"📁 Project root: {self.project_root}")
        print(f"📤 Output directory: {self.output_dir}")
    
    async def build_single_language(self, target_lang: str) -> LocaleFileData:
        """构建单个语言的本地化文件 / Build localization file for a single language"""
        
        print(f"\n🌍 Building {target_lang} ({self.language_config[target_lang]['name']})...")
        
        # 1. 提取SuperClaude内容 / Extract SuperClaude content
        print("📖 Extracting SuperClaude content...")
        source_content = self.extractor.extract_all_content()
        
        stats = self.extractor.get_content_statistics()
        print(f"   Found {stats['total']} items: {dict(stats)}")
        
        # 2. 翻译内容 / Translate content
        print("🔄 Translating content...")
        if self.translation_manager:
            translated_content = await self.translation_manager.translate_superclaude_content(
                source_content, target_lang
            )
        else:
            translated_content = await self.translator.translate_superclaude_content(
                source_content, target_lang
            )
        
        # 3. 质量验证 / Quality validation
        print("✅ Validating translation quality...")
        validation_results = self._validate_translations(
            source_content, translated_content, target_lang
        )
        
        quality_report = self.validator.generate_quality_report(validation_results)
        quality_score = quality_report["summary"]["average_score"]
        
        print(f"   Quality score: {quality_score:.3f}")
        print(f"   Pass rate: {quality_report['summary']['pass_rate']:.3f}")
        
        # 4. 构建本地化文件 / Build localization file
        build_metadata = BuildMetadata(
            language=target_lang,
            name=self.language_config[target_lang]["name"],
            version="1.0.0",
            build_time=datetime.now().isoformat(),
            total_items=stats["total"],
            build_cost=self._estimate_build_cost(source_content),
            quality_score=quality_score
        )
        
        locale_data = LocaleFileData(
            metadata=asdict(build_metadata),
            commands=translated_content.get("commands", {}),
            personas=translated_content.get("personas", {}),
            ui=translated_content.get("ui", {}),
            errors=translated_content.get("errors", {}),
            help=translated_content.get("help", {})
        )
        
        print(f"✅ Completed {target_lang}: {stats['total']} translations")
        return locale_data
    
    async def build_all_languages(self, target_languages: List[str] = None) -> Dict[str, LocaleFileData]:
        """构建所有语言的本地化文件 / Build localization files for all languages"""
        
        if target_languages is None:
            target_languages = list(self.language_config.keys())
        
        print(f"🚀 Building {len(target_languages)} languages...")
        
        results = {}
        total_start = time.time()
        
        for lang in target_languages:
            if lang not in self.language_config:
                print(f"⚠️  Unsupported language: {lang}")
                continue
            
            try:
                start_time = time.time()
                locale_data = await self.build_single_language(lang)
                results[lang] = locale_data
                
                build_time = time.time() - start_time
                print(f"   Built in {build_time:.1f}s")
                
            except Exception as e:
                print(f"❌ Failed to build {lang}: {e}")
                continue
        
        total_time = time.time() - total_start
        total_cost = sum(data.metadata["build_cost"] for data in results.values())
        
        print(f"\n🎉 Build completed!")
        print(f"   Languages: {len(results)}")
        print(f"   Total time: {total_time:.1f}s")
        print(f"   Total cost: ¥{total_cost:.4f}")
        
        return results
    
    def save_locale_files(self, locale_data_map: Dict[str, LocaleFileData]):
        """保存本地化文件到磁盘 / Save localization files to disk"""
        
        print(f"\n💾 Saving locale files...")
        
        for lang, locale_data in locale_data_map.items():
            file_path = self.output_dir / f"{lang}.json"
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(locale_data.to_dict(), f, ensure_ascii=False, indent=2)
            
            total_items = locale_data.metadata["total_items"]
            print(f"   {lang}.json ({total_items} items)")
        
        # 创建语言索引文件 / Create language index file
        self._create_language_index(locale_data_map)
        
        print(f"📋 Created language index")
    
    def _create_language_index(self, locale_data_map: Dict[str, LocaleFileData]):
        """创建语言索引文件 / Create language index file"""
        
        index_data = {
            "supported_languages": list(locale_data_map.keys()),
            "default_language": "en_US",
            "fallback_language": "en_US", 
            "build_time": datetime.now().isoformat(),
            "languages": {}
        }
        
        for lang, locale_data in locale_data_map.items():
            index_data["languages"][lang] = {
                "name": locale_data.metadata["name"],
                "total_items": locale_data.metadata["total_items"],
                "quality_score": locale_data.metadata["quality_score"],
                "build_cost": locale_data.metadata["build_cost"]
            }
        
        index_file = self.output_dir / "index.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def _validate_translations(self, 
                             source_content: Dict[str, Dict[str, str]],
                             translated_content: Dict[str, Dict[str, str]],
                             target_lang: str) -> Dict[str, Any]:
        """验证翻译质量 / Validate translation quality"""
        
        validation_pairs = []
        
        for category in source_content:
            if category not in translated_content:
                continue
                
            source_items = source_content[category]
            translated_items = translated_content[category]
            
            for key in source_items:
                if key in translated_items:
                    validation_pairs.append((
                        source_items[key],
                        translated_items[key], 
                        target_lang,
                        category
                    ))
        
        return self.validator.batch_validate(validation_pairs)
    
    def _estimate_build_cost(self, source_content: Dict[str, Dict[str, str]]) -> float:
        """估算构建成本 / Estimate build cost"""
        if self.translation_manager:
            cost_info = self.translation_manager.get_cost_estimate(source_content)
            # 根据引擎类型返回相应的成本 / Return corresponding cost based on engine type
            if "estimated_cost_usd" in cost_info:
                return cost_info["estimated_cost_usd"]  # OpenRouter返回USD / OpenRouter returns USD
            elif "estimated_cost_rmb" in cost_info:
                return cost_info["estimated_cost_rmb"]  # Qwen返回RMB / Qwen returns RMB
            else:
                return 0.0
        else:
            return self.translator.get_cost_estimate(source_content)["estimated_cost_rmb"]
    
    def generate_build_report(self, locale_data_map: Dict[str, LocaleFileData]) -> Dict:
        """生成构建报告 / Generate build report"""
        
        total_items = sum(data.metadata["total_items"] for data in locale_data_map.values())
        total_cost = sum(data.metadata["build_cost"] for data in locale_data_map.values()) 
        avg_quality = sum(data.metadata["quality_score"] for data in locale_data_map.values()) / len(locale_data_map)
        
        return {
            "summary": {
                "languages_built": len(locale_data_map),
                "total_translations": total_items,
                "total_cost_rmb": round(total_cost, 4),
                "average_quality": round(avg_quality, 3),
                "build_time": datetime.now().isoformat()
            },
            "by_language": {
                lang: {
                    "name": data.metadata["name"],
                    "items": data.metadata["total_items"],
                    "cost": data.metadata["build_cost"],
                    "quality": data.metadata["quality_score"]
                }
                for lang, data in locale_data_map.items()
            },
            "recommendations": self._generate_build_recommendations(locale_data_map)
        }
    
    def _generate_build_recommendations(self, locale_data_map: Dict[str, LocaleFileData]) -> List[str]:
        """生成构建建议 / Generate build recommendations"""
        recommendations = []
        
        # 检查质量分数 / Check quality scores
        low_quality_langs = [
            lang for lang, data in locale_data_map.items()
            if data.metadata["quality_score"] < 0.8
        ]
        
        if low_quality_langs:
            recommendations.append(f"以下语言质量较低，建议人工校验: {', '.join(low_quality_langs)}")
        
        # 检查成本 / Check cost
        total_cost = sum(data.metadata["build_cost"] for data in locale_data_map.values())
        if total_cost > 10.0:
            recommendations.append("构建成本较高，建议启用缓存以减少重复翻译 / Build cost is high, recommend enabling cache to reduce duplicate translations")
        
        # 通用建议 / General recommendations
        recommendations.append("定期更新术语词典以提高翻译一致性 / Regularly update terminology dictionary to improve translation consistency")
        recommendations.append("建议社区贡献者review翻译质量 / Recommend community contributors to review translation quality")
        
        return recommendations


# 创建默认的英语基础文件 / Create default English base file
def create_base_english_locale(output_dir: Path):
    """创建英语基础本地化文件 / Create English base localization file"""
    
    extractor = SuperClaudeContentExtractor()
    source_content = extractor.extract_all_content()
    
    # 英语作为基础语言，直接使用原文 / English as base language, use original text directly
    base_locale = LocaleFileData(
        metadata={
            "language": "en_US",
            "name": "English",
            "version": "1.0.0",
            "build_time": datetime.now().isoformat(),
            "total_items": sum(len(items) for items in source_content.values()),
            "build_cost": 0.0,
            "quality_score": 1.0
        },
        commands=source_content.get("commands", {}),
        personas=source_content.get("personas", {}),
        ui=source_content.get("ui", {}),
        errors=source_content.get("errors", {}),
        help=source_content.get("help", {})
    )
    
    output_dir.mkdir(parents=True, exist_ok=True)
    en_file = output_dir / "en_US.json"
    
    with open(en_file, "w", encoding="utf-8") as f:
        json.dump(base_locale.to_dict(), f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created base English locale: {en_file}")


if __name__ == "__main__":
    # 测试构建器 / Test builder
    async def test_builder():
        builder = SuperClaudeI18nBuilder()
        
        # 构建中文 / Build Chinese
        zh_locale = await builder.build_single_language("zh_CN")
        
        # 保存文件 / Save files
        builder.save_locale_files({"zh_CN": zh_locale})
        
        # 生成报告 / Generate report
        report = builder.generate_build_report({"zh_CN": zh_locale})
        print(f"\nBuild Report:")
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    # 运行测试（需要设置DASHSCOPE_API_KEY） / Run test (requires DASHSCOPE_API_KEY to be set)
    # asyncio.run(test_builder())