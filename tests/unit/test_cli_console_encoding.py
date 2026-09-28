"""Tests for the CLI's console encoding guard (#559)."""

import io
import sys

import click
import pytest

from superclaude.cli.main import _ensure_utf8_console

EMOJI_LINE = "📋 Available Commands:"


def _cp1252_stream() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="cp1252", write_through=True)


class TestEnsureUtf8Console:
    def test_emoji_output_survives_a_cp1252_console_on_windows(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.delenv("PYTHONIOENCODING", raising=False)
        stdout = _cp1252_stream()
        stderr = _cp1252_stream()
        monkeypatch.setattr(sys, "stdout", stdout)
        monkeypatch.setattr(sys, "stderr", stderr)

        # Without the guard this is the crash from the issue.
        with pytest.raises(UnicodeEncodeError):
            stdout.write(EMOJI_LINE)

        _ensure_utf8_console()

        click.echo(EMOJI_LINE)
        click.echo(EMOJI_LINE, err=True)
        assert stdout.buffer.getvalue() == (EMOJI_LINE + "\n").encode("utf-8")
        assert stderr.buffer.getvalue() == (EMOJI_LINE + "\n").encode("utf-8")

    def test_streams_are_left_alone_off_windows(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "linux")
        monkeypatch.delenv("PYTHONIOENCODING", raising=False)
        stdout = _cp1252_stream()
        monkeypatch.setattr(sys, "stdout", stdout)

        _ensure_utf8_console()

        assert stdout.encoding == "cp1252"

    def test_explicit_pythonioencoding_wins(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setenv("PYTHONIOENCODING", "cp1252")
        stdout = _cp1252_stream()
        monkeypatch.setattr(sys, "stdout", stdout)

        _ensure_utf8_console()

        assert stdout.encoding == "cp1252"

    def test_streams_without_reconfigure_are_skipped(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.delenv("PYTHONIOENCODING", raising=False)
        monkeypatch.setattr(sys, "stdout", io.StringIO())
        monkeypatch.setattr(sys, "stderr", io.StringIO())

        _ensure_utf8_console()  # must not raise
