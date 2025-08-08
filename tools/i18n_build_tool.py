#!/usr/bin/env python3
"""
SuperClaude i18n构建工具 / SuperClaude i18n Build Tool
命令行工具，用于构建SuperClaude的多语言本地化文件 / Command-line tool for building SuperClaude multilingual localization files
"""

import sys
import os
import asyncio
import argparse
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from i18n.builder import SuperClaudeI18nBuilder, create_base_english_locale
    from i18n.extractor import SuperClaudeContentExtractor
    from i18n.cache import TranslationCache
    from i18n.translation_engine import TranslationEngineManager, EngineType, create_translation_manager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("请确保从SuperClaude项目根目录运行此工具")
    sys.exit(1)


def print_banner():
    """打印工具横幅 / Print tool banner"""
    print("""
╔══════════════════════════════════════╗
║     SuperClaude i18n Build Tool      ║
║     多引擎AI翻译本地化构建工具           ║
╚══════════════════════════════════════╝
    """)


async def build_languages(languages: list, project_root: str = ".", engine: str = "auto"):
    """构建指定语言"""
    
    try:
        # 初始化引擎管理器
        manager = create_translation_manager()
        
        # 显示可用引擎
        available_engines = manager.get_available_engines()
        print(f"🚀 可用引擎: {', '.join([e.value for e in available_engines])}")
        
        # 选择引擎
        if engine == "auto":
            # 自动选择引擎
            demo_content = {"test": {"item": "test"}}
            selected_engine = manager.recommend_engine(demo_content, priority="quality")
            print(f"🎯 自动选择引擎: {selected_engine.value}")
        else:
            try:
                selected_engine = EngineType(engine.lower())
                if selected_engine not in available_engines:
                    print(f"⚠️ 引擎 '{engine}' 不可用，使用默认引擎")
                    selected_engine = available_engines[0]
                else:
                    print(f"🎯 使用指定引擎: {selected_engine.value}")
            except ValueError:
                print(f"⚠️ 无效引擎 '{engine}'，使用默认引擎")
                selected_engine = available_engines[0]
        
        # 创建构建器（使用翻译引擎管理器）
        builder = SuperClaudeI18nBuilder(project_root, translation_manager=manager)
        
        # 设置引擎管理器使用的引擎
        manager.set_default_engine(selected_engine)
        print(f"🔧 已设置引擎管理器默认引擎: {selected_engine.value}")
        
        # 设置构建超时 (10分钟)
        timeout_seconds = 600
        
        print(f"⏱️  构建超时设置: {timeout_seconds//60} 分钟")
        
        # 构建所有语言 (带超时)
        results = await asyncio.wait_for(
            builder.build_all_languages(languages), 
            timeout=timeout_seconds
        )
        
        if not results:
            print("❌ No languages were built successfully")
            return False
        
        # 保存文件
        builder.save_locale_files(results)
        
        # 生成报告
        report = builder.generate_build_report(results)
        
        # 显示构建报告
        print(f"\n📊 Build Report:")
        print(f"   Languages built: {report['summary']['languages_built']}")
        print(f"   Total translations: {report['summary']['total_translations']}")
        print(f"   Total cost: ¥{report['summary']['total_cost_rmb']}")
        print(f"   Average quality: {report['summary']['average_quality']:.3f}")
        
        # 保存报告
        report_file = Path(project_root) / "i18n" / "build_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"📋 Build report saved: {report_file}")
        
        # 显示建议
        if report["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")
        
        return True
        
    except asyncio.TimeoutError:
        print(f"⏰ 构建超时 ({timeout_seconds//60} 分钟)。请考虑:")
        print("   • 减少翻译内容数量")
        print("   • 检查网络连接")
        print("   • 检查API配额限制")
        return False
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "limit_requests" in error_msg:
            print("🚫 API频率限制错误。建议:")
            print("   • 等待1-2分钟后重试")
            print("   • 检查API配额使用情况")
        elif "400" in error_msg or "invalid_parameter" in error_msg:
            print("⚠️  API参数错误。建议:")
            print("   • 检查API密钥是否正确")
            print("   • 确认模型访问权限")
        else:
            print(f"❌ 构建失败: {e}")
        return False


def extract_content(project_root: str = "."):
    """提取SuperClaude内容"""
    
    try:
        extractor = SuperClaudeContentExtractor(project_root)
        content = extractor.extract_all_content()
        stats = extractor.get_content_statistics()
        
        print(f"📖 SuperClaude Content Statistics:")
        for category, count in stats.items():
            if category != "total":
                print(f"   {category}: {count} items")
        print(f"   Total: {stats['total']} items")
        
        # 显示内容示例
        print(f"\n📝 Content Preview:")
        for category, items in content.items():
            print(f"\n{category.upper()}:")
            for key, text in list(items.items())[:3]:
                preview = text[:60] + "..." if len(text) > 60 else text
                print(f"   {key}: {preview}")
            if len(items) > 3:
                print(f"   ... and {len(items) - 3} more items")
        
        return True
        
    except Exception as e:
        print(f"❌ Content extraction failed: {e}")
        return False


def create_english_base(project_root: str = "."):
    """创建英语基础文件"""
    
    try:
        output_dir = Path(project_root) / "i18n" / "locales"
        create_base_english_locale(output_dir)
        print("✅ English base locale created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create English base: {e}")
        return False


