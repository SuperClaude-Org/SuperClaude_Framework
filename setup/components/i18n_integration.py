#!/usr/bin/env python3
"""
SuperClaude i18n系统构建集成 / SuperClaude i18n System Build Integration
将增量翻译功能集成到SuperClaude构建和安装流程中 / Integrate incremental translation functionality into SuperClaude build and installation process
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from i18n.incremental import IncrementalTranslationManager
    from i18n.cache import TranslationCache
    from tools.hooks.translation_hook import TranslationHook
except ImportError as e:
    print(f"⚠️ i18n导入警告: {e}")


class I18nBuildIntegration:
    """i18n构建集成管理器 / i18n Build Integration Manager"""
    
    def __init__(self, project_root: str = None, build_config: Dict[str, Any] = None):
        if project_root is None:
            project_root = PROJECT_ROOT
        
        self.project_root = Path(project_root)
        self.build_config = build_config or self._get_default_config()
        
        # 组件初始化
        self.incremental_manager = None
        self.translation_hook = None
        
        # 构建状态
        self.is_ci_environment = self._detect_ci_environment()
        self.build_mode = self._determine_build_mode()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认构建配置"""
        return {
            "auto_translation": True,           # 是否自动翻译
            "require_translation_success": False,  # 翻译失败时是否阻止构建
            "target_languages": ["zh_CN", "ja_JP", "ko_KR"],  # 默认目标语言
            "cache_enabled": True,              # 启用缓存
            "incremental_enabled": True,        # 启用增量翻译
            "quality_threshold": 0.8,           # 质量阈值
            "ci_auto_translate": False,         # CI环境下是否自动翻译
            "hooks_enabled": True,              # Git hooks集成
            "pre_build_translation": True,     # 构建前翻译
            "post_build_validation": True       # 构建后验证
        }
    
    def _detect_ci_environment(self) -> bool:
        """检测是否在CI环境中"""
        ci_indicators = [
            "CI", "CONTINUOUS_INTEGRATION",
            "GITHUB_ACTIONS", "GITLAB_CI", "TRAVIS", 
            "JENKINS_URL", "BUILDKITE"
        ]
        
        return any(os.getenv(indicator) for indicator in ci_indicators)
    
    def _determine_build_mode(self) -> str:
        """确定构建模式"""
        if self.is_ci_environment:
            return "ci"
        elif os.getenv("SUPERCLAUDE_BUILD_MODE"):
            return os.getenv("SUPERCLAUDE_BUILD_MODE")
        else:
            return "development"
    
    def _initialize_components(self):
        """初始化组件（延迟初始化）"""
        if self.incremental_manager is None:
            try:
                self.incremental_manager = IncrementalTranslationManager(str(self.project_root))
            except Exception as e:
                print(f"⚠️ 增量翻译管理器初始化失败: {e}")
                self.incremental_manager = None
        
        if self.translation_hook is None:
            try:
                self.translation_hook = TranslationHook(str(self.project_root))
            except Exception as e:
                print(f"⚠️ 翻译Hook初始化失败: {e}")
                self.translation_hook = None
    
    def should_run_translation(self) -> bool:
        """判断是否应该运行翻译"""
        # 检查配置
        if not self.build_config.get("auto_translation", True):
            return False
        
        # CI环境检查
        if self.is_ci_environment and not self.build_config.get("ci_auto_translate", False):
            print("ℹ️ CI环境下跳过自动翻译（可通过配置启用）")
            return False
        
        # 环境变量控制
        if os.getenv("SKIP_TRANSLATION", "false").lower() in ("true", "1", "yes"):
            print("ℹ️ 通过环境变量跳过翻译")
            return False
        
        # API密钥检查
        has_qwen = bool(os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY"))
        has_openrouter = bool(os.getenv("OPENROUTER_API_KEY"))
        
        if not (has_qwen or has_openrouter):
            print("⚠️ 未找到翻译API密钥，跳过翻译")
            return False
        
        return True
    
    def run_pre_build_translation(self) -> Dict[str, Any]:
        """构建前翻译处理"""
        print("🚀 构建前翻译检查...")
        
        if not self.should_run_translation():
            return {"status": "skipped", "message": "翻译已跳过"}
        
        self._initialize_components()
        
        if self.incremental_manager is None:
            return {"status": "error", "message": "增量翻译管理器不可用"}
        
        try:
            # 检测变更
            changes = self.incremental_manager.detect_content_changes()
            
            if not changes:
                return {"status": "success", "message": "无变更需要翻译"}
            
            print(f"📋 检测到 {len(changes)} 项内容变更")
            
            # 执行增量翻译
            if self.build_config.get("incremental_enabled", True):
                result = asyncio.run(self._run_incremental_translation(changes))
                return result
            else:
                # 全量翻译模式
                return {"status": "success", "message": "增量翻译已禁用，需手动运行全量翻译"}
                
        except Exception as e:
            error_msg = f"构建前翻译失败: {e}"
            print(f"❌ {error_msg}")
            
            if self.build_config.get("require_translation_success", False):
                return {"status": "error", "message": error_msg}
            else:
                return {"status": "warning", "message": f"翻译失败但继续构建: {e}"}
    
    async def _run_incremental_translation(self, changes: List) -> Dict[str, Any]:
        """运行增量翻译"""
        target_languages = self.build_config.get("target_languages", ["zh_CN"])
        
        try:
            result = await self.incremental_manager.translate_changes(
                changes, target_languages
            )
            
            print(f"✅ 增量翻译完成: {result.get('translations', 0)} 项新翻译")
            return {"status": "success", "result": result}
            
        except Exception as e:
            return {"status": "error", "message": f"增量翻译执行失败: {e}"}
    
    def run_post_build_validation(self) -> Dict[str, Any]:
        """构建后验证"""
        print("✅ 构建后翻译验证...")
        
        if not self.build_config.get("post_build_validation", True):
            return {"status": "skipped", "message": "构建后验证已禁用"}
        
        try:
            validation_results = []
            
            # 检查本地化文件完整性
            locale_dir = self.project_root / "i18n" / "locales"
            target_languages = self.build_config.get("target_languages", ["zh_CN"])
            
            for lang in target_languages:
                locale_file = locale_dir / f"{lang}.json"
                if locale_file.exists():
                    try:
                        import json
                        with open(locale_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # 检查基本结构
                        required_sections = ["metadata", "commands", "personas", "ui"]
                        missing_sections = []
                        
                        for section in required_sections:
                            if section not in data or not data[section]:
                                missing_sections.append(section)
                        
                        if missing_sections:
                            validation_results.append({
                                "language": lang,
                                "status": "warning",
                                "message": f"缺少或为空的部分: {', '.join(missing_sections)}"
                            })
                        else:
                            item_count = sum(len(data[section]) for section in required_sections[1:])
                            validation_results.append({
                                "language": lang,
                                "status": "success",
                                "message": f"验证通过，{item_count} 项翻译"
                            })
                    
                    except Exception as e:
                        validation_results.append({
                            "language": lang,
                            "status": "error",
                            "message": f"文件解析失败: {e}"
                        })
                else:
                    validation_results.append({
                        "language": lang,
                        "status": "warning",
                        "message": "本地化文件不存在"
                    })
            
            # 生成验证报告
            success_count = sum(1 for r in validation_results if r["status"] == "success")
            total_count = len(validation_results)
            
            if success_count == total_count:
                return {
                    "status": "success",
                    "message": f"所有 {total_count} 种语言验证通过",
                    "details": validation_results
                }
            else:
                return {
                    "status": "warning",
                    "message": f"{success_count}/{total_count} 种语言验证通过",
                    "details": validation_results
                }
                
        except Exception as e:
            return {"status": "error", "message": f"构建后验证失败: {e}"}
    
    def install_git_hooks(self) -> Dict[str, Any]:
        """安装Git hooks"""
        if not self.build_config.get("hooks_enabled", True):
            return {"status": "skipped", "message": "Git hooks安装已禁用"}
        
        try:
            from tools.install_hooks import GitHooksInstaller
            
            installer = GitHooksInstaller(str(self.project_root))
            success = installer.install_hooks()
            
            if success:
                return {"status": "success", "message": "Git hooks安装成功"}
            else:
                return {"status": "error", "message": "Git hooks安装失败"}
                
        except ImportError:
            return {"status": "error", "message": "Git hooks安装工具不可用"}
        except Exception as e:
            return {"status": "error", "message": f"Git hooks安装异常: {e}"}
    
    def get_build_integration_status(self) -> Dict[str, Any]:
        """获取构建集成状态"""
        self._initialize_components()
        
        status = {
            "build_mode": self.build_mode,
            "ci_environment": self.is_ci_environment,
            "auto_translation": self.should_run_translation(),
            "components": {
                "incremental_manager": self.incremental_manager is not None,
                "translation_hook": self.translation_hook is not None
            },
            "api_keys": {
                "qwen": bool(os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")),
                "openrouter": bool(os.getenv("OPENROUTER_API_KEY"))
            },
            "config": self.build_config
        }
        
        # 缓存统计
        if self.build_config.get("cache_enabled", True):
            try:
                cache = TranslationCache()
                cache_stats = cache.get_cache_statistics()
                status["cache_stats"] = cache_stats
            except Exception:
                status["cache_stats"] = {"status": "error"}
        
        # 增量翻译统计
        if self.incremental_manager:
            try:
                incremental_stats = self.incremental_manager.get_incremental_statistics()
                status["incremental_stats"] = incremental_stats
            except Exception:
                status["incremental_stats"] = {"status": "error"}
        
        return status
    
    def run_full_build_integration(self) -> Dict[str, Any]:
        """运行完整的构建集成流程"""
        print("🏗️ SuperClaude i18n构建集成")
        print("=" * 50)
        
        results = {}
        overall_success = True
        
        # 1. 构建前翻译
        if self.build_config.get("pre_build_translation", True):
            pre_build_result = self.run_pre_build_translation()
            results["pre_build_translation"] = pre_build_result
            
            if pre_build_result["status"] == "error" and self.build_config.get("require_translation_success", False):
                overall_success = False
        
        # 2. 构建后验证
        if self.build_config.get("post_build_validation", True):
            post_build_result = self.run_post_build_validation()
            results["post_build_validation"] = post_build_result
        
        # 3. Git hooks安装
        if self.build_config.get("hooks_enabled", True):
            hooks_result = self.install_git_hooks()
            results["git_hooks"] = hooks_result
        
        # 生成总结
        results["summary"] = {
            "overall_success": overall_success,
            "build_mode": self.build_mode,
            "ci_environment": self.is_ci_environment,
            "status": "success" if overall_success else "partial_failure"
        }
        
        return results


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SuperClaude i18n构建集成")
    parser.add_argument("action", choices=["integrate", "status", "hooks", "validate"],
                       help="操作类型")
    parser.add_argument("--project-root", default=".",
                       help="项目根目录")
    parser.add_argument("--config-file", 
                       help="构建配置文件路径")
    parser.add_argument("--ci", action="store_true",
                       help="强制CI模式")
    
    args = parser.parse_args()
    
    # 加载配置
    build_config = None
    if args.config_file:
        try:
            import json
            with open(args.config_file, 'r', encoding='utf-8') as f:
                build_config = json.load(f)
        except Exception as e:
            print(f"⚠️ 加载配置文件失败: {e}")
    
    # 强制CI模式
    if args.ci:
        os.environ["CI"] = "true"
    
    # 创建集成管理器
    integration = I18nBuildIntegration(args.project_root, build_config)
    
    if args.action == "integrate":
        result = integration.run_full_build_integration()
        print(f"\n📊 构建集成结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return 0 if result["summary"]["overall_success"] else 1
    
    elif args.action == "status":
        status = integration.get_build_integration_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return 0
    
    elif args.action == "hooks":
        result = integration.install_git_hooks()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "success" else 1
    
    elif args.action == "validate":
        result = integration.run_post_build_validation()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] in ["success", "warning"] else 1


if __name__ == "__main__":
    sys.exit(main())