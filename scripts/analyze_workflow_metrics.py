#!/usr/bin/env python3
"""
Workflow Metrics Analysis Script

Analyzes workflow_metrics.jsonl for continuous optimization and A/B testing.

Usage:
    python scripts/analyze_workflow_metrics.py --period week
    python scripts/analyze_workflow_metrics.py --period month
    python scripts/analyze_workflow_metrics.py --task-type bug_fix
"""

import argparse
import json
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class WorkflowMetricsAnalyzer:
    """Analyze workflow metrics for optimization"""

    def __init__(self, metrics_file: Path):
        self.metrics_file = metrics_file
        self.metrics: List[Dict] = []
        self._load_metrics()

    def _load_metrics(self):
        """Load metrics from JSONL file"""
        if not self.metrics_file.exists():
            print(f"Warning: {self.metrics_file} not found")
            return

        with open(self.metrics_file, 'r') as f:
            for line in f:
                if line.strip():
                    self.metrics.append(json.loads(line))

        print(f"Loaded {len(self.metrics)} metric records")

    def filter_by_period(self, period: str) -> List[Dict]:
        """Filter metrics by time period"""
        now = datetime.now()

        if period == "week":
            cutoff = now - timedelta(days=7)
        elif period == "month":
            cutoff = now - timedelta(days=30)
        elif period == "all":
            return self.metrics
        else:
            raise ValueError(f"Invalid period: {period}")

        filtered = [
            m for m in self.metrics
            if datetime.fromisoformat(m['timestamp']) >= cutoff
        ]

        print(f"Filtered to {len(filtered)} records in last {period}")
        return filtered

    def analyze_by_task_type(self, metrics: List[Dict]) -> Dict:
        """Analyze metrics grouped by task type"""
        by_task = defaultdict(list)

        for m in metrics:
            by_task[m['task_type']].append(m)

        results = {}
        for task_type, task_metrics in by_task.items():
            results[task_type] = {
                'count': len(task_metrics),
                'avg_tokens': statistics.mean(m['tokens_used'] for m in task_metrics),
                'avg_time_ms': statistics.mean(m['time_ms'] for m in task_metrics),
                'success_rate': sum(m['success'] for m in task_metrics) / len(task_metrics) * 100,
                'avg_files_read': statistics.mean(m.get('files_read', 0) for m in task_metrics),
            }

        return results

    def analyze_by_complexity(self, metrics: List[Dict]) -> Dict:
        """Analyze metrics grouped by complexity level"""
        by_complexity = defaultdict(list)

        for m in metrics:
            by_complexity[m['complexity']].append(m)

        results = {}
        for complexity, comp_metrics in by_complexity.items():
            results[complexity] = {
                'count': len(comp_metrics),
                'avg_tokens': statistics.mean(m['tokens_used'] for m in comp_metrics),
                'avg_time_ms': statistics.mean(m['time_ms'] for m in comp_metrics),
                'success_rate': sum(m['success'] for m in comp_metrics) / len(comp_metrics) * 100,
            }

        return results

    def analyze_by_workflow(self, metrics: List[Dict]) -> Dict:
        """Analyze metrics grouped by workflow variant"""
        by_workflow = defaultdict(list)

        for m in metrics:
            by_workflow[m['workflow_id']].append(m)

        results = {}
        for workflow_id, wf_metrics in by_workflow.items():
            results[workflow_id] = {
                'count': len(wf_metrics),
                'avg_tokens': statistics.mean(m['tokens_used'] for m in wf_metrics),
                'median_tokens': statistics.median(m['tokens_used'] for m in wf_metrics),
                'avg_time_ms': statistics.mean(m['time_ms'] for m in wf_metrics),
                'success_rate': sum(m['success'] for m in wf_metrics) / len(wf_metrics) * 100,
            }

        return results

    def identify_best_workflows(self, metrics: List[Dict]) -> Dict[str, str]:
        """Identify best workflow for each task type"""
        by_task_workflow = defaultdict(lambda: defaultdict(list))

        for m in metrics:
            by_task_workflow[m['task_type']][m['workflow_id']].append(m)

        best_workflows = {}
        for task_type, workflows in by_task_workflow.items():
            best_workflow = None
            best_score = float('inf')

            for workflow_id, wf_metrics in workflows.items():
                # Score = avg_tokens (lower is better)
                avg_tokens = statistics.mean(m['tokens_used'] for m in wf_metrics)
                success_rate = sum(m['success'] for m in wf_metrics) / len(wf_metrics)

                # Only consider if success rate >= 95%
                if success_rate >= 0.95:
                    if avg_tokens < best_score:
                        best_score = avg_tokens
                        best_workflow = workflow_id

            if best_workflow:
                best_workflows[task_type] = best_workflow

        return best_workflows

    def identify_inefficiencies(self, metrics: List[Dict]) -> List[Dict]:
        """Identify inefficient patterns"""
        inefficiencies = []

        # Expected token budgets by complexity
        budgets = {
            'ultra-light': 800,
            'light': 2000,
            'medium': 5000,
            'heavy': 20000,
            'ultra-heavy': 50000
        }

        for m in metrics:
            issues = []

            # Check token budget overrun
            expected_budget = budgets.get(m['complexity'], 5000)
            if m['tokens_used'] > expected_budget * 1.3:  # 30% over budget
                issues.append(f"Token overrun: {m['tokens_used']} vs {expected_budget}")

            # Check success rate
            if not m['success']:
                issues.append("Task failed")

            # Check time performance (light tasks should be fast)
            if m['complexity'] in ['ultra-light', 'light'] and m['time_ms'] > 10000:
                issues.append(f"Slow execution: {m['time_ms']}ms for {m['complexity']} task")

            if issues:
                inefficiencies.append({
                    'timestamp': m['timestamp'],
                    'task_type': m['task_type'],
                    'complexity': m['complexity'],
                    'workflow_id': m['workflow_id'],
                    'issues': issues
                })

        return inefficiencies

    def calculate_token_savings(self, metrics: List[Dict]) -> Dict:
        """Calculate token savings vs unlimited baseline"""
        # Unlimited baseline estimates
        baseline = {
            'ultra-light': 1000,
            'light': 2500,
            'medium': 7500,
            'heavy': 30000,
            'ultra-heavy': 100000
        }

        total_actual = 0
        total_baseline = 0

        for m in metrics:
            total_actual += m['tokens_used']
            total_baseline += baseline.get(m['complexity'], 7500)

        savings = total_baseline - total_actual
        savings_percent = (savings / total_baseline * 100) if total_baseline > 0 else 0

        return {
            'total_actual': total_actual,
            'total_baseline': total_baseline,
            'total_savings': savings,
            'savings_percent': savings_percent
        }

    def generate_report(self, period: str) -> str:
        """Generate comprehensive analysis report"""
        metrics = self.filter_by_period(period)

        if not metrics:
            return "No metrics available for analysis"

        report = []
        report.append("=" * 80)
        report.append(f"WORKFLOW METRICS ANALYSIS REPORT - Last {period}")
        report.append("=" * 80)
        report.append("")

        # Overall statistics
        report.append("## Overall Statistics")
        report.append(f"Total Tasks: {len(metrics)}")
        report.append(f"Success Rate: {sum(m['success'] for m in metrics) / len(metrics) * 100:.1f}%")
        report.append(f"Avg Tokens: {statistics.mean(m['tokens_used'] for m in metrics):.0f}")
        report.append(f"Avg Time: {statistics.mean(m['time_ms'] for m in metrics):.0f}ms")
        report.append("")

        # Token savings
        savings = self.calculate_token_savings(metrics)
        report.append("## Token Efficiency")
        report.append(f"Actual Usage: {savings['total_actual']:,} tokens")
        report.append(f"Unlimited Baseline: {savings['total_baseline']:,} tokens")
        report.append(f"Total Savings: {savings['total_savings']:,} tokens ({savings['savings_percent']:.1f}%)")
        report.append("")

        # By task type
        report.append("## Analysis by Task Type")
        by_task = self.analyze_by_task_type(metrics)
        for task_type, stats in sorted(by_task.items()):
            report.append(f"\n### {task_type}")
            report.append(f"  Count: {stats['count']}")
            report.append(f"  Avg Tokens: {stats['avg_tokens']:.0f}")
            report.append(f"  Avg Time: {stats['avg_time_ms']:.0f}ms")
            report.append(f"  Success Rate: {stats['success_rate']:.1f}%")
            report.append(f"  Avg Files Read: {stats['avg_files_read']:.1f}")

        report.append("")

        # By complexity
        report.append("## Analysis by Complexity")
        by_complexity = self.analyze_by_complexity(metrics)
        for complexity in ['ultra-light', 'light', 'medium', 'heavy', 'ultra-heavy']:
            if complexity in by_complexity:
                stats = by_complexity[complexity]
                report.append(f"\n### {complexity}")
                report.append(f"  Count: {stats['count']}")
                report.append(f"  Avg Tokens: {stats['avg_tokens']:.0f}")
                report.append(f"  Success Rate: {stats['success_rate']:.1f}%")

        report.append("")

        # Best workflows
        report.append("## Best Workflows per Task Type")
        best = self.identify_best_workflows(metrics)
        for task_type, workflow_id in sorted(best.items()):
            report.append(f"  {task_type}: {workflow_id}")

        report.append("")

        # Inefficiencies
        inefficiencies = self.identify_inefficiencies(metrics)
        if inefficiencies:
            report.append("## Inefficiencies Detected")
            report.append(f"Total Issues: {len(inefficiencies)}")
            for issue in inefficiencies[:5]:  # Show top 5
                report.append(f"\n  {issue['timestamp']}")
                report.append(f"    Task: {issue['task_type']} ({issue['complexity']})")
                report.append(f"    Workflow: {issue['workflow_id']}")
                for problem in issue['issues']:
                    report.append(f"    - {problem}")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Analyze workflow metrics")
    parser.add_argument(
        '--period',
        choices=['week', 'month', 'all'],
        default='week',
        help='Analysis time period'
    )
    parser.add_argument(
        '--task-type',
        help='Filter by specific task type'
    )
    parser.add_argument(
        '--output',
        help='Output file (default: stdout)'
    )

    args = parser.parse_args()

    # Find metrics file
    metrics_file = Path('docs/memory/workflow_metrics.jsonl')

    analyzer = WorkflowMetricsAnalyzer(metrics_file)
    report = analyzer.generate_report(args.period)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()
