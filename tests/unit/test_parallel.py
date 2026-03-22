"""
Unit tests for ParallelExecutor

Tests automatic parallelization, dependency resolution,
and concurrent execution capabilities.
"""

import time

import pytest

from superclaude.execution.parallel import (
    ExecutionPlan,
    ParallelExecutor,
    ParallelGroup,
    Task,
    TaskStatus,
    parallel_file_operations,
    should_parallelize,
)


class TestTask:
    """Test suite for Task dataclass"""

    def test_task_creation(self):
        """Test basic task creation"""
        task = Task(
            id="t1",
            description="Test task",
            execute=lambda: "result",
            depends_on=[],
        )
        assert task.id == "t1"
        assert task.status == TaskStatus.PENDING
        assert task.result is None
        assert task.error is None

    def test_task_can_execute_no_deps(self):
        """Task with no dependencies can always execute"""
        task = Task(id="t1", description="No deps", execute=lambda: None, depends_on=[])
        assert task.can_execute(set()) is True
        assert task.can_execute({"other"}) is True

    def test_task_can_execute_with_deps_met(self):
        """Task can execute when all dependencies are completed"""
        task = Task(
            id="t2", description="With deps", execute=lambda: None, depends_on=["t1"]
        )
        assert task.can_execute({"t1"}) is True
        assert task.can_execute({"t1", "t0"}) is True

    def test_task_cannot_execute_deps_unmet(self):
        """Task cannot execute when dependencies are not met"""
        task = Task(
            id="t2",
            description="With deps",
            execute=lambda: None,
            depends_on=["t1", "t3"],
        )
        assert task.can_execute(set()) is False
        assert task.can_execute({"t1"}) is False  # t3 missing

    def test_task_can_execute_all_deps_met(self):
        """Task can execute when all multiple dependencies are met"""
        task = Task(
            id="t3",
            description="Multi deps",
            execute=lambda: None,
            depends_on=["t1", "t2"],
        )
        assert task.can_execute({"t1", "t2"}) is True


