#!/usr/bin/env python3
"""
翻译缓存系统 / Translation Cache System
提供翻译结果的缓存和管理功能，减少重复API调用 / Provides caching and management functionality for translation results, reducing duplicate API calls
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict


@dataclass
class CacheEntry:
    """缓存条目 / Cache entry"""
    source_text: str
    target_text: str
    source_lang: str
    target_lang: str
    content_type: str
    timestamp: float
    confidence: float
    cost: float = 0.0


class TranslationCache:
    """翻译缓存管理器 / Translation cache manager"""
    
    def __init__(self, cache_dir: str = None, max_age_days: int = 30):
        """
        初始化翻译缓存
        
        Args:
            cache_dir: 缓存目录路径
            max_age_days: 缓存最大保存天数
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".superclaude" / "translation_cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_age_seconds = max_age_days * 24 * 3600
        self.cache_file = self.cache_dir / "translations.json"
        self.cache_data = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Dict]:
        """加载缓存数据"""
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 清理过期缓存
            current_time = time.time()
            cleaned_data = {}
            
            for key, entry_data in data.items():
                timestamp = entry_data.get('timestamp', 0)
                if current_time - timestamp < self.max_age_seconds:
                    cleaned_data[key] = entry_data
            
            # 如果有清理，保存清理后的数据
            if len(cleaned_data) != len(data):
                self._save_cache(cleaned_data)
                
            return cleaned_data
            
        except Exception as e:
            print(f"Warning: Failed to load translation cache: {e}")
            return {}
    
    def _save_cache(self, data: Dict[str, Dict] = None):
        """保存缓存数据"""
        if data is None:
            data = self.cache_data
            
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save translation cache: {e}")
    
    def _generate_cache_key(self, 
                           source_text: str, 
                           target_lang: str,
                           content_type: str = "default") -> str:
        """生成缓存键"""
        # 使用文本内容+目标语言+内容类型生成唯一键
        content = f"{source_text}|{target_lang}|{content_type}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get_translation(self, 
                       source_text: str, 
                       target_lang: str,
                       content_type: str = "default") -> Optional[str]:
        """获取缓存的翻译"""
        cache_key = self._generate_cache_key(source_text, target_lang, content_type)
        
        if cache_key in self.cache_data:
            entry_data = self.cache_data[cache_key]
            
            # 检查是否过期
            current_time = time.time()
            if current_time - entry_data['timestamp'] < self.max_age_seconds:
                return entry_data['target_text']
            else:
                # 删除过期条目
                del self.cache_data[cache_key]
                self._save_cache()
        
        return None
    
    def store_translation(self,
                         source_text: str,
                         target_text: str, 
                         target_lang: str,
                         content_type: str = "default",
                         confidence: float = 1.0,
                         cost: float = 0.0):
        """存储翻译结果"""
        cache_key = self._generate_cache_key(source_text, target_lang, content_type)
        
        entry = CacheEntry(
            source_text=source_text,
            target_text=target_text,
            source_lang="auto",  # 通常自动检测
            target_lang=target_lang,
            content_type=content_type,
            timestamp=time.time(),
            confidence=confidence,
            cost=cost
        )
        
        self.cache_data[cache_key] = asdict(entry)
        self._save_cache()
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_entries = len(self.cache_data)
        total_cost = sum(entry.get('cost', 0) for entry in self.cache_data.values())
        
        # 按语言统计
        lang_stats = {}
        for entry in self.cache_data.values():
            lang = entry.get('target_lang', 'unknown')
            lang_stats[lang] = lang_stats.get(lang, 0) + 1
        
        # 按内容类型统计
        type_stats = {}
        for entry in self.cache_data.values():
            content_type = entry.get('content_type', 'default')
            type_stats[content_type] = type_stats.get(content_type, 0) + 1
        
        return {
            "total_entries": total_entries,
            "total_saved_cost": round(total_cost, 4),
            "cache_file_size": self.cache_file.stat().st_size if self.cache_file.exists() else 0,
            "by_language": lang_stats,
            "by_content_type": type_stats,
            "cache_directory": str(self.cache_dir)
        }
    
    def clear_cache(self, target_lang: str = None, content_type: str = None):
        """清理缓存"""
        if target_lang is None and content_type is None:
            # 清理全部缓存
            self.cache_data = {}
        else:
            # 选择性清理
            keys_to_remove = []
            for key, entry in self.cache_data.items():
                should_remove = True
                
                if target_lang is not None and entry.get('target_lang') != target_lang:
                    should_remove = False
                
                if content_type is not None and entry.get('content_type') != content_type:
                    should_remove = False
                
                if should_remove:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.cache_data[key]
        
        self._save_cache()
    
    def export_cache(self, export_file: str) -> bool:
        """导出缓存到文件"""
        try:
            export_path = Path(export_file)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Failed to export cache: {e}")
            return False
    
    def import_cache(self, import_file: str) -> bool:
        """从文件导入缓存"""
        try:
            import_path = Path(import_file)
            if not import_path.exists():
                print(f"Import file does not exist: {import_file}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # 合并导入的数据
            current_time = time.time()
            imported_count = 0
            
            for key, entry in imported_data.items():
                # 检查条目有效性
                if isinstance(entry, dict) and 'timestamp' in entry:
                    # 检查是否过期
                    if current_time - entry['timestamp'] < self.max_age_seconds:
                        self.cache_data[key] = entry
                        imported_count += 1
            
            self._save_cache()
            print(f"Imported {imported_count} cache entries")
            return True
            
        except Exception as e:
            print(f"Failed to import cache: {e}")
            return False
    
    def batch_store(self, translations: Dict[str, Dict]):
        """批量存储翻译结果"""
        for source_text, translation_data in translations.items():
            self.store_translation(
                source_text=source_text,
                target_text=translation_data.get('target_text', ''),
                target_lang=translation_data.get('target_lang', 'zh_CN'),
                content_type=translation_data.get('content_type', 'default'),
                confidence=translation_data.get('confidence', 1.0),
                cost=translation_data.get('cost', 0.0)
            )
    
    def get_similar_translations(self, source_text: str, target_lang: str, 
                                content_type: str = "default", 
                                similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """获取相似的翻译（用于翻译记忆库功能）"""
        similar = []
        
        # 简单的相似度检测（基于文本长度和关键词）
        source_words = set(source_text.lower().split())
        source_len = len(source_text)
        
        for entry_data in self.cache_data.values():
            if (entry_data.get('target_lang') == target_lang and 
                entry_data.get('content_type') == content_type):
                
                cached_source = entry_data.get('source_text', '')
                cached_words = set(cached_source.lower().split())
                cached_len = len(cached_source)
                
                # 计算简单相似度
                word_intersection = len(source_words & cached_words)
                word_union = len(source_words | cached_words)
                
                if word_union > 0:
                    word_similarity = word_intersection / word_union
                    length_similarity = min(source_len, cached_len) / max(source_len, cached_len) if max(source_len, cached_len) > 0 else 0
                    
                    overall_similarity = (word_similarity + length_similarity) / 2
                    
                    if overall_similarity >= similarity_threshold:
                        similar.append({
                            'source_text': cached_source,
                            'target_text': entry_data.get('target_text', ''),
                            'similarity': overall_similarity,
                            'confidence': entry_data.get('confidence', 1.0),
                            'timestamp': entry_data.get('timestamp', 0)
                        })
        
        # 按相似度排序
        similar.sort(key=lambda x: x['similarity'], reverse=True)
        return similar[:5]  # 返回最相似的5个
    
    def update_translation_metadata(self, source_text: str, target_lang: str,
                                   content_type: str = "default", 
                                   metadata: Dict[str, Any] = None):
        """更新翻译元数据"""
        cache_key = self._generate_cache_key(source_text, target_lang, content_type)
        
        if cache_key in self.cache_data and metadata:
            self.cache_data[cache_key].update(metadata)
            self._save_cache()
    
    def get_cache_efficiency_report(self) -> Dict[str, Any]:
        """获取缓存效率报告"""
        if not self.cache_data:
            return {"status": "empty", "message": "缓存为空"}
        
        # 统计缓存效率
        total_entries = len(self.cache_data)
        current_time = time.time()
        
        # 按使用时间分类
        recent_entries = 0  # 近30天使用
        old_entries = 0     # 超过30天未使用
        
        cost_by_lang = {}
        confidence_scores = []
        
        for entry in self.cache_data.values():
            timestamp = entry.get('timestamp', 0)
            days_old = (current_time - timestamp) / 86400
            
            if days_old <= 30:
                recent_entries += 1
            else:
                old_entries += 1
            
            # 成本统计
            target_lang = entry.get('target_lang', 'unknown')
            cost = entry.get('cost', 0.0)
            cost_by_lang[target_lang] = cost_by_lang.get(target_lang, 0) + cost
            
            # 质量统计
            confidence = entry.get('confidence', 1.0)
            confidence_scores.append(confidence)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        total_saved_cost = sum(cost_by_lang.values())
        
        return {
            "total_entries": total_entries,
            "recent_entries": recent_entries,
            "old_entries": old_entries,
            "cache_freshness": recent_entries / total_entries if total_entries > 0 else 0,
            "total_saved_cost": round(total_saved_cost, 4),
            "average_confidence": round(avg_confidence, 3),
            "cost_by_language": cost_by_lang,
            "cache_file_size_mb": round(self.cache_file.stat().st_size / (1024*1024), 2) if self.cache_file.exists() else 0
        }
    
    def optimize_cache(self, max_entries: int = 10000, min_confidence: float = 0.7):
        """优化缓存（清理低质量和过期条目）"""
        if not self.cache_data:
            return {"removed": 0, "message": "缓存为空，无需优化"}
        
        original_count = len(self.cache_data)
        current_time = time.time()
        
        # 筛选条件
        cleaned_data = {}
        removed_reasons = {"low_confidence": 0, "too_old": 0, "excess": 0}
        
        # 按质量和时间筛选
        for key, entry in self.cache_data.items():
            confidence = entry.get('confidence', 1.0)
            timestamp = entry.get('timestamp', 0)
            days_old = (current_time - timestamp) / 86400
            
            # 过滤低质量翻译
            if confidence < min_confidence:
                removed_reasons["low_confidence"] += 1
                continue
                
            # 过滤超过缓存期的条目
            if days_old > self.max_age_seconds / 86400:
                removed_reasons["too_old"] += 1
                continue
            
            cleaned_data[key] = entry
        
        # 如果仍然超过最大条目数，保留最新的
        if len(cleaned_data) > max_entries:
            # 按时间排序，保留最新的
            sorted_entries = sorted(cleaned_data.items(), 
                                  key=lambda x: x[1].get('timestamp', 0), 
                                  reverse=True)
            
            excess_count = len(cleaned_data) - max_entries
            removed_reasons["excess"] = excess_count
            
            cleaned_data = dict(sorted_entries[:max_entries])
        
        # 保存优化后的缓存
        self.cache_data = cleaned_data
        self._save_cache()
        
        removed_count = original_count - len(cleaned_data)
        
        return {
            "original_entries": original_count,
            "remaining_entries": len(cleaned_data),
            "removed": removed_count,
            "removed_reasons": removed_reasons,
            "space_saved_mb": 0,  # 这里可以计算空间节省
            "optimization_ratio": removed_count / original_count if original_count > 0 else 0
        }


if __name__ == "__main__":
    # 测试翻译缓存
    cache = TranslationCache()
    
    # 测试存储和获取
    cache.store_translation(
        source_text="Multi-dimensional code analysis",
        target_text="多维度代码分析",
        target_lang="zh_CN",
        content_type="commands",
        confidence=0.95,
        cost=0.002
    )
    
    # 测试获取
    cached = cache.get_translation("Multi-dimensional code analysis", "zh_CN", "commands")
    print(f"Cached translation: {cached}")
    
    # 显示统计信息
    stats = cache.get_cache_statistics()
    print(f"Cache statistics: {json.dumps(stats, indent=2)}")