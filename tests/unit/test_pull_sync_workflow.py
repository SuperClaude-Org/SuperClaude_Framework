"""Regression tests for the pull-sync workflow's PR creation step."""

import os
import subprocess
from pathlib import Path
from textwrap import dedent

import pytest

WORKFLOW = (
    Path(__file__).resolve().parents[2] / ".github/workflows/pull-sync-framework.yml"
)
PERMISSION_ERROR = (
    "pull request create failed: GraphQL: GitHub Actions is not permitted "
    "to create or approve pull requests (createPullRequest)"
)


@pytest.mark.unit
@pytest.mark.parametrize("base_branch", ["master", "main"])
@pytest.mark.parametrize(
    ("status", "output", "manual_review"),
    [
        (0, "https://github.com/example/plugin/pull/1", False),
        (1, PERMISSION_ERROR, True),
        (1, "pull request create failed: GraphQL: No commits between branches", False),
        (4, "authentication required", False),
    ],
)
def test_create_sync_pull_request(tmp_path, base_branch, status, output, manual_review):
    step = WORKFLOW.read_text().split(
        "      - name: Create Pull Request for Review\n", 1
    )[1]
    assert "BASE_BRANCH: ${{ github.event.repository.default_branch }}" in step
    assert "SYNC_BRANCH: ${{ steps.commit-changes.outputs.sync-branch }}" in step
    assert "FRAMEWORK_HEAD: ${{ steps.check-updates.outputs.framework-head }}" in step
    script = dedent(step.split("        run: |\n", 1)[1])
    summary = tmp_path / "summary"
    args_file = tmp_path / "args"
    env = {
        **os.environ,
        "BASE_BRANCH": base_branch,
        "SYNC_BRANCH": "framework-sync/2026-10-23-1652",
        "FRAMEWORK_HEAD": "a" * 40,
        "GITHUB_REPOSITORY": "example/plugin",
        "GITHUB_SERVER_URL": "https://github.com",
        "GITHUB_STEP_SUMMARY": str(summary),
        "MOCK_ARGS": str(args_file),
        "MOCK_OUTPUT": output,
        "MOCK_STATUS": str(status),
    }
    mock_gh = """
    gh() {
      printf '%s\\n' "$@" > "$MOCK_ARGS"
      printf '%s\\n' "$MOCK_OUTPUT" >&2
      return "$MOCK_STATUS"
    }
    """
    result = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", dedent(mock_gh) + script],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )

    args = args_file.read_text().splitlines()
    assert args[:2] == ["pr", "create"]
    assert args[args.index("--repo") + 1] == "example/plugin"
    assert args[args.index("--base") + 1] == base_branch
    assert args[args.index("--head") + 1] == env["SYNC_BRANCH"]
    assert args[args.index("--title") + 1] == f"chore: framework sync {'a' * 40}"
    assert "Review required before merge." in args_file.read_text()
    assert output in result.stdout + result.stderr
    assert result.returncode == (0 if manual_review else status)

    if manual_review:
        url = (
            f"https://github.com/example/plugin/compare/{base_branch}"
            f"...{env['SYNC_BRANCH']}?expand=1"
        )
        assert "::warning::" in result.stdout
        assert url in result.stdout
        assert url in summary.read_text()
        assert "no pull request was created" in summary.read_text()
        assert "Allow GitHub Actions to create and approve pull requests" in (
            summary.read_text()
        )
    else:
        assert "::warning::" not in result.stdout
        assert not summary.exists()
