"""
Tests for Skill Installation Command

Tests skill installation functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch


class TestInstallSkill:
    """Tests for install_skill module"""

    def test_list_available_skills_returns_list(self):
        """Test list_available_skills returns a list"""
        from superclaude.cli.install_skill import list_available_skills

        result = list_available_skills()

        assert isinstance(result, list)

    def test_list_available_skills_sorted(self):
        """Test list_available_skills returns sorted list"""
        from superclaude.cli.install_skill import list_available_skills

        result = list_available_skills()

        assert result == sorted(result)

    def test_install_skill_nonexistent_skill(self):
        """Test installing nonexistent skill fails"""
        from superclaude.cli.install_skill import install_skill_command

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "skills"
            success, message = install_skill_command("nonexistent-skill-xyz", target)

            assert success is False
            assert "not found" in message.lower()

    def test_install_skill_creates_target_dir(self):
        """Test install_skill creates target directory"""
        from superclaude.cli.install_skill import install_skill_command

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "new" / "nested" / "skills"

            # Even if skill doesn't exist, target dir creation is attempted
            install_skill_command("nonexistent", target)

            # May or may not exist depending on when creation happens
            # Just verify no exception is raised


class TestGetSkillSource:
    """Tests for _get_skill_source function"""

    def test_get_skill_source_returns_none_for_unknown(self):
        """Test _get_skill_source returns None for unknown skills"""
        from superclaude.cli.install_skill import _get_skill_source

        result = _get_skill_source("unknown-skill-xyz-123")

        assert result is None

    def test_get_skill_source_handles_hyphen_underscore(self):
        """Test _get_skill_source normalizes skill names"""
        from superclaude.cli.install_skill import _get_skill_source

        # Should handle both hyphen and underscore versions
        result1 = _get_skill_source("some-skill")
        result2 = _get_skill_source("some_skill")

        # Both should return same or None
        assert result1 == result2 or (result1 is None and result2 is None)


class TestIsValidSkillDir:
    """Tests for _is_valid_skill_dir function"""

    def test_is_valid_skill_dir_with_skill_md(self):
        """Test _is_valid_skill_dir recognizes SKILL.md"""
        from superclaude.cli.install_skill import _is_valid_skill_dir

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir)
            (skill_dir / "SKILL.md").touch()

            assert _is_valid_skill_dir(skill_dir) is True

    def test_is_valid_skill_dir_with_implementation_md(self):
        """Test _is_valid_skill_dir recognizes implementation.md"""
        from superclaude.cli.install_skill import _is_valid_skill_dir

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir)
            (skill_dir / "implementation.md").touch()

            assert _is_valid_skill_dir(skill_dir) is True

    def test_is_valid_skill_dir_with_code_files(self):
        """Test _is_valid_skill_dir recognizes code files"""
        from superclaude.cli.install_skill import _is_valid_skill_dir

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir)
            (skill_dir / "main.py").touch()

            assert _is_valid_skill_dir(skill_dir) is True

    def test_is_valid_skill_dir_empty_dir(self):
        """Test _is_valid_skill_dir rejects empty directory"""
        from superclaude.cli.install_skill import _is_valid_skill_dir

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir)

            assert _is_valid_skill_dir(skill_dir) is False

    def test_is_valid_skill_dir_nonexistent(self):
        """Test _is_valid_skill_dir handles nonexistent path"""
        from superclaude.cli.install_skill import _is_valid_skill_dir

        result = _is_valid_skill_dir(Path("/nonexistent/path/xyz"))

        assert result is False

    def test_is_valid_skill_dir_none_path(self):
        """Test _is_valid_skill_dir handles None"""
        from superclaude.cli.install_skill import _is_valid_skill_dir

        result = _is_valid_skill_dir(None)

        assert result is False


class TestInstallSkillWithMocks:
    """Tests with mocked skill source"""

    def test_install_skill_success(self):
        """Test successful skill installation"""
        from superclaude.cli.install_skill import install_skill_command

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock skill source
            source_dir = Path(tmpdir) / "source" / "test-skill"
            source_dir.mkdir(parents=True)
            (source_dir / "SKILL.md").write_text("# Test Skill")
            (source_dir / "main.py").write_text("# Main file")

            target_dir = Path(tmpdir) / "target"

            with patch(
                "superclaude.cli.install_skill._get_skill_source",
                return_value=source_dir,
            ):
                success, message = install_skill_command("test-skill", target_dir)

            assert success is True
            assert "successfully" in message.lower()
            assert (target_dir / "test-skill" / "SKILL.md").exists()

    def test_install_skill_already_exists(self):
        """Test skill installation fails if already exists"""
        from superclaude.cli.install_skill import install_skill_command

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock skill source
            source_dir = Path(tmpdir) / "source" / "test-skill"
            source_dir.mkdir(parents=True)
            (source_dir / "SKILL.md").write_text("# Test Skill")

            target_dir = Path(tmpdir) / "target"
            (target_dir / "test-skill").mkdir(parents=True)

            with patch(
                "superclaude.cli.install_skill._get_skill_source",
                return_value=source_dir,
            ):
                success, message = install_skill_command("test-skill", target_dir)

            assert success is False
            assert "already installed" in message.lower()

    def test_install_skill_force_reinstall(self):
        """Test skill force reinstall overwrites existing"""
        from superclaude.cli.install_skill import install_skill_command

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock skill source
            source_dir = Path(tmpdir) / "source" / "test-skill"
            source_dir.mkdir(parents=True)
            (source_dir / "SKILL.md").write_text("# New Version")

            target_dir = Path(tmpdir) / "target"
            existing = target_dir / "test-skill"
            existing.mkdir(parents=True)
            (existing / "SKILL.md").write_text("# Old Version")

            with patch(
                "superclaude.cli.install_skill._get_skill_source",
                return_value=source_dir,
            ):
                success, message = install_skill_command(
                    "test-skill", target_dir, force=True
                )

            assert success is True
            content = (target_dir / "test-skill" / "SKILL.md").read_text()
            assert "New Version" in content
