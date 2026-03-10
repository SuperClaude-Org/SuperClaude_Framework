"""Cross-phase deduplication and consolidation of audit findings.

Implements T04.01 / D-0027 / AC18: deduplicates findings from surface,
structural, and cross-cutting phases using file-path keying, merges
evidence, and resolves conflicting classifications by highest-confidence-wins.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .classification import ClassificationResult, V2Action, V2Tier, map_to_v1


@dataclass
class ConflictRecord:
    """Records a classification conflict that was resolved."""

    file_path: str
    phase_classifications: list[dict[str, Any]]
    winner_phase: str
    winner_confidence: float
    resolution_rule: str = "highest-confidence-wins"

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "phase_classifications": self.phase_classifications,
            "winner_phase": self.winner_phase,
            "winner_confidence": self.winner_confidence,
            "resolution_rule": self.resolution_rule,
        }


@dataclass
class ConsolidatedFinding:
    """A single consolidated finding for one file path."""

    file_path: str
    tier: V2Tier
    action: V2Action
    confidence: float
    evidence: list[str]
    source_phases: list[str]
    conflict: ConflictRecord | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "file_path": self.file_path,
            "tier": self.tier.value,
            "action": self.action.value,
            "v1_category": map_to_v1(self.tier, self.action).value,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "source_phases": self.source_phases,
        }
        if self.conflict:
            result["conflict"] = self.conflict.to_dict()
        return result


@dataclass
class ConsolidationReport:
    """Full consolidation output."""

    findings: list[ConsolidatedFinding] = field(default_factory=list)
    conflicts: list[ConflictRecord] = field(default_factory=list)
    total_input_findings: int = 0
    total_consolidated: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_input_findings": self.total_input_findings,
            "total_consolidated": self.total_consolidated,
            "conflict_count": len(self.conflicts),
            "findings": [f.to_dict() for f in self.findings],
            "conflicts": [c.to_dict() for c in self.conflicts],
        }

    def file_paths(self) -> set[str]:
        return {f.file_path for f in self.findings}


@dataclass
class PhaseFinding:
    """A finding tagged with its source phase."""

    phase: str
    result: ClassificationResult


def consolidate(
    phase_findings: list[PhaseFinding],
) -> ConsolidationReport:
    """Consolidate findings across phases.

    Dedup key: file_path (primary key).
    Conflict resolution: highest-confidence classification wins.
    Evidence: merged from all phases (no evidence loss).

    Args:
        phase_findings: All findings from all phases, each tagged with phase name.

    Returns:
        ConsolidationReport with deduplicated, merged findings.
    """
    # Group by file_path
    by_file: dict[str, list[PhaseFinding]] = {}
    for pf in phase_findings:
        by_file.setdefault(pf.result.file_path, []).append(pf)

    report = ConsolidationReport(total_input_findings=len(phase_findings))
    findings: list[ConsolidatedFinding] = []

    for file_path in sorted(by_file.keys()):
        group = by_file[file_path]

        # Merge all evidence from all phases
        merged_evidence: list[str] = []
        source_phases: list[str] = []
        for pf in group:
            for ev in pf.result.evidence:
                if ev not in merged_evidence:
                    merged_evidence.append(ev)
            if pf.phase not in source_phases:
                source_phases.append(pf.phase)

        # Check for classification conflicts
        unique_classifications = set()
        for pf in group:
            unique_classifications.add((pf.result.tier, pf.result.action))

        conflict: ConflictRecord | None = None

        if len(unique_classifications) > 1:
            # Conflict: resolve by highest confidence
            phase_entries = [
                {
                    "phase": pf.phase,
                    "tier": pf.result.tier.value,
                    "action": pf.result.action.value,
                    "confidence": pf.result.confidence,
                }
                for pf in group
            ]
            winner = max(group, key=lambda pf: pf.result.confidence)
            conflict = ConflictRecord(
                file_path=file_path,
                phase_classifications=phase_entries,
                winner_phase=winner.phase,
                winner_confidence=winner.result.confidence,
            )
            report.conflicts.append(conflict)

            tier = winner.result.tier
            action = winner.result.action
            confidence = winner.result.confidence
        else:
            # No conflict: use the classification (all agree)
            best = max(group, key=lambda pf: pf.result.confidence)
            tier = best.result.tier
            action = best.result.action
            confidence = best.result.confidence

        findings.append(ConsolidatedFinding(
            file_path=file_path,
            tier=tier,
            action=action,
            confidence=confidence,
            evidence=merged_evidence,
            source_phases=source_phases,
            conflict=conflict,
        ))

    report.findings = findings
    report.total_consolidated = len(findings)
    return report
