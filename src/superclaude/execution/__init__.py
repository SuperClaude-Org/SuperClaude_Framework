"""
SuperClaude Execution Engine

Integrates three execution engines:
1. Reflection Engine: Think × 3 before execution
2. Parallel Engine: Execute at maximum speed
3. Self-Correction Engine: Learn from mistakes

Usage:
    from superclaude.execution import intelligent_execute

    result = intelligent_execute(
        task="Create user authentication system",
        context={"project_index": "...", "git_status": "..."},
        operations=[op1, op2, op3]
    )
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from .reflection import ReflectionEngine, ConfidenceScore, reflect_before_execution
from .parallel import ParallelExecutor, Task, ExecutionPlan, should_parallelize
from .self_correction import SelfCorrectionEngine, RootCause, learn_from_failure

__all__ = [
    "intelligent_execute",
    "ReflectionEngine",
    "ParallelExecutor",
    "SelfCorrectionEngine",
    "ConfidenceScore",
    "ExecutionPlan",
    "RootCause",
]


def intelligent_execute(
    task: str,
    operations: List[Callable],
    context: Optional[Dict[str, Any]] = None,
    repo_path: Optional[Path] = None,
    auto_correct: bool = True
) -> Dict[str, Any]:
    """
    Intelligent Task Execution with Reflection, Parallelization, and Self-Correction

    Workflow:
    1. Reflection × 3: Analyze task before execution
    2. Plan: Create parallel execution plan
    3. Execute: Run operations at maximum speed
    4. Validate: Check results and learn from failures

    Args:
        task: Task description
        operations: List of callables to execute
        context: Optional context (project index, git status, etc.)
        repo_path: Repository path (defaults to cwd)
        auto_correct: Enable automatic self-correction

    Returns:
        Dict with execution results and metadata
    """

    if repo_path is None:
        repo_path = Path.cwd()

    print("\n" + "=" * 70)
    print("🧠 INTELLIGENT EXECUTION ENGINE")
    print("=" * 70)
    print(f"Task: {task}")
    print(f"Operations: {len(operations)}")
    print("=" * 70)

    # Phase 1: Reflection × 3
    print("\n📋 PHASE 1: REFLECTION × 3")
    print("-" * 70)

    reflection_engine = ReflectionEngine(repo_path)
    confidence = reflection_engine.reflect(task, context)

    if not confidence.should_proceed:
        print("\n🔴 EXECUTION BLOCKED")
        print(f"Confidence too low: {confidence.confidence:.0%} < 70%")
        print("\nBlockers:")
        for blocker in confidence.blockers:
            print(f"  ❌ {blocker}")
        print("\nRecommendations:")
        for rec in confidence.recommendations:
            print(f"  💡 {rec}")

        return {
            "status": "blocked",
            "confidence": confidence.confidence,
            "blockers": confidence.blockers,
            "recommendations": confidence.recommendations
        }

    print(f"\n✅ HIGH CONFIDENCE ({confidence.confidence:.0%}) - PROCEEDING")

    # Phase 2: Parallel Planning
    print("\n📦 PHASE 2: PARALLEL PLANNING")
    print("-" * 70)

    executor = ParallelExecutor(max_workers=10)

    # Convert operations to Tasks
    tasks = [
        Task(
            id=f"task_{i}",
            description=f"Operation {i+1}",
            execute=op,
            depends_on=[]  # Assume independent for now (can enhance later)
        )
        for i, op in enumerate(operations)
    ]

    plan = executor.plan(tasks)

    # Phase 3: Execution
    print("\n⚡ PHASE 3: PARALLEL EXECUTION")
    print("-" * 70)

    try:
        results = executor.execute(plan)

        # Check for failures
        failures = [
            (task_id, None)  # Placeholder - need actual error
            for task_id, result in results.items()
            if result is None
        ]

        if failures and auto_correct:
            # Phase 4: Self-Correction
            print("\n🔍 PHASE 4: SELF-CORRECTION")
            print("-" * 70)

            correction_engine = SelfCorrectionEngine(repo_path)

            for task_id, error in failures:
                failure_info = {
                    "type": "execution_error",
                    "error": "Operation returned None",
                    "task_id": task_id
                }

                root_cause = correction_engine.analyze_root_cause(task, failure_info)
                correction_engine.learn_and_prevent(task, failure_info, root_cause)

        execution_status = "success" if not failures else "partial_failure"

        print("\n" + "=" * 70)
        print(f"✅ EXECUTION COMPLETE: {execution_status.upper()}")
        print("=" * 70)

        return {
            "status": execution_status,
            "confidence": confidence.confidence,
            "results": results,
            "failures": len(failures),
            "speedup": plan.speedup
        }

    except Exception as e:
        # Unhandled exception - learn from it
        print(f"\n❌ EXECUTION FAILED: {e}")

        if auto_correct:
            print("\n🔍 ANALYZING FAILURE...")

            correction_engine = SelfCorrectionEngine(repo_path)

            failure_info = {
                "type": "exception",
                "error": str(e),
                "exception": e
            }

            root_cause = correction_engine.analyze_root_cause(task, failure_info)
            correction_engine.learn_and_prevent(task, failure_info, root_cause)

        print("=" * 70)

        return {
            "status": "failed",
            "error": str(e),
            "confidence": confidence.confidence
        }


# Convenience functions

def quick_execute(operations: List[Callable]) -> List[Any]:
    """
    Quick parallel execution without reflection

    Use for simple, low-risk operations.
    """
    executor = ParallelExecutor()

    tasks = [
        Task(id=f"op_{i}", description=f"Op {i}", execute=op, depends_on=[])
        for i, op in enumerate(operations)
    ]

    plan = executor.plan(tasks)
    results = executor.execute(plan)

    return [results[task.id] for task in tasks]


def safe_execute(task: str, operation: Callable, context: Optional[Dict] = None) -> Any:
    """
    Safe single operation execution with reflection

    Blocks if confidence <70%.
    """
    result = intelligent_execute(task, [operation], context)

    if result["status"] == "blocked":
        raise RuntimeError(f"Execution blocked: {result['blockers']}")

    if result["status"] == "failed":
        raise RuntimeError(f"Execution failed: {result.get('error')}")

    return result["results"]["task_0"]