class TestParallelExecutor:
    """Test suite for ParallelExecutor class"""

    def test_plan_independent_tasks(self):
        """Independent tasks should be in a single parallel group"""
        executor = ParallelExecutor(max_workers=5)
        tasks = [
            Task(id=f"t{i}", description=f"Task {i}", execute=lambda: i, depends_on=[])
            for i in range(5)
        ]

        plan = executor.plan(tasks)

        assert plan.total_tasks == 5
        assert len(plan.groups) == 1  # All independent = 1 group
        assert len(plan.groups[0].tasks) == 5

    def test_plan_sequential_tasks(self):
        """Tasks with chain dependencies should be in separate groups"""
        executor = ParallelExecutor()
        tasks = [
            Task(id="t0", description="First", execute=lambda: 0, depends_on=[]),
            Task(id="t1", description="Second", execute=lambda: 1, depends_on=["t0"]),
            Task(id="t2", description="Third", execute=lambda: 2, depends_on=["t1"]),
        ]

        plan = executor.plan(tasks)

        assert plan.total_tasks == 3
        assert len(plan.groups) == 3  # Each depends on previous

    def test_plan_mixed_dependencies(self):
        """Wave-Checkpoint-Wave pattern should create correct groups"""
        executor = ParallelExecutor()
        tasks = [
            # Wave 1: independent reads
            Task(id="read1", description="Read 1", execute=lambda: "r1", depends_on=[]),
            Task(id="read2", description="Read 2", execute=lambda: "r2", depends_on=[]),
            Task(id="read3", description="Read 3", execute=lambda: "r3", depends_on=[]),
            # Wave 2: depends on all reads
            Task(
                id="analyze",
                description="Analyze",
                execute=lambda: "a",
                depends_on=["read1", "read2", "read3"],
            ),
            # Wave 3: depends on analysis
            Task(
                id="report",
                description="Report",
                execute=lambda: "rp",
                depends_on=["analyze"],
            ),
        ]

        plan = executor.plan(tasks)

        assert len(plan.groups) == 3
        assert len(plan.groups[0].tasks) == 3  # 3 parallel reads
        assert len(plan.groups[1].tasks) == 1  # analyze
        assert len(plan.groups[2].tasks) == 1  # report

    def test_plan_speedup_calculation(self):
        """Speedup should be > 1 for parallelizable tasks"""
        executor = ParallelExecutor()
        tasks = [
            Task(id=f"t{i}", description=f"Task {i}", execute=lambda: i, depends_on=[])
            for i in range(10)
        ]

        plan = executor.plan(tasks)

        assert plan.speedup >= 1.0
        assert plan.sequential_time_estimate > plan.parallel_time_estimate

    def test_plan_circular_dependency_detection(self):
        """Circular dependencies should raise ValueError"""
        executor = ParallelExecutor()
        tasks = [
            Task(id="a", description="A", execute=lambda: None, depends_on=["b"]),
            Task(id="b", description="B", execute=lambda: None, depends_on=["a"]),
        ]

        with pytest.raises(ValueError, match="Circular dependency"):
            executor.plan(tasks)

    def test_execute_returns_results(self):
        """Execute should return dict of task_id -> result"""
        executor = ParallelExecutor()
        tasks = [
            Task(id="t0", description="Return 42", execute=lambda: 42, depends_on=[]),
            Task(
                id="t1", description="Return hello", execute=lambda: "hello", depends_on=[]
            ),
        ]

        plan = executor.plan(tasks)
        results = executor.execute(plan)

        assert results["t0"] == 42
        assert results["t1"] == "hello"

    def test_execute_handles_failures(self):
        """Failed tasks should have None result and error set"""
        executor = ParallelExecutor()

        def failing_task():
            raise RuntimeError("Task failed!")

        tasks = [
            Task(id="good", description="Good", execute=lambda: "ok", depends_on=[]),
            Task(id="bad", description="Bad", execute=failing_task, depends_on=[]),
        ]

        plan = executor.plan(tasks)
        results = executor.execute(plan)

        assert results["good"] == "ok"
        assert results["bad"] is None

        # Check task error was recorded
        bad_task = [t for t in tasks if t.id == "bad"][0]
        assert bad_task.status == TaskStatus.FAILED
        assert bad_task.error is not None

    def test_execute_respects_dependency_order(self):
        """Dependent tasks should run after their dependencies"""
        execution_order = []

        def make_task(name):
            def fn():
                execution_order.append(name)
                return name

            return fn

        executor = ParallelExecutor(max_workers=1)  # Force sequential within groups
        tasks = [
            Task(id="first", description="First", execute=make_task("first"), depends_on=[]),
            Task(
                id="second",
                description="Second",
                execute=make_task("second"),
                depends_on=["first"],
            ),
        ]

        plan = executor.plan(tasks)
        executor.execute(plan)

        assert execution_order.index("first") < execution_order.index("second")

    def test_execute_parallel_speedup(self):
        """Parallel execution should be faster than sequential"""
        executor = ParallelExecutor(max_workers=5)

        def slow_task(n):
            def fn():
                time.sleep(0.05)
                return n

            return fn

        tasks = [
            Task(
                id=f"t{i}",
                description=f"Task {i}",
                execute=slow_task(i),
                depends_on=[],
            )
            for i in range(5)
        ]

        plan = executor.plan(tasks)

        start = time.time()
        results = executor.execute(plan)
        elapsed = time.time() - start

        # 5 tasks x 0.05s = 0.25s sequential. Parallel should be ~0.05s
        assert elapsed < 0.20  # Allow generous margin
        assert len(results) == 5


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_should_parallelize_above_threshold(self):
        """Items above threshold should trigger parallelization"""
        assert should_parallelize([1, 2, 3]) is True
        assert should_parallelize([1, 2, 3, 4]) is True

    def test_should_parallelize_below_threshold(self):
        """Items below threshold should not trigger parallelization"""
        assert should_parallelize([1]) is False
        assert should_parallelize([1, 2]) is False

    def test_should_parallelize_custom_threshold(self):
        """Custom threshold should be respected"""
        assert should_parallelize([1, 2], threshold=2) is True
        assert should_parallelize([1], threshold=2) is False

    def test_parallel_file_operations(self):
        """parallel_file_operations should apply operation to all files"""
        results = parallel_file_operations(
            ["a.py", "b.py", "c.py"],
            lambda f: f.upper(),
        )

        assert results == ["A.PY", "B.PY", "C.PY"]
