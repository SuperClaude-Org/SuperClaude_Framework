"""
Unit tests for CLI main entry point and console encoding configuration.
"""

import io
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from superclaude.cli.main import _configure_console_encoding, main


class TestConsoleEncodingConfiguration:
    """Test suite for console encoding reconfiguration on Windows (Issue #559)."""

    def test_configure_console_encoding_on_windows(self):
        """Verify reconfigure(encoding='utf-8', errors='replace') is invoked on Windows."""
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()

        with (
            patch("sys.platform", "win32"),
            patch("sys.stdout", mock_stdout),
            patch("sys.stderr", mock_stderr),
        ):
            _configure_console_encoding()

            mock_stdout.reconfigure.assert_called_once_with(
                encoding="utf-8", errors="replace"
            )
            mock_stderr.reconfigure.assert_called_once_with(
                encoding="utf-8", errors="replace"
            )

    def test_configure_console_encoding_skipped_on_non_windows(self):
        """Verify reconfigure is not called on non-Windows platforms."""
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()

        with (
            patch("sys.platform", "linux"),
            patch("sys.stdout", mock_stdout),
            patch("sys.stderr", mock_stderr),
        ):
            _configure_console_encoding()

            mock_stdout.reconfigure.assert_not_called()
            mock_stderr.reconfigure.assert_not_called()

    def test_configure_console_encoding_handles_none_stream(self):
        """Verify None streams (e.g. GUI/daemon execution) are handled gracefully."""
        with (
            patch("sys.platform", "win32"),
            patch("sys.stdout", None),
            patch("sys.stderr", None),
        ):
            # Should not raise AttributeError
            _configure_console_encoding()

    def test_configure_console_encoding_handles_stream_without_reconfigure(self):
        """Verify streams without reconfigure attribute do not raise errors."""
        mock_stream = object()
        with (
            patch("sys.platform", "win32"),
            patch("sys.stdout", mock_stream),
            patch("sys.stderr", mock_stream),
        ):
            _configure_console_encoding()

    def test_emoji_output_survives_cp1252_encoding_after_reconfigure(self):
        """
        Regression test for #559: Emoji output crashed on cp1252 consoles.
        After reconfigure, writing emojis must not raise UnicodeEncodeError.
        """
        buf = io.BytesIO()
        wrapper = io.TextIOWrapper(buf, encoding="cp1252")
        wrapper.reconfigure(encoding="utf-8", errors="replace")

        test_emojis = "📋 Available Commands: 📦 ✅ ⬜ 🔌 📁 🚀 💡 ❌ ⚠️"
        wrapper.write(test_emojis)
        wrapper.flush()

        output = buf.getvalue().decode("utf-8")
        assert "Available Commands" in output


class TestCliCommands:
    """Test CLI commands execution via CliRunner."""

    def test_cli_version_command(self):
        runner = CliRunner()
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "SuperClaude version" in result.output

    def test_cli_install_list_command(self):
        runner = CliRunner()
        result = runner.invoke(main, ["install", "--list"])
        assert result.exit_code == 0
        assert "Available Commands" in result.output
        assert "Available Agents" in result.output
