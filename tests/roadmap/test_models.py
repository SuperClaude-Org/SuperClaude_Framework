"""Tests for roadmap/models.py -- AgentSpec and RoadmapConfig."""

from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import PipelineConfig
from superclaude.cli.roadmap.models import AgentSpec, RoadmapConfig


class TestAgentSpec:
    def test_parse_model_persona(self):
        a = AgentSpec.parse("opus:architect")
        assert a.model == "opus"
        assert a.persona == "architect"

    def test_parse_model_only(self):
        a = AgentSpec.parse("haiku")
        assert a.model == "haiku"
        assert a.persona == "architect"

    def test_parse_with_whitespace(self):
        a = AgentSpec.parse("  sonnet : security  ")
        assert a.model == "sonnet"
        assert a.persona == "security"

    def test_id_property(self):
        a = AgentSpec("opus", "architect")
        assert a.id == "opus-architect"

    def test_parse_various_formats(self):
        cases = [
            ("opus:architect", "opus", "architect"),
            ("haiku:qa", "haiku", "qa"),
            ("sonnet", "sonnet", "architect"),
            ("claude-3-opus:security", "claude-3-opus", "security"),
        ]
        for spec, expected_model, expected_persona in cases:
            result = AgentSpec.parse(spec)
            assert result.model == expected_model
            assert result.persona == expected_persona


class TestRoadmapConfig:
    def test_inherits_pipeline_config(self):
        assert issubclass(RoadmapConfig, PipelineConfig)

    def test_default_agents(self):
        config = RoadmapConfig()
        assert len(config.agents) == 2
        assert config.agents[0].model == "opus"
        assert config.agents[0].persona == "architect"
        assert config.agents[1].model == "haiku"
        assert config.agents[1].persona == "architect"

    def test_default_depth(self):
        config = RoadmapConfig()
        assert config.depth == "standard"

    def test_custom_agents(self):
        agents = [AgentSpec("sonnet", "security"), AgentSpec("haiku", "qa")]
        config = RoadmapConfig(agents=agents)
        assert config.agents[0].model == "sonnet"
        assert config.agents[1].persona == "qa"

    def test_has_pipeline_fields(self):
        config = RoadmapConfig(
            work_dir=Path("/tmp"),
            dry_run=True,
            max_turns=100,
            model="opus",
            debug=True,
        )
        assert config.work_dir == Path("/tmp")
        assert config.dry_run is True
        assert config.max_turns == 100
        assert config.model == "opus"
        assert config.debug is True

    def test_roadmap_specific_fields(self):
        config = RoadmapConfig(
            spec_file=Path("/tmp/spec.md"),
            output_dir=Path("/tmp/output"),
            depth="deep",
        )
        assert config.spec_file == Path("/tmp/spec.md")
        assert config.output_dir == Path("/tmp/output")
        assert config.depth == "deep"
