"""
Tests for Parallel Execution Engine

Tests automatic parallelization and execution planning.
"""

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
    """Tests for Task dataclass"""

    def test_task_creation(self):
        """Test basic task creation"""
        task = Task(
            id="test1",
            description="Test task",
            execute=lambda: "result",
            depends_on=[],
        )

        assert task.id == "test1"
        assert task.description == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.result is None
        assert task.error is None

    def test_task_can_execute_no_deps(self):
        """Test task with no dependencies can always execute"""
        task = Task(
            id="test1",
            description="Test",
            execute=lambda: None,
            depends_on=[],
        )

        assert task.can_execute(set()) is True
        assert task.can_execute({"other"}) is True

    def test_task_can_execute_with_deps(self):
        """Test task with dependencies"""
        task = Task(
            id="test1",
            description="Test",
            execute=lambda: None,
            depends_on=["dep1", "dep2"],
        )

        assert task.can_execute(set()) is False
        assert task.can_execute({"dep1"}) is False
        assert task.can_execute({"dep1", "dep2"}) is True
        assert task.can_execute({"dep1", "dep2", "dep3"}) is True

    def test_task_status_enum(self):
        """Test TaskStatus enum values"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"


class TestParallelGroup:
    """Tests for ParallelGroup dataclass"""

    def test_parallel_group_creation(self):
        """Test parallel group creation"""
        tasks = [
            Task("t1", "Task 1", lambda: None, []),
            Task("t2", "Task 2", lambda: None, []),
        ]
        group = ParallelGroup(group_id=0, tasks=tasks, dependencies=set())

        assert group.group_id == 0
        assert len(group.tasks) == 2

    def test_parallel_group_repr(self):
        """Test parallel group string representation"""
        tasks = [Task("t1", "Task 1", lambda: None, [])]
        group = ParallelGroup(group_id=1, tasks=tasks, dependencies=set())

        repr_str = repr(group)
        assert "Group 1" in repr_str
        assert "1 tasks" in repr_str


class TestExecutionPlan:
    """Tests for ExecutionPlan dataclass"""

    def test_execution_plan_creation(self):
        """Test execution plan creation"""
        plan = ExecutionPlan(
            groups=[],
            total_tasks=5,
            sequential_time_estimate=5.0,
            parallel_time_estimate=2.0,
            speedup=2.5,
        )

        assert plan.total_tasks == 5
        assert plan.speedup == 2.5

    def test_execution_plan_repr(self):
        """Test execution plan string representation"""
        plan = ExecutionPlan(
            groups=[],
            total_tasks=10,
            sequential_time_estimate=10.0,
            parallel_time_estimate=3.0,
            speedup=3.3,
        )

        repr_str = repr(plan)
        assert "Execution Plan" in repr_str
        assert "10" in repr_str
        assert "3.3x" in repr_str


class TestParallelExecutor:
    """Tests for ParallelExecutor"""

    def test_executor_creation(self):
        """Test executor creation with default workers"""
        executor = ParallelExecutor()
        assert executor.max_workers == 10

    def test_executor_custom_workers(self):
        """Test executor creation with custom workers"""
        executor = ParallelExecutor(max_workers=5)
        assert executor.max_workers == 5

    def test_plan_single_task(self):
        """Test planning with single task"""
        executor = ParallelExecutor()
        tasks = [Task("t1", "Task 1", lambda: "result", [])]

        plan = executor.plan(tasks)

        assert plan.total_tasks == 1
        assert len(plan.groups) == 1

    def test_plan_parallel_tasks(self):
        """Test planning with independent parallel tasks"""
        executor = ParallelExecutor()
        tasks = [
            Task("t1", "Task 1", lambda: "r1", []),
            Task("t2", "Task 2", lambda: "r2", []),
            Task("t3", "Task 3", lambda: "r3", []),
        ]

        plan = executor.plan(tasks)

        assert plan.total_tasks == 3
        assert len(plan.groups) == 1  # All in one group (no deps)
        assert len(plan.groups[0].tasks) == 3

    def test_plan_dependent_tasks(self):
        """Test planning with dependent tasks"""
        executor = ParallelExecutor()
        tasks = [
            Task("t1", "Task 1", lambda: "r1", []),
            Task("t2", "Task 2", lambda: "r2", []),
            Task("t3", "Depends on t1 and t2", lambda: "r3", ["t1", "t2"]),
        ]

        plan = executor.plan(tasks)

        assert plan.total_tasks == 3
        assert len(plan.groups) == 2  # Two groups: parallel then dependent

    def test_plan_sequential_chain(self):
        """Test planning with sequential chain"""
        executor = ParallelExecutor()
        tasks = [
            Task("t1", "First", lambda: "r1", []),
            Task("t2", "Second", lambda: "r2", ["t1"]),
            Task("t3", "Third", lambda: "r3", ["t2"]),
        ]

        plan = executor.plan(tasks)

        assert plan.total_tasks == 3
        assert len(plan.groups) == 3  # All sequential

    def test_plan_circular_dependency_raises(self):
        """Test planning detects circular dependencies"""
        executor = ParallelExecutor()
        tasks = [
            Task("t1", "Task 1", lambda: "r1", ["t2"]),
            Task("t2", "Task 2", lambda: "r2", ["t1"]),
        ]

        with pytest.raises(ValueError, match="Circular dependency"):
            executor.plan(tasks)

    def test_execute_single_task(self):
        """Test executing single task"""
        executor = ParallelExecutor()
        tasks = [Task("t1", "Task 1", lambda: "result", [])]

        plan = executor.plan(tasks)
        results = executor.execute(plan)

        assert "t1" in results
        assert results["t1"] == "result"

    def test_execute_parallel_tasks(self):
        """Test executing parallel tasks"""
        executor = ParallelExecutor()
        tasks = [
            Task("t1", "Task 1", lambda: "r1", []),
            Task("t2", "Task 2", lambda: "r2", []),
        ]

        plan = executor.plan(tasks)
        results = executor.execute(plan)

        assert results["t1"] == "r1"
        assert results["t2"] == "r2"

    def test_execute_handles_task_failure(self):
        """Test executing handles task failures gracefully"""
        executor = ParallelExecutor()

        def failing_task():
            raise ValueError("Intentional failure")

        tasks = [
            Task("t1", "Good task", lambda: "success", []),
            Task("t2", "Bad task", failing_task, []),
        ]

        plan = executor.plan(tasks)
        results = executor.execute(plan)

        assert results["t1"] == "success"
        assert results["t2"] is None  # Failed task returns None


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_should_parallelize_below_threshold(self):
        """Test should_parallelize returns False below threshold"""
        assert should_parallelize([1, 2]) is False
        assert should_parallelize([1]) is False
        assert should_parallelize([]) is False

    def test_should_parallelize_at_threshold(self):
        """Test should_parallelize returns True at/above threshold"""
        assert should_parallelize([1, 2, 3]) is True
        assert should_parallelize([1, 2, 3, 4, 5]) is True

    def test_should_parallelize_custom_threshold(self):
        """Test should_parallelize with custom threshold"""
        assert should_parallelize([1, 2], threshold=2) is True
        assert should_parallelize([1, 2, 3, 4], threshold=5) is False

    def test_parallel_file_operations(self):
        """Test parallel_file_operations helper"""
        files = ["file1.txt", "file2.txt"]

        results = parallel_file_operations(files, lambda f: f.upper())

        assert len(results) == 2
        assert "FILE1.TXT" in results
        assert "FILE2.TXT" in results


class TestParallelExecutorIntegration:
    """Integration tests for parallel executor"""

    def test_speedup_calculation(self):
        """Test speedup is calculated correctly"""
        executor = ParallelExecutor()
        tasks = [
            Task("t1", "Task 1", lambda: "r1", []),
            Task("t2", "Task 2", lambda: "r2", []),
            Task("t3", "Task 3", lambda: "r3", []),
        ]

        plan = executor.plan(tasks)

        assert plan.speedup > 1.0  # Should show speedup

    def test_wave_checkpoint_wave_pattern(self):
        """Test Wave -> Checkpoint -> Wave pattern"""
        executor = ParallelExecutor()

        # Wave 1: Read files (parallel)
        # Checkpoint: Analyze (depends on all reads)
        # Wave 2: Edit files (depends on analyze)
        tasks = [
            Task("read1", "Read file1", lambda: "c1", []),
            Task("read2", "Read file2", lambda: "c2", []),
            Task("read3", "Read file3", lambda: "c3", []),
            Task(
                "analyze",
                "Analyze all",
                lambda: "analyzed",
                ["read1", "read2", "read3"],
            ),
            Task("edit1", "Edit file1", lambda: "e1", ["analyze"]),
            Task("edit2", "Edit file2", lambda: "e2", ["analyze"]),
        ]

        plan = executor.plan(tasks)

        # Should have 3 groups:
        # Group 0: read1, read2, read3 (parallel)
        # Group 1: analyze
        # Group 2: edit1, edit2 (parallel)
        assert len(plan.groups) == 3
        assert len(plan.groups[0].tasks) == 3  # 3 reads
        assert len(plan.groups[1].tasks) == 1  # 1 analyze
        assert len(plan.groups[2].tasks) == 2  # 2 edits
