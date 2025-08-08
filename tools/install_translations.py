#!/usr/bin/env python3
"""
SuperClaude 翻译文件安装工具
确保翻译文件在所有部署环境下都能正确访问
"""

import os
import sys
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional

def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent.parent

def get_user_claude_dir() -> Path:
    """获取用户Claude目录"""
    return Path.home() / ".claude"

def ensure_translation_accessibility():
    """确保翻译文件在所有环境下都能访问"""
    project_root = get_project_root()
    claude_dir = get_user_claude_dir()
    
    # 创建必要的目录
    i18n_dir = claude_dir / "i18n"
    translations_dir = i18n_dir / "translations"
    i18n_dir.mkdir(parents=True, exist_ok=True)
    translations_dir.mkdir(parents=True, exist_ok=True)
    
    # 源翻译文件目录
    source_locales = project_root / "i18n" / "locales"
    
    if not source_locales.exists():
        print("⚠️ 源翻译文件目录不存在，跳过翻译文件复制")
        return False
    
    success_count = 0
    total_count = 0
    
    # 复制所有翻译文件到用户目录作为后备
    for locale_file in source_locales.glob("*.json"):
        if locale_file.name == "index.json":
            continue  # 跳过索引文件
            
        total_count += 1
        target_file = translations_dir / locale_file.name
        
        try:
            shutil.copy2(locale_file, target_file)
            print(f"✅ 复制翻译文件: {locale_file.name}")
            success_count += 1
        except Exception as e:
            print(f"❌ 复制失败 {locale_file.name}: {e}")
    
    # 安装语言切换器
    switcher_source = project_root / "i18n" / "language_switcher.py"
    switcher_target = i18n_dir / "language_switcher.py"
    
    if switcher_source.exists():
        try:
            shutil.copy2(switcher_source, switcher_target)
            if hasattr(os, 'chmod'):
                os.chmod(switcher_target, 0o755)
            print(f"✅ 安装语言切换器: {switcher_target}")
        except Exception as e:
            print(f"❌ 语言切换器安装失败: {e}")
            return False
    
    print(f"📊 翻译文件安装完成: {success_count}/{total_count}")
    return success_count == total_count

def verify_translation_access():
    """验证翻译文件访问"""
    claude_dir = get_user_claude_dir()
    translations_dir = claude_dir / "i18n" / "translations"
    
    if not translations_dir.exists():
        print("❌ 翻译目录不存在")
        return False
    
    # 检查预期的语言文件
    expected_languages = ["zh_CN", "zh_TW", "ja_JP", "ko_KR", "ru_RU", "es_ES", "de_DE", "fr_FR", "ar_SA"]
    found_languages = []
    
    for lang in expected_languages:
        lang_file = translations_dir / f"{lang}.json"
        if lang_file.exists():
            found_languages.append(lang)
        
    print(f"✅ 找到翻译文件: {', '.join(found_languages)}")
    
    # 测试语言切换器
    switcher_file = claude_dir / "i18n" / "language_switcher.py"
    if switcher_file.exists():
        print(f"✅ 语言切换器已安装: {switcher_file}")
        
        # 尝试运行语言列表命令
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(switcher_file), "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and "zh_TW" in result.stdout:
                print("✅ zh_TW 语言支持验证成功")
                return True
            else:
                print("⚠️ 语言切换器测试未完全通过")
                if result.stderr:
                    print(f"错误: {result.stderr}")
                return False
        except Exception as e:
            print(f"⚠️ 语言切换器测试失败: {e}")
            return False
    else:
        print("❌ 语言切换器未安装")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SuperClaude 翻译文件安装工具")
    parser.add_argument("action", choices=["install", "verify"], 
                       help="操作类型: install(安装) 或 verify(验证)")
    parser.add_argument("--force", action="store_true",
                       help="强制重新安装")
    
    args = parser.parse_args()
    
    if args.action == "install":
        print("🚀 开始安装SuperClaude翻译文件...")
        success = ensure_translation_accessibility()
        if success:
            print("✅ 翻译文件安装成功")
            return 0
        else:
            print("❌ 翻译文件安装失败")
            return 1
    
    elif args.action == "verify":
        print("🔍 验证翻译文件安装状态...")
        success = verify_translation_access()
        if success:
            print("✅ 翻译系统验证通过")
            return 0
        else:
            print("❌ 翻译系统验证失败")
            return 1

if __name__ == "__main__":
    sys.exit(main())