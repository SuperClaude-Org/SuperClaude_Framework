#!/usr/bin/env python3
"""
A/B Testing Framework for Workflow Variants

Compares two workflow variants with statistical significance testing.

Usage:
    python scripts/ab_test_workflows.py \\
        --variant-a progressive_v3_layer2 \\
        --variant-b experimental_eager_layer3 \\
        --metric tokens_used
"""

import argparse
import json
import statistics
from pathlib import Path
from typing import Dict, List, Tuple

from scipy import stats


class ABTestAnalyzer:
    """A/B testing framework for workflow optimization"""

    def __init__(self, metrics_file: Path):
        self.metrics_file = metrics_file
        self.metrics: List[Dict] = []
        self._load_metrics()

    def _load_metrics(self):
        """Load metrics from JSONL file"""
        if not self.metrics_file.exists():
            print(f"Error: {self.metrics_file} not found")
            return

        with open(self.metrics_file, 'r') as f:
            for line in f:
                if line.strip():
                    self.metrics.append(json.loads(line))

    def get_variant_metrics(self, workflow_id: str) -> List[Dict]:
        """Get all metrics for a specific workflow variant"""
        return [m for m in self.metrics if m['workflow_id'] == workflow_id]

    def extract_metric_values(self, metrics: List[Dict], metric: str) -> List[float]:
        """Extract specific metric values from metrics list"""
        values = []
        for m in metrics:
            if metric in m:
                value = m[metric]
                # Handle boolean metrics
                if isinstance(value, bool):
                    value = 1.0 if value else 0.0
                values.append(float(value))
        return values

    def calculate_statistics(self, values: List[float]) -> Dict:
        """Calculate statistical measures"""
        if not values:
            return {
                'count': 0,
                'mean': 0,
                'median': 0,
                'stdev': 0,
                'min': 0,
                'max': 0
            }

        return {
            'count': len(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values)
        }

    def perform_ttest(
        self,
        variant_a_values: List[float],
        variant_b_values: List[float]
    ) -> Tuple[float, float]:
        """
        Perform independent t-test between two variants.

        Returns:
            (t_statistic, p_value)
        """
        if len(variant_a_values) < 2 or len(variant_b_values) < 2:
            return 0.0, 1.0  # Not enough data

        t_stat, p_value = stats.ttest_ind(variant_a_values, variant_b_values)
        return t_stat, p_value

    def determine_winner(
        self,
        variant_a_stats: Dict,
        variant_b_stats: Dict,
        p_value: float,
        metric: str,
        lower_is_better: bool = True
    ) -> str:
        """
        Determine winning variant based on statistics.

        Args:
            variant_a_stats: Statistics for variant A
            variant_b_stats: Statistics for variant B
            p_value: Statistical significance (p-value)
            metric: Metric being compared
            lower_is_better: True if lower values are better (e.g., tokens_used)

        Returns:
            Winner description
        """
        # Require statistical significance (p < 0.05)
        if p_value >= 0.05:
            return "No significant difference (p ≥ 0.05)"

        # Require minimum sample size (20 trials per variant)
        if variant_a_stats['count'] < 20 or variant_b_stats['count'] < 20:
            return f"Insufficient data (need 20 trials, have {variant_a_stats['count']}/{variant_b_stats['count']})"

        # Compare means
        a_mean = variant_a_stats['mean']
        b_mean = variant_b_stats['mean']

        if lower_is_better:
            if a_mean < b_mean:
                improvement = ((b_mean - a_mean) / b_mean) * 100
                return f"Variant A wins ({improvement:.1f}% better)"
            else:
                improvement = ((a_mean - b_mean) / a_mean) * 100
                return f"Variant B wins ({improvement:.1f}% better)"
        else:
            if a_mean > b_mean:
                improvement = ((a_mean - b_mean) / b_mean) * 100
                return f"Variant A wins ({improvement:.1f}% better)"
            else:
                improvement = ((b_mean - a_mean) / a_mean) * 100
                return f"Variant B wins ({improvement:.1f}% better)"

    def generate_recommendation(
        self,
        winner: str,
        variant_a_stats: Dict,
        variant_b_stats: Dict,
        p_value: float
    ) -> str:
        """Generate actionable recommendation"""
        if "No significant difference" in winner:
            return "⚖️ Keep current workflow (no improvement detected)"

        if "Insufficient data" in winner:
            return "📊 Continue testing (need more trials)"

        if "Variant A wins" in winner:
            return "✅ Keep Variant A as standard (statistically better)"

        if "Variant B wins" in winner:
            if variant_b_stats['mean'] > variant_a_stats['mean'] * 0.8:  # At least 20% better
                return "🚀 Promote Variant B to standard (significant improvement)"
            else:
                return "⚠️ Marginal improvement - continue testing before promotion"

        return "🤔 Manual review recommended"

    def compare_variants(
        self,
        variant_a_id: str,
        variant_b_id: str,
        metric: str = 'tokens_used',
        lower_is_better: bool = True
    ) -> str:
        """
        Compare two workflow variants on a specific metric.

        Args:
            variant_a_id: Workflow ID for variant A
            variant_b_id: Workflow ID for variant B
            metric: Metric to compare (default: tokens_used)
            lower_is_better: True if lower values are better

        Returns:
            Comparison report
        """
        # Get metrics for each variant
        variant_a_metrics = self.get_variant_metrics(variant_a_id)
        variant_b_metrics = self.get_variant_metrics(variant_b_id)

        if not variant_a_metrics:
            return f"Error: No data for variant A ({variant_a_id})"
        if not variant_b_metrics:
            return f"Error: No data for variant B ({variant_b_id})"

        # Extract metric values
        a_values = self.extract_metric_values(variant_a_metrics, metric)
        b_values = self.extract_metric_values(variant_b_metrics, metric)

        # Calculate statistics
        a_stats = self.calculate_statistics(a_values)
        b_stats = self.calculate_statistics(b_values)

        # Perform t-test
        t_stat, p_value = self.perform_ttest(a_values, b_values)

        # Determine winner
        winner = self.determine_winner(a_stats, b_stats, p_value, metric, lower_is_better)

        # Generate recommendation
        recommendation = self.generate_recommendation(winner, a_stats, b_stats, p_value)

        # Format report
        report = []
        report.append("=" * 80)
        report.append("A/B TEST COMPARISON REPORT")
        report.append("=" * 80)
        report.append("")
        report.append(f"Metric: {metric}")
        report.append(f"Better: {'Lower' if lower_is_better else 'Higher'} values")
        report.append("")

        report.append(f"## Variant A: {variant_a_id}")
        report.append(f"  Trials: {a_stats['count']}")
        report.append(f"  Mean: {a_stats['mean']:.2f}")
        report.append(f"  Median: {a_stats['median']:.2f}")
        report.append(f"  Std Dev: {a_stats['stdev']:.2f}")
        report.append(f"  Range: {a_stats['min']:.2f} - {a_stats['max']:.2f}")
        report.append("")

        report.append(f"## Variant B: {variant_b_id}")
        report.append(f"  Trials: {b_stats['count']}")
        report.append(f"  Mean: {b_stats['mean']:.2f}")
        report.append(f"  Median: {b_stats['median']:.2f}")
        report.append(f"  Std Dev: {b_stats['stdev']:.2f}")
        report.append(f"  Range: {b_stats['min']:.2f} - {b_stats['max']:.2f}")
        report.append("")

        report.append("## Statistical Significance")
        report.append(f"  t-statistic: {t_stat:.4f}")
        report.append(f"  p-value: {p_value:.4f}")
        if p_value < 0.01:
            report.append("  Significance: *** (p < 0.01) - Highly significant")
        elif p_value < 0.05:
            report.append("  Significance: ** (p < 0.05) - Significant")
        elif p_value < 0.10:
            report.append("  Significance: * (p < 0.10) - Marginally significant")
        else:
            report.append("  Significance: n.s. (p ≥ 0.10) - Not significant")
        report.append("")

        report.append(f"## Result: {winner}")
        report.append(f"## Recommendation: {recommendation}")
        report.append("")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="A/B test workflow variants")
    parser.add_argument(
        '--variant-a',
        required=True,
        help='Workflow ID for variant A'
    )
    parser.add_argument(
        '--variant-b',
        required=True,
        help='Workflow ID for variant B'
    )
    parser.add_argument(
        '--metric',
        default='tokens_used',
        help='Metric to compare (default: tokens_used)'
    )
    parser.add_argument(
        '--higher-is-better',
        action='store_true',
        help='Higher values are better (default: lower is better)'
    )
    parser.add_argument(
        '--output',
        help='Output file (default: stdout)'
    )

    args = parser.parse_args()

    # Find metrics file
    metrics_file = Path('docs/memory/workflow_metrics.jsonl')

    analyzer = ABTestAnalyzer(metrics_file)
    report = analyzer.compare_variants(
        args.variant_a,
        args.variant_b,
        args.metric,
        lower_is_better=not args.higher_is_better
    )

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()
