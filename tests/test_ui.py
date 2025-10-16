"""
Tests for rich-based UI (modern typer + rich implementation)

Note: Custom UI utilities (setup/utils/ui.py) have been removed.
The new CLI uses typer + rich natively via superclaude/cli/
"""

import pytest
from unittest.mock import patch
from rich.console import Console
from io import StringIO


def test_rich_console_available():
    """Test that rich console is available and functional"""
    console = Console(file=StringIO())
    console.print("[green]Success[/green]")
    # No assertion needed - just verify no errors


def test_typer_cli_imports():
    """Test that new typer CLI can be imported"""
    from superclaude.cli.app import app, cli_main

    assert app is not None
    assert callable(cli_main)


@pytest.mark.integration
def test_cli_help_command():
    """Test CLI help command works"""
    from typer.testing import CliRunner
    from superclaude.cli.app import app

    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "SuperClaude Framework CLI" in result.output


@pytest.mark.integration
def test_cli_version_command():
    """Test CLI version command"""
    from typer.testing import CliRunner
    from superclaude.cli.app import app

    runner = CliRunner()
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "SuperClaude" in result.output
