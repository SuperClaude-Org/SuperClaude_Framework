import pytest
from pathlib import Path
import shutil
import tarfile
import tempfile
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
