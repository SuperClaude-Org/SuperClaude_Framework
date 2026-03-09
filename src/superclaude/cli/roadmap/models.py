"""Roadmap data models -- RoadmapConfig and AgentSpec.

RoadmapConfig extends PipelineConfig with roadmap-specific fields.
AgentSpec represents a model:persona pair for generate steps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from ..pipeline.models import PipelineConfig


@dataclass
class AgentSpec:
    """Represents a model:persona pair for a generate step.

    The model value is passed directly to ``claude -p --model``
    (no resolution -- claude CLI accepts opus/sonnet/haiku natively).
    """

    model: str
    persona: str

    @classmethod
    def parse(cls, spec: str) -> AgentSpec:
        """Parse a 'model:persona' or 'model' string into an AgentSpec.

        Examples:
            AgentSpec.parse("opus:architect") -> AgentSpec("opus", "architect")
            AgentSpec.parse("haiku")          -> AgentSpec("haiku", "architect")
        """
        if ":" in spec:
            model, persona = spec.split(":", 1)
            return cls(model=model.strip(), persona=persona.strip())
        return cls(model=spec.strip(), persona="architect")

    @property
    def id(self) -> str:
        """Short identifier for filenames, e.g. 'opus-architect'."""
        return f"{self.model}-{self.persona}"


@dataclass
class RoadmapConfig(PipelineConfig):
    """Configuration for the roadmap generation pipeline.

    Extends PipelineConfig with roadmap-specific fields:
    spec_file, agents, depth, output_dir, retrospective_file.
    """

    spec_file: Path = field(default_factory=lambda: Path("."))
    agents: list[AgentSpec] = field(
        default_factory=lambda: [
            AgentSpec("opus", "architect"),
            AgentSpec("haiku", "architect"),
        ]
    )
    depth: Literal["quick", "standard", "deep"] = "standard"
    output_dir: Path = field(default_factory=lambda: Path("."))
    retrospective_file: Path | None = None


@dataclass
class ValidateConfig(PipelineConfig):
    """Configuration for the roadmap validation pipeline.

    Extends PipelineConfig with validation-specific fields:
    output_dir, agents. Inherits model, max_turns, debug from PipelineConfig.
    """

    output_dir: Path = field(default_factory=lambda: Path("."))
    agents: list[AgentSpec] = field(
        default_factory=lambda: [
            AgentSpec("opus", "architect"),
            AgentSpec("haiku", "architect"),
        ]
    )
