"""
Unit tests for CLI install functionality

Tests agent installation and bulk skill installation.
"""

from superclaude.cli.install_assets import (
    install_agents,
    list_available_agents,
)
from superclaude.cli.install_skill import (
    install_all_skills,
    list_available_skills,
)


class TestInstallAgents:
    """Test suite for agent installation"""

    def test_list_available_agents(self):
        """Test listing available agents"""
        agents = list_available_agents()

        assert isinstance(agents, list)
        assert agents == sorted(agents)
        assert "explore-haiku" in agents

    def test_install_agents_to_temp_dir(self, tmp_path):
        """Test installing agents to a temporary directory"""
        target_dir = tmp_path / "agents"

        success, message = install_agents(target_path=target_dir, force=False)

        assert success is True
        assert "Installed" in message
        assert (target_dir / "explore-haiku.md").exists()

    def test_install_agents_skip_existing(self, tmp_path):
        """Test that existing agents are skipped without --force"""
        target_dir = tmp_path / "agents"

        success1, _ = install_agents(target_path=target_dir, force=False)
        assert success1 is True

        success2, message2 = install_agents(target_path=target_dir, force=False)
        assert success2 is True
        assert "Skipped" in message2

    def test_install_agents_force_reinstall(self, tmp_path):
        """Test force reinstall overwrites existing agents"""
        target_dir = tmp_path / "agents"

        install_agents(target_path=target_dir, force=False)

        agent_file = target_dir / "explore-haiku.md"
        agent_file.write_text("modified")

        success, message = install_agents(target_path=target_dir, force=True)
        assert success is True
        assert "Installed" in message
        assert agent_file.read_text() != "modified"

    def test_install_agents_creates_target_directory(self, tmp_path):
        """Test that target directory is created if it doesn't exist"""
        target_dir = tmp_path / "nested" / "agents"

        assert not target_dir.exists()

        success, _ = install_agents(target_path=target_dir, force=False)

        assert success is True
        assert target_dir.exists()


class TestInstallAllSkills:
    """Test suite for bulk skill installation"""

    def test_list_available_skills(self):
        """Test all v5 skills are available"""
        skills = list_available_skills()

        for expected in ["confidence-check", "pm-reflexion", "socratic", "spec-panel"]:
            assert expected in skills, f"Expected skill '{expected}' not found"

    def test_install_all_skills_to_temp_dir(self, tmp_path):
        """Test installing all skills to a temporary directory"""
        target_dir = tmp_path / "skills"

        success, message = install_all_skills(target_path=target_dir, force=False)

        assert success is True
        assert "Installed" in message
        assert (target_dir / "confidence-check" / "SKILL.md").exists()
        assert (target_dir / "spec-panel" / "SKILL.md").exists()
        assert (target_dir / "socratic" / "SKILL.md").exists()
        assert (target_dir / "pm-reflexion" / "SKILL.md").exists()

    def test_install_all_skills_skip_existing(self, tmp_path):
        """Test that existing skills are skipped without force"""
        target_dir = tmp_path / "skills"

        success1, _ = install_all_skills(target_path=target_dir, force=False)
        assert success1 is True

        success2, message2 = install_all_skills(target_path=target_dir, force=False)
        assert success2 is True
        assert "Skipped" in message2

    def test_install_all_skills_force_reinstall(self, tmp_path):
        """Test force reinstall overwrites existing skills"""
        target_dir = tmp_path / "skills"

        install_all_skills(target_path=target_dir, force=False)

        skill_md = target_dir / "confidence-check" / "SKILL.md"
        skill_md.write_text("modified")

        success, message = install_all_skills(target_path=target_dir, force=True)
        assert success is True
        assert "Installed" in message
        assert skill_md.read_text() != "modified"

    def test_install_only_subset(self, tmp_path):
        """Test installing a restricted subset of skills (--minimal path)"""
        target_dir = tmp_path / "skills"

        success, message = install_all_skills(
            target_path=target_dir, force=False, only=["confidence-check"]
        )

        assert success is True
        assert (target_dir / "confidence-check").exists()
        assert not (target_dir / "spec-panel").exists()

    def test_install_only_unknown_skill_fails(self, tmp_path):
        """Test that restricting to an unknown skill fails"""
        target_dir = tmp_path / "skills"

        success, message = install_all_skills(
            target_path=target_dir, force=False, only=["nonexistent-xyz"]
        )

        assert success is False
        assert "not found" in message.lower()


def test_cli_integration():
    """Integration test: verify CLI can import and use install functions"""
    from superclaude.cli.install_assets import list_available_agents
    from superclaude.cli.install_skill import list_available_skills

    assert len(list_available_agents()) > 0
    assert len(list_available_skills()) > 0
