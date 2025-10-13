import pytest
from unittest.mock import patch, MagicMock
from setup.utils.ui import display_header
import io

from setup.utils.ui import display_authors


@patch("sys.stdout", new_callable=io.StringIO)
def test_display_header_with_authors(mock_stdout):
    # Mock the author and email info from superclaude/__init__.py
    with patch("superclaude.__author__", "Author One, Author Two"), patch(
        "superclaude.__email__", "one@example.com, two@example.com"
    ):

        display_header("Test Title", "Test Subtitle")

        output = mock_stdout.getvalue()

        assert "Test Title" in output
        assert "Test Subtitle" in output
        assert "Author One <one@example.com>" in output
        assert "Author Two <two@example.com>" in output
        assert "Author One <one@example.com> | Author Two <two@example.com>" in output


@patch("sys.stdout", new_callable=io.StringIO)
def test_display_authors(mock_stdout):
    # Mock the author, email, and github info from superclaude/__init__.py
    with patch("superclaude.__author__", "Author One, Author Two"), patch(
        "superclaude.__email__", "one@example.com, two@example.com"
    ), patch("superclaude.__github__", "user1, user2"):

        display_authors()

        output = mock_stdout.getvalue()

        assert "SuperClaude Authors" in output
        assert "Author One" in output
        assert "one@example.com" in output
        assert "https://github.com/user1" in output
        assert "Author Two" in output
        assert "two@example.com" in output
        assert "https://github.com/user2" in output
