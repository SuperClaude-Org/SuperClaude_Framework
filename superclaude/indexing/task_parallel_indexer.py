"""
Task Tool-based Parallel Repository Indexer

Claude Code の Task tool を使った真の並列実行
GIL の制約なし、API レベルでの並列処理

Features:
- Multiple Task agents running in parallel
- No GIL limitations
- Real 3-5x speedup expected
- Agent specialization for each task type

Usage:
    # This file provides the prompt templates for Task tool
    # Actual execution happens via Claude Code Task tool

Design:
    1. Create 5 parallel Task tool calls in single message
    2. Each Task analyzes different directory
    3. Claude Code executes them in parallel
    4. Collect and merge results
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import json


@dataclass
class TaskDefinition:
    """Definition for a single Task tool call"""

    task_id: str
    agent_type: str  # e.g., "system-architect", "technical-writer"
    description: str
    prompt: str  # Full prompt for the Task

    def to_task_prompt(self) -> Dict:
        """Convert to Task tool parameters"""
        return {
            "subagent_type": self.agent_type,
            "description": self.description,
            "prompt": self.prompt
        }


class TaskParallelIndexer:
    """
    Task tool-based parallel indexer

    This class generates prompts for parallel Task execution
    The actual parallelization happens at Claude Code level
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()

    def create_parallel_tasks(self) -> List[TaskDefinition]:
        """
        Create parallel task definitions

        Returns list of TaskDefinition that should be executed
        as parallel Task tool calls in a SINGLE message
        """

        tasks = []

        # Task 1: Code Structure Analysis
        tasks.append(TaskDefinition(
            task_id="code_structure",
            agent_type="Explore",  # Use Explore agent for fast scanning
            description="Analyze code structure",
            prompt=self._create_code_analysis_prompt()
        ))

        # Task 2: Documentation Analysis
        tasks.append(TaskDefinition(
            task_id="documentation",
            agent_type="Explore",  # Use Explore agent
            description="Analyze documentation",
            prompt=self._create_docs_analysis_prompt()
        ))

        # Task 3: Configuration Analysis
        tasks.append(TaskDefinition(
            task_id="configuration",
            agent_type="Explore",  # Use Explore agent
            description="Analyze configuration files",
            prompt=self._create_config_analysis_prompt()
        ))

        # Task 4: Test Analysis
        tasks.append(TaskDefinition(
            task_id="tests",
            agent_type="Explore",  # Use Explore agent
            description="Analyze test structure",
            prompt=self._create_test_analysis_prompt()
        ))

        # Task 5: Scripts Analysis
        tasks.append(TaskDefinition(
            task_id="scripts",
            agent_type="Explore",  # Use Explore agent
            description="Analyze scripts and utilities",
            prompt=self._create_scripts_analysis_prompt()
        ))

        return tasks

    def _create_code_analysis_prompt(self) -> str:
        """Generate prompt for code structure analysis"""
        return f"""Analyze the code structure of this repository: {self.repo_path}

Task: Find and analyze all source code directories (src/, lib/, superclaude/, setup/, apps/, packages/)

For each directory found:
1. List all Python/JavaScript/TypeScript files
2. Identify the purpose/responsibility
3. Note key files and entry points
4. Detect any organizational issues

Output format (JSON):
{{
    "directories": [
        {{
            "path": "relative/path",
            "purpose": "description",
            "file_count": 10,
            "key_files": ["file1.py", "file2.py"],
            "issues": ["redundant nesting", "orphaned files"]
        }}
    ],
    "total_files": 100
}}

Use Glob and Grep tools to search efficiently.
Be thorough: "very thorough" level.
"""

    def _create_docs_analysis_prompt(self) -> str:
        """Generate prompt for documentation analysis"""
        return f"""Analyze the documentation of this repository: {self.repo_path}

Task: Find and analyze all documentation (docs/, README*, *.md files)

For each documentation section:
1. List all markdown/rst files
2. Assess documentation coverage
3. Identify missing documentation
4. Detect redundant/duplicate docs

Output format (JSON):
{{
    "directories": [
        {{
            "path": "docs/",
            "purpose": "User/developer documentation",
            "file_count": 50,
            "coverage": "good|partial|poor",
            "missing": ["API reference", "Architecture guide"],
            "duplicates": ["README vs docs/README"]
        }}
    ],
    "root_docs": ["README.md", "CLAUDE.md"],
    "total_files": 75
}}

Use Glob to find all .md files.
Check for duplicate content patterns.
"""

    def _create_config_analysis_prompt(self) -> str:
        """Generate prompt for configuration analysis"""
        return f"""Analyze the configuration files of this repository: {self.repo_path}

Task: Find and analyze all configuration files (.toml, .yaml, .yml, .json, .ini, .cfg)

For each config file:
1. Identify purpose (build, deps, CI/CD, etc.)
2. Note importance level
3. Check for issues (deprecated, unused)

Output format (JSON):
{{
    "config_files": [
        {{
            "path": "pyproject.toml",
            "type": "python_project",
            "importance": "critical",
            "issues": []
        }}
    ],
    "total_files": 15
}}

Use Glob with appropriate patterns.
"""

    def _create_test_analysis_prompt(self) -> str:
        """Generate prompt for test analysis"""
        return f"""Analyze the test structure of this repository: {self.repo_path}

Task: Find and analyze all tests (tests/, __tests__/, *.test.*, *.spec.*)

For each test directory/file:
1. Count test files
2. Identify test types (unit, integration, performance)
3. Assess coverage (if pytest/coverage data available)

Output format (JSON):
{{
    "test_directories": [
        {{
            "path": "tests/",
            "test_count": 20,
            "types": ["unit", "integration", "benchmark"],
            "coverage": "unknown"
        }}
    ],
    "total_tests": 25
}}

Use Glob to find test files.
"""

    def _create_scripts_analysis_prompt(self) -> str:
        """Generate prompt for scripts analysis"""
        return f"""Analyze the scripts and utilities of this repository: {self.repo_path}

Task: Find and analyze all scripts (scripts/, bin/, tools/, *.sh, *.bash)

For each script:
1. Identify purpose
2. Note language (bash, python, etc.)
3. Check if documented

Output format (JSON):
{{
    "script_directories": [
        {{
            "path": "scripts/",
            "script_count": 5,
            "purposes": ["build", "deploy", "utility"],
            "documented": true
        }}
    ],
    "total_scripts": 10
}}

Use Glob to find script files.
"""

    def generate_execution_instructions(self) -> str:
        """
        Generate instructions for executing tasks in parallel

        This returns a prompt that explains HOW to execute
        the parallel tasks using Task tool
        """

        tasks = self.create_parallel_tasks()

        instructions = [
            "# Parallel Repository Indexing Execution Plan",
            "",
            "## Objective",
            f"Create comprehensive repository index for: {self.repo_path}",
            "",
            "## Execution Strategy",
            "",
            "Execute the following 5 tasks IN PARALLEL using Task tool.",
            "IMPORTANT: All 5 Task tool calls must be in a SINGLE message for parallel execution.",
            "",
            "## Tasks to Execute (Parallel)",
            ""
        ]

        for i, task in enumerate(tasks, 1):
            instructions.extend([
                f"### Task {i}: {task.description}",
                f"- Agent: {task.agent_type}",
                f"- ID: {task.task_id}",
                "",
                "**Prompt**:",
                "```",
                task.prompt,
                "```",
                ""
            ])

        instructions.extend([
            "## Expected Output",
            "",
            "Each task will return JSON with analysis results.",
            "After all tasks complete, merge the results into a single repository index.",
            "",
            "## Performance Expectations",
            "",
            "- Sequential execution: ~300ms",
            "- Parallel execution: ~60-100ms (3-5x faster)",
            "- No GIL limitations (API-level parallelism)",
            ""
        ])

        return "\n".join(instructions)

    def save_execution_plan(self, output_path: Path):
        """Save execution plan to file"""
        instructions = self.generate_execution_instructions()
        output_path.write_text(instructions)
        print(f"📝 Execution plan saved to: {output_path}")


