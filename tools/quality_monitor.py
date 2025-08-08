#!/usr/bin/env python3
"""
SuperClaude翻译质量监控系统 / SuperClaude Translation Quality Monitoring System
实时监控翻译质量，生成质量报告和改进建议 / Real-time monitoring of translation quality, generating quality reports and improvement suggestions
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from i18n.cache import TranslationCache
    from i18n.validator import QualityValidator
    from i18n.incremental import IncrementalTranslationManager
except ImportError as e:
    print(f"⚠️ 导入警告: {e}")


@dataclass
class QualityMetrics:
    """质量指标 / Quality Metrics"""
    language: str
    total_items: int
    quality_score: float
    consistency_score: float
    completeness_score: float
    accuracy_score: float
    fluency_score: float
    build_time: str
    file_size_kb: float
    last_updated: str


@dataclass
class QualityTrend:
    """质量趋势 / Quality Trend"""
    language: str
    quality_history: List[Tuple[str, float]]  # (timestamp, quality_score)
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float  # 0.0-1.0
    recommendation: str


@dataclass
class QualityAlert:
    """质量告警 / Quality Alert"""
    severity: str  # "low", "medium", "high", "critical"
    language: str
    metric: str
    current_value: float
    threshold_value: float
    message: str
    timestamp: str


class TranslationQualityMonitor:
    """翻译质量监控器 / Translation Quality Monitor"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.locale_dir = self.project_root / "i18n" / "locales"
        self.monitor_data_dir = self.project_root / ".superclaude" / "quality_monitor"
        self.monitor_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 质量历史文件
        self.quality_history_file = self.monitor_data_dir / "quality_history.jsonl"
        self.alerts_file = self.monitor_data_dir / "quality_alerts.json"
        self.config_file = self.monitor_data_dir / "monitor_config.json"
        
        # 加载配置
        self.config = self._load_monitor_config()
        
        # 初始化组件
        self.validator = QualityValidator()
        self.cache = TranslationCache()
        
    def _load_monitor_config(self) -> Dict[str, Any]:
        """加载监控配置"""
        default_config = {
            "quality_thresholds": {
                "critical": 0.6,    # 低于此分数为严重问题
                "warning": 0.8,     # 低于此分数为警告
                "target": 0.95      # 目标质量分数
            },
            "completeness_thresholds": {
                "critical": 0.7,    # 完整度低于70%为严重问题
                "warning": 0.9,     # 完整度低于90%为警告
                "target": 1.0       # 目标完整度100%
            },
            "trend_analysis": {
                "history_days": 30, # 分析最近30天的趋势
                "min_data_points": 3 # 至少3个数据点才分析趋势
            },
            "alert_settings": {
                "max_alerts": 100,  # 最大告警数量
                "alert_cooldown": 3600 # 相同告警的冷却时间（秒）
            },
            "monitored_languages": ["zh_CN", "ja_JP", "ko_KR", "ru_RU", "es_ES", "de_DE", "fr_FR", "ar_SA"]
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并用户配置和默认配置
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️ 加载监控配置失败: {e}")
        
        return default_config
    
    def _save_monitor_config(self):
        """保存监控配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存监控配置失败: {e}")
    
    def _calculate_quality_metrics(self, locale_file: Path) -> Optional[QualityMetrics]:
        """计算单个语言的质量指标"""
        if not locale_file.exists():
            return None
        
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            language = metadata.get('language', locale_file.stem)
            
            # 基础指标
            total_items = metadata.get('total_items', 0)
            quality_score = metadata.get('quality_score', 0.0)
            build_time = metadata.get('build_time', '')
            
            # 计算完整度
            expected_sections = ['commands', 'personas', 'ui', 'errors', 'help']
            completeness_score = 0.0
            
            if total_items > 0:
                existing_items = 0
                for section in expected_sections:
                    if section in data and isinstance(data[section], dict):
                        existing_items += len([v for v in data[section].values() if v.strip()])
                
                completeness_score = existing_items / total_items if total_items > 0 else 0
            
            # 计算一致性分数（基于术语使用）
            consistency_score = self._calculate_consistency_score(data)
            
            # 准确性和流畅性评分（简化版本）
            accuracy_score = min(quality_score * 1.1, 1.0)  # 基于质量分数估算
            fluency_score = min(quality_score * 1.05, 1.0)   # 基于质量分数估算
            
            # 文件大小
            file_size_kb = locale_file.stat().st_size / 1024
            
            return QualityMetrics(
                language=language,
                total_items=total_items,
                quality_score=quality_score,
                consistency_score=consistency_score,
                completeness_score=completeness_score,
                accuracy_score=accuracy_score,
                fluency_score=fluency_score,
                build_time=build_time,
                file_size_kb=round(file_size_kb, 2),
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"⚠️ 计算质量指标失败 {locale_file}: {e}")
            return None
    
    def _calculate_consistency_score(self, data: Dict[str, Any]) -> float:
        """计算翻译一致性分数"""
        # 这里可以实现更复杂的一致性检查逻辑
        # 目前使用简化版本
        
        try:
            # 检查关键术语的一致性
            key_terms = {
                "SuperClaude", "Claude", "AI", "API", "Git", "GitHub",
                "命令", "分析", "实现", "构建", "翻译", "质量"
            }
            
            all_text = []
            for section in ['commands', 'personas', 'ui', 'errors', 'help']:
                if section in data and isinstance(data[section], dict):
                    all_text.extend(data[section].values())
            
            if not all_text:
                return 0.8  # 默认分数
            
            # 简单的一致性评分
            text_content = " ".join(all_text).lower()
            consistency_indicators = 0
            total_checks = 0
            
            for term in key_terms:
                if term.lower() in text_content:
                    # 检查术语使用的一致性（这里简化处理）
                    count = text_content.count(term.lower())
                    if count > 0:
                        consistency_indicators += min(count / len(all_text), 1.0)
                        total_checks += 1
            
            consistency_score = consistency_indicators / total_checks if total_checks > 0 else 0.8
            return min(consistency_score, 1.0)
            
        except Exception:
            return 0.8  # 发生错误时返回默认分数
    
    def collect_quality_metrics(self) -> Dict[str, QualityMetrics]:
        """收集所有语言的质量指标"""
        metrics = {}
        
        if not self.locale_dir.exists():
            print("⚠️ 本地化目录不存在")
            return metrics
        
        monitored_languages = self.config.get('monitored_languages', [])
        
        for locale_file in self.locale_dir.glob('*.json'):
            if locale_file.name == 'index.json':
                continue
                
            language = locale_file.stem
            if monitored_languages and language not in monitored_languages:
                continue
            
            metric = self._calculate_quality_metrics(locale_file)
            if metric:
                metrics[language] = metric
        
        return metrics
    
    def _record_quality_history(self, metrics: Dict[str, QualityMetrics]):
        """记录质量历史"""
        timestamp = datetime.now().isoformat()
        
        try:
            with open(self.quality_history_file, 'a', encoding='utf-8') as f:
                for language, metric in metrics.items():
                    history_entry = {
                        'timestamp': timestamp,
                        'language': language,
                        'quality_score': metric.quality_score,
                        'completeness_score': metric.completeness_score,
                        'consistency_score': metric.consistency_score,
                        'total_items': metric.total_items
                    }
                    f.write(json.dumps(history_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠️ 记录质量历史失败: {e}")
    
    def _load_quality_history(self, language: str, days: int = 30) -> List[Tuple[str, float]]:
        """加载质量历史"""
        if not self.quality_history_file.exists():
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        history = []
        
        try:
            with open(self.quality_history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if entry.get('language') == language:
                            entry_date = datetime.fromisoformat(entry['timestamp'])
                            if entry_date >= cutoff_date:
                                history.append((entry['timestamp'], entry['quality_score']))
        except Exception as e:
            print(f"⚠️ 加载质量历史失败: {e}")
        
        return sorted(history, key=lambda x: x[0])
    
    def analyze_quality_trends(self, metrics: Dict[str, QualityMetrics]) -> Dict[str, QualityTrend]:
        """分析质量趋势"""
        trends = {}
        history_days = self.config['trend_analysis']['history_days']
        min_data_points = self.config['trend_analysis']['min_data_points']
        
        for language, current_metric in metrics.items():
            history = self._load_quality_history(language, history_days)
            
            if len(history) < min_data_points:
                # 数据不足，无法分析趋势
                trends[language] = QualityTrend(
                    language=language,
                    quality_history=history,
                    trend_direction="insufficient_data",
                    trend_strength=0.0,
                    recommendation="需要更多历史数据来分析趋势"
                )
                continue
            
            # 计算趋势
            scores = [score for _, score in history]
            
            # 简单的趋势分析：比较前半段和后半段的平均分
            mid_point = len(scores) // 2
            early_avg = sum(scores[:mid_point]) / mid_point if mid_point > 0 else 0
            recent_avg = sum(scores[mid_point:]) / (len(scores) - mid_point)
            
            trend_change = recent_avg - early_avg
            trend_strength = abs(trend_change)
            
            if trend_change > 0.02:  # 提升超过2%
                trend_direction = "improving"
                recommendation = "质量呈上升趋势，继续保持"
            elif trend_change < -0.02:  # 下降超过2%
                trend_direction = "declining"
                recommendation = "质量呈下降趋势，需要关注和改进"
            else:
                trend_direction = "stable"
                recommendation = "质量保持稳定"
            
            trends[language] = QualityTrend(
                language=language,
                quality_history=history,
                trend_direction=trend_direction,
                trend_strength=min(trend_strength * 10, 1.0),  # 规范化到0-1
                recommendation=recommendation
            )
        
        return trends
    
    def generate_quality_alerts(self, metrics: Dict[str, QualityMetrics]) -> List[QualityAlert]:
        """生成质量告警"""
        alerts = []
        timestamp = datetime.now().isoformat()
        
        quality_thresholds = self.config['quality_thresholds']
        completeness_thresholds = self.config['completeness_thresholds']
        
        for language, metric in metrics.items():
            # 质量分数告警
            if metric.quality_score < quality_thresholds['critical']:
                alerts.append(QualityAlert(
                    severity="critical",
                    language=language,
                    metric="quality_score",
                    current_value=metric.quality_score,
                    threshold_value=quality_thresholds['critical'],
                    message=f"{language}翻译质量严重偏低({metric.quality_score:.3f})",
                    timestamp=timestamp
                ))
            elif metric.quality_score < quality_thresholds['warning']:
                alerts.append(QualityAlert(
                    severity="medium",
                    language=language,
                    metric="quality_score",
                    current_value=metric.quality_score,
                    threshold_value=quality_thresholds['warning'],
                    message=f"{language}翻译质量需要改进({metric.quality_score:.3f})",
                    timestamp=timestamp
                ))
            
            # 完整度告警
            if metric.completeness_score < completeness_thresholds['critical']:
                alerts.append(QualityAlert(
                    severity="critical",
                    language=language,
                    metric="completeness_score",
                    current_value=metric.completeness_score,
                    threshold_value=completeness_thresholds['critical'],
                    message=f"{language}翻译完整度严重不足({metric.completeness_score:.1%})",
                    timestamp=timestamp
                ))
            elif metric.completeness_score < completeness_thresholds['warning']:
                alerts.append(QualityAlert(
                    severity="medium",
                    language=language,
                    metric="completeness_score",
                    current_value=metric.completeness_score,
                    threshold_value=completeness_thresholds['warning'],
                    message=f"{language}翻译完整度需要提升({metric.completeness_score:.1%})",
                    timestamp=timestamp
                ))
            
            # 一致性告警
            if metric.consistency_score < 0.7:
                alerts.append(QualityAlert(
                    severity="medium",
                    language=language,
                    metric="consistency_score",
                    current_value=metric.consistency_score,
                    threshold_value=0.7,
                    message=f"{language}翻译一致性需要改进({metric.consistency_score:.3f})",
                    timestamp=timestamp
                ))
        
        return alerts
    
    def _save_alerts(self, alerts: List[QualityAlert]):
        """保存告警"""
        try:
            alerts_data = [asdict(alert) for alert in alerts]
            
            # 加载现有告警
            existing_alerts = []
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    existing_alerts = json.load(f)
            
            # 合并告警（避免重复）
            max_alerts = self.config['alert_settings']['max_alerts']
            all_alerts = alerts_data + existing_alerts
            
            # 按时间排序并限制数量
            all_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
            all_alerts = all_alerts[:max_alerts]
            
            # 保存告警
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(all_alerts, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ 保存告警失败: {e}")
    
    def generate_quality_report(self, include_trends: bool = True, 
                               include_alerts: bool = True) -> Dict[str, Any]:
        """生成质量报告"""
        print("📊 生成翻译质量报告...")
        
        # 收集指标
        metrics = self.collect_quality_metrics()
        
        if not metrics:
            return {
                "status": "error",
                "message": "未找到翻译文件或质量指标",
                "timestamp": datetime.now().isoformat()
            }
        
        # 记录历史
        self._record_quality_history(metrics)
        
        # 分析趋势
        trends = {}
        if include_trends:
            trends = self.analyze_quality_trends(metrics)
        
        # 生成告警
        alerts = []
        if include_alerts:
            alerts = self.generate_quality_alerts(metrics)
            self._save_alerts(alerts)
        
        # 计算总体统计
        total_languages = len(metrics)
        avg_quality = sum(m.quality_score for m in metrics.values()) / total_languages
        avg_completeness = sum(m.completeness_score for m in metrics.values()) / total_languages
        avg_consistency = sum(m.consistency_score for m in metrics.values()) / total_languages
        
        # 获取缓存统计
        cache_stats = {}
        try:
            cache_stats = self.cache.get_cache_statistics()
        except Exception:
            cache_stats = {"status": "unavailable"}
        
        report = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_languages": total_languages,
                "average_quality": round(avg_quality, 3),
                "average_completeness": round(avg_completeness, 3),
                "average_consistency": round(avg_consistency, 3),
                "total_alerts": len(alerts),
                "critical_alerts": len([a for a in alerts if a.severity == "critical"])
            },
            "metrics": {lang: asdict(metric) for lang, metric in metrics.items()},
            "cache_stats": cache_stats
        }
        
        if include_trends:
            report["trends"] = {lang: asdict(trend) for lang, trend in trends.items()}
        
        if include_alerts:
            report["alerts"] = [asdict(alert) for alert in alerts]
        
        return report
    
    def run_continuous_monitoring(self, interval_minutes: int = 60):
        """运行持续监控"""
        print(f"🔄 启动持续监控，间隔 {interval_minutes} 分钟")
        
        try:
            while True:
                print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 运行质量检查")
                
                report = self.generate_quality_report()
                
                if report["status"] == "success":
                    summary = report["summary"]
                    print(f"📊 质量摘要:")
                    print(f"   语言数量: {summary['total_languages']}")
                    print(f"   平均质量: {summary['average_quality']:.3f}")
                    print(f"   平均完整度: {summary['average_completeness']:.3f}")
                    print(f"   告警数量: {summary['total_alerts']}")
                    
                    if summary['critical_alerts'] > 0:
                        print(f"🚨 发现 {summary['critical_alerts']} 个严重告警!")
                else:
                    print(f"❌ 质量检查失败: {report.get('message', '未知错误')}")
                
                print(f"😴 等待 {interval_minutes} 分钟...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n⏹️ 监控已停止")
        except Exception as e:
            print(f"❌ 监控异常: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="SuperClaude翻译质量监控")
    parser.add_argument("action", choices=[
        "report", "monitor", "alerts", "config", "trends"
    ], help="操作类型")
    
    parser.add_argument("--project-root", default=".",
                       help="项目根目录")
    parser.add_argument("--interval", type=int, default=60,
                       help="监控间隔（分钟）")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                       help="输出格式")
    parser.add_argument("--save-report", 
                       help="保存报告到指定文件")
    parser.add_argument("--no-trends", action="store_true",
                       help="不包含趋势分析")
    parser.add_argument("--no-alerts", action="store_true",
                       help="不包含告警生成")
    
    args = parser.parse_args()
    
    # 创建质量监控器
    monitor = TranslationQualityMonitor(args.project_root)
    
    if args.action == "report":
        # 生成质量报告
        report = monitor.generate_quality_report(
            include_trends=not args.no_trends,
            include_alerts=not args.no_alerts
        )
        
        if args.format == "json":
            output = json.dumps(report, ensure_ascii=False, indent=2)
        else:
            # 文本格式输出
            if report["status"] == "success":
                summary = report["summary"]
                output = f"""📊 SuperClaude翻译质量报告

🌍 总体概况:
   支持语言: {summary['total_languages']} 种
   平均质量: {summary['average_quality']:.3f}
   平均完整度: {summary['average_completeness']:.1%}
   平均一致性: {summary['average_consistency']:.3f}

⚠️ 告警统计:
   总告警数: {summary['total_alerts']}
   严重告警: {summary['critical_alerts']}

📈 详细指标:"""
                
                for lang, metric in report["metrics"].items():
                    output += f"""
   {lang}: 质量{metric['quality_score']:.3f} 完整度{metric['completeness_score']:.1%}"""
            else:
                output = f"❌ 报告生成失败: {report.get('message', '未知错误')}"
        
        print(output)
        
        # 保存报告
        if args.save_report:
            try:
                with open(args.save_report, 'w', encoding='utf-8') as f:
                    if args.format == "json":
                        json.dump(report, f, ensure_ascii=False, indent=2)
                    else:
                        f.write(output)
                print(f"✅ 报告已保存到: {args.save_report}")
            except Exception as e:
                print(f"⚠️ 保存报告失败: {e}")
    
    elif args.action == "monitor":
        # 运行持续监控
        monitor.run_continuous_monitoring(args.interval)
    
    elif args.action == "alerts":
        # 显示告警
        if monitor.alerts_file.exists():
            with open(monitor.alerts_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
                print(json.dumps(alerts, ensure_ascii=False, indent=2))
        else:
            print("📭 暂无告警记录")
    
    elif args.action == "config":
        # 显示配置
        print("⚙️ 当前监控配置:")
        print(json.dumps(monitor.config, ensure_ascii=False, indent=2))
    
    elif args.action == "trends":
        # 趋势分析
        metrics = monitor.collect_quality_metrics()
        trends = monitor.analyze_quality_trends(metrics)
        
        print("📈 质量趋势分析:")
        for lang, trend in trends.items():
            print(f"\n{lang}:")
            print(f"   趋势方向: {trend.trend_direction}")
            print(f"   趋势强度: {trend.trend_strength:.3f}")
            print(f"   建议: {trend.recommendation}")


if __name__ == "__main__":
    main()