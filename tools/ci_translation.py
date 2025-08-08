#!/usr/bin/env python3
"""
SuperClaude CI环境翻译工具 / SuperClaude CI Environment Translation Tool
专为CI/CD环境设计的轻量级翻译工具 / Lightweight translation tool designed for CI/CD environments
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from i18n.incremental import IncrementalTranslationManager
    from i18n.cache import TranslationCache
    from i18n.extractor import SuperClaudeContentExtractor
    from setup.components.i18n_integration import I18nBuildIntegration
except ImportError as e:
    print(f"⚠️ 导入警告: {e}")
    print("CI翻译工具将在基础模式下运行")


class CITranslationTool:
    """CI环境翻译工具 / CI Environment Translation Tool"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or PROJECT_ROOT)
        self.ci_environment = self._detect_ci_environment()
        self.github_context = self._get_github_context()
        
        # 初始化组件
        self.extractor = None
        self.incremental_manager = None
        self.cache = None
        self.build_integration = None
    
    def _detect_ci_environment(self) -> Dict[str, Any]:
        """检测CI环境"""
        ci_info = {
            "is_ci": bool(os.getenv("CI")),
            "provider": "unknown",
            "workflow_name": None,
            "build_number": None,
            "branch": None,
            "commit_sha": None
        }
        
        # GitHub Actions
        if os.getenv("GITHUB_ACTIONS"):
            ci_info.update({
                "provider": "github_actions",
                "workflow_name": os.getenv("GITHUB_WORKFLOW"),
                "build_number": os.getenv("GITHUB_RUN_NUMBER"),
                "branch": os.getenv("GITHUB_REF_NAME"),
                "commit_sha": os.getenv("GITHUB_SHA")
            })
        
        # GitLab CI
        elif os.getenv("GITLAB_CI"):
            ci_info.update({
                "provider": "gitlab_ci", 
                "workflow_name": os.getenv("CI_JOB_NAME"),
                "build_number": os.getenv("CI_JOB_ID"),
                "branch": os.getenv("CI_COMMIT_REF_NAME"),
                "commit_sha": os.getenv("CI_COMMIT_SHA")
            })
        
        # Travis CI
        elif os.getenv("TRAVIS"):
            ci_info.update({
                "provider": "travis_ci",
                "build_number": os.getenv("TRAVIS_BUILD_NUMBER"),
                "branch": os.getenv("TRAVIS_BRANCH"),
                "commit_sha": os.getenv("TRAVIS_COMMIT")
            })
        
        return ci_info
    
    def _get_github_context(self) -> Dict[str, Any]:
        """获取GitHub上下文"""
        return {
            "event_name": os.getenv("GITHUB_EVENT_NAME"),
            "repository": os.getenv("GITHUB_REPOSITORY"),
            "actor": os.getenv("GITHUB_ACTOR"),
            "workflow": os.getenv("GITHUB_WORKFLOW"),
            "job": os.getenv("GITHUB_JOB"),
            "run_id": os.getenv("GITHUB_RUN_ID"),
            "run_number": os.getenv("GITHUB_RUN_NUMBER")
        }
    
    def _initialize_components(self):
        """初始化组件"""
        try:
            if self.extractor is None:
                self.extractor = SuperClaudeContentExtractor(str(self.project_root))
            
            if self.incremental_manager is None:
                self.incremental_manager = IncrementalTranslationManager(str(self.project_root))
            
            if self.cache is None:
                self.cache = TranslationCache()
                
            if self.build_integration is None:
                self.build_integration = I18nBuildIntegration(str(self.project_root))
                
        except Exception as e:
            print(f"⚠️ 组件初始化警告: {e}")
    
    def check_api_credentials(self) -> Dict[str, bool]:
        """检查API凭据可用性"""
        return {
            "qwen": bool(os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")),
            "openrouter": bool(os.getenv("OPENROUTER_API_KEY")),
            "has_any": bool(
                os.getenv("QWEN_API_KEY") or 
                os.getenv("DASHSCOPE_API_KEY") or 
                os.getenv("OPENROUTER_API_KEY")
            )
        }
    
    def extract_and_analyze_content(self) -> Dict[str, Any]:
        """提取和分析内容"""
        self._initialize_components()
        
        if self.extractor is None:
            return {"status": "error", "message": "内容提取器不可用"}
        
        try:
            print("📖 提取SuperClaude内容...")
            content = self.extractor.extract_all_content()
            stats = self.extractor.get_content_statistics()
            
            result = {
                "status": "success",
                "content_stats": dict(stats),
                "content_summary": {
                    "total_items": stats["total"],
                    "categories": list(content.keys()),
                    "largest_category": max(content.keys(), key=lambda k: len(content[k])) if content else None
                }
            }
            
            print(f"📊 内容统计: {dict(stats)}")
            return result
            
        except Exception as e:
            return {"status": "error", "message": f"内容提取失败: {e}"}
    
    async def detect_changes(self) -> Dict[str, Any]:
        """检测内容变更"""
        self._initialize_components()
        
        if self.incremental_manager is None:
            return {"status": "error", "message": "增量翻译管理器不可用"}
        
        try:
            print("🔍 检测内容变更...")
            changes = self.incremental_manager.detect_content_changes()
            
            result = {
                "status": "success",
                "changes_detected": len(changes),
                "changes": []
            }
            
            # 添加变更详情（限制数量避免输出过多）
            for change in changes[:10]:  # 只显示前10项变更
                result["changes"].append({
                    "key": change.key,
                    "content_type": change.content_type,
                    "change_type": change.change_type,
                    "new_text_preview": change.new_text[:100] + "..." if len(change.new_text) > 100 else change.new_text
                })
            
            if len(changes) > 10:
                result["changes_truncated"] = f"显示前10项，共{len(changes)}项变更"
            
            print(f"📋 检测到 {len(changes)} 项变更")
            return result
            
        except Exception as e:
            return {"status": "error", "message": f"变更检测失败: {e}"}
    
    async def run_incremental_translation(self, target_languages: List[str] = None, 
                                        dry_run: bool = False) -> Dict[str, Any]:
        """运行增量翻译"""
        self._initialize_components()
        
        if self.incremental_manager is None:
            return {"status": "error", "message": "增量翻译管理器不可用"}
        
        # 检查API凭据
        credentials = self.check_api_credentials()
        if not credentials["has_any"] and not dry_run:
            return {
                "status": "skipped",
                "message": "未配置翻译API密钥，运行dry-run模式",
                "credentials": credentials
            }
        
        if target_languages is None:
            target_languages = ["zh_CN", "ja_JP", "ko_KR"]
        
        try:
            # 检测变更
            changes = self.incremental_manager.detect_content_changes()
            
            if not changes:
                return {
                    "status": "success",
                    "message": "未检测到需要翻译的变更",
                    "changes": 0,
                    "translations": 0
                }
            
            print(f"🚀 准备翻译 {len(changes)} 项变更到 {len(target_languages)} 种语言...")
            
            if dry_run:
                # Dry run模式：只检测，不执行翻译
                return {
                    "status": "success",
                    "message": f"Dry run完成: 检测到 {len(changes)} 项变更",
                    "mode": "dry_run",
                    "changes": len(changes),
                    "target_languages": target_languages,
                    "estimated_translations": len(changes) * len(target_languages)
                }
            else:
                # 执行实际翻译
                result = await self.incremental_manager.translate_changes(changes, target_languages)
                return {
                    "status": "success",
                    "message": f"增量翻译完成",
                    "mode": "translation",
                    "result": result
                }
                
        except Exception as e:
            return {"status": "error", "message": f"增量翻译失败: {e}"}
    
    def validate_translations(self) -> Dict[str, Any]:
        """验证翻译质量"""
        self._initialize_components()
        
        if self.build_integration is None:
            return {"status": "error", "message": "构建集成组件不可用"}
        
        try:
            print("✅ 验证翻译质量...")
            result = self.build_integration.run_post_build_validation()
            return result
            
        except Exception as e:
            return {"status": "error", "message": f"翻译验证失败: {e}"}
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """获取综合状态"""
        self._initialize_components()
        
        status = {
            "ci_environment": self.ci_environment,
            "github_context": self.github_context,
            "credentials": self.check_api_credentials(),
            "project_info": {
                "root": str(self.project_root),
                "exists": self.project_root.exists()
            }
        }
        
        # 缓存状态
        if self.cache:
            try:
                cache_stats = self.cache.get_cache_statistics()
                status["cache"] = cache_stats
            except Exception as e:
                status["cache"] = {"status": "error", "message": str(e)}
        
        # 增量翻译状态
        if self.incremental_manager:
            try:
                incremental_stats = self.incremental_manager.get_incremental_statistics()
                status["incremental"] = incremental_stats
            except Exception as e:
                status["incremental"] = {"status": "error", "message": str(e)}
        
        # 构建集成状态
        if self.build_integration:
            try:
                build_status = self.build_integration.get_build_integration_status()
                status["build_integration"] = build_status
            except Exception as e:
                status["build_integration"] = {"status": "error", "message": str(e)}
        
        return status
    
    async def run_ci_workflow(self, target_languages: List[str] = None,
                             mode: str = "auto", dry_run: bool = False) -> Dict[str, Any]:
        """运行完整的CI翻译工作流"""
        print("🚀 SuperClaude CI翻译工具")
        print("=" * 50)
        
        workflow_result = {
            "ci_info": self.ci_environment,
            "steps": {},
            "overall_status": "success"
        }
        
        try:
            # 步骤1: 提取内容
            print("\n📖 步骤1: 提取内容")
            extract_result = self.extract_and_analyze_content()
            workflow_result["steps"]["extract"] = extract_result
            
            if extract_result["status"] != "success":
                workflow_result["overall_status"] = "error"
                return workflow_result
            
            # 步骤2: 检测变更
            print("\n🔍 步骤2: 检测变更")
            changes_result = await self.detect_changes()
            workflow_result["steps"]["detect_changes"] = changes_result
            
            if changes_result["status"] != "success":
                workflow_result["overall_status"] = "error"
                return workflow_result
            
            # 步骤3: 运行翻译（如果有变更或强制模式）
            if changes_result["changes_detected"] > 0 or mode == "force":
                print("\n🚀 步骤3: 运行增量翻译")
                translation_result = await self.run_incremental_translation(
                    target_languages, dry_run
                )
                workflow_result["steps"]["translation"] = translation_result
                
                if translation_result["status"] not in ["success", "skipped"]:
                    workflow_result["overall_status"] = "error"
                    return workflow_result
            else:
                print("\n⚪ 步骤3: 跳过翻译（无变更）")
                workflow_result["steps"]["translation"] = {
                    "status": "skipped",
                    "message": "未检测到变更"
                }
            
            # 步骤4: 验证翻译
            if not dry_run:
                print("\n✅ 步骤4: 验证翻译")
                validation_result = self.validate_translations()
                workflow_result["steps"]["validation"] = validation_result
                
                if validation_result["status"] == "error":
                    workflow_result["overall_status"] = "warning"
            
            print(f"\n✅ CI工作流完成: {workflow_result['overall_status']}")
            return workflow_result
            
        except Exception as e:
            workflow_result["overall_status"] = "error"
            workflow_result["error"] = str(e)
            print(f"\n❌ CI工作流失败: {e}")
            return workflow_result


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="SuperClaude CI翻译工具")
    parser.add_argument("action", choices=[
        "status", "extract", "detect", "translate", "validate", "workflow"
    ], help="操作类型")
    
    parser.add_argument("--project-root", default=".",
                       help="项目根目录")
    parser.add_argument("--languages", default="zh_CN,ja_JP,ko_KR",
                       help="目标语言（逗号分隔）")
    parser.add_argument("--mode", choices=["auto", "force"], default="auto",
                       help="翻译模式")
    parser.add_argument("--dry-run", action="store_true",
                       help="Dry run模式（只检测，不翻译）")
    parser.add_argument("--output-format", choices=["json", "text"], default="json",
                       help="输出格式")
    
    args = parser.parse_args()
    
    # 解析目标语言
    target_languages = [lang.strip() for lang in args.languages.split(",")]
    
    # 创建CI工具
    ci_tool = CITranslationTool(args.project_root)
    
    # 执行操作
    result = None
    
    if args.action == "status":
        result = ci_tool.get_comprehensive_status()
    
    elif args.action == "extract":
        result = ci_tool.extract_and_analyze_content()
    
    elif args.action == "detect":
        result = await ci_tool.detect_changes()
    
    elif args.action == "translate":
        result = await ci_tool.run_incremental_translation(target_languages, args.dry_run)
    
    elif args.action == "validate":
        result = ci_tool.validate_translations()
    
    elif args.action == "workflow":
        result = await ci_tool.run_ci_workflow(target_languages, args.mode, args.dry_run)
    
    # 输出结果
    if args.output_format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 文本格式输出
        if result.get("status"):
            print(f"状态: {result['status']}")
            if result.get("message"):
                print(f"消息: {result['message']}")
        else:
            print("详细信息:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 返回适当的退出码
    if result and result.get("status") == "error":
        return 1
    elif result and result.get("overall_status") == "error":
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))