def generate_task_tool_calls_code() -> str:
    """
    Generate Python code showing how to make parallel Task tool calls

    This is example code for Claude Code to execute
    """

    code = '''
# Example: How to execute parallel tasks using Task tool
# This should be executed by Claude Code, not by Python directly

from pathlib import Path

repo_path = Path(".")

# Define 5 parallel tasks
tasks = [
    # Task 1: Code Structure
    {
        "subagent_type": "Explore",
        "description": "Analyze code structure",
        "prompt": """Analyze code in superclaude/, setup/ directories.
        Use Glob to find all .py files.
        Output: JSON with directory structure."""
    },

    # Task 2: Documentation
    {
        "subagent_type": "Explore",
        "description": "Analyze documentation",
        "prompt": """Analyze docs/ and root .md files.
        Use Glob to find all .md files.
        Output: JSON with documentation structure."""
    },

    # Task 3: Configuration
    {
        "subagent_type": "Explore",
        "description": "Analyze configuration",
        "prompt": """Find all .toml, .yaml, .json config files.
        Output: JSON with config file list."""
    },

    # Task 4: Tests
    {
        "subagent_type": "Explore",
        "description": "Analyze tests",
        "prompt": """Analyze tests/ directory.
        Output: JSON with test structure."""
    },

    # Task 5: Scripts
    {
        "subagent_type": "Explore",
        "description": "Analyze scripts",
        "prompt": """Analyze scripts/, bin/ directories.
        Output: JSON with script list."""
    },
]

# CRITICAL: Execute all 5 Task tool calls in SINGLE message
# This enables true parallel execution at Claude Code level

# Pseudo-code for Claude Code execution:
for task in tasks:
    Task(
        subagent_type=task["subagent_type"],
        description=task["description"],
        prompt=task["prompt"]
    )
    # All Task calls in same message = parallel execution

# Results will come back as each task completes
# Merge results into final repository index
'''

    return code


if __name__ == "__main__":
    """Generate execution plan for Task tool parallel indexing"""

    repo_path = Path(".")
    indexer = TaskParallelIndexer(repo_path)

    # Save execution plan
    plan_path = repo_path / "PARALLEL_INDEXING_PLAN.md"
    indexer.save_execution_plan(plan_path)

    print("\n" + "="*80)
    print("✅ Task Tool Parallel Indexing Plan Generated")
    print("="*80)
    print(f"\nExecution plan: {plan_path}")
    print("\nNext steps:")
    print("1. Read the execution plan")
    print("2. Execute all 5 Task tool calls in SINGLE message")
    print("3. Wait for parallel execution to complete")
    print("4. Merge results into PROJECT_INDEX.md")
    print("\nExpected speedup: 3-5x faster than sequential")
    print("="*80 + "\n")
