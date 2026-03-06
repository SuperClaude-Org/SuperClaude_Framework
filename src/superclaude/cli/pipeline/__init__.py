"""Pipeline module -- shared base for sprint and roadmap CLI commands.

Public API surface (42 symbols):
- PipelineConfig, Step, StepResult, StepStatus, GateCriteria, SemanticCheck  (models)
- Deliverable, DeliverableKind  (deliverable schema)
- decompose_deliverables, is_behavioral  (deliverable analysis)
- execute_pipeline  (executor)
- gate_passed  (gates)
- ClaudeProcess  (process)
- GuardDetection, GuardKind, TypeTransitionKind  (guard analyzer)
- GuardResolutionOutput, ReleaseGateWarning, AcceptedRisk  (guard resolution)
- GuardAnalysisOutput, run_guard_analysis_pass  (guard pipeline pass)
- InvariantRegistryOutput, run_invariant_registry_pass  (invariant registry pass)
- DetectionDifficulty, Severity, FMEAFailureMode, classify_failure_modes  (FMEA classifier)
- FMEAPromotionOutput, ReleaseGateViolation, promote_failure_modes  (FMEA promotion)
- CombinedM2Output, run_combined_m2_pass  (combined M2 pass)
- DataFlowGraph, DataFlowNode, DataFlowEdge, NodeOperation, build_dataflow_graph  (M4 graph)
- ImplicitContract, extract_implicit_contracts  (M4 contract extractor)
- ConflictKind, ConflictDetection, detect_conflicts  (M4 conflict detector)
- DataFlowTracingOutput, run_dataflow_tracing_pass  (M4 pipeline pass)
"""

from .combined_m2_pass import CombinedM2Output, run_combined_m2_pass
from .conflict_detector import ConflictDetection, ConflictKind, detect_conflicts
from .contract_extractor import ImplicitContract, extract_implicit_contracts
from .dataflow_graph import (
    DataFlowEdge,
    DataFlowGraph,
    DataFlowNode,
    NodeOperation,
    build_dataflow_graph,
)
from .dataflow_pass import DataFlowTracingOutput, run_dataflow_tracing_pass
from .deliverables import decompose_deliverables, is_behavioral
from .executor import execute_pipeline
from .fmea_classifier import (
    DetectionDifficulty,
    FMEAFailureMode,
    Severity,
    classify_failure_modes,
)
from .fmea_promotion import (
    FMEAPromotionOutput,
    ReleaseGateViolation,
    promote_failure_modes,
)
from .gates import gate_passed
from .guard_analyzer import GuardDetection, GuardKind, TypeTransitionKind
from .guard_pass import GuardAnalysisOutput, run_guard_analysis_pass
from .guard_resolution import AcceptedRisk, GuardResolutionOutput, ReleaseGateWarning
from .invariant_pass import InvariantRegistryOutput, run_invariant_registry_pass
from .models import (
    Deliverable,
    DeliverableKind,
    GateCriteria,
    PipelineConfig,
    SemanticCheck,
    Step,
    StepResult,
    StepStatus,
)
from .process import ClaudeProcess

__all__ = [
    "AcceptedRisk",
    "ClaudeProcess",
    "CombinedM2Output",
    "ConflictDetection",
    "ConflictKind",
    "DataFlowEdge",
    "DataFlowGraph",
    "DataFlowNode",
    "DataFlowTracingOutput",
    "Deliverable",
    "DeliverableKind",
    "DetectionDifficulty",
    "FMEAFailureMode",
    "FMEAPromotionOutput",
    "GateCriteria",
    "GuardAnalysisOutput",
    "GuardDetection",
    "GuardKind",
    "GuardResolutionOutput",
    "ImplicitContract",
    "InvariantRegistryOutput",
    "NodeOperation",
    "PipelineConfig",
    "ReleaseGateViolation",
    "ReleaseGateWarning",
    "SemanticCheck",
    "Severity",
    "Step",
    "StepResult",
    "StepStatus",
    "TypeTransitionKind",
    "build_dataflow_graph",
    "classify_failure_modes",
    "decompose_deliverables",
    "detect_conflicts",
    "execute_pipeline",
    "extract_implicit_contracts",
    "gate_passed",
    "is_behavioral",
    "promote_failure_modes",
    "run_combined_m2_pass",
    "run_dataflow_tracing_pass",
    "run_guard_analysis_pass",
    "run_invariant_registry_pass",
]
