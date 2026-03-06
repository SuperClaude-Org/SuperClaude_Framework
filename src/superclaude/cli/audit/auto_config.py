"""Auto-config generation for cold-start repository audits.

Implements AC13: cold-start runs (no pre-existing config) generate a usable
configuration automatically from repository profiling output.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .profiler import ProfileReport

logger = logging.getLogger(__name__)

CONFIG_FILENAME = ".cleanup-audit.json"


@dataclass
class AuditConfig:
    """Audit configuration with all required fields."""

    batch_size: int = 50
    depth: str = "standard"  # "surface", "standard", "deep"
    report_mode: str = "full"  # "summary", "full", "verbose"
    budget: int = 50_000  # token budget

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuditConfig:
        return cls(
            batch_size=data.get("batch_size", 50),
            depth=data.get("depth", "standard"),
            report_mode=data.get("report_mode", "full"),
            budget=data.get("budget", 50_000),
        )


def detect_cold_start(config_dir: Path) -> bool:
    """Check for absence of audit config file."""
    config_path = config_dir / CONFIG_FILENAME
    return not config_path.exists()


def generate_config(profile: ProfileReport) -> AuditConfig:
    """Generate default audit config from profiling output.

    Derives configuration values from repository characteristics:
    - batch_size: based on total file count
    - depth: based on risk distribution
    - budget: based on file count and risk tiers
    """
    file_count = len(profile.files)
    risk_dist = profile.risk_distribution
    high_count = risk_dist.get("high", 0)

    # Batch size: smaller batches for smaller repos
    if file_count <= 50:
        batch_size = 25
    elif file_count <= 200:
        batch_size = 50
    else:
        batch_size = 100

    # Depth: deeper for repos with many high-risk files
    high_ratio = high_count / file_count if file_count > 0 else 0
    if high_ratio > 0.3:
        depth = "deep"
    elif high_ratio > 0.1:
        depth = "standard"
    else:
        depth = "surface"

    # Budget: scale with file count and risk
    base_budget = file_count * 200
    risk_multiplier = 1.0 + (high_ratio * 2.0)
    budget = int(base_budget * risk_multiplier)
    budget = max(10_000, min(budget, 500_000))

    return AuditConfig(
        batch_size=batch_size,
        depth=depth,
        report_mode="full",
        budget=budget,
    )


def write_config(config: AuditConfig, config_dir: Path) -> Path:
    """Write generated config to standard location.

    Returns the path to the written config file.
    Logs the config generation event.
    """
    config_path = config_dir / CONFIG_FILENAME
    config_path.parent.mkdir(parents=True, exist_ok=True)

    data = config.to_dict()
    config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    logger.info(
        "Auto-generated audit config: %s",
        json.dumps(data),
    )

    return config_path


def ensure_config(config_dir: Path, profile: ProfileReport) -> AuditConfig:
    """Ensure config exists. Generate from profile if cold-start.

    Returns the loaded or generated config.
    """
    config_path = config_dir / CONFIG_FILENAME

    if config_path.exists():
        data = json.loads(config_path.read_text(encoding="utf-8"))
        return AuditConfig.from_dict(data)

    # Cold start: generate from profile
    config = generate_config(profile)
    write_config(config, config_dir)
    return config
