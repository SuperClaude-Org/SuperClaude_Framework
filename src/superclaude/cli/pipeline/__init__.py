"""Pipeline module -- shared base for sprint and roadmap CLI commands.

Public API surface (9 symbols):
- PipelineConfig, Step, StepResult, StepStatus, GateCriteria, SemanticCheck  (models)
- execute_pipeline  (executor)
- gate_passed  (gates)
- ClaudeProcess  (process)
"""

from .executor import execute_pipeline
from .gates import gate_passed
from .models import (
    GateCriteria,
    PipelineConfig,
    SemanticCheck,
    Step,
    StepResult,
    StepStatus,
)
from .process import ClaudeProcess

__all__ = [
    "ClaudeProcess",
    "GateCriteria",
    "PipelineConfig",
    "SemanticCheck",
    "Step",
    "StepResult",
    "StepStatus",
    "execute_pipeline",
    "gate_passed",
]
