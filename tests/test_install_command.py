import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, ANY
import argparse
from setup.cli.commands import install


class TestInstallCommand:
    @patch("setup.cli.commands.install.get_components_to_install")
    @patch("setup.cli.commands.install.ComponentRegistry")
    @patch("setup.cli.commands.install.ConfigService")
    @patch("setup.cli.commands.install.Validator")
    @patch("setup.cli.commands.install.display_installation_plan")
    @patch("setup.cli.commands.install.perform_installation")
    @patch("setup.cli.commands.install.confirm", return_value=True)
    @patch("setup.cli.commands.install.validate_system_requirements", return_value=True)
    @patch("pathlib.Path.home")
    def test_run_resolves_dependencies_before_planning(
        self,
        mock_home,
        mock_validate_reqs,
        mock_confirm,
        mock_perform,
        mock_display,
        mock_validator,
        mock_config,
        mock_registry_class,
        mock_get_components,
        tmp_path,
    ):
        # Arrange
        mock_home.return_value = tmp_path
        install_dir = tmp_path / ".claude"

        mock_args = argparse.Namespace(
            components=["mcp"],
            install_dir=install_dir,
            quiet=True,  # to avoid calling display_header
            yes=True,
            force=False,
            dry_run=False,
            diagnose=False,
            list_components=False,
        )

        mock_registry_instance = MagicMock()
        mock_registry_class.return_value = mock_registry_instance

        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.validate_config_files.return_value = []

        mock_get_components.return_value = ["mcp"]
        mock_registry_instance.resolve_dependencies.return_value = ["core", "mcp"]

        # Act
        install.run(mock_args)

        # Assert
        # Check that resolve_dependencies was called with the initial list
        mock_registry_instance.resolve_dependencies.assert_called_once_with(["mcp"])

        # Check that display_installation_plan was not called because of quiet=True
        mock_display.assert_not_called()

        # Check that perform_installation was called with the resolved list
        mock_perform.assert_called_once_with(["core", "mcp"], mock_args, ANY)
