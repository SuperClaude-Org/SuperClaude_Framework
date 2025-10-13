import pytest
from pathlib import Path
import shutil
import tarfile
import tempfile
from unittest.mock import MagicMock
from setup.core.installer import Installer


class TestInstaller:
    def test_create_backup_empty_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            installer = Installer(install_dir=temp_dir)

            backup_path = installer.create_backup()

            assert backup_path is not None
            assert backup_path.exists()

            # This is the crucial part: check if it's a valid tar file.
            # An empty file created with .touch() is not a valid tar file.
            try:
                with tarfile.open(backup_path, "r:gz") as tar:
                    members = tar.getmembers()
                    # An empty archive can have 0 members, or 1 member (the root dir)
                    if len(members) == 1:
                        assert members[0].name == "."
                    else:
                        assert len(members) == 0
            except tarfile.ReadError as e:
                pytest.fail(f"Backup file is not a valid tar.gz file: {e}")

    def test_skips_already_installed_component(self):
        # Create a mock component that is NOT reinstallable
        mock_component = MagicMock()
        mock_component.get_metadata.return_value = {"name": "test_component"}
        mock_component.is_reinstallable.return_value = False
        mock_component.install.return_value = True
        mock_component.validate_prerequisites.return_value = (True, [])

        installer = Installer()
        installer.register_component(mock_component)

        # Simulate component is already installed
        installer.installed_components = {"test_component"}

        installer.install_component("test_component", {})

        # Assert that the install method was NOT called
        mock_component.install.assert_not_called()
        assert "test_component" in installer.skipped_components

    def test_installs_reinstallable_component(self):
        # Create a mock component that IS reinstallable
        mock_component = MagicMock()
        mock_component.get_metadata.return_value = {"name": "reinstallable_component"}
        mock_component.is_reinstallable.return_value = True
        mock_component.install.return_value = True
        mock_component.validate_prerequisites.return_value = (True, [])

        installer = Installer()
        installer.register_component(mock_component)

        # Simulate component is already installed
        installer.installed_components = {"reinstallable_component"}

        installer.install_component("reinstallable_component", {})

        # Assert that the install method WAS called
        mock_component.install.assert_called_once()
        assert "reinstallable_component" not in installer.skipped_components

    def test_post_install_validation_only_validates_updated_components(self):
        # Arrange
        installer = Installer()

        mock_comp1 = MagicMock()
        mock_comp1.get_metadata.return_value = {"name": "comp1"}
        mock_comp1.validate_installation.return_value = (True, [])

        mock_comp2 = MagicMock()
        mock_comp2.get_metadata.return_value = {"name": "comp2"}
        mock_comp2.validate_installation.return_value = (True, [])

        installer.register_component(mock_comp1)
        installer.register_component(mock_comp2)

        installer.updated_components = {"comp1"}

        # Act
        installer._run_post_install_validation()

        # Assert
        mock_comp1.validate_installation.assert_called_once()
        mock_comp2.validate_installation.assert_not_called()
