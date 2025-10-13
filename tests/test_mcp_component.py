import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from setup.components.mcp import MCPComponent


class TestMCPComponent:
    @patch("setup.components.mcp.MCPComponent._post_install", return_value=True)
    @patch(
        "setup.components.mcp.MCPComponent.validate_prerequisites",
        return_value=(True, []),
    )
    @patch("setup.components.mcp.MCPComponent._install_mcp_server")
    def test_install_selected_servers_only(
        self, mock_install_mcp_server, mock_validate_prereqs, mock_post_install
    ):
        mock_install_mcp_server.return_value = True

        component = MCPComponent(install_dir=Path("/fake/dir"))
        component.installed_servers_in_session = []

        # Simulate selecting only the 'magic' server
        config = {"selected_mcp_servers": ["magic"]}

        success = component._install(config)

        assert success is True
        assert component.installed_servers_in_session == ["magic"]

        # Assert that _install_mcp_server was called exactly once
        assert mock_install_mcp_server.call_count == 1

        # Assert that it was called with the correct server info
        called_args, _ = mock_install_mcp_server.call_args
        server_info_arg = called_args[0]

        assert server_info_arg["name"] == "magic"
        assert server_info_arg["npm_package"] == "@21st-dev/magic"

    @patch("subprocess.run")
    def test_validate_installation_success(self, mock_subprocess_run):
        component = MCPComponent(install_dir=Path("/fake/dir"))

        # Mock settings manager
        component.settings_manager = MagicMock()
        component.settings_manager.is_component_installed.return_value = True
        component.settings_manager.get_component_version.return_value = (
            component.get_metadata()["version"]
        )
        component.settings_manager.get_metadata_setting.return_value = [
            "magic",
            "playwright",
        ]

        # Mock `claude mcp list` output
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = "magic\nplaywright\n"

        success, errors = component.validate_installation()

        assert success is True
        assert not errors

    @patch("subprocess.run")
    def test_validate_installation_failure(self, mock_subprocess_run):
        component = MCPComponent(install_dir=Path("/fake/dir"))

        # Mock settings manager
        component.settings_manager = MagicMock()
        component.settings_manager.is_component_installed.return_value = True
        component.settings_manager.get_component_version.return_value = (
            component.get_metadata()["version"]
        )
        component.settings_manager.get_metadata_setting.return_value = [
            "magic",
            "playwright",
        ]

        # Mock `claude mcp list` output - 'playwright' is missing
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = "magic\n"

        success, errors = component.validate_installation()

        assert success is False
        assert len(errors) == 1
        assert "playwright" in errors[0]
