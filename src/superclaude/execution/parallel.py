"""
Parallel Execution Engine - Automatic Parallelization

Analyzes task dependencies and executes independent operations
concurrently for maximum speed.

Key features:
- Dependency graph construction
- Automatic parallel group detection
- Concurrent execution with ThreadPoolExecutor
- Result aggregation and error handling
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set


class TaskStatus(Enum):
    """Task execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Single executable task"""

    id: str
    description: str
    execute: Callable
    depends_on: List[str]  # Task IDs this depends on
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None

    def can_execute(self, completed_tasks: Set[str]) -> bool:
        """Check if all dependencies are satisfied"""
        return all(dep in completed_tasks for dep in self.depends_on)


@dataclass
class ParallelGroup:
    """Group of tasks that can execute in parallel"""

    group_id: int
    tasks: List[Task]
    dependencies: Set[str]  # External task IDs this group depends on

    def __repr__(self) -> str:
        return f"Group {self.group_id}: {len(self.tasks)} tasks"


@dataclass
class ExecutionPlan:
    """Complete execution plan with parallelization strategy"""

    groups: List[ParallelGroup]
    total_tasks: int
    sequential_time_estimate: float
    parallel_time_estimate: float
    speedup: float

    def __repr__(self) -> str:
        return (
            f"Execution Plan:\n"
            f"  Total tasks: {self.total_tasks}\n"
            f"  Parallel groups: {len(self.groups)}\n"
            f"  Sequential time: {self.sequential_time_estimate:.1f}s\n"
            f"  Parallel time: {self.parallel_time_estimate:.1f}s\n"
            f"  Speedup: {self.speedup:.1f}x"
        )


class ParallelExecutor:
    """
    Automatic Parallel Execution Engine

    Analyzes task dependencies and executes independent operations
    concurrently for maximum performance.

    Example:
        executor = ParallelExecutor(max_workers=10)

        tasks = [
            Task("read1", "Read file1.py", lambda: read_file("file1.py"), []),
            Task("read2", "Read file2.py", lambda: read_file("file2.py"), []),
            Task("analyze", "Analyze", lambda: analyze(), ["read1", "read2"]),
        ]

        plan = executor.plan(tasks)
        results = executor.execute(plan)
    """

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers

    def plan(self, tasks: List[Task]) -> ExecutionPlan:
        """
        Create execution plan with automatic parallelization

        Builds dependency graph and identifies parallel groups.
        """

        print(f"⚡ Parallel Executor: Planning {len(tasks)} tasks")
        print("=" * 60)

        # Find parallel groups using topological sort
        groups = []
        completed = set()
        group_id = 0

        while len(completed) < len(tasks):
            # Find tasks that can execute now (dependencies met)
            ready = [
                task
                for task in tasks
                if task.id not in completed and task.can_execute(completed)
            ]

            if not ready:
                # Circular dependency or logic error
                remaining = [t.id for t in tasks if t.id not in completed]
                raise ValueError(f"Circular dependency detected: {remaining}")

            # Create parallel group
            group = ParallelGroup(
                group_id=group_id,
                tasks=ready,
                dependencies=set().union(*[set(t.depends_on) for t in ready]),
            )
            groups.append(group)

            # Mark as completed for dependency resolution
            completed.update(task.id for task in ready)
            group_id += 1

        # Calculate time estimates
        # Assume each task takes 1 second (placeholder)
        task_time = 1.0

        sequential_time = len(tasks) * task_time

        # Parallel time = sum of slowest task in each group
        parallel_time = sum(
            max(1, len(group.tasks) // self.max_workers) * task_time for group in groups
        )

        speedup = sequential_time / parallel_time if parallel_time > 0 else 1.0

        plan = ExecutionPlan(
            groups=groups,
            total_tasks=len(tasks),
            sequential_time_estimate=sequential_time,
            parallel_time_estimate=parallel_time,
            speedup=speedup,
        )

        print(plan)
        print("=" * 60)

        return plan

    def execute(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Execute plan with parallel groups

        Returns dict of task_id -> result
        """

        print(f"\n🚀 Executing {plan.total_tasks} tasks in {len(plan.groups)} groups")
        print("=" * 60)

        results = {}
        start_time = time.time()

        for group in plan.groups:
            print(f"\n📦 {group}")
            group_start = time.time()

            # Execute group in parallel
            group_results = self._execute_group(group)
            results.update(group_results)

            group_time = time.time() - group_start
            print(f"   Completed in {group_time:.2f}s")

        total_time = time.time() - start_time
        actual_speedup = plan.sequential_time_estimate / total_time

        print("\n" + "=" * 60)
        print(f"✅ All tasks completed in {total_time:.2f}s")
        print(f"   Estimated: {plan.parallel_time_estimate:.2f}s")
        print(f"   Actual speedup: {actual_speedup:.1f}x")
        print("=" * 60)

        return results

    def _execute_group(self, group: ParallelGroup) -> Dict[str, Any]:
        """Execute single parallel group"""

        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks in group
            future_to_task = {
                executor.submit(task.execute): task for task in group.tasks
            }

            # Collect results as they complete
            for future in as_completed(future_to_task):
                task = future_to_task[future]

                try:
                    result = future.result()
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    results[task.id] = result

                    print(f"   ✅ {task.description}")

                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = e
                    results[task.id] = None

                    print(f"   ❌ {task.description}: {e}")

        return results


