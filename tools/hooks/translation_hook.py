#!/usr/bin/env python3
"""
SuperClaude Git Hooks翻译集成
自动检测可翻译内容变更并触发增量翻译
"""

import os
import sys
import json
import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import Set, List, Dict, Optional

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from i18n.extractor import SuperClaudeContentExtractor
    from i18n.incremental import IncrementalTranslationManager
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    print("Git hook将在基础模式下运行")


class TranslationHook:
    """Git hooks翻译集成管理器"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            project_root = PROJECT_ROOT
        
        self.project_root = Path(project_root)
        self.hooks_data_dir = self.project_root / ".superclaude" / "hooks"
        self.hooks_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 需要监控的文件模式
        self.monitored_patterns = [
            "SuperClaude/Commands/*.md",
            "SuperClaude/Core/PERSONAS.md", 
            "SuperClaude/Core/COMMANDS.md",
            "setup/utils/ui.py",
            "**/*.py",  # Python文件中的UI文本
            "README*.md",
            "docs/**/*.md"
        ]
        
        # 内容变更状态文件
        self.content_state_file = self.hooks_data_dir / "content_state.json"
    
    def _get_git_staged_files(self) -> Set[str]:
        """获取Git暂存区的文件列表"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            if result.returncode == 0:
                files = set(line.strip() for line in result.stdout.splitlines() if line.strip())
                return files
            else:
                print(f"⚠️ Git命令执行失败: {result.stderr}")
                return set()
                
        except Exception as e:
            print(f"⚠️ 获取Git暂存文件失败: {e}")
            return set()
    
    def _is_translation_relevant(self, file_path: str) -> bool:
        """检查文件是否与翻译相关"""
        file_path = Path(file_path)
        
        # 检查文件扩展名
        relevant_extensions = {'.md', '.py', '.txt', '.json'}
        if file_path.suffix not in relevant_extensions:
            return False
            
        # 检查关键目录
        path_str = str(file_path)
        relevant_patterns = [
            "SuperClaude/Commands",
            "SuperClaude/Core",
            "setup/utils",
            "docs/",
            "README"
        ]
        
        return any(pattern in path_str for pattern in relevant_patterns)
    
    def _calculate_file_hash(self, file_path: Path) -> Optional[str]:
        """计算文件内容哈希"""
        try:
            if not file_path.exists():
                return None
                
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            print(f"⚠️ 计算文件哈希失败 {file_path}: {e}")
            return None
    
    def _load_content_state(self) -> Dict[str, str]:
        """加载内容状态"""
        if not self.content_state_file.exists():
            return {}
            
        try:
            with open(self.content_state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载内容状态失败: {e}")
            return {}
    
    def _save_content_state(self, state: Dict[str, str]):
        """保存内容状态"""
        try:
            with open(self.content_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存内容状态失败: {e}")
    
    def detect_content_changes(self) -> Dict[str, List[str]]:
        """检测内容变更"""
        staged_files = self._get_git_staged_files()
        translation_files = {f for f in staged_files if self._is_translation_relevant(f)}
        
        if not translation_files:
            return {
                "changed_files": [], 
                "total_changed": 0,
                "total_staged": len(staged_files),
                "summary": "无翻译相关变更"
            }
        
        # 加载历史状态
        old_state = self._load_content_state()
        new_state = {}
        changed_files = []
        
        # 检查每个相关文件的变更
        for file_path in translation_files:
            full_path = self.project_root / file_path
            new_hash = self._calculate_file_hash(full_path)
            old_hash = old_state.get(file_path)
            
            new_state[file_path] = new_hash or ""
            
            if new_hash != old_hash:
                changed_files.append(file_path)
                print(f"🔍 检测到变更: {file_path}")
        
        # 保存新状态
        if changed_files:
            self._save_content_state(new_state)
        
        return {
            "changed_files": changed_files,
            "total_changed": len(changed_files),
            "total_staged": len(staged_files),
            "summary": f"检测到 {len(changed_files)} 个翻译相关文件变更"
        }
    
    def should_trigger_translation(self, changes: Dict[str, List[str]]) -> bool:
        """判断是否应该触发翻译"""
        # 检查跳过标志
        skip_env = os.getenv("SKIP_TRANSLATION", "false").lower()
        if skip_env in ("true", "1", "yes"):
            print("🔄 跳过翻译 (SKIP_TRANSLATION环境变量)")
            return False
        
        # 检查Git提交消息中的跳过标志
        try:
            # 尝试获取提交消息模板或缓存的消息
            commit_msg_file = self.project_root / ".git" / "COMMIT_EDITMSG"
            if commit_msg_file.exists():
                commit_msg = commit_msg_file.read_text()
                if "[skip-translation]" in commit_msg.lower():
                    print("🔄 跳过翻译 ([skip-translation]标志)")
                    return False
        except Exception:
            pass
        
        # 如果有翻译相关变更，触发翻译
        return changes["total_changed"] > 0
    
    def run_incremental_translation(self, changed_files: List[str]) -> bool:
        """运行增量翻译"""
        try:
            print(f"🚀 启动增量翻译处理 {len(changed_files)} 个文件...")
            
            # 这里会在后续实现IncrementalTranslationManager
            print("⚠️ 增量翻译管理器尚未完全实现，使用快速模式")
            
            # 简单的内容提取和变更检测
            extractor = SuperClaudeContentExtractor(str(self.project_root))
            content = extractor.extract_all_content()
            
            total_items = sum(len(section) for section in content.values())
            print(f"📊 提取到 {total_items} 项内容")
            
            # 在实际实现中，这里会调用增量翻译
            # incremental_manager = IncrementalTranslationManager()
            # result = incremental_manager.translate_changes(changed_files)
            
            print("✅ 增量翻译检查完成（开发模式）")
            return True
            
        except Exception as e:
            print(f"❌ 增量翻译失败: {e}")
            return False
    
    def run_pre_commit_hook(self) -> int:
        """运行pre-commit钩子"""
        print("🔗 SuperClaude Translation Hook - Pre-commit")
        print("=" * 50)
        
        try:
            # 1. 检测内容变更
            changes = self.detect_content_changes()
            print(f"📋 变更摘要: {changes['summary']}")
            
            # 2. 判断是否需要翻译
            if not self.should_trigger_translation(changes):
                print("✅ 无需翻译处理，继续提交")
                return 0
            
            # 3. 运行增量翻译
            success = self.run_incremental_translation(changes['changed_files'])
            
            if success:
                print("✅ 翻译处理完成，继续提交")
                return 0
            else:
                print("❌ 翻译处理失败")
                print("💡 使用 'git commit --no-verify' 跳过翻译检查")
                print("💡 或设置环境变量: SKIP_TRANSLATION=true")
                return 1
                
        except Exception as e:
            print(f"❌ Git hook执行失败: {e}")
            print("💡 使用 'git commit --no-verify' 跳过hook")
            return 1


def main():
    """主入口函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # 测试模式
        hook = TranslationHook()
        changes = hook.detect_content_changes()
        print(json.dumps(changes, ensure_ascii=False, indent=2))
        return 0
    
    # 正常的pre-commit hook执行
    hook = TranslationHook()
    return hook.run_pre_commit_hook()


if __name__ == "__main__":
    sys.exit(main())