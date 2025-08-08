#!/usr/bin/env python3
"""
SuperClaude增量翻译管理器 / SuperClaude Incremental Translation Manager
智能检测内容变更，只翻译变更部分，大幅降低翻译成本 / Intelligently detects content changes, translates only changed parts, significantly reducing translation costs
"""

import os
import json
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from .extractor import SuperClaudeContentExtractor
from .cache import TranslationCache
from .translation_engine import TranslationEngineManager, create_translation_manager


@dataclass
class ContentChange:
    """内容变更记录 / Content change record"""
    key: str                    # 内容键
    content_type: str          # 内容类型 (commands, personas, ui, etc.)
    old_text: Optional[str]    # 原文本
    new_text: str              # 新文本
    change_type: str           # 变更类型: added, modified, deleted
    file_source: Optional[str] # 源文件
    hash_old: Optional[str]    # 旧内容哈希
    hash_new: str              # 新内容哈希


@dataclass
class TranslationMemory:
    """翻译记忆库条目"""
    source_text: str
    target_text: str
    source_lang: str
    target_lang: str
    content_type: str
    confidence: float
    last_used: str
    usage_count: int
    translation_engine: str


class IncrementalTranslationManager:
    """增量翻译管理器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / ".superclaude" / "incremental"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 状态文件
        self.content_snapshot_file = self.data_dir / "content_snapshot.json"
        self.translation_memory_file = self.data_dir / "translation_memory.json"
        self.incremental_log_file = self.data_dir / "incremental_log.jsonl"
        
        # 组件初始化
        self.extractor = SuperClaudeContentExtractor(str(self.project_root))
        self.cache = TranslationCache()
        self.translation_manager = None
        
        # 翻译记忆库
        self.translation_memory = self._load_translation_memory()
        
        # 支持的语言
        self.target_languages = [
            "zh_CN", "zh_TW", "ja_JP", "ko_KR", "ru_RU",
            "es_ES", "de_DE", "fr_FR", "ar_SA"
        ]
    
    def _initialize_translation_manager(self):
        """初始化翻译管理器（延迟初始化）"""
        if self.translation_manager is None:
            try:
                self.translation_manager = create_translation_manager()
            except Exception as e:
                print(f"⚠️ 翻译管理器初始化失败 / Translation manager initialization failed: {e}")
                self.translation_manager = None
    
    def _calculate_content_hash(self, content: Dict[str, Dict[str, str]]) -> str:
        """计算内容哈希"""
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(content_str.encode('utf-8')).hexdigest()
    
    def _load_content_snapshot(self) -> Dict[str, Any]:
        """加载内容快照"""
        if not self.content_snapshot_file.exists():
            return {}
        
        try:
            with open(self.content_snapshot_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载内容快照失败 / Failed to load content snapshot: {e}")
            return {}
    
    def _save_content_snapshot(self, snapshot: Dict[str, Any]):
        """保存内容快照"""
        try:
            with open(self.content_snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存内容快照失败 / Failed to save content snapshot: {e}")
    
    def _load_translation_memory(self) -> Dict[str, TranslationMemory]:
        """加载翻译记忆库"""
        if not self.translation_memory_file.exists():
            return {}
        
        try:
            with open(self.translation_memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            memory = {}
            for key, entry_data in data.items():
                memory[key] = TranslationMemory(**entry_data)
            
            return memory
        except Exception as e:
            print(f"⚠️ 加载翻译记忆库失败 / Failed to load translation memory: {e}")
            return {}
    
    def _save_translation_memory(self):
        """保存翻译记忆库"""
        try:
            data = {}
            for key, memory_entry in self.translation_memory.items():
                data[key] = asdict(memory_entry)
            
            with open(self.translation_memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存翻译记忆库失败 / Failed to save translation memory: {e}")
    
    def _generate_memory_key(self, source_text: str, target_lang: str, content_type: str) -> str:
        """生成翻译记忆库键"""
        content = f"{source_text}|{target_lang}|{content_type}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _add_to_translation_memory(self, source_text: str, target_text: str, 
                                  target_lang: str, content_type: str,
                                  confidence: float = 1.0, engine: str = "unknown"):
        """添加到翻译记忆库"""
        memory_key = self._generate_memory_key(source_text, target_lang, content_type)
        
        if memory_key in self.translation_memory:
            # 更新现有条目
            memory_entry = self.translation_memory[memory_key]
            memory_entry.target_text = target_text
            memory_entry.confidence = confidence
            memory_entry.last_used = datetime.now().isoformat()
            memory_entry.usage_count += 1
            memory_entry.translation_engine = engine
        else:
            # 创建新条目
            self.translation_memory[memory_key] = TranslationMemory(
                source_text=source_text,
                target_text=target_text,
                source_lang="en",
                target_lang=target_lang,
                content_type=content_type,
                confidence=confidence,
                last_used=datetime.now().isoformat(),
                usage_count=1,
                translation_engine=engine
            )
    
    def _get_from_translation_memory(self, source_text: str, target_lang: str, 
                                   content_type: str) -> Optional[str]:
        """从翻译记忆库获取翻译"""
        memory_key = self._generate_memory_key(source_text, target_lang, content_type)
        
        if memory_key in self.translation_memory:
            memory_entry = self.translation_memory[memory_key]
            memory_entry.last_used = datetime.now().isoformat()
            memory_entry.usage_count += 1
            return memory_entry.target_text
        
        return None
    
    def detect_content_changes(self) -> List[ContentChange]:
        """检测内容变更"""
        print("🔍 检测内容变更... / Detecting content changes...")
        
        # 提取当前内容
        current_content = self.extractor.extract_all_content()
        current_hash = self._calculate_content_hash(current_content)
        
        # 加载历史快照
        old_snapshot = self._load_content_snapshot()
        old_content = old_snapshot.get("content", {})
        old_hash = old_snapshot.get("content_hash", "")
        
        changes = []
        
        # 如果整体哈希相同，没有变更
        if current_hash == old_hash:
            print("✅ 未检测到内容变更 / No content changes detected")
            return changes
        
        print(f"📊 检测到内容变更 / Content changes detected (哈希 / hash: {old_hash[:8]} -> {current_hash[:8]})")
        
        # 详细对比每个内容类型和键
        all_content_types = set(current_content.keys()) | set(old_content.keys())
        
        for content_type in all_content_types:
            current_section = current_content.get(content_type, {})
            old_section = old_content.get(content_type, {})
            
            all_keys = set(current_section.keys()) | set(old_section.keys())
            
            for key in all_keys:
                current_text = current_section.get(key)
                old_text = old_section.get(key)
                
                if current_text != old_text:
                    if current_text is None:
                        # 删除的内容
                        change = ContentChange(
                            key=key,
                            content_type=content_type,
                            old_text=old_text,
                            new_text="",
                            change_type="deleted",
                            file_source=None,
                            hash_old=hashlib.md5(old_text.encode()).hexdigest() if old_text else None,
                            hash_new=""
                        )
                    elif old_text is None:
                        # 新增的内容
                        change = ContentChange(
                            key=key,
                            content_type=content_type,
                            old_text=None,
                            new_text=current_text,
                            change_type="added",
                            file_source=None,
                            hash_old=None,
                            hash_new=hashlib.md5(current_text.encode()).hexdigest()
                        )
                    else:
                        # 修改的内容
                        change = ContentChange(
                            key=key,
                            content_type=content_type,
                            old_text=old_text,
                            new_text=current_text,
                            change_type="modified",
                            file_source=None,
                            hash_old=hashlib.md5(old_text.encode()).hexdigest(),
                            hash_new=hashlib.md5(current_text.encode()).hexdigest()
                        )
                    
                    changes.append(change)
        
        print(f"📋 检测到 {len(changes)} 项内容变更 / Detected {len(changes)} content changes")
        
        # 按变更类型分组显示
        change_summary = {}
        for change in changes:
            change_type = change.change_type
            change_summary[change_type] = change_summary.get(change_type, 0) + 1
        
        for change_type, count in change_summary.items():
            print(f"   {change_type}: {count} 项")
        
        # 保存新的快照
        new_snapshot = {
            "content": current_content,
            "content_hash": current_hash,
            "timestamp": datetime.now().isoformat(),
            "changes_detected": len(changes)
        }
        self._save_content_snapshot(new_snapshot)
        
        return changes
    
    async def translate_changes(self, changes: List[ContentChange], 
                              target_languages: List[str] = None) -> Dict[str, Any]:
        """翻译变更内容"""
        if not changes:
            return {"status": "success", "message": "无变更需要翻译", "translations": 0}
        
        if target_languages is None:
            target_languages = self.target_languages
        
        print(f"🚀 开始增量翻译 / Starting incremental translation: {len(changes)} 项变更 / changes, {len(target_languages)} 种语言 / languages")
        
        # 初始化翻译管理器
        self._initialize_translation_manager()
        if self.translation_manager is None:
            return {"status": "error", "message": "翻译管理器初始化失败"}
        
        translation_results = {}
        total_translations = 0
        cache_hits = 0
        
        for target_lang in target_languages:
            print(f"\n🌍 翻译到 / Translating to {target_lang}...")
            translation_results[target_lang] = {}
            
            for change in changes:
                if change.change_type == "deleted":
                    continue  # 跳过删除的内容
                
                source_text = change.new_text
                content_type = change.content_type
                key = change.key
                
                # 首先尝试翻译记忆库
                cached_translation = self._get_from_translation_memory(
                    source_text, target_lang, content_type
                )
                
                if cached_translation:
                    translation_results[target_lang][key] = cached_translation
                    cache_hits += 1
                    continue
                
                # 然后尝试翻译缓存
                cached_translation = self.cache.get_translation(
                    source_text, target_lang, content_type
                )
                
                if cached_translation:
                    translation_results[target_lang][key] = cached_translation
                    # 添加到翻译记忆库
                    self._add_to_translation_memory(
                        source_text, cached_translation, target_lang, 
                        content_type, confidence=0.9, engine="cache"
                    )
                    cache_hits += 1
                    continue
                
                # 需要新翻译
                try:
                    print(f"   🔄 翻译 / Translating {content_type}.{key}...")
                    
                    # 获取翻译引擎
                    engine = self.translation_manager.get_engine()
                    context = engine.contexts.get(content_type, engine.contexts["commands"])
                    
                    # 执行翻译
                    result = await self.translation_manager.translate_with_context(
                        source_text, target_lang, context
                    )
                    
                    translation_results[target_lang][key] = result.target
                    
                    # 存储到缓存和记忆库
                    self.cache.store_translation(
                        source_text, result.target, target_lang, content_type,
                        confidence=result.confidence, cost=result.cost_estimate
                    )
                    
                    self._add_to_translation_memory(
                        source_text, result.target, target_lang, content_type,
                        confidence=result.confidence, engine="live"
                    )
                    
                    total_translations += 1
                    
                    # 添加延迟避免API限制
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f"⚠️ 翻译失败 / Translation failed {content_type}.{key}: {e}")
                    # 使用原文作为fallback
                    translation_results[target_lang][key] = source_text
        
        # 保存翻译记忆库
        self._save_translation_memory()
        
        # 记录增量翻译日志
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "changes_count": len(changes),
            "target_languages": target_languages,
            "total_translations": total_translations,
            "cache_hits": cache_hits,
            "cache_hit_rate": cache_hits / (total_translations + cache_hits) if (total_translations + cache_hits) > 0 else 0
        }
        
        try:
            with open(self.incremental_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠️ 记录增量翻译日志失败 / Failed to log incremental translation: {e}")
        
        print(f"\n✅ 增量翻译完成 / Incremental translation completed!")
        print(f"   新翻译 / New translations: {total_translations} 项 / items")
        print(f"   缓存命中 / Cache hits: {cache_hits} 项 / items")
        print(f"   缓存命中率 / Cache hit rate: {log_entry['cache_hit_rate']:.1%}")
        
        return {
            "status": "success",
            "message": f"增量翻译完成: {total_translations} 项新翻译, {cache_hits} 项缓存命中",
            "translations": total_translations,
            "cache_hits": cache_hits,
            "cache_hit_rate": log_entry['cache_hit_rate'],
            "results": translation_results
        }
    
    def get_incremental_statistics(self) -> Dict[str, Any]:
        """获取增量翻译统计信息"""
        stats = {
            "translation_memory_size": len(self.translation_memory),
            "cache_stats": self.cache.get_cache_statistics(),
            "last_snapshot": None,
            "total_incremental_runs": 0,
            "total_translations": 0,
            "average_cache_hit_rate": 0.0
        }
        
        # 读取快照信息
        if self.content_snapshot_file.exists():
            try:
                with open(self.content_snapshot_file, 'r', encoding='utf-8') as f:
                    snapshot = json.load(f)
                    stats["last_snapshot"] = {
                        "timestamp": snapshot.get("timestamp"),
                        "content_hash": snapshot.get("content_hash", "")[:8],
                        "changes_detected": snapshot.get("changes_detected", 0)
                    }
            except Exception:
                pass
        
        # 读取增量翻译日志统计
        if self.incremental_log_file.exists():
            try:
                total_runs = 0
                total_translations = 0
                total_cache_hits = 0
                
                with open(self.incremental_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            log_entry = json.loads(line)
                            total_runs += 1
                            total_translations += log_entry.get("total_translations", 0)
                            total_cache_hits += log_entry.get("cache_hits", 0)
                
                stats["total_incremental_runs"] = total_runs
                stats["total_translations"] = total_translations
                
                if total_translations + total_cache_hits > 0:
                    stats["average_cache_hit_rate"] = total_cache_hits / (total_translations + total_cache_hits)
                    
            except Exception:
                pass
        
        return stats
    
    def reset_incremental_data(self):
        """重置增量翻译数据（用于测试或重新开始）"""
        print("🗑️ 重置增量翻译数据...")
        
        files_to_remove = [
            self.content_snapshot_file,
            self.translation_memory_file,
            self.incremental_log_file
        ]
        
        for file_path in files_to_remove:
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"✅ 已删除: {file_path}")
                except Exception as e:
                    print(f"⚠️ 删除失败 {file_path}: {e}")
        
        # 重置内存中的数据
        self.translation_memory = {}
        
        print("✅ 增量翻译数据重置完成")


async def main():
    """测试增量翻译管理器"""
    print("🧪 测试增量翻译管理器")
    print("=" * 50)
    
    manager = IncrementalTranslationManager()
    
    # 显示统计信息
    stats = manager.get_incremental_statistics()
    print("📊 当前状态:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    # 检测变更
    changes = manager.detect_content_changes()
    
    if changes:
        print(f"\n📋 检测到 {len(changes)} 项变更:")
        for i, change in enumerate(changes[:5], 1):  # 只显示前5项
            print(f"   {i}. {change.change_type}: {change.content_type}.{change.key}")
            if change.new_text and len(change.new_text) < 100:
                print(f"      -> {change.new_text}")
        
        if len(changes) > 5:
            print(f"   ... 还有 {len(changes) - 5} 项变更")
        
        # 询问是否执行翻译（在实际使用中会自动执行）
        print(f"\n是否执行增量翻译？(仅测试模式)")
        # 在这里可以添加用户确认逻辑
        
    else:
        print("✅ 无变更需要翻译")


if __name__ == "__main__":
    asyncio.run(main())