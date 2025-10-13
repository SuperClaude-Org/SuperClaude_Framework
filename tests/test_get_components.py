import pytest
from unittest.mock import patch, MagicMock
import argparse
from setup.cli.commands.install import get_components_to_install


class TestGetComponents:
    @patch("setup.cli.commands.install.select_mcp_servers")
    def test_get_components_to_install_interactive_mcp(self, mock_select_mcp):
        # Arrange
        mock_registry = MagicMock()
        mock_config_manager = MagicMock()
        mock_config_manager._installation_context = {}
        mock_select_mcp.return_value = ["magic"]

        args = argparse.Namespace(components=["mcp"])

        # Act
        components = get_components_to_install(args, mock_registry, mock_config_manager)

        # Assert
        mock_select_mcp.assert_called_once()
        assert "mcp" in components
        assert "mcp_docs" in components  # Should be added automatically
        assert hasattr(mock_config_manager, "_installation_context")
        assert mock_config_manager._installation_context["selected_mcp_servers"] == [
            "magic"
        ]