def show_cache_stats(project_root: str = "."):
    """显示缓存统计"""
    
    try:
        cache = TranslationCache()
        stats = cache.get_cache_statistics()
        
        print(f"💾 Translation Cache Statistics:")
        print(f"   Total entries: {stats['total_entries']}")
        print(f"   Total saved cost: ¥{stats['total_saved_cost']}")
        print(f"   Cache file size: {stats['cache_file_size']} bytes")
        print(f"   Cache directory: {stats['cache_directory']}")
        
        if stats['by_language']:
            print(f"\n   By Language:")
            for lang, count in stats['by_language'].items():
                print(f"     {lang}: {count} entries")
        
        if stats['by_content_type']:
            print(f"\n   By Content Type:")
            for content_type, count in stats['by_content_type'].items():
                print(f"     {content_type}: {count} entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to show cache stats: {e}")
        return False


def clear_cache():
    """清理翻译缓存"""
    
    try:
        cache = TranslationCache()
        cache.clear_cache()
        print("✅ Translation cache cleared")
        return True
        
    except Exception as e:
        print(f"❌ Failed to clear cache: {e}")
        return False


def check_environment():
    """检查环境配置"""
    
    issues = []
    
    # 检查API密钥
    qwen_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if qwen_key:
        print("✅ Qwen API key is set")
    else:
        print("⚠️ Qwen API key not found (QWEN_API_KEY or DASHSCOPE_API_KEY)")
    
    if openrouter_key:
        print("✅ OpenRouter API key is set")
    else:
        print("⚠️ OpenRouter API key not found (OPENROUTER_API_KEY)")
    
    if not qwen_key and not openrouter_key:
        issues.append("❌ No translation API keys available")
    
    # 检查项目结构
    required_dirs = ["SuperClaude", "SuperClaude/Commands", "SuperClaude/Core"]
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            issues.append(f"❌ Required directory not found: {dir_name}")
        else:
            print(f"✅ Found directory: {dir_name}")
    
    # 检查关键文件
    required_files = [
        "SuperClaude/Core/PERSONAS.md",
        "SuperClaude/Core/COMMANDS.md"
    ]
    for file_name in required_files:
        if not Path(file_name).exists():
            issues.append(f"⚠️  Optional file not found: {file_name}")
        else:
            print(f"✅ Found file: {file_name}")
    
    if issues:
        print(f"\n⚠️  Issues found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print(f"\n🎉 Environment check passed!")
        return True


async def main():
    """主函数"""
    
    parser = argparse.ArgumentParser(
        description="SuperClaude i18n Build Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build all languages with auto engine selection
  python i18n_build_tool.py --build-all
  
  # Build specific languages with OpenRouter engine
  python i18n_build_tool.py --build zh_CN ja_JP --engine openrouter
  
  # Build using Qwen engine specifically
  python i18n_build_tool.py --build-all --engine qwen
  
  # Extract content only
  python i18n_build_tool.py --extract
  
  # Create English base
  python i18n_build_tool.py --create-base
  
  # Check environment
  python i18n_build_tool.py --check
        """
    )
    
    parser.add_argument("--build", nargs="+", metavar="LANG",
                       help="Build specific languages (zh_CN, ja_JP, ko_KR, etc.)")
    parser.add_argument("--build-all", action="store_true",
                       help="Build all supported languages")
    parser.add_argument("--extract", action="store_true",
                       help="Extract and preview SuperClaude content")
    parser.add_argument("--create-base", action="store_true",
                       help="Create English base locale file")
    parser.add_argument("--cache-stats", action="store_true",
                       help="Show translation cache statistics")
    parser.add_argument("--clear-cache", action="store_true",
                       help="Clear translation cache")
    parser.add_argument("--check", action="store_true",
                       help="Check environment and prerequisites")
    parser.add_argument("--project-root", default=".",
                       help="Project root directory (default: current directory)")
    parser.add_argument("--engine", default="auto", 
                       choices=["auto", "qwen", "openrouter"],
                       help="Translation engine to use (default: auto)")
    
    args = parser.parse_args()
    
    # 显示横幅
    print_banner()
    
    # 如果没有指定任何操作，显示帮助
    if not any([args.build, args.build_all, args.extract, args.create_base,
               args.cache_stats, args.clear_cache, args.check]):
        parser.print_help()
        return
    
    success = True
    
    # 环境检查
    if args.check:
        success = check_environment() and success
    
    # 清理缓存
    if args.clear_cache:
        success = clear_cache() and success
    
    # 显示缓存统计
    if args.cache_stats:
        success = show_cache_stats(args.project_root) and success
    
    # 提取内容
    if args.extract:
        success = extract_content(args.project_root) and success
    
    # 创建英语基础文件
    if args.create_base:
        success = create_english_base(args.project_root) and success
    
    # 构建语言
    if args.build_all:
        languages = ["zh_CN", "zh_TW", "ja_JP", "ko_KR", "ru_RU", 
                    "es_ES", "de_DE", "fr_FR", "ar_SA"]
        success = await build_languages(languages, args.project_root, args.engine) and success
    elif args.build:
        success = await build_languages(args.build, args.project_root, args.engine) and success
    
    # 退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Build interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)