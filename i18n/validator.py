#!/usr/bin/env python3
"""
翻译质量验证器 / Translation Quality Validator
验证翻译质量，检查术语一致性和格式正确性 / Validates translation quality, checks terminology consistency and format correctness
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class QualityIssue:
    """质量问题 / Quality issue"""
    issue_type: str  # terminology, format, length, consistency
    severity: str    # critical, warning, info
    description: str
    suggestion: Optional[str] = None


@dataclass 
class QualityScore:
    """质量评分 / Quality score"""
    overall_score: float  # 0.0 - 1.0
    terminology_score: float
    format_score: float
    consistency_score: float
    readability_score: float
    issues: List[QualityIssue]
    passed: bool


class QualityValidator:
    """翻译质量验证器 / Translation quality validator"""
    
    def __init__(self):
        """初始化质量验证器"""
        
        # SuperClaude专业术语标准词典
        self.standard_terms = {
            "zh_CN": {
                "analyze": "分析",
                "implement": "实现", 
                "build": "构建",
                "improve": "改进",
                "design": "设计",
                "component": "组件",
                "persona": "专家角色",
                "framework": "框架",
                "architecture": "架构",
                "performance": "性能",
                "security": "安全",
                "workflow": "工作流",
                "orchestration": "编排",
                "troubleshoot": "故障排除"
            },
            "ja_JP": {
                "analyze": "分析",
                "implement": "実装",
                "build": "ビルド",
                "improve": "改善",
                "design": "設計",
                "component": "コンポーネント",
                "persona": "ペルソナ",
                "framework": "フレームワーク",
                "architecture": "アーキテクチャ",
                "performance": "パフォーマンス",
                "security": "セキュリティ",
                "workflow": "ワークフロー",
                "orchestration": "オーケストレーション",
                "troubleshoot": "トラブルシューティング"
            }
        }
        
        # 不应被翻译的技术标识符
        self.protected_patterns = [
            r'/sc:\w+',           # SuperClaude命令
            r'--[\w-]+',          # 命令参数
            r'\{\w+\}',           # 变量占位符
            r'```[\s\S]*?```',    # 代码块
            r'`[^`]+`',           # 行内代码
            r'https?://\S+',      # URL链接
            r'[\w./]+\.py',       # 文件路径
        ]
        
        # 质量评分权重
        self.score_weights = {
            "terminology": 0.35,
            "format": 0.25,
            "consistency": 0.25,
            "readability": 0.15
        }
    
    def validate_translation(self, 
                           original: str, 
                           translated: str, 
                           target_lang: str,
                           content_type: str = "default") -> QualityScore:
        """验证翻译质量"""
        
        issues = []
        
        # 1. 术语一致性检查
        terminology_score, term_issues = self._check_terminology_consistency(
            original, translated, target_lang
        )
        issues.extend(term_issues)
        
        # 2. 格式保持性检查
        format_score, format_issues = self._check_format_preservation(
            original, translated
        )
        issues.extend(format_issues)
        
        # 3. 技术标识符保护检查
        consistency_score, consistency_issues = self._check_technical_preservation(
            original, translated
        )
        issues.extend(consistency_issues)
        
        # 4. 可读性检查
        readability_score, readability_issues = self._check_readability(
            translated, target_lang, content_type
        )
        issues.extend(readability_issues)
        
        # 计算综合评分
        overall_score = (
            terminology_score * self.score_weights["terminology"] +
            format_score * self.score_weights["format"] +
            consistency_score * self.score_weights["consistency"] +
            readability_score * self.score_weights["readability"]
        )
        
        # 判断是否通过质量检查
        passed = overall_score >= 0.8 and not any(
            issue.severity == "critical" for issue in issues
        )
        
        return QualityScore(
            overall_score=overall_score,
            terminology_score=terminology_score,
            format_score=format_score,
            consistency_score=consistency_score,
            readability_score=readability_score,
            issues=issues,
            passed=passed
        )
    
    def _check_terminology_consistency(self, 
                                     original: str, 
                                     translated: str,
                                     target_lang: str) -> Tuple[float, List[QualityIssue]]:
        """检查术语一致性"""
        issues = []
        score = 1.0
        
        if target_lang not in self.standard_terms:
            # 不支持的语言，跳过术语检查
            return score, issues
        
        terms = self.standard_terms[target_lang]
        original_lower = original.lower()
        
        for english_term, standard_translation in terms.items():
            if english_term in original_lower:
                # 检查译文中是否使用了标准翻译
                if standard_translation not in translated:
                    issues.append(QualityIssue(
                        issue_type="terminology",
                        severity="warning",
                        description=f"术语 '{english_term}' 可能未使用标准翻译 '{standard_translation}'",
                        suggestion=f"建议使用标准术语: {standard_translation}"
                    ))
                    score -= 0.1
        
        return max(0.0, score), issues
    
    def _check_format_preservation(self, 
                                 original: str, 
                                 translated: str) -> Tuple[float, List[QualityIssue]]:
        """检查格式保持性"""
        issues = []
        score = 1.0
        
        # 检查标记符号
        format_elements = [
            ('**', '粗体标记'),
            ('*', '斜体标记'),
            ('`', '代码标记'),
            ('```', '代码块标记'),
            ('[', '链接开始'),
            (']', '链接结束'),
            ('(', '括号开始'),
            (')', '括号结束')
        ]
        
        for marker, description in format_elements:
            original_count = original.count(marker)
            translated_count = translated.count(marker)
            
            if original_count != translated_count:
                issues.append(QualityIssue(
                    issue_type="format",
                    severity="warning",
                    description=f"{description}数量不匹配: 原文{original_count}个，译文{translated_count}个",
                    suggestion=f"检查{description}是否正确保留"
                ))
                score -= 0.1
        
        return max(0.0, score), issues
    
    def _check_technical_preservation(self, 
                                    original: str, 
                                    translated: str) -> Tuple[float, List[QualityIssue]]:
        """检查技术标识符保护"""
        issues = []
        score = 1.0
        
        for pattern in self.protected_patterns:
            original_matches = re.findall(pattern, original)
            translated_matches = re.findall(pattern, translated)
            
            # 检查技术标识符是否完整保留
            for match in original_matches:
                if match not in translated:
                    issues.append(QualityIssue(
                        issue_type="consistency",
                        severity="critical",
                        description=f"技术标识符 '{match}' 在译文中丢失",
                        suggestion=f"必须保留技术标识符: {match}"
                    ))
                    score -= 0.2
        
        return max(0.0, score), issues
    
    def _check_readability(self, 
                          translated: str, 
                          target_lang: str,
                          content_type: str) -> Tuple[float, List[QualityIssue]]:
        """检查可读性"""
        issues = []
        score = 1.0
        
        # 长度合理性检查
        length = len(translated)
        if length < 5:
            issues.append(QualityIssue(
                issue_type="readability",
                severity="warning",
                description="译文过短，可能信息不完整",
                suggestion="检查翻译是否完整"
            ))
            score -= 0.1
        elif length > 500:
            issues.append(QualityIssue(
                issue_type="readability",
                severity="info",
                description="译文较长，建议检查是否可以简化",
                suggestion="考虑简化表达"
            ))
        
        # 特殊字符检查
        if content_type == "ui":
            # UI文本应该简洁
            if length > 100:
                issues.append(QualityIssue(
                    issue_type="readability",
                    severity="warning",
                    description="UI文本过长，可能影响用户体验",
                    suggestion="UI文本建议保持简洁"
                ))
                score -= 0.1
        
        # 检查是否包含翻译错误标记
        error_indicators = ["[翻译失败", "[Translation failed", "ERROR"]
        for indicator in error_indicators:
            if indicator in translated:
                issues.append(QualityIssue(
                    issue_type="readability",
                    severity="critical",
                    description="译文包含错误标记",
                    suggestion="需要重新翻译"
                ))
                score = 0.0
                break
        
        return max(0.0, score), issues
    
    def batch_validate(self, 
                      translations: List[Tuple[str, str, str, str]]) -> Dict[str, QualityScore]:
        """
        批量验证翻译质量
        
        Args:
            translations: [(original, translated, target_lang, content_type), ...]
        
        Returns:
            Dict: {index: QualityScore}
        """
        results = {}
        
        for i, (original, translated, target_lang, content_type) in enumerate(translations):
            score = self.validate_translation(original, translated, target_lang, content_type)
            results[str(i)] = score
        
        return results
    
    def generate_quality_report(self, 
                              validation_results: Dict[str, QualityScore]) -> Dict:
        """生成质量报告"""
        
        total_count = len(validation_results)
        passed_count = sum(1 for score in validation_results.values() if score.passed)
        
        # 统计问题类型
        issue_counts = {
            "critical": 0,
            "warning": 0, 
            "info": 0
        }
        
        issue_type_counts = {
            "terminology": 0,
            "format": 0,
            "consistency": 0,
            "readability": 0
        }
        
        all_issues = []
        total_score = 0.0
        
        for score in validation_results.values():
            total_score += score.overall_score
            all_issues.extend(score.issues)
            
            for issue in score.issues:
                issue_counts[issue.severity] += 1
                issue_type_counts[issue.issue_type] += 1
        
        average_score = total_score / total_count if total_count > 0 else 0.0
        pass_rate = passed_count / total_count if total_count > 0 else 0.0
        
        return {
            "summary": {
                "total_translations": total_count,
                "passed_translations": passed_count,
                "pass_rate": round(pass_rate, 3),
                "average_score": round(average_score, 3)
            },
            "issues": {
                "by_severity": issue_counts,
                "by_type": issue_type_counts,
                "total_issues": len(all_issues)
            },
            "recommendations": self._generate_recommendations(issue_type_counts, pass_rate)
        }
    
    def _generate_recommendations(self, 
                                issue_counts: Dict[str, int], 
                                pass_rate: float) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if pass_rate < 0.7:
            recommendations.append("整体翻译质量较低，建议重新检查翻译策略和术语词典")
        
        if issue_counts.get("terminology", 0) > 0:
            recommendations.append("存在术语不一致问题，建议完善术语词典并加强术语干预")
        
        if issue_counts.get("consistency", 0) > 0:
            recommendations.append("存在技术标识符丢失，建议完善保护模式列表")
        
        if issue_counts.get("format", 0) > 0:
            recommendations.append("存在格式不一致，建议检查标记符号处理逻辑")
        
        if issue_counts.get("readability", 0) > 0:
            recommendations.append("存在可读性问题，建议优化翻译风格和长度控制")
        
        if not recommendations:
            recommendations.append("翻译质量良好，保持现有标准")
        
        return recommendations


if __name__ == "__main__":
    # 测试质量验证器
    validator = QualityValidator()
    
    # 测试用例
    test_cases = [
        (
            "Multi-dimensional code analysis with /sc:analyze",
            "多维度代码分析使用 /sc:analyze",
            "zh_CN",
            "commands"
        ),
        (
            "**Bold text** and `code snippet`",
            "**粗体文本** 和 `代码片段`",
            "zh_CN", 
            "ui"
        ),
        (
            "Error: File not found",
            "[翻译失败: API错误]",
            "zh_CN",
            "errors"
        )
    ]
    
    # 验证测试用例
    for i, (original, translated, lang, content_type) in enumerate(test_cases):
        score = validator.validate_translation(original, translated, lang, content_type)
        print(f"\n测试用例 {i+1}:")
        print(f"原文: {original}")
        print(f"译文: {translated}")
        print(f"总分: {score.overall_score:.2f}")
        print(f"通过: {score.passed}")
        
        if score.issues:
            print("问题:")
            for issue in score.issues:
                print(f"  - {issue.severity}: {issue.description}")
    
    # 生成质量报告
    results = {
        str(i): validator.validate_translation(original, translated, lang, content_type)
        for i, (original, translated, lang, content_type) in enumerate(test_cases)
    }
    
    report = validator.generate_quality_report(results)
    print(f"\n质量报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))