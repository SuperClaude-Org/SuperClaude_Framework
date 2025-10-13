import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from setup.components.mcp_docs import MCPDocsComponent


class TestMCPDocsComponent:
    @patch(
        "setup.components.mcp_docs.MCPDocsComponent._post_install", return_value=True
    )
    def test_install_calls_post_install_even_if_no_docs(self, mock_post_install):
        component = MCPDocsComponent(install_dir=Path("/fake/dir"))

        # Simulate no servers selected
        config = {"selected_mcp_servers": []}

        success = component._install(config)

        assert success is True
        mock_post_install.assert_called_once()

    @patch(
        "setup.components.mcp_docs.MCPDocsComponent._post_install", return_value=True
    )
    @patch(
        "setup.components.mcp_docs.MCPDocsComponent.get_files_to_install",
        return_value=[],
    )
    @patch("setup.core.base.Component.validate_prerequisites", return_value=(True, []))
    def test_install_calls_post_install_if_docs_not_found(
        self, mock_validate_prereqs, mock_get_files, mock_post_install
    ):
        component = MCPDocsComponent(install_dir=Path("/tmp/fake_dir"))

        # Simulate a server was selected, but the doc file doesn't exist
        config = {"selected_mcp_servers": ["some_server_with_no_doc_file"]}

        success = component._install(config)

        assert success is True
        mock_post_install.assert_called_once()
