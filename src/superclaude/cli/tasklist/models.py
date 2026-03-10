"""Tasklist data models -- TasklistValidateConfig.

TasklistValidateConfig extends PipelineConfig with tasklist-specific fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..pipeline.models import PipelineConfig


@dataclass
class TasklistValidateConfig(PipelineConfig):
    """Configuration for the tasklist validation pipeline.

    Extends PipelineConfig with tasklist-specific fields:
    output_dir, roadmap_file, tasklist_dir.
    """

    output_dir: Path = field(default_factory=lambda: Path("."))
    roadmap_file: Path = field(default_factory=lambda: Path("."))
    tasklist_dir: Path = field(default_factory=lambda: Path("."))
