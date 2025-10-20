#!/usr/bin/env python3
"""
Demo: Intelligent Execution Engine

Demonstrates:
1. Reflection × 3 before execution
2. Parallel execution planning
3. Automatic self-correction

Usage:
    python scripts/demo_intelligent_execution.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from superclaude.core import intelligent_execute, quick_execute, safe_execute
import time


def demo_high_confidence_execution():
    """Demo 1: High confidence task execution"""

    print("\n" + "=" * 80)
    print("DEMO 1: High Confidence Execution")
    print("=" * 80)

    # Define operations
    def read_file_1():
        time.sleep(0.1)
        return "Content of file1.py"

    def read_file_2():
        time.sleep(0.1)
        return "Content of file2.py"

    def read_file_3():
        time.sleep(0.1)
        return "Content of file3.py"

    def analyze_files():
        time.sleep(0.2)
        return "Analysis complete"

    # Execute with high confidence
    result = intelligent_execute(
        task="Read and analyze three validation files: file1.py, file2.py, file3.py",
        operations=[read_file_1, read_file_2, read_file_3, analyze_files],
        context={
            "project_index": "Loaded project structure",
            "current_branch": "main",
            "git_status": "clean"
        }
    )

    print(f"\nResult: {result['status']}")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Speedup: {result.get('speedup', 0):.1f}x")


def demo_low_confidence_blocked():
    """Demo 2: Low confidence blocks execution"""

    print("\n" + "=" * 80)
    print("DEMO 2: Low Confidence Blocked")
    print("=" * 80)

    result = intelligent_execute(
        task="Do something",  # Vague task
        operations=[lambda: "result"],
        context=None  # No context
    )

    print(f"\nResult: {result['status']}")
    print(f"Confidence: {result['confidence']:.0%}")

    if result['status'] == 'blocked':
        print("\nBlockers:")
        for blocker in result['blockers']:
            print(f"  ❌ {blocker}")

        print("\nRecommendations:")
        for rec in result['recommendations']:
            print(f"  💡 {rec}")


def demo_self_correction():
    """Demo 3: Self-correction learns from failure"""

    print("\n" + "=" * 80)
    print("DEMO 3: Self-Correction Learning")
    print("=" * 80)

    # Operation that fails
    def validate_form():
        raise ValueError("Missing required field: email")

    result = intelligent_execute(
        task="Validate user registration form with email field check",
        operations=[validate_form],
        context={"project_index": "Loaded"},
        auto_correct=True
    )

    print(f"\nResult: {result['status']}")
    print(f"Error: {result.get('error', 'N/A')}")

    # Check reflexion memory
    reflexion_file = Path.cwd() / "docs" / "memory" / "reflexion.json"
    if reflexion_file.exists():
        import json
        with open(reflexion_file) as f:
            data = json.load(f)

        print(f"\nLearning captured:")
        print(f"  Mistakes recorded: {len(data.get('mistakes', []))}")
        print(f"  Prevention rules: {len(data.get('prevention_rules', []))}")

        if data.get('prevention_rules'):
            print("\n  Latest prevention rule:")
            print(f"    📝 {data['prevention_rules'][-1]}")


def demo_quick_execution():
    """Demo 4: Quick execution without reflection"""

    print("\n" + "=" * 80)
    print("DEMO 4: Quick Execution (No Reflection)")
    print("=" * 80)

    ops = [
        lambda: "Task 1 complete",
        lambda: "Task 2 complete",
        lambda: "Task 3 complete",
    ]

    start = time.time()
    results = quick_execute(ops)
    elapsed = time.time() - start

    print(f"\nResults: {results}")
    print(f"Time: {elapsed:.3f}s")
    print("✅ No reflection overhead - fastest execution")


def demo_parallel_speedup():
    """Demo 5: Parallel execution speedup comparison"""

    print("\n" + "=" * 80)
    print("DEMO 5: Parallel Speedup Demonstration")
    print("=" * 80)

    # Create 10 slow operations
    def slow_op(i):
        time.sleep(0.1)
        return f"Operation {i} complete"

    ops = [lambda i=i: slow_op(i) for i in range(10)]

    # Sequential time estimate
    sequential_time = 10 * 0.1  # 1.0s

    print(f"Sequential time (estimated): {sequential_time:.1f}s")
    print(f"Operations: {len(ops)}")

    # Execute in parallel
    start = time.time()

    result = intelligent_execute(
        task="Process 10 files in parallel for validation and security checks",
        operations=ops,
        context={"project_index": "Loaded"}
    )

    elapsed = time.time() - start

    print(f"\nParallel execution time: {elapsed:.2f}s")
    print(f"Theoretical speedup: {sequential_time / elapsed:.1f}x")
    print(f"Reported speedup: {result.get('speedup', 0):.1f}x")


def main():
    print("\n" + "=" * 80)
    print("🧠 INTELLIGENT EXECUTION ENGINE - DEMONSTRATION")
    print("=" * 80)
    print("\nThis demo showcases:")
    print("  1. Reflection × 3 for confidence checking")
    print("  2. Automatic parallel execution planning")
    print("  3. Self-correction and learning from failures")
    print("  4. Quick execution mode for simple tasks")
    print("  5. Parallel speedup measurements")
    print("=" * 80)

    # Run demos
    demo_high_confidence_execution()
    demo_low_confidence_blocked()
    demo_self_correction()
    demo_quick_execution()
    demo_parallel_speedup()

    print("\n" + "=" * 80)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  ✅ Reflection prevents wrong-direction execution")
    print("  ✅ Parallel execution achieves significant speedup")
    print("  ✅ Self-correction learns from failures automatically")
    print("  ✅ Flexible modes for different use cases")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
