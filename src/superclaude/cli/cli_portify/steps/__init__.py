"""Step implementations for cli-portify pipeline.

Phase 3 (deterministic steps):
- validate_config: Step 1 — config validation
- discover_components: Step 2 — component inventory
- gates: EXEMPT/STANDARD gate checks for Steps 1-2

Phase 5 (core content generation, Claude-assisted):
- analyze_workflow: Step 3 — workflow analysis
- design_pipeline: Step 4 — pipeline design with dry-run and review gate
- synthesize_spec: Step 5 — spec synthesis with sentinel scan

Phase 6 (quality amplification):
- brainstorm_gaps: Step 6 — gap identification with multi-persona analysis
- panel_review: Step 7 — iterative panel review with convergence engine
"""

from .analyze_workflow import run_analyze_workflow
from .brainstorm_gaps import run_brainstorm_gaps
from .design_pipeline import run_design_pipeline
from .discover_components import run_discover_components
from .gates import (
    DISCOVER_COMPONENTS_GATE,
    VALIDATE_CONFIG_GATE,
    gate_discover_components,
    gate_validate_config,
)
from .panel_review import run_panel_review
from .synthesize_spec import run_synthesize_spec, scan_sentinels
from .validate_config import run_validate_config

__all__ = [
    "run_validate_config",
    "run_discover_components",
    "run_analyze_workflow",
    "run_design_pipeline",
    "run_synthesize_spec",
    "scan_sentinels",
    "run_brainstorm_gaps",
    "run_panel_review",
    "gate_validate_config",
    "gate_discover_components",
    "VALIDATE_CONFIG_GATE",
    "DISCOVER_COMPONENTS_GATE",
]
