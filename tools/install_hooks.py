#!/usr/bin/env python3
"""
SuperClaude Git Hooks安装工具 / SuperClaude Git Hooks Installation Tool
自动安装和配置Git hooks用于翻译自动化 / Automatically install and configure Git hooks for translation automation
"""

import os
import sys
import stat
import shutil
from pathlib import Path


class GitHooksInstaller:
    """Git Hooks安装器 / Git Hooks Installer"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent
        
        self.project_root = Path(project_root)
        self.git_hooks_dir = self.project_root / ".git" / "hooks"
        self.template_dir = self.project_root / "tools" / "hooks"
        
        # 确保目录存在
        self.git_hooks_dir.mkdir(parents=True, exist_ok=True)
    
    def _check_git_repository(self) -> bool:
        """检查是否在Git仓库中 / Check if in Git repository"""
        git_dir = self.project_root / ".git"
        return git_dir.exists()
    
    def _backup_existing_hook(self, hook_name: str) -> bool:
        """备份现有的Git hook"""
        hook_file = self.git_hooks_dir / hook_name
        
        if hook_file.exists():
            backup_file = self.git_hooks_dir / f"{hook_name}.backup"
            try:
                shutil.copy2(hook_file, backup_file)
                print(f"✅ 已备份现有hook: {hook_name} -> {hook_name}.backup")
                return True
            except Exception as e:
                print(f"⚠️ 备份hook失败: {e}")
                return False
        return True
    
    def _create_pre_commit_hook(self) -> bool:
        """创建pre-commit hook"""
        hook_content = f'''#!/bin/bash
# SuperClaude Translation Hook
# 自动检测翻译内容变更并触发增量翻译

# 设置Python路径和项目根目录
export PYTHONPATH="{self.project_root}:$PYTHONPATH"
cd "{self.project_root}"

# 运行翻译hook
python3 tools/hooks/translation_hook.py

# 获取退出码
exit_code=$?

# 如果翻译处理失败，给出提示
if [ $exit_code -ne 0 ]; then
    echo ""
    echo "💡 翻译处理提示："
    echo "   • 使用 'git commit --no-verify' 跳过翻译检查"
    echo "   • 设置环境变量跳过: export SKIP_TRANSLATION=true"
    echo "   • 在提交消息中添加 [skip-translation] 标志"
    echo ""
fi

exit $exit_code
'''
        
        hook_file = self.git_hooks_dir / "pre-commit"
        
        try:
            with open(hook_file, 'w', encoding='utf-8') as f:
                f.write(hook_content)
            
            # 设置可执行权限
            hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
            
            print(f"✅ 创建pre-commit hook: {hook_file}")
            return True
            
        except Exception as e:
            print(f"❌ 创建pre-commit hook失败: {e}")
            return False
    
    def _create_post_commit_hook(self) -> bool:
        """创建post-commit hook（用于统计和报告）"""
        hook_content = f'''#!/bin/bash
# SuperClaude Post-commit Hook
# 提交后的翻译统计和报告

# 设置Python路径
export PYTHONPATH="{self.project_root}:$PYTHONPATH"
cd "{self.project_root}"

# 运行翻译统计（静默模式）
if command -v python3 >/dev/null 2>&1; then
    python3 -c "
try:
    from i18n.cache import TranslationCache
    cache = TranslationCache()
    stats = cache.get_cache_statistics()
    if stats['total_entries'] > 0:
        print(f'📊 翻译缓存: {{stats[\"total_entries\"]}}项翻译, 节省成本¥{{stats[\"total_saved_cost\"]}}')
except ImportError:
    pass
except Exception:
    pass
    " 2>/dev/null
fi
'''
        
        hook_file = self.git_hooks_dir / "post-commit"
        
        try:
            with open(hook_file, 'w', encoding='utf-8') as f:
                f.write(hook_content)
            
            # 设置可执行权限
            hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
            
            print(f"✅ 创建post-commit hook: {hook_file}")
            return True
            
        except Exception as e:
            print(f"⚠️ 创建post-commit hook失败: {e}")
            return False
    
    def install_hooks(self, hooks: list = None) -> bool:
        """安装Git hooks"""
        if hooks is None:
            hooks = ["pre-commit", "post-commit"]
        
        print("🚀 SuperClaude Git Hooks安装器")
        print("=" * 40)
        
        # 检查Git仓库
        if not self._check_git_repository():
            print("❌ 错误: 不在Git仓库中")
            return False
        
        print(f"📁 项目根目录: {self.project_root}")
        print(f"📁 Git hooks目录: {self.git_hooks_dir}")
        
        success = True
        
        # 安装每个hook
        for hook_name in hooks:
            print(f"\n🔗 安装 {hook_name} hook...")
            
            # 备份现有hook
            if not self._backup_existing_hook(hook_name):
                print(f"⚠️ 备份{hook_name}失败，继续安装")
            
            # 创建新hook
            if hook_name == "pre-commit":
                hook_success = self._create_pre_commit_hook()
            elif hook_name == "post-commit":
                hook_success = self._create_post_commit_hook()
            else:
                print(f"⚠️ 未知的hook类型: {hook_name}")
                hook_success = False
            
            if not hook_success:
                success = False
        
        if success:
            print("\n✅ Git hooks安装完成!")
            print("\n📋 使用说明:")
            print("   • Git提交时会自动检测翻译内容变更")
            print("   • 检测到变更时会自动运行增量翻译")
            print("   • 使用 'git commit --no-verify' 跳过翻译检查")
            print("   • 设置 SKIP_TRANSLATION=true 环境变量跳过翻译")
            print("   • 在提交消息中添加 [skip-translation] 跳过翻译")
        else:
            print("\n❌ Git hooks安装失败")
        
        return success
    
    def uninstall_hooks(self) -> bool:
        """卸载Git hooks"""
        print("🗑️ 卸载SuperClaude Git Hooks")
        print("=" * 40)
        
        hooks_to_remove = ["pre-commit", "post-commit"]
        success = True
        
        for hook_name in hooks_to_remove:
            hook_file = self.git_hooks_dir / hook_name
            backup_file = self.git_hooks_dir / f"{hook_name}.backup"
            
            if hook_file.exists():
                try:
                    # 检查是否是我们创建的hook
                    content = hook_file.read_text()
                    if "SuperClaude Translation Hook" in content:
                        hook_file.unlink()
                        print(f"✅ 已删除 {hook_name} hook")
                        
                        # 恢复备份
                        if backup_file.exists():
                            shutil.copy2(backup_file, hook_file)
                            backup_file.unlink()
                            print(f"✅ 已恢复备份的 {hook_name} hook")
                    else:
                        print(f"⚠️ {hook_name} hook非SuperClaude创建，跳过删除")
                        
                except Exception as e:
                    print(f"❌ 删除 {hook_name} hook失败: {e}")
                    success = False
            else:
                print(f"ℹ️ {hook_name} hook不存在")
        
        if success:
            print("\n✅ Git hooks卸载完成!")
        else:
            print("\n⚠️ Git hooks卸载部分失败")
        
        return success
    
    def test_hooks(self) -> bool:
        """测试Git hooks"""
        print("🧪 测试SuperClaude Git Hooks")
        print("=" * 40)
        
        # 测试translation_hook.py
        hook_script = self.template_dir / "translation_hook.py"
        
        if not hook_script.exists():
            print(f"❌ Hook脚本不存在: {hook_script}")
            return False
        
        try:
            import subprocess
            
            # 测试hook脚本
            result = subprocess.run(
                [sys.executable, str(hook_script), "--test"],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            print(f"📋 Hook脚本测试结果:")
            print(f"   返回码: {result.returncode}")
            if result.stdout:
                print(f"   输出: {result.stdout}")
            if result.stderr:
                print(f"   错误: {result.stderr}")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ 测试hook脚本失败: {e}")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SuperClaude Git Hooks管理工具")
    parser.add_argument("action", choices=["install", "uninstall", "test"],
                       help="操作: install(安装), uninstall(卸载), test(测试)")
    parser.add_argument("--project-root", default=".",
                       help="项目根目录 (默认: 当前目录)")
    
    args = parser.parse_args()
    
    installer = GitHooksInstaller(args.project_root)
    
    if args.action == "install":
        success = installer.install_hooks()
    elif args.action == "uninstall":
        success = installer.uninstall_hooks()
    elif args.action == "test":
        success = installer.test_hooks()
    else:
        print(f"❌ 未知操作: {args.action}")
        success = False
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())