# Convenience functions for common patterns


def parallel_file_operations(files: List[str], operation: Callable) -> List[Any]:
    """
    Execute operation on multiple files in parallel

    Example:
        results = parallel_file_operations(
            ["file1.py", "file2.py", "file3.py"],
            lambda f: read_file(f)
        )
    """

    executor = ParallelExecutor()

    tasks = [
        Task(
            id=f"op_{i}",
            description=f"Process {file}",
            execute=lambda f=file: operation(f),
            depends_on=[],
        )
        for i, file in enumerate(files)
    ]

    plan = executor.plan(tasks)
    results = executor.execute(plan)

    return [results[task.id] for task in tasks]


def should_parallelize(items: List[Any], threshold: int = 3) -> bool:
    """
    Auto-trigger for parallel execution

    Returns True if number of items exceeds threshold.
    """
    return len(items) >= threshold


# Example usage patterns


def example_parallel_read():
    """Example: Parallel file reading"""

    files = ["file1.py", "file2.py", "file3.py", "file4.py", "file5.py"]

    executor = ParallelExecutor()

    tasks = [
        Task(
            id=f"read_{i}",
            description=f"Read {file}",
            execute=lambda f=file: f"Content of {f}",  # Placeholder
            depends_on=[],
        )
        for i, file in enumerate(files)
    ]

    plan = executor.plan(tasks)
    results = executor.execute(plan)

    return results


def example_dependent_tasks():
    """Example: Tasks with dependencies"""

    executor = ParallelExecutor()

    tasks = [
        # Wave 1: Independent reads (parallel)
        Task("read1", "Read config.py", lambda: "config", []),
        Task("read2", "Read utils.py", lambda: "utils", []),
        Task("read3", "Read main.py", lambda: "main", []),
        # Wave 2: Analysis (depends on reads)
        Task(
            "analyze", "Analyze code", lambda: "analysis", ["read1", "read2", "read3"]
        ),
        # Wave 3: Generate report (depends on analysis)
        Task("report", "Generate report", lambda: "report", ["analyze"]),
    ]

    plan = executor.plan(tasks)
    # Expected: 3 groups (Wave 1: 3 parallel, Wave 2: 1, Wave 3: 1)

    results = executor.execute(plan)

    return results


if __name__ == "__main__":
    print("Example 1: Parallel file reading")
    example_parallel_read()

    print("\n" * 2)

    print("Example 2: Dependent tasks")
    example_dependent_tasks